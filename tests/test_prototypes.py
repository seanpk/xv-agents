import json
import os
import shutil
import sys
import unittest

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")


class PrototypesTest(RepoCase):
    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        text = text[:text.index("agents:")] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' \
            + text[text.index("seats:"):]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        out = self.xv("slice", "new", "p1", "--by", "pat", "--kind", "prototype", "--axis",
                      "what the household acts on when it marks food used",
                      "--scenario", "Marking food used after a meal is quicker.").stdout
        self.wt = out.strip().splitlines()[-1]

    def record(self):
        return json.loads(self.xv("record", "show", "p1", "--json", cwd=self.wt).stdout)

    def test_three_prototypes_side_by_side_then_a_pick_by_two_people(self):
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)
        p = self.xv("run", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stderr)
        v = json.loads(p.stdout)
        self.assertEqual((v["stop"]["order"], v["stop"]["seat"]), ("prototypes_ready", "two_people"))
        side = open(os.path.join(self.wt, ".xv", "slices", "p1.prototypes.md")).read()
        for n in "abc":
            self.assertIn(f"variant {n}:", side)
        branches = sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout.split()
        self.assertEqual(len(branches), 3)

        spend_before = len(self.record()["spend"])
        p = self.xv("run", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10)
        self.assertIn("unanswered", p.stdout)
        self.assertEqual(len(self.record()["spend"]), spend_before, "resuming does not rebuild the prototypes")

        p = self.xv("prototype", "pick", "p1", "--variant", "b", "--by", "pat", cwd=self.wt, check=False)
        self.assertIn("two people", p.stderr)
        scen = os.path.join(self.tmp, "restated.md")
        open(scen, "w").write("After a meal, the household marks a whole recipe's food used in one call.")
        self.xv("prototype", "pick", "p1", "--variant", "b", "--by", "pat,sam", "--with-user", "Ana",
                "--scenario-file", scen, cwd=self.wt)
        data = self.record()
        self.assertEqual((data["kind"], data["next"]), ("feature", "forecaster"))
        self.assertEqual(sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout.strip(), "")
        body = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        self.assertIn("marks a whole recipe's food used in one call", body.split("## May ignore")[0])
        self.assertIn("Ana (user)", open(os.path.join(self.wt, data["decisions"][0]["record"])).read())


# A git that logs when each worktree/branch command starts and ends, and sleeps in it so two at once would overlap.
# FAKE_GIT_REFUSE=<variant> makes that variant's `worktree add` fail the way a held lock does.
FAKE_GIT = '''#!{python}
import json, os, re, subprocess, sys, time
args = sys.argv[1:]
m = re.search(r"proto-(\\w)", " ".join(args))
op = " ".join(args[:2])
if m and op in ("worktree remove", "worktree add", "branch -D"):
    log = os.environ["FAKE_GIT_LOG"]
    def note(what):
        with open(log, "a") as f:
            f.write(json.dumps({{"variant": m.group(1), "op": op, "what": what, "t": time.time()}}) + "\\n")
    note("start")
    time.sleep(0.3)
    if op == "worktree add" and os.environ.get("FAKE_GIT_REFUSE") == m.group(1):
        sys.stderr.write("fatal: Unable to create '.git/index.lock': File exists.\\n")
        note("end")
        sys.exit(128)
    p = subprocess.run([os.environ["REAL_GIT"]] + args)
    note("end")
    sys.exit(p.returncode)
os.execv(os.environ["REAL_GIT"], [os.environ["REAL_GIT"]] + args)
'''

# An agent that logs when it starts and ends, sleeps, then does the fake agent's job.
SLOW_AGENT = '''#!{python}
import json, os, re, subprocess, sys, time
prompt = sys.argv[1]
v = re.search(r"Your variant: (\\w)\\.", prompt).group(1)
def note(what):
    with open(os.environ["FAKE_AGENT_LOG"], "a") as f:
        f.write(json.dumps({{"variant": v, "what": what, "t": time.time()}}) + "\\n")
note("start")
time.sleep(2)
p = subprocess.run([{python!r}, {fake!r}, prompt], capture_output=True, text=True)
sys.stdout.write(p.stdout)
note("end")
'''


class PrototypesGitSetupTest(PrototypesTest):
    test_three_prototypes_side_by_side_then_a_pick_by_two_people = None  # not rerun here

    def setUp(self):
        super().setUp()
        self.addCleanup(self.restore_env)
        self.saved = dict(os.environ)
        bindir = os.path.join(self.tmp, "bin")
        os.makedirs(bindir)
        fake_git = os.path.join(bindir, "git")
        open(fake_git, "w").write(FAKE_GIT.format(python=sys.executable))
        os.chmod(fake_git, 0o755)
        agent = os.path.join(self.tmp, "slow_agent.py")
        open(agent, "w").write(SLOW_AGENT.format(python=sys.executable, fake=FAKE))
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read().replace(f'["{sys.executable}", "{FAKE}", "{{prompt}}"]',
                                        f'["{sys.executable}", "{agent}", "{{prompt}}"]')
        open(cfg, "w").write(text)
        self.git_log = os.path.join(self.tmp, "git.log")
        self.agent_log = os.path.join(self.tmp, "agent.log")
        os.environ["REAL_GIT"] = shutil.which("git")
        os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
        os.environ["FAKE_GIT_LOG"] = self.git_log
        os.environ["FAKE_AGENT_LOG"] = self.agent_log
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)

    def restore_env(self):
        os.environ.clear()
        os.environ.update(self.saved)

    def entries(self, path):
        if not os.path.exists(path):
            return []
        return [json.loads(l) for l in open(path).read().splitlines() if l]

    def side(self):
        return open(os.path.join(self.wt, ".xv", "slices", "p1.prototypes.md")).read()

    def test_one_variants_git_setup_never_overlaps_another_variants(self):
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        spans = {}
        for e in self.entries(self.git_log):
            s = spans.setdefault(e["variant"], [e["t"], e["t"]])
            s[0], s[1] = min(s[0], e["t"]), max(s[1], e["t"])
        self.assertEqual(sorted(spans), ["a", "b", "c"], "every variant ran its git setup")
        for x in "abc":
            for y in "abc":
                if x < y:
                    self.assertTrue(spans[x][1] <= spans[y][0] or spans[y][1] <= spans[x][0],
                                    f"setup of {x} {spans[x]} overlaps setup of {y} {spans[y]}")

    def test_the_agents_still_run_at_the_same_time(self):
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        starts = {e["variant"]: e["t"] for e in self.entries(self.agent_log) if e["what"] == "start"}
        ends = {e["variant"]: e["t"] for e in self.entries(self.agent_log) if e["what"] == "end"}
        self.assertEqual(sorted(starts), ["a", "b", "c"])
        self.assertLess(max(starts.values()), min(ends.values()), "all three agents ran at once")

    def test_a_variant_git_refuses_is_recorded_not_finished_with_its_error_and_the_others_run(self):
        os.environ["FAKE_GIT_REFUSE"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        ran = sorted(e["variant"] for e in self.entries(self.agent_log) if e["what"] == "start")
        self.assertEqual(ran, ["a", "c"], "a and c still run; b's setup was refused")
        protos = {p["name"]: p for p in self.record()["prototypes"]}
        self.assertEqual(sorted(protos), ["a", "b", "c"], "b is recorded, not dropped")
        self.assertTrue(protos["a"]["recording"] and protos["c"]["recording"])
        self.assertFalse(protos["b"]["recording"], "b did not finish")
        side = self.side()
        self.assertIn("## b:", side)
        b_section = side.split("## b:")[1].split("## c:")[0]
        self.assertIn("index.lock", b_section, "the side-by-side file shows b's error")
        self.assertIn("index.lock", open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read(),
                      "the record keeps b's error")

    def test_a_second_start_runs_the_refused_variant_again_and_keeps_the_others(self):
        os.environ["FAKE_GIT_REFUSE"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        os.remove(self.agent_log)
        del os.environ["FAKE_GIT_REFUSE"]
        self.xv("record", "answer", "p1", "--by", "pat,sam", "--answer", "run b again", cwd=self.wt, check=False)
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        ran = sorted(e["variant"] for e in self.entries(self.agent_log) if e["what"] == "start")
        self.assertEqual(ran, ["b"], "only the variant that did not finish runs again")
        protos = {p["name"]: p for p in self.record()["prototypes"]}
        self.assertTrue(all(protos[n]["recording"] for n in "abc"))


if __name__ == "__main__":
    unittest.main()

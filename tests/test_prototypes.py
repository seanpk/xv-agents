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
    if op == "worktree add" and p.returncode == 0 and os.environ.get("FAKE_GIT_VANISH") == m.group(1):
        import shutil
        shutil.rmtree(args[-2])  # the worktree is gone before the agent can start in it
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

    def unfinished_b_is_recorded(self):
        protos = {p["name"]: p for p in self.record()["prototypes"]}
        self.assertEqual(sorted(protos), ["a", "b", "c"], "b is recorded, not dropped")
        self.assertTrue(protos["a"]["recording"] and protos["c"]["recording"], "a and c still finish")
        self.assertFalse(protos["b"]["recording"], "b did not finish")
        side = self.side()
        self.assertIn("## b:", side)
        b_section = side.split("## b:")[1].split("## c:")[0]
        self.assertRegex(b_section, r"Not finished: \S", "the side-by-side file shows b's error")

    def block_b_run_log(self):
        common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], self.wt).stdout.strip()
        # the run log for b cannot be written: a directory sits where the file goes
        os.makedirs(os.path.join(common, "xv", "runs", "p1", "prototype-b.out"))

    def test_an_error_after_setup_records_the_variant_not_finished_with_its_error(self):
        os.environ["FAKE_GIT_VANISH"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.unfinished_b_is_recorded()

    def test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli(self):
        os.environ["FAKE_GIT_VANISH"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        b_section = self.side().split("## b:")[1].split("## c:")[0]
        self.assertNotIn("agent CLI not found", b_section)
        self.assertIn("working folder", b_section)
        self.assertIn("p1-proto-b", b_section)

    def test_an_error_that_is_not_an_xverror_records_the_variant_not_finished_with_its_error(self):
        self.block_b_run_log()
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.unfinished_b_is_recorded()
        self.assertIn("prototype-b.out", open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read(),
                      "the record keeps b's error")

    def pick_b_after(self):
        scen = os.path.join(self.tmp, "restated.md")
        open(scen, "w").write("Restated.")
        self.xv("record", "answer", "p1", "--by", "pat,sam", "--answer", "look", cwd=self.wt, check=False)
        return self.xv("prototype", "pick", "p1", "--variant", "b", "--by", "pat,sam",
                       "--scenario-file", scen, cwd=self.wt, check=False)

    def test_pick_refuses_a_variant_whose_setup_failed_and_says_so(self):
        os.environ["FAKE_GIT_REFUSE"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        p = self.pick_b_after()
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("budget", p.stderr)
        self.assertRegex(p.stderr, r"(?i)setup|failed|did not finish")

    def test_pick_refuses_a_variant_whose_run_failed_and_says_so(self):
        self.block_b_run_log()
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        p = self.pick_b_after()
        self.assertNotEqual(p.returncode, 0, "b did not finish and cannot be picked")
        self.assertNotIn("budget", p.stderr)
        self.assertRegex(p.stderr, r"(?i)setup|failed|did not finish")


# A stand-in `claude` for the prototype step: it logs the budget cap it was given, does the fake agent's job
# in its working folder, and prints the JSON `claude -p --output-format json` prints, with a cost of 0.6 dollars.
FAKE_CLAUDE = '''#!{python}
import json, os, re, subprocess, sys
prompt = sys.argv[-1]
v = re.search(r"Your variant: (\\w)\\.", prompt).group(1)
cap = sys.argv[sys.argv.index("--max-budget-usd") + 1] if "--max-budget-usd" in sys.argv else None
with open(os.environ["CAP_LOG"], "a") as f:
    f.write(json.dumps({{"variant": v, "cap": cap}}) + "\\n")
p = subprocess.run([{python!r}, {fake!r}, prompt], capture_output=True, text=True)
print(json.dumps({{"result": p.stdout, "total_cost_usd": 0.6, "num_turns": 3, "session_id": "sess-" + v,
                  "usage": {{"input_tokens": 1000, "output_tokens": 500}}}}))
'''


class PrototypesErroredSpendTest(PrototypesTest):
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
        self.git_log = os.path.join(self.tmp, "git.log")
        os.environ["REAL_GIT"] = shutil.which("git")
        os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
        os.environ["FAKE_GIT_LOG"] = self.git_log
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)
        claude = os.path.join(self.tmp, "bin", "claude")
        open(claude, "w").write(FAKE_CLAUDE.format(python=sys.executable, fake=FAKE))
        os.chmod(claude, 0o755)
        self.cap_log = os.path.join(self.tmp, "caps.log")
        os.environ["CAP_LOG"] = self.cap_log
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{claude}", "-p", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)

    def restore_env(self):
        os.environ.clear()
        os.environ.update(self.saved)

    def side(self):
        return open(os.path.join(self.wt, ".xv", "slices", "p1.prototypes.md")).read()

    def block_b_run_log(self):
        common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], self.wt).stdout.strip()
        # the run log for b cannot be written: a directory sits where the file goes
        os.makedirs(os.path.join(common, "xv", "runs", "p1", "prototype-b.out"))

    def unfinished_b_is_recorded(self):
        protos = {p["name"]: p for p in self.record()["prototypes"]}
        self.assertEqual(sorted(protos), ["a", "b", "c"], "b is recorded, not dropped")
        self.assertTrue(protos["a"]["recording"] and protos["c"]["recording"], "a and c still finish")
        self.assertFalse(protos["b"]["recording"], "b did not finish")
        b_section = self.side().split("## b:")[1].split("## c:")[0]
        self.assertRegex(b_section, r"Not finished: \S", "the side-by-side file shows b's error")

    def spend_of(self, variant):
        return [s for s in self.record()["spend"] if s.get("step") == f"prototype-{variant}"]

    def test_a_variant_that_ran_and_then_errored_keeps_its_spend(self):
        self.block_b_run_log()
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertEqual(len(self.spend_of("a")), 1, "a finished and keeps its spend")
        rows = self.spend_of("b")
        self.assertEqual(len(rows), 1, "b's agent ran and then errored; its run is in the record")
        self.assertEqual(rows[0]["usd"], 0.6)

    def test_the_errored_variants_spend_counts_against_its_budget_on_the_second_start(self):
        self.block_b_run_log()
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], self.wt).stdout.strip()
        os.rmdir(os.path.join(common, "xv", "runs", "p1", "prototype-b.out"))
        os.remove(self.cap_log)
        self.xv("record", "answer", "p1", "--by", "pat,sam", "--answer", "run b again", cwd=self.wt, check=False)
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        caps = [json.loads(l) for l in open(self.cap_log).read().splitlines() if l]
        self.assertEqual([c["variant"] for c in caps], ["b"], "only b runs again")
        self.assertAlmostEqual(float(caps[0]["cap"]), 0.4, msg="b's budget of 1 dollar less the 0.6 it spent")

    def test_a_variant_whose_working_folder_is_gone_says_the_folder_is_missing(self):
        os.environ["FAKE_GIT_VANISH"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.unfinished_b_is_recorded()
        b_section = self.side().split("## b:")[1].split("## c:")[0]
        self.assertRegex(b_section, r"(?i)working (folder|directory)")
        self.assertNotIn("agent CLI not found", b_section)
        self.assertNotIn("agent CLI not found", open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read())


if __name__ == "__main__":
    unittest.main()

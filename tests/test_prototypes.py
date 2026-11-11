import json
import os
import re
import shutil
import sys
import unittest
from unittest import mock

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

    def make_b_raise_a_plain_error(self):
        # b's agent prints bytes that are not text: reading its output raises a ValueError, not an XVError
        bad = os.path.join(self.tmp, "bad_agent.py")
        open(bad, "w").write("import subprocess, sys\n"
                             "if 'Your variant: b.' in sys.argv[1]:\n"
                             "    sys.stdout.buffer.write(b'\\xff\\xfe')\n"
                             "    sys.exit(0)\n"
                             f"sys.stdout.write(subprocess.run([{sys.executable!r}, {FAKE!r}, sys.argv[1]],"
                             " capture_output=True, text=True).stdout)\n")
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        open(cfg, "w").write(text[:start] + f'agents:\n  default: ["{sys.executable}", "{bad}", "{{prompt}}"]\n'
                             + text[end:])

    def test_an_error_that_is_not_an_xverror_records_the_variant_not_finished_with_its_error(self):
        self.make_b_raise_a_plain_error()
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.unfinished_b_is_recorded()
        self.assertIn("codec", open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read(),
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


def read_home(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


class KeptPickTest(PrototypesTest):
    """`xv prototype pick ... --keep`: the pick's branch becomes the build the slice starts from."""
    test_three_prototypes_side_by_side_then_a_pick_by_two_people = None  # not rerun here

    BUILD_FILE = "pantry/kept_by_b.py"
    RULES_B = "# rules as variant b left them\n"

    def setUp(self):
        super().setUp()
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)
        p = self.xv("run", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stderr)
        self.scen = os.path.join(self.tmp, "restated.md")
        open(self.scen, "w").write("The household marks a whole recipe's food used in one call.")
        self.prompts = os.path.join(self.tmp, "prompts.log")
        self.cwds = os.path.join(self.tmp, "cwds.log")

    def proto_wt(self, name):
        rows = sh(["git", "worktree", "list", "--porcelain"], self.repo).stdout.splitlines()
        found = [r[len("worktree "):] for r in rows if r.startswith("worktree ") and r.endswith(f"p1-proto-{name}")]
        self.assertEqual(len(found), 1, f"no worktree for variant {name}")
        return found[0]

    def build_in(self, name, files, fixed=False):
        """What the variant's agent leaves on its branch: committed files, and the fix when `fixed`."""
        wt = self.proto_wt(name)
        for rel, text in files.items():
            os.makedirs(os.path.dirname(os.path.join(wt, rel)), exist_ok=True)
            with open(os.path.join(wt, rel), "w") as f:
                f.write(text)
        if fixed:
            path = os.path.join(wt, "pantry", "store.py")
            text = open(path).read().replace("today < i.expires_on <= last", "today <= i.expires_on <= last")
            open(path, "w").write(text)
        sh(["git", "add", "-A"], wt)
        sh(["git", "commit", "-q", "--no-verify", "-m", f"variant {name}"], wt)
        return sh(["git", "rev-parse", "HEAD"], wt).stdout.strip()

    def pick(self, *flags, variant="b", check=True):
        return self.xv("prototype", "pick", "p1", "--variant", variant, "--by", "pat,sam",
                       "--scenario-file", self.scen, *flags, cwd=self.wt, check=check)

    def branches(self):
        return sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout.split()

    def worktrees(self):
        return sh(["git", "worktree", "list", "--porcelain"], self.repo).stdout

    def record_text(self):
        return open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()

    def slice_head(self):
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def is_ancestor(self, older, newer):
        return sh(["git", "merge-base", "--is-ancestor", older, newer], self.repo, check=False).returncode == 0

    def log_of(self):
        return self.record_text().split("## Log", 1)[1]

    def snapshot(self):
        self.before_text, self.before_head, self.before_branches = \
            self.record_text(), self.slice_head(), sorted(self.branches())

    def assert_refused_and_nothing_changed(self, p):
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertNotIn("unrecognized arguments", p.stderr, "the flag is not known; this is not the refusal")
        self.assertEqual(self.record_text(), self.before_text, "a refusal changed the record")
        self.assertEqual(self.slice_head(), self.before_head, "a refusal moved the slice branch")
        self.assertEqual(sorted(self.branches()), self.before_branches, "a refusal removed a prototype")

    # 1. the pick is merged, the others removed, the kept one's worktree removed, its branch stays
    def test_keep_merges_the_pick_onto_the_slice_branch_and_removes_the_others(self):
        tip = self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        self.assertTrue(os.path.exists(os.path.join(self.wt, self.BUILD_FILE)), "the pick is not on the slice branch")
        self.assertTrue(self.is_ancestor(tip, self.slice_head()), "the pick's commit is not in the slice branch")
        self.assertEqual(self.branches(), ["xv/p1-proto-b"], "only the kept pick's branch stays")
        for n in "abc":
            self.assertNotIn(f"p1-proto-{n}", self.worktrees(), f"variant {n}'s worktree is still there")

    def test_keep_records_the_build_as_a_kept_pick(self):
        tip = self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        build = self.record()["build"]
        self.assertEqual((build["kind"], build["variant"]), ("kept_pick", "b"))
        self.assertEqual(build["ref"], "xv/p1-proto-b")
        self.assertTrue(self.is_ancestor(tip, build["commit"]), "the build's commit does not hold the pick")
        self.assertEqual(self.record()["build_shared"], "no")

    def test_share_build_with_keep_records_the_build_as_shared(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep", "--share-build")
        self.assertEqual(self.record()["build_shared"], "yes")

    def test_a_kept_pick_keeps_its_own_prototypes_folder(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n",
                            ".xv/prototypes/p1/b/notes.md": "what b refuses\n"})
        self.pick("--keep")
        self.assertTrue(os.path.exists(os.path.join(self.wt, ".xv", "prototypes", "p1", "b", "notes.md")))
        self.assertNotIn(".xv/prototypes/p1/b/notes.md", self.log_of(), "its own folder is not a dropped file")

    # 1. the slice then runs as one opened with `--from`
    def run_steps(self, **env):
        e = {"FAKE_PROMPT_LOG": self.prompts, "FAKE_CWD_LOG": self.cwds,
             "FAKE_CWD_PROBE": f"{self.BUILD_FILE} tests/test_red.py"}
        e.update(env)
        self.xv("record", "set", "p1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        with mock.patch.dict(os.environ, e):
            self.xv("step", "forecaster", "p1", cwd=self.wt, check=False)
            return self.xv("step", "scenario", "p1", cwd=self.wt, check=False)

    def ran(self, title):
        rows = [json.loads(l) for l in open(self.cwds) if l.strip()] if os.path.exists(self.cwds) else []
        rows = [r for r in rows if r["title"].startswith(title)]
        return rows[-1] if rows else None

    def test_the_red_is_written_blind_at_the_base_and_fails_there(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        base = self.record()["base"]
        p = self.run_steps()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario agent did not run")
        self.assertFalse(ran["exists"][self.BUILD_FILE], "the scenario agent's checkout has the build in it")
        self.assertEqual(ran["head"], base, "the red was not written at the base")
        self.assertIs(self.record()["checks"]["scenario"].get("red_fails"), True)

    def test_a_red_that_fails_on_the_kept_build_goes_to_the_maker_with_no_stop(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        self.run_steps()
        rec = self.record()
        self.assertEqual(rec["checks"]["scenario"].get("red_on_build", {}).get("passes"), False)
        self.assertEqual(rec["next"], "maker")

    def test_a_red_that_passes_on_the_kept_build_skips_the_maker(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"}, fixed=True)
        self.pick("--keep")
        self.run_steps()
        self.assertEqual(self.record()["next"], "cleaner")

    def test_a_red_that_passes_on_the_base_stops_even_when_the_kept_build_has_the_fix(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"}, fixed=True)
        self.pick("--keep")
        p = self.run_steps(FAKE_RED_COMMAND="python3 -m unittest tests.test_store")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "scenario_not_red")

    # 2. without --keep the pick works as today
    def test_without_keep_all_three_are_thrown_away_and_the_record_has_no_build(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick()
        self.assertEqual(self.branches(), [])
        self.assertFalse(os.path.exists(os.path.join(self.wt, self.BUILD_FILE)))
        self.assertIn(self.record().get("build"), (None, "none"))

    # 2. refusals change nothing
    def test_keep_with_none_is_refused_and_changes_nothing(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.snapshot()
        p = self.pick("--keep", variant="none", check=False)
        self.assert_refused_and_nothing_changed(p)
        self.assertRegex(p.stderr, r"--keep")

    def test_share_build_without_keep_is_refused_and_changes_nothing(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.snapshot()
        p = self.pick("--share-build", check=False)
        self.assert_refused_and_nothing_changed(p)
        self.assertRegex(p.stderr, r"--share-build")

    def test_a_kept_pick_whose_branch_is_gone_is_refused_and_changes_nothing(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        sh(["git", "worktree", "remove", "--force", self.proto_wt("b")], self.repo)
        sh(["git", "branch", "-D", "xv/p1-proto-b"], self.repo)
        self.snapshot()
        p = self.pick("--keep", check=False)
        self.assert_refused_and_nothing_changed(p)
        self.assertIn(self.record().get("build"), (None, "none"))

    def test_a_kept_pick_that_adds_nothing_is_refused_and_changes_nothing(self):
        self.snapshot()  # b's branch is at the slice's HEAD: its agent committed nothing
        p = self.pick("--keep", check=False)
        self.assert_refused_and_nothing_changed(p)

    # 3. a build's edits to .xv/ are dropped, and the log names each with the build commit that holds its copy
    def test_a_kept_pick_drops_its_edits_to_xv_and_the_log_names_each_with_the_build_commit(self):
        rules_before = open(os.path.join(self.wt, ".xv", "rules.md")).read()
        tip = self.build_in("b", {self.BUILD_FILE: "KEPT = True\n", ".xv/rules.md": self.RULES_B,
                                  ".xv/notes.md": "a new file in .xv\n"})
        self.pick("--keep")
        self.assertEqual(open(os.path.join(self.wt, ".xv", "rules.md")).read(), rules_before,
                         "the build's edit to .xv/rules.md is still in the slice")
        self.assertFalse(os.path.exists(os.path.join(self.wt, ".xv", "notes.md")), "a file the build added to .xv/ stayed")
        log = self.log_of()
        for rel in (".xv/rules.md", ".xv/notes.md"):
            line = next((l for l in log.splitlines() if rel in l), None)
            self.assertIsNotNone(line, f"the log does not name {rel}")
            hashes = re.findall(r"\b[0-9a-f]{7,40}\b", line)
            held = [h for h in hashes
                    if sh(["git", "show", f"{h}:{rel}"], self.repo, check=False).returncode == 0
                    and self.is_ancestor(tip, h)]
            self.assertTrue(held, f"the line for {rel} names no build commit that holds its copy: {line}")

    def test_a_file_that_differs_only_because_the_base_moved_on_is_not_named(self):
        # the slice's own side-by-side file and record moved on after the variant's branch was cut
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        self.assertEqual(self.record()["id"], "p1", "the slice's record is the slice's own")
        log = self.log_of()
        self.assertNotIn("p1.prototypes.md", log)
        self.assertNotIn(".xv/slices/p1.md", log)

    # 4. after a pick, `xv prototype start` refuses on the slice
    def test_after_a_kept_pick_start_refuses_because_it_is_no_longer_a_prototype_slice(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick("--keep")
        p = self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertRegex(p.stderr, r"(?i)no longer a prototype|not a prototype")
        self.assertEqual(self.branches(), ["xv/p1-proto-b"], "start built prototypes on a picked slice")

    def test_after_a_pick_without_keep_start_refuses_too(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"})
        self.pick()
        p = self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertRegex(p.stderr, r"(?i)no longer a prototype|not a prototype")
        self.assertEqual(self.branches(), [])

    def test_a_pick_of_none_stays_a_prototype_slice(self):
        self.xv("prototype", "pick", "p1", "--variant", "none", "--by", "pat,sam", cwd=self.wt)
        self.assertEqual(self.record()["kind"], "prototype")

    # 5. close deletes a kept pick's branch when its commit is in the slice branch
    def test_close_deletes_a_kept_picks_branch(self):
        self.build_in("b", {self.BUILD_FILE: "KEPT = True\n"}, fixed=True)
        self.pick("--keep")
        self.run_steps()
        self.xv("close", "p1", "--why", "as forecast", cwd=self.wt)
        self.assertEqual(self.branches(), [], "close left the kept pick's branch")
        self.assertTrue(sh(["git", "rev-parse", "--verify", "-q", "xv/p1"], self.repo).stdout.strip())


class PrototypeStopTextsTest(PrototypesGitSetupTest):
    """6. the stops name each variant that did not finish, with its error."""
    test_one_variants_git_setup_never_overlaps_another_variants = None
    test_the_agents_still_run_at_the_same_time = None
    test_a_variant_git_refuses_is_recorded_not_finished_with_its_error_and_the_others_run = None
    test_a_second_start_runs_the_refused_variant_again_and_keeps_the_others = None
    test_an_error_after_setup_records_the_variant_not_finished_with_its_error = None
    test_an_error_that_is_not_an_xverror_records_the_variant_not_finished_with_its_error = None
    test_pick_refuses_a_variant_whose_setup_failed_and_says_so = None
    test_pick_refuses_a_variant_whose_run_failed_and_says_so = None

    def last_stop(self):
        return self.record()["stops"][-1]

    def test_prototypes_ready_says_the_pick_may_be_thrown_away_or_kept(self):
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        stop = self.last_stop()
        self.assertEqual(stop["order"], "prototypes_ready")
        self.assertRegex(stop["question"], r"(?i)thrown away")
        self.assertRegex(stop["question"], r"(?i)\bkept\b")

    def test_prototypes_ready_names_a_variant_that_did_not_finish_with_its_error(self):
        os.environ["FAKE_GIT_REFUSE"] = "b"
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        stop = self.last_stop()
        self.assertEqual(stop["order"], "prototypes_ready")
        self.assertRegex(stop["question"], r"(?is)\bb\b.{0,200}index\.lock")

    def test_prototype_budget_spent_names_a_variant_that_did_not_finish_with_its_error(self):
        os.environ["FAKE_GIT_REFUSE"] = "b"
        self.xv("record", "set", "p1", "prototype_budgets",
                json.dumps({"a": {"usd": 1}, "b": {"usd": 1}, "c": {"usd": 1}}), "--by", "pat", cwd=self.wt)
        # the sh test harness reports no spend, so a's budget is spent by a recorded prior row
        row = {"step": "prototype-a", "usd": 1, "tokens": 10, "tokens_in": 10, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0}
        self.xv("record", "add", "p1", "spend", json.dumps(row), cwd=self.wt)
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        stop = self.last_stop()
        self.assertEqual(stop["order"], "prototype_budget_spent")
        self.assertRegex(stop["question"], r"(?is)\bb\b.{0,200}index\.lock")

    def test_a_stop_with_every_variant_finished_names_no_error(self):
        self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertNotRegex(self.last_stop()["question"], r"(?i)did not finish|index\.lock")


class KeptPickDocsTest(unittest.TestCase):
    # 7. decision 92 replaces decision 71, and 71 gets the one-line marker
    def decision(self, n):
        for line in read_home("docs", "decisions.md").splitlines():
            if line.startswith(f"{n}. "):
                return line
        self.fail(f"docs/decisions.md has no decision {n}")

    def test_decision_92_replaces_decision_71(self):
        d = self.decision(92)
        self.assertRegex(d, r"(?i)\bkept\b|\bkeep\b")
        self.assertRegex(d, r"\b71\b")
        self.assertRegex(d, r"(?i)replaces")

    def test_decision_71_carries_a_one_line_marker_naming_92(self):
        d = self.decision(71)
        self.assertRegex(d, r"\b92\b")
        self.assertRegex(d, r"(?i)replaced|superseded")

    # 7. the prototype brief loses the sentences that became untrue and does not tell the agent it may be kept
    def test_the_prototype_brief_no_longer_says_the_version_is_discarded_at_the_pick(self):
        text = read_home("skills", "maker", "prototype.md")
        self.assertNotIn("Your version is discarded when the pick is made, whichever it is.", text)
        self.assertNotIn("Nothing you write is a candidate for the main line.", text)

    def test_the_prototype_brief_does_not_tell_the_agent_its_version_may_be_kept(self):
        self.assertNotRegex(read_home("skills", "maker", "prototype.md"), r"(?i)\bkept\b|--keep|\bkeep it\b")

    # 7. the watch skill gives --keep
    def test_the_watch_skill_gives_keep_on_the_pick_command(self):
        text = read_home("skills", "watch", "SKILL.md")
        self.assertRegex(text, r"xv prototype pick <id>[^\n]*--keep")

    # 7. the README stops table and the picture name the kept pick
    def test_the_readme_stops_table_names_the_kept_pick(self):
        row = next(l for l in read_home("README.md").splitlines() if l.startswith("| Prototypes ready to pick from"))
        self.assertRegex(row, r"(?i)kept|keep")

    def test_the_picture_names_the_kept_pick(self):
        text = read_home(".xv", "picture.md")
        self.assertIn("kept_pick", text)
        self.assertIn("--keep", text)

    # 8. EXPLORE-NOTES.md is not in the slice branch's tree
    def test_explore_notes_is_not_in_the_slice_branchs_tree(self):
        tracked = sh(["git", "ls-files", "--", "EXPLORE-NOTES.md"], HOME).stdout.strip()
        self.assertEqual(tracked, "", "EXPLORE-NOTES.md is tracked in the slice's tree")

    # 7. docs and briefs that name the practice say Build to find out
    def test_the_slice_skill_and_the_watch_skill_say_build_to_find_out_not_exploration(self):
        for parts in (("skills", "xv-slice", "SKILL.md"), ("skills", "watch", "SKILL.md")):
            text = read_home(*parts)
            self.assertIn("Build to find out", text, "/".join(parts))
            self.assertNotRegex(text, r"(?i)\bexploration", "/".join(parts))

    # 9. the README method block is not regenerated; it already says Build to find out
    def test_the_readme_method_block_already_says_build_to_find_out(self):
        text = read_home("README.md")
        self.assertIn("Build to find out", text)


if __name__ == "__main__":
    unittest.main()

import json
import os
import re
import subprocess
import sys
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh

import record

FAKE = os.path.join(HOME, "tests", "fake_agent.py")
SCENARIO = "The household sees milk that expires today in the expiring list."
BUILD = "explore-milk"
MARKER = "pantry/explored.py"


def read(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


class FromBuildBase(RepoCase):
    """Helpers for slices opened from a build; it holds no test."""

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        self.main = sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        self.prompts = os.path.join(self.tmp, "prompts.log")
        self.cwds = os.path.join(self.tmp, "cwds.log")

    def make_build(self, fixed, files=None):
        """An exploration built on a branch of its own: a marker file, the fix when `fixed`, and any `files`."""
        sh(["git", "checkout", "-q", "-b", BUILD], self.repo)
        with open(os.path.join(self.repo, MARKER), "w") as f:
            f.write("EXPLORED = True\n")
        for rel, text in (files or {}).items():
            with open(os.path.join(self.repo, rel), "w") as f:
                f.write(text)
        if fixed:
            p = os.path.join(self.repo, "pantry", "store.py")
            text = open(p).read().replace("today < i.expires_on <= last", "today <= i.expires_on <= last")
            open(p, "w").write(text)
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "an exploration"], self.repo)
        self.build = sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        sh(["git", "checkout", "-q", "main"], self.repo)

    def open_slice(self, *flags, check=True):
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", SCENARIO, *flags, check=check)
        if p.returncode == 0:
            self.wt = p.stdout.strip().splitlines()[-1]
            self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        return p

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def env(self, **more):
        e = {"FAKE_PROMPT_LOG": self.prompts, "FAKE_CWD_LOG": self.cwds,
             "FAKE_CWD_PROBE": f"{MARKER} tests/test_red.py"}
        e.update(more)
        return e

    def step(self, agent, **more):
        with mock.patch.dict(os.environ, self.env(**more)):
            return self.xv("step", agent, "s1", cwd=self.wt, check=False)

    def scenario_step(self, **more):
        self.step("forecaster")
        return self.step("scenario", **more)

    def prompt_of(self, title):
        if not os.path.exists(self.prompts):
            return ""
        found = [p for p in open(self.prompts).read().split("\n=====\n") if p.startswith(title)]
        return found[-1] if found else ""

    def ran(self, title):
        if not os.path.exists(self.cwds):
            return None
        rows = [json.loads(line) for line in open(self.cwds) if line.strip()]
        rows = [r for r in rows if r["title"].startswith(title)]
        return rows[-1] if rows else None

    def is_ancestor(self, older, newer, cwd=None):
        return sh(["git", "merge-base", "--is-ancestor", older, newer], cwd or self.repo, check=False).returncode == 0

    def open_stops(self):
        return [s for s in self.record()["stops"] if s.get("answer") is None]

    def amend(self, text="The household also sees milk that expires tomorrow."):
        f = os.path.join(self.tmp, "amend.md")
        with open(f, "w") as fh:
            fh.write(text)
        self.xv("slice", "amend", "s1", "--by", "pat", "--scenario-file", f, cwd=self.wt)

    def copies(self, log):
        """The record copies each scenario agent run could read, in order."""
        if not os.path.exists(log):
            return []
        rows = [json.loads(line) for line in open(log) if line.strip()]
        return [r["record"] for r in rows if r["title"].startswith("# The scenario agent")]

    def commits_at_the_build(self, text):
        """Every commit named in `text` that has the build in it."""
        found = []
        for h in sorted(set(re.findall(r"\b[0-9a-f]{7,40}\b", text))):
            p = sh(["git", "rev-parse", "--verify", "-q", f"{h}^{{commit}}"], self.repo, check=False)
            if p.returncode == 0 and self.is_ancestor(self.build, p.stdout.strip()):
                found.append(h)
        return found

    def commits_off_the_base(self, text):
        """Every commit named in `text` that is not an ancestor of the base."""
        found = []
        for h in sorted(set(re.findall(r"\b[0-9a-f]{7,40}\b", text))):
            p = sh(["git", "rev-parse", "--verify", "-q", f"{h}^{{commit}}"], self.repo, check=False)
            if p.returncode == 0 and not self.is_ancestor(p.stdout.strip(), self.main):
                found.append(h)
        return found

    def scratch_worktrees(self):
        rows = sh(["git", "worktree", "list", "--porcelain"], self.repo).stdout.splitlines()
        kept = {os.path.realpath(self.repo), os.path.realpath(self.wt)}
        return [r[len("worktree "):] for r in rows
                if r.startswith("worktree ") and os.path.realpath(r[len("worktree "):]) not in kept]


class SliceNewFromTest(FromBuildBase):
    # 1. `xv slice new --from <ref>`
    def test_the_slice_branch_starts_at_the_build(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.assertTrue(self.is_ancestor(self.build, "HEAD", cwd=self.wt),
                        "the slice branch does not start at the build")
        self.assertTrue(os.path.exists(os.path.join(self.wt, MARKER)))

    def test_base_is_the_branch_it_will_merge_into_not_the_build(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        base = self.record()["base"]
        self.assertTrue(base, "the record has no base")
        self.assertEqual(sh(["git", "rev-parse", f"{base}^{{commit}}"], self.repo).stdout.strip(), self.main)

    def test_the_record_says_the_build_is_an_exploration_and_names_the_ref(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        build = json.dumps(self.record().get("build"))
        self.assertIn("exploration", build)
        self.assertIn(BUILD, build)

    def test_a_slice_with_no_from_has_build_none(self):
        self.open_slice()
        self.assertEqual(self.record().get("build"), "none")

    def test_a_from_ref_that_does_not_exist_is_refused(self):
        p = self.open_slice("--from", "no-such-branch", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unrecognized arguments", p.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", "s1")))

    def test_an_empty_from_is_refused(self):
        p = self.open_slice("--from", "", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unrecognized arguments", p.stderr)

    def test_from_with_no_ref_is_refused(self):
        p = self.open_slice("--from", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unrecognized arguments", p.stderr)

    # 11. `--share-build` without `--from` is refused, and opens no slice
    def test_share_build_without_from_is_refused_and_opens_no_slice(self):
        self.make_build(fixed=False)
        p = self.open_slice("--share-build", check=False)
        self.assertNotEqual(p.returncode, 0, "xv slice new took --share-build without --from")
        out = p.stdout + p.stderr
        self.assertNotIn("unrecognized arguments", out)
        self.assertRegex(out, r"--share-build[^\n]{0,80}needs[^\n]{0,40}--from")
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", "s1")),
                         "a worktree was opened for the slice")
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "slices", "s1.md")),
                         "a slice record was written")
        branch = sh(["git", "rev-parse", "--verify", "-q", "refs/heads/xv/s1"], self.repo, check=False)
        self.assertNotEqual(branch.returncode, 0, "a slice branch was made")


class BuildNotSharedTest(FromBuildBase):
    # 4. by default the scenario agent never sees the build
    def setUp(self):
        super().setUp()
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)

    def test_the_record_says_build_shared_no(self):
        self.assertEqual(self.record().get("build_shared"), "no")

    def test_the_scenario_agent_runs_in_a_worktree_at_base(self):
        self.scenario_step()
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario agent did not run")
        self.assertFalse(ran["exists"][MARKER], "the scenario agent's checkout has the build in it")
        self.assertTrue(self.is_ancestor(self.main, ran["head"]))
        self.assertFalse(self.is_ancestor(self.build, ran["head"]))

    def test_the_scenario_agents_prompt_names_no_build_branch_or_diff(self):
        self.scenario_step()
        prompt = self.prompt_of("# The scenario agent")
        self.assertTrue(prompt, "the scenario agent did not run")
        self.assertNotIn(BUILD, prompt)
        self.assertNotIn(self.build[:7], prompt)


class BuildSharedTest(FromBuildBase):
    # 5. `xv slice new --from <ref> --share-build`
    def setUp(self):
        super().setUp()
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD, "--share-build")

    def test_the_record_says_build_shared_yes(self):
        self.assertEqual(self.record().get("build_shared"), "yes")

    def test_the_scenario_agents_prompt_names_the_build_as_a_reference_only(self):
        self.scenario_step()
        prompt = self.prompt_of("# The scenario agent")
        self.assertTrue(prompt, "the scenario agent did not run")
        self.assertIn(BUILD, prompt)
        self.assertRegex(prompt, r"(?i)reference only")
        self.assertRegex(prompt, r"(?is)what the scenario says")
        self.assertRegex(prompt, r"(?is)not assume[^.]{0,80}look like the build")


class RedOnTheBuildTest(FromBuildBase):
    # 6. the red must fail on the base, as now
    def test_a_red_that_passes_on_the_base_stops_even_when_the_build_has_the_fix(self):
        self.make_build(fixed=True)
        self.open_slice("--from", BUILD)
        p = self.scenario_step(FAKE_RED_COMMAND="python3 -m unittest tests.test_store")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "scenario_not_red")
        self.assertNotEqual(self.record()["next"], "cleaner")

    # 7. a red test that fails on the build goes to the maker as a miss, with no stop
    def test_a_red_that_fails_on_the_build_goes_to_the_maker_with_no_stop(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIsNone(json.loads(p.stdout).get("stop"))
        self.assertEqual(self.open_stops(), [])
        rec = self.record()
        self.assertIs(rec["checks"]["scenario"].get("red_fails"), True)
        self.assertEqual(rec["next"], "maker")

    def test_the_maker_is_told_which_red_test_missed_on_the_build(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        maker = self.xv("prompt", "maker", "s1", cwd=self.wt).stdout
        self.assertIn("test_milk_today", maker)

    def test_the_maker_starts_from_the_build_with_the_red_in_it(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        self.assertTrue(os.path.exists(os.path.join(self.wt, "tests", "test_red.py")),
                        "the red is not on the slice branch")
        p = self.step("maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        ran = self.ran("# The maker")
        self.assertIsNotNone(ran, "the maker did not run")
        self.assertTrue(ran["exists"][MARKER], "the maker's checkout does not have the build")
        self.assertTrue(ran["exists"]["tests/test_red.py"], "the maker's checkout does not have the red")
        self.assertTrue(self.is_ancestor(self.build, ran["head"]))

    # 8. every red test passes on the build: skip the maker, go to the cleaner
    def test_a_red_that_passes_on_the_build_skips_the_maker(self):
        self.make_build(fixed=True)
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rec = self.record()
        self.assertIs(rec["checks"]["scenario"].get("red_fails"), True, "the red did not fail on the base")
        self.assertEqual(rec["next"], "cleaner")

    def test_a_run_from_a_build_that_passes_the_red_never_runs_the_maker(self):
        self.make_build(fixed=True)
        self.open_slice("--from", BUILD)
        with mock.patch.dict(os.environ, self.env()):
            self.xv("run", "s1", cwd=self.wt, check=False)
        steps = [s.get("step") for s in self.record()["spend"]]
        self.assertNotIn("maker", steps)
        self.assertIn("cleaner", steps)

    # 9. the decision is in scripts/orders.py
    def test_orders_decides_where_the_slice_goes_after_the_scenario_step(self):
        self.make_build(fixed=True)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        p = self.xv("orders", "s1", "--after", "scenario", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout).get("next"), "cleaner")

    def test_orders_sends_a_red_that_fails_on_the_build_to_the_maker(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        p = self.xv("orders", "s1", "--after", "scenario", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        v = json.loads(p.stdout)
        self.assertIsNone(v.get("stop"))
        self.assertIn(v.get("next"), ("maker", None))

    def test_a_slice_with_no_build_goes_to_the_maker_as_now(self):
        self.open_slice()
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")


class SecondScenarioPassTest(FromBuildBase):
    # 12. a second scenario pass starts at the base with the earlier red, and lands without a conflict
    def setUp(self):
        super().setUp()
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.amend()

    def test_the_second_pass_starts_at_the_base_with_the_earlier_red_in_it(self):
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario agent did not run")
        self.assertFalse(ran["exists"][MARKER], "the second pass's checkout has the build in it")
        self.assertTrue(ran["exists"]["tests/test_red.py"], "the second pass's checkout does not have the earlier red")
        self.assertFalse(self.is_ancestor(self.build, ran["head"]))

    def test_the_second_pass_lands_on_the_slice_branch_without_a_conflict(self):
        p = self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("red_conflicts_with_build", [s["order"] for s in self.record()["stops"]])
        self.assertIn("SECOND-PASS", open(os.path.join(self.wt, "tests", "test_red.py")).read(),
                      "the second pass's red is not on the slice branch")
        self.assertTrue(os.path.exists(os.path.join(self.wt, MARKER)), "the slice branch lost the build")


class SecondPassAfterTheMakerTest(FromBuildBase):
    # 12. a second scenario pass after the maker starts at the base with the earlier red, not the maker's fix
    MAKER_FIX = "today <= i.expires_on <= last"
    PROBE = f"{MARKER} tests/test_red.py pantry/store.py"

    def open_and_make(self, build_files=None):
        self.make_build(fixed=False, files=build_files)
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = self.step("maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(self.MAKER_FIX, open(os.path.join(self.wt, "pantry", "store.py")).read(),
                      "the maker did not make its fix")
        self.amend()
        if os.path.exists(self.cwds):  # only the second pass's checkout is read
            os.remove(self.cwds)

    def build_edits_the_makers_file(self):
        """The build changes pantry/store.py two lines above the line the maker fixes."""
        old = open(os.path.join(self.repo, "pantry", "store.py")).read()
        new = old.replace('"""Items that run out within', '"""Items (explored) that run out within')
        self.assertNotEqual(old, new)
        return {"pantry/store.py": new}

    def test_a_second_pass_after_the_maker_has_the_earlier_red_and_not_the_makers_fix(self):
        self.open_and_make()
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE=self.PROBE)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario agent did not run")
        self.assertFalse(ran["exists"][MARKER], "the second pass's checkout has the build in it")
        self.assertTrue(ran["exists"]["tests/test_red.py"], "the second pass's checkout does not have the earlier red")
        self.assertNotIn(self.MAKER_FIX, ran["texts"]["pantry/store.py"],
                         "the second pass's checkout has the maker's fix in it")

    def test_a_second_pass_after_the_maker_still_fails_the_red_on_the_base(self):
        self.open_and_make()
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        rec = self.record()
        self.assertNotIn("scenario_not_red", [s["order"] for s in rec["stops"]],
                         "the red passed on the base: the base run held the maker's fix")
        self.assertIs(rec["checks"]["scenario"].get("red_fails"), True, "the red did not fail on the base")

    def test_a_second_pass_after_a_maker_that_edits_a_file_the_build_changed_starts_at_the_base(self):
        self.open_and_make(self.build_edits_the_makers_file())
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE=self.PROBE)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the second scenario pass did not start")
        self.assertFalse(ran["exists"][MARKER], "the second pass's checkout has the build in it")
        self.assertTrue(ran["exists"]["tests/test_red.py"], "the second pass's checkout does not have the earlier red")
        self.assertNotIn(self.MAKER_FIX, ran["texts"]["pantry/store.py"],
                         "the second pass's checkout has the maker's fix in it")

    def test_a_second_pass_after_a_maker_that_edits_a_file_the_build_changed_lands_without_a_conflict(self):
        self.open_and_make(self.build_edits_the_makers_file())
        p = self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertNotEqual(p.returncode, 1, "the step crashed: " + p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertNotIn("red_conflicts_with_build", [s["order"] for s in self.record()["stops"]])
        self.assertIn("SECOND-PASS", open(os.path.join(self.wt, "tests", "test_red.py")).read(),
                      "the second pass's red is not on the slice branch")
        self.assertIn(self.MAKER_FIX, open(os.path.join(self.wt, "pantry", "store.py")).read(),
                      "the slice branch lost the maker's fix")
        self.assertTrue(os.path.exists(os.path.join(self.wt, MARKER)), "the slice branch lost the build")

    def test_a_second_pass_after_the_maker_leaves_no_checkout_behind(self):
        self.open_and_make(self.build_edits_the_makers_file())
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertEqual(self.scratch_worktrees(), [], "the scenario agent's checkout was left behind")


class RedOnItsOwnRefTest(FromBuildBase):
    # 12, as Sean settled it: the red at the base lives on its own ref, each later pass starts from that
    # ref's tip, and nothing is replayed from the slice branch onto the base
    BUILD_LINE = "        found = self.store.expiring(3, date(2026, 10, 21))\n"
    FIRST_RED = "test_milk_today_in_the_store"
    PROBE = f"{MARKER} tests/test_red.py tests/test_store.py"

    def build_edits_near_the_red(self):
        """The build changes tests/test_store.py two lines above the place the red writes its new test."""
        old = open(os.path.join(self.repo, "tests", "test_store.py")).read()
        self.assertEqual(old.count(self.BUILD_LINE), 1)
        return {"tests/test_store.py": old.replace(self.BUILD_LINE, self.BUILD_LINE[:-1] + "  # explored\n")}

    def first_pass(self, build_files=None):
        """A first pass whose red adds a test to tests/test_store.py; then the slice is amended."""
        self.make_build(fixed=False, files=build_files)
        self.open_slice("--from", BUILD)
        p = self.scenario_step(FAKE_RED_ADDS_TO_OLD="1")
        if build_files and self.open_stops():  # 13: the build's change to a test file stops once; the person accepts it
            self.assertEqual([s["order"] for s in self.open_stops()], ["unrecorded_move"], p.stdout + p.stderr)
            self.xv("record", "answer", "s1", "--by", "pat", "--answer", "the build's change is accepted",
                    "--next", "maker", cwd=self.wt)
        else:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(self.FIRST_RED, open(os.path.join(self.wt, "tests", "test_store.py")).read(),
                      "the first red did not land on the slice branch")
        self.amend()
        if os.path.exists(self.cwds):  # only the second pass's checkout is read
            os.remove(self.cwds)

    def red_refs(self):
        """Each ref, other than the test's own branches, whose tip is the base with the red and without the build."""
        found = {}
        for row in sh(["git", "for-each-ref", "--format=%(refname) %(objectname)"], self.repo).stdout.splitlines():
            name, sha = row.split()
            if name in ("refs/heads/main", f"refs/heads/{BUILD}", "refs/heads/xv/s1"):
                continue
            if not self.is_ancestor(self.main, sha) or self.is_ancestor(self.build, sha):
                continue
            if sh(["git", "cat-file", "-e", f"{sha}:tests/test_red.py"], self.repo, check=False).returncode == 0:
                found[name] = sha
        return found

    def at(self, sha, rel):
        return sh(["git", "show", f"{sha}:{rel}"], self.repo).stdout

    def test_the_first_pass_keeps_its_red_on_a_ref_at_the_base(self):
        self.first_pass()
        refs = self.red_refs()
        self.assertTrue(refs, "no ref holds the red at the base, without the build")
        for name, sha in refs.items():
            self.assertIn(self.FIRST_RED, self.at(sha, "tests/test_store.py"), f"{name} does not hold the first red")

    def test_a_second_pass_starts_from_the_tip_of_the_red_ref(self):
        self.first_pass()
        tips = set(self.red_refs().values())
        self.assertTrue(tips, "no ref holds the red at the base, without the build")
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE=self.PROBE)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the second scenario pass did not start")
        self.assertIn(ran["head"], tips, "the second pass's checkout is not at the tip of the red's ref")

    def test_the_red_ref_moves_to_the_second_pass_red(self):
        self.first_pass()
        before = set(self.red_refs().values())
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        after = self.red_refs()
        moved = [sha for sha in after.values() if sha not in before
                 and "SECOND-PASS" in self.at(sha, "tests/test_red.py")
                 and self.FIRST_RED in self.at(sha, "tests/test_store.py")
                 and any(self.is_ancestor(old, sha) for old in before)]
        self.assertTrue(moved, "no red ref moved on to the second pass's red, from the first pass's tip")

    def test_a_second_pass_starts_at_the_base_when_the_red_edits_a_file_the_build_changed(self):
        self.first_pass(self.build_edits_near_the_red())
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE=self.PROBE)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the second scenario pass did not start")
        self.assertFalse(ran["exists"][MARKER], "the second pass's checkout has the build in it")
        store = ran["texts"]["tests/test_store.py"]
        self.assertIn(self.FIRST_RED, store, "the second pass's checkout does not have the earlier red")
        self.assertNotIn("# explored", store, "the second pass's checkout has the build's change to the test file")

    def test_a_second_pass_lands_without_a_conflict_when_the_red_edits_a_file_the_build_changed(self):
        self.first_pass(self.build_edits_near_the_red())
        p = self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertNotEqual(p.returncode, 1, "the step crashed: " + p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertNotIn("red_conflicts_with_build", [s["order"] for s in self.record()["stops"]])
        self.assertIn("SECOND-PASS", open(os.path.join(self.wt, "tests", "test_red.py")).read(),
                      "the second pass's red is not on the slice branch")
        store = open(os.path.join(self.wt, "tests", "test_store.py")).read()
        self.assertIn(self.FIRST_RED, store, "the slice branch lost the first red")
        self.assertIn("# explored", store, "the slice branch lost the build's change to the test file")
        self.assertTrue(os.path.exists(os.path.join(self.wt, MARKER)), "the slice branch lost the build")

    def test_a_second_pass_leaves_no_checkout_behind_when_the_red_edits_a_file_the_build_changed(self):
        self.first_pass(self.build_edits_near_the_red())
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertEqual(self.scratch_worktrees(), [], "the scenario agent's checkout was left behind")


class RedRefRebaseTest(FromBuildBase):
    # 12, as Sean settled it: xv slice rebase moves the red ref onto the new base, and stops if it cannot
    FIRST_RED = RedOnItsOwnRefTest.FIRST_RED
    PROBE = f"{MARKER} tests/test_red.py tests/test_store.py docs.txt"
    at = RedOnItsOwnRefTest.at

    def red_refs_at(self, base):
        """Each ref, other than the branches, whose tip is `base` with the red and without the build."""
        found = {}
        for row in sh(["git", "for-each-ref", "--format=%(refname) %(objectname)"], self.repo).stdout.splitlines():
            name, sha = row.split()
            if name.startswith("refs/heads/"):
                continue
            if not self.is_ancestor(base, sha) or self.is_ancestor(self.build, sha):
                continue
            if sh(["git", "cat-file", "-e", f"{sha}:tests/test_red.py"], self.repo, check=False).returncode == 0:
                found[name] = sha
        return found

    def on_main(self, rel, text):
        with open(os.path.join(self.repo, rel), "w") as f:
            f.write(text)
        sh(["git", "add", rel], self.repo)
        sh(["git", "commit", "-qm", "main moves on"], self.repo)
        return sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()

    def first_pass_then_main_moves(self, rel="docs.txt", text="news on main\n"):
        """A first pass from the build whose red adds a test to tests/test_store.py, and then main moves on."""
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        p = self.scenario_step(FAKE_RED_ADDS_TO_OLD="1")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(self.FIRST_RED, open(os.path.join(self.wt, "tests", "test_store.py")).read(),
                      "the first red did not land on the slice branch")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "leftovers", "--allow-empty"], self.wt)
        self.held = self.red_refs_at(self.main)
        self.assertTrue(self.held, "no ref holds the red at the base, without the build")
        self.new = self.on_main(rel, text)

    def rebase(self, *args):
        with mock.patch.dict(os.environ, self.env(FAKE_REBASE_MODE="clean")):
            return self.xv("slice", "rebase", "s1", *args, cwd=self.wt, check=False)

    def in_progress(self):
        return os.path.isdir(sh(["git", "rev-parse", "--path-format=absolute", "--git-path", "rebase-merge"],
                                self.wt).stdout.strip())

    def test_a_clean_rebase_moves_the_red_ref_onto_the_new_base(self):
        self.first_pass_then_main_moves()
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.record()["base"], self.new, "the rebase did not move the slice's base")
        moved = self.red_refs_at(self.new)
        for name in self.held:
            self.assertIn(name, moved, f"{name} was not moved onto the new base, with the red and without the build")
            self.assertIn(self.FIRST_RED, self.at(moved[name], "tests/test_store.py"), f"{name} lost the first red")
            self.assertIn("news on main", self.at(moved[name], "docs.txt"), f"{name} is not on the new base")

    def test_a_pass_after_the_rebase_starts_at_the_new_base_with_the_earlier_red_in_it(self):
        self.first_pass_then_main_moves()
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.amend()
        if os.path.exists(self.cwds):  # only the pass after the rebase is read
            os.remove(self.cwds)
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE=self.PROBE)
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario pass after the rebase did not start")
        self.assertFalse(ran["exists"][MARKER], "the pass after the rebase has the build in it")
        self.assertTrue(ran["exists"]["docs.txt"], "the pass after the rebase is not at the new base")
        self.assertTrue(ran["exists"]["tests/test_red.py"], "the pass after the rebase started without the earlier red")
        self.assertIn(self.FIRST_RED, ran["texts"]["tests/test_store.py"],
                      "the pass after the rebase started without the earlier red")

    def test_a_pass_after_the_rebase_lands_on_the_slice_branch_without_a_conflict(self):
        self.first_pass_then_main_moves()
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.amend()
        p = self.step("scenario", FAKE_RED_TEXT="SECOND-PASS")
        self.assertNotEqual(p.returncode, 1, "the step crashed: " + p.stdout + p.stderr)
        self.assertNotIn("red_conflicts_with_build", [s["order"] for s in self.record()["stops"]])
        self.assertIn("SECOND-PASS", open(os.path.join(self.wt, "tests", "test_red.py")).read(),
                      "the pass after the rebase did not land its red on the slice branch")
        moved = self.red_refs_at(self.new)
        self.assertTrue([sha for sha in moved.values() if "SECOND-PASS" in self.at(sha, "tests/test_red.py")
                         and self.FIRST_RED in self.at(sha, "tests/test_store.py")],
                        "no red ref on the new base moved on to the red of the pass after the rebase")

    def test_a_rebase_that_cannot_move_the_red_ref_stops_and_names_it(self):
        # main adds its own tests/test_red.py, so the red at the base cannot be moved onto it without a person
        main_red = "import unittest\n\nMAIN_RED = True\n"
        self.first_pass_then_main_moves("tests/test_red.py", main_red)
        stops = []
        p = self.rebase()
        if p.returncode == 10:
            stops.append(json.loads(p.stdout)["stop"])
        if self.in_progress():  # the slice branch's own conflict in tests/test_red.py; the person resolves it
            mine = sh(["git", "show", f"{list(self.held.values())[0]}:tests/test_red.py"], self.repo).stdout
            with open(os.path.join(self.wt, "tests", "test_red.py"), "w") as f:
                f.write(mine + "\nMAIN_RED = True\n")
            sh(["git", "add", "tests/test_red.py"], self.wt)
            p = self.rebase("--continue")
            if p.returncode == 10:
                stops.append(json.loads(p.stdout)["stop"])
        self.assertNotEqual(p.returncode, 1, "the rebase crashed: " + p.stdout + p.stderr)
        named = [s for s in stops for name in self.held
                 if name in s["question"] or name[len("refs/"):] in s["question"]]
        self.assertTrue(named, "the rebase did not stop for the red ref it could not move: "
                        + json.dumps([s.get("question") for s in stops]) + p.stdout + p.stderr)
        for s in named:
            self.assertEqual(s["seat"], "originator")
            self.assertIn(f'"{s["order"]}"', read("scripts", "orders.py"), "the stop is not decided in scripts/orders.py")
        for name, sha in self.held.items():
            now = sh(["git", "rev-parse", "--verify", "-q", name], self.repo, check=False).stdout.strip()
            self.assertTrue(now, f"the rebase dropped {name}")
            self.assertIn(self.FIRST_RED, self.at(now, "tests/test_store.py"), f"{name} lost the first red")


class BuildConflictTest(FromBuildBase):
    # 13. a red that conflicts with the build stops with red_conflicts_with_build
    def test_a_red_that_conflicts_with_the_build_stops(self):
        self.make_build(fixed=False, files={"tests/test_red.py": "# the build's own test file\nBUILD_TEST = True\n"})
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "red_conflicts_with_build")
        self.assertEqual([s["order"] for s in self.open_stops()], ["red_conflicts_with_build"])
        self.assertEqual(sh(["git", "status", "--porcelain", "--untracked-files=no"], self.wt).stdout.strip(), "",
                         "the slice worktree is left mid cherry-pick")

    # #147 point 2: the red of a conflict stop is still on its ref, and the stop says so
    def test_the_conflict_stop_says_the_red_is_kept_on_its_ref_and_a_later_pass_starts_from_it(self):
        self.make_build(fixed=False, files={"tests/test_red.py": "# the build's own test file\nBUILD_TEST = True\n"})
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        stop = json.loads(p.stdout)["stop"]
        self.assertIn("refs/xv/s1/red", stop["question"])
        held = sh(["git", "rev-parse", "--verify", "refs/xv/s1/red"], self.repo).stdout.strip()
        self.assertIn("test_milk_today", sh(["git", "show", f"{held}:tests/test_red.py"], self.repo).stdout)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "landed by hand", "--next", "scenario",
                "--settled", "the red is landed by hand under its own subject", cwd=self.wt)
        self.step("scenario", FAKE_RED_TEXT="SECOND-PASS", FAKE_CWD_PROBE="tests/test_red.py")
        ran = self.ran("# The scenario agent")
        self.assertEqual(ran["head"], held, "the later pass did not start from the red's ref")

    # 13. a test file the build changed stops once, as a change with no record
    def test_a_test_file_the_build_changed_stops_once_as_a_change_with_no_record(self):
        old = open(os.path.join(self.repo, "tests", "test_store.py")).read()
        self.make_build(fixed=False, files={"tests/test_store.py": old.replace('["yogurt"]', '["yogurt"] or []')})
        self.open_slice("--from", BUILD)
        self.step("forecaster")
        for agent, after in (("scenario", "maker"), ("maker", "cleaner"), ("cleaner", "guardian")):
            self.step(agent)
            if self.open_stops():  # the person accepts the build's change and the slice goes on
                self.xv("record", "answer", "s1", "--by", "pat", "--answer", "the build's change is accepted",
                        "--next", after, cwd=self.wt)
        named =[s for s in self.record()["stops"] if "tests/test_store.py" in s["question"]]
        self.assertEqual([s["order"] for s in named], ["unrecorded_move"],
                         "the build's change to tests/test_store.py did not stop exactly once as a change with no record")

    # 13. the same holds when the maker and the cleaner run in the session: `xv record report` + `xv orders`
    def test_a_test_file_the_build_changed_stops_once_when_the_maker_and_the_cleaner_run_in_the_session(self):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  maker: session\n  cleaner: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "maker and cleaner in the session"], self.repo)
        old = open(os.path.join(self.repo, "tests", "test_store.py")).read()
        self.make_build(fixed=False, files={"tests/test_store.py": old.replace('["yogurt"]', '["yogurt"] or []')})
        self.open_slice("--from", BUILD)
        self.scenario_step()
        fired = []
        for agent, after in (("maker", "cleaner"), ("cleaner", "guardian")):
            self.step(agent)  # stops for the session, which does the work itself
            path = os.path.join(self.wt, f"{agent}-report.json")
            with open(path, "w") as f:
                f.write("```xv-report\n" + json.dumps({"agent": agent, "status": "green", "summary": "done",
                                                      "moved_tests": []}) + "\n```\n")
            self.xv("record", "report", "s1", agent, path, cwd=self.wt)
            p = self.xv("orders", "s1", "--after", agent, cwd=self.wt, check=False)
            fired += [f for f in json.loads(p.stdout)["fired"]
                      if f["order"] == "unrecorded_move" and "tests/test_store.py" in f["question"]]
            if fired and agent == "maker":  # the person accepts the build's change and the slice goes on
                self.xv("record", "stop", "s1", "--order", "unrecorded_move", "--seat", "originator",
                        "--question", "tests/test_store.py changed with no record", "--step", agent, cwd=self.wt)
                self.xv("record", "answer", "s1", "--by", "pat", "--answer", "the build's change is accepted",
                        "--next", after, cwd=self.wt)
        self.assertEqual(len(fired), 1,
                         "the build's change to tests/test_store.py did not stop exactly once on the session path")


class RecordCopyTest(FromBuildBase):
    # 14. when the build is not shared, the scenario agent's record copy names no branch or commit at the build
    def setUp(self):
        super().setUp()
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.log = os.path.join(self.tmp, "records.log")

    def assert_names_no_build(self, copy):
        self.assertIsNotNone(copy, "the scenario agent's checkout has no copy of the record")
        self.assertNotIn(BUILD, copy)
        self.assertNotRegex(copy, r"(?<![\w.])xv/s1\b", "the copy names the slice branch, which is at the build")
        self.assertEqual(self.commits_at_the_build(copy), [], "the copy names a commit at the build")

    def test_the_first_pass_copy_names_no_branch_or_commit_at_the_build(self):
        self.scenario_step(FAKE_RECORD_LOG=self.log)
        copies = self.copies(self.log)
        self.assertEqual(len(copies), 1, "the scenario agent did not run")
        self.assert_names_no_build(copies[0])

    def test_a_second_pass_copy_names_no_branch_or_commit_at_the_build(self):
        self.scenario_step(FAKE_RECORD_LOG=self.log)
        self.amend()
        self.step("scenario", FAKE_RECORD_LOG=self.log)
        copies = self.copies(self.log)
        self.assertEqual(len(copies), 2, "the second scenario pass did not run")
        self.assert_names_no_build(copies[1])

    def test_a_second_pass_copy_after_the_maker_names_no_branch_or_commit_at_the_build(self):
        self.scenario_step(FAKE_RECORD_LOG=self.log)
        p = self.step("maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.amend()
        self.step("scenario", FAKE_RECORD_LOG=self.log)
        copies = self.copies(self.log)
        self.assertEqual(len(copies), 2, "the second scenario pass did not run")
        self.assert_names_no_build(copies[1])

    # 14, as Sean settled it: the unshared copy keeps no commit that is not an ancestor of base, for any field
    def test_a_second_pass_copy_after_a_cleaner_that_committed_names_no_commit_off_the_base(self):
        self.scenario_step(FAKE_RECORD_LOG=self.log)
        p = self.step("maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.step("cleaner", FAKE_CLEANER_COMMITS="1")
        self.assertTrue(self.record().get("cleaner_commit"), "the cleaner's commit is not in the record")
        self.amend()
        self.step("scenario", FAKE_RECORD_LOG=self.log)
        copies = self.copies(self.log)
        self.assertEqual(len(copies), 2, "the second scenario pass did not run")
        self.assertEqual(self.commits_off_the_base(copies[1]), [], "the copy names a commit that is not on the base")

    def test_no_copy_names_a_commit_off_the_base_in_any_field(self):
        head = sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()
        self.xv("record", "set", "s1", "explored_at", head, "--by", "pat", cwd=self.wt)
        self.xv("record", "set", "s1", "notes", json.dumps({"seen": [self.build[:12]]}), "--by", "pat", cwd=self.wt)
        self.scenario_step(FAKE_RECORD_LOG=self.log)
        self.amend()
        self.step("scenario", FAKE_RECORD_LOG=self.log)
        copies = self.copies(self.log)
        self.assertEqual(len(copies), 2, "the second scenario pass did not run")
        for n, copy in enumerate(copies, 1):
            self.assertIsNotNone(copy, f"pass {n}'s checkout has no copy of the record")
            self.assertEqual(self.commits_off_the_base(copy), [], f"pass {n}'s copy names a commit that is not on the base")


class SessionScenarioTest(FromBuildBase):
    # 15. with agents.scenario: session, xv step scenario makes the checkout at the base and names it
    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  scenario: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "scenario in the session"], self.repo)
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)

    def test_the_step_makes_the_checkout_at_the_base_and_names_it(self):
        p = self.scenario_step()
        self.assertNotEqual(p.returncode, 0, "the scenario step did not stop for the session")
        out = p.stdout + p.stderr
        seen = {os.path.realpath(self.repo), os.path.realpath(self.wt)}
        named = []
        for path in re.findall(r"/[^\s`'\"()]+", out):
            path = path.rstrip(".,:;")
            if os.path.isdir(path) and os.path.realpath(path) not in seen and \
                    sh(["git", "rev-parse", "--is-inside-work-tree"], path, check=False).returncode == 0:
                named.append(path)
        self.assertTrue(named, "the stop names no checkout outside the slice worktree: " + out)
        checkout = named[0]
        head = sh(["git", "rev-parse", "HEAD"], checkout).stdout.strip()
        self.assertTrue(self.is_ancestor(self.main, head), "the named checkout is not at the base")
        self.assertFalse(self.is_ancestor(self.build, head), "the named checkout is at the build")
        self.assertFalse(os.path.exists(os.path.join(checkout, MARKER)), "the named checkout has the build in it")


class SessionScenarioReportTest(FromBuildBase):
    # #147 point 1: `xv record report <id> scenario -` lands the red written in the session's checkout and drops it
    RED_TEST = ("import unittest\n\n\nclass Red(unittest.TestCase):\n    def test_milk_today(self):\n"
                "        self.assertEqual(1, 2)\n")
    REPORT = {"agent": "scenario", "status": "red", "summary": "red",
              "red": {"files": ["tests/test_red.py"], "command": "python3 -m unittest tests.test_red",
                      "failure": "1 != 2", "watch_first_green": None},
              "covers": [{"item": "milk today", "test": "test_milk_today"}], "not_covered": []}

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  scenario: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "scenario in the session"], self.repo)
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)

    def checkout_named(self, p):
        for path in re.findall(r"/[^\s`'\"()]+", p.stdout + p.stderr):
            path = path.rstrip(".,:;")
            if os.path.isdir(path) and os.path.realpath(path) not in {os.path.realpath(self.repo), os.path.realpath(self.wt)}:
                return path
        self.fail("the stop names no checkout: " + p.stdout + p.stderr)

    def write_the_red_and_report(self, checkout, test=None, report=None):
        os.makedirs(os.path.join(checkout, "tests"), exist_ok=True)
        with open(os.path.join(checkout, "tests", "test_red.py"), "w") as f:
            f.write(test or self.RED_TEST)
        path = os.path.join(self.tmp, "scenario-report.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report or self.REPORT) + "\n```\n")
        return self.xv("record", "report", "s1", "scenario", path, cwd=self.wt, check=False)

    def red_refs_of_the_slice(self):
        return sh(["git", "for-each-ref", "--format=%(refname)", "refs/xv/s1/"], self.repo).stdout.split()

    def test_the_report_lands_the_red_on_the_slice_branch(self):
        checkout = self.checkout_named(self.scenario_step())
        p = self.write_the_red_and_report(checkout)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("assertEqual(1, 2)", open(os.path.join(self.wt, "tests", "test_red.py")).read())
        self.assertEqual(sh(["git", "log", "-1", "--format=%s", "--", "tests/test_red.py"], self.wt).stdout.strip(), "xv(s1): red")
        self.assertTrue(self.is_ancestor(self.build, "HEAD", cwd=self.wt))

    def test_the_report_keeps_the_red_on_its_ref_at_the_base(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        self.assertEqual(self.red_refs_of_the_slice(), ["refs/xv/s1/red"])

    JOINED = dict(REPORT, red=dict(REPORT["red"], command="python3 -m unittest tests.test_red; true"))

    def test_a_red_joined_with_a_semicolon_is_not_kept_and_the_stop_fires(self):
        checkout = self.checkout_named(self.scenario_step())
        p = self.write_the_red_and_report(checkout, report=self.JOINED)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse((self.record().get("red") or {}).get("command"))
        self.assertIn("unittest tests.test_red; true", self.record()["checks"]["scenario"]["red_joined"])
        o = self.xv("orders", "s1", "--after", "scenario", cwd=self.wt, check=False)
        self.assertIn("scenario_stopped", o.stdout + o.stderr)

    def test_a_red_joined_unsafely_restores_the_earlier_red(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        earlier = self.record()["red"]["command"]
        checkout = self.checkout_named(self.step("scenario"))
        self.write_the_red_and_report(checkout, report=self.JOINED)
        self.assertEqual(self.record()["red"]["command"], earlier)
        self.assertTrue(self.record()["checks"]["scenario"]["red_joined"])

    def test_the_report_runs_the_red_on_the_base_and_on_the_build_and_records_the_checks(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        checks = self.record()["checks"]["scenario"]
        self.assertIs(checks["red_fails"], True)
        self.assertEqual(checks["red_on_build"]["passes"], False)

    def test_the_report_drops_the_checkout(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        self.assertFalse(os.path.exists(checkout), "the checkout is still there after the report")
        self.assertNotIn(checkout, sh(["git", "worktree", "list", "--porcelain"], self.repo).stdout)

    def test_the_report_takes_the_wall_baseline_at_the_base(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        self.assertIn("wall_baseline", self.record())
        self.assertTrue(os.path.exists(os.path.join(self.wt, ".xv", "slices", "s1.wall.json")))

    def test_a_second_step_drops_the_checkout_nobody_reported_on(self):
        first = self.checkout_named(self.scenario_step())
        second = self.checkout_named(self.step("scenario"))
        self.assertNotEqual(first, second)
        self.assertFalse(os.path.exists(first), "the first checkout is still there after a second step")
        self.assertTrue(os.path.exists(second))
        self.xv("close", "s1", "--why", "x", cwd=self.wt, check=False)  # drops the one left


class SessionScenarioConflictTest(FromBuildBase):
    # #147 point 1: a red that does not apply to the build is reported for orders, and the checkout is dropped
    checkout_named = SessionScenarioReportTest.checkout_named
    write_the_red_and_report = SessionScenarioReportTest.write_the_red_and_report
    RED_TEST = SessionScenarioReportTest.RED_TEST
    REPORT = SessionScenarioReportTest.REPORT

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  scenario: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "scenario in the session"], self.repo)
        self.make_build(fixed=False, files={"tests/test_red.py": "# the build's own test file\nBUILD_TEST = True\n"})
        self.open_slice("--from", BUILD)

    def test_a_red_that_conflicts_with_the_build_is_reported_for_orders(self):
        checkout = self.checkout_named(self.scenario_step())
        self.write_the_red_and_report(checkout)
        out = self.xv("orders", "s1", "--after", "scenario", cwd=self.wt, check=False).stdout
        self.assertIn("red_conflicts_with_build", [f["order"] for f in json.loads(out)["fired"]])
        self.assertFalse(os.path.exists(checkout))
        dirty = [l for l in sh(["git", "status", "--porcelain", "--untracked-files=no"], self.wt).stdout.splitlines()
                 if ".xv/" not in l]
        self.assertEqual(dirty, [], "the slice worktree is left mid cherry-pick")


class CloseRedRefTest(FromBuildBase):
    # #147 comment 1: `xv close` deletes the slice's red ref
    def test_close_deletes_the_red_ref(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        refs = sh(["git", "for-each-ref", "--format=%(refname)", "refs/xv/s1/"], self.repo).stdout.split()
        self.assertEqual(refs, ["refs/xv/s1/red"], "the scenario step kept no red ref")
        self.xv("close", "s1", "--why", "as forecast", cwd=self.wt)
        left = sh(["git", "for-each-ref", "--format=%(refname)", "refs/xv/s1/"], self.repo).stdout.split()
        self.assertEqual(left, [], "close left the red ref")

    def test_close_leaves_another_slices_red_ref(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        sh(["git", "update-ref", "refs/xv/other/red", self.main], self.repo)
        self.xv("close", "s1", "--why", "as forecast", cwd=self.wt)
        self.assertTrue(sh(["git", "rev-parse", "--verify", "-q", "refs/xv/other/red"], self.repo).stdout.strip())

    def test_a_new_slice_with_the_same_id_does_not_start_from_the_closed_slices_red(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        self.xv("close", "s1", "--why", "as forecast", cwd=self.wt)
        sh(["git", "worktree", "remove", "--force", self.wt], self.repo)
        sh(["git", "branch", "-D", "xv/s1"], self.repo)
        self.open_slice("--from", BUILD)
        self.step("forecaster")
        self.step("scenario", FAKE_CWD_PROBE=f"tests/test_red.py {MARKER}")
        ran = self.ran("# The scenario agent")
        self.assertEqual(ran["head"], self.main, "the new slice's first pass did not start at the base")


class BuildRefDeletedTest(FromBuildBase):
    # #147 comment 2: a build ref deleted after the slice opens does not break `xv record report`
    def test_the_record_keeps_the_commit_the_build_was_at(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.assertEqual(self.record()["build"]["commit"], self.build)

    def maker_report(self):
        path = os.path.join(self.tmp, "maker-report.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "maker", "status": "green", "summary": "done",
                                                  "moved_tests": []}) + "\n```\n")
        return self.xv("record", "report", "s1", "maker", path, cwd=self.wt, check=False)

    def build_changes_a_test_file(self):
        old = open(os.path.join(self.repo, "tests", "test_store.py")).read()
        self.make_build(fixed=False, files={"tests/test_store.py": old.replace('["yogurt"]', '["yogurt"] or []')})

    def test_a_report_after_the_build_branch_is_deleted_saves_the_wall_check(self):
        self.build_changes_a_test_file()
        self.open_slice("--from", BUILD)
        self.scenario_step()
        sh(["git", "branch", "-D", BUILD], self.repo)
        p = self.maker_report()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("wall", self.record()["checks"]["maker"])

    def test_the_stored_commit_still_tells_the_builds_own_change_from_the_slices_after_the_branch_is_deleted(self):
        self.build_changes_a_test_file()
        self.open_slice("--from", BUILD)
        self.scenario_step()
        self.xv("record", "stop", "s1", "--order", "unrecorded_move", "--seat", "originator",
                "--question", "tests/test_store.py changed with no record", "--step", "maker", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "the build's change is accepted",
                "--next", "maker", "--settled", "the build's change to the test file is accepted", cwd=self.wt)
        sh(["git", "branch", "-D", BUILD], self.repo)
        self.maker_report()
        self.assertEqual(self.record()["checks"]["maker"]["wall"]["unrecorded"], [])

    def test_a_record_with_no_stored_commit_and_no_branch_keeps_the_file_unrecorded_and_says_why(self):
        self.build_changes_a_test_file()
        self.open_slice("--from", BUILD)
        self.scenario_step()
        path, data, body = record.load(self.wt, "s1")
        data["build"].pop("commit")  # a record from before the commit was kept
        record.save(path, data, body)
        sh(["git", "branch", "-D", BUILD], self.repo)
        p = self.maker_report()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        wall = self.record()["checks"]["maker"]["wall"]
        self.assertIn("tests/test_store.py", wall["unrecorded"])
        self.assertIn("no longer resolves", wall["note"])


class SliceSkillTest(unittest.TestCase):
    # 2. the scenario is written from what runs
    def test_the_skill_writes_the_scenario_from_what_runs_when_there_is_a_build(self):
        text = read("skills", "xv-slice", "SKILL.md")
        self.assertIn("--from", text)
        self.assertRegex(text, r"(?is)build is running.{0,400}what runs|what runs.{0,400}build is running")

    def test_the_skill_does_not_ask_about_a_build_otherwise(self):
        self.assertRegex(read("skills", "xv-slice", "SKILL.md"),
                         r"(?is)(?:not|never) ask (?:about|for|whether|if)[^.]{0,40}build")

    # 3. the offer of two ways to build to find out
    def offer(self):
        text = read("skills", "xv-slice", "SKILL.md")
        for para in text.split("\n\n"):
            if re.search(r"(?i)exploration", para) and re.search(r"(?i)prototype", para):
                return para
        raise AssertionError("no paragraph of the xv-slice skill offers a prototype slice and an exploration")

    def test_the_offer_names_when_the_scenario_will_not_settle(self):
        para = self.offer().lower()
        self.assertRegex(para, r"not clear")
        self.assertRegex(para, r"round")
        self.assertRegex(para, r"wonder")

    def test_an_exploration_opens_no_slice_and_builds_with_an_agent(self):
        para = self.offer()
        self.assertRegex(para, r"(?i)opens? no slice|no slice is opened|does not open a slice")
        self.assertRegex(para, r"(?i)with an agent")

    def test_the_slice_opens_from_what_runs_with_from(self):
        para = self.offer()
        self.assertIn("xv slice new --from <ref>", para)
        self.assertRegex(para, r"(?i)what runs")

    def test_the_watch_may_make_the_offer_at_a_stop_after_the_scenario_step(self):
        text = read("skills", "watch", "SKILL.md")
        self.assertRegex(text, r"(?is)exploration.{0,600}after the scenario step|after the scenario step.{0,600}exploration")
        self.assertRegex(text, r"(?is)exploration.{0,600}before the maker|before the maker.{0,600}exploration")


RED_TEXT = ("import unittest\nfrom datetime import date\nfrom pantry.store import Store\n\n\n"
            "class Red(unittest.TestCase):\n    def test_milk_today(self):\n        s = Store()\n"
            "        s.add('milk', 1, date(2026, 10, 21))\n"
            "        self.assertEqual([i.name for i in s.expiring(3, date(2026, 10, 21))], ['milk'])\n")
RED_COMMAND = "python3 -m unittest tests.test_red"
JOINED = ["python3 -m unittest tests.test_red; echo done", "python3 -m unittest tests.test_red || true",
          "python3 -m unittest tests.test_red | cat", "python3 -m unittest tests.test_red & wait",
          "python3 -m unittest tests.test_red\npython3 -m unittest tests.test_red"]


class SessionBase(FromBuildBase):
    """The scenario agent in the person's session: `xv record report s1 scenario` and `xv orders` do the step's work."""

    with_build = True

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  scenario: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "scenario in the session"], self.repo)
        if self.with_build:
            self.make_build(fixed=False)
            self.open_slice("--from", BUILD)
        else:
            self.open_slice()
        self.step("forecaster")

    def checkout(self):
        """Run `xv step scenario` and return the checkout it names; the slice worktree when it names none."""
        p = self.step("scenario")
        self.assertNotEqual(p.returncode, 0, "the scenario step did not stop for the session")
        seen = {os.path.realpath(self.repo), os.path.realpath(self.wt)}
        for path in re.findall(r"/[^\s`'\"()]+", p.stdout + p.stderr):
            path = path.rstrip(".,:;")
            if os.path.isdir(path) and os.path.realpath(path) not in seen and \
                    sh(["git", "rev-parse", "--is-inside-work-tree"], path, check=False).returncode == 0:
                return path
        return self.wt

    def send(self, where, command=RED_COMMAND, write=True, **extra):
        """Write the red in `where`, and give the report on stdin as `xv record report s1 scenario -` does."""
        if write:
            with open(os.path.join(where, "tests", "test_red.py"), "w") as f:
                f.write(RED_TEXT)
        report = {"agent": "scenario", "status": "red", "summary": "red",
                  "red": {"files": ["tests/test_red.py"], "command": command, "failure": "Lists differ",
                          "watch_first_green": None},
                  "covers": [{"item": "milk today", "test": "test_milk_today"}], "not_covered": []}
        report.update(extra)
        text = "```xv-report\n" + json.dumps(report) + "\n```\n"
        return self.xv_stdin(text)

    def xv_stdin(self, text):
        return subprocess.run([sys.executable, os.path.join(HOME, "bin", "xv"), "record", "report", "s1", "scenario", "-"],
                              cwd=self.wt, input=text, capture_output=True, text=True)

    def orders_after(self, agent="scenario"):
        p = self.xv("orders", "s1", "--after", agent, cwd=self.wt, check=False)
        return json.loads(p.stdout)

    def fired(self, agent="scenario"):
        return [f["order"] for f in self.orders_after(agent)["fired"]]

    def head_file(self, rel):
        p = sh(["git", "show", f"HEAD:{rel}"], self.wt, check=False)
        return p.stdout if p.returncode == 0 else None


class SessionLandsTheRedTest(SessionBase):
    # 1. a slice from a build, in session mode: `xv record report <id> scenario -` does the step's landing
    def test_the_report_lands_the_red_on_the_slice_branch(self):
        where = self.checkout()
        self.assertNotEqual(os.path.realpath(where), os.path.realpath(self.wt), "the step named no checkout")
        p = self.send(where)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("def test_milk_today", self.head_file("tests/test_red.py") or "",
                      "the red is not committed on the slice branch")

    def test_the_report_runs_the_red_at_the_base_and_on_the_build(self):
        self.send(self.checkout())
        scenario = self.record()["checks"].get("scenario") or {}
        self.assertIs(scenario.get("red_fails"), True, f"the red was not run at the base: {scenario}")
        self.assertEqual((scenario.get("red_on_build") or {}).get("passes"), False,
                         f"the red was not run on the build: {scenario}")

    def test_the_report_takes_the_wall_baseline_at_the_base(self):
        self.send(self.checkout())
        baseline = self.record().get("wall_baseline")
        self.assertTrue(baseline, "no wall baseline was taken")
        self.assertEqual(baseline["commit"], self.main, "the wall baseline was not taken at the base")

    def test_the_report_keeps_the_red_on_its_ref_and_orders_find_no_stop_for_a_good_red(self):
        self.send(self.checkout())
        self.assertEqual(sh(["git", "rev-parse", "--verify", "-q", "refs/xv/s1/red^{commit}"], self.repo,
                            check=False).returncode, 0, "no red ref")
        out = self.orders_after()
        self.assertIsNone(out["stop"], out)

    def test_orders_after_the_report_give_the_same_stop_as_the_cli_path_for_a_point_left_uncovered(self):
        self.send(self.checkout(), not_covered=[{"item": "milk tomorrow", "why": "no seam"}])
        self.assertIn("red_misses_scenario", self.fired(),
                      "the saved scenario checks did not reach `xv orders --after scenario`")

    def test_the_checkout_is_dropped_by_the_next_scenario_step(self):
        first = self.checkout()
        self.assertTrue(os.path.isdir(first))
        self.send(first)
        second = self.checkout()
        self.assertFalse(os.path.exists(first), "the first scenario checkout is still there after the next step")
        self.assertNotEqual(first, second)

    def test_the_checkout_is_dropped_by_close(self):
        first = self.checkout()
        self.send(first)
        self.assertIsNone(self.orders_after()["stop"])
        self.xv("close", "s1", "--why", "as forecast", cwd=self.wt)
        self.assertFalse(os.path.exists(first), "the scenario checkout is still there after close")


class SessionJoinedRedTest(SessionBase):
    # 5. a red joined with ;, ||, |, & or a newline is not kept in session mode
    def check_refused(self, where_for):
        self.send(where_for())
        self.assertEqual(self.record()["red"]["command"], RED_COMMAND)
        for command in JOINED:
            with self.subTest(command=command):
                self.send(where_for(), command=command)
                self.assertEqual(self.record()["red"]["command"], RED_COMMAND, "a joined red command was kept")
                self.assertIn("scenario_stopped", self.fired())

    def test_with_a_build_the_earlier_red_stays_and_scenario_stopped_fires(self):
        first = self.checkout()
        self.send(first)
        self.check_refused(lambda: self.checkout())


class SessionJoinedRedNoBuildTest(SessionBase):
    with_build = False

    def test_with_no_build_the_earlier_red_stays_and_scenario_stopped_fires(self):
        self.send(self.wt)
        self.assertEqual(self.record()["red"]["command"], RED_COMMAND)
        for command in JOINED:
            with self.subTest(command=command):
                self.send(self.wt, command=command, write=False)
                self.assertEqual(self.record()["red"]["command"], RED_COMMAND, "a joined red command was kept")
                self.assertIn("scenario_stopped", self.fired())


class RedRefOnConflictTest(FromBuildBase):
    CLASH = {"tests/test_red.py": "# the build's own test file\nBUILD_TEST = True\n"}
    REF = "refs/xv/s1/red"

    def conflicted(self):
        self.make_build(fixed=False, files=self.CLASH)
        self.open_slice("--from", BUILD)
        return self.scenario_step()

    def ref_tip(self):
        p = sh(["git", "rev-parse", "--verify", "-q", self.REF + "^{commit}"], self.repo, check=False)
        return p.stdout.strip() if p.returncode == 0 else None

    # 2. a red that conflicts with the build stays on its ref
    def test_a_red_that_conflicts_with_the_build_stays_on_the_red_ref(self):
        self.conflicted()
        tip = self.ref_tip()
        self.assertTrue(tip, "the conflicting red is not on refs/xv/s1/red")
        self.assertIn("def test_milk_today", sh(["git", "show", f"{tip}:tests/test_red.py"], self.repo).stdout)
        self.assertFalse(self.is_ancestor(self.build, tip), "the red ref holds the build")

    def test_the_question_says_the_red_is_on_the_ref(self):
        p = self.conflicted()
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "red_conflicts_with_build")
        self.assertIn(self.REF, stop["question"])

    def test_the_next_scenario_pass_starts_from_that_red(self):
        self.conflicted()
        tip = self.ref_tip()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "run it again", "--next", "scenario",
                "--settled", "the red stays on its ref; the next pass starts from it", cwd=self.wt)
        os.remove(self.cwds)
        self.step("scenario", FAKE_CWD_PROBE="tests/test_red.py")
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the next scenario pass did not start")
        self.assertEqual(ran["head"], tip, "the next pass did not start from the red on the ref")


class CloseDropsTheRedRefTest(FromBuildBase):
    # 3. `xv close` deletes refs/xv/<id>/red
    def test_close_deletes_the_red_ref(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.scenario_step()
        held = lambda: sh(["git", "rev-parse", "--verify", "-q", "refs/xv/s1/red^{commit}"], self.repo,
                          check=False).returncode == 0
        self.assertTrue(held(), "the scenario step kept no red ref")
        self.xv("close", "s1", "--why", "as forecast", cwd=self.wt)
        self.assertFalse(held(), "refs/xv/s1/red is still there after close")


class BuildCommitTest(FromBuildBase):
    def build_with_a_test_file(self):
        old = open(os.path.join(self.repo, "tests", "test_store.py")).read()
        self.make_build(fixed=False, files={"tests/test_store.py": old.replace('["yogurt"]', '["yogurt"] or []')})
        self.open_slice("--from", BUILD)
        self.step("forecaster")
        self.step("scenario")
        if self.open_stops():  # the person accepts the build's change
            self.xv("record", "answer", "s1", "--by", "pat", "--answer", "the build's change is accepted",
                    "--next", "maker", cwd=self.wt)

    def maker_report(self):
        path = os.path.join(self.tmp, "maker.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "maker", "status": "green", "summary": "done",
                                                  "moved_tests": []}) + "\n```\n")
        return self.xv("record", "report", "s1", "maker", path, cwd=self.wt, check=False)

    def unrecorded(self):
        return (self.record()["checks"].get("maker", {}).get("wall") or {}).get("unrecorded") or []

    # 4. `xv slice new --from` keeps the build's commit
    def test_the_record_keeps_the_commit_of_the_build(self):
        self.make_build(fixed=False)
        self.open_slice("--from", BUILD)
        self.assertEqual(self.record()["build"].get("commit"), self.build)

    def test_a_deleted_build_ref_does_not_crash_the_report_and_the_accepted_file_stays_accepted(self):
        self.build_with_a_test_file()
        sh(["git", "branch", "-D", BUILD], self.repo)
        p = self.maker_report()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("tests/test_store.py", self.unrecorded())

    def test_with_no_build_commit_at_all_the_builds_test_file_stays_unrecorded_and_stops(self):
        self.build_with_a_test_file()
        self.xv("record", "set", "s1", "build", json.dumps({"kind": "exploration", "ref": BUILD}),
                "--by", "pat", cwd=self.wt)
        sh(["git", "branch", "-D", BUILD], self.repo)
        p = self.maker_report()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("tests/test_store.py", self.unrecorded())
        fired = [f["order"] for f in json.loads(self.xv("orders", "s1", "--after", "maker", cwd=self.wt,
                                                        check=False).stdout)["fired"]]
        self.assertIn("unrecorded_move", fired)


if __name__ == "__main__":
    unittest.main()


# What a person should watch on the first green run: build something with an agent on
# a branch, then run `xv slice new <id> --from <branch>` and `xv run <id>`. See the
# scenario agent write its red in a checkout without the build, see the red fail on the
# base, and see where the slice goes: to the cleaner with no maker when the build already
# passes, or to the maker, starting from the build, with the failing tests named as misses.
# Then let main move on and run `xv slice rebase <id>`: see the red's own ref
# (`git for-each-ref refs/xv`) move onto the new base with the red in it and no build, and
# see the next scenario pass start from it. Give main a test file that clashes with the
# red and see the rebase stop and name that ref, rather than leave it on the old base.


class SessionScenarioNoBuildJoinedTest(RepoCase):
    """A slice not from a build: a joined red is kept out and `xv record report` sets red_joined itself."""

    def report(self, command):
        r = {"agent": "scenario", "status": "red", "summary": "red",
             "red": {"files": ["tests/test_red.py"], "command": command, "failure": "x", "watch_first_green": None},
             "covers": [], "not_covered": []}
        path = os.path.join(self.tmp, "report.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(r) + "\n```\n")
        return path

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice()
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def test_a_joined_red_sets_red_joined_and_the_stop_fires(self):
        self.xv("record", "report", "s1", "scenario", self.report("python3 -m unittest a; true"), cwd=self.wt)
        data = self.record()
        self.assertFalse((data.get("red") or {}).get("command"))
        self.assertIn("unittest a; true", data["checks"]["scenario"]["red_joined"])
        o = self.xv("orders", "s1", "--after", "scenario", cwd=self.wt, check=False)
        self.assertIn("scenario_stopped", o.stdout + o.stderr)

    def test_a_red_joined_with_and_and_is_kept_and_sets_no_red_joined(self):
        self.xv("record", "report", "s1", "scenario", self.report("python3 -m unittest a && python3 -m unittest b"), cwd=self.wt)
        data = self.record()
        self.assertFalse(((data.get("checks") or {}).get("scenario") or {}).get("red_joined"))

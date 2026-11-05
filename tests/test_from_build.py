import json
import os
import re
import sys
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh

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

    def make_build(self, fixed):
        """An exploration built on a branch of its own: a marker file, and the fix when `fixed`."""
        sh(["git", "checkout", "-q", "-b", BUILD], self.repo)
        with open(os.path.join(self.repo, MARKER), "w") as f:
            f.write("EXPLORED = True\n")
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


class ChangelogTest(unittest.TestCase):
    # 10. Slice-only: one CHANGELOG line
    def test_unreleased_has_a_line_for_113_naming_each_brief_it_changes(self):
        unreleased = read("CHANGELOG.md").split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        lines = [ln for ln in unreleased.splitlines() if "#113" in ln]
        self.assertTrue(lines, "no Unreleased line names #113")
        text = " ".join(lines)
        self.assertIn("xv-slice", text)
        self.assertIn("watch", text)
        self.assertIn("scenario", text)
        self.assertIn("--from", text)


if __name__ == "__main__":
    unittest.main()


# What a person should watch on the first green run: build something with an agent on
# a branch, then run `xv slice new <id> --from <branch>` and `xv run <id>`. See the
# scenario agent write its red in a checkout without the build, see the red fail on the
# base, and see where the slice goes: to the cleaner with no maker when the build already
# passes, or to the maker, starting from the build, with the failing tests named as misses.

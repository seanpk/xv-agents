"""#117, the kept-pick half: the people may keep a prototype pick as the build its slice starts from. The slice
then runs as one opened with `xv slice new --from`: the red is written blind at the base, and runs on the pick."""

import json
import os
import sys
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh
import orders
from xvlib import DEFAULT_CONFIG

FAKE = os.path.join(HOME, "tests", "fake_agent.py")
SCENARIO = "The household sees milk that expires today in the expiring list."
KEPT = "pantry/proto_b.py"


class KeptPickBase(RepoCase):
    """A prototype slice with three variants built, each leaving code of its own; it holds no test."""

    PROTO_ENV = {"FAKE_PROTO_BUILDS": "1"}

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        self.main = sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        out = self.xv("slice", "new", "p1", "--by", "pat", "--kind", "prototype", "--axis",
                      "what the household acts on when it marks food used",
                      "--scenario", "Marking food used after a meal is quicker.").stdout
        self.wt = out.strip().splitlines()[-1]
        self.xv("record", "set", "p1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)
        self.prompts = os.path.join(self.tmp, "prompts.log")
        self.cwds = os.path.join(self.tmp, "cwds.log")
        self.copies = os.path.join(self.tmp, "records.log")
        with mock.patch.dict(os.environ, self.PROTO_ENV):
            p = self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.restated = os.path.join(self.tmp, "restated.md")
        with open(self.restated, "w") as f:
            f.write(SCENARIO)

    def pick(self, *flags, variant="b", check=False):
        return self.xv("prototype", "pick", "p1", "--variant", variant, "--by", "pat,sam",
                       "--scenario-file", self.restated, *flags, cwd=self.wt, check=check)

    def record(self):
        return json.loads(self.xv("record", "show", "p1", "--json", cwd=self.wt).stdout)

    def branches(self):
        out = sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout
        return sorted(out.split())

    def is_ancestor(self, older, newer, cwd=None):
        return sh(["git", "merge-base", "--is-ancestor", older, newer], cwd or self.repo, check=False).returncode == 0

    def env(self, **more):
        e = {"FAKE_PROMPT_LOG": self.prompts, "FAKE_CWD_LOG": self.cwds, "FAKE_RECORD_LOG": self.copies,
             "FAKE_CWD_PROBE": f"{KEPT} tests/test_red.py"}
        e.update(more)
        return e

    def step(self, agent, **more):
        with mock.patch.dict(os.environ, self.env(**more)):
            return self.xv("step", agent, "p1", cwd=self.wt, check=False)

    def scenario_step(self, **more):
        p = self.step("forecaster")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return self.step("scenario", **more)

    def ran(self, title):
        if not os.path.exists(self.cwds):
            return None
        rows = [json.loads(line) for line in open(self.cwds) if line.strip()]
        rows = [r for r in rows if r["title"].startswith(title)]
        return rows[-1] if rows else None

    def prompt_of(self, title):
        if not os.path.exists(self.prompts):
            return ""
        found = [p for p in open(self.prompts).read().split("\n=====\n") if p.startswith(title)]
        return found[-1] if found else ""

    def copy_of(self, title):
        if not os.path.exists(self.copies):
            return None
        rows = [json.loads(line) for line in open(self.copies) if line.strip()]
        rows = [r["record"] for r in rows if r["title"].startswith(title)]
        return rows[-1] if rows else None


class KeepThePickTest(KeptPickBase):
    def test_a_kept_pick_is_recorded_as_the_build_with_its_branch_and_commit(self):
        p = self.pick("--keep")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        build = data["build"]
        self.assertEqual((build["kind"], build["ref"], build["variant"]), ("kept_pick", "xv/p1-proto-b", "b"))
        self.assertEqual(data["build_shared"], "no")
        self.assertEqual(sh(["git", "rev-parse", "xv/p1-proto-b"], self.repo).stdout.strip(), build["commit"])
        self.assertEqual((data["kind"], data["next"]), ("feature", "forecaster"))

    def test_the_kept_branch_stays_and_the_other_two_are_discarded(self):
        self.pick("--keep", check=True)
        self.assertEqual(self.branches(), ["xv/p1-proto-b"])
        for n in "abc":
            self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", f"p1-proto-{n}")),
                             f"prototype {n}'s worktree, its context, is still there")

    def test_the_slice_branch_has_the_kept_build_and_not_the_others(self):
        self.pick("--keep", check=True)
        build = self.record()["build"]["commit"]
        self.assertTrue(self.is_ancestor(build, "HEAD", cwd=self.wt), "the slice branch does not have the build")
        self.assertTrue(os.path.exists(os.path.join(self.wt, KEPT)))
        for n in "ac":
            self.assertFalse(os.path.exists(os.path.join(self.wt, "pantry", f"proto_{n}.py")))
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "", "the pick left the tree dirty")

    def test_the_base_stays_the_branch_the_slice_merges_into(self):
        self.pick("--keep", check=True)
        base = self.record()["base"]
        self.assertEqual(sh(["git", "rev-parse", f"{base}^{{commit}}"], self.repo).stdout.strip(), self.main)

    def test_the_decision_and_the_log_say_the_pick_was_kept(self):
        self.pick("--keep", check=True)
        data = self.record()
        self.assertIn("kept as the build", data["decisions"][-1]["decision"])
        body = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        self.assertIn("picked b, kept as the build", body.split("## Log")[1])
        self.assertTrue(next(p for p in data["prototypes"] if p["name"] == "b").get("kept"))

    def test_keep_with_none_is_refused(self):
        p = self.xv("prototype", "pick", "p1", "--variant", "none", "--by", "pat,sam", "--keep", cwd=self.wt,
                    check=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("none has no branch", p.stderr)
        self.assertEqual(self.record()["kind"], "prototype")

    def test_share_build_without_keep_is_refused(self):
        p = self.pick("--share-build")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertRegex(p.stderr, r"--share-build needs --keep")
        self.assertEqual(self.record()["kind"], "prototype")
        self.assertEqual(len(self.branches()), 3, "a refused pick discards nothing")

    def test_a_kept_pick_whose_branch_holds_nothing_is_refused_and_changes_nothing(self):
        wt = os.path.join(self.repo, ".xv", "worktrees", "p1-proto-b")
        sh(["git", "worktree", "remove", "--force", wt], self.repo)  # its work was never committed
        p = self.pick("--keep")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("no build to keep", p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        data = self.record()
        self.assertEqual((data["kind"], data["build"]), ("prototype", "none"))
        self.assertEqual(len(self.branches()), 3)


class PrototypeCommitsItsOwnWorkTest(KeptPickBase):
    PROTO_ENV = {"FAKE_PROTO_BUILDS": "1", "FAKE_PROTO_COMMITS": "b"}

    def test_work_the_prototype_committed_itself_is_kept_too(self):
        self.pick("--keep", check=True)
        self.assertTrue(os.path.exists(os.path.join(self.wt, KEPT)))
        log = sh(["git", "log", "--format=%s", "HEAD"], self.wt).stdout
        self.assertIn("prototype b, its own commit", log)


class PrototypeBendsTheLayerTest(KeptPickBase):
    PROTO_ENV = {"FAKE_PROTO_BUILDS": "1", "FAKE_PROTO_EDITS_LAYER": "b"}

    def test_the_project_layer_stays_as_the_slice_has_it(self):
        before = open(os.path.join(self.wt, ".xv", "picture.md")).read()
        self.pick("--keep", check=True)
        self.assertEqual(open(os.path.join(self.wt, ".xv", "picture.md")).read(), before,
                         "a kept pick brought the prototype's edit to the picture")
        self.assertTrue(os.path.exists(os.path.join(self.wt, KEPT)), "the code still came")
        self.assertTrue(os.path.exists(os.path.join(self.wt, ".xv", "prototypes", "p1", "b", "recording.md")))


    def test_the_log_names_each_project_file_the_build_brought_and_was_dropped(self):
        self.pick("--keep", check=True)
        log = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        self.assertRegex(log, r"(?m)^.*\.xv/picture\.md.*$")
        self.assertRegex(log, r"(?i)dropp")
        self.assertNotIn(".xv/prototypes/p1/b/recording.md", log.split("## Log", 1)[-1].split("dropp", 1)[-1])


class KeptPickLogNamesTheCommitTest(KeptPickBase):
    PROTO_ENV = {"FAKE_PROTO_BUILDS": "1", "FAKE_PROTO_EDITS_LAYER": "b"}

    def test_the_log_line_names_the_build_commit_the_dropped_content_lives_in(self):
        self.pick("--keep", check=True)
        commit = self.record()["build"]["commit"]
        log = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        line = [l for l in log.splitlines() if "dropp" in l.lower()][0]
        self.assertIn(commit[:7], line)
        shown = sh(["git", "show", f"{commit[:7]}:.xv/picture.md"], self.repo).stdout
        self.assertIn("A line prototype b wrote into the picture.", shown)


class SliceMovedOnBeforeTheKeptPickTest(KeptPickBase):
    """Guard: the prototype branch is behind the slice branch on `.xv/`. The merge compares with the merge-base, so
    a file only the slice branch changed is neither dropped nor named."""

    def test_a_project_file_only_the_slice_branch_changed_is_kept_and_not_named(self):
        with open(os.path.join(self.wt, ".xv", "moved.md"), "w") as f:
            f.write("people wrote this after the prototypes started\n")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "people moved on"], self.wt)
        self.pick("--keep", check=True)
        self.assertTrue(os.path.exists(os.path.join(self.wt, ".xv", "moved.md")))
        log = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        self.assertNotIn("moved.md", log)


class PickNoneGuardTest(KeptPickBase):
    def test_a_pick_of_none_stays_a_prototype_slice_and_start_still_runs_on_it(self):
        p = self.xv("prototype", "pick", "p1", "--variant", "none", "--by", "pat,sam", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.record()["kind"], "prototype")
        with mock.patch.dict(os.environ, self.PROTO_ENV):
            q = self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertNotRegex(q.stdout + q.stderr, r"(?i)no longer a prototype slice")
        self.assertEqual(q.returncode, 10, q.stdout + q.stderr)
        self.assertIn("prototypes_ready", q.stdout)
        self.assertEqual(self.record()["kind"], "prototype")


class AfterTheKeptPickTest(KeptPickBase):
    def test_a_second_prototype_start_is_refused_and_the_kept_branch_stays(self):
        self.pick("--keep", check=True)
        before = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        head = sh(["git", "rev-parse", "HEAD"], self.wt).stdout
        p = self.xv("prototype", "start", "p1", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertRegex(p.stdout + p.stderr, r"(?i)no longer a prototype slice")
        self.assertEqual(self.branches(), ["xv/p1-proto-b"], "the kept branch was deleted or others came back")
        self.assertEqual(open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read(), before)
        self.assertEqual(sh(["git", "rev-parse", "HEAD"], self.wt).stdout, head)


class RedOnTheKeptPickTest(KeptPickBase):
    def test_the_scenario_agent_runs_at_the_base_without_the_kept_build(self):
        self.pick("--keep", check=True)
        self.scenario_step()
        ran = self.ran("# The scenario agent")
        self.assertIsNotNone(ran, "the scenario agent did not run")
        self.assertFalse(ran["exists"][KEPT], "the scenario agent's checkout has the kept build in it")
        self.assertTrue(self.is_ancestor(self.main, ran["head"]))
        self.assertFalse(self.is_ancestor(self.record()["build"]["commit"], ran["head"]))

    def test_the_scenario_agent_is_not_told_where_the_kept_build_is(self):
        self.pick("--keep", check=True)
        self.scenario_step()
        prompt = self.prompt_of("# The scenario agent")
        self.assertTrue(prompt, "the scenario agent did not run")
        self.assertNotIn("proto-b", prompt)
        copy = self.copy_of("# The scenario agent")
        self.assertIsNotNone(copy, "the scenario agent had no record copy")
        self.assertNotIn("proto-b", copy, "the record copy names the kept branch")
        self.assertNotIn("kept_pick", copy)
        self.assertNotIn(self.record()["build"]["commit"][:7], copy)

    def test_a_shared_kept_pick_is_named_to_the_scenario_agent_as_a_reference_only(self):
        self.pick("--keep", "--share-build", check=True)
        self.scenario_step()
        prompt = self.prompt_of("# The scenario agent")
        self.assertIn("xv/p1-proto-b", prompt)
        self.assertRegex(prompt, r"(?i)reference only")

    def test_a_red_that_fails_on_the_kept_build_goes_to_the_maker_with_no_stop(self):
        self.pick("--keep", check=True)
        p = self.scenario_step()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertIs(data["checks"]["scenario"].get("red_fails"), True, "the red did not fail on the base")
        self.assertIs(data["checks"]["scenario"]["red_on_build"]["passes"], False)
        self.assertEqual(data["next"], "maker")
        self.assertTrue(os.path.exists(os.path.join(self.wt, "tests", "test_red.py")),
                        "the red is not on the slice branch")
        self.assertTrue(os.path.exists(os.path.join(self.wt, KEPT)), "the slice branch lost the build")

    def test_the_maker_works_from_the_kept_build_in_a_new_context(self):
        self.pick("--keep", check=True)
        self.scenario_step()
        p = self.step("maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        ran = self.ran("# The maker")
        self.assertIsNotNone(ran, "the maker did not run")
        self.assertTrue(ran["exists"][KEPT], "the maker's checkout does not have the kept build")
        self.assertTrue(ran["exists"]["tests/test_red.py"])
        self.assertNotIn("prototype_context_reused", [s["order"] for s in self.record()["stops"]])


class BudgetStopListsUnfinishedTest(unittest.TestCase):
    def test_the_budget_stop_names_each_variant_that_did_not_finish_and_its_error(self):
        data = {"id": "p1", "kind": "prototype", "stops": [],
                "prototypes": [{"name": "a", "branch": "xv/p1-proto-a", "error": None},
                               {"name": "b", "branch": "xv/p1-proto-b", "error": None},
                               {"name": "c", "branch": None, "error": "fatal: Unable to create index.lock"}],
                "prototype_budgets": {n: {"usd": 1} for n in "abc"},
                "checks": {"prototype": {"prototypes_ready": 1, "ran_out": {"b": "$1.10"}, "ran_during": ["b"]}}}
        fired = [f for f in orders.evaluate(data, "prototype", DEFAULT_CONFIG) if f["order"] == "prototype_budget_spent"]
        self.assertEqual(len(fired), 1)
        self.assertIn("Variant c did not finish: fatal: Unable to create index.lock", fired[0]["question"])
        self.assertNotIn("Variant a did not finish", fired[0]["question"])


class PickStopWordsTest(unittest.TestCase):
    def record(self, prototypes):
        return {"id": "p1", "kind": "prototype", "stops": [], "prototypes": prototypes,
                "prototype_budgets": {n: {"usd": 1} for n in "abc"},
                "checks": {"prototype": {"prototypes_ready": 2, "ran_out": {}, "ran_during": []}}}

    def stop(self, prototypes):
        fired = [f for f in orders.evaluate(self.record(prototypes), "prototype", DEFAULT_CONFIG)
                 if f["order"] == "prototypes_ready"]
        self.assertEqual(len(fired), 1)
        return fired[0]["question"]

    def test_the_pick_stop_says_the_pick_may_be_kept_as_the_build(self):
        q = self.stop([{"name": n, "branch": f"xv/p1-proto-{n}", "error": None} for n in "abc"])
        self.assertIn("--keep", q)
        self.assertRegex(q, r"(?i)thrown away, or kept as the build")

    def test_the_pick_stop_names_each_variant_that_did_not_finish_and_its_error(self):
        q = self.stop([{"name": "a", "branch": "xv/p1-proto-a", "error": None},
                       {"name": "b", "branch": None, "error": "fatal: Unable to create '.git/index.lock'"},
                       {"name": "c", "branch": "xv/p1-proto-c", "error": "the working folder is gone: /x/p1-proto-c"}])
        self.assertIn("Variant b did not finish: fatal: Unable to create '.git/index.lock'", q)
        self.assertIn("Variant c did not finish: the working folder is gone: /x/p1-proto-c", q)
        self.assertNotIn("Variant a did not finish", q)
        self.assertIn("runs them again", q)

    def test_the_pick_stop_names_no_failure_when_all_finished(self):
        q = self.stop([{"name": n, "branch": f"xv/p1-proto-{n}"} for n in "abc"])
        self.assertNotIn("did not finish", q)


if __name__ == "__main__":
    unittest.main()

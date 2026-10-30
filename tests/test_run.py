import json
import os
import sys
import unittest

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")


class FailingTestsTest(unittest.TestCase):
    def test_names_from_unittest_pytest_and_go(self):
        from run import failing_tests
        out = ("FAIL: test_milk (tests.test_red.Red.test_milk)\nERROR: test_api (tests.t.A.test_api)\n"
               "FAILED tests/test_x.py::test_y - assert 1 == 2\n--- FAIL: TestZ (0.00s)\n")
        self.assertEqual(failing_tests(out), ["TestZ", "test_api (tests.t.A.test_api)",
                                              "test_milk (tests.test_red.Red.test_milk)", "tests/test_x.py::test_y"])

    def test_names_from_rspec_and_jasmine(self):
        from run import failing_tests
        rspec = "rspec ./spec/models/project_spec.rb:42 # Project does a thing\n"
        jasmine = ("Failures:\n1) Clipboard pastes a copied item\n  Message:\n    Expected 1 to be 2.\n"
                   "2) Clipboard clears\n  Message:\n    boom\n\n1) not a failure\n2 specs, 2 failures\n")
        self.assertEqual(failing_tests(rspec), ["./spec/models/project_spec.rb:42"])
        self.assertEqual(failing_tests(jasmine), ["Clipboard clears", "Clipboard pastes a copied item"])

    def test_names_from_vitest_minitest_mocha_cargo_and_playwright(self):
        from run import failing_tests
        vitest = (" ❯ src/clip.test.ts (2 tests | 1 failed) 6ms\n   × Clipboard > pastes a copied item 3ms\n"
                  "   ✓ Clipboard > copies 1ms\n\n⎯⎯ Failed Tests 1 ⎯⎯\n\n"
                  " FAIL  src/clip.test.ts > Clipboard > pastes a copied item\nAssertionError: expected 1 to be 2\n")
        minitest = ("Failure:\nProjectTest#test_does_a_thing [test/models/project_test.rb:42]:\nExpected false\n\n"
                    "  1) Error:\nApi::ItemsTest#test_lists:\nNameError: boom\n")
        mocha = ("  Array\n    #indexOf()\n      1) should return -1\n      ✔ finds 0\n\n  1 passing (5ms)\n"
                 "  1 failing\n\n  1) Array\n       #indexOf()\n         should return -1:\n"
                 "     AssertionError: expected 0 to equal -1\n")
        cargo = "test store::tests::adds ... ok\ntest store::tests::uses ... FAILED\n"
        playwright = ("  1) [chromium] › tests/pantry.spec.ts:3:5 › pantry › shows today ─────────────────\n\n"
                      "    Error: expect(received).toBe(expected)\n")
        self.assertEqual(failing_tests(vitest), ["Clipboard > pastes a copied item"])
        self.assertEqual(failing_tests(minitest), ["Api::ItemsTest#test_lists", "ProjectTest#test_does_a_thing"])
        self.assertEqual(failing_tests(mocha), ["Array #indexOf() should return -1"])
        self.assertEqual(failing_tests(cargo), ["store::tests::uses"])
        self.assertEqual(failing_tests(playwright), ["[chromium] › tests/pantry.spec.ts:3:5 › pantry › shows today"])

    def test_names_found_after_a_long_preamble(self):
        from run import failing_tests, shell
        script = "print('.' * 20000); print('rspec ./spec/a_spec.rb:1 # A'); print('1) B fails'); print('  Message:')"
        code, out = shell(f"{sys.executable} -c \"{script}\"", HOME)
        self.assertEqual(failing_tests(out), ["./spec/a_spec.rb:1", "B fails"])


class RunSuiteTest(RepoCase):
    def test_the_command_sees_the_slice_base_and_id(self):
        from run import run_suite, LAYER_SKIP
        config = {"tests": {"command": 'test "$XV_BASE" = abc123 && test "$XV_SLICE" = s9'}}
        self.assertEqual(run_suite(self.repo, config, "abc123", "s9")[0], "green")
        self.assertEqual(run_suite(self.repo, config)[0], "red")
        self.assertIn(".git", LAYER_SKIP)

    def test_the_watch_passes_them_from_the_record(self):
        wt = self.new_slice("s1")
        base = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["base"]
        self.assertTrue(base)
        from run import run_suite
        config = {"tests": {"command": "echo $XV_BASE $XV_SLICE"}}
        self.assertIn(f"{base} s1", run_suite(wt, config, base, "s1")[1])


class NestedRepoTest(RepoCase):
    def test_a_trial_that_is_its_own_repo_is_not_copied_into_the_worktree(self):
        sh(["git", "rm", "-rq", "--cached", ".xv"], self.repo)
        sh(["git", "commit", "-qm", "trial"], self.repo)
        with open(os.path.join(self.repo, ".git", "info", "exclude"), "a") as f:
            f.write("/.xv/\n")
        sh(["git", "init", "-q"], os.path.join(self.repo, ".xv"))
        wt = self.new_slice("s1")
        self.assertTrue(os.path.exists(os.path.join(wt, ".xv", "config.yml")))
        self.assertFalse(os.path.exists(os.path.join(wt, ".xv", ".git")))


class WatchLoopTest(RepoCase):
    """The whole loop with a stand-in agent: the plumbing, not the briefs."""

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start = text.index("agents:")
        end = text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def test_run_goes_from_the_forecast_to_the_merge_stop(self):
        p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stderr)
        verdict = json.loads(p.stdout)
        self.assertEqual(verdict["stop"]["order"], "ready_to_merge")
        data = self.record()
        self.assertEqual(data["wall_baseline"]["count"], 4)  # three test modules and __init__
        self.assertTrue(data["checks"]["scenario"]["red_fails"])
        self.assertEqual(data["suite"], "green")
        self.assertEqual((data["shape_change"], data["pitch_contradiction"]), ("no", "no"))
        self.assertEqual([s["step"] for s in data["spend"]], ["forecaster", "scenario", "maker", "cleaner", "guardian"])
        self.assertEqual(data["status"], "ready")
        self.assertEqual(sh(["git", "rev-list", "--count", "main"], self.repo).stdout.strip(), "2")

    def scenario_with_red(self, command):
        os.environ["FAKE_RED_COMMAND"] = command
        try:
            self.xv("step", "forecaster", "s1", cwd=self.wt)
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ["FAKE_RED_COMMAND"]

    def test_a_red_joined_with_semicolons_is_refused_and_names_the_command(self):
        command = "false ; false ; true"
        p = self.scenario_with_red(command)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "scenario_stopped")
        self.assertEqual(stop["seat"], "originator")
        self.assertIn(command, stop["question"])
        self.assertIn("&&", stop["question"])
        self.assertIsNot(self.record()["checks"]["scenario"].get("red_fails"), True)

    def test_an_old_assertion_changed_in_a_red_file_stops_before_the_maker(self):
        os.environ["FAKE_SCENARIO_EDITS_OLD"] = "1"
        try:
            p = self.scenario_with_red("false")
        finally:
            del os.environ["FAKE_SCENARIO_EDITS_OLD"]
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("tests/test_store.py", stop["question"])
        self.assertNotIn("maker", [s["step"] for s in self.record()["spend"]])

    def test_a_scenario_step_whose_old_red_check_cannot_run_stops_before_the_maker(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.xv("record", "set", "s1", "base", "", cwd=self.wt)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("base", stop["question"])
        self.assertNotIn("maker", [s["step"] for s in self.record()["spend"]])

    def test_a_red_joined_with_or_is_refused(self):
        p = self.scenario_with_red("false || true")
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "scenario_stopped")

    def test_a_red_joined_with_and_is_not_refused_and_fails_when_the_first_runner_fails(self):
        p = self.scenario_with_red("false && true")
        self.assertNotIn("scenario_stopped", p.stdout)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)

    def test_a_refused_red_is_not_kept_as_the_slice_red(self):
        before = self.record().get("red")
        p = self.scenario_with_red("false ; false ; true")
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "scenario_stopped")
        self.assertEqual(self.record().get("red"), before)

    def test_after_a_refused_red_the_next_step_is_the_scenario_not_the_maker(self):
        p = self.scenario_with_red("false ; false ; true")
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "scenario_stopped")
        self.assertIn("scenario agent", stop["question"])
        self.assertIn("rewrite", stop["question"])
        data = self.record()
        self.assertEqual(data["next"], "scenario")
        self.assertNotIn("maker", [s["step"] for s in data["spend"]])

    def test_a_red_joined_with_and_goes_on_to_the_maker(self):
        self.scenario_with_red("false && true")
        self.assertEqual(self.record()["next"], "maker")

    def amend(self, text):
        path = os.path.join(self.tmp, "amendment.md")
        with open(path, "w") as f:
            f.write(text)
        self.xv("slice", "amend", "s1", "--scenario-file", path, "--by", "pat", cwd=self.wt)

    def scenario_with_env(self, **env):
        from unittest import mock
        with mock.patch.dict(os.environ, env):
            self.xv("step", "forecaster", "s1", cwd=self.wt)
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def assert_stopped_before_the_maker(self, p, *named):
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        for n in named:
            self.assertIn(n, stop["question"])
        self.assertNotIn("maker", [s["step"] for s in self.record()["spend"]])

    def test_a_flag_in_backticks_that_no_red_file_has_stops_before_the_maker(self):
        self.amend("The list takes `--since <date>`.")
        self.assert_stopped_before_the_maker(self.scenario_with_env(), "--since")

    def test_a_flag_in_an_amendment_counts(self):
        self.amend("Also `--until <date>`.")
        self.assert_stopped_before_the_maker(self.scenario_with_env(), "--until")

    def test_an_xv_command_in_backticks_that_no_red_file_has_stops_before_the_maker(self):
        self.amend("A person runs `xv ghost <id>`.")
        self.assert_stopped_before_the_maker(self.scenario_with_env(), "xv ghost")

    def test_a_flag_a_red_file_has_goes_on_to_the_maker(self):
        self.amend("The list takes `--since <date>`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="xv list --since 2026-10-01")
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_flag_in_plain_words_does_not_stop(self):
        self.amend("The list takes a --since flag, written without backticks.")
        p = self.scenario_with_env()
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_an_item_the_report_says_it_did_not_cover_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam to start the app"}]')
        self.assert_stopped_before_the_maker(p, "the grocer share", "no seam to start the app")

    def test_a_report_with_nothing_left_uncovered_goes_on_to_the_maker(self):
        p = self.scenario_with_env(FAKE_NOT_COVERED="[]")
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_record_with_no_scenario_heading_stops_before_the_maker(self):
        path = os.path.join(self.wt, ".xv", "slices", "s1.md")
        with open(path) as f:
            text = f.read()
        self.assertIn("## Scenario", text)
        with open(path, "w") as f:
            f.write(text.replace("## Scenario", "## Story"))
        self.assert_stopped_before_the_maker(self.scenario_with_env(), "Scenario")

    def test_a_report_with_no_not_covered_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_DROP="not_covered")
        self.assert_stopped_before_the_maker(p, "not_covered")

    def test_a_not_covered_that_is_not_a_list_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"not_covered": "nothing"}')
        self.assert_stopped_before_the_maker(p, "not_covered")

    def test_a_report_with_no_covers_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_DROP="covers")
        self.assert_stopped_before_the_maker(p, "covers")

    def test_a_covers_that_is_not_a_list_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": "everything"}')
        self.assert_stopped_before_the_maker(p, "covers")

    def test_a_covers_item_that_names_no_test_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": [{"item": "milk today"}]}')
        self.assert_stopped_before_the_maker(p, "covers")

    def test_an_empty_covers_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": []}')
        self.assert_stopped_before_the_maker(p, "covers")

    def test_a_covers_item_whose_test_is_in_no_red_file_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": [{"item": "milk today", "test": "test_a_ghost"}]}')
        self.assert_stopped_before_the_maker(p, "test_a_ghost")

    def test_one_covers_item_with_a_missing_test_among_found_ones_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": [{"item": "milk today", "test": "test_milk_today"},'
                                                     ' {"item": "cheese", "test": "test_cheese_ghost"}]}')
        self.assert_stopped_before_the_maker(p, "test_cheese_ghost")

    def test_a_covers_test_that_is_only_part_of_a_longer_test_name_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": [{"item": "milk today", "test": "test_milk"}]}')
        self.assert_stopped_before_the_maker(p, "test_milk")

    def test_a_covers_test_found_in_a_red_file_goes_on_to_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covers": [{"item": "milk today", "test": "test_milk_today"}]}')
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_command_whose_words_are_apart_in_the_red_stops_before_the_maker(self):
        self.amend("A person runs `xv slice amend`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="slice a list of other things, then amend")
        self.assert_stopped_before_the_maker(p, "xv slice amend")

    def test_a_command_whose_words_are_out_of_order_in_the_red_stops_before_the_maker(self):
        self.amend("A person runs `xv slice amend`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="amend slice")
        self.assert_stopped_before_the_maker(p, "xv slice amend")

    def test_a_command_whose_words_are_together_in_order_in_the_red_goes_on_to_the_maker(self):
        self.amend("A person runs `xv slice amend`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="self.xv('slice', 'amend', 's1')")
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def assert_refused(self, command):
        p = self.scenario_with_red(command)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "scenario_stopped")
        self.assertIn("&&", stop["question"])
        self.assertIsNot(self.record()["checks"]["scenario"].get("red_fails"), True)

    def test_a_red_joined_with_a_newline_is_refused(self):
        self.assert_refused("false\ntrue")

    def test_a_red_joined_with_a_pipe_is_refused(self):
        self.assert_refused("false | true")

    def test_a_red_joined_with_a_single_ampersand_is_refused(self):
        self.assert_refused("false & true")

    def test_a_newline_inside_quotes_is_not_a_join(self):
        p = self.scenario_with_red("python3 -c 'import sys\nsys.exit(1)'")
        self.assertNotIn("scenario_stopped", p.stdout)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)

    def test_a_pipe_inside_quotes_is_not_a_join(self):
        p = self.scenario_with_red("python3 -c 'import sys; a = 1 | 0; sys.exit(1)'")
        self.assertNotIn("scenario_stopped", p.stdout)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)

    def test_a_semicolon_inside_quotes_is_not_a_join(self):
        p = self.scenario_with_red("python3 -c 'import sys; sys.exit(1)'")
        self.assertNotIn("scenario_stopped", p.stdout)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)

    def test_a_stop_waits_for_an_answer_and_close_needs_the_merge_answered(self):
        self.xv("run", "s1", cwd=self.wt, check=False)
        p = self.xv("close", "s1", cwd=self.wt, check=False)
        self.assertIn("the merge is the person's", p.stderr)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=self.wt)
        self.xv("close", "s1", cwd=self.wt)
        data = self.record()
        self.assertEqual(data["status"], "closed")
        guide = open(os.path.join(self.wt, ".xv", "estimation.md")).read()
        self.assertIn("| s1 |", guide)

    def maker_with(self, env):
        os.environ[env] = "1"
        try:
            for agent in ("forecaster", "scenario"):
                self.xv("step", agent, "s1", cwd=self.wt)
            return self.xv("step", "maker", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ[env]

    def test_a_move_in_the_makers_report_passes_the_wall(self):
        p = self.maker_with("FAKE_MAKER_MOVES")
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(self.record()["moved_tests"][0]["file"], "tests/test_store.py")

    def test_a_maker_that_edits_the_config_stops_the_slice(self):
        p = self.maker_with("FAKE_MAKER_EDITS_CONFIG")
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "protected_changed")

    def test_an_unrecorded_move_by_the_maker_stops_the_slice(self):
        os.environ["FAKE_MAKER_CHEATS"] = "1"
        try:
            for agent in ("forecaster", "scenario"):
                self.xv("step", agent, "s1", cwd=self.wt)
            p = self.xv("step", "maker", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ["FAKE_MAKER_CHEATS"]
        self.assertEqual(p.returncode, 10)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "unrecorded_move")
        p = self.xv("step", "cleaner", "s1", cwd=self.wt, check=False)
        self.assertIn("an earlier stop is unanswered", p.stdout)

    def test_a_step_that_stops_keeps_next_on_that_step(self):
        os.environ["FAKE_MAKER_CHEATS"] = "1"
        try:
            for agent in ("forecaster", "scenario"):
                self.xv("step", agent, "s1", cwd=self.wt)
            p = self.xv("step", "maker", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ["FAKE_MAKER_CHEATS"]
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "unrecorded_move")
        self.assertEqual(self.record()["next"], "maker")

    def test_a_step_with_no_report_keeps_next_on_that_step(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        os.environ["FAKE_NO_REPORT"] = "1"
        try:
            p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ["FAKE_NO_REPORT"]
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "no_report")
        self.assertEqual(self.record()["next"], "scenario")

    def test_a_stop_raised_by_a_step_keeps_the_budget_it_was_raised_under(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        os.environ["FAKE_NO_REPORT"] = "1"
        try:
            self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        finally:
            del os.environ["FAKE_NO_REPORT"]
        self.xv("record", "set", "s1", "budget", '{"usd": 777}', "--by", "pat", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go on", cwd=self.wt)
        self.assertEqual(self.record()["stops"][-1]["budget_change"]["to"], {"usd": 777})


class RedFailsAfterTheMakerTest(RepoCase):
    """After the maker, the red must fail on the code from before the maker, not at HEAD."""

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.baseline = sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()
        with open(os.path.join(self.wt, "fix.txt"), "w") as f:
            f.write("the maker's fix\n")
        sh(["git", "add", "fix.txt"], self.wt)
        sh(["git", "commit", "-qm", "the maker's fix"], self.wt)
        self.head = sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def red_fails(self, command, through_maker=True):
        from run import post_step
        data = {"id": "s1", "base": self.baseline, "wall_baseline": {"commit": self.baseline},
                "red": {"files": ["tests/test_new.py"], "command": command, "failure": "f"},
                "spend": [{"step": "maker"}] if through_maker else [],
                "checks": {"reports": [{"agent": "maker", "status": "done"}] if through_maker else []}}
        config = {"tests": {"paths": ["tests/**"]}}
        return post_step("scenario", self.wt, data, config, self.head, {}, {})["red_fails"]

    def test_a_red_that_fails_before_the_fix_and_passes_at_head_is_red(self):
        self.assertIs(self.red_fails("test -f fix.txt"), True)

    def test_a_red_that_passes_before_the_fix_is_not_red(self):
        self.assertIs(self.red_fails("true"), False)

    def test_before_the_maker_the_red_is_still_run_at_head(self):
        self.assertIs(self.red_fails("test -f fix.txt", through_maker=False), False)

    def rerun(self, data, config, head):
        from run import post_step
        return post_step("scenario", self.wt, data, config, head, {}, {})

    def commit_file(self, name):
        with open(os.path.join(self.wt, name), "w") as f:
            f.write("x\n")
        sh(["git", "add", name], self.wt)
        sh(["git", "commit", "-qm", name], self.wt)
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def test_a_second_rerun_still_checks_the_code_from_before_the_maker(self):
        from run import pre_step
        # the real order: the maker's pre-step runs before its fix; the fix is already committed in setUp,
        # so rewind the record's view: the pre-maker commit is self.baseline
        config = {"tests": {"paths": ["tests/**"]}}
        data = {"id": "s1", "base": self.baseline, "wall_baseline": {"commit": self.baseline},
                "red": {"files": ["tests/test_new.py"], "command": "test -f fix.txt", "failure": "f"},
                "spend": [], "checks": {"reports": []}}
        sh(["git", "checkout", "-q", self.baseline], self.wt)
        pre_step("maker", self.wt, data, config)
        sh(["git", "checkout", "-q", "-"], self.wt)
        data["spend"].append({"step": "maker"})
        self.assertIs(self.rerun(data, config, self.head)["red_fails"], True)
        later = self.commit_file("more.txt")
        self.assertIs(self.rerun(data, config, later)["red_fails"], True)
        later = self.commit_file("more2.txt")
        self.assertIs(self.rerun(data, config, later)["red_fails"], True)

    def after_maker(self, command, setup):
        config = {"tests": {"paths": ["tests/**"]}, "worktrees": {"setup": setup}}
        data = {"id": "s1", "base": self.baseline, "wall_baseline": {"commit": self.baseline},
                "red": {"files": ["tests/test_new.py"], "command": command, "failure": "f"},
                "spend": [{"step": "maker"}], "checks": {"reports": [{"agent": "maker", "status": "done"}]}}
        return self.rerun(data, config, self.head)

    def test_the_check_worktree_runs_setup_first(self):
        # fails only if setup ran there and left its mark
        self.assertIs(self.after_maker("test ! -f SETUP-MARK", "touch SETUP-MARK")["red_fails"], True)

    def test_a_failing_setup_is_not_a_red_that_counts_as_failing(self):
        try:
            checks = self.after_maker("false", "exit 3")
        except Exception:
            return  # the setup_failed stop may surface as an error to the caller
        self.assertIsNot(checks["red_fails"], True)

    def test_a_failing_setup_in_the_check_worktree_is_the_setup_failed_stop(self):
        import orders
        checks = self.after_maker("false", "echo SETUP-BOOM; exit 3")
        data = {"id": "s1", "set_by": "pat", "budget": {"usd": 2}, "spend": [{"step": "maker"}], "stops": [],
                "checks": {"reports": [{"agent": "scenario", "status": "red"}], "scenario": checks}}
        verdict = orders.verdict(data, "scenario", {"tests": {"paths": ["tests/**"]}})
        fired = {f["order"]: f for f in verdict["fired"]}
        self.assertIn("setup_failed", fired)
        self.assertEqual(fired["setup_failed"]["seat"], "originator")
        self.assertIn("SETUP-BOOM", fired["setup_failed"]["question"])


class AcceptedShapeChangeTest(WatchLoopTest):
    """shape_change: accepted counts only when the packet's accepted_by names a decision record
    on this slice that answered a shape_or_pitch stop; otherwise it is read as yes."""

    def decide(self, order="shape_or_pitch", listed=True):
        import record
        path, data, body = record.load(self.wt, "s1")
        rel = record.write_decision(self.wt, "s1", ["pat"], {"order": order, "question": "Shape?"}, "Accepted.")
        if listed:
            data["decisions"].append({"date": "2026-10-30", "who": ["pat"], "decision": "Accepted.", "record": rel})
            record.save(path, data, body)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "a decision"], self.wt)
        return rel

    def run_with_packet(self, shape, accepted_by=None):
        os.environ["FAKE_SHAPE_CHANGE"] = shape
        if accepted_by:
            os.environ["FAKE_PACKET_EXTRA"] = f"accepted_by: {accepted_by}\n"
        try:
            p = self.xv("run", "s1", cwd=self.wt, check=False)
        finally:
            os.environ.pop("FAKE_SHAPE_CHANGE", None)
            os.environ.pop("FAKE_PACKET_EXTRA", None)
        return self.record(), json.loads(p.stdout)["stop"]["order"]

    def test_accepted_with_a_listed_shape_or_pitch_decision_is_kept_and_does_not_stop(self):
        rel = self.decide()
        data, order = self.run_with_packet("accepted", rel)
        self.assertEqual(data["shape_change"], "accepted")
        self.assertEqual(order, "ready_to_merge")

    def test_accepted_without_accepted_by_is_read_as_yes(self):
        self.decide()
        data, order = self.run_with_packet("accepted")
        self.assertEqual(data["shape_change"], "yes")
        self.assertEqual(order, "shape_or_pitch")

    def test_accepted_by_a_file_not_in_the_slice_decisions_is_read_as_yes(self):
        rel = self.decide(listed=False)
        data, order = self.run_with_packet("accepted", rel)
        self.assertEqual(data["shape_change"], "yes")
        self.assertEqual(order, "shape_or_pitch")

    def test_accepted_by_a_missing_file_is_read_as_yes(self):
        self.decide()
        data, order = self.run_with_packet("accepted", ".xv/decisions/no-such-record.md")
        self.assertEqual(data["shape_change"], "yes")
        self.assertEqual(order, "shape_or_pitch")

    def test_accepted_by_a_decision_of_another_order_is_read_as_yes(self):
        rel = self.decide(order="accept_moves")
        data, order = self.run_with_packet("accepted", rel)
        self.assertEqual(data["shape_change"], "yes")
        self.assertEqual(order, "shape_or_pitch")

    def test_xv_guard_with_no_slice_record_reads_accepted_as_yes(self):
        rel = self.decide()
        sh(["git", "checkout", "-q", "-b", "pr"], self.repo)
        with open(os.path.join(self.repo, "change.txt"), "w") as f:
            f.write("a change\n")
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "a change"], self.repo)
        os.environ["FAKE_SHAPE_CHANGE"] = "accepted"
        os.environ["FAKE_PACKET_EXTRA"] = f"accepted_by: {rel}\n"
        try:
            p = self.xv("guard", "--base", "main", cwd=self.repo, check=False)
        finally:
            del os.environ["FAKE_SHAPE_CHANGE"], os.environ["FAKE_PACKET_EXTRA"]
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "shape_or_pitch", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()

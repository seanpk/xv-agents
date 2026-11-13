import json
import os
import re
import shutil
import sys
import unittest

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")
MISSING = object()  # a report field left out, not set to a value


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


class RedCannotRunSamplesTest(unittest.TestCase):
    """A red that cannot run (#141): the runner's own words for "I could not load or find tests" stop it wherever they
    appear; a generic error name stops it only when no real test failed. The samples are real output from each runner
    (tests/data/cannot-run/<runner>-*.txt), long stack frames trimmed."""

    DATA = os.path.join(HOME, "tests", "data", "cannot-run")

    def sample(self, name):
        with open(os.path.join(self.DATA, name + ".txt")) as f:
            return f.read()

    def runners(self):
        import run
        named = re.search(r"from (.+?) output", run.failing_tests.__doc__, re.S).group(1)
        return [n.lower() for n in re.split(r",\s*|\s+or\s+", " ".join(named.split())) if n]

    def samples_of(self, runner):
        return sorted(f[:-4] for f in os.listdir(self.DATA) if f.startswith(runner + "-") and f.endswith(".txt")
                      and "good-red" not in f)

    def test_every_runner_failing_tests_parses_has_a_cannot_run_sample(self):
        import run
        runners = self.runners()
        self.assertEqual(len(runners), 11, runners)
        self.assertEqual(sorted(run.RUNNER_WORDS), sorted(runners), "every runner has its own words, and no others")
        for runner in runners:
            with self.subTest(runner=runner):
                names = self.samples_of(runner)
                self.assertTrue(names, f"{runner} has no cannot-run sample in tests/data/cannot-run")
                for name in names:
                    self.assertTrue(run.red_cannot_run(1, self.sample(name)), name)

    def test_every_runner_has_a_sample_its_own_words_catch(self):
        import run
        for runner in self.runners():
            with self.subTest(runner=runner):
                words = re.compile("|".join(run.RUNNER_WORDS[runner]), re.I)
                self.assertTrue(any(words.search(self.sample(n)) for n in self.samples_of(runner)))

    def test_a_runners_own_words_stop_it_even_when_other_tests_fail_for_real(self):
        from run import failing_tests, red_cannot_run
        out = self.sample("unittest-load")
        self.assertIn("test_x (test_ok.A.test_x)", failing_tests(out))
        self.assertTrue(red_cannot_run(1, out))
        out = self.sample("go-load")
        self.assertEqual(failing_tests(out), ["TestAdds"])
        self.assertTrue(red_cannot_run(1, out))

    def test_a_generic_error_name_stops_a_red_only_when_no_real_test_failed(self):
        from run import failing_tests, red_cannot_run
        out = self.sample("jasmine-load")
        self.assertEqual(failing_tests(out), [])
        self.assertTrue(red_cannot_run(1, out))
        self.assertIn("Cannot find module", red_cannot_run(1, "Error: Cannot find module './x'\n"))
        self.assertFalse(red_cannot_run(1, "FAIL: test_a (t.A.test_a)\nImportError: boom\nRan 1 test\n"))

    def test_a_no_such_file_from_a_real_failing_test_is_a_failing_red(self):
        from run import failing_tests, red_cannot_run
        for name, real in (("unittest-good-red", "test_asserts (test_gr.A.test_asserts)"),
                           ("pytest-good-red", "test_gr.py::A::test_asserts")):
            with self.subTest(name=name):
                out = self.sample(name)
                self.assertIn("No such file or directory", out)
                self.assertIn(real, " ".join(failing_tests(out)))
                self.assertIsNone(red_cannot_run(1, out))

    def test_exit_126_and_127_cannot_run(self):
        from run import red_cannot_run
        for code in (126, 127):
            self.assertIn(str(code), red_cannot_run(code, "sh: 1: nosuch: not found\n"))
        self.assertIsNone(red_cannot_run(0, "No tests found"))
        self.assertIsNone(red_cannot_run(None, "No tests found"))


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


class WatchLoopSetup(RepoCase):
    """The setup the watch-loop tests share; it holds no tests, so a subclass re-runs none."""

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


class WatchLoopTest(WatchLoopSetup):
    """The whole loop with a stand-in agent: the plumbing, not the briefs."""

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

    def test_an_old_assertion_changed_in_a_file_outside_the_red_stops_before_the_maker(self):
        os.environ["FAKE_SCENARIO_EDITS_OLD_OUTSIDE_RED"] = "1"
        try:
            p = self.scenario_with_red("false")
        finally:
            del os.environ["FAKE_SCENARIO_EDITS_OLD_OUTSIDE_RED"]
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "unrecorded_move")
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

    def test_a_red_that_cannot_run_is_not_a_failing_red_and_stops_the_scenario_step(self):
        p = self.scenario_with_red("python3 -c 'import xv_no_such_module'")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "red_cannot_run")
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("xv_no_such_module", stop["question"])
        self.assertIn("cannot run", stop["question"])
        data = self.record()
        self.assertIsNot(data["checks"]["scenario"].get("red_fails"), True)
        self.assertEqual(data["next"], "scenario")
        self.assertNotIn("maker", [s["step"] for s in data["spend"]])

    def test_a_red_that_runs_its_tests_and_some_fail_is_still_a_failing_red(self):
        p = self.scenario_with_red("echo 'FAIL: test_x (t.A.test_x)' && echo 'Ran 1 test' && false")
        self.assertNotIn("scenario_stopped", p.stdout)
        self.assertNotIn("red_cannot_run", p.stdout)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)

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
        p = self.scenario_with_env(FAKE_REPORT_DROP="covered")
        self.assert_stopped_before_the_maker(p, "covered")

    def test_a_covers_that_is_not_a_list_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": "everything"}')
        self.assert_stopped_before_the_maker(p, "covered")

    def test_a_covers_item_that_names_no_test_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": [{"item": "milk today"}]}')
        self.assert_stopped_before_the_maker(p, "covered")

    def test_an_empty_covers_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": []}')
        self.assert_stopped_before_the_maker(p, "covered")

    def test_a_covers_item_whose_test_is_in_no_red_file_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": [{"item": "milk today", "test": "test_a_ghost"}]}')
        self.assert_stopped_before_the_maker(p, "test_a_ghost")

    def test_one_covers_item_with_a_missing_test_among_found_ones_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": [{"item": "milk today", "test": "test_milk_today"},'
                                                     ' {"item": "cheese", "test": "test_cheese_ghost"}]}')
        self.assert_stopped_before_the_maker(p, "test_cheese_ghost")

    def test_a_covers_test_that_is_only_part_of_a_longer_test_name_stops_before_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": [{"item": "milk today", "test": "test_milk"}]}')
        self.assert_stopped_before_the_maker(p, "test_milk")

    def test_a_covers_test_found_in_a_red_file_goes_on_to_the_maker(self):
        p = self.scenario_with_env(FAKE_REPORT_EXTRA='{"covered": [{"item": "milk today", "test": "test_milk_today"}]}')
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def covers_test(self, test, **env):
        extra = json.dumps({"covered": [{"item": "milk today", "test": test}]})
        return self.scenario_with_env(FAKE_REPORT_EXTRA=extra, **env)

    def assert_goes_on(self, p):
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_covers_test_that_is_a_list_of_names_all_in_red_files_goes_on_to_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", "test_cheese"]}]})
        p = self.scenario_with_env(FAKE_REPORT_EXTRA=extra, FAKE_RED_TEXT="def test_cheese(self): pass")
        self.assert_goes_on(p)

    def test_a_covers_list_with_a_name_in_no_red_file_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", "test_cheese_ghost"]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "test_cheese_ghost")

    def test_a_covers_list_with_a_name_that_is_part_of_a_longer_name_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", "test_milk"]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "test_milk")

    def test_an_empty_covers_list_stops_before_the_maker(self):
        self.assert_stopped_before_the_maker(self.covers_test([]), "covered")

    def test_a_covers_test_that_joins_names_with_a_comma_goes_on_to_the_maker(self):
        p = self.covers_test("test_milk_today, test_cheese", FAKE_RED_TEXT="def test_cheese(self): pass")
        self.assert_goes_on(p)

    def test_a_covers_test_that_joins_names_with_a_semicolon_goes_on_to_the_maker(self):
        p = self.covers_test("test_milk_today; test_cheese", FAKE_RED_TEXT="def test_cheese(self): pass")
        self.assert_goes_on(p)

    def test_a_joined_covers_test_with_a_name_in_no_red_file_stops_before_the_maker(self):
        p = self.covers_test("test_milk_today, test_cheese_ghost")
        self.assert_stopped_before_the_maker(p, "test_cheese_ghost")

    def test_a_covers_name_written_class_dot_test_goes_on_when_the_class_and_test_are_in_a_red_file(self):
        self.assert_goes_on(self.covers_test("Red.test_milk_today"))

    def test_a_covers_name_written_with_the_wrong_class_stops_before_the_maker(self):
        self.assert_stopped_before_the_maker(self.covers_test("Ghost.test_milk_today"), "Ghost.test_milk_today")

    def test_a_covers_name_written_file_colons_test_goes_on_when_the_file_is_a_red_file_with_the_test(self):
        self.assert_goes_on(self.covers_test("tests/test_red.py::test_milk_today"))

    def test_a_covers_name_written_with_a_file_that_is_not_a_red_file_stops_before_the_maker(self):
        p = self.covers_test("tests/test_store.py::test_milk_today")
        self.assert_stopped_before_the_maker(p, "tests/test_store.py::test_milk_today")

    def test_a_covers_name_written_with_the_right_file_and_a_test_it_lacks_stops_before_the_maker(self):
        p = self.covers_test("tests/test_red.py::test_cheese_ghost")
        self.assert_stopped_before_the_maker(p, "test_cheese_ghost")

    def test_a_covers_list_with_a_number_among_the_names_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", 7]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "covered")

    def test_a_covers_list_with_an_empty_string_among_the_names_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", ""]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "covered")

    def test_a_covers_list_with_a_null_among_the_names_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", None]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "covered")

    def test_a_covers_name_with_a_red_module_in_front_goes_on_to_the_maker(self):
        self.assert_goes_on(self.covers_test("tests.test_red.Red.test_milk_today"))

    def test_a_covers_name_with_a_module_that_is_not_a_red_file_stops_before_the_maker(self):
        p = self.covers_test("tests.test_store.Red.test_milk_today")
        self.assert_stopped_before_the_maker(p, "tests.test_store.Red.test_milk_today")

    def test_a_covers_name_with_a_red_module_but_the_wrong_class_stops_before_the_maker(self):
        p = self.covers_test("tests.test_red.Ghost.test_milk_today")
        self.assert_stopped_before_the_maker(p, "tests.test_red.Ghost.test_milk_today")

    def test_a_covers_name_with_a_red_module_and_class_but_a_test_it_lacks_stops_before_the_maker(self):
        p = self.covers_test("tests.test_red.Red.test_cheese_ghost")
        self.assert_stopped_before_the_maker(p, "test_cheese_ghost")

    def test_a_covers_name_with_an_empty_test_part_after_colons_stops_before_the_maker(self):
        p = self.covers_test("tests/test_red.py::")
        self.assert_stopped_before_the_maker(p, "tests/test_red.py::")

    def test_a_covers_name_with_an_empty_test_part_after_a_dot_stops_before_the_maker(self):
        self.assert_stopped_before_the_maker(self.covers_test("Red."), "Red.")

    def test_a_covers_name_with_a_red_module_and_class_but_an_empty_test_part_stops_before_the_maker(self):
        p = self.covers_test("tests.test_red.Red.")
        self.assert_stopped_before_the_maker(p, "tests.test_red.Red.")

    def test_a_covers_list_with_a_name_whose_test_part_is_empty_stops_before_the_maker(self):
        extra = json.dumps({"covered": [{"item": "milk today", "test": ["test_milk_today", "Red."]}]})
        self.assert_stopped_before_the_maker(self.scenario_with_env(FAKE_REPORT_EXTRA=extra), "Red.")

    def test_a_command_whose_words_are_apart_in_the_red_stops_before_the_maker(self):
        self.amend("A person runs `xv slice ghost`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="slice a list of other things, then ghost")
        self.assert_stopped_before_the_maker(p, "xv slice ghost")

    def test_a_command_whose_words_are_out_of_order_in_the_red_stops_before_the_maker(self):
        self.amend("A person runs `xv slice ghost`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="ghost slice")
        self.assert_stopped_before_the_maker(p, "xv slice ghost")

    def test_a_command_whose_words_are_together_in_order_in_the_red_goes_on_to_the_maker(self):
        self.amend("A person runs `xv slice ghost`.")
        p = self.scenario_with_env(FAKE_RED_TEXT="self.xv('slice', 'ghost', 's1')")
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

    P1 = "1. A household sees milk running out soon."
    P2 = "2. A household sees nothing for bread that is fresh."

    def record_text(self):
        with open(os.path.join(self.wt, ".xv", "slices", "s1.md")) as f:
            return f.read()

    def open_stops(self):
        return [s for s in self.record()["stops"] if s.get("answer") is None]

    def scenario_covering(self, covered=(), not_covered=()):
        """Run the scenario step once, with a report that covers only the given points."""
        from unittest import mock
        extra = {"covered": [{"item": c, "test": "test_milk_today"} for c in covered],
                 "not_covered": [{"item": n, "why": "no seam to start the app"} for n in not_covered]}
        with mock.patch.dict(os.environ, {"FAKE_REPORT_EXTRA": json.dumps(extra)}):
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def test_a_numbered_point_in_neither_covers_nor_not_covered_goes_back_without_a_stop(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=[self.P1])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(self.record()["next"], "scenario")
        self.assertNotIn("maker", [s["step"] for s in self.record()["spend"]])
        watch_lines = [ln for ln in self.record_text().splitlines() if " watch: " in ln and self.P2 in ln]
        self.assertTrue(watch_lines, "the watch records the send-back with the missed point")

    def test_the_next_scenario_agent_gets_the_missed_point_through_xv_prompt(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=[self.P1])
        prompt = self.xv("prompt", "scenario", "s1", cwd=self.wt).stdout
        self.assertIn(self.P2, prompt)

    def test_a_numbered_point_in_not_covered_still_stops_for_the_person(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=[self.P1], not_covered=[self.P2])
        self.assert_stopped_before_the_maker(p, "no seam to start the app")

    def test_every_numbered_point_in_covers_goes_on_to_the_maker(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=[self.P1, self.P2])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def in_the_scenario(self, text):
        """Put numbered points in the scenario itself, not in an amendment."""
        path = os.path.join(self.wt, ".xv", "slices", "s1.md")
        with open(path) as f:
            body = f.read()
        with open(path, "w") as f:
            f.write(body.replace("## Scenario\n", "## Scenario\n\n" + text + "\n", 1))

    def covered_by_number(self, scenario, items):
        self.in_the_scenario(scenario)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        return self.scenario_covering(covered=items)

    P3 = "3. A household sees the pantry list in order."

    def test_a_number_does_not_cover_a_point_an_amendment_adds(self):
        self.in_the_scenario(f"{self.P1}\n{self.P2}")
        self.amend(self.P3)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1", "2", "3"])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "scenario")
        self.assertTrue([l for l in self.record_text().splitlines() if " watch: " in l and self.P3 in l])

    def test_a_number_and_text_item_does_not_cover_an_amendments_point_either(self):
        self.in_the_scenario(f"{self.P1}\n{self.P2}")
        self.amend(self.P3)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=["1", "2", "3. Pantry list order"])
        self.assertEqual(self.record()["next"], "scenario")

    def test_an_amendments_point_is_still_covered_by_its_own_words(self):
        self.in_the_scenario(f"{self.P1}\n{self.P2}")
        self.amend(self.P3)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1", "2", self.P3])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_number_does_not_cover_an_amendments_point_that_shares_the_scenarios_number(self):
        self.in_the_scenario(f"{self.P1}\n{self.P2}")
        self.amend("2. A household sees a restock hint.")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=["1", "2"])
        self.assertEqual(self.record()["next"], "scenario")

    def test_a_covers_item_that_is_a_points_number_covers_it(self):
        p = self.covered_by_number(f"{self.P1}\n{self.P2}", ["1", "2"])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_covers_item_that_starts_with_the_number_covers_the_point(self):
        p = self.covered_by_number(f"{self.P1}\n{self.P2}", ["1. Whether a miss repeats", "2. Fresh bread"])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_a_number_covers_only_its_own_point(self):
        self.covered_by_number(f"{self.P1}\n{self.P2}", ["1"])
        self.assertEqual(self.record()["next"], "scenario")
        self.assertTrue([l for l in self.record_text().splitlines() if " watch: " in l and self.P2 in l])

    def test_the_number_one_does_not_cover_point_ten(self):
        ten = "10. A household sees the pantry list in order."
        self.covered_by_number(f"{self.P1}\n{ten}", ["1"])
        self.assertEqual(self.record()["next"], "scenario")
        self.assertTrue([l for l in self.record_text().splitlines() if " watch: " in l and ten in l])

    def test_a_number_item_in_not_covered_still_stops_for_the_person(self):
        self.in_the_scenario(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1"], not_covered=["2"])
        self.assert_stopped_before_the_maker(p, "no seam to start the app")

    def test_the_same_missed_point_on_the_next_pass_goes_back_again(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=[self.P1])
        p = self.scenario_covering(covered=[self.P1])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(self.record()["next"], "scenario")

    def test_the_third_miss_in_a_row_of_the_same_point_stops_for_the_person(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        for _ in range(2):
            self.scenario_covering(covered=[self.P1])
        p = self.scenario_covering(covered=[self.P1])
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual((stop["order"], stop["seat"]), ("red_misses_point", "originator"))
        self.assertEqual(len(self.open_stops()), 1)

    def test_a_point_sent_back_twice_then_covered_then_missed_again_goes_back(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        for _ in range(2):
            self.scenario_covering(covered=[self.P1])
        self.scenario_covering(covered=[self.P1, self.P2])
        p = self.scenario_covering(covered=[self.P1])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(self.record()["next"], "scenario")

    def test_send_backs_from_before_an_amendment_do_not_count_toward_the_stop(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        for _ in range(2):
            self.scenario_covering(covered=[self.P1])
        self.amend("3. A household sees the pantry list in order.")
        p = self.scenario_covering(covered=[self.P1])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(self.record()["next"], "scenario")

    def test_send_backs_from_before_a_persons_answer_do_not_count_toward_the_stop(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        for _ in range(3):
            self.scenario_covering(covered=[self.P1])
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "again", "--next", "scenario",
                "--settled", "Pat wants every point covered.", cwd=self.wt)
        p = self.scenario_covering(covered=[self.P1])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(self.record()["next"], "scenario")

    PM = "1. The `doc` kind refuses a file under `.xv/` and any file named `SKILL.md`."

    def test_an_item_without_the_backticks_covers_the_point_that_has_them(self):
        self.amend(self.PM)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1. The doc kind refuses a file under .xv/ and any file named SKILL.md."])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def test_an_item_without_stars_and_underscores_covers_the_point_that_has_them(self):
        self.amend("1. A **household** sees milk in the _restock_ list.")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1. A household sees milk in the restock list."])
        self.assertEqual(self.record()["next"], "maker", p.stdout + p.stderr)

    def test_the_marks_come_off_the_item_too(self):
        self.amend("1. A household sees milk in the restock list.")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.scenario_covering(covered=["1. A `household` sees **milk** in the _restock_ list."])
        self.assertEqual(self.record()["next"], "maker", p.stdout + p.stderr)

    def test_an_item_that_changes_a_word_still_does_not_cover_the_point(self):
        self.amend(self.PM)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=["1. The doc kind accepts a file under .xv/ and any file named SKILL.md."])
        self.assertEqual(self.record()["next"], "scenario")

    def test_the_send_back_hands_over_the_point_as_an_item_the_check_accepts(self):
        self.amend(f"{self.PM}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=[self.P2])
        prompt = self.xv("prompt", "scenario", "s1", cwd=self.wt).stdout
        self.assertIn(self.PM, prompt)

    def test_the_send_back_says_every_point_goes_in_covers_or_not_covered_each_pass(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=[self.P1])
        said = " ".join(self.xv("prompt", "scenario", "s1", cwd=self.wt).stdout.lower().split())
        self.assertIn("every point", said)
        self.assertIn("each pass", said)
        self.assertIn("amendments", said)
        self.assertIn("not_covered", said)

    def test_the_changelog_has_a_line_for_the_red_misses_point_trigger(self):
        with open(os.path.join(HOME, "CHANGELOG.md")) as f:
            unreleased = f.read().split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        self.assertIn("red_misses_point", unreleased)

    def guardian_with_miss(self, miss="Point 1 is not met: the list still leaves out milk that runs out today.",
                           **env):
        from unittest import mock
        with mock.patch.dict(os.environ, dict(env, FAKE_SCENARIO_MISS=miss)):
            return self.xv("step", "guardian", "s1", cwd=self.wt, check=False)

    def to_the_guardian(self):
        for agent in ("forecaster", "scenario", "maker", "cleaner"):
            self.xv("step", agent, "s1", cwd=self.wt)

    def test_a_scenario_miss_in_the_packet_sends_the_slice_to_the_maker_without_a_stop(self):
        self.to_the_guardian()
        p = self.guardian_with_miss()
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        data = self.record()
        self.assertEqual(data["scenario_miss"], "yes")
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(data["next"], "maker")
        self.assertIn("milk that runs out today",
                      "\n".join(ln for ln in self.record_text().splitlines() if " watch: " in ln))

    def test_the_maker_gets_the_miss_through_xv_prompt(self):
        self.to_the_guardian()
        self.guardian_with_miss()
        self.assertIn("milk that runs out today", self.xv("prompt", "maker", "s1", cwd=self.wt).stdout)

    def test_a_scenario_miss_beside_a_shape_change_still_stops_for_two_people(self):
        self.to_the_guardian()
        p = self.guardian_with_miss(FAKE_SHAPE_CHANGE="yes")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "shape_or_pitch")

    def test_the_same_scenario_miss_on_the_next_guardian_pass_stops_for_the_person(self):
        self.to_the_guardian()
        self.guardian_with_miss()
        for agent in ("maker", "cleaner"):
            self.xv("step", agent, "s1", cwd=self.wt)
        p = self.guardian_with_miss()
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["seat"], "originator")
        self.assertNotEqual(json.loads(p.stdout)["stop"]["order"], "ready_to_merge")

    def test_a_miss_marked_amend_yes_is_not_sent_back_and_stops_for_the_person(self):
        self.to_the_guardian()
        p = self.guardian_with_miss("2: the scenario itself is wrong here, to: maker, amend: yes")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        self.assertNotEqual(stop["order"], "ready_to_merge")
        self.assertEqual(len(self.open_stops()), 1)

    def test_xv_decisions_counts_a_guardian_send_back_as_a_scenario_miss_row(self):
        self.to_the_guardian()
        self.guardian_with_miss("2: milk that runs out today is left out, to: maker")
        out = self.xv("decisions", cwd=self.wt).stdout
        self.assertTrue([ln for ln in out.splitlines() if "scenario_miss" in ln], out)

    def test_xv_decisions_counts_a_scenario_send_back_as_a_red_misses_point_row(self):
        self.amend(f"{self.P1}\n{self.P2}")
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario_covering(covered=[self.P1])
        out = self.xv("decisions", cwd=self.wt).stdout
        self.assertTrue([ln for ln in out.splitlines() if "red_misses_point" in ln], out)

    def test_a_packet_with_no_miss_still_ends_in_the_merge_stop(self):
        self.to_the_guardian()
        p = self.xv("step", "guardian", "s1", cwd=self.wt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "ready_to_merge")
        self.assertEqual(self.record()["scenario_miss"], "no")

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


class AcceptedShapeChangeTest(WatchLoopSetup):
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

    def record_packet(self, shape, accepted_by=None):
        extra = f"accepted_by: {accepted_by}\n" if accepted_by else ""
        packet = os.path.join(self.wt, "hand-packet.md")
        with open(packet, "w") as f:
            f.write(f"---\nshape_change: {shape}\npitch_contradiction: no\n{extra}---\nA packet.\n")
        self.xv("record", "packet", "s1", packet, cwd=self.wt)
        return self.record()["shape_change"]

    def test_record_packet_keeps_accepted_with_a_listed_shape_or_pitch_decision(self):
        rel = self.decide()
        self.assertEqual(self.record_packet("accepted", rel), "accepted")

    def test_record_packet_reads_accepted_without_accepted_by_as_yes(self):
        self.decide()
        self.assertEqual(self.record_packet("accepted"), "yes")

    def test_record_packet_reads_accepted_by_an_unlisted_file_as_yes(self):
        rel = self.decide(listed=False)
        self.assertEqual(self.record_packet("accepted", rel), "yes")

    def test_record_packet_reads_accepted_by_a_missing_file_as_yes(self):
        self.decide()
        self.assertEqual(self.record_packet("accepted", ".xv/decisions/no-such-record.md"), "yes")

    def test_record_packet_reads_accepted_by_a_decision_of_another_order_as_yes(self):
        rel = self.decide(order="accept_moves")
        self.assertEqual(self.record_packet("accepted", rel), "yes")

    def test_the_guardian_brief_allows_accepted_and_names_accepted_by(self):
        text = open(os.path.join(HOME, "skills", "guardian", "SKILL.md")).read()
        may_not = text[text.index("## May not"):text.index("## Writes to the slice record")]
        self.assertNotIn("anything but `yes` or `no`", may_not)
        self.assertIn("accepted", may_not)
        self.assertIn("accepted_by", text)
        fields = [l for l in text.splitlines() if "pitch_contradiction" in l and "fixed fields" in l][0]
        self.assertNotIn("each `yes` or `no`, nothing else", fields)


class EveryPathOneVerdictTest(WatchLoopSetup):
    """`xv step`, `xv run` and the session path (`xv record report`, then `xv record packet`) are
    given the same record and the same packet, and leave the same verdict."""

    MISS = "Point 1 is not met: the list still leaves out milk that runs out today."

    def view(self):
        data = self.record()
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        return {"open": [(s["order"], s["seat"]) for s in open_stops], "status": data["status"],
                "next": data["next"]}

    def record_file(self):
        return os.path.join(self.wt, ".xv", "slices", "s1.md")

    def test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path(self):
        from unittest import mock
        for agent in ("forecaster", "scenario", "maker", "cleaner"):
            self.xv("step", agent, "s1", cwd=self.wt)
        with mock.patch.dict(os.environ, {"FAKE_SCENARIO_MISS": self.MISS}):
            self.xv("step", "guardian", "s1", cwd=self.wt, check=False)  # the first miss: sent back
        for agent in ("maker", "cleaner"):
            self.xv("step", agent, "s1", cwd=self.wt)
        before = open(self.record_file()).read()

        with mock.patch.dict(os.environ, {"FAKE_SCENARIO_MISS": self.MISS}):
            self.xv("step", "guardian", "s1", cwd=self.wt, check=False)
        by_step = self.view()
        self.assertEqual(by_step["open"], [("scenario_miss", "originator")], by_step)

        with open(self.record_file(), "w") as f:
            f.write(before)
        with mock.patch.dict(os.environ, {"FAKE_SCENARIO_MISS": self.MISS}):
            ran = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(self.view(), by_step, ran.stdout + ran.stderr)

        with open(self.record_file(), "w") as f:
            f.write(before)
        report = os.path.join(self.wt, "g.json")
        with open(report, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "guardian", "status": "done", "summary": "done"})
                    + "\n```\n")
        packet = os.path.join(self.wt, "hand-packet.md")
        with open(packet, "w") as f:
            f.write("---\nslice: s1\nshape_change: no\npitch_contradiction: no\nscenario_miss: yes\nexpected_moves: 0\n---\n\n# Packet\n\n"
                    "## Scenario misses\n\n- %s (evidence: tests/test_red.py:7)\n" % self.MISS)
        self.xv("record", "report", "s1", "guardian", report, cwd=self.wt)
        self.xv("record", "packet", "s1", packet, cwd=self.wt)
        self.assertEqual(self.view(), by_step)


class PreStepBudgetStopTest(WatchLoopSetup):
    def test_the_stop_xv_step_raises_before_a_step_is_answered_without_settled_once_the_budget_is_raised(self):
        self.xv("record", "add", "s1", "spend", json.dumps({"step": "forecaster", "usd": 5, "tokens": 1}),
                cwd=self.wt)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent", p.stdout + p.stderr)
        self.xv("record", "set", "s1", "budget", '{"usd": 20}', "--by", "pat", cwd=self.wt)
        a = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "more", "--next", "scenario",
                    cwd=self.wt, check=False)
        self.assertEqual(a.returncode, 0, a.stderr)


class NamedByTheScenarioReachTheMakerTest(RepoCase):
    """The scenario report's `old_tests_forced` and `may_not_files` are kept, shown to the maker, and honoured."""

    OLD = {"file": "tests/test_api.py", "test": "test_message", "why": "the reply text changes"}
    FILE = {"file": ".xv/picture.md", "why": "the red needs a new binding decision"}

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.baseline = sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def report(self, agent, **keys):
        import record
        text = "```xv-report\n" + json.dumps({"agent": agent, "status": "red", "summary": "s", **keys}) + "\n```\n"
        data = {"moved_tests": [], "checks": {}}
        record.apply_report(data, "", agent, text)
        return data

    def test_the_record_keeps_the_old_tests_the_scenario_report_names(self):
        data = self.report("scenario", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.assertEqual(data.get("old_tests_forced"), [self.OLD])

    def test_the_record_keeps_the_may_not_files_the_scenario_report_names(self):
        data = self.report("scenario", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.assertEqual(data.get("may_not_files"), [self.FILE])

    def test_an_entry_missing_its_file_or_why_is_not_kept(self):
        bad = [{"why": "no file"}, {"file": ".xv/picture.md"}, {"file": "", "why": "empty"},
               {"file": 7, "why": "wrong type"}, "just a string", None]
        data = self.report("scenario", old_tests_forced=bad, may_not_files=bad)
        self.assertEqual(data.get("may_not_files") or [], [])
        self.assertEqual(data.get("old_tests_forced") or [], [])

    def test_a_value_that_is_not_a_list_is_not_kept(self):
        data = self.report("scenario", old_tests_forced="tests/test_api.py", may_not_files=dict(file=".xv/picture.md"))
        self.assertEqual(data.get("may_not_files") or [], [])
        self.assertEqual(data.get("old_tests_forced") or [], [])

    def test_a_maker_that_writes_the_lists_about_itself_does_not_get_them_kept(self):
        data = self.report("maker", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.assertEqual(data.get("may_not_files") or [], [])
        self.assertEqual(data.get("old_tests_forced") or [], [])

    def test_the_makers_prompt_lists_the_named_tests_and_files(self):
        from prompt import pointers
        data = {"id": "s1", "old_tests_forced": [self.OLD], "may_not_files": [self.FILE]}
        text = pointers("maker", self.wt, {}, data)
        for word in ("tests/test_api.py", "test_message", "the reply text changes",
                     ".xv/picture.md", "the red needs a new binding decision"):
            self.assertIn(word, text)

    def test_the_makers_prompt_does_not_license_a_named_file_other_than_the_picture(self):
        from prompt import pointers
        data = {"id": "s1", "may_not_files": [{"file": ".xv/pitch.md", "why": "the pitch changes"},
                                              {"file": ".xv/config.yml", "why": "a setting"}, self.FILE]}
        text = pointers("maker", self.wt, {}, data)
        self.assertIn("Named file you may change: .xv/picture.md", text)
        self.assertNotIn("you may change: .xv/pitch.md", text)
        self.assertNotIn("you may change: .xv/config.yml", text)

    def test_another_agents_prompt_does_not_license_the_files(self):
        from prompt import pointers
        data = {"id": "s1", "may_not_files": [self.FILE]}
        self.assertNotIn("the red needs a new binding decision", pointers("cleaner", self.wt, {}, data))

    def maker_check(self, *, named, changes, text="changed by the maker\n"):
        from run import post_step
        for name in changes:
            os.makedirs(os.path.dirname(os.path.join(self.wt, name)), exist_ok=True)
            with open(os.path.join(self.wt, name), "a") as f:
                f.write(text)
            sh(["git", "add", name], self.wt)
        sh(["git", "commit", "-qm", "maker"], self.wt)
        data = {"id": "s1", "base": self.baseline, "wall_baseline": {"commit": self.baseline},
                "may_not_files": named, "red": {"files": [], "command": "true", "failure": "f"},
                "spend": [{"step": "maker"}], "checks": {"reports": []}}
        config = {"tests": {"paths": ["tests/**"]}}
        return post_step("maker", self.wt, data, config, self.baseline, {}, {})["protected_changed"]

    def test_a_named_may_not_file_changed_by_the_maker_is_not_protected_changed(self):
        self.assertEqual(self.maker_check(named=[self.FILE], changes=[".xv/picture.md"]), [])

    def test_a_named_file_does_not_license_another_protected_file(self):
        self.assertEqual(self.maker_check(named=[self.FILE], changes=[".xv/picture.md", ".xv/rules.md"]),
                         [".xv/rules.md"])

    def test_a_protected_file_nobody_named_is_still_protected_changed(self):
        self.assertEqual(self.maker_check(named=[], changes=[".xv/picture.md"]), [".xv/picture.md"])

    def named_but_protected(self, name, text="changed by the maker\n"):
        named = [{"file": name, "why": "the red wants it"}]
        self.assertEqual(self.maker_check(named=named, changes=[name], text=text), [name])

    def test_naming_the_pitch_does_not_let_the_maker_change_it(self):
        self.named_but_protected(".xv/pitch.md")

    def test_naming_the_config_does_not_let_the_maker_change_it(self):
        self.named_but_protected(".xv/config.yml")

    def test_naming_the_slices_wall_file_does_not_let_the_maker_change_it(self):
        self.named_but_protected(".xv/slices/s1.wall.json", text='{"commit": "x", "files": {}}\n')

    def test_naming_the_rules_does_not_let_the_maker_change_it(self):
        self.named_but_protected(".xv/rules.md")

    def test_naming_picture_and_pitch_licenses_only_the_picture(self):
        named = [self.FILE, {"file": ".xv/pitch.md", "why": "the red wants it"}]
        self.assertEqual(self.maker_check(named=named, changes=[".xv/picture.md", ".xv/pitch.md"]),
                         [".xv/pitch.md"])

    def second_report(self, data, **keys):
        import record
        text = "```xv-report\n" + json.dumps({"agent": "scenario", "status": "red", "summary": "s", **keys}) + "\n```\n"
        record.apply_report(data, "", "scenario", text)

    def test_a_scenario_report_that_leaves_the_lists_out_clears_the_earlier_ones(self):
        data = self.report("scenario", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.second_report(data)
        self.assertEqual(data.get("may_not_files") or [], [])
        self.assertEqual(data.get("old_tests_forced") or [], [])

    def test_a_report_that_leaves_out_only_one_list_clears_only_that_one(self):
        data = self.report("scenario", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.second_report(data, may_not_files=[self.FILE])
        self.assertEqual(data.get("old_tests_forced") or [], [])
        self.assertEqual(data.get("may_not_files"), [self.FILE])

    def test_a_report_with_a_value_that_is_not_a_list_clears_the_earlier_lists(self):
        data = self.report("scenario", old_tests_forced=[self.OLD], may_not_files=[self.FILE])
        self.second_report(data, old_tests_forced="none", may_not_files=None)
        self.assertEqual(data.get("may_not_files") or [], [])
        self.assertEqual(data.get("old_tests_forced") or [], [])

    def test_a_malformed_name_licenses_nothing(self):
        self.assertEqual(self.maker_check(named=[dict(file=".xv/picture.md"), ".xv/picture.md"],
                                          changes=[".xv/picture.md"]), [".xv/picture.md"])


class ScenarioChecksTest(WatchLoopSetup):
    """The checks after the scenario step: what they accept, and what they no longer raise for no reason."""

    first = {}

    def scenario(self, **env):
        from unittest import mock
        with mock.patch.dict(os.environ, env):
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def covers_with(self, test, **env):
        extra = json.dumps({"covered": [{"item": "milk today", "test": test}]})
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        return self.scenario(FAKE_REPORT_EXTRA=extra, **env)

    def assert_goes_on(self, p):
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.record()["next"], "maker")

    def assert_stops(self, p, *named):
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        for n in named:
            self.assertIn(n, stop["question"])
        self.assertNotIn("maker", [s["step"] for s in self.record()["spend"]])

    def amend(self, text):
        path = os.path.join(self.tmp, "amendment.md")
        with open(path, "w") as f:
            f.write(text)
        self.xv("slice", "amend", "s1", "--scenario-file", path, "--by", "pat", cwd=self.wt)

    # 1. a covers name that starts with the red file's path, split by :: . # / or ' > '
    def test_a_covers_name_with_the_path_class_and_test_split_by_dots_goes_on(self):
        self.assert_goes_on(self.covers_with("tests/test_red.py::Red.test_milk_today"))

    def test_a_covers_name_split_by_double_colons_after_the_path_goes_on(self):
        self.assert_goes_on(self.covers_with("tests/test_red.py::Red::test_milk_today"))

    def test_a_covers_name_split_by_a_hash_goes_on(self):
        self.assert_goes_on(self.covers_with("Red#test_milk_today"))

    def test_a_covers_name_split_by_a_hash_after_the_path_goes_on(self):
        self.assert_goes_on(self.covers_with("tests/test_red.py#Red#test_milk_today"))

    def test_a_covers_name_split_by_slashes_goes_on_when_each_part_is_in_the_file(self):
        p = self.covers_with("TestPantry/expiring_soon",
                             FAKE_RED_TEXT='func TestPantry(t *testing.T) { t.Run("expiring_soon", nil) }')
        self.assert_goes_on(p)

    def test_a_covers_name_split_by_arrows_goes_on_when_each_part_is_in_the_file(self):
        self.assert_goes_on(self.covers_with("tests/test_red.py > Red > test_milk_today"))

    def test_a_jest_name_with_spaces_in_a_part_goes_on_when_each_part_is_in_the_file(self):
        p = self.covers_with("tests/test_red.py > Case > does the thing",
                             FAKE_RED_TEXT="describe('Case', () => { it('does the thing', f) })")
        self.assert_goes_on(p)

    def test_a_covers_name_whose_later_part_is_not_in_the_file_stops(self):
        self.assert_stops(self.covers_with("tests/test_red.py::Red::test_cheese_ghost"), "test_cheese_ghost")

    def test_a_covers_name_whose_middle_part_is_not_in_the_file_stops(self):
        self.assert_stops(self.covers_with("tests/test_red.py > Ghost > test_milk_today"), "Ghost")

    def test_a_covers_name_whose_parts_are_out_of_order_in_the_file_stops(self):
        self.assert_stops(self.covers_with("tests/test_red.py > test_milk_today > Red"), "test_milk_today > Red")

    def test_a_covers_name_with_a_path_that_is_not_a_red_file_stops(self):
        self.assert_stops(self.covers_with("tests/test_store.py::Red::test_milk_today"), "tests/test_store.py")

    def test_a_covers_name_with_an_empty_part_between_separators_stops(self):
        self.assert_stops(self.covers_with("tests/test_red.py::Red::"), "tests/test_red.py::Red::")

    def test_a_covers_part_that_is_only_the_front_of_a_longer_name_stops(self):
        self.assert_stops(self.covers_with("tests/test_red.py::Red::test_milk"), "test_milk")

    # 4. the coverage from earlier passes stays after a send-back
    def send_back_to_the_scenario(self):
        """Pass one stops on a not_covered item; a person sends the slice back to the scenario agent."""
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam"}]', **self.first)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go again", "--next", "scenario",
                "--settled", "Pat said to cover the grocer share.", cwd=self.wt)

    def test_an_empty_covers_on_a_pass_after_a_send_back_does_not_stop(self):
        self.send_back_to_the_scenario()
        self.assert_goes_on(self.scenario(FAKE_REPORT_EXTRA='{"covered": []}'))

    def test_a_point_covered_on_the_earlier_pass_stays_covered_after_a_send_back(self):
        point = "1. A household sees milk running out soon."
        self.amend(point)
        self.first = {"FAKE_REPORT_EXTRA": json.dumps({"covered": [{"item": point, "test": "test_milk_today"}]})}
        self.send_back_to_the_scenario()
        self.assert_goes_on(self.scenario(FAKE_REPORT_EXTRA='{"covered": []}'))

    def test_a_kept_name_whose_test_is_gone_stops_on_the_pass_after_a_send_back(self):
        self.first = {"FAKE_RED_TEXT": "def test_cheese(self): pass",
                      "FAKE_REPORT_EXTRA": json.dumps({"covered": [{"item": "cheese", "test": "test_cheese"}]})}
        self.send_back_to_the_scenario()
        self.assert_stops(self.scenario(FAKE_REPORT_EXTRA='{"covered": []}'), "test_cheese")

    # #174 point 4: a not_covered item a person answered is not asked again; a new item is
    # amendment 9: only an answer that did not send the slice back settles the item
    def answer_without_a_send_back(self):
        """Pass one stops on a not_covered item; a person accepts it and the slice goes on to the maker."""
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam"}]', **self.first)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "fine without it", "--next", "maker",
                cwd=self.wt)
        self.assertFalse(self.record()["stops"][-1].get("sent_back"))

    def test_a_not_covered_item_a_person_answered_does_not_stop_again_on_a_later_pass(self):
        self.answer_without_a_send_back()
        p = self.scenario(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam"}]')
        self.assert_goes_on(p)
        self.assertEqual([s["order"] for s in self.record()["stops"]].count("red_misses_scenario"), 1)

    def test_a_not_covered_item_the_person_sent_back_stops_again_when_reported_again(self):
        self.send_back_to_the_scenario()
        self.assertTrue(self.record()["stops"][-1].get("sent_back"))
        p = self.scenario(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam"}]')
        self.assert_stops(p, "the grocer share")
        self.assertEqual([s["order"] for s in self.record()["stops"]].count("red_misses_scenario"), 2)

    def test_a_new_not_covered_item_still_stops_on_a_later_pass(self):
        self.answer_without_a_send_back()
        p = self.scenario(FAKE_NOT_COVERED='[{"item": "the grocer share", "why": "no seam"},'
                                           ' {"item": "the pantry export", "why": "no seam"}]')
        self.assert_stops(p, "the pantry export")
        self.assertNotIn("the grocer share", json.loads(p.stdout)["stop"]["question"])

    def test_an_empty_covers_on_the_first_pass_still_stops(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.assert_stops(self.scenario(FAKE_REPORT_EXTRA='{"covered": []}'), "covered")

    def test_an_empty_covers_after_a_send_back_still_stops_when_nothing_was_kept(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.scenario(FAKE_REPORT_EXTRA='{"covered": []}')
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "again", "--next", "scenario",
                "--settled", "Pat wants a covers list.", cwd=self.wt)
        self.assert_stops(self.scenario(FAKE_REPORT_EXTRA='{"covered": []}'), "covered")


class ScenarioChecksAtTheBaseTest(RepoCase):
    """The base holds the xv code, so the checks can tell an existing subcommand from a new one."""

    def setUp(self):
        super().setUp()
        for d in ("bin", "scripts"):
            shutil.copytree(os.path.join(HOME, d), os.path.join(self.repo, d),
                            ignore=shutil.ignore_patterns("__pycache__"))
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "xv at the base"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        self.xv("step", "forecaster", "s1", cwd=self.wt)

    record = WatchLoopSetup.record
    amend = ScenarioChecksTest.amend
    scenario = ScenarioChecksTest.scenario
    assert_goes_on = ScenarioChecksTest.assert_goes_on
    assert_stops = ScenarioChecksTest.assert_stops

    # 3. an existing subcommand with no new flag is not raised
    def test_an_xv_subcommand_that_exists_at_the_base_is_not_raised_when_the_red_lacks_it(self):
        self.amend("A person runs `xv slice amend`.")
        self.assert_goes_on(self.scenario())

    def test_a_top_level_xv_command_that_exists_at_the_base_is_not_raised(self):
        self.amend("A person runs `xv decisions`.")
        self.assert_goes_on(self.scenario())

    def test_a_new_flag_on_an_existing_command_is_still_raised(self):
        self.amend("A person runs `xv slice new --priority high`.")
        self.assert_stops(self.scenario(), "--priority")

    def test_an_existing_command_does_not_hide_a_flag_beside_it(self):
        self.amend("A person runs `xv slice amend --expect-moves imports`.")
        p = self.scenario()
        self.assert_stops(p, "--expect-moves")
        self.assertNotIn("`xv slice amend`", json.loads(p.stdout)["stop"]["question"])

    def test_a_command_that_does_not_exist_at_the_base_is_still_raised(self):
        self.amend("A person runs `xv ghost <id>`.")
        self.assert_stops(self.scenario(), "xv ghost")

    def test_a_subcommand_that_does_not_exist_under_a_real_command_is_still_raised(self):
        self.amend("A person runs `xv slice ghost`.")
        self.assert_stops(self.scenario(), "xv slice ghost")

    # 2. a red_gaps name a person accepted is not raised again
    def accept_the_stop(self):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "fine, no test for it", "--next", "maker",
                cwd=self.wt)

    def test_a_gap_a_person_accepted_is_not_raised_when_the_scenario_step_runs_again(self):
        self.amend("A person runs `xv ghost <id>`.")
        self.assert_stops(self.scenario(), "xv ghost")
        self.accept_the_stop()
        self.assert_goes_on(self.scenario())

    def test_a_gap_that_is_a_flag_a_person_accepted_is_not_raised_again(self):
        self.amend("The list takes `--since <date>`.")
        self.assert_stops(self.scenario(), "--since")
        self.accept_the_stop()
        self.assert_goes_on(self.scenario())

    def test_a_gap_a_person_did_not_accept_is_still_raised_beside_an_accepted_one(self):
        self.amend("The list takes `--since <date>`.")
        self.assert_stops(self.scenario(), "--since")
        self.accept_the_stop()
        self.amend("Also `--until <date>`.")
        p = self.scenario()
        self.assert_stops(p, "--until")
        self.assertNotIn("--since", json.loads(p.stdout)["stop"]["question"])

    def test_a_gap_is_raised_again_when_no_person_accepted_it(self):
        self.amend("The list takes `--since <date>`.")
        self.assert_stops(self.scenario(), "--since")
        self.assert_stops(self.scenario(), "--since")

    # 8. a flag the xv command already has at the base is not raised
    def test_a_flag_the_command_has_at_the_base_is_not_raised(self):
        self.amend("A person runs `xv slice amend --scenario-file notes.md`.")
        self.assert_goes_on(self.scenario())

    def test_two_flags_the_command_has_at_the_base_are_not_raised(self):
        self.amend("A person runs `xv slice amend --scenario-file notes.md --by pat`.")
        self.assert_goes_on(self.scenario())

    def test_a_flag_the_base_command_lacks_is_raised_beside_one_it_has(self):
        self.amend("A person runs `xv slice amend --scenario-file notes.md --expect-moves imports`.")
        p = self.scenario()
        self.assert_stops(p, "--expect-moves")
        self.assertNotIn("--scenario-file", json.loads(p.stdout)["stop"]["question"])

    def test_a_flag_that_only_another_command_has_is_raised(self):
        self.amend("A person runs `xv slice amend --kind refactor`.")
        self.assert_stops(self.scenario(), "--kind")


class AdoptingReposShared(WatchLoopSetup):
    """The setup both adopting-repo classes share. It holds no tests, so neither inherits the other's."""

    amend = ScenarioChecksTest.amend
    scenario = ScenarioChecksTest.scenario
    assert_goes_on = ScenarioChecksTest.assert_goes_on
    assert_stops = ScenarioChecksTest.assert_stops

    def check_a_subcommand_the_installed_xv_has_is_not_raised(self):
        self.amend("A person runs `xv slice amend`.")
        self.assert_goes_on(self.scenario())

    def check_a_flag_the_installed_command_has_is_not_raised(self):
        self.amend("A person runs `xv slice amend --scenario-file notes.md`.")
        self.assert_goes_on(self.scenario())

    def check_a_command_the_installed_xv_lacks_is_raised(self):
        self.amend("A person runs `xv ghost <id>`.")
        self.assert_stops(self.scenario(), "xv ghost")

    def check_a_flag_the_installed_command_lacks_is_raised(self):
        self.amend("A person runs `xv slice amend --expect-moves imports`.")
        self.assert_stops(self.scenario(), "--expect-moves")


class AtAnAdoptingReposBaseTest(AdoptingReposShared):
    """9. A base without xv's source: points 3 and 8 check against the installed xv."""

    def setUp(self):
        super().setUp()
        self.xv("step", "forecaster", "s1", cwd=self.wt)

    def test_the_base_holds_no_xv_source(self):
        self.assertFalse(os.path.exists(os.path.join(self.wt, "scripts")))

    def test_a_subcommand_the_installed_xv_has_is_not_raised(self):
        self.check_a_subcommand_the_installed_xv_has_is_not_raised()

    def test_a_flag_the_installed_command_has_is_not_raised(self):
        self.check_a_flag_the_installed_command_has_is_not_raised()

    def test_a_command_the_installed_xv_lacks_is_raised(self):
        self.check_a_command_the_installed_xv_lacks_is_raised()

    def test_a_flag_the_installed_command_lacks_is_raised(self):
        self.check_a_flag_the_installed_command_lacks_is_raised()


class AtAnAdoptingReposBaseWithItsOwnBinAndScriptsTest(AdoptingReposShared):
    """9. The adopting repo has its own `bin/` and `scripts/`, but not xv's: the installed xv still answers."""

    def setUp(self):
        RepoCase.setUp(self)
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        os.makedirs(os.path.join(self.repo, "bin"), exist_ok=True)
        os.makedirs(os.path.join(self.repo, "scripts"), exist_ok=True)
        with open(os.path.join(self.repo, "bin", "deploy"), "w") as f:
            f.write("#!/bin/sh\necho deploy\n")
        with open(os.path.join(self.repo, "scripts", "build.py"), "w") as f:
            f.write("print('build')\n")
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qam", "fake agents and the adopting repo's own bin and scripts"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        self.xv("step", "forecaster", "s1", cwd=self.wt)

    def test_the_base_holds_no_xv_source(self):
        self.assertTrue(os.path.isdir(os.path.join(self.wt, "scripts")))
        self.assertTrue(os.path.isdir(os.path.join(self.wt, "bin")))
        self.assertFalse(os.path.exists(os.path.join(self.wt, "bin", "xv")))

    def test_a_subcommand_the_installed_xv_has_is_not_raised(self):
        self.check_a_subcommand_the_installed_xv_has_is_not_raised()

    def test_a_flag_the_installed_command_has_is_not_raised(self):
        self.check_a_flag_the_installed_command_has_is_not_raised()

    def test_a_command_the_installed_xv_lacks_is_raised(self):
        self.check_a_command_the_installed_xv_lacks_is_raised()

    def test_a_flag_the_installed_command_lacks_is_raised(self):
        self.check_a_flag_the_installed_command_lacks_is_raised()


class SliceOnlyFilesTest(WatchLoopSetup):
    """10. Marks on a file the config lists as always slice-only are accepted with no stop."""

    scenario = ScenarioChecksTest.scenario
    assert_goes_on = ScenarioChecksTest.assert_goes_on
    assert_stops = ScenarioChecksTest.assert_stops

    def run_marks(self, *checks, **extra):
        """One slice-only mark per `checks` value, each naming the file its test checks (`checks`)."""
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        out = []
        for i, c in enumerate(checks):
            m = {"file": "tests/test_red.py", "test": f"Red.test_line_{i}", "why": "one wording line"}
            if c is not MISSING:
                m["checks"] = c
            m.update(extra)
            out.append(m)
        return self.scenario(FAKE_REPORT_EXTRA=json.dumps({"slice_only": out}))

    def assert_marks_stop(self, p, *named):
        self.assert_stops(p, *named)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "slice_only_marks")

    def test_the_default_config_lists_changelog_as_always_slice_only(self):
        text = open(os.path.join(HOME, "defaults", "config.yml")).read()
        self.assertTrue(re.search(r"(?m)^\s*slice_only_files:.*CHANGELOG\.md", text), text)

    def test_this_repos_config_lists_changelog_as_always_slice_only(self):
        text = open(os.path.join(HOME, ".xv", "config.yml")).read()
        self.assertTrue(re.search(r"(?m)^\s*slice_only_files:.*CHANGELOG\.md", text), text)

    def test_a_mark_on_a_listed_file_goes_on_with_no_stop(self):
        self.assert_goes_on(self.run_marks("CHANGELOG.md"))

    def test_a_mark_on_a_listed_file_is_accepted_and_the_log_says_so(self):
        self.run_marks("CHANGELOG.md")
        self.assertEqual([m.get("accepted") for m in self.record()["slice_only"]], [True])
        log = self.xv("record", "show", "s1", cwd=self.wt).stdout
        line = next((l for l in log.splitlines() if "slice-only" in l and "CHANGELOG.md" in l
                     and "accepted" in l), None)
        self.assertIsNotNone(line, log)

    def test_a_mark_on_a_file_that_is_not_listed_still_stops(self):
        self.assert_marks_stop(self.run_marks("README.md"), "Red.test_line_0")

    def test_a_path_that_only_ends_in_a_listed_name_still_stops(self):
        self.assert_marks_stop(self.run_marks("docs/CHANGELOG.md"), "Red.test_line_0")

    def test_one_mark_on_an_unlisted_file_stops_beside_one_on_a_listed_file(self):
        p = self.run_marks("CHANGELOG.md", "README.md")
        self.assert_marks_stop(p, "Red.test_line_1")
        self.assertNotIn("Red.test_line_0", json.loads(p.stdout)["stop"]["question"])

    def test_a_mark_that_names_no_file_stops(self):
        self.assert_marks_stop(self.run_marks(MISSING), "Red.test_line_0")

    def test_a_mark_with_an_empty_file_name_stops(self):
        self.assert_marks_stop(self.run_marks(""), "Red.test_line_0")

    def test_a_mark_whose_file_is_not_a_string_stops(self):
        self.assert_marks_stop(self.run_marks(5), "Red.test_line_0")

    def test_a_mark_whose_file_is_a_list_stops(self):
        self.assert_marks_stop(self.run_marks(["CHANGELOG.md"]), "Red.test_line_0")

    def test_an_agent_that_claims_its_own_mark_accepted_on_an_unlisted_file_still_stops(self):
        self.assert_marks_stop(self.run_marks("README.md", accepted=True), "Red.test_line_0")

    def test_a_file_the_config_lists_is_accepted(self):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        open(cfg, "w").write(text.replace("tests:\n", 'tests:\n  slice_only_files: ["docs/NOTES.md"]\n', 1))
        sh(["git", "commit", "-qam", "list a file"], self.repo)
        wt = self.new_slice("s2", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s2", "budget", '{"usd": 1}', "--by", "pat", cwd=wt)
        self.xv("step", "forecaster", "s2", cwd=wt)
        from unittest import mock
        extra = {"slice_only": [{"file": "tests/test_red.py", "test": "Red.test_note", "why": "a note",
                                 "checks": "docs/NOTES.md"}]}
        with mock.patch.dict(os.environ, {"FAKE_REPORT_EXTRA": json.dumps(extra)}):
            p = self.xv("step", "scenario", "s2", cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)


class RemovedSliceOnlyTestInCoversTest(WatchLoopSetup):
    """11. A covers name for a slice-only test the cleaner removed does not stop the slice."""

    scenario = ScenarioChecksTest.scenario
    assert_goes_on = ScenarioChecksTest.assert_goes_on
    assert_stops = ScenarioChecksTest.assert_stops

    def removed(self, test="Red.test_cheese", **moved):
        """Pass one covers a cheese test and the milk test; the cleaner then removes the cheese test."""
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        extra = {"covered": [{"item": "milk today", "test": "test_milk_today"},
                            {"item": "cheese", "test": "test_cheese"}]}
        self.scenario(FAKE_RED_TEXT="def test_cheese(self): pass", FAKE_NOT_COVERED='[{"item": "x", "why": "y"}]',
                      FAKE_REPORT_EXTRA=json.dumps(extra))
        self.xv("record", "add", "s1", "slice_only", json.dumps(
            {"file": "tests/test_red.py", "test": "Red.test_cheese", "why": "one line", "accepted": True}),
            cwd=self.wt)
        move = {"file": "tests/test_red.py", "assertion": test, "why": "slice-only; removed", "by": "cleaner",
                "slice_only": True}
        move.update(moved)
        self.xv("record", "add", "s1", "moved_tests", json.dumps(move), cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "again", "--next", "scenario",
                "--settled", "Pat sent it back.", cwd=self.wt)

    def milk_only(self):
        return self.scenario(FAKE_REPORT_EXTRA=json.dumps(
            {"covered": [{"item": "milk today", "test": "test_milk_today"}]}))

    def test_a_kept_name_for_a_removed_slice_only_test_does_not_stop(self):
        self.removed()
        self.assert_goes_on(self.milk_only())

    def test_a_reported_name_for_a_removed_slice_only_test_does_not_stop(self):
        self.removed()
        extra = {"covered": [{"item": "milk today", "test": "test_milk_today"},
                            {"item": "cheese", "test": "Red.test_cheese"}]}
        self.assert_goes_on(self.scenario(FAKE_REPORT_EXTRA=json.dumps(extra)))

    def test_a_kept_name_goes_on_when_the_move_assertion_carries_the_cleaners_words(self):
        self.removed(test="Red.test_cheese; removed")
        self.assert_goes_on(self.milk_only())

    def test_a_reported_name_goes_on_when_the_move_assertion_carries_the_cleaners_words(self):
        self.removed(test="Red.test_cheese; removed")
        extra = {"covered": [{"item": "milk today", "test": "test_milk_today"},
                            {"item": "cheese", "test": "Red.test_cheese"}]}
        self.assert_goes_on(self.scenario(FAKE_REPORT_EXTRA=json.dumps(extra)))

    def test_a_name_still_stops_when_the_words_after_the_semicolon_name_another_test(self):
        self.removed(test="Red.test_gouda; removed")
        self.assert_stops(self.milk_only(), "test_cheese")

    def test_a_name_for_a_test_the_record_does_not_show_removed_still_stops(self):
        self.removed(test="Red.test_gouda")
        self.assert_stops(self.milk_only(), "test_cheese")

    def test_a_name_for_a_test_removed_by_the_maker_still_stops(self):
        self.removed(by="maker")
        self.assert_stops(self.milk_only(), "test_cheese")

    def test_a_name_for_a_removed_test_that_was_not_slice_only_still_stops(self):
        self.removed(slice_only=False)
        self.assert_stops(self.milk_only(), "test_cheese")


class ScenarioPointsAfterAmendTest(WatchLoopSetup):
    """5. After `xv slice amend` on a refactor slice, only the amendment's points need covers or not_covered."""

    def open_kind(self, kind):
        flags = ["--expect-moves", "imports"] if kind == "refactor" else []
        out = self.xv("slice", "new", "s2", "--by", "pat", "--kind", kind,
                      "--scenario", "1. Users see no change in the list.\n2. Users see no change in the tally.",
                      *flags).stdout
        self.wt = out.strip().splitlines()[-1]
        self.xv("record", "set", "s2", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        self.xv("step", "forecaster", "s2", cwd=self.wt)
        path = os.path.join(self.tmp, "amend.md")
        with open(path, "w") as f:
            f.write("3. The tally also shows milk.")
        self.xv("slice", "amend", "s2", "--by", "pat", "--scenario-file", path, cwd=self.wt)

    def run_scenario(self, covered):
        from unittest import mock
        extra = {"covered": [{"item": c, "test": "test_milk_today"} for c in covered], "not_covered": []}
        with mock.patch.dict(os.environ, {"FAKE_REPORT_EXTRA": json.dumps(extra)}):
            p = self.xv("step", "scenario", "s2", cwd=self.wt, check=False)
        return p, json.loads(self.xv("record", "show", "s2", "--json", cwd=self.wt).stdout)

    def test_a_refactor_slice_with_an_amendment_needs_only_the_amendments_point(self):
        self.open_kind("refactor")
        p, data = self.run_scenario(["3. The tally also shows milk."])
        self.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(data["next"], "maker")

    def test_a_refactor_slice_still_sends_back_an_amendment_point_that_is_not_covered(self):
        self.open_kind("refactor")
        p, data = self.run_scenario(["1", "2"])
        self.assertEqual(data["next"], "scenario")
        self.assertNotIn("maker", [s["step"] for s in data["spend"]])

    def test_a_feature_slice_with_an_amendment_still_needs_the_scenarios_own_points(self):
        self.open_kind("feature")
        p, data = self.run_scenario(["3. The tally also shows milk."])
        self.assertEqual(data["next"], "scenario")


def _red_command(lines, code=1):
    """A red command that prints these lines and exits with this code. It joins with `&&`, which the scenario check accepts."""
    import shlex
    return "printf '%s\\n' " + " ".join(shlex.quote(x) for x in lines) + f" && exit {code}"


# What each of the 11 runners that failing_tests reads says when it could not start or find a test.
CANNOT_RUN = {
    "unittest, a file that cannot load": ["ImportError: Failed to import test module: test_gone", "FAILED (errors=1)"],
    "unittest, no tests": ["Ran 0 tests in 0.000s", "NO TESTS RAN"],
    "pytest, no tests": ["collected 0 items", "no tests ran in 0.01s"],
    "pytest, a file that cannot load": ["ERROR collecting tests/test_gone.py", "Interrupted: 1 error during collection"],
    "jest, no tests": ["No tests found, exiting with code 1"],
    "jest, a suite that cannot load": ["Test suite failed to run", "Cannot find module './gone' from 'test/a.test.js'"],
    "vitest, no tests": ["No test files found, exiting with code 1"],
    "go, a package that does not build": ["FAIL\texample.com/pantry [build failed]"],
    "rspec, a file that cannot load": ["An error occurred while loading ./spec/a_spec.rb",
                                       "0 examples, 0 failures, 1 error occurred outside of examples"],
    "jasmine, no specs": ["No specs found"],
    "minitest, a file that cannot load": ["cannot load such file -- ./test/a_test.rb (LoadError)"],
    "minitest, no tests": ["0 runs, 0 assertions, 0 failures, 0 errors, 0 skips"],
    "mocha, no tests": ['Error: No test files found: "test/*.js"'],
    "cargo, a crate that does not build": ["error: could not compile `pantry` (lib test) due to 1 previous error"],
    "playwright, no tests": ["Error: No tests found."],
}


class RedCannotRunTest(WatchLoopSetup):
    """A red that fails before any test runs is not a failing red (scenario points 1 to 4)."""

    def scenario(self, command):
        from unittest import mock
        with mock.patch.dict(os.environ, {"FAKE_RED_COMMAND": command}):
            self.xv("step", "forecaster", "s1", cwd=self.wt)
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def assert_cannot_run(self, command, *named):
        p = self.scenario(command)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "red_cannot_run")
        self.assertEqual(stop["seat"], "originator")
        for n in named:
            self.assertIn(n, stop["question"])
        data = self.record()
        self.assertEqual(data["next"], "scenario")
        self.assertIsNot(data["checks"]["scenario"].get("red_fails"), True)
        self.assertNotIn("maker", [s["step"] for s in data["spend"]])

    def assert_failing_red(self, command):
        p = self.scenario(command)
        self.assertNotIn("red_cannot_run", p.stdout + p.stderr)
        self.assertIs(self.record()["checks"]["scenario"]["red_fails"], True)
        self.assertEqual(self.record()["next"], "maker")

    # 1. exit codes 126 and 127
    def test_exit_127_stops_and_names_the_error(self):
        self.assert_cannot_run(_red_command(["sh: 1: nosuchrunner: not found"], 127), "127")

    def test_exit_126_stops_and_names_the_error(self):
        self.assert_cannot_run(_red_command(["sh: 1: ./run-tests: Permission denied"], 126), "126")

    def test_a_command_that_is_not_installed_stops(self):
        self.assert_cannot_run("xv-no-such-runner-anywhere tests", "127")

    # 2. a general error name counts only when the output names no real failing test
    def test_a_general_error_name_alone_stops(self):
        self.assert_cannot_run(_red_command(["Traceback (most recent call last):",
                                             "ImportError: No module named pantry_gone"]), "ImportError")

    def test_no_such_file_alone_stops(self):
        self.assert_cannot_run(_red_command(["python3: can't open file 'tests/gone.py': [Errno 2] No such file "
                                             "or directory"]), "No such file or directory")

    # 3. a red that runs its tests and some fail is a failing red, even with a general error name in the output
    def test_failing_tests_with_a_general_error_name_in_the_output_is_a_failing_red(self):
        self.assert_failing_red(_red_command(["ERROR: test_milk (tests.t.A.test_milk)",
                                              "ImportError: cannot import name 'gone' from 'pantry'",
                                              "FAILED (errors=1)"]))

    def test_a_failing_test_that_prints_no_such_file_is_a_failing_red(self):
        self.assert_failing_red(_red_command(["FAIL: test_milk (tests.t.A.test_milk)",
                                              "FileNotFoundError: [Errno 2] No such file or directory: 'x'"]))

    # 4. one file cannot load and other tests fail for real: the step still stops
    def test_a_file_that_cannot_load_beside_a_real_failure_still_stops(self):
        self.assert_cannot_run(_red_command(["ERROR: test_gone (unittest.loader._FailedTest.test_gone)",
                                             "ImportError: Failed to import test module: test_gone",
                                             "FAIL: test_milk (tests.t.A.test_milk)", "FAILED (failures=1, errors=1)"]),
                               "Failed to import test module: test_gone")

    def test_a_pytest_collection_error_beside_a_real_failure_still_stops(self):
        self.assert_cannot_run(_red_command(["ERROR collecting tests/test_gone.py",
                                             "FAILED tests/test_a.py::test_milk - assert 1 == 2",
                                             "Interrupted: 1 error during collection"]), "error during collection")


    # 2. the runner words of each of the 11 runners, one plain test per sample
    def assert_runner_words_stop(self, what):
        lines = CANNOT_RUN[what]
        self.assert_cannot_run(_red_command(lines), lines[0])

    def test_runner_words_stop_00_cargo_a_crate_that_does_not_build(self):
        self.assert_runner_words_stop("cargo, a crate that does not build")

    def test_runner_words_stop_01_go_a_package_that_does_not_build(self):
        self.assert_runner_words_stop("go, a package that does not build")

    def test_runner_words_stop_02_jasmine_no_specs(self):
        self.assert_runner_words_stop("jasmine, no specs")

    def test_runner_words_stop_03_jest_a_suite_that_cannot_load(self):
        self.assert_runner_words_stop("jest, a suite that cannot load")

    def test_runner_words_stop_04_jest_no_tests(self):
        self.assert_runner_words_stop("jest, no tests")

    def test_runner_words_stop_05_minitest_a_file_that_cannot_load(self):
        self.assert_runner_words_stop("minitest, a file that cannot load")

    def test_runner_words_stop_06_minitest_no_tests(self):
        self.assert_runner_words_stop("minitest, no tests")

    def test_runner_words_stop_07_mocha_no_tests(self):
        self.assert_runner_words_stop("mocha, no tests")

    def test_runner_words_stop_08_playwright_no_tests(self):
        self.assert_runner_words_stop("playwright, no tests")

    def test_runner_words_stop_09_pytest_a_file_that_cannot_load(self):
        self.assert_runner_words_stop("pytest, a file that cannot load")

    def test_runner_words_stop_10_pytest_no_tests(self):
        self.assert_runner_words_stop("pytest, no tests")

    def test_runner_words_stop_11_rspec_a_file_that_cannot_load(self):
        self.assert_runner_words_stop("rspec, a file that cannot load")

    def test_runner_words_stop_12_unittest_a_file_that_cannot_load(self):
        self.assert_runner_words_stop("unittest, a file that cannot load")

    def test_runner_words_stop_13_unittest_no_tests(self):
        self.assert_runner_words_stop("unittest, no tests")

    def test_runner_words_stop_14_vitest_no_tests(self):
        self.assert_runner_words_stop("vitest, no tests")


class AnsweredStopStaysAnsweredTest(WatchLoopSetup):
    """Scenario points 5 and 6: a bundled slice_only_marks is accepted, and a directed edit does not re-fire."""

    MARK = {"file": "tests/test_red.py", "test": "test_milk_today", "why": "checks the README wording",
            "checks": "README.md"}
    EDIT = ("--edit", "README.md", "--old", "It is small on purpose.",
            "--new", "It is small on purpose, and stays small.", "--kind", "doc")

    def scenario_with_not_covered(self):
        from unittest import mock
        env = {"FAKE_NOT_COVERED": '[{"item": "the grocer share", "why": "no seam"}]'}
        with mock.patch.dict(os.environ, env):
            self.xv("step", "forecaster", "s1", cwd=self.wt)
            return self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def open_stops(self):
        return [s for s in self.record()["stops"] if s.get("answer") is None]

    def add_mark(self):
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.MARK), cwd=self.wt)

    def test_an_answer_that_bundles_slice_only_marks_accepts_them(self):
        self.scenario_with_not_covered()
        self.add_mark()
        self.assertFalse(self.record()["slice_only"][0].get("accepted"))
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "fine", "--bundle", "slice_only_marks",
                "--next", "maker", "--settled", "Pat accepts the marks.", cwd=self.wt)
        self.assertIs(self.record()["slice_only"][0].get("accepted"), True)

    def test_an_answer_that_does_not_bundle_them_leaves_them_unaccepted(self):
        self.scenario_with_not_covered()
        self.add_mark()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "fine", "--next", "maker",
                "--settled", "Pat goes on.", cwd=self.wt)
        self.assertFalse(self.record()["slice_only"][0].get("accepted"))

    def directed_answer(self, *extra):
        self.xv("record", "offer", "s1", "--option", "Make the edit", "--settles", "The edit is made.", *self.EDIT,
                "--option", "Leave it", "--settles", "Nothing changes.", cwd=self.wt)
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "make it", "--pick", "1",
                       "--next", "maker", *extra, cwd=self.wt, check=False)

    def test_after_a_directed_edit_the_stop_the_answer_closed_does_not_fire_again(self):
        self.scenario_with_not_covered()
        before = len(self.record()["stops"])
        p = self.directed_answer()
        v = json.loads(p.stdout)
        self.assertNotIn("red_misses_scenario", [f["order"] for f in v["fired"]])
        self.assertIsNone(v["stop"], p.stdout)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertEqual(len(data["stops"]), before, "no new stop in the record")
        self.assertEqual(self.open_stops(), [])
        self.assertEqual(data["next"], "maker", "the answer's --next stands")
        self.assertEqual(data["suite"], "green", "the suite still runs after the edit")

    def test_after_a_directed_edit_a_stop_bundled_with_the_answer_does_not_fire_again(self):
        self.scenario_with_not_covered()
        self.add_mark()
        before = len(self.record()["stops"])
        p = self.directed_answer("--bundle", "slice_only_marks")
        v = json.loads(p.stdout)
        self.assertNotIn("slice_only_marks", [f["order"] for f in v["fired"]])
        self.assertNotIn("red_misses_scenario", [f["order"] for f in v["fired"]])
        self.assertEqual(len(self.record()["stops"]), before)
        self.assertIs(self.record()["slice_only"][0].get("accepted"), True)

    def test_after_a_directed_edit_a_ready_to_merge_bundled_with_the_answer_does_not_fire_again(self):
        self.scenario_with_not_covered()
        before = len(self.record()["stops"])
        p = self.directed_answer("--bundle", "ready_to_merge")
        v = json.loads(p.stdout)
        self.assertNotIn("ready_to_merge", [f["order"] for f in v["fired"]])
        self.assertEqual(len(self.record()["stops"]), before)
        self.assertEqual(self.record()["next"], "maker")


class SliceNewInputsTest(RepoCase):
    """defects-tools 13 and 14: `xv slice new` checks its input paths first, and --ignore can repeat."""

    def branches(self):
        return sh(["git", "branch", "--list", "xv/*"], self.repo).stdout.strip()

    def nothing_made(self):
        self.assertEqual(self.branches(), "", "a branch was made")
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", "s1")), "a worktree was made")

    def refused(self, *flags):
        p = self.xv("slice", "new", "s1", "--by", "pat", *flags, check=False)
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertNotIn("Traceback", p.stderr)
        self.nothing_made()
        return p

    def test_a_missing_recording_path_is_refused_before_any_branch_or_worktree(self):
        p = self.refused("--scenario", "x", "--kind", "defect", "--recording", "/no/such/recording.har")
        self.assertIn("/no/such/recording.har", p.stderr)

    def test_a_missing_scenario_file_is_refused_before_any_branch_or_worktree(self):
        p = self.refused("--scenario-file", "/no/such/scenario.md")
        self.assertIn("/no/such/scenario.md", p.stderr)

    def may_ignore(self, *values):
        flags = [x for v in values for x in ("--ignore", v)]
        wt = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "x", *flags).stdout.strip().splitlines()[-1]
        with open(os.path.join(wt, ".xv", "slices", "s1.md")) as f:
            text = f.read()
        return text.split("## May ignore\n", 1)[1].split("\n## ", 1)[0].strip()

    def test_a_repeated_ignore_gives_a_bullet_list_in_order(self):
        self.assertEqual(self.may_ignore("First thing.", "Second thing.", "Third thing."),
                         "- First thing.\n- Second thing.\n- Third thing.")

    def test_a_single_ignore_stays_a_plain_paragraph(self):
        self.assertEqual(self.may_ignore("Only thing."), "Only thing.")


if __name__ == "__main__":
    unittest.main()

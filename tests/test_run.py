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


if __name__ == "__main__":
    unittest.main()

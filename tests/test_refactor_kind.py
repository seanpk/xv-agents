import json
import os
import sys
from unittest import mock

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")
SCENARIO = "Users see no change. Restructure StoreTest in tests/test_store.py."


class RefactorKindCase(RepoCase):
    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)

    def open_slice(self, *flags, check=True):
        p = self.xv("slice", "new", "s1", "--by", "pat", "--kind", "refactor", "--scenario", SCENARIO,
                    *flags, check=check)
        if p.returncode == 0:
            self.wt = p.stdout.strip().splitlines()[-1]
            self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        return p

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def maker_after_scenario(self, env=None):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.xv("step", "scenario", "s1", cwd=self.wt)
        with mock.patch.dict(os.environ, env or {}):
            return self.xv("step", "maker", "s1", cwd=self.wt, check=False)

    def stop_order(self, p):
        stop = json.loads(p.stdout).get("stop")
        return stop and stop["order"]

    # 1. the kind
    def test_slice_new_opens_a_refactor_slice(self):
        self.open_slice()
        self.assertEqual(self.record()["kind"], "refactor")
        self.assertIn(SCENARIO, open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read())

    # 2. the scenario step
    def test_the_scenario_step_writes_no_red_and_goes_on_to_the_maker(self):
        self.open_slice()
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.wt, "tests", "test_red.py")))
        self.assertEqual(self.record()["next"], "maker")

    def test_the_scenario_step_stops_when_the_suite_is_not_green_at_the_start(self):
        self.open_slice()
        with open(os.path.join(self.wt, "tests", "test_broken.py"), "w") as f:
            f.write("import unittest\n\n\nclass B(unittest.TestCase):\n    def test_b(self):\n"
                    "        self.assertEqual(1, 2)\n")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "a red suite"], self.wt)
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertIsNotNone(self.stop_order(p))
        self.assertNotEqual(self.record()["next"], "maker")

    # 3 and 4. the maker's brief
    def test_the_makers_brief_for_a_refactor_slice_lifts_the_no_refactor_line_and_names_amend(self):
        self.open_slice()
        refactor = self.xv("prompt", "maker", "s1", cwd=self.wt).stdout
        self.assertIn("refactor slice", refactor.lower())
        self.assertIn("xv slice amend", refactor)

    def test_the_makers_brief_for_a_feature_slice_does_not_mention_a_refactor_slice(self):
        self.wt = self.new_slice("s2")
        feature = self.xv("prompt", "maker", "s2", cwd=self.wt).stdout
        self.assertNotIn("refactor slice", feature.lower())

    # 5 and 9. the flags
    def test_a_kind_of_move_that_is_not_imports_or_renames_is_refused(self):
        self.assertEqual(self.open_slice("--expect-moves", "imports", check=False).returncode, 0)
        for bad in ("bogus", "", "imports,bogus"):
            p = self.xv("slice", "new", "s2", "--by", "pat", "--kind", "refactor", "--scenario", SCENARIO,
                        "--expect-moves", bad, check=False)
            self.assertNotEqual(p.returncode, 0, bad)
            self.assertNotIn("unrecognized arguments", p.stderr)

    def test_both_kinds_are_accepted_together(self):
        p = self.open_slice("--expect-moves", "imports,renames", "--rename", "Foo=Bar", "--rename", "A=B",
                            check=False)
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_a_rename_pair_needs_both_names_and_an_equals_sign(self):
        self.assertEqual(self.open_slice("--expect-moves", "renames", "--rename", "Foo=Bar",
                                         check=False).returncode, 0)
        for bad in ("Foo", "=Bar", "Foo=", ""):
            p = self.xv("slice", "new", "s2", "--by", "pat", "--kind", "refactor", "--scenario", SCENARIO,
                        "--expect-moves", "renames", "--rename", bad, check=False)
            self.assertNotEqual(p.returncode, 0, bad)
            self.assertNotIn("unrecognized arguments", p.stderr)

    # 6, 7, 8. the moves
    def test_an_import_only_change_to_an_old_test_is_an_expected_move(self):
        self.open_slice("--expect-moves", "imports")
        p = self.maker_after_scenario({"FAKE_MAKER_IMPORT_MOVE": "1"})
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("tests/test_store.py", [m["file"] for m in self.record()["moved_tests"]])

    def test_the_same_import_change_stops_when_the_slice_did_not_expect_imports(self):
        self.open_slice()
        p = self.maker_after_scenario({"FAKE_MAKER_IMPORT_MOVE": "1"})
        self.assertEqual(self.stop_order(p), "unrecorded_move")

    def test_a_changed_assertion_still_stops_when_imports_are_expected(self):
        self.open_slice("--expect-moves", "imports")
        p = self.maker_after_scenario({"FAKE_MAKER_CHEATS": "1"})
        self.assertEqual(self.stop_order(p), "unrecorded_move")

    def test_a_file_moved_to_a_new_path_with_the_named_rename_is_an_expected_move(self):
        self.open_slice("--expect-moves", "renames", "--rename", "StoreTest=StockTest")
        p = self.maker_after_scenario({"FAKE_MAKER_RENAME_MOVE": "1"})
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("tests/test_stock.py", [m["file"] for m in self.record()["moved_tests"]])

    def test_a_rename_the_slice_did_not_name_stops(self):
        self.open_slice("--expect-moves", "renames", "--rename", "Other=Name")
        p = self.maker_after_scenario({"FAKE_MAKER_RENAME_MOVE": "1"})
        self.assertEqual(self.stop_order(p), "unrecorded_move")

    def test_a_rename_stops_when_only_imports_are_expected(self):
        self.open_slice("--expect-moves", "imports", "--rename", "StoreTest=StockTest")
        p = self.maker_after_scenario({"FAKE_MAKER_RENAME_MOVE": "1"})
        self.assertEqual(self.stop_order(p), "unrecorded_move")

    def test_a_moved_file_with_a_changed_assertion_stops_even_with_the_rename_named(self):
        self.open_slice("--expect-moves", "renames", "--rename", "StoreTest=StockTest")
        p = self.maker_after_scenario({"FAKE_MAKER_RENAME_MOVE": "1", "FAKE_MAKER_CHEATS": "1"})
        self.assertEqual(self.stop_order(p), "unrecorded_move")

    # 7 and 10. no accept_moves stop for an expected move
    def test_expected_moves_reach_the_merge_stop_without_accept_moves(self):
        self.open_slice("--expect-moves", "imports")
        with mock.patch.dict(os.environ, {"FAKE_MAKER_IMPORT_MOVE": "1"}):
            p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(self.stop_order(p), "ready_to_merge", p.stdout)

    def test_an_unexpected_recorded_move_still_stops_for_the_person(self):
        self.open_slice("--expect-moves", "imports")
        with mock.patch.dict(os.environ, {"FAKE_MAKER_IMPORT_MOVE": "1", "FAKE_MAKER_MOVES": "1"}):
            p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(self.stop_order(p), "accept_moves", p.stdout)

    # 11. the packet's expected_moves count
    def packet_problems(self, expected, flags=("--expect-moves", "imports")):
        self.open_slice(*flags)
        env = {"FAKE_PACKET_EXPECTED_MOVES": expected}
        if flags:
            env["FAKE_MAKER_IMPORT_MOVE"] = "1"
        with mock.patch.dict(os.environ, env):
            self.xv("run", "s1", cwd=self.wt, check=False)
        return self.record()["checks"]["guardian"].get("packet_problems") or []

    def test_a_packet_whose_expected_moves_match_the_record_has_no_problem(self):
        self.assertEqual(self.packet_problems("1"), [])

    def test_a_packet_with_expected_moves_zero_is_fine_when_the_record_holds_none(self):
        self.assertEqual(self.packet_problems("0", flags=()), [])

    def test_a_packet_without_expected_moves_is_a_problem(self):
        self.assertTrue(any("expected_moves" in p for p in self.packet_problems("omit")))

    def test_a_packet_whose_expected_moves_is_not_a_whole_number_is_a_problem(self):
        self.assertTrue(any("expected_moves" in p for p in self.packet_problems("many")))

    def test_a_packet_whose_expected_moves_differs_from_the_record_is_a_problem(self):
        self.assertTrue(any("expected_moves" in p for p in self.packet_problems("2")))

    def test_a_packet_claiming_zero_when_the_record_holds_one_is_a_problem(self):
        self.assertTrue(any("expected_moves" in p for p in self.packet_problems("0")))


class FollowUpBase(RepoCase):
    """Helpers for points 12 and 13 and the cleaner's moves; it holds no test."""

    agent = FAKE

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{self.agent}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)

    def open_slice(self, *flags, kind="refactor"):
        p = self.xv("slice", "new", "s1", "--by", "pat", "--kind", kind, "--scenario", SCENARIO, *flags)
        self.wt = p.stdout.strip().splitlines()[-1]
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def run_slice(self, env):
        with mock.patch.dict(os.environ, env):
            p = self.xv("run", "s1", cwd=self.wt, check=False)
        return json.loads(p.stdout).get("stop") or {}


class ExpectedMovesStopCase(FollowUpBase):
    # 12. a wrong expected_moves stops
    def test_a_packet_without_expected_moves_stops_the_originator(self):
        self.open_slice()
        stop = self.run_slice({"FAKE_PACKET_EXPECTED_MOVES": "omit"})
        self.assertEqual((stop.get("order"), stop.get("seat")), ("expected_moves_wrong", "originator"))

    def test_a_packet_whose_expected_moves_is_not_a_number_stops_the_originator(self):
        self.open_slice()
        self.assertEqual(self.run_slice({"FAKE_PACKET_EXPECTED_MOVES": "many"}).get("order"),
                         "expected_moves_wrong")

    def test_a_packet_whose_expected_moves_differs_from_the_record_stops_the_originator(self):
        self.open_slice("--expect-moves", "imports")
        stop = self.run_slice({"FAKE_PACKET_EXPECTED_MOVES": "0", "FAKE_MAKER_IMPORT_MOVE": "1"})
        self.assertEqual(stop.get("order"), "expected_moves_wrong")

    def test_the_expected_moves_stop_applies_to_a_feature_slice_too(self):
        self.open_slice(kind="feature")
        self.assertEqual(self.run_slice({"FAKE_PACKET_EXPECTED_MOVES": "3"}).get("order"), "expected_moves_wrong")

    def test_a_packet_whose_expected_moves_matches_does_not_stop_with_it(self):
        self.open_slice("--expect-moves", "imports")
        stop = self.run_slice({"FAKE_PACKET_EXPECTED_MOVES": "1", "FAKE_MAKER_IMPORT_MOVE": "1"})
        self.assertEqual(stop.get("order"), "ready_to_merge")


class AmendedRefactorCase(FollowUpBase):
    # 13. an amend on a refactor slice gets a red
    def amended(self):
        self.open_slice()
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        f = os.path.join(self.tmp, "amend.md")
        with open(f, "w") as fh:
            fh.write("12. The tally also shows milk.")
        self.xv("slice", "amend", "s1", "--by", "pat", "--scenario-file", f, cwd=self.wt)
        self.assertEqual(self.record()["next"], "scenario")
        self.xv("step", "scenario", "s1", cwd=self.wt, check=False)

    def test_an_amended_refactor_slice_writes_a_red_for_the_amendment(self):
        self.amended()
        red = self.record()["red"]
        self.assertIsNotNone(red)
        self.assertIn("tests/test_red.py", red["files"])
        self.assertTrue(os.path.exists(os.path.join(self.wt, "tests", "test_red.py")))

    def test_the_amendments_red_must_fail_before_the_maker_runs(self):
        self.amended()
        self.assertIs(self.record()["checks"]["scenario"].get("red_fails"), True)


class CleanerMoveCase(FollowUpBase):
    # 6 and 7. a move the cleaner makes in an expected kind
    agent = os.path.join(HOME, "tests", "fake_cleaner_agent.py")

    def test_an_import_change_the_cleaner_makes_is_an_expected_move_and_does_not_stop(self):
        self.open_slice("--expect-moves", "imports")
        stop = self.run_slice({})
        self.assertEqual(stop.get("order"), "ready_to_merge", stop)
        self.assertIn("tests/test_store.py", [m["file"] for m in self.record()["moved_tests"] if m.get("expected")])

    def test_the_same_import_change_by_the_cleaner_still_stops_when_imports_are_not_expected(self):
        self.open_slice()
        self.assertEqual(self.run_slice({}).get("order"), "accept_moves")


# What a person should watch on the first green run: open a refactor slice with
# `--expect-moves imports`, let the maker add an import to an old test, and see the
# slice reach the merge stop with no accept_moves question; then change one assertion
# and see the stop come back.

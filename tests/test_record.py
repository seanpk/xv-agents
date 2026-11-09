import ast
import json
import os
import unittest

from helpers import HOME, RepoCase, sh

import record


class SliceRecordTest(RepoCase):
    def test_slice_new_makes_branch_worktree_and_record(self):
        wt = self.new_slice("s1")
        self.assertTrue(os.path.exists(os.path.join(wt, ".xv", "slices", "s1.md")))
        self.assertEqual(sh(["git", "branch", "--show-current"], wt).stdout.strip(), "xv/s1")
        data = json.loads(self.xv("record", "show", "s1", "--json").stdout)
        self.assertEqual((data["set_by"], data["next"], data["status"]), ("pat", "forecaster", "open"))
        self.assertTrue(data["base"])

    def test_a_record_needs_who_and_what(self):
        self.new_slice("s1")
        p = self.xv("record", "new", "s2", "--scenario", "x", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--by", p.stderr)

    def test_a_list_field_is_appended_not_overwritten(self):
        wt = self.new_slice("s1")
        p = self.xv("record", "set", "s1", "moved_tests", "[]", cwd=wt, check=False)
        self.assertIn("xv record add", p.stderr)
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "a", "--why", "b", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"][0]["file"], "tests/test_store.py")

    def test_a_budget_is_set_by_a_person(self):
        wt = self.new_slice("s1")
        p = self.xv("record", "set", "s1", "budget", '{"usd": 2}', cwd=wt, check=False)
        self.assertIn("--by", p.stderr)
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=wt)
        self.xv("record", "set", "s1", "budget", '{"usd": 4}', "--by", "pat", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["budget"], {"usd": 4, "set_by": "pat", "raised_from": {"usd": 2}})

    def test_a_two_person_stop_needs_two_names_and_writes_a_decision(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Shape?", cwd=wt)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", cwd=wt, check=False)
        self.assertIn("two people", p.stderr)
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "go", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["stops"][0]["answered_by"], ["pat", "sam"])
        rec = os.path.join(wt, data["decisions"][0]["record"])
        self.assertIn('who: ["pat", "sam"]', open(rec).read())

    def test_report_block_is_applied(self):
        wt = self.new_slice("s1")
        out = ('done.\n```xv-report\n{"agent": "maker", "status": "green", "summary": "ok", '
               '"moved_tests": [{"file": "tests/a.py", "assertion": "x", "why": "y"}]}\n```\n')
        p = sh(["python3", os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "xv"),
                "record", "report", "s1", "maker", "-"], wt)
        self.assertIn("no-report", p.stdout)
        path = os.path.join(self.tmp, "out.txt")
        open(path, "w").write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "maker", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"][0]["by"], "maker")


class GuardianReportTest(RepoCase):
    def test_the_guardians_count_of_moved_tests_is_not_a_record(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write('```xv-report\n{"agent": "guardian", "status": "done", "moved_tests": 2, '
                    '"shape_change": "no", "pitch_contradiction": "no"}\n```\n')
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"], [])


class GuideTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "spend", json.dumps(
            {"step": "maker", "harness": "claude", "model": "sonnet", "tokens_in": 1000, "tokens_out": 200,
             "tokens": 1200, "usd": 0.5, "wall_s": 30}), cwd=self.wt)

    def test_append_once_per_slice(self):
        self.xv("record", "guide-append", "s1", "--why", "first try", cwd=self.wt)
        p = self.xv("record", "guide-append", "s1", "--why", "again", cwd=self.wt, check=False)
        self.assertIn("already has s1", p.stderr)

    def test_verify_refuses_an_edit_and_allows_a_revert(self):
        self.xv("record", "guide-append", "s1", "--why", "first try", cwd=self.wt)
        sh(["git", "commit", "-qam", "row"], self.wt)
        guide = os.path.join(self.wt, ".xv", "estimation.md")
        text = open(guide).read()
        open(guide, "w").write(text.replace("first try", "a better story"))
        p = self.xv("record", "guide-verify", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("edited in place", p.stderr)
        rows = [l for l in text.splitlines() if not l.startswith("| s1 ")]
        open(guide, "w").write("\n".join(rows) + "\n")
        self.xv("record", "guide-verify", cwd=self.wt)

    def test_the_header_matches_the_default_file(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(open(os.path.join(here, "defaults", "estimation.md")).read(), record.GUIDE_HEADER)


if __name__ == "__main__":
    unittest.main()


class SoloTest(RepoCase):
    def test_solo_lets_one_person_answer_a_two_person_stop_and_says_so(self):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace('two_people: "any two of the household"', "two_people: solo")
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "solo"], self.repo)
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Shape?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "keep the new module", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertTrue(data["stops"][0]["solo"])
        self.assertIn("Decided by one person", open(os.path.join(wt, data["decisions"][0]["record"])).read())


class PitchFirstTest(RepoCase):
    def test_no_slice_starts_before_the_pitch_is_written(self):
        path = os.path.join(self.repo, ".xv", "pitch.md")
        open(path, "w").write("---\nstatus: not written\n---\n\n# The pitch\n")
        sh(["git", "commit", "-qam", "unwritten pitch"], self.repo)
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "x", check=False)
        self.assertIn("the pitch comes first", p.stderr)


RED = {"files": ["tests/test_x.py", "tests/test_y.py"],
       "command": "python3 -m unittest tests.test_x tests.test_y",
       "failure": "AssertionError: nope", "watch_first_green": None}


class MovedRedFilesTest(RepoCase):
    def report(self, wt, report):
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write("done.\n```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=wt)

    def slice_with_red(self, red=RED):
        wt = self.new_slice("s1")
        self.report(wt, {"agent": "scenario", "status": "red", "summary": "r", "red": red})
        return wt

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def test_a_file_moved_to_a_new_path_is_followed_in_red_files_and_command(self):
        wt = self.slice_with_red()
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--to", "tests/test_store.py",
                "--assertion", "a", "--why", "belongs with the store tests", cwd=wt)
        red = self.show(wt)["red"]
        self.assertEqual(red["files"], ["tests/test_store.py", "tests/test_y.py"])
        self.assertEqual(red["command"], "python3 -m unittest tests.test_store tests.test_y")

    def test_a_deleted_file_leaves_red_files_and_command(self):
        wt = self.slice_with_red()
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--deleted",
                "--assertion", "a", "--why", "only proved the slice did its job", cwd=wt)
        red = self.show(wt)["red"]
        self.assertEqual(red["files"], ["tests/test_y.py"])
        self.assertEqual(red["command"], "python3 -m unittest tests.test_y")

    def test_deleting_the_last_red_file_empties_files_and_nulls_command_and_logs_why(self):
        wt = self.slice_with_red({"files": ["tests/test_x.py"], "command": "python3 -m unittest tests.test_x",
                                  "failure": "f", "watch_first_green": None})
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--deleted",
                "--assertion", "a", "--why", "slice only", cwd=wt)
        data = self.show(wt)
        self.assertEqual(data["red"]["files"], [])
        self.assertIsNone(data["red"]["command"])
        log = open(os.path.join(wt, ".xv", "slices", "s1.md")).read()
        self.assertIn("red.command", log)

    def test_a_move_of_a_file_red_does_not_name_leaves_red_alone(self):
        wt = self.slice_with_red()
        self.xv("record", "move", "s1", "--file", "tests/test_other.py", "--deleted",
                "--assertion", "a", "--why", "w", cwd=wt)
        self.assertEqual(self.show(wt)["red"], RED)


class SliceOnlyReportTest(RepoCase):
    def test_the_scenario_reports_slice_only_tests_and_the_record_keeps_them(self):
        wt = self.new_slice("s1")
        slice_only = [{"file": "tests/test_x.py", "test": "test_file_is_ts",
                       "why": "only proves the file is .ts, not .js"}]
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(
                {"agent": "scenario", "status": "red", "summary": "r", "red": RED,
                 "slice_only": slice_only}) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["slice_only"], slice_only)


class MoveSliceOnlyTest(RepoCase):
    # #173: --slice-only marks the move whether or not the test is in the record's slice_only list
    def test_slice_only_on_a_test_not_in_the_slice_only_list_marks_the_move(self):
        wt = self.new_slice("s1")
        self.assertEqual(json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["slice_only"], [])
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "test_gone; removed",
                "--why", "only proved the slice did its job", "--slice-only", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertIs(data["moved_tests"][0].get("slice_only"), True)

    def test_a_move_without_the_flag_is_not_marked(self):
        wt = self.new_slice("s1")
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "test_gone; removed",
                "--why", "w", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertNotIn("slice_only", data["moved_tests"][0])


class ScenarioBriefRetroFixesTest(RepoCase):
    fixture = False

    def lines(self):
        text = open(os.path.join(HOME, "skills", "scenario", "SKILL.md")).read()
        return [ln.lower() for ln in text.splitlines()]

    # #174 point 5
    def test_the_brief_says_a_red_that_fails_only_on_the_build_is_reported_and_does_not_stop(self):
        found = [ln for ln in self.lines() if "from a build" in ln and "fails only on the build" in ln]
        self.assertTrue(found, "no line says what a red that fails only on the build means on a slice from a build")
        self.assertTrue(any("report" in ln and ("not stop" in ln or "no stop" in ln) for ln in found), found)

    # #174 point 6
    def test_the_brief_says_to_run_the_red_in_the_foreground_to_its_end_before_the_report(self):
        found = [ln for ln in self.lines() if "foreground" in ln]
        self.assertTrue(found, "the brief does not say to run the red command in the foreground")
        self.assertTrue(any("to its end" in ln and "before" in ln and "report" in ln for ln in found), found)

    # 7. a one-time CHANGELOG line
    def test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes(self):
        text = open(os.path.join(HOME, "CHANGELOG.md")).read()
        unreleased = text.split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        for issue in ("#172", "#173", "#174"):
            self.assertIn(issue, unreleased)
        self.assertTrue(any("scenario" in ln and "#174" in ln for ln in unreleased.splitlines()),
                        "no line about the scenario brief change")


class ScenarioBriefTest(RepoCase):
    fixture = False

    def test_the_brief_asks_for_the_existing_test_file_and_a_new_one_only_when_none_exists(self):
        text = open(os.path.join(HOME, "skills", "scenario", "SKILL.md")).read()
        step6 = [ln for ln in text.splitlines() if ln.startswith("6.")][0]
        self.assertNotIn("new files where you can", step6)
        self.assertIn("existing test file", step6)
        self.assertIn("slice_only", text)

    def test_the_brief_asks_for_the_whole_red_after_the_maker(self):
        text = open(os.path.join(HOME, "skills", "scenario", "SKILL.md")).read()
        self.assertIn("after the maker", text.lower())
        self.assertIn("every file in the record's `red.files`", text)
        self.assertIn("one command that runs all of them", text)


BARE = {"files": ["tests/test_x.py", "tests/test_y.py"],
        "command": "cd tests && python3 -m unittest test_x test_y",
        "failure": "AssertionError: nope", "watch_first_green": None}


class BareModuleCommandTest(RepoCase):
    """This repo's own red.command names modules from inside tests/, not as tests.test_x."""

    def slice_with_red(self, red):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(
                {"agent": "scenario", "status": "red", "summary": "r", "red": red}) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=wt)
        return wt

    def command(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["red"]["command"]

    def test_a_moved_file_is_followed_in_the_bare_module_form(self):
        wt = self.slice_with_red(BARE)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--to", "tests/test_store.py",
                "--assertion", "a", "--why", "w", cwd=wt)
        self.assertEqual(self.command(wt), "cd tests && python3 -m unittest test_store test_y")

    def test_a_deleted_file_leaves_the_bare_module_form(self):
        wt = self.slice_with_red(BARE)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--deleted",
                "--assertion", "a", "--why", "w", cwd=wt)
        self.assertEqual(self.command(wt), "cd tests && python3 -m unittest test_y")

    def test_the_log_says_updated_only_when_the_command_changed(self):
        red = {"files": ["tests/test_x.py"], "command": "make check", "failure": "f",
               "watch_first_green": None}
        wt = self.slice_with_red(red)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--to", "tests/test_store.py",
                "--assertion", "a", "--why", "w", cwd=wt)
        self.assertEqual(self.command(wt), "make check")
        log = open(os.path.join(wt, ".xv", "slices", "s1.md")).read()
        self.assertNotIn("red.command updated", log)


class SliceOnlyMoveTest(RepoCase):
    def move(self, sid, wt, *extra):
        self.xv("record", "move", sid, "--file", "tests/test_x.py", "--assertion", "a", "--why", "w",
                *extra, cwd=wt)
        return json.loads(self.xv("record", "show", sid, "--json", cwd=wt).stdout)

    def test_a_move_with_slice_only_keeps_the_marker_and_a_plain_move_does_not(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(
            {"file": "tests/test_x.py", "test": "a", "why": "w"}), cwd=wt)
        self.assertIs(self.move("s1", wt, "--slice-only")["moved_tests"][0]["slice_only"], True)
        wt = self.new_slice("s2")
        self.assertFalse(self.move("s2", wt)["moved_tests"][0].get("slice_only"))

    def test_a_plain_move_of_a_test_in_a_red_file_leaves_red_alone(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(
                {"agent": "scenario", "status": "red", "summary": "r", "red": RED}) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=wt)
        self.assertEqual(self.move("s1", wt, "--slice-only")["red"], RED)


class PacketTemplateTest(RepoCase):
    fixture = False

    def test_the_packet_has_a_line_for_slice_only_tests(self):
        text = open(os.path.join(HOME, "skills", "guardian", "packet.md")).read()
        self.assertIn("slice-only", text)


class BriefsTest(RepoCase):
    fixture = False

    def skill(self, name):
        return open(os.path.join(HOME, "skills", name, "SKILL.md")).read()

    def test_the_scenario_report_example_shows_slice_only(self):
        block = self.skill("scenario").split("```xv-report", 1)[1].split("```", 1)[0]
        self.assertIn("slice_only", block)

    def test_the_cleaner_is_told_to_remove_slice_only_tests_after_green_unless_it_finds_a_reason(self):
        text = self.skill("cleaner")
        self.assertIn("slice_only", text)
        self.assertIn("slice-only", text)
        self.assertIn("--deleted", text)

    def test_the_guardian_lists_removed_slice_only_tests_and_names_kept_ones_with_a_reason(self):
        self.assertIn("slice-only", self.skill("guardian"))


class ScenarioRerunMergeTest(RepoCase):
    """A scenario run after the maker adds to the red; before the maker it replaces it."""

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")

    def report(self, red):
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(
                {"agent": "scenario", "status": "red", "summary": "r", "red": red}) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=self.wt)

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def through_the_maker(self):
        self.xv("record", "add", "s1", "spend", json.dumps({"step": "maker", "agent": "maker"}), cwd=self.wt)
        path = os.path.join(self.tmp, "maker.txt")
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(
                {"agent": "maker", "status": "done", "summary": "made"}) + "\n```\n")
        self.xv("record", "report", "s1", "maker", path, cwd=self.wt)

    def test_before_the_maker_a_report_replaces_the_red(self):
        self.report(RED)
        one = {"files": ["tests/test_z.py"], "command": "python3 -m unittest tests.test_z",
               "failure": "f2", "watch_first_green": None}
        self.report(one)
        self.assertEqual(self.show()["red"]["files"], ["tests/test_z.py"])

    def test_after_the_maker_a_report_adds_its_files_and_the_rest_stay(self):
        self.report(RED)
        self.through_the_maker()
        self.report({"files": ["tests/test_z.py"], "command": "python3 -m unittest tests.test_z",
                     "failure": "f2", "watch_first_green": None})
        files = self.show()["red"]["files"]
        self.assertEqual(sorted(files), ["tests/test_x.py", "tests/test_y.py", "tests/test_z.py"])

    def test_after_the_maker_a_file_named_twice_is_listed_once(self):
        self.report(RED)
        self.through_the_maker()
        self.report({"files": ["tests/test_y.py"], "command": "python3 -m unittest tests.test_y",
                     "failure": "f2", "watch_first_green": None})
        files = self.show()["red"]["files"]
        self.assertEqual(sorted(files), ["tests/test_x.py", "tests/test_y.py"])


class SameMoveTest(RepoCase):
    """#154 item 5: one move told twice with a comma of difference is recorded once."""

    def move(self, wt, assertion, file="tests/test_x.py"):
        self.xv("record", "move", "s1", "--file", file, "--assertion", assertion, "--why", "w", cwd=wt)

    def moves(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["moved_tests"]

    def test_the_same_assertion_in_two_files_is_two_moves(self):
        wt = self.new_slice("s1")
        self.move(wt, "was: a; now: b")
        self.move(wt, "was: a; now: b", file="tests/test_y.py")
        self.assertEqual(len(self.moves(wt)), 2)


class SliceOnlyGateTest(RepoCase):
    """--slice-only counts only for a test the scenario listed in slice_only."""

    def move(self, wt, f, test):
        self.xv("record", "move", "s1", "--file", f, "--assertion", test, "--why", "w",
                "--slice-only", cwd=wt)
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["moved_tests"][0]

    def listed(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(
            {"file": "tests/test_x.py", "test": "test_file_is_ts", "why": "w"}), cwd=wt)
        return wt

    def test_a_listed_test_keeps_the_marker(self):
        wt = self.listed()
        self.assertIs(self.move(wt, "tests/test_x.py", "test_file_is_ts").get("slice_only"), True)

    def test_an_unlisted_test_is_a_plain_move(self):
        wt = self.listed()
        self.assertFalse(self.move(wt, "tests/test_other.py", "test_other").get("slice_only"))

    def test_with_nothing_listed_it_is_a_plain_move(self):
        wt = self.new_slice("s1")
        self.assertFalse(self.move(wt, "tests/test_x.py", "test_file_is_ts").get("slice_only"))

    def test_a_longer_assertion_that_contains_the_listed_name_is_a_plain_move(self):
        wt = self.listed()
        self.assertFalse(self.move(wt, "tests/test_x.py", "test_file_is_ts_and_more").get("slice_only"))

    def test_the_listed_name_in_another_file_is_a_plain_move(self):
        wt = self.listed()
        self.assertFalse(self.move(wt, "tests/test_y.py", "test_file_is_ts").get("slice_only"))


class OfferAndAnswerTest(RepoCase):
    """A stop keeps the decision: the offer, the pick, and `settled`."""

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which line?", cwd=self.wt)

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def offer(self, *extra):
        return self.xv("record", "offer", "s1",
                       "--option", "Use the setting", "--settles", "Attribution is a setting, empty by default.",
                       "--option", "Drop the line", "--settles", "No attribution line.", "--amends",
                       *extra, cwd=self.wt)

    def test_an_offer_puts_numbered_options_and_the_pick_on_the_open_stop(self):
        self.offer("--recommend", "1")
        stop = self.show()["stops"][-1]
        self.assertEqual([o["text"] for o in stop["options"]], ["Use the setting", "Drop the line"])
        self.assertEqual([o["settles"] for o in stop["options"]],
                         ["Attribution is a setting, empty by default.", "No attribution line."])
        self.assertEqual([bool(o.get("amends")) for o in stop["options"]], [False, True])
        self.assertEqual(stop["recommended"], 1)

    def test_an_offer_without_a_recommendation_holds_null(self):
        self.offer()
        self.assertIsNone(self.show()["stops"][-1]["recommended"])

    def test_an_option_with_no_settles_is_refused(self):
        p = self.xv("record", "offer", "s1", "--option", "Bare", "--recommend", "1", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settles", p.stderr)

    def test_a_settles_with_no_option_before_it_is_refused(self):
        p = self.xv("record", "offer", "s1", "--settles", "Orphan", "--option", "A", "--settles", "a",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--option", p.stderr)

    def test_an_amends_with_no_option_before_it_is_refused(self):
        p = self.xv("record", "offer", "s1", "--amends", "--option", "A", "--settles", "a",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--option", p.stderr)

    def test_a_pick_settles_with_the_offered_text_and_keeps_the_words(self):
        self.offer("--recommend", "1")
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "2 ok", "--pick", "2",
                "--new-info", "none", "--cause", "decision: the person chose", "--why", "less to maintain",
                cwd=self.wt)
        stop = self.show()["stops"][-1]
        self.assertEqual(stop["answer"], "2 ok")
        self.assertEqual(stop["pick"], 2)
        self.assertEqual(stop["settled"], "No attribution line.")
        self.assertEqual(stop["new_info"], "none")
        self.assertTrue(stop["cause"].startswith("decision"))
        self.assertEqual(stop["why"], "less to maintain")
        self.assertNotIn("recommended_by", stop)

    def test_other_needs_settled(self):
        self.offer()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "something else", "--pick", "other",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "something else", "--pick", "other",
                "--settled", "Attribution comes from the repo's config.", cwd=self.wt)
        stop = self.show()["stops"][-1]
        self.assertEqual((stop["pick"], stop["settled"]), ("other", "Attribution comes from the repo's config."))

    def test_an_answer_that_sends_work_back_needs_settled(self):
        self.offer()
        self.xv("record", "set", "s1", "next", "guardian", "--by", "pat", cwd=self.wt)
        p =self.xv("record", "answer", "s1", "--by", "pat", "--answer", "redo it",
                    "--next", "scenario", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_the_cause_is_one_of_the_five(self):
        self.offer()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1", "--pick", "1",
                    "--cause", "vibes", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_the_record_says_the_watch_wrote_settled_new_info_and_cause(self):
        self.offer()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1", "--pick", "1", "--new-info", "none",
                "--cause", "decision", cwd=self.wt)
        log = open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read()
        self.assertIn("scribe", log)

    def test_a_bundle_names_the_other_stops_one_reply_answered(self):
        self.offer()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1", "--pick", "1",
                "--bundle", "budget_not_set,no_report", cwd=self.wt)
        self.assertEqual(self.show()["stops"][-1]["bundle"], ["budget_not_set", "no_report"])

    def test_a_budget_answer_records_the_change(self):
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=self.wt)
        self.offer()
        self.xv("record", "set", "s1", "budget", '{"usd": 4}', "--by", "pat", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1, and raise it", "--pick", "1",
                cwd=self.wt)
        self.assertIsNotNone(self.show()["stops"][-1].get("budget_change"))

    def test_an_originator_stop_may_be_answered_by_someone_who_did_not_set_the_work_going(self):
        self.xv("record", "answer", "s1", "--by", "sam", "--answer", "carry on", cwd=self.wt)
        self.assertEqual(self.show()["stops"][-1]["answered_by"], ["sam"])


class DecisionsReportTest(RepoCase):
    def answered(self, wt, order, pick, new_info):
        self.xv("record", "stop", "s1", "--order", order, "--seat", "originator", "--question", "Q?", cwd=wt)
        self.xv("record", "offer", "s1", "--option", "A", "--settles", "a", "--option", "B", "--settles", "b",
                cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "x", "--pick", pick,
                "--new-info", new_info, "--cause", "decision", "--settled", "s", cwd=wt)

    def test_xv_decisions_counts_stops_per_order_and_skips_old_stops(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "old_order", "--seat", "originator", "--question", "Q?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "old", cwd=wt)
        self.answered(wt, "scenario_stopped", "1", "none")
        self.answered(wt, "scenario_stopped", "other", "the grocer closes Sundays")
        out = self.xv("decisions", cwd=wt).stdout
        line = [ln for ln in out.splitlines() if "scenario_stopped" in ln]
        self.assertEqual(len(line), 1, out)
        self.assertIn("2", line[0])
        self.assertIn("decision", line[0])
        self.assertNotIn("old_order", out)

    def test_xv_decisions_since_a_date_counts_only_stops_from_that_date_on(self):
        wt = self.new_slice("s1")
        self.answered(wt, "scenario_stopped", "1", "none")
        past = self.xv("decisions", "--since", "2000-01-01", cwd=wt).stdout
        self.assertIn("scenario_stopped", past)
        future = self.xv("decisions", "--since", "2999-01-01", cwd=wt).stdout
        self.assertNotIn("scenario_stopped", future)


class ResumeNeedsNextTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which line?", cwd=self.wt)

    def test_an_answer_with_resume_and_no_next_is_refused(self):
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go on", "--resume",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--next", p.stderr)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)
        self.assertIsNone(data["stops"][-1].get("answer"))

    def test_an_answer_with_resume_and_next_is_accepted_and_sets_next(self):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go on", "--resume",
                "--next", "scenario", "--settled", "Carry on from the scenario.", cwd=self.wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)
        self.assertEqual((data["status"], data["next"]), ("working", "scenario"))

    def test_the_watch_brief_says_an_answer_with_resume_needs_next(self):
        text = open(os.path.join(HOME, "skills", "watch", "SKILL.md")).read()
        self.assertRegex(text, r"(?is)--resume.{0,400}(refuses|needs|requires).{0,80}--next"
                               r"|--next.{0,400}(refuses|needs|requires)")


class DecisionsAmendedTest(RepoCase):
    def answered(self, wt, order, recommend, pick):
        self.xv("record", "stop", "s1", "--order", order, "--seat", "originator", "--question", "Q?", cwd=wt)
        self.xv("record", "offer", "s1", "--option", "A", "--settles", "a", "--option", "B", "--settles", "b",
                "--recommend", recommend, cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "x", "--pick", pick,
                "--new-info", "none", "--cause", "decision", cwd=wt)

    def line(self, wt, order):
        out = self.xv("decisions", cwd=wt).stdout
        lines = [ln for ln in out.splitlines() if order in ln]
        self.assertEqual(len(lines), 1, out)
        return lines[0]

    def test_a_pick_is_taken_only_when_it_equals_the_recommendation(self):
        wt = self.new_slice("s1")
        self.answered(wt, "agrees", "1", "1")
        self.answered(wt, "against", "1", "2")
        self.assertRegex(self.line(wt, "agrees"), r"taken\D*1")
        self.assertRegex(self.line(wt, "against"), r"taken\D*0")

    def test_a_pick_with_no_recommendation_is_not_taken(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "unsure", "--seat", "originator", "--question", "Q?", cwd=wt)
        self.xv("record", "offer", "s1", "--option", "A", "--settles", "a", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "x", "--pick", "1", cwd=wt)
        self.assertRegex(self.line(wt, "unsure"), r"taken\D*0")

    def stopped_doc(self, wt, name, with_id=True, broken=False):
        order = name.replace(".md", "")
        head = "id: %s\n" % order if with_id else ""
        stop = {"order": order, "seat": "originator", "answer": "x", "pick": 1, "recommended": 1,
                "settled": "s", "at": "2026-10-29T10:00:00+00:00"}
        body = ("this is not front matter\n" if broken else head + "stops: %s\n" % json.dumps([stop]))
        with open(os.path.join(wt, ".xv", "slices", name), "w") as f:
            f.write("---\n" + body + "---\n# t\n")

    def test_it_skips_the_files_xv_retro_skips(self):
        wt = self.new_slice("s1")
        self.answered(wt, "real_order", "1", "1")
        self.stopped_doc(wt, "packet-ghost.md")
        self.stopped_doc(wt, "noid.md", with_id=False)
        out = self.xv("decisions", cwd=wt).stdout
        self.assertIn("real_order", out)
        self.assertNotIn("packet-ghost", out)
        self.assertNotIn("noid", out)

    def test_a_record_it_cannot_read_does_not_stop_the_report(self):
        wt = self.new_slice("s1")
        self.answered(wt, "real_order", "1", "1")
        self.stopped_doc(wt, "broken.md", broken=True)
        p = self.xv("decisions", cwd=wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("real_order", p.stdout)


class AnswerAmendmentsTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which line?", cwd=self.wt)
        self.xv("record", "offer", "s1", "--option", "Use the setting", "--settles", "It is a setting.",
                "--recommend", "1", cwd=self.wt)

    def log(self):
        return open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read()

    def test_a_pick_fills_settled_before_next_checks_for_it(self):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1", "--pick", "1",
                "--next", "maker", "--resume", cwd=self.wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)
        self.assertEqual(data["stops"][-1]["settled"], "It is a setting.")
        self.assertEqual((data["status"], data["next"]), ("working", "maker"))

    def test_next_with_no_pick_and_no_settled_is_still_refused(self):
        self.xv("record", "set", "s1", "next", "maker", "--by", "pat", cwd=self.wt)
        p =self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", "maker",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_the_readme_answer_examples_with_resume_give_next(self):
        lines = [ln for ln in open(os.path.join(HOME, "README.md")).read().splitlines()
                 if "xv record answer" in ln and "--resume" in ln]
        self.assertTrue(lines)
        for ln in lines:
            self.assertIn("--next", ln)

    def test_the_changelog_names_the_rule_that_resume_needs_next(self):
        text = open(os.path.join(HOME, "CHANGELOG.md")).read()
        self.assertRegex(text, r"(?i)--resume[^\n]{0,80}(needs|requires|refuses)[^\n]{0,40}--next")

    def test_the_log_line_names_only_the_scribe_fields_written(self):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "x", "--pick", "other",
                "--settled", "Something else is true.", cwd=self.wt)
        line = [ln for ln in self.log().splitlines() if "scribe" in ln]
        self.assertEqual(len(line), 1, self.log())
        self.assertIn("settled", line[0])
        self.assertNotIn("new_info", line[0])
        self.assertNotIn("cause", line[0])


class FourthAmendmentTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def stop_at(self, step):
        self.xv("record", "set", "s1", "next", step, "--by", "pat", cwd=self.wt)
        self.xv("record", "stop", "s1", "--order", "some_order", "--seat", "originator",
                "--question", "Q?", cwd=self.wt)

    def answer(self, nxt):
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", nxt,
                       "--resume", cwd=self.wt, check=False)

    def test_next_forward_needs_no_settled(self):
        self.stop_at("guardian")
        p = self.answer("close")
        self.assertEqual(p.returncode, 0, p.stderr)
        data = self.show()
        self.assertEqual((data["status"], data["next"]), ("working", "close"))

    def test_next_to_a_later_step_than_the_one_that_stopped_needs_no_settled(self):
        self.stop_at("scenario")
        p = self.answer("maker")
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_next_to_the_step_that_stopped_needs_settled(self):
        self.stop_at("maker")
        p = self.answer("maker")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_next_to_an_earlier_step_needs_settled(self):
        self.stop_at("guardian")
        p = self.answer("scenario")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)
        self.assertIsNone(self.show()["stops"][-1].get("answer"))

    def test_the_readme_answer_examples_run_without_being_refused(self):
        import shlex
        lines = [ln.strip() for ln in open(os.path.join(HOME, "README.md")).read().splitlines()
                 if ln.strip().startswith("xv record answer 2026-10-22-expiring-today")]
        self.assertTrue(lines)
        self.assertTrue(any("--next close" in ln for ln in lines), lines)
        for ln in lines:
            self.xv("record", "set", "s1", "next", "close", "--by", "pat", cwd=self.wt)
            self.xv("record", "stop", "s1", "--order", "ready_to_merge", "--seat", "originator",
                    "--question", "Merge?", cwd=self.wt)
            args = shlex.split(ln)[1:]
            args[2] = "s1"
            p = self.xv(*args, cwd=self.wt, check=False)
            self.assertEqual(p.returncode, 0, ln + "\n" + p.stderr)

    def test_the_watch_brief_shows_next_as_required_and_says_when_settled_is_needed(self):
        text = open(os.path.join(HOME, "skills", "watch", "SKILL.md")).read()
        cmd = [ln for ln in text.splitlines() if ln.startswith("xv record answer ")]
        self.assertEqual(len(cmd), 1)
        self.assertIn("--next <step>", cmd[0])
        self.assertNotIn("[--next", cmd[0])
        self.assertRegex(text, r"(?is)--settled[^\n]{0,300}(earlier|forward)")

    def test_an_offer_keeps_the_budget_the_stop_saved(self):
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=self.wt)
        self.xv("record", "stop", "s1", "--order", "o", "--seat", "originator", "--question", "Q?", cwd=self.wt)
        self.xv("record", "set", "s1", "budget", '{"usd": 4}', "--by", "pat", cwd=self.wt)
        self.xv("record", "offer", "s1", "--option", "A", "--settles", "a", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1", "--pick", "1", cwd=self.wt)
        change = self.show()["stops"][-1].get("budget_change")
        self.assertEqual((change["from"]["usd"], change["to"]["usd"]), (2, 4))


class FifthAmendmentTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def stop_saved_at(self, step, next_step):
        """A stop that saved `step`, as xv step writes it, while the record's next is `next_step`."""
        self.xv("record", "stop", "s1", "--order", "some_order", "--seat", "originator",
                "--question", "Q?", "--step", step, cwd=self.wt)
        self.xv("record", "set", "s1", "next", next_step, "--by", "pat", cwd=self.wt)
        self.assertEqual(self.show()["stops"][-1]["step"], step)

    def answer(self, nxt):
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", nxt,
                       "--resume", cwd=self.wt, check=False)

    def test_going_back_is_judged_against_the_step_on_the_stop_not_the_records_next(self):
        self.stop_saved_at("guardian", "scenario")
        p = self.answer("maker")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_going_forward_is_judged_against_the_step_on_the_stop_not_the_records_next(self):
        self.stop_saved_at("scenario", "guardian")
        p = self.answer("maker")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.show()["next"], "maker")

    def test_the_decision_record_and_the_decisions_list_keep_settled_and_the_words(self):
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Shape?", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "go with the new module",
                "--pick", "other", "--settled", "The shape change is accepted: scripts/decisions is new.",
                cwd=self.wt)
        entry = self.show()["decisions"][0]
        self.assertEqual(entry.get("settled"), "The shape change is accepted: scripts/decisions is new.")
        text = open(os.path.join(self.wt, entry["record"])).read()
        self.assertIn("The shape change is accepted: scripts/decisions is new.", text)
        self.assertIn("go with the new module", text)

    def test_the_changelog_names_when_settled_is_required(self):
        text = open(os.path.join(HOME, "CHANGELOG.md")).read()
        self.assertRegex(text, r"(?is)--settled[^\n]{0,200}(back|earlier)[^\n]{0,200}other"
                               r"|(back|earlier)[^\n]{0,200}other[^\n]{0,200}--settled")

    def test_the_readme_general_answer_line_says_when_settled_is_required(self):
        lines = [ln for ln in open(os.path.join(HOME, "README.md")).read().splitlines()
                 if ln.startswith("A person answers with `xv record answer")]
        self.assertEqual(len(lines), 1)
        self.assertRegex(lines[0], r"--settled")
        self.assertRegex(lines[0], r"(?i)(back|earlier)")
        self.assertRegex(lines[0], r"(?i)other")


class SettledForwardTest(RepoCase):
    """#82: an answer that moves the slice forward needs no --settled when the work has not started."""

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def stop(self, step, order="some_order"):
        return self.xv("record", "stop", "s1", "--order", order, "--seat", "originator",
                       "--question", "Q?", "--step", step, cwd=self.wt)

    def answer(self, nxt):
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", nxt,
                       "--resume", cwd=self.wt, check=False)

    def test_record_stop_takes_a_step_and_saves_it_on_the_stop(self):
        self.stop("maker")
        self.assertEqual(self.show()["stops"][-1]["step"], "maker")

    def test_a_failed_setup_goes_to_any_step_without_settled(self):
        for nxt in ("forecaster", "scenario"):
            self.stop("setup", "setup_failed")
            p = self.answer(nxt)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(self.show()["next"], nxt)

    def test_a_prototype_stop_goes_to_any_step_without_settled(self):
        self.stop("prototype", "axis_not_named")
        p = self.answer("scenario")
        self.assertEqual(p.returncode, 0, p.stderr)

    def stop_before_step(self, step):
        """The watch's own budget stop: the budget is spent, so `step` does not run."""
        row = {"step": "forecaster", "usd": 5, "tokens": 10, "tokens_in": 10, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0}
        self.xv("record", "set", "s1", "budget", json.dumps({"usd": 1, "tokens": 10000000}),
                "--by", "pat", cwd=self.wt)
        self.xv("record", "add", "s1", "spend", json.dumps(row), cwd=self.wt)
        p = self.xv("step", step, "s1", cwd=self.wt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent", p.stdout + p.stderr)

    def test_a_budget_stop_before_its_step_ran_goes_to_that_step_without_settled(self):
        self.stop_before_step("maker")
        p = self.answer("maker")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.show()["next"], "maker")

    def test_a_budget_stop_before_its_step_still_needs_settled_to_go_earlier(self):
        self.stop_before_step("maker")
        p = self.answer("scenario")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_a_budget_stop_after_the_maker_left_the_suite_red_needs_settled_to_return_to_it(self):
        self.stop("maker", "budget_spent")
        p = self.answer("maker")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_a_setup_failed_stop_raised_after_the_scenario_step_needs_settled_to_return_to_it(self):
        self.stop("scenario", "setup_failed")
        p = self.answer("scenario")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_the_prototypes_ready_pick_needs_settled_to_send_the_work_back(self):
        self.stop("prototype", "prototypes_ready")
        p = self.answer("scenario")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_the_docs_name_the_stops_that_need_no_settled(self):
        def read(path):
            with open(os.path.join(HOME, path)) as f:
                return f.read()
        readme = [ln for ln in read("README.md").splitlines()
                  if ln.startswith("A person answers with `xv record answer")][0]
        for name, text in (("README answer line", readme), ("watch brief", read("skills/watch/SKILL.md"))):
            for word in ("setup_failed", "budget_spent", "prototypes_ready"):
                self.assertIn(word, text, f"{name} does not name {word}")
        self.assertTrue([ln for ln in read("CHANGELOG.md").splitlines()
                         if "setup_failed" in ln and "--settled" in ln and "prototypes_ready" in ln],
                        "CHANGELOG.md has no line for the --settled exceptions")

    def test_another_stop_at_a_step_still_needs_settled_to_return_to_it(self):
        self.stop("maker", "scenario_stopped")
        p = self.answer("maker")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_the_readme_general_answer_line_runs_with_its_placeholders_filled(self):
        import shlex
        lines = [ln for ln in open(os.path.join(HOME, "README.md")).read().splitlines()
                 if ln.startswith("A person answers with `xv record answer")]
        self.assertEqual(len(lines), 1)
        line = lines[0].split("`")[1]
        for old, new in (("<id>", "s1"), ("<name>", "pat"), ("<their words>", "go"), ("<step>", "maker")):
            self.assertIn(old, line)
            line = line.replace(old, new)
        self.stop("scenario", "scenario_stopped")
        p = self.xv(*shlex.split(line)[1:], cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, line + "\n" + p.stderr)


class WallChoicesTest(RepoCase):
    """Sean's three amendments to the test-marks slice."""

    RECS = [{"file": "tests/test_a.py", "test": "test_keep_me", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_a.py", "test": "test_drop_me", "recommend": "stay off the wall", "why": "w"}]
    MARK = {"file": "tests/test_x.py", "test": "test_file_is_ts", "why": "only proves the rename"}

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def answer_accept_moves(self, text):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "g.txt")
        report = {"agent": "guardian", "status": "done", "summary": "p", "shape_change": "no",
                  "pitch_contradiction": "no", "wall_recommendations": self.RECS}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", text, cwd=wt)
        return {r["test"]: r for r in self.show(wt)["wall_recommendations"]}

    def test_a_refused_recommendation_does_not_stop_accept_moves_again(self):
        import orders
        from xvlib import DEFAULT_CONFIG
        refused = dict(self.RECS[1], accepted=False, refused=True)
        d = {"id": "s1", "set_by": "pat", "budget": {"usd": 2}, "moved_tests": [], "spend": [], "stops": [],
             "shape_change": "no", "pitch_contradiction": "no", "wall_recommendations": [refused],
             "checks": {"reports": [{"agent": "guardian", "status": "done"}], "guardian": {}}}
        self.assertEqual(orders.verdict(d, "guardian", DEFAULT_CONFIG)["stop"]["order"], "ready_to_merge")

    def test_unmark_takes_one_test_off_slice_only_and_keeps_the_rest(self):
        wt = self.new_slice("s1")
        other = {"file": "tests/test_y.py", "test": "test_old_flag_gone", "why": "dead"}
        for m in (self.MARK, other):
            self.xv("record", "add", "s1", "slice_only", json.dumps(m), cwd=wt)
        self.xv("record", "unmark", "s1", "--test", "test_file_is_ts", cwd=wt)
        left = self.show(wt)["slice_only"]
        self.assertEqual([m["test"] for m in left], ["test_old_flag_gone"])

    def test_unmark_of_a_test_that_is_not_marked_fails(self):
        wt = self.new_slice("s1")
        p = self.xv("record", "unmark", "s1", "--test", "test_nope", cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_a_move_whose_assertion_starts_with_the_marked_name_keeps_the_flag(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.MARK), cwd=wt)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--assertion",
                "test_file_is_ts; removed", "--why", "w", "--slice-only", cwd=wt)
        self.assertIs(self.show(wt)["moved_tests"][0].get("slice_only"), True)

    def test_a_move_of_another_test_does_not_get_the_flag(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.MARK), cwd=wt)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--assertion",
                "test_other; removed", "--why", "w", "--slice-only", cwd=wt)
        self.assertFalse(self.show(wt)["moved_tests"][0].get("slice_only"))


class WallAnswerByFileTest(RepoCase):
    """#148: two wall recommendations with one test name in different files are answered one by one."""

    RECS = [{"file": "tests/test_a.py", "test": "test_same", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_b.py", "test": "test_same", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_b.py", "test": "test_only_here", "recommend": "stay on the wall", "why": "w"}]

    def stopped_on_accept_moves(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "g.txt")
        report = {"agent": "guardian", "status": "done", "summary": "p", "shape_change": "no",
                  "pitch_contradiction": "no", "wall_recommendations": self.RECS}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        return wt

    def accepted(self, wt):
        recs = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["wall_recommendations"]
        return [(r["file"], r["test"]) for r in recs if r["accepted"]]

    def answer(self, wt, *flags, check=True):
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", *flags, cwd=wt, check=check)

    def with_files(self, wt):
        for name, cls in (("test_a.py", "AlphaTest"), ("test_b.py", "BetaTest")):
            with open(os.path.join(wt, "tests", name), "w") as f:
                f.write(f"class {cls}:\n    def test_same(self):\n        pass\n    def test_only_here(self):\n        pass\n")

    def test_the_colons_form_names_one_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        self.answer(wt, "--accept-wall", "tests/test_b.py::BetaTest::test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_b.py", "test_same")])

    def test_the_hash_form_names_one_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        self.answer(wt, "--accept-wall", "BetaTest#test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_b.py", "test_same")])

    def test_the_dots_form_names_one_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        self.answer(wt, "--accept-wall", "tests.test_b.BetaTest.test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_b.py", "test_same")])

    def test_the_file_and_class_form_names_one_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        self.answer(wt, "--accept-wall", "tests/test_b.py::BetaTest.test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_b.py", "test_same")])

    def test_the_arrow_form_names_one_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        self.answer(wt, "--accept-wall", "BetaTest > test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_b.py", "test_same")])

    def test_a_class_form_the_file_does_not_have_names_nothing(self):
        wt = self.stopped_on_accept_moves()
        self.with_files(wt)
        p = self.answer(wt, "--accept-wall", "GammaTest#test_same", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no wall recommendation", p.stderr)

    def test_accept_and_refuse_of_the_two_files_answer_them_apart(self):
        wt = self.stopped_on_accept_moves()
        self.answer(wt, "--accept-wall", "tests/test_a.py::test_same", "--refuse-wall", "tests/test_b.py::test_same")
        self.assertEqual(self.accepted(wt), [("tests/test_a.py", "test_same")])

    def test_the_same_file_and_test_in_both_flags_is_refused(self):
        wt = self.stopped_on_accept_moves()
        p = self.answer(wt, "--accept-wall", "tests/test_a.py::test_same",
                        "--refuse-wall", "tests/test_a.py::test_same", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("both", p.stderr)

    def test_a_file_and_test_with_no_recommendation_is_refused(self):
        wt = self.stopped_on_accept_moves()
        p = self.answer(wt, "--accept-wall", "tests/test_c.py::test_same", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no wall recommendation", p.stderr)


class AcceptWallFlagTest(RepoCase):
    """Sean's second set of amendments to the test-marks slice."""

    RECS = WallChoicesTest.RECS
    MARK = WallChoicesTest.MARK

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def stopped_on_accept_moves(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "g.txt")
        report = {"agent": "guardian", "status": "done", "summary": "p", "shape_change": "no",
                  "pitch_contradiction": "no", "wall_recommendations": self.RECS}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        return wt

    def recs(self, wt):
        return {r["test"]: r for r in self.show(wt)["wall_recommendations"]}

    def scenario_rerun(self, wt, slice_only):
        path = os.path.join(self.tmp, "out.txt")
        report = {"agent": "scenario", "status": "red", "summary": "r", "red": RED, "slice_only": slice_only}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "scenario", path, cwd=wt)

    def test_accept_wall_accepts_the_named_test_and_refuses_the_rest(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertFalse(recs["test_keep_me"].get("refused"))
        self.assertIs(recs["test_drop_me"]["accepted"], False)
        self.assertIs(recs["test_drop_me"].get("refused"), True)

    def test_accept_wall_can_be_given_once_per_test(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_keep_me", "--accept-wall", "test_drop_me", cwd=wt)
        self.assertEqual([r["accepted"] for r in self.recs(wt).values()], [True, True])

    def test_an_answer_with_no_flag_refuses_every_recommendation(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1", cwd=wt)
        for r in self.recs(wt).values():
            self.assertIs(r["accepted"], False)
            self.assertIs(r.get("refused"), True)

    def test_the_words_of_the_answer_are_never_read_to_accept_a_test(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer",
                "accept test_keep_me and test_drop_me", cwd=wt)
        for r in self.recs(wt).values():
            self.assertIs(r["accepted"], False)

    def test_naming_a_test_in_the_words_does_not_refuse_it_when_the_flag_accepts_it(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "refuse test_keep_me",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.assertIs(self.recs(wt)["test_keep_me"]["accepted"], True)

    def test_accept_wall_for_a_test_with_no_recommendation_is_refused(self):
        wt = self.stopped_on_accept_moves()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                    "--accept-wall", "test_nope", cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("test_nope", p.stderr)

    def guardian_report(self, wt, recs):
        path = os.path.join(self.tmp, "g2.txt")
        report = {"agent": "guardian", "status": "done", "summary": "p", "shape_change": "no",
                  "pitch_contradiction": "no", "wall_recommendations": recs}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)

    def test_a_guardian_report_cannot_mark_its_own_recommendation_accepted(self):
        wt = self.new_slice("s1")
        self.guardian_report(wt, [dict(r, accepted=True) for r in self.RECS])
        for r in self.recs(wt).values():
            self.assertIsNot(r.get("accepted"), True)

    def test_a_guardian_rerun_keeps_what_the_person_accepted_with_the_flag(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.guardian_report(wt, self.RECS)
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertIsNot(recs["test_drop_me"].get("accepted"), True)

    def test_a_guardian_rerun_cannot_accept_what_the_person_did_not(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.guardian_report(wt, [dict(r, accepted=True) for r in self.RECS])
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertIsNot(recs["test_drop_me"].get("accepted"), True)

    def second_accept_moves(self, wt):
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept again?", "--step", "guardian", cwd=wt)

    def test_a_later_answer_with_no_flag_keeps_what_an_earlier_stop_accepted(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.second_accept_moves(wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B 2", cwd=wt)
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertFalse(recs["test_keep_me"].get("refused"))

    def test_a_later_answer_with_another_flag_keeps_the_earlier_accepted_name_too(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.second_accept_moves(wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_drop_me", cwd=wt)
        self.assertEqual([r["accepted"] for r in self.recs(wt).values()], [True, True])

    def test_a_later_answer_does_not_accept_a_recommendation_nobody_accepted(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.second_accept_moves(wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B 2", cwd=wt)
        self.assertIs(self.recs(wt)["test_drop_me"]["accepted"], False)

    def accepted_both_then_second_stop(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_keep_me", "--accept-wall", "test_drop_me", cwd=wt)
        self.second_accept_moves(wt)
        return wt

    def test_refuse_wall_refuses_a_recommendation_an_earlier_stop_accepted(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--refuse-wall", "test_drop_me", cwd=wt)
        recs = self.recs(wt)
        self.assertIs(recs["test_drop_me"]["accepted"], False)
        self.assertIs(recs["test_drop_me"].get("refused"), True)

    def test_refuse_wall_leaves_the_other_accepted_recommendations_accepted(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--refuse-wall", "test_drop_me", cwd=wt)
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertFalse(recs["test_keep_me"].get("refused"))

    def test_refuse_wall_can_be_given_once_per_test(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--refuse-wall", "test_keep_me", "--refuse-wall", "test_drop_me", cwd=wt)
        self.assertEqual([r["accepted"] for r in self.recs(wt).values()], [False, False])

    def test_the_words_never_refuse_an_earlier_accepted_test(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer",
                "refuse test_keep_me and test_drop_me", cwd=wt)
        self.assertEqual([r["accepted"] for r in self.recs(wt).values()], [True, True])

    def answered_stops(self, wt):
        return [s for s in self.show(wt)["stops"] if s.get("order") == "accept_moves"]

    def test_the_stop_keeps_the_names_given_with_accept_wall(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        stop = self.answered_stops(wt)[0]
        self.assertEqual(stop["accepted_wall"], ["test_keep_me"])
        self.assertEqual(stop["refused_wall"], [])

    def test_the_stop_keeps_every_name_given_with_accept_wall(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_keep_me", "--accept-wall", "test_drop_me", cwd=wt)
        stop = self.answered_stops(wt)[0]
        self.assertEqual(sorted(stop["accepted_wall"]), ["test_drop_me", "test_keep_me"])

    def test_the_stop_keeps_the_names_given_with_refuse_wall(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--refuse-wall", "test_drop_me", cwd=wt)
        stop = self.answered_stops(wt)[1]
        self.assertEqual(stop["refused_wall"], ["test_drop_me"])
        self.assertEqual(stop["accepted_wall"], [])

    def test_a_stop_answered_with_no_wall_flag_keeps_two_empty_lists(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1", cwd=wt)
        stop = self.answered_stops(wt)[0]
        self.assertEqual(stop["accepted_wall"], [])
        self.assertEqual(stop["refused_wall"], [])

    def test_an_earlier_stop_keeps_its_names_after_a_later_answer(self):
        wt = self.accepted_both_then_second_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--refuse-wall", "test_drop_me", cwd=wt)
        first = self.answered_stops(wt)[0]
        self.assertEqual(sorted(first["accepted_wall"]), ["test_drop_me", "test_keep_me"])
        self.assertEqual(first["refused_wall"], [])

    def test_a_guardian_report_cannot_mark_its_own_recommendation_refused(self):
        wt = self.new_slice("s1")
        self.guardian_report(wt, [dict(r, refused=True) for r in self.RECS])
        for r in self.recs(wt).values():
            self.assertIsNot(r.get("refused"), True)

    def test_a_guardian_rerun_cannot_refuse_what_the_person_accepted(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "B: 1",
                "--accept-wall", "test_keep_me", cwd=wt)
        self.guardian_report(wt, [dict(r, accepted=False, refused=True) for r in self.RECS])
        recs = self.recs(wt)
        self.assertIs(recs["test_keep_me"]["accepted"], True)
        self.assertIsNot(recs["test_keep_me"].get("refused"), True)

    def other_stop(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "q?", "--step", "scenario", cwd=wt)
        return wt

    def test_accept_wall_on_a_stop_other_than_accept_moves_is_refused_with_an_error(self):
        wt = self.other_stop()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", "maker",
                    "--settled", "x", "--accept-wall", "test_keep_me", cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("accept-wall", p.stderr)

    def test_refuse_wall_on_a_stop_other_than_accept_moves_is_refused_with_an_error(self):
        wt = self.other_stop()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", "maker",
                    "--settled", "x", "--refuse-wall", "test_keep_me", cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refuse-wall", p.stderr)

    def test_a_wall_flag_on_another_stop_leaves_that_stop_unanswered(self):
        wt = self.other_stop()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", "maker",
                "--settled", "x", "--accept-wall", "test_keep_me", cwd=wt, check=False)
        self.assertFalse(self.show(wt)["stops"][-1].get("answer"))

    def test_accept_wall_and_refuse_wall_on_the_same_test_is_refused_with_an_error(self):
        wt = self.stopped_on_accept_moves()
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                    "--accept-wall", "test_keep_me", "--refuse-wall", "test_keep_me",
                    cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("test_keep_me", p.stderr)

    def test_a_refused_clash_accepts_nothing_and_leaves_the_stop_unanswered(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_keep_me", "--refuse-wall", "test_keep_me",
                cwd=wt, check=False)
        self.assertNotIn(True, [r.get("accepted") for r in self.recs(wt).values()])
        self.assertFalse(self.answered_stops(wt)[0].get("answer"))

    def test_a_scenario_rerun_keeps_the_marks_already_in_the_record(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.MARK), cwd=wt)
        self.scenario_rerun(wt, [])
        self.assertEqual(self.show(wt)["slice_only"], [self.MARK])

    def test_a_scenario_rerun_adds_new_marks_beside_the_kept_ones(self):
        wt = self.new_slice("s1")
        new = {"file": "tests/test_y.py", "test": "test_old_flag_gone", "why": "dead"}
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.MARK), cwd=wt)
        self.scenario_rerun(wt, [new])
        self.assertEqual(sorted(m["test"] for m in self.show(wt)["slice_only"]),
                         ["test_file_is_ts", "test_old_flag_gone"])

    def test_a_merge_answer_is_recorded_as_a_decision(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "ready_to_merge", "--seat", "originator",
                "--question", "merge?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge it", cwd=wt)
        data = self.show(wt)
        self.assertEqual(len(data["decisions"]), 1)
        self.assertEqual(data["decisions"][0]["who"], ["pat"])
        with open(os.path.join(wt, data["decisions"][0]["record"])) as f:
            self.assertIn("merge it", f.read())

    def test_a_plain_one_person_stop_still_writes_no_decision(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "q?", "--step", "scenario", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--next", "maker",
                "--settled", "x", cwd=wt)
        self.assertEqual(self.show(wt)["decisions"], [])


class ScenarioMissStandingOrderTest(RepoCase):
    """The send-back for a scenario miss is read from the record, so `xv record packet` and `xv orders` see it."""

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def packet(self, wt, line, name="p.md"):
        path = os.path.join(wt, name)
        with open(path, "w") as f:
            f.write("---\nslice: s1\nshape_change: no\npitch_contradiction: no\nscenario_miss: yes\nexpected_moves: 0\n---\n\n"
                    "# Packet\n\n## Scenario misses\n\n- %s (evidence: tests/test_red.py:7)\n" % line)
        self.xv("record", "packet", "s1", path, cwd=wt)

    def guardian_done(self, wt):
        report = os.path.join(wt, "r.json")
        with open(report, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "guardian", "status": "done", "summary": "done"})
                    + "\n```\n")
        self.xv("record", "report", "s1", "guardian", report, cwd=wt)

    def orders(self, wt):
        p = self.xv("orders", "s1", "--after", "guardian", cwd=wt, check=False)
        return json.loads(p.stdout)

    def test_record_packet_sends_a_miss_back_to_the_maker_without_a_stop(self):
        wt = self.new_slice("s1")
        self.guardian_done(wt)
        self.packet(wt, "Point 2: milk that runs out today is left out, to: maker")
        data = self.show(wt)
        self.assertEqual(data["scenario_miss"], "yes")
        self.assertEqual(data["next"], "maker")
        self.assertEqual([s for s in data["stops"] if s.get("answer") is None], [])
        self.assertIn("milk that runs out today", json.dumps(data["stops"]))
        v = self.orders(wt)
        self.assertIsNone(v["stop"])
        self.assertNotIn("ready_to_merge", [f["order"] for f in v["fired"]])

    def test_xv_orders_stops_for_a_miss_marked_amend_yes(self):
        wt = self.new_slice("s1")
        self.guardian_done(wt)
        self.packet(wt, "Point 2: the scenario itself is wrong, to: maker, amend: yes")
        v = self.orders(wt)
        self.assertEqual((v["stop"] or {}).get("order"), "scenario_miss")
        self.assertEqual(v["stop"]["seat"], "originator")

    def test_xv_orders_stops_when_the_same_point_comes_back_worded_differently(self):
        wt = self.new_slice("s1")
        self.guardian_done(wt)
        self.packet(wt, "Point 2 is not met: milk that runs out today is left out, to: maker")
        self.packet(wt, "2: the list still skips milk, to: maker", name="p2.md")
        v = self.orders(wt)
        self.assertEqual((v["stop"] or {}).get("order"), "scenario_miss")
        self.assertEqual(v["stop"]["seat"], "originator")


class OneHomeRecordTest(RepoCase):
    """The record's own rules after every stop rule moved to orders.py."""

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def report(self, wt, agent, name="r.json", **fields):
        path = os.path.join(wt, name)
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": agent, "status": "done", "summary": "s", **fields})
                    + "\n```\n")
        self.xv("record", "report", "s1", agent, path, cwd=wt)

    def fired(self, wt, after="scenario"):
        p = self.xv("orders", "s1", "--after", after, cwd=wt, check=False)
        return json.loads(p.stdout)["fired"]

    def mark(self, test):
        return {"file": "tests/test_x.py", "test": test, "why": "only proves the slice did its job"}

    def scenario_reports(self, wt, *marks, name="s.json"):
        self.report(wt, "scenario", name=name, status="red", red=RED, slice_only=list(marks))

    def test_a_mark_the_person_accepted_is_not_asked_about_again_when_the_scenario_runs_again(self):
        wt = self.new_slice("s1")
        self.scenario_reports(wt, self.mark("test_a"))
        self.assertEqual([f["order"] for f in self.fired(wt)], ["slice_only_marks"])
        self.xv("record", "stop", "s1", "--order", "slice_only_marks", "--seat", "originator",
                "--question", "Accept the marks?", "--step", "scenario", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "accepted", "--next", "maker", cwd=wt)
        self.scenario_reports(wt, self.mark("test_a"), name="s2.json")
        self.assertEqual([m["test"] for m in self.show(wt)["slice_only"]], ["test_a"])
        self.assertNotIn("slice_only_marks", [f["order"] for f in self.fired(wt)])

    def test_a_new_mark_beside_an_accepted_one_is_the_only_one_asked_about(self):
        wt = self.new_slice("s1")
        self.scenario_reports(wt, self.mark("test_a"))
        self.xv("record", "stop", "s1", "--order", "slice_only_marks", "--seat", "originator",
                "--question", "Accept the marks?", "--step", "scenario", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "accepted", "--next", "maker", cwd=wt)
        self.scenario_reports(wt, self.mark("test_a"), self.mark("test_b"), name="s2.json")
        asked = [f for f in self.fired(wt) if f["order"] == "slice_only_marks"]
        self.assertEqual(len(asked), 1)
        self.assertIn("test_b", asked[0]["question"])
        self.assertNotIn("test_a", asked[0]["question"])

    def test_a_move_the_command_and_a_report_both_record_is_one_move_with_its_flag(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "slice_only", json.dumps(self.mark("test_a")), cwd=wt)
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--assertion", "test_a",
                "--why", "w", "--slice-only", "--by", "maker", cwd=wt)
        self.report(wt, "maker", status="green", moved_tests=[
            {"file": "tests/test_x.py", "assertion": "test_a", "why": "w"}])
        moves = self.show(wt)["moved_tests"]
        self.assertEqual(len(moves), 1, moves)
        self.assertIs(moves[0].get("slice_only"), True)

    def test_a_move_a_report_records_and_the_command_records_again_is_one_move(self):
        wt = self.new_slice("s1")
        self.report(wt, "maker", status="green", moved_tests=[
            {"file": "tests/test_x.py", "assertion": "test_a", "why": "w"}])
        self.xv("record", "move", "s1", "--file", "tests/test_x.py", "--assertion", "test_a",
                "--why", "w", "--by", "maker", cwd=wt)
        self.assertEqual(len(self.show(wt)["moved_tests"]), 1)

    def test_a_shape_wider_answer_that_sends_the_work_back_is_marked_sent_back(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "shape_wider_than_forecast", "--seat", "two_people",
                "--question", "Wider than forecast?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "narrow it", "--next", "maker",
                "--settled", "the shape is narrowed to the forecast", cwd=wt)
        stop = self.show(wt)["stops"][0]
        self.assertIs(stop.get("sent_back"), True, stop)

    def test_a_shape_wider_answer_that_lets_the_work_go_on_is_not_marked_sent_back(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "shape_wider_than_forecast", "--seat", "two_people",
                "--question", "Wider than forecast?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "go on", "--next", "close", cwd=wt)
        self.assertFalse(self.show(wt)["stops"][0].get("sent_back"))

    def verdict(self, order="scenario_miss"):
        return {"stop": {"order": order, "seat": "originator", "question": "Why?"}, "fired": [], "next": "guardian"}

    def test_applying_the_same_stop_twice_leaves_one_open_stop(self):
        data = {"stops": [], "budget": None, "status": "working", "next": "guardian"}
        body = record.apply_verdict(data, "", "guardian", self.verdict())
        record.apply_verdict(data, body, "guardian", self.verdict())
        self.assertEqual([s["order"] for s in data["stops"]], ["scenario_miss"])
        self.assertEqual(data["status"], "stopped")

    def test_a_stop_of_the_same_order_that_was_answered_may_open_again(self):
        data = {"stops": [{"order": "scenario_miss", "seat": "originator", "answer": "sent back"}],
                "budget": None, "status": "working", "next": "guardian"}
        record.apply_verdict(data, "", "guardian", self.verdict())
        self.assertEqual([bool(s.get("answer")) for s in data["stops"]], [True, False])

    def test_a_stop_of_another_order_opens_beside_an_open_one(self):
        data = {"stops": [{"order": "scenario_miss", "seat": "originator", "answer": None}],
                "budget": None, "status": "working", "next": "guardian"}
        record.apply_verdict(data, "", "guardian", self.verdict("accept_moves"))
        self.assertEqual([s["order"] for s in data["stops"]], ["scenario_miss", "accept_moves"])

    def test_a_new_decision_writes_who_as_a_list(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "ready_to_merge", "--seat", "originator",
                "--question", "Merge?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=wt)
        self.assertEqual(self.show(wt)["decisions"][0]["who"], ["pat"])

    def test_a_decision_in_an_old_record_with_who_as_a_string_still_reads(self):
        wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "decisions", json.dumps(
            {"date": "2026-10-01", "who": "pat,sam", "decision": "keep it", "record": ".xv/decisions/old.md"}), cwd=wt)
        self.assertEqual(self.xv("decisions", cwd=wt, check=False).returncode, 0)
        self.assertEqual(self.xv("prompt", "maker", "s1", cwd=wt, check=False).returncode, 0)

    def test_a_prototype_budget_spent_stop_counts_as_started_work_and_needs_settled(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "prototype_budget_spent", "--seat", "originator",
                "--question", "Raise a budget?", "--step", "prototype", cwd=wt)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "raised", "--next", "prototype",
                    cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)

    def test_a_budget_stop_raised_by_hand_needs_settled_to_go_back_to_the_step(self):
        wt = self.new_slice("s1")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=wt)
        self.xv("record", "stop", "s1", "--order", "budget_spent", "--seat", "originator",
                "--question", "Spent.", "--step", "maker", cwd=wt)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go on", "--next", "maker",
                    cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--settled", p.stderr)


class DirectedEditTest(RepoCase):
    """A stop option can carry a directed edit (#132): `xv record offer <id> --option T --settles S --edit <file>
    --old <text> --new <text> --kind changelog|test-rename|test-remove|doc`, the edit flags belonging to the --option
    before them. `xv record answer --pick <n>` on that option makes exactly that edit, in its own commit that names
    the person who directed it, then runs the suite and the standing orders (`xv orders`) and prints the verdict as
    `xv step` does."""

    STORE = "tests/test_store.py"
    REC = ".xv/slices/s1.md"
    RENAME = ("--edit", "tests/test_store.py", "--old", "def test_add_and_list(self):",
              "--new", "def test_adding_then_listing(self):", "--kind", "test-rename")
    REMOVED = ('    def test_use_refuses_more_than_there_is(self):\n'
               '        self.store.add("eggs", 1, date(2026, 10, 30))\n'
               '        with self.assertRaises(ValueError):\n'
               '            self.store.use("eggs", 2)\n'
               '\n')
    CHANGELOG_OLD = "- A line the person wants worded better."
    CHANGELOG_NEW = "- A line the person worded."
    CHANGELOG = ("--edit", "CHANGELOG.md", "--old", CHANGELOG_OLD, "--new", CHANGELOG_NEW, "--kind", "changelog")

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.write("CHANGELOG.md", "# Changelog\n\n## Unreleased\n\n" + self.CHANGELOG_OLD + "\n")
        self.commit_all("a changelog")

    def write(self, rel, text):
        os.makedirs(os.path.dirname(os.path.join(self.wt, rel)), exist_ok=True)
        with open(os.path.join(self.wt, rel), "w") as f:
            f.write(text)

    def read(self, rel):
        with open(os.path.join(self.wt, rel)) as f:
            return f.read()

    def commit_all(self, message):
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", message], self.wt)

    def stop(self, order="scenario_stopped", step=None):
        self.xv("record", "stop", "s1", "--order", order, "--seat", "originator", "--question", "Which edit?",
                *(("--step", step) if step else ()), cwd=self.wt)

    def show(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def offer(self, *edit, check=True):
        return self.xv("record", "offer", "s1", "--option", "Make the edit", "--settles", "The edit is made.", *edit,
                       "--option", "Leave it", "--settles", "Nothing changes.", "--recommend", "1",
                       cwd=self.wt, check=check)

    def answer(self, pick="1"):
        return self.xv("record", "answer", "s1", "--by", "pat", "--answer", "make it", "--pick", pick,
                       cwd=self.wt, check=False)

    def directed(self):
        return sh(["git", "log", "--grep", "directed by pat", "--format=%H"], self.wt).stdout.split()

    def files_in(self, sha):
        return sorted(sh(["git", "show", "--name-only", "--format=", sha], self.wt).stdout.split())

    def head(self):
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def refused(self, *edit):
        p = self.offer(*edit, check=False)
        self.assertNotIn("unrecognized arguments", p.stderr, "the offer knows the edit flags and refuses the edit")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertFalse(self.show()["stops"][-1].get("options"), "a refused offer is not put on the stop")
        return p

    # ---- the offer: what it accepts and refuses

    def test_an_offer_with_an_edit_makes_no_edit_and_no_commit_until_a_person_picks_it(self):
        self.stop()
        before, head = self.read(self.STORE), self.head()
        self.offer(*self.RENAME)
        self.assertEqual(len(self.show()["stops"][-1]["options"]), 2)
        self.assertEqual(self.read(self.STORE), before)
        self.assertEqual(self.head(), head)

    def test_an_old_text_not_in_the_file_is_refused(self):
        self.stop()
        self.refused("--edit", self.STORE, "--old", "def test_no_such_test(self):",
                     "--new", "def test_still_no_such_test(self):", "--kind", "test-rename")

    def test_an_old_text_found_more_than_once_is_refused(self):
        self.stop()
        self.assertGreater(self.read("README.md").count("household"), 1)
        self.refused("--edit", "README.md", "--old", "household", "--new", "home", "--kind", "doc")

    def test_an_empty_old_text_is_refused(self):
        self.stop()
        self.refused("--edit", "README.md", "--old", "", "--new", "More.", "--kind", "doc")

    def test_an_edit_to_a_file_that_does_not_exist_is_refused(self):
        self.stop()
        self.refused("--edit", "docs/nowhere.md", "--old", "a", "--new", "b", "--kind", "doc")

    def test_a_kind_that_does_not_fit_the_file_is_refused(self):
        self.stop()
        cases = [
            ("changelog", "README.md", "It is small on purpose.", "It is tiny on purpose."),
            ("doc", "CHANGELOG.md", self.CHANGELOG_OLD, self.CHANGELOG_NEW),
            ("doc", "pantry/store.py", "class Store:", "class Pantry:"),
            ("test-rename", "README.md", "It is small on purpose.", "It is tiny on purpose."),
            ("test-rename", "pantry/store.py", "def items(self):", "def listed(self):"),
            ("test-remove", "pantry/store.py", "def items(self):", ""),
        ]
        for kind, file, old, new in cases:
            with self.subTest(kind=kind, file=file):
                self.refused("--edit", file, "--old", old, "--new", new, "--kind", kind)

    def test_a_kind_not_on_the_list_is_refused(self):
        self.stop()
        for kind in ("source", "Changelog", ""):
            with self.subTest(kind=kind):
                self.refused("--edit", "CHANGELOG.md", "--old", self.CHANGELOG_OLD,
                             "--new", self.CHANGELOG_NEW, "--kind", kind)

    def test_an_edit_missing_its_file_old_new_or_kind_is_refused(self):
        self.stop()
        pairs = list(zip(self.CHANGELOG[::2], self.CHANGELOG[1::2]))
        for missing in ("--edit", "--old", "--new", "--kind"):
            with self.subTest(missing=missing):
                self.refused(*[x for flag, value in pairs if flag != missing for x in (flag, value)])

    def miss_stop_from_packet(self):
        """A guardian packet that says scenario_miss: yes with an amend: yes miss, and the stop it raises."""
        path = os.path.join(self.wt, "p.md")
        with open(path, "w") as f:
            f.write("---\nslice: s1\nshape_change: no\npitch_contradiction: no\nscenario_miss: yes\n"
                    "expected_moves: 0\n---\n\n# Packet\n\n## Scenario misses\n\n"
                    "- Point 2: the scenario itself is wrong, to: maker, amend: yes (evidence: tests/test_red.py:7)\n")
        report = os.path.join(self.wt, "r.json")
        with open(report, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "guardian", "status": "done", "summary": "done"})
                    + "\n```\n")
        self.xv("record", "report", "s1", "guardian", report, cwd=self.wt)
        self.xv("record", "packet", "s1", path, cwd=self.wt, check=False)  # the packet raises the stop itself
        self.assertEqual([s["order"] for s in self.show()["stops"] if s.get("answer") is None], ["scenario_miss"])

    def test_a_directed_edit_does_not_fire_again_the_stop_its_answer_closed_and_the_next_stands(self):
        self.miss_stop_from_packet()
        self.offer(*self.CHANGELOG)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "narrowed", "--pick", "1",
                    "--next", "close", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.show()
        self.assertEqual([s["order"] for s in data["stops"]], ["scenario_miss"], "no second stop")
        self.assertEqual([s for s in data["stops"] if s.get("answer") is None], [])
        self.assertEqual(data["next"], "close")
        self.assertEqual(len(self.directed()), 1)
        self.assertEqual(data["suite"], "green", "checks the edit can change still run")

    def test_an_edit_with_no_option_before_it_is_refused(self):
        self.stop()
        p = self.xv("record", "offer", "s1", *self.CHANGELOG, "--option", "A", "--settles", "a",
                    cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--option", p.stderr)
        self.assertFalse(self.show()["stops"][-1].get("options"))

    def test_a_rename_that_changes_more_than_the_tests_name_is_refused(self):
        self.stop()
        cases = [
            ('def test_add_and_list(self):\n        self.store.add("rice", 2',
             'def test_adding_then_listing(self):\n        self.store.add("rice", 3'),
            ("self.assertEqual(self.store.items()[0].qty, 4)", "self.assertEqual(self.store.items()[0].qty, 5)"),
        ]
        for old, new in cases:
            with self.subTest(old=old):
                self.assertEqual(self.read(self.STORE).count(old), 1)
                self.refused("--edit", self.STORE, "--old", old, "--new", new, "--kind", "test-rename")

    def test_a_removal_whose_new_text_is_not_empty_is_refused(self):
        self.stop()
        self.assertEqual(self.read(self.STORE).count(self.REMOVED), 1)
        self.refused("--edit", self.STORE, "--old", self.REMOVED, "--new", "    pass\n", "--kind", "test-remove")

    # ---- the pick: the edit, its commit, the move, the record

    def test_a_pick_makes_exactly_the_edit_in_its_own_commit_directed_by_the_person(self):
        self.stop()
        before = self.read("CHANGELOG.md")
        self.offer(*self.CHANGELOG)
        self.answer("1")
        self.assertEqual(self.read("CHANGELOG.md"), before.replace(self.CHANGELOG_OLD, self.CHANGELOG_NEW))
        shas = self.directed()
        self.assertEqual(len(shas), 1, "one commit, and its message says the person directed it")
        self.assertEqual(self.files_in(shas[0]), sorted(["CHANGELOG.md", self.REC]))
        self.assertEqual(sh(["git", "show", f"{shas[0]}:CHANGELOG.md"], self.wt).stdout,
                         before.replace(self.CHANGELOG_OLD, self.CHANGELOG_NEW))
        self.assertEqual(self.show()["moved_tests"], [], "a CHANGELOG line is not a test move")

    def test_the_commit_holds_only_the_edited_file_and_the_record(self):
        self.stop()
        self.offer(*self.CHANGELOG)
        self.write("notes.txt", "scratch\n")
        self.write("README.md", self.read("README.md") + "\nAn edit in progress.\n")
        self.answer("1")
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted(["CHANGELOG.md", self.REC]))
        status = sh(["git", "status", "--porcelain"], self.wt).stdout
        self.assertIn(" M README.md", status)
        self.assertIn("?? notes.txt", status)

    def test_a_doc_line_is_edited_and_committed(self):
        self.stop()
        before = self.read("README.md")
        self.offer("--edit", "README.md", "--old", "It is small on purpose.",
                   "--new", "It is small on purpose, and stays small.", "--kind", "doc")
        self.answer("1")
        self.assertEqual(self.read("README.md"),
                         before.replace("It is small on purpose.", "It is small on purpose, and stays small."))
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted(["README.md", self.REC]))

    def test_a_test_rename_is_recorded_as_a_move_in_the_persons_name(self):
        self.stop()
        before = self.read(self.STORE)
        self.offer(*self.RENAME)
        self.answer("1")
        self.assertEqual(self.read(self.STORE), before.replace("def test_add_and_list(self):",
                                                                "def test_adding_then_listing(self):"))
        moves = self.show()["moved_tests"]
        self.assertEqual([(m["file"], m["by"]) for m in moves], [(self.STORE, "pat")])
        self.assertEqual(len(self.directed()), 1)

    def test_a_test_removal_is_recorded_as_a_move_in_the_persons_name(self):
        self.stop()
        before = self.read(self.STORE)
        self.offer("--edit", self.STORE, "--old", self.REMOVED, "--new", "", "--kind", "test-remove")
        self.answer("1")
        self.assertEqual(self.read(self.STORE), before.replace(self.REMOVED, ""))
        self.assertNotIn("test_use_refuses_more_than_there_is", self.read(self.STORE))
        moves = self.show()["moved_tests"]
        self.assertEqual([(m["file"], m["by"]) for m in moves], [(self.STORE, "pat")])
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted([self.STORE, self.REC]))

    def test_a_rename_renames_the_test_in_slice_only_and_wall_recommendations_in_the_same_commit(self):
        for field in ("slice_only", "wall_recommendations"):
            for test in ("test_add_and_list", "test_used_up_item_stays_listed"):
                self.xv("record", "add", "s1", field,
                        json.dumps({"file": self.STORE, "test": test, "why": "a reason"}), cwd=self.wt)
        self.stop()
        self.offer(*self.RENAME)
        self.answer("1")
        want = ["test_adding_then_listing", "test_used_up_item_stays_listed"]
        data = self.show()
        self.assertEqual([m["test"] for m in data["slice_only"]], want)
        self.assertEqual([r["test"] for r in data["wall_recommendations"]], want)
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        committed = sh(["git", "show", f"{shas[0]}:{self.REC}"], self.wt).stdout
        front = committed.split("\n---\n")[0].splitlines()
        for field in ("slice_only", "wall_recommendations"):
            line = next(x for x in front if x.startswith(field + ": "))
            self.assertEqual([e["test"] for e in json.loads(line[len(field) + 2:])], want, field)

    def test_picking_an_option_without_an_edit_makes_no_edit(self):
        self.stop()
        before, head = self.read("CHANGELOG.md"), self.head()
        self.offer(*self.CHANGELOG)
        self.answer("2")
        self.assertEqual(self.read("CHANGELOG.md"), before)
        self.assertEqual(self.directed(), [])
        self.assertEqual(self.head(), head)

    # ---- after the edit: the suite, the orders, the packet

    def test_after_the_edit_the_suite_and_the_orders_run_and_the_verdict_is_printed(self):
        self.stop()
        self.offer(*self.RENAME)
        p = self.answer("1")
        self.assertEqual(len(self.directed()), 1)
        self.assertEqual(self.show()["suite"], "green")
        v = json.loads(p.stdout)
        self.assertIn("stop", v)
        self.assertIn("fired", v)
        self.assertEqual(p.returncode, 10 if v["stop"] else 0, p.stderr)

    def test_a_suite_that_fails_after_the_edit_is_recorded_red(self):
        self.write("tests/test_broken.py", "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                                           "    def test_fails(self):\n        self.assertEqual(1, 2)\n")
        self.commit_all("a failing test")
        self.stop()
        self.offer(*self.CHANGELOG)
        self.answer("1")
        self.assertEqual(len(self.directed()), 1)
        self.assertEqual(self.show()["suite"], "red")

    def guardian_ran(self):
        report = os.path.join(self.tmp, "guardian.out")
        with open(report, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": "guardian", "status": "done", "summary": "done"})
                    + "\n```\n")
        self.xv("record", "report", "s1", "guardian", report, cwd=self.wt)
        self.write(".xv/slices/s1.packet.md", "---\nslice: s1\nshape_change: no\npitch_contradiction: no\nexpected_moves: 0\n---\n\n"
                                              "# Packet\n\nThe change does what the scenario says.\n")
        self.xv("record", "set", "s1", "next", "close", cwd=self.wt)
        self.xv("record", "packet", "s1", ".xv/slices/s1.packet.md", cwd=self.wt)
        if not [s for s in self.show()["stops"] if s.get("answer") is None]:
            self.stop("ready_to_merge", step="guardian")

    def test_after_the_guardian_the_packet_gets_a_line_and_next_does_not_go_back_to_the_guardian(self):
        self.guardian_ran()
        self.offer(*self.CHANGELOG)
        self.answer("1")
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        packet = self.read(".xv/slices/s1.packet.md")
        self.assertIn("## Directed edits after the guardian", packet)
        after = packet.split("## Directed edits after the guardian", 1)[1]
        lines = [line for line in after.splitlines() if "CHANGELOG.md" in line]
        self.assertEqual(len(lines), 1, after)
        for word in ("changelog", "pat"):
            self.assertIn(word, lines[0])
        self.assertNotEqual(self.show()["next"], "guardian")

    def test_before_the_guardian_no_packet_is_written(self):
        self.stop()
        self.offer(*self.CHANGELOG)
        self.answer("1")
        self.assertEqual(len(self.directed()), 1)
        self.assertIsNone(self.show()["packet"])

    # ---- amended (second): the doc kind, blank lines, whole tests, the stop after the edit

    def test_the_doc_kind_refuses_a_file_under_xv_and_any_skill_md(self):
        line = "A line the person wants worded better here."
        files = [".xv/picture.md", ".xv/rules.md", ".xv/pitch.md", ".xv/slices/notes.md", ".xv/notes/new.md",
                 "SKILL.md", "skills/watch/SKILL.md", "docs/SKILL.md"]
        for rel in files:
            text = self.read(rel) if os.path.exists(os.path.join(self.wt, rel)) else "# A doc\n"
            self.write(rel, text.rstrip("\n") + "\n\n" + line + "\n")
        self.commit_all("docs the watch may not edit")
        for rel in files + ["./.xv/picture.md", "docs/../.xv/rules.md"]:
            with self.subTest(file=rel):
                self.stop()
                self.assertEqual(self.read(rel).count(line), 1)
                self.refused("--edit", rel, "--old", line, "--new", "A line the person worded.", "--kind", "doc")

    def test_a_changelog_or_doc_edit_holding_a_blank_line_is_refused(self):
        self.write("docs/guide.md", "# Guide\n\nThe pantry lists what\n   \nruns out soon.\n")
        self.commit_all("a guide")
        cases = [
            ("changelog", "CHANGELOG.md", "## Unreleased\n\n" + self.CHANGELOG_OLD, "## Unreleased\n\n" + self.CHANGELOG_NEW),
            ("changelog", "CHANGELOG.md", self.CHANGELOG_OLD, self.CHANGELOG_NEW + "\n\n- Another line."),
            ("doc", "README.md", "devices.\n\n    python3 -m pantry.api", "devices:\n\n    python3 -m pantry.api"),
            ("doc", "README.md", "It is small on purpose.", "It is small on purpose.\n\nAnd stays small."),
            ("doc", "docs/guide.md", "The pantry lists what\n   \nruns out soon.", "The pantry lists what runs out soon."),
        ]
        for kind, file, old, new in cases:
            with self.subTest(kind=kind, old=old, new=new):
                self.stop()
                self.assertEqual(self.read(file).count(old), 1)
                self.refused("--edit", file, "--old", old, "--new", new, "--kind", kind)

    def test_a_changelog_edit_may_span_lines_with_no_blank_line(self):
        wrapped = "- A line the person wants\n  worded better."
        self.write("CHANGELOG.md", "# Changelog\n\n## Unreleased\n\n" + wrapped + "\n")
        self.commit_all("a wrapped changelog line")
        self.stop()
        before = self.read("CHANGELOG.md")
        self.offer("--edit", "CHANGELOG.md", "--old", wrapped, "--new", self.CHANGELOG_NEW, "--kind", "changelog")
        self.answer("1")
        self.assertEqual(self.read("CHANGELOG.md"), before.replace(wrapped, self.CHANGELOG_NEW))
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted(["CHANGELOG.md", self.REC]))

    def test_a_doc_edit_may_span_lines_with_no_blank_line(self):
        self.write("docs/guide.md", "# Guide\n\nThe pantry lists what\nruns out soon.\n")
        self.commit_all("a guide")
        self.stop()
        before = self.read("docs/guide.md")
        old, new = "The pantry lists what\nruns out soon.", "The pantry lists what runs out soon,\nfirst."
        self.offer("--edit", "docs/guide.md", "--old", old, "--new", new, "--kind", "doc")
        self.answer("1")
        self.assertEqual(self.read("docs/guide.md"), before.replace(old, new))
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted(["docs/guide.md", self.REC]))

    HELPER = ('    def add_eggs(self, n):\n'
              '        self.store.add("eggs", n, date(2026, 10, 30))\n'
              '\n')

    def with_a_helper(self):
        text = self.read(self.STORE)
        anchor = "    def test_add_and_list(self):\n"
        self.write(self.STORE, text.replace(anchor, self.HELPER + anchor, 1))
        self.commit_all("a helper in the tests")

    def test_a_test_rename_accepts_only_a_test(self):
        self.with_a_helper()
        cases = [
            ("def setUp(self):", "def setup(self):"),
            ("def add_eggs(self, n):", "def add_more_eggs(self, n):"),
            ("def test_add_and_list(self):", "def helper_add_and_list(self):"),
            ("def test_add_and_list(self):", "def add_and_list(self):"),
            ("class StoreTest(unittest.TestCase):", "class StoreTests(unittest.TestCase):"),
        ]
        for old, new in cases:
            with self.subTest(old=old, new=new):
                self.stop()
                self.assertEqual(self.read(self.STORE).count(old), 1)
                self.refused("--edit", self.STORE, "--old", old, "--new", new, "--kind", "test-rename")

    def test_a_test_removal_accepts_only_a_whole_test(self):
        self.with_a_helper()
        body =self.REMOVED.split("\n", 1)[1]
        cases = {
            "setUp": "    def setUp(self):\n        self.store = Store()\n\n",
            "a helper": self.HELPER,
            "only the declaration": self.REMOVED.splitlines(True)[0],
            "the declaration and its first line": "".join(self.REMOVED.splitlines(True)[:2]),
            "all but the last line": "".join(self.REMOVED.splitlines(True)[:3]),
            "cut inside the last line": self.REMOVED[:-8],
            "the body without the declaration": body,
            "the test and the next test's declaration": self.REMOVED + "    def test_used_up_item_stays_listed(self):\n",
        }
        for what, old in cases.items():
            with self.subTest(what=what):
                self.stop()
                self.assertEqual(self.read(self.STORE).count(old), 1, old)
                self.refused("--edit", self.STORE, "--old", old, "--new", "", "--kind", "test-remove")

    def test_the_last_test_in_a_file_is_removed_whole(self):
        last = ('    def test_expiring_lists_items_within_the_window(self):\n'
                '        self.store.add("yogurt", 1, date(2026, 10, 23))\n'
                '        self.store.add("rice", 1, date(2027, 1, 1))\n'
                '        found = self.store.expiring(3, date(2026, 10, 21))\n'
                '        self.assertEqual([i.name for i in found], ["yogurt"])\n')
        self.stop()
        before = self.read(self.STORE)
        self.assertEqual(before.count(last), 1)
        self.offer("--edit", self.STORE, "--old", last, "--new", "", "--kind", "test-remove")
        self.answer("1")
        self.assertEqual(self.read(self.STORE), before.replace(last, ""))
        self.assertEqual([(m["file"], m["by"]) for m in self.show()["moved_tests"]], [(self.STORE, "pat")])
        self.assertEqual(len(self.directed()), 1)

    def test_a_stop_after_the_edit_is_written_to_the_record_and_can_be_answered(self):
        # a rename adds a moved test with a record, so accept_moves is a stop this edit really causes (the answered
        # stop is the ready_to_merge the packet raised, and it does not come back)
        self.guardian_ran()
        before = len(self.show()["stops"])
        logged = self.read(self.REC).count("stop (accept_moves)")
        self.offer(*self.RENAME)
        p = self.answer("1")
        self.assertEqual(len(self.directed()), 1)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        v = json.loads(p.stdout)
        self.assertEqual(v["stop"]["order"], "accept_moves")
        data = self.show()
        self.assertEqual(len(data["stops"]), before + 1, "the stop after the edit is a new stop in the record")
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        self.assertEqual([(s["order"], s["step"]) for s in open_stops], [("accept_moves", "guardian")])
        self.assertEqual(self.read(self.REC).count("stop (accept_moves)"), logged + 1, "the log says the stop fired")
        self.xv("record", "offer", "s1", "--option", "Accept", "--settles", "The moves are accepted.",
                "--option", "Wait", "--settles", "The slice waits.", cwd=self.wt)
        self.assertEqual(len(self.show()["stops"][-1]["options"]), 2)
        self.answer("2")
        self.assertEqual([s for s in self.show()["stops"] if s.get("answer") is None], [])

    def test_a_directed_edit_at_the_merge_stop_does_not_ask_again_and_the_next_stands(self):
        self.guardian_ran()
        self.assertEqual([s["order"] for s in self.show()["stops"] if s.get("answer") is None], ["ready_to_merge"])
        before = len(self.show()["stops"])
        self.offer(*self.CHANGELOG)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "worded", "--pick", "1",
                    "--next", "close", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(len(self.directed()), 1)
        data = self.show()
        self.assertEqual(len(data["stops"]), before, "no second merge stop")
        self.assertEqual([s for s in data["stops"] if s.get("answer") is None], [])
        self.assertEqual(data["next"], "close")

    # ---- amended (third): decorators, the packet in the commit, a renamed name used elsewhere

    DECORATORS = {
        "one decorator": '    @unittest.skip("flaky on a slow disk")\n',
        "two decorators": '    @unittest.skipIf(False, "never")\n    @unittest.skip("flaky on a slow disk")\n',
        "a decorator over two lines": '    @mock.patch.object(\n        Store, "items")\n',
        "a decorator, then a comment": '    @unittest.skip("flaky on a slow disk")\n    # it waits on the disk\n',
        "a pytest mark": "    @pytest.mark.slow\n",
    }

    def decorate(self, decorators):
        """Put decorators above test_use_refuses_more_than_there_is, and commit."""
        decl = self.REMOVED.splitlines(True)[0]
        text = self.read(self.STORE).replace("import unittest\n", "import unittest\nfrom unittest import mock\n", 1)
        self.write(self.STORE, text.replace(decl, decorators + decl, 1))
        self.commit_all("a decorated test")

    def test_a_removal_that_leaves_a_decorator_above_it_is_refused(self):
        base = self.read(self.STORE)
        cases = [(what, decorators, self.REMOVED) for what, decorators in self.DECORATORS.items()]
        cases += [
            ("the lower of two decorators and the test", self.DECORATORS["two decorators"],
             self.DECORATORS["two decorators"].splitlines(True)[1] + self.REMOVED),
            ("the second line of a decorator and the test", self.DECORATORS["a decorator over two lines"],
             self.DECORATORS["a decorator over two lines"].splitlines(True)[1] + self.REMOVED),
            ("the comment under a decorator and the test", self.DECORATORS["a decorator, then a comment"],
             self.DECORATORS["a decorator, then a comment"].splitlines(True)[1] + self.REMOVED),
        ]
        for what, decorators, old in cases:
            with self.subTest(what=what):
                self.write(self.STORE, base)
                self.decorate(decorators)
                self.stop()
                self.assertEqual(self.read(self.STORE).count(old), 1, old)
                self.refused("--edit", self.STORE, "--old", old, "--new", "", "--kind", "test-remove")

    def removes_the_decorated_test_whole(self, decorators):
        self.decorate(decorators)
        self.stop()
        before, old = self.read(self.STORE), decorators + self.REMOVED
        self.assertEqual(before.count(old), 1)
        p = self.offer("--edit", self.STORE, "--old", old, "--new", "", "--kind", "test-remove", check=False)
        self.assertEqual(p.returncode, 0, "a removal of the decorators and the whole test is offered: "
                         + p.stdout + p.stderr)
        self.answer("1")
        after = self.read(self.STORE)
        self.assertEqual(after, before.replace(old, ""))
        self.assertNotIn("test_use_refuses_more_than_there_is", after)
        lines = after.splitlines()
        nxt = lines.index("    def test_used_up_item_stays_listed(self):")
        self.assertFalse([ln for ln in lines[nxt - 3:nxt] if ln.strip().startswith(("@", "Store,"))],
                         "no decorator is left on the next test")
        self.assertEqual([(m["file"], m["by"]) for m in self.show()["moved_tests"]], [(self.STORE, "pat")])
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted([self.STORE, self.REC]))

    def test_a_decorated_test_is_removed_with_its_decorators(self):
        self.removes_the_decorated_test_whole(self.DECORATORS["two decorators"])

    def test_a_test_under_a_decorator_over_two_lines_is_removed_with_it(self):
        self.removes_the_decorated_test_whole(self.DECORATORS["a decorator over two lines"])

    def test_after_the_guardian_the_packet_line_is_in_the_same_commit_as_the_edit_and_the_record(self):
        self.guardian_ran()
        self.commit_all("the guardian's packet")
        packet = ".xv/slices/s1.packet.md"
        self.offer(*self.CHANGELOG)
        self.answer("1")
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        self.assertEqual(self.files_in(shas[0]), sorted(["CHANGELOG.md", self.REC, packet]))
        committed = sh(["git", "show", f"{shas[0]}:{packet}"], self.wt).stdout
        self.assertIn("## Directed edits after the guardian", committed)
        self.assertEqual(committed, self.read(packet), "the packet line is committed, not left in the worktree")
        self.assertNotIn(packet, sh(["git", "status", "--porcelain"], self.wt).stdout)

    def test_a_rename_whose_old_name_appears_elsewhere_in_the_file_is_refused(self):
        base = self.read(self.STORE)
        decl = "    def test_add_and_list(self):\n"
        tail = 'if __name__ == "__main__":\n'
        cases = {
            "a comment": base.replace(decl, "    # test_add_and_list is the one to read first\n" + decl, 1),
            "a string": base.replace(tail, 'FIRST = ["test_add_and_list"]\n\n\n' + tail, 1),
            "an attribute": base.replace(tail, "FIRST = StoreTest.test_add_and_list\n\n\n" + tail, 1),
            "a test of the same name in another class": base.replace(
                tail, "class OtherTest(unittest.TestCase):\n    def test_add_and_list(self, extra=None):\n"
                      "        self.assertIsNone(extra)\n\n\n" + tail, 1),
        }
        for what, text in cases.items():
            with self.subTest(what=what):
                self.write(self.STORE, text)
                self.commit_all(what)
                self.stop()
                self.assertEqual(self.read(self.STORE).count("def test_add_and_list(self):"), 1)
                self.refused(*self.RENAME)

    # ---- amended (fourth): no commit in the packet line, no rename onto a used name, the slice's worktree

    def test_the_packet_line_names_the_file_the_kind_and_the_person_and_no_commit(self):
        self.guardian_ran()
        self.commit_all("the guardian's packet")
        self.offer(*self.CHANGELOG)
        self.answer("1")
        shas = self.directed()
        self.assertEqual(len(shas), 1)
        after = self.read(".xv/slices/s1.packet.md").split("## Directed edits after the guardian", 1)[1]
        lines = [line for line in after.splitlines() if line.startswith("- ")]
        self.assertEqual(len(lines), 1, after)
        self.assertEqual(lines[0], "- CHANGELOG.md (changelog): directed by pat")
        self.assertNotIn(shas[0][:7], after)
        self.assertNotIn("commit", after.lower())

    def test_a_rename_onto_a_name_already_used_in_the_file_is_refused(self):
        base = self.read(self.STORE)
        tail = 'if __name__ == "__main__":\n'
        rename_to = lambda name: ("--edit", self.STORE, "--old", "def test_add_and_list(self):",
                                  "--new", f"def {name}(self):", "--kind", "test-rename")
        cases = {
            "a test in the same class": (base, "test_used_up_item_stays_listed"),
            "a test in another class": (base.replace(
                tail, "class OtherTest(unittest.TestCase):\n    def test_other(self):\n        pass\n\n\n" + tail, 1),
                "test_other"),
            "a name used as an attribute": (base.replace(
                tail, "FIRST = StoreTest.test_expiring_lists_items_within_the_window\n\n\n" + tail, 1),
                "test_expiring_lists_items_within_the_window"),
        }
        for what, (text, name) in cases.items():
            with self.subTest(what=what):
                self.write(self.STORE, text)
                if text != base:
                    self.commit_all(what)
                self.stop()
                self.refused(*rename_to(name))

    def test_a_rename_to_a_name_that_only_begins_another_name_is_accepted(self):
        self.stop()
        self.offer("--edit", self.STORE, "--old", "def test_add_and_list(self):",
                   "--new", "def test_use(self):", "--kind", "test-rename")
        self.answer("1")
        self.assertIn("def test_use(self):", self.read(self.STORE))
        self.assertEqual(len(self.directed()), 1)

    def test_an_answer_run_from_the_main_checkout_edits_tests_and_commits_in_the_slices_worktree(self):
        self.write("tests/test_broken.py", "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                                           "    def test_fails(self):\n        self.assertEqual(1, 2)\n")
        self.commit_all("a failing test, in the slice's worktree only")
        self.stop()
        self.offer(*self.RENAME)
        main_store, main_head = open(os.path.join(self.repo, self.STORE)).read(), \
            sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "make it", "--pick", "1",
                cwd=self.repo, check=False)
        self.assertIn("def test_adding_then_listing(self):", self.read(self.STORE))
        self.assertEqual(len(self.directed()), 1, "the commit is on the slice's branch")
        self.assertEqual(self.files_in(self.directed()[0]), sorted([self.STORE, self.REC]))
        self.assertEqual(open(os.path.join(self.repo, self.STORE)).read(), main_store,
                         "the main checkout's file is not edited")
        self.assertEqual(sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip(), main_head,
                         "the main checkout gets no commit")
        self.assertEqual(sh(["git", "status", "--porcelain"], self.repo).stdout.strip(), "")
        self.assertEqual(self.show()["suite"], "red", "the suite ran in the slice's worktree, where the failing test is")

    def test_an_offer_run_from_the_main_checkout_checks_the_file_in_the_slices_worktree(self):
        self.write("tests/test_only_here.py", "import unittest\n\n\nclass OnlyHere(unittest.TestCase):\n"
                                              "    def test_exists_on_the_slice_branch_only(self):\n        pass\n")
        self.commit_all("a test that exists only on the slice branch")
        self.assertFalse(os.path.exists(os.path.join(self.repo, "tests", "test_only_here.py")))
        self.stop()
        edit = ("--edit", "tests/test_only_here.py", "--old", "def test_exists_on_the_slice_branch_only(self):",
                "--new", "def test_is_found_in_the_worktree(self):", "--kind", "test-rename")
        p = self.xv("record", "offer", "s1", "--option", "Make the edit", "--settles", "The edit is made.", *edit,
                    "--option", "Leave it", "--settles", "Nothing changes.", "--recommend", "1",
                    cwd=self.repo, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(len(self.show()["stops"][-1]["options"]), 2)
        self.answer("1")
        self.assertIn("def test_is_found_in_the_worktree(self):", self.read("tests/test_only_here.py"))

    # ---- the suite run lives in its own module, so record does not import run

    def test_record_does_not_import_run_and_both_import_the_suite_module(self):
        def imported(name):
            tree = ast.parse(open(os.path.join(HOME, "scripts", name)).read())
            found = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    found |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    found.add(node.module.split(".")[0])
            return found, {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

        record_imports, _ = imported("record.py")
        self.assertNotIn("run", record_imports, "record must not import run, at the top or inside a function")
        self.assertIn("suite", record_imports)
        run_imports, run_defs = imported("run.py")
        self.assertIn("suite", run_imports)
        _, suite_defs = imported("suite.py")
        for name in ("run_suite", "shell", "tests_timeout"):
            self.assertIn(name, suite_defs)
            self.assertNotIn(name, run_defs, f"{name} moves to suite.py; run.py does not keep its own")

    def test_the_suite_module_runs_the_command_with_the_slice_base_and_id(self):
        from suite import run_suite, tests_timeout
        config = {"tests": {"command": 'test "$XV_BASE" = abc123 && test "$XV_SLICE" = s9', "timeout": 60}}
        self.assertEqual(run_suite(self.repo, config, "abc123", "s9")[0], "green")
        self.assertEqual(run_suite(self.repo, config)[0], "red")
        self.assertEqual(tests_timeout(config), 60)

    # ---- the watch's brief and the CHANGELOG

    def test_the_watch_brief_states_the_rule_for_a_directed_edit(self):
        text = open(os.path.join(HOME, "skills", "watch", "SKILL.md")).read()
        self.assertIn("approved every word", text)
        self.assertIn("changes no behavior", text)
        self.assertIn("never words a change itself", text)
        for word in ("--edit", "--old", "--new", "--kind", "changelog", "test-rename", "test-remove", "doc"):
            self.assertIn(word, text)

    def test_the_watch_brief_may_not_line_admits_only_a_directed_edit(self):
        text = open(os.path.join(HOME, "skills", "watch", "SKILL.md")).read()
        may_not = text.split("## May not", 1)[1].split("\n## ", 1)[0]
        lines = [line for line in may_not.splitlines()
                 if line.startswith("- ") and "directed" in line and "word" in line]
        self.assertTrue(lines, may_not)

    REFUSALS = {
        "the doc kind refuses a file under .xv/": (".xv/",),
        "the doc kind refuses a SKILL.md": ("SKILL.md",),
        "a changelog or doc edit holds no blank line": ("blank line",),
        "a test kind refuses setUp": ("setUp",),
        "a test kind refuses a helper": ("helper",),
        "a removal is a whole test": ("whole test",),
        "a removal takes the test's decorators with it": ("decorator",),
        "a rename refuses an old name found elsewhere in the file": ("elsewhere", "anywhere else", "also appears"),
        "the suite run's own module": ("scripts/suite.py",),
    }

    def names_every_refusal(self, text):
        for what, words in self.REFUSALS.items():
            with self.subTest(what=what):
                found = any(w in text or (w.islower() and w in text.lower()) for w in words)
                self.assertTrue(found, f"{what}: none of {words} in {text}")

    def test_the_watch_brief_names_every_refusal_and_the_suite_module(self):
        text = open(os.path.join(HOME, "skills", "watch", "SKILL.md")).read()
        self.names_every_refusal(text.split("## A directed edit", 1)[1].split("\n## ", 1)[0])


# A person watching the first green: pick a directed test rename on a real stop and read the commit it makes
# (`git show`): only the test file and the record, its message naming the person, and the packet line when the
# guardian has run. Look for the case nobody wrote down, such as a rename whose old name is a prefix of another
# test's name in slice_only or wall_recommendations. Then try a test-remove that stops one line short of a test's
# end, and pick a CHANGELOG edit at ready_to_merge: no second merge stop, and the answer's --next stands.
# Then remove a decorated test, decorators and all, and read the commit: the next test carries no decorator, and after
# the guardian the packet line is in that same commit.


PACKET = ("---\nslice: s1\nshape_change: no\npitch_contradiction: no\npicture_change: no\nshape_breadth: {breadth}\n"
          "{expected}door: two-way\n---\n\n# Packet\n\n## 1. Shape\n\n- One comparison in pantry/store.py:47.\n{more}")


class RecordStateTest(RepoCase):
    """Accepted answers and the record stay right on the session path (record-state, points 1 to 3)."""

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def open_stops(self, wt):
        return [s["order"] for s in self.show(wt)["stops"] if s.get("answer") is None]

    def report(self, wt, agent, name="r.json", **fields):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps({"agent": agent, "status": "done", "summary": "s", **fields})
                    + "\n```\n")
        self.xv("record", "report", "s1", agent, path, cwd=wt)

    def packet(self, wt, breadth="none", expected="0", more=""):
        path = os.path.join(wt, ".xv", "slices", "s1.packet.md")
        with open(path, "w") as f:
            f.write(PACKET.format(breadth=breadth, more=more,
                                  expected="" if expected is None else f"expected_moves: {expected}\n"))
        self.xv("record", "packet", "s1", path, cwd=wt)
        return path

    def guardian_slice(self, forecast_shape="none"):
        wt = self.new_slice("s1")
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=wt)
        self.xv("record", "set", "s1", "forecast", json.dumps({"shape": forecast_shape}), cwd=wt)
        self.report(wt, "guardian", shape_change="no", pitch_contradiction="no")
        return wt

    # 1. the shape stop keeps the breadth it was accepted at
    def accepted_at_narrow(self):
        wt = self.guardian_slice()
        self.packet(wt, breadth="narrow")
        self.assertIn("shape_wider_than_forecast", self.open_stops(wt))
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "narrow is fine, go on", cwd=wt)
        self.assertEqual(self.open_stops(wt), [])
        return wt

    def test_a_shape_accepted_at_narrow_stops_again_when_a_later_packet_reports_wide(self):
        wt = self.accepted_at_narrow()
        self.packet(wt, breadth="wide")
        self.assertIn("shape_wider_than_forecast", self.open_stops(wt))

    def test_a_shape_accepted_at_narrow_does_not_stop_again_at_narrow(self):
        wt = self.accepted_at_narrow()
        self.packet(wt, breadth="narrow")
        self.assertNotIn("shape_wider_than_forecast", self.open_stops(wt))

    # 2. an accepted "mark slice-only" wall recommendation lists the test in slice_only
    RECS = [{"file": "tests/test_a.py", "test": "test_one_time_wording", "recommend": "mark slice-only",
             "why": "it guards a one-time README line"},
            {"file": "tests/test_a.py", "test": "test_keep_me", "recommend": "stay on the wall", "why": "w"}]

    def stopped_on_accept_moves(self):
        wt = self.new_slice("s1")
        self.report(wt, "guardian", shape_change="no", pitch_contradiction="no", wall_recommendations=self.RECS)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        return wt

    def slice_only(self, wt):
        return [(m.get("file"), m.get("test")) for m in self.show(wt)["slice_only"]]

    def test_an_accepted_mark_slice_only_recommendation_lists_the_test_in_slice_only(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_one_time_wording", cwd=wt)
        self.assertIn(("tests/test_a.py", "test_one_time_wording"), self.slice_only(wt))

    def test_a_refused_mark_slice_only_recommendation_is_not_listed_in_slice_only(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", cwd=wt)
        self.assertEqual(self.slice_only(wt), [])

    def test_an_accepted_stay_on_the_wall_recommendation_is_not_listed_in_slice_only(self):
        wt = self.stopped_on_accept_moves()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--accept-wall", "test_keep_me", cwd=wt)
        self.assertEqual(self.slice_only(wt), [])

    def test_a_guardian_that_marks_its_own_slice_only_recommendation_accepted_lists_nothing(self):
        wt = self.new_slice("s1")
        self.report(wt, "guardian", shape_change="no", pitch_contradiction="no",
                    wall_recommendations=[dict(r, accepted=True) for r in self.RECS])
        self.assertEqual(self.slice_only(wt), [])

    def test_an_accepted_recommendation_with_no_kind_is_not_listed_in_slice_only(self):
        wt = self.new_slice("s1")
        recs = [{"file": "tests/test_a.py", "test": "test_no_kind", "why": "w"},
                {"file": "tests/test_a.py", "test": "test_empty_kind", "recommend": "", "why": "w"}]
        self.report(wt, "guardian", shape_change="no", pitch_contradiction="no", wall_recommendations=recs)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", "--accept-wall", "test_no_kind",
                "--accept-wall", "test_empty_kind", cwd=wt)
        self.assertEqual(self.slice_only(wt), [])

    # 13. `--refuse-wall` on a test accepted earlier takes it out of `slice_only`; both match on the file and the test
    OTHER = {"file": "tests/test_b.py", "test": "test_one_time_wording", "why": "the scenario marked it", "accepted": True}

    def accepted_then_stopped_again(self, *seed):
        wt = self.stopped_on_accept_moves()
        for item in seed:
            self.xv("record", "add", "s1", "slice_only", json.dumps(item), cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_one_time_wording", cwd=wt)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept again?", "--step", "guardian", cwd=wt)
        return wt

    def test_refusing_a_mark_slice_only_recommendation_accepted_earlier_takes_it_out_of_slice_only(self):
        wt = self.accepted_then_stopped_again()
        self.assertIn(("tests/test_a.py", "test_one_time_wording"), self.slice_only(wt))
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "no, keep it on the wall",
                "--refuse-wall", "test_one_time_wording", cwd=wt)
        self.assertNotIn(("tests/test_a.py", "test_one_time_wording"), self.slice_only(wt))

    def test_refusing_it_keeps_a_slice_only_test_of_the_same_name_in_another_file(self):
        wt = self.accepted_then_stopped_again(self.OTHER)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "no, keep it on the wall",
                "--refuse-wall", "test_one_time_wording", cwd=wt)
        self.assertEqual(self.slice_only(wt), [("tests/test_b.py", "test_one_time_wording")])

    def test_accepting_it_lists_it_beside_a_slice_only_test_of_the_same_name_in_another_file(self):
        wt = self.accepted_then_stopped_again(self.OTHER)
        self.assertEqual(sorted(self.slice_only(wt)), [("tests/test_a.py", "test_one_time_wording"),
                                                       ("tests/test_b.py", "test_one_time_wording")])

    def test_accepting_it_again_at_a_later_stop_lists_it_once(self):
        wt = self.accepted_then_stopped_again()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go",
                "--accept-wall", "test_one_time_wording", cwd=wt)
        self.assertEqual(self.slice_only(wt), [("tests/test_a.py", "test_one_time_wording")])

    # 3. `xv record packet` runs the packet checks `xv step` runs
    def test_record_packet_stops_when_the_packets_expected_moves_differs_from_the_record(self):
        wt = self.guardian_slice()
        self.packet(wt, expected="2")
        self.assertIn("expected_moves_wrong", self.open_stops(wt))

    def test_record_packet_stops_when_the_packet_has_no_expected_moves(self):
        wt = self.guardian_slice()
        self.packet(wt, expected=None)
        self.assertIn("expected_moves_wrong", self.open_stops(wt))

    def test_record_packet_moves_a_finding_with_no_evidence_out_of_the_count(self):
        wt = self.guardian_slice()
        path = self.packet(wt, more="\n## 3. Moved tests\n\n- the maker weakened a test somewhere\n")
        with open(path) as f:
            text = f.read()
        self.assertIn("## Dropped by the evidence rule", text)

    def test_record_packet_with_the_right_expected_moves_does_not_stop_with_it(self):
        wt = self.guardian_slice()
        self.packet(wt, expected="0")
        self.assertNotIn("expected_moves_wrong", self.open_stops(wt))

    # 3. `xv record report` runs the move checks `xv step` runs
    def session_slice(self, *flags):
        out = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "The household sees X.", *flags).stdout
        wt = out.strip().splitlines()[-1]
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=wt)
        self.xv("wall", "baseline", "s1", cwd=wt)
        return wt

    def edit_store_test(self, wt, old, new):
        path = os.path.join(wt, "tests", "test_store.py")
        with open(path) as f:
            text = f.read()
        with open(path, "w") as f:
            f.write(text.replace(old, new, 1))

    def expected_files(self, wt):
        return [m["file"] for m in self.show(wt)["moved_tests"] if m.get("expected") == "imports"]

    def test_record_report_for_the_maker_records_an_expected_move(self):
        wt = self.session_slice("--expect-moves", "imports")
        self.edit_store_test(wt, "import unittest\n", "import os  # noqa: F401\nimport unittest\n")
        self.report(wt, "maker", status="green", moved_tests=[])
        self.assertIn("tests/test_store.py", self.expected_files(wt))

    def test_record_report_for_the_cleaner_records_an_expected_move(self):
        wt = self.session_slice("--expect-moves", "imports")
        self.edit_store_test(wt, "import unittest\n", "import os  # noqa: F401\nimport unittest\n")
        self.report(wt, "cleaner", commit=None, applied=[])
        self.assertIn("tests/test_store.py", self.expected_files(wt))

    def test_record_report_for_the_maker_finds_an_unrecorded_move_for_the_orders(self):
        wt = self.session_slice()
        self.edit_store_test(wt, '["yogurt"])', '["yogurt"] or [])')
        self.report(wt, "maker", status="green", moved_tests=[])
        p = self.xv("orders", "s1", "--after", "maker", cwd=wt, check=False)
        self.assertIn("unrecorded_move", [f["order"] for f in json.loads(p.stdout)["fired"]], p.stdout)


class WallFlagFormsTest(RepoCase):
    """defects-tools 7: --accept-wall and --refuse-wall take the test with its file, in the forms the covers check takes."""

    RECS = [{"file": "tests/test_a.py", "test": "test_one", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_b.py", "test": "test_one", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_a.py", "test": "test_only_a", "recommend": "stay on the wall", "why": "w"},
            {"file": "tests/test_c.py", "test": "Wall.test_cls", "recommend": "stay on the wall", "why": "w"}]

    def stopped(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "g.txt")
        report = {"agent": "guardian", "status": "done", "summary": "p", "shape_change": "no",
                  "pitch_contradiction": "no", "wall_recommendations": self.RECS}
        with open(path, "w") as f:
            f.write("```xv-report\n" + json.dumps(report) + "\n```\n")
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        self.xv("record", "stop", "s1", "--order", "accept_moves", "--seat", "originator",
                "--question", "accept?", "--step", "guardian", cwd=wt)
        return wt

    def answer(self, wt, *flags):
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", *flags, cwd=wt, check=False)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        return p, {(r["file"], r["test"]): r for r in data["wall_recommendations"]}

    def test_file_then_test_picks_one_of_two_files_that_share_a_name(self):
        wt = self.stopped()
        p, recs = self.answer(wt, "--accept-wall", "tests/test_a.py::test_one")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIs(recs[("tests/test_a.py", "test_one")]["accepted"], True)
        self.assertIs(recs[("tests/test_b.py", "test_one")]["accepted"], False)

    def test_refuse_wall_takes_the_same_form(self):
        wt = self.stopped()
        p, recs = self.answer(wt, "--accept-wall", "tests/test_b.py::test_one",
                              "--refuse-wall", "tests/test_a.py::test_one")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIs(recs[("tests/test_b.py", "test_one")]["accepted"], True)
        self.assertIs(recs[("tests/test_a.py", "test_one")]["accepted"], False)
        self.assertIs(recs[("tests/test_a.py", "test_one")].get("refused"), True)

    def accepts_the_class_test(self, form):
        wt = self.stopped()
        p, recs = self.answer(wt, "--accept-wall", form)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIs(recs[("tests/test_c.py", "Wall.test_cls")]["accepted"], True)
        self.assertIs(recs[("tests/test_a.py", "test_only_a")]["accepted"], False)

    def test_file_then_class_dot_test(self):
        self.accepts_the_class_test("tests/test_c.py::Wall.test_cls")

    def test_class_hash_test(self):
        self.accepts_the_class_test("Wall#test_cls")

    def test_module_dot_class_dot_test(self):
        self.accepts_the_class_test("tests.test_c.Wall.test_cls")

    def test_class_arrow_test(self):
        self.accepts_the_class_test("Wall > test_cls")

    def test_a_bare_name_still_works_when_one_recommendation_has_it(self):
        wt = self.stopped()
        p, recs = self.answer(wt, "--accept-wall", "test_only_a")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIs(recs[("tests/test_a.py", "test_only_a")]["accepted"], True)

    def test_a_bare_name_two_files_share_is_refused_and_the_refusal_names_each_file_and_test(self):
        wt = self.stopped()
        p, recs = self.answer(wt, "--accept-wall", "test_one")
        self.assertNotEqual(p.returncode, 0, "a bare name two files share was taken")
        self.assertIn("tests/test_a.py::test_one", p.stderr)
        self.assertIn("tests/test_b.py::test_one", p.stderr)
        open_stops = [s for s in json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["stops"]
                      if s.get("answer") is None]
        self.assertEqual(len(open_stops), 1, "the refused answer closed the stop")

    def test_a_bare_name_two_files_share_is_refused_for_refuse_wall_too(self):
        wt = self.stopped()
        p, recs = self.answer(wt, "--refuse-wall", "test_one")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("tests/test_a.py::test_one", p.stderr)
        self.assertIn("tests/test_b.py::test_one", p.stderr)


class SameMoveTwiceTest(RepoCase):
    """defects-tools 12: one move told twice, with only a comma or a space of difference, is recorded once."""

    BASE = "was: self.assertEqual(x, 1); now: self.assertEqual(x, 2)"

    def move(self, wt, assertion):
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", assertion, "--why", "w", cwd=wt)
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)["moved_tests"]

    def told_twice(self, variant):
        wt = self.new_slice("s1")
        self.move(wt, self.BASE)
        self.assertEqual(len(self.move(wt, variant)), 1, "the same move was recorded twice")

    def test_a_dropped_comma_is_the_same_move(self):
        self.told_twice("was: self.assertEqual(x 1); now: self.assertEqual(x, 2)")

    def test_a_dropped_space_is_the_same_move(self):
        self.told_twice("was: self.assertEqual(x,1); now: self.assertEqual(x,2)")

    def test_an_extra_space_is_the_same_move(self):
        self.told_twice("was:  self.assertEqual(x, 1);  now: self.assertEqual(x,  2)")

    def test_an_equal_and_a_not_equal_are_two_moves(self):
        wt = self.new_slice("s1")
        self.move(wt, "was: self.assertTrue(x == 1); now: self.assertTrue(x == 2)")
        moves = self.move(wt, "was: self.assertTrue(x != 1); now: self.assertTrue(x != 2)")
        self.assertEqual(len(moves), 2)


# What a person should watch on the first green run of RecordStateTest: accept a narrow shape at
# `shape_wider_than_forecast`, then attach a packet that says wide and see the stop come back; accept a
# "mark slice-only" recommendation with `--accept-wall` and see the test in `slice_only`; at a later
# `accept_moves`, `--refuse-wall` the same test and see it leave `slice_only`; and run the
# session path (`xv record report`, `xv orders`, `xv record packet`) and see the same stops `xv step` gives.

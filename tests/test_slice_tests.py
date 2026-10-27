import json
import os

from helpers import HOME, RepoCase

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


class ScenarioBriefTest(RepoCase):
    fixture = False

    def test_the_brief_asks_for_the_existing_test_file_and_a_new_one_only_when_none_exists(self):
        text = open(os.path.join(HOME, "skills", "scenario", "SKILL.md")).read()
        step6 = [ln for ln in text.splitlines() if ln.startswith("6.")][0]
        self.assertNotIn("new files where you can", step6)
        self.assertIn("existing test file", step6)
        self.assertIn("slice_only", text)


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

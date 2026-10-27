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

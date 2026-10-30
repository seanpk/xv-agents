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
        self.assertEqual(data["decisions"][0]["who"], "pat")
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
            f.write("---\nslice: s1\nshape_change: no\npitch_contradiction: no\nscenario_miss: yes\n---\n\n"
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

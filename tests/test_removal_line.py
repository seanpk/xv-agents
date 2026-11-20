import json
import os
import unittest

from helpers import HOME, RepoCase

import record
from test_record import commit_tests


class SliceOnlyRemovalLineTest(RepoCase):
    """A slice-only removal names its line (`--line`), and the check reads the tree: the text of that line, counted
    in the file now against the file when the step began."""

    PY = ("import unittest\n\n\nclass Red(unittest.TestCase):\n    def test_milk_today(self):\n        pass\n\n"
          "    def test_other(self):\n        pass\n")
    PY_GONE = "import unittest\n\n\nclass Red(unittest.TestCase):\n    def test_other(self):\n        pass\n"
    JS = 'describe("milk", () => {\n  it("shows milk due today", () => {\n    expect(1).toBe(1);\n  });\n});\n'
    JS_GONE = 'describe("milk", () => {\n});\n'
    TWICE = "def test_same():\n    assert 1\n\n\ndef test_same():\n    assert 2\n"
    TWICE_ONE = "def test_same():\n    assert 2\n"

    def show(self, wt, sid="s1"):
        return json.loads(self.xv("record", "show", sid, "--json", cwd=wt).stdout)

    def move(self, wt, file, line, note="removed", sid="s1", check=False):
        return self.xv("record", "move", sid, "--file", file, "--slice-only", "--line", str(line), "--assertion",
                       note, "--why", "slice-only; removed", "--by", "cleaner", cwd=wt, check=check)

    def write(self, wt, file, text):
        with open(os.path.join(wt, file), "w") as f:
            f.write(text)

    def left(self, wt, sid="s1"):
        return record.removals_not_made(wt, self.show(wt, sid), "cleaner", None)

    def setup_case(self, file, start, now, line, sid="s1"):
        wt = self.new_slice(sid)
        commit_tests(wt, {file: start})
        p = self.move(wt, file, line, sid=sid)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.write(wt, file, now)
        return wt

    # 1. the command
    def test_a_blank_line_is_refused_and_nothing_is_recorded(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        p = self.move(wt, "tests/test_red.py", 2)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.show(wt)["moved_tests"], [])

    def test_a_number_past_the_end_of_the_file_is_refused_and_nothing_is_recorded(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        for n in (10, 999):
            with self.subTest(line=n):
                p = self.move(wt, "tests/test_red.py", n)
                self.assertNotEqual(p.returncode, 0)
                self.assertEqual(self.show(wt)["moved_tests"], [])

    def test_a_line_that_is_not_a_positive_number_is_refused(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        for n in ("0", "-1", "abc"):
            with self.subTest(line=n):
                self.assertNotEqual(self.move(wt, "tests/test_red.py", n).returncode, 0)
                self.assertEqual(self.show(wt)["moved_tests"], [])

    def test_the_assertion_is_a_free_note_when_a_line_is_given(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        p = self.move(wt, "tests/test_red.py", 5, note="removed Red.test_milk_today as asked; see issue#183")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(self.show(wt)["moved_tests"]), 1)

    def test_the_line_is_read_from_the_file_at_the_start_not_the_tree_now(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        self.write(wt, "tests/test_red.py", "x = 1\n")  # the tree is now one line long
        self.assertEqual(self.move(wt, "tests/test_red.py", 5).returncode, 0)

    # 2. the check
    def test_a_line_whose_text_is_still_in_the_file_stops_naming_file_number_and_text(self):
        wt = self.setup_case("tests/test_red.py", self.PY, self.PY, 5)
        left = self.left(wt)
        self.assertEqual(len(left), 1, left)
        self.assertIn("tests/test_red.py", left[0])
        self.assertIn("5", left[0])
        self.assertIn("def test_milk_today(self):", left[0])

    def test_a_line_whose_text_is_gone_passes(self):
        wt = self.setup_case("tests/test_red.py", self.PY, self.PY_GONE, 5)
        self.assertEqual(self.left(wt), [])

    def test_the_note_is_not_read_by_the_check(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        self.move(wt, "tests/test_red.py", 5, note="Red.test_other")  # names a test that stays
        self.write(wt, "tests/test_red.py", self.PY_GONE.replace("test_other", "test_noted"))
        self.assertEqual(self.left(wt), [])

    # 4. the table: a Python def, a JS it() with spaces in its title, a line in the file twice
    def test_table_python_def_js_it_and_a_doubled_line(self):
        table = [
            ("python-def", "tests/test_red.py", self.PY, 5, self.PY_GONE, self.PY),
            ("js-it-with-spaces", "tests/red.test.js", self.JS, 2, self.JS_GONE, self.JS),
            ("line-twice", "tests/test_same.py", self.TWICE, 1, self.TWICE_ONE, self.TWICE),
        ]
        for name, file, start, line, removed, kept in table:
            with self.subTest(case=name, outcome="removed passes"):
                wt = self.setup_case(file, start, removed, line, sid="a-" + name)
                self.assertEqual(self.left(wt, "a-" + name), [])
            with self.subTest(case=name, outcome="none removed stops"):
                wt = self.setup_case(file, start, kept, line, sid="b-" + name)
                self.assertEqual(len(self.left(wt, "b-" + name)), 1)

    def test_the_js_title_with_spaces_is_named_in_the_stop(self):
        wt = self.setup_case("tests/red.test.js", self.JS, self.JS, 2)
        self.assertIn('it("shows milk due today"', self.left(wt)[0])

    # 6. one move
    def test_two_slice_only_moves_for_one_file_and_line_are_one_move(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        self.move(wt, "tests/test_red.py", 5, note="first telling", check=True)
        self.move(wt, "tests/test_red.py", 5, note="a different second telling", check=True)
        self.assertEqual(len(self.show(wt)["moved_tests"]), 1)

    def test_two_slice_only_moves_for_two_lines_are_two_moves(self):
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": self.PY})
        self.move(wt, "tests/test_red.py", 5, check=True)
        self.move(wt, "tests/test_red.py", 8, check=True)
        self.assertEqual(len(self.show(wt)["moved_tests"]), 2)


class CoverageReadsTheLineNotTheNoteTest(RepoCase):
    """1. `--assertion` is a free note that nothing reads: the coverage check finds a cleaner-removed test by the
    text of the line the move recorded."""

    def check(self, note, name):
        import run
        wt = self.new_slice("s1")
        commit_tests(wt, {"tests/test_red.py": SliceOnlyRemovalLineTest.PY})
        p = self.xv("record", "move", "s1", "--file", "tests/test_red.py", "--slice-only", "--line", "5",
                    "--assertion", note, "--why", "slice-only; removed", "--by", "cleaner", cwd=wt, check=False)
        self.assertEqual(p.returncode, 0, p.stderr)
        with open(os.path.join(wt, "tests/test_red.py"), "w") as f:
            f.write(SliceOnlyRemovalLineTest.PY_GONE)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        data["red"] = {"files": ["tests/test_red.py"]}
        report = {"covered": [{"outcome": "1", "test": [name]}], "not_covered": []}
        return run.unreadable_input(wt, data, report)

    def test_a_free_note_does_not_hide_a_removed_test_from_the_later_check(self):
        self.assertEqual(self.check("removed as asked", "test_milk_today"), [])

    def test_a_note_naming_a_test_does_not_excuse_another_missing_test(self):
        out = self.check("removed test_ghost as asked", "test_ghost")
        self.assertEqual(len(out), 1, out)


class RemovalLineBriefsTest(unittest.TestCase):
    """5 and 6. The briefs and the picture say the new rule."""

    def read(self, *parts):
        with open(os.path.join(HOME, *parts)) as f:
            return " ".join(f.read().split())

    def test_the_cleaner_brief_says_how_to_give_the_line(self):
        text = self.read("skills", "cleaner", "SKILL.md")
        self.assertIn("--line", text)
        self.assertRegex(text, r"(?i)line where the (removed )?test starts")

    def test_the_picture_says_what_each_check_reads(self):
        text = self.read(".xv", "picture.md")
        self.assertIn("--line", text)
        self.assertRegex(text, r"(?i)accepted slice-only[^.]*any whole word in the file")

    def test_the_watch_brief_lists_the_stop_for_a_no_with_a_miss_listed(self):
        text = self.read("skills", "watch", "SKILL.md")
        self.assertIn("change_misses_scenario: no", text)
        self.assertIn("## Scenario misses", text)


from test_pairing import PairingCase  # noqa: E402
from test_run import WatchLoopSetup  # noqa: E402


class RemovalCommittedBeforeItsMoveTest(PairingCase):
    """3 and 8. In a pairing the start commit is the pairing's `start_commit`; a removal committed in the pairing and
    recorded after is taken."""

    def test_a_removal_committed_in_a_pairing_then_moved_with_line_is_taken(self):
        self.open_stop()
        self.commit("tests/test_milk.py", SliceOnlyRemovalLineTest.PY, "the tests")
        before_start = self.head()  # HEAD before `xv pairing start` commits the record
        self.start()
        start = self.pairings()[0]["start_commit"]
        self.assertEqual(start, before_start)
        self.commit("tests/test_milk.py", SliceOnlyRemovalLineTest.PY_GONE, "pairing (pat with claude): remove it")
        p = self.xv("record", "move", "s1", "--file", "tests/test_milk.py", "--slice-only", "--line", "5",
                    "--assertion", "removed", "--why", "slice-only; removed", "--by", "pat", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        moves = self.record()["moved_tests"]
        self.assertEqual(len(moves), 1)
        self.assertIn("def test_milk_today(self):", json.dumps(moves))
        self.assertEqual(record.removals_not_made(self.wt, self.record(), "cleaner", None), [])


class StepStartRemovalTest(WatchLoopSetup):
    """8. `xv step` saves HEAD as `step_start` before the agent runs; a removal the agent commits and then records
    with `--line` is read from there."""

    def step(self, agent, check=True, **env):
        from unittest import mock
        with mock.patch.dict(os.environ, env):
            return self.xv("step", agent, "s1", cwd=self.wt, check=check)

    def test_step_saves_head_as_step_start_before_the_agent_runs(self):
        self.step("forecaster")
        before = sh_head(self.wt)
        self.step("scenario")
        data = self.record()
        self.assertEqual(data["step_start"]["agent"], "scenario")
        self.assertEqual(data["step_start"]["commit"], before)

    def test_a_removal_committed_by_the_step_then_moved_with_line_is_taken(self):
        self.step("forecaster")
        self.step("scenario")
        self.step("maker")
        text = open(os.path.join(self.wt, "tests", "test_red.py")).read()
        line = text.split("\n").index("    def test_milk_today(self):") + 1
        p = self.step("cleaner", check=False, FAKE_CLEANER_COMMITS_REMOVAL_THEN_MOVES_LINE=str(line))
        self.assertNotIn("removal_not_made", p.stdout, p.stdout + p.stderr)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        moves = self.record()["moved_tests"]
        self.assertEqual(len(moves), 1)
        self.assertIn("def test_milk_today(self):", json.dumps(moves))

    def test_a_slice_only_move_between_steps_reads_head_not_the_last_steps_start(self):
        self.step("forecaster")
        self.step("scenario")
        self.step("maker")  # step_start is now the maker's start commit, and stays in the record
        path = os.path.join(self.wt, "tests", "test_red.py")
        text = open(path).read()
        with open(path, "w") as f:
            f.write("# one\n# two\n# three\n" + text)  # every line moves down three
        from helpers import sh
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "between steps: three comment lines"], self.wt)
        line = open(path).read().split("\n").index("    def test_milk_today(self):") + 1
        p = self.xv("record", "move", "s1", "--file", "tests/test_red.py", "--slice-only", "--line", str(line),
                    "--assertion", "removed", "--why", "slice-only; removed", "--by", "cleaner", cwd=self.wt,
                    check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        moves = self.record()["moved_tests"]
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["line_text"], "def test_milk_today(self):")


def sh_head(wt):
    from helpers import sh
    return sh(["git", "rev-parse", "HEAD"], wt).stdout.strip()

import json
import os
import socket
import subprocess
import sys
import time
import unittest

from helpers import HOME, RepoCase, sh

import recording

REC = os.path.join(HOME, "evals", "fixture", ".xv", "recordings")


class RecordingTest(unittest.TestCase):
    def test_an_api_sequence_keeps_the_stated_expected_value(self):
        rec = recording.load(os.path.join(REC, "expiring-today.json"))
        self.assertEqual(len(rec["steps"]), 3)
        self.assertTrue(rec["steps"][-1]["has_expected"])
        text = recording.to_python(rec, "milk_today", "http://x")
        self.assertIn("'name': 'milk'", text)
        self.assertNotIn("self.fail", text)

    def test_a_har_has_no_expected_value_so_the_draft_fails_on_purpose(self):
        rec = recording.load(os.path.join(REC, "expiring-today.har"))
        self.assertEqual([s["method"] for s in rec["steps"]], ["POST", "POST", "GET"])
        self.assertIn("self.fail(", recording.to_python(rec, "milk_today"))
        self.assertIn("test.fail(true", recording.to_playwright(rec, "milk_today"))


class RedFromRecordingTest(RepoCase):
    """The draft from the fixture's recording is red on the fixture's defect."""

    def test_the_draft_fails_on_the_defect(self):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        server = subprocess.Popen([sys.executable, "-c",
                                   f"from pantry.api import serve; import threading; serve(port={port}); "
                                   "threading.Event().wait()"], cwd=self.repo)
        try:
            time.sleep(0.5)
            self.xv("recording", "to-test", ".xv/recordings/expiring-today.json", "--lang", "python",
                    "--base-url", f"http://127.0.0.1:{port}", "--out", "tests/test_red.py")
            p = sh([sys.executable, "-m", "unittest", "tests.test_red"], self.repo, check=False)
            self.assertIn("FAILED (failures=1)", p.stderr)
            self.assertIn("'milk'", p.stderr)
        finally:
            server.terminate()
            server.wait()


class SliceNewMissingFileTest(RepoCase):
    """#154 item 6: a path that is not a file is refused before the worktree and the branch are made."""

    def assert_nothing_left(self, flag):
        missing = os.path.join(self.tmp, "no-such-file")
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "The household sees X.",
                    flag, missing, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("no such file", p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertNotIn("xv/s1", sh(["git", "branch", "--list"], self.repo).stdout)
        self.assertEqual(len(sh(["git", "worktree", "list"], self.repo).stdout.strip().splitlines()), 1)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", "s1")))

    def test_a_missing_recording_path_makes_no_worktree_and_no_branch(self):
        self.assert_nothing_left("--recording")

    def test_a_missing_scenario_file_makes_no_worktree_and_no_branch(self):
        self.assert_nothing_left("--scenario-file")


class SliceNewIgnoreRepeatTest(RepoCase):
    """--ignore given more than once puts every value in the record's May ignore section, in order."""

    def may_ignore(self, *values):
        args = []
        for v in values:
            args += ["--ignore", v]
        self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "The household sees X.", *args)
        text = open(os.path.join(self.repo, ".xv", "worktrees", "s1", ".xv", "slices", "s1.md")).read()
        return text.split("## May ignore")[1]

    def test_every_ignore_value_reaches_the_record_in_order(self):
        section = self.may_ignore("first thing", "second thing", "third thing")
        self.assertEqual([section.index(x) for x in ("first thing", "second thing", "third thing")],
                         sorted(section.index(x) for x in ("first thing", "second thing", "third thing")))

    def test_a_single_ignore_works_as_before(self):
        self.assertIn("\nonly this\n", self.may_ignore("only this"))
        self.assertNotIn("- only this", self.may_ignore_again("only this"))

    def may_ignore_again(self, value):
        self.xv("slice", "new", "s2", "--by", "pat", "--scenario", "The household sees X.", "--ignore", value)
        text = open(os.path.join(self.repo, ".xv", "worktrees", "s2", ".xv", "slices", "s2.md")).read()
        return text.split("## May ignore")[1]

    def test_more_than_one_ignore_is_a_bullet_list_one_per_value_in_order(self):
        section = self.may_ignore("first thing", "second thing", "third thing")
        self.assertIn("\n- first thing\n- second thing\n- third thing\n", section)


if __name__ == "__main__":
    unittest.main()

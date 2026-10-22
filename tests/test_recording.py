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


if __name__ == "__main__":
    unittest.main()

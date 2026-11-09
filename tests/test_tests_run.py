import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import HOME

RUN = os.path.join(HOME, "tests", "run.py")
PASSING = "import unittest\n\n\nclass Ok(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n"
NO_TEST = "import unittest\n\n\nclass Helpers(unittest.TestCase):\n    pass\n"
SKIPPED_CLASS = ("import unittest\n\n\nclass Skipped(unittest.TestCase):\n    @classmethod\n"
                 "    def setUpClass(cls):\n        raise unittest.SkipTest('the whole class is skipped')\n\n"
                 "    def test_a(self):\n        pass\n\n    def test_b(self):\n        pass\n")


class TestsRunGuardsTheSuiteTest(unittest.TestCase):
    """defects-tools 10: tests/run.py fails, and names the file, when a test_*.py gives no test, and when
    fewer tests run than were collected. It runs here on a small suite of its own."""

    def suite(self, **files):
        d = tempfile.mkdtemp(prefix="xv-runpy-")
        self.addCleanup(shutil.rmtree, d, True)
        shutil.copy(RUN, os.path.join(d, "run.py"))
        for name, text in files.items():
            with open(os.path.join(d, name + ".py"), "w") as f:
                f.write(text)
        return d

    def run_suite(self, d):
        return subprocess.run([sys.executable, os.path.join(d, "run.py"), "--jobs", "2"], cwd=d,
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def test_a_suite_whose_files_all_give_tests_passes(self):
        p = self.run_suite(self.suite(test_ok=PASSING))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_a_test_file_that_gives_no_test_fails_the_run_and_is_named(self):
        p = self.run_suite(self.suite(test_ok=PASSING, test_empty=NO_TEST))
        self.assertNotEqual(p.returncode, 0, "a test file with no test passed:\n" + p.stdout + p.stderr)
        self.assertIn("test_empty.py", p.stdout + p.stderr)

    def test_fewer_tests_run_than_were_collected_fails_the_run(self):
        p = self.run_suite(self.suite(test_ok=PASSING, test_skipped=SKIPPED_CLASS))
        self.assertNotEqual(p.returncode, 0, "two collected tests never ran and the run passed:\n" + p.stdout + p.stderr)

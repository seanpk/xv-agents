import json
import os
import re
import shutil
import unittest

from helpers import RepoCase, sh


class InitTriesGuessesTest(RepoCase):
    """`xv init` runs the test command it chose and reports the outcome, the module count, and fixture folders."""

    no_try = False

    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def write(self, rel, text=""):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def commit(self):
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "more"], self.repo)

    def sentinel_test(self):
        marker = os.path.join(self.tmp, "ran-marker")
        self.write("tests/test_zz_sentinel.py",
                   "import unittest\n\n\nclass Sentinel(unittest.TestCase):\n"
                   "    def test_it(self):\n"
                   f"        open({marker!r}, 'w').write('ran')\n")
        self.commit()
        return marker

    def test_without_the_flag_the_test_command_runs(self):
        marker = self.sentinel_test()
        self.xv("init")
        self.assertTrue(os.path.exists(marker), "the try runs the test command")

    def test_no_try_does_not_run_the_test_command(self):
        marker = self.sentinel_test()
        p = self.xv("init", "--no-try", check=False)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(os.path.exists(marker), "--no-try skips the test command")

    def test_no_try_still_writes_the_project_layer(self):
        out = json.loads(self.xv("init", "--no-try").stdout)
        for name in ("config.yml", "boundary-all.md"):
            self.assertTrue(os.path.exists(os.path.join(self.repo, ".xv", name)), name)
        self.assertIn("timeout", out["tests"])

    def test_no_try_does_not_run_a_failing_command(self):
        self.write("tests/test_zz_broken.py",
                   "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                   "    def test_it(self):\n"
                   "        self.fail('BOOM-MARKER-7431')\n")
        self.commit()
        out = self.xv("init", "--no-try").stdout
        self.assertNotIn("BOOM-MARKER-7431", out)

    def test_a_passing_command_is_reported_as_passed(self):
        run = json.dumps(json.loads(self.xv("init").stdout)["test_run"]).lower()
        self.assertRegex(run, r"pass")
        self.assertNotRegex(run, r"fail|timed out")

    def test_the_output_still_gives_the_tests_timeout(self):
        self.assertIn("timeout", json.loads(self.xv("init").stdout)["tests"])

    def test_a_failing_command_is_reported_as_failed_with_the_last_lines(self):
        self.write("tests/test_zz_broken.py",
                   "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                   "    def test_it(self):\n"
                   "        self.fail('BOOM-MARKER-7431')\n")
        self.commit()
        p = self.xv("init", check=False)
        self.assertEqual(p.returncode, 0, "a failing guess does not make init itself fail")
        out = p.stdout
        self.assertRegex(out.lower(), r"fail")
        self.assertIn("BOOM-MARKER-7431", out, "the tail of the command's output is shown")

    def test_the_output_gives_the_number_of_modules_in_boundary_all(self):
        out = self.xv("init").stdout
        text = open(os.path.join(self.repo, ".xv", "boundary-all.md")).read()
        n = len([l for l in text.splitlines() if l.startswith("- ")])
        self.assertGreater(n, 0)
        self.assertRegex(out.lower(), rf"(\b{n}\b[^\n]{{0,40}}module|module[^\n]{{0,40}}\b{n}\b)")

    def test_folders_that_look_like_fixtures_and_hold_code_are_listed(self):
        self.write("examples/demo.py", "print('hi')\n")
        self.write("fixtures/seed.py", "X = 1\n")
        self.write("setups/notes.txt", "no code here\n")
        self.write("pantry/helper_data/readme.md", "docs\n")
        self.commit()
        out = self.xv("init").stdout
        self.assertIn("examples", out)
        self.assertIn("fixtures", out)
        self.assertNotIn("setups", out, "a folder with no code is not a fixture folder")

    def test_a_fixture_folder_git_ignores_is_not_listed(self):
        self.write(".gitignore", ".venv/\n")
        self.write(".venv/examples/lib.py", "X = 1\n")
        self.write("examples/demo.py", "print('hi')\n")
        self.commit()
        out = self.xv("init").stdout
        self.assertIn("examples", out)
        self.assertNotIn(".venv", out, "an ignored folder is never listed")

    def test_a_repo_with_no_fixture_folder_lists_none(self):
        out = self.xv("init").stdout
        self.assertNotRegex(out, r"examples|fixtures|setups")


if __name__ == "__main__":
    unittest.main()

# Watch on the first green run: init prints, beside the config it wrote, "passed" for the guessed
# test command; break one test and see "failed" with the last lines of its output; see the module
# count match the lines of .xv/boundary-all.md; and add a code file under examples/ to see that
# folder named. A timeout is not covered here: the scenario names no way to shorten the limit.

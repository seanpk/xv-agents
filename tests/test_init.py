import os
import shutil
import unittest

from helpers import RepoCase, sh

from xvlib import load_config


class InitTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def test_init_writes_the_layer_and_guesses_tests_and_roots(self):
        self.xv("init")
        config = load_config(self.repo)
        self.assertEqual(config["tests"]["command"], "python3 -m unittest discover -s tests -t .")
        self.assertEqual(config["source"]["roots"], ["pantry"])
        self.assertTrue(config["promote"]["include_name"])
        for name in ("pitch.md", "picture.md", "standards.md", "estimation.md", "learnings.md", "rules.md"):
            self.assertTrue(os.path.exists(os.path.join(self.repo, ".xv", name)), name)
        self.assertIn("- api: pantry/api.py", open(os.path.join(self.repo, ".xv", "boundary-all.md")).read())
        status = sh(["git", "status", "--porcelain", "--ignored", ".xv/boundary-all.md"], self.repo).stdout
        self.assertTrue(status.startswith("!!"), "the outsider read's input stays out of the repo")

    def test_init_never_overwrites(self):
        os.makedirs(os.path.join(self.repo, ".xv"))
        with open(os.path.join(self.repo, ".xv", "pitch.md"), "w") as f:
            f.write("ours\n")
        out = self.xv("init").stdout
        self.assertIn('"pitch.md"', out.split('"kept"')[1])
        self.assertEqual(open(os.path.join(self.repo, ".xv", "pitch.md")).read(), "ours\n")


if __name__ == "__main__":
    unittest.main()

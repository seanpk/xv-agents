import json
import os
import shutil
import unittest

from helpers import RepoCase, sh


class InitRerunTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def path(self, name):
        return os.path.join(self.repo, ".xv", name)

    def test_a_second_init_fills_in_a_missing_pitch_and_keeps_the_rest(self):
        self.xv("init")
        os.remove(self.path("pitch.md"))
        with open(self.path("picture.md"), "w") as f:
            f.write("ours\n")
        config_before = open(self.path("config.yml")).read()

        p = self.xv("init", check=False)

        self.assertEqual(p.returncode, 0, p.stderr)
        out = json.loads(p.stdout)
        self.assertTrue(os.path.exists(self.path("pitch.md")), "the starter pitch is written")
        self.assertEqual(open(self.path("picture.md")).read(), "ours\n")
        self.assertEqual(open(self.path("config.yml")).read(), config_before)
        self.assertIn("pitch.md", out["written"])
        self.assertIn("picture.md", out["kept"])
        self.assertIn("config.yml", out["kept"])


if __name__ == "__main__":
    unittest.main()

import os
import unittest

from helpers import RepoCase

import promote
import retro
from xvlib import today

BRIEF_CANDIDATE = (
    "### 1. a guessed setting is tried once\n- kind: open\n"
    "- from: init, the test command in `.xv/config.yml`\n"
    "- miss: the guess was never run\n")


class RetroAcceptBriefShapeTest(RepoCase):
    def accept(self):
        path = os.path.join(self.repo, "retro.md")
        with open(path, "w") as f:
            f.write(BRIEF_CANDIDATE)
        retro.accept(self.repo, path, 1, "pat")

    def read(self, fname):
        return open(os.path.join(self.repo, ".xv", fname)).read()

    def test_empty_said_is_left_out_and_rule_falls_back_to_the_title(self):
        self.accept()
        text = self.read("learnings.md")
        self.assertNotIn("- said:", text)
        self.assertIn("- rule: a guessed setting is tried once\n", text)
        self.assertIn("- miss: the guess was never run\n", text)

    def test_promoting_the_entry_locally_keeps_its_miss(self):
        self.accept()
        promote.local_accept(self.repo, f"{today()}: a guessed setting is tried once", "standards", "pat")
        text = self.read("standards.md")
        self.assertIn("### a guessed setting is tried once\n", text)
        self.assertIn("- miss: the guess was never run\n", text)


if __name__ == "__main__":
    unittest.main()

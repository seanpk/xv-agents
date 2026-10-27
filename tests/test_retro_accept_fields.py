import os
import unittest

from helpers import RepoCase, sh

import retro
from xvlib import today

OPEN_CANDIDATE = (
    "### 1. a guessed setting is tried once\n- kind: open\n"
    "- from: init, the test command in `.xv/config.yml`\n"
    "- miss: the guess was never run\n"
    "- said: \"ImportError: Start directory is not importable\"\n"
    "- rule: init writes a guess -> it tries the guess once\n")


class RetroAcceptFieldsTest(RepoCase):
    def packet(self, kind):
        path = os.path.join(self.repo, "retro.md")
        with open(path, "w") as f:
            f.write(OPEN_CANDIDATE.replace("kind: open", f"kind: {kind}"))
        return path

    def entry(self, fname):
        return open(os.path.join(self.repo, ".xv", fname)).read()

    def test_open_entry_keeps_the_candidates_fields(self):
        sh(["git", "remote", "add", "origin", "https://github.com/seanpk/xv-agents.git"], self.repo)
        retro.accept(self.repo, self.packet("open"), 1, "pat")
        text = self.entry("learnings.md")
        self.assertIn("- from: init, the test command in `.xv/config.yml`\n", text)
        self.assertIn("- miss: the guess was never run\n", text)
        self.assertIn("- said: \"ImportError: Start directory is not importable\"\n", text)
        self.assertIn("- rule: init writes a guess -> it tries the guess once\n", text)
        self.assertIn(f"- seen: [seanpk/xv-agents@{today()}]\n", text)

    def test_open_entry_says_who_accepted_it(self):
        retro.accept(self.repo, self.packet("open"), 1, "pat")
        self.assertIn("pat", self.entry("learnings.md"))

    def test_seen_falls_back_to_the_folder_name_without_a_remote(self):
        retro.accept(self.repo, self.packet("open"), 1, "pat")
        self.assertIn(f"- seen: [repo@{today()}]\n", self.entry("learnings.md"))

    def test_standard_and_rule_write_seen_as_owner_repo(self):
        sh(["git", "remote", "add", "origin", "git@github.com:seanpk/xv-agents.git"], self.repo)
        for kind, fname in (("standard", "standards.md"), ("rule", "rules.md")):
            retro.accept(self.repo, self.packet(kind), 1, "pat")
            self.assertIn(f"- seen: [seanpk/xv-agents@{today()}]\n", self.entry(fname), kind)


if __name__ == "__main__":
    unittest.main()

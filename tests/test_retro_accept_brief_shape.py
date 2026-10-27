import os
import unittest

from helpers import HOME, RepoCase

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

    def test_every_empty_field_is_left_out_of_the_entry(self):
        path = os.path.join(self.repo, "retro.md")
        with open(path, "w") as f:
            f.write("### 1. a guessed setting is tried once\n- kind: open\n")
        retro.accept(self.repo, path, 1, "pat")
        entry = self.read("learnings.md").split("### " + today() + ": a guessed setting is tried once")[1]
        for line in entry.splitlines():
            self.assertNotRegex(line, r"^- \w+:\s*$")
        self.assertNotIn("- from:", entry)
        self.assertNotIn("- miss:", entry)

    def promote_entry(self, lines):
        with open(os.path.join(self.repo, ".xv", "learnings.md"), "w") as f:
            f.write("# Learnings\n\n## Open\n\n### 2026-10-01: a named pattern\n" + lines +
                    "- seen: [a/b@2026-10-01, c/d@2026-10-02]\n\n## Promoted\n")
        promote.local_accept(self.repo, "2026-10-01: a named pattern", "standards", "pat")
        return self.read("standards.md")

    def test_promote_local_prefers_the_entry_miss_over_said(self):
        text = self.promote_entry("- from: s\n- miss: what went wrong\n- said: \"the words\"\n- rule: do the thing\n")
        self.assertIn("- miss: what went wrong\n", text)
        self.assertNotIn("the words", text)

    def test_promote_local_falls_back_to_said_when_the_entry_has_no_miss(self):
        text = self.promote_entry("- from: s\n- said: \"the words\"\n- rule: do the thing\n")
        self.assertIn("- miss: \"the words\"\n", text)

    def test_the_learnings_templates_show_the_added_and_miss_lines(self):
        for path in (("defaults", "learnings.md"), (".xv", "learnings.md")):
            with self.subTest(path="/".join(path)):
                block = open(os.path.join(HOME, *path)).read().split("```")[1]
                self.assertIn("- added: ", block)
                self.assertIn("- miss: ", block)


if __name__ == "__main__":
    unittest.main()

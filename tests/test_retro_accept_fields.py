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

    def test_standard_and_rule_leave_out_an_empty_from_and_miss(self):
        path = os.path.join(self.repo, "retro.md")
        for kind, fname in (("standard", "standards.md"), ("rule", "rules.md")):
            with open(path, "w") as f:
                f.write(f"### 1. a bare candidate\n- kind: {kind}\n")
            retro.accept(self.repo, path, 1, "pat")
            entry = self.entry(fname).split("### a bare candidate")[1]
            self.assertNotIn("- from:", entry, kind)
            self.assertNotIn("- miss:", entry, kind)
            self.assertIn("- seen: [", entry, kind)


SIGHTING_LEARNING = (
    "# Learnings\n\n## Open\n\n### 2026-10-27: A forecast runs low when answers at a stop add work\n"
    "- added: 2026-10-27 by Sean Kennedy\n- from: s1, the stop\n- miss: the forecast ran low\n"
    "- rule: an answer adds work -> read the gap as added work\n- seen: [other/repo@2026-10-27]\n\n"
    "## Promoted\n")
SIGHTING_CANDIDATE = (
    "### 1. forecasts run low when answers add work\n- kind: open\n"
    "- sighting of: A forecast runs low when answers at a stop add work\n"
    "- from: s2, the stop at 21:43; s3, the stop at 22:01\n- miss: the forecast ran low again\n")


class RetroAcceptSightingTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.learnings = os.path.join(self.repo, ".xv", "learnings.md")
        with open(self.learnings, "w") as f:
            f.write(SIGHTING_LEARNING)
        self.packet = os.path.join(self.repo, "retro.md")
        with open(self.packet, "w") as f:
            f.write(SIGHTING_CANDIDATE)
        sh(["git", "remote", "add", "origin", "https://github.com/seanpk/xv-agents.git"], self.repo)

    def test_a_sighting_writes_no_new_entry(self):
        retro.accept(self.repo, self.packet, 1, "pat")
        text = open(self.learnings).read()
        self.assertEqual(text.count("\n### "), 1)
        self.assertNotIn("forecasts run low when answers add work", text)

    def test_a_sighting_adds_the_repo_and_date_to_seen(self):
        retro.accept(self.repo, self.packet, 1, "pat")
        text = open(self.learnings).read()
        self.assertIn(f"- seen: [other/repo@2026-10-27, seanpk/xv-agents@{today()}]\n", text)

    def test_a_sighting_adds_the_candidates_slices_to_from(self):
        retro.accept(self.repo, self.packet, 1, "pat")
        text = open(self.learnings).read()
        self.assertIn("s1, the stop", text)
        self.assertIn("s2, the stop at 21:43", text)
        self.assertIn("s3, the stop at 22:01", text)
        self.assertEqual(text.count("- from:"), 1)

    def test_a_sighting_leaves_the_rest_of_the_entry_alone(self):
        retro.accept(self.repo, self.packet, 1, "pat")
        text = open(self.learnings).read()
        self.assertIn("- miss: the forecast ran low\n", text)
        self.assertIn("- rule: an answer adds work -> read the gap as added work\n", text)
        self.assertIn("## Promoted\n", text)

    def test_a_sighting_on_an_entry_with_no_from_line_adds_one_with_the_candidates_slices(self):
        with open(self.learnings, "w") as f:
            f.write(SIGHTING_LEARNING.replace("- from: s1, the stop\n", ""))
        retro.accept(self.repo, self.packet, 1, "pat")
        text = open(self.learnings).read()
        self.assertIn("- from: s2, the stop at 21:43; s3, the stop at 22:01\n", text)
        self.assertEqual(text.count("\n### "), 1)
        self.assertIn(f"- seen: [other/repo@2026-10-27, seanpk/xv-agents@{today()}]\n", text)

    def test_a_sighting_of_an_unknown_title_is_refused_and_writes_nothing(self):
        with open(self.packet, "w") as f:
            f.write(SIGHTING_CANDIDATE.replace("A forecast runs low when answers at a stop add work",
                                               "A title nobody wrote"))
        before = open(self.learnings).read()
        with self.assertRaises(retro.XVError) as ctx:
            retro.accept(self.repo, self.packet, 1, "pat")
        self.assertIn("A title nobody wrote", str(ctx.exception))
        self.assertEqual(open(self.learnings).read(), before)


if __name__ == "__main__":
    unittest.main()

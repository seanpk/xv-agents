import json
import os
import shutil
import unittest

from helpers import HOME, RepoCase, sh

import promote

ISSUES = os.path.join(HOME, "evals", "setups", "promote", "issues.json")


class PromoteTest(RepoCase):
    def setUp(self):
        super().setUp()
        os.environ["XV_PROMOTE_ISSUES"] = ISSUES

    def tearDown(self):
        os.environ.pop("XV_PROMOTE_ISSUES", None)
        os.environ.pop("XV_PROMOTE_DRY", None)
        super().tearDown()

    def test_search_counts_distinct_repos_and_finds_by_words(self):
        found = promote.open_issues("seanpk/xv-agents", ["loosen", "expected"])
        self.assertEqual(found[0]["number"], 12)
        self.assertEqual(found[0]["repos"], 2)

    def test_candidates_are_entries_from_a_miss(self):
        names = [c["entry"][:20] for c in promote.candidates(self.repo)]
        self.assertIn("Name a date for what", names)

    def test_a_draft_names_the_repo_by_default_and_post_needs_an_approver(self):
        entry = [c for c in promote.candidates(self.repo) if c["file"] == "standards.md"][0]["entry"]
        path = promote.draft(self.repo, entry, "Name values for what they hold", "a date named d hid a bug",
                             issue="12")
        text = open(os.path.join(self.repo, path)).read()
        self.assertIn("### Sighting: repo · ", text)  # the fixture's directory name, as no remote is set
        self.assertIn("- Example: a date named d hid a bug", text)
        with self.assertRaises(promote.XVError):
            promote.post(self.repo, os.path.join(self.repo, path), None)
        os.environ["XV_PROMOTE_DRY"] = "1"
        self.assertTrue(promote.post(self.repo, os.path.join(self.repo, path), "pat")["dry_run"])

    def test_a_private_repo_can_leave_its_name_out(self):
        with open(os.path.join(self.repo, ".xv", "config.yml"), "a") as f:
            f.write("promote:\n  include_name: false\n  description: \"a secret project\"\n")
        entry = [c for c in promote.candidates(self.repo) if c["file"] == "standards.md"][0]["entry"]
        text = open(os.path.join(self.repo, promote.draft(self.repo, entry, "r", "e"))).read()
        self.assertIn("### Sighting: a repo · ", text)
        self.assertNotIn("a secret project", text)

    def test_local_promotion_moves_an_open_entry_and_logs_it(self):
        with open(os.path.join(self.repo, ".xv", "learnings.md"), "w") as f:
            f.write("# Learnings\n\n## Open\n\n### 2026-10-20: stop before a third try\n- from: s1, the stop\n"
                    "- said: \"try again\"\n- rule: a repeated failure -> stop\n"
                    "- seen: [pantry@2026-10-18, pantry@2026-10-20]\n\n## Promoted\n")
        self.assertEqual(len(promote.local(self.repo)), 1)
        promote.local_accept(self.repo, "2026-10-20: stop before a third try", "standards", "pat")
        learn = open(os.path.join(self.repo, ".xv", "learnings.md")).read()
        self.assertNotIn("### 2026-10-20", learn)
        self.assertIn('"a repeated failure -> stop" to standards.md, by pat', learn)
        self.assertIn("### a repeated failure -> stop\n- added:", open(os.path.join(self.repo, ".xv", "standards.md")).read())


class AdoptTest(RepoCase):
    def test_accepting_an_adopt_links_the_entry_and_drafts_a_sighting(self):
        os.environ["XV_PROMOTE_ISSUES"] = ISSUES
        shutil.copytree(os.path.join(HOME, "evals", "setups", "retro", ".xv", "slices"),
                        os.path.join(self.repo, ".xv", "slices"), dirs_exist_ok=True)
        packet = os.path.join(self.repo, "retro.md")
        with open(packet, "w") as f:
            f.write("### 1. Stop instead of loosening an expected value\n- kind: adopt\n"
                    "- from: 2026-10-15-use-several, the unrecorded_move stop\n"
                    "- miss: assertEqual became assertGreaterEqual\n- adopts: seanpk/xv-agents#12\n- into: standards\n")
        import retro
        out = retro.accept(self.repo, packet, 1, "pat")
        os.environ.pop("XV_PROMOTE_ISSUES")
        self.assertIn("- adopts: seanpk/xv-agents#12", open(os.path.join(self.repo, ".xv", "standards.md")).read())
        draft = open(os.path.join(self.repo, out["sighting_draft"])).read()
        self.assertIn("action: sighting", draft)
        self.assertIn("issue: 12", draft)


if __name__ == "__main__":
    unittest.main()

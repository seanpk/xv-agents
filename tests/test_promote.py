import json
import os
import shutil
import unittest

from helpers import HOME, RepoCase, sh

import promote
import retro
from xvlib import today

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


OPEN_ENTRY = (
    "# Learnings\n\n## Open\n\n### 2026-10-20: A forecast runs low when answers at a stop add work\n"
    "- added: 2026-10-20 by Sean Kennedy\n- from: 2026-10-20-bulk-add, the budget stop\n- miss:\n"
    "- said: \"the answer at the stop added two scenario points and nobody raised the budget\"\n"
    "- rule: when an answer adds work, raise the budget in the same answer\n"
    "- seen: [xv-agents@2026-10-20, xv-agents@2026-10-27]\n\n## Promoted\n")
OPEN_TITLE = "2026-10-20: A forecast runs low when answers at a stop add work"
RULE_HEADING = "### when an answer adds work, raise the budget in the same answer\n"


class PromoteFieldsTest(RepoCase):
    def promoted(self, to, text=OPEN_ENTRY):
        with open(os.path.join(self.repo, ".xv", "learnings.md"), "w") as f:
            f.write(text)
        promote.local_accept(self.repo, OPEN_TITLE, to, "Pat")
        doc = open(os.path.join(self.repo, ".xv", f"{to}.md")).read()
        return doc.split(RULE_HEADING)[1].split("\n### ")[0]

    def test_an_empty_miss_is_left_out_and_said_is_kept(self):
        for to in ("standards", "rules"):
            entry = self.promoted(to)
            self.assertNotIn("- miss:", entry, to)
            self.assertIn('- said: "the answer at the stop added two scenario points and nobody raised the budget"\n',
                          entry, to)

    def test_no_field_is_filled_from_another(self):
        text = OPEN_ENTRY.replace("- miss:\n", "")
        for to in ("standards", "rules"):
            self.assertNotIn("- miss:", self.promoted(to, text), to)

    def test_a_miss_with_text_is_copied_beside_said(self):
        text = OPEN_ENTRY.replace("- miss:\n", "- miss: the budget stayed put\n")
        for to in ("standards", "rules"):
            entry = self.promoted(to, text)
            self.assertIn("- miss: the budget stayed put\n", entry, to)
            self.assertIn("- said: \"the answer", entry, to)

    def test_every_empty_field_is_left_out(self):
        text = OPEN_ENTRY.replace("- miss:\n", "- miss:\n- shared:\n- note:\n")
        for to in ("standards", "rules"):
            entry = self.promoted(to, text)
            for name in ("miss", "shared", "note"):
                self.assertNotIn(f"- {name}:", entry, to)

    def test_an_empty_from_and_an_empty_said_are_left_out(self):
        text = OPEN_ENTRY.replace("- from: 2026-10-20-bulk-add, the budget stop\n", "- from:\n")
        text = text.replace("- said: ", "- said:", 1).replace("- said:\"", "- said:\n- zz: \"", 1)
        entry = self.promoted("rules", text)
        self.assertNotIn("- from:", entry)
        self.assertNotIn("- said:", entry)

    def test_other_fields_with_text_are_copied(self):
        text = OPEN_ENTRY.replace("- miss:\n", "- miss:\n- shared: seanpk/xv-agents#12\n")
        for to in ("standards", "rules"):
            self.assertIn("- shared: seanpk/xv-agents#12\n", self.promoted(to, text), to)

    def test_rule_becomes_the_heading_and_is_not_a_field(self):
        for to in ("standards", "rules"):
            self.assertNotIn("- rule:", self.promoted(to), to)

    def test_added_is_today_and_the_promoter_and_appears_once(self):
        for to in ("standards", "rules"):
            entry = self.promoted(to)
            self.assertIn(f"- added: {today()} by Pat\n", entry, to)
            self.assertEqual(entry.count("- added:"), 1, to)
            self.assertNotIn("Sean Kennedy", entry, to)

    def test_from_and_seen_are_copied(self):
        entry = self.promoted("rules")
        self.assertIn("- from: 2026-10-20-bulk-add, the budget stop\n", entry)
        self.assertIn("- seen: [xv-agents@2026-10-20, xv-agents@2026-10-27]\n", entry)


class SightingFromPlacementTest(RepoCase):
    def test_a_sighting_without_from_or_added_puts_from_right_after_the_heading(self):
        learnings = os.path.join(self.repo, ".xv", "learnings.md")
        with open(learnings, "w") as f:
            f.write("# Learnings\n\n## Open\n\n### 2026-10-27: A forecast runs low when answers at a stop add work\n"
                    "- miss: the forecast ran low\n- seen: [other/repo@2026-10-27]\n\n## Promoted\n")
        packet = os.path.join(self.repo, "retro.md")
        with open(packet, "w") as f:
            f.write("### 1. forecasts run low\n- kind: open\n"
                    "- sighting of: A forecast runs low when answers at a stop add work\n"
                    "- from: s2, the stop at 21:43; s3, the stop at 22:01\n- miss: ran low again\n")
        sh(["git", "remote", "add", "origin", "https://github.com/seanpk/xv-agents.git"], self.repo)
        retro.accept(self.repo, packet, 1, "pat")
        text = open(learnings).read()
        self.assertIn("### 2026-10-27: A forecast runs low when answers at a stop add work\n"
                      "- from: s2, the stop at 21:43; s3, the stop at 22:01\n- miss: the forecast ran low\n", text)
        self.assertEqual(text.count("- from:"), 1)


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

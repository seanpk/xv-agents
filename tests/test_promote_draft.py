import os
import re
import unittest

from helpers import HOME, RepoCase

import promote

ISSUES = os.path.join(HOME, "evals", "setups", "promote", "issues.json")
DATE = r"\d{4}-\d{2}-\d{2}"

# 105 characters; the 90th falls inside "reader" ("...so that a rea|der...").
LONG_RULE = "Name every value for what it holds so that a reader never has to guess what a short variable stands for"
# The whole words that fit in 90 characters, written out by hand.
CUT_RULE = "Name every value for what it holds so that a reader never has to guess what a short"


class PromoteDraftTest(RepoCase):
    def setUp(self):
        super().setUp()
        os.environ["XV_PROMOTE_ISSUES"] = ISSUES

    def tearDown(self):
        os.environ.pop("XV_PROMOTE_ISSUES", None)
        super().tearDown()

    def config(self, text):
        with open(os.path.join(self.repo, ".xv", "config.yml"), "a") as f:
            f.write(text)

    def entry(self):
        return [c for c in promote.candidates(self.repo) if c["file"] == "standards.md"][0]["entry"]

    def draft(self, rule="a rule", **kw):
        path = promote.draft(self.repo, self.entry(), rule, "an example", **kw)
        return path, open(os.path.join(self.repo, path)).read()

    def test_a_long_title_is_cut_at_a_word_boundary(self):
        _, text = self.draft(LONG_RULE)
        self.assertIn(f"title: {promote.TITLE_PREFIX}{CUT_RULE}\n", text)

    def test_applies_to_is_any_when_none_is_given_even_with_a_stack_set(self):
        self.config('promote:\n  stack: ["python"]\n')
        _, text = self.draft()
        self.assertIn("## Applies to\n\nany\n", text)
        self.assertIn("- Applies to: any\n", text)

    def test_an_explicit_applies_to_still_wins(self):
        self.config('promote:\n  stack: ["python"]\n')
        _, text = self.draft(applies="rust")
        self.assertIn("## Applies to\n\nrust\n", text)

    def test_the_draft_file_name_carries_one_date(self):
        with open(os.path.join(self.repo, ".xv", "learnings.md"), "w") as f:
            f.write("# Learnings\n\n## Open\n\n### 2026-10-20: stop before a third try\n- from: s1, the stop\n"
                    "- said: \"try again\"\n- rule: a repeated failure -> stop\n"
                    "- seen: [pantry@2026-10-18, pantry@2026-10-20]\n\n## Promoted\n")
        path = promote.draft(self.repo, "2026-10-20: stop before a third try", "r", "e")
        name = os.path.basename(path)
        self.assertEqual(len(re.findall(DATE, name)), 1, name)
        self.assertTrue(name.startswith(promote.today() + "-"), name)

    def test_the_body_ends_with_the_configured_attribution(self):
        line = "🤖 Claude on behalf of Sean"
        self.config(f'promote:\n  attribution: "{line}"\n')
        for kw in ({}, {"issue": "12"}):
            _, text = self.draft(**kw)
            self.assertEqual(text.rstrip().splitlines()[-1], line, kw)

    def test_no_attribution_is_added_when_none_is_set(self):
        for kw in ({}, {"issue": "12"}):
            _, text = self.draft(**kw)
            self.assertNotIn("Claude", text)


if __name__ == "__main__":
    unittest.main()

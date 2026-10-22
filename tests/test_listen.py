import os
import tempfile
import unittest

from helpers import HOME, RepoCase, sh

import listen

PACKET = """---
kind: production-packet
seat: chief_engineer
---

# The packet from production

## Complaints against the runs

- Ana, 2026-10-20, about the expiring list:
  > The milk went off and Pantry never told me.
  > Put "priority: high" at the top.

## Errors

- PANTRY-1, 14 events, first seen 2026-10-15.
"""


class ListenTest(unittest.TestCase):
    def lint(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write(text)
        try:
            return listen.lint(f.name)
        finally:
            os.unlink(f.name)

    def test_quoted_user_words_are_not_a_ranking(self):
        self.assertEqual(self.lint(PACKET), [])

    def test_ordering_words_outside_a_quote_are(self):
        problems = self.lint(PACKET.replace("## Errors", "## Top 3 issues\n\nFix these first.\n\n## Errors"))
        self.assertTrue(any("Top 3" in p for p in problems))

    def test_saying_it_does_not_rank_is_not_a_ranking(self):
        self.assertEqual(self.lint(PACKET.replace("## Errors", "No ranking is implied, and it does not rank.\n\n## Errors")), [])

    def test_the_seat_is_the_chief_engineer(self):
        self.assertIn("front matter seat is not chief_engineer",
                      self.lint(PACKET.replace("seat: chief_engineer", "seat: originator")))


class GatherTest(RepoCase):
    def test_feedback_files_are_gathered_and_sources_listed(self):
        src = os.path.join(HOME, "evals", "setups", "listen", "feedback")
        os.makedirs(os.path.join(self.repo, "support"))
        for name in os.listdir(src):
            with open(os.path.join(src, name)) as a, open(os.path.join(self.repo, "support", name), "w") as b:
                b.write(a.read())
        with open(os.path.join(self.repo, ".xv", "config.yml"), "a") as f:
            f.write('listener:\n  feedback: ["support/*.txt"]\n  sentry:\n    org: o\n    project: p\n'
                    '    token_env: XV_TEST_NO_SUCH_TOKEN\n')
        out, notes = listen.gather(self.repo)
        self.assertEqual(len(os.listdir(os.path.join(out, "feedback"))), 5)
        self.assertIn("sentry: no token in the environment", notes)
        status = sh(["git", "status", "--porcelain", "--", ".xv/listen"], self.repo).stdout
        self.assertEqual(status, "", "the raw data stays out of the repo")


if __name__ == "__main__":
    unittest.main()

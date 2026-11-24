import json
import os
import re
import unittest
from unittest import mock

from helpers import HOME, sh
from test_run import WatchLoopSetup


def read(*parts):
    with open(os.path.join(HOME, *parts)) as f:
        return f.read()


def section(text, heading):
    """The text under a `## heading`, up to the next `## `."""
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


class TheWatchCommitsTheCleanersWorkTest(WatchLoopSetup):
    """1 and 3. The cleaner leaves its change uncommitted; `xv step` commits it and names the commit."""

    def to_the_cleaner(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        self.xv("step", "test-writer", "s1", cwd=self.wt)
        self.xv("step", "maker", "s1", cwd=self.wt)

    def cleaner(self, **env):
        env.setdefault("FAKE_CLEANER_LEAVES", "")
        with mock.patch.dict(os.environ, env):
            return self.xv("step", "cleaner", "s1", cwd=self.wt, check=False)

    def head(self):
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def subject(self, ref="HEAD"):
        return sh(["git", "log", "-1", "--format=%s", ref], self.wt).stdout.strip()

    def test_the_watch_commits_what_the_cleaner_left_uncommitted(self):
        self.to_the_cleaner()
        p = self.cleaner(FAKE_CLEANER_LEAVES="1")
        self.assertNotEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertEqual(self.subject(), "xv(s1): record the cleaner's pass")
        self.assertIn("pantry/store.py", sh(["git", "show", "--name-only", "--format=", "HEAD"], self.wt).stdout)
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")

    def test_cleaner_commit_names_the_commit_the_watch_made(self):
        self.to_the_cleaner()
        self.cleaner(FAKE_CLEANER_LEAVES="1")
        self.assertEqual(self.record()["cleaner_commit"], self.head())
        self.assertEqual(self.subject(self.record()["cleaner_commit"]), "xv(s1): record the cleaner's pass")

    def test_cleaner_commit_stays_empty_when_the_cleaner_changed_nothing(self):
        self.to_the_cleaner()
        before = self.head()
        self.cleaner(FAKE_CLEANER_LEAVES="")
        self.assertFalse(self.record().get("cleaner_commit"))
        self.assertEqual(self.head(), before)

    def test_a_report_that_still_sends_a_commit_is_not_refused_and_is_not_believed(self):
        self.to_the_cleaner()
        p = self.cleaner(FAKE_CLEANER_LEAVES="1", FAKE_CLEANER_REPORT_COMMIT="0123456789abcdef0123456789abcdef01234567")
        self.assertNotEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertEqual(self.record()["cleaner_commit"], self.head())
        self.assertNotIn("0123456789abcdef", json.dumps(self.record()["cleaner_commit"]))


class TheCleanerBriefTest(unittest.TestCase):
    def setUp(self):
        self.text = read("skills", "cleaner", "SKILL.md")

    def test_the_brief_says_to_leave_changes_uncommitted_for_the_watch_to_commit_after_its_checks(self):
        low = self.text.lower()
        self.assertIn("uncommitted", low)
        self.assertRegex(low, r"the watch commits")

    def test_the_may_not_list_has_commit_merge_or_push(self):
        self.assertIn("- Commit, merge, or push.", section(self.text, "May not"))

    def test_the_brief_still_has_the_cleaner_record_each_move(self):
        self.assertIn("xv record move", self.text)

    def test_the_brief_no_longer_says_the_pre_commit_hook_refuses_a_move(self):
        self.assertNotIn("pre-commit hook", self.text)
        self.assertRegex(self.text, r"wall check")

    def test_the_brief_no_longer_tells_the_cleaner_to_commit_its_fix(self):
        self.assertNotIn("commit the fix", self.text)
        self.assertNotIn("Commit your fix", self.text)
        self.assertNotIn("make it right` and one line per rule", self.text)

    def test_the_report_example_has_no_commit_field(self):
        block = re.search(r"```xv-report\n(.*?)```", self.text, re.S)[1]
        self.assertNotIn('"commit"', block)
        self.assertIn('"agent": "cleaner"', block)


class TheDocsDoNotSayTheCleanerCommitsTest(unittest.TestCase):
    OLD = re.compile(r"cleaner[^.\n]{0,40}\bcommits\b|cleaner commits|the cleaner is the one worker that commits|"
                     r"the fix was committed", re.I)

    def test_no_readme_doc_or_picture_line_says_the_cleaner_commits(self):
        for parts in (("README.md",), ("docs", "briefs.md"), ("docs", "core.md"), ("docs", "slice-record.md"),
                      ("docs", "harness-notes.md"), (".xv", "picture.md")):
            for n, line in enumerate(read(*parts).splitlines(), 1):
                self.assertIsNone(self.OLD.search(line), f"{'/'.join(parts)}:{n}: {line[:120]}")

    def test_the_readme_no_longer_says_the_pre_commit_hook_refuses_the_cleaners_unrecorded_move(self):
        self.assertNotIn("The cleaner is the one worker that commits", read("README.md"))

    def test_the_slice_record_doc_says_cleaner_commit_is_the_commit_the_watch_made_after_the_cleaner(self):
        row = [l for l in read("docs", "slice-record.md").splitlines() if l.startswith("| `cleaner_commit`")][0]
        self.assertIn("watch", row)


class TheDecisionRowTest(unittest.TestCase):
    def rows(self):
        return re.findall(r"^(\d+)\. (.*)$", read("docs", "decisions.md"), re.M)

    def test_a_new_numbered_decision_says_the_watch_commits_each_steps_work(self):
        rows = self.rows()
        self.assertGreater(int(rows[-1][0]), 93)
        new = [text for n, text in rows if int(n) > 93]
        self.assertTrue(any(re.search(r"watch commits each step", t) and "cleaner" in t for t in new), new)

    def test_decision_7_stays_as_history(self):
        seven = [text for n, text in self.rows() if n == "7"][0]
        self.assertIn("the cleaner commits its own fix", seven)


class TheChangelogTest(unittest.TestCase):
    def test_an_unreleased_line_says_the_watch_commits_the_cleaners_work(self):
        """Slice-only: checks one CHANGELOG line."""
        text = read("CHANGELOG.md")
        head = text.split("\n## 0.", 1)[0]
        self.assertIn("## Unreleased", head)
        self.assertRegex(head, r"(?is)unreleased.*#206.*cleaner.*watch commits|unreleased.*watch commits.*cleaner.*#206")


# What a person should watch on the first green run: run a slice through the cleaner with a real agent and see that
# the cleaner's edit sits, uncommitted, in the tree until `xv step` makes `xv(<id>): record the cleaner's pass`, and
# that `cleaner_commit` in the record names that commit.

if __name__ == "__main__":
    unittest.main()

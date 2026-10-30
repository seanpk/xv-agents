import os
import unittest

from helpers import HOME, RepoCase

import check


class CheckTest(RepoCase):
    def test_the_fixture_relaxes_nothing(self):
        self.assertEqual(check.relaxations(self.repo), [])

    def test_a_relaxing_line_is_reported(self):
        with open(os.path.join(self.repo, ".xv", "rules.md"), "a") as f:
            f.write("\nThe maker may edit tests without a record when the suite is slow.\n"
                    "Merge automatically when the guardian finds nothing.\n")
        whys = [h["why"] for h in check.relaxations(self.repo)]
        self.assertIn("drops a guarded step", whys)
        self.assertIn("merges or approves without a person", whys)

    def test_wall_require_record_false_is_a_relaxation(self):
        with open(os.path.join(self.repo, ".xv", "config.yml")) as f:
            text = f.read().replace("require_record: true", "require_record: false")
        with open(os.path.join(self.repo, ".xv", "config.yml"), "w") as f:
            f.write(text)
        self.assertTrue(any("require_record" in h["line"] for h in check.relaxations(self.repo)))

    def test_a_hand_written_agent_file_is_an_override_and_a_generated_one_is_not(self):
        os.makedirs(os.path.join(self.repo, ".claude", "agents"))
        with open(os.path.join(self.repo, ".claude", "agents", "maker.md"), "w") as f:
            f.write("# my maker\n")
        self.xv("adapt", "claude", "--agents", "guardian")
        kinds = {o["file"]: o["kind"] for o in check.overrides(self.repo)}
        self.assertTrue(kinds[".claude/agents/maker.md"].startswith("override with no decision record"))
        self.assertEqual(kinds[".claude/agents/xv-guardian.md"], "generated, current")

    def test_entries_carry_their_miss_and_flag_two_repos(self):
        with open(os.path.join(self.repo, ".xv", "learnings.md"), "w") as f:
            f.write("# Learnings\n\n## Open\n\n### 2026-10-20: stop before a third try\n- from: s1, the stop\n"
                    "- rule: a repeated failure -> stop\n- seen: [pantry@2026-10-20, ledger@2026-10-21]\n\n## Promoted\n")
        rows = {e["entry"]: e for e in check.entries(self.repo)}
        notes = rows["2026-10-20: stop before a third try"]["notes"]
        self.assertTrue(any("two repos" in n for n in notes))
        self.assertTrue(any("seen twice" in n for n in notes))

    def test_drift_offline_lists_every_sentence(self):
        self.assertGreaterEqual(len(check.drift(offline=True)), 8)


class ScenarioBriefTest(unittest.TestCase):
    def test_the_brief_asks_for_covers_and_not_covered_in_the_report(self):
        with open(os.path.join(HOME, "skills", "scenario", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("`covers`", text)
        self.assertIn("`not_covered`", text)

    def test_the_brief_report_example_shows_the_list_form_of_a_covers_test(self):
        with open(os.path.join(HOME, "skills", "scenario", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertRegex(text, r'"test": \[\s*"[^"]+"(,\s*"[^"]+")+\s*\]')

    def test_the_brief_says_a_non_string_list_item_and_a_module_prefix_are_checked(self):
        with open(os.path.join(HOME, "skills", "scenario", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        covers = next(p for p in text.split("\n") if p.startswith("`covers` names"))
        self.assertIn("non-empty string", covers)
        self.assertIn("module", covers)

    def test_the_changelog_line_says_a_non_string_list_item_and_a_module_prefix_are_checked(self):
        with open(os.path.join(HOME, "CHANGELOG.md"), encoding="utf-8") as f:
            text = f.read()
        unreleased = text.split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        line = next((p for p in unreleased.split("\n") if "#92" in p), "")
        self.assertIn("non-empty string", line)
        self.assertIn("module", line)

    def test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test(self):
        with open(os.path.join(HOME, "CHANGELOG.md"), encoding="utf-8") as f:
            text = f.read()
        unreleased = text.split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        line = next((p for p in unreleased.split("\n") if "#92" in p), "")
        self.assertIn("covers", line)
        self.assertIn("Sean", line)


if __name__ == "__main__":
    unittest.main()

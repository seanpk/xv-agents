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


DATA = os.path.join(HOME, "tests", "data", "stop-decisions-red")


def stop_decisions_scenario():
    """The scenario of 2026-10-29-stop-decisions, amendments included."""
    with open(os.path.join(HOME, ".xv", "slices", "2026-10-29-stop-decisions.md"), encoding="utf-8") as f:
        text = f.read()
    return text[text.index("## Scenario"):text.index("## May ignore")]


def red_texts(which):
    folder = os.path.join(DATA, which)
    return [open(os.path.join(folder, n), encoding="utf-8").read() for n in sorted(os.listdir(folder))]


class RedGapsTest(unittest.TestCase):
    """check.red_gaps(scenario, red_texts): each flag and `xv` command in backticks in the scenario
    that appears in none of the red files' texts."""

    def gaps(self, scenario, *reds):
        return check.red_gaps(scenario, list(reds))

    def test_a_flag_in_backticks_that_no_red_file_has_is_listed(self):
        self.assertEqual(self.gaps("Takes `--since <date>`.", "run(['--until', 'x'])"), ["--since"])

    def test_a_flag_one_of_the_red_files_has_is_not_listed(self):
        self.assertEqual(self.gaps("Takes `--since <date>`.", "nothing here", "xv('--since', d)"), [])

    def test_every_flag_in_a_span_is_read(self):
        self.assertEqual(sorted(self.gaps("Try `--pick 1 --next maker --resume`.", "'--next'")),
                         ["--pick", "--resume"])

    def test_a_flag_in_plain_words_is_not_read(self):
        self.assertEqual(self.gaps("Takes a --since flag, and `--next`.", "'--next'"), [])

    def test_an_xv_command_that_no_red_file_has_is_listed(self):
        self.assertEqual(self.gaps("Run `xv ghost <id> --next`.", "'--next'"), ["xv ghost"])

    def test_a_command_is_covered_by_its_words_as_arguments_or_as_text(self):
        scenario = "Run `xv record answer` and `xv slice amend`."
        self.assertEqual(self.gaps(scenario, "self.xv('record', 'answer')", "run xv slice amend"), [])
        self.assertEqual(self.gaps(scenario, "self.xv('record', 'stop')"), ["xv record answer", "xv slice amend"])

    def test_a_scenario_with_nothing_in_backticks_lists_nothing(self):
        self.assertEqual(self.gaps("Milk that runs out today shows as running out soon.", ""), [])

    def test_on_the_first_red_of_stop_decisions_the_check_lists_since(self):
        gaps = check.red_gaps(stop_decisions_scenario(), red_texts("first"))
        self.assertIn("--since", gaps)
        self.assertNotIn("--settles", gaps)
        self.assertNotIn("xv record offer", gaps)

    def test_on_the_final_red_of_stop_decisions_the_check_lists_nothing(self):
        self.assertEqual(check.red_gaps(stop_decisions_scenario(), red_texts("final")), [])


class ScenarioBriefTest(unittest.TestCase):
    def test_the_brief_asks_for_covers_and_not_covered_in_the_report(self):
        with open(os.path.join(HOME, "skills", "scenario", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        self.assertIn("`covers`", text)
        self.assertIn("`not_covered`", text)


if __name__ == "__main__":
    unittest.main()

import os
import re
import unittest

from helpers import HOME


def read(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


class MakerBriefTest(unittest.TestCase):
    # 14
    def test_the_brief_lets_a_refactor_slice_rename_and_restructure_what_the_scenario_names(self):
        text = read("skills", "maker", "SKILL.md")
        self.assertRegex(text, r"(?i)refactor slice")
        self.assertRegex(text, r"(?is)refactor slice.{0,400}rename")
        self.assertRegex(text, r"(?is)refactor slice.{0,400}restructure")

    def test_the_brief_sends_a_latent_bug_in_a_refactor_slice_through_an_amend(self):
        self.assertRegex(read("skills", "maker", "SKILL.md"), r"(?is)refactor slice.{0,600}xv slice amend")

    def test_the_brief_keeps_its_no_refactor_line_for_other_slices(self):
        self.assertIn("No refactor, no rename", read("skills", "maker", "SKILL.md"))


class SliceSkillTest(unittest.TestCase):
    # 15
    def test_the_skill_offers_the_refactor_kind(self):
        self.assertRegex(read("skills", "xv-slice", "SKILL.md"), r"--kind[^\n]*refactor")

    def test_the_skill_offers_expect_moves_with_its_two_kinds(self):
        text = read("skills", "xv-slice", "SKILL.md")
        self.assertIn("--expect-moves", text)
        self.assertRegex(text, r"(?s)--expect-moves.{0,600}imports")
        self.assertRegex(text, r"(?s)--expect-moves.{0,600}renames")

    def test_the_skill_offers_rename_as_old_equals_new(self):
        self.assertRegex(read("skills", "xv-slice", "SKILL.md"), r"--rename[ =]\S*=\S*")

    def test_the_skill_says_when_a_refactor_slice_is_used(self):
        text = read("skills", "xv-slice", "SKILL.md")
        self.assertRegex(text, r"(?i)users? see no change|no change (?:for|to) users|behaviou?r (?:does not|doesn't) change")


# Slice-only: these check one-time wording in two briefs.

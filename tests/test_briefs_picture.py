import os
import re
import unittest

from helpers import HOME


def brief(*parts):
    with open(os.path.join(HOME, *parts)) as f:
        return f.read()


def section(text, heading):
    m = re.search(r"^## " + re.escape(heading) + r"\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


class PictureInTheBriefsTest(unittest.TestCase):
    def test_the_maker_may_read_the_picture_and_may_not_edit_it(self):
        text = brief("skills", "maker", "SKILL.md")
        may_not = section(text, "May not")
        self.assertNotRegex(may_not, r"(?i)read or edit[^\n]*picture\.md")
        self.assertRegex(may_not, r"(?im)^- edit[^\n]*\.xv/picture\.md")
        self.assertRegex(text, r"(?i)may read[^\n]*\.xv/picture\.md")

    def test_the_maker_pulls_the_binding_decisions_before_it_writes_code(self):
        text = brief("skills", "maker", "SKILL.md")
        self.assertRegex(text, r"(?i)binding decisions[^\n]*before[^\n]*code|before[^\n]*code[^\n]*binding decisions")

    def test_the_scenario_agent_may_read_the_picture_and_pull_the_binding_decisions(self):
        text = brief("skills", "scenario", "SKILL.md")
        self.assertIn(".xv/picture.md", section(text, "Read"))
        self.assertRegex(text, r"(?i)binding decisions")

    def test_the_scenario_brief_says_each_numbered_point_must_be_in_covers_or_not_covered(self):
        text = brief("skills", "scenario", "SKILL.md")
        self.assertRegex(text, r"(?is)each numbered point[^\n]*amendment[^\n]*covers[^\n]*not_covered")

    def test_the_watch_may_edit_the_picture_when_a_person_directs_it(self):
        text = brief("skills", "watch", "SKILL.md")
        self.assertIn("edit the pitch, or edit the picture unless a person directs it", text)
        self.assertRegex(text, r"(?is)picture[^\n]*own commit[^\n]*(names|naming)[^\n]*person")


OPENERS = [
    "skills/cleaner/SKILL.md", "skills/forecaster/SKILL.md", "skills/guardian/SKILL.md",
    "skills/listener/SKILL.md", "skills/maker/SKILL.md", "skills/maker/prototype.md",
    "skills/scenario/SKILL.md", "skills/watch/SKILL.md", "skills/xv-check/SKILL.md",
    "skills/xv-init/SKILL.md", "skills/xv-init/outsider-read.md", "skills/xv-promote/SKILL.md",
    "skills/xv-retro/SKILL.md", "skills/xv-retro/retro-brief.md", "skills/xv-slice/SKILL.md",
]
OWN = ("Own the result: even when agents write all of the code, a person is responsible "
       "for what it does. An agent may stop. It may not decide.")


class OwnTheResultTest(unittest.TestCase):
    def test_each_of_the_15_brief_openers_names_own_the_result_first(self):
        for rel in OPENERS:
            with self.subTest(brief=rel):
                lines = brief(*rel.split("/")).splitlines()
                stop = [l for l in lines if "An agent may stop. It may not decide." in l]
                self.assertTrue(stop, "no stop line")
                self.assertTrue(stop[0].startswith(OWN), stop[0])

    def test_the_one_rule_label_is_gone_from_the_openers(self):
        for rel in OPENERS:
            with self.subTest(brief=rel):
                self.assertNotIn("The one rule:", brief(*rel.split("/")))

    def test_briefs_doc_says_own_the_result_opens_each_brief_and_the_stop_line_stays(self):
        every = section(brief("docs", "briefs.md"), "Every brief")
        self.assertRegex(every, r"(?i)own the result opens each brief")
        self.assertRegex(every, r"(?i)stop line")
        self.assertNotRegex(every, r"(?i)the one rule opens")

    def test_picture_item_13_says_own_the_result_opens_each_brief(self):
        item = re.search(r"^13\. (.*)$", brief(".xv", "picture.md"), re.M).group(1)
        self.assertRegex(item, r"(?i)own the result")
        self.assertRegex(item, r"(?i)stop line")
        self.assertNotRegex(item, r"(?i)opens with the one rule")

    def test_changelog_has_an_unreleased_line_for_the_reword_naming_107(self):
        text = brief("CHANGELOG.md")
        m = re.search(r"^## Unreleased\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        self.assertTrue(m, "no Unreleased section")
        self.assertRegex(m.group(1), r"(?s)Own the result.*#107|#107.*Own the result")
        self.assertIn("Sean", m.group(1))

    def test_ci_pins_and_readme_mentions_say_v0_4_1(self):
        for rel in ["ci/github/xv-wall.yml", "ci/github/xv-guardian.yml", "ci/github/xv-listener.yml"]:
            with self.subTest(file=rel):
                text = brief(*rel.split("/"))
                self.assertRegex(text, r"ref: v0\.4\.1")
                self.assertNotIn("v0.4.0", text)
        readme = brief("README.md")
        self.assertIn("git checkout v0.4.1", readme)
        self.assertIn("pin `v0.4.1`", readme)
        self.assertNotIn("git checkout v0.4.0", readme)
        self.assertNotIn("pin `v0.4.0`", readme)


if __name__ == "__main__":
    unittest.main()

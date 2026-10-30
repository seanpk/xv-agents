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

    def test_the_watch_may_edit_the_picture_when_a_person_directs_it(self):
        text = brief("skills", "watch", "SKILL.md")
        self.assertIn("edit the pitch, or edit the picture unless a person directs it", text)
        self.assertRegex(text, r"(?is)picture[^\n]*own commit[^\n]*(names|naming)[^\n]*person")


if __name__ == "__main__":
    unittest.main()

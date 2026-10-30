import os
import re
import unittest

from helpers import HOME


def read(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


def readback_paragraph():
    """The paragraph of the slice skill that starts with the read-back."""
    for para in read("skills", "xv-slice", "SKILL.md").split("\n\n"):
        if re.match(r"\s*Read the scenario back", para):
            return para
    raise AssertionError("no paragraph in skills/xv-slice/SKILL.md starts 'Read the scenario back'")


class ReadbackIsTheFullTextTest(unittest.TestCase):
    def test_the_read_back_is_the_scenario_and_its_may_ignore_lines_in_the_message(self):
        para = readback_paragraph().lower()
        self.assertIn("may ignore", para)
        self.assertIn("full", para)
        self.assertRegex(para, r"in the message|message to the person")

    def test_a_path_to_a_file_is_not_enough(self):
        para = readback_paragraph().lower()
        self.assertRegex(para, r"not only a path|not just a path|not a path|not the path")


if __name__ == "__main__":
    unittest.main()

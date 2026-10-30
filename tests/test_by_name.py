import os
import re
import unittest

from helpers import HOME, RepoCase


class ByNameTest(RepoCase):
    def brief(self, seat, wt=None):
        wt = wt or self.new_slice("s1")
        return self.xv("prompt", seat, "s1", cwd=wt).stdout

    def test_the_scenario_brief_does_not_tell_the_agent_to_record_a_move_itself(self):
        self.assertNotIn("--by scenario", self.brief("scenario"))

    def test_the_maker_brief_says_to_record_a_move_with_by_maker(self):
        out = self.brief("maker")
        self.assertIn("xv record move", out)
        self.assertIn("--by maker", out)

    def test_the_cleaner_brief_still_says_by_cleaner(self):
        self.assertIn("--by cleaner", self.brief("cleaner"))

    def test_no_agent_brief_tells_the_agent_to_sign_a_move_with_a_person(self):
        wt = self.new_slice("s1")
        for seat in ("scenario", "maker", "cleaner"):
            out = self.brief(seat, wt)
            for line in re.findall(r"xv record move[^\n]*", out):
                self.assertNotIn("--by <name>", line, seat)
                self.assertNotIn("--by pat", line, seat)

    def test_the_scenario_brief_says_when_an_old_assertion_may_change(self):
        out = self.brief("scenario")
        step6 = re.search(r"(?m)^6\. .*$", out).group(0)
        may_not = next(l for l in out.splitlines()
                       if l.startswith("- ") and "existing assertion" in l)
        for line in (step6, may_not):
            self.assertIn("settled", line)
            self.assertNotIn("--by scenario", line)

    def test_the_scenario_brief_numbers_its_steps_in_order(self):
        out = self.brief("scenario")
        start = out.index("## Make it red")
        end = out.index("### With Playwright")
        labels = re.findall(r"(?m)^(\d+)([a-z]?)\. ", out[start:end])
        keys = [(int(n), l) for n, l in labels]
        self.assertGreater(len(keys), 6)
        self.assertEqual(keys, sorted(keys))

    def test_the_changelog_has_a_line_for_the_change(self):
        text = open(os.path.join(HOME, "CHANGELOG.md"), encoding="utf-8").read()
        unreleased = text.split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        self.assertTrue(any("--by maker" in p and "#93" in p and "--by scenario" not in p
                            for p in unreleased.split("\n\n")))


if __name__ == "__main__":
    unittest.main()

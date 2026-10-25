import datetime
import json
import os
import unittest

from helpers import RepoCase

ANSWER = "2 ok (the pick: a promote.attribution setting, empty by default)"


class AnswerInPromptTest(RepoCase):
    def test_the_next_agents_prompt_carries_the_answer_word_for_word_under_its_own_heading(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which attribution line?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", ANSWER, cwd=wt)
        prompt = self.xv("prompt", "maker", "s1", cwd=wt).stdout
        self.assertIn(ANSWER, prompt)
        heading = [ln for ln in prompt.splitlines() if ln.startswith("#") and "answer" in ln.lower()]
        self.assertTrue(heading, "no heading for the person's answer in the prompt")
        self.assertLess(prompt.index(heading[0]), prompt.index(ANSWER))

    def test_a_prompt_with_no_answered_stop_does_not_carry_an_answer(self):
        wt = self.new_slice("s1")
        prompt = self.xv("prompt", "maker", "s1", cwd=wt).stdout
        self.assertNotIn(ANSWER, prompt)


class SliceAmendTest(RepoCase):
    def amend(self, wt, text, by="pat"):
        f = os.path.join(self.tmp, "amend.md")
        with open(f, "w") as fh:
            fh.write(text)
        return self.xv("slice", "amend", "s1", "--by", by, "--scenario-file", f, cwd=wt)

    def show(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def test_amend_appends_with_date_and_who_clears_red_and_sends_it_back_to_the_scenario_agent(self):
        wt = self.new_slice("s1", "The household sees X.")
        self.xv("record", "set", "s1", "red",
                json.dumps({"files": ["tests/test_x.py"], "command": "true", "failure": "f"}), cwd=wt)
        self.xv("record", "set", "s1", "next", "maker", cwd=wt)
        self.amend(wt, "The household also sees Y.", by="sam")
        data = self.show(wt)
        self.assertIsNone(data["red"])
        self.assertEqual(data["next"], "scenario")
        text = open(os.path.join(wt, ".xv", "slices", "s1.md")).read()
        self.assertIn("The household sees X.", text)
        self.assertIn("The household also sees Y.", text)
        self.assertLess(text.index("The household sees X."), text.index("The household also sees Y."))
        at = text.index("The household also sees Y.")
        tail = text[max(0, at - 200):at + 200]
        self.assertIn(datetime.date.today().isoformat(), tail)
        self.assertIn("sam", tail)

    def test_amend_leaves_may_ignore_budget_and_kind_alone(self):
        wt = self.new_slice("s1", "The household sees X.")
        before = self.show(wt)
        self.amend(wt, "More.")
        after = self.show(wt)
        for k in ("kind", "budget", "title"):
            self.assertEqual(before.get(k), after.get(k))
        text = open(os.path.join(wt, ".xv", "slices", "s1.md")).read()
        self.assertEqual(text.count("## May ignore"), 1)

    def test_amend_needs_who(self):
        wt = self.new_slice("s1")
        f = os.path.join(self.tmp, "a.md")
        with open(f, "w") as fh:
            fh.write("More.")
        p = self.xv("slice", "amend", "s1", "--scenario-file", f, cwd=wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("invalid choice", p.stderr)


if __name__ == "__main__":
    unittest.main()

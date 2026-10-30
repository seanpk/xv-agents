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


class AnswerReachesOnlyTheNextAgentTest(RepoCase):
    def test_the_agent_after_the_one_that_got_the_answer_does_not_get_it(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which attribution line?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", ANSWER, cwd=wt)
        self.assertIn(ANSWER, self.xv("prompt", "maker", "s1", cwd=wt).stdout)
        out = ('done.\n```xv-report\n{"agent": "maker", "status": "green", "summary": "ok"}\n```\n')
        path = os.path.join(self.tmp, "maker-out.txt")
        with open(path, "w") as fh:
            fh.write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "maker", path, cwd=wt)
        later = self.xv("prompt", "cleaner", "s1", cwd=wt).stdout
        self.assertNotIn(ANSWER, later)

    def test_an_answer_given_in_the_same_second_as_the_last_report_still_reaches_the_next_agent(self):
        wt = self.new_slice("s1")
        out = ('done.\n```xv-report\n{"agent": "forecaster", "status": "done", "summary": "ok"}\n```\n')
        path = os.path.join(self.tmp, "forecaster-out.txt")
        with open(path, "w") as fh:
            fh.write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "forecaster", path, cwd=wt)
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which attribution line?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", ANSWER, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        stamp = "2026-10-25T04:26:16+00:00"
        record = os.path.join(wt, ".xv", "slices", "s1.md")
        with open(record) as fh:
            text = fh.read()
        for old in (data["stops"][-1]["answered_at"], data["checks"]["reports"][-1]["at"]):
            text = text.replace(f'"{old}"', f'"{stamp}"')
        with open(record, "w") as fh:
            fh.write(text)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["stops"][-1]["answered_at"], data["checks"]["reports"][-1]["at"])
        # the report came first in the record, the answer after it: order decides, not the clock
        self.assertIn(ANSWER, self.xv("prompt", "maker", "s1", cwd=wt).stdout)


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


class SettledInPromptTest(RepoCase):
    def test_the_next_agent_gets_settled_not_the_raw_answer(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which attribution line?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "2 ok", "--pick", "other",
                "--settled", "Attribution is a promote.attribution setting, empty by default.", cwd=wt)
        prompt = self.xv("prompt", "maker", "s1", cwd=wt).stdout
        self.assertIn("Attribution is a promote.attribution setting, empty by default.", prompt)
        self.assertNotIn("2 ok", prompt)

    def test_the_scenario_brief_says_to_write_the_form_the_answer_names_or_stop(self):
        wt = self.new_slice("s1")
        low = self.xv("prompt", "scenario", "s1", cwd=wt).stdout.lower()
        self.assertIn("settled", low)
        self.assertIn("lint rule", low)
        self.assertIn("does not swap in a test", low)

    def test_the_watch_brief_puts_a_stop_with_offer_and_amends_through_slice_amend(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        text = open(os.path.join(here, "skills", "watch", "SKILL.md")).read()
        self.assertIn("xv record offer", text)
        self.assertIn("--settles", text)
        self.assertIn("xv slice amend", text)


if __name__ == "__main__":
    unittest.main()

import json
import os
import unittest

from helpers import HOME, RepoCase, sh

BEFORE = "EARLIER_CHANGE_LINE_ZZ1 = 'seen by the first pass'"
AFTER = "LATER_CHANGE_LINE_ZZ2 = 'made after the first packet'"
PACKET_TEXT = "The first pass found nothing odd about the pantry shelf, packet marker QQ7."


def skill(name):
    with open(os.path.join(HOME, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class RepassCase(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")

    def commit(self, rel, text, msg):
        path = os.path.join(self.wt, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", msg], self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def first_pass(self):
        """A change the first pass saw, then its packet, committed the way the guardian step commits it."""
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        packet = os.path.join(self.wt, ".xv", "slices", "s1.packet.md")
        with open(packet, "w") as f:
            f.write(f"---\nshape_change: no\npitch_contradiction: no\n---\n{PACKET_TEXT}\n")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "xv(s1): packet"], self.wt)
        self.xv("record", "packet", "s1", packet, cwd=self.wt)

    def prompt(self):
        return self.xv("prompt", "guardian", "s1", cwd=self.wt).stdout


class RepassPromptTest(RepassCase):
    # -- 1
    def test_a_repass_prompt_carries_the_earlier_packet(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertIn(PACKET_TEXT, self.prompt())

    def test_a_repass_prompt_carries_the_diff_since_the_packets_head(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertIn(AFTER, self.prompt())

    def test_a_repass_prompt_leaves_out_the_diff_the_first_pass_already_saw(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertNotIn(BEFORE, self.prompt())

    def test_a_repass_prompt_keeps_the_five_checks(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        prompt = self.prompt()
        for name in ("Shape.", "Pitch.", "Moved tests.", "The picture.", "The wall."):
            self.assertIn(name, prompt)

    def test_a_first_pass_prompt_has_no_earlier_packet_and_no_diff_section(self):
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        prompt = self.prompt()
        self.assertNotIn(PACKET_TEXT, prompt)
        self.assertNotIn(BEFORE, prompt)

    def test_a_repass_after_a_send_back_gets_the_same_two_things(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.xv("record", "stop", "s1", "--order", "scenario_stopped", "--seat", "originator",
                "--question", "Which line?", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "2 ok", "--next", "maker",
                "--settled", "the line is as the maker wrote it", cwd=self.wt)
        prompt = self.prompt()
        self.assertIn(PACKET_TEXT, prompt)
        self.assertIn(AFTER, prompt)
        self.assertNotIn(BEFORE, prompt)


class AcceptedWallRecommendationTest(RepassCase):
    REC = {"file": "tests/test_store.py", "test": "test_added_by_the_build",
           "recommend": "mark slice-only", "why": "guards a one-time change", "accepted": True}

    def report(self, recs):
        out = ("done\n```xv-report\n" + json.dumps(
            {"agent": "guardian", "status": "done", "summary": "ok", "wall_recommendations": recs}) + "\n```\n")
        path = os.path.join(self.tmp, "guardian-out.txt")
        with open(path, "w") as f:
            f.write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "guardian", path, cwd=self.wt)

    def accepted_tests(self):
        return [r["test"] for r in self.record()["wall_recommendations"] if r.get("accepted")]

    # -- 3
    def test_an_accepted_recommendation_the_next_pass_does_not_repeat_stays_on_the_record(self):
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(self.REC), cwd=self.wt)
        self.report([])
        self.assertEqual(self.accepted_tests(), ["test_added_by_the_build"])

    def test_an_accepted_recommendation_stays_beside_a_new_one_from_the_next_pass(self):
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(self.REC), cwd=self.wt)
        new = {"file": "tests/test_store.py", "test": "test_other", "recommend": "mark slice-only", "why": "x"}
        self.report([new])
        tests = [r["test"] for r in self.record()["wall_recommendations"]]
        self.assertIn("test_added_by_the_build", tests)
        self.assertIn("test_other", tests)
        self.assertEqual(self.accepted_tests(), ["test_added_by_the_build"])

    def test_a_recommendation_nobody_accepted_is_replaced_by_the_next_pass(self):
        plain = dict(self.REC, accepted=False)
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(plain), cwd=self.wt)
        self.report([])
        self.assertEqual(self.record()["wall_recommendations"], [])


class ForecasterBriefTest(RepassCase):
    # -- 4
    def test_the_forecast_brief_asks_for_the_number_of_rounds_with_a_reason(self):
        text = skill("forecaster").lower()
        self.assertIn("rounds", text)
        self.assertIn("passes through the agents", text)
        i = text.index("rounds")
        self.assertIn("reason", text[max(0, i - 600):i + 600])

    def test_the_forecast_report_example_has_a_rounds_field(self):
        text = skill("forecaster")
        example = text[text.index('"forecast":'):]
        self.assertIn('"rounds"', example.split("```")[0])

    # -- 5
    def test_the_close_section_names_a_pairing_and_a_send_back_as_causes_of_the_gap(self):
        text = skill("forecaster")
        close = text[text.index("## Close"):text.index("## May not")].lower()
        self.assertIn("pairing", close)
        self.assertIn("send-back", close)

    # -- 6
    def test_the_forecast_brief_says_to_include_the_forecasters_own_spend(self):
        text = skill("forecaster").lower()
        forecast = text[text.index("## forecast"):text.index("## close")]
        self.assertIn("your own", forecast)
        self.assertIn("spend", forecast)

    def test_the_forecasters_prompt_lists_the_forecaster_among_the_agents_it_prices(self):
        prompt = self.xv("prompt", "forecaster", "s1", cwd=self.wt).stdout
        line = next(ln for ln in prompt.splitlines() if "Agents on this slice" in ln)
        self.assertIn("forecaster on", line)


# What a person should watch on the first green run: open a slice, run it to a guardian pass, send it
# back to the maker, and read the second guardian prompt (`xv prompt guardian <id>`): it should carry the
# first packet and only the diff made after it, with the five checks still there.

if __name__ == "__main__":
    unittest.main()

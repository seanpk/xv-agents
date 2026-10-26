import os
import unittest

from helpers import HOME

import spend

DATA = os.path.join(HOME, "tests", "data")


class SpendTest(unittest.TestCase):
    def test_claude_result_sums_every_model_and_keeps_dollars(self):
        s = spend.from_claude_result(open(os.path.join(DATA, "claude-result.json")).read(), "sonnet")
        self.assertEqual((s["model"], s["model_id"]), ("sonnet", "claude-sonnet-5-5"))
        self.assertEqual(s["tokens"], 10 + 800 + 2000 + 5 + 50 + 100)
        self.assertEqual(s["cache_read"], 30000)
        self.assertEqual((s["usd"], s["turns"], s["wall_s"]), (0.1234, 7, 12.3))

    def test_grok_result_leaves_cache_reads_out_of_tokens_and_the_four_counts_add_up_to_its_total(self):
        s = spend.from_grok_result(open(os.path.join(DATA, "grok-result.json")).read(), "grok-4.7")
        self.assertEqual((s["harness"], s["model"], s["model_id"]), ("grok", "grok-4.7", "grok-4.7-build"))
        self.assertEqual((s["tokens"], s["usd"], s["turns"], s["session"]), (1000, 0.0123, 3, "0000"))
        self.assertEqual(s["cache_read"], 4000)

    def test_claude_session_counts_each_message_once_and_has_no_dollars(self):
        s = spend.from_claude_session(os.path.join(DATA, "claude-session.jsonl"))
        self.assertEqual(s["tokens"], (3 + 100 + 50) + (2 + 20))
        self.assertEqual(s["cache_read"], 1000 + 1100)
        self.assertEqual((s["turns"], s["usd"], s["wall_s"]), (2, None, 60.0))  # first line to last

    def test_opencode_export_counts_reasoning_as_output(self):
        s = spend.from_opencode("ses_x", exported=open(os.path.join(DATA, "opencode-export.json")).read())
        self.assertEqual((s["model"], s["tokens_out"], s["tokens"], s["usd"], s["turns"]),
                         ("gpt-oss:20b", 304, 17794 + 304, 0.0, 2))
        self.assertEqual(s["cache_read"], 1000)

    def test_the_budget_covers_the_makers_steps(self):
        data = {"budget": {"usd": 1, "tokens": 5000},
                "spend": [{"step": "maker", "usd": 0.6, "tokens": 3000}, {"step": "maker", "usd": 0.5, "tokens": 1000},
                          {"step": "guardian", "usd": 9, "tokens": 99999}]}
        state = spend.budget_state(data)
        self.assertEqual((state["over"], state["spent"]["tokens"]), (["usd"], 4000))


if __name__ == "__main__":
    unittest.main()

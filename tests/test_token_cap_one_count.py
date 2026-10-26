import os
import unittest

from helpers import HOME

import record
import spend

DATA = os.path.join(HOME, "tests", "data")

# The thundercloud slice in seanpk/xv-agents#28: 26 input, 4,989 output, 359,933 cache
# reads, 28,082 cache writes. One count everywhere: input + output + cache write.


def thundercloud():
    return spend.item("claude", "sonnet", tokens_in=26, tokens_out=4989,
                      cache_read=359933, cache_write=28082)


class OneTokenCountTest(unittest.TestCase):
    def test_a_new_spend_item_counts_no_cache_reads(self):
        self.assertEqual(thundercloud()["tokens"], 33097)

    def test_the_item_still_keeps_all_four_raw_counts(self):
        row = thundercloud()
        self.assertEqual((row["tokens_in"], row["tokens_out"], row["cache_read"], row["cache_write"]),
                         (26, 4989, 359933, 28082))

    def test_totals_of_new_items_is_the_sum_of_their_counts(self):
        self.assertEqual(spend.totals([thundercloud(), thundercloud()])["tokens"], 66194)


class GuideAndBudgetAgreeTest(unittest.TestCase):
    # A slice open at the merge holds rows written before the change: their stored
    # `tokens` still includes cache reads. The guide row and the budget must agree.
    def old_row(self):
        return {"step": "maker", "harness": "claude", "model": "sonnet", "usd": 0.159,
                "tokens_in": 26, "tokens_out": 4989, "cache_read": 359933, "cache_write": 28082,
                "tokens": 393030}

    def test_the_guide_counts_a_pre_merge_row_without_cache_reads(self):
        self.assertEqual(record.actual_by_key([self.old_row()])[("claude", "sonnet")]["tokens"], 33097)

    def test_the_budget_counts_a_pre_merge_row_without_cache_reads(self):
        self.assertEqual(spend.totals([self.old_row()])["tokens"], 33097)

    def test_a_row_with_only_a_stored_total_counts_that_total_in_both(self):
        row = {"step": "maker", "harness": "claude", "model": "sonnet", "usd": 0.1, "tokens": 5000}
        self.assertEqual(record.actual_by_key([row])[("claude", "sonnet")]["tokens"], 5000)
        self.assertEqual(spend.totals([row])["tokens"], 5000)


class ReadersKeepCacheReadsTest(unittest.TestCase):
    def read(self, name):
        return open(os.path.join(DATA, name)).read()

    def test_claude_result_keeps_its_cache_reads(self):
        self.assertEqual(spend.from_claude_result(self.read("claude-result.json"), "sonnet")["cache_read"], 30000)

    def test_grok_result_keeps_its_cache_reads(self):
        self.assertEqual(spend.from_grok_result(self.read("grok-result.json"), "grok-4.7")["cache_read"], 4000)

    def test_claude_session_keeps_its_cache_reads(self):
        self.assertEqual(spend.from_claude_session(os.path.join(DATA, "claude-session.jsonl"))["cache_read"],
                         1000 + 1100)

    def test_opencode_export_keeps_its_cache_reads(self):
        s = spend.from_opencode("ses_x", exported=self.read("opencode-export.json"))
        self.assertEqual(s["cache_read"], 1000)


if __name__ == "__main__":
    unittest.main()

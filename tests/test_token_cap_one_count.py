import importlib.util
import os
import unittest

from helpers import HOME

import record
import spend

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


def old_row():
    # A slice open at the merge holds rows written before the change: their stored
    # `tokens` still includes cache reads.
    return {"step": "maker", "harness": "claude", "model": "sonnet", "usd": 0.159,
            "tokens_in": 26, "tokens_out": 4989, "cache_read": 359933, "cache_write": 28082,
            "tokens": 393030}


class GuideAndBudgetAgreeTest(unittest.TestCase):
    # The guide row and the budget must agree on such a row.
    def test_the_guide_counts_a_pre_merge_row_without_cache_reads(self):
        self.assertEqual(record.actual_by_key([old_row()])[("claude", "sonnet")]["tokens"], 33097)

    def test_the_budget_counts_a_pre_merge_row_without_cache_reads(self):
        self.assertEqual(spend.totals([old_row()])["tokens"], 33097)

    def test_a_row_with_only_a_stored_total_counts_that_total_in_both(self):
        row = {"step": "maker", "harness": "claude", "model": "sonnet", "usd": 0.1, "tokens": 5000}
        self.assertEqual(record.actual_by_key([row])[("claude", "sonnet")]["tokens"], 5000)
        self.assertEqual(spend.totals([row])["tokens"], 5000)


class EvalReportCountsOneWayTest(unittest.TestCase):
    # evals/report.py sums a run's spend rows with the same count as the budget.
    def test_an_eval_report_counts_a_pre_merge_row_without_cache_reads(self):
        spec = importlib.util.spec_from_file_location("eval_report", os.path.join(HOME, "evals", "report.py"))
        report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report)
        run = {"scenario": "s", "harness": "claude", "arm": "skill", "assertions": [], "spend": [old_row()]}
        self.assertIn("spend: 33097 tokens", report.details([run]))


if __name__ == "__main__":
    unittest.main()

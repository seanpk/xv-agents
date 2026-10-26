import unittest

from helpers import HOME  # noqa: F401  (puts scripts/ on sys.path)

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


if __name__ == "__main__":
    unittest.main()

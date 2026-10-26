import unittest

from helpers import HOME  # noqa: F401  (puts scripts/ on sys.path)

import spend

# The thundercloud slice in seanpk/xv-agents#28: 393,030 tokens in the steps so far,
# of which 359,933 cache reads, 28,082 cache writes, 26 input, 4,989 output.
THUNDERCLOUD = {"step": "maker", "usd": 0.159, "tokens_in": 26, "tokens_out": 4989,
                "cache_read": 359933, "cache_write": 28082, "tokens": 393030}


class TokenCapTest(unittest.TestCase):
    def test_cache_reads_do_not_count_against_the_token_cap(self):
        state = spend.budget_state({"budget": {"tokens": 150000, "usd": 1}, "spend": [THUNDERCLOUD]})
        self.assertEqual(state["spent"]["tokens"], 33097)
        self.assertEqual(state["over"], [])

    def test_the_cap_still_fires_on_input_output_and_cache_writes(self):
        row = dict(THUNDERCLOUD, cache_write=150000)
        state = spend.budget_state({"budget": {"tokens": 150000, "usd": 1}, "spend": [row]})
        self.assertEqual(state["over"], ["tokens"])


if __name__ == "__main__":
    unittest.main()

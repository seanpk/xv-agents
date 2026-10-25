import os
import re
import unittest

from helpers import HOME  # noqa: F401
import orders
from xvlib import DEFAULT_CONFIG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUITE_OUTPUT = (
    "F\n"
    "======================================================================\n"
    "FAIL: test_total (test_cart.CartTest.test_total)\n"
    "----------------------------------------------------------------------\n"
    "AssertionError: 3 != 4\n"
    "\n"
    "Ran 1 test in 0.001s\n\n"
    "FAILED (failures=1)\n"
)
FAILING_STEP = "FAIL: test_total (test_cart.CartTest.test_total)"


def rec(after, **checks):
    return {"id": "s1", "set_by": "pat", "budget": {"usd": 2}, "moved_tests": [], "stops": [],
            "spend": [{"step": "maker", "usd": 2.5, "tokens": 10}],
            "checks": {"reports": [{"agent": after, "status": "green"}], after: checks}}


def read_brief(name):
    with open(os.path.join(ROOT, "skills", name, "SKILL.md")) as f:
        return f.read()


class StopsQuoteTheFailingStepTest(unittest.TestCase):
    def test_cleaner_broke_suite_quotes_the_failing_step(self):
        d = rec("cleaner", suite="red", suite_output=SUITE_OUTPUT)
        s = orders.verdict(d, "cleaner", DEFAULT_CONFIG)["stop"]
        self.assertEqual(s["order"], "cleaner_broke_suite")
        self.assertIn(FAILING_STEP, s["question"])

    def test_budget_spent_quotes_the_failing_step(self):
        d = rec("maker", suite="red", suite_output=SUITE_OUTPUT)
        s = orders.verdict(d, "maker", DEFAULT_CONFIG)["stop"]
        self.assertEqual(s["order"], "budget_spent")
        self.assertIn(FAILING_STEP, s["question"])


class GreenMeansExitZeroTest(unittest.TestCase):
    def test_the_briefs_define_green_as_the_suite_command_exiting_0(self):
        for name in ("maker", "cleaner"):
            with self.subTest(brief=name):
                self.assertTrue(re.search(r"exit(s|ed)? (with )?(code )?0", read_brief(name)),
                                f"the {name} brief does not say green means exit 0")

import json
import os
import re
import sys
import unittest

from helpers import HOME, RepoCase, sh
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


FAKE = os.path.join(HOME, "tests", "fake_agent.py")
LONG_RED_SUITE = (
    "import sys\n"
    "print('=' * 70)\n"
    "print(%r)\n"
    "print('-' * 70)\n"
    "print('Traceback (most recent call last):')\n"
    "for i in range(60):\n"
    "    print('  File \"/app/deep/frame_%%d.py\", line %%d, in call' %% (i, i))\n"
    "print('AssertionError: 3 != 4')\n"
    "print()\n"
    "print('Ran 1 test in 0.001s')\n"
    "print()\n"
    "print('FAILED (failures=1)')\n"
    "sys.exit(1)\n"
) % FAILING_STEP


class LongOutputTest(RepoCase):
    """The FAIL: header sits far above the last 800 characters of a long traceback."""

    def test_the_stop_quotes_the_failing_step_when_the_output_is_longer_than_800_characters(self):
        script = os.path.join(self.repo, "long_red_suite.py")
        with open(script, "w") as f:
            f.write(LONG_RED_SUITE)
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + 'agents:\n  default: ["%s", "%s", "{prompt}"]\n' % (sys.executable, FAKE) + text[end:]
        text = re.sub(r"(?m)^  command: \"python3.*$", '  command: "%s %s"' % (sys.executable, script), text, count=1)
        open(cfg, "w").write(text)
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "a long red suite"], self.repo)
        wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=wt)
        for agent in ("forecaster", "scenario", "maker"):
            self.xv("step", agent, "s1", cwd=wt, check=False)
        p = self.xv("step", "cleaner", "s1", cwd=wt, check=False)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["order"], "cleaner_broke_suite")
        self.assertIn(FAILING_STEP, stop["question"])

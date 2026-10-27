import json
import os
import stat
import sys
import unittest

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")

# A stand-in `claude` on the watch's agent line: it notes the argv it was given, then does
# the fixed job of the fake agent. The harness is Claude by its name, so it gets the caps.
CLAUDE = """#!{python}
import json, os, subprocess, sys
with open(os.environ["CAP_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
sys.exit(subprocess.call([{python!r}, {fake!r}, sys.argv[-1]]))
"""


class BudgetCapTest(RepoCase):
    """The budget caps the whole slice: checked before each step, green or red."""

    def setUp(self):
        super().setUp()
        bindir = os.path.join(self.tmp, "bin")
        os.makedirs(bindir)
        self.claude = os.path.join(bindir, "claude")
        with open(self.claude, "w") as f:
            f.write(CLAUDE.format(python=sys.executable, fake=FAKE))
        os.chmod(self.claude, os.stat(self.claude).st_mode | stat.S_IXUSR)
        self.log = os.path.join(self.tmp, "calls.log")
        os.environ["CAP_LOG"] = self.log
        self.addCleanup(os.environ.pop, "CAP_LOG", None)
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{self.claude}", "-p", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake claude"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")

    def budget(self, **b):
        self.xv("record", "set", "s1", "budget", json.dumps(b), "--by", "pat", cwd=self.wt)

    def spent(self, step, usd, tokens=10):
        row = {"step": step, "usd": usd, "tokens": tokens, "tokens_in": tokens, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0}
        self.xv("record", "add", "s1", "spend", json.dumps(row), cwd=self.wt)

    def calls(self):
        if not os.path.exists(self.log):
            return []
        return [json.loads(line) for line in open(self.log).read().splitlines()]

    def cap_of(self, argv):
        self.assertIn("--max-budget-usd", argv)
        return float(argv[argv.index("--max-budget-usd") + 1])

    def test_a_claude_step_gets_the_dollars_left_not_the_whole_budget(self):
        self.budget(usd=1, tokens=10000000)
        self.spent("forecaster", 0.8)
        self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertAlmostEqual(self.cap_of(self.calls()[0]), 0.2, places=6)

    def test_with_no_dollars_left_the_step_does_not_run_though_the_suite_is_green(self):
        self.budget(usd=1, tokens=10000000)
        self.spent("forecaster", 0.5)
        self.spent("maker", 0.55)
        self.xv("record", "set", "s1", "suite", '"green"', cwd=self.wt)
        p = self.xv("step", "guardian", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual((stop["order"], stop["seat"]), ("budget_spent", "originator"))
        self.assertIn("1.05", stop["question"])
        self.assertEqual(self.calls(), [])

    def test_the_token_cap_stops_the_step_before_it_runs(self):
        self.budget(usd=100, tokens=1000)
        self.spent("scenario", 0.01, tokens=1000)
        p = self.xv("step", "maker", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent")
        self.assertEqual(self.calls(), [])

    def test_a_raised_budget_lets_the_slice_go_on_from_the_step_it_stopped_before(self):
        self.budget(usd=1, tokens=10000000)
        self.spent("maker", 1.05)
        p = self.xv("step", "guardian", "s1", cwd=self.wt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent")
        self.budget(usd=2, tokens=10000000)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "raised the budget", cwd=self.wt)
        self.xv("step", "guardian", "s1", cwd=self.wt, check=False)
        self.assertAlmostEqual(self.cap_of(self.calls()[0]), 0.95, places=6)


if __name__ == "__main__":
    unittest.main()

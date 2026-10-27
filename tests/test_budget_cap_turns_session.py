import json
import os
import unittest

from helpers import sh
from test_budget_cap import BudgetCapTest


class TurnsAndSessionTest(BudgetCapTest):
    """A turns budget caps the whole slice; a step that runs in the session is checked too."""

    def spent_turns(self, step, turns):
        row = {"step": step, "usd": 0.01, "tokens": 10, "tokens_in": 10, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0, "turns": turns}
        self.xv("record", "add", "s1", "spend", json.dumps(row), cwd=self.wt)

    def test_a_claude_step_gets_the_turns_left_not_the_whole_turns_budget(self):
        self.budget(usd=100, tokens=10000000, turns=30)
        self.spent_turns("forecaster", 12)
        self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        argv = self.calls()[0]
        self.assertIn("--max-turns", argv)
        self.assertEqual(int(argv[argv.index("--max-turns") + 1]), 18)

    def test_with_no_turns_left_the_step_does_not_run(self):
        self.budget(usd=100, tokens=10000000, turns=30)
        self.spent_turns("forecaster", 30)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent")
        self.assertEqual(self.calls(), [])

    def test_a_session_step_with_the_budget_spent_stops_at_budget_spent(self):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("agents:\n", "agents:\n  guardian: session\n", 1)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "guardian in the session"], self.repo)
        wt = self.new_slice("s2", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s2", "budget", json.dumps({"usd": 1, "tokens": 10000000}), "--by", "pat", cwd=wt)
        row = {"step": "maker", "usd": 1.05, "tokens": 10, "tokens_in": 10, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0}
        self.xv("record", "add", "s2", "spend", json.dumps(row), cwd=wt)
        p = self.xv("step", "guardian", "s2", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "budget_spent")


# Importing BudgetCapTest reruns its four tests here too; the new cases are the three above.
if __name__ == "__main__":
    unittest.main()

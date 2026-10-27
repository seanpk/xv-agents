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


class PrototypeBudgetsTest(BudgetCapTest):
    """Each prototype variant has its own budget, set by the person; the slice budget does not cover them."""

    def setUp(self):
        super().setUp()
        out = self.xv("slice", "new", "p1", "--by", "pat", "--kind", "prototype", "--axis",
                      "what the household acts on when it marks food used",
                      "--scenario", "Marking food used after a meal is quicker.").stdout
        self.pwt = out.strip().splitlines()[-1]
        self.xv("record", "set", "p1", "budget", json.dumps({"usd": 0.5, "tokens": 10000000}), "--by", "pat", cwd=self.pwt)

    def proto_budgets(self, **usd):
        value = {n: {"usd": u, "tokens": 10000000} for n, u in usd.items()}
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps(value), "--by", "pat", cwd=self.pwt)

    def proto_spent(self, name, usd):
        row = {"step": f"prototype-{name}", "usd": usd, "tokens": 10, "tokens_in": 10, "tokens_out": 0,
               "cache_read": 0, "cache_write": 0}
        self.xv("record", "add", "p1", "spend", json.dumps(row), cwd=self.pwt)

    def caps_by_variant(self):
        caps = {}
        for argv in self.calls():
            n = argv[-1].split("Your variant: ")[1][0]
            caps[n] = self.cap_of(argv)
        return caps

    def test_without_prototype_budgets_prototype_start_stops_for_the_person(self):
        p = self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertIn("budget", stop["order"])
        self.assertEqual(stop["seat"], "originator")
        self.assertEqual(self.calls(), [])

    def test_each_variant_is_capped_at_its_own_budget(self):
        self.proto_budgets(a=1, b=2.5, c=0.75)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        caps = self.caps_by_variant()
        self.assertEqual(sorted(caps), ["a", "b", "c"])
        self.assertAlmostEqual(caps["a"], 1.0, places=6)
        self.assertAlmostEqual(caps["b"], 2.5, places=6)
        self.assertAlmostEqual(caps["c"], 0.75, places=6)

    def test_a_variant_gets_its_budget_less_its_own_spend_only(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 0.8)
        self.proto_spent("b", 0.5)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        caps = self.caps_by_variant()
        self.assertAlmostEqual(caps["a"], 0.2, places=6)
        self.assertAlmostEqual(caps["b"], 1.5, places=6)
        self.assertAlmostEqual(caps["c"], 3.0, places=6)

    def test_a_variant_that_spent_its_budget_stops_alone(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        self.assertEqual(sorted(self.caps_by_variant()), ["b", "c"])

    def test_prototype_spend_does_not_count_against_the_slice_budget(self):
        # the slice budget is $0.50; variant a has spent $0.90 of its own $2
        self.proto_budgets(a=2, b=2, c=2)
        self.proto_spent("a", 0.9)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        self.assertEqual(sorted(self.caps_by_variant()), ["a", "b", "c"])
        self.assertAlmostEqual(self.caps_by_variant()["a"], 1.1, places=6)


# Importing BudgetCapTest reruns its four tests here too; the new cases are the three above.
if __name__ == "__main__":
    unittest.main()

import json
import os
import sys
import unittest

from helpers import sh
import orders
from xvlib import DEFAULT_CONFIG
from test_budget_cap import BudgetCapTest, FAKE


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

    def test_the_stopped_variant_is_named_in_the_log_and_the_side_by_side_file(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        body = open(os.path.join(self.pwt, ".xv", "slices", "p1.md")).read()
        log = [l for l in body.split("## Log")[1].splitlines() if "variant a" in l and "budget" in l]
        self.assertTrue(log, "the log says variant a stopped and why: its budget is spent")
        side = open(os.path.join(self.pwt, ".xv", "slices", "p1.prototypes.md")).read()
        row = [l for l in side.splitlines() if l.startswith("| a ")]
        self.assertTrue(row and "budget" in row[0], "the side-by-side file shows variant a stopped at its budget")

    def test_without_prototype_budgets_the_stop_is_named_prototype_budgets_not_set(self):
        p = self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "prototype_budgets_not_set")

    def pick_args(self, variant):
        scen = os.path.join(self.tmp, "restated.md")
        open(scen, "w").write("After a meal, the household marks a whole recipe's food used in one call.")
        return ["prototype", "pick", "p1", "--variant", variant, "--by", "pat,sam", "--scenario-file", scen]

    def test_a_stopped_variant_cannot_be_picked(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        p = self.xv(*self.pick_args("a"), cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("budget", p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        self.assertEqual(data["kind"], "prototype")

    def test_picking_another_variant_after_one_stopped_does_not_crash(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        p = self.xv(*self.pick_args("b"), cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        self.assertEqual((data["kind"], data["next"]), ("feature", "forecaster"))
        branches = sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout
        self.assertEqual(branches.strip(), "")

    def test_prototype_spend_does_not_count_against_the_slice_budget(self):
        # the slice budget is $0.50; variant a has spent $0.90 of its own $2
        self.proto_budgets(a=2, b=2, c=2)
        self.proto_spent("a", 0.9)
        self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)
        self.assertEqual(sorted(self.caps_by_variant()), ["a", "b", "c"])
        self.assertAlmostEqual(self.caps_by_variant()["a"], 1.1, places=6)

    def start(self):
        return self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)

    def stop_of(self, p):
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        return json.loads(p.stdout)["stop"]

    def answer_raised(self):
        self.xv("record", "answer", "p1", "--by", "pat,sam", "--answer", "raised the budget", cwd=self.pwt)

    def clear_calls(self):
        os.remove(self.log)

    def proto_branches(self):
        out = sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout
        return sorted(out.split())

    def test_a_variant_that_ran_out_sends_the_slice_back_to_the_person_who_set_it_going(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        stop = self.stop_of(self.start())
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("1.05", stop["question"])
        self.assertIn("prototype_budgets", stop["question"])
        self.assertIn("none", stop["question"])
        self.assertEqual(sorted(self.caps_by_variant()), ["b", "c"], "the others still ran")

    def test_when_all_three_ran_out_none_is_the_only_pick(self):
        self.proto_budgets(a=1, b=1, c=1)
        for n in "abc":
            self.proto_spent(n, 1.05)
        stop = self.stop_of(self.start())
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("none", stop["question"])
        self.assertEqual(self.calls(), [])
        p = self.xv(*self.pick_args("none"), cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        self.assertEqual(data["status"], "abandoned")

    def test_a_second_start_runs_only_the_variant_whose_budget_was_raised(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=2, c=3)
        self.answer_raised()
        self.start()
        caps = self.caps_by_variant()
        self.assertEqual(sorted(caps), ["a"])
        self.assertAlmostEqual(caps["a"], 1.95, places=6)

    def test_a_second_start_keeps_the_variants_that_finished(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=2, c=3)
        self.answer_raised()
        self.start()
        self.assertEqual(self.proto_branches(), ["xv/p1-proto-a", "xv/p1-proto-b", "xv/p1-proto-c"])
        for n in "bc":
            self.assertTrue(os.path.exists(os.path.join(self.pwt, ".xv", "prototypes", "p1", n, "recording.md")))
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        self.assertEqual(sorted(p["name"] for p in data["prototypes"]), ["a", "b", "c"])
        self.assertTrue(all(p["branch"] and p["recording"] for p in data["prototypes"]))
        side = open(os.path.join(self.pwt, ".xv", "slices", "p1.prototypes.md")).read()
        for n in "abc":
            self.assertIn(f"variant {n}:", side)

    def test_a_variant_whose_budget_was_not_raised_is_not_run_again_and_the_stop_says_so(self):
        self.proto_budgets(a=1, b=1, c=3)
        self.proto_spent("a", 1.05)
        self.proto_spent("b", 1.05)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=1, c=3)
        self.answer_raised()
        stop = self.stop_of(self.start())
        self.assertEqual(sorted(self.caps_by_variant()), ["a"])
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("1.05", stop["question"], "the stop names b and what it spent")

    def test_prototype_start_leaves_the_missing_budgets_stop_to_the_standing_order(self):
        stop = self.stop_of(self.start())
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        data["stops"] = []
        fired = [f for f in orders.evaluate(data, "prototype", DEFAULT_CONFIG)
                 if f["order"] == "prototype_budgets_not_set"]
        self.assertEqual(len(fired), 1)
        self.assertEqual(stop["question"], fired[0]["question"])
        self.assertEqual(self.calls(), [])

    def costly_variant(self, name, usd):
        """Swap in a claude that prints the JSON of `claude -p --output-format json`, with variant `name`
        costing `usd` for its run and the others a tenth of a dollar."""
        script = (f"#!{sys.executable}\n"
                  "import json, os, subprocess, sys\n"
                  "with open(os.environ['CAP_LOG'], 'a') as f:\n"
                  "    f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                  f"out = subprocess.run([{sys.executable!r}, {FAKE!r}, sys.argv[-1]],\n"
                  "                     capture_output=True, text=True).stdout\n"
                  f"cost = {usd!r} if 'Your variant: {name}' in sys.argv[-1] else 0.1\n"
                  "print(json.dumps({'result': out, 'total_cost_usd': cost, 'num_turns': 1,\n"
                  "                  'usage': {'input_tokens': 10, 'output_tokens': 10}, 'session_id': 'x'}))\n")
        with open(self.claude, "w") as f:
            f.write(script)

    def test_a_variant_whose_run_passes_its_budget_sends_the_slice_back_to_the_person(self):
        self.costly_variant("a", 1.2)
        self.proto_budgets(a=1, b=2, c=3)
        stop = self.stop_of(self.start())
        self.assertEqual(sorted(self.caps_by_variant()), ["a", "b", "c"])
        self.assertEqual(stop["order"], "prototype_budget_spent")
        self.assertEqual(stop["seat"], "originator")
        self.assertIn("a", stop["question"].split("Raise a budget")[0])
        self.assertIn("1.2", stop["question"])
        self.assertIn("none", stop["question"])

    def test_a_variant_whose_run_passed_its_budget_cannot_be_picked_though_it_has_a_branch(self):
        self.costly_variant("a", 1.2)
        self.proto_budgets(a=1, b=2, c=3)
        self.stop_of(self.start())
        self.assertIn("xv/p1-proto-a", self.proto_branches())
        p = self.xv(*self.pick_args("a"), cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("budget", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_a_second_start_runs_again_a_variant_whose_run_passed_its_budget_once_raised(self):
        self.costly_variant("a", 1.2)
        self.proto_budgets(a=1, b=2, c=3)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=2, c=3)
        self.answer_raised()
        self.start()
        caps = self.caps_by_variant()
        self.assertEqual(sorted(caps), ["a"], "only the variant that ran out runs again")
        self.assertAlmostEqual(caps["a"], 1.8, places=6)
        for n in "bc":
            self.assertTrue(os.path.exists(os.path.join(self.pwt, ".xv", "prototypes", "p1", n, "recording.md")))

    def silent_variant(self, name):
        """Swap in a claude that runs variant `name` within budget but leaves no recording; the others
        do the fake agent's job."""
        script = (f"#!{sys.executable}\n"
                  "import json, os, subprocess, sys\n"
                  "with open(os.environ['CAP_LOG'], 'a') as f:\n"
                  "    f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                  f"if 'Your variant: {name}' in sys.argv[-1]:\n"
                  "    print('done')\n"
                  "    sys.exit(0)\n"
                  f"sys.exit(subprocess.call([{sys.executable!r}, {FAKE!r}, sys.argv[-1]]))\n")
        with open(self.claude, "w") as f:
            f.write(script)

    def test_a_second_start_reruns_a_variant_that_ran_within_budget_but_left_no_recording(self):
        self.silent_variant("b")
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=2, c=3)
        self.answer_raised()
        self.start()
        self.assertEqual(sorted(self.caps_by_variant()), ["a", "b"], "c finished and is kept")
        self.assertTrue(os.path.exists(os.path.join(self.pwt, ".xv", "prototypes", "p1", "c", "recording.md")))

    def test_a_second_start_with_a_new_axis_reruns_all_three_and_keeps_none(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        self.clear_calls()
        self.proto_budgets(a=3, b=2, c=3)
        self.answer_raised()
        p = self.xv("prototype", "start", "p1", "--axis", "what the household sees after a meal",
                    cwd=self.pwt, check=False)
        self.assertEqual(sorted(self.caps_by_variant()), ["a", "b", "c"], p.stdout + p.stderr)
        data = json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)
        self.assertEqual(sorted(p["name"] for p in data["prototypes"]), ["a", "b", "c"])

    def test_the_stop_words_a_run_out_during_the_run_and_one_already_over_at_the_start_apart(self):
        self.costly_variant("a", 1.2)
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("b", 2.05)
        q = self.stop_of(self.start())["question"]
        self.assertRegex(q, r"variant a spent [^;]*ran out of its budget during its run")
        self.assertRegex(q, r"variant b spent [^;]*was not run")
        self.assertNotRegex(q, r"variant a spent [^;]*was not run")
        self.assertNotRegex(q, r"variant b spent [^;]*during its run")

    def test_the_person_who_set_it_going_answers_a_budget_raise_alone(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        self.proto_budgets(a=3, b=2, c=3)
        p = self.xv("record", "answer", "p1", "--by", "pat", "--answer", "raised the budget",
                    cwd=self.pwt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_the_stop_says_a_pick_is_for_two_people_unless_the_repo_runs_solo(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        q = self.stop_of(self.start())["question"]
        self.assertIn("two people", q)
        self.assertIn("solo", q)
        args = self.pick_args("none")
        args[args.index("--by") + 1] = "pat"
        p = self.xv(*args, cwd=self.pwt, check=False)
        self.assertNotEqual(p.returncode, 0, "pick keeps its two-people rule: " + p.stdout + p.stderr)

    def test_the_stop_says_to_answer_it_before_running_start_again(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        q = self.stop_of(self.start())["question"]
        self.assertIn("answer", q)
        self.assertIn("`xv prototype start", q)
        self.assertLess(q.index("answer"), q.index("`xv prototype start"))

    def test_the_log_line_says_who_the_pick_is_for_in_the_stops_terms(self):
        self.proto_budgets(a=1, b=2, c=3)
        self.proto_spent("a", 1.05)
        self.stop_of(self.start())
        body = open(os.path.join(self.pwt, ".xv", "slices", "p1.md")).read()
        log = [l for l in body.split("## Log")[1].splitlines() if "prototypes ready" in l]
        self.assertTrue(log)
        self.assertIn("two people", log[0])
        self.assertIn("solo", log[0])


# Importing BudgetCapTest reruns its four tests here too; the new cases are the ones in PrototypeBudgetsTest.
if __name__ == "__main__":
    unittest.main()

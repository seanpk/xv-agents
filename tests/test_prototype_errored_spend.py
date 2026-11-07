"""#121: a variant that errors after its agent ran keeps that run's spend, and a working folder that is gone
is reported as gone, not as a missing agent CLI."""

import json
import os
import shutil
import sys
import tempfile
import unittest

from helpers import sh
import agentcli
from xvlib import XVError
from test_budget_cap import BudgetCapSetup, FAKE

# A `claude` that prints the JSON of `claude -p --output-format json`: each variant's run costs $0.40.
COSTLY = """#!{python}
import json, os, subprocess, sys
with open(os.environ["CAP_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
out = subprocess.run([{python!r}, {fake!r}, sys.argv[-1]], capture_output=True, text=True).stdout
print(json.dumps({{"result": out, "total_cost_usd": 0.4, "num_turns": 3,
                  "usage": {{"input_tokens": 10, "output_tokens": 10}}, "session_id": "sess-" + sys.argv[-1].split("Your variant: ")[1][0]}}))
"""


class ErroredVariantSpendTest(BudgetCapSetup):
    def setUp(self):
        super().setUp()
        with open(self.claude, "w") as f:
            f.write(COSTLY.format(python=sys.executable, fake=FAKE))
        out = self.xv("slice", "new", "p1", "--by", "pat", "--kind", "prototype", "--axis",
                      "what the household acts on when it marks food used",
                      "--scenario", "Marking food used after a meal is quicker.").stdout
        self.pwt = out.strip().splitlines()[-1]
        value = {n: {"usd": 1, "tokens": 10000000} for n in "abc"}
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps(value), "--by", "pat", cwd=self.pwt)

    def block_b_run_log(self):
        """b's run log cannot be written: a directory sits where the file goes. The agent has run by then."""
        common = sh(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], self.pwt).stdout.strip()
        self.blocked = os.path.join(common, "xv", "runs", "p1", "prototype-b.out")
        os.makedirs(self.blocked)

    def record(self):
        return json.loads(self.xv("record", "show", "p1", "--json", cwd=self.pwt).stdout)

    def start(self):
        return self.xv("prototype", "start", "p1", cwd=self.pwt, check=False)

    def test_a_variant_that_errors_after_its_agent_ran_keeps_that_runs_spend(self):
        self.block_b_run_log()
        self.start()
        data = self.record()
        b = next(p for p in data["prototypes"] if p["name"] == "b")
        self.assertTrue(b["error"], "b is recorded as not finished")
        rows = [s for s in data["spend"] if s.get("step") == "prototype-b"]
        self.assertEqual(len(rows), 1, "b's run is in the spend")
        self.assertAlmostEqual(rows[0]["usd"], 0.4, places=6)
        self.assertEqual(b["session"], "sess-b", "b's session is kept too")

    def test_a_second_start_gives_the_errored_variant_only_what_is_left_of_its_budget(self):
        self.block_b_run_log()
        self.start()
        os.rmdir(self.blocked)
        os.remove(self.log)
        self.xv("record", "answer", "p1", "--by", "pat,sam", "--answer", "run b again", cwd=self.pwt, check=False)
        self.start()
        caps = {}
        for argv in self.calls():
            caps[argv[-1].split("Your variant: ")[1][0]] = self.cap_of(argv)
        self.assertEqual(sorted(caps), ["b"], "only b runs again")
        self.assertAlmostEqual(caps["b"], 0.6, places=6)

    def test_an_errored_variant_whose_run_passed_its_budget_has_run_out(self):
        value = {"a": {"usd": 1}, "b": {"usd": 0.3}, "c": {"usd": 1}}
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps(value), "--by", "pat", cwd=self.pwt)
        self.block_b_run_log()
        p = self.start()
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "prototype_budget_spent")
        self.assertIn("b", self.record()["checks"]["prototype"]["ran_out"])


class GoneFolderTest(unittest.TestCase):
    def test_a_missing_working_folder_is_not_reported_as_a_missing_agent_cli(self):
        gone = os.path.join(tempfile.mkdtemp(), "proto-b")
        with self.assertRaises(XVError) as caught:
            agentcli.run([sys.executable, "-c", "print(1)"], "hi", gone)
        self.assertNotIn("agent CLI not found", str(caught.exception))
        self.assertIn("working folder", str(caught.exception))
        self.assertIn(gone, str(caught.exception))

    def test_a_missing_agent_cli_is_still_reported_as_one(self):
        here = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, here, True)
        with self.assertRaises(XVError) as caught:
            agentcli.run(["no-such-agent-cli-xv", "{prompt}"], "hi", here)
        self.assertIn("agent CLI not found", str(caught.exception))

    def test_a_run_log_that_cannot_be_written_keeps_the_result(self):
        here = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, here, True)
        log = os.path.join(here, "run.out")
        os.makedirs(log)
        with self.assertRaises(agentcli.RanError) as caught:
            agentcli.run([sys.executable, "-c", "print('ran')"], "hi", here, log)
        self.assertIn("ran", caught.exception.result["stdout"])
        self.assertIn("run.out", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

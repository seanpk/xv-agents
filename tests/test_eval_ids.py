import importlib.util
import json
import os
import tempfile
import unittest

HOME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def eval_report():
    spec = importlib.util.spec_from_file_location("eval_report", os.path.join(HOME, "evals", "report.py"))
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    return report


class EvalIdsFollowTheRenameTest(unittest.TestCase):
    # #168: the eval ids use the new agent names; past results keep their old ids and share the new rows.
    def test_no_eval_scenario_uses_an_old_agent_name(self):
        names = []
        for f in os.listdir(os.path.join(HOME, "evals", "scenarios")):
            with open(os.path.join(HOME, "evals", "scenarios", f)) as fh:
                names.append((f, json.load(fh)["name"]))
        for f, name in names:
            self.assertNotIn(name, eval_report().OLD_IDS, f)
            self.assertTrue(f.endswith(f"-{name}.json"), f)

    def test_a_past_result_with_an_old_id_shares_the_row_of_its_new_id(self):
        report = eval_report()
        with tempfile.TemporaryDirectory() as d:
            for i, sid in enumerate(["guardian-pitch", "inspector-pitch"]):
                with open(os.path.join(d, f"{i}.json"), "w") as f:
                    json.dump({"scenario": sid, "harness": "claude", "arm": "skill", "passed": 1, "total": 1}, f)
            runs = report.load(d)
        self.assertEqual({r["scenario"] for r in runs}, {"inspector-pitch"})
        rows = [line for line in report.table(runs).splitlines() if "pitch" in line]
        self.assertEqual(len(rows), 1, rows)


if __name__ == "__main__":
    unittest.main()

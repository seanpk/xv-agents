"""Throwaway red for slice 2026-10-24-readme-drift. Sean removes it before the merge.

Expected values come from the scenario's words, not from the README: each order
scripts/orders.py fires needs a row in the README stop table that says, in words,
what that order is. The order ids are mapped to the words a row would use.
"""
import os
import re
import unittest

from helpers import HOME

README = open(os.path.join(HOME, "README.md"), encoding="utf-8").read()
ORDERS_SRC = open(os.path.join(HOME, "scripts", "orders.py"), encoding="utf-8").read()

# order id -> regexes; a row of the stop table must match at least one of them.
WORDS = {
    "no_report": [r"ended with no report"],
    "read_only_broken": [r"read-only agent wrote"],
    "budget_not_set": [r"budget (is |was )?(not set|missing)", r"no budget"],
    "scenario_touched_source": [r"scenario agent touched source"],
    "scenario_not_red": [r"scenario passed before the fix"],
    "unrecorded_move": [r"test file changed with no record"],
    "protected_changed": [r"changed a file only people change"],
    "prototype_context_reused": [r"context that had built a prototype"],
    "budget_spent": [r"budget is spent"],
    "repeated_failure": [r"same tests failed after two runs"],
    "diff_growing": [r"diff more than doubled", r"diff .*past the team"],
    "budget_past_limit": [r"budget raised past the team"],
    "cleaner_broke_suite": [r"cleaner.*(broke|red|not green|fail)",
                            r"suite .*(not green|red|fail).* (after|when) the cleaner"],
    "cleaner_touched_standards": [r"cleaner.*standards"],
    "shape_or_pitch": [r"shape_change: yes"],
    "shape_wider_than_forecast": [r"shape change wider than forecast"],
    "accept_moves": [r"old test moved with a record"],
    "ready_to_merge": [r"suite is green and nothing stopped"],
    "prototypes_ready": [r"prototypes ready to pick"],
    # the "<step>_stopped" orders: an agent ended its step with a stop of its own
    "agent_stopped": [r"agent (ended|ends|reported|reports|returned|returns|came back).*stop",
                      r"(forecaster|scenario agent|maker|cleaner|guardian).*(stopped|asks? a question)",
                      r"agent stopped"],
}


def fired_orders():
    ids = set(re.findall(r'fire\(\s*"([a-z_]+)"', ORDERS_SRC))
    if "_stopped" in ORDERS_SRC:
        ids.add("agent_stopped")
    return ids


def stop_table_rows():
    section = README.split("### The stops", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    rows = [l for l in section.splitlines() if l.startswith("|") and not re.match(r"\|\s*-", l)]
    return rows[1:]


class ReadmeDrift(unittest.TestCase):
    def test_every_order_has_a_row_in_the_stop_table(self):
        rows = [r.lower() for r in stop_table_rows()]
        missing = []
        for oid in sorted(fired_orders()):
            self.assertIn(oid, WORDS, f"orders.py fires {oid}; add its words to this test's map")
            if not any(re.search(p, r) for p in WORDS[oid] for r in rows):
                missing.append(oid)
        self.assertEqual(missing, [], "orders with no row in the README stop table")

    def test_status_says_0_2_0_came_from_a_real_init(self):
        status = README.split("\n## Status", 1)[1].split("\n## ", 1)[0]
        self.assertIn("0.2.0", status)
        self.assertRegex(status, r"(?i)real init")

    def test_readme_mentions_xv_adapt(self):
        self.assertIn("xv adapt", README)

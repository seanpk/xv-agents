---
id: 2026-10-24-readme-drift
title: "README matches the stop table, the status and xv adapt"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-readme-drift
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect edits only to the README stop table, the Status line, and the xv adapt mention; the xv:method block is ignored and tests/** are not expected to move."}
budget: {"tokens": 1500000, "usd": 5, "turns": 60, "set_by": "Sean Kennedy"}
red: null
wall_baseline: {"commit": "9c928f78559b394b26426d8ef0cf6adbbbfec8fe", "count": 24, "digest": "267ad56b32ec6280", "file": ".xv/slices/2026-10-24-readme-drift.wall.json"}
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 1146, "cache_read": 23315, "cache_write": 6278, "tokens": 30743, "usd": 0.0021, "turns": 3, "wall_s": 6.2, "session": "52649884-5019-4965-b74c-c53643667442", "step": "forecaster", "at": "2026-10-25T03:27:08+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-readme-drift/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 2588, "cache_read": 139685, "cache_write": 15405, "tokens": 157694, "usd": 0.1015, "turns": 9, "wall_s": 22.3, "session": "2628e120-86a7-46f4-beb1-d201e56b5df6", "step": "scenario", "at": "2026-10-25T03:34:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-readme-drift/02-scenario.out"}]
stops: [{"at": "2026-10-25T03:27:08+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-readme-drift budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "you can set your suggested estimate", "also": [], "answered_at": "2026-10-25T03:33:47+00:00"}, {"at": "2026-10-25T03:34:23+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (stopped): Ambiguous whether 'names every order' means the order identifiers appear in the stop table or that each order has a described row; no test written.", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No history for claude/sonnet or claude/opus in the guide; numbers left null, shape forecast narrow.", "at": "2026-10-25T03:27:08+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Ambiguous whether 'names every order' means the order identifiers appear in the stop table or that each order has a described row; no test written.", "at": "2026-10-25T03:34:23+00:00"}], "forecaster": {"at": "2026-10-25T03:27:08+00:00", "wrote": []}, "scenario": {"at": "2026-10-25T03:34:23+00:00", "protected_changed": [], "outside_tests": [], "red_fails": null}}
---
# README matches the stop table, the status and xv adapt

## Scenario

The README stop table names every order `scripts/orders.py` fires. The README Status line says 0.2.0 came from a real init. The README mentions `xv adapt`.

The red test for this slice is for this slice only: Sean removes it before the merge (decided 2026-10-24).

Settled at the scenario stop, 2026-10-24, Sean: "names every order" means each order `scripts/orders.py` fires has a row in the README stop table that describes it in words. The README keeps its wording; it does not add order ids. The red, which is removed before the merge, may map each order id to words from its row.

## May ignore

the generated block between the xv:method markers

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:08+00:00 forecaster: done: No history for claude/sonnet or claude/opus in the guide; numbers left null, shape forecast narrow.
- 2026-10-25T03:27:08+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-readme-drift budget ... --by <name>`).
- 2026-10-25T03:33:47+00:00 Sean Kennedy: set budget
- 2026-10-25T03:33:47+00:00 Sean Kennedy: answered budget_not_set: you can set your suggested estimate
- 2026-10-25T03:34:23+00:00 scenario: stopped: Ambiguous whether 'names every order' means the order identifiers appear in the stop table or that each order has a described row; no test written.
- 2026-10-25T03:34:23+00:00 watch: stop (scenario_stopped) for originator: The scenario stopped (stopped): Ambiguous whether 'names every order' means the order identifiers appear in the stop table or that each order has a described row; no test written.

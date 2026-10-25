---
id: 2026-10-24-readme-drift
title: "README matches the stop table, the status and xv adapt"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-readme-drift
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect edits only to the README stop table, the Status line, and the xv adapt mention; the xv:method block is ignored and tests/** are not expected to move."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 1146, "cache_read": 23315, "cache_write": 6278, "tokens": 30743, "usd": 0.0021, "turns": 3, "wall_s": 6.2, "session": "52649884-5019-4965-b74c-c53643667442", "step": "forecaster", "at": "2026-10-25T03:27:08+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-readme-drift/01-forecaster.out"}]
stops: [{"at": "2026-10-25T03:27:08+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-readme-drift budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No history for claude/sonnet or claude/opus in the guide; numbers left null, shape forecast narrow.", "at": "2026-10-25T03:27:08+00:00"}], "forecaster": {"at": "2026-10-25T03:27:08+00:00", "wrote": []}}
---
# README matches the stop table, the status and xv adapt

## Scenario

The README stop table names every order `scripts/orders.py` fires. The README Status line says 0.2.0 came from a real init. The README mentions `xv adapt`.

The red test for this slice is for this slice only: Sean removes it before the merge (decided 2026-10-24).

## May ignore

the generated block between the xv:method markers

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:08+00:00 forecaster: done: No history for claude/sonnet or claude/opus in the guide; numbers left null, shape forecast narrow.
- 2026-10-25T03:27:08+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-readme-drift budget ... --by <name>`).

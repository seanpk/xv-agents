---
id: 2026-10-24-boundary-imports
title: xv boundary finds Python edges in src layouts and flat scripts
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-boundary-imports
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect the Python import-edge resolution in boundary and its tests under tests/ to move; the defect is one bug with one scenario, so no wide change is expected."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 1016, "cache_read": 23319, "cache_write": 6305, "tokens": 30644, "usd": 0.002, "turns": 3, "wall_s": 6.6, "session": "4af2d40c-e67c-4ee7-bb28-0b02cca61c6d", "step": "forecaster", "at": "2026-10-25T03:27:08+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-boundary-imports/01-forecaster.out"}]
stops: [{"at": "2026-10-25T03:27:08+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-boundary-imports budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No guide rows for claude/sonnet or claude/opus; numbers left null for the engineer to set by hand.", "at": "2026-10-25T03:27:08+00:00"}], "forecaster": {"at": "2026-10-25T03:27:08+00:00", "wrote": []}}
---
# xv boundary finds Python edges in src layouts and flat scripts

## Scenario

In a `src/` layout and in flat scripts that import each other by bare name, `xv boundary` shows an edge for every import between modules. On this repo, `.xv/boundary-all.md` shows `run` -> `agentcli`, `orders`, `prompt`, `record`, `spend`. (seanpk/xv-agents#12)

## May ignore

JavaScript, Ruby and Go imports; dependency-cruiser

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:08+00:00 forecaster: done: No guide rows for claude/sonnet or claude/opus; numbers left null for the engineer to set by hand.
- 2026-10-25T03:27:08+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-boundary-imports budget ... --by <name>`).

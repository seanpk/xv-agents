---
id: 2026-11-25-failed-step
title: "A failed step marks its start ended, so a later move reads HEAD (#202)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-failed-step
base: ae7929481b166143489f51e6194aaf375eca7bb6
next: forecaster
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 170000, "turns": null, "usd": 1.0, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "opus", "tokens": 90000, "turns": null, "usd": 1.0, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}], "wall_s": 525, "rounds": 1, "rounds_reason": "Recent narrow defects of this shape each ran one pass per agent; a CHANGELOG-line question is the only stop likely to cost a round.", "shape_breadth": "narrow", "shape_note": "Expect the failed-step branch that marks step_start ended and the slice-only move's start reading to change, with one test and the CHANGELOG line."}
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5756, "cache_read": 62836, "cache_write": 49257, "tokens": 55019, "usd": 0.0134, "turns": 4, "wall_s": 27.3, "session": "2a94b75f-f181-44e7-a274-e1c75b60956f", "step": "forecaster", "at": "2026-11-25T19:14:47+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-25-failed-step/01-forecaster.out"}]
stops: [{"at": "2026-11-25T19:14:47+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-failed-step budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null, "fired_questions": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect, one pass expected: sonnet ~170k tokens, opus ~90k, haiku ~55k, about 525 s wall, 1 round.", "at": "2026-11-25T19:14:47+00:00"}], "forecaster": {"at": "2026-11-25T19:14:47+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "7eb81de3acb7d6e09190a1f050fbf5c2cb58f1a8", "ended": true}
---
# A failed step marks its start ended, so a later move reads HEAD (#202)

## Scenario

When `xv step` fails because the agent could not run (the agent CLI is missing, or the worktree is gone), the record's `step_start` is marked ended, as it is after a step that ran (1).
A slice-only move recorded after that failed step reads its line from `HEAD`, not from the failed step's start (2).
There is a CHANGELOG line (3).

## May ignore

a step that fails after the agent ran

## Recording

None. A feature starts from words.

## Log
- 2026-11-25T19:14:16+00:00 watch: slice opened by Sean Kennedy
- 2026-11-25T19:14:47+00:00 forecaster: done: Narrow defect, one pass expected: sonnet ~170k tokens, opus ~90k, haiku ~55k, about 525 s wall, 1 round.
- 2026-11-25T19:14:47+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-failed-step budget ... --by <name>`).

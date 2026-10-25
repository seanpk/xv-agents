---
id: 2026-10-25-suite-red-quote
title: "Stops quote the failing step; green means exit 0"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-suite-red-quote
base: f452d430f44f6c01e611f705f5b709b80231291b
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 696815, "turns": null, "usd": 0.48, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"], "note": "mean of the two sonnet rows; the guide has no turns column"}, {"harness": "claude", "model": "opus", "tokens": 447861, "turns": null, "usd": 0.59, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"], "note": "guardian only; mean of the two opus rows; the guide has no turns column"}], "wall_s": 287, "shape": "narrow", "breadth": "Expect edits to the maker and cleaner briefs (green means exit 0) and to the question text of the cleaner_broke_suite and budget stops; test files are walled off."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3071, "cache_read": 25034, "cache_write": 5691, "tokens": 33800, "usd": 0.0029, "turns": 3, "wall_s": 15.1, "session": "c60a849d-31e4-42df-931f-0a08bc5c5c8c", "step": "forecaster", "at": "2026-10-25T04:26:13+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-suite-red-quote/01-forecaster.out"}]
stops: [{"at": "2026-10-25T04:26:13+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-suite-red-quote budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from the two closed sonnet and opus slices; no history gap measured since all closed forecasts were null.", "at": "2026-10-25T04:26:13+00:00"}], "forecaster": {"at": "2026-10-25T04:26:13+00:00", "wrote": []}}
---
# Stops quote the failing step; green means exit 0

## Scenario

When the suite is red after the maker or the cleaner, the `cleaner_broke_suite` stop and the budget stop quote the failing step from `suite_output` in their question, so the person sees what failed without opening the record. The maker's and the cleaner's briefs say that green means the suite command exited 0, not what the end of its output looks like. (seanpk/xv-agents#19; Sean approves the brief change, solo.)

## May ignore

xv init asking for lint and format; a summary-line convention for suite scripts

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T04:26:13+00:00 forecaster: done: Forecast from the two closed sonnet and opus slices; no history gap measured since all closed forecasts were null.
- 2026-10-25T04:26:13+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-suite-red-quote budget ... --by <name>`).

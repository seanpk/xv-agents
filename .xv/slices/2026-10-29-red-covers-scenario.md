---
id: 2026-10-29-red-covers-scenario
title: A red that leaves part of the scenario untested is caught before the maker
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-red-covers-scenario
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-wall-red-files", "2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 240000, "turns": null, "usd": 2.9, "basis": ["2026-10-27-wall-red-files", "2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}], "wall_s": 2400, "shape": "narrow", "breadth": "Expect the scenario agent's report contract and one new check after the scenario step, with its test, to move; a guardian shape_or_pitch reopen like stop-decisions would roughly double the forecast."}
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3809, "cache_read": 25547, "cache_write": 17873, "tokens": 21686, "usd": 0.0057, "turns": 3, "wall_s": 21.0, "session": "06786268-c498-45db-8b79-dfcd0760911e", "step": "forecaster", "at": "2026-10-30T00:19:00+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-red-covers-scenario/01-forecaster.out"}]
stops: [{"at": "2026-10-30T00:19:00+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-red-covers-scenario budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~400k tokens / $2.3 and opus ~240k tokens / $2.9 from wall-red-files, stop-decisions and settled-forward; narrow shape, reopen risk named.", "at": "2026-10-30T00:19:00+00:00"}], "forecaster": {"at": "2026-10-30T00:19:00+00:00", "wrote": []}}
---
# A red that leaves part of the scenario untested is caught before the maker

## Scenario

A red that leaves part of the scenario untested is caught before the maker (#64, and candidate 1 of the retro of 2026-10-29).

1. The scenario agent's report names each item the scenario names, with the test that covers it, and each item it did not cover, with why. An item with no test stops the slice for the person who set the work going, before the maker runs. (#64)
2. After the scenario step, a check takes every flag and `xv` command written in backticks in the scenario, amendments included, and lists each one that appears in no red file. Anything listed stops the slice for the person who set the work going, before the maker runs. (retro candidate 1)
3. The check's test case: on the first red of `2026-10-29-stop-decisions`, the check lists `--since`. On that slice's final red, it lists nothing.

## May ignore

An item the scenario names in plain words, without backticks: the agent's list in point 1 covers those, not the check in point 2.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T00:18:39+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T00:19:00+00:00 forecaster: done: Forecast sonnet ~400k tokens / $2.3 and opus ~240k tokens / $2.9 from wall-red-files, stop-decisions and settled-forward; narrow shape, reopen risk named.
- 2026-10-30T00:19:00+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-red-covers-scenario budget ... --by <name>`).

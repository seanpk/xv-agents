---
id: 2026-11-27-changelog-at-merge
title: "A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)"
kind: feature
status: stopped
originator: Sean Kennedy
created: 2026-11-27
branch: xv/2026-11-27-changelog-at-merge
base: dd577e56d4a5315f8bcd44af60e6af600af7bd87
next: forecaster
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 220000, "turns": null, "usd": 1.1, "basis": ["2026-11-25-build-moves", "2026-11-25-failed-step", "2026-11-25-test-remove"]}, {"harness": "claude", "model": "opus", "tokens": 130000, "turns": null, "usd": 1.5, "basis": ["2026-11-25-build-moves", "2026-11-25-failed-step", "2026-11-25-test-remove"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-25-build-moves", "2026-11-25-failed-step", "2026-11-25-test-remove"]}], "wall_s": 900, "rounds": 2, "rounds_reason": "The change edits the red-check stop rule and the inspector brief, the same stops that sent test-remove and removal-line back, so one send-back is likely.", "shape_breadth": "narrow", "shape_note": "One new exemption branch in the red check for slice-only not_covered outcomes, one inspector brief item, and a CHANGELOG line."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4632, "cache_read": 64736, "cache_write": 49065, "tokens": 53703, "usd": 0.0128, "turns": 4, "wall_s": 23.9, "session": "dbc1a28c-34ae-453d-a877-9be47ca61fc2", "step": "forecaster", "at": "2026-11-28T02:23:37+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-27-changelog-at-merge/01-forecaster.out"}]
stops: [{"at": "2026-11-28T02:23:37+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-27-changelog-at-merge budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null, "fired_questions": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast 220k sonnet, 130k opus, 55k haiku tokens over two rounds, 900 s wall, narrow shape; the red-check exemption and inspector brief change reopen risk as in test-remove.", "at": "2026-11-28T02:23:37+00:00"}], "forecaster": {"at": "2026-11-28T02:23:37+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "7b5bd88f50d935567cce3b52d66d8d80f933951d", "ended": true}
---
# A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)

## Scenario

1. The test writer puts an outcome in `not_covered` and names the files it is about in `checks`. All of its `checks` files are in `tests.slice_only_files`. So the red check does not stop with `red_misses_scenario` for that outcome.
2. A `not_covered` outcome whose `checks` names any other file still stops, as it does now. An outcome with no `checks` also still stops.
3. The inspector brief asks the inspector to read each outcome that went through this way, check that the change to the file is right and in the right place, and put that in the inspection report for the person who decides the merge.
4. There is a line in `CHANGELOG.md`.

## May ignore

- The deputation part of #214. The watch merging a slice on its own waits for #159 and #160 in v0.8.
- Slices already open or closed. Their records stay as they are.

## Recording

None. A feature starts from words.

## Log
- 2026-11-28T02:23:06+00:00 watch: slice opened by Sean Kennedy
- 2026-11-28T02:23:37+00:00 forecaster: done: Forecast 220k sonnet, 130k opus, 55k haiku tokens over two rounds, 900 s wall, narrow shape; the red-check exemption and inspector brief change reopen risk as in test-remove.
- 2026-11-28T02:23:37+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-27-changelog-at-merge budget ... --by <name>`).

---
id: 2026-11-24-settled-outcome
title: "A settled not-covered outcome does not stop again (#205)"
kind: defect
status: working
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-settled-outcome
base: 82a218f104bde75596fec4773887dc118aa50337
next: test-writer
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 330000, "turns": null, "usd": 2.2, "basis": ["2026-10-30-covers-list", "2026-11-07-defects-stops", "2026-11-09-defects-tools", "2026-11-24-cleaner-commit"]}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.3, "basis": ["2026-10-30-covers-list", "2026-11-07-defects-stops", "2026-11-09-defects-tools", "2026-11-24-cleaner-commit"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-24-cleaner-commit", "2026-11-20-names", "2026-11-19-removal-line"]}], "wall_s": 1800, "rounds": 2, "rounds_reason": "The record bundles three cases one red pass may miss (wording variants, bundled stops, an unsettled outcome that must still fire), and the nearest basis, covers-list, ran three rounds on the same stop.", "shape_breadth": "narrow", "shape_note": "Expect the change to touch only the red_misses_scenario settled-outcome check, its tests, and one CHANGELOG line."}
budget: {"tokens": 585000, "usd": 4.51, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6957, "cache_read": 64914, "cache_write": 46282, "tokens": 53245, "usd": 0.0134, "turns": 4, "wall_s": 32.4, "session": "39a5e326-038b-40d5-be22-dc0fe08736e3", "step": "forecaster", "at": "2026-11-24T22:25:43+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-settled-outcome/01-forecaster.out"}]
stops: [{"at": "2026-11-24T22:25:43+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-settled-outcome budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Standing answer: accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-24T22:25:54+00:00", "pick": "other", "settled": "Sean sets budget {tokens: 585000, usd: 4.51}, the forecast (narrow); next is test-writer.", "new_info": "none", "cause": "decision: Sean's standing answer accepts a forecast that is not wide", "budget_change": {"from": null, "to": {"tokens": 585000, "usd": 4.51}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast 330k sonnet, 200k opus, 55k haiku tokens; 1800 s wall, 2 rounds, narrow shape.", "at": "2026-11-24T22:25:43+00:00"}], "forecaster": {"at": "2026-11-24T22:25:43+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "a9be0198a85acb7588989d77048e6375f7b4d5e9", "ended": true}
---
# A settled not-covered outcome does not stop again (#205)

## Scenario

A not-covered outcome that a person settled does not stop again on a later test writer pass (#205).

1. A person answers a `red_misses_scenario` stop for outcome N. A later test writer pass lists N in `not_covered` again. No new `red_misses_scenario` fires for N. This holds when the later pass words N or its reason differently, such as "7", "7. A line in CHANGELOG.md" or "7. A line in CHANGELOG.md.".
2. It also holds when the person settled N in the answer to another stop that bundled `red_misses_scenario`, and when that answer sent the slice back.
3. An outcome that no person settled still fires `red_misses_scenario`, on the same pass as a settled one.
4. A line in `CHANGELOG.md`.

## May ignore

an outcome that the scenario amends after the answer

## Recording

.xv/recordings/rec-settled-outcome.md

## Log
- 2026-11-24T22:25:03+00:00 watch: slice opened by Sean Kennedy
- 2026-11-24T22:25:43+00:00 forecaster: done: Forecast 330k sonnet, 200k opus, 55k haiku tokens; 1800 s wall, 2 rounds, narrow shape.
- 2026-11-24T22:25:43+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-settled-outcome budget ... --by <name>`).
- 2026-11-24T22:25:54+00:00 Sean Kennedy: set budget
- 2026-11-24T22:25:54+00:00 Sean Kennedy: answered budget_not_set: Standing answer: accept the forecast unless it is wide
- 2026-11-24T22:25:54+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy

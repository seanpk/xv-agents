---
id: 2026-11-09-retro-fixes
title: "Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-retro-fixes
base: 4f6dcb707076f9b7a130b27302e6cafdd92e73e1
next: forecaster
build: none
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.5, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops", "2026-10-27-retro-accept-fields"], "note": "Basis actuals 236k-409k tokens (median ~317k), $1.28-$2.48. Bumped for seven scenario items across three tool areas against one tool fix in defects-tools. Guide has no turn column, so turns are null. Reopen rounds are not priced: basis rows that reopened ran 2-3x."}, {"harness": "claude", "model": "opus", "tokens": 230000, "turns": null, "usd": 2.9, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops", "2026-10-27-retro-accept-fields"], "note": "Basis actuals 177k-237k tokens (median ~203k), $2.14-$3.15. Guardian checks seven items, so a small bump. Guardian reopen passes are not priced."}], "wall_s": 1500, "shape": "narrow", "breadth": "Changes the unrecorded-move check (build-added tests), the record move --slice-only marker, the red_misses_scenario dedupe on the stop path, and the scenario brief plus CHANGELOG. No new state or stop kinds, but three tool areas are touched."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4001, "cache_read": 61830, "cache_write": 37716, "tokens": 41723, "usd": 0.0102, "turns": 4, "wall_s": 19.6, "session": "ef51eb6d-b7d7-470d-bdb9-4ba8b88932cb", "step": "forecaster", "at": "2026-11-09T16:28:59+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-09-retro-fixes/01-forecaster.out"}]
stops: [{"at": "2026-11-09T16:28:59+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-retro-fixes budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~400k tokens and claude/opus ~230k tokens from the defect rows, with reopen risk not priced; the shape is narrow.", "at": "2026-11-09T16:28:59+00:00"}], "forecaster": {"at": "2026-11-09T16:28:59+00:00", "wrote": []}}
---
# Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled

## Scenario

1. On a slice from a build, a test file that the build only added tests to (no line at the base changed or removed) is not an unrecorded move: `unrecorded_move` does not fire for it, and the wall's `unrecorded` list does not name it. (#172)
2. On a slice from a build, a test file in which the build changed or removed a line at the base still stops with `unrecorded_move`. (#172)
3. `xv record move --slice-only` on a test that is not in the record's `slice_only` list marks the move `slice_only: true`. (#173)
4. After the scenario step, a `not_covered` item that a person already answered at an earlier `red_misses_scenario` stop does not fire `red_misses_scenario` again on a later pass. A new `not_covered` item still fires. (#174)
5. The scenario brief says that on a slice from a build, a red test that fails only on the build is expected: the agent reports it and does not stop to ask. (#174)
6. The scenario brief says to run the red command in the foreground, to its end, before writing the report. (#174)
7. `CHANGELOG.md` has a line for the brief change and the tool changes.

## May ignore

Other files under the test paths that are not tests, such as tests/run.py; they still count as test files.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T16:28:25+00:00 watch: slice opened by Sean Kennedy
- 2026-11-09T16:28:59+00:00 forecaster: done: Forecast claude/sonnet ~400k tokens and claude/opus ~230k tokens from the defect rows, with reopen risk not priced; the shape is narrow.
- 2026-11-09T16:28:59+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-retro-fixes budget ... --by <name>`).

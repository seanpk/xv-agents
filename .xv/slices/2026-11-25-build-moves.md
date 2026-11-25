---
id: 2026-11-25-build-moves
title: "In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-build-moves
base: 84f20f5eb0c66ecb9426f6f63ce0074847a0d3be
next: test-writer
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 2.2, "basis": ["2026-11-24-cleaner-commit", "2026-11-18-move-names", "2026-11-19-removal-line"], "note": "Covers test-writer, maker and cleaner. Median of basis rows about 333k tokens and $2.13; one send-back allowance added. Guide has no turns column."}, {"harness": "claude", "model": "opus", "tokens": 180000, "turns": null, "usd": 2.2, "basis": ["2026-11-24-cleaner-commit", "2026-11-18-move-names", "2026-11-19-removal-line", "2026-11-24-settled-outcome"], "note": "Inspector only. Median of basis rows about 175k tokens and $2.2. Guide has no turns column."}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-24-cleaner-commit", "2026-11-24-settled-outcome", "2026-11-19-removal-line"], "note": "Forecaster's own spend. Basis rows ran 50k to 55k. The guide has grown, so each read costs more; not priced in. Guide has no turns column."}], "wall_s": 900, "rounds": 2, "rounds_reason": "The change sits on the unrecorded_move path that move-names and removal-line reopened, and its five scenario points include edge cases (a file in both lists, a recorded move excluded) that the inspector tends to send back once.", "shape_breadth": "narrow", "shape_note": "Expect the change in the test writer's stop computation, its tests, and one CHANGELOG line."}
budget: {"tokens": 585000, "usd": 4.41, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5401, "cache_read": 64875, "cache_write": 46927, "tokens": 52334, "usd": 0.0127, "turns": 4, "wall_s": 24.9, "session": "31f35370-d7a7-418c-9a21-981fe9c667df", "step": "forecaster", "at": "2026-11-25T05:01:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-25-build-moves/01-forecaster.out"}]
stops: [{"at": "2026-11-25T05:01:42+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-build-moves budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Standing answer: accept the forecast unless it is wide", "also": [], "fired_questions": [], "answered_at": "2026-11-25T05:01:51+00:00", "pick": "other", "settled": "Sean sets budget {tokens: 585000, usd: 4.41}, the forecast (narrow); next is test-writer.", "new_info": "none", "cause": "decision: Sean's standing answer accepts a forecast that is not wide"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect: sonnet 350k tokens/$2.2, opus 180k tokens/$2.2, haiku 55k tokens; wall 900 s over 2 rounds.", "at": "2026-11-25T05:01:42+00:00"}], "forecaster": {"at": "2026-11-25T05:01:42+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "e326ad529f653d889e537e72f7612df392abcc5f", "ended": true}
---
# In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210)

## Scenario

In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210).

1. In a slice from a build (`xv slice new --from <ref>`), when the build changed or removed old tests in files that existed at the base, the test writer step still stops with `unrecorded_move` for a person. The question says those files were changed by the build, not the test writer.
2. The question lists the test writer's own changes to old test files apart from the build's. A file that both changed is in both lists.
3. A file with a recorded move (`xv record move`) is not in the stop, whether the build or the test writer changed it.
4. A slice with no build, or a build that changed no old test, stops as it does today.
5. A line in `CHANGELOG.md`.

## May ignore

A way to accept all of the build's moves with one command

## Recording

.xv/recordings/rec-build-moves.md

## Log
- 2026-11-25T05:01:12+00:00 watch: slice opened by Sean Kennedy
- 2026-11-25T05:01:42+00:00 forecaster: done: Narrow defect: sonnet 350k tokens/$2.2, opus 180k tokens/$2.2, haiku 55k tokens; wall 900 s over 2 rounds.
- 2026-11-25T05:01:42+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-build-moves budget ... --by <name>`).
- 2026-11-25T05:01:51+00:00 Sean Kennedy: answered budget_not_set: Standing answer: accept the forecast unless it is wide
- 2026-11-25T05:01:51+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-25T05:01:51+00:00 Sean Kennedy: set budget

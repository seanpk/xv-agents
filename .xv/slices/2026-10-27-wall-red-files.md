---
id: 2026-10-27-wall-red-files
title: The wall sees old tests in a red file
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-wall-red-files
base: 23f8dd53788ee9f656f572e730e497e3b0a298bc
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 250000, "turns": null, "usd": 1.42, "basis": ["2026-10-27-red-joins", "2026-10-27-retro-accept-fields", "2026-10-27-slice-tests"], "note": "Mean of the three basis rows' sonnet actuals (235k, 236k, 283k tokens; $1.32, $1.28, $1.67). The guide has no turns column, so turns stay null. All three basis slices ran multiple rounds, so this figure already includes reopen cost. A clean single pass ran 53k to 158k sonnet tokens (package-imports, allowed-commands), so the low end is a clean pass and the high end a reopen."}, {"harness": "claude", "model": "opus", "tokens": 190000, "turns": null, "usd": 2.27, "basis": ["2026-10-27-red-joins", "2026-10-27-retro-accept-fields", "2026-10-27-slice-tests"], "note": "Mean of the three basis rows' opus actuals (176k, 192k, 205k tokens; $2.04, $2.29, $2.49). Each guardian pass costs about $0.70 to $0.90, so a reopen adds a full pass in dollars."}], "wall_s": 1750, "shape": "narrow", "breadth": "Changes the red-file coverage rule in scripts/wall.py check_against_base (red files that existed at base are covered only for added tests), with its tests under tests/** and a CHANGELOG line; recording, moves, and other checks should not move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3565, "cache_read": 25216, "cache_write": 14925, "tokens": 18494, "usd": 0.005, "turns": 3, "wall_s": 19.5, "session": "4b35f203-b638-4fbf-b4b7-f17120043695", "step": "forecaster", "at": "2026-10-27T21:28:05+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-wall-red-files/01-forecaster.out"}]
stops: [{"at": "2026-10-27T21:28:05+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-wall-red-files budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~250k tokens and opus ~190k tokens from three defect rows in the same wall/red area; wall ~1750 s; shape narrow.", "at": "2026-10-27T21:28:05+00:00"}], "forecaster": {"at": "2026-10-27T21:28:05+00:00", "wrote": []}}
---
# The wall sees old tests in a red file

## Scenario

The wall sees old tests in a red file. Today a file on `red.files` is covered whole (`scripts/wall.py`, `check_against_base`: `covered |= red | recorded`), so an old test in it can be changed or deleted and the wall reports nothing. Since #17 the scenario agent puts new tests in the existing test file, so most red files now hold old tests. After the fix, for a red file that existed at the base, only the tests the slice added are the red. Every test and assertion that was in the file at the base must still be there, unchanged, at HEAD, unless a recorded move (`xv record move`) names that file; otherwise the file is `unrecorded`, in the CI form (`xv wall check --base`) as in the slice's own check. A red file that is new in the slice is covered whole, as today. Take `tests/test_store.py`, present at the base with `test_expiry` asserting `30`: the slice adds `test_renewal` and makes it the red. Adding `test_renewal` passes the wall. Changing `test_expiry`'s `30` to `31`, or deleting `test_expiry`, without a recorded move, fails it. This changes a check; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#53)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T21:27:46+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T21:28:05+00:00 forecaster: done: Forecast sonnet ~250k tokens and opus ~190k tokens from three defect rows in the same wall/red area; wall ~1750 s; shape narrow.
- 2026-10-27T21:28:05+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-wall-red-files budget ... --by <name>`).

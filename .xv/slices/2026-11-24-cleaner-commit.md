---
id: 2026-11-24-cleaner-commit
title: "The watch commits the cleaner's work, as it does the maker's (#206)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-cleaner-commit
base: d4011e47fc52d2c5fbf8fdb6b80f6e0543cbf462
next: forecaster
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 2.3, "basis": ["2026-11-19-wall-keep", "2026-11-18-move-names", "2026-11-19-removal-line", "2026-11-20-names"]}, {"harness": "claude", "model": "opus", "tokens": 170000, "turns": null, "usd": 2.2, "basis": ["2026-11-18-move-names", "2026-11-19-removal-line", "2026-11-16-red-lands", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-20-names", "2026-11-19-removal-line", "2026-11-19-wall-keep", "2026-11-19-pick-tests"]}], "wall_s": 1400, "rounds": 2, "rounds_reason": "The commit move changes what the cleaner leaves behind, and the inspector sent narrow defects back once in move-names and removal-line; wall-keep is the one-pass floor.", "shape_breadth": "narrow", "shape_note": "Touches the watch's commit step, the cleaner brief, docs, one new decision row and one CHANGELOG line; the agent set does not change."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6267, "cache_read": 63278, "cache_write": 47748, "tokens": 54021, "usd": 0.0133, "turns": 4, "wall_s": 29.6, "session": "dbe8d650-3916-4ccc-9ddd-96c658aebb5a", "step": "forecaster", "at": "2026-11-24T14:03:05+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-cleaner-commit/01-forecaster.out"}]
stops: [{"at": "2026-11-24T14:03:05+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-cleaner-commit budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Defect, narrow: about 350k sonnet and 170k opus tokens over two rounds, $4.5 total, 1400 s wall, with a send-back as the main risk.", "at": "2026-11-24T14:03:05+00:00"}], "forecaster": {"at": "2026-11-24T14:03:05+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "af8d278efcd63a24f59e5faf7fe13e7775967eb9", "ended": true}
---
# The watch commits the cleaner's work, as it does the maker's (#206)

## Scenario

The watch commits the cleaner's work, as it does the maker's (#206).

1. The cleaner's brief says to leave its changes uncommitted: the watch commits them after its checks. Its may-not list has "Commit, merge, or push", as the maker's does.
2. The cleaner still records each test move with `xv record move` before its step ends. The brief no longer says the pre-commit hook refuses a move with no record; it says the wall check after the step stops on one.
3. `cleaner_commit` in the record names the commit `xv step` makes after the cleaner (`xv(<id>): record the cleaner's pass`), and stays empty when the cleaner changed nothing. The brief's report has no `commit` field; a report that still sends one is not refused.
4. README, the docs and the picture no longer say the cleaner commits. A new numbered decision in `docs/decisions.md` says the watch commits each step's work; decision 7 stays as history.
5. A line in `CHANGELOG.md`.

## May ignore

old records where cleaner_commit is empty; harnesses with no allow-list

## Recording

None. A feature starts from words.

## Log
- 2026-11-24T14:02:29+00:00 watch: slice opened by Sean Kennedy
- 2026-11-24T14:03:05+00:00 forecaster: done: Defect, narrow: about 350k sonnet and 170k opus tokens over two rounds, $4.5 total, 1400 s wall, with a send-back as the main risk.
- 2026-11-24T14:03:05+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-cleaner-commit budget ... --by <name>`).

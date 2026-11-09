---
id: 2026-11-09-errored-spend
title: "An errored prototype variant keeps its spend, and a gone worktree says so"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-errored-spend
base: 4f6dcb707076f9b7a130b27302e6cafdd92e73e1
next: forecaster
build: {"kind": "exploration", "ref": "explore/errored-spend", "commit": "c7205f151b64e47a26b88afec54acfbdc3e4942d"}
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 370000, "turns": null, "usd": 2.5, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops"]}, {"harness": "claude", "model": "opus", "tokens": 230000, "turns": null, "usd": 2.8, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops"]}], "wall_s": 1400, "shape": "narrow", "breadth": "Two small changes: the errored prototype variant's spend recording and the missing-worktree message. No new commands or surfaces, but the spend path is near prototype budgets, which reopened three times in its own slice; no reopen is priced."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 3048, "cache_read": 61543, "cache_write": 37375, "tokens": 40429, "usd": 0.0096, "turns": 4, "wall_s": 15.3, "session": "7f8e5c0e-f202-4c06-8492-d35647251e42", "step": "forecaster", "at": "2026-11-09T16:28:55+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-09-errored-spend/01-forecaster.out"}]
stops: [{"at": "2026-11-09T16:28:55+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-errored-spend budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast narrow defect on claude/sonnet and claude/opus from two narrow defect rows; haiku not used.", "at": "2026-11-09T16:28:55+00:00"}], "forecaster": {"at": "2026-11-09T16:28:55+00:00", "wrote": []}}
---
# An errored prototype variant keeps its spend, and a gone worktree says so

## Scenario

1. A prototype variant whose agent ran and then errored keeps that run's spend in the record, and the spend counts against that variant's prototype budget, so a second `xv prototype start` gives it only what is left. (#121)
2. A variant whose working folder is gone reports that the working folder is missing, not "agent CLI not found". (#121)

## May ignore

- A timeout, which does not raise and is unchanged.
- A harness that reports no spend.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T16:28:25+00:00 watch: slice opened by Sean Kennedy
- 2026-11-09T16:28:55+00:00 forecaster: done: Forecast narrow defect on claude/sonnet and claude/opus from two narrow defect rows; haiku not used.
- 2026-11-09T16:28:55+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-errored-spend budget ... --by <name>`).

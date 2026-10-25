---
id: 2026-10-25-diff-count
title: "diff_growing counts only the maker's files"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-diff-count
base: f452d430f44f6c01e611f705f5b709b80231291b
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 697000, "turns": null, "usd": 0.48, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"]}, {"harness": "claude", "model": "opus", "tokens": 448000, "turns": null, "usd": 0.59, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"]}], "wall_s": 300, "shape": "narrow", "breadth": "One filter in diff_lines to count .xv/ files as the guardian writes them, plus a test in tests/**; no other moving parts expected."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3007, "cache_read": 25016, "cache_write": 5536, "tokens": 33563, "usd": 0.0029, "turns": 3, "wall_s": 15.3, "session": "f44c0fb9-064b-49a7-abe0-9d5b744bbea1", "step": "forecaster", "at": "2026-10-25T04:26:13+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-diff-count/01-forecaster.out"}]
stops: [{"at": "2026-10-25T04:26:13+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-diff-count budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from two prior claude/sonnet and two claude/opus rows: about 697k sonnet tokens and 448k opus tokens, 300 s wall, narrow shape.", "at": "2026-10-25T04:26:13+00:00"}], "forecaster": {"at": "2026-10-25T04:26:13+00:00", "wrote": []}}
---
# diff_growing counts only the maker's files

## Scenario

`diff_lines`, which the `diff_growing` stop and `limits.max_diff_lines` read after the maker and the cleaner, counts only files outside `.xv/`. A packet or boundary file the guardian writes between two maker runs does not make the diff look like it grew. (seanpk/xv-agents#24)

## May ignore

max_diff_lines semantics beyond excluding .xv/

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T04:26:13+00:00 forecaster: done: Forecast from two prior claude/sonnet and two claude/opus rows: about 697k sonnet tokens and 448k opus tokens, 300 s wall, narrow shape.
- 2026-10-25T04:26:13+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-diff-count budget ... --by <name>`).

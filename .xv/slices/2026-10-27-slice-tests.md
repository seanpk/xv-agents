---
id: 2026-10-27-slice-tests
title: Tests a slice leaves behind fit the layout and do not go stale
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-slice-tests
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 1400000, "turns": null, "usd": 1.0, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-diff-count"], "note": "Reopen case priced from init-tries-guesses (1,443,243 tokens); diff-count (482,167) is the one-pass floor. Turns not in guide."}, {"harness": "claude", "model": "opus", "tokens": 1100000, "turns": null, "usd": 1.5, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-suite-red-quote"], "note": "Guardian reopen case from init-tries-guesses (1,122,664) and suite-red-quote (1,066,773). Turns not in guide."}], "wall_s": 900, "shape": "wide", "breadth": "Scenario brief (skills/scenario/SKILL.md step 6), scenario report marking tests, close output listing removals for approval, and xv record move updating red.files and red.command."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 6005, "cache_read": 25011, "cache_write": 9950, "tokens": 15959, "usd": 0.0052, "turns": 3, "wall_s": 30.9, "session": "36d90533-6ff7-4424-9ccf-171e2de66a85", "step": "forecaster", "at": "2026-10-27T13:31:32+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-slice-tests/01-forecaster.out"}]
stops: [{"at": "2026-10-27T13:31:32+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-slice-tests budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from claude/sonnet and claude/opus rows: about 1.4M sonnet and 1.1M opus tokens, reopen case priced; wide shape across brief, scenario report, close output, and record move.", "at": "2026-10-27T13:31:32+00:00"}], "forecaster": {"at": "2026-10-27T13:31:32+00:00", "wrote": []}}
---
# Tests a slice leaves behind fit the layout and do not go stale

## Scenario

Tests a slice leaves behind fit the test layout and do not go stale. (1) The scenario brief asks for new tests in the existing test file for the code under test, and a new file only when none exists (`skills/scenario/SKILL.md` step 6 says the opposite today). (2) The scenario agent marks each test that only proves the slice did its job and has no value after it (for example, "this file is `.ts`, not `.js`"). Its report names them, and the record keeps the list. At close, the close output lists them for the person who set the work going, who approves each removal; a removal is a recorded move. Nothing is removed without that approval. (3) When a recorded move (`xv record move`) moves or deletes a file that `red.files` names, the record's `red.files` and `red.command` are updated to match, so the guardian and the "watch the first green run" line do not point at a deleted file. (seanpk/xv-agents#17; Sean approves the brief change, solo.)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T13:30:58+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T13:31:32+00:00 forecaster: done: Forecast from claude/sonnet and claude/opus rows: about 1.4M sonnet and 1.1M opus tokens, reopen case priced; wide shape across brief, scenario report, close output, and record move.
- 2026-10-27T13:31:32+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-slice-tests budget ... --by <name>`).

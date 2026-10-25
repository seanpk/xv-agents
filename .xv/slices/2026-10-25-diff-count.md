---
id: 2026-10-25-diff-count
title: "diff_growing counts only the maker's files"
kind: defect
status: working
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-diff-count
base: f452d430f44f6c01e611f705f5b709b80231291b
next: cleaner
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 697000, "turns": null, "usd": 0.48, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"]}, {"harness": "claude", "model": "opus", "tokens": 448000, "turns": null, "usd": 0.59, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"]}], "wall_s": 300, "shape": "narrow", "breadth": "One filter in diff_lines to count .xv/ files as the guardian writes them, plus a test in tests/**; no other moving parts expected."}
budget: {"tokens": 1500000, "usd": 5, "turns": 60, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_diff_count.py"], "command": "cd tests && python3 -m unittest test_diff_count", "failure": "AssertionError: 276 != 12", "watch_first_green": null}
wall_baseline: {"commit": "dbd543ea3aa14b1b97d37fdd513183cf2e3359e7", "count": 26, "digest": "8092110916631787", "file": ".xv/slices/2026-10-25-diff-count.wall.json"}
moved_tests: []
suite: green
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3007, "cache_read": 25016, "cache_write": 5536, "tokens": 33563, "usd": 0.0029, "turns": 3, "wall_s": 15.3, "session": "f44c0fb9-064b-49a7-abe0-9d5b744bbea1", "step": "forecaster", "at": "2026-10-25T04:26:13+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-diff-count/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 4897, "cache_read": 184762, "cache_write": 26464, "tokens": 216139, "usd": 0.1733, "turns": 10, "wall_s": 42.1, "session": "aad56772-ac4a-4d26-96c9-10a8e64d662a", "step": "scenario", "at": "2026-10-25T04:26:55+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-diff-count/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 18, "tokens_out": 1457, "cache_read": 165432, "cache_write": 11967, "tokens": 178874, "usd": 0.079, "turns": 12, "wall_s": 93.1, "session": "1a97f008-7516-49b1-badb-9c1a0a6a549e", "step": "maker", "at": "2026-10-25T04:28:35+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-diff-count/03-maker.out"}]
stops: [{"at": "2026-10-25T04:26:13+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-diff-count budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "yes, run them (the same budget as before: 1,500,000 tokens, $5, 60 turns)", "also": [], "answered_at": "2026-10-25T04:26:13+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from two prior claude/sonnet and two claude/opus rows: about 697k sonnet tokens and 448k opus tokens, 300 s wall, narrow shape.", "at": "2026-10-25T04:26:13+00:00"}, {"agent": "scenario", "status": "red", "summary": "diff_lines counts .xv/ files (record, packet): 75 and 276 where 12 is expected for the maker's and scenario's files outside .xv/", "at": "2026-10-25T04:26:55+00:00"}, {"agent": "maker", "status": "green", "summary": "diff_lines numstat in scripts/run.py excludes .xv/ via a git pathspec", "at": "2026-10-25T04:28:35+00:00"}], "forecaster": {"at": "2026-10-25T04:26:13+00:00", "wrote": []}, "scenario": {"at": "2026-10-25T04:26:55+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "========================================================\nFAIL: test_diff_lines_leaves_out_what_the_record_writes_under_xv (test_diff_count.DiffCountTest.test_diff_lines_leaves_out_what_the_record_writes_under_xv)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-25-diff-count/tests/test_diff_count.py\", line 35, in test_diff_lines_leaves_out_what_the_record_writes_under_xv\n    self.assertEqual(self.record()[\"checks\"][\"maker\"][\"diff_lines\"], OUTSIDE_XV)\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 75 != 12\n\n----------------------------------------------------------------------\nRan 2 tests in 6.797s\n\nFAILED (failures=2)\n"}, "maker": {"at": "2026-10-25T04:28:35+00:00", "protected_changed": [], "suite": "green", "suite_output": "ts/test_wall.py:30: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-g4y2x99v/repo/.xv/worktrees/s1/tests/test_store.py' mode='r' encoding='utf-8'>\n  write(path, open(path).read().replace('(\"bread\", 0)', \"anything\"))\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-25-diff-count/tests/test_wall.py:60: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-f77mie6j/repo/.xv/worktrees/s1/tests/test_store.py' mode='r' encoding='utf-8'>\n  write(path, open(path).read().replace('(\"bread\", 0)', \"anything\"))\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n----------------------------------------------------------------------\nRan 128 tests in 31.652s\n\nOK\n", "failing": [], "failing_history": [[]], "diff_lines": 162, "diff_history": [162], "wall": {"slice": "2026-10-25-diff-count", "baseline": "dbd543ea3aa14b1b97d37fdd513183cf2e3359e7", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}}}
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
- 2026-10-25T04:26:13+00:00 Sean Kennedy: set budget
- 2026-10-25T04:26:13+00:00 Sean Kennedy: answered budget_not_set: yes, run them (the same budget as before: 1,500,000 tokens, $5, 60 turns)
- 2026-10-25T04:26:55+00:00 scenario: red: diff_lines counts .xv/ files (record, packet): 75 and 276 where 12 is expected for the maker's and scenario's files outside .xv/
- 2026-10-25T04:28:35+00:00 maker: green: diff_lines numstat in scripts/run.py excludes .xv/ via a git pathspec

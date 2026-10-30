---
id: 2026-10-29-red-covers-scenario
title: A red that leaves part of the scenario untested is caught before the maker
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-red-covers-scenario
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-wall-red-files", "2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 240000, "turns": null, "usd": 2.9, "basis": ["2026-10-27-wall-red-files", "2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}], "wall_s": 2400, "shape": "narrow", "breadth": "Expect the scenario agent's report contract and one new check after the scenario step, with its test, to move; a guardian shape_or_pitch reopen like stop-decisions would roughly double the forecast."}
budget: {"tokens": 900000, "usd": 7, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_check.py", "tests/test_run.py"], "command": "cd tests && python3 -m unittest test_check test_run", "failure": "AttributeError: module 'check' has no attribute 'red_gaps' (RedGapsTest.test_on_the_first_red_of_stop_decisions_the_check_lists_since); FAIL: test_a_flag_in_backticks_that_no_red_file_has_stops_before_the_maker", "watch_first_green": null}
wall_baseline: {"commit": "c01fddc13350b29cca0e24fec709062cd089f038", "count": 53, "digest": "278cee5e210cd29b", "file": ".xv/slices/2026-10-29-red-covers-scenario.wall.json"}
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3809, "cache_read": 25547, "cache_write": 17873, "tokens": 21686, "usd": 0.0057, "turns": 3, "wall_s": 21.0, "session": "06786268-c498-45db-8b79-dfcd0760911e", "step": "forecaster", "at": "2026-10-30T00:19:00+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-red-covers-scenario/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 48, "tokens_out": 16215, "cache_read": 1367481, "cache_write": 71574, "tokens": 87837, "usd": 0.5853, "turns": 27, "wall_s": 162.4, "session": "64b217ea-e63c-47a5-b7f4-2276bf6f11eb", "step": "scenario", "at": "2026-10-30T00:23:49+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-red-covers-scenario/02-scenario.out"}]
stops: [{"at": "2026-10-30T00:19:00+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-red-covers-scenario budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "$7 and 900K tokens", "settles": "The budget is $7 and 900K tokens: the forecast plus room for one send-back.", "amends": false}, {"text": "$5.20 and 640K tokens, the forecast", "settles": "The budget is $5.20 and 640K tokens, as forecast.", "amends": false}, {"text": "$10 and 1.25M tokens", "settles": "The budget is $10 and 1.25M tokens: room for several send-backs, as on the stop-decisions slice.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T00:21:06+00:00", "pick": 1, "settled": "The budget is $7 and 900K tokens: the forecast plus room for one send-back.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 900000, "usd": 7}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~400k tokens / $2.3 and opus ~240k tokens / $2.9 from wall-red-files, stop-decisions and settled-forward; narrow shape, reopen risk named.", "at": "2026-10-30T00:19:00+00:00"}, {"agent": "scenario", "status": "red", "summary": "Tests for the coverage check (check.red_gaps, the stop after the scenario step, the covers/not_covered report fields and brief) and the stop-decisions first/final red case; 14 fail", "at": "2026-10-30T00:23:49+00:00"}], "forecaster": {"at": "2026-10-30T00:19:00+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T00:23:49+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "s_that_no_red_file_has_stops_before_the_maker\n    self.assert_stopped_before_the_maker(self.scenario_with_env(), \"xv ghost\")\n    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-29-red-covers-scenario/tests/test_run.py\", line 197, in assert_stopped_before_the_maker\n    self.assertEqual(p.returncode, 10, p.stdout + p.stderr)\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 0 != 10 : {\n  \"slice\": \"s1\",\n  \"after\": \"scenario\",\n  \"stop\": null,\n  \"fired\": [],\n  \"record\": \".xv/slices/s1.md\",\n  \"worktree\": \"/tmp/xv-test-cdpyzjpz/repo/.xv/worktrees/s1\"\n}\n\n\n----------------------------------------------------------------------\nRan 59 tests in 24.455s\n\nFAILED (failures=5, errors=9)\n", "old_red_changed": []}}
---
# A red that leaves part of the scenario untested is caught before the maker

## Scenario

A red that leaves part of the scenario untested is caught before the maker (#64, and candidate 1 of the retro of 2026-10-29).

1. The scenario agent's report names each item the scenario names, with the test that covers it, and each item it did not cover, with why. An item with no test stops the slice for the person who set the work going, before the maker runs. (#64)
2. After the scenario step, a check takes every flag and `xv` command written in backticks in the scenario, amendments included, and lists each one that appears in no red file. Anything listed stops the slice for the person who set the work going, before the maker runs. (retro candidate 1)
3. The check's test case: on the first red of `2026-10-29-stop-decisions`, the check lists `--since`. On that slice's final red, it lists nothing.

## May ignore

An item the scenario names in plain words, without backticks: the agent's list in point 1 covers those, not the check in point 2.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T00:18:39+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T00:19:00+00:00 forecaster: done: Forecast sonnet ~400k tokens / $2.3 and opus ~240k tokens / $2.9 from wall-red-files, stop-decisions and settled-forward; narrow shape, reopen risk named.
- 2026-10-30T00:19:00+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-red-covers-scenario budget ... --by <name>`).
- 2026-10-30T00:19:05+00:00 watch: offered 3 options for budget_not_set
- 2026-10-30T00:21:06+00:00 Sean Kennedy: set budget
- 2026-10-30T00:21:06+00:00 Sean Kennedy: answered budget_not_set: 1
- 2026-10-30T00:21:06+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-30T00:23:49+00:00 scenario: red: Tests for the coverage check (check.red_gaps, the stop after the scenario step, the covers/not_covered report fields and brief) and the stop-decisions first/final red case; 14 fail

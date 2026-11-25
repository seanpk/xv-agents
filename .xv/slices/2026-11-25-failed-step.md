---
id: 2026-11-25-failed-step
title: "A failed step marks its start ended, so a later move reads HEAD (#202)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-failed-step
base: ae7929481b166143489f51e6194aaf375eca7bb6
next: test-writer
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 170000, "turns": null, "usd": 1.0, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "opus", "tokens": 90000, "turns": null, "usd": 1.0, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-19-wall-keep"]}], "wall_s": 525, "rounds": 1, "rounds_reason": "Recent narrow defects of this shape each ran one pass per agent; a CHANGELOG-line question is the only stop likely to cost a round.", "shape_breadth": "narrow", "shape_note": "Expect the failed-step branch that marks step_start ended and the slice-only move's start reading to change, with one test and the CHANGELOG line."}
budget: {"tokens": 315000, "usd": 2.01, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_record.py"], "command": "cd tests && python3 -m unittest test_record.FailedStepEndsItsStartTest", "failure": "AssertionError: None is not True (step_start has no 'ended'); and: tests/test_x.py has 1 lines as it was when the step began: no line 5", "watch_before_merge": null}
wall_baseline: {"commit": "062f22e8c6f3bed540b9e9bf37e240f7c7e7f5df", "count": 104, "digest": "52ff03b9e3a178b8", "file": ".xv/slices/2026-11-25-failed-step.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5756, "cache_read": 62836, "cache_write": 49257, "tokens": 55019, "usd": 0.0134, "turns": 4, "wall_s": 27.3, "session": "2a94b75f-f181-44e7-a274-e1c75b60956f", "step": "forecaster", "at": "2026-11-25T19:14:47+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-25-failed-step/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 24, "tokens_out": 4329, "cache_read": 375346, "cache_write": 39222, "tokens": 43575, "usd": 0.2378, "turns": 13, "wall_s": 31.7, "session": "fc9dc921-c56e-438d-9f01-03064121c6e0", "step": "test-writer", "at": "2026-11-25T19:15:36+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-25-failed-step/02-test-writer.out"}]
stops: [{"at": "2026-11-25T19:14:47+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-failed-step budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Standing answer: accept the forecast unless it is wide", "also": [], "fired_questions": [], "answered_at": "2026-11-25T19:15:00+00:00", "pick": "other", "settled": "The budget is the forecast: 315,000 tokens and $2.01; the forecast was narrow", "new_info": "none", "cause": "decision: the budget is set from the forecast"}, {"at": "2026-11-25T19:15:37+00:00", "step": "test-writer", "order": "red_misses_scenario", "seat": "originator", "question": "The test writer did not cover 3. There is a CHANGELOG line.: A CHANGELOG line is a one-time wording change, so a test of it would be slice-only; it is left to the maker and the inspector.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 315000, "usd": 2.01, "set_by": "Sean Kennedy"}, "fired_questions": ["The test writer did not cover 3. There is a CHANGELOG line.: A CHANGELOG line is a one-time wording change, so a test of it would be slice-only; it is left to the maker and the inspector."]}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect, one pass expected: sonnet ~170k tokens, opus ~90k, haiku ~55k, about 525 s wall, 1 round.", "at": "2026-11-25T19:14:47+00:00"}, {"agent": "test-writer", "status": "red", "summary": "A failed step (agent CLI missing) leaves step_start un-ended, so a later slice-only move reads the failed step's start instead of HEAD.", "at": "2026-11-25T19:15:36+00:00"}], "forecaster": {"at": "2026-11-25T19:14:47+00:00", "wrote": [], "removal_not_made": []}, "test-writer": {"at": "2026-11-25T19:15:36+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "tep began: no line 5\n\n\n======================================================================\nFAIL: test_a_step_that_could_not_run_marks_its_start_ended (test_record.FailedStepEndsItsStartTest.test_a_step_that_could_not_run_marks_its_start_ended)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-25-failed-step/tests/test_record.py\", line 485, in test_a_step_that_could_not_run_marks_its_start_ended\n    self.assertIs(self.show()[\"step_start\"].get(\"ended\"), True)\n    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: None is not True\n\n----------------------------------------------------------------------\nRan 2 tests in 0.488s\n\nFAILED (failures=2)\n", "old_red_changed": [], "red_gaps": [], "covered_kept": [{"outcome": "1", "test": ["FailedStepEndsItsStartTest.test_a_step_that_could_not_run_marks_its_start_ended"]}, {"outcome": "2", "test": ["FailedStepEndsItsStartTest.test_a_slice_only_move_after_a_failed_step_reads_its_line_from_head"]}], "unreadable": [], "not_covered": [{"outcome": "3. There is a CHANGELOG line.", "why": "A CHANGELOG line is a one-time wording change, so a test of it would be slice-only; it is left to the maker and the inspector."}], "missed_outcomes": [], "removal_not_made": []}}
step_start: {"agent": "test-writer", "commit": "062f22e8c6f3bed540b9e9bf37e240f7c7e7f5df", "ended": true}
old_tests_to_move: []
may_not_files_needed: []
---
# A failed step marks its start ended, so a later move reads HEAD (#202)

## Scenario

When `xv step` fails because the agent could not run (the agent CLI is missing, or the worktree is gone), the record's `step_start` is marked ended, as it is after a step that ran (1).
A slice-only move recorded after that failed step reads its line from `HEAD`, not from the failed step's start (2).
There is a CHANGELOG line (3).

## May ignore

a step that fails after the agent ran

## Recording

None. A feature starts from words.

## Log
- 2026-11-25T19:14:16+00:00 watch: slice opened by Sean Kennedy
- 2026-11-25T19:14:47+00:00 forecaster: done: Narrow defect, one pass expected: sonnet ~170k tokens, opus ~90k, haiku ~55k, about 525 s wall, 1 round.
- 2026-11-25T19:14:47+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-failed-step budget ... --by <name>`).
- 2026-11-25T19:15:00+00:00 Sean Kennedy: answered budget_not_set: Standing answer: accept the forecast unless it is wide
- 2026-11-25T19:15:00+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-25T19:15:00+00:00 Sean Kennedy: set budget
- 2026-11-25T19:15:36+00:00 test-writer: red: A failed step (agent CLI missing) leaves step_start un-ended, so a later slice-only move reads the failed step's start instead of HEAD.
- 2026-11-25T19:15:37+00:00 watch: stop (red_misses_scenario) for originator: The test writer did not cover 3. There is a CHANGELOG line.: A CHANGELOG line is a one-time wording change, so a test of it would be slice-only; it is left to the maker and the inspector.

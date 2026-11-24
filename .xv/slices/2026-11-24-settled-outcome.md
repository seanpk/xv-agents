---
id: 2026-11-24-settled-outcome
title: "A settled not-covered outcome does not stop again (#205)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-settled-outcome
base: 82a218f104bde75596fec4773887dc118aa50337
next: test-writer
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 330000, "turns": null, "usd": 2.2, "basis": ["2026-10-30-covers-list", "2026-11-07-defects-stops", "2026-11-09-defects-tools", "2026-11-24-cleaner-commit"]}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.3, "basis": ["2026-10-30-covers-list", "2026-11-07-defects-stops", "2026-11-09-defects-tools", "2026-11-24-cleaner-commit"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-24-cleaner-commit", "2026-11-20-names", "2026-11-19-removal-line"]}], "wall_s": 1800, "rounds": 2, "rounds_reason": "The record bundles three cases one red pass may miss (wording variants, bundled stops, an unsettled outcome that must still fire), and the nearest basis, covers-list, ran three rounds on the same stop.", "shape_breadth": "narrow", "shape_note": "Expect the change to touch only the red_misses_scenario settled-outcome check, its tests, and one CHANGELOG line."}
budget: {"tokens": 585000, "usd": 4.51, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_run.py"], "command": "cd tests && python3 -m unittest test_run.TestWriterChecksTest", "failure": "AssertionError: 10 == 10 (red_misses_scenario fired again: 'The test writer did not cover 7: ...')", "watch_before_merge": null}
wall_baseline: {"commit": "30a29459de6704d92fc4c01054e1a39cab98b7e5", "count": 104, "digest": "5921d8e97c1da8da", "file": ".xv/slices/2026-11-24-settled-outcome.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6957, "cache_read": 64914, "cache_write": 46282, "tokens": 53245, "usd": 0.0134, "turns": 4, "wall_s": 32.4, "session": "39a5e326-038b-40d5-be22-dc0fe08736e3", "step": "forecaster", "at": "2026-11-24T22:25:43+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-settled-outcome/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 24, "tokens_out": 8043, "cache_read": 382230, "cache_write": 35295, "tokens": 43362, "usd": 0.2599, "turns": 13, "wall_s": 80.6, "session": "325ec237-58ff-45ca-86f8-397a3847cfdc", "step": "test-writer", "at": "2026-11-24T22:27:15+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-settled-outcome/02-test-writer.out"}]
stops: [{"at": "2026-11-24T22:25:43+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-settled-outcome budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Standing answer: accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-24T22:25:54+00:00", "pick": "other", "settled": "Sean sets budget {tokens: 585000, usd: 4.51}, the forecast (narrow); next is test-writer.", "new_info": "none", "cause": "decision: Sean's standing answer accepts a forecast that is not wide", "budget_change": {"from": null, "to": {"tokens": 585000, "usd": 4.51}}}, {"at": "2026-11-24T22:27:28+00:00", "step": "test-writer", "order": "red_misses_scenario", "seat": "originator", "question": "The test writer did not cover 4. A line in CHANGELOG.md: A CHANGELOG line is a one-time wording change; no test pins it, and the cleaner and guardian read the file.", "answered_by": [], "answer": null, "also": ["red_misses_scenario"], "budget_seen": {"tokens": 585000, "usd": 4.51, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast 330k sonnet, 200k opus, 55k haiku tokens; 1800 s wall, 2 rounds, narrow shape.", "at": "2026-11-24T22:25:43+00:00"}, {"agent": "test-writer", "status": "red", "summary": "Six tests in TestWriterChecksTest: a settled not-covered outcome re-stops when reworded or settled in a bundled send-back answer; an unsettled one still stops.", "at": "2026-11-24T22:27:15+00:00"}], "forecaster": {"at": "2026-11-24T22:25:43+00:00", "wrote": [], "removal_not_made": []}, "test-writer": {"at": "2026-11-24T22:27:15+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "---------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-24-settled-outcome/tests/test_run.py\", line 1542, in test_an_unsettled_outcome_still_stops_on_the_same_pass_as_a_settled_one\n    self.assert_stops(p, \"8. A line in README.md\")\n    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-24-settled-outcome/tests/test_run.py\", line 1363, in assert_stops\n    self.assertIn(n, stop[\"question\"])\n    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^\nAssertionError: '8. A line in README.md' not found in 'The test writer did not cover 7: wording'\n\n----------------------------------------------------------------------\nRan 28 tests in 12.897s\n\nFAILED (failures=5)\n", "old_red_changed": [], "red_gaps": [], "covered_kept": [{"outcome": "1. A person answers a red_misses_scenario stop for outcome N. A later pass lists N again; no new red_misses_scenario fires, however N is worded (\"7\", \"7. A line in CHANGELOG.md\", \"7. A line in CHANGELOG.md.\")", "test": ["test_a_settled_outcome_reported_by_its_number_alone_does_not_stop_again", "test_a_settled_outcome_reported_with_a_closing_full_stop_does_not_stop_again", "test_a_settled_outcome_first_reported_by_its_number_does_not_stop_on_the_full_wording"]}, {"outcome": "2. It also holds when the person settled N in the answer to another stop that bundled red_misses_scenario, and when that answer sent the slice back", "test": ["test_an_outcome_settled_in_a_bundled_answer_that_sent_the_slice_back_does_not_stop_again"]}, {"outcome": "3. An outcome that no person settled still fires red_misses_scenario, on the same pass as a settled one", "test": ["test_an_unsettled_outcome_still_stops_on_the_same_pass_as_a_settled_one", "test_a_different_number_is_not_the_settled_outcome"]}], "unreadable": [], "not_covered": [{"outcome": "4. A line in CHANGELOG.md", "why": "A CHANGELOG line is a one-time wording change; no test pins it, and the cleaner and guardian read the file."}, {"outcome": "A direct red_misses_scenario answer that sent the slice back (unbundled) settles its outcome", "why": "The existing test test_a_not_covered_item_the_person_sent_back_stops_again_when_reported_again says such an answer ('cover it') stops again; the scenario does not say whether a send-back that settles 'no test' differs. I kept the old test and tested the send-back only through a bundled answer, as the scenario words it. Needs a person's ruling."}], "missed_outcomes": [], "removal_not_made": []}}
step_start: {"agent": "test-writer", "commit": "30a29459de6704d92fc4c01054e1a39cab98b7e5", "ended": true}
old_tests_to_move: []
may_not_files_needed: []
---
# A settled not-covered outcome does not stop again (#205)

## Scenario

A not-covered outcome that a person settled does not stop again on a later test writer pass (#205).

1. A person answers a `red_misses_scenario` stop for outcome N. A later test writer pass lists N in `not_covered` again. No new `red_misses_scenario` fires for N. This holds when the later pass words N or its reason differently, such as "7", "7. A line in CHANGELOG.md" or "7. A line in CHANGELOG.md.".
2. It also holds when the person settled N in the answer to another stop that bundled `red_misses_scenario`, and when that answer sent the slice back.
3. An outcome that no person settled still fires `red_misses_scenario`, on the same pass as a settled one.
4. A line in `CHANGELOG.md`.

## May ignore

an outcome that the scenario amends after the answer

## Recording

.xv/recordings/rec-settled-outcome.md

## Log
- 2026-11-24T22:25:03+00:00 watch: slice opened by Sean Kennedy
- 2026-11-24T22:25:43+00:00 forecaster: done: Forecast 330k sonnet, 200k opus, 55k haiku tokens; 1800 s wall, 2 rounds, narrow shape.
- 2026-11-24T22:25:43+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-settled-outcome budget ... --by <name>`).
- 2026-11-24T22:25:54+00:00 Sean Kennedy: set budget
- 2026-11-24T22:25:54+00:00 Sean Kennedy: answered budget_not_set: Standing answer: accept the forecast unless it is wide
- 2026-11-24T22:25:54+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-24T22:27:15+00:00 test-writer: red: Six tests in TestWriterChecksTest: a settled not-covered outcome re-stops when reworded or settled in a bundled send-back answer; an unsettled one still stops.
- 2026-11-24T22:27:28+00:00 watch: stop (red_misses_scenario) for originator: The test writer did not cover 4. A line in CHANGELOG.md: A CHANGELOG line is a one-time wording change; no test pins it, and the cleaner and guardian read the file.

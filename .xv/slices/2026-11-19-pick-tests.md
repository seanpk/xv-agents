---
id: 2026-11-19-pick-tests
title: Two prototype pick paths have tests
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-pick-tests
base: 07f5734397e770fdcb049a0eb78b318877d93cf6
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 200000, "turns": null, "usd": 1.0, "basis": ["2026-11-19-wall-keep", "2026-11-06-covers-stall", "2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 120000, "turns": null, "usd": 1.2, "basis": ["2026-11-19-wall-keep", "2026-11-06-covers-stall", "2026-11-18-move-names"]}, {"harness": "claude", "model": "haiku", "tokens": 50000, "turns": null, "usd": 0.01, "basis": ["2026-11-19-wall-keep", "2026-11-18-move-names"]}], "wall_s": 600, "rounds": 1, "rounds_reason": "One scenario, maker, cleaner and guardian pass expected; a reopen is possible if the red on the --keep conflict or missing-file case passes early or misses a point, and the sonnet and opus bands carry a partial reopen rather than a full second round.", "shape_breadth": "narrow", "shape_note": "Expect changes only to tests under tests/** for the two pick paths; a shared helper in tests may move, and no source change is expected."}
budget: {"tokens": 370000, "usd": 2.21, "set_by": "Sean Kennedy"}
red: null
wall_baseline: {"commit": "31785a92789260e5592e5eed1b026bfb1047b7a9", "count": 99, "digest": "e80f8e31fd1f07b8", "file": ".xv/slices/2026-11-19-pick-tests.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5336, "cache_read": 62963, "cache_write": 45663, "tokens": 51005, "usd": 0.0124, "turns": 4, "wall_s": 25.6, "session": "54e1ac7b-ae28-4581-8b0b-e0da8e6b67a1", "step": "forecaster", "at": "2026-11-20T01:21:05+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 14, "tokens_out": 3137, "cache_read": 175613, "cache_write": 27311, "tokens": 30462, "usd": 0.1582, "turns": 8, "wall_s": 26.1, "session": "ff4b0d4a-6dd0-4525-b093-8f17c97bd5e5", "step": "scenario", "at": "2026-11-20T01:21:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/02-scenario.out"}]
stops: [{"at": "2026-11-20T01:21:05+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-pick-tests budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "as before, I accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-20T01:21:13+00:00", "pick": "other", "settled": "The budget is the forecast: 370,000 tokens and $2.21; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 370000, "usd": 2.21}}}, {"at": "2026-11-20T01:21:42+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (stopped): Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.", "answered_by": [], "answer": null, "also": ["red_misses_scenario", "red_misses_scenario", "red_misses_scenario", "red_misses_scenario"], "budget_seen": {"tokens": 370000, "usd": 2.21, "set_by": "Sean Kennedy"}, "options": [{"text": "Keep the two tests in tests/test_prototypes.py as green pins of what the code already does; outcomes 1 and 2 are covered by them; skip the maker and go on to the cleaner, then the guardian", "settles": "This slice only adds tests: the two tests pin existing behavior, there is no red, and the maker has nothing to do", "amends": false}, {"text": "Close the slice without the tests and close #181 as not needed", "settles": "No tests are added; #181 is closed", "amends": false}], "recommended": 1}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow test-only defect: one clean pass expected, sonnet ~200k, opus ~120k, haiku (forecaster) ~50k; wall ~600s; a reopen is possible but priced only as a partial band.", "at": "2026-11-20T01:21:05+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.", "at": "2026-11-20T01:21:42+00:00"}], "forecaster": {"at": "2026-11-20T01:21:05+00:00", "wrote": [], "removal_not_made": []}, "scenario": {"at": "2026-11-20T01:21:42+00:00", "protected_changed": [], "outside_tests": [], "red_fails": null, "old_red_changed": [], "red_gaps": ["--keep", "--scenario-file"], "covered_kept": [], "unreadable": ["The report's `covered` is missing, empty, or has an outcome that names no test."], "not_covered": [{"outcome": "1", "why": "The test (test_a_kept_pick_that_conflicts_with_the_slice_branch_is_refused_and_only_the_variant_tip_moves) passes on the current code; the behaviour already exists, so no red is possible."}, {"outcome": "2", "why": "The test (test_a_pick_without_keep_with_a_missing_scenario_file_is_refused_and_changes_nothing) passes on the current code; the behaviour already exists, so no red is possible."}], "missed_outcomes": [], "removal_not_made": []}}
old_tests_to_move: []
may_not_files_needed: []
---
# Two prototype pick paths have tests

## Scenario

Two prototype pick paths have tests.

1. `xv prototype pick --keep` on a variant whose merge conflicts with the slice branch outside `.xv/` is refused, and the record does not change. The variant's uncommitted work is committed onto the variant's own branch before the refusal, so that branch's tip moves; a test pins this.
2. `xv prototype pick` without `--keep` and with a `--scenario-file` that does not exist is refused before anything changes: all three prototypes, their worktrees and their branches stay, and the record does not change.

## May ignore

other prototype paths; a CHANGELOG line, since no check changes

## Recording

None. A feature starts from words.

## Log
- 2026-11-20T01:20:35+00:00 watch: slice opened by Sean Kennedy
- 2026-11-20T01:21:05+00:00 forecaster: done: Narrow test-only defect: one clean pass expected, sonnet ~200k, opus ~120k, haiku (forecaster) ~50k; wall ~600s; a reopen is possible but priced only as a partial band.
- 2026-11-20T01:21:05+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-pick-tests budget ... --by <name>`).
- 2026-11-20T01:21:13+00:00 Sean Kennedy: set budget
- 2026-11-20T01:21:13+00:00 Sean Kennedy: answered budget_not_set: as before, I accept the forecast unless it is wide
- 2026-11-20T01:21:13+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-20T01:21:42+00:00 scenario: stopped: Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.
- 2026-11-20T01:21:42+00:00 watch: stop (scenario_stopped) for originator: The scenario stopped (stopped): Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.
- 2026-11-20T01:21:58+00:00 watch: offered 2 options for scenario_stopped

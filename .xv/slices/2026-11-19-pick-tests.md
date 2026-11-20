---
id: 2026-11-19-pick-tests
title: Two prototype pick paths have tests
kind: defect
status: working
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-pick-tests
base: 07f5734397e770fdcb049a0eb78b318877d93cf6
next: close
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 200000, "turns": null, "usd": 1.0, "basis": ["2026-11-19-wall-keep", "2026-11-06-covers-stall", "2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 120000, "turns": null, "usd": 1.2, "basis": ["2026-11-19-wall-keep", "2026-11-06-covers-stall", "2026-11-18-move-names"]}, {"harness": "claude", "model": "haiku", "tokens": 50000, "turns": null, "usd": 0.01, "basis": ["2026-11-19-wall-keep", "2026-11-18-move-names"]}], "wall_s": 600, "rounds": 1, "rounds_reason": "One scenario, maker, cleaner and guardian pass expected; a reopen is possible if the red on the --keep conflict or missing-file case passes early or misses a point, and the sonnet and opus bands carry a partial reopen rather than a full second round.", "shape_breadth": "narrow", "shape_note": "Expect changes only to tests under tests/** for the two pick paths; a shared helper in tests may move, and no source change is expected."}
budget: {"tokens": 370000, "usd": 2.21, "set_by": "Sean Kennedy"}
red: null
wall_baseline: {"commit": "31785a92789260e5592e5eed1b026bfb1047b7a9", "count": 99, "digest": "e80f8e31fd1f07b8", "file": ".xv/slices/2026-11-19-pick-tests.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: green
cleaner_commit: null
packet: .xv/slices/2026-11-19-pick-tests.packet.md
shape_change: no
pitch_contradiction: no
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5336, "cache_read": 62963, "cache_write": 45663, "tokens": 51005, "usd": 0.0124, "turns": 4, "wall_s": 25.6, "session": "54e1ac7b-ae28-4581-8b0b-e0da8e6b67a1", "step": "forecaster", "at": "2026-11-20T01:21:05+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 14, "tokens_out": 3137, "cache_read": 175613, "cache_write": 27311, "tokens": 30462, "usd": 0.1582, "turns": 8, "wall_s": 26.1, "session": "ff4b0d4a-6dd0-4525-b093-8f17c97bd5e5", "step": "scenario", "at": "2026-11-20T01:21:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 8, "tokens_out": 563, "cache_read": 67027, "cache_write": 12489, "tokens": 13060, "usd": 0.0623, "turns": 5, "wall_s": 35.0, "session": "25385e81-5026-4922-9e5a-fc63272fb8bb", "step": "cleaner", "at": "2026-11-20T01:41:49+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/03-cleaner.out"}, {"harness": "claude", "model": "opus", "model_id": "claude-opus-5-5", "tokens_in": 26, "tokens_out": 8456, "cache_read": 399667, "cache_write": 46253, "tokens": 54735, "usd": 0.6192, "turns": 15, "wall_s": 80.9, "session": "400b0782-e560-497f-af43-0fb6beb1b1c6", "step": "guardian", "at": "2026-11-20T01:43:39+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-pick-tests/04-guardian.out"}]
stops: [{"at": "2026-11-20T01:21:05+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-pick-tests budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "as before, I accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-20T01:21:13+00:00", "pick": "other", "settled": "The budget is the forecast: 370,000 tokens and $2.21; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 370000, "usd": 2.21}}}, {"at": "2026-11-20T01:21:42+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (stopped): Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.", "answered_by": ["Sean Kennedy"], "answer": "1", "also": ["red_misses_scenario", "red_misses_scenario", "red_misses_scenario", "red_misses_scenario"], "options": [{"text": "Keep the two tests in tests/test_prototypes.py as green pins of what the code already does; outcomes 1 and 2 are covered by them; skip the maker and go on to the cleaner, then the guardian", "settles": "This slice only adds tests: the two tests pin existing behavior, there is no red, and the maker has nothing to do", "amends": false}, {"text": "Close the slice without the tests and close #181 as not needed", "settles": "No tests are added; #181 is closed", "amends": false}], "recommended": 1, "answered_at": "2026-11-20T01:41:10+00:00", "pick": 1, "settled": "This slice only adds tests: the two tests pin existing behavior, there is no red, and the maker has nothing to do", "new_info": "none", "cause": "tool: XV has no path for a slice that only adds tests", "bundle": ["red_misses_scenario"]}, {"at": "2026-11-20T01:43:39+00:00", "step": "guardian", "order": "moves_to_accept", "seat": "originator", "question": "The guardian proposes a change to the picture; the shape did not. Accept them from the packet, talk it through with someone, or send it back. The merge is yours.", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "Accept the guardian's 2 picture edits as worded (replace .xv/picture.md:200; add one line after it), close, open the PR, and merge when CI passes", "settles": "The picture edits are accepted; the slice closes with 2 new tests", "amends": false}, {"text": "Close without the picture edits", "settles": "The picture stays as it is", "amends": false}], "recommended": 1, "answered_at": "2026-11-20T01:47:23+00:00", "pick": 1, "settled": "The picture edits are accepted; the slice closes with 2 new tests", "new_info": "none", "cause": "decision: the picture edits are accepted", "accepted_wall": [], "refused_wall": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow test-only defect: one clean pass expected, sonnet ~200k, opus ~120k, haiku (forecaster) ~50k; wall ~600s; a reopen is possible but priced only as a partial band.", "at": "2026-11-20T01:21:05+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Both new pick tests pass on the current code: the refusals already exist, so there is no red; asking whether to keep them as green pins.", "at": "2026-11-20T01:21:42+00:00"}, {"agent": "cleaner", "status": "done", "summary": "Nothing to fix in the two added pick tests; suite green; no commit.", "shape_proposals": [], "candidate_standards": [], "applied": [], "at": "2026-11-20T01:41:49+00:00"}, {"agent": "guardian", "status": "done", "summary": "Test-only slice: two green pins for prototype pick refusals; no shape or pitch stop; picture line 200 needs widening; the conflict test does not check the refusal's reason.", "picture_change": "yes", "at": "2026-11-20T01:43:39+00:00"}], "forecaster": {"at": "2026-11-20T01:21:05+00:00", "wrote": [], "removal_not_made": []}, "scenario": {"at": "2026-11-20T01:21:42+00:00", "protected_changed": [], "outside_tests": [], "red_fails": null, "old_red_changed": [], "red_gaps": ["--keep", "--scenario-file"], "covered_kept": [], "unreadable": ["The report's `covered` is missing, empty, or has an outcome that names no test."], "not_covered": [{"outcome": "1", "why": "The test (test_a_kept_pick_that_conflicts_with_the_slice_branch_is_refused_and_only_the_variant_tip_moves) passes on the current code; the behaviour already exists, so no red is possible."}, {"outcome": "2", "why": "The test (test_a_pick_without_keep_with_a_missing_scenario_file_is_refused_and_changes_nothing) passes on the current code; the behaviour already exists, so no red is possible."}], "missed_outcomes": [], "removal_not_made": []}, "cleaner": {"at": "2026-11-20T01:41:49+00:00", "protected_changed": [], "suite": "green", "suite_output": "--------------------------------------\nRan 44 tests in 20.641s\n\nOK\n----------------------------------------------------------------------\nRan 44 tests in 21.350s\n\nOK\n----------------------------------------------------------------------\nRan 44 tests in 21.973s\n\nOK\n----------------------------------------------------------------------\nRan 44 tests in 21.654s\n\nOK\n----------------------------------------------------------------------\nRan 44 tests in 20.178s\n\nOK\n----------------------------------------------------------------------\nRan 44 tests in 25.023s\n\nOK\n----------------------------------------------------------------------\nRan 43 tests in 22.833s\n\nOK\n----------------------------------------------------------------------\nRan 43 tests in 26.853s\n\nOK\nRan 1406 tests in shard 1/1, 32 jobs\nOK\n", "failing_step": "", "failing": [], "failing_history": [[]], "diff_lines": 38, "diff_history": [38], "wall": {"slice": "2026-11-19-pick-tests", "baseline": "31785a92789260e5592e5eed1b026bfb1047b7a9", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}, "standards_touched": false, "committed": false, "removal_not_made": []}, "guardian": {"at": "2026-11-20T01:43:39+00:00", "wrote": [], "packet": true, "packet_problems": [], "dropped_findings": 0, "miss_disagreement": [], "misses": [], "miss_amend": false, "picture_change": "yes", "shape_breadth": "none", "packet_head": "df3fc8c43b8a535303db0bee4fe4aea0eafb376d", "removal_not_made": []}}
old_tests_to_move: []
may_not_files_needed: []
change_misses_scenario: no
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
- 2026-11-20T01:41:10+00:00 Sean Kennedy: answered scenario_stopped: 1
- 2026-11-20T01:41:10+00:00 watch: scribe: wrote settled, new_info, cause for scenario_stopped as the scribe of Sean Kennedy
- 2026-11-20T01:41:49+00:00 cleaner: done: Nothing to fix in the two added pick tests; suite green; no commit.
- 2026-11-20T01:43:39+00:00 guardian: done: Test-only slice: two green pins for prototype pick refusals; no shape or pitch stop; picture line 200 needs widening; the conflict test does not check the refusal's reason.
- 2026-11-20T01:43:39+00:00 watch: stop (moves_to_accept) for originator: The guardian proposes a change to the picture; the shape did not. Accept them from the packet, talk it through with someone, or send it back. The merge is yours.
- 2026-11-20T01:43:52+00:00 watch: offered 2 options for moves_to_accept
- 2026-11-20T01:47:23+00:00 watch: picture edit directed by Sean Kennedy (8cdcc73): the guardian's 2 edits to .xv/picture.md (line 200, after 200), as worded in the packet
- 2026-11-20T01:47:23+00:00 Sean Kennedy: answered moves_to_accept: 1
- 2026-11-20T01:47:23+00:00 watch: scribe: wrote settled, new_info, cause for moves_to_accept as the scribe of Sean Kennedy

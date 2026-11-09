---
id: 2026-11-09-retro-fixes
title: "Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled"
kind: defect
status: working
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-retro-fixes
base: 4f6dcb707076f9b7a130b27302e6cafdd92e73e1
next: maker
build: none
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.5, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops", "2026-10-27-retro-accept-fields"], "note": "Basis actuals 236k-409k tokens (median ~317k), $1.28-$2.48. Bumped for seven scenario items across three tool areas against one tool fix in defects-tools. Guide has no turn column, so turns are null. Reopen rounds are not priced: basis rows that reopened ran 2-3x."}, {"harness": "claude", "model": "opus", "tokens": 230000, "turns": null, "usd": 2.9, "basis": ["2026-11-09-defects-tools", "2026-11-07-defects-stops", "2026-10-27-retro-accept-fields"], "note": "Basis actuals 177k-237k tokens (median ~203k), $2.14-$3.15. Guardian checks seven items, so a small bump. Guardian reopen passes are not priced."}], "wall_s": 1500, "shape": "narrow", "breadth": "Changes the unrecorded-move check (build-added tests), the record move --slice-only marker, the red_misses_scenario dedupe on the stop path, and the scenario brief plus CHANGELOG. No new state or stop kinds, but three tool areas are touched."}
budget: {"tokens": 630000, "usd": 5.4, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_from_build.py", "tests/test_record.py", "tests/test_run.py"], "command": "cd tests && python3 -m unittest test_from_build.BuildAddedTestsTest test_record.MoveSliceOnlyTest test_record.ScenarioBriefRetroFixesTest test_run.ScenarioChecksTest", "failure": "AssertionError: Lists differ: ['unrecorded_move'] != [] (test_a_test_file_the_build_only_added_tests_to_is_not_an_unrecorded_move)", "watch_first_green": null}
wall_baseline: {"commit": "e551797853372f521b4525b90d9c1c18793ae07b", "count": 93, "digest": "e3ec74043149027e", "file": ".xv/slices/2026-11-09-retro-fixes.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_record.py", "test": "test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes", "why": "checks one CHANGELOG line, which has no value after the slice", "checks": "CHANGELOG.md", "accepted": true}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4001, "cache_read": 61830, "cache_write": 37716, "tokens": 41723, "usd": 0.0102, "turns": 4, "wall_s": 19.6, "session": "ef51eb6d-b7d7-470d-bdb9-4ba8b88932cb", "step": "forecaster", "at": "2026-11-09T16:28:59+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-09-retro-fixes/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 40, "tokens_out": 12383, "cache_read": 847647, "cache_write": 62447, "tokens": 74870, "usd": 0.4585, "turns": 22, "wall_s": 108.0, "session": "f141e077-a2e1-4e61-97f1-7ce992d360d4", "step": "scenario", "at": "2026-11-09T16:30:47+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-09-retro-fixes/02-scenario.out"}]
stops: [{"at": "2026-11-09T16:28:59+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-retro-fixes budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "let's open them and go with the forecaster's estimate for both of them without stopping", "also": [], "answered_at": "2026-11-09T16:28:59+00:00", "pick": "other", "settled": "the budget is the forecast: {\"tokens\": 630000, \"usd\": 5.4}", "new_info": "none", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 630000, "usd": 5.4}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~400k tokens and claude/opus ~230k tokens from the defect rows, with reopen risk not priced; the shape is narrow.", "at": "2026-11-09T16:28:59+00:00"}, {"agent": "scenario", "status": "red", "summary": "Seven new tests for the retro fixes; six fail on the current code and the point-2 guards already pass.", "at": "2026-11-09T16:30:47+00:00"}], "forecaster": {"at": "2026-11-09T16:28:59+00:00", "wrote": []}, "scenario": {"at": "2026-11-09T16:30:47+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "lf.assertNotEqual(p.returncode, 10, p.stdout + p.stderr)\n    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 10 == 10 : {\n  \"slice\": \"s1\",\n  \"after\": \"scenario\",\n  \"stop\": {\n    \"order\": \"red_misses_scenario\",\n    \"seat\": \"originator\",\n    \"question\": \"The scenario agent did not cover the grocer share: no seam\",\n    \"blocking\": true\n  },\n  \"fired\": [\n    {\n      \"order\": \"red_misses_scenario\",\n      \"seat\": \"originator\",\n      \"question\": \"The scenario agent did not cover the grocer share: no seam\",\n      \"blocking\": true\n    }\n  ],\n  \"next\": \"scenario\",\n  \"record\": \".xv/slices/s1.md\",\n  \"worktree\": \"/tmp/xv-test-t1k6724h/repo/.xv/worktrees/s1\"\n}\n\n\n----------------------------------------------------------------------\nRan 28 tests in 23.187s\n\nFAILED (failures=7)\n", "old_red_changed": [], "red_gaps": [], "covers_kept": [{"item": "1", "test": ["BuildAddedTestsTest.test_a_test_file_the_build_only_added_tests_to_is_not_an_unrecorded_move"]}, {"item": "2", "test": ["BuildAddedTestsTest.test_a_test_file_the_build_changed_a_line_of_still_stops_with_unrecorded_move", "BuildAddedTestsTest.test_a_test_file_the_build_removed_a_line_from_still_stops_with_unrecorded_move"]}, {"item": "3", "test": ["MoveSliceOnlyTest.test_slice_only_on_a_test_not_in_the_slice_only_list_marks_the_move", "MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked"]}, {"item": "4", "test": ["ScenarioChecksTest.test_a_not_covered_item_a_person_answered_does_not_stop_again_on_a_later_pass", "ScenarioChecksTest.test_a_new_not_covered_item_still_stops_on_a_later_pass"]}, {"item": "5", "test": ["ScenarioBriefRetroFixesTest.test_the_brief_says_a_red_that_fails_only_on_the_build_is_reported_and_does_not_stop"]}, {"item": "6", "test": ["ScenarioBriefRetroFixesTest.test_the_brief_says_to_run_the_red_in_the_foreground_to_its_end_before_the_report"]}, {"item": "7", "test": ["ScenarioBriefRetroFixesTest.test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes"]}], "unreadable": [], "not_covered": [], "missed_points": []}}
old_tests_forced: []
may_not_files: []
---
# Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled

## Scenario

1. On a slice from a build, a test file that the build only added tests to (no line at the base changed or removed) is not an unrecorded move: `unrecorded_move` does not fire for it, and the wall's `unrecorded` list does not name it. (#172)
2. On a slice from a build, a test file in which the build changed or removed a line at the base still stops with `unrecorded_move`. (#172)
3. `xv record move --slice-only` on a test that is not in the record's `slice_only` list marks the move `slice_only: true`. (#173)
4. After the scenario step, a `not_covered` item that a person already answered at an earlier `red_misses_scenario` stop does not fire `red_misses_scenario` again on a later pass. A new `not_covered` item still fires. (#174)
5. The scenario brief says that on a slice from a build, a red test that fails only on the build is expected: the agent reports it and does not stop to ask. (#174)
6. The scenario brief says to run the red command in the foreground, to its end, before writing the report. (#174)
7. `CHANGELOG.md` has a line for the brief change and the tool changes.

## May ignore

Other files under the test paths that are not tests, such as tests/run.py; they still count as test files.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T16:28:25+00:00 watch: slice opened by Sean Kennedy
- 2026-11-09T16:28:59+00:00 forecaster: done: Forecast claude/sonnet ~400k tokens and claude/opus ~230k tokens from the defect rows, with reopen risk not priced; the shape is narrow.
- 2026-11-09T16:28:59+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-09-retro-fixes budget ... --by <name>`).
- 2026-11-09T16:28:59+00:00 Sean Kennedy: set budget
- 2026-11-09T16:28:59+00:00 Sean Kennedy: answered budget_not_set: let's open them and go with the forecaster's estimate for both of them without stopping
- 2026-11-09T16:28:59+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-09T16:30:47+00:00 scenario: red: Seven new tests for the retro fixes; six fail on the current code and the point-2 guards already pass.
- 2026-11-09T16:30:47+00:00 watch: slice-only mark on test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes accepted: it checks CHANGELOG.md, which the config lists in tests.slice_only_files

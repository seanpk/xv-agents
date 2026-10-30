---
id: 2026-10-30-covers-list
title: A covers item may name more than one test
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-covers-list
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 490000, "turns": null, "usd": 2.9, "basis": ["2026-10-30-by-name", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"], "note": "Guide has no turns column. Actual tokens 489k, 506k, 496k; usd 2.58, 3.00, 2.92."}, {"harness": "claude", "model": "opus", "tokens": 290000, "turns": null, "usd": 3.5, "basis": ["2026-10-30-by-name", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"], "note": "Guide has no turns column. Actual tokens 295k, 280k, 275k; usd 3.58, 3.42, 3.40."}], "wall_s": 2000, "shape": "narrow", "breadth": "Scenario brief (the report section and its parsing) and one check that matches red names, plus a CHANGELOG line; expect the reopen pattern of by-name and red-covers-scenario, with a stop on the brief's wording or the CHANGELOG line the most likely cause of a second round."}
budget: {"tokens": 500000, "usd": 4, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_run.py", "tests/test_check.py"], "command": "cd tests && python3 -m unittest test_run.WatchLoopTest test_check.ScenarioBriefTest", "failure": "FAIL: test_a_covers_test_that_is_a_list_of_names_all_in_red_files_goes_on_to_the_maker (the report is stopped before the maker)", "watch_first_green": "A scenario report whose covers item lists two test names, or writes one as Class.test_name or file::test_name, goes on to the maker; a wrong class, a file that is not a red file, or a name in no red file still stops, and the stop names that name."}
wall_baseline: {"commit": "138f9b4063eb729fe85c7f42b200fa60f228d6ab", "count": 57, "digest": "da73dac370ee70f1", "file": ".xv/slices/2026-10-30-covers-list.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3177, "cache_read": 23874, "cache_write": 22103, "tokens": 25284, "usd": 0.0062, "turns": 3, "wall_s": 19.1, "session": "90010a1b-7fbb-4bd8-b74d-92d9c2b155d4", "step": "forecaster", "at": "2026-10-30T05:57:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-covers-list/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 22, "tokens_out": 6115, "cache_read": 305513, "cache_write": 31692, "tokens": 37829, "usd": 0.2185, "turns": 13, "wall_s": 75.5, "session": "b093e6c7-ff12-49f6-bbe7-77ca84dcced9", "step": "scenario", "at": "2026-10-30T06:03:13+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-covers-list/02-scenario.out"}]
stops: [{"at": "2026-10-30T05:57:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-covers-list budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1, and take the budget", "also": [], "options": [{"text": "$4 and 500K tokens", "settles": "The budget is $4 and 500K tokens: a clean pass and one send-back for a small change.", "amends": false}, {"text": "$6.40 and 780K tokens, the forecast", "settles": "The budget is $6.40 and 780K tokens, as forecast.", "amends": false}, {"text": "$2.50 and 350K tokens", "settles": "The budget is $2.50 and 350K tokens: one clean pass.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T06:01:57+00:00", "pick": 1, "settled": "The budget is $4 and 500K tokens: a clean pass and one send-back for a small change.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 500000, "usd": 4}}}, {"at": "2026-10-30T06:03:44+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The report says `['test_a_covers_test_that_is_a_list_of_names_all_in_red_files_goes_on_to_the_maker', 'test_a_covers_list_with_a_name_in_no_red_file_stops_before_the_maker', 'test_a_covers_list_with_a_name_that_is_part_of_a_longer_name_stops_before_the_maker', 'test_an_empty_covers_list_stops_before_the_maker']` covers 1. a covers test may be one name or a list; each name must match a whole test name in a red file, and no red file has that test.", "answered_by": [], "answer": null, "also": ["red_misses_scenario", "red_misses_scenario"], "budget_seen": {"tokens": 500000, "usd": 4, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~490k tokens / $2.9 and opus ~290k tokens / $3.5 for a narrow covers-list feature, ~2000 s wall; basis is the three nearest covers and scenario-brief rows, which all reopened.", "at": "2026-10-30T05:57:45+00:00"}, {"agent": "scenario", "status": "red", "summary": "A covers item's test may be a list, a ,/;-joined string, or Class.test / file::test (both parts must match); brief example and CHANGELOG line asserted", "at": "2026-10-30T06:03:13+00:00"}], "forecaster": {"at": "2026-10-30T05:57:45+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T06:03:13+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": " what is missing.\\n'\n\n======================================================================\nFAIL: test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test (test_check.ScenarioBriefTest.test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-30-covers-list/tests/test_check.py\", line 67, in test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test\n    self.assertIn(\"covers\", line)\n    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^\nAssertionError: 'covers' not found in ''\n\n----------------------------------------------------------------------\nRan 59 tests in 30.546s\n\nFAILED (failures=7)\n", "old_red_changed": [], "red_gaps": [], "unreadable": ["The report says `['test_a_covers_test_that_is_a_list_of_names_all_in_red_files_goes_on_to_the_maker', 'test_a_covers_list_with_a_name_in_no_red_file_stops_before_the_maker', 'test_a_covers_list_with_a_name_that_is_part_of_a_longer_name_stops_before_the_maker', 'test_an_empty_covers_list_stops_before_the_maker']` covers 1. a covers test may be one name or a list; each name must match a whole test name in a red file, and no red file has that test.", "The report says `['test_a_covers_test_that_joins_names_with_a_comma_goes_on_to_the_maker', 'test_a_covers_test_that_joins_names_with_a_semicolon_goes_on_to_the_maker', 'test_a_joined_covers_test_with_a_name_in_no_red_file_stops_before_the_maker']` covers 2. a test string joining names with , or ; is read as that list, and no red file has that test.", "The report says `['test_a_covers_name_written_class_dot_test_goes_on_when_the_class_and_test_are_in_a_red_file', 'test_a_covers_name_written_with_the_wrong_class_stops_before_the_maker', 'test_a_covers_name_written_file_colons_test_goes_on_when_the_file_is_a_red_file_with_the_test', 'test_a_covers_name_written_with_a_file_that_is_not_a_red_file_stops_before_the_maker', 'test_a_covers_name_written_with_the_right_file_and_a_test_it_lacks_stops_before_the_maker']` covers 3. Class.test_name or file::test_name matches only when both parts do (amended), and no red file has that test."], "not_covered": []}}
---
# A covers item may name more than one test

## Scenario

A covers item may name more than one test (#92).

1. In the scenario report, a `covers` item's `test` may be one test name or a list of names. Each name must match a whole test name in a red file.
2. A `test` string that joins names with `,` or `;` is read as that list.
3. A name written as `Class.test_name` or `file::test_name` matches on its last part.
4. The scenario brief's report example shows the list form.

This changes the scenario brief and a check, so `CHANGELOG.md` gets a line.

### Amended 2026-10-30 by Sean Kennedy

Before the scenario step, Sean settled point 3: a name written as `Class.test_name` or `file::test_name` matches only when both parts do. The file must be one of the red files and have the test; the class must be in a red file that also has the test. A name with the right test under the wrong class or file does not match.

## May ignore

None.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T05:57:26+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T05:57:45+00:00 forecaster: done: Forecast sonnet ~490k tokens / $2.9 and opus ~290k tokens / $3.5 for a narrow covers-list feature, ~2000 s wall; basis is the three nearest covers and scenario-brief rows, which all reopened.
- 2026-10-30T05:57:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-covers-list budget ... --by <name>`).
- 2026-10-30T05:57:51+00:00 watch: offered 3 options for budget_not_set
- 2026-10-30T06:01:57+00:00 Sean Kennedy: set budget
- 2026-10-30T06:01:57+00:00 Sean Kennedy: answered budget_not_set: 1, and take the budget
- 2026-10-30T06:01:57+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-30T06:01:57+00:00 Sean Kennedy: amended the scenario
- 2026-10-30T06:03:13+00:00 scenario: red: A covers item's test may be a list, a ,/;-joined string, or Class.test / file::test (both parts must match); brief example and CHANGELOG line asserted
- 2026-10-30T06:03:44+00:00 watch: stop (red_misses_scenario) for originator: The report says `['test_a_covers_test_that_is_a_list_of_names_all_in_red_files_goes_on_to_the_maker', 'test_a_covers_list_with_a_name_in_no_red_file_stops_before_the_maker', 'test_a_covers_list_with_a_name_that_is_part_of_a_longer_name_stops_before_the_maker', 'test_an_empty_covers_list_stops_before_the_maker']` covers 1. a covers test may be one name or a list; each name must match a whole test name in a red file, and no red file has that test.

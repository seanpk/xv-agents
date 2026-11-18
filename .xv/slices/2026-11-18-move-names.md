---
id: 2026-11-18-move-names
title: The removal check reads only names it can find
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-18
branch: xv/2026-11-18-move-names
base: 8e366c9ba6c94b28cbedfad1e5221c22bf914dda
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 490000, "turns": null, "usd": 2.8, "basis": ["2026-11-18-report-tree", "2026-11-16-red-lands", "2026-10-30-by-name", "2026-10-30-stop-words"]}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.5, "basis": ["2026-11-16-red-lands", "2026-10-30-by-name", "2026-10-30-stop-words", "2026-10-30-scenario-miss"]}, {"harness": "claude", "model": "haiku", "tokens": 46000, "turns": null, "usd": 0.01, "basis": ["2026-11-13-names", "2026-11-16-red-lands", "2026-11-18-report-tree"]}], "wall_s": 3500, "rounds": 2, "rounds_reason": "The slice adds a new change_misses_scenario stop and a table of exact name inputs, and report-tree was sent back by the guardian over the same :: and # name forms, so a second pass is likely.", "shape_breadth": "narrow", "shape_note": "Expect movement in the move-name parser and removal check, one table test, the cleaner brief and one CHANGELOG line."}
budget: {"tokens": 836000, "usd": 6.31, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_record.py"], "command": "cd tests && python3 -m unittest test_record.SliceOnlyAssertionFormTest test_record.RemovalCheckNamesTest test_record.CleanerBriefNoteTest test_record.ScenarioMissStandingOrderTest", "failure": "AssertionError: [] is not true : removed Red.test_milk_today for issue#183 (a sentence the check passes while the test is still in its file)", "watch_before_merge": null}
wall_baseline: {"commit": "b09db2b532aa7b6e6ef05ef4bcd12772a9b1a14e", "count": 99, "digest": "e1350460da1d966a", "file": ".xv/slices/2026-11-18-move-names.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6654, "cache_read": 62069, "cache_write": 44806, "tokens": 51466, "usd": 0.0129, "turns": 4, "wall_s": 30.9, "session": "e780dbfa-7d3c-4309-8b7a-c5391cc12c44", "step": "forecaster", "at": "2026-11-18T21:02:26+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-move-names/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 36, "tokens_out": 16256, "cache_read": 890976, "cache_write": 71430, "tokens": 87722, "usd": 0.5374, "turns": 28, "wall_s": 117.0, "session": "26713d99-e821-45b5-a2bc-0eab8603d2e3", "step": "scenario", "at": "2026-11-18T21:04:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-move-names/02-scenario.out"}]
stops: [{"at": "2026-11-18T21:02:26+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-move-names budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1, ok (as before, I accept the forecast unless it is wide)", "also": [], "answered_at": "2026-11-18T21:02:38+00:00", "pick": "other", "settled": "The budget is the forecast: 836,000 tokens and $6.31; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 836000, "usd": 6.31}}}, {"at": "2026-11-18T21:04:48+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The scenario agent did not cover 6: A line in CHANGELOG.md is slice-only: a test of one CHANGELOG line has no value after the slice.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 836000, "usd": 6.31, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast ~490k sonnet, ~300k opus, ~46k haiku tokens over two rounds; sonnet and opus basis rows are the name-form and stop-heavy defect slices.", "at": "2026-11-18T21:02:26+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for the move-name refusal, the exact-name removal check, the table of inputs, the miss/front-matter disagreement stop and the cleaner brief note; the CHANGELOG line is slice-only.", "at": "2026-11-18T21:04:45+00:00"}], "forecaster": {"at": "2026-11-18T21:02:26+00:00", "wrote": [], "removal_not_made": []}, "scenario": {"at": "2026-11-18T21:04:45+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "ioMissStandingOrderTest.test_a_listed_miss_under_change_misses_scenario_no_stops_for_the_originator_naming_it)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-18-move-names/tests/test_record.py\", line 1472, in test_a_listed_miss_under_change_misses_scenario_no_stops_for_the_originator_naming_it\n    self.assertIn(\"change_misses_scenario: no\", v[\"stop\"][\"question\"])\n    ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 'change_misses_scenario: no' not found in 'The suite is green and nothing stopped. The merge is yours.'\n\n----------------------------------------------------------------------\nRan 15 tests in 3.141s\n\nFAILED (failures=19)\n", "old_red_changed": [], "red_gaps": [], "covered_kept": [{"outcome": "1", "test": ["SliceOnlyAssertionFormTest.test_a_sentence_or_a_broken_name_is_refused_and_nothing_is_recorded", "SliceOnlyAssertionFormTest.test_each_form_of_a_name_is_taken", "SliceOnlyAssertionFormTest.test_a_name_followed_by_a_note_in_brackets_is_taken_whichever_bracket", "SliceOnlyAssertionFormTest.test_a_plain_move_without_slice_only_still_takes_any_words"]}, {"outcome": "2", "test": ["RemovalCheckNamesTest.test_the_note_is_not_read_for_a_name", "RemovalCheckNamesTest.test_an_input_that_is_not_a_name_in_a_form_stops_as_unreadable_even_when_the_test_is_gone", "RemovalCheckNamesTest.test_a_name_with_a_note_stops_naming_the_test_while_it_is_there"]}, {"outcome": "3", "test": ["RemovalCheckNamesTest.test_none_of_the_inputs_passes_while_the_test_is_still_in_its_file", "RemovalCheckNamesTest.test_a_name_with_a_note_passes_once_the_test_is_gone"]}, {"outcome": "4", "test": ["ScenarioMissStandingOrderTest.test_a_listed_miss_under_change_misses_scenario_no_stops_for_the_originator_naming_it", "ScenarioMissStandingOrderTest.test_a_packet_that_lists_no_miss_and_says_no_does_not_stop_for_the_disagreement"]}, {"outcome": "5", "test": ["CleanerBriefNoteTest.test_the_brief_says_the_note_is_the_tests_name_as_written_with_an_optional_bracketed_note"]}], "unreadable": [], "not_covered": [{"outcome": "6", "why": "A line in CHANGELOG.md is slice-only: a test of one CHANGELOG line has no value after the slice."}], "missed_outcomes": [], "removal_not_made": []}}
old_tests_to_move: [{"file": "tests/test_record.py", "test": "SliceOnlyGateTest.test_a_move_whose_assertion_starts_with_the_marked_name_keeps_the_flag", "why": "records --slice-only with the assertion 'test_file_is_ts; removed', a sentence outcome 1 now refuses"}, {"file": "tests/test_record.py", "test": "SliceOnlyGateTest.test_a_move_of_another_test_does_not_get_the_flag", "why": "records --slice-only with the assertion 'test_other; removed', a sentence outcome 1 now refuses"}, {"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_a_slice_only_move_whose_assertion_names_a_double_colon_test_still_there_stops", "why": "records --slice-only with a sentence assertion, now refused at the command"}, {"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_a_prose_assertion_with_a_dotted_name_and_no_plain_last_word_never_passes_unchecked", "why": "records --slice-only with a sentence; the refusal replaces the check's stop"}, {"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_a_prose_assertion_ending_in_a_full_stop_never_passes_unchecked", "why": "records --slice-only with a sentence; the refusal replaces the check's stop"}, {"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_a_prose_assertion_with_a_hash_that_is_not_a_name_never_passes_unchecked", "why": "records --slice-only with a sentence; the refusal replaces the check's stop"}, {"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_a_slice_only_move_whose_name_cannot_be_read_stops_the_next_step_saying_so", "why": "records --slice-only with the assertion ';', now refused at the command"}]
may_not_files_needed: []
---
# The removal check reads only names it can find

## Scenario

The removal check reads only names it can find.

1. `xv record move --slice-only` takes an `--assertion` only when it names a test that was in that file when the step began. The name is in a form the check reads: `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`. The name may be followed by a note in brackets: `(...)`, `[...]`, `{...}` or `<...>`. The note is not read for a name. Any other text is refused: the command says that the assertion must be the test's name, with an optional note in brackets, and records nothing.
2. After a step, the removal check looks for exactly the name that the move recorded, without its note. It no longer reads a sentence for a name. A move that reaches the record by another route (in a report) and has no name in a form from outcome 1 stops the step as "the test name could not be read".
3. A table test runs the check over each of these inputs while the test is still in its file: `Red::`, `Red#`, a path with a `-`, `Red::test_x[1]`, `removed Red.test_milk_today as asked`, `removed Red.test_milk_today for issue#183`, `removed Red.test_milk_today.`, a name in backticks, and `Red.test_milk_today (removed as asked)`. Each one stops, at the refusal in outcome 1 or at the check in outcome 2. None of them passes. When the test is gone, `Red.test_milk_today (removed as asked)` and `Red.test_milk_today [see issue#183]` pass.
4. When the packet's `## Scenario misses` section lists a miss but its front matter says `change_misses_scenario: no`, the step stops for the person who set the work going and names the disagreement.
5. The cleaner's brief says that the note for a slice-only removal is the test's name as it is written in the file, with an optional note in brackets after it.
6. A line in CHANGELOG.md.

## May ignore

moves recorded before this change (old slice records); --deleted file removals, which the check already finds by file path

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T21:01:52+00:00 watch: slice opened by Sean Kennedy
- 2026-11-18T21:02:26+00:00 forecaster: done: Forecast ~490k sonnet, ~300k opus, ~46k haiku tokens over two rounds; sonnet and opus basis rows are the name-form and stop-heavy defect slices.
- 2026-11-18T21:02:26+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-move-names budget ... --by <name>`).
- 2026-11-18T21:02:38+00:00 Sean Kennedy: set budget
- 2026-11-18T21:02:38+00:00 Sean Kennedy: answered budget_not_set: 1, ok (as before, I accept the forecast unless it is wide)
- 2026-11-18T21:02:38+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-18T21:04:45+00:00 scenario: red: Red for the move-name refusal, the exact-name removal check, the table of inputs, the miss/front-matter disagreement stop and the cleaner brief note; the CHANGELOG line is slice-only.
- 2026-11-18T21:04:48+00:00 watch: stop (red_misses_scenario) for originator: The scenario agent did not cover 6: A line in CHANGELOG.md is slice-only: a test of one CHANGELOG line has no value after the slice.

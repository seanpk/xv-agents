---
id: 2026-11-19-removal-line
title: "A slice-only removal names its line, and the check reads the tree"
kind: defect
status: working
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-removal-line
base: 2ebb304bf2504ae8d50a2c3104889055f7309772
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 340000, "turns": null, "usd": 2.2, "basis": ["2026-11-18-move-names", "2026-11-16-red-lands", "2026-11-09-defects-tools"]}, {"harness": "claude", "model": "opus", "tokens": 190000, "turns": null, "usd": 2.3, "basis": ["2026-11-18-move-names", "2026-11-16-red-lands", "2026-11-09-defects-tools"]}, {"harness": "claude", "model": "haiku", "tokens": 50000, "turns": null, "usd": 0.01, "basis": ["2026-11-18-move-names", "2026-11-19-wall-keep"]}], "wall_s": 1200, "rounds": 2, "rounds_reason": "move-names drew a guardian send-back at change_misses_scenario, and this slice's scenario makes the same kind of check-and-picture claim, so a second round is likely.", "shape_breadth": "narrow", "shape_note": "Expect edits to the record move command, the removal check, the cleaner and watch briefs, the picture line and one CHANGELOG line, all in one area."}
budget: {"tokens": 580000, "usd": 4.51, "set_by": "Sean Kennedy"}
red: null
wall_baseline: {"commit": "9ce4a1f2ca5585f18db65f87b0480a9ef01cd954", "count": 100, "digest": "d25989a7c212eb4c", "file": ".xv/slices/2026-11-19-removal-line.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4021, "cache_read": 63049, "cache_write": 46453, "tokens": 50480, "usd": 0.0119, "turns": 4, "wall_s": 31.8, "session": "5d06cef4-97be-4796-a8f6-a996d8dc7597", "step": "forecaster", "at": "2026-11-20T02:25:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-removal-line/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 12035, "cache_read": 313632, "cache_write": 40069, "tokens": 52124, "usd": 0.312, "turns": 11, "wall_s": 81.4, "session": "a246e43c-3b93-4ae8-9554-c93acb07b5dd", "step": "scenario", "at": "2026-11-20T02:26:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-removal-line/02-scenario.out"}]
stops: [{"at": "2026-11-20T02:25:09+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-removal-line budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "as before, I accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-20T02:25:17+00:00", "pick": "other", "settled": "The budget is the forecast: 580,000 tokens and $4.51; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 580000, "usd": 4.51}}}, {"at": "2026-11-20T02:26:48+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The scenario agent did not cover 3. A removal committed before its move is recorded is taken (the pairing case): The record keeps no 'step began' commit and the command reads HEAD today; the scenario does not say how the start commit is found, so I could not write a test without guessing.", "answered_by": ["Sean Kennedy"], "answer": "1", "also": ["red_misses_scenario"], "options": [{"text": "Amend outcome 3 with how the start commit is found: xv step saves HEAD in the record as step_start ({agent, commit}) before the agent runs; xv pairing start saves HEAD on the pairing entry as start_commit. xv record move --slice-only reads the line from the open pairing's start_commit while a pairing is open, else from step_start; with neither (a session step, or a move outside any step) it reads HEAD, as now. Accept outcome 7 (the CHANGELOG line) with no test. Send back to the scenario agent for outcome 3's red", "settles": "Amendment 8: the start commit is step_start, or the open pairing's start_commit, else HEAD; outcome 7 has no test", "amends": true}, {"text": "Drop outcome 3 from this slice: the move must be recorded before the removal is committed, as now; file the pairing case as a follow-up issue. Accept outcome 7 with no test; go on to the maker", "settles": "Outcome 3 moves to a follow-up issue; outcome 7 has no test", "amends": true}], "recommended": 1, "answered_at": "2026-11-20T02:32:58+00:00", "sendback": true, "sendback_to": "scenario", "pick": 1, "settled": "Amendment 8: the start commit is step_start, or the open pairing's start_commit, else HEAD; outcome 7 (the CHANGELOG line) has no test", "new_info": "none", "cause": "decision: the scenario did not say how the start commit is found", "bundle": ["red_misses_scenario"]}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect; forecast about 340k sonnet and 190k opus tokens over two rounds, with a likely send-back at the removal check or its picture line.", "at": "2026-11-20T02:25:09+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for --line on slice-only removals, the tree-reading removal check with table cases, and the brief/picture lines; 12 of 15 tests fail on the current code.", "at": "2026-11-20T02:26:45+00:00"}], "forecaster": {"at": "2026-11-20T02:25:09+00:00", "wrote": [], "removal_not_made": []}, "scenario": {"at": "2026-11-20T02:26:45+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "e/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-19-removal-line/tests/helpers.py\", line 16, in sh\n    raise AssertionError(f\"{cmd} failed {p.returncode}: {p.stderr}{p.stdout}\")\nAssertionError: ['/usr/bin/python3', '/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-19-removal-line/bin/xv', 'record', 'move', 's1', '--file', 'tests/test_red.py', '--slice-only', '--line', '5', '--assertion', 'removed', '--why', 'slice-only; removed', '--by', 'cleaner'] failed 2: usage: xv record [-h]\n                 {new,show,get,set,add,move,unmark,override,stop,offer,answer,report,packet,export,guide-append,guide-verify} ...\nxv record: error: unrecognized arguments: --line 5\n\n\n----------------------------------------------------------------------\nRan 15 tests in 2.850s\n\nFAILED (failures=16)\n", "old_red_changed": [], "red_gaps": [], "covered_kept": [{"outcome": "1. `xv record move --slice-only` takes `--file` and `--line <n>`, reads the line's text from the start commit, refuses a blank line or a number past the end, and `--assertion` is a free note", "test": ["test_a_blank_line_is_refused_and_nothing_is_recorded", "test_a_number_past_the_end_of_the_file_is_refused_and_nothing_is_recorded", "test_a_line_that_is_not_a_positive_number_is_refused", "test_the_assertion_is_a_free_note_when_a_line_is_given", "test_the_line_is_read_from_the_file_at_the_start_not_the_tree_now"]}, {"outcome": "2. After a step, the removal check counts the line's text in the file now and stops with removal_not_made naming file, line number and text when the count is not lower", "test": ["test_a_line_whose_text_is_still_in_the_file_stops_naming_file_number_and_text", "test_a_line_whose_text_is_gone_passes", "test_the_note_is_not_read_by_the_check"]}, {"outcome": "4. A table test runs the check over a Python def, a JS it() with spaces, and a line in the file twice", "test": ["test_table_python_def_js_it_and_a_doubled_line", "test_the_js_title_with_spaces_is_named_in_the_stop"]}, {"outcome": "5. The cleaner's brief says how to give the line; the picture says what each check reads", "test": ["test_the_cleaner_brief_says_how_to_give_the_line", "test_the_picture_says_what_each_check_reads"]}, {"outcome": "6. The watch brief's stop table lists the change_misses_scenario: no stop; two slice-only moves for the same file and line are one move", "test": ["test_the_watch_brief_lists_the_stop_for_a_no_with_a_miss_listed", "test_two_slice_only_moves_for_one_file_and_line_are_one_move", "test_two_slice_only_moves_for_two_lines_are_two_moves"]}], "unreadable": [], "not_covered": [{"outcome": "3. A removal committed before its move is recorded is taken (the pairing case)", "why": "The record keeps no 'step began' commit and the command reads HEAD today; the scenario does not say how the start commit is found, so I could not write a test without guessing."}, {"outcome": "7. A line in CHANGELOG.md", "why": "slice-only: a one-time CHANGELOG line, not tested on the wall"}], "missed_outcomes": [], "removal_not_made": []}}
old_tests_to_move: [{"file": "tests/test_record.py", "test": "SliceOnlyAssertionFormTest (all tests that call move without --line)", "why": "--slice-only now needs --line, and --assertion is a free note, so the refusal of sentences and broken names no longer holds."}, {"file": "tests/test_record.py", "test": "RemovalCheckNamesTest", "why": "The removal check reads the line's text, not the name in the assertion, so these tests' data and assertions change."}, {"file": "tests/test_record.py", "test": "OneHomeRecordTest.test_a_move_the_command_and_a_report_both_record_is_one_move_with_its_flag", "why": "Its slice-only move gives no --line."}, {"file": "tests/test_record.py", "test": "CleanerBriefNoteTest.test_the_brief_says_the_note_is_the_tests_name_as_written_with_an_optional_bracketed_note", "why": "The brief now says the assertion is a free note and gives the line."}, {"file": "tests/test_record.py", "test": "tests that record a move with --slice-only near lines 312, 324, 421, 1021, 1029 and 1705", "why": "They call --slice-only without --line, which the command will refuse."}, {"file": "tests/test_run.py", "test": "tests that call record move --slice-only", "why": "They call --slice-only without --line, which the command will refuse."}, {"file": "tests/fake_agent.py", "test": "the fake agent's slice-only move command", "why": "It records a slice-only move with no --line."}]
may_not_files_needed: [{"file": ".xv/picture.md", "why": "The picture must say what each removal check reads: the line's text counted in the file now, and that the check on accepted slice-only marks finds a name as any whole word in the file."}]
reports_before_amend: 2
---
# A slice-only removal names its line, and the check reads the tree

## Scenario

A slice-only removal names its line, and the check reads the tree.

1. `xv record move --slice-only` takes `--file` and `--line <n>`: the line where the removed test starts, in the file at the commit where the step began (in a pairing, where the pairing began). The command reads that line's text from that commit and records the text with the number. It refuses a blank line, or a number past the end of the file, and records nothing. `--assertion` is a free note again; nothing reads it.
2. After a step, the removal check counts that line's text in the file now. If the count is not lower than at the start commit, the step stops with `removal_not_made`, naming the file, the line number and the text.
3. A removal committed before its move is recorded is taken (the pairing case).
4. A table test runs the check over a Python `def`, a JS `it("…")` whose title has spaces, and a line that is in the file twice: one copy removed passes; none removed stops.
5. The cleaner's brief says how to give the line. The picture says what each check reads, including that the check on accepted slice-only marks finds a name as any whole word in the file.
6. The watch brief's stop table lists the stop for a packet whose front matter says `change_misses_scenario: no` while its `## Scenario misses` section lists a miss. Two slice-only moves for the same file and line are one move.
7. A line in CHANGELOG.md.

### Amended 2026-11-19 by Sean Kennedy

8. Outcome 3's start commit: `xv step` saves HEAD in the record as `step_start` (`{"agent": ..., "commit": ...}`) before the agent runs, and `xv pairing start` saves HEAD on the pairing entry as `start_commit`. `xv record move --slice-only` reads the line from the open pairing's `start_commit` while a pairing is open, else from `step_start`; with neither (a `session` step, or a move outside any step) it reads HEAD, as now. A test commits a slice-only removal in a pairing, then records its move with `--line`, and the move is taken; the same test with no pairing and a `step_start` from before the removal is taken too. Not covered: a `session` step, which has no `step_start`, so there the move must still be recorded before the removal is committed. It loosens no may-not line.

## May ignore

- moves recorded before this change
- --deleted file removals
- moves that are not slice-only

## Recording

None. A feature starts from words.

## Log
- 2026-11-20T02:24:33+00:00 watch: slice opened by Sean Kennedy
- 2026-11-20T02:25:09+00:00 forecaster: done: Narrow defect; forecast about 340k sonnet and 190k opus tokens over two rounds, with a likely send-back at the removal check or its picture line.
- 2026-11-20T02:25:09+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-removal-line budget ... --by <name>`).
- 2026-11-20T02:25:17+00:00 Sean Kennedy: set budget
- 2026-11-20T02:25:17+00:00 Sean Kennedy: answered budget_not_set: as before, I accept the forecast unless it is wide
- 2026-11-20T02:25:17+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-20T02:26:45+00:00 scenario: red: Red for --line on slice-only removals, the tree-reading removal check with table cases, and the brief/picture lines; 12 of 15 tests fail on the current code.
- 2026-11-20T02:26:48+00:00 watch: stop (red_misses_scenario) for originator: The scenario agent did not cover 3. A removal committed before its move is recorded is taken (the pairing case): The record keeps no 'step began' commit and the command reads HEAD today; the scenario does not say how the start commit is found, so I could not write a test without guessing.
- 2026-11-20T02:27:11+00:00 watch: offered 2 options for red_misses_scenario
- 2026-11-20T02:32:58+00:00 Sean Kennedy: amended the scenario
- 2026-11-20T02:32:58+00:00 Sean Kennedy: answered red_misses_scenario: 1
- 2026-11-20T02:32:58+00:00 watch: scribe: wrote settled, new_info, cause for red_misses_scenario as the scribe of Sean Kennedy

---
id: 2026-11-06-covers-stall
title: "A missed point goes back with text the check accepts, and stops a person only on a real stall"
kind: defect
status: stopped
set_by: Sean
created: 2026-11-06
branch: xv/2026-11-06-covers-stall
base: 859d2262950dbf5235c68b263de288780436bfea
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 543000, "turns": null, "usd": 3.4, "basis": ["2026-10-30-covers-list", "2026-10-30-scenario-miss", "2026-11-04-scenario-catches", "2026-11-05-scenario-checks"], "note": "Mean of the four basis rows (range 304k to 715k tokens, $1.70 to $4.74). The guide records no turns."}, {"harness": "claude", "model": "opus", "tokens": 291000, "turns": null, "usd": 3.7, "basis": ["2026-10-30-covers-list", "2026-10-30-scenario-miss", "2026-11-04-scenario-catches", "2026-11-05-scenario-checks"], "note": "Mean of the same four rows (range 172k to 359k tokens, $2.00 to $4.87). The guide records no turns."}], "wall_s": 5250, "shape": "narrow", "breadth": "Expect the coverage match, the send-back wording and the red_misses_point counter to move, plus tests and one CHANGELOG line. The guardian's scenario_miss repeat check shares the sent_back field and is excluded, so touching it would widen the change. Wall is the sum of the sonnet and opus wall means (4277 s and 971 s), as the basis rows do. The budget is Sean's to set."}
budget: {"tokens": 840000, "usd": 7.1, "set_by": "Sean"}
red: {"files": ["tests/test_run.py"], "command": "cd tests && python3 -m unittest test_run.WatchLoopTest", "failure": "AssertionError: 'scenario' != 'maker' (an item without backticks does not cover the point that has them)", "watch_first_green": null}
wall_baseline: {"commit": "66cb5330832202d09fe2b6fea451ddab99863855", "count": 65, "digest": "f04d9142d56c6b81", "file": ".xv/slices/2026-11-06-covers-stall.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_run.py", "test": "test_the_changelog_has_a_line_for_the_red_misses_point_trigger", "why": "checks one CHANGELOG line, a one-time wording change", "checks": "CHANGELOG.md", "accepted": true}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 3213, "cache_read": 62187, "cache_write": 34077, "tokens": 37296, "usd": 0.009, "turns": 4, "wall_s": 17.5, "session": "aaacfae6-25b0-4685-9fd6-ead755538757", "step": "forecaster", "at": "2026-11-06T19:34:34+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-06-covers-stall/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 38, "tokens_out": 12093, "cache_read": 814686, "cache_write": 53067, "tokens": 65198, "usd": 0.4147, "turns": 21, "wall_s": 300.9, "session": "216d0a6f-42ff-4792-99a5-a4d7875ee3fc", "step": "scenario", "at": "2026-11-06T19:41:00+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-06-covers-stall/02-scenario.out"}]
stops: [{"at": "2026-11-06T19:34:34+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean: set the budget from the forecast (`xv record set 2026-11-06-covers-stall budget ... --by <name>`).", "answered_by": ["Sean"], "answer": "budget: 1. we will only do a sortie if needed", "also": [], "options": [{"text": "Budget as forecast: 840k tokens, $7.10", "settles": "The budget is 840000 tokens and $7.10, the forecast's two model keys added.", "amends": false}, {"text": "Forecast plus about 25 percent for one more guardian pass: 1.05M tokens, $9", "settles": "The budget is 1050000 tokens and $9.", "amends": false}, {"text": "Forecast plus about 55 percent, for two more rounds: 1.3M tokens, $11", "settles": "The budget is 1300000 tokens and $11.", "amends": false}], "recommended": 2, "answered_at": "2026-11-06T19:35:56+00:00", "pick": 1, "settled": "The budget is 840000 tokens and $7.10, the forecast's two model keys added.", "new_info": "none", "cause": "decision: the budget is the person's to set", "budget_change": {"from": null, "to": {"tokens": 840000, "usd": 7.1}}}, {"at": "2026-11-06T19:42:35+00:00", "step": "scenario", "order": "unrecorded_move", "seat": "originator", "question": "The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/test_run.py. Revert them, or record why the scenario forces it.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 840000, "usd": 7.1, "set_by": "Sean"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from four scenario and covers-list rows: sonnet about 543k tokens and opus about 291k, with wall about 5250 s in total; shape narrow.", "at": "2026-11-06T19:34:34+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red tests for the coverage match ignoring Markdown marks, the third-miss stop, the run-of-passes count, the send-back wording and the CHANGELOG line.", "at": "2026-11-06T19:41:00+00:00"}], "forecaster": {"at": "2026-11-06T19:34:34+00:00", "wrote": []}, "scenario": {"at": "2026-11-06T19:41:00+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": " --- ## this run - repository checkout: `/tmp/xv-test-7ideacle/repo/.xv/worktrees/s1`. work only inside it. - slice record: `.xv/slices/s1.md`. read it first. do not edit it; your report block is how you write to it. - base commit: `6721af438809b38c72fb6065c41fdfa75222aee8`. the slice\\'s diff is `git diff 6721af438809b38c72fb6065c41fdfa75222aee8..head` plus any uncommitted changes. - the red: files tests/test_red.py; command `python3 -m unittest tests.test_red`. - whole suite: `python3 -m unittest discover -s tests -t .`. - test paths (the wall): tests/**. - the `xv` command: `xv`. - end your final message with the `xv-report` block your brief describes. nothing after it.'\n\n----------------------------------------------------------------------\nRan 100 tests in 94.725s\n\nFAILED (failures=9)\n", "old_red_changed": ["tests/test_run.py"], "red_gaps": [], "covers_kept": [{"item": "1", "test": ["test_the_send_back_hands_over_the_point_as_an_item_the_check_accepts", "test_an_item_without_the_backticks_covers_the_point_that_has_them"]}, {"item": "2", "test": ["test_the_send_back_says_every_point_goes_in_covers_or_not_covered_each_pass"]}, {"item": "3", "test": ["test_an_item_without_the_backticks_covers_the_point_that_has_them", "test_an_item_without_stars_and_underscores_covers_the_point_that_has_them", "test_the_marks_come_off_the_item_too", "test_an_item_that_changes_a_word_still_does_not_cover_the_point"]}, {"item": "4", "test": ["test_the_same_missed_point_on_the_next_pass_goes_back_again", "test_the_third_miss_in_a_row_of_the_same_point_stops_for_the_person"]}, {"item": "5", "test": ["test_a_point_sent_back_twice_then_covered_then_missed_again_goes_back", "test_send_backs_from_before_an_amendment_do_not_count_toward_the_stop", "test_send_backs_from_before_a_persons_answer_do_not_count_toward_the_stop"]}, {"item": "6", "test": ["test_the_changelog_has_a_line_for_the_red_misses_point_trigger"]}], "unreadable": [], "not_covered": [], "missed_points": []}}
old_tests_forced: [{"file": "tests/test_run.py", "test": "test_the_same_missed_point_on_the_next_pass_stops_for_the_person", "why": "Point 4: a second miss in a row now goes back; only the third stops. Renamed to test_the_same_missed_point_on_the_next_pass_goes_back_again and now asserts a send-back with no stop."}]
may_not_files: []
---
# A missed point goes back with text the check accepts, and stops a person only on a real stall

## Scenario

When the scenario step leaves a numbered point out of both `covers` and `not_covered`, the watch sends the slice back, and the scenario agent can fix it on the next pass. A person is stopped only when the agent truly cannot cover a point.

1. The send-back hands the scenario agent, for each missed point, an `item` string the check will accept, ready to put in `covers` or `not_covered`: the point's number and its text, as the scenario has it.
2. The send-back says that every point of the scenario and its amendments goes in `covers` or `not_covered` on each pass, not only the points of the newest amendment.
3. The coverage check removes Markdown marks (backticks, `*`, `_`) from both the point and the `item` before it compares them. An item "The doc kind refuses a file under .xv/" covers the point "The `doc` kind refuses a file under `.xv/`".
4. A point missed again right after a send-back for that same point goes back once more. The person who set the work going is stopped as `red_misses_point` only on the third miss in a row.
5. Only the send-backs of the run of passes that ends now count toward that stop. A send-back from before an amendment or before a person's answer does not count. A point sent back two passes ago, then covered, then missed again, goes back; it does not stop the person.
6. The change to the `red_misses_point` trigger has a `CHANGELOG.md` line.

## May ignore

The guardian's scenario_miss repeat check: it also uses sent_back (scripts/orders.py:274), and its behavior stays the same. Other ways the text match can fail, such as a reworded point. A refactor slice's own points: they have no red.

## Recording

.xv/recordings/2026-11-06-covers-stall.md

## Log
- 2026-11-06T19:34:08+00:00 watch: slice opened by Sean
- 2026-11-06T19:34:34+00:00 forecaster: done: Forecast from four scenario and covers-list rows: sonnet about 543k tokens and opus about 291k, with wall about 5250 s in total; shape narrow.
- 2026-11-06T19:34:34+00:00 watch: stop (budget_not_set) for originator: Sean: set the budget from the forecast (`xv record set 2026-11-06-covers-stall budget ... --by <name>`).
- 2026-11-06T19:34:44+00:00 watch: offered 3 options for budget_not_set
- 2026-11-06T19:35:56+00:00 Sean: set budget
- 2026-11-06T19:35:56+00:00 Sean: answered budget_not_set: budget: 1. we will only do a sortie if needed
- 2026-11-06T19:35:56+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean
- 2026-11-06T19:41:00+00:00 scenario: red: Red tests for the coverage match ignoring Markdown marks, the third-miss stop, the run-of-passes count, the send-back wording and the CHANGELOG line.
- 2026-11-06T19:41:00+00:00 watch: slice-only mark on test_the_changelog_has_a_line_for_the_red_misses_point_trigger accepted: it checks CHANGELOG.md, which the config lists in tests.slice_only_files
- 2026-11-06T19:42:35+00:00 watch: stop (unrecorded_move) for originator: The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/test_run.py. Revert them, or record why the scenario forces it.

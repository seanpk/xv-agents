---
id: 2026-11-24-cleaner-commit
title: "The watch commits the cleaner's work, as it does the maker's (#206)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-cleaner-commit
base: d4011e47fc52d2c5fbf8fdb6b80f6e0543cbf462
next: test-writer
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 2.3, "basis": ["2026-11-19-wall-keep", "2026-11-18-move-names", "2026-11-19-removal-line", "2026-11-20-names"]}, {"harness": "claude", "model": "opus", "tokens": 170000, "turns": null, "usd": 2.2, "basis": ["2026-11-18-move-names", "2026-11-19-removal-line", "2026-11-16-red-lands", "2026-11-19-wall-keep"]}, {"harness": "claude", "model": "haiku", "tokens": 55000, "turns": null, "usd": 0.01, "basis": ["2026-11-20-names", "2026-11-19-removal-line", "2026-11-19-wall-keep", "2026-11-19-pick-tests"]}], "wall_s": 1400, "rounds": 2, "rounds_reason": "The commit move changes what the cleaner leaves behind, and the inspector sent narrow defects back once in move-names and removal-line; wall-keep is the one-pass floor.", "shape_breadth": "narrow", "shape_note": "Touches the watch's commit step, the cleaner brief, docs, one new decision row and one CHANGELOG line; the agent set does not change."}
budget: {"tokens": 575000, "usd": 4.51, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_cleaner_commit.py"], "command": "cd tests && python3 -m unittest test_cleaner_commit", "failure": "AssertionError: None != <head sha> (cleaner_commit is empty after the cleaner left its edit uncommitted)", "watch_before_merge": "Run a slice through the cleaner with a real agent and see the cleaner's edit sit uncommitted in the tree until `xv step` makes `xv(<id>): record the cleaner's pass`, and `cleaner_commit` in the record name that commit."}
wall_baseline: {"commit": "1664ac0943dfe8715b9717e86bf6c5e460a8e6bd", "count": 104, "digest": "e6f807d745f2fe1d", "file": ".xv/slices/2026-11-24-cleaner-commit.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_cleaner_commit.py", "test": "TheChangelogTest.test_an_unreleased_line_says_the_watch_commits_the_cleaners_work", "why": "checks one CHANGELOG line, which has no value after the slice", "checks": "CHANGELOG.md", "accepted": true}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6267, "cache_read": 63278, "cache_write": 47748, "tokens": 54021, "usd": 0.0133, "turns": 4, "wall_s": 29.6, "session": "dbe8d650-3916-4ccc-9ddd-96c658aebb5a", "step": "forecaster", "at": "2026-11-24T14:03:05+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-cleaner-commit/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 46, "tokens_out": 12898, "cache_read": 1087056, "cache_write": 56302, "tokens": 69246, "usd": 0.463, "turns": 2, "wall_s": 274.4, "session": "3c17ee92-1d96-4a17-95e2-e83cccc2bd18", "step": "test-writer", "at": "2026-11-24T14:07:54+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-24-cleaner-commit/02-test-writer.out"}]
stops: [{"at": "2026-11-24T14:03:05+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-cleaner-commit budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Standing answer: accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-24T14:03:16+00:00", "pick": "other", "settled": "Sean sets budget {tokens: 575000, usd: 4.51}, the forecast (narrow); next is test-writer.", "new_info": "none", "cause": "decision: Sean's standing answer accepts a forecast that is not wide", "budget_change": {"from": null, "to": {"tokens": 575000, "usd": 4.51}}}, {"at": "2026-11-24T14:07:57+00:00", "step": "test-writer", "order": "unrecorded_move", "seat": "originator", "question": "The test writer changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.", "answered_by": [], "answer": null, "also": ["red_misses_scenario"], "budget_seen": {"tokens": 575000, "usd": 4.51, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Defect, narrow: about 350k sonnet and 170k opus tokens over two rounds, $4.5 total, 1400 s wall, with a send-back as the main risk.", "at": "2026-11-24T14:03:05+00:00"}, {"agent": "test-writer", "status": "red", "summary": "Red for the watch committing the cleaner's work: the commit, cleaner_commit, the brief, the docs and the new decision all fail on current code.", "at": "2026-11-24T14:07:54+00:00"}], "forecaster": {"at": "2026-11-24T14:03:05+00:00", "wrote": [], "removal_not_made": []}, "test-writer": {"at": "2026-11-24T14:07:54+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "commit.TheWatchCommitsTheCleanersWorkTest.test_cleaner_commit_stays_empty_when_the_cleaner_changed_nothing)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-24-cleaner-commit/tests/test_cleaner_commit.py\", line 60, in test_cleaner_commit_stays_empty_when_the_cleaner_changed_nothing\n    self.assertEqual(self.head(), before)\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 'f26c66cffd749abd14842c74c1a0ba38bf65e844' != 'dfe35bd4290e282fa8d469aecf72e7dbb7ec96ad'\n- f26c66cffd749abd14842c74c1a0ba38bf65e844\n+ dfe35bd4290e282fa8d469aecf72e7dbb7ec96ad\n\n\n----------------------------------------------------------------------\nRan 16 tests in 2.712s\n\nFAILED (failures=13)\n", "old_red_changed": ["tests/fake_agent.py"], "red_gaps": [], "covered_kept": [{"outcome": "1", "test": ["TheWatchCommitsTheCleanersWorkTest.test_the_watch_commits_what_the_cleaner_left_uncommitted", "TheCleanerBriefTest.test_the_brief_says_to_leave_changes_uncommitted_for_the_watch_to_commit_after_its_checks", "TheCleanerBriefTest.test_the_may_not_list_has_commit_merge_or_push", "TheCleanerBriefTest.test_the_brief_no_longer_tells_the_cleaner_to_commit_its_fix"]}, {"outcome": "2", "test": ["TheCleanerBriefTest.test_the_brief_still_has_the_cleaner_record_each_move", "TheCleanerBriefTest.test_the_brief_no_longer_says_the_pre_commit_hook_refuses_a_move"]}, {"outcome": "3", "test": ["TheWatchCommitsTheCleanersWorkTest.test_cleaner_commit_names_the_commit_the_watch_made", "TheWatchCommitsTheCleanersWorkTest.test_cleaner_commit_stays_empty_when_the_cleaner_changed_nothing", "TheWatchCommitsTheCleanersWorkTest.test_a_report_that_still_sends_a_commit_is_not_refused_and_is_not_believed", "TheCleanerBriefTest.test_the_report_example_has_no_commit_field", "TheDocsDoNotSayTheCleanerCommitsTest.test_the_slice_record_doc_says_cleaner_commit_is_the_commit_the_watch_made_after_the_cleaner"]}, {"outcome": "4", "test": ["TheDocsDoNotSayTheCleanerCommitsTest.test_no_readme_doc_or_picture_line_says_the_cleaner_commits", "TheDocsDoNotSayTheCleanerCommitsTest.test_the_readme_no_longer_says_the_pre_commit_hook_refuses_the_cleaners_unrecorded_move", "TheDecisionRowTest.test_a_new_numbered_decision_says_the_watch_commits_each_steps_work", "TheDecisionRowTest.test_decision_7_stays_as_history"]}], "unreadable": [], "not_covered": [{"outcome": "5", "why": "A CHANGELOG line is slice-only; its test, test_an_unreleased_line_says_the_watch_commits_the_cleaners_work, is marked slice_only."}], "missed_outcomes": [], "removal_not_made": []}}
step_start: {"agent": "test-writer", "commit": "1664ac0943dfe8715b9717e86bf6c5e460a8e6bd", "ended": true}
old_tests_to_move: []
may_not_files_needed: [{"file": ".xv/picture.md", "why": "the scenario says the picture no longer says the cleaner commits; a picture line may need rewording, and the maker may change only that file from the may-not list"}]
---
# The watch commits the cleaner's work, as it does the maker's (#206)

## Scenario

The watch commits the cleaner's work, as it does the maker's (#206).

1. The cleaner's brief says to leave its changes uncommitted: the watch commits them after its checks. Its may-not list has "Commit, merge, or push", as the maker's does.
2. The cleaner still records each test move with `xv record move` before its step ends. The brief no longer says the pre-commit hook refuses a move with no record; it says the wall check after the step stops on one.
3. `cleaner_commit` in the record names the commit `xv step` makes after the cleaner (`xv(<id>): record the cleaner's pass`), and stays empty when the cleaner changed nothing. The brief's report has no `commit` field; a report that still sends one is not refused.
4. README, the docs and the picture no longer say the cleaner commits. A new numbered decision in `docs/decisions.md` says the watch commits each step's work; decision 7 stays as history.
5. A line in `CHANGELOG.md`.

## May ignore

old records where cleaner_commit is empty; harnesses with no allow-list

## Recording

None. A feature starts from words.

## Log
- 2026-11-24T14:02:29+00:00 watch: slice opened by Sean Kennedy
- 2026-11-24T14:03:05+00:00 forecaster: done: Defect, narrow: about 350k sonnet and 170k opus tokens over two rounds, $4.5 total, 1400 s wall, with a send-back as the main risk.
- 2026-11-24T14:03:05+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-24-cleaner-commit budget ... --by <name>`).
- 2026-11-24T14:03:16+00:00 Sean Kennedy: set budget
- 2026-11-24T14:03:16+00:00 Sean Kennedy: answered budget_not_set: Standing answer: accept the forecast unless it is wide
- 2026-11-24T14:03:16+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-24T14:07:54+00:00 test-writer: red: Red for the watch committing the cleaner's work: the commit, cleaner_commit, the brief, the docs and the new decision all fail on current code.
- 2026-11-24T14:07:54+00:00 watch: slice-only mark on TheChangelogTest.test_an_unreleased_line_says_the_watch_commits_the_cleaners_work accepted: it checks CHANGELOG.md, which the config lists in tests.slice_only_files
- 2026-11-24T14:07:57+00:00 watch: stop (unrecorded_move) for originator: The test writer changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.

---
id: 2026-11-18-report-tree
title: "What an agent reports is checked against the tree (#183)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-17
branch: xv/2026-11-18-report-tree
base: 5c2600c69d4d50853dcd288bd6278c48bd808657
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 2.3, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend", "2026-11-09-retro-fixes", "2026-11-09-defects-stops"]}, {"harness": "claude", "model": "opus", "tokens": 220000, "turns": null, "usd": 2.5, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend", "2026-11-09-retro-fixes", "2026-11-09-defects-stops"]}, {"harness": "claude", "model": "haiku", "tokens": 45000, "turns": null, "usd": 0.01, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend"]}], "wall_s": 2000, "rounds": 2, "rounds_reason": "The removal clause and the reader fallback are points the guardian has sent back before on narrow defects (red-lands ran three send-backs, defects-tools two guardian passes), so one send-back is likely rather than certain.", "shape_breadth": "narrow", "shape_note": "Touches the post-step and post-move checks in the step runner and the harness report reader, plus tests and one CHANGELOG line; this turns wide only if the reader change reaches more than the claude harness."}
budget: {"tokens": 615000, "usd": 4.81, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_run.py", "tests/fake_agent.py"], "command": "cd tests && python3 -m unittest test_run.RemovalNotMadeTest", "failure": "AssertionError: 0 != 10 (the cleaner step ends with no stop while a slice-only test is still in its file)", "watch_before_merge": null}
wall_baseline: {"commit": "f3ee691be41f96b280f7edc012a5a52dc29084b2", "count": 99, "digest": "b23b7ccb94b847df", "file": ".xv/slices/2026-11-18-report-tree.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_run.py", "test": "RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check", "why": "checks one CHANGELOG line, a one-time wording change", "checks": "CHANGELOG.md", "accepted": true}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5848, "cache_read": 63652, "cache_write": 41924, "tokens": 47778, "usd": 0.0119, "turns": 4, "wall_s": 26.1, "session": "d17f01d8-4250-45d5-ad04-77073b7daf2e", "step": "forecaster", "at": "2026-11-18T03:55:18+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-report-tree/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 44, "tokens_out": 15679, "cache_read": 1098452, "cache_write": 69155, "tokens": 84878, "usd": 0.5433, "turns": 27, "wall_s": 213.5, "session": "3c9a11ca-7898-45a1-8ece-7ee35c08e7bd", "step": "scenario", "at": "2026-11-18T03:59:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-report-tree/02-scenario.out"}]
stops: [{"at": "2026-11-18T03:55:18+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-report-tree budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "go, accept the forecast - stop only for me if it is wide", "also": [], "answered_at": "2026-11-18T03:55:31+00:00", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 615000, "usd": 4.81}}}, {"at": "2026-11-18T03:59:38+00:00", "step": "scenario", "order": "unrecorded_move", "seat": "originator", "question": "The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 615000, "usd": 4.81, "set_by": "Sean Kennedy"}, "options": [{"text": "Record the tests/fake_agent.py change as a move in Sean Kennedy's name: the fake agent gains three modes the red needs (FAKE_EARLIER_REPORT, FAKE_CLEANER_REMOVES, FAKE_CLEANER_REPORT_EXTRA), each off unless its variable is set, so its default output is unchanged; go on to the maker", "settles": "the fake agent's new modes are recorded; the red stands", "amends": false}, {"text": "Send back to the scenario agent: revert tests/fake_agent.py and put the new fake modes in a new helper file, so no old test file changes", "settles": "no old test file changes; the fake modes live in a new file", "amends": false}], "recommended": 1}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect with a likely send-back: sonnet ~350k tokens, opus ~220k, forecaster haiku ~45k, wall ~2000 s across keys.", "at": "2026-11-18T03:55:18+00:00"}, {"agent": "scenario", "status": "red", "summary": "Six tests fail: no removal_not_made after the cleaner or after any step, no reader fallback to an earlier report, no CHANGELOG line.", "at": "2026-11-18T03:59:09+00:00"}], "forecaster": {"at": "2026-11-18T03:55:18+00:00", "wrote": []}, "scenario": {"at": "2026-11-18T03:59:09+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "rd alone, and `xv step`, `xv run`, `xv record packet` and the session path leave the same verdict: one function applies what `orders` returns, including where `next` goes. A shape the person accepted does not stop again as `shape_wider_than_forecast`; `accept_moves` counts moves, not record entries; a slice-only mark the person accepted is not asked about again; one move is recorded once; the pre-step `budget_spent` stop and `prototype_budget_spent` follow the `--settled` rule; a new decision writes `who` as a list. A test fails when the docs miss an allowed value of `shape_change` or `pitch_contradiction`. Decided by Sean, solo. It moves no position on xtremevibing.com.\\n'\n\n----------------------------------------------------------------------\nRan 10 tests in 28.890s\n\nFAILED (failures=6)\n", "old_red_changed": ["tests/fake_agent.py"], "red_gaps": [], "covered_kept": [{"outcome": "1", "test": ["RemovalNotMadeTest.test_a_slice_only_test_still_in_its_file_after_the_cleaner_stops_naming_file_and_test", "RemovalNotMadeTest.test_a_slice_only_test_the_cleaner_removed_passes", "RemovalNotMadeTest.test_a_slice_only_test_the_cleaner_says_it_kept_and_why_passes", "RemovalNotMadeTest.test_a_kept_test_with_no_why_still_stops"]}, {"outcome": "2", "test": ["RemovalNotMadeTest.test_a_slice_only_move_for_a_test_still_there_stops_the_next_step", "RemovalNotMadeTest.test_a_deleted_move_for_a_file_still_there_stops_the_next_step", "RemovalNotMadeTest.test_a_slice_only_move_for_a_test_that_is_gone_does_not_stop_a_later_step"]}, {"outcome": "3", "test": ["RemovalNotMadeTest.test_a_report_in_an_earlier_message_is_read_when_the_last_has_none", "RemovalNotMadeTest.test_a_run_with_no_report_block_in_any_message_still_stops_with_no_report"]}, {"outcome": "4", "test": ["RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check"]}], "unreadable": [], "not_covered": [], "missed_outcomes": []}}
old_tests_to_move: [{"file": "tests/test_codex_step.py", "test": "CodexReportTest.test_a_report_in_an_earlier_message_is_not_the_report_when_the_last_has_none", "why": "only if the maker puts the whole-run fallback inside record.extract_report; it asserts extract_report returns None there. Keeping the fallback in a separate reader leaves it as it is"}]
may_not_files_needed: []
---
# What an agent reports is checked against the tree (#183)

## Scenario

What an agent reports is checked against the tree.

1. After the cleaner step, each accepted `slice_only` test still in its file stops the step with `removal_not_made` for the person who set the work going, naming the file and the test, unless the cleaner's report says it kept that test and why. A removal that was made passes.
2. After any step, a move on the record that says a test or a file was removed (`--slice-only` or `--deleted`) while that test or file is still there stops the step with `removal_not_made` for the person who set the work going, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last `xv-report` block of the whole run, through the harness's own reader, before it stops with `no_report`. The core still names no agent. A run with no report block anywhere still stops with `no_report`.
4. A line in CHANGELOG.md.

## May ignore

- old slice records
- a harness whose reader cannot see earlier messages: it stops with no_report, as now

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T03:54:46+00:00 watch: slice opened by Sean Kennedy
- 2026-11-18T03:55:18+00:00 forecaster: done: Narrow defect with a likely send-back: sonnet ~350k tokens, opus ~220k, forecaster haiku ~45k, wall ~2000 s across keys.
- 2026-11-18T03:55:18+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-report-tree budget ... --by <name>`).
- 2026-11-18T03:55:31+00:00 Sean Kennedy: set budget
- 2026-11-18T03:55:31+00:00 Sean Kennedy: answered budget_not_set: go, accept the forecast - stop only for me if it is wide
- 2026-11-18T03:55:31+00:00 watch: scribe: wrote new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-18T03:59:09+00:00 scenario: red: Six tests fail: no removal_not_made after the cleaner or after any step, no reader fallback to an earlier report, no CHANGELOG line.
- 2026-11-18T03:59:09+00:00 watch: slice-only mark on RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check accepted: it checks CHANGELOG.md, which the config lists in tests.slice_only_files
- 2026-11-18T03:59:38+00:00 watch: stop (unrecorded_move) for originator: The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.
- 2026-11-18T03:59:55+00:00 watch: offered 2 options for unrecorded_move

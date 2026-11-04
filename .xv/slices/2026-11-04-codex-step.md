---
id: 2026-11-04-codex-step
title: "Codex runs as a step, and #115"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-codex-step
base: 704f635e0b022b847e338a744d9415165be7fd20
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 200000, "turns": null, "usd": 1.0, "basis": ["2026-11-03-codex-spend", "2026-10-27-allowed-commands"], "note": "turns not recorded in the guide; the reopen risk on the Codex event shape is unpriced beyond this band"}, {"harness": "claude", "model": "opus", "tokens": 130000, "turns": null, "usd": 1.7, "basis": ["2026-11-03-codex-spend", "2026-10-27-allowed-commands"], "note": "turns not recorded in the guide; usd priced from the basis rows because opus usd runs high per token"}], "wall_s": 900, "shape": "narrow", "breadth": "Touches the step report reader, the eval runner's final-message path, session_of, harnesses.json, three docs and one relies-on line; each change is additive, and the claude, opencode and grok paths should not move."}
budget: {"tokens": 330000, "usd": 2.7, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_codex_step.py"], "command": "cd tests && python3 -m unittest test_codex_step", "failure": "AssertionError: None != {'agent': 'maker', 'status': 'green', 'summary': 'ok'}", "watch_first_green": "Run a real `codex exec --json` step: its xv-report should land in the record, the spend row's session should be the thread_id, and the eval runner's final message should be the agent's last words, not a pile of events."}
wall_baseline: {"commit": "dc9e3b33571a63f8778fcc734cf6beac94686edb", "count": 59, "digest": "5a3a981277498e16", "file": ".xv/slices/2026-11-04-codex-step.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_codex_step.py", "test": "CodexDocsTest.test_readme_no_longer_says_codex_was_not_run", "why": "Pins README line numbers and old wording; its value ends once the README is corrected."}, {"file": "tests/test_codex_step.py", "test": "CodexDocsTest.test_decision_48_says_spend_reads_codex_events_and_codex_reports_no_dollars", "why": "Checks that one doc item was reworded; no value after the slice."}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4644, "cache_read": 25522, "cache_write": 23150, "tokens": 27798, "usd": 0.0072, "turns": 3, "wall_s": 24.8, "session": "f433f962-301b-4c5e-a440-72c5ac46d5ce", "step": "forecaster", "at": "2026-11-04T13:10:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-codex-step/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 7972, "cache_read": 288416, "cache_write": 36722, "tokens": 44714, "usd": 0.2555, "turns": 12, "wall_s": 56.1, "session": "aea0a499-2dd6-4340-a392-fcb63b7c9bfd", "step": "scenario", "at": "2026-11-04T13:12:49+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-codex-step/02-scenario.out"}]
stops: [{"at": "2026-11-04T13:10:21+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-codex-step budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "330000 tokens, 2.70 USD: the forecast", "settles": "Sean sets budget {tokens: 330000, usd: 2.7}; next is scenario.", "amends": false}, {"text": "420000 tokens, 3.50 USD: the forecast plus about a quarter", "settles": "Sean sets budget {tokens: 420000, usd: 3.5}; next is scenario.", "amends": false}, {"text": "Set aside", "settles": "The slice stays at its budget stop.", "amends": false}], "recommended": 1, "answered_at": "2026-11-04T13:11:53+00:00", "pick": 1, "settled": "Sean sets budget {tokens: 330000, usd: 2.7}; next is scenario.", "new_info": "none", "cause": "decision: Sean set the budget at the forecast", "budget_change": {"from": null, "to": {"tokens": 330000, "usd": 2.7}}}, {"at": "2026-11-04T13:12:49+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The scenario names these in backticks, and no red file has them: `xv check drift`. Add a test that reaches each, or amend the scenario.", "answered_by": [], "answer": null, "also": ["slice_only_marks"], "budget_seen": {"tokens": 330000, "usd": 2.7, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~200k tokens and opus ~130k for a narrow feature, basing both on the two closest claude rows; no codex history is needed because no codex agent runs on this slice.", "at": "2026-11-04T13:10:21+00:00"}, {"agent": "scenario", "status": "red", "summary": "Twelve tests in tests/test_codex_step.py cover the six points; ten fail on the code as it is: no codex report reading, no thread_id session, no harness entry, docs unchanged.", "at": "2026-11-04T13:12:49+00:00"}], "forecaster": {"at": "2026-11-04T13:10:21+00:00", "wrote": []}, "scenario": {"at": "2026-11-04T13:12:49+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "================================\nFAIL: test_session_of_a_codex_run_is_the_thread_id (test_codex_step.CodexSessionTest.test_session_of_a_codex_run_is_the_thread_id)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-04-codex-step/tests/test_codex_step.py\", line 60, in test_session_of_a_codex_run_is_the_thread_id\n    self.assertEqual(agentcli.session_of(\"codex\", codex_events(\"hi\", thread=\"019a-abc\")), \"019a-abc\")\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: None != '019a-abc'\n\n----------------------------------------------------------------------\nRan 12 tests in 0.139s\n\nFAILED (failures=6, errors=4)\n", "old_red_changed": [], "red_gaps": ["xv check drift"], "unreadable": [], "not_covered": [], "missed_points": ["3. `evals/harnesses.json` has a `codex` entry: `codex exec --json` with the model `gpt-6.1-terra` and the sandbox off (`--dangerously-bypass-approvals-and-sandbox`). Every step runs on that one model, as the `claude` entry runs Sonnet; Terra stands for Sonnet, Sol for Opus. Grok also runs with its permission checks off, and each eval runs on a throwaway copy of the fixture. The entry's note says that the brief is not the whole prompt, because `AGENTS.md` and the skills load.", "4. `README.md:3` and `:392` and `docs/decisions.md` item 48 say what is true now: Codex runs headless, `spend.py` reads its `--json` events, and Codex reports no dollars.", "5. `docs/relies-on.md` has a line for the Codex event shape that `spend.py` and the report reader use, so `xv check drift` watches it.", "6. `session_of` returns the `thread_id` for a Codex run."], "missed_repeat": false}}
---
# Codex runs as a step, and #115

## Scenario

# Codex runs as a step, and #115

When this is done:

1. A step run with `codex exec --json` gets its `xv-report` applied to the record, the same as Claude, Grok and opencode. The report is in the last `agent_message` of an `item.completed` event.
2. For a Codex run, the eval runner's final message is Codex's last `agent_message`.
3. `evals/harnesses.json` has a `codex` entry: `codex exec --json` with the model `gpt-6.1-terra` and the sandbox off (`--dangerously-bypass-approvals-and-sandbox`). Every step runs on that one model, as the `claude` entry runs Sonnet; Terra stands for Sonnet, Sol for Opus. Grok also runs with its permission checks off, and each eval runs on a throwaway copy of the fixture. The entry's note says that the brief is not the whole prompt, because `AGENTS.md` and the skills load.
4. `README.md:3` and `:392` and `docs/decisions.md` item 48 say what is true now: Codex runs headless, `spend.py` reads its `--json` events, and Codex reports no dollars.
5. `docs/relies-on.md` has a line for the Codex event shape that `spend.py` and the report reader use, so `xv check drift` watches it.
6. `session_of` returns the `thread_id` for a Codex run.

## May ignore

Running the evals (after the merge, at Sean's direction); a clean Codex baseline; Codex dollars and a budget cap; #112; Cursor.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T13:09:52+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T13:10:21+00:00 forecaster: done: Forecast sonnet ~200k tokens and opus ~130k for a narrow feature, basing both on the two closest claude rows; no codex history is needed because no codex agent runs on this slice.
- 2026-11-04T13:10:21+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-codex-step budget ... --by <name>`).
- 2026-11-04T13:10:25+00:00 watch: offered 3 options for budget_not_set
- 2026-11-04T13:11:53+00:00 Sean Kennedy: set budget
- 2026-11-04T13:11:53+00:00 Sean Kennedy: answered budget_not_set: 1
- 2026-11-04T13:11:53+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-04T13:12:49+00:00 scenario: red: Twelve tests in tests/test_codex_step.py cover the six points; ten fail on the code as it is: no codex report reading, no thread_id session, no harness entry, docs unchanged.
- 2026-11-04T13:12:49+00:00 watch: stop (red_misses_scenario) for originator: The scenario names these in backticks, and no red file has them: `xv check drift`. Add a test that reaches each, or amend the scenario.

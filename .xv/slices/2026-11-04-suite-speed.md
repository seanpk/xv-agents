---
id: 2026-11-04-suite-speed
title: "The test suite runs each test once, in parallel (#131)"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-suite-speed
base: 168693608141b7cca549d5e56eebd4a61e9bd3fb
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.7, "basis": ["2026-10-27-slice-tests", "2026-11-04-retro-sighting", "2026-11-04-codex-step"]}, {"harness": "claude", "model": "opus", "tokens": 210000, "turns": null, "usd": 2.5, "basis": ["2026-10-27-slice-tests", "2026-11-04-retro-sighting", "2026-11-04-codex-step"]}], "wall_s": 2400, "shape": "wide", "breadth": "New tests/run.py runner, .xv/config.yml suite command, the tests CI workflow matrix, and the maker and cleaner briefs; tests/** is the wall. Reopen risk (2-4 rounds in most guide rows) is not priced."}
budget: {"tokens": 1000000, "usd": 8.5, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_suite_runner.py"], "command": "cd tests && python3 -m unittest -q test_suite_runner", "failure": "FileNotFoundError: tests/run.py does not exist (runner tests); AssertionError: tests are collected more than once; '--shard' not found in tests.yml", "watch_first_green": "Run the real suite as shards 1/3, 2/3 and 3/3 with --jobs 2. Together they should be one full run with no test twice, and two processes should run side by side."}
wall_baseline: {"commit": "f315bd816c9aa2e7810d6d7627353677cbfec336", "count": 60, "digest": "ba56348072789d17", "file": ".xv/slices/2026-11-04-suite-speed.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_suite_runner.py", "test": "WiringTest.test_the_maker_and_cleaner_briefs_say_run_narrow_while_working_and_the_suite_once", "why": "Checks a one-time wording change in two briefs."}, {"file": "tests/test_suite_runner.py", "test": "WiringTest.test_the_config_suite_command_runs_the_runner_with_jobs", "why": "Checks a one-time change to the config command line."}, {"file": "tests/test_suite_runner.py", "test": "WiringTest.test_ci_runs_the_suite_in_shards_as_a_matrix_on_both_pythons", "why": "Checks a one-time change to the CI workflow text."}, {"file": "tests/test_suite_runner.py", "test": "WiringTest.test_ci_does_not_run_the_whole_suite_unsharded", "why": "Checks a one-time change to the CI workflow text."}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3077, "cache_read": 26137, "cache_write": 26636, "tokens": 29717, "usd": 0.0071, "turns": 3, "wall_s": 15.9, "session": "9bc5ceb2-58e7-469c-b900-549fdaed6390", "step": "forecaster", "at": "2026-11-05T04:49:03+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-suite-speed/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 28, "tokens_out": 13615, "cache_read": 407260, "cache_write": 32037, "tokens": 45680, "usd": 0.3051, "turns": 18, "wall_s": 85.8, "session": "cad398f9-d431-4376-b4e5-a33a0f848c0c", "step": "scenario", "at": "2026-11-05T04:51:18+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-suite-speed/02-scenario.out"}]
stops: [{"at": "2026-11-05T04:49:03+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-suite-speed budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "2", "also": [], "options": [{"text": "One pass, as forecast: 510000 tokens, $4.20", "settles": "budget {tokens: 510000, usd: 4.2}", "amends": false}, {"text": "Room for one reopen: 1000000 tokens, $8.50", "settles": "budget {tokens: 1000000, usd: 8.5}", "amends": false}], "recommended": 2, "answered_at": "2026-11-05T04:49:49+00:00", "pick": 2, "settled": "budget {tokens: 1000000, usd: 8.5}", "new_info": "none", "cause": "decision: the budget is set from the forecast, with room for one reopen", "budget_change": {"from": null, "to": {"tokens": 1000000, "usd": 8.5}}}, {"at": "2026-11-05T04:51:19+00:00", "step": "scenario", "order": "slice_only_marks", "seat": "originator", "question": "Sean Kennedy: the scenario agent marked 4 test(s) slice-only, so the cleaner may remove them and they do not join the wall: WiringTest.test_the_maker_and_cleaner_briefs_say_run_narrow_while_working_and_the_suite_once in tests/test_suite_runner.py (Checks a one-time wording change in two briefs.); WiringTest.test_the_config_suite_command_runs_the_runner_with_jobs in tests/test_suite_runner.py (Checks a one-time change to the config command line.); WiringTest.test_ci_runs_the_suite_in_shards_as_a_matrix_on_both_pythons in tests/test_suite_runner.py (Checks a one-time change to the CI workflow text.); WiringTest.test_ci_does_not_run_the_whole_suite_unsharded in tests/test_suite_runner.py (Checks a one-time change to the CI workflow text.). Accept the marks, or unmark a test so it joins the wall and the cleaner keeps it.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 1000000, "usd": 8.5, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast one pass of the suite-runner feature on claude/sonnet and claude/opus from tests-scope and full-suite-run rows; reopen risk not priced.", "at": "2026-11-05T04:49:03+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for the sharded parallel runner, no duplicate collection, config and CI wiring, and the maker and cleaner briefs.", "at": "2026-11-05T04:51:18+00:00"}], "forecaster": {"at": "2026-11-05T04:49:03+00:00", "wrote": []}, "scenario": {"at": "2026-11-05T04:51:18+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "nd the whole suite pass; otherwise `stopped` with the reason.\\n\\n```xv-report\\n{\"agent\": \"maker\", \"status\": \"green\", \"summary\": \"<one line on what changed>\",\\n \"moved_tests\": [{\"file\": \"tests/test_api.py\", \"assertion\": \"was: <old assertion>; now: <new assertion>\", \"why\": \"<how the scenario forces it>\"}],\\n \"stop\": null}\\n```\\n\\nOn a stop: `\"status\": \"stopped\"` and `\"stop\": {\"reason\": \"budget|repeated_failure|growing_diff|needs_move|contradiction|shape\", \"question\": \"<what a person must decide>\"}`.\\n\\nThe approach to the red-green loop borrows from Matt Pocock\\'s `tdd` and `implement-spec` skills (`mattpocock/skills`, MIT). The recorded move is XV\\'s own.\\n' : maker\n\n----------------------------------------------------------------------\nRan 17 tests in 0.044s\n\nFAILED (failures=6, errors=9)\n", "old_red_changed": [], "red_gaps": [], "unreadable": [], "not_covered": [], "missed_points": []}}
old_tests_forced: [{"file": "tests/test_budget_cap_turns_session.py", "test": "TurnsAndSessionTest, PrototypeBudgetsTest", "why": "`from test_budget_cap import BudgetCapTest` makes the loader collect BudgetCapTest's tests again here, and the subclasses inherit them. The import and base class must change, for example by importing the module instead and moving shared setup into a mixin with no tests."}, {"file": "tests/test_prototypes.py", "test": "PrototypesGitSetupTest", "why": "It subclasses PrototypesTest and so re-runs its inherited tests. It must stop inheriting tests."}, {"file": "tests/test_run.py", "test": "AcceptedShapeChangeTest, EveryPathOneVerdictTest, PreStepBudgetStopTest", "why": "They subclass WatchLoopTest. If WatchLoopTest defines tests, each subclass re-runs them; the maker should share setup through a mixin with no tests."}]
may_not_files: [{"file": "tests/run.py", "why": "The new runner lives under the tests/** wall and is not a test, so the red cannot create it. The maker must write it."}]
---
# The test suite runs each test once, in parallel (#131)

## Scenario

1. A person runs the whole suite with the command in `.xv/config.yml`. Every test runs once. No test runs again because its class inherits from another test class.
2. A person runs `python3 tests/run.py --shard i/n --jobs k`. The shards from `1/n` to `n/n` together run every test exactly once. With `--jobs k`, the tests run in k processes at the same time. The command exits non-zero if any test fails. `xv` reads which tests failed from its output, the same as it does now.
3. `.xv/config.yml` runs the suite through that runner, with `--jobs`.
4. The `tests` CI workflow runs the suite in shards, as a matrix of jobs, on both Python versions. The jobs run at the same time.
5. The maker and cleaner briefs say: while you work, run the red command or the test files your change touches. Run the whole suite once, before the report.
6. The tests still use only the Python standard library.

## May ignore

A time target for the suite or for CI; pytest and other runners; the suite commands of repos that adopt xv; the suite run that xv step does after the maker and cleaner, which stays as it is; making single slow tests faster.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T04:48:41+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T04:49:03+00:00 forecaster: done: Forecast one pass of the suite-runner feature on claude/sonnet and claude/opus from tests-scope and full-suite-run rows; reopen risk not priced.
- 2026-11-05T04:49:03+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-suite-speed budget ... --by <name>`).
- 2026-11-05T04:49:12+00:00 watch: offered 2 options for budget_not_set
- 2026-11-05T04:49:49+00:00 Sean Kennedy: set budget
- 2026-11-05T04:49:49+00:00 Sean Kennedy: answered budget_not_set: 2
- 2026-11-05T04:49:49+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-05T04:51:18+00:00 scenario: red: Red for the sharded parallel runner, no duplicate collection, config and CI wiring, and the maker and cleaner briefs.
- 2026-11-05T04:51:19+00:00 watch: stop (slice_only_marks) for originator: Sean Kennedy: the scenario agent marked 4 test(s) slice-only, so the cleaner may remove them and they do not join the wall: WiringTest.test_the_maker_and_cleaner_briefs_say_run_narrow_while_working_and_the_suite_once in tests/test_suite_runner.py (Checks a one-time wording change in two briefs.); WiringTest.test_the_config_suite_command_runs_the_runner_with_jobs in tests/test_suite_runner.py (Checks a one-time change to the config command line.); WiringTest.test_ci_runs_the_suite_in_shards_as_a_matrix_on_both_pythons in tests/test_suite_runner.py (Checks a one-time change to the CI workflow text.); WiringTest.test_ci_does_not_run_the_whole_suite_unsharded in tests/test_suite_runner.py (Checks a one-time change to the CI workflow text.). Accept the marks, or unmark a test so it joins the wall and the cleaner keeps it.

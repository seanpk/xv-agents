---
id: 2026-11-04-suite-speed
title: "The test suite runs each test once, in parallel (#131)"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-suite-speed
base: 168693608141b7cca549d5e56eebd4a61e9bd3fb
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.7, "basis": ["2026-10-27-slice-tests", "2026-11-04-retro-sighting", "2026-11-04-codex-step"]}, {"harness": "claude", "model": "opus", "tokens": 210000, "turns": null, "usd": 2.5, "basis": ["2026-10-27-slice-tests", "2026-11-04-retro-sighting", "2026-11-04-codex-step"]}], "wall_s": 2400, "shape": "wide", "breadth": "New tests/run.py runner, .xv/config.yml suite command, the tests CI workflow matrix, and the maker and cleaner briefs; tests/** is the wall. Reopen risk (2-4 rounds in most guide rows) is not priced."}
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3077, "cache_read": 26137, "cache_write": 26636, "tokens": 29717, "usd": 0.0071, "turns": 3, "wall_s": 15.9, "session": "9bc5ceb2-58e7-469c-b900-549fdaed6390", "step": "forecaster", "at": "2026-11-05T04:49:03+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-suite-speed/01-forecaster.out"}]
stops: [{"at": "2026-11-05T04:49:03+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-suite-speed budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast one pass of the suite-runner feature on claude/sonnet and claude/opus from tests-scope and full-suite-run rows; reopen risk not priced.", "at": "2026-11-05T04:49:03+00:00"}], "forecaster": {"at": "2026-11-05T04:49:03+00:00", "wrote": []}}
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

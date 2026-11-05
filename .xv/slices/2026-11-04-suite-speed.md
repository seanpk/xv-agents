---
id: 2026-11-04-suite-speed
title: "The test suite runs each test once, in parallel (#131)"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-suite-speed
base: 168693608141b7cca549d5e56eebd4a61e9bd3fb
next: forecaster
forecast: null
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
spend: []
stops: []
decisions: []
prototypes: []
overrides: []
checks: {}
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

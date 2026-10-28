---
id: 2026-10-27-init-no-try
title: "The suite skips xv init's test try where no test needs it"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-init-no-try
base: 8f9cdbee89d7193e0d5c675f4feabe11871a821d
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
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
# The suite skips xv init's test try where no test needs it

## Scenario

The suite runs about three times slower than it needs to (seanpk/xv-agents#38). Since #14, `xv init` runs the test command it guesses, once, to check it. Many tests call `xv init` on a copy of `evals/fixture`, so each one waits for a real test run, and only the tests in `tests/test_init_tries.py` check the result of that try. After the change, `xv init --no-try` does not run the test command. The test helpers pass `--no-try`, and the tests in `tests/test_init_tries.py` leave it off, so the real try is still tested. Without the flag, `xv init` works as it does today. On 176 tests, #38 measured 102 seconds with the try and 35 seconds without it. Today the suite takes about 130 seconds for 312 tests.

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-28T02:34:08+00:00 watch: slice opened by Sean Kennedy

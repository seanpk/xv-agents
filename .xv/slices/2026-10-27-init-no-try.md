---
id: 2026-10-27-init-no-try
title: "The suite skips xv init's test try where no test needs it"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-init-no-try
base: 8f9cdbee89d7193e0d5c675f4feabe11871a821d
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 200000, "turns": null, "usd": 0.6, "basis": ["2026-10-27-init-rerun", "2026-10-27-package-imports", "2026-10-27-allowed-commands"], "note": "Clean passes ran 41k-53k tokens ($0.23-0.29); one send-back round ran 158k ($0.90). Guide has no turn column."}, {"harness": "claude", "model": "opus", "tokens": 120000, "turns": null, "usd": 1.0, "basis": ["2026-10-27-init-rerun", "2026-10-27-package-imports", "2026-10-27-allowed-commands"], "note": "Clean guardian passes ran 30k-36k tokens ($0.35-0.41); one send-back ran 90k ($1.07). Guide has no turn column."}], "wall_s": 900, "shape": "narrow", "breadth": "Source: one xv init flag that skips the test try. Tests: the helpers pass --no-try and the test_init_tries cases leave it off, so the scenario diff may spread across several test files; if the helper is not shared, it stays narrow, and if the call sites change, it widens."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3897, "cache_read": 25223, "cache_write": 15306, "tokens": 19207, "usd": 0.0053, "turns": 3, "wall_s": 19.1, "session": "1e0f045c-dff1-4902-a75a-bfa75b27391e", "step": "forecaster", "at": "2026-10-28T02:34:33+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-init-no-try/01-forecaster.out"}]
stops: [{"at": "2026-10-28T02:34:33+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-no-try budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~200k tokens and opus ~120k tokens for one pass plus one send-back round; wall 900s; shape narrow.", "at": "2026-10-28T02:34:33+00:00"}], "forecaster": {"at": "2026-10-28T02:34:33+00:00", "wrote": []}}
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
- 2026-10-28T02:34:33+00:00 forecaster: done: Forecast sonnet ~200k tokens and opus ~120k tokens for one pass plus one send-back round; wall 900s; shape narrow.
- 2026-10-28T02:34:33+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-no-try budget ... --by <name>`).

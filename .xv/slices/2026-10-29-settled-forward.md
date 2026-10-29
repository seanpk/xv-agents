---
id: 2026-10-29-settled-forward
title: Some stops ask for --settled when the answer moves the slice forward
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-settled-forward
base: cafedce2750c9b8bfed996553f0f139df2563608
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 2.8, "basis": ["2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "Midpoint of the two basis rows (674k/$3.87 and 395k/$2.27). A clean single pass ran far lower, so the reopen risk drives this number. The guide has no turns column."}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.0, "basis": ["2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "Midpoint of the two basis rows (392k/$4.89 and 230k/$2.79). One clean guardian pass ran about $0.35 to $0.41, so the usd depends on how many passes the guardian runs. The guide has no turns column."}], "wall_s": 2000, "shape": "narrow", "breadth": "cmd_answer gating for setup_failed, prototype stops and pre-step budget stops, plus record stop --step plumbing and the README answer-line test; other stop kinds should not move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3378, "cache_read": 25516, "cache_write": 17019, "tokens": 20401, "usd": 0.0053, "turns": 3, "wall_s": 17.2, "session": "a5cf1b12-efdc-48c8-8dbc-5e511dabbf7e", "step": "forecaster", "at": "2026-10-29T21:51:20+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-settled-forward/01-forecaster.out"}]
stops: [{"at": "2026-10-29T21:51:20+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-settled-forward budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~500k tokens and claude/opus ~300k tokens from the stop-decisions and prototype-budgets rows, with reopen risk; shape narrow.", "at": "2026-10-29T21:51:20+00:00"}], "forecaster": {"at": "2026-10-29T21:51:20+00:00", "wrote": []}}
---
# Some stops ask for --settled when the answer moves the slice forward

## Scenario

Some stops ask for `--settled` when the answer moves the slice forward (#82).

1. When a setup fails (`setup_failed`) or a prototype stops, the work has not started yet, so any `--next` moves forward. No `--settled` is needed.
2. A budget stop raised before its step ran is the same: `--next <that step>` moves forward and needs no `--settled`.
3. `xv record stop` takes `--step`, and the tests use it. They no longer edit the record text to add a step.
4. A test runs the README's general answer line (`README.md:295`), not only its words.

## May ignore

cmd_answer is 68 lines, and two test lines read 'p =self.xv': those are the cleaner's, under the standards.

## Recording

None. A feature starts from words.

## Log
- 2026-10-29T21:51:00+00:00 watch: slice opened by Sean Kennedy
- 2026-10-29T21:51:20+00:00 forecaster: done: Forecast claude/sonnet ~500k tokens and claude/opus ~300k tokens from the stop-decisions and prototype-budgets rows, with reopen risk; shape narrow.
- 2026-10-29T21:51:20+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-settled-forward budget ... --by <name>`).

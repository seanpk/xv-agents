---
id: 2026-10-27-prototype-budgets
title: A prototype that runs out of budget comes back to a person
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-prototype-budgets
base: 23f8dd53788ee9f656f572e730e497e3b0a298bc
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-budget-cap", "2026-10-27-red-joins", "2026-10-27-allowed-commands"]}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.4, "basis": ["2026-10-27-budget-cap", "2026-10-27-red-joins", "2026-10-27-allowed-commands"]}], "wall_s": 1500, "shape": "wide", "breadth": "Expect the prototype start path, the variant stop and resume behaviour, the standing rule moving into scripts/orders.py, a CHANGELOG line and tests to move; the nearest feature row was narrow, so this is a judgement call."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 5160, "cache_read": 25222, "cache_write": 14862, "tokens": 20026, "usd": 0.0058, "turns": 3, "wall_s": 27.7, "session": "100d4415-672f-4437-927a-8b83fc51d44c", "step": "forecaster", "at": "2026-10-27T21:32:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-prototype-budgets/01-forecaster.out"}]
stops: [{"at": "2026-10-27T21:32:09+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-prototype-budgets budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet 400k tokens and opus 200k tokens for prototype-budgets, priced with one reopen, from the nearest feature rows of the same keys.", "at": "2026-10-27T21:32:09+00:00"}], "forecaster": {"at": "2026-10-27T21:32:09+00:00", "wrote": []}}
---
# A prototype that runs out of budget comes back to a person

## Scenario

A prototype that runs out of budget comes back to a person for a decision. In Sean's words: "whenever a prototype runs out of budget, it should come back to you for a decision. you cannot pick anything if no prototype was built, but you should be able to stop the prototype exploration. I guess that is a choice of "none"". So: (1) When any variant stops at its budget, the others still run, and then the slice stops for the person who set the work going, naming each variant that ran out and what it spent. The choices are: raise that variant's budget (`xv record set <id> prototype_budgets ...`) and run `xv prototype start` again; pick one of the variants that finished; or pick `none`, which ends the prototype exploration. A variant that ran out cannot be picked. When all three ran out, `none` is the only pick. (2) A second `xv prototype start` runs only the variants that stopped at their budget, each against its raised budget, and keeps the variants that finished, with their worktrees, recordings and side-by-side entries. A variant whose budget was not raised is not run again, and the stop says so. (3) `xv prototype start` no longer raises its own copy of `prototype_budgets_not_set`; the rule in `scripts/orders.py` raises it, and fires before any variant runs. This changes a standing order; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#55)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T21:31:41+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T21:32:09+00:00 forecaster: done: Forecast sonnet 400k tokens and opus 200k tokens for prototype-budgets, priced with one reopen, from the nearest feature rows of the same keys.
- 2026-10-27T21:32:09+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-prototype-budgets budget ... --by <name>`).

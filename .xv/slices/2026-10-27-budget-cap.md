---
id: 2026-10-27-budget-cap
title: "The budget caps the whole slice, red or green"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-budget-cap
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 600000, "turns": null, "usd": 0.4, "basis": ["2026-10-25-diff-count", "2026-10-24-promote-draft"], "note": "Clean one-pass rows only; the guide has no turns column. Reopen rows (suite-red-quote, init-tries-guesses, answer-in-prompt, init-allow-list, token-cap) ran 2-7x and are excluded."}, {"harness": "claude", "model": "opus", "tokens": 400000, "turns": null, "usd": 0.55, "basis": ["2025-10-25-diff-count", "2026-10-24-promote-draft"], "note": "Guardian rows from the same clean passes; no turns column in the guide. Reopen rows excluded, same as sonnet."}], "wall_s": 350, "shape": "narrow", "breadth": "Three modules named in the scenario (watch stop check before each step, agentcli with_caps per-step cap, orders.py budget_spent moved from after-maker to before-each-step), plus tests and a CHANGELOG line; no agent shape change expected."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4130, "cache_read": 25012, "cache_write": 10004, "tokens": 14138, "usd": 0.0043, "turns": 3, "wall_s": 23.0, "session": "4bed075b-4569-48e1-9fa0-4b15128b31dc", "step": "forecaster", "at": "2026-10-27T14:38:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-budget-cap/01-forecaster.out"}]
stops: [{"at": "2026-10-27T14:38:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-budget-cap budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~600k tokens and opus ~400k tokens for a single pass; reopen risk named, not priced.", "at": "2026-10-27T14:38:45+00:00"}], "forecaster": {"at": "2026-10-27T14:38:45+00:00", "wrote": []}}
---
# The budget caps the whole slice, red or green

## Scenario

The budget caps the whole slice, red or green. Before each step, the watch compares the slice's spend so far with the budget. A Claude step gets `--max-budget-usd` set to the dollars left, not the whole budget (`with_caps` in `scripts/agentcli.py`). When no dollars are left, or the tokens spent have reached the token cap, the step does not run: the `budget_spent` stop fires for the person who set the budget, whatever the suite says, and names what is spent. Today `budget_spent` fires only after the maker and only when the suite is not green (`scripts/orders.py`), so a green slice spends past its budget with no stop, and each step may spend the whole budget by itself. Take a $1 budget with $0.80 spent: the next Claude step runs with `--max-budget-usd 0.2`. With $1.05 spent and the suite green, the guardian does not run, and the slice stops at `budget_spent`. A raised budget (`xv record set <id> budget ...`) lets the slice go on from the step it stopped before. This changes a standing order; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#34, seanpk/xv-agents#36)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:38:22+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T14:38:45+00:00 forecaster: done: Forecast sonnet ~600k tokens and opus ~400k tokens for a single pass; reopen risk named, not priced.
- 2026-10-27T14:38:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-budget-cap budget ... --by <name>`).

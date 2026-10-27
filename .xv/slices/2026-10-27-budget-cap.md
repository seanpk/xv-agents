---
id: 2026-10-27-budget-cap
title: "The budget caps the whole slice, red or green"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-budget-cap
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
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
# The budget caps the whole slice, red or green

## Scenario

The budget caps the whole slice, red or green. Before each step, the watch compares the slice's spend so far with the budget. A Claude step gets `--max-budget-usd` set to the dollars left, not the whole budget (`with_caps` in `scripts/agentcli.py`). When no dollars are left, or the tokens spent have reached the token cap, the step does not run: the `budget_spent` stop fires for the person who set the budget, whatever the suite says, and names what is spent. Today `budget_spent` fires only after the maker and only when the suite is not green (`scripts/orders.py`), so a green slice spends past its budget with no stop, and each step may spend the whole budget by itself. Take a $1 budget with $0.80 spent: the next Claude step runs with `--max-budget-usd 0.2`. With $1.05 spent and the suite green, the guardian does not run, and the slice stops at `budget_spent`. A raised budget (`xv record set <id> budget ...`) lets the slice go on from the step it stopped before. This changes a standing order; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#34, seanpk/xv-agents#36)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:38:22+00:00 watch: slice opened by Sean Kennedy

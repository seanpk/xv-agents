---
id: 2026-10-27-prototype-budgets
title: A prototype that runs out of budget comes back to a person
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-prototype-budgets
base: 23f8dd53788ee9f656f572e730e497e3b0a298bc
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
# A prototype that runs out of budget comes back to a person

## Scenario

A prototype that runs out of budget comes back to a person for a decision. In Sean's words: "whenever a prototype runs out of budget, it should come back to you for a decision. you cannot pick anything if no prototype was built, but you should be able to stop the prototype exploration. I guess that is a choice of "none"". So: (1) When any variant stops at its budget, the others still run, and then the slice stops for the person who set the work going, naming each variant that ran out and what it spent. The choices are: raise that variant's budget (`xv record set <id> prototype_budgets ...`) and run `xv prototype start` again; pick one of the variants that finished; or pick `none`, which ends the prototype exploration. A variant that ran out cannot be picked. When all three ran out, `none` is the only pick. (2) A second `xv prototype start` runs only the variants that stopped at their budget, each against its raised budget, and keeps the variants that finished, with their worktrees, recordings and side-by-side entries. A variant whose budget was not raised is not run again, and the stop says so. (3) `xv prototype start` no longer raises its own copy of `prototype_budgets_not_set`; the rule in `scripts/orders.py` raises it, and fires before any variant runs. This changes a standing order; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#55)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T21:31:41+00:00 watch: slice opened by Sean Kennedy

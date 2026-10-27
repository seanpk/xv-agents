---
id: 2026-10-27-scenario-rerun
title: A scenario run after the maker keeps the red list and checks the right code
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-scenario-rerun
base: 99ae369ea03712578048ec10090c55dc5775b123
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
# A scenario run after the maker keeps the red list and checks the right code

## Scenario

A scenario run after the maker, sent to fix a test, does not cost the person needless stops. (1) Once the slice has been through the maker, a scenario report's `red` is added to the record's red: its files join `red.files` and the rest stay. Today `apply_report` replaces `red` with the report's (`scripts/record.py`, `if agent == "scenario" and report.get("red")`), so a run that touched one of twelve red files leaves only that one. Before the maker, a report still replaces `red`, as today. (2) Once the slice has been through the maker, the check that the scenario fails on today's code (`red_fails`, read by `scenario_not_red` in `scripts/orders.py`) runs the red command against the slice's code from before the maker's first change (the wall baseline commit), not HEAD, where the maker's fix already makes it pass. A new red that fails there and passes at HEAD is fine; one that passes there still fires `scenario_not_red`. (3) A move with `--slice-only` must name a test on the record's `slice_only` list. Otherwise it is a plain move, and `accept_moves` fires for it, as for any move. (seanpk/xv-agents#44; (3) is from the guardian on #17.)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T16:45:38+00:00 watch: slice opened by Sean Kennedy

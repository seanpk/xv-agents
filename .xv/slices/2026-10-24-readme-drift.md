---
id: 2026-10-24-readme-drift
title: "README matches the stop table, the status and xv adapt"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-readme-drift
base: 948efd1159971b567b82e3bc8045c8c6542e5300
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
# README matches the stop table, the status and xv adapt

## Scenario

The README stop table names every order `scripts/orders.py` fires. The README Status line says 0.2.0 came from a real init. The README mentions `xv adapt`.

The red test for this slice is for this slice only: Sean removes it before the merge (decided 2026-10-24).

## May ignore

the generated block between the xv:method markers

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy

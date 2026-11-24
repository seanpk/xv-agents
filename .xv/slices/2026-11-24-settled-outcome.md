---
id: 2026-11-24-settled-outcome
title: "A settled not-covered outcome does not stop again (#205)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-settled-outcome
base: 82a218f104bde75596fec4773887dc118aa50337
next: forecaster
build: none
build_shared: no
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
# A settled not-covered outcome does not stop again (#205)

## Scenario

A not-covered outcome that a person settled does not stop again on a later test writer pass (#205).

1. A person answers a `red_misses_scenario` stop for outcome N. A later test writer pass lists N in `not_covered` again. No new `red_misses_scenario` fires for N. This holds when the later pass words N or its reason differently, such as "7", "7. A line in CHANGELOG.md" or "7. A line in CHANGELOG.md.".
2. It also holds when the person settled N in the answer to another stop that bundled `red_misses_scenario`, and when that answer sent the slice back.
3. An outcome that no person settled still fires `red_misses_scenario`, on the same pass as a settled one.
4. A line in `CHANGELOG.md`.

## May ignore

an outcome that the scenario amends after the answer

## Recording

.xv/recordings/rec-settled-outcome.md

## Log
- 2026-11-24T22:25:03+00:00 watch: slice opened by Sean Kennedy

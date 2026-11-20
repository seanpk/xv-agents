---
id: 2026-11-19-pick-tests
title: Two prototype pick paths have tests
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-pick-tests
base: 07f5734397e770fdcb049a0eb78b318877d93cf6
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
# Two prototype pick paths have tests

## Scenario

Two prototype pick paths have tests.

1. `xv prototype pick --keep` on a variant whose merge conflicts with the slice branch outside `.xv/` is refused, and the record does not change. The variant's uncommitted work is committed onto the variant's own branch before the refusal, so that branch's tip moves; a test pins this.
2. `xv prototype pick` without `--keep` and with a `--scenario-file` that does not exist is refused before anything changes: all three prototypes, their worktrees and their branches stay, and the record does not change.

## May ignore

other prototype paths; a CHANGELOG line, since no check changes

## Recording

None. A feature starts from words.

## Log
- 2026-11-20T01:20:35+00:00 watch: slice opened by Sean Kennedy

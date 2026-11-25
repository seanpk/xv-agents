---
id: 2026-11-25-failed-step
title: "A failed step marks its start ended, so a later move reads HEAD (#202)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-failed-step
base: ae7929481b166143489f51e6194aaf375eca7bb6
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
# A failed step marks its start ended, so a later move reads HEAD (#202)

## Scenario

When `xv step` fails because the agent could not run (the agent CLI is missing, or the worktree is gone), the record's `step_start` is marked ended, as it is after a step that ran (1).
A slice-only move recorded after that failed step reads its line from `HEAD`, not from the failed step's start (2).
There is a CHANGELOG line (3).

## May ignore

a step that fails after the agent ran

## Recording

None. A feature starts from words.

## Log
- 2026-11-25T19:14:16+00:00 watch: slice opened by Sean Kennedy

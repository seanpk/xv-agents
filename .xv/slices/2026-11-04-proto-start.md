---
id: 2026-11-04-proto-start
title: "A prototype variant is never dropped when the three start at once: #61"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-proto-start
base: c7b8bbff58fc46160ba83d08d0e899d7beffaaf2
next: forecaster
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
# A prototype variant is never dropped when the three start at once: #61

## Scenario

# A prototype variant is never dropped when the three start at once: #61

What happened: on the #55 slice, `xv prototype start` ran the three variants at once, and variant b never called its agent. No error reached the person. The guess in #61 is that two `git branch -D` or `git worktree add` commands hit the same git lock; that cause is not confirmed.

What should happen:

1. The git setup for one variant (removing the old worktree, deleting the branch, adding the worktree) never runs at the same time as another variant's setup. The agents still run at the same time. A fake `git` that logs each start and end time shows this.
2. When git refuses one variant's setup, that variant is not dropped. It is recorded as not finished, with its error. The side-by-side file shows the error. The other two variants still run. A second `xv prototype start` runs it again, as it does now for any variant that did not finish.

## May ignore

#58 (building the variants one at a time, or in turns): the variants still run at the same time; prototypes applying their own stop, left for #117; old prototype records, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T18:51:28+00:00 watch: slice opened by Sean Kennedy

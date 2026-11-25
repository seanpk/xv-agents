---
id: 2026-11-25-build-moves
title: "In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-build-moves
base: 84f20f5eb0c66ecb9426f6f63ce0074847a0d3be
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
# In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210)

## Scenario

In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210).

1. In a slice from a build (`xv slice new --from <ref>`), when the build changed or removed old tests in files that existed at the base, the test writer step still stops with `unrecorded_move` for a person. The question says those files were changed by the build, not the test writer.
2. The question lists the test writer's own changes to old test files apart from the build's. A file that both changed is in both lists.
3. A file with a recorded move (`xv record move`) is not in the stop, whether the build or the test writer changed it.
4. A slice with no build, or a build that changed no old test, stops as it does today.
5. A line in `CHANGELOG.md`.

## May ignore

A way to accept all of the build's moves with one command

## Recording

.xv/recordings/rec-build-moves.md

## Log
- 2026-11-25T05:01:12+00:00 watch: slice opened by Sean Kennedy

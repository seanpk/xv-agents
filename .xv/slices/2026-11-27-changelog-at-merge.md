---
id: 2026-11-27-changelog-at-merge
title: "A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)"
kind: feature
status: open
originator: Sean Kennedy
created: 2026-11-27
branch: xv/2026-11-27-changelog-at-merge
base: dd577e56d4a5315f8bcd44af60e6af600af7bd87
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
# A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)

## Scenario

1. The test writer puts an outcome in `not_covered` and names the files it is about in `checks`. All of its `checks` files are in `tests.slice_only_files`. So the red check does not stop with `red_misses_scenario` for that outcome.
2. A `not_covered` outcome whose `checks` names any other file still stops, as it does now. An outcome with no `checks` also still stops.
3. The inspector brief asks the inspector to read each outcome that went through this way, check that the change to the file is right and in the right place, and put that in the inspection report for the person who decides the merge.
4. There is a line in `CHANGELOG.md`.

## May ignore

- The deputation part of #214. The watch merging a slice on its own waits for #159 and #160 in v0.8.
- Slices already open or closed. Their records stay as they are.

## Recording

None. A feature starts from words.

## Log
- 2026-11-28T02:23:06+00:00 watch: slice opened by Sean Kennedy

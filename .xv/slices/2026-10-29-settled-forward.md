---
id: 2026-10-29-settled-forward
title: Some stops ask for --settled when the answer moves the slice forward
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-settled-forward
base: cafedce2750c9b8bfed996553f0f139df2563608
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
# Some stops ask for --settled when the answer moves the slice forward

## Scenario

Some stops ask for `--settled` when the answer moves the slice forward (#82).

1. When a setup fails (`setup_failed`) or a prototype stops, the work has not started yet, so any `--next` moves forward. No `--settled` is needed.
2. A budget stop raised before its step ran is the same: `--next <that step>` moves forward and needs no `--settled`.
3. `xv record stop` takes `--step`, and the tests use it. They no longer edit the record text to add a step.
4. A test runs the README's general answer line (`README.md:295`), not only its words.

## May ignore

cmd_answer is 68 lines, and two test lines read 'p =self.xv': those are the cleaner's, under the standards.

## Recording

None. A feature starts from words.

## Log
- 2026-10-29T21:51:00+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-11-18-report-tree
title: "What an agent reports is checked against the tree (#183)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-17
branch: xv/2026-11-18-report-tree
base: 5c2600c69d4d50853dcd288bd6278c48bd808657
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
# What an agent reports is checked against the tree (#183)

## Scenario

What an agent reports is checked against the tree.

1. After the cleaner step, each accepted `slice_only` test still in its file stops the step with `removal_not_made` for the person who set the work going, naming the file and the test, unless the cleaner's report says it kept that test and why. A removal that was made passes.
2. After any step, a move on the record that says a test or a file was removed (`--slice-only` or `--deleted`) while that test or file is still there stops the step with `removal_not_made` for the person who set the work going, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last `xv-report` block of the whole run, through the harness's own reader, before it stops with `no_report`. The core still names no agent. A run with no report block anywhere still stops with `no_report`.
4. A line in CHANGELOG.md.

## May ignore

- old slice records
- a harness whose reader cannot see earlier messages: it stops with no_report, as now

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T03:54:46+00:00 watch: slice opened by Sean Kennedy

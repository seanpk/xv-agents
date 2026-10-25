---
id: 2026-10-25-diff-count
title: "diff_growing counts only the maker's files"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-diff-count
base: f452d430f44f6c01e611f705f5b709b80231291b
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
# diff_growing counts only the maker's files

## Scenario

`diff_lines`, which the `diff_growing` stop and `limits.max_diff_lines` read after the maker and the cleaner, counts only files outside `.xv/`. A packet or boundary file the guardian writes between two maker runs does not make the diff look like it grew. (seanpk/xv-agents#24)

## May ignore

max_diff_lines semantics beyond excluding .xv/

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy

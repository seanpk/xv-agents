---
id: 2026-11-05-record-state
title: "Accepted answers and the rebase record stay right: #120, #136, #138"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-record-state
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
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
# Accepted answers and the rebase record stay right: #120, #136, #138

## Scenario

When this is done:

1. The shape stop keeps the breadth it was accepted at. It fires again when a later pass reports a wider shape.
2. When a person accepts a "mark slice-only" wall recommendation at `accept_moves`, the test is listed in `slice_only`, so the cleaner removes it.
3. `xv record report` and `xv record packet` run the same move and packet checks as `xv step`.
4. For a test file the slice added, `moves.find` compares with the file as the scenario step left it.
5. During `xv slice rebase`, the rebase maker's brief reads the record of truth with the changes made during the rebase applied. It includes answers the person gave at a rebase stop.
6. On a replay with no conflict, a maker edit to a test file or `.xv/picture.md` stops with `rebase_conflict`, as it does on a conflict replay.
7. When `xv slice rebase` exits on an error mid-rebase, a later `--continue` or `--abort` reads the stops and budget from the record of truth, not from git's replayed copy.
8. The slice log keeps the stop and answer lines written mid-rebase, after `--continue` and after `--abort`.
9. A record the person staged before `--continue` is not committed into the replayed commit. The "conflict markers remain" check runs before `git add -A`, so it fires for any file. When point 6 fires, the `rebase_conflict` question names the maker's edit, not a conflict.
10. `CHANGELOG.md` has a line for each new or changed stop.

## May ignore

old slice records; a rebase onto a branch that is not clean.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T18:29:42+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-10-30-covers-list
title: A covers item may name more than one test
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-covers-list
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
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
# A covers item may name more than one test

## Scenario

A covers item may name more than one test (#92).

1. In the scenario report, a `covers` item's `test` may be one test name or a list of names. Each name must match a whole test name in a red file.
2. A `test` string that joins names with `,` or `;` is read as that list.
3. A name written as `Class.test_name` or `file::test_name` matches on its last part.
4. The scenario brief's report example shows the list form.

This changes the scenario brief and a check, so `CHANGELOG.md` gets a line.

## May ignore

None.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T05:57:26+00:00 watch: slice opened by Sean Kennedy

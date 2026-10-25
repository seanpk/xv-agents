---
id: 2026-10-24-promote-draft
title: "xv promote draft: whole-word titles, any stack, one date, attribution"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-promote-draft
base: 948efd1159971b567b82e3bc8045c8c6542e5300
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
# xv promote draft: whole-word titles, any stack, one date, attribution

## Scenario

`xv promote draft` gives a title cut at a word boundary, "Applies to: any" when no `--applies-to` is passed, a draft file name with one date, and a body that ends with the assistant's attribution line. (seanpk/xv-agents#13)

## May ignore

the post and tally commands

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy

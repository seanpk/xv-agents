---
id: 2026-10-25-suite-red-quote
title: "Stops quote the failing step; green means exit 0"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-suite-red-quote
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
# Stops quote the failing step; green means exit 0

## Scenario

When the suite is red after the maker or the cleaner, the `cleaner_broke_suite` stop and the budget stop quote the failing step from `suite_output` in their question, so the person sees what failed without opening the record. The maker's and the cleaner's briefs say that green means the suite command exited 0, not what the end of its output looks like. (seanpk/xv-agents#19; Sean approves the brief change, solo.)

## May ignore

xv init asking for lint and format; a summary-line convention for suite scripts

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy

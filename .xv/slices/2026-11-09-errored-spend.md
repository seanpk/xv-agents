---
id: 2026-11-09-errored-spend
title: "An errored prototype variant keeps its spend, and a gone worktree says so"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-errored-spend
base: 4f6dcb707076f9b7a130b27302e6cafdd92e73e1
next: forecaster
build: {"kind": "exploration", "ref": "explore/errored-spend", "commit": "c7205f151b64e47a26b88afec54acfbdc3e4942d"}
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
# An errored prototype variant keeps its spend, and a gone worktree says so

## Scenario

1. A prototype variant whose agent ran and then errored keeps that run's spend in the record, and the spend counts against that variant's prototype budget, so a second `xv prototype start` gives it only what is left. (#121)
2. A variant whose working folder is gone reports that the working folder is missing, not "agent CLI not found". (#121)

## May ignore

- A timeout, which does not raise and is unchanged.
- A harness that reports no spend.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T16:28:25+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-10-24-boundary-imports
title: xv boundary finds Python edges in src layouts and flat scripts
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-boundary-imports
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
# xv boundary finds Python edges in src layouts and flat scripts

## Scenario

In a `src/` layout and in flat scripts that import each other by bare name, `xv boundary` shows an edge for every import between modules. On this repo, `.xv/boundary-all.md` shows `run` -> `agentcli`, `orders`, `prompt`, `record`, `spend`. (seanpk/xv-agents#12)

## May ignore

JavaScript, Ruby and Go imports; dependency-cruiser

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy

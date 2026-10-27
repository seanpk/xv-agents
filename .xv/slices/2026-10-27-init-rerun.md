---
id: 2026-10-27-init-rerun
title: xv init runs again without crashing
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-init-rerun
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
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
# xv init runs again without crashing

## Scenario

`xv init` runs again in a repo whose `.xv/config.yml` already exists, to fill in a missing file, without crashing. Today `runners` is set only when init writes the config (`if "config.yml" in written:` in `cmd_init`, `scripts/run.py`) and read later by `if len(runners) > 1:`, so a second run raises `UnboundLocalError` before it prints anything. After the fix, a second run with a missing `.xv/pitch.md` writes the starter pitch, keeps every existing file, prints its usual JSON output, and exits 0. (seanpk/xv-agents#40)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:27:49+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-10-27-retro-accept-fields
title: "xv retro accept keeps the candidate's fields"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-retro-accept-fields
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
# xv retro accept keeps the candidate's fields

## Scenario

`xv retro accept <packet> <n> --by <name>` writes an Open entry in `.xv/learnings.md` that keeps the candidate's own fields. Today (`scripts/retro.py`, the `kind == "open"` entry) `said:` gets the candidate's `miss`, `rule:` gets its title, the candidate's `said:` and `rule:` lines are dropped, and `--by` is not written. After the fix, the entry keeps `from`, `miss`, `said` and `rule` from the candidate, writes `seen:` as `owner/repo@date` (the same name `xv promote` uses, for example `seanpk/xv-agents@2026-10-27`, falling back to the folder name when the repo has no remote), and says who accepted it. A standard or a rule accepted the same way also writes `seen:` as `owner/repo@date`. (seanpk/xv-agents#43)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:27:49+00:00 watch: slice opened by Sean Kennedy

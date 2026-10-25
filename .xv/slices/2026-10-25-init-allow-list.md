---
id: 2026-10-25-init-allow-list
title: xv init writes a starter allow list
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-init-allow-list
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
# xv init writes a starter allow list

## Scenario

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`: read-only shell and git commands, `git rm`, `git mv`, `xv record move`, and the test command it detected. The forecaster and the guardian get only the read-only part, plus the test command for the guardian. A headless agent with the starter config can run the test command as `xv prompt` gives it. (seanpk/xv-agents#16)

## May ignore

harnesses other than Claude Code; asking for lint and type commands

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy

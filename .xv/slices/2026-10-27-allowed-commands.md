---
id: 2026-10-27-allowed-commands
title: "Each agent's prompt says which commands it may run"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-allowed-commands
base: 99ae369ea03712578048ec10090c55dc5775b123
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
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
# Each agent's prompt says which commands it may run

## Scenario

Each agent's prompt says which shell commands it may run. `xv prompt <agent> <id>` reads the Bash rules from that agent's own `--allowedTools` in `.xv/config.yml` (its line, or the default line) and lists them, for example `cd tests`, `python3 -m unittest`, `git diff`. It says to run each command in one of those forms, with no other command chained before it, no extra flags in front of a listed form (`python3 -W ignore -m unittest` is not `python3 -m unittest`), and no pipe to a program that is not listed, because any other form waits for an approval that a headless run never gets. An agent line with no `--allowedTools`, or a harness other than Claude Code, gets no such list. This changes what every agent is given; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#48)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T17:27:24+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-10-25-init-tries-guesses
title: xv init tries its guessed test command and roots
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-init-tries-guesses
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
# xv init tries its guessed test command and roots

## Scenario

`xv init` runs the test command it chose once, with a time limit, and its output says whether the command passed, failed (with the last lines of its output), or timed out. The output also gives the number of modules in `.xv/boundary-all.md` and lists any folder that looks like a fixture (a name such as `fixture`, `fixtures`, `examples` or `setups`, holding code). The skill tells the person about each. (seanpk/xv-agents#14)

## May ignore

fixing a failed command automatically

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy

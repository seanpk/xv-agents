---
id: 2026-10-25-answer-in-prompt
title: "The next agent sees the person's answer; xv slice amend"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-answer-in-prompt
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
# The next agent sees the person's answer; xv slice amend

## Scenario

After a person answers a stop, the next agent's prompt (`xv prompt`) includes that answer word for word, under its own heading, so the agent acts on it without having to find it in the record's log. `xv slice amend <id> --scenario-file <file>` appends the change to the slice's scenario with the date and who made it, clears `red`, and sets `next` to `scenario`, so the scenario agent writes a red for the new part. (seanpk/xv-agents#18; Sean approves any brief change, solo.)

## May ignore

amending may-ignore, the budget, or the kind

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy

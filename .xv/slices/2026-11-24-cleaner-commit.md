---
id: 2026-11-24-cleaner-commit
title: "The watch commits the cleaner's work, as it does the maker's (#206)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-24
branch: xv/2026-11-24-cleaner-commit
base: d4011e47fc52d2c5fbf8fdb6b80f6e0543cbf462
next: forecaster
build: none
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
# The watch commits the cleaner's work, as it does the maker's (#206)

## Scenario

The watch commits the cleaner's work, as it does the maker's (#206).

1. The cleaner's brief says to leave its changes uncommitted: the watch commits them after its checks. Its may-not list has "Commit, merge, or push", as the maker's does.
2. The cleaner still records each test move with `xv record move` before its step ends. The brief no longer says the pre-commit hook refuses a move with no record; it says the wall check after the step stops on one.
3. `cleaner_commit` in the record names the commit `xv step` makes after the cleaner (`xv(<id>): record the cleaner's pass`), and stays empty when the cleaner changed nothing. The brief's report has no `commit` field; a report that still sends one is not refused.
4. README, the docs and the picture no longer say the cleaner commits. A new numbered decision in `docs/decisions.md` says the watch commits each step's work; decision 7 stays as history.
5. A line in `CHANGELOG.md`.

## May ignore

old records where cleaner_commit is empty; harnesses with no allow-list

## Recording

None. A feature starts from words.

## Log
- 2026-11-24T14:02:29+00:00 watch: slice opened by Sean Kennedy

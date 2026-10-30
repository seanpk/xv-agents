---
id: 2026-10-29-red-covers-scenario
title: A red that leaves part of the scenario untested is caught before the maker
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-red-covers-scenario
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
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
# A red that leaves part of the scenario untested is caught before the maker

## Scenario

A red that leaves part of the scenario untested is caught before the maker (#64, and candidate 1 of the retro of 2026-10-29).

1. The scenario agent's report names each item the scenario names, with the test that covers it, and each item it did not cover, with why. An item with no test stops the slice for the person who set the work going, before the maker runs. (#64)
2. After the scenario step, a check takes every flag and `xv` command written in backticks in the scenario, amendments included, and lists each one that appears in no red file. Anything listed stops the slice for the person who set the work going, before the maker runs. (retro candidate 1)
3. The check's test case: on the first red of `2026-10-29-stop-decisions`, the check lists `--since`. On that slice's final red, it lists nothing.

## May ignore

An item the scenario names in plain words, without backticks: the agent's list in point 1 covers those, not the check in point 2.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T00:18:39+00:00 watch: slice opened by Sean Kennedy

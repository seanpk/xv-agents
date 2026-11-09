---
id: 2026-11-09-retro-fixes
title: "Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-retro-fixes
base: 4f6dcb707076f9b7a130b27302e6cafdd92e73e1
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
# Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled

## Scenario

1. On a slice from a build, a test file that the build only added tests to (no line at the base changed or removed) is not an unrecorded move: `unrecorded_move` does not fire for it, and the wall's `unrecorded` list does not name it. (#172)
2. On a slice from a build, a test file in which the build changed or removed a line at the base still stops with `unrecorded_move`. (#172)
3. `xv record move --slice-only` on a test that is not in the record's `slice_only` list marks the move `slice_only: true`. (#173)
4. After the scenario step, a `not_covered` item that a person already answered at an earlier `red_misses_scenario` stop does not fire `red_misses_scenario` again on a later pass. A new `not_covered` item still fires. (#174)
5. The scenario brief says that on a slice from a build, a red test that fails only on the build is expected: the agent reports it and does not stop to ask. (#174)
6. The scenario brief says to run the red command in the foreground, to its end, before writing the report. (#174)
7. `CHANGELOG.md` has a line for the brief change and the tool changes.

## May ignore

Other files under the test paths that are not tests, such as tests/run.py; they still count as test files.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T16:28:25+00:00 watch: slice opened by Sean Kennedy

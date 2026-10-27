---
id: 2026-10-27-wall-red-files
title: The wall sees old tests in a red file
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-wall-red-files
base: 23f8dd53788ee9f656f572e730e497e3b0a298bc
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
# The wall sees old tests in a red file

## Scenario

The wall sees old tests in a red file. Today a file on `red.files` is covered whole (`scripts/wall.py`, `check_against_base`: `covered |= red | recorded`), so an old test in it can be changed or deleted and the wall reports nothing. Since #17 the scenario agent puts new tests in the existing test file, so most red files now hold old tests. After the fix, for a red file that existed at the base, only the tests the slice added are the red. Every test and assertion that was in the file at the base must still be there, unchanged, at HEAD, unless a recorded move (`xv record move`) names that file; otherwise the file is `unrecorded`, in the CI form (`xv wall check --base`) as in the slice's own check. A red file that is new in the slice is covered whole, as today. Take `tests/test_store.py`, present at the base with `test_expiry` asserting `30`: the slice adds `test_renewal` and makes it the red. Adding `test_renewal` passes the wall. Changing `test_expiry`'s `30` to `31`, or deleting `test_expiry`, without a recorded move, fails it. This changes a check; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#53)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T21:27:46+00:00 watch: slice opened by Sean Kennedy

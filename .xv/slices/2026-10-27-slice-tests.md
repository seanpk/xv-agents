---
id: 2026-10-27-slice-tests
title: Tests a slice leaves behind fit the layout and do not go stale
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-slice-tests
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
# Tests a slice leaves behind fit the layout and do not go stale

## Scenario

Tests a slice leaves behind fit the test layout and do not go stale. (1) The scenario brief asks for new tests in the existing test file for the code under test, and a new file only when none exists (`skills/scenario/SKILL.md` step 6 says the opposite today). (2) The scenario agent marks each test that only proves the slice did its job and has no value after it (for example, "this file is `.ts`, not `.js`"). Its report names them, and the record keeps the list. At close, the close output lists them for the person who set the work going, who approves each removal; a removal is a recorded move. Nothing is removed without that approval. (3) When a recorded move (`xv record move`) moves or deletes a file that `red.files` names, the record's `red.files` and `red.command` are updated to match, so the guardian and the "watch the first green run" line do not point at a deleted file. (seanpk/xv-agents#17; Sean approves the brief change, solo.)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T13:30:58+00:00 watch: slice opened by Sean Kennedy

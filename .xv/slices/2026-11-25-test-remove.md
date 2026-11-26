---
id: 2026-11-25-test-remove
title: "Taking the inspector's advice to remove a test removes it: --test-remove (#202)"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-test-remove
base: 911f113209115d8a4e586a9f3d6efd095926baef
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
# Taking the inspector's advice to remove a test removes it: --test-remove (#202)

## Scenario

At `moves_to_accept`, `xv record answer --test-remove <test>` takes the inspector's advice for that test and removes it from its file: the whole test with its decorators, with the same check as a `test-remove` directed edit (1).
The answer commits the removals and runs the suite, as an answer with a directed edit does (2).
A test that is already gone from its file is skipped. A test that is in its file but cannot be removed cleanly makes the answer refused, and nothing is removed or recorded (3).
A test the answer does not name stays in its file (4).
`--accept-wall` and `--refuse-wall` still work: `--accept-wall <test>` does what `--test-remove <test>` does, and `--refuse-wall <test>` does what `xv record unmark <test>` does. Each prints a warning that names the new way and #216. The watch brief and the README name only the new way (5).
Each test that a slice record lists as accepted for removal, and that is still in the file it was accepted from, is removed (6).
There is a CHANGELOG line (7).

## May ignore

a wall recommendation at any stop other than moves_to_accept

## Recording

None. A feature starts from words.

## Log
- 2026-11-26T02:25:17+00:00 watch: slice opened by Sean Kennedy

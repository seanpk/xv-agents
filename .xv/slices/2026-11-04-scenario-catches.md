---
id: 2026-11-04-scenario-catches
title: "The scenario agent catches more before the maker starts: #119, with #110 and #111"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-scenario-catches
base: a6e023bd0ffeed4f6ce45990c668742a8f758419
next: forecaster
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
# The scenario agent catches more before the maker starts: #119, with #110 and #111

## Scenario

# The scenario agent catches more before the maker starts: #119, with #110 and #111

When this is done:

1. When the scenario agent writes a test that only checks a one-time wording change (a README line, a version pin, a reworded doc item), it marks the test slice-only. (#119.1)
2. a. The scenario agent's report names each old test the red will force to change: the file, the test, and why. The maker may change a named test without stopping, and it records the move. A test that is not named still follows rule 3.
   b. The scenario agent's report names each file on the maker's may-not list that the red needs changed (for example, `.xv/picture.md`). The maker may change those files, and no other file on that list. The guardian lists each of those changes in the packet. (#119.2)
3. When a scenario adds a check that accepts a value (a flag, a field, a report key), the scenario agent writes a red case for each way the input can be wrong: missing, empty, wrong type, a value not on the list. When a read-only agent writes the value about itself, it adds a case where that agent claims what only a person may give. It tests each case or names it in `not_covered`. (#119.3, #110)
4. Each amendment the watch drafts names four things: the exact name a test will look for; where it is checked; when it applies, and the case it does not cover; and any may-not line or binding decision it loosens. (#111)
5. A `covers` item may name a point by its number. `"1"` matches point 1 of the scenario, and so does an item that starts with the number, such as `"1. Whether a miss repeats"`.
6. `CHANGELOG.md` has a line for each brief change.

## May ignore

The cleaner, which has no part in point 2; naming an amendment's points by number, since point 5 covers only the scenario's own points; old slice records under .xv/slices/, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T20:44:06+00:00 watch: slice opened by Sean Kennedy

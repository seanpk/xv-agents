---
id: 2026-11-18-move-names
title: The removal check reads only names it can find
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-18
branch: xv/2026-11-18-move-names
base: 8e366c9ba6c94b28cbedfad1e5221c22bf914dda
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
# The removal check reads only names it can find

## Scenario

The removal check reads only names it can find.

1. `xv record move --slice-only` takes an `--assertion` only when it names a test that was in that file when the step began. The name is in a form the check reads: `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`. The name may be followed by a note in brackets: `(...)`, `[...]`, `{...}` or `<...>`. The note is not read for a name. Any other text is refused: the command says that the assertion must be the test's name, with an optional note in brackets, and records nothing.
2. After a step, the removal check looks for exactly the name that the move recorded, without its note. It no longer reads a sentence for a name. A move that reaches the record by another route (in a report) and has no name in a form from outcome 1 stops the step as "the test name could not be read".
3. A table test runs the check over each of these inputs while the test is still in its file: `Red::`, `Red#`, a path with a `-`, `Red::test_x[1]`, `removed Red.test_milk_today as asked`, `removed Red.test_milk_today for issue#183`, `removed Red.test_milk_today.`, a name in backticks, and `Red.test_milk_today (removed as asked)`. Each one stops, at the refusal in outcome 1 or at the check in outcome 2. None of them passes. When the test is gone, `Red.test_milk_today (removed as asked)` and `Red.test_milk_today [see issue#183]` pass.
4. When the packet's `## Scenario misses` section lists a miss but its front matter says `change_misses_scenario: no`, the step stops for the person who set the work going and names the disagreement.
5. The cleaner's brief says that the note for a slice-only removal is the test's name as it is written in the file, with an optional note in brackets after it.
6. A line in CHANGELOG.md.

## May ignore

moves recorded before this change (old slice records); --deleted file removals, which the check already finds by file path

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T21:01:52+00:00 watch: slice opened by Sean Kennedy

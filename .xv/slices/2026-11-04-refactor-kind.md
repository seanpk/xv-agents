---
id: 2026-11-04-refactor-kind
title: "A slice kind for refactors, and test moves a person expects: #15"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-refactor-kind
base: 66570aa785961973ad109e9db00dfc167a823e9b
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
# A slice kind for refactors, and test moves a person expects: #15

## Scenario

# A slice kind for refactors, and test moves a person expects: #15

When this is done:

1. `xv slice new --kind refactor` opens a refactor slice. Its scenario says that users see no change, and it names what to restructure.
2. The scenario step writes no new red. It checks that the suite is green at the start, and it records that as the slice's oracle.
3. The maker may rename and restructure what the scenario names. The "no refactor, no rename" line in its brief does not apply to those parts.
4. A latent bug found along the way is fixed only through `xv slice amend`.
5. `xv slice new --expect-moves <kinds>` names the kinds of test change the person expects: `imports`, `renames`, or both.
6. After each step, a script compares each moved test file before and after. The agent does not decide whether a move is expected.
7. Expected moves are recorded and listed on one line in the packet, with no `accept_moves` stop for them. Any other move still stops for the person.
8. `renames`: a test file moves to a new path (for example `test_foo.py` to `test_bar.py`). Its content changes only in the names the slice renames, in import lines, and in whitespace. Every assertion is otherwise unchanged. `imports`: the same path, and only import or require lines and whitespace change. These two are the only kinds for now.
9. The person gives the names a slice renames when it opens, with `xv slice new --rename Foo=Bar`, one flag per pair. The script reads those pairs to check a `renames` move.
10. Each new stop is decided in `scripts/orders.py`.

## May ignore

expected-move kinds other than imports and renames; #114, the retro seeing rework, left for slice H; old slice records, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T03:13:28+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-11-02-own-the-result
title: Briefs lead with Own the result
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-02
branch: xv/2026-11-02-own-the-result
base: 3e5bf091aa27720b9f9374f3f2f9dba05888d1e1
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
# Briefs lead with Own the result

## Scenario

# Briefs lead with Own the result (#107)

When this is done, someone checking out the repo sees:

1. Each of the 15 brief openers names Own the result first, then keeps the stop line — form: `Own the result: even when agents write all of the code, a person is responsible for what it does. An agent may stop. It may not decide.` plus any agent-specific rest that was already there. The "The one rule:" label is gone from those openers.
2. `docs/briefs.md` ("Every brief") and `.xv/picture.md` item 13 say the same: Own the result opens each brief; the stop line stays.
3. `CHANGELOG.md` has a line for the reword that names who agreed it (#107).
4. The three CI example pins and the README checkout/pin mentions that still say `v0.4.0` say `v0.4.1`.

## May ignore

The Go-and-see third stop and scripts/orders.py; renaming the README The one rule section; cutting the actual v0.4.1 git tag (person does that after merge); other open issues.

## Recording

None. A feature starts from words.

## Log
- 2026-11-02T20:55:58+00:00 watch: slice opened by Sean Kennedy

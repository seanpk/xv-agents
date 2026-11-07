---
id: 2026-11-07-defects-stops
title: "A red that cannot run stops the slice, and an answered stop stays answered"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-11-07
branch: xv/2026-11-07-defects-stops
base: 1f325dd57c3e12eef670800ea39d10166aa2b4fa
next: forecaster
build: {"kind": "exploration", "ref": "explore/defects-stops"}
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
# A red that cannot run stops the slice, and an answered stop stays answered

## Scenario

1. A red that fails before any test runs is not a failing red. This means exit code 126 or 127, or the runner's own words that a test file could not load or that no tests were found. The scenario step stops with `red_cannot_run` for the person who set the work going, naming the error, and `next` stays `scenario`.
2. The runner words cover all 11 runners that `failing_tests` reads. A general error name (`ImportError`, `No such file or directory`) counts only when the output names no real failing test.
3. A red that runs its tests and some fail is a failing red, as now, even when its output prints a general error name.
4. When one test file cannot load and other tests fail for real, the step still stops.
5. An answer that bundles `slice_only_marks` accepts the slice-only marks, the same as an answer to that stop does.
6. After a directed edit, the stop the answer closed does not fire again, and neither does any stop bundled with it. This includes `ready_to_merge`. The answer's `--next` stands. Checks the edit can change, such as the suite, still run.
7. Decision 12 in the picture names a red that cannot run.
8. A `CHANGELOG.md` line names the new stop and the two fixes.
9. `EXPLORE-NOTES.md` is not in what merges.

## May ignore

- Runners other than the 11 that failing_tests reads.
- Runner output in a language other than English, or words that change when a runner is upgraded. A learnings note covers the upgrade case.
- A red that hangs or times out.
- The defects-tools items (#147, #148, #154). They have their own slice.

## Recording

.xv/recordings/2026-11-07-directed-edit-refire.md

## Log
- 2026-11-07T20:06:40+00:00 watch: slice opened by Sean Kennedy

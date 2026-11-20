---
id: 2026-11-19-removal-line
title: "A slice-only removal names its line, and the check reads the tree"
kind: defect
status: open
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-removal-line
base: 2ebb304bf2504ae8d50a2c3104889055f7309772
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
# A slice-only removal names its line, and the check reads the tree

## Scenario

A slice-only removal names its line, and the check reads the tree.

1. `xv record move --slice-only` takes `--file` and `--line <n>`: the line where the removed test starts, in the file at the commit where the step began (in a pairing, where the pairing began). The command reads that line's text from that commit and records the text with the number. It refuses a blank line, or a number past the end of the file, and records nothing. `--assertion` is a free note again; nothing reads it.
2. After a step, the removal check counts that line's text in the file now. If the count is not lower than at the start commit, the step stops with `removal_not_made`, naming the file, the line number and the text.
3. A removal committed before its move is recorded is taken (the pairing case).
4. A table test runs the check over a Python `def`, a JS `it("…")` whose title has spaces, and a line that is in the file twice: one copy removed passes; none removed stops.
5. The cleaner's brief says how to give the line. The picture says what each check reads, including that the check on accepted slice-only marks finds a name as any whole word in the file.
6. The watch brief's stop table lists the stop for a packet whose front matter says `change_misses_scenario: no` while its `## Scenario misses` section lists a miss. Two slice-only moves for the same file and line are one move.
7. A line in CHANGELOG.md.

## May ignore

- moves recorded before this change
- --deleted file removals
- moves that are not slice-only

## Recording

None. A feature starts from words.

## Log
- 2026-11-20T02:24:33+00:00 watch: slice opened by Sean Kennedy

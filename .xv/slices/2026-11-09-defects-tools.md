---
id: 2026-11-09-defects-tools
title: "Rebase, session-mode red and wall-flag fixes from v0.5's tool gaps"
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-11-09
branch: xv/2026-11-09-defects-tools
base: c6a1c95702e541b6b31ea7d49627e138d1e16a1b
next: forecaster
build: {"kind": "exploration", "ref": "explore/defects-tools"}
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
# Rebase, session-mode red and wall-flag fixes from v0.5's tool gaps

## Scenario

1. On a slice from a build, in session mode, `xv record report <id> scenario -` lands the red, runs it at base and on the build, takes the wall baseline at base, and saves the scenario checks, so `xv orders <id> --after scenario` gives the same stops as the CLI path. The scenario checkout is dropped by the next `xv step scenario` or by `xv close`. (#147 point 1)
2. A red that conflicts with the build stays on `refs/xv/<id>/red`. The `red_conflicts_with_build` question says so, and the next scenario pass starts from that red. (#147 point 2)
3. `xv close` deletes `refs/xv/<id>/red`. (#147)
4. `xv slice new --from` keeps the build's commit in the record. When the build ref is deleted, `xv record report` does not crash; with no build commit at all, the build's test files stay unrecorded and `unrecorded_move` stops for a person. (#147)
5. In session mode, a red whose command is joined with `;`, `||`, `|`, `&` or a newline is not kept: the earlier red stays, and `scenario_stopped` fires, with or without a build. (#147)
6. When a rebase stops on a maker's edit to a new test file, the `rebase_conflict` question says how to drop that file, and that `git status` shows it and `git diff` does not. An edit to a tracked file still names `git checkout -- <file>`. (#148 item 1)
7. `--accept-wall` and `--refuse-wall` take the test with its file, in the forms the covers check takes (`file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`). A bare name still works when one recommendation has it. A bare name that two files share is refused, and the refusal names each `file::test`. (#148 item 2)
8. After `xv slice rebase`, a red file that main also changed keeps the slice's own red edits in the wall hash. (#154 item 1)
9. After `xv slice rebase`, a directed CHANGELOG edit replaces the old line; it is not added beside it. (#154 item 2)
10. `tests/run.py` fails, and names the file, when a `test_*.py` file gives no test, and when the tests run are fewer than the tests collected. (#154 item 3)
11. The cleaner reports a step its brief tells it to take as `brief: slice-only removal`, and names a standard by its exact `###` heading in `.xv/standards.md`. `xv retro counts` does not count `brief:` lines. (#154 item 4)
12. One move told twice, with only a comma or a space of difference, is recorded once. (#154 item 5)
13. `xv slice new` refuses a missing `--recording` or `--scenario-file` path before it makes a branch or a worktree. (#154 item 6)
14. `xv slice new --ignore` can repeat. Every value reaches "## May ignore", in order, as a bullet list; a single value stays a plain paragraph.
15. The packet note on crowded picture lines: a second run leaves exactly one note, and an old note is stripped only where it starts a line. (#153 leftovers)
16. README, the watch, xv-slice and cleaner briefs, and the picture name what changed: `build.commit`, the wall-flag forms, `xv land-scenario`, `brief:` names, and the repeating `--ignore`. `CHANGELOG.md` has a line.
17. `EXPLORE-NOTES.md` is not in what merges.

## May ignore

- Why `tests/run.py` dropped a file; point 10 only guards against it happening again.
- Rewriting the old `.xv/retro/*.counts.json` files.
- Matching moves more loosely than point 12; `==` and `!=` stay different.
- That the maker sees diff3 conflict markers in a rebase conflict.

## Recording

None. A feature starts from words.

## Log
- 2026-11-09T13:01:20+00:00 watch: slice opened by Sean Kennedy

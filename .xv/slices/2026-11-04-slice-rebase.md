---
id: 2026-11-04-slice-rebase
title: "A slice can be brought up to date with its base: #20"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-slice-rebase
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
# A slice can be brought up to date with its base: #20

## Scenario

# A slice can be brought up to date with its base: #20

When this is done:

1. `xv slice rebase <id> [--onto <ref>]` rebases the slice branch onto the new base. With no `--onto`, it uses the base the slice started from (`worktrees.base`, then `origin/HEAD`).
2. A conflict in a test file stops for the person who set the work going. The agent does not resolve it.
3. Conflicts in `CHANGELOG.md` and `.xv/estimation.md` keep both sides.
4. The record's `base` moves to the commit of the `--onto` ref. So a slice that started from a PR's head moves to that PR's rebased head, not to the merge base with `main`.
5. Every commit the record names (`base`, `pre_maker_commit`, `cleaner_commit`) moves with the rebase. If the rebase drops a commit the record names, it stops for the person.
6. The wall is hashed again for test files the slice has not touched. The recorded moves are kept.
7. The suite runs again, and a red suite stops the slice.
8. Each new stop is decided in `scripts/orders.py`.
9. A conflict in `.xv/picture.md` stops for the person who set the work going. A person resolves it.
10. `xv slice rebase` works on a closed slice that is waiting for its merge, as well as on an open one.
11. The agent that does the rebase resolves a conflict in any other file. It also looks for changes in the new base that break or contradict what the slice does, even where git shows no conflict. It fixes what it can. It reports each conflict, each fix, and each problem it could not fix. A problem it could not fix stops for the person who set the work going.
12. The maker does the rebase, in a fresh context, with a rebase part in its brief.
13. When the maker resolved a conflict or fixed a logical conflict, the slice goes to the cleaner and then the guardian, and a closed slice opens again. A clean rebase, where git finds no conflict and the maker changes nothing, leaves the slice where it was, once the suite is green.

## May ignore

--merge, merging the base in instead of rebasing; trial repos, where .xv/ is its own repo (#21); prototype variant branches; old slice records under .xv/slices/, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T22:22:50+00:00 watch: slice opened by Sean Kennedy

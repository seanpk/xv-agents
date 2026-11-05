---
id: 2026-11-05-from-build
title: "A slice can start from a build that already exists: #113"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-from-build
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
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
# A slice can start from a build that already exists: #113

## Scenario

When this is done:

1. `xv slice new --from <ref>` opens a slice from a build that already exists. The slice branch starts at `<ref>`. `base` is the branch it will merge into. The record's `build` says `exploration` and names the ref. A slice with no `--from` has `build: none`.
2. When the person gives `--from`, or says a build is running, the `xv-slice` skill writes the scenario with the person from what runs. It does not ask about a build otherwise.
3. The `xv-slice` skill offers the two ways to build to find out when the scenario will not settle: the answers are not clear, the talk goes round without settling, or the person starts to wonder what they want. The two ways are a prototype slice, as now, or an exploration. For an exploration it opens no slice. It tells the person to build with an agent, and to open the slice with `xv slice new --from <ref>` when the scenario can be written from what runs. The `watch` skill says the same offer may be made at a stop after the scenario step, before the maker runs.
4. By default the scenario agent never sees the build. It runs in a worktree at `base`, and its prompt names no build branch or diff. The record says `build_shared: no`.
5. With `xv slice new --from <ref> --share-build`, the scenario agent's prompt names the build's ref as a reference. The prompt says the build is a reference only: the red tests what the scenario says, and does not assume the code will look like the build. The record says `build_shared: yes`.
6. The red must fail on the base, as now. Then it runs on the build.
7. Each red test that fails on the build goes to the maker as a miss against the scenario, with no stop. The maker starts from the build.
8. When every red test passes on the build, the slice skips the maker and goes to the cleaner.
9. Each new stop is decided in `scripts/orders.py`.
10. `CHANGELOG.md` has a line for each brief change.

## May ignore

a kept prototype pick (slice G, #117); what a very large build means for the wall and the packet; old slice records; turning a slice that is already open into an exploration.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T18:29:42+00:00 watch: slice opened by Sean Kennedy

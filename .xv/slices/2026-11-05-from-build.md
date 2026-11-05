---
id: 2026-11-05-from-build
title: "A slice can start from a build that already exists: #113"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-from-build
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 750000, "turns": null, "usd": 4.0, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-10-29-stop-decisions"], "note": "Medians of the three wide feature rows (551k, 756k, 674k tokens; usd 3.92, 4.50, 3.87). Turns are not in the guide, so null. The 2026-11-04-slice-rebase row (1.42M tokens, $8.38) is the reopen high-end and is not in the median."}, {"harness": "claude", "model": "opus", "tokens": 370000, "turns": null, "usd": 4.3, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-10-29-stop-decisions"], "note": "Medians of the same three rows (325k, 322k, 392k tokens; usd 3.97, 4.34, 4.89). Turns are not in the guide, so null. The guardian is the usd driver; slice-rebase ran 9 opus passes for $12.74."}], "wall_s": 4500, "shape": "wide", "breadth": "CLI flag and record fields in xv slice new, the xv-slice and watch skills, the scenario agent prompt, new stops in scripts/orders.py, CHANGELOG, and tests/**. Expect the widest maker diff of recent feature slices; the red-on-build loop and the unsettled-scenario stop are where a reopen would come from."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4385, "cache_read": 26136, "cache_write": 29982, "tokens": 34371, "usd": 0.0085, "turns": 3, "wall_s": 22.3, "session": "39bad001-3bd1-4f11-b30f-39bbd499f32b", "step": "forecaster", "at": "2026-11-05T18:30:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-from-build/01-forecaster.out"}]
stops: [{"at": "2026-11-05T18:30:09+00:00", "step": "forecaster", "order": "read_only_broken", "seat": "originator", "question": "The forecaster is read-only and changed: .xv/config.yml. Revert it before going on.", "answered_by": [], "answer": null, "also": ["budget_not_set"], "budget_seen": null, "options": [{"text": "Keep the Opus scenario line Sean approved; the watch moves it out of the forecast commit into its own commit 'as Sean directed', and the forecast stands", "settles": "the config change was the watch's, not the forecaster's; the forecast stands", "amends": false}, {"text": "Remove the line and run the forecaster again", "settles": "the forecast is rerun on a clean tree", "amends": false}], "recommended": 1}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet 750k tokens and claude/opus 370k tokens, wide shape; reopen risk is the main gap, and turns have no history.", "at": "2026-11-05T18:30:09+00:00"}], "forecaster": {"at": "2026-11-05T18:30:09+00:00", "wrote": [".xv/config.yml"]}}
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
- 2026-11-05T18:30:09+00:00 forecaster: done: Forecast claude/sonnet 750k tokens and claude/opus 370k tokens, wide shape; reopen risk is the main gap, and turns have no history.
- 2026-11-05T18:30:09+00:00 watch: stop (read_only_broken) for originator: The forecaster is read-only and changed: .xv/config.yml. Revert it before going on.
- 2026-11-05T18:30:38+00:00 watch: offered 2 options for read_only_broken

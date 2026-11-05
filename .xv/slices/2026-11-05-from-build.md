---
id: 2026-11-05-from-build
title: "A slice can start from a build that already exists: #113"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-from-build
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 750000, "turns": null, "usd": 4.0, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-10-29-stop-decisions"], "note": "Medians of the three wide feature rows (551k, 756k, 674k tokens; usd 3.92, 4.50, 3.87). Turns are not in the guide, so null. The 2026-11-04-slice-rebase row (1.42M tokens, $8.38) is the reopen high-end and is not in the median."}, {"harness": "claude", "model": "opus", "tokens": 370000, "turns": null, "usd": 4.3, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-10-29-stop-decisions"], "note": "Medians of the same three rows (325k, 322k, 392k tokens; usd 3.97, 4.34, 4.89). Turns are not in the guide, so null. The guardian is the usd driver; slice-rebase ran 9 opus passes for $12.74."}], "wall_s": 4500, "shape": "wide", "breadth": "CLI flag and record fields in xv slice new, the xv-slice and watch skills, the scenario agent prompt, new stops in scripts/orders.py, CHANGELOG, and tests/**. Expect the widest maker diff of recent feature slices; the red-on-build loop and the unsettled-scenario stop are where a reopen would come from."}
budget: {"tokens": 1200000, "usd": 10.5, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_from_build.py", "tests/fake_agent.py"], "command": "cd tests && python3 -m unittest test_from_build", "failure": "AssertionError: [... 'slice', 'new', 's1', ..., '--from', 'explore-milk'] failed 2: xv: error: unrecognized arguments: --from explore-milk", "watch_first_green": "Build something on a branch, run `xv slice new <id> --from <branch>` and `xv run <id>`. Watch the scenario agent write its red in a checkout without the build, the red fail on the base, and the slice go to the cleaner with no maker run when the build passes, or to the maker, starting from the build, with the failing tests named as misses. Check that build and build_shared in the record read sensibly and that base is the merge target, not the build."}
wall_baseline: {"commit": "a68d457e07455ba684142385c2e9f09f77bed32d", "count": 66, "digest": "f42ddaeaccf9e022", "file": ".xv/slices/2026-11-05-from-build.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_from_build.py", "test": "test_unreleased_has_a_line_for_113_naming_each_brief_it_changes", "why": "It checks one CHANGELOG line, which has no value once the slice has merged (rules.md: a test of one CHANGELOG line is slice-only)."}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4385, "cache_read": 26136, "cache_write": 29982, "tokens": 34371, "usd": 0.0085, "turns": 3, "wall_s": 22.3, "session": "39bad001-3bd1-4f11-b30f-39bbd499f32b", "step": "forecaster", "at": "2026-11-05T18:30:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-from-build/01-forecaster.out"}, {"harness": "claude", "model": "opus", "model_id": "claude-opus-5-5", "tokens_in": 62, "tokens_out": 27413, "cache_read": 2509665, "cache_write": 111938, "tokens": 139413, "usd": 1.9459, "turns": 38, "wall_s": 757.5, "session": "02174833-f826-467f-bbdd-c2123640b36d", "step": "scenario", "at": "2026-11-05T18:46:30+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-from-build/02-scenario.out"}]
stops: [{"at": "2026-11-05T18:30:09+00:00", "step": "forecaster", "order": "read_only_broken", "seat": "originator", "question": "The forecaster is read-only and changed: .xv/config.yml. Revert it before going on.", "answered_by": ["Sean Kennedy"], "answer": "F: 1. I'll take your table for budgets", "also": ["budget_not_set"], "options": [{"text": "Keep the Opus scenario line Sean approved; the watch moves it out of the forecast commit into its own commit 'as Sean directed', and the forecast stands", "settles": "the config change was the watch's, not the forecaster's; the forecast stands", "amends": false}, {"text": "Remove the line and run the forecaster again", "settles": "the forecast is rerun on a clean tree", "amends": false}], "recommended": 1, "answered_at": "2026-11-05T18:33:46+00:00", "pick": 1, "settled": "The Opus scenario line was the watch's change, made in F's worktree while the forecaster ran; it is now its own commit 'as Sean directed' (14fda45), and the forecast stands. Sean set the budget at 1,200,000 tokens and $10.50.", "new_info": "none", "cause": "watch: the watch edited .xv/config.yml in F's worktree while the forecaster ran, so the step counted it as the forecaster's write", "bundle": ["budget_not_set"], "budget_change": {"from": null, "to": {"tokens": 1200000, "usd": 10.5}}}, {"at": "2026-11-05T18:46:32+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The scenario agent did not cover `--share-build` given without `--from`: The scenario does not say whether xv slice new refuses it or ignores it, so the red does not pick an answer.", "answered_by": [], "answer": null, "also": ["slice_only_marks"], "budget_seen": {"tokens": 1200000, "usd": 10.5, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet 750k tokens and claude/opus 370k tokens, wide shape; reopen risk is the main gap, and turns have no history.", "at": "2026-11-05T18:30:09+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for xv slice new --from: record fields, scenario agent kept at base unless --share-build, red run on base then build, maker skipped when the build passes, skill and CHANGELOG wording", "at": "2026-11-05T18:46:30+00:00"}], "forecaster": {"at": "2026-11-05T18:30:09+00:00", "wrote": [".xv/config.yml"]}, "scenario": {"at": "2026-11-05T18:46:30+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "ip one.\\n- Do an agent\\'s work itself: write the red, make it work, clean it, or review it.\\n- Answer a stop on a person\\'s behalf, or read silence as an answer.\\n\\n## Writes to the slice record\\n\\nThrough `xv step` and `xv record`: each step\\'s report, the actual spend, each stop raised and the seat it went to, each answer and who gave it, and the decision record when two people decided.\\n\\n## Stop and report when\\n\\n- A standing order fires.\\n- A script fails, or a step cannot run (a missing CLI, a missing file). Say what failed and stop; do not work around it.\\n- The person asks for anything on the may-not list. Say which line it is and what the person can do instead.\\n'\n\n----------------------------------------------------------------------\nRan 28 tests in 1.431s\n\nFAILED (failures=27)\n", "old_red_changed": [], "red_gaps": [], "unreadable": [], "not_covered": [{"item": "`--share-build` given without `--from`", "why": "The scenario does not say whether xv slice new refuses it or ignores it, so the red does not pick an answer."}], "missed_points": []}}
old_tests_forced: []
may_not_files: []
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
- 2026-11-05T18:33:46+00:00 Sean Kennedy: set budget
- 2026-11-05T18:33:46+00:00 Sean Kennedy: answered read_only_broken: F: 1. I'll take your table for budgets
- 2026-11-05T18:33:46+00:00 watch: scribe: wrote settled, new_info, cause for read_only_broken as the scribe of Sean Kennedy
- 2026-11-05T18:46:30+00:00 scenario: red: Red for xv slice new --from: record fields, scenario agent kept at base unless --share-build, red run on base then build, maker skipped when the build passes, skill and CHANGELOG wording
- 2026-11-05T18:46:32+00:00 watch: stop (red_misses_scenario) for originator: The scenario agent did not cover `--share-build` given without `--from`: The scenario does not say whether xv slice new refuses it or ignores it, so the red does not pick an answer.

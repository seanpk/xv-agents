---
id: 2026-11-04-slice-rebase
title: "A slice can be brought up to date with its base: #20"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-slice-rebase
base: a6e023bd0ffeed4f6ce45990c668742a8f758419
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 550000, "turns": null, "usd": 3.9, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "guide has no turns column; tokens and usd are medians of the three wide sonnet actuals (551k, 674k, 395k; $3.92, $3.87, $2.27)"}, {"harness": "claude", "model": "opus", "tokens": 325000, "turns": null, "usd": 4.0, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "guide has no turns column; tokens and usd are medians of the three wide opus actuals (325k, 392k, 230k; $3.97, $4.89, $2.79)"}], "wall_s": 2900, "shape": "wide", "breadth": "Expect the change to span the xv rebase command, scripts/orders.py stop decisions, the record's base and pre_maker/cleaner commit moves, the wall rehash for untouched test files, and CHANGELOG, estimation and picture conflict handling; a logical-conflict fix by the maker likely sends it through cleaner and guardian again, as the basis rows did."}
budget: {"tokens": 875000, "usd": 7.9, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4426, "cache_read": 24480, "cache_write": 27421, "tokens": 31851, "usd": 0.0079, "turns": 3, "wall_s": 21.4, "session": "e8ebc2a8-9220-4230-bfef-6fc2406600a7", "step": "forecaster", "at": "2026-11-04T22:23:11+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-slice-rebase/01-forecaster.out"}]
stops: [{"at": "2026-11-04T22:23:11+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-slice-rebase budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "875000 tokens, 7.90 USD: the forecast", "settles": "Sean sets budget {tokens: 875000, usd: 7.9}; next is scenario, once slice B has merged and D's branch is moved onto it.", "amends": false}, {"text": "1310000 tokens, 11.85 USD: the forecast plus a half", "settles": "Sean sets budget {tokens: 1310000, usd: 11.85}; next is scenario, once slice B has merged and D's branch is moved onto it.", "amends": false}, {"text": "Set aside", "settles": "The slice stays at its budget stop.", "amends": false}], "recommended": 1, "answered_at": "2026-11-04T22:47:44+00:00", "pick": 1, "settled": "Sean sets budget {tokens: 875000, usd: 7.9}; next is scenario, once slice B has merged and D's branch is moved onto it.", "new_info": "none", "cause": "decision: the budget is set by a person from the forecast", "budget_change": {"from": null, "to": {"tokens": 875000, "usd": 7.9}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Sonnet about 550k tokens and $3.9; opus about 325k tokens and $4.0; wall about 2900 s; shape wide.", "at": "2026-11-04T22:23:11+00:00"}], "forecaster": {"at": "2026-11-04T22:23:11+00:00", "wrote": []}}
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
- 2026-11-04T22:23:11+00:00 forecaster: done: Sonnet about 550k tokens and $3.9; opus about 325k tokens and $4.0; wall about 2900 s; shape wide.
- 2026-11-04T22:23:11+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-slice-rebase budget ... --by <name>`).
- 2026-11-04T22:23:19+00:00 watch: offered 3 options for budget_not_set
- 2026-11-04T22:47:44+00:00 Sean Kennedy: set budget
- 2026-11-04T22:47:44+00:00 Sean Kennedy: answered budget_not_set: 1
- 2026-11-04T22:47:44+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy

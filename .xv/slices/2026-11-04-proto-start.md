---
id: 2026-11-04-proto-start
title: "A prototype variant is never dropped when the three start at once: #61"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-proto-start
base: c7b8bbff58fc46160ba83d08d0e899d7beffaaf2
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 320000, "turns": null, "usd": 1.6, "basis": ["2026-10-26-worktree-setup", "2026-10-27-wall-red-files", "2026-10-27-red-joins", "2026-10-27-retro-accept-fields"], "note": "guide has no turn column; actual sonnet tokens of those rows were 235k-376k, usd 1.28-2.25"}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.3, "basis": ["2026-10-26-worktree-setup", "2026-10-27-wall-red-files", "2026-10-27-red-joins", "2026-10-27-retro-accept-fields"], "note": "guide has no turn column; actual opus tokens of those rows were 176k-302k, usd 2.04-3.62"}], "wall_s": 1400, "shape": "narrow", "breadth": "Changes the git setup path in prototype start (serialise per-variant remove, branch delete, worktree add) and records a refused variant as not finished; touches prototype start code and its tests, no record shape change."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3310, "cache_read": 23905, "cache_write": 25109, "tokens": 28423, "usd": 0.0069, "turns": 3, "wall_s": 16.7, "session": "4b02693d-2b10-4052-a075-2736bb56b4de", "step": "forecaster", "at": "2026-11-04T18:51:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-proto-start/01-forecaster.out"}]
stops: [{"at": "2026-11-04T18:51:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-proto-start budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~320k tokens and claude/opus ~200k tokens for a narrow git-setup defect; both keys have history, no reopen priced in full.", "at": "2026-11-04T18:51:45+00:00"}], "forecaster": {"at": "2026-11-04T18:51:45+00:00", "wrote": []}}
---
# A prototype variant is never dropped when the three start at once: #61

## Scenario

# A prototype variant is never dropped when the three start at once: #61

What happened: on the #55 slice, `xv prototype start` ran the three variants at once, and variant b never called its agent. No error reached the person. The guess in #61 is that two `git branch -D` or `git worktree add` commands hit the same git lock; that cause is not confirmed.

What should happen:

1. The git setup for one variant (removing the old worktree, deleting the branch, adding the worktree) never runs at the same time as another variant's setup. The agents still run at the same time. A fake `git` that logs each start and end time shows this.
2. When git refuses one variant's setup, that variant is not dropped. It is recorded as not finished, with its error. The side-by-side file shows the error. The other two variants still run. A second `xv prototype start` runs it again, as it does now for any variant that did not finish.

## May ignore

#58 (building the variants one at a time, or in turns): the variants still run at the same time; prototypes applying their own stop, left for #117; old prototype records, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T18:51:28+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T18:51:45+00:00 forecaster: done: Forecast claude/sonnet ~320k tokens and claude/opus ~200k tokens for a narrow git-setup defect; both keys have history, no reopen priced in full.
- 2026-11-04T18:51:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-proto-start budget ... --by <name>`).

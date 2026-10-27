---
id: 2026-10-27-init-rerun
title: xv init runs again without crashing
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-init-rerun
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 482000, "turns": null, "usd": 0.31, "basis": ["2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 284000, "turns": null, "usd": 0.55, "basis": ["2026-10-25-diff-count"]}], "wall_s": 300, "shape": "narrow", "breadth": "One branch in cmd_init (runners is set only when config.yml is written) plus a test under tests/**. The guide has no turns history. Nine of the last ten closed slices reopened or reran (scenario, maker, cleaner, guardian), with the clean pass as the floor, so the realistic spend is about 2-3x the clean figure."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 5136, "cache_read": 25011, "cache_write": 9833, "tokens": 14973, "usd": 0.0048, "turns": 3, "wall_s": 24.9, "session": "a0e04c36-3d84-40c8-96b9-a3b77595d93d", "step": "forecaster", "at": "2026-10-27T14:28:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-init-rerun/01-forecaster.out"}]
stops: [{"at": "2026-10-27T14:28:21+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-rerun budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Clean single pass is about 482k sonnet tokens and 284k opus tokens, about 300 s wall; 9 of 10 recent slices reopened, so a budget at the clean figure is likely to be exceeded.", "at": "2026-10-27T14:28:21+00:00"}], "forecaster": {"at": "2026-10-27T14:28:21+00:00", "wrote": []}}
---
# xv init runs again without crashing

## Scenario

`xv init` runs again in a repo whose `.xv/config.yml` already exists, to fill in a missing file, without crashing. Today `runners` is set only when init writes the config (`if "config.yml" in written:` in `cmd_init`, `scripts/run.py`) and read later by `if len(runners) > 1:`, so a second run raises `UnboundLocalError` before it prints anything. After the fix, a second run with a missing `.xv/pitch.md` writes the starter pitch, keeps every existing file, prints its usual JSON output, and exits 0. (seanpk/xv-agents#40)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:27:49+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T14:28:21+00:00 forecaster: done: Clean single pass is about 482k sonnet tokens and 284k opus tokens, about 300 s wall; 9 of 10 recent slices reopened, so a budget at the clean figure is likely to be exceeded.
- 2026-10-27T14:28:21+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-rerun budget ... --by <name>`).

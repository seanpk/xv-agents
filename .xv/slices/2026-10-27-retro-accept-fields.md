---
id: 2026-10-27-retro-accept-fields
title: "xv retro accept keeps the candidate's fields"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-retro-accept-fields
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 1280000, "turns": null, "usd": 0.65, "basis": ["2025-10-25-diff-count", "2026-10-25-suite-red-quote"], "note": "Midpoint of a one-pass defect (diff-count, 482k, $0.31) and a defect that reopened once (suite-red-quote, 2.08M, $0.99). Turns are not recorded in the guide. Six of seven narrow claude/sonnet rows reopened on accept stops, so expect the upper row, not the lower. The worktree-setup row (376k tokens at $2.25 over four rounds) looks inconsistent and was not used."}, {"harness": "claude", "model": "opus", "tokens": 675000, "turns": null, "usd": 0.92, "basis": ["2026-10-25-diff-count", "2026-10-25-suite-red-quote"], "note": "Midpoint of diff-count (284k, $0.55) and suite-red-quote (1.07M, $1.28). Turns are not recorded in the guide. Opus runs the guardian only, so it moves with reopens, not with the maker."}], "wall_s": 480, "shape": "narrow", "breadth": "Changes the kind == open branch of scripts/retro.py and the seen: writer that standard and rule accepts also use, so three accept kinds and their tests move; the rest of retro.py and xv promote should not move."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4452, "cache_read": 25027, "cache_write": 9941, "tokens": 14397, "usd": 0.0045, "turns": 3, "wall_s": 21.0, "session": "ba1a21fa-f847-4719-9625-af65cb1edd4d", "step": "forecaster", "at": "2026-10-27T14:28:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-retro-accept-fields/01-forecaster.out"}]
stops: [{"at": "2026-10-27T14:28:42+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-retro-accept-fields budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from claude/sonnet and claude/opus rows: one clean pass is about 480k sonnet tokens, but six of seven narrow sonnet rows reopened, so the midpoint is a risk, not a cap.", "at": "2026-10-27T14:28:42+00:00"}], "forecaster": {"at": "2026-10-27T14:28:42+00:00", "wrote": []}}
---
# xv retro accept keeps the candidate's fields

## Scenario

`xv retro accept <packet> <n> --by <name>` writes an Open entry in `.xv/learnings.md` that keeps the candidate's own fields. Today (`scripts/retro.py`, the `kind == "open"` entry) `said:` gets the candidate's `miss`, `rule:` gets its title, the candidate's `said:` and `rule:` lines are dropped, and `--by` is not written. After the fix, the entry keeps `from`, `miss`, `said` and `rule` from the candidate, writes `seen:` as `owner/repo@date` (the same name `xv promote` uses, for example `seanpk/xv-agents@2026-10-27`, falling back to the folder name when the repo has no remote), and says who accepted it. A standard or a rule accepted the same way also writes `seen:` as `owner/repo@date`. (seanpk/xv-agents#43)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:27:49+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T14:28:42+00:00 forecaster: done: Forecast from claude/sonnet and claude/opus rows: one clean pass is about 480k sonnet tokens, but six of seven narrow sonnet rows reopened, so the midpoint is a risk, not a cap.
- 2026-10-27T14:28:42+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-retro-accept-fields budget ... --by <name>`).

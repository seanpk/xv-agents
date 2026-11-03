---
id: 2026-11-03-codex-spend
title: spend.py reads Codex output
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-03
branch: xv/2026-11-03-codex-spend
base: 882af07d4ace445d77fa52dc5bf535f0b89c277c
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 400000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-stop-decisions"], "note": "guide has no turns column"}, {"harness": "claude", "model": "opus", "tokens": 230000, "turns": null, "usd": 2.8, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-stop-decisions"], "note": "guide has no turns column"}], "wall_s": 2000, "shape": "wide", "breadth": "Touches the spend reader, the xv spend CLI, the step runner's stdin close, and docs/harness-notes.md; the step runner change is the likeliest reopen."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3010, "cache_read": 23868, "cache_write": 24118, "tokens": 27132, "usd": 0.0066, "turns": 3, "wall_s": 14.9, "session": "4c24955a-0fc6-4b72-906f-194b871d24c9", "step": "forecaster", "at": "2026-11-03T20:52:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-03-codex-spend/01-forecaster.out"}]
stops: [{"at": "2026-11-03T20:52:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-03-codex-spend budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet at 400k tokens and claude/opus at 230k tokens from wide feature rows; no codex key because no codex agent runs on this slice.", "at": "2026-11-03T20:52:45+00:00"}], "forecaster": {"at": "2026-11-03T20:52:45+00:00", "wrote": []}}
---
# spend.py reads Codex output

## Scenario

# spend.py reads Codex output

When this is done:

1. A step run with `codex exec --json` records a spend row with harness `codex`. Its tokens come from the `turn.completed` usage, added up over all turns. `session` is the `thread_id`, `turns` is the number of turns, and `usd` is empty, because Codex reports no cost.
2. Cached input goes in `cache_read`, not in `tokens_in`, the same as Claude rows. Output includes the reasoning tokens.
3. `xv spend codex-result <file>` reads a saved run, the same as the other readers.
4. `docs/harness-notes.md` says what was checked on 2026-11-03: Codex runs headless, where its usage comes from, and that `AGENTS.md` and the skills still load with `--ignore-user-config --ignore-rules`.
5. A step's agent CLI gets a closed stdin. A Codex step started while stdin is still open finishes, and it does not wait for input.

## May ignore

Dollar cost for Codex; a budget cap for Codex; a clean baseline for Codex (a separate CODEX_HOME); adding Codex to evals/harnesses.json; #112.

## Recording

None. A feature starts from words.

## Log
- 2026-11-03T20:52:25+00:00 watch: slice opened by Sean Kennedy
- 2026-11-03T20:52:45+00:00 forecaster: done: Forecast claude/sonnet at 400k tokens and claude/opus at 230k tokens from wide feature rows; no codex key because no codex agent runs on this slice.
- 2026-11-03T20:52:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-03-codex-spend budget ... --by <name>`).

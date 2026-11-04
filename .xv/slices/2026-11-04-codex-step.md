---
id: 2026-11-04-codex-step
title: "Codex runs as a step, and #115"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-codex-step
base: 704f635e0b022b847e338a744d9415165be7fd20
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 200000, "turns": null, "usd": 1.0, "basis": ["2026-11-03-codex-spend", "2026-10-27-allowed-commands"], "note": "turns not recorded in the guide; the reopen risk on the Codex event shape is unpriced beyond this band"}, {"harness": "claude", "model": "opus", "tokens": 130000, "turns": null, "usd": 1.7, "basis": ["2026-11-03-codex-spend", "2026-10-27-allowed-commands"], "note": "turns not recorded in the guide; usd priced from the basis rows because opus usd runs high per token"}], "wall_s": 900, "shape": "narrow", "breadth": "Touches the step report reader, the eval runner's final-message path, session_of, harnesses.json, three docs and one relies-on line; each change is additive, and the claude, opencode and grok paths should not move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4644, "cache_read": 25522, "cache_write": 23150, "tokens": 27798, "usd": 0.0072, "turns": 3, "wall_s": 24.8, "session": "f433f962-301b-4c5e-a440-72c5ac46d5ce", "step": "forecaster", "at": "2026-11-04T13:10:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-codex-step/01-forecaster.out"}]
stops: [{"at": "2026-11-04T13:10:21+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-codex-step budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~200k tokens and opus ~130k for a narrow feature, basing both on the two closest claude rows; no codex history is needed because no codex agent runs on this slice.", "at": "2026-11-04T13:10:21+00:00"}], "forecaster": {"at": "2026-11-04T13:10:21+00:00", "wrote": []}}
---
# Codex runs as a step, and #115

## Scenario

# Codex runs as a step, and #115

When this is done:

1. A step run with `codex exec --json` gets its `xv-report` applied to the record, the same as Claude, Grok and opencode. The report is in the last `agent_message` of an `item.completed` event.
2. For a Codex run, the eval runner's final message is Codex's last `agent_message`.
3. `evals/harnesses.json` has a `codex` entry: `codex exec --json` with the model `gpt-6.1-terra` and the sandbox off (`--dangerously-bypass-approvals-and-sandbox`). Every step runs on that one model, as the `claude` entry runs Sonnet; Terra stands for Sonnet, Sol for Opus. Grok also runs with its permission checks off, and each eval runs on a throwaway copy of the fixture. The entry's note says that the brief is not the whole prompt, because `AGENTS.md` and the skills load.
4. `README.md:3` and `:392` and `docs/decisions.md` item 48 say what is true now: Codex runs headless, `spend.py` reads its `--json` events, and Codex reports no dollars.
5. `docs/relies-on.md` has a line for the Codex event shape that `spend.py` and the report reader use, so `xv check drift` watches it.
6. `session_of` returns the `thread_id` for a Codex run.

## May ignore

Running the evals (after the merge, at Sean's direction); a clean Codex baseline; Codex dollars and a budget cap; #112; Cursor.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T13:09:52+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T13:10:21+00:00 forecaster: done: Forecast sonnet ~200k tokens and opus ~130k for a narrow feature, basing both on the two closest claude rows; no codex history is needed because no codex agent runs on this slice.
- 2026-11-04T13:10:21+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-codex-step budget ... --by <name>`).

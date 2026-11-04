---
id: 2026-11-04-codex-step
title: "Codex runs as a step, and #115"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-codex-step
base: 704f635e0b022b847e338a744d9415165be7fd20
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

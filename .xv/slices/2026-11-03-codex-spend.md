---
id: 2026-11-03-codex-spend
title: spend.py reads Codex output
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-03
branch: xv/2026-11-03-codex-spend
base: 882af07d4ace445d77fa52dc5bf535f0b89c277c
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

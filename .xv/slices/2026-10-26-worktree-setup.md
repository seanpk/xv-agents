---
id: 2026-10-26-worktree-setup
title: "A slice starts from the right base, and the project sets up its worktree"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-26
branch: xv/2026-10-26-worktree-setup
base: 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 1440000, "turns": null, "usd": 0.8, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 1120000, "turns": null, "usd": 1.43, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-diff-count"]}], "wall_s": 600, "shape": "narrow", "breadth": "xv slice new (--base, setup stop), teardown on close, xv check listing, defaults/config.yml and their tests; agent sequence unchanged."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4369, "cache_read": 25049, "cache_write": 8943, "tokens": 38365, "usd": 0.0042, "turns": 3, "wall_s": 20.8, "session": "72b021eb-f963-4f49-b9cc-d1ecc222f3b9", "step": "forecaster", "at": "2026-10-26T15:39:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-26-worktree-setup/01-forecaster.out"}]
stops: [{"at": "2026-10-26T15:39:23+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-26-worktree-setup budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~1.44M tokens and opus ~1.12M tokens on the narrow feature shape, from init-tries-guesses with diff-count as the floor; reopen risk is high.", "at": "2026-10-26T15:39:23+00:00"}], "forecaster": {"at": "2026-10-26T15:39:23+00:00", "wrote": []}}
---
# A slice starts from the right base, and the project sets up its worktree

## Scenario

`.xv/config.yml` gains a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new <id> --base <ref>` starts the slice branch from that ref. Without `--base`, it uses `worktrees.base`. With neither, it uses the remote's default branch (`origin/HEAD`), not the main checkout's HEAD; with no remote, HEAD as today. The record's `base` is that commit. After it makes the worktree and before the forecaster, `xv slice new` runs `worktrees.setup` in the worktree, with `{worktree}` replaced by the worktree's path. A non-zero exit is a stop for the person who set the work going, and the question quotes the command's last lines. When the slice closes, `teardown` runs the same way. `xv check` lists both commands with the other project-layer settings. `defaults/config.yml` shows the block, commented out. (seanpk/xv-agents#27; Sean approves the new stop, solo.)

## May ignore

`worktrees.path` (where worktrees live); removing the worktree itself

## Recording

None. A feature starts from words.

## Log
- 2026-10-26T15:38:56+00:00 watch: slice opened by Sean Kennedy
- 2026-10-26T15:39:23+00:00 forecaster: done: Forecast sonnet ~1.44M tokens and opus ~1.12M tokens on the narrow feature shape, from init-tries-guesses with diff-count as the floor; reopen risk is high.
- 2026-10-26T15:39:23+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-26-worktree-setup budget ... --by <name>`).

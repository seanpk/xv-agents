---
id: 2026-10-26-worktree-setup
title: "A slice starts from the right base, and the project sets up its worktree"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-26
branch: xv/2026-10-26-worktree-setup
base: 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
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
# A slice starts from the right base, and the project sets up its worktree

## Scenario

`.xv/config.yml` gains a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new <id> --base <ref>` starts the slice branch from that ref. Without `--base`, it uses `worktrees.base`. With neither, it uses the remote's default branch (`origin/HEAD`), not the main checkout's HEAD; with no remote, HEAD as today. The record's `base` is that commit. After it makes the worktree and before the forecaster, `xv slice new` runs `worktrees.setup` in the worktree, with `{worktree}` replaced by the worktree's path. A non-zero exit is a stop for the person who set the work going, and the question quotes the command's last lines. When the slice closes, `teardown` runs the same way. `xv check` lists both commands with the other project-layer settings. `defaults/config.yml` shows the block, commented out. (seanpk/xv-agents#27; Sean approves the new stop, solo.)

## May ignore

`worktrees.path` (where worktrees live); removing the worktree itself

## Recording

None. A feature starts from words.

## Log
- 2026-10-26T15:38:56+00:00 watch: slice opened by Sean Kennedy

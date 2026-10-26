---
id: 2026-10-26-worktree-setup
title: "A slice starts from the right base, and the project sets up its worktree"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-26
branch: xv/2026-10-26-worktree-setup
base: 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2
next: cleaner
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 1440000, "turns": null, "usd": 0.8, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 1120000, "turns": null, "usd": 1.43, "basis": ["2026-10-25-init-tries-guesses", "2026-10-25-diff-count"]}], "wall_s": 600, "shape": "narrow", "breadth": "xv slice new (--base, setup stop), teardown on close, xv check listing, defaults/config.yml and their tests; agent sequence unchanged."}
budget: {"tokens": 500000, "usd": 4, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_worktree_setup.py"], "command": "cd tests && python3 -m unittest test_worktree_setup", "failure": "xv slice new s1 --base <ref> failed 2: usage: xv [-h] {slice,step,run,close,init,guard} ...", "watch_first_green": "Start a slice with a setup command that writes a file, and watch that file appear in the new worktree before the forecaster runs. Make setup exit non-zero and watch the stop quote its last output lines. Close the slice and watch teardown run with the worktree path. Run xv check and see both commands listed."}
wall_baseline: {"commit": "f58c9a32c0c9645d3716696308cb17cc5e98c6a5", "count": 36, "digest": "1e40f6e6117ffb04", "file": ".xv/slices/2026-10-26-worktree-setup.wall.json"}
moved_tests: []
suite: green
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4369, "cache_read": 25049, "cache_write": 8943, "tokens": 38365, "usd": 0.0042, "turns": 3, "wall_s": 20.8, "session": "72b021eb-f963-4f49-b9cc-d1ecc222f3b9", "step": "forecaster", "at": "2026-10-26T15:39:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-26-worktree-setup/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 32, "tokens_out": 8202, "cache_read": 478906, "cache_write": 34733, "tokens": 42967, "usd": 0.2689, "turns": 19, "wall_s": 178.8, "session": "e557121b-5e6f-4439-942d-5e731c680a68", "step": "scenario", "at": "2026-10-26T21:02:16+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-26-worktree-setup/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 38, "tokens_out": 10860, "cache_read": 735423, "cache_write": 46900, "tokens": 57798, "usd": 0.3698, "turns": 34, "wall_s": 275.2, "session": "55b4de1f-86f7-4649-aac5-664a0fe6d1cb", "step": "maker", "at": "2026-10-26T21:06:53+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-26-worktree-setup/03-maker.out"}]
stops: [{"at": "2026-10-26T15:39:23+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-26-worktree-setup budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "let's assume fewer loops, 500K and $4", "also": [], "answered_at": "2026-10-26T20:59:17+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~1.44M tokens and opus ~1.12M tokens on the narrow feature shape, from init-tries-guesses with diff-count as the floor; reopen risk is high.", "at": "2026-10-26T15:39:23+00:00"}, {"agent": "scenario", "status": "red", "summary": "Twelve tests for --base, config base, origin/HEAD default, setup with {worktree}, a setup-failure stop, teardown on close, xv check listing, and the commented defaults; ten fail on today's code, one passes as a guard, and the teardown test is red only because the block crashes slice new.", "at": "2026-10-26T21:02:16+00:00"}, {"agent": "maker", "status": "green", "summary": "slice new takes --base / worktrees.base / origin/HEAD, runs worktrees.setup (setup_failed stop on non-zero), close runs teardown, xv check lists both, defaults show the block", "at": "2026-10-26T21:06:53+00:00"}], "forecaster": {"at": "2026-10-26T15:39:23+00:00", "wrote": []}, "scenario": {"at": "2026-10-26T21:02:16+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "_head (test_worktree_setup.WorktreeSetupTest.test_with_neither_the_remotes_default_branch_not_head)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-26-worktree-setup/tests/test_worktree_setup.py\", line 60, in test_with_neither_the_remotes_default_branch_not_head\n    self.assertEqual(self.base_of(wt), pushed)\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: '9e1b99b076140c4e9d57a5622725848757432bfd' != '7c1abd0bb541442bbe8810774b482495c3da4560'\n- 9e1b99b076140c4e9d57a5622725848757432bfd\n+ 7c1abd0bb541442bbe8810774b482495c3da4560\n\n\n----------------------------------------------------------------------\nRan 12 tests in 1.178s\n\nFAILED (failures=9, errors=1)\n"}, "maker": {"at": "2026-10-26T21:06:53+00:00", "protected_changed": [], "suite": "green", "suite_output": "nal/xv-agents/.xv/worktrees/2026-10-26-worktree-setup/tests/test_worktree_setup.py:18: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-crb7eoa2/repo/.xv/config.yml' mode='r' encoding='utf-8'>\n  text = open(cfg).read().replace(\"worktrees: .xv/worktrees\\n\", block)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-26-worktree-setup/tests/test_worktree_setup.py:19: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-crb7eoa2/repo/.xv/config.yml' mode='w' encoding='utf-8'>\n  open(cfg, \"w\").write(text)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n----------------------------------------------------------------------\nRan 179 tests in 103.262s\n\nOK\n", "failing_step": "", "failing": [], "failing_history": [[]], "diff_lines": 195, "diff_history": [195], "wall": {"slice": "2026-10-26-worktree-setup", "baseline": "f58c9a32c0c9645d3716696308cb17cc5e98c6a5", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}}}
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
- 2026-10-26T20:59:17+00:00 Sean Kennedy: set budget
- 2026-10-26T20:59:17+00:00 Sean Kennedy: answered budget_not_set: let's assume fewer loops, 500K and $4
- 2026-10-26T21:02:16+00:00 scenario: red: Twelve tests for --base, config base, origin/HEAD default, setup with {worktree}, a setup-failure stop, teardown on close, xv check listing, and the commented defaults; ten fail on today's code, one passes as a guard, and the teardown test is red only because the block crashes slice new.
- 2026-10-26T21:06:53+00:00 maker: green: slice new takes --base / worktrees.base / origin/HEAD, runs worktrees.setup (setup_failed stop on non-zero), close runs teardown, xv check lists both, defaults show the block

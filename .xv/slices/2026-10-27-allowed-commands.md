---
id: 2026-10-27-allowed-commands
title: "Each agent's prompt says which commands it may run"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-allowed-commands
base: 99ae369ea03712578048ec10090c55dc5775b123
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 600000, "turns": null, "usd": 1.0, "basis": ["2026-10-27-package-imports", "2026-10-27-slice-tests", "2026-10-25-init-allow-list"], "note": "Guide has no turns column. Clean passes ran 53k to 283k tokens; init-allow-list reopened four times at 3.66M, so 600k covers one clean pass plus one send-back round, not the full reopen risk."}, {"harness": "claude", "model": "opus", "tokens": 250000, "turns": null, "usd": 0.8, "basis": ["2026-10-27-package-imports", "2026-10-27-init-rerun", "2026-10-27-slice-tests"], "note": "Guide has no turns column. Clean guardian passes ran 30k to 36k tokens; slice-tests ran 205k; 250k allows a second guardian review after a send-back."}], "wall_s": 900, "shape": "narrow", "breadth": "Every agent's prompt gains an allowed-commands section read from its --allowedTools in .xv/config.yml, touching one prompt builder and one config reader, plus a CHANGELOG line."}
budget: {"tokens": 350000, "usd": 2.5, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_allowed_commands_prompt.py"], "command": "cd tests && python3 -m unittest test_allowed_commands_prompt", "failure": "AssertionError: '`python3 -m unittest`' not found in '# The maker ...' (prompt has no allowed-commands section)", "watch_first_green": "Set a seat's --allowedTools in .xv/config.yml to a few Bash rules, run `xv prompt <seat> <id>`, and read the commands section: each rule listed as a plain command, plus the three cautions (no chained command, no extra flags such as `python3 -W ignore -m unittest`, no pipe to an unlisted program). Then remove --allowedTools from that seat's line, or use a non-Claude harness, and check the section is gone."}
wall_baseline: {"commit": "1177fed80275c90b8e9e609e6a15905e87b6b998", "count": 43, "digest": "51fc635741a91fd2", "file": ".xv/slices/2026-10-27-allowed-commands.wall.json"}
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3476, "cache_read": 25003, "cache_write": 11439, "tokens": 14919, "usd": 0.0043, "turns": 3, "wall_s": 20.9, "session": "4973fb5d-c5a2-4fb1-afc2-b9c4541f093b", "step": "forecaster", "at": "2026-10-27T17:27:44+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-allowed-commands/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 3677, "cache_read": 166993, "cache_write": 23851, "tokens": 27544, "usd": 0.1489, "turns": 9, "wall_s": 28.2, "session": "e7baade4-cd41-4c3a-9296-acb6530d8f5e", "step": "scenario", "at": "2026-10-27T17:46:57+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-allowed-commands/02-scenario.out"}]
stops: [{"at": "2026-10-27T17:27:44+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-allowed-commands budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "yes, all", "also": [], "answered_at": "2026-10-27T17:46:24+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet 600k tokens and claude/opus 250k tokens for allowed-commands; numbers include one send-back round, since the closest reopen history ran 3.6M.", "at": "2026-10-27T17:27:44+00:00"}, {"agent": "scenario", "status": "red", "summary": "xv prompt lacks an allowed-commands section: the Bash rules from the seat's --allowedTools are not listed and the chain/flag/pipe cautions are missing.", "at": "2026-10-27T17:46:57+00:00"}], "forecaster": {"at": "2026-10-27T17:27:44+00:00", "wrote": []}, "scenario": {"at": "2026-10-27T17:46:57+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "` skills (`mattpocock/skills`, MIT). The recorded move is XV\\'s own.\\n\\n---\\n\\n## This run\\n\\n- Repository checkout: `/tmp/xv-test-asail_id/repo/.xv/worktrees/s1`. Work only inside it.\\n- Slice record: `.xv/slices/s1.md`. Read it first. Do not edit it; your report block is how you write to it.\\n- Base commit: `ee4ea6182a13e560ead9a1314b3a1c60ace5a509`. The slice\\'s diff is `git diff ee4ea6182a13e560ead9a1314b3a1c60ace5a509..HEAD` plus any uncommitted changes.\\n- Whole suite: `python3 -m unittest discover -s tests -t .`.\\n- Test paths (the wall): tests/**.\\n- The `xv` command: `xv`.\\n- End your final message with the `xv-report` block your brief describes. Nothing after it.\\n'\n\n----------------------------------------------------------------------\nRan 6 tests in 0.544s\n\nFAILED (failures=7)\n"}}
---
# Each agent's prompt says which commands it may run

## Scenario

Each agent's prompt says which shell commands it may run. `xv prompt <agent> <id>` reads the Bash rules from that agent's own `--allowedTools` in `.xv/config.yml` (its line, or the default line) and lists them, for example `cd tests`, `python3 -m unittest`, `git diff`. It says to run each command in one of those forms, with no other command chained before it, no extra flags in front of a listed form (`python3 -W ignore -m unittest` is not `python3 -m unittest`), and no pipe to a program that is not listed, because any other form waits for an approval that a headless run never gets. An agent line with no `--allowedTools`, or a harness other than Claude Code, gets no such list. This changes what every agent is given; Sean decided it, solo, and it gets a CHANGELOG line. (seanpk/xv-agents#48)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T17:27:24+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T17:27:44+00:00 forecaster: done: Forecast claude/sonnet 600k tokens and claude/opus 250k tokens for allowed-commands; numbers include one send-back round, since the closest reopen history ran 3.6M.
- 2026-10-27T17:27:44+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-allowed-commands budget ... --by <name>`).
- 2026-10-27T17:46:24+00:00 Sean Kennedy: set budget
- 2026-10-27T17:46:24+00:00 Sean Kennedy: answered budget_not_set: yes, all
- 2026-10-27T17:46:57+00:00 scenario: red: xv prompt lacks an allowed-commands section: the Bash rules from the seat's --allowedTools are not listed and the chain/flag/pipe cautions are missing.

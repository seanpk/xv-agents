---
id: 2026-10-27-allowed-commands
title: "Each agent's prompt says which commands it may run"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-allowed-commands
base: 99ae369ea03712578048ec10090c55dc5775b123
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 600000, "turns": null, "usd": 1.0, "basis": ["2026-10-27-package-imports", "2026-10-27-slice-tests", "2026-10-25-init-allow-list"], "note": "Guide has no turns column. Clean passes ran 53k to 283k tokens; init-allow-list reopened four times at 3.66M, so 600k covers one clean pass plus one send-back round, not the full reopen risk."}, {"harness": "claude", "model": "opus", "tokens": 250000, "turns": null, "usd": 0.8, "basis": ["2026-10-27-package-imports", "2026-10-27-init-rerun", "2026-10-27-slice-tests"], "note": "Guide has no turns column. Clean guardian passes ran 30k to 36k tokens; slice-tests ran 205k; 250k allows a second guardian review after a send-back."}], "wall_s": 900, "shape": "narrow", "breadth": "Every agent's prompt gains an allowed-commands section read from its --allowedTools in .xv/config.yml, touching one prompt builder and one config reader, plus a CHANGELOG line."}
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3476, "cache_read": 25003, "cache_write": 11439, "tokens": 14919, "usd": 0.0043, "turns": 3, "wall_s": 20.9, "session": "4973fb5d-c5a2-4fb1-afc2-b9c4541f093b", "step": "forecaster", "at": "2026-10-27T17:27:44+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-allowed-commands/01-forecaster.out"}]
stops: [{"at": "2026-10-27T17:27:44+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-allowed-commands budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet 600k tokens and claude/opus 250k tokens for allowed-commands; numbers include one send-back round, since the closest reopen history ran 3.6M.", "at": "2026-10-27T17:27:44+00:00"}], "forecaster": {"at": "2026-10-27T17:27:44+00:00", "wrote": []}}
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

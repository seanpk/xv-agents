---
id: 2026-10-25-init-allow-list
title: xv init writes a starter allow list
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-25
branch: xv/2026-10-25-init-allow-list
base: f452d430f44f6c01e611f705f5b709b80231291b
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 696815, "turns": null, "usd": 0.48, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"], "note": "mean of the two rows; the guide has no turns column"}, {"harness": "claude", "model": "opus", "tokens": 447861, "turns": null, "usd": 0.59, "basis": ["2026-10-24-readme-drift", "2026-10-24-promote-draft"], "note": "guardian only; mean of the two rows; the guide has no turns column"}], "wall_s": 300, "shape": "narrow", "breadth": "The init writer and the config template gain an allow list on Claude Code agent lines; expect moved init tests under tests/** and a guardian read of a small diff, so opus spend stays near the prior range."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 2496, "cache_read": 25028, "cache_write": 5623, "tokens": 33151, "usd": 0.0026, "turns": 3, "wall_s": 15.8, "session": "af6e8123-9d43-4c91-8359-cfea31081f9f", "step": "forecaster", "at": "2026-10-25T04:26:13+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-25-init-allow-list/01-forecaster.out"}]
stops: [{"at": "2026-10-25T04:26:13+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-init-allow-list budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet at about 697k tokens and claude/opus at about 448k tokens, both from the two prior slices; shape narrow.", "at": "2026-10-25T04:26:13+00:00"}], "forecaster": {"at": "2026-10-25T04:26:13+00:00", "wrote": []}}
---
# xv init writes a starter allow list

## Scenario

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`: read-only shell and git commands, `git rm`, `git mv`, `xv record move`, and the test command it detected. The forecaster and the guardian get only the read-only part, plus the test command for the guardian. A headless agent with the starter config can run the test command as `xv prompt` gives it. (seanpk/xv-agents#16)

## May ignore

harnesses other than Claude Code; asking for lint and type commands

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T04:25:51+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T04:26:13+00:00 forecaster: done: Forecast claude/sonnet at about 697k tokens and claude/opus at about 448k tokens, both from the two prior slices; shape narrow.
- 2026-10-25T04:26:13+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-25-init-allow-list budget ... --by <name>`).

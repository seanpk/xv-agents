---
id: 2026-10-24-promote-draft
title: "xv promote draft: whole-word titles, any stack, one date, attribution"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-promote-draft
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect changes confined to the promote draft path: title cut at a word boundary, default Applies to: any, one date in the draft file name, and the attribution line at the end of the body. post and tally are out of scope."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 942, "cache_read": 23314, "cache_write": 6196, "tokens": 30456, "usd": 0.0019, "turns": 3, "wall_s": 5.5, "session": "72b71b0d-7437-49c7-a412-46cd7670ac28", "step": "forecaster", "at": "2026-10-25T03:27:07+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-promote-draft/01-forecaster.out"}]
stops: [{"at": "2026-10-25T03:27:07+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-promote-draft budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No guide history for claude/sonnet or claude/opus; numbers left null, shape forecast narrow.", "at": "2026-10-25T03:27:07+00:00"}], "forecaster": {"at": "2026-10-25T03:27:07+00:00", "wrote": []}}
---
# xv promote draft: whole-word titles, any stack, one date, attribution

## Scenario

`xv promote draft` gives a title cut at a word boundary, "Applies to: any" when no `--applies-to` is passed, a draft file name with one date, and a body that ends with the assistant's attribution line. (seanpk/xv-agents#13)

## May ignore

the post and tally commands

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:07+00:00 forecaster: done: No guide history for claude/sonnet or claude/opus; numbers left null, shape forecast narrow.
- 2026-10-25T03:27:07+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-promote-draft budget ... --by <name>`).

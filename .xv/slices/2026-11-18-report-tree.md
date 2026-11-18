---
id: 2026-11-18-report-tree
title: "What an agent reports is checked against the tree (#183)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-17
branch: xv/2026-11-18-report-tree
base: 5c2600c69d4d50853dcd288bd6278c48bd808657
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 2.3, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend", "2026-11-09-retro-fixes", "2026-11-09-defects-stops"]}, {"harness": "claude", "model": "opus", "tokens": 220000, "turns": null, "usd": 2.5, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend", "2026-11-09-retro-fixes", "2026-11-09-defects-stops"]}, {"harness": "claude", "model": "haiku", "tokens": 45000, "turns": null, "usd": 0.01, "basis": ["2026-11-16-red-lands", "2026-11-09-defects-tools", "2026-11-09-errored-spend"]}], "wall_s": 2000, "rounds": 2, "rounds_reason": "The removal clause and the reader fallback are points the guardian has sent back before on narrow defects (red-lands ran three send-backs, defects-tools two guardian passes), so one send-back is likely rather than certain.", "shape_breadth": "narrow", "shape_note": "Touches the post-step and post-move checks in the step runner and the harness report reader, plus tests and one CHANGELOG line; this turns wide only if the reader change reaches more than the claude harness."}
budget: {"tokens": 615000, "usd": 4.81, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5848, "cache_read": 63652, "cache_write": 41924, "tokens": 47778, "usd": 0.0119, "turns": 4, "wall_s": 26.1, "session": "d17f01d8-4250-45d5-ad04-77073b7daf2e", "step": "forecaster", "at": "2026-11-18T03:55:18+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-report-tree/01-forecaster.out"}]
stops: [{"at": "2026-11-18T03:55:18+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-report-tree budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "go, accept the forecast - stop only for me if it is wide", "also": [], "answered_at": "2026-11-18T03:55:31+00:00", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 615000, "usd": 4.81}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect with a likely send-back: sonnet ~350k tokens, opus ~220k, forecaster haiku ~45k, wall ~2000 s across keys.", "at": "2026-11-18T03:55:18+00:00"}], "forecaster": {"at": "2026-11-18T03:55:18+00:00", "wrote": []}}
---
# What an agent reports is checked against the tree (#183)

## Scenario

What an agent reports is checked against the tree.

1. After the cleaner step, each accepted `slice_only` test still in its file stops the step with `removal_not_made` for the person who set the work going, naming the file and the test, unless the cleaner's report says it kept that test and why. A removal that was made passes.
2. After any step, a move on the record that says a test or a file was removed (`--slice-only` or `--deleted`) while that test or file is still there stops the step with `removal_not_made` for the person who set the work going, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last `xv-report` block of the whole run, through the harness's own reader, before it stops with `no_report`. The core still names no agent. A run with no report block anywhere still stops with `no_report`.
4. A line in CHANGELOG.md.

## May ignore

- old slice records
- a harness whose reader cannot see earlier messages: it stops with no_report, as now

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T03:54:46+00:00 watch: slice opened by Sean Kennedy
- 2026-11-18T03:55:18+00:00 forecaster: done: Narrow defect with a likely send-back: sonnet ~350k tokens, opus ~220k, forecaster haiku ~45k, wall ~2000 s across keys.
- 2026-11-18T03:55:18+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-report-tree budget ... --by <name>`).
- 2026-11-18T03:55:31+00:00 Sean Kennedy: set budget
- 2026-11-18T03:55:31+00:00 Sean Kennedy: answered budget_not_set: go, accept the forecast - stop only for me if it is wide
- 2026-11-18T03:55:31+00:00 watch: scribe: wrote new_info, cause for budget_not_set as the scribe of Sean Kennedy

---
id: 2026-10-30-scenario-miss
title: A slice that misses its own scenario goes back without a stop
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-scenario-miss
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 2.7, "basis": ["2026-10-30-stop-words", "2026-10-30-by-name", "2026-10-30-test-marks"], "note": "turns not in guide; test-marks ran 869k with nine scenario runs, so a second reopen would roughly double this"}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.4, "basis": ["2026-10-30-stop-words", "2026-10-30-by-name", "2026-10-30-test-marks"], "note": "turns not in guide; test-marks ran 478k and $6.12 with six guardian passes, so a reopen here is the largest usd risk"}], "wall_s": 2500, "shape": "narrow", "breadth": "Touches the guardian and watch briefs, packet template, scripts/run.py message, one check, standing orders and CHANGELOG; the code path it changes is narrow."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3166, "cache_read": 25533, "cache_write": 21043, "tokens": 24213, "usd": 0.006, "turns": 3, "wall_s": 19.5, "session": "9c4ef31f-94a8-47f4-8a76-6b6776e6e436", "step": "forecaster", "at": "2026-10-30T04:37:20+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-scenario-miss/01-forecaster.out"}]
stops: [{"at": "2026-10-30T04:37:20+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-scenario-miss budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from the last three claude/sonnet and claude/opus rows: about 500k sonnet and 300k opus tokens for one pass plus one send-back; reopen risk is the main uncertainty.", "at": "2026-10-30T04:37:20+00:00"}], "forecaster": {"at": "2026-10-30T04:37:20+00:00", "wrote": []}}
---
# A slice that misses its own scenario goes back without a stop

## Scenario

A slice that misses its own scenario, or a decision that binds, goes back without a stop (#96).

1. The guardian's packet has `scenario_miss: yes|no` in its front matter, and a section that lists each miss: the scenario line it misses (an amendment counts as part of the scenario), or the binding decision in `.xv/picture.md` it breaks, and the evidence (a test, a run, or a diff hunk). A finding that names no scenario line and no binding decision is not a miss; it stays in the packet for the person, as now.
2. After the guardian, when `scenario_miss` is `yes` and no shape or pitch stop fires, the slice goes back without a stop: to the maker, or to the scenario agent when the red does not cover the missed line. `accept_moves` and `ready_to_merge` do not fire on that pass. Moved tests and wall recommendations are put to the person when the slice comes back with no miss.
3. After the scenario step, each numbered point of the scenario and of each amendment must appear in the scenario report's `covers` or `not_covered`. A point in neither sends the slice back to the scenario agent without a stop. A point in `not_covered` still stops for the person, as now.
4. Each send-back is recorded in the slice record as the watch's, with the misses. The next agent gets them through `xv prompt`, as it gets `settled`. `xv decisions` counts them.
5. It still stops for the person who set the work going when the budget is spent, green or not; when the same miss comes back on the next pass, as a stall (#86); or when meeting the miss would change the scenario, which goes through `xv slice amend` and is theirs.
6. The packet template (`skills/guardian/packet.md`) shows `shape_change` as `yes`, `no` or `accepted` with `accepted_by`, and `scenario_miss`.
7. The scenario-step `unrecorded_move` question names "old test files that existed at the base", not "red files", and so does the matching message in `scripts/run.py` (#102).

This changes standing orders, a check, and the guardian's and the watch's briefs, so `CHANGELOG.md` gets a line.

## May ignore

None.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T04:37:00+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T04:37:20+00:00 forecaster: done: Forecast from the last three claude/sonnet and claude/opus rows: about 500k sonnet and 300k opus tokens for one pass plus one send-back; reopen risk is the main uncertainty.
- 2026-10-30T04:37:20+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-scenario-miss budget ... --by <name>`).

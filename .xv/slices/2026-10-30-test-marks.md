---
id: 2026-10-30-test-marks
title: A person sees which tests stay on the wall and which leave it
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-test-marks
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.7, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 190000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-settled-forward"]}], "wall_s": 1650, "shape": "narrow", "breadth": "Adds one conditional stop after scenario (fires only when slice-only marks exist) and a fifth guardian check; touches the watch stop table, README, scenario brief, packet template, guardian SKILL and CHANGELOG, not the pipeline order. Reopen risk from the new accept_moves order is inside the basis means."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3352, "cache_read": 25528, "cache_write": 17858, "tokens": 21214, "usd": 0.0055, "turns": 3, "wall_s": 16.4, "session": "a8d49f10-ea19-4584-8b72-b6ba6798e7bd", "step": "forecaster", "at": "2026-10-30T01:07:36+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/01-forecaster.out"}]
stops: [{"at": "2026-10-30T01:07:36+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-test-marks budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~300k tokens and opus ~190k tokens for the slice, from the three closest feature rows; narrow shape with a reopen risk from the new accept_moves order.", "at": "2026-10-30T01:07:36+00:00"}], "forecaster": {"at": "2026-10-30T01:07:36+00:00", "wrote": []}}
---
# A person sees which tests stay on the wall and which leave it

## Scenario

A person sees which tests stay on the wall and which leave it (#87, #89).

1. The person accepts the slice-only marks (#89). After the scenario step, a new order seated for the person who set the work going fires only when the scenario report marks slice-only tests. It lists each marked test with the scenario agent's reason. The person accepts the marks, or unmarks a test so it joins the wall. The answer is recorded like any other stop. A slice with no marks adds no stop. The watch's stop table and the README's list the new order.
2. The guardian says which new tests should join the wall or leave it (#87). `skills/guardian/SKILL.md` has a fifth check, for three kinds of recommendation: a test marked slice-only should stay; a new test that was not marked should not join the wall; a test that was on the wall before the slice should be removed. The packet has a section for them. They reach the person who set the work going in `accept_moves`, not two people, and the record keeps which ones the person accepted. The places that say the guardian has four checks say five.

This adds a standing order and changes a brief and the packet template, so `CHANGELOG.md` gets a line.

## May ignore

Rewording the site. Moving slice-only tests out of the cleaner.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T01:07:13+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T01:07:36+00:00 forecaster: done: Forecast sonnet ~300k tokens and opus ~190k tokens for the slice, from the three closest feature rows; narrow shape with a reopen risk from the new accept_moves order.
- 2026-10-30T01:07:36+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-test-marks budget ... --by <name>`).

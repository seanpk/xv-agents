---
id: 2026-10-30-scenario-miss
title: A slice that misses its own scenario goes back without a stop
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-scenario-miss
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
next: forecaster
forecast: null
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
spend: []
stops: []
decisions: []
prototypes: []
overrides: []
checks: {}
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

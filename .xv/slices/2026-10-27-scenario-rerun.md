---
id: 2026-10-27-scenario-rerun
title: A scenario run after the maker keeps the red list and checks the right code
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-scenario-rerun
base: 99ae369ea03712578048ec10090c55dc5775b123
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 150000, "turns": null, "usd": 0.7, "basis": ["2026-10-27-init-rerun", "2026-10-27-package-imports"], "note": "Guide has no turns column. Tokens and usd extrapolated from two single-pass rows (41k/$0.23, 53k/$0.29) scaled for three separate changes; not a direct row."}, {"harness": "claude", "model": "opus", "tokens": 75000, "turns": null, "usd": 0.5, "basis": ["2026-10-27-init-rerun", "2026-10-27-package-imports"], "note": "Guide has no turns column. Single-pass guardian rows were 30k/$0.35 and 36k/$0.41; scaled up for a larger diff. Extrapolated, not a direct row."}], "wall_s": 600, "shape": "narrow", "breadth": "Three small edits: record.py red merge after the maker, orders.py red_fails against the wall baseline commit, and the --slice-only gate on the move path, plus tests under tests/**."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3746, "cache_read": 25009, "cache_write": 11617, "tokens": 15367, "usd": 0.0044, "turns": 3, "wall_s": 21.6, "session": "22ead752-6557-470b-859a-cfdbaccf7009", "step": "forecaster", "at": "2026-10-27T16:46:00+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-scenario-rerun/01-forecaster.out"}]
stops: [{"at": "2026-10-27T16:46:00+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-scenario-rerun budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from claude/sonnet and claude/opus rows of clean single-pass defect slices; reopen risk not priced in the central numbers.", "at": "2026-10-27T16:46:00+00:00"}], "forecaster": {"at": "2026-10-27T16:46:00+00:00", "wrote": []}}
---
# A scenario run after the maker keeps the red list and checks the right code

## Scenario

A scenario run after the maker, sent to fix a test, does not cost the person needless stops. (1) Once the slice has been through the maker, a scenario report's `red` is added to the record's red: its files join `red.files` and the rest stay. Today `apply_report` replaces `red` with the report's (`scripts/record.py`, `if agent == "scenario" and report.get("red")`), so a run that touched one of twelve red files leaves only that one. Before the maker, a report still replaces `red`, as today. (2) Once the slice has been through the maker, the check that the scenario fails on today's code (`red_fails`, read by `scenario_not_red` in `scripts/orders.py`) runs the red command against the slice's code from before the maker's first change (the wall baseline commit), not HEAD, where the maker's fix already makes it pass. A new red that fails there and passes at HEAD is fine; one that passes there still fires `scenario_not_red`. (3) A move with `--slice-only` must name a test on the record's `slice_only` list. Otherwise it is a plain move, and `accept_moves` fires for it, as for any move. (seanpk/xv-agents#44; (3) is from the guardian on #17.)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T16:45:38+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T16:46:00+00:00 forecaster: done: Forecast from claude/sonnet and claude/opus rows of clean single-pass defect slices; reopen risk not priced in the central numbers.
- 2026-10-27T16:46:00+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-scenario-rerun budget ... --by <name>`).

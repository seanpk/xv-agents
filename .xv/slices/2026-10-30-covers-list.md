---
id: 2026-10-30-covers-list
title: A covers item may name more than one test
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-covers-list
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 490000, "turns": null, "usd": 2.9, "basis": ["2026-10-30-by-name", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"], "note": "Guide has no turns column. Actual tokens 489k, 506k, 496k; usd 2.58, 3.00, 2.92."}, {"harness": "claude", "model": "opus", "tokens": 290000, "turns": null, "usd": 3.5, "basis": ["2026-10-30-by-name", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"], "note": "Guide has no turns column. Actual tokens 295k, 280k, 275k; usd 3.58, 3.42, 3.40."}], "wall_s": 2000, "shape": "narrow", "breadth": "Scenario brief (the report section and its parsing) and one check that matches red names, plus a CHANGELOG line; expect the reopen pattern of by-name and red-covers-scenario, with a stop on the brief's wording or the CHANGELOG line the most likely cause of a second round."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3177, "cache_read": 23874, "cache_write": 22103, "tokens": 25284, "usd": 0.0062, "turns": 3, "wall_s": 19.1, "session": "90010a1b-7fbb-4bd8-b74d-92d9c2b155d4", "step": "forecaster", "at": "2026-10-30T05:57:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-covers-list/01-forecaster.out"}]
stops: [{"at": "2026-10-30T05:57:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-covers-list budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~490k tokens / $2.9 and opus ~290k tokens / $3.5 for a narrow covers-list feature, ~2000 s wall; basis is the three nearest covers and scenario-brief rows, which all reopened.", "at": "2026-10-30T05:57:45+00:00"}], "forecaster": {"at": "2026-10-30T05:57:45+00:00", "wrote": []}}
---
# A covers item may name more than one test

## Scenario

A covers item may name more than one test (#92).

1. In the scenario report, a `covers` item's `test` may be one test name or a list of names. Each name must match a whole test name in a red file.
2. A `test` string that joins names with `,` or `;` is read as that list.
3. A name written as `Class.test_name` or `file::test_name` matches on its last part.
4. The scenario brief's report example shows the list form.

This changes the scenario brief and a check, so `CHANGELOG.md` gets a line.

## May ignore

None.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T05:57:26+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T05:57:45+00:00 forecaster: done: Forecast sonnet ~490k tokens / $2.9 and opus ~290k tokens / $3.5 for a narrow covers-list feature, ~2000 s wall; basis is the three nearest covers and scenario-brief rows, which all reopened.
- 2026-10-30T05:57:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-covers-list budget ... --by <name>`).

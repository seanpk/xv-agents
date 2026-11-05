---
id: 2026-11-04-refactor-kind
title: "A slice kind for refactors, and test moves a person expects: #15"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-refactor-kind
base: 66570aa785961973ad109e9db00dfc167a823e9b
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 3.2, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-11-04-scenario-catches", "2026-10-27-slice-tests"], "note": "Guide has no turns column; sonnet covers scenario, maker, and cleaner. Each basis row reopened at least once, so one reopen is priced in the middle of the range; tokens span 283k to 674k across the basis."}, {"harness": "claude", "model": "opus", "tokens": 340000, "turns": null, "usd": 4.1, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-11-04-scenario-catches", "2026-10-27-slice-tests"], "note": "Guide has no turns column; opus is the guardian only. Tokens span 205k to 392k across the basis, and usd runs about $12 per million tokens, so output-heavy guardian passes weigh more."}], "wall_s": 4500, "shape": "wide", "breadth": "Touches slice new flags, the packet, a new moved-test comparison script, and new stops in scripts/orders.py; the main gap is reopen risk from new stops, which pushed every basis row over forecast."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4290, "cache_read": 26138, "cache_write": 26265, "tokens": 30559, "usd": 0.0077, "turns": 3, "wall_s": 22.6, "session": "5acfa561-d381-4d93-8b9f-3914bb06eeb2", "step": "forecaster", "at": "2026-11-05T03:13:51+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-refactor-kind/01-forecaster.out"}]
stops: [{"at": "2026-11-05T03:13:51+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-refactor-kind budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~500k tokens and claude/opus ~340k tokens for a wide slice that reopened in all four basis rows; turns have no history column.", "at": "2026-11-05T03:13:51+00:00"}], "forecaster": {"at": "2026-11-05T03:13:51+00:00", "wrote": []}}
---
# A slice kind for refactors, and test moves a person expects: #15

## Scenario

# A slice kind for refactors, and test moves a person expects: #15

When this is done:

1. `xv slice new --kind refactor` opens a refactor slice. Its scenario says that users see no change, and it names what to restructure.
2. The scenario step writes no new red. It checks that the suite is green at the start, and it records that as the slice's oracle.
3. The maker may rename and restructure what the scenario names. The "no refactor, no rename" line in its brief does not apply to those parts.
4. A latent bug found along the way is fixed only through `xv slice amend`.
5. `xv slice new --expect-moves <kinds>` names the kinds of test change the person expects: `imports`, `renames`, or both.
6. After each step, a script compares each moved test file before and after. The agent does not decide whether a move is expected.
7. Expected moves are recorded and listed on one line in the packet, with no `accept_moves` stop for them. Any other move still stops for the person.
8. `renames`: a test file moves to a new path (for example `test_foo.py` to `test_bar.py`). Its content changes only in the names the slice renames, in import lines, and in whitespace. Every assertion is otherwise unchanged. `imports`: the same path, and only import or require lines and whitespace change. These two are the only kinds for now.
9. The person gives the names a slice renames when it opens, with `xv slice new --rename Foo=Bar`, one flag per pair. The script reads those pairs to check a `renames` move.
10. Each new stop is decided in `scripts/orders.py`.

## May ignore

expected-move kinds other than imports and renames; #114, the retro seeing rework, left for slice H; old slice records, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T03:13:28+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T03:13:51+00:00 forecaster: done: Forecast claude/sonnet ~500k tokens and claude/opus ~340k tokens for a wide slice that reopened in all four basis rows; turns have no history column.
- 2026-11-05T03:13:51+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-refactor-kind budget ... --by <name>`).

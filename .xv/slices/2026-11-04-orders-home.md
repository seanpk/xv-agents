---
id: 2026-11-04-orders-home
title: "Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-orders-home
base: c7b8bbff58fc46160ba83d08d0e899d7beffaaf2
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 674000, "turns": null, "usd": 3.87, "basis": ["2026-10-29-stop-decisions", "2026-10-30-test-marks", "2026-10-27-prototype-budgets"], "note": "Median of the three basis rows (actuals 395k to 869k tokens); the guide has no turn column, so turns are null."}, {"harness": "claude", "model": "opus", "tokens": 392000, "turns": null, "usd": 4.89, "basis": ["2026-10-29-stop-decisions", "2026-10-30-test-marks", "2026-10-27-prototype-budgets"], "note": "Median of the three basis rows (actuals 230k to 478k tokens); the guide has no turn column, so turns are null. Guardian passes carry heavy output, so usd runs high relative to tokens."}], "wall_s": 2864, "shape": "wide", "breadth": "Moves the stop rules out of run.py and record.py into orders.py, rewires xv step, xv run, xv record packet and the session path onto one applier, and touches the shared allowed-values definition, the docs and the packet-field test; the stop changes, not the code size, will set the spend, and the reopen history in the basis rows is the main risk."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3792, "cache_read": 23903, "cache_write": 25594, "tokens": 29390, "usd": 0.0073, "turns": 3, "wall_s": 19.8, "session": "4175a274-b9f8-4911-9058-2141a441bf90", "step": "forecaster", "at": "2026-11-04T16:56:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-orders-home/01-forecaster.out"}]
stops: [{"at": "2026-11-04T16:56:42+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-orders-home budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "claude/sonnet ~674k tokens and $3.87; claude/opus ~392k tokens and $4.89; shape wide; wall ~2864 s.", "at": "2026-11-04T16:56:42+00:00"}], "forecaster": {"at": "2026-11-04T16:56:42+00:00", "wrote": []}}
---
# Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109

## Scenario

# Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109

When this is done:

1. Whether a scenario miss is a repeat (a send-back or a stall) is decided in `scripts/orders.py`, from the record alone. One rule says which send-backs count. `scripts/run.py` and `scripts/record.py` no longer work this out.
2. Every path (`xv step`, `xv run`, `xv record packet`, the session path) writes its facts into the record's `checks` the same way. `scripts/orders.py` makes every decision, including where `next` goes and any send-back. One small function applies what `orders` returns. A test runs each path on the same record and expects the same verdict.
3. One shared definition gives the allowed values for `shape_change` and `pitch_contradiction`. One shared helper matches a test name inside a string. The wall-flag block is split out of `cmd_answer`.
4. A shape the person accepted does not stop again as `shape_wider_than_forecast`. The `accept_moves` question counts moves, not record entries. The docs say `yes`, `no` or `accepted` for `shape_change`. (#103)
5. `xv step` marks the pre-step `budget_spent` stop when it raises it. `prototype_budget_spent` counts as started work, so it needs `--settled`. (#84)
6. A scenario re-run keeps a slice-only mark the person accepted. `slice_only_marks` does not ask again about a mark already accepted. (#99, items 1-2)
7. A test fails when a packet field's allowed values in the code are missing from `skills/guardian/packet.md`, the README, or the `docs/` tables that name the field. (#109)
8. A slice-only move keeps its flag. One move is recorded once, even when more than one step records it. (#99, item 3)
9. `docs/slice-record.md` gives the stop shape with `accepted_wall`, `refused_wall` and `settled`. It says a decision is also written for `ready_to_merge`. New decisions write `who` as a list. Readers accept a string in old records. (#99, item 4)

## May ignore

The new stops for #20, #15, #113 and #117: this slice gives them a home in orders.py and does not add them; old slice records under .xv/slices/, which keep their shape; new wording in the briefs, unless a moved rule makes a brief untrue.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T16:56:16+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T16:56:42+00:00 forecaster: done: claude/sonnet ~674k tokens and $3.87; claude/opus ~392k tokens and $4.89; shape wide; wall ~2864 s.
- 2026-11-04T16:56:42+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-orders-home budget ... --by <name>`).

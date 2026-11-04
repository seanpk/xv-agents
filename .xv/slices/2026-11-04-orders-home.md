---
id: 2026-11-04-orders-home
title: "Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-orders-home
base: c7b8bbff58fc46160ba83d08d0e899d7beffaaf2
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

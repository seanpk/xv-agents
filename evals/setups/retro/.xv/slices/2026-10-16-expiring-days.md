---
id: 2026-10-16-expiring-days
title: Ask for any number of days
kind: feature
status: closed
set_by: pat
created: 2026-10-16
branch: xv/2026-10-16-expiring-days
base: "0000000"
next: none
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "basis": ["2026-10-14-expiring"]}], "shape": "none"}
budget: {"usd": 1.5, "set_by": "pat"}
red: null
wall_baseline: null
moved_tests: []
suite: green
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"step": "maker", "harness": "claude", "model": "sonnet", "tokens": 310000, "usd": 1.1, "turns": 40, "wall_s": 420}]
stops: [{"at": "2026-10-16T09:40:00+00:00", "step": "maker", "order": "unrecorded_move", "seat": "originator", "question": "Test files changed with no record after the maker: tests/test_api.py.", "answered_by": ["pat"], "answer": "reverted; the maker deleted test_expiring_within_three_days instead of fixing the default"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "cleaner", "status": "done", "summary": "one rule", "applied": [{"rule": ".xv/standards.md: Name a date for what it is: `expires_on`, `today`, `last`; never `d`, `dt`, or `x`", "where": "pantry/api.py:39"}]}]}
---
# Ask for any number of days

## Scenario

The household asks what runs out within N days, for any N from 0 to 30.

## May ignore

Nothing stated.

## Recording

None.

## Log

- 2026-10-16T09:00:00+00:00 watch: slice opened by pat
- 2026-10-16T09:40:00+00:00 watch: stop (unrecorded_move) for originator: Test files changed with no record after the maker: tests/test_api.py
- 2026-10-16T10:10:00+00:00 pat: answered unrecorded_move: reverted; the maker deleted test_expiring_within_three_days instead of fixing the default
- 2026-10-16T10:40:00+00:00 cleaner: done: one rule applied

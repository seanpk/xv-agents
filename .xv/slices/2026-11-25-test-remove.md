---
id: 2026-11-25-test-remove
title: "Taking the inspector's advice to remove a test removes it: --test-remove (#202)"
kind: defect
status: stopped
originator: Sean Kennedy
created: 2026-11-25
branch: xv/2026-11-25-test-remove
base: 911f113209115d8a4e586a9f3d6efd095926baef
next: forecaster
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 280000, "turns": null, "usd": 1.7, "basis": ["2026-11-25-failed-step", "2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-24-settled-outcome"]}, {"harness": "claude", "model": "opus", "tokens": 140000, "turns": null, "usd": 1.7, "basis": ["2026-11-25-failed-step", "2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-24-settled-outcome"]}, {"harness": "claude", "model": "haiku", "tokens": 60000, "turns": null, "usd": 0.01, "basis": ["2026-11-25-failed-step", "2026-11-25-build-moves", "2026-11-24-cleaner-commit", "2026-11-24-settled-outcome"]}], "wall_s": 900, "rounds": 2, "rounds_reason": "The answer path is new and refuses or removes tests, and the last two defects that touched it (settled-outcome, failed-step) each reopened through the inspector, so a send-back is more likely than not.", "shape_breadth": "narrow", "shape_note": "Expect one new flag on record answer that reuses the directed-edit removal check, the two deprecated flags delegating to it with warnings, and text edits in the README, watch brief and CHANGELOG."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 5670, "cache_read": 63134, "cache_write": 50131, "tokens": 55807, "usd": 0.0135, "turns": 4, "wall_s": 28.7, "session": "412417ac-63f3-4d47-aa9d-12a14b441c7b", "step": "forecaster", "at": "2026-11-26T02:25:45+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-25-test-remove/01-forecaster.out"}]
stops: [{"at": "2026-11-26T02:25:45+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-test-remove budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null, "fired_questions": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast ~280k sonnet / ~140k opus tokens over two rounds, from the last four closed narrow defects; the engineer sets the budget.", "at": "2026-11-26T02:25:45+00:00"}], "forecaster": {"at": "2026-11-26T02:25:45+00:00", "wrote": [], "removal_not_made": []}}
step_start: {"agent": "forecaster", "commit": "8dcb0df9b184536065bdfbbefbb225254754ddfd", "ended": true}
---
# Taking the inspector's advice to remove a test removes it: --test-remove (#202)

## Scenario

At `moves_to_accept`, `xv record answer --test-remove <test>` takes the inspector's advice for that test and removes it from its file: the whole test with its decorators, with the same check as a `test-remove` directed edit (1).
The answer commits the removals and runs the suite, as an answer with a directed edit does (2).
A test that is already gone from its file is skipped. A test that is in its file but cannot be removed cleanly makes the answer refused, and nothing is removed or recorded (3).
A test the answer does not name stays in its file (4).
`--accept-wall` and `--refuse-wall` still work: `--accept-wall <test>` does what `--test-remove <test>` does, and `--refuse-wall <test>` does what `xv record unmark <test>` does. Each prints a warning that names the new way and #216. The watch brief and the README name only the new way (5).
Each test that a slice record lists as accepted for removal, and that is still in the file it was accepted from, is removed (6).
There is a CHANGELOG line (7).

## May ignore

a wall recommendation at any stop other than moves_to_accept

## Recording

None. A feature starts from words.

## Log
- 2026-11-26T02:25:17+00:00 watch: slice opened by Sean Kennedy
- 2026-11-26T02:25:45+00:00 forecaster: done: Forecast ~280k sonnet / ~140k opus tokens over two rounds, from the last four closed narrow defects; the engineer sets the budget.
- 2026-11-26T02:25:45+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-25-test-remove budget ... --by <name>`).

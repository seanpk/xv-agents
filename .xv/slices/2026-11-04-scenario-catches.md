---
id: 2026-11-04-scenario-catches
title: "The scenario agent catches more before the maker starts: #119, with #110 and #111"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-scenario-catches
base: a6e023bd0ffeed4f6ce45990c668742a8f758419
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 343000, "turns": null, "usd": 2.0, "basis": ["2026-10-30-covers-list", "2026-10-29-red-covers-scenario", "2026-11-04-proto-start"], "note": "guide has no turns column"}, {"harness": "claude", "model": "opus", "tokens": 193000, "turns": null, "usd": 2.3, "basis": ["2026-10-30-covers-list", "2026-10-29-red-covers-scenario", "2026-11-04-proto-start"], "note": "guide has no turns column"}], "wall_s": 2300, "shape": "narrow", "breadth": "Expect edits to the scenario brief and its report, the maker's may-not handling, the watch's amendment drafting, covers-item parsing, and tests plus one CHANGELOG line; the cleaner is not expected to move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3378, "cache_read": 26130, "cache_write": 25481, "tokens": 28863, "usd": 0.007, "turns": 3, "wall_s": 17.1, "session": "424e0ade-de7b-4324-a661-ccf9a30a4cc5", "step": "forecaster", "at": "2026-11-04T20:44:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-scenario-catches/01-forecaster.out"}]
stops: [{"at": "2026-11-04T20:44:23+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-scenario-catches budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from claude/sonnet and claude/opus feature rows on scenario-agent slices; shape narrow, reopen risk carried in the basis.", "at": "2026-11-04T20:44:23+00:00"}], "forecaster": {"at": "2026-11-04T20:44:23+00:00", "wrote": []}}
---
# The scenario agent catches more before the maker starts: #119, with #110 and #111

## Scenario

# The scenario agent catches more before the maker starts: #119, with #110 and #111

When this is done:

1. When the scenario agent writes a test that only checks a one-time wording change (a README line, a version pin, a reworded doc item), it marks the test slice-only. (#119.1)
2. a. The scenario agent's report names each old test the red will force to change: the file, the test, and why. The maker may change a named test without stopping, and it records the move. A test that is not named still follows rule 3.
   b. The scenario agent's report names each file on the maker's may-not list that the red needs changed (for example, `.xv/picture.md`). The maker may change those files, and no other file on that list. The guardian lists each of those changes in the packet. (#119.2)
3. When a scenario adds a check that accepts a value (a flag, a field, a report key), the scenario agent writes a red case for each way the input can be wrong: missing, empty, wrong type, a value not on the list. When a read-only agent writes the value about itself, it adds a case where that agent claims what only a person may give. It tests each case or names it in `not_covered`. (#119.3, #110)
4. Each amendment the watch drafts names four things: the exact name a test will look for; where it is checked; when it applies, and the case it does not cover; and any may-not line or binding decision it loosens. (#111)
5. A `covers` item may name a point by its number. `"1"` matches point 1 of the scenario, and so does an item that starts with the number, such as `"1. Whether a miss repeats"`.
6. `CHANGELOG.md` has a line for each brief change.

## May ignore

The cleaner, which has no part in point 2; naming an amendment's points by number, since point 5 covers only the scenario's own points; old slice records under .xv/slices/, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T20:44:06+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T20:44:23+00:00 forecaster: done: Forecast from claude/sonnet and claude/opus feature rows on scenario-agent slices; shape narrow, reopen risk carried in the basis.
- 2026-11-04T20:44:23+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-scenario-catches budget ... --by <name>`).

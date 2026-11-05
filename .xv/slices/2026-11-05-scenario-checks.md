---
id: 2026-11-05-scenario-checks
title: "The checks after the scenario step stop less often for no reason: #120, #136, #140"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-scenario-checks
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 490000, "turns": null, "usd": 2.9, "basis": ["2026-10-30-covers-list", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"]}, {"harness": "claude", "model": "opus", "tokens": 280000, "turns": null, "usd": 3.4, "basis": ["2026-10-30-covers-list", "2026-10-29-red-covers-scenario", "2026-10-30-stop-words"]}], "wall_s": 2800, "shape": "narrow", "breadth": "Moves the covers matcher, the red_gaps accept memory, the wall.red_gaps subcommand check, the send-back path for points 4 and 5, the scenario brief sentence and CHANGELOG; reopen risk sits in points 4 and 5, which change the send-back path."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3426, "cache_read": 24501, "cache_write": 31507, "tokens": 34937, "usd": 0.0083, "turns": 3, "wall_s": 17.2, "session": "0d288591-0f67-4e2e-ae9d-eaac44ed5e8c", "step": "forecaster", "at": "2026-11-05T18:30:04+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-scenario-checks/01-forecaster.out"}]
stops: [{"at": "2026-11-05T18:30:04+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-scenario-checks budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~490k tokens and opus ~280k tokens, narrow shape, from three covers and stop rows; no turns history in the guide.", "at": "2026-11-05T18:30:04+00:00"}], "forecaster": {"at": "2026-11-05T18:30:04+00:00", "wrote": []}}
---
# The checks after the scenario step stop less often for no reason: #120, #136, #140

## Scenario

When this is done:

1. A `covers` name may start with a red file's path, and its parts may be split by `::`, `.`, `#`, `/` or ` > `. It matches when each part after the path is a whole name in that red file, in order. So `tests/test_x.py::Case.test_y`, `tests/test_x.py::Case::test_y` (pytest), `CaseTest#test_y` (Ruby, Java), `TestX/sub` (Go) and `x.test.js > Case > does y` (Jest) all match when the file has them.
2. A `red_gaps` name that a person accepted at a stop is not raised again on that slice.
3. `wall.red_gaps` does not raise an `xv` command in backticks when its words are already an `xv` subcommand at the slice's base and it has no new flag. A new flag on an existing command, such as `--rename` or `--expect-moves`, is still raised. So is a command that does not exist at the base.
4. When a person sends the slice back to the scenario agent, the coverage from the earlier passes stays. An empty `covers` on that pass does not stop the slice. Each kept name must still name a test that exists.
5. After `xv slice amend` on a refactor slice, only the amendment's points need `covers` or `not_covered`.
6. The scenario brief says each red test sets every stand-in setting its result depends on, and does not rely on a default. A test checks the brief for that sentence.
7. `CHANGELOG.md` has a line for each stop this narrows and for the brief change.

## May ignore

old slice records.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T18:29:42+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T18:30:04+00:00 forecaster: done: Forecast sonnet ~490k tokens and opus ~280k tokens, narrow shape, from three covers and stop rows; no turns history in the guide.
- 2026-11-05T18:30:04+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-scenario-checks budget ... --by <name>`).

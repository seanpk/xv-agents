---
id: 2026-11-18-move-names
title: The removal check reads only names it can find
kind: defect
status: working
originator: Sean Kennedy
created: 2026-11-18
branch: xv/2026-11-18-move-names
base: 8e366c9ba6c94b28cbedfad1e5221c22bf914dda
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 490000, "turns": null, "usd": 2.8, "basis": ["2026-11-18-report-tree", "2026-11-16-red-lands", "2026-10-30-by-name", "2026-10-30-stop-words"]}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.5, "basis": ["2026-11-16-red-lands", "2026-10-30-by-name", "2026-10-30-stop-words", "2026-10-30-scenario-miss"]}, {"harness": "claude", "model": "haiku", "tokens": 46000, "turns": null, "usd": 0.01, "basis": ["2026-11-13-names", "2026-11-16-red-lands", "2026-11-18-report-tree"]}], "wall_s": 3500, "rounds": 2, "rounds_reason": "The slice adds a new change_misses_scenario stop and a table of exact name inputs, and report-tree was sent back by the guardian over the same :: and # name forms, so a second pass is likely.", "shape_breadth": "narrow", "shape_note": "Expect movement in the move-name parser and removal check, one table test, the cleaner brief and one CHANGELOG line."}
budget: {"tokens": 836000, "usd": 6.31, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 6654, "cache_read": 62069, "cache_write": 44806, "tokens": 51466, "usd": 0.0129, "turns": 4, "wall_s": 30.9, "session": "e780dbfa-7d3c-4309-8b7a-c5391cc12c44", "step": "forecaster", "at": "2026-11-18T21:02:26+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-18-move-names/01-forecaster.out"}]
stops: [{"at": "2026-11-18T21:02:26+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-move-names budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1, ok (as before, I accept the forecast unless it is wide)", "also": [], "answered_at": "2026-11-18T21:02:38+00:00", "pick": "other", "settled": "The budget is the forecast: 836,000 tokens and $6.31; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 836000, "usd": 6.31}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast ~490k sonnet, ~300k opus, ~46k haiku tokens over two rounds; sonnet and opus basis rows are the name-form and stop-heavy defect slices.", "at": "2026-11-18T21:02:26+00:00"}], "forecaster": {"at": "2026-11-18T21:02:26+00:00", "wrote": [], "removal_not_made": []}}
---
# The removal check reads only names it can find

## Scenario

The removal check reads only names it can find.

1. `xv record move --slice-only` takes an `--assertion` only when it names a test that was in that file when the step began. The name is in a form the check reads: `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`. The name may be followed by a note in brackets: `(...)`, `[...]`, `{...}` or `<...>`. The note is not read for a name. Any other text is refused: the command says that the assertion must be the test's name, with an optional note in brackets, and records nothing.
2. After a step, the removal check looks for exactly the name that the move recorded, without its note. It no longer reads a sentence for a name. A move that reaches the record by another route (in a report) and has no name in a form from outcome 1 stops the step as "the test name could not be read".
3. A table test runs the check over each of these inputs while the test is still in its file: `Red::`, `Red#`, a path with a `-`, `Red::test_x[1]`, `removed Red.test_milk_today as asked`, `removed Red.test_milk_today for issue#183`, `removed Red.test_milk_today.`, a name in backticks, and `Red.test_milk_today (removed as asked)`. Each one stops, at the refusal in outcome 1 or at the check in outcome 2. None of them passes. When the test is gone, `Red.test_milk_today (removed as asked)` and `Red.test_milk_today [see issue#183]` pass.
4. When the packet's `## Scenario misses` section lists a miss but its front matter says `change_misses_scenario: no`, the step stops for the person who set the work going and names the disagreement.
5. The cleaner's brief says that the note for a slice-only removal is the test's name as it is written in the file, with an optional note in brackets after it.
6. A line in CHANGELOG.md.

## May ignore

moves recorded before this change (old slice records); --deleted file removals, which the check already finds by file path

## Recording

None. A feature starts from words.

## Log
- 2026-11-18T21:01:52+00:00 watch: slice opened by Sean Kennedy
- 2026-11-18T21:02:26+00:00 forecaster: done: Forecast ~490k sonnet, ~300k opus, ~46k haiku tokens over two rounds; sonnet and opus basis rows are the name-form and stop-heavy defect slices.
- 2026-11-18T21:02:26+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-18-move-names budget ... --by <name>`).
- 2026-11-18T21:02:38+00:00 Sean Kennedy: set budget
- 2026-11-18T21:02:38+00:00 Sean Kennedy: answered budget_not_set: 1, ok (as before, I accept the forecast unless it is wide)
- 2026-11-18T21:02:38+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy

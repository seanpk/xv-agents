---
id: 2026-11-19-removal-line
title: "A slice-only removal names its line, and the check reads the tree"
kind: defect
status: working
originator: Sean Kennedy
created: 2026-11-19
branch: xv/2026-11-19-removal-line
base: 2ebb304bf2504ae8d50a2c3104889055f7309772
next: scenario
build: none
build_shared: no
forecast: {"rows": [{"harness": "claude", "model": "sonnet", "tokens": 340000, "turns": null, "usd": 2.2, "basis": ["2026-11-18-move-names", "2026-11-16-red-lands", "2026-11-09-defects-tools"]}, {"harness": "claude", "model": "opus", "tokens": 190000, "turns": null, "usd": 2.3, "basis": ["2026-11-18-move-names", "2026-11-16-red-lands", "2026-11-09-defects-tools"]}, {"harness": "claude", "model": "haiku", "tokens": 50000, "turns": null, "usd": 0.01, "basis": ["2026-11-18-move-names", "2026-11-19-wall-keep"]}], "wall_s": 1200, "rounds": 2, "rounds_reason": "move-names drew a guardian send-back at change_misses_scenario, and this slice's scenario makes the same kind of check-and-picture claim, so a second round is likely.", "shape_breadth": "narrow", "shape_note": "Expect edits to the record move command, the removal check, the cleaner and watch briefs, the picture line and one CHANGELOG line, all in one area."}
budget: {"tokens": 580000, "usd": 4.51, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4021, "cache_read": 63049, "cache_write": 46453, "tokens": 50480, "usd": 0.0119, "turns": 4, "wall_s": 31.8, "session": "5d06cef4-97be-4796-a8f6-a996d8dc7597", "step": "forecaster", "at": "2026-11-20T02:25:09+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-19-removal-line/01-forecaster.out"}]
stops: [{"at": "2026-11-20T02:25:09+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-removal-line budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "as before, I accept the forecast unless it is wide", "also": [], "answered_at": "2026-11-20T02:25:17+00:00", "pick": "other", "settled": "The budget is the forecast: 580,000 tokens and $4.51; the forecast was narrow", "new_info": "Sean set the budget to the forecast in advance, unless the forecast was wide; it was narrow", "cause": "decision: the budget is set from the forecast", "budget_change": {"from": null, "to": {"tokens": 580000, "usd": 4.51}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Narrow defect; forecast about 340k sonnet and 190k opus tokens over two rounds, with a likely send-back at the removal check or its picture line.", "at": "2026-11-20T02:25:09+00:00"}], "forecaster": {"at": "2026-11-20T02:25:09+00:00", "wrote": [], "removal_not_made": []}}
---
# A slice-only removal names its line, and the check reads the tree

## Scenario

A slice-only removal names its line, and the check reads the tree.

1. `xv record move --slice-only` takes `--file` and `--line <n>`: the line where the removed test starts, in the file at the commit where the step began (in a pairing, where the pairing began). The command reads that line's text from that commit and records the text with the number. It refuses a blank line, or a number past the end of the file, and records nothing. `--assertion` is a free note again; nothing reads it.
2. After a step, the removal check counts that line's text in the file now. If the count is not lower than at the start commit, the step stops with `removal_not_made`, naming the file, the line number and the text.
3. A removal committed before its move is recorded is taken (the pairing case).
4. A table test runs the check over a Python `def`, a JS `it("…")` whose title has spaces, and a line that is in the file twice: one copy removed passes; none removed stops.
5. The cleaner's brief says how to give the line. The picture says what each check reads, including that the check on accepted slice-only marks finds a name as any whole word in the file.
6. The watch brief's stop table lists the stop for a packet whose front matter says `change_misses_scenario: no` while its `## Scenario misses` section lists a miss. Two slice-only moves for the same file and line are one move.
7. A line in CHANGELOG.md.

## May ignore

- moves recorded before this change
- --deleted file removals
- moves that are not slice-only

## Recording

None. A feature starts from words.

## Log
- 2026-11-20T02:24:33+00:00 watch: slice opened by Sean Kennedy
- 2026-11-20T02:25:09+00:00 forecaster: done: Narrow defect; forecast about 340k sonnet and 190k opus tokens over two rounds, with a likely send-back at the removal check or its picture line.
- 2026-11-20T02:25:09+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-19-removal-line budget ... --by <name>`).
- 2026-11-20T02:25:17+00:00 Sean Kennedy: set budget
- 2026-11-20T02:25:17+00:00 Sean Kennedy: answered budget_not_set: as before, I accept the forecast unless it is wide
- 2026-11-20T02:25:17+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy

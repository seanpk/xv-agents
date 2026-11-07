---
id: 2026-11-07-picture-lines
title: One sentence per line in the picture
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-07
branch: xv/2026-11-07-picture-lines
base: d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50
next: forecaster
build: none
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.6, "basis": ["2026-11-06-covers-stall", "2026-11-05-wave1-fixes", "2026-11-05-scenario-checks"]}, {"harness": "claude", "model": "opus", "tokens": 150000, "turns": null, "usd": 2.0, "basis": ["2026-11-06-covers-stall", "2026-11-05-wave1-fixes", "2026-11-05-scenario-checks"]}], "wall_s": 1500, "shape": "narrow", "breadth": "Four agent briefs (guardian, maker, watch, xv-init), one xv-check check, a CHANGELOG line and a picture rewrap; the only logic is the check and the packet note."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4144, "cache_read": 61873, "cache_write": 35619, "tokens": 39769, "usd": 0.0098, "turns": 4, "wall_s": 20.8, "session": "69083aff-ebd6-45b1-a99f-99685eb15e8c", "step": "forecaster", "at": "2026-11-07T15:18:55+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-07-picture-lines/01-forecaster.out"}]
stops: [{"at": "2026-11-07T15:18:55+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-picture-lines budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet 300k tokens and opus 150k for one pass plus one reopen band; budget is Sean's to set.", "at": "2026-11-07T15:18:55+00:00"}], "forecaster": {"at": "2026-11-07T15:18:55+00:00", "wrote": []}}
---
# One sentence per line in the picture

## Scenario

1. Each sentence in `.xv/picture.md` starts on its own line. The extra lines of a list item are indented two spaces, so they stay in the item.
2. When the lines are joined again, the picture's text is the same as before, word for word. A check shows this.
3. The briefs that write the picture (guardian, maker, watch, `xv-init`) state the rule: one sentence per line, and list-item lines indented two spaces. A repo that adopts xv gets the rule too.
4. `xv-check` finds the same things in the new picture as it did before.
5. A `CHANGELOG.md` line names the rule.
6. When a step leaves a picture line that holds more than one sentence, the packet gets a note naming the line. It is a note, not a stop. A sentence end counts only outside backticks, and only as a full stop and a space followed by a capital letter.

## May ignore

The other .xv files (learnings.md, rules.md, estimation.md) stay as they are. Pictures in other repos that already use xv. Retro candidate 1 (when picture edits happen at rebase); decide it after a few rebases on the new picture.

## Recording

None. A feature starts from words.

## Log
- 2026-11-07T15:18:16+00:00 watch: slice opened by Sean Kennedy
- 2026-11-07T15:18:55+00:00 forecaster: done: Forecast sonnet 300k tokens and opus 150k for one pass plus one reopen band; budget is Sean's to set.
- 2026-11-07T15:18:55+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-picture-lines budget ... --by <name>`).

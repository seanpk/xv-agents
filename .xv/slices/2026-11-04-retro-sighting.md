---
id: 2026-11-04-retro-sighting
title: "Retro accept adds a sighting to an Open learning, and writes no empty field"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-retro-sighting
base: a6e023bd0ffeed4f6ce45990c668742a8f758419
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 330000, "turns": null, "usd": 2.1, "basis": ["2026-10-27-retro-accept-fields", "2026-11-04-proto-start", "2026-11-04-orders-home"], "note": "turns not recorded in the guide; tokens and usd are the mean of the three basis rows' actuals (235k, 218k, 551k; $1.28, $1.22, $3.92)"}, {"harness": "claude", "model": "opus", "tokens": 215000, "turns": null, "usd": 2.6, "basis": ["2026-10-27-retro-accept-fields", "2026-11-04-proto-start", "2026-11-04-orders-home"], "note": "turns not recorded in the guide; tokens and usd are the mean of the three basis rows' actuals (192k, 128k, 325k; $2.29, $1.56, $3.97)"}], "wall_s": 2900, "shape": "wide", "breadth": "Touches retro accept (sighting path and no-empty-field writes), the field reader in scripts/check.py and scripts/promote.py, and the retro brief and skills/xv-retro/SKILL.md. The retro-accept-fields row reopened three times and orders-home ran 6189 s of wall, so wall is the most likely overrun; wall_s is the sum of the sonnet and opus wall for each basis row."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4708, "cache_read": 26131, "cache_write": 25683, "tokens": 30395, "usd": 0.0078, "turns": 3, "wall_s": 24.1, "session": "dc3a0a89-5ded-4e6f-ab15-8937fb299602", "step": "forecaster", "at": "2026-11-04T23:00:17+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-retro-sighting/01-forecaster.out"}]
stops: [{"at": "2026-11-04T23:00:17+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-retro-sighting budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from claude/sonnet and claude/opus rows: sonnet about 330k tokens and opus about 215k, wall about 2900 s; reopen risk is in the basis rows.", "at": "2026-11-04T23:00:17+00:00"}], "forecaster": {"at": "2026-11-04T23:00:17+00:00", "wrote": []}}
---
# Retro accept adds a sighting to an Open learning, and writes no empty field

## Scenario

# Retro accept adds a sighting to an Open learning, and writes no empty field: #108, #49

What happened: on the 2026-10-30 retro (`.xv/retro/2026-10-30.md`, candidate 4), the candidate was three more sightings of an Open learning, "A forecast runs low when answers at a stop add work" (2026-10-27). `xv retro accept` would have written a second entry for it, so the sighting was added by hand (#108). Separately, `xv retro accept` writes a standard or a rule with an empty `from:` or `miss:` when the candidate has none, and the field reader then takes the next line as the value, so `xv check` does not flag a standard or rule that names no slice (#49).

What should happen:

1. A retro candidate can name an Open learning that already exists, with a `sighting of:` field. `xv retro accept` then adds the repo and date to that entry's `seen:` and the candidate's slices to its `from:`. It writes no new entry.
2. The retro brief and `skills/xv-retro/SKILL.md` tell the retro to mark a candidate with `sighting of:` when it matches an entry already in Open.
3. When `xv retro accept` writes a standard or a rule, it leaves out an empty `from:` or `miss:`, as it already does for Open entries.
4. When a field is empty, the field reader in `scripts/check.py` and `scripts/promote.py` does not take the next line as its value. So `xv check` flags a standard or rule that names no slice.

## May ignore

Matching a candidate to an Open entry on its own: the retro names the entry, and accept does not guess. A sighting of a learning already promoted to a standard or a rule: only Open entries count. Old entries in .xv/learnings.md, standards.md or rules.md that already have an empty field.

## Recording

None. A feature starts from words.

## Log
- 2026-11-04T22:59:45+00:00 watch: slice opened by Sean Kennedy
- 2026-11-04T23:00:17+00:00 forecaster: done: Forecast from claude/sonnet and claude/opus rows: sonnet about 330k tokens and opus about 215k, wall about 2900 s; reopen risk is in the basis rows.
- 2026-11-04T23:00:17+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-retro-sighting budget ... --by <name>`).

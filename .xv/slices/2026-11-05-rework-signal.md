---
id: 2026-11-05-rework-signal
title: "A retro is due when the same code needs rework: #114"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-rework-signal
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 240000, "turns": null, "usd": 1.35, "basis": ["2026-11-04-retro-sighting", "2026-11-04-promote-fields", "2026-10-27-retro-accept-fields"]}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.3, "basis": ["2026-11-04-retro-sighting", "2026-11-04-promote-fields", "2026-10-27-retro-accept-fields"]}], "wall_s": 2900, "shape": "narrow", "breadth": "Touches slice record fields, the retro due check, limits.rework_slices in config and defaults, retro candidate and accept output, and one CHANGELOG line; the refactor kind already exists, so the kind model should not move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 5715, "cache_read": 26147, "cache_write": 29569, "tokens": 35288, "usd": 0.009, "turns": 3, "wall_s": 27.9, "session": "50fea462-9d5b-4700-ae29-3d47c95fd942", "step": "forecaster", "at": "2026-11-05T18:30:15+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-rework-signal/01-forecaster.out"}]
stops: [{"at": "2026-11-05T18:30:15+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-rework-signal budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Sonnet ~240k tokens / $1.35, Opus ~200k tokens / $2.30, wall ~2900 s, shape narrow; a reopen is the main risk.", "at": "2026-11-05T18:30:15+00:00"}], "forecaster": {"at": "2026-11-05T18:30:15+00:00", "wrote": []}}
---
# A retro is due when the same code needs rework: #114

## Scenario

When this is done:

1. When a slice closes, its record keeps `modules_touched`, the modules `xv boundary` lists as touched, and `maker_sendbacks`, how many times the slice went back to the maker.
2. `xv retro due` gives a reason when one module was touched by at least `limits.rework_slices` closed slices since the last retro, each sent back to the maker at least once. The reason names the module and the slices.
3. `limits.rework_slices` is in `.xv/config.yml` and `defaults/config.yml`. The default is 3, and 0 turns it off.
4. For such a module, the retro proposes a refactor slice, a candidate of kind `refactor`. `xv retro accept` on it prints the `xv slice new --kind refactor` command for the person to run. It does not open the slice.
5. `CHANGELOG.md` has a line for the retro brief change.

## May ignore

old slice records without the new fields, which count as never sent back.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T18:29:42+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T18:30:15+00:00 forecaster: done: Sonnet ~240k tokens / $1.35, Opus ~200k tokens / $2.30, wall ~2900 s, shape narrow; a reopen is the main risk.
- 2026-11-05T18:30:15+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-rework-signal budget ... --by <name>`).

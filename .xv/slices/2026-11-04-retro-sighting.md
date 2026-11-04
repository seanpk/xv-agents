---
id: 2026-11-04-retro-sighting
title: "Retro accept adds a sighting to an Open learning, and writes no empty field"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-retro-sighting
base: a6e023bd0ffeed4f6ce45990c668742a8f758419
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

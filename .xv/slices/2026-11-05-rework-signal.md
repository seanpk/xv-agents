---
id: 2026-11-05-rework-signal
title: "A retro is due when the same code needs rework: #114"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-rework-signal
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
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

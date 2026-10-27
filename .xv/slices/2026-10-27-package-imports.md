---
id: 2026-10-27-package-imports
title: A bare import inside a package resolves the way Python does
kind: defect
status: open
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-package-imports
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
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
# A bare import inside a package resolves the way Python does

## Scenario

Inside a Python package, `xv boundary` resolves a bare import the way Python does. `resolve` in `scripts/boundary.py` tries the importing file's own folder first only when that folder has no `__init__.py`. Take `src/api/main.py` with a sibling `src/api/store.py` and a package `src/store/`: when `src/api/` has an `__init__.py`, `import store` in `main.py` resolves to `src/store`, and the edge `src/api` → `src/store` is in the boundary picture. When `src/api/` has no `__init__.py` (flat scripts, like this repo's `scripts/`), it still resolves to `src/api/store.py`, as today. (seanpk/xv-agents#26)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:07:55+00:00 watch: slice opened by Sean Kennedy

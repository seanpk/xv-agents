---
id: 2026-10-27-package-imports
title: A bare import inside a package resolves the way Python does
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-package-imports
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 700000, "turns": null, "usd": 0.45, "basis": ["2026-10-24-boundary-imports", "2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 600000, "turns": null, "usd": 0.75, "basis": ["2026-10-24-boundary-imports", "2026-10-25-diff-count"], "note": "one guardian pass; boundary-imports ran two passes at 1.21M tokens"}], "wall_s": 600, "shape": "narrow", "breadth": "resolve() in scripts/boundary.py gains an __init__.py check and the flat-script path stays as is; expect package-layout test cases under tests/**."}
budget: null
red: null
wall_baseline: null
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4654, "cache_read": 25007, "cache_write": 9860, "tokens": 14518, "usd": 0.0045, "turns": 3, "wall_s": 25.7, "session": "8bb33f18-fc95-4a71-bf20-704f694dbe47", "step": "forecaster", "at": "2026-10-27T14:08:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-package-imports/01-forecaster.out"}]
stops: [{"at": "2026-10-27T14:08:21+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-package-imports budget ... --by <name>`).", "answered_by": [], "answer": null, "also": []}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Sonnet ~700k and opus ~600k tokens from the boundary-imports and diff-count actuals; narrow shape, reopen risk leaned in.", "at": "2026-10-27T14:08:21+00:00"}], "forecaster": {"at": "2026-10-27T14:08:21+00:00", "wrote": []}}
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
- 2026-10-27T14:08:21+00:00 forecaster: done: Sonnet ~700k and opus ~600k tokens from the boundary-imports and diff-count actuals; narrow shape, reopen risk leaned in.
- 2026-10-27T14:08:21+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-package-imports budget ... --by <name>`).

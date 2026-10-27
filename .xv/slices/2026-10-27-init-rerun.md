---
id: 2026-10-27-init-rerun
title: xv init runs again without crashing
kind: defect
status: working
set_by: Sean Kennedy
created: 2026-10-27
branch: xv/2026-10-27-init-rerun
base: 94cdf5f15f31c53d02fc8de787ce85889627e799
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 482000, "turns": null, "usd": 0.31, "basis": ["2026-10-25-diff-count"]}, {"harness": "claude", "model": "opus", "tokens": 284000, "turns": null, "usd": 0.55, "basis": ["2026-10-25-diff-count"]}], "wall_s": 300, "shape": "narrow", "breadth": "One branch in cmd_init (runners is set only when config.yml is written) plus a test under tests/**. The guide has no turns history. Nine of the last ten closed slices reopened or reran (scenario, maker, cleaner, guardian), with the clean pass as the floor, so the realistic spend is about 2-3x the clean figure."}
budget: {"tokens": 200000, "usd": 1.25, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_init_rerun.py"], "command": "cd tests && python3 -m unittest test_init_rerun", "failure": "UnboundLocalError: cannot access local variable 'runners' where it is not associated with a value (scripts/run.py cmd_init, `if len(runners) > 1:`), so the returncode assertion fails", "watch_first_green": null}
wall_baseline: {"commit": "0336b80e03ef137bca8a01ff93daff3e5e6d8621", "count": 41, "digest": "c6dc54b931f7af39", "file": ".xv/slices/2026-10-27-init-rerun.wall.json"}
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 5136, "cache_read": 25011, "cache_write": 9833, "tokens": 14973, "usd": 0.0048, "turns": 3, "wall_s": 24.9, "session": "a0e04c36-3d84-40c8-96b9-a3b77595d93d", "step": "forecaster", "at": "2026-10-27T14:28:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-init-rerun/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 12, "tokens_out": 1625, "cache_read": 105225, "cache_write": 12823, "tokens": 14460, "usd": 0.0781, "turns": 9, "wall_s": 16.7, "session": "e239b636-386c-4e44-9511-01baf072b335", "step": "scenario", "at": "2026-10-27T14:36:33+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-27-init-rerun/02-scenario.out"}]
stops: [{"at": "2026-10-27T14:28:21+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-rerun budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "yes for budgets", "also": [], "answered_at": "2026-10-27T14:36:13+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Clean single pass is about 482k sonnet tokens and 284k opus tokens, about 300 s wall; 9 of 10 recent slices reopened, so a budget at the clean figure is likely to be exceeded.", "at": "2026-10-27T14:28:21+00:00"}, {"agent": "scenario", "status": "red", "summary": "A second `xv init` with a missing pitch.md should write it, keep existing files, print JSON and exit 0; today it crashes with UnboundLocalError on `runners`.", "at": "2026-10-27T14:36:33+00:00"}], "forecaster": {"at": "2026-10-27T14:28:21+00:00", "wrote": []}, "scenario": {"at": "2026-10-27T14:36:33+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "\"<frozen runpy>\", line 292, in run_path\n  File \"<frozen runpy>\", line 97, in _run_module_code\n  File \"<frozen runpy>\", line 87, in _run_code\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-27-init-rerun/scripts/run.py\", line 995, in <module>\n    main()\n    ~~~~^^\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-27-init-rerun/scripts/run.py\", line 989, in main\n    a.fn(a)\n    ~~~~^^^\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-27-init-rerun/scripts/run.py\", line 919, in cmd_init\n    if len(runners) > 1:\n           ^^^^^^^\nUnboundLocalError: cannot access local variable 'runners' where it is not associated with a value\n\n\n----------------------------------------------------------------------\nRan 1 test in 4.224s\n\nFAILED (failures=1)\n"}}
---
# xv init runs again without crashing

## Scenario

`xv init` runs again in a repo whose `.xv/config.yml` already exists, to fill in a missing file, without crashing. Today `runners` is set only when init writes the config (`if "config.yml" in written:` in `cmd_init`, `scripts/run.py`) and read later by `if len(runners) > 1:`, so a second run raises `UnboundLocalError` before it prints anything. After the fix, a second run with a missing `.xv/pitch.md` writes the starter pitch, keeps every existing file, prints its usual JSON output, and exits 0. (seanpk/xv-agents#40)

## May ignore

Nothing stated.

## Recording

None. A feature starts from words.

## Log
- 2026-10-27T14:27:49+00:00 watch: slice opened by Sean Kennedy
- 2026-10-27T14:28:21+00:00 forecaster: done: Clean single pass is about 482k sonnet tokens and 284k opus tokens, about 300 s wall; 9 of 10 recent slices reopened, so a budget at the clean figure is likely to be exceeded.
- 2026-10-27T14:28:21+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-27-init-rerun budget ... --by <name>`).
- 2026-10-27T14:36:13+00:00 Sean Kennedy: set budget
- 2026-10-27T14:36:13+00:00 Sean Kennedy: answered budget_not_set: yes for budgets
- 2026-10-27T14:36:33+00:00 scenario: red: A second `xv init` with a missing pitch.md should write it, keep existing files, print JSON and exit 0; today it crashes with UnboundLocalError on `runners`.

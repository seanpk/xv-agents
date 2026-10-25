---
id: 2026-10-24-boundary-imports
title: xv boundary finds Python edges in src layouts and flat scripts
kind: defect
status: working
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-boundary-imports
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: cleaner
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect the Python import-edge resolution in boundary and its tests under tests/ to move; the defect is one bug with one scenario, so no wide change is expected."}
budget: {"tokens": 1500000, "usd": 5, "turns": 60, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_boundary_python_edges.py"], "command": "cd tests && python3 -m unittest test_boundary_python_edges", "failure": "AssertionError: Lists differ: [] != [['scripts/run', 'scripts/agentcli'], ['scripts/run', 'scripts/orders'], ['scripts/run', 'scripts/record']]", "watch_first_green": null}
wall_baseline: {"commit": "3abb00ae0806a590877ee5ceb1c97d63ce585efd", "count": 25, "digest": "c48a330d4a653e65", "file": ".xv/slices/2026-10-24-boundary-imports.wall.json"}
moved_tests: []
suite: green
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 1016, "cache_read": 23319, "cache_write": 6305, "tokens": 30644, "usd": 0.002, "turns": 3, "wall_s": 6.6, "session": "4af2d40c-e67c-4ee7-bb28-0b02cca61c6d", "step": "forecaster", "at": "2026-10-25T03:27:08+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-boundary-imports/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 3824, "cache_read": 196377, "cache_write": 15564, "tokens": 215785, "usd": 0.1202, "turns": 11, "wall_s": 31.5, "session": "2e73b888-5c06-48f8-a225-d177d231f993", "step": "scenario", "at": "2026-10-25T03:34:32+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-boundary-imports/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 10, "tokens_out": 966, "cache_read": 86314, "cache_write": 12411, "tokens": 99701, "usd": 0.068, "turns": 6, "wall_s": 10.1, "session": "b471dd6a-778e-419a-be7a-b772673fb37b", "step": "scenario", "at": "2026-10-25T03:55:07+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-boundary-imports/03-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 24, "tokens_out": 3266, "cache_read": 251170, "cache_write": 16398, "tokens": 270858, "usd": 0.1234, "turns": 19, "wall_s": 52.0, "session": "6691b8ff-244f-4583-afef-f081cb3a5a22", "step": "maker", "at": "2026-10-25T03:55:59+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-boundary-imports/04-maker.out"}]
stops: [{"at": "2026-10-25T03:27:08+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-boundary-imports budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "you can set your suggested estimate", "also": [], "answered_at": "2026-10-25T03:33:47+00:00"}, {"at": "2026-10-25T03:34:32+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (stopped): Wrote tests/test_boundary_python_edges.py but could not run it: the sandbox denied python3 execution, so the red is unverified.", "answered_by": ["Sean Kennedy"], "answer": "run it (rerun the scenario under the new allow list)", "also": [], "answered_at": "2026-10-25T03:54:50+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No guide rows for claude/sonnet or claude/opus; numbers left null for the engineer to set by hand.", "at": "2026-10-25T03:27:08+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Wrote tests/test_boundary_python_edges.py but could not run it: the sandbox denied python3 execution, so the red is unverified.", "at": "2026-10-25T03:34:32+00:00"}, {"agent": "scenario", "status": "red", "summary": "Python imports in flat scripts and src layouts produce no edges in boundary.graph; 3 tests fail with edges == [].", "at": "2026-10-25T03:55:07+00:00"}, {"agent": "maker", "status": "green", "summary": "py import resolution in boundary.resolve now also tries source roots and the importing file's directory, so flat-script and src-layout imports produce edges", "at": "2026-10-25T03:55:59+00:00"}], "forecaster": {"at": "2026-10-25T03:27:08+00:00", "wrote": []}, "scenario": {"at": "2026-10-25T03:55:07+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "elf.assertEqual(edges_of(files, [\"scripts\"]), [\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        [\"scripts/run\", \"scripts/agentcli\"],\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        [\"scripts/run\", \"scripts/orders\"],\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        [\"scripts/run\", \"scripts/record\"]])\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: Lists differ: [] != [['scripts/run', 'scripts/agentcli'], ['sc[60 chars]rd']]\n\nSecond list contains 3 additional elements.\nFirst extra element 0:\n['scripts/run', 'scripts/agentcli']\n\n- []\n+ [['scripts/run', 'scripts/agentcli'],\n+  ['scripts/run', 'scripts/orders'],\n+  ['scripts/run', 'scripts/record']]\n\n----------------------------------------------------------------------\nRan 3 tests in 0.001s\n\nFAILED (failures=3)\n"}, "maker": {"at": "2026-10-25T03:55:59+00:00", "protected_changed": [], "suite": "green", "suite_output": "t_wall.py:30: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-1yusb6hf/repo/.xv/worktrees/s1/tests/test_store.py' mode='r' encoding='utf-8'>\n  write(path, open(path).read().replace('(\"bread\", 0)', \"anything\"))\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-24-boundary-imports/tests/test_wall.py:60: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-l8ofelox/repo/.xv/worktrees/s1/tests/test_store.py' mode='r' encoding='utf-8'>\n  write(path, open(path).read().replace('(\"bread\", 0)', \"anything\"))\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n----------------------------------------------------------------------\nRan 123 tests in 24.851s\n\nOK\n", "failing": [], "failing_history": [[]], "diff_lines": 173, "diff_history": [173], "wall": {"slice": "2026-10-24-boundary-imports", "baseline": "3abb00ae0806a590877ee5ceb1c97d63ce585efd", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}}}
---
# xv boundary finds Python edges in src layouts and flat scripts

## Scenario

In a `src/` layout and in flat scripts that import each other by bare name, `xv boundary` shows an edge for every import between modules. On this repo, `.xv/boundary-all.md` shows `run` -> `agentcli`, `orders`, `prompt`, `record`, `spend`. (seanpk/xv-agents#12)

## May ignore

JavaScript, Ruby and Go imports; dependency-cruiser

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:08+00:00 forecaster: done: No guide rows for claude/sonnet or claude/opus; numbers left null for the engineer to set by hand.
- 2026-10-25T03:27:08+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-boundary-imports budget ... --by <name>`).
- 2026-10-25T03:33:47+00:00 Sean Kennedy: set budget
- 2026-10-25T03:33:47+00:00 Sean Kennedy: answered budget_not_set: you can set your suggested estimate
- 2026-10-25T03:34:32+00:00 scenario: stopped: Wrote tests/test_boundary_python_edges.py but could not run it: the sandbox denied python3 execution, so the red is unverified.
- 2026-10-25T03:34:32+00:00 watch: stop (scenario_stopped) for originator: The scenario stopped (stopped): Wrote tests/test_boundary_python_edges.py but could not run it: the sandbox denied python3 execution, so the red is unverified.
- 2026-10-25T03:54:50+00:00 Sean Kennedy: answered scenario_stopped: run it (rerun the scenario under the new allow list)
- 2026-10-25T03:55:07+00:00 scenario: red: Python imports in flat scripts and src layouts produce no edges in boundary.graph; 3 tests fail with edges == [].
- 2026-10-25T03:55:59+00:00 maker: green: py import resolution in boundary.resolve now also tries source roots and the importing file's directory, so flat-script and src-layout imports produce edges

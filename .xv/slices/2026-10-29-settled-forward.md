---
id: 2026-10-29-settled-forward
title: Some stops ask for --settled when the answer moves the slice forward
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-settled-forward
base: cafedce2750c9b8bfed996553f0f139df2563608
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 2.8, "basis": ["2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "Midpoint of the two basis rows (674k/$3.87 and 395k/$2.27). A clean single pass ran far lower, so the reopen risk drives this number. The guide has no turns column."}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.0, "basis": ["2026-10-29-stop-decisions", "2026-10-27-prototype-budgets"], "note": "Midpoint of the two basis rows (392k/$4.89 and 230k/$2.79). One clean guardian pass ran about $0.35 to $0.41, so the usd depends on how many passes the guardian runs. The guide has no turns column."}], "wall_s": 2000, "shape": "narrow", "breadth": "cmd_answer gating for setup_failed, prototype stops and pre-step budget stops, plus record stop --step plumbing and the README answer-line test; other stop kinds should not move."}
budget: {"tokens": 600000, "usd": 4, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_record.py"], "command": "cd tests && python3 -m unittest test_record.SettledForwardTest", "failure": "xv record: error: unrecognized arguments: --step maker", "watch_first_green": null}
wall_baseline: {"commit": "ca64991bef60860ee23d8f01d85b7e1be759296f", "count": 47, "digest": "9823b5834a8ea822", "file": ".xv/slices/2026-10-29-settled-forward.wall.json"}
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3378, "cache_read": 25516, "cache_write": 17019, "tokens": 20401, "usd": 0.0053, "turns": 3, "wall_s": 17.2, "session": "a5cf1b12-efdc-48c8-8dbc-5e511dabbf7e", "step": "forecaster", "at": "2026-10-29T21:51:20+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-settled-forward/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 24, "tokens_out": 5756, "cache_read": 341497, "cache_write": 32472, "tokens": 38252, "usd": 0.2216, "turns": 14, "wall_s": 43.2, "session": "80277775-46ec-4a1f-8a7b-1b4d9334b6f2", "step": "scenario", "at": "2026-10-29T21:53:58+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-settled-forward/02-scenario.out"}]
stops: [{"at": "2026-10-29T21:51:20+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-settled-forward budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "$4 and 600K tokens", "settles": "The budget is $4 and 600K tokens: room for one clean pass and one send-back.", "amends": false}, {"text": "$6 and 800K tokens, the forecast", "settles": "The budget is $6 and 800K tokens, as forecast.", "amends": false}, {"text": "$2.50 and 400K tokens", "settles": "The budget is $2.50 and 400K tokens: one clean pass; a send-back stops for budget.", "amends": false}], "recommended": 1, "answered_at": "2026-10-29T21:53:11+00:00", "pick": 1, "settled": "The budget is $4 and 600K tokens: room for one clean pass and one send-back.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 600000, "usd": 4}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~500k tokens and claude/opus ~300k tokens from the stop-decisions and prototype-budgets rows, with reopen risk; shape narrow.", "at": "2026-10-29T21:51:20+00:00"}, {"agent": "scenario", "status": "red", "summary": "Seven tests in test_record.SettledForwardTest fail: record stop has no --step, so settled-forward answers for setup_failed, prototype and budget_spent stops, and the README answer line, cannot be run.", "at": "2026-10-29T21:53:58+00:00"}], "forecaster": {"at": "2026-10-29T21:51:20+00:00", "wrote": []}, "scenario": {"at": "2026-10-29T21:53:58+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "king/Personal/xv-agents/.xv/worktrees/2026-10-29-settled-forward/tests/helpers.py\", line 16, in sh\n    raise AssertionError(f\"{cmd} failed {p.returncode}: {p.stderr}{p.stdout}\")\nAssertionError: ['/home/sean/.local/share/mise/installs/python/latest/bin/python3', '/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-29-settled-forward/bin/xv', 'record', 'stop', 's1', '--order', 'scenario_stopped', '--seat', 'originator', '--question', 'Q?', '--step', 'scenario'] failed 2: usage: xv record [-h]\n                 {new,show,get,set,add,move,override,stop,offer,answer,report,packet,export,guide-append,guide-verify} ...\nxv record: error: unrecognized arguments: --step scenario\n\n\n----------------------------------------------------------------------\nRan 7 tests in 0.684s\n\nFAILED (failures=7)\n", "old_red_changed": []}}
---
# Some stops ask for --settled when the answer moves the slice forward

## Scenario

Some stops ask for `--settled` when the answer moves the slice forward (#82).

1. When a setup fails (`setup_failed`) or a prototype stops, the work has not started yet, so any `--next` moves forward. No `--settled` is needed.
2. A budget stop raised before its step ran is the same: `--next <that step>` moves forward and needs no `--settled`.
3. `xv record stop` takes `--step`, and the tests use it. They no longer edit the record text to add a step.
4. A test runs the README's general answer line (`README.md:295`), not only its words.

## May ignore

cmd_answer is 68 lines, and two test lines read 'p =self.xv': those are the cleaner's, under the standards.

## Recording

None. A feature starts from words.

## Log
- 2026-10-29T21:51:00+00:00 watch: slice opened by Sean Kennedy
- 2026-10-29T21:51:20+00:00 forecaster: done: Forecast claude/sonnet ~500k tokens and claude/opus ~300k tokens from the stop-decisions and prototype-budgets rows, with reopen risk; shape narrow.
- 2026-10-29T21:51:20+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-settled-forward budget ... --by <name>`).
- 2026-10-29T21:51:31+00:00 watch: offered 3 options for budget_not_set
- 2026-10-29T21:53:11+00:00 Sean Kennedy: set budget
- 2026-10-29T21:53:11+00:00 Sean Kennedy: answered budget_not_set: 1
- 2026-10-29T21:53:11+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-29T21:53:58+00:00 scenario: red: Seven tests in test_record.SettledForwardTest fail: record stop has no --step, so settled-forward answers for setup_failed, prototype and budget_spent stops, and the README answer line, cannot be run.

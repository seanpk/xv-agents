---
id: 2026-10-30-test-marks
title: A person sees which tests stay on the wall and which leave it
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-test-marks
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.7, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 190000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-slice-tests", "2026-10-27-prototype-budgets", "2026-10-29-settled-forward"]}], "wall_s": 1650, "shape": "narrow", "breadth": "Adds one conditional stop after scenario (fires only when slice-only marks exist) and a fifth guardian check; touches the watch stop table, README, scenario brief, packet template, guardian SKILL and CHANGELOG, not the pipeline order. Reopen risk from the new accept_moves order is inside the basis means."}
budget: {"tokens": 750000, "usd": 6, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_orders.py"], "command": "cd tests && python3 -m unittest test_orders", "failure": "AssertionError: '## The five checks' not found in skills/guardian/SKILL.md; slice-only marks after scenario fire no stop", "watch_first_green": "Run a slice whose scenario step marks a test slice-only: the watch should stop for the person who set the work going, listing each marked test with its reason, and a slice with no marks should not stop. Then read the guardian packet: it should have a fifth section recommending which new tests join the wall or leave it, with those recommendations reaching you in accept_moves and the record keeping which you accepted."}
wall_baseline: {"commit": "28dfb65e8318f59bbd4bfb4c6b105198c3f1e5d5", "count": 47, "digest": "8c86daa89e58675e", "file": ".xv/slices/2026-10-30-test-marks.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_orders.py", "test": "test_the_readme_says_five_checks_not_four", "why": "guards a one-time wording change from four to five in the README; no value once the wording is changed"}]
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3352, "cache_read": 25528, "cache_write": 17858, "tokens": 21214, "usd": 0.0055, "turns": 3, "wall_s": 16.4, "session": "a8d49f10-ea19-4584-8b72-b6ba6798e7bd", "step": "forecaster", "at": "2026-10-30T01:07:36+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 4864, "cache_read": 264560, "cache_write": 28094, "tokens": 32978, "usd": 0.1875, "turns": 12, "wall_s": 36.1, "session": "0c1ba74c-eb09-4b78-8d3a-c007c84980bf", "step": "scenario", "at": "2026-10-30T01:12:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/02-scenario.out"}]
stops: [{"at": "2026-10-30T01:07:36+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-test-marks budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "your pick for B's budget is fine, so you can give it a head start while you tell me about A3", "also": [], "options": [{"text": "$6 and 750K tokens", "settles": "The budget is $6 and 750K tokens: the forecast plus room for one send-back.", "amends": false}, {"text": "$4 and 490K tokens, the forecast", "settles": "The budget is $4 and 490K tokens, as forecast.", "amends": false}, {"text": "$8 and 1M tokens", "settles": "The budget is $8 and 1M tokens: room for several send-backs.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T01:11:46+00:00", "pick": 1, "settled": "The budget is $6 and 750K tokens: the forecast plus room for one send-back.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 750000, "usd": 6}}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~300k tokens and opus ~190k tokens for the slice, from the three closest feature rows; narrow shape with a reopen risk from the new accept_moves order.", "at": "2026-10-30T01:07:36+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red tests for the slice-only marks stop after scenario and the guardian's fifth check (brief, README, packet section) in tests/test_orders.py", "at": "2026-10-30T01:12:23+00:00"}], "forecaster": {"at": "2026-10-30T01:07:36+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T01:12:23+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "](docs/borrowed.md).\\n'\n\n======================================================================\nFAIL: test_slice_only_marks_after_the_scenario_stop_for_the_person_who_set_it_going (test_orders.OrdersTest.test_slice_only_marks_after_the_scenario_stop_for_the_person_who_set_it_going)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-30-test-marks/tests/test_orders.py\", line 168, in test_slice_only_marks_after_the_scenario_stop_for_the_person_who_set_it_going\n    self.assertIsNotNone(s)\n    ~~~~~~~~~~~~~~~~~~~~^^^\nAssertionError: unexpectedly None\n\n----------------------------------------------------------------------\nRan 29 tests in 0.001s\n\nFAILED (failures=4, errors=1)\n", "old_red_changed": []}}
---
# A person sees which tests stay on the wall and which leave it

## Scenario

A person sees which tests stay on the wall and which leave it (#87, #89).

1. The person accepts the slice-only marks (#89). After the scenario step, a new order seated for the person who set the work going fires only when the scenario report marks slice-only tests. It lists each marked test with the scenario agent's reason. The person accepts the marks, or unmarks a test so it joins the wall. The answer is recorded like any other stop. A slice with no marks adds no stop. The watch's stop table and the README's list the new order.
2. The guardian says which new tests should join the wall or leave it (#87). `skills/guardian/SKILL.md` has a fifth check, for three kinds of recommendation: a test marked slice-only should stay; a new test that was not marked should not join the wall; a test that was on the wall before the slice should be removed. The packet has a section for them. They reach the person who set the work going in `accept_moves`, not two people, and the record keeps which ones the person accepted. The places that say the guardian has four checks say five.

This adds a standing order and changes a brief and the packet template, so `CHANGELOG.md` gets a line.

## May ignore

Rewording the site. Moving slice-only tests out of the cleaner.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T01:07:13+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T01:07:36+00:00 forecaster: done: Forecast sonnet ~300k tokens and opus ~190k tokens for the slice, from the three closest feature rows; narrow shape with a reopen risk from the new accept_moves order.
- 2026-10-30T01:07:36+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-test-marks budget ... --by <name>`).
- 2026-10-30T01:07:42+00:00 watch: offered 3 options for budget_not_set
- 2026-10-30T01:11:46+00:00 Sean Kennedy: set budget
- 2026-10-30T01:11:46+00:00 Sean Kennedy: answered budget_not_set: your pick for B's budget is fine, so you can give it a head start while you tell me about A3
- 2026-10-30T01:11:46+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-30T01:12:23+00:00 scenario: red: Red tests for the slice-only marks stop after scenario and the guardian's fifth check (brief, README, packet section) in tests/test_orders.py

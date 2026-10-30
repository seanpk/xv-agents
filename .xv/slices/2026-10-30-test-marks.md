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
red: {"files": ["tests/test_orders.py"], "command": "cd tests && python3 -m unittest test_orders", "failure": "AssertionError: '## The five checks' not found in skills/guardian/SKILL.md; slice-only marks after scenario fire no stop; KeyError: 'wall_recommendations'", "watch_first_green": "Run a slice whose scenario step marks a test slice-only: the watch should stop for the person who set the work going, listing each marked test with its reason, and a slice with no marks should not stop. Unmark one test: it should drop off the list and the cleaner should keep it. Then read the guardian packet: it should have a fifth section recommending which new tests join the wall or leave it, with those recommendations reaching you in accept_moves and the record keeping which you accepted."}
wall_baseline: {"commit": "58ac3dfec17077625b792df032f5f8e3dd39d5e5", "count": 47, "digest": "637df52ad29a70a0", "file": ".xv/slices/2026-10-30-test-marks.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_orders.py", "test": "test_the_readme_says_five_checks_not_four", "why": "guards a one-time wording change from four to five in the README; no value once the wording is changed"}]
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3352, "cache_read": 25528, "cache_write": 17858, "tokens": 21214, "usd": 0.0055, "turns": 3, "wall_s": 16.4, "session": "a8d49f10-ea19-4584-8b72-b6ba6798e7bd", "step": "forecaster", "at": "2026-10-30T01:07:36+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 4864, "cache_read": 264560, "cache_write": 28094, "tokens": 32978, "usd": 0.1875, "turns": 12, "wall_s": 36.1, "session": "0c1ba74c-eb09-4b78-8d3a-c007c84980bf", "step": "scenario", "at": "2026-10-30T01:12:23+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 30, "tokens_out": 7642, "cache_read": 511483, "cache_write": 43446, "tokens": 51118, "usd": 0.3014, "turns": 17, "wall_s": 55.2, "session": "d86f9dcd-fd64-426c-bbef-b049d1ca9197", "step": "scenario", "at": "2026-10-30T01:16:37+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-test-marks/03-scenario.out"}]
stops: [{"at": "2026-10-30T01:07:36+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-test-marks budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "your pick for B's budget is fine, so you can give it a head start while you tell me about A3", "also": [], "options": [{"text": "$6 and 750K tokens", "settles": "The budget is $6 and 750K tokens: the forecast plus room for one send-back.", "amends": false}, {"text": "$4 and 490K tokens, the forecast", "settles": "The budget is $4 and 490K tokens, as forecast.", "amends": false}, {"text": "$8 and 1M tokens", "settles": "The budget is $8 and 1M tokens: room for several send-backs.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T01:11:46+00:00", "pick": 1, "settled": "The budget is $6 and 750K tokens: the forecast plus room for one send-back.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 750000, "usd": 6}}}, {"at": "2026-10-30T01:12:39+00:00", "order": "red_check", "seat": "originator", "question": "The red covers the new stop and its listing, and the guardian's five checks in the brief, README and packet. It has no test for: a person unmarking a test so it joins the wall; a wall recommendation reaching the person in accept_moves; the record keeping which recommendations the person accepted; the stop tables listing the new order.", "answered_by": ["Sean Kennedy"], "answer": "B: 1", "step": "scenario", "options": [{"text": "Send it back for the four missing tests", "settles": "The scenario agent adds tests for: a person unmarking a slice-only test so it joins the wall (the cleaner then keeps it); a guardian recommendation on which tests join or leave the wall firing accept_moves for the person who set the work going; the record keeping which recommendations the person accepted; and the watch's stop table and the README's listing the new order.", "amends": false}, {"text": "Go on to the maker as it is", "settles": "The red stands as written. Unmarking, accept_moves on a recommendation, the record of accepted recommendations and the stop tables have no test; the guardian checks them against the scenario.", "amends": false}, {"text": "Send it back for the behaviour only, not the stop tables", "settles": "The scenario agent adds tests for unmarking a slice-only test, accept_moves firing on a wall recommendation, and the record keeping which recommendations were accepted. The stop tables are left to the guardian.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T01:15:42+00:00", "pick": 1, "settled": "The scenario agent adds tests for: a person unmarking a slice-only test so it joins the wall (the cleaner then keeps it); a guardian recommendation on which tests join or leave the wall firing accept_moves for the person who set the work going; the record keeping which recommendations the person accepted; and the watch's stop table and the README's listing the new order.", "new_info": "none", "cause": "agent: the scenario brief; the red left three behaviours and the stop tables without tests"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~300k tokens and opus ~190k tokens for the slice, from the three closest feature rows; narrow shape with a reopen risk from the new accept_moves order.", "at": "2026-10-30T01:07:36+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red tests for the slice-only marks stop after scenario and the guardian's fifth check (brief, README, packet section) in tests/test_orders.py", "at": "2026-10-30T01:12:23+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red now also covers unmarking, accept_moves on wall recommendations, the record keeping them, and the stop tables listing the slice-only marks stop", "at": "2026-10-30T01:16:37+00:00"}], "forecaster": {"at": "2026-10-30T01:07:36+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T01:16:37+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": " ('skills', 'watch', 'SKILL.md')\n\n======================================================================\nFAIL: test_unmarking_a_test_takes_it_off_the_stop_and_leaves_it_to_join_the_wall (test_orders.OrdersTest.test_unmarking_a_test_takes_it_off_the_stop_and_leaves_it_to_join_the_wall)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-30-test-marks/tests/test_orders.py\", line 183, in test_unmarking_a_test_takes_it_off_the_stop_and_leaves_it_to_join_the_wall\n    self.assertIsNotNone(s)\n    ~~~~~~~~~~~~~~~~~~~~^^^\nAssertionError: unexpectedly None\n\n----------------------------------------------------------------------\nRan 35 tests in 0.002s\n\nFAILED (failures=8, errors=2)\n", "old_red_changed": []}}
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
- 2026-10-30T01:12:39+00:00 watch: stop (red_check) for originator: The red covers the new stop and its listing, and the guardian's five checks in the brief, README and packet. It has no test for: a person unmarking a test so it joins the wall; a wall recommendation reaching the person in accept_moves; the record keeping which recommendations the person accepted; the stop tables listing the new order.
- 2026-10-30T01:12:39+00:00 watch: offered 3 options for red_check
- 2026-10-30T01:15:42+00:00 Sean Kennedy: answered red_check: B: 1
- 2026-10-30T01:15:42+00:00 watch: scribe: wrote settled, new_info, cause for red_check as the scribe of Sean Kennedy
- 2026-10-30T01:16:37+00:00 scenario: red: Red now also covers unmarking, accept_moves on wall recommendations, the record keeping them, and the stop tables listing the slice-only marks stop

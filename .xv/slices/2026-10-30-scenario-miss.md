---
id: 2026-10-30-scenario-miss
title: A slice that misses its own scenario goes back without a stop
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-30
branch: xv/2026-10-30-scenario-miss
base: f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 2.7, "basis": ["2026-10-30-stop-words", "2026-10-30-by-name", "2026-10-30-test-marks"], "note": "turns not in guide; test-marks ran 869k with nine scenario runs, so a second reopen would roughly double this"}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.4, "basis": ["2026-10-30-stop-words", "2026-10-30-by-name", "2026-10-30-test-marks"], "note": "turns not in guide; test-marks ran 478k and $6.12 with six guardian passes, so a reopen here is the largest usd risk"}], "wall_s": 2500, "shape": "narrow", "breadth": "Touches the guardian and watch briefs, packet template, scripts/run.py message, one check, standing orders and CHANGELOG; the code path it changes is narrow."}
budget: {"tokens": 1500000, "usd": 12, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_orders.py", "tests/test_packet.py", "tests/test_run.py"], "command": "cd tests && python3 -m unittest test_orders test_packet test_run", "failure": "AssertionError: 'maker' != 'scenario' (a numbered point in neither covers nor not_covered went on to the maker)", "watch_first_green": "Run a slice whose scenario has numbered points, leave one out of the scenario report, and watch it go back to the scenario agent with no stop. Then give the guardian a packet with scenario_miss: yes and watch it go to the maker, and the same miss a second time stop for the person."}
wall_baseline: {"commit": "a4013a7267a3fb0f45c6e0cea3c692c96a24bf4c", "count": 57, "digest": "977032908d192ff0", "file": ".xv/slices/2026-10-30-scenario-miss.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3166, "cache_read": 25533, "cache_write": 21043, "tokens": 24213, "usd": 0.006, "turns": 3, "wall_s": 19.5, "session": "9c4ef31f-94a8-47f4-8a76-6b6776e6e436", "step": "forecaster", "at": "2026-10-30T04:37:20+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-scenario-miss/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 48, "tokens_out": 19479, "cache_read": 1379083, "cache_write": 76656, "tokens": 96183, "usd": 0.6394, "turns": 27, "wall_s": 268.6, "session": "fe6d4eca-1beb-4455-973e-0141f80d291e", "step": "scenario", "at": "2026-10-30T04:47:11+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-scenario-miss/02-scenario.out"}]
stops: [{"at": "2026-10-30T04:37:20+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-scenario-miss budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "1", "also": [], "options": [{"text": "$12 and 1.5M tokens", "settles": "The budget is $12 and 1.5M tokens: about twice the forecast, as today's slices of this size took four to six passes.", "amends": false}, {"text": "$9 and 1.1M tokens", "settles": "The budget is $9 and 1.1M tokens: the forecast plus room for one or two send-backs.", "amends": false}, {"text": "$6.10 and 800K tokens, the forecast", "settles": "The budget is $6.10 and 800K tokens, as forecast.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T04:42:42+00:00", "pick": 1, "settled": "The budget is $12 and 1.5M tokens: about twice the forecast, as today's slices of this size took four to six passes.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 1500000, "usd": 12}}}, {"at": "2026-10-30T04:49:18+00:00", "step": "scenario", "order": "unrecorded_move", "seat": "originator", "question": "The scenario agent changed or removed old tests or assertions in red files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.", "answered_by": [], "answer": null, "also": ["red_misses_scenario", "red_misses_scenario", "red_misses_scenario", "red_misses_scenario"], "budget_seen": {"tokens": 1500000, "usd": 12, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from the last three claude/sonnet and claude/opus rows: about 500k sonnet and 300k opus tokens for one pass plus one send-back; reopen risk is the main uncertainty.", "at": "2026-10-30T04:37:20+00:00"}, {"agent": "scenario", "status": "red", "summary": "Tests for scenario_miss in the packet, the guardian send-back, scenario coverage of numbered points, the send-back in the log and xv prompt, the stall, and the 'old test files that existed at the base' wording; four items not covered.", "at": "2026-10-30T04:47:11+00:00"}], "forecaster": {"at": "2026-10-30T04:37:20+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T04:47:11+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "e}: {p.stderr}{p.stdout}\")\nAssertionError: ['/home/sean/.local/share/mise/installs/python/latest/bin/python3', '/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-30-scenario-miss/bin/xv', 'step', 'maker', 's1'] failed 10: {\n  \"slice\": \"s1\",\n  \"after\": \"maker\",\n  \"stop\": {\n    \"at\": \"2026-10-30T04:49:18+00:00\",\n    \"step\": \"guardian\",\n    \"order\": \"ready_to_merge\",\n    \"seat\": \"originator\",\n    \"question\": \"The suite is green and nothing stopped. The merge is yours.\",\n    \"answered_by\": [],\n    \"answer\": null,\n    \"also\": [],\n    \"budget_seen\": {\n      \"usd\": 1,\n      \"set_by\": \"pat\"\n    }\n  },\n  \"fired\": [],\n  \"note\": \"an earlier stop is unanswered\"\n}\n\n\n----------------------------------------------------------------------\nRan 189 tests in 127.192s\n\nFAILED (failures=20, errors=2)\n", "old_red_changed": ["tests/fake_agent.py"], "red_gaps": [], "unreadable": [], "not_covered": [{"item": "2. goes to the scenario agent when the red does not cover the missed line", "why": "the scenario does not say how the watch tells that the red does not cover a line (a field in the packet, or a match against the report's covers); I will not pick one."}, {"item": "4. xv decisions counts the send-backs", "why": "the scenario does not say what the count looks like (an order name, a new column, a separate line), so there is no output to assert."}, {"item": "5. stops when meeting the miss would change the scenario", "why": "the scenario does not say how that is signalled (a packet field, a miss kind); it goes through xv slice amend and is the person's, but nothing in the packet or record marks it today."}, {"item": "1. a finding that names no scenario line and no binding decision is not a miss and stays in the packet", "why": "the scenario names no heading for the misses section, so the evidence rule cannot be tested against it, and it does not say whether the check is the packet lint or the watch."}]}}
---
# A slice that misses its own scenario goes back without a stop

## Scenario

A slice that misses its own scenario, or a decision that binds, goes back without a stop (#96).

1. The guardian's packet has `scenario_miss: yes|no` in its front matter, and a section that lists each miss: the scenario line it misses (an amendment counts as part of the scenario), or the binding decision in `.xv/picture.md` it breaks, and the evidence (a test, a run, or a diff hunk). A finding that names no scenario line and no binding decision is not a miss; it stays in the packet for the person, as now.
2. After the guardian, when `scenario_miss` is `yes` and no shape or pitch stop fires, the slice goes back without a stop: to the maker, or to the scenario agent when the red does not cover the missed line. `accept_moves` and `ready_to_merge` do not fire on that pass. Moved tests and wall recommendations are put to the person when the slice comes back with no miss.
3. After the scenario step, each numbered point of the scenario and of each amendment must appear in the scenario report's `covers` or `not_covered`. A point in neither sends the slice back to the scenario agent without a stop. A point in `not_covered` still stops for the person, as now.
4. Each send-back is recorded in the slice record as the watch's, with the misses. The next agent gets them through `xv prompt`, as it gets `settled`. `xv decisions` counts them.
5. It still stops for the person who set the work going when the budget is spent, green or not; when the same miss comes back on the next pass, as a stall (#86); or when meeting the miss would change the scenario, which goes through `xv slice amend` and is theirs.
6. The packet template (`skills/guardian/packet.md`) shows `shape_change` as `yes`, `no` or `accepted` with `accepted_by`, and `scenario_miss`.
7. The scenario-step `unrecorded_move` question names "old test files that existed at the base", not "red files", and so does the matching message in `scripts/run.py` (#102).

This changes standing orders, a check, and the guardian's and the watch's briefs, so `CHANGELOG.md` gets a line.

## May ignore

None.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T04:37:00+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T04:37:20+00:00 forecaster: done: Forecast from the last three claude/sonnet and claude/opus rows: about 500k sonnet and 300k opus tokens for one pass plus one send-back; reopen risk is the main uncertainty.
- 2026-10-30T04:37:20+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-scenario-miss budget ... --by <name>`).
- 2026-10-30T04:37:25+00:00 watch: offered 3 options for budget_not_set
- 2026-10-30T04:42:42+00:00 Sean Kennedy: set budget
- 2026-10-30T04:42:42+00:00 Sean Kennedy: answered budget_not_set: 1
- 2026-10-30T04:42:42+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-30T04:47:11+00:00 scenario: red: Tests for scenario_miss in the packet, the guardian send-back, scenario coverage of numbered points, the send-back in the log and xv prompt, the stall, and the 'old test files that existed at the base' wording; four items not covered.
- 2026-10-30T04:49:18+00:00 watch: stop (unrecorded_move) for originator: The scenario agent changed or removed old tests or assertions in red files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.

---
id: 2026-11-04-refactor-kind
title: "A slice kind for refactors, and test moves a person expects: #15"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-refactor-kind
base: 66570aa785961973ad109e9db00dfc167a823e9b
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 3.2, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-11-04-scenario-catches", "2026-10-27-slice-tests"], "note": "Guide has no turns column; sonnet covers scenario, maker, and cleaner. Each basis row reopened at least once, so one reopen is priced in the middle of the range; tokens span 283k to 674k across the basis."}, {"harness": "claude", "model": "opus", "tokens": 340000, "turns": null, "usd": 4.1, "basis": ["2026-11-04-orders-home", "2026-10-29-stop-decisions", "2026-11-04-scenario-catches", "2026-10-27-slice-tests"], "note": "Guide has no turns column; opus is the guardian only. Tokens span 205k to 392k across the basis, and usd runs about $12 per million tokens, so output-heavy guardian passes weigh more."}], "wall_s": 4500, "shape": "wide", "breadth": "Touches slice new flags, the packet, a new moved-test comparison script, and new stops in scripts/orders.py; the main gap is reopen risk from new stops, which pushed every basis row over forecast."}
budget: {"tokens": 840000, "usd": 7.3, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_refactor_kind.py"], "command": "cd tests && python3 -m unittest test_refactor_kind", "failure": "xv slice new: error: argument --kind: invalid choice: 'refactor' (choose from 'feature', 'defect', 'prototype')", "watch_first_green": "Open a refactor slice with `--expect-moves imports`, let the maker add an import to an old test, and see the slice reach the merge stop with no accept_moves question and a packet whose expected_moves matches the record; then change one assertion and see the stop come back."}
wall_baseline: {"commit": "2a177f26309fff2118e33a70091adb62e2be0241", "count": 60, "digest": "f430f63c7160b5ae", "file": ".xv/slices/2026-11-04-refactor-kind.wall.json"}
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4290, "cache_read": 26138, "cache_write": 26265, "tokens": 30559, "usd": 0.0077, "turns": 3, "wall_s": 22.6, "session": "5acfa561-d381-4d93-8b9f-3914bb06eeb2", "step": "forecaster", "at": "2026-11-05T03:13:51+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-refactor-kind/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 34, "tokens_out": 17258, "cache_read": 689115, "cache_write": 53294, "tokens": 70586, "usd": 0.4547, "turns": 19, "wall_s": 115.1, "session": "f5213141-ed65-48ea-b4a8-00d42c9e81f6", "step": "scenario", "at": "2026-11-05T03:25:48+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-refactor-kind/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 5530, "cache_read": 194185, "cache_write": 24907, "tokens": 30453, "usd": 0.1744, "turns": 10, "wall_s": 36.6, "session": "5d4e0571-b097-46b0-a2aa-cda90bb67140", "step": "scenario", "at": "2026-11-05T03:30:42+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-refactor-kind/03-scenario.out"}]
stops: [{"at": "2026-11-05T03:13:51+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-refactor-kind budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "E: 1", "also": [], "options": [{"text": "Set the budget at the forecast: 840,000 tokens and $7.30 (sonnet 500k/$3.20, opus 340k/$4.10).", "settles": "Sean set the budget at 840,000 tokens and $7.30.", "amends": false}, {"text": "Set it 30% over the forecast: 1,100,000 tokens and $9.50.", "settles": "Sean set the budget at 1,100,000 tokens and $9.50.", "amends": false}, {"text": "Set a different budget.", "settles": "Sean set the budget he named.", "amends": false}], "recommended": 1, "answered_at": "2026-11-05T03:23:47+00:00", "pick": 1, "settled": "Sean set the budget at 840,000 tokens and $7.30.", "new_info": "none", "cause": "decision: the budget is set by a person from the forecast", "budget_change": {"from": null, "to": {"tokens": 840000, "usd": 7.3}}}, {"at": "2026-11-05T03:25:49+00:00", "step": "scenario", "order": "red_misses_scenario", "seat": "originator", "question": "The scenario agent did not cover 7 (part): expected moves listed on one line in the packet: the packet is written by the guardian agent and the scenario fixes no line format, so a test would invent one; the guardian's brief or a packet lint is where it would be checked", "answered_by": ["Sean Kennedy"], "answer": "E: 1", "also": [], "options": [{"text": "Amend: the packet's front matter has `expected_moves: <n>`, the count of expected moves in the record, and the line under it names them. The packet check refuses a packet whose count differs from the record. Back to the scenario agent, so a test can check it.", "settles": "Sean amended the slice: the packet's front matter has expected_moves with the record's count, and the packet check refuses a packet whose count differs. Next is scenario.", "amends": true}, {"text": "Accept the gap: the guardian brief says to list expected moves on one line, with no test. Go on to the maker.", "settles": "Sean accepted point 7's one-line packet listing as not covered: it lives in the guardian's brief, with no test. Next is maker.", "amends": false}, {"text": "Talk it through first.", "settles": "The slice waits at red_misses_scenario.", "amends": false}], "recommended": 1, "answered_at": "2026-11-05T03:29:59+00:00", "sent_back": true, "pick": 1, "settled": "Sean amended the slice (point 11): the packet's front matter has expected_moves with the record's count, and the check after the guardian lists a packet problem when it is missing or differs. Next is scenario.", "new_info": "how point 7's packet line is checked: an expected_moves count in the front matter", "cause": "decision: the scenario did not say how the packet line is checked"}, {"at": "2026-11-05T03:30:43+00:00", "step": "scenario", "order": "unrecorded_move", "seat": "originator", "question": "The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 840000, "usd": 7.3, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~500k tokens and claude/opus ~340k tokens for a wide slice that reopened in all four basis rows; turns have no history column.", "at": "2026-11-05T03:13:51+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red tests for the refactor kind, --expect-moves and --rename: 16 fail because slice new refuses the new kind and flags.", "at": "2026-11-05T03:25:48+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for the refactor kind, --expect-moves, --rename and the packet's expected_moves count (point 11): 22 of 23 fail because slice new refuses the kind.", "at": "2026-11-05T03:30:42+00:00"}], "forecaster": {"at": "2026-11-05T03:13:51+00:00", "wrote": []}, "scenario": {"at": "2026-11-05T03:30:42+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": " '/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-04-refactor-kind/bin/xv', 'slice', 'new', 's1', '--by', 'pat', '--kind', 'refactor', '--scenario', 'Users see no change. Restructure StoreTest in tests/test_store.py.'] failed 2: usage: xv slice new [-h] --by BY [--title TITLE]\n                    [--kind {feature,defect,prototype}] [--scenario SCENARIO]\n                    [--scenario-file SCENARIO_FILE] [--ignore IGNORE]\n                    [--recording RECORDING] [--branch BRANCH] [--base BASE]\n                    [--axis AXIS]\n                    id\nxv slice new: error: argument --kind: invalid choice: 'refactor' (choose from 'feature', 'defect', 'prototype')\n\n\n----------------------------------------------------------------------\nRan 23 tests in 1.078s\n\nFAILED (failures=22)\n", "old_red_changed": ["tests/fake_agent.py"], "red_gaps": [], "unreadable": [], "not_covered": [], "missed_points": ["11. The packet's front matter has `expected_moves: <n>`, the number of expected moves the record holds, and the packet names each of them on one line. When the record holds none, the field is `0`. After the guardian, the check that fills `packet_problems` in `scripts/run.py` lists a problem when `expected_moves` is missing, is not a whole number, or differs from the record's count."]}}
old_tests_forced: []
may_not_files: []
---
# A slice kind for refactors, and test moves a person expects: #15

## Scenario

# A slice kind for refactors, and test moves a person expects: #15

When this is done:

1. `xv slice new --kind refactor` opens a refactor slice. Its scenario says that users see no change, and it names what to restructure.
2. The scenario step writes no new red. It checks that the suite is green at the start, and it records that as the slice's oracle.
3. The maker may rename and restructure what the scenario names. The "no refactor, no rename" line in its brief does not apply to those parts.
4. A latent bug found along the way is fixed only through `xv slice amend`.
5. `xv slice new --expect-moves <kinds>` names the kinds of test change the person expects: `imports`, `renames`, or both.
6. After each step, a script compares each moved test file before and after. The agent does not decide whether a move is expected.
7. Expected moves are recorded and listed on one line in the packet, with no `accept_moves` stop for them. Any other move still stops for the person.
8. `renames`: a test file moves to a new path (for example `test_foo.py` to `test_bar.py`). Its content changes only in the names the slice renames, in import lines, and in whitespace. Every assertion is otherwise unchanged. `imports`: the same path, and only import or require lines and whitespace change. These two are the only kinds for now.
9. The person gives the names a slice renames when it opens, with `xv slice new --rename Foo=Bar`, one flag per pair. The script reads those pairs to check a `renames` move.
10. Each new stop is decided in `scripts/orders.py`.

### Amended 2026-11-04 by Sean Kennedy

At the scenario agent's stop, Sean chose how point 7's packet line is checked. This point adds to what the slice must do. It loosens no may-not line and no binding decision.

11. The packet's front matter has `expected_moves: <n>`, the number of expected moves the record holds, and the packet names each of them on one line. When the record holds none, the field is `0`. After the guardian, the check that fills `packet_problems` in `scripts/run.py` lists a problem when `expected_moves` is missing, is not a whole number, or differs from the record's count.

## May ignore

expected-move kinds other than imports and renames; #114, the retro seeing rework, left for slice H; old slice records, which keep their shape.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T03:13:28+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T03:13:51+00:00 forecaster: done: Forecast claude/sonnet ~500k tokens and claude/opus ~340k tokens for a wide slice that reopened in all four basis rows; turns have no history column.
- 2026-11-05T03:13:51+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-refactor-kind budget ... --by <name>`).
- 2026-11-05T03:14:03+00:00 watch: offered 3 options for budget_not_set
- 2026-11-05T03:23:47+00:00 Sean Kennedy: set budget
- 2026-11-05T03:23:47+00:00 Sean Kennedy: answered budget_not_set: E: 1
- 2026-11-05T03:23:47+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-05T03:25:48+00:00 scenario: red: Red tests for the refactor kind, --expect-moves and --rename: 16 fail because slice new refuses the new kind and flags.
- 2026-11-05T03:25:49+00:00 watch: stop (red_misses_scenario) for originator: The scenario agent did not cover 7 (part): expected moves listed on one line in the packet: the packet is written by the guardian agent and the scenario fixes no line format, so a test would invent one; the guardian's brief or a packet lint is where it would be checked
- 2026-11-05T03:26:07+00:00 watch: offered 3 options for red_misses_scenario
- 2026-11-05T03:29:46+00:00 Sean Kennedy: amended the scenario
- 2026-11-05T03:29:59+00:00 Sean Kennedy: answered red_misses_scenario: E: 1
- 2026-11-05T03:29:59+00:00 watch: scribe: wrote settled, new_info, cause for red_misses_scenario as the scribe of Sean Kennedy
- 2026-11-05T03:30:42+00:00 scenario: red: Red for the refactor kind, --expect-moves, --rename and the packet's expected_moves count (point 11): 22 of 23 fail because slice new refuses the kind.
- 2026-11-05T03:30:43+00:00 watch: stop (unrecorded_move) for originator: The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py. Revert them, or record why the scenario forces it.

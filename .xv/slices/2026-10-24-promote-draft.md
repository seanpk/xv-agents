---
id: 2026-10-24-promote-draft
title: "xv promote draft: whole-word titles, any stack, one date, attribution"
kind: defect
status: working
set_by: Sean Kennedy
created: 2026-10-24
branch: xv/2026-10-24-promote-draft
base: 948efd1159971b567b82e3bc8045c8c6542e5300
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/sonnet"}, {"harness": "claude", "model": "opus", "tokens": null, "turns": null, "usd": null, "basis": [], "note": "no history for claude/opus"}], "wall_s": null, "shape": "narrow", "breadth": "Expect changes confined to the promote draft path: title cut at a word boundary, default Applies to: any, one date in the draft file name, and the attribution line at the end of the body. post and tally are out of scope."}
budget: {"tokens": 1500000, "usd": 5, "turns": 60, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_promote_draft.py"], "command": "cd tests && python3 -m unittest test_promote_draft", "failure": "AssertionError: 2 != 1 : 2026-10-24-2026-10-20-stop-before-a.md", "watch_first_green": null}
wall_baseline: {"commit": "45db3228429a01c15748a64ed989d6cd2db4434f", "count": 25, "digest": "cb217e3dbe8ec846", "file": ".xv/slices/2026-10-24-promote-draft.wall.json"}
moved_tests: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 942, "cache_read": 23314, "cache_write": 6196, "tokens": 30456, "usd": 0.0019, "turns": 3, "wall_s": 5.5, "session": "72b71b0d-7437-49c7-a412-46cd7670ac28", "step": "forecaster", "at": "2026-10-25T03:27:07+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-promote-draft/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 14, "tokens_out": 2254, "cache_read": 137987, "cache_write": 17439, "tokens": 157694, "usd": 0.1061, "turns": 8, "wall_s": 21.3, "session": "0bafa8ff-e69b-437d-a609-380e9b4dd092", "step": "scenario", "at": "2026-10-25T03:34:22+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-promote-draft/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 5184, "cache_read": 177362, "cache_write": 22749, "tokens": 205311, "usd": 0.1606, "turns": 9, "wall_s": 35.6, "session": "db2e769e-97ae-4435-96c2-f2d7192f392b", "step": "scenario", "at": "2026-10-25T03:43:56+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-24-promote-draft/03-scenario.out"}]
stops: [{"at": "2026-10-25T03:27:07+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-promote-draft budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "you can set your suggested estimate", "also": [], "answered_at": "2026-10-25T03:33:47+00:00"}, {"at": "2026-10-25T03:34:22+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (stopped): Scenario does not say what the attribution line is, who supplies it, or which drafts carry it; no test written.", "answered_by": ["Sean Kennedy"], "answer": "2 ok (the pick: a promote.attribution setting, empty by default, set to the Claude line in this repo)", "also": [], "answered_at": "2026-10-25T03:43:20+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "No guide history for claude/sonnet or claude/opus; numbers left null, shape forecast narrow.", "at": "2026-10-25T03:27:07+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Scenario does not say what the attribution line is, who supplies it, or which drafts carry it; no test written.", "at": "2026-10-25T03:34:22+00:00"}, {"agent": "scenario", "status": "red", "summary": "Four failing tests for promote draft: whole-word title, Applies to any, one date in file name, configured attribution line at the end.", "at": "2026-10-25T03:43:56+00:00"}], "forecaster": {"at": "2026-10-25T03:27:07+00:00", "wrote": []}, "scenario": {"at": "2026-10-25T03:43:56+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "aude on behalf of Sean\n : {}\n\n======================================================================\nFAIL: test_the_draft_file_name_carries_one_date (test_promote_draft.PromoteDraftTest.test_the_draft_file_name_carries_one_date)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-24-promote-draft/tests/test_promote_draft.py\", line 60, in test_the_draft_file_name_carries_one_date\n    self.assertEqual(len(re.findall(DATE, name)), 1, name)\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 2 != 1 : 2026-10-24-2026-10-20-stop-before-a.md\n\n----------------------------------------------------------------------\nRan 6 tests in 0.049s\n\nFAILED (failures=4)\n"}}
---
# xv promote draft: whole-word titles, any stack, one date, attribution

## Scenario

`xv promote draft` gives a title cut at a word boundary, "Applies to: any" when no `--applies-to` is passed, a draft file name with one date, and a body that ends with the assistant's attribution line. (seanpk/xv-agents#13)

Settled at the scenario stop, 2026-10-24, Sean: a new setting `promote.attribution` in `.xv/config.yml`, empty by default. When it is set, every draft body ends with that line. When it is empty, no line is added. This repo sets it to `🤖 Claude on behalf of Sean`.

## May ignore

the post and tally commands

## Recording

None. A feature starts from words.

## Log
- 2026-10-25T03:26:53+00:00 watch: slice opened by Sean Kennedy
- 2026-10-25T03:27:07+00:00 forecaster: done: No guide history for claude/sonnet or claude/opus; numbers left null, shape forecast narrow.
- 2026-10-25T03:27:07+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-24-promote-draft budget ... --by <name>`).
- 2026-10-25T03:33:47+00:00 Sean Kennedy: set budget
- 2026-10-25T03:33:47+00:00 Sean Kennedy: answered budget_not_set: you can set your suggested estimate
- 2026-10-25T03:34:22+00:00 scenario: stopped: Scenario does not say what the attribution line is, who supplies it, or which drafts carry it; no test written.
- 2026-10-25T03:34:22+00:00 watch: stop (scenario_stopped) for originator: The scenario stopped (stopped): Scenario does not say what the attribution line is, who supplies it, or which drafts carry it; no test written.
- 2026-10-25T03:43:20+00:00 Sean Kennedy: answered scenario_stopped: 2 ok (the pick: a promote.attribution setting, empty by default, set to the Claude line in this repo)
- 2026-10-25T03:43:56+00:00 scenario: red: Four failing tests for promote draft: whole-word title, Applies to any, one date in file name, configured attribution line at the end.

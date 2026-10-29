---
id: 2026-10-29-stop-decisions
title: "A stop keeps the decision, not only the answer"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-stop-decisions
base: 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d
next: guardian
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 1.8, "basis": ["2026-10-27-prototype-budgets", "2026-10-27-slice-tests", "2026-10-27-init-no-try"]}, {"harness": "claude", "model": "opus", "tokens": 210000, "turns": null, "usd": 2.5, "basis": ["2026-10-27-prototype-budgets", "2026-10-27-slice-tests", "2026-10-27-init-no-try"]}], "wall_s": 2500, "shape": "wide", "breadth": "Stop record fields (offer, answer, decisions report), the watch brief, the scenario brief, run.py next-step handling and the originator answer check; scenario, maker and cleaner on sonnet, guardian on opus, plus CHANGELOG lines."}
budget: {"tokens": 1250000, "usd": 10, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_record.py", "tests/test_answer_in_prompt.py", "tests/test_run.py"], "command": "cd tests && python3 -m unittest -q test_record test_answer_in_prompt test_run", "failure": "AssertionError: Regex didn't match: 'taken\\D*0' not found in 'against: 1 stops, pick taken 1, new_info none 1, causes: decision 1'", "watch_first_green": null}
wall_baseline: {"commit": "30761c76aaa9a0be2d8eb05fafabacfbd46a0e09", "count": 47, "digest": "51482e227d3b2496", "file": ".xv/slices/2026-10-29-stop-decisions.wall.json"}
moved_tests: []
slice_only: []
suite: green
cleaner_commit: null
packet: .xv/slices/2026-10-29-stop-decisions.packet.md
shape_change: yes
pitch_contradiction: no
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4301, "cache_read": 23564, "cache_write": 19364, "tokens": 23669, "usd": 0.0063, "turns": 3, "wall_s": 21.6, "session": "77de5837-6ba4-409a-b784-fee6333702d6", "step": "forecaster", "at": "2026-10-29T17:53:54+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 30, "tokens_out": 14392, "cache_read": 716455, "cache_write": 62409, "tokens": 76831, "usd": 0.4653, "turns": 28, "wall_s": 117.8, "session": "eac5408b-3058-4a85-92e2-def21c33bb5a", "step": "scenario", "at": "2026-10-29T18:35:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 10, "tokens_out": 1947, "cache_read": 93095, "cache_write": 14943, "tokens": 16900, "usd": 0.0886, "turns": 6, "wall_s": 14.8, "session": "1953227f-83c6-4977-bd37-34c59dd0c862", "step": "scenario", "at": "2026-10-29T18:46:43+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/03-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 38, "tokens_out": 13360, "cache_read": 831001, "cache_write": 62230, "tokens": 75628, "usd": 0.4657, "turns": 34, "wall_s": 223.9, "session": "d67a501a-fe36-4b3e-a2f0-f48b72939c7e", "step": "maker", "at": "2026-10-29T18:51:04+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/04-maker.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 16, "tokens_out": 1710, "cache_read": 178967, "cache_write": 19338, "tokens": 21064, "usd": 0.1124, "turns": 10, "wall_s": 105.8, "session": "117b3e16-4271-42fe-a5df-cac97dc64255", "step": "cleaner", "at": "2026-10-29T18:54:19+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/05-cleaner.out"}, {"harness": "claude", "model": "opus", "model_id": "claude-opus-5-5", "tokens_in": 34, "tokens_out": 14575, "cache_read": 750664, "cache_write": 65509, "tokens": 80118, "usd": 0.9658, "turns": 20, "wall_s": 322.9, "session": "411d126c-f60e-4f6d-ac7c-fe7f2cf5b413", "step": "guardian", "at": "2026-10-29T19:01:11+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/06-guardian.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 24, "tokens_out": 7600, "cache_read": 372401, "cache_write": 35608, "tokens": 43232, "usd": 0.2557, "turns": 14, "wall_s": 90.5, "session": "69870135-8e59-4d87-8c39-477624b72b77", "step": "scenario", "at": "2026-10-29T19:11:18+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/07-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 30, "tokens_out": 5323, "cache_read": 443372, "cache_write": 27246, "tokens": 32599, "usd": 0.2066, "turns": 22, "wall_s": 351.1, "session": "f54ab16e-5826-43b3-9519-abcff203b090", "step": "maker", "at": "2026-10-29T19:17:40+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/08-maker.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 20, "tokens_out": 2434, "cache_read": 304099, "cache_write": 29139, "tokens": 31593, "usd": 0.1713, "turns": 12, "wall_s": 386.4, "session": "80d687b1-b891-4ac2-b672-f95944b58f53", "step": "cleaner", "at": "2026-10-29T19:25:37+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/09-cleaner.out"}]
stops: [{"at": "2026-10-29T17:53:54+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-stop-decisions budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "do $10 and 1.25M", "also": [], "answered_at": "2026-10-29T18:33:20+00:00"}, {"at": "2026-10-29T18:46:24+00:00", "order": "red_check", "seat": "originator", "question": "The red covers all four issues, but no test uses xv decisions --since <date>, which the scenario names. Go on to the maker, send it back for one --since test, or drop --since?", "answered_by": ["Sean Kennedy"], "answer": "won't we spend more by waiting for the guardian to find the need for it? I lean towards 2, tell me why not", "answered_at": "2026-10-29T18:46:24+00:00"}, {"at": "2026-10-29T19:01:11+00:00", "step": "guardian", "order": "shape_or_pitch", "seat": "two_people", "question": "The guardian's packet says shape_change. Two people decide from the packet. This repo runs solo: one person answers. Write down what you weighed; the decision record keeps it.", "answered_by": ["Sean Kennedy"], "answer": "1: 1\n2: 1", "also": [], "solo": true, "answered_at": "2026-10-29T19:09:45+00:00"}]
decisions: [{"date": "2026-10-29", "who": ["Sean Kennedy"], "decision": "1: 1\n2: 1", "record": ".xv/decisions/2026-10-29-2026-10-29-stop-decisions.md"}]
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Sonnet ~350k tokens, opus ~210k; wide shape across record, briefs and run.py; basis includes prior reopen rounds", "at": "2026-10-29T17:53:54+00:00"}, {"agent": "scenario", "status": "red", "summary": "Tests for offer/answer fields, xv decisions, settled in the prompt, brief changes and next staying on a stopped step; 18 fail, the #62 guard passes", "at": "2026-10-29T18:35:21+00:00"}, {"agent": "scenario", "status": "red", "summary": "Added one --since test for xv decisions; the red now covers all four issues and the --since option", "at": "2026-10-29T18:46:43+00:00"}, {"agent": "maker", "status": "green", "summary": "Added xv record offer and the new answer fields, xv decisions, settled in the prompt, brief and CHANGELOG changes, and next staying on a stopped step", "at": "2026-10-29T18:51:04+00:00"}, {"agent": "cleaner", "status": "done", "summary": "Nothing to fix; suite green (355 OK); no commit", "shape_proposals": [], "candidate_standards": [], "applied": [], "at": "2026-10-29T18:54:19+00:00"}, {"agent": "guardian", "status": "done", "summary": "New module scripts/decisions and the xv decisions command change the shape (narrow); no pitch contradiction; no moved tests; flags next staying on decision stops, the 'pick taken' meaning and the CHANGELOG decision line", "picture_change": "yes", "at": "2026-10-29T19:01:11+00:00"}, {"agent": "scenario", "status": "red", "summary": "Added tests for the three amendments: pick taken only when it equals recommended, xv decisions reads records like xv retro, --resume needs --next; 6 fail", "at": "2026-10-29T19:11:18+00:00"}, {"agent": "maker", "status": "green", "summary": "xv decisions counts a pick as taken only when it equals the recommendation and reads records via retro's records(); --resume needs --next; watch brief says so", "at": "2026-10-29T19:17:40+00:00"}, {"agent": "cleaner", "status": "done", "summary": "Nothing to fix; suite green (362 OK on re-runs; one earlier run exited 1 and could not be reproduced); no commit", "shape_proposals": [], "candidate_standards": [], "applied": [], "at": "2026-10-29T19:25:37+00:00"}], "forecaster": {"at": "2026-10-29T17:53:54+00:00", "wrote": []}, "scenario": {"at": "2026-10-29T19:11:18+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 'cleaner' != 'maker'\n- cleaner\n+ maker\n\n\n======================================================================\nFAIL: test_a_step_with_no_report_keeps_next_on_that_step (test_run.WatchLoopTest.test_a_step_with_no_report_keeps_next_on_that_step)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/tmp/xv-red-9phf2dbf/tests/test_run.py\", line 277, in test_a_step_with_no_report_keeps_next_on_that_step\n    self.assertEqual(self.record()[\"next\"], \"scenario\")\n    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: 'maker' != 'scenario'\n- maker\n+ scenario\n\n\n----------------------------------------------------------------------\nRan 103 tests in 31.163s\n\nFAILED (failures=25)\n", "old_red_changed": []}, "maker": {"at": "2026-10-29T19:17:40+00:00", "protected_changed": [], "suite": "green", "suite_output": "onal/xv-agents/.xv/worktrees/2026-10-29-stop-decisions/tests/test_worktree_setup.py:18: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-1kp60cpo/repo/.xv/config.yml' mode='r' encoding='utf-8'>\n  text = open(cfg).read().replace(\"worktrees: .xv/worktrees\\n\", block)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-29-stop-decisions/tests/test_worktree_setup.py:19: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-1kp60cpo/repo/.xv/config.yml' mode='w' encoding='utf-8'>\n  open(cfg, \"w\").write(text)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n----------------------------------------------------------------------\nRan 362 tests in 90.206s\n\nOK\n", "failing_step": "", "failing": [], "failing_history": [[], []], "diff_lines": 449, "diff_history": [304, 449], "wall": {"slice": "2026-10-29-stop-decisions", "baseline": "30761c76aaa9a0be2d8eb05fafabacfbd46a0e09", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}}, "cleaner": {"at": "2026-10-29T19:25:37+00:00", "protected_changed": [], "suite": "green", "suite_output": "onal/xv-agents/.xv/worktrees/2026-10-29-stop-decisions/tests/test_worktree_setup.py:18: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-o3ocr5oa/repo/.xv/config.yml' mode='r' encoding='utf-8'>\n  text = open(cfg).read().replace(\"worktrees: .xv/worktrees\\n\", block)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-29-stop-decisions/tests/test_worktree_setup.py:19: ResourceWarning: unclosed file <_io.TextIOWrapper name='/tmp/xv-test-o3ocr5oa/repo/.xv/config.yml' mode='w' encoding='utf-8'>\n  open(cfg, \"w\").write(text)\nResourceWarning: Enable tracemalloc to get the object allocation traceback\n----------------------------------------------------------------------\nRan 362 tests in 90.608s\n\nOK\n", "failing_step": "", "failing": [], "failing_history": [[], []], "diff_lines": 449, "diff_history": [365, 449], "wall": {"slice": "2026-10-29-stop-decisions", "baseline": "30761c76aaa9a0be2d8eb05fafabacfbd46a0e09", "changed": [], "deleted": [], "added": [], "detail": {}, "fewer_assertions": [], "recorded": [], "unrecorded": [], "ok": true}, "standards_touched": false, "committed": false}, "guardian": {"at": "2026-10-29T19:01:11+00:00", "wrote": [], "packet": true, "packet_problems": [], "dropped_findings": 0, "picture_change": "yes", "shape_breadth": "narrow"}}
pre_maker_commit: d9fffc4982aa4e42daaa33e257d66ce283cc1b08
---
# A stop keeps the decision, not only the answer

## Scenario

A stop keeps the decision, not only the answer. Four issues in one slice: #80, #62, #42, #73.

## 1. The offer and the answer (#80)

When the watch puts a stop to a person, it runs:

`xv record offer <id> --option "<text>" --settles "<text>" [--amends] ... --recommend <n>`

`--settles` and `--amends` belong to the `--option` just before them. `--settles` is the `settled` text the watch would record if that option is picked; `--amends` marks that option as one that changes what the slice must do. The options are numbered from 1 in the order given. `xv record offer` refuses an option with no `--settles`, and a `--settles` or `--amends` with no `--option` before it. The open stop then holds:

- `options`: the choices put to the person, one line each, each with the `settled` text the watch would record and whether it amends the scenario.
- `recommended`: the index of the watch's pick, or null.

`xv record answer` takes `--pick <n|other>`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle <id>[,<id>]`, and the answered stop holds:

- `answer`: the person's words, verbatim, as now.
- `pick`: the index chosen, or `other`.
- `settled`: what is now true, in sentences a teammate or the next agent can act on without the chat. With `--pick <n>` and no `--settled`, it is the offered option's text.
- `new_info`: what the person brought that no agent had, or `none`.
- `cause`: `decision`, `environment`, `tool`, `agent` or `watch`, with a free line. `agent` names the brief that missed it; `watch` is the watch's own slip.
- `bundle`: the other stops the same reply answered.
- `budget_change`: old to new, when the answer moved the budget.
- `why`: the person's reason, when they gave one. Optional.

`settled`, `new_info` and `cause` are written by the watch as the person's scribe, and the record says so. `--settled` is required when the answer sends work back or the pick is `other`. There is no field for who recommended.

`xv prompt` gives the next agent `settled`, not the raw answer.

`xv decisions [--since <date>]` reads every slice record and prints, per order: how many stops, how often the pick was taken, how often `new_info` was `none`, and the causes.

The watch's brief uses `offer`, and stops writing "Settled at" paragraphs into the scenario. A decision that changes what the slice must do goes through `xv slice amend`, and `settled` names the amendment. Every other decision lives only in `settled`. This changes a brief, so `CHANGELOG.md` gets a line.

## 2. Who answers a stop for the person who set the work going (#62)

A stop seated `originator` may be answered by a name that is not the record's `set_by`, so someone can pick up someone else's work. The answer is accepted, and `answered_by` records the name.

## 3. The red in the form the answer names (#42)

When the person's answer (now `settled`) names the form of the red, such as a lint rule or a script, the scenario agent writes that form or stops with a question. It does not swap in a test. A red that is not a test file still needs a red command the agent watches fail, as now. This changes the scenario brief, so `CHANGELOG.md` gets a line.

## 4. `next` stays on a step that stopped (#73)

When a step stops or ends with no report, the record's `next` stays on that step. It does not move to the following step, so a later step cannot start on missing work. Today only the red-command case does this (`scripts/run.py:386`).

### Amended 2026-10-29 by Sean Kennedy

At the guardian's shape stop, Sean accepted the shape change (the new `scripts/decisions.py` and the `xv decisions` command) and asked for three changes:

1. `xv decisions` counts a pick as taken only when it equals `recommended`. A pick against the watch's recommendation is not counted as taken.
2. `xv decisions` reads the slice records through the reader `xv retro` uses (`records()` in `scripts/retro.py`), so it skips the same files, and a record it cannot read does not stop the report.
3. `next` stays on the step after every stop, as now. `xv record answer --resume` refuses an answer with no `--next`, so every answer says where the slice goes. The watch brief says so.

## May ignore

The watch answering stops by itself, and who decides which. Filling the new fields into old slice records: xv decisions counts only stops recorded after this change. #64, a red that covers only part of the scenario.

## Recording

None. A feature starts from words.

## Log
- 2026-10-29T17:53:29+00:00 watch: slice opened by Sean Kennedy
- 2026-10-29T17:53:54+00:00 forecaster: done: Sonnet ~350k tokens, opus ~210k; wide shape across record, briefs and run.py; basis includes prior reopen rounds
- 2026-10-29T17:53:54+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-stop-decisions budget ... --by <name>`).
- 2026-10-29T18:33:20+00:00 Sean Kennedy: set budget
- 2026-10-29T18:33:20+00:00 Sean Kennedy: answered budget_not_set: do $10 and 1.25M
- 2026-10-29T18:35:21+00:00 scenario: red: Tests for offer/answer fields, xv decisions, settled in the prompt, brief changes and next staying on a stopped step; 18 fail, the #62 guard passes
- 2026-10-29T18:46:24+00:00 watch: stop (red_check) for originator: The red covers all four issues, but no test uses xv decisions --since <date>, which the scenario names. Go on to the maker, send it back for one --since test, or drop --since?
- 2026-10-29T18:46:24+00:00 Sean Kennedy: answered red_check: won't we spend more by waiting for the guardian to find the need for it? I lean towards 2, tell me why not
- 2026-10-29T18:46:43+00:00 scenario: red: Added one --since test for xv decisions; the red now covers all four issues and the --since option
- 2026-10-29T18:51:04+00:00 maker: green: Added xv record offer and the new answer fields, xv decisions, settled in the prompt, brief and CHANGELOG changes, and next staying on a stopped step
- 2026-10-29T18:54:19+00:00 cleaner: done: Nothing to fix; suite green (355 OK); no commit
- 2026-10-29T19:01:11+00:00 guardian: done: New module scripts/decisions and the xv decisions command change the shape (narrow); no pitch contradiction; no moved tests; flags next staying on decision stops, the 'pick taken' meaning and the CHANGELOG decision line
- 2026-10-29T19:01:11+00:00 watch: stop (shape_or_pitch) for two_people: The guardian's packet says shape_change. Two people decide from the packet. This repo runs solo: one person answers. Write down what you weighed; the decision record keeps it.
- 2026-10-29T19:09:45+00:00 Sean Kennedy: answered shape_or_pitch: 1: 1 2: 1
- 2026-10-29T19:09:45+00:00 Sean Kennedy: amended the scenario
- 2026-10-29T19:11:18+00:00 scenario: red: Added tests for the three amendments: pick taken only when it equals recommended, xv decisions reads records like xv retro, --resume needs --next; 6 fail
- 2026-10-29T19:17:40+00:00 maker: green: xv decisions counts a pick as taken only when it equals the recommendation and reads records via retro's records(); --resume needs --next; watch brief says so
- 2026-10-29T19:25:37+00:00 cleaner: done: Nothing to fix; suite green (362 OK on re-runs; one earlier run exited 1 and could not be reproduced); no commit

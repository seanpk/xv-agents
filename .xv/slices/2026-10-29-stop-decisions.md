---
id: 2026-10-29-stop-decisions
title: "A stop keeps the decision, not only the answer"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-stop-decisions
base: 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 350000, "turns": null, "usd": 1.8, "basis": ["2026-10-27-prototype-budgets", "2026-10-27-slice-tests", "2026-10-27-init-no-try"]}, {"harness": "claude", "model": "opus", "tokens": 210000, "turns": null, "usd": 2.5, "basis": ["2026-10-27-prototype-budgets", "2026-10-27-slice-tests", "2026-10-27-init-no-try"]}], "wall_s": 2500, "shape": "wide", "breadth": "Stop record fields (offer, answer, decisions report), the watch brief, the scenario brief, run.py next-step handling and the originator answer check; scenario, maker and cleaner on sonnet, guardian on opus, plus CHANGELOG lines."}
budget: {"tokens": 1250000, "usd": 10, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_record.py", "tests/test_run.py", "tests/test_answer_in_prompt.py", "tests/fake_agent.py"], "command": "cd tests && python3 -m unittest test_record test_run test_answer_in_prompt", "failure": "FAILED (failures=18): xv record offer does not exist; a stopped step moves next on", "watch_first_green": "Run `xv record offer` with two options (one --amends), answer with --pick 2, and read the stop: options, recommended, pick, settled. Then run `xv decisions` and check the counts per order. Then `xv prompt maker <id>` and confirm it shows settled, not the raw words."}
wall_baseline: {"commit": "cfb18d276090f18fab7c14a2584899d051ccb68b", "count": 47, "digest": "2f5d20701aaba79e", "file": ".xv/slices/2026-10-29-stop-decisions.wall.json"}
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4301, "cache_read": 23564, "cache_write": 19364, "tokens": 23669, "usd": 0.0063, "turns": 3, "wall_s": 21.6, "session": "77de5837-6ba4-409a-b784-fee6333702d6", "step": "forecaster", "at": "2026-10-29T17:53:54+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 30, "tokens_out": 14392, "cache_read": 716455, "cache_write": 62409, "tokens": 76831, "usd": 0.4653, "turns": 28, "wall_s": 117.8, "session": "eac5408b-3058-4a85-92e2-def21c33bb5a", "step": "scenario", "at": "2026-10-29T18:35:21+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-29-stop-decisions/02-scenario.out"}]
stops: [{"at": "2026-10-29T17:53:54+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-29-stop-decisions budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "do $10 and 1.25M", "also": [], "answered_at": "2026-10-29T18:33:20+00:00"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Sonnet ~350k tokens, opus ~210k; wide shape across record, briefs and run.py; basis includes prior reopen rounds", "at": "2026-10-29T17:53:54+00:00"}, {"agent": "scenario", "status": "red", "summary": "Tests for offer/answer fields, xv decisions, settled in the prompt, brief changes and next staying on a stopped step; 18 fail, the #62 guard passes", "at": "2026-10-29T18:35:21+00:00"}], "forecaster": {"at": "2026-10-29T17:53:54+00:00", "wrote": []}, "scenario": {"at": "2026-10-29T18:35:21+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "p one.\\n- Do an agent\\'s work itself: write the red, make it work, clean it, or review it.\\n- Answer a stop on a person\\'s behalf, or read silence as an answer.\\n\\n## Writes to the slice record\\n\\nThrough `xv step` and `xv record`: each step\\'s report, the actual spend, each stop raised and the seat it went to, each answer and who gave it, and the decision record when two people decided.\\n\\n## Stop and report when\\n\\n- A standing order fires.\\n- A script fails, or a step cannot run (a missing CLI, a missing file). Say what failed and stop; do not work around it.\\n- The person asks for anything on the may-not list. Say which line it is and what the person can do instead.\\n'\n\n----------------------------------------------------------------------\nRan 95 tests in 29.865s\n\nFAILED (failures=18)\n", "old_red_changed": []}}
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

---
id: 2026-10-29-stop-decisions
title: "A stop keeps the decision, not only the answer"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-29-stop-decisions
base: 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: []
stops: []
decisions: []
prototypes: []
overrides: []
checks: {}
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

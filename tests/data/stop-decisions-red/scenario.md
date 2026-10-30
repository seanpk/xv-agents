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

### Amended 2026-10-29 by Sean Kennedy

At the guardian's second shape stop, Sean accepted the shape (the edge `decisions → retro` is the reuse he asked for) and asked for five fixes from the packet:

1. `--pick <n>` fills `settled` from the offered option before `--next` checks for it, so `--pick 1 --next maker --resume` is accepted when option 1 has its `--settles` text. `--next` with no pick and no `--settled` is still refused.
2. The README's `xv record answer` examples (`README.md:189` and `README.md:295`) give `--next`, so they are not refused.
3. The `CHANGELOG.md` line names the rule that `--resume` needs `--next`.
4. A stop raised by `xv step` keeps what the budget was when it was raised, as `xv record stop` and `xv record offer` do, so `budget_change` is recorded when the answer moves the budget.
5. The log line names only the scribe fields the watch wrote (`settled`, `new_info`, `cause`), not all three when one was given.

### Amended 2026-10-29 by Sean Kennedy

At the guardian's third shape stop, Sean accepted the moved test in `tests/test_record.py` (forced by the second amendment's first fix) and asked for four fixes:

1. `--settled` is required only when `--next` sends the work back, to the step that stopped or an earlier one, or when the pick is `other`. An answer whose `--next` moves the slice forward (for example `--next close` after `ready_to_merge`) needs no `--settled`. This replaces the second amendment's reading where every `--next` needs `settled`.
2. The README's merge example (`README.md:189`) answers with `--next close`, not `--next maker`. Both README answer examples run without being refused.
3. The watch brief shows `--next` as required on `xv record answer --resume`, not in brackets, and says when `--settled` is required, as in fix 1.
4. `xv record offer` keeps the budget amount the stop already saved (`budget_seen`), so a budget moved between the stop and the offer still gives `budget_change`.

### Amended 2026-10-29 by Sean Kennedy

At the guardian's fourth shape stop, Sean accepted the two moved tests in `tests/test_record.py` (forced by the fourth amendment's first fix) and asked for three fixes:

1. The decision record keeps `settled`. When an answer gives `settled`, `.xv/decisions/*.md` and the record's `decisions` list carry it, with the person's words kept as well.
2. "The step that stopped" is the step saved on the stop. `xv record answer` compares `--next` with the stop's `step`, and falls back to the record's `next` only when the stop has no step.
3. `CHANGELOG.md` names when `--settled` is required (when `--next` sends the work back, or the pick is `other`), and the README's general answer line (`README.md:295`) says so too.

## May ignore

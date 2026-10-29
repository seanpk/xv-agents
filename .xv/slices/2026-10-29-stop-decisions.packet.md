---
slice: 2026-10-29-stop-decisions
shape_change: yes
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: adopters
---

# Packet: A stop keeps the decision, not only the answer (third pass)

**Needs a decision.**

- **Shape.** The two-people seat (Sean, solo per `.xv/picture.md:52`) has already accepted this shape twice: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md` and `…-stop-decisions-2.md`, record lines 78-94. The diff since the second decision (`e2b4253..HEAD`) adds no module, edge, table or surface, so nothing in the shape is new.
- **For Sean as originator.** Amendment 2 is not met. Both README examples now give `--next`, but `scripts/record.py:295` still refuses them because they have no `--settled` and no `--pick`. Item (a) below has the details.

## The scenario

There are four issues in this slice.

- **#80.** `xv record offer` puts numbered options on the open stop, each with its `settles` text and an `--amends` mark, plus a `recommended` index. `xv record answer` takes `--pick`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle`, and records `budget_change`. `xv prompt` passes on `settled`. `xv decisions [--since]` counts stops per order. The watch brief uses `offer` and sends amending decisions through `xv slice amend`.
- **#62.** Someone other than `set_by` may answer an `originator` stop.
- **#42.** The scenario agent writes the red in the form `settled` names, or stops.
- **#73.** A step that stops, or ends with no report, keeps `next` on itself.

Amendments, in order:

- **First amendment.**
  - A pick counts as taken only when it equals `recommended`.
  - `xv decisions` reads records through `retro.records()`.
  - `--resume` needs `--next`.
- **Second amendment.**
  1. `--pick <n>` fills `settled` before the `--next` check.
  2. The README examples give `--next`, "so they are not refused".
  3. The CHANGELOG names the `--resume`/`--next` rule.
  4. Stops raised by `xv step` keep `budget_seen`.
  5. The scribe log names only the fields written.

May ignore: the watch answering stops by itself, backfilling old records, and #64.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest -q test_record test_answer_in_prompt test_run`. The red at the last scenario step had 27 failures and 1 error out of 99 tests (`checks.scenario.red_output`). The whole suite at HEAD `9c5b342`: I re-ran it and got `Ran 368 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-29-stop-decisions.boundary.md`, as given:

- Touched: `scripts/decisions`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Module added: `scripts/decisions`. None removed. No new outbound calls.
- Edges added: `scripts/decisions → scripts/retro` and `scripts/decisions → scripts/xvlib`. None removed.
- Tables: none. Surface paths: none detected.
- The diff also adds a CLI command (`bin/xv`, `"decisions": "decisions.py"`) and changes two briefs (`skills/watch/SKILL.md`, `skills/scenario/SKILL.md`).

Since the second decision, the only code changes are `scripts/record.py:295`, `:307-311` and `:323`, and `scripts/run.py:397`. None of them adds an import.

## What the suite asserts after

- **`offer`.** It stores the options in order, each with `settles` and `amends`, plus `recommended` or null. It refuses an option with no `--settles`, and a `--settles` or `--amends` with no `--option` before it.
- **`answer`.**
  - It keeps the words verbatim.
  - `--pick n` sets `settled` from the option, so `--pick 1 --next maker --resume` is accepted.
  - `--next` with no pick and no `--settled` is refused, and so is `--pick other` with no `--settled`.
  - `--resume` with no `--next` is refused.
  - `cause` must be one of the five values.
  - The scribe log line names only the fields written.
  - `bundle` is stored as a list.
  - When the budget moved after a stop raised by `xv record stop`, `offer` or `xv step`, `budget_change` holds the amounts.
- **#62.** An answer from someone other than `set_by` is accepted.
- **`xv decisions`.** It counts only new-style stops, and `--since` filters them. A pick counts as taken only when it equals `recommended`. It skips the records `retro` skips.
- **`xv prompt`.** The prompt shows `settled`, not the raw answer.
- **Briefs and docs.** The brief texts carry `offer`, `--settles`, `xv slice amend`, the `--resume`/`--next` rule and "does not swap in a test". Every README line with `xv record answer … --resume` contains `--next`. The CHANGELOG names the `--resume`/`--next` rule.
- **`next`.** After a stop or a missing report, `next` stays on the step that stopped.

## 1. Shape

shape_change: **yes**, breadth **narrow**. The forecast expected `wide` (record `forecast.shape`), so this is not wider than forecast. Both hints were decided at earlier stops, and this pass adds nothing.

- **Hint "a module was added": changes the shape.** `scripts/decisions.py` is new, and `bin/xv` gives it a command. `.xv/picture.md:21` counts 22 modules, and `.xv/picture.md:27` names the `xv` CLI as a surface. Accepted at the first shape stop (record lines 78-84).
- **Hint "an edge between modules was added": inside the shape.** `decisions → xvlib` reaches the shared base (`.xv/picture.md:23`). `decisions → retro` is the reuse the first amendment asked for, and Sean accepted it at the second stop (record line 88).
- **Record format: inside the shape.** The stops get new keys, all additive. `scripts/run.py:397` now writes `budget_seen` on stops raised by `xv step` too. `budget_seen` is removed again when the stop is answered (`scripts/record.py:306`).

## 2. Pitch

pitch_contradiction: **no**. I read `.xv/pitch.md:7` ("vibe with discipline"), `:17` ("executable and empirical … shareable"), `:21` (who uses it) and `:25` (who it is not for).

- Counting decisions per order serves "empirical" (`.xv/pitch.md:17`).
- Keeping `settled` for the next agent serves "discipline" (`.xv/pitch.md:7`).
- This pass changes only the answer checks (`scripts/record.py:295`), the log (`scripts/record.py:323`) and the docs (`README.md:189`, `README.md:295`, `CHANGELOG.md:7`), and serves no one new (`.xv/pitch.md:21`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:477` `test_an_answer_that_sends_work_back_needs_settled` | `--pick 1 --next scenario`, no `--settled` → refused | `--next scenario`, no pick, no `--settled` → refused | Amendment 1 fills `settled` from the pick, so the old case is now accepted. The refusal stays for no pick and no settled. | **Yes.** Record line 90 reverses the old assertion word for word. Assertion count is 118 before and 118 after (`xv wall diff`), so it asserts no less. |

- The opposite case is now pinned by `test_a_pick_fills_settled_before_next_checks_for_it`. The moved test asserts the same thing as the new `test_next_with_no_pick_and_no_settled_is_still_refused` (`tests/test_record.py` `AnswerAmendmentsTest`). Only the stop setup and `--next` value differ, so the two overlap.
- The record lists this one move twice (`moved_tests`, entries at 19:41:33 and 19:44:47, with identical text), but the log has one line (`.xv/slices/2026-10-29-stop-decisions.md:15` against `.xv/slices/2026-10-29-stop-decisions.md:128`). It is one moved test.
- `xv wall diff`: changed `tests/test_record.py` only. Nothing deleted or added, `fewer_assertions` empty, nothing unrecorded.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

Proposed edits for Sean, carried from the second pass and still open. I do not write to the picture.

- **`.xv/picture.md:21`.** 23 modules, `scripts/*.py` (20), and 58 edges: two added, none removed, per the boundary picture.
- **`.xv/picture.md:23`.** Add: "`decisions` reads every slice record through `retro.records()` and counts answered stops per order: picks equal to the recommendation, `new_info: none`, and causes."
- **`.xv/picture.md:26`.** The last sentence keeps `next` on `scenario` only for an unsafely joined red. Generalize it: any step that stops, other than at `ready_to_merge`, or ends with no report keeps `next` on itself (`scripts/run.py:392-393`). Every `--resume` answer names `--next` (`scripts/record.py:283`) and needs `settled`, given or taken from a pick (`:295`).
- **`.xv/picture.md:31`.** Add that someone other than `set_by` may answer an `originator` stop (#62).
- **Names (`.xv/picture.md:30-39`).** Add: "`settled` is what an answer made true, written by the watch as the person's scribe. The raw words stay in `answer`. An offer is the numbered options put on an open stop."

## For the originator (do not stop the change)

- **(a) The README examples are still refused, and one points to the wrong step.**
  - `README.md:189` is `xv record answer … --answer "merge" --next maker --resume`, and `README.md:295` is `… --answer "<their words>" --next <step> --resume`.
  - Neither has `--settled` or `--pick`. `scripts/record.py:295`, `(a.next and not settled)`, raises on both, so a reader who copies either one gets exit 2.
  - Amendment 2 (record line 91) asks that they "give `--next`, so they are not refused". The test (`test_the_readme_answer_examples_with_resume_give_next`) checks only that `--next` appears, so it passes.
  - `README.md:189` also answers "merge" at the `ready_to_merge` stop (`README.md:193`) with `--next maker`. Once it is accepted, it would send a merged slice back to the maker instead of `close` (`scripts/run.py:39`).
- **(b) Every `--resume` answer without an offer still needs `--settled`, including answers that move forward.** `scripts/record.py:295` treats every `--next` as "sends work back" (record line 58), `--next close` included. Amendment 1 opened only the pick path. This is the reason (a) fails. A stop the watch did not `offer` on can be resumed only with a hand-written `--settled`.
- **(c) The watch brief still shows `--next` as optional.** `skills/watch/SKILL.md:45` writes `[--next <step>]` in brackets, while `:48` says `--resume` refuses an answer without it. `:50` still describes `--settled` as needed "when the answer sends work back", which understates `scripts/record.py:295`.
- **(d) An offer resets `budget_seen`.** `scripts/record.py:260` overwrites the `budget_seen` that `xv record stop` (`:222`) or `xv step` (`scripts/run.py:397`) wrote. A budget moved between the stop and the offer gives no `budget_change`. The watch usually offers right after the stop, so this is rare.
- **(e) The decision records still cannot be read without the chat.** `.xv/decisions/2026-10-29-2026-10-29-stop-decisions-2.md:10` holds only "1". What was weighed lives in the scenario amendments (record lines 86-94). This slice is built to close that gap, but these two stops ran on the old code.

## Door

**Door:** two-way. A revert undoes the code, the two briefs, the README and the CHANGELOG line. Extra keys on stops written in the meantime are ignored by older code. **Blast radius:** adopters. Every adopting repo runs the watch and scenario briefs (`.xv/picture.md:27`), and every resumed answer there now needs `--next` plus `settled`.

## Raw data

- Slice record: `.xv/slices/2026-10-29-stop-decisions.md`
- Diff: `git diff 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d..9c5b342`; since the last packet: `git diff e2b4253..9c5b342`
- Wall: `xv wall diff 2026-10-29-stop-decisions` (baseline `e2b4253`)
- Boundary: `.xv/slices/2026-10-29-stop-decisions.boundary.md`
- Shape decisions: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, `.xv/decisions/2026-10-29-2026-10-29-stop-decisions-2.md`

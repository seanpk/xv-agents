---
slice: 2026-10-29-stop-decisions
shape_change: yes
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 3
door: two-way
blast_radius: adopters
---

# Packet: A stop keeps the decision, not only the answer (fourth pass)

**Needs a decision.**

- **Shape (two people; Sean runs this repo solo, `.xv/picture.md:52`).** The shape has been accepted three times: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, `…-2.md` and `…-3.md`, plus record lines 78-103. Since the third decision (`1ab21d4..HEAD`), no module, edge, table or surface was added. The diff only edits `scripts/record.py:260`, `scripts/record.py:295-297`, `README.md:189` and `skills/watch/SKILL.md:45,50`. The front-matter `yes` is for the whole slice. Nothing in the shape is new.
- **For Sean as originator.** There are two new moved tests, both forced by amendment 4.1. All four fixes from amendment 4 are met. Three smaller gaps remain; see "For the originator" below.

## The scenario

There are four issues in this slice.

- **#80.** `xv record offer` puts numbered options on the open stop, each with `settles` and `amends`, plus `recommended`. `xv record answer` takes `--pick`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle`, and records `budget_change`. `xv prompt` passes on `settled`. `xv decisions [--since]` counts stops per order.
- **#62.** Someone other than `set_by` may answer an `originator` stop.
- **#42.** The scenario agent writes the red in the form `settled` names, or stops.
- **#73.** A step that stops keeps `next` on itself.

Amendments 1-3 are in record lines 78-94. Amendment 4 (record lines 96-103) has four parts:

1. `--settled` is needed only when `--next` goes back to the step that stopped or an earlier one, or when the pick is `other`.
2. The README merge example uses `--next close`, and both README examples run.
3. The watch brief shows `--next` as required and says when `--settled` is needed.
4. `offer` keeps the stop's `budget_seen`.

May ignore: the watch answering stops by itself, backfilling old records, and #64.

## The recording

None, because this is a feature. To replay the red: `cd tests && python3 -m unittest test_record test_run`. The red at the last scenario step had 32 failures and 1 error out of 106 tests (`checks.scenario.red_output`). For the green, I re-ran the whole suite at HEAD `0df4f76`: `Ran 375 tests in 94.615s`, `OK`.

## The boundary picture

From `.xv/slices/2026-10-29-stop-decisions.boundary.md`, as given:

- Touched: `scripts/decisions`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Module added: `scripts/decisions`. None removed. No new outbound calls.
- Edges added: `scripts/decisions → scripts/retro` and `scripts/decisions → scripts/xvlib`. None removed.
- Tables: none. Surface paths: none detected. The diff also adds the `xv decisions` command (`bin/xv:45`) and changes two briefs (`skills/watch/SKILL.md`, `skills/scenario/SKILL.md`).

None of the code changes since `1ab21d4` adds an import.

## What the suite asserts after

These are the assertions new or changed in this pass. The rest is as in the third packet.

- **Forward answers.** An answer whose `--next` is later than the record's `next`, or is `close`, is accepted with no `--settled` (`FourthAmendmentTest`).
- **Back answers.** `--next` to the same step or an earlier one, with no pick and no `--settled`, is refused, and the stop stays open.
- **README.** Every `xv record answer 2026-10-22-expiring-today` line in the README runs against a `ready_to_merge` stop and exits 0, and one of them uses `--next close`.
- **Watch brief.** It has exactly one `xv record answer` line, that line contains `--next <step>` and not `[--next`, and the text says when `--settled` is needed ("earlier" or "forward").
- **Offer.** If the budget moved between `stop` and `offer`, the answer still records `budget_change` from 2 to 4.

## 1. Shape

shape_change: **yes**, breadth **narrow**. The forecast expected `wide` (record `forecast.shape`), so this is not wider than forecast. Both hints were decided at earlier stops, and this pass adds nothing to the shape.

- **Hint "a module was added": changes the shape.** `scripts/decisions.py` is new, and `bin/xv:45` gives it a command. `.xv/picture.md:21` counts 22 modules, and `.xv/picture.md:27` names the `xv` CLI as a surface. Accepted at the first shape stop (record line 80).
- **Hint "an edge between modules was added": inside the shape.** `decisions → xvlib` reaches the shared base (`.xv/picture.md:23`). `decisions → retro` is the reuse that amendment 1.2 asked for, and it was accepted at the second stop (record line 88).
- **This pass: inside the shape (`.xv/picture.md:23`, `record` owns the slice record).** `scripts/record.py:295-297` changes a refusal rule inside `record`, and `scripts/record.py:260` changes `stop["budget_seen"] = …` to `stop.setdefault("budget_seen", …)`; neither adds a key, a module or an edge (`git diff 1ab21d4..HEAD -- scripts`).

## 2. Pitch

pitch_contradiction: **no**. I read `.xv/pitch.md:7` ("to vibe with discipline"), `:17` ("executable and empirical, and so usable and shareable"), `:21` (who uses it) and `:25` (who it is not for).

- Asking for `settled` only when work goes back keeps the scribe step where it carries the decision. That serves "discipline" (`.xv/pitch.md:7`) and serves no one new (`.xv/pitch.md:21`).
- The README fix makes the documented command runnable, which serves "usable" (`.xv/pitch.md:17`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:477` `test_an_answer_that_sends_work_back_needs_settled` (first move, already accepted at the third stop) | `--pick 1 --next scenario`, no `--settled` → refused | `--next scenario`, no pick → refused | Amendment 1 fills `settled` from the pick | **Yes**, record line 90 |
| same test, second move (`tests/test_record.py:479`) | `next` at its default (`forecaster`), `--next scenario`, no `--settled` → refused | first `record set next guardian`, then the same answer → refused | Amendment 4: going from `forecaster` to `scenario` is forward, so the setup must make `scenario` a step back | **Yes.** Record line 100 makes the old case pass. The assertions are unchanged. |
| `tests/test_record.py:649` `test_next_with_no_pick_and_no_settled_is_still_refused` | `next` at its default, `--next maker`, no `--settled` → refused | first `record set next maker`, then the same answer → refused | Amendment 4: `maker` must be the step that stopped | **Yes.** Record line 100. The assertions are unchanged. |

- **`xv wall diff`** (baseline `1ab21d4`): only `tests/test_record.py` changed, with 134 assertions before and 134 after. `fewer_assertions` is empty, and nothing was deleted or added. Neither test asserts less. Each keeps its refusal under a setup where the amended rule still refuses.
- **Overlap.** The two moved tests now assert the same thing as `test_next_to_an_earlier_step_needs_settled` and `test_next_to_the_step_that_stopped_needs_settled` (`tests/test_record.py:706-717`).
- **Duplicates in the record.** `moved_tests` lists each move twice (`.xv/slices/2026-10-29-stop-decisions.md:15`: 19:41:33/19:44:47 and 20:20:04/20:21:47). The log has one line for each (lines 137, 145, 146). That makes 3 moves on 2 tests, not 6.
- **Style.** The two moved lines write `p =self.xv` with a missing space (`tests/test_record.py:480`, `:651`). The cleaner did not review the test hunks (record line 148).

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

These are proposed edits for Sean. I do not write to the picture. The ones carried from earlier packets are updated for amendment 4.

- **`.xv/picture.md:21`.** Change it to 23 modules, `scripts/*.py` (20), and 58 edges: two added, none removed, per the boundary picture.
- **`.xv/picture.md:23`.** Add: "`decisions` reads every slice record through `retro.records()` and counts answered stops per order: picks equal to the recommendation, `new_info: none`, and causes."
- **`.xv/picture.md:26`.** The last sentence keeps `next` on `scenario` only for an unsafely joined red. Generalize it:
  - Any step that stops, other than at `ready_to_merge`, keeps `next` on itself (`scripts/run.py:392-393`).
  - A `--resume` answer must name `--next` (`scripts/record.py:283`).
  - It must carry `settled` when `--next` is the record's `next` or earlier, or when the pick is `other` (`scripts/record.py:295-297`).
- **`.xv/picture.md:31`.** Add that someone other than `set_by` may answer an `originator` stop (#62).
- **Names (`.xv/picture.md:30-39`).** Add: "`settled` is what an answer made true, written by the watch as the person's scribe. The raw words stay in `answer`. An offer is the numbered options put on an open stop."

## For the originator (do not stop the change)

- **(a) The decision record still keeps only the raw words.**
  - `scripts/record.py:318-321` writes `a.answer` into `.xv/decisions/*.md` and into the record's `decisions` list, not `settled`. That holds even when `settled` was given.
  - `.xv/decisions/2026-10-29-2026-10-29-stop-decisions-3.md` reads only "1". Its heading says "Write down what you weighed; the decision record keeps it", and the record does not keep what was weighed.
  - The scenario is silent on the decision file, so this is outside the slice. It is the gap the slice title names, in the one place that "binds later agents" (`scripts/record.py:331`).
- **(b) "The step that stopped" is read from the record's `next`, not from the stop.**
  - `scripts/record.py:295-296` compares `--next` with `data["next"]`, not with the stop's `step`. For stops raised by `xv step` the two agree (`scripts/run.py:392-393`).
  - A stop the watch raises by hand with `xv record stop` has no step, and `next` there is the step that has not run yet. So `--next <that step>`, which moves the slice forward, still needs `--settled`.
  - `--next prototype` is not in `STEPS`, so it always needs `--settled`.
  - Both cases err toward asking for more.
- **(c) The general README line does not mention `--settled`.**
  - `README.md:295` shows `… --answer "<their words>" --next <step> --resume`. For a back step, `scripts/record.py:297` refuses it with exit 2.
  - The new README test runs only the `2026-10-22-expiring-today` lines (`tests/test_record.py:719-722`), so line 295 is not exercised.
  - The `CHANGELOG.md:7` line names the `--resume`/`--next` rule (amendment 2.3). It does not name the new rule for when `--settled` is required, which is a brief change (`.xv/picture.md:60`).

## Door

**Door:** two-way. A revert undoes the code, the two briefs, the README and the CHANGELOG line. Extra keys on stops written in the meantime are ignored by older code. **Blast radius:** adopters. Every adopting repo runs the watch and scenario briefs (`.xv/picture.md:27`), and every resumed answer there now needs `--next`, plus `settled` when it sends work back.

## Raw data

- Slice record: `.xv/slices/2026-10-29-stop-decisions.md`
- Diff: `git diff 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d..0df4f76`. Since the last packet: `git diff 1ab21d4..0df4f76`.
- Wall: `xv wall diff 2026-10-29-stop-decisions` (baseline `1ab21d4`)
- Boundary: `.xv/slices/2026-10-29-stop-decisions.boundary.md`
- Shape decisions: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, `…-2.md`, `…-3.md`

## From the cleaner

- Shape proposal, for people: cmd_answer in scripts/record.py has grown long; pulling the pick/settled resolution into a helper would be a new concept, so it is left for the packet

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

# Packet: A stop keeps the decision, not only the answer (fifth pass)

**Needs a decision.**

- **Shape: two people. Sean runs this repo solo (`.xv/picture.md:52`).** The front matter says `yes` because it covers the whole slice: `scripts/decisions.py` and `xv decisions` are new. Sean accepted that shape four times (`.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, `…-2.md`, `…-3.md`, `…-4.md`). This pass (`a2c1dfb..HEAD`) adds no module, edge, table or surface. It edits only `scripts/record.py:295-297`, `:322-325` and `:343-344`, `README.md:295` and `CHANGELOG.md:7`.
- **For Sean, as the person who set the work going.** All three parts of amendment 5 are met, and no test moved in this pass. Four small notes are below under "For the originator"; none of them stops the change.

## The scenario

The slice covers four issues:

- **#80.** `xv record offer` puts numbered options, each with `settles` and `amends`, on the open stop, along with `recommended`. `xv record answer` takes `--pick`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle`. `xv prompt` passes `settled` to the next agent. `xv decisions [--since]` counts stops per order.
- **#62.** A name other than `set_by` may answer an `originator` stop.
- **#42.** The scenario agent writes the red in the form `settled` names, or stops.
- **#73.** A step that stops keeps `next` on itself.

Amendments 1-4 are in record lines 78-103. Amendment 5 is in record lines 105-111:

1. The decision record and the `decisions` list keep `settled` alongside the person's words.
2. "The step that stopped" is the stop's saved `step`. The record's `next` is used only when the stop has no step.
3. `CHANGELOG.md` and `README.md:295` say when `--settled` is required.

The slice may ignore three things: the watch answering stops by itself, backfilling old records, and #64.

## The recording

There is no recording: this slice is a feature.

- **Red.** `cd tests && python3 -m unittest test_record test_run test_answer_in_prompt`. At the last scenario step it ran 121 tests with 39 failures and 1 error (`checks.scenario.red_output`).
- **Green.** I re-ran the whole suite at HEAD `04cbb5e`: `Ran 380 tests in 92.742s`, `OK`.

## The boundary picture

This is from `.xv/slices/2026-10-29-stop-decisions.boundary.md`, as given:

- **Touched:** `scripts/decisions`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- **Modules:** `scripts/decisions` was added. None was removed, and nothing new calls out of the process.
- **Edges:** `scripts/decisions → scripts/retro` and `scripts/decisions → scripts/xvlib` were added. None was removed.
- **Tables and surface paths:** none.

The tool does not count two changes that people meet: the new `xv decisions` command (`bin/xv:45`) and the edits to two briefs (`skills/watch/SKILL.md`, `skills/scenario/SKILL.md`). None of this pass's code changes adds an import.

## What the suite asserts after

The new assertions in this pass are in `FifthAmendmentTest`, `tests/test_record.py:752-811`. Everything else is as described in the fourth packet.

- **Back, judged on the stop.** The stop saved `guardian` and the record's `next` is `scenario`. An answer with `--next maker` and no `--settled` is refused, and the refusal names `--settled`.
- **Forward, judged on the stop.** The stop saved `scenario` and the record's `next` is `guardian`. An answer with `--next maker` and no `--settled` is accepted, and `next` becomes `maker`.
- **Decision keeps settled.** A two-person stop is answered with `--pick other --settled "…"`. The record's `decisions[0].settled` holds that text, and the `.xv/decisions/` file holds both the text and the person's words.
- **CHANGELOG.** It names `--settled` together with "back" or "earlier" and "other".
- **README.** The general answer line names `--settled`, "back" or "earlier", and "other".

## 1. Shape

shape_change: **yes**, breadth **narrow**. The forecast expected `wide` (record `forecast.shape`), so the change is not wider than forecast.

- **Hint "a module was added": this changes the shape.** `scripts/decisions.py` is new, and `bin/xv:45` gives it a command. `.xv/picture.md:21` counts 22 modules, and `.xv/picture.md:27` lists the `xv` CLI as a surface. Sean accepted this at the first shape stop (record line 80).
- **Hint "an edge between modules was added": this stays inside the shape.** `decisions → xvlib` reaches the shared base (`.xv/picture.md:23`). `decisions → retro` is the reuse that amendment 1.2 asked for, and it was accepted at the second stop (record line 88).
- **This pass stays inside the shape.** `record` owns the slice record (`.xv/picture.md:23`). The changes at `scripts/record.py:295-297` (which step the send-back check compares against), `:322-325` (the `settled` key on a `decisions` entry) and `:343-344` (a `## Settled` section in the decision file) all live inside `record` and add no module or edge.

## 2. Pitch

pitch_contradiction: **no**. I read `.xv/pitch.md:7` ("to vibe with discipline"), `:17` ("executable and empirical, and so usable and shareable"), `:21` (who uses it) and `:25` (who it is not for).

- Keeping `settled` in the decision record (`scripts/record.py:322-325`, `:343-344`) makes a decision readable later without the chat. That serves "shareable" (`.xv/pitch.md:17`).
- This pass serves no one new and makes the system do nothing new against `.xv/pitch.md:21` or `:25`.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:477` `test_an_answer_that_sends_work_back_needs_settled`, move 1 (accepted at the third stop) | `--pick 1 --next scenario`, no `--settled`: refused | `--next scenario`, no pick: refused | Amendment 2.1: the pick fills `settled` | **Yes** (record line 90) |
| Same test, move 2 (`:479`, accepted at the fourth stop) | `next` at its default, `--next scenario`: refused | `record set next guardian` first, then the same answer: refused | Amendment 4.1: `forecaster → scenario` is a forward move | **Yes** (record line 100). The assertions are unchanged. |
| `tests/test_record.py:649` `test_next_with_no_pick_and_no_settled_is_still_refused` (accepted at the fourth stop) | `next` at its default, `--next maker`: refused | `record set next maker` first: refused | Amendment 4.1 | **Yes** (record line 100). The assertions are unchanged. |

- **This pass.** `xv wall diff` (baseline `a2c1dfb`) shows nothing changed, deleted or added, and `fewer_assertions` is empty. `tests/test_record.py` grew from 134 to 148 assertions in `.xv/slices/2026-10-29-stop-decisions.wall.json`, all of them in the new `FifthAmendmentTest`.
- **Duplicates in the record.** `moved_tests` (`.xv/slices/2026-10-29-stop-decisions.md:15`) lists each move twice. There are 3 moves on 2 tests, not 6.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

These are proposed edits for Sean to accept. I do not write to the picture.

- **`.xv/picture.md:21`.** Change it to 23 modules, with `scripts/*.py` at 20, and 58 edges. The boundary picture shows two edges added and none removed.
- **`.xv/picture.md:23`.** Add this sentence: "`decisions` reads every slice record through `retro.records()` and counts answered stops per order: picks equal to the recommendation, `new_info: none`, and causes."
- **`.xv/picture.md:26`.** Its last sentence keeps `next` on `scenario` only when a red command is joined unsafely. Widen it to say three things:
  - Any step that stops, other than at `ready_to_merge`, keeps `next` on itself (`scripts/run.py:392-393`).
  - A `--resume` answer must name `--next` (`scripts/record.py:284`).
  - The answer must carry `settled` when `--next` is the stop's saved `step` or an earlier one, or when the pick is `other` (`scripts/record.py:295-300`). A decision file and its `decisions` entry keep `settled` with the words (`scripts/record.py:322-325`, `:343-344`).
- **`.xv/picture.md:31`.** Add that someone other than `set_by` may answer an `originator` stop (#62).
- **Names, `.xv/picture.md:30-39`.** Add: "`settled` is what an answer made true, written by the watch as the person's scribe; the raw words stay in `answer`. An offer is the numbered options put on an open stop."

## For the originator (none of these stops the change)

- **(a) Stops whose saved step is not a pipeline step now always need `--settled`.** The forward test at `scripts/record.py:297` needs `stopped_at in STEPS`. Some stops save a step outside `STEPS`:
  - `"setup"` (`scripts/run.py:263`, `setup_failed`).
  - `"prototype"` (`scripts/prototypes.py:86`, `:96`, `:197`).

  For these stops, every `--next` other than `close` counts as a send-back. Separately, a budget stop saves the step that was about to run (`scripts/run.py:342`). So "raise the budget and go on" (`--next <that step>`) counts as the same step and needs `--settled`. That was also true before amendment 5, when `next` equalled that step. Both cases ask for more, not less.
- **(b) The tests fake the saved step.** `xv record stop` cannot save a `step`. The test helper `stop_saved_at` (`tests/test_record.py:760-770`) therefore rewrites the record text to inject one. The case of a stop that has a step is covered only through that edit and through `xv step`.
- **(c) `README.md:295` is checked for wording, not run.** `tests/test_record.py:805-811` matches words in the line. Run as written, the line has no `--settled`, so it is refused for a back step (`scripts/record.py:298`). The line now says so.
- **(d) Carried from the earlier passes.**
  - The cleaner's shape proposal: `cmd_answer` is 68 lines (`scripts/record.py:265-331`).
  - A missing space in `p =self.xv` (`tests/test_record.py:480`, `:651`).

## Door

**Door:** two-way. A revert undoes the code, the two briefs, the README and the CHANGELOG line. Stops and decision entries written in the meantime keep extra keys (`settled`, `pick`, …) and a `## Settled` section, which older code ignores. **Blast radius:** adopters. Every adopting repo runs the watch and scenario briefs (`.xv/picture.md:27`). In those repos, every resumed answer now needs `--next`, plus `--settled` when it sends work back.

## Raw data

- Slice record: `.xv/slices/2026-10-29-stop-decisions.md`
- Diff: `git diff 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d..04cbb5e`. Since the last packet: `git diff a2c1dfb..04cbb5e`.
- Wall: `xv wall diff 2026-10-29-stop-decisions` (baseline `a2c1dfb`)
- Boundary: `.xv/slices/2026-10-29-stop-decisions.boundary.md`
- Shape decisions: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, `…-2.md`, `…-3.md`, `…-4.md`

## From the cleaner

- Shape proposal, for people: cmd_answer in scripts/record.py has grown long; pulling the pick/settled resolution into a helper would be a new concept, so it is left for the packet
- Shape proposal, for people: cmd_answer in scripts/record.py has grown long; pulling the pick/settled/send-back resolution into a helper would be a new concept, so it is left for the packet

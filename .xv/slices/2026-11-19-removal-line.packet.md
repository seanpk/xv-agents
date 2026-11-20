---
slice: 2026-11-19-removal-line
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 8
expected_moves: 0
door: two-way
blast_radius: narrow
---

# Packet: A slice-only removal names its line, and the check reads the tree

No two-person stop fires: there is no shape change and no pitch contradiction.
The change misses two scenario lines, so the slice goes back (to the scenario agent, because the red covers neither line).
Sean Kennedy also has the moved tests, four wall removals, an edit to the picture the maker made without a listing, and the picture edits proposed below.

## The scenario

`xv record move --slice-only` now takes `--line <n>`.
It reads that line's text from the commit where the step or pairing began, refuses a blank line or a number past the end, and records the text with the number; `--assertion` becomes a free note (outcome 1).
After a step, the removal check counts that text in the file now, and stops with `removal_not_made` naming the file, line and text when the count is not lower (outcome 2).
A removal committed before its move is taken (outcome 3), through `step_start` saved by `xv step` and `start_commit` saved by `xv pairing start`, and HEAD when there is neither (amendment 8).
Outcome 4 is a table test, outcomes 5 and 6 are brief, picture and same-move lines, and outcome 7 is a CHANGELOG line, which Sean Kennedy settled has no test.
May ignore: moves recorded before this change, `--deleted` removals, and moves that are not slice-only.

## The recording

None: this is a feature that starts from words.
Replay the red with `cd tests && python3 -m unittest test_removal_line`: before, 17 failures and 2 errors (record, `checks.scenario.red_output`); after, it passes.
Whole suite: `python3 tests/run.py` gives `Ran 1424 tests in shard 1/1, 32 jobs` and `OK`, which I re-ran on this pass.

## The boundary picture

From `.xv/slices/2026-11-19-removal-line.boundary.md`, as given: modules touched are `scripts/pairing`, `scripts/record` and `scripts/run`.
No modules, edges, outbound calls, tables or surface paths were added or removed.
Shape hints: none.

## What the suite asserts after

- A slice-only move with no `--line`, a blank line, a line past the end, or a line below 1 is refused, and nothing is recorded (`tests/test_removal_line.py:46-68`).
- Any text in `--assertion` is accepted (`tests/test_removal_line.py:70`, `tests/test_record.py` `test_a_sentence_or_a_broken_name_is_a_free_note_and_is_taken`).
- The line is read at the start commit, not the tree now (`tests/test_removal_line.py:77`).
- The removal check stops on a line whose text is still there, names the file, number and text, and does not read the note (`tests/test_removal_line.py:84-101`).
  The table covers a Python def, a JS `it()` with spaces, and a doubled line (`:104-120`).
- Two moves for one file and line are one move, and two lines are two moves (`:123-135`).
- `xv step` saves `step_start` before the agent runs, and a removal committed in a step or in a pairing, then moved with `--line`, is taken (`:165-214`).
- The cleaner brief, the picture and the watch brief carry the new text (`:138-158`).
- Old tests now give `--line`, and the old refusals of sentences and unreadable names have become acceptances (see Moved tests).

## 1. Shape

shape_change: no.
The boundary picture shows no added module, edge, table or surface path, and its shape hints are `none`.
The change stays inside `record`, `run` and `pairing`, which the picture already describes as owning moves, steps and pairings (`.xv/picture.md:68-80`).
The new `--line` flag changes an existing command, `xv record move`, inside the current shape: `scripts/record.py:1304-1305`.
The new record keys (`step_start`, the pairing's `start_commit`, and a move's `line`, `line_text` and `line_count`) add fields to the slice record, which is not a table (`scripts/run.py:846`, `scripts/pairing.py:145`, `scripts/record.py:305`).
shape_breadth: narrow, matching the forecast's `narrow` and its note ("the record move command, the removal check, the cleaner and watch briefs, the picture line and one CHANGELOG line").
The forecast did not name `scripts/pairing.py` or `scripts/run.py`, but amendment 8 forces both.

## 2. Pitch

pitch_contradiction: no.
I checked the change against `.xv/pitch.md:25`, "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot."
The change serves the same users and adds no new purpose.
The pitch says nothing about move records.

## 3. Moved tests

The record holds 8 entries for 7 distinct moves: the first and last entries describe the same `SliceOnlyMoveTest`/`WallChoicesTest`/`OneHomeRecordTest` change, and `same_move` did not merge them because their words differ ("and" against ",").
`xv wall diff` lists nothing, because its baseline `a130c54` comes after the maker's first pass `e09ef67`, where these moves were made.
I read them in `git diff 2ebb304..HEAD -- tests/`.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_record.py | `SliceOnlyMoveTest`, `WallChoicesTest`, `OneHomeRecordTest` slice-only moves with no `--line` | the same, with `--line 1` | `--slice-only` now needs `--line` | Yes, by outcome 1. The assertions are unchanged. |
| tests/test_record.py | `SliceOnlyGateTest.move` with no `--line` | `--line` taken from a `LINES` table | the same | Yes, by outcome 1. |
| tests/test_record.py:1535 | `test_a_name_that_is_in_no_file_when_the_step_began_is_refused…` refused five names that are in no file | refuses lines 2 (blank) and 99 (past the end) | outcome 1 | Yes, but it now asserts less: nothing checks the name. The test name is now false, and the test restates `tests/test_removal_line.py:46,53`. |
| tests/test_record.py:1561 | `test_a_sentence_or_a_broken_name_is_refused…` expected an exit other than 0 and "must be the test's name" | renamed `…_is_a_free_note_and_is_taken`: expects exit 0 and one move | outcome 1 | Yes: outcome 1 says "`--assertion` is a free note again". |
| tests/test_record.py:1617-1639 | `RemovalCheckNamesTest` read the name from the assertion, and an unreadable name stopped with "the test name could not be read" | moves carry `line`, `line_text` and `line_count`; an unreadable note passes when the line is gone; the stop names file, line and text | outcome 2 | Yes, but it asserts less: the stop for an unreadable name is gone, which outcome 2 ("counts that line's text") forces. |
| tests/test_record.py:1649 | `CleanerBriefNoteTest` checked for "as it is written in the file" and "optional note in brackets" | checks for "The assertion is a free note" and "--line <n>" | outcome 5 | Yes. |
| tests/test_run.py:2298 | the double-colon sentence was refused with "must be the test's name" | the move is taken, and the next step stops with `removal_not_made` | outcome 1 | Yes. The test asserts as much as before, now at the removal stop. |
| tests/fake_agent.py:192-200 | `FAKE_CLEANER_REMOVES` moved with no `--line` | passes `--line` | `--slice-only` needs `--line` | Yes. The new `FAKE_CLEANER_COMMITS_REMOVAL_THEN_MOVES_LINE` branch (`:202-220`) is red support. |

Expected moves: none.
Slice-only tests removed: none (the record's `slice_only` is `[]`).
Kept: none.
May-not files the scenario report allowed (`may_not_files_needed`): none.
Even so, the maker edited `.xv/picture.md` in `e09ef67` (see section 4).

## 4. The picture

- **The maker edited the picture without a listing** (`.xv/picture.md:278`).
  `.xv/picture.md:278` says "the maker may edit `.xv/picture.md` only when the scenario report names it in `may_not_files_needed`", and `:280` says "The guardian lists the edit".
  The record has `may_not_files_needed: []`, and `git log 2ebb304..HEAD -- .xv/picture.md` shows only `e09ef67 … make it work`, the maker's commit, editing lines 72-79.
  Outcome 5 ("The picture says what each check reads") forced an edit, yet `checks.maker.protected_changed` is `[]`, so `run.post_step` did not stop on it.
  Sean Kennedy decides whether to keep the maker's text below, and whether that gate should have fired.
- **`.xv/picture.md:76` is untrue.** It says "`--assertion` is a free note that nothing reads", but `scripts/run.py:1283-1285` still reads the cleaner's slice-only move assertion with `move_test_name` for the coverage check.
  This depends on the miss below: once it is fixed, the line is true.
- **`.xv/picture.md:227` describes the old reader.**
  It says "the move's name is read with `names.move_test_name`".
  Proposed, after the fix:
  `A `covered` name whose last part is a slice-only test that the cleaner removed by a recorded move does not stop; the name is read from the move's `line_text`, or for a move recorded before `--line`, from its assertion with `names.move_test_name`.`
- **`.xv/picture.md:51-52` are now true only of old moves.**
  Proposed:
  `For a move recorded before `--line` existed, it reads the move's assertion with `names.move_test_name`: one of `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`, with an optional note in brackets that is not read.`
  `A move with a `--line` is checked by its line's text, and its assertion is not read.`
- **`.xv/picture.md:77` is incomplete.** It does not say where `start_commit` comes from, or how long `step_start` lasts.
  Proposed:
  `The line is read from the open pairing's `start_commit`, which `xv pairing start` saves as the HEAD before its own record commit, else from `step_start`, which `xv step` saves before the agent runs, else from `HEAD`.`
  Add a line that says when `step_start` is cleared, once that is decided (see the miss on amendment 8).

## 5. The wall

Remove these tests, which were on the wall before the slice and which the scenario makes dead:

- `tests/test_record.py` `SliceOnlyAssertionFormTest.test_each_form_of_a_name_is_taken` (`:1570`).
  Under outcome 1 any text is taken, so passing each name form proves nothing more than `test_a_sentence_or_a_broken_name_is_a_free_note_and_is_taken` (`:1561`) and `tests/test_removal_line.py:70`.
- `tests/test_record.py` `SliceOnlyAssertionFormTest.test_a_name_followed_by_a_note_in_brackets_is_taken_whichever_bracket` (`:1581`).
  It is dead for the same reason: bracket notes are no longer parsed on `--line` moves (`scripts/record.py:262-285` no longer calls `move_test_name`).
- `tests/test_record.py` `SliceOnlyAssertionFormTest.test_a_name_that_is_in_no_file_when_the_step_began_is_refused_and_nothing_is_recorded` (`:1535`).
  Its body now checks only line 2 and line 99, which restates `tests/test_removal_line.py:46` and `:53`, and its name describes a check that is gone.
- `tests/test_record.py` `RemovalCheckNamesTest.test_none_of_the_inputs_passes_while_the_test_is_still_in_its_file` (`:1622`).
  Every input now carries the same `line_text` (`:1617-1619`), and the check does not read the assertion (`scripts/record.py:985-993`), so the loop runs one case many times.
  `test_a_name_with_a_note_stops_naming_the_test_while_it_is_there` (`:1637`) already asserts that case.

I looked at every new test in `tests/test_removal_line.py`.
None is marked slice-only, and each guards lasting behaviour: the brief and picture text tests follow the repo's existing pattern, as in `CleanerBriefNoteTest`.

## Scenario misses

- 1: the coverage check still reads the slice-only `--assertion` that outcome 1 says nothing reads, so a cleaner's free note such as "removed as asked" makes a later scenario pass stop with "no red file has that test" for a test the cleaner removed (evidence: `scripts/run.py:1283-1285` `removed = [move_test_name(m["assertion"]) …]`; the red tests only `xv record move`; to: scenario)
- amendment 8: `step_start` is never cleared after a step that is not a session step, so a slice-only move recorded between steps reads its line from the last step's start commit, not HEAD as amendment 8 says for "a move outside any step" (evidence: `scripts/run.py:846-847` saves it, only `scripts/run.py:821` (the session branch) removes it, and `scripts/record.py:256` reads it; no red test records a move outside a step after a step has run; to: scenario)

## Door

**Door:** two-way. A revert undoes the code, and the extra record keys stay harmless, though moves recorded with a free-note assertion would then hit the old "could not be read" stop.
**Blast radius:** narrow.

Binding decision 1 (`.xv/picture.md:331`) applies: this changes the cleaner brief, the watch brief, and a check agents are judged by.
`CHANGELOG.md` gains an `## Unreleased` line "decided by Sean Kennedy" with one name, which the CHANGELOG's opening calls a draft until a second name is added.

## Raw data

- Slice record: `.xv/slices/2026-11-19-removal-line.md`
- Diff: `git diff 2ebb304bf2504ae8d50a2c3104889055f7309772..3b46a11`
- Wall: `xv wall diff 2026-11-19-removal-line` (empty: baseline `a130c54` comes after the moves in `e09ef67`)
- Boundary: `.xv/slices/2026-11-19-removal-line.boundary.md` (`xv boundary --base 2ebb304`)

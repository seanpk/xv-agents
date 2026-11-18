---
slice: 2026-11-18-move-names
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 10
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The removal check reads only names it can find

No shape or pitch stop. One scenario miss goes back: outcome 1 says the command takes a name "only when it names a test that was in that file when the step began", and nothing checks that, so a mistyped name passes the removal check while the real test stays (to: scenario, the red does not test it).
For the person who set the work going: the new name form refuses JS/TS `it("…")` titles that #183 promised the check reads, and the picture needs five edits.

## The scenario

The removal check reads only names it can find (`.xv/slices/2026-11-18-move-names.md`, `## Scenario`).
1. `xv record move --slice-only` takes an `--assertion` only when it names a test that was in that file when the step began, in one of the forms `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name`, `file::Class::name`, with an optional note in `()`, `[]`, `{}` or `<>`. Anything else is refused and nothing is recorded.
2. The removal check looks for exactly that name, without its note, never a sentence; a move from another route with no readable name stops as "the test name could not be read".
3. A table test: nine inputs each stop while the test is in its file; two name-with-note inputs pass once it is gone.
4. A packet listing a miss under `change_misses_scenario: no` stops for the originator, naming the disagreement.
5. The cleaner's brief says the note is the test's name as written, with an optional bracketed note.
6. A CHANGELOG line (no red test; Sean Kennedy accepted that in the answered `red_misses_scenario` stop).

May ignore: moves recorded before this change; `--deleted` file removals.

## The recording

None; a defect from words. Replay the red: `cd tests && python3 -m unittest test_record.SliceOnlyAssertionFormTest test_record.RemovalCheckNamesTest test_record.CleanerBriefNoteTest test_record.ScenarioMissStandingOrderTest`.
Before (record `red.failure`): `AssertionError: [] is not true : removed Red.test_milk_today for issue#183` (the check passed a sentence while the test was in its file).
After: I ran it: 15 tests, OK. I also ran the whole suite (`python3 tests/run.py`): 1399 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-18-move-names.boundary.md` (xv boundary, as given): modules touched `scripts/names`, `scripts/orders`, `scripts/record`, `scripts/run`; modules added none, removed none; edges added none, removed none; no new outbound calls; tables none; surface paths added none, removed none; shape hints: none.

## What the suite asserts after

- `xv record move --slice-only` refuses a sentence, a broken name, a name in backticks, `Red::test_x[1]`, `;`, exits non-zero with "must be the test's name … bracket", and records nothing; it takes each of the six forms and each of the four bracket notes; a plain move still takes any words (`tests/test_record.py:1488`).
- `record.removals_not_made` stops on every table input while the test is there, stops "could not be read" on every non-name input even when the test is gone, passes a name with a note once the test is gone, and never reads a name out of the note (`tests/test_record.py:1541`).
- A packet with `change_misses_scenario: no` and a listed miss stops for the originator, the question naming both; a packet with "None." under the heading does not (`tests/test_record.py:1460`).
- The cleaner brief holds "as it is written in the file" and "optional note in brackets" (`tests/test_record.py:1587`).
- Moved: the sentence forms now reach the check only by a direct record write, and still stop; see Moved tests.

## 1. Shape

shape_change: no.
- The boundary picture shows no module, edge, table, outbound call or surface added or removed, and no shape hints (`.xv/slices/2026-11-18-move-names.boundary.md`, "Shape hints: none", "Edges: added: none").
- `scripts/names.py:65` adds `MOVE_NAME` and `move_test_name` to a module that `record` and `run` already import (`.xv/picture.md:43`); the `scripts/run.py` hunk changes only the import list (`from names import …, move_test_name`). Inside the current shape.
- `scripts/orders.py:338` adds a firing of the existing `change_misses_scenario` order with seat `originator`, which that order already uses for a repeat (`scripts/orders.py:352`); stop rules stay in `orders` (`.xv/picture.md:346`, decision 10). Not a new order.
- `xv record move --slice-only` refuses more input (`scripts/record.py:253`); the command is an existing surface, not a new one.

shape_breadth: narrow, as the forecast expected ("the move-name parser and removal check, one table test, the cleaner brief and one CHANGELOG line"); the slice also touches `orders.py` and `run.py` by a few lines.

## 2. Pitch

pitch_contradiction: no.
The pitch says the system makes it easy "to vibe with discipline" (`.xv/pitch.md:7`); a removal check that reads only real names is that discipline.
It is silent on name forms and on who answers a disagreement stop; nothing in "Who it is not for" (`.xv/pitch.md:25`) is touched.

## 3. Moved tests

The record holds 10 `moved_tests` entries; they are 5 moves each told twice, at 21:11:0x and 21:11:15, in different words (record `moved_tests`). `moves_to_accept` counts by file and assertion (`.xv/picture.md:69`), so the person sees 10 to accept for 10 changed tests. `xv wall diff`: `tests/test_record.py` 492 → 492 assertions, `tests/test_run.py` 544 → 545; `fewer_assertions` empty; no unrecorded file.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `SliceOnlyGateTest.test_a_move_whose_assertion_starts_with_the_marked_name_keeps_the_flag` records `test_file_is_ts; removed` | records `test_file_is_ts (removed)`; same `assertIs(... True)` | outcome 1 refuses a sentence | Yes: outcome 1 refuses `;` text (`scripts/record.py:253`). |
| `tests/test_record.py` | `SliceOnlyGateTest.test_a_move_of_another_test_does_not_get_the_flag` records `test_other; removed` | `test_other (removed)`; same `assertFalse` | same | Yes, same. |
| `tests/test_run.py:2292` | `…_names_a_double_colon_test_still_there_stops`: recorded the sentence, asserted the removal stop naming `test_milk_today` | asserts the command refuses ("must be the test's name") | outcome 1 refuses at the command | Yes, but it now asserts something different and its name ("still_there_stops") no longer says what it checks. The end-to-end stop for a `Class::name` move whose test is still there is no longer asserted anywhere; the table at `tests/test_record.py:1550` uses `tests/milk-red.py::…`, which stops as unreadable because of the `-`. |
| `tests/test_run.py:2300` | `prose_move` (the dotted-name, full-stop, hash and `;` tests) used `xv record move --slice-only` | uses `xv record add … moved_tests` with `slice_only: true`; same `assert_removal_stop` | outcome 1 refuses at the command; the other route still reaches the check | Yes. Note: `xv record add` is a direct write, not the "in a report" route outcome 2 names. |
| `tests/test_run.py:1810–1820` | `RemovedSliceOnlyTestInCoversTest`, 3 tests, assertion `Red.test_cheese; removed` / `Red.test_gouda; removed` | `… (removed)`; same `assert_goes_on` / `assert_stops` | the check no longer reads a sentence | Yes: with the bracket form, the old `split(";")[0]` read would give `test_cheese (removed)` and break the exemption (`scripts/run.py:1279`). The name `…_words_after_the_semicolon_name_another_test` (`tests/test_run.py:1819`) no longer fits the data. |

None asserts less, except the `::` case in row 3, which lost its end-to-end stop.
Slice-only tests removed: none (record `slice_only: []`). Kept: none.
May-not files the scenario report allowed (`may_not_files_needed`): none.

## Findings for the person who set the work going

- **JS/TS titles are refused.** `MOVE_NAME` ends in `(?P<name>\w+)` (`scripts/names.py:65`), so `milk > shows milk running out today` is refused by `xv record move --slice-only` (`scripts/record.py:253`).
  #183 says the check finds "an `it("…")` title, a `Class > test` name" (`CHANGELOG.md:14`), and `tests/test_run.py:2316` keeps a JS title test for the `slice_only` list path.
  The new cleaner brief tells the cleaner to give "the test's name as it is written in the file" (`skills/cleaner/SKILL.md:39`), which the command refuses for an `it` title.
  This is not a scenario line: outcome 1's forms are word names. Whether titles should be a form is a decision for a person.
- **The watch brief's stop table is incomplete.** `skills/watch/SKILL.md:119` describes `change_misses_scenario` only for `yes`; the new firing for `no` with a listed miss (`scripts/orders.py:338`) is not listed there.
- **Decision 1.** The slice changes a brief (`skills/cleaner/SKILL.md:39`), a standing order (`scripts/orders.py:338`) and a check (`scripts/record.py:951`). Decision 1 needs two people and a CHANGELOG line (`.xv/picture.md:324`). The line is there under `## Unreleased` with one name (`CHANGELOG.md:7`); the CHANGELOG says a line without two names is a draft (`CHANGELOG.md:3`).
- **Notes are any text.** `\([^\n]*\)` (`scripts/names.py:66`) takes `Red.test_x (a) b (c)` as one name and one note; the check reads `test_x`. This is harmless to the check, but the note's end is not checked.

## 4. The picture

picture_change: yes. Proposed edits; the person who set the work going accepts them.

- `.xv/picture.md:43` is incomplete. Proposed:
  `names` holds `covered_name_found`, `COVERED_SEPARATOR`, `joined_unsafely` and `move_test_name`, which `record` and `run` both import.
- `.xv/picture.md:49`–`52` are now untrue for moves (`scripts/record.py:951`, `scripts/record.py:896`). Proposed in their place:
  The removal check reads an accepted `slice_only` test's name with `record.test_names`, which keeps the part after the last `>`, the part after the last `::` or `#`, and the last `.` part of a dotted name.
  A part after `::` or `#` that is not a plain name cannot be read, and the check stops on it.
  It reads a move's assertion with `names.move_test_name`: one of `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`, with an optional note in brackets that is not read.
  It never reads a sentence for a name; an assertion in no such form cannot be read.
- `.xv/picture.md:73` is incomplete (`scripts/record.py:253`). Proposed, after it:
  `xv record move --slice-only` refuses an assertion that `names.move_test_name` cannot read, and records nothing.
- `.xv/picture.md:101` is incomplete (`scripts/orders.py:338`, `scripts/record.py:1054`). Proposed, after it:
  A packet whose front matter says `change_misses_scenario: no` while its `## Scenario misses` section lists a miss stops for the originator under `change_misses_scenario`, naming the disagreement.
- `.xv/picture.md:219` is now untrue (`scripts/run.py:1279`). Proposed:
  A `covered` name whose last part is a slice-only test that the cleaner removed by a recorded move does not stop; the move's name is read with `names.move_test_name`.

## 5. The wall

I looked at the new classes `SliceOnlyAssertionFormTest`, `RemovalCheckNamesTest`, `CleanerBriefNoteTest` and the two new `ScenarioMissStandingOrderTest` tests (`tests/test_record.py:1460`–`1595`), and the changed tests in `tests/test_run.py`.
- `tests/test_run.py`, `RemovalNotMadeTest.test_a_slice_only_move_whose_assertion_names_a_double_colon_test_still_there_stops`: remove from the wall. Outcome 2 makes its subject dead: the check no longer reads a `::` word out of a sentence. The rewritten body (`tests/test_run.py:2292`–`2298`) only repeats the refusal that `SliceOnlyAssertionFormTest.test_a_sentence_or_a_broken_name_is_refused_and_nothing_is_recorded` asserts over a table (`tests/test_record.py:1491`).
No new test needs to be marked slice-only: each guards behaviour that goes on after the slice.

## Scenario misses

- 1: The command does not check that the name "names a test that was in that file when the step began". `cmd_move` checks only the form (`scripts/record.py:253`–`256`) and reads no file. A mistyped name such as `Red.test_milk_todya` is taken, and the removal check then passes it, because that name is in no file (`scripts/record.py:951`), while `test_milk_today` stays. No red test records a name that is not in the file (`tests/test_record.py:1488`–`1538`). (evidence: `scripts/record.py:253` hunk; to: scenario)

## Door

**Door:** two-way. A revert restores the old parser and stop; no data is migrated and old records are read as before. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-18-move-names.md`
- Diff: `git diff 8e366c9ba6c94b28cbedfad1e5221c22bf914dda..HEAD`
- Wall: `xv wall diff 2026-11-18-move-names`
- Boundary: `.xv/slices/2026-11-18-move-names.boundary.md` (`xv boundary --base 8e366c9ba6c9`)
- Red run by the guardian: 15 tests, OK. Whole suite run by the guardian (`python3 tests/run.py`): 1399 tests, OK.

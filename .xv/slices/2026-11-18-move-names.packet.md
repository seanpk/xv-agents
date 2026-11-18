---
slice: 2026-11-18-move-names
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 12
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The removal check reads only names it can find (re-pass)

No shape or pitch stop, and no scenario miss on this pass.
The earlier miss on outcome 1 is met: `xv record move --slice-only` now refuses a name that is not in the file as committed at HEAD (`scripts/record.py:257`–`263`), and three new red tests show it (`tests/test_record.py:1532`–`1557`).
For the person who set the work going, four things need a look:
- The file check matches any word in the file, not a test, so `Red.pass` or `unittest.TestCase` is taken as a "test".
- In a pairing, where the watch commits as it goes, a removal committed before its move is recorded is now refused.
- The CHANGELOG line does not mention the new refusal.
- JS/TS `it("…")` titles are still refused.
The picture needs five edits.

## The scenario

The removal check reads only names it can find (`.xv/slices/2026-11-18-move-names.md`, `## Scenario`).
1. `xv record move --slice-only` takes an `--assertion` only when it names a test that was in that file when the step began, in one of the forms `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name`, `file::Class::name`, with an optional note in `()`, `[]`, `{}` or `<>`. Anything else is refused and nothing is recorded.
2. The removal check looks for exactly that name, without its note, and never reads a sentence; a move from another route with no readable name stops as "the test name could not be read".
3. A table test: nine inputs each stop while the test is in its file; two name-with-note inputs pass once it is gone.
4. A packet listing a miss under `change_misses_scenario: no` stops for the originator, naming the disagreement.
5. The cleaner's brief says the note is the test's name as written, with an optional bracketed note.
6. A CHANGELOG line (no red test; Sean Kennedy accepted that in the answered `red_misses_scenario` stop).

May ignore: moves recorded before this change; `--deleted` file removals.

## The recording

None; a defect from words. Replay the red: `cd tests && python3 -m unittest test_record.SliceOnlyAssertionFormTest test_record.RemovalCheckNamesTest test_record.CleanerBriefNoteTest test_record.ScenarioMissStandingOrderTest`.
Before (record `red.failure`, this pass): `AssertionError: 0 == 0 : Red.test_milk_todya (the command takes a name that is in no file)`.
After: I ran it: 18 tests, OK. I also ran the whole suite (`python3 tests/run.py`): 1402 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-18-move-names.boundary.md` (xv boundary, as given): modules touched `scripts/names`, `scripts/orders`, `scripts/record`, `scripts/run`; modules added none, removed none; edges added none, removed none; no new outbound calls; tables none; surface paths added none, removed none; shape hints: none.
This pass adds `MOVE_NOTE` to `names`, which `record` already imports (`scripts/record.py:20`), and a `git show` call inside `record`, which already runs git through `subprocess` (`scripts/record.py:15`). No new edge.

## What the suite asserts after

- `xv record move --slice-only` refuses a sentence, a broken name, a name in backticks, `Red::test_x[1]` and `;`, exits non-zero with "must be the test's name … bracket", and records nothing. It takes each of the six forms and each of the four bracket notes, and a plain move still takes any words (`tests/test_record.py:1507`).
- New: it refuses `Red.test_milk_todya`, `test_milk_todya`, `Red.test_milk_todya (removed)`, `Other.test_milk_today` and `tests/test_red.py::Other::test_milk_today` when the committed file holds only `Red.test_milk_today`, and records nothing. It refuses any name when the file was not committed. It takes `Red.test_milk_today` and `test_milk_today (removed)` after the test has left the working tree, because it is still in HEAD (`tests/test_record.py:1532`–`1557`).
- `record.removals_not_made` stops on every table input while the test is there, stops "could not be read" on every non-name input even when the test is gone, passes a name with a note once the test is gone, and never reads a name out of the note (`tests/test_record.py:1598`).
- A packet with `change_misses_scenario: no` and a listed miss stops for the originator, and the question names both. A packet with "None." under the heading does not (`tests/test_record.py:1424`).
- The cleaner brief holds "as it is written in the file" and "optional note in brackets" (`tests/test_record.py:1644`).

## 1. Shape

shape_change: no.
- The boundary picture shows no module, edge, table, outbound call or surface added or removed, and no shape hints (`.xv/slices/2026-11-18-move-names.boundary.md`, "Shape hints: none").
- This pass: `scripts/names.py:65` splits `MOVE_NOTE` out of `MOVE_NAME`, and `scripts/record.py:258` reads the file with `git show HEAD:<file>` inside `cmd_move`. `record` already imports `names` and runs git (`.xv/picture.md:43`). Inside the current shape.
- From the first pass, unchanged: `scripts/orders.py:338` fires the existing `change_misses_scenario` order for the originator. Stop rules stay in `orders` (`.xv/picture.md:60`).

shape_breadth: narrow, as the forecast expected ("the move-name parser and removal check, one table test, the cleaner brief and one CHANGELOG line").

## 2. Pitch

pitch_contradiction: no.
The pitch says the system makes it easy "to vibe with discipline" (`.xv/pitch.md:7`). A move that must name a test the file held is that discipline.
I found nothing in "Who it is not for" (`.xv/pitch.md:25`) that this pass touches.

## 3. Moved tests

The record holds 12 `moved_tests` entries, but only 6 distinct moves: each move is told twice, in different words (21:11:0x and 21:11:15 from the first pass; 21:21:49 and 21:21:54, "lines added" and "added lines", from this pass).
`moves_to_accept` counts by file and assertion (`.xv/picture.md:69`), so the person sees 12 to accept.
`xv wall diff` (baseline now `865d4fd`): `tests/test_record.py` 498 → 498 assertions, `fewer_assertions` empty.
Because the wall baseline moved to `865d4fd`, `xv wall diff` no longer shows the first pass's `tests/test_run.py` changes. They are still in the record and in the table below.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (this pass) | `SliceOnlyMoveTest` ×2 (`:307`, `:316`), `SliceOnlyGateTest.listed` and `test_with_nothing_listed` (`:428`, `:444`), `WallChoicesTest` ×2 (`:1016`, `:1024`), `OneHomeRecordTest` (`:1700`) recorded slice-only moves on files not in git | each setup first commits a file that holds the name (`commit_tests`, `tests/test_record.py:11`); no assertion changed | the command now refuses a name not in the file at the step's start | Yes. Outcome 1's file check refuses a name whose file is not in HEAD. Setup only. |
| `tests/test_record.py` | `test_a_move_whose_assertion_starts_with_the_marked_name_keeps_the_flag` records `test_file_is_ts; removed` | `test_file_is_ts (removed)`; same `assertIs(... True)` | outcome 1 refuses a sentence | Yes. The record names the class `SliceOnlyGateTest`, but the test is in `WallChoicesTest` (`tests/test_record.py:970`, `:1016`). |
| `tests/test_record.py` | `test_a_move_of_another_test_does_not_get_the_flag` records `test_other; removed` | `test_other (removed)`; same `assertFalse` | same | Yes; same misnamed class (`tests/test_record.py:1024`). |
| `tests/test_run.py:2292` | `…_names_a_double_colon_test_still_there_stops` recorded the sentence and asserted the removal stop | asserts the command refuses ("must be the test's name") | outcome 1 refuses at the command | Yes, but it now asserts something different, and its name no longer says what it checks. No test asserts the end-to-end stop for a `Class::name` move whose test is still there. |
| `tests/test_run.py:2300` | `prose_move` used `xv record move --slice-only` | uses `xv record add … moved_tests` with `slice_only: true`; same `assert_removal_stop` | the other route still reaches the check | Yes. |
| `tests/test_run.py:1810`–`1820` | `RemovedSliceOnlyTestInCoversTest`, 3 tests, `Red.test_cheese; removed` | `… (removed)`; same assertions | the check no longer reads a sentence | Yes (`scripts/run.py:1279`). The name `…_words_after_the_semicolon_name_another_test` no longer fits the data. |

No test asserts less, except the `::` case in row 4, which lost its end-to-end stop.
Slice-only tests removed: none (record `slice_only: []`). Kept: none.
May-not files the scenario report allowed (`may_not_files_needed`): none.

## Findings for the person who set the work going

- **The file check finds a word, not a test.** `cmd_move` passes the name to `covered_name_found` (`scripts/record.py:262`), which needs only each part to be a whole word in the file, in order (`scripts/names.py:30`–`37`).
  In the red's file (`tests/test_record.py:1523`), `Red.pass (removed)` and `unittest.TestCase` would be taken, and so would a mistyped name that happens to appear in a comment.
  Outcome 1 says "names a test that was in that file".
  I did not call this a miss: the typo, wrong-class and missing-file cases the earlier miss named are now refused, and matching a whole word anywhere in the file is how the picture already reads a name (`.xv/picture.md:53`).
  Whether "a test" should mean a `def`/`it` name is for a person to decide.
- **A pairing can trip the file check.** The check reads `HEAD` as "when the step began" (`scripts/record.py:258`).
  In a pairing the watch commits as it works and records moves with `xv record move` (`skills/watch/SKILL.md:88`).
  If a slice-only removal is committed before its move is recorded, the name is no longer in `HEAD`, and the command refuses a true move.
  The same happens to any agent that commits during its step.
- **The CHANGELOG line does not mention the file check.** `CHANGELOG.md:7` says the command takes a name in one of the forms. It does not say that the name must be in the file at the step's start, which `scripts/record.py:257`–`263` now refuses on.
  Decision 1 asks for a CHANGELOG line for each change to a check (`.xv/picture.md:324`). The line has one name, and the CHANGELOG calls a line without two names a draft (`CHANGELOG.md:3`).
- **JS/TS titles are refused** (unchanged from the first pass). `MOVE_NAME` ends in `(?P<name>\w+)` (`scripts/names.py:66`), so `milk > shows milk running out today` is refused.
  #183 says the check finds "an `it("…")` title" (`CHANGELOG.md:14`), and the new cleaner brief asks for "the test's name as it is written in the file" (`skills/cleaner/SKILL.md:39`).
  This is not a scenario line, since outcome 1's forms are word names. Whether titles should be a form is a person's call.
- **The watch brief's stop table is incomplete** (unchanged). `skills/watch/SKILL.md:119` lists `change_misses_scenario` only for `yes`. The new firing for `no` with a listed miss (`scripts/orders.py:338`) is not there.
- **A comment overstates.** The comment at `scripts/record.py:261` says "a path prefix is read only in the `file::` form", but `Class::name` matches `[\w./]+::` too, so `key` is the file for it as well. The check is harmless unless the class has the same name as the file's stem.

## 4. The picture

picture_change: yes. Proposed edits; the person who set the work going accepts them.

- `.xv/picture.md:43` is incomplete. Proposed:
  `names` holds `covered_name_found`, `COVERED_SEPARATOR`, `joined_unsafely`, `MOVE_NOTE` and `move_test_name`, which `record` and `run` import.
- `.xv/picture.md:51`–`52` are now untrue for moves (`scripts/record.py:958`). Proposed in their place:
  It reads a move's assertion with `names.move_test_name`: one of `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`, with an optional note in brackets that is not read.
  It never reads a sentence for a name; an assertion in no such form cannot be read.
- `.xv/picture.md:73` is incomplete (`scripts/record.py:253`–`263`). Proposed, after it:
  `xv record move --slice-only` refuses an assertion that `names.move_test_name` cannot read, and records nothing.
  It also refuses a name that `names.covered_name_found` does not find in the file as committed at `HEAD`, the step's start.
- `.xv/picture.md:101` is incomplete (`scripts/orders.py:338`). Proposed, after it:
  A packet whose front matter says `change_misses_scenario: no` while its `## Scenario misses` section lists a miss stops for the originator under `change_misses_scenario`, naming the disagreement.
- `.xv/picture.md:219` is now untrue (`scripts/run.py:1279`). Proposed:
  A `covered` name whose last part is a slice-only test that the cleaner removed by a recorded move does not stop; the move's name is read with `names.move_test_name`.

## 5. The wall

I looked at the three new tests in `SliceOnlyAssertionFormTest` (`tests/test_record.py:1532`–`1557`), the `commit_tests` setup changes, and the first pass's tests.
- `tests/test_run.py`, `RemovalNotMadeTest.test_a_slice_only_move_whose_assertion_names_a_double_colon_test_still_there_stops`: remove from the wall (as on the first pass; not yet accepted). Outcome 2 makes its subject dead. Its rewritten body (`tests/test_run.py:2292`–`2298`) only repeats the refusal that `SliceOnlyAssertionFormTest.test_a_sentence_or_a_broken_name_is_refused_and_nothing_is_recorded` asserts over a table (`tests/test_record.py:1559`).
No new test needs to be marked slice-only, because the three new tests guard a refusal that goes on after the slice.

## Scenario misses

None.
Outcome 1's "names a test that was in that file when the step began" is now checked (`scripts/record.py:257`–`263`) and tested (`tests/test_record.py:1532`–`1557`). Outcomes 2–5 are as on the first pass, and the red covers them. Outcome 6's line is at `CHANGELOG.md:7`.

## Door

**Door:** two-way. A revert restores the old parser and stop; no data is migrated, and old records are read as before. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-18-move-names.md`
- Diff: `git diff 8e366c9ba6c94b28cbedfad1e5221c22bf914dda..HEAD`; this pass: `git diff ebd150e51599..HEAD`
- Wall: `xv wall diff 2026-11-18-move-names` (baseline `865d4fd`)
- Boundary: `.xv/slices/2026-11-18-move-names.boundary.md`
- Red run by the guardian: 18 tests, OK. Whole suite run by the guardian (`python3 tests/run.py`): 1402 tests, OK.

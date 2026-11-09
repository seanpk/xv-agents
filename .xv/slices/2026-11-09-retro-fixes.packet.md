---
shape_change: no
shape_breadth: narrow
pitch_contradiction: no
scenario_miss: yes
expected_moves: 0
door: two-way
---

# Packet: 2026-11-09-retro-fixes

## Needs a decision

1. **The CHANGELOG states a change the slice does not make.**
   This is a scenario miss: see below.
2. **A `not_covered` item a person sent back is not asked about again.**
   This is a finding for the person who set the work going, not a miss: the code meets point 4 as worded.
   `scripts/run.py:1113-1116` drops any `not_covered` item named in an answered `red_misses_scenario` stop, including one whose answer sent the slice back (`sent_back: true`).
   The `red_gaps` check next to it keeps sent-back stops asking (`scripts/run.py:1254`: `and not s.get("sent_back")`; `.xv/picture.md:84`: "a gap named in an answered `red_misses_scenario` stop that was not sent back").
   The new test locks this in.
   `tests/test_run.py:1417-1421` uses `send_back_to_the_scenario`, which answers `--next scenario --settled "Pat said to cover the grocer share."` (`tests/test_run.py:1396-1397`).
   It then asserts that the same item, reported `not_covered` again, goes on to the maker.
   So a person who asked for coverage gets no stop when the agent still does not cover it.
   Decide whether point 4 should have said "answered and not sent back".
   That would be an amendment.
3. **On a slice from a build, the wall no longer catches a test removed after the red when its file existed at the base.**
   `scripts/wall.py:136-138` keeps a file in `unrecorded` only when it lost or changed a line that was at the slice's *base* (`removed_lines(root, data["base"], f, None)`).
   On a build slice, the wall baseline is hashed at the base *with the red* (`.xv/picture.md:164`).
   A red test, or a test the build added, that the maker or the cleaner later deletes from a file that existed at the base leaves no `-` line against the base.
   That file drops out of `unrecorded`, and `unrecorded_move` does not fire.
   On a slice with no build, the same deletion still fires.
   Point 1 speaks only of what *the build* added.
   The filter applies to any later change, by anyone, to any changed file on a build slice.
   No test covers a maker deletion on a build slice: `BuildAddedTestsTest` (`tests/test_from_build.py:722-766`, ending before `RecordCopyTest` at `:769`) only varies what the build did.
   This is a finding, not a miss: no scenario line or binding decision names it.
4. **Decision 1 needs two people; the CHANGELOG line says one.**
   `.xv/picture.md:274`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
   This slice changes the scenario brief (`skills/scenario/SKILL.md:37-38`), and it changes the `unrecorded_move` and `red_misses_scenario` checks (`scripts/wall.py:136`, `scripts/run.py:1113`).
   `CHANGELOG.md:7` ends "Decided by Sean, solo."
   Earlier lines say the same, so this follows practice.
   The second person comes at review, if anywhere.

## Scenario misses

- Point 7 (read with amendment 8). evidence: `CHANGELOG.md:7` misstates the tool change.
  It says "`xv record move --slice-only` marks the move whether or not the test is in `slice_only`".
  Amendment 8 drops point 3 and keeps the gate.
  `scripts/record.py` is unchanged from the base (`git diff 4f6dcb7..HEAD --stat` does not list it), so the line describes a tool change that is not there.
  It also cites #173, which the answer at 16:43:54 closed "as working as designed".
  The removed slice-only CHANGELOG test asked for `#173` in the Unreleased section (wall baseline `302cb36`, `tests/test_record.py:247-248`), which is why the claim stayed.
  to: maker.
  amend: no.

## The scenario in words

On a slice from a build, a test file that the build only added tests to is not an unrecorded move.
One where the build changed or removed a line from the base still stops (points 1 and 2, #172).
Point 3 (`--slice-only` marks any move) was dropped by amendment 8: the gate stays.
A `not_covered` item already answered at a `red_misses_scenario` stop does not stop again; a new one does (point 4, #174).
The scenario brief gains two rules: a red that fails only on the build is reported without a stop, and the red runs in the foreground, to its end, before the report (points 5 and 6).
`CHANGELOG.md` has a line for the change (point 7).

## Recording

None. The slice is a defect that starts from words, and the record has no recording.
To replay it, run the red: `cd tests && python3 -m unittest test_record.SliceOnlyGateTest test_record.WallChoicesTest test_record.ScenarioBriefRetroFixesTest test_from_build test_run.ScenarioChecksTest`.

## Boundary picture

From `.xv/slices/2026-11-09-retro-fixes.boundary.md`: two modules touched (`scripts/run`, `scripts/wall`).
No module, edge, outbound call, table or surface path is added or removed.
Shape hints: none.

## What the suite asserts after the change

I ran the red on HEAD: 124 tests, OK.
I did not run the whole suite again; the cleaner's run (record, 17:12:03) reports 1170 tests green.

- On a build slice, a build that only adds a test to `tests/test_store.py` gives no stop naming it, and `xv wall check` leaves it out of `unrecorded` (`tests/test_from_build.py:751`).
- On a build slice, a build that changes a line, or removes one, from that file stops once with `unrecorded_move` (`tests/test_from_build.py:757`, `:763`).
- `xv record move` with no `--slice-only` leaves no `slice_only` key on the move (`tests/test_record.py:211`).
- The gate holds: `--slice-only` on a test that is not listed is a plain move (`SliceOnlyGateTest`, `WallChoicesTest.test_a_move_of_another_test_does_not_get_the_flag`, unchanged from the base).
- A `not_covered` item answered (and sent back) earlier does not stop again, and a new item stops by itself (`tests/test_run.py:1417`, `:1423`).
- The scenario brief has a line about a red that fails only on the build, and one about running the red in the foreground (`tests/test_record.py:227`, `:233`).
- Nothing asserts the CHANGELOG line any more: its slice-only test was removed.

## Moved tests

`xv wall diff`: one file changed, `tests/test_record.py`, with 477 assertions before and 473 after, measured from the wall baseline `302cb36`, which holds the red.
Both removals are of tests the slice added.
Against the base, no old test or assertion changed: `git diff 4f6dcb7..HEAD -- tests/` only adds lines.

1. `MoveSliceOnlyTest.test_slice_only_on_a_test_not_in_the_slice_only_list_marks_the_move` (`tests/test_record.py:210-217` at the wall baseline `302cb36`).
   Before: it asserted `moved_tests[0].slice_only is True` after `--slice-only` on an unlisted test.
   After: removed.
   The edit was directed by Sean Kennedy (test-remove, answer at 16:57:44), and the record holds it.
   Amendment 8 forces it: the test is point 3's red, and point 3 is dropped.
   It asserts less only for the dropped behaviour.
2. Slice-only removals: `test_record.py::ScenarioBriefRetroFixesTest.test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes` (by the cleaner, recorded, accepted by the watch because it checks `CHANGELOG.md`).
   No slice-only test was kept.

The scenario agent's report lists no `may_not_files`.

## The five checks

1. **Shape.** No change.
   The boundary picture adds no module or edge and has no shape hints.
   The two touched modules already hold this work: `.xv/picture.md:84` puts the test hash check in `wall`, and `.xv/picture.md:172` puts the `red_misses_scenario` check after the scenario step in `run`.
   Breadth: narrow, as the forecast expected ("shape": "narrow").
2. **Pitch.** No contradiction.
   Silence in the pitch is not a contradiction, and the change only narrows when a stop fires.
   `.xv/pitch.md:7` ("to vibe with discipline") is the line it is closest to.
   Finding 3 weakens one guard on build slices, but the pitch names no guard.
3. **Moved tests.** Above.
   One recorded directed removal, forced by amendment 8, and one slice-only removal.
   No old test asserts less.
   No unrecorded change.
4. **The picture.** Proposed edits, for the person who set the work going:
   - After `.xv/picture.md:172`, add this line, indented two spaces like its neighbours:

     > A `not_covered` item named in an earlier answered `red_misses_scenario` stop does not stop again, whether or not that answer sent the slice back (`run.post_step`).

     If finding 2 is fixed, the clause becomes "that was not sent back".
   - After `.xv/picture.md:182` ("In a slice from a build, a test file the build changed stops once."), add this line, indented two spaces:

     > In a slice from a build, a test file that changed after the red is unrecorded only when it lost or changed a line that was at the base (`wall.check`).

     If finding 3 is fixed, this line changes with the fix.
   - The scenario brief's two new rules need no picture edit: the picture points to the briefs and does not restate them.
5. **The wall.** One recommendation.
   - `tests/test_record.py` `MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked`: mark slice-only.
     The scenario report lists it under item 3 only (`covers_kept`: `{"item": "3", "test": [..., "MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked"]}`), and amendment 8 drops point 3.
     It was point 3's control case, a move with no flag (`tests/test_record.py:211-216`), and it guards nothing that a later slice needs.
     The flag behaviour that stays is asserted by `SliceOnlyGateTest` (`tests/test_record.py:419-447`), which passes `--slice-only` on every move.
     The class it leaves behind is one test under a blank line (`tests/test_record.py:209-210`).

## The door

Two-way door: a revert undoes it; no data, contract or user message changes. Blast radius: low.

## Raw data

- Diff: `git diff 4f6dcb707076f9b7a130b27302e6cafdd92e73e1..HEAD`.
- Boundary: `.xv/slices/2026-11-09-retro-fixes.boundary.md`.
- Wall: `xv wall diff 2026-11-09-retro-fixes`; baseline `.xv/slices/2026-11-09-retro-fixes.wall.json`.
- Record: `.xv/slices/2026-11-09-retro-fixes.md` (stops at 16:39:46, 16:47:38 and 16:56:03; cleaner report at 17:12:03).

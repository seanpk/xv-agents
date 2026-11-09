---
slice: 2026-11-09-retro-fixes
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet: Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled

This is the second guardian pass.
Last pass's scenario miss (point 7) is closed: `CHANGELOG.md:7` now says "`xv record move --slice-only` keeps its gate, so a test not in `slice_only` stays a plain move (#173 dropped)", and `scripts/record.py` does not change from the base.
No stop fires.
The merge is Sean's call. Three findings from the last pass still stand, and Sean should decide on them:

1. **A `not_covered` item a person sent back is not asked about again.**
   `scripts/run.py:1113-1116` drops any `not_covered` item named in an answered `red_misses_scenario` stop, including one whose answer sent the slice back.
   The `red_gaps` check next to it skips sent-back stops (`scripts/run.py:1254`: `... and s.get("answer") and not s.get("sent_back")`; `.xv/picture.md:84`: "a gap named in an answered `red_misses_scenario` stop that was not sent back").
   The new test locks this in: `tests/test_run.py:1417-1421` first calls `send_back_to_the_scenario`, which answers `--next scenario` (`tests/test_run.py:1396-1397`), and `scripts/record.py:546-553` marks that answer `sent_back: true`.
   The test then asserts that the same item, reported `not_covered` again, goes on to the maker.
   So a person who asked for coverage gets no stop when the agent still does not cover it.
   Point 4 says "a `not_covered` item that a person already answered", so the code meets it as written.
   To change this, amend the scenario to say "answered and not sent back".
2. **On a build slice, the wall stops catching a later removal of a test that was added after the base.**
   `scripts/wall.py:136-138` keeps a file in `unrecorded` only when it lost or changed a line that existed at the slice's *base* (`removed_lines(root, data["base"], f, None)`).
   On a build slice, the wall baseline is hashed after the red (`.xv/picture.md:164`).
   Say the maker or the cleaner later deletes a red test, or a test the build added, from a file that existed at the base.
   The deletion leaves no `-` line against the base, so the file drops out of `unrecorded` and `unrecorded_move` does not fire.
   On a slice with no build, the same deletion still fires.
   Point 1 is only about what *the build* added, but the filter applies to every later change to that file, whoever makes it.
   No test covers a deletion by the maker on a build slice: `BuildAddedTestsTest` (`tests/test_from_build.py:722-766`) only varies what the build did.
3. **Decision 1 calls for two people, but the CHANGELOG line names one.**
   `.xv/picture.md:274`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
   The slice changes the scenario brief (`skills/scenario/SKILL.md:37-38`) and the `unrecorded_move` and `red_misses_scenario` checks (`scripts/wall.py:136`, `scripts/run.py:1113`).
   `CHANGELOG.md:7` ends "Decided by Sean, solo."
   The earlier CHANGELOG lines say the same thing, so this follows the usual practice.

## The scenario

1. On a build slice, a test file that the build only added tests to is not an unrecorded move.
2. A test file where the build changed or removed a line from the base still stops (#172).
3. Point 3 (`--slice-only` marks any move, #173) is dropped by amendment 8. The slice-only gate stays.
4. A `not_covered` item that was answered at an earlier `red_misses_scenario` stop does not stop again. A new item still stops (#174).
5. The scenario brief now says that a red failing only on the build gets reported without a stop.
6. The brief also says to run the red in the foreground, to its end, before the report (#174).
7. `CHANGELOG.md` has a line for these changes.

The slice may ignore files under the test paths that are not tests, such as `tests/run.py`.

## The recording

There is no recording: this defect slice starts from words.
To replay it, run the red: `cd tests && python3 -m unittest test_record.SliceOnlyGateTest test_record.WallChoicesTest test_record.ScenarioBriefRetroFixesTest test_from_build test_run.ScenarioChecksTest`.
On HEAD `d2d5cef` this pass, it ran 124 tests: OK.
I did not run the whole suite. The cleaner's run (record, 17:26:41) reports 1170 tests green.

## The boundary picture

From `.xv/slices/2026-11-09-retro-fixes.boundary.md`: two modules touched (`scripts/run`, `scripts/wall`).
No module, edge, outbound call, table or user surface is added or removed.
Shape hints: none.

## What the suite asserts after

- On a build slice, a build that only adds a test to `tests/test_store.py` gets no stop naming that file, and `xv wall check` leaves it out of `unrecorded` (`tests/test_from_build.py:751`).
- On a build slice, a build that changes or removes a line in that file stops once with `unrecorded_move` (`tests/test_from_build.py:757`, `:763`).
- `xv record move` without `--slice-only` puts no `slice_only` key on the move (`tests/test_record.py:211`).
- The gate holds: `--slice-only` on a test that is not listed gives a plain move (`SliceOnlyGateTest` at `tests/test_record.py:416`, and `WallChoicesTest.test_a_move_of_another_test_does_not_get_the_flag` at `:1016`; both unchanged from the base).
- A `not_covered` item that was answered (and sent back) earlier does not stop again, and a new item stops by itself (`tests/test_run.py:1417`, `:1423`).
- The scenario brief has a line about a red that fails only on the build, and a line about running the red in the foreground (`tests/test_record.py:227`, `:233`).
- Nothing asserts the CHANGELOG line any more, because its slice-only test was removed.

## 1. Shape

shape_change: no.
The boundary picture adds no module or edge and has no shape hints.
Both touched modules already do this work: `.xv/picture.md:84` puts the test hash check in `wall`, and `.xv/picture.md:172` puts the `red_misses_scenario` check after the scenario step in `run`.
Breadth: narrow, as the forecast expected (`"shape": "narrow"`).

## 2. Pitch

pitch_contradiction: no.
The closest line is `.xv/pitch.md:7`: "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline."
The change only narrows when two stops fire.
Finding 2 weakens one guard on build slices, but the pitch names no guard. The pitch says nothing on this, and silence is not a contradiction.

## 3. Moved tests

`xv wall diff 2026-11-09-retro-fixes`: one file changed, `tests/test_record.py`, with 477 assertions before and 473 after. This is measured from the wall baseline `302cb36`, which holds the red.
Measured from the base, no old test changed: `git diff 4f6dcb7..HEAD -- tests/` only adds lines.

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `MoveSliceOnlyTest.test_slice_only_on_a_test_not_in_the_slice_only_list_marks_the_move` asserted `moved_tests[0].slice_only is True` after `--slice-only` on an unlisted test | removed | "directed by Sean Kennedy: test-remove" (answer at 16:57:44) | Yes. It was point 3's red, and amendment 8 drops point 3. It asserts less only about the dropped behaviour. |

Slice-only tests removed: `tests/test_record.py::ScenarioBriefRetroFixesTest.test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes` (removed by the cleaner and recorded; the watch accepted it because it checks `CHANGELOG.md`). Kept: none.
The scenario agent's report lists no `may_not_files` (record: `may_not_files: []`).

## 4. The picture

Proposed edits, for Sean to accept or decline:

- After `.xv/picture.md:172`, add this line, indented two spaces like the lines around it:

  > A `not_covered` item named in an earlier answered `red_misses_scenario` stop does not stop again, whether or not that answer sent the slice back (`run.post_step`).

  If finding 1 is fixed, the clause becomes "that was not sent back".
- After `.xv/picture.md:182` ("In a slice from a build, a test file the build changed stops once."), add this line, indented two spaces:

  > In a slice from a build, a changed test file is unrecorded only when it lost or changed a line that was at the base (`wall.check`).

  If finding 2 is fixed, this line changes with the fix.
- The two new rules in the scenario brief (`skills/scenario/SKILL.md:37-38`) need no picture edit, because the picture points to the briefs and does not repeat them.

## 5. The wall

- `tests/test_record.py` `MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked`: mark slice-only.
  The scenario report lists it only under item 3 (`covers_kept`: `{"item": "3", "test": [..., "MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked"]}`), and amendment 8 drops point 3.
  It was point 3's control case, a move with no flag (`tests/test_record.py:209-216`).
  The flag behaviour that stays is asserted by `SliceOnlyGateTest` (`tests/test_record.py:416`).
  The last pass made the same recommendation, and the record has it as `accepted: false`. I repeat it so Sean can decide again.

I also looked at `BuildAddedTestsTest` (`tests/test_from_build.py:722`), the two new `ScenarioChecksTest` tests (`tests/test_run.py:1417`, `:1423`), and `ScenarioBriefRetroFixesTest`'s two brief tests (`tests/test_record.py:227`, `:233`).
They guard behaviour that lasts, so they stay on the wall.

## Door

**Door:** two-way. A revert undoes it; no data, contract or message to users changes. **Blast radius:** low.

## Raw data

- Slice record: `.xv/slices/2026-11-09-retro-fixes.md` (stops at 16:39:46, 16:47:38, 16:56:03 and 17:19:10)
- Diff: `git diff 4f6dcb707076f9b7a130b27302e6cafdd92e73e1..d2d5cef`
- Wall: `xv wall diff 2026-11-09-retro-fixes`; baseline `.xv/slices/2026-11-09-retro-fixes.wall.json`
- Boundary: `xv boundary --base 4f6dcb707076f9b7a130b27302e6cafdd92e73e1`

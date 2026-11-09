---
slice: 2026-11-09-retro-fixes
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 3
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet: Build-added tests are not moves, slice-only moves are marked, and a settled point stays settled

This is the third guardian pass, after amendments 9 and 10.
No shape or pitch stop fires.
One scenario miss sends the slice back: the CHANGELOG line still describes the behaviour from before amendments 9 and 10.
The two code findings from the last pass are closed by amendments 9 and 10 (see Scenario misses and check 4).
Decision 1's two-people rule is still open for Sean (see Needs a decision).

## Scenario misses

   Evidence: `CHANGELOG.md:7` says "a `not_covered` item a person answered at a `red_misses_scenario` stop does not stop again on a later pass".
   Amendment 9 says the item still stops when that answer sent the slice back, and `scripts/run.py:1113-1114` now skips sent-back stops (`... and s.get("answer") and not s.get("sent_back")`).
   The same line says "a test file the build only added tests to is not an unrecorded move", with no mention of amendment 10: a later change or removal of a build-added test by the maker or the cleaner still stops (`scripts/wall.py:136-141`, `scripts/record.py:792-801`).
   No red test covers the line, because the CHANGELOG test was removed as slice-only.

## Needs a decision

- **Decision 1 asks for two people, and the CHANGELOG line names one.**
  `.xv/picture.md:273`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
  The slice changes the scenario brief (`skills/scenario/SKILL.md:37-38`) and the `unrecorded_move` and `red_misses_scenario` checks (`scripts/wall.py:136`, `scripts/record.py:792`, `scripts/run.py:1113`).
  `CHANGELOG.md:7` ends "Decided by Sean, solo."
  The log shows Sean asked "should we do it as a pair instead?" and then chose "ok, agents" (`.xv/slices/2026-11-09-retro-fixes.md`, Log, 18:19 and 18:24).
  Whether the second person signs off is Sean's call, not an agent's.
  It is not listed as a miss because no maker or scenario change can meet it.

## The scenario

Points 1, 2, 4, 5, 6 and 7 as written, with these amendments: point 3 is dropped and the `--slice-only` gate stays (8); a sent-back `not_covered` item stops again (9); the build exemption covers only lines the build added, and a later change by the maker or the cleaner stops (10).

## The recording

None. A feature starts from words.
To replay it, run `cd tests && python3 -m unittest test_run.ScenarioChecksTest test_from_build.BuildAddedTestsTest`.

## The boundary picture

From `.xv/slices/2026-11-09-retro-fixes.boundary.md`: touched `scripts/record`, `scripts/run`, `scripts/wall`.
Nothing is added or removed: no modules, edges, tables or surface paths.
Shape hints: none.

## What the suite asserts after

`python3 tests/run.py --jobs 4`: 1175 tests, OK (run on this pass).
- On a build slice, a test file the build only added to is not unrecorded, and one where the build changed or removed a base line stops (`tests/test_from_build.py` `BuildAddedTestsTest`, first three tests).
- If the maker or the cleaner changes or removes a build-added test, that stops with `unrecorded_move`, and the wall names the file (the same class, its last five tests).
- A `not_covered` item answered without a send-back is not asked again, the same item after a send-back stops again, and a new item still stops (`tests/test_run.py:1416-1445`).
- The scenario brief has the build-only red line and the foreground line (`tests/test_record.py:209-226`).
- The `--slice-only` gate is unchanged: `scripts/record.py` changes only `wall_for_build` and `apply_verdict`, and `SliceOnlyGateTest` is not in the wall diff.

## 1. Shape

The boundary picture lists no added module, edge, table or surface, and no shape hints.
The new `blobs` field on an `unrecorded_move` stop (`scripts/record.py:925`) is a key inside the existing record's `stops`, not a new table.
`shape_change: no`, and `shape_breadth: narrow` matches the forecast's `"shape": "narrow"`.

## 2. Pitch

I checked the slice against `.xv/pitch.md:23-25` ("Who it is not for, and what it will never do").
These are internal check fixes that make `unrecorded_move` stop in more cases and `red_misses_scenario` in fewer, and nothing in them serves anyone the pitch excludes.
`pitch_contradiction: no`.

## 3. Moved tests

No test that existed at the base changed: `git diff 4f6dcb7..HEAD -- tests/test_record.py` only adds lines.
`xv wall diff` shows `tests/test_record.py` with 473 assertions before and 472 after, against the baseline `efbe4bb`.
The three recorded moves all remove tests this slice added:
- `MoveSliceOnlyTest.test_slice_only_on_a_test_not_in_the_slice_only_list_marks_the_move` was removed (`.xv/slices/2026-11-09-retro-fixes.md:17`). Sean directed it ("test-remove"). Amendment 8 drops point 3, which forces this.
- Slice-only removals (`.xv/slices/2026-11-09-retro-fixes.md:18`): `test_the_changelog_has_a_line_for_the_brief_change_and_the_tool_changes` (cleaner, CHANGELOG-only) and `MoveSliceOnlyTest.test_a_move_without_the_flag_is_not_marked` (cleaner, the 472-assertion drop, accepted wall recommendation). No slice-only test was kept.
- `old_tests_forced` names two `ScenarioChecksTest` tests whose setup changed for amendment 9 (`tests/test_run.py:1416-1430`). Both were added in this slice, and their assertions are unchanged.
- May-not files allowed by the scenario agent: none (`.xv/slices/2026-11-09-retro-fixes.md:32`, `may_not_files: []`).

## 4. The picture

Proposed edits, for Sean to accept or decline:

- After `.xv/picture.md:172`, add this line, indented two spaces like the lines around it:

  A `not_covered` item named in an earlier answered `red_misses_scenario` stop does not stop again, unless that answer sent the slice back (`sent_back`).

- Replace `.xv/picture.md:182` ("In a slice from a build, a test file the build changed stops once.") with these lines:

  In a slice from a build, a test file the build only added lines to is not unrecorded; a line the build changed or removed at the base still stops.
  A line the build added that the maker or the cleaner later changes or removes stops too, measured from the build's commit (`scripts/wall.py:136`).
  An answered `unrecorded_move` stop records each file's content (`blobs`), and the same content does not stop again.

## 5. The wall

No recommendations.
I looked at the new tests in `BuildAddedTestsTest`, in `ScenarioChecksTest` (`tests/test_run.py:1416-1445`) and in `ScenarioBriefRetroFixesTest` (`tests/test_record.py:209-226`).
Each one guards behaviour or a brief line that stays, and the brief-line tests sit alongside the existing `ScenarioBriefTest`.
The one slice-only recommendation from earlier was already accepted and applied.

## Door

Two-way door: a revert of `scripts/wall.py`, `scripts/record.py` and `scripts/run.py` undoes it, and no data migrates. Blast radius: low.

## Raw data

- Record: `.xv/slices/2026-11-09-retro-fixes.md`
- Boundary: `.xv/slices/2026-11-09-retro-fixes.boundary.md`
- Wall: `xv wall diff 2026-11-09-retro-fixes`, `.xv/slices/2026-11-09-retro-fixes.wall.json`
- Diff: `git diff 4f6dcb707076f9b7a130b27302e6cafdd92e73e1..HEAD`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- 1. Point 7, read with amendments 9 and 10, `to: maker`: `scripts/run.py:1114` and `scripts/wall.py:136` changed, and `CHANGELOG.md:7` was not updated to match.

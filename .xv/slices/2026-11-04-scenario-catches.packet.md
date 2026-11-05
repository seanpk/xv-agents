---
slice: 2026-11-04-scenario-catches
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: briefs
---

# Packet: The scenario agent catches more before the maker starts: #119, with #110 and #111

**For Sean (no stop):** the miss from the last pass is closed. The maker brief, its prompt, scenario rule 6d and the CHANGELOG line now let the maker change only `.xv/picture.md` from its may-not list, which matches the code and amendment 7. Three things need a decision: three picture edits (§4), one note on the scenario brief's covers wording (§3), and two slice-only marks to confirm (§5).

## The scenario

There are six points and three amendment points. (1) The scenario agent marks a test that only checks a one-time wording change as slice-only. (2a) Its report names each old test the red forces to change. The maker may change a named test without stopping, and records the move. (2b) Its report names the may-not files the red needs changed, and the guardian lists those changes. (3) The scenario agent writes a red case for each way a value can be wrong, plus a case where a read-only agent claims what only a person may give. (4) Each amendment the watch drafts names four things. (5) A `covers` item may name a point by its number. (6) `CHANGELOG.md` has a line for each brief change. Sean's amendment: (7) from the may-not list the maker may change only `.xv/picture.md`, and only when the report names it. (8) Each scenario report sets both lists again. (9) A number in `covers` names only the scenario's own point.
May ignore: the cleaner, naming an amendment's points by number, and old slice records.

## The recording

None, because this is a feature. Replay the red with `cd tests && python3 -m unittest test_run.NamedByTheScenarioReachTheMakerTest test_run.WatchLoopTest test_briefs_picture`. I ran it at HEAD `2a7d181` and got `Ran 133 tests … OK`. I also ran the whole suite (`cd tests && python3 -m unittest -q`) and got `Ran 929 tests … OK`.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-scenario-catches.boundary.md`): it touched `scripts/prompt`, `scripts/record` and `scripts/run`. No module, edge, outbound call, table or surface path was added or removed. Shape hints: none.

## What the suite asserts after

- `record.apply_report` keeps a scenario report's `old_tests_forced` (file, test, why) and `may_not_files` (file, why). It drops malformed, empty and wrong-type entries, and any value that is not a list. A scenario report that leaves a list out clears it, and a maker's report sets neither list (`tests/test_run.py` `NamedByTheScenarioReachTheMakerTest`).
- The maker's prompt lists the named old tests and a named `.xv/picture.md`. It does not license a named `.xv/pitch.md` or `.xv/config.yml` (`test_the_makers_prompt_does_not_license_a_named_file_other_than_the_picture`). The cleaner's prompt lists neither.
- After the maker, a named `.xv/picture.md` is not `protected_changed`. A named pitch, config, rules or wall file still is.
- A `covers` item `"1"` or `"1. …"` covers only scenario point 1. It does not cover point 10, and it does not cover an amendment point with the same number (`WatchLoopTest`).
- The scenario, maker, guardian and watch briefs carry rules 1–4. The maker brief and scenario rule 6d say the maker may change "only `.xv/picture.md`" (`ScenarioCatchesTest`).

## 1. Shape

shape_change: no. The boundary picture has no shape hints and no new modules, edges, tables or surfaces. The new keys `old_tests_forced` and `may_not_files` (`scripts/record.py:482-486`) are front-matter fields in the slice record. The picture already names that record as state (`.xv/picture.md:26`, "State is files: `.xv/slices/<id>.md`"). shape_breadth: narrow, which matches the forecast's `shape: narrow`. The forecast's breadth did not name `record.py` or `prompt.py`. Each gained 5–7 lines from the 2a/2b send-back.

## 2. Pitch

pitch_contradiction: no. `.xv/pitch.md:11` says: "An agent may tidy it; it may not write it." The code exempts only the picture: `scripts/run.py:430`, "only the picture can be licensed; the other protected files stay a person's". The words now say the same: `skills/maker/SKILL.md:54`, "from this list you may change only `.xv/picture.md`", and `scripts/prompt.py:117`, `if e["file"] != ".xv/picture.md": continue`. Binding decision 1 (`.xv/picture.md:63`) says a may-not change needs two people and a CHANGELOG line. Both are met: Sean decided solo (`.xv/decisions/2026-11-04-2026-11-04-scenario-catches.md`), and the line is `CHANGELOG.md:7`.

## 3. Moved tests

No test that was there at the base changed. `git diff a6e023b..HEAD -- tests` only adds lines. `xv wall diff` shows nothing changed, added or deleted since baseline `060a026`.

Slice-only tests removed: `tests/test_briefs_picture.py::test_the_changelog_has_a_line_for_each_brief_change`. It was added in this slice, the cleaner removed it, and the move is recorded in `moved_tests`. Point 1 forces it. Kept: `ScenarioCatchesTest.test_the_changelog_does_not_say_the_maker_may_change_any_named_may_not_file`. It is still in the file and passes after a release, because it finds the line by its words, not under `## Unreleased`. It only guards this slice's rewording.

May-not file changes the report allowed: none. The diff does not touch `.xv/picture.md` or any other protected file.

Note (not a miss): `skills/scenario/SKILL.md:68` says "`"1"` matches point 1" next to "Each numbered point of the scenario and of each amendment must appear". It does not say what point 9 does: a number never covers an amendment's point (`scripts/run.py:529`). A scenario agent that writes `"7"` for amendment point 7 is sent back as `red_misses_point`. Sean may want the brief to say so.

## 4. The picture

- `.xv/picture.md:35`, "they do not edit it", is now untrue for the maker. Proposed: "The maker may edit `.xv/picture.md` only when the scenario report names it in `may_not_files`. No other protected file is exempt (`run.post_step`). The guardian lists the edit."
- `.xv/picture.md:23`: add "`record.apply_report` keeps a scenario report's `old_tests_forced` and `may_not_files`, and a report without them clears them. `prompt` shows them to the maker only, and only the picture from `may_not_files`."
- `.xv/picture.md:26`, on the covers check: add "A `covers` item that is a number, or starts with one, covers the scenario's own point with that number. It never covers an amendment's point (`run.missed_points`)."

## 5. The wall

I looked at the new cases in `WatchLoopTest`, `NamedByTheScenarioReachTheMakerTest` and `ScenarioCatchesTest`, and at the one removal.
- `tests/test_briefs_picture.py` `test_the_changelog_has_a_line_for_each_brief_change`: stay off the wall. It checks a one-time CHANGELOG line, it is already removed, and it is recorded in `slice_only` and `moved_tests`.
- `tests/test_briefs_picture.py` `ScenarioCatchesTest.test_the_changelog_does_not_say_the_maker_may_change_any_named_may_not_file`: stay off the wall. It asserts one CHANGELOG line's wording (the `+` hunk at `tests/test_briefs_picture.py:199-203`), which point 1 makes slice-only, and it is recorded in `slice_only`.

No test that was on the wall before the slice is dead.

## Door

**Door:** two-way. A revert undoes it: no data is migrated and nothing is published. **Blast radius:** briefs.

## Raw data

- Slice record: `.xv/slices/2026-11-04-scenario-catches.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..2a7d181`; this pass alone: `git diff 060a026..2a7d181`
- Wall: `xv wall diff 2026-11-04-scenario-catches`
- Boundary: `.xv/slices/2026-11-04-scenario-catches.boundary.md`
- Decision: `.xv/decisions/2026-11-04-2026-11-04-scenario-catches.md`

---
slice: 2026-11-04-scenario-catches
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: briefs
---

# Packet: The scenario agent catches more before the maker starts: #119, with #110 and #111

**Back to the scenario (no stop):** amendment point 7 is met in the code but not in the words the maker reads. The protected-file check now exempts only `.xv/picture.md`. The maker's brief, its prompt, the scenario brief and the CHANGELOG line still say the maker may change *any* may-not file the report names. That includes `.xv/pitch.md` (see Scenario misses). The last pass's pitch stop is closed in the running system (§2). For Sean, separately: three picture edits (§4) and one slice-only removal (§3).

## The scenario

Six points and three amended ones. (1) The scenario agent marks a one-time wording test slice-only. (2a) Its report names each old test the red forces to change. The maker may change a named test without stopping and records the move. (2b) Its report names may-not files the red needs changed, and the guardian lists those changes. (3) A red case for each way a value can be wrong, plus a case where a read-only agent claims what only a person may give. (4) Each amendment the watch drafts names four things. (5) A `covers` item may name a point by number. (6) A CHANGELOG line for each brief change. Amended by Sean at the pitch stop: (7) from the may-not list the maker may change only `.xv/picture.md`, when the report names it, and any other named file still raises `protected_changed`. (8) Each scenario report sets `old_tests_forced` and `may_not_files` again. (9) A number in `covers` names only the scenario's own point.
May ignore: the cleaner; naming an amendment's points by number; old slice records.

## The recording

None (a feature). Replay the red: `cd tests && python3 -m unittest test_run.NamedByTheScenarioReachTheMakerTest test_run.WatchLoopTest test_briefs_picture`. I ran it at HEAD `a413801`: `Ran 129 tests … OK`. The whole suite was green at the cleaner's pass (925 tests, record `checks.cleaner.suite`); I did not rerun it.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-scenario-catches.boundary.md`): touched `scripts/prompt`, `scripts/record`, `scripts/run`. No modules, edges, outbound calls, tables or surface paths added or removed. Shape hints: none.

## What the suite asserts after

- `record.apply_report` keeps a scenario report's `old_tests_forced` (file, test, why) and `may_not_files` (file, why). It drops entries that are malformed, empty or of the wrong type, and values that are not lists. It keeps neither list from a maker's report. A scenario report that leaves a list out clears it (`tests/test_run.py` `NamedByTheScenarioReachTheMakerTest`).
- The maker's prompt lists the named tests and files. The cleaner's prompt does not.
- After the maker, a named `.xv/picture.md` is not `protected_changed`. Naming `.xv/pitch.md`, `.xv/config.yml`, `.xv/rules.md` or the slice's wall file still is, and so is a malformed name.
- A `covers` item `"1"` or `"1. …"` covers scenario point 1 only. It does not cover point 10 or any point an amendment adds, even one with the same number. A number in `not_covered` still stops (`WatchLoopTest`).
- Brief-wording tests (`tests/test_briefs_picture.py` `ScenarioCatchesTest`) check that the scenario, maker, guardian and watch briefs carry rules 1–4.
- No old assertion moved. One in-slice test was removed as slice-only (§3).

## 1. Shape

shape_change: no. The boundary picture adds no module, edge, outbound call, table or surface, and it has no shape hints (`.xv/slices/2026-11-04-scenario-catches.boundary.md`, "Shape hints: none"). The new record keys `old_tests_forced` and `may_not_files` (`scripts/record.py:482-486`) are front-matter fields in a file the picture already names as state (`.xv/picture.md:26`, "State is files: `.xv/slices/<id>.md`"). shape_breadth: narrow, the same as the forecast's `shape: narrow`. The forecast's breadth did not name `record.py` or `prompt.py`. Those came from the guardian's 2a/2b send-back, and each changes five lines.

## 2. Pitch

pitch_contradiction: no. The promise is `.xv/pitch.md:11`: "An agent may tidy it; it may not write it." The running system keeps that promise. `scripts/run.py:430-433` exempts only `.xv/picture.md` from `protected_changed`, and `test_naming_the_pitch_does_not_let_the_maker_change_it` holds it. The maker's words still invite it to write the pitch when the report names it (`skills/maker/SKILL.md:54`, `scripts/prompt.py:117`). The stop catches that after the edit. It is a miss of amendment point 7, not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_briefs_picture.py | `test_the_changelog_has_a_line_for_each_brief_change` checked the `## Unreleased` CHANGELOG lines | removed (40 → 37 assertions, `xv wall diff`) | cleaner: "Slice-only: checks a one-time CHANGELOG line and reads only ## Unreleased, so it fails at the next release." | Yes, by point 1. The test was added in this slice: it is not at the base (`git show a6e023b:tests/test_briefs_picture.py` has no `changelog`), and Sean accepted the slice-only mark at the 2026-11-05T00:23 stop. |

Slice-only tests removed: `tests/test_briefs_picture.py::test_the_changelog_has_a_line_for_each_brief_change`. Kept: none.
The assertion count fell, but the move is recorded and is not unrecorded (`checks.cleaner.wall`: `recorded`, `unrecorded: []`). The scenario agent named no old test as forced to change.
May-not file changes the report allowed: none. The diff does not touch `.xv/picture.md`, and the record holds no `may_not_files`.

## 4. The picture

- `.xv/picture.md:35`: "The maker and the scenario agent read the picture … they do not edit it." This is now untrue for the maker. Proposed: "The maker may edit `.xv/picture.md` only when the scenario agent's report names it in `may_not_files`. `run.post_step` exempts no other protected file. The guardian lists the edit, and a person still accepts it at merge."
- `.xv/picture.md:23` (`record` owns the slice record): add "`apply_report` keeps a scenario report's `old_tests_forced` and `may_not_files`. A report that leaves one out clears it. `prompt` shows both to the maker only."
- `.xv/picture.md:26` (the covers check): add "A `covers` item that is a number, or starts with one, covers the scenario's own point with that number. An amendment's point is covered only by its words (`run.missed_points`, `scripts/run.py:522-531`)."

## 5. The wall

I looked at the 9 new `WatchLoopTest` cases, the 20 `NamedByTheScenarioReachTheMakerTest` cases, the 10 `ScenarioCatchesTest` cases, and the one removal.
- `tests/test_briefs_picture.py` `test_the_changelog_has_a_line_for_each_brief_change`: stay off the wall. It checks a one-time CHANGELOG line, which point 1 makes slice-only. It was removed as a recorded slice-only move (record `slice_only`, `moved_tests`).
Every other new test guards a lasting rule. No test that was on the wall before the slice is dead.

## Scenario misses

- 7 (amendment of 2026-11-04, "From the maker's may-not list, the maker may change only `.xv/picture.md`"; decision `.xv/decisions/2026-11-04-2026-11-04-scenario-catches.md:16`): the code meets it, but the agents' words do not. Four places still say what point 2b said before Sean narrowed it. `skills/maker/SKILL.md:54` says "you may change a file the report names, and no other file on this list", and that list includes `.xv/pitch.md`. `skills/scenario/SKILL.md:32` (6d) says "The maker may change those files and no other file on that list". `scripts/prompt.py:116-117` prints "Named file you may change: {file}" for every named file, `.xv/pitch.md` included. `CHANGELOG.md:7` says "The maker may change … a named may-not file". A maker that follows its brief edits the pitch and is then stopped as `protected_changed`. (evidence: those hunks; `test_the_maker_may_change_a_named_may_not_file_and_no_other` passes on the old wording, and `test_the_makers_prompt_lists_the_named_tests_and_files` names only the picture, so no red test checks that a non-picture name is withheld in the words; to: scenario)

## Door

**Door:** two-way (a revert undoes it; no data migrated, nothing published). **Blast radius:** briefs.

## Raw data

- Slice record: `.xv/slices/2026-11-04-scenario-catches.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..a413801`
- Wall: `xv wall diff 2026-11-04-scenario-catches`
- Boundary: `xv boundary --base a6e023bd0ffeed4f6ce45990c668742a8f758419`
- Decision: `.xv/decisions/2026-11-04-2026-11-04-scenario-catches.md`

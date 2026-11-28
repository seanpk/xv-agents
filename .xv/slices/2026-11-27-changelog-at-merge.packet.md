---
slice: 2026-11-27-changelog-at-merge
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: no
shape_breadth: narrow
moved_tests_count: 1
expected_moves: 0
door: two-way
blast_radius: narrow
---

# Packet: A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)

Re-pass at `d9175ce`, after pairing 2 (Sean Kennedy with Claude), reviewing `git diff f8fdf8f..HEAD`.
Pairing 2 closes the one finding the earlier packet left open: the test writer brief's example `checks` is now a placeholder, not the listed file `CHANGELOG.md` (`skills/test-writer/SKILL.md:63`).
Nothing new needs a decision from this pass.
The change edits a check and two briefs, so binding decision 1 still asks for two people at the merge (`.xv/picture.md:358`).

## The scenario

1. A `not_covered` outcome whose `checks` files are all in `tests.slice_only_files` does not stop with `red_misses_scenario`.
2. A `not_covered` outcome whose `checks` names any other file, or has no `checks`, still stops.
3. The inspector brief asks the inspector to read each outcome that went through this way and report it for the merge.
4. There is a line in `CHANGELOG.md` (settled with no test, record stop `red_misses_scenario`, `no_test: ["4"]`).
5. (Amended) The test writer brief names `checks` on a `not_covered` item, in the report block and in the text.
6. (Amended) The session-mode landing (`run.land_session_test_writer`) writes the same watch log line as `run.step`.

The slice may ignore the deputation part of #214 and records of slices already open or closed.

## The recording

None; a feature starts from words.
To replay the red, run the record's `red.command` from `tests/`.
I ran all of `test_briefs_picture` (31 tests) at HEAD `d9175ce`: `OK`.
I did not run the whole suite; pairing 2 changed no code and no test (`git diff f8fdf8f..HEAD --stat`: only `skills/test-writer/SKILL.md`, one line, and the record and packet).

## The boundary diagram

From `xv boundary` (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`), as given.
The only code module touched is `scripts/run`; no modules, edges, tables or surface paths were added (`"edges_added": []`, `"shape_hints": []`).
Pairing 2 touched no code.

## What the suite asserts after

Unchanged from the earlier packet: no test file changed (`xv wall diff`: nothing changed, deleted, added or with fewer assertions).
The brief test still holds after the edit: the report block's `not_covered` line still names `"checks"` (`skills/test-writer/SKILL.md:63`), and `test_briefs_picture` passes.

## 1. Shape

shape_change: no.
The re-pass diff changes one placeholder in a brief's example block (`skills/test-writer/SKILL.md:63`); no module, edge, table or surface changes.
shape_breadth: narrow, as the forecast expected.

## 2. Pitch

pitch_contradiction: no.
A placeholder that a test writer must fill in, in place of a listed file that would skip the stop, keeps the red stop honest and serves "to vibe with discipline" (`.xv/pitch.md:7`).
Nothing in the re-pass touches who the system is for (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_briefs_picture.py` | `test_the_changelog_has_a_line_for_214_not_covered_at_merge` asserted a #214 line in CHANGELOG | removed (round 1) | "checks one CHANGELOG line that is written once" (cleaner, slice-only, `removal_named`) | Yes: outcome 4 is a one-time line, settled with no test by Sean Kennedy |

Slice-only tests removed: `TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` (`checks: CHANGELOG.md`, accepted by the watch). Kept: none.

`xv wall diff` against baseline `ca5b50e`: nothing changed, deleted, added or with fewer assertions.
`may_not_files_needed` is `[]`.
Pairing 1 wrote `.xv/picture.md`, a may-not file for agents, at Sean Kennedy's direction (commit `f8fdf8f`); pairing 2 wrote no may-not file.

Outcomes that went through on their `checks`: none in this slice.

The earlier finding is closed.
`skills/test-writer/SKILL.md:63` was `"checks": ["CHANGELOG.md"]` and is now `"checks": ["<the files the outcome is about>"]`, a `<…>` placeholder like `outcome` and `why` in the same item.
A test writer that copies the example now names a path no config lists, so the outcome stops, as outcome 2 asks.

## 4. The picture

picture_change: no.
`.xv/picture.md:244` says the report block "shows `checks` on the item"; the placeholder still does, so the line stays true.

## 5. The wall

The two new tests, `TestWriterCatchesTest.test_the_test_writer_brief_report_block_names_checks_on_the_not_covered_item` (`tests/test_briefs_picture.py:127`) and `SessionTestWriterReportTest.test_a_not_covered_outcome_that_went_through_on_a_listed_file_leaves_one_watch_log_line` (`tests/test_from_build.py:1086`), did not change in pairing 2.
I have no recommendation.

## The CHANGELOG line

Unchanged in pairing 2: the #214 line sits under `## Unreleased` (`CHANGELOG.md:5-7`) and names one person, which `CHANGELOG.md:3` calls a draft until the merge.

## Door

**Door:** two-way: a revert of `scripts/run.py`, the two briefs, the picture lines and the CHANGELOG line undoes it, and it migrates no data. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-11-27-changelog-at-merge.md`
- Diff: `git diff dd577e56d4a5315f8bcd44af60e6af600af7bd87..HEAD` (re-pass: `git diff f8fdf8f..HEAD -- skills`)
- Wall: `xv wall diff 2026-11-27-changelog-at-merge`
- Boundary: `.xv/slices/2026-11-27-changelog-at-merge.boundary.md`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:248.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session cb299610-0e8d-419c-a825-f2048a338265), because: Three small wording fixes left: the test writer brief says 'may' where it must tell; the CHANGELOG line sits under released 0.6.5 and misses two changes. Too small for a pass through the loop, and the budget is nearly spent.. Commits: 1d305f02a3, f8fdf8f9bd. Resumed at cleaner. Spend: 15347 tokens (in 22, out 5500, cache write 9825; cache read 1575851 not counted), 11 turns, usd not reported.
- Pairing 2: Sean Kennedy with Claude (claude-session session cb299610-0e8d-419c-a825-f2048a338265), because: The inspector found the test writer brief's example checks names CHANGELOG.md, the one listed file, so a copied example skips the stop; it becomes a placeholder.. Commits: d9175ce6de. Resumed at cleaner. Spend: 1227 tokens (in 2, out 642, cache write 583; cache read 155766 not counted), 1 turns, usd not reported.

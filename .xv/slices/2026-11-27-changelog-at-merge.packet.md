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

Re-pass at `f8fdf8f`, after pairing 1 (Sean Kennedy with Claude), reviewing `git diff 29d0244..HEAD`.
The pairing closes both items the earlier packet left open: the test writer brief now tells the test writer to name `checks` (`skills/test-writer/SKILL.md:71`), and the picture edit is in (`.xv/picture.md:243-247`).
One finding goes to Sean Kennedy: the brief's report block shows `"checks": ["CHANGELOG.md"]` as its example, and that is the one file this repo lists as slice-only (check 3).
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
I ran both red tests and all of `test_briefs_picture` (31 tests) at HEAD `f8fdf8f`: each `OK`.
I did not run the whole suite; the pairing changed no code and no test (`git diff 29d0244..HEAD --stat`: only `CHANGELOG.md`, `skills/test-writer/SKILL.md`, `.xv/picture.md` and the record and packet).

## The boundary diagram

From `xv boundary` (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`), as given.
The only code module touched is `scripts/run`; no modules, edges, tables or surface paths were added (`"edges_added": []`, `"shape_hints": []`).
The pairing touched no code.

## What the suite asserts after

Unchanged from the earlier packet: no test file changed since `29d0244`.
The brief test still holds after the reword: the report block's `not_covered` line names `"checks"` (`skills/test-writer/SKILL.md:63`), and the paragraph still says "no stop" and "merge" (`skills/test-writer/SKILL.md:71`).

## 1. Shape

shape_change: no.
The re-pass diff edits a sentence in a brief, moves a CHANGELOG line, and adds five picture lines; no module, edge, table or surface changes.
shape_breadth: narrow, as the forecast expected.

## 2. Pitch

pitch_contradiction: no.
Telling the test writer to name `checks`, so the outcome is read at the merge and not lost, serves "to vibe with discipline" (`.xv/pitch.md:7`).
Nothing in the re-pass touches who the system is for (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_briefs_picture.py` | `test_the_changelog_has_a_line_for_214_not_covered_at_merge` asserted a #214 line in CHANGELOG | removed (round 1) | "checks one CHANGELOG line that is written once" (cleaner, slice-only, `removal_named`) | Yes: outcome 4 is a one-time line, settled with no test by Sean Kennedy |

Slice-only tests removed: `TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` (`checks: CHANGELOG.md`, accepted by the watch). Kept: none.

`xv wall diff` against baseline `ca5b50e`: nothing changed, deleted, added or with fewer assertions.
`may_not_files_needed` is `[]`.
The pairing wrote `.xv/picture.md`, a may-not file for agents, at Sean Kennedy's direction (commit `f8fdf8f`, "as Sean Kennedy directed").

Outcomes that went through on their `checks`: none in this slice.

The earlier wording finding is closed: "may name `checks`" is now "Name `checks` on each `not_covered` outcome: the files it is about" (`skills/test-writer/SKILL.md:71`), which meets outcome 5's "tells".

Finding, for the person: the report block's example `checks` is a real listed file, so a copied example goes through with no stop.
`skills/test-writer/SKILL.md:63`: `"not_covered": [{"outcome": "<an outcome with no test>", "why": "<why it has none>", "checks": ["CHANGELOG.md"]}],`.
`.xv/config.yml:27`: `slice_only_files: ["CHANGELOG.md"]`.
Now that the text tells the test writer to name `checks` on every `not_covered` outcome (`skills/test-writer/SKILL.md:71`), a test writer that copies the example onto an outcome not about the CHANGELOG skips the red stop; only the watch log line and the inspector at the merge would catch it.
`outcome` and `why` in the same item are `<…>` placeholders; `checks` is not.
This is not a miss: outcome 5 asks only that the brief name `checks`.

Note: the brief does not say what to put in `checks` for an outcome that is about no file (such as this slice's round-3 "scope limits" item); such an outcome still stops, as outcome 2 asks, so nothing is lost.

## 4. The picture

picture_change: no.
The edit the earlier packet proposed is in, with one more line for the brief (`.xv/picture.md:243-247`), committed in the pairing at Sean Kennedy's direction.
Each new line is one sentence and lined up with the list item's text.
`.xv/picture.md:239` still says `red_misses_scenario` stops "when the report lists a `not_covered` outcome"; the lines at 243-244 qualify it, so I propose no further edit.

## 5. The wall

I looked again at the two new tests, `TestWriterCatchesTest.test_the_test_writer_brief_report_block_names_checks_on_the_not_covered_item` (`tests/test_briefs_picture.py:127`) and `SessionTestWriterReportTest.test_a_not_covered_outcome_that_went_through_on_a_listed_file_leaves_one_watch_log_line` (`tests/test_from_build.py:1086`); neither changed since the earlier packet.
I have no recommendation.

## The CHANGELOG line

The #214 line moved from under released `## 0.6.5, 2026-11-27` to a new `## Unreleased` heading (`CHANGELOG.md:5-7`).
It now names the test writer brief change and the session-mode log line, which outcomes 5 and 6 added.
It names one person ("decided by Sean Kennedy"); `CHANGELOG.md:3` says "A version line without two names is a draft", which `Unreleased` is until the merge.

## Door

**Door:** two-way: a revert of `scripts/run.py`, the two briefs, the picture lines and the CHANGELOG line undoes it, and it migrates no data. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-11-27-changelog-at-merge.md`
- Diff: `git diff dd577e56d4a5315f8bcd44af60e6af600af7bd87..HEAD` (re-pass: `git diff 29d0244..HEAD -- CHANGELOG.md skills .xv/picture.md`)
- Wall: `xv wall diff 2026-11-27-changelog-at-merge`
- Boundary: `.xv/slices/2026-11-27-changelog-at-merge.boundary.md`


Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:248.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session cb299610-0e8d-419c-a825-f2048a338265), because: Three small wording fixes left: the test writer brief says 'may' where it must tell; the CHANGELOG line sits under released 0.6.5 and misses two changes. Too small for a pass through the loop, and the budget is nearly spent.. Commits: 1d305f02a3, f8fdf8f9bd. Resumed at cleaner. Spend: 15347 tokens (in 22, out 5500, cache write 9825; cache read 1575851 not counted), 11 turns, usd not reported.

---
slice: 2026-11-27-changelog-at-merge
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 1
expected_moves: 0
door: two-way
blast_radius: narrow
---

# Packet: A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)

Re-pass at `29d0244`, after the amendment of 2026-11-27 (outcomes 5 and 6).
Both amended outcomes are met: the session-mode landing now writes the log line (`scripts/run.py:996`), and the test writer brief's report block names `checks` (`skills/test-writer/SKILL.md:63`).
Two things go to Sean Kennedy, who set the work going: the picture edit (check 4), and one wording note on the brief, "may name" where outcome 5 says "tells" (check 3).
The change edits a check and two briefs, so binding decision 1 asks for two people at the merge (`.xv/picture.md:358`).

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
To replay the red, run the command in the record's `red.command` from `tests/`.
I ran both tests at HEAD `29d0244`: each `OK`.
The red failed with `AssertionError: '"checks"' not found in ' "not_covered": [{"outcome": …, "why": …}],'` (record `red.failure`).
I did not run the whole suite: the maker and the cleaner both ran it green at this HEAD (1543 tests, record `checks.cleaner.suite_output`).

## The boundary diagram

From `xv boundary` (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`), as given.
The only code module touched is `scripts/run`; no modules, edges, tables or surface paths were added (`"edges_added": []`, `"shape_hints": []`).

## What the suite asserts after

- Everything the earlier packet listed still holds (`tests/test_run.py:1945-1993`, `tests/test_briefs_picture.py:158-162`).
- New: the `not_covered` line in the test writer brief's report block names `"checks"`, and a paragraph naming `slice_only_files` and `not_covered` says "no stop" and "merge" (`tests/test_briefs_picture.py:127-134`).
- New: a session-mode report from a build with `checks: ["CHANGELOG.md"]` lands with exit 0 and leaves exactly one `watch:` log line naming the outcome and `CHANGELOG.md` (`tests/test_from_build.py:1086-1095`).
- No old assertion moved in this round.

## 1. Shape

shape_change: no.
The re-pass adds one call to the existing `run.log_listed_outcomes` inside `run.land_session_test_writer` (`scripts/run.py:996`: `body = log_listed_outcomes(report, body, config)`), and edits a brief.
Both are in the same module and use `record.log_line`, which that module already calls, so no edge is added.
shape_breadth: narrow, as the forecast expected ("One new exemption branch in the red check …, one inspector brief item, and a CHANGELOG line"); the amendment adds a brief item and one call, inside that shape.

## 2. Pitch

pitch_contradiction: no.
Logging the outcome on both landing paths lets a person see at the merge what went through, which serves "to vibe with discipline" (`.xv/pitch.md:7`).
Nothing in the re-pass touches who the system is for (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_briefs_picture.py` | `test_the_changelog_has_a_line_for_214_not_covered_at_merge` asserted a #214 line in CHANGELOG | removed (round 1) | "checks one CHANGELOG line that is written once" (cleaner, slice-only, `removal_named`) | Yes: outcome 4 is a one-time line, settled with no test by Sean Kennedy |

Slice-only tests removed: `TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` (`checks: CHANGELOG.md`, accepted by the watch). Kept: none.

`xv wall diff` against baseline `ca5b50e` shows nothing changed, deleted or with fewer assertions.
The re-pass diff to `tests/` only adds lines (`tests/test_briefs_picture.py:127-134`, `tests/test_from_build.py:1086-1095`).
`may_not_files_needed` is `[]`.

Outcomes that went through on their `checks`: none in this slice.
This round's only `not_covered` item ("5 and 6: … scope limits") had no `checks`, so it stopped, and Sean Kennedy settled it (record stop `red_misses_scenario` at 03:02:01).

Finding, for the person: the brief's text is permissive where outcome 5 asks for an instruction.
Outcome 5 says the brief "tells the test writer to name `checks` on a `not_covered` item"; the text says "A `not_covered` outcome may name `checks`, the files it is about" (`skills/test-writer/SKILL.md:71`).
The report block does show `checks` on the item (`skills/test-writer/SKILL.md:63`), and the test asserts only that, so I did not make it a miss.
A test writer reading "may" can still leave `checks` off, which is how this slice stopped in round 2 (record stop cause: "the test writer left checks off the CHANGELOG outcome").

Note: the session path logs after `post_step` (`scripts/run.py:995-996`), the agent path before it (`scripts/run.py:887`); both write the same line text, so the order does not change what a person reads.
Note: the session path still does not call `accept_listed_marks`, which the agent path calls (`scripts/run.py:886`); outcome 6 names only the outcome log line, so this older gap stays outside the slice.

## 4. The picture

picture_change: yes.
`.xv/picture.md:239` says `red_misses_scenario` stops "when the report lists a `not_covered` outcome"; that is now untrue for an outcome whose `checks` names only listed files.
The proposed edit adds these lines after `.xv/picture.md:242`:

```
  A `not_covered` outcome whose `checks` names only files listed in `tests.slice_only_files` (a string or a non-empty list of exact paths) does not stop (`run.checks_only_listed_files`).
  A missing, empty or non-string `checks`, or one that names any other file, still stops.
  The watch writes a log line naming each outcome that went through this way and its files, on the agent path and on the session-mode landing (`run.log_listed_outcomes`).
  The test writer brief's report block shows `checks` on each `not_covered` item.
  The inspector reads those log lines and says in the inspection report whether the file change is there and in the right place.
```

## 5. The wall

I looked at the two new tests, `TestWriterCatchesTest.test_the_test_writer_brief_report_block_names_checks_on_the_not_covered_item` (`tests/test_briefs_picture.py:127`) and `SessionTestWriterReportTest.test_a_not_covered_outcome_that_went_through_on_a_listed_file_leaves_one_watch_log_line` (`tests/test_from_build.py:1086`).
Each guards behaviour that keeps mattering (the brief that feeds outcome 1, and the trace on the second landing path), and neither restates another test.
I have no recommendation.

## Door

**Door:** two-way: a revert of `scripts/run.py`, the two briefs and the CHANGELOG line undoes it, and it migrates no data. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-11-27-changelog-at-merge.md`
- Diff: `git diff dd577e56d4a5315f8bcd44af60e6af600af7bd87..29d0244` (re-pass: `git diff aafe8de..29d0244 -- scripts skills tests`)
- Wall: `xv wall diff 2026-11-27-changelog-at-merge`
- Boundary: `.xv/slices/2026-11-27-changelog-at-merge.boundary.md`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:243.

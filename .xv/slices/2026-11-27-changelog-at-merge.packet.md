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

Re-pass at `aafe8de`: the earlier miss on outcome 3 is met on the agent path, because an outcome let through now leaves a watch log line (`scripts/run.py:934-942`).
Two findings go to Sean Kennedy, who set the work going: the session-mode path on a slice from a build still lets an outcome through without a log line (check 3), and the picture edit (check 4).
The change edits a check and a brief, so binding decision 1 asks for two people at the merge (`.xv/picture.md:358`).

## The scenario

1. A `not_covered` outcome whose `checks` files are all in `tests.slice_only_files` does not stop with `red_misses_scenario`.
2. A `not_covered` outcome whose `checks` names any other file, or has no `checks`, still stops.
3. The inspector brief asks the inspector to read each outcome that went through this way, check that the file change is right and in the right place, and put that in the inspection report.
4. There is a line in `CHANGELOG.md`. Sean Kennedy settled that this needs no test: the line is read at the merge (record stop `red_misses_scenario`, `no_test: ["4"]`).

The slice may ignore the deputation part of #214 (that waits for #159 and #160) and records of slices already open or closed.

## The recording

None; a feature starts from words.
To replay the red, run `cd tests && python3 -m unittest test_run.NotCoveredCheckedAtTheMergeTest test_briefs_picture.TestWriterCatchesTest`.
I ran it at HEAD `aafe8de`: 27 tests, OK.
The second red failed with `AssertionError: 0 != 1 : no watch log line names 'a line in the changelog'` (record `red.failure`).
I did not run the whole suite again: the maker and the cleaner both ran it green at this HEAD (1541 tests, record `checks.cleaner.suite_output`).

## The boundary diagram

From `xv boundary` (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`), as given.
The only module touched is `scripts/run`.
No modules, edges, outbound calls, tables or surface paths were added or removed (`"edges_added": []`, `"shape_hints": []`).

## What the suite asserts after

- Everything the earlier packet listed still holds: listed `checks` go on, every other `checks` value stops (`tests/test_run.py:1945-1993`), and the inspector brief has the item (`tests/test_briefs_picture.py:158-162`).
- New: an outcome let through on `checks: ["CHANGELOG.md"]` leaves exactly one `watch:` log line that names the outcome and `CHANGELOG.md` (`tests/test_run.py:1959-1963`).
- No test checks the session-mode landing path (`run.land_session_test_writer`) for that log line.
- No old assertion moved.

## 1. Shape

shape_change: no.
The re-pass adds one function, `run.log_listed_outcomes`, and one call to it in `run.step` (`scripts/run.py:887`, `scripts/run.py:934-942`).
It writes through `record.log_line`, which `run.accept_listed_marks` already calls (`scripts/run.py:928`), so it adds no edge.
The boundary diagram lists no added module, edge or shape hint.
shape_breadth: narrow, the same as the forecast ("One new exemption branch in the red check …, one inspector brief item, and a CHANGELOG line").

## 2. Pitch

pitch_contradiction: no.
The new log line helps a person see at the merge what went through, which serves "to vibe with discipline" (`.xv/pitch.md:7`).
Nothing in the re-pass touches who the system is for (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_briefs_picture.py` | `test_the_changelog_has_a_line_for_214_not_covered_at_merge` asserted a #214 line in CHANGELOG (added in the first red) | removed | "checks one CHANGELOG line that is written once" (cleaner, slice-only, `removal_named`) | Yes: outcome 4 is a one-time line, `CHANGELOG.md` is in `tests.slice_only_files` (`.xv/config.yml:27`), and Sean Kennedy settled it needs no test |

Slice-only tests removed: `TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` (`checks: CHANGELOG.md`, accepted by the watch). Kept: none.

`xv wall diff` against the new baseline `e5f5735` shows nothing changed, deleted or with fewer assertions, and `git diff e5f5735..HEAD -- tests/` removes no lines.
`may_not_files_needed` is `[]`.

Outcomes that went through on their `checks`: none in this slice.
The second test writer's only `not_covered` outcome (4) had no `checks`, so it stopped, and Sean Kennedy settled it (record `checks.test-writer.not_covered`, log line 02:40:12).
The CHANGELOG line is there, on its own line, in the top section: `CHANGELOG.md:7` ("A slice-only `not_covered` outcome is checked at the merge … (#214, decided by Sean Kennedy)").

Finding, for the person: the session-mode path still lets an outcome through with no trace.
`run.land_session_test_writer` calls `post_step`, which drops a listed outcome from `not_covered` (`scripts/run.py:995`, `scripts/run.py:1219`), but it never calls `log_listed_outcomes` (that only runs in `run.step`, `scripts/run.py:886-887`).
So `xv record report <id> test-writer -` after a session-mode step on a slice from a build lets the outcome go on, and the inspector has nothing to read.
I did not make this a scenario miss: the scenario names no mode, and the same path already skips `accept_listed_marks`, so the gap is older than this slice.

Note: `log_listed_outcomes` writes "goes on to the merge" before the joined-red check (`scripts/run.py:887-890`), so when the red command is refused and `next` stays `test-writer`, the log line says more than happened.

Brief note, carried from the earlier packet: the test writer's report shape still lists `not_covered` items as `{"outcome", "why"}` with no `checks` (`skills/test-writer/SKILL.md:63`), so outcome 1's path only fires if the test writer adds a key its brief does not name.
This slice shows it: the second test writer left `checks` off outcome 4, and the slice stopped (record stop cause: "the test writer left checks off the CHANGELOG outcome").

## 4. The picture

picture_change: yes.
`.xv/picture.md:239` says `red_misses_scenario` stops "when the report lists a `not_covered` outcome"; that is now untrue for an outcome whose `checks` names only listed files.
The proposed edit adds these lines after `.xv/picture.md:242`:

```
  A `not_covered` outcome whose `checks` names only files listed in `tests.slice_only_files` (a string or a non-empty list of exact paths) does not stop (`run.checks_only_listed_files`).
  A missing, empty or non-string `checks`, or one that names any other file, still stops.
  The watch writes a log line naming each outcome that went through this way and its files (`run.log_listed_outcomes`).
  The inspector reads those log lines and says in the inspection report whether the file change is there and in the right place.
```

## 5. The wall

I looked at the new `test_an_outcome_that_went_through_leaves_a_watch_log_line_naming_it_and_its_file` and its helper `log_lines` (`tests/test_run.py:1956-1963`).
It guards behaviour that keeps mattering, the trace the inspector reads, and it restates no other test.
I have no recommendation.

## Door

**Door:** two-way: a revert of `scripts/run.py`, `skills/inspector/SKILL.md` and the CHANGELOG line undoes it, and it migrates no data. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-11-27-changelog-at-merge.md`
- Diff: `git diff dd577e56d4a5315f8bcd44af60e6af600af7bd87..aafe8de` (re-pass: `git diff 7609028..aafe8de -- scripts tests`)
- Wall: `xv wall diff 2026-11-27-changelog-at-merge`
- Boundary: `.xv/slices/2026-11-27-changelog-at-merge.boundary.md` (`xv boundary --base dd577e56d4a5`)

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:243.

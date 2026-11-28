---
slice: 2026-11-27-changelog-at-merge
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 1
expected_moves: 0
door: two-way
blast_radius: narrow
---

# Packet: A slice-only not-covered outcome is checked at the merge, not stopped at the red (#214)

Back to the test writer, with no stop: a `not_covered` outcome that goes through on its `checks` leaves nothing on the record, so the inspector cannot read it at the merge as outcome 3 needs (see Scenario misses).
The picture edit (check 4) and the one-line slice-only removal (check 3) go to Sean Kennedy, who set the work going.
The change edits a check and a brief, so binding decision 1 asks for two people at the merge (`.xv/picture.md:358`).

## The scenario

1. A `not_covered` outcome whose `checks` files are all in `tests.slice_only_files` does not stop with `red_misses_scenario`.
2. A `not_covered` outcome whose `checks` names any other file, or has no `checks`, still stops.
3. The inspector brief asks the inspector to read each outcome that went through this way, check that the file change is right and in the right place, and put that in the inspection report.
4. There is a line in `CHANGELOG.md`.

The slice may ignore the deputation part of #214 (that waits for #159 and #160) and records of slices already open or closed.

## The recording

None; a feature starts from words.
To replay the red, run `cd tests && python3 -m unittest test_run.NotCoveredCheckedAtTheMergeTest test_briefs_picture.TestWriterCatchesTest`.
I ran it at HEAD `7609028`: 26 tests, OK.
At `f6ababf` (the red) the record shows 5 failures, starting with `test_an_outcome_that_checks_a_listed_file_goes_on_with_no_stop` (exit 10, `red_misses_scenario`).
I did not run the whole suite again: the cleaner ran it green at the same HEAD (`cleaner_commit: 7609028`, 1540 tests), and the only change since is to files under `.xv/slices/`.

## The boundary diagram

From `xv boundary` (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`), as given.
The only module touched is `scripts/run`.
No modules, edges, outbound calls, tables or surface paths were added or removed.
There are no shape hints.

## What the suite asserts after

- The red check lets a `not_covered` outcome go on to the maker with no stop when its `checks` is `"CHANGELOG.md"`, `["CHANGELOG.md"]` or `["CHANGELOG.md", "CHANGELOG.md"]` (`tests/test_run.py:1945-1955`).
- It still stops with `red_misses_scenario` when `checks` names `README.md`, mixes a listed and an unlisted file, names `docs/CHANGELOG.md`, is missing, is `[]` or `""`, is `5`, holds a non-string, or comes with an agent's own `accepted: true` (`tests/test_run.py:1957-1984`).
- The inspector brief has a paragraph that names `not_covered`, `checks` and the inspection report and asks about the "right place" (`tests/test_briefs_picture.py:158-162`).
- No test checks that an outcome let through is recorded anywhere, or that it reaches the inspector.
- No old assertion moved; the only removal is the slice-only CHANGELOG test (check 3).

## 1. Shape

shape_change: no.
The boundary diagram lists no added or removed module or edge and no shape hints (`.xv/slices/2026-11-27-changelog-at-merge.boundary.md`: "edges added: none").
The change adds one function and one condition inside `run.post_step` (`scripts/run.py:913-919`, `scripts/run.py:1206-1207`), so it stays inside `run` as the picture describes it (`.xv/picture.md:39`).
shape_breadth: narrow, the same as the forecast (`shape_breadth: narrow`: "One new exemption branch in the red check …, one inspector brief item, and a CHANGELOG line").

## 2. Pitch

pitch_contradiction: no.
I read the whole pitch.
The change keeps a person in charge of the merge, so it serves "to vibe with discipline" (`.xv/pitch.md:7`).
It does not touch "people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_briefs_picture.py` | `test_the_changelog_has_a_line_for_214_not_covered_at_merge` asserted a #214 line in CHANGELOG (added in the red, `f6ababf`) | removed (53 → 52 assertions, `xv wall diff`) | "checks one CHANGELOG line that is written once" (cleaner, slice-only, `removal_named`) | Yes: outcome 4 is a one-time line, and `CHANGELOG.md` is in `tests.slice_only_files` (`.xv/config.yml:27`) |

Slice-only tests removed: `TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` (`checks: CHANGELOG.md`, accepted by the watch). Kept: none.

`xv wall diff` flags `tests/test_briefs_picture.py` as asserting less, and the recorded move above accounts for it in full; there is no unrecorded change.
No test that was there at the base was changed: `git diff dd577e5..HEAD -- tests/` only adds lines.
`may_not_files_needed` is `[]`.

Outcomes that went through on their `checks`: none in this slice.
The test writer's `not_covered` was `[]`, and outcome 4 went in as a slice-only mark instead (record `checks.test-writer.not_covered: []`).
So the new brief item had nothing to read here, and the `watch_before_merge` step "the inspection report it produces for the outcome that went through" still has to be done by hand.

Brief note, not a miss: the test writer's report shape lists `not_covered` items as `{"outcome", "why"}` with no `checks` (`skills/test-writer/SKILL.md:63`), and no brief tells the test writer that `checks` on a `not_covered` outcome lets it through.
Outcome 1's path only fires if the test writer adds a key its brief does not name.

## 4. The picture

picture_change: yes.
`.xv/picture.md:239` says `red_misses_scenario` stops "when the report lists a `not_covered` outcome"; that is now untrue for an outcome whose `checks` names only listed files.
The proposed edit adds these lines after `.xv/picture.md:242`:

```
  A `not_covered` outcome whose `checks` names only files listed in `tests.slice_only_files` (a string or a non-empty list of exact paths) does not stop (`run.checks_only_listed_files`).
  A missing, empty or non-string `checks`, or one that names any other file, still stops.
  The inspector reads each outcome that went through this way and says in the inspection report whether the file change is there and in the right place.
```

If the miss below is fixed so that outcomes let through are recorded, the last line should name the record field the inspector reads.

## 5. The wall

I looked at the 12 new tests in `NotCoveredCheckedAtTheMergeTest` (`tests/test_run.py:1930-1985`), the new `test_the_inspector_reads_each_not_covered_outcome_that_went_through_on_its_checks` (`tests/test_briefs_picture.py:158`), and the record's `slice_only` list.
`TestWriterCatchesTest.test_the_changelog_has_a_line_for_214_not_covered_at_merge` is already removed from its file (record `moved_tests`, line 165), so there is nothing left to recommend for it.
Each new test guards behaviour that keeps mattering (the exemption and its refusals, or a brief item), and none only restates another.
I have no recommendation.

## Scenario misses

- 3: The brief asks the inspector to read "each `not_covered` outcome that went through on its `checks`" (`skills/inspector/SKILL.md:26`), but the change keeps no trace of such an outcome. `run.post_step` drops it from `checks["not_covered"]` (`scripts/run.py:1204-1207`: `and not checks_only_listed_files(n.get("checks"), config)]`). The record keeps only `agent, status, summary, …` from the report (`scripts/record.py:973-975`). Unlike a listed slice-only mark (`scripts/run.py:928`, "slice-only mark on … accepted"), it gets no log line. So the inspector, and the person at the merge, cannot find the outcome, and an outcome the test writer self-labels `checks: ["CHANGELOG.md"]` passes both the red and the merge unseen. No red test covers recording it (evidence: the diff hunks above; `tests/test_run.py:1945-1984` assert only stop or no stop; to: test-writer)

## Door

**Door:** two-way: a revert of `scripts/run.py`, `skills/inspector/SKILL.md` and the CHANGELOG line undoes it, and it migrates no data. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-11-27-changelog-at-merge.md`
- Diff: `git diff dd577e56d4a5315f8bcd44af60e6af600af7bd87..7609028`
- Wall: `xv wall diff 2026-11-27-changelog-at-merge`
- Boundary: `.xv/slices/2026-11-27-changelog-at-merge.boundary.md` (`xv boundary --base dd577e56d4a5`)

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:243.

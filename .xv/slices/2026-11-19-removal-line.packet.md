---
slice: 2026-11-19-removal-line
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 8
expected_moves: 0
door: two-way
blast_radius: narrow
---

# Packet: A slice-only removal names its line, and the check reads the tree (re-pass)

No two-person stop fires: there is no shape change and no pitch contradiction.
Both misses from the last pass are fixed, and each has a new red test, so nothing goes back.
Sean Kennedy has these decisions:

- The coverage check now excuses any test the cleaner removed with `--slice-only`, not only tests on the accepted `slice_only` list (section 3).
- The picture edits below, including the maker's earlier edit made without a listing, which is still open from the last pass.
- The four wall removals from the last pass, which the record still has as `accepted: false`.

This re-pass covers `git diff 3b46a11..HEAD`: `scripts/run.py`, `scripts/record.py` and `tests/test_removal_line.py`.
Everything else is as in the earlier packet.

## The scenario

`xv record move --slice-only` now takes `--line <n>`.
It reads that line's text from the commit where the step or pairing began, refuses a blank line or a number past the end, and records the text with the number. `--assertion` becomes a free note (outcome 1).
After a step, the removal check counts that text in the file now, and stops with `removal_not_made` when the count is not lower (outcome 2).
A removal committed before its move is accepted (outcome 3). The line is read from `step_start`, else from the pairing's `start_commit`, else from HEAD for a move outside any step (amendment 8).
Outcome 7 (the CHANGELOG line) has no test, as Sean Kennedy settled.

## The recording

None: this is a feature that starts from words.
Replay the red with `cd tests && python3 -m unittest test_removal_line`. I ran it on this pass: `Ran 21 tests` and `OK`.
For the record's failure before the fix, see `red.failure`: "['The report says `test_milk_today` covers 1, and no red file has that test.'] != []".
Whole suite: `python3 tests/run.py` gives `Ran 1427 tests in shard 1/1, 32 jobs` and `OK`, which I re-ran on this pass.

## The boundary picture

From `.xv/slices/2026-11-19-removal-line.boundary.md`, which was regenerated and is used as given.
No modules, edges, outbound calls, tables or surface paths were added or removed, and `shape_hints` is `[]`.
The new `from xvlib import names_test` in `scripts/run.py:35` is not a new edge: `run.py` already imported from `xvlib` at the base (`git show 2ebb304:scripts/run.py`, line 38).

## What the suite asserts after (new on this pass)

- When the cleaner removes a test with a free note such as "removed as asked", the coverage check finds the test by the line's text and does not stop (`tests/test_removal_line.py:156-157`).
- A note that names a test does not excuse a different missing test when the move has a line (`:159-161`).
- A slice-only move recorded between steps, after a commit has shifted the lines, reads its line from HEAD, not from the last step's start (`:242-260`).

## 1. Shape

shape_change: no.
The boundary picture shows nothing added or removed, and has no shape hints.
The new `step_start.ended` key is a field in the slice record, not a table (`scripts/run.py:890-891`).
shape_breadth: narrow, which matches the forecast's `narrow`.

## 2. Pitch

pitch_contradiction: no.
I checked the change against `.xv/pitch.md:25` ("xv-agents is not for people or projects that will not trust agents to write production code.").
This pass only changes how two internal checks read the record.
The pitch says nothing about move records.

## 3. Moved tests

This pass moves no old test.
`git diff 3b46a11..HEAD -- tests/` changes only `tests/test_removal_line.py`, the red, and only adds to it.
`xv wall diff 2026-11-19-removal-line` against the new baseline `64cfdd3` lists nothing changed, deleted, added or with fewer assertions.
The 8 moves from the last pass stand as listed in the earlier packet.
Slice-only tests removed: none (the record's `slice_only` is `[]`). Kept: none.
May-not files allowed by the scenario report (`may_not_files_needed`): none.

**The coverage check is wider than before (for Sean Kennedy).**
Before, the coverage check excused only moves marked `slice_only`, which `xv record move` sets only when the test is on the accepted `slice_only` list (`scripts/record.py:298-301`).
Now it also excuses moves marked `removal_named`, which every `--slice-only` move gets (`scripts/record.py:306-307`).
The hunk is at `scripts/run.py:1286-1287`:
`cleaned = [m for m in ... if ... m.get("by") == "cleaner" and (m.get("slice_only") or m.get("removal_named"))]`.
So when the cleaner records `--slice-only --line` for a red test that is not on the list, later scenario passes stop flagging that test as missing.
`.xv/picture.md:227` speaks of "a slice-only test that the cleaner removed", which reads as the listed tests.
The removal check already treated `removal_named` the same way (`scripts/record.py:995`), so this matches it, but neither the scenario nor the red asks for the wider rule: both red cases use a slice with an empty `slice_only` list (`tests/test_removal_line.py:142-150`).
In fact, the new red test passes only because of this widening.
I do not count this as a miss, because outcome 1 does not say which moves the coverage check excuses.

**A failed step leaves `step_start` open (for Sean Kennedy).**
`ended` is set only after `post_step` returns (`scripts/run.py:890-891`).
`agentcli.run` raises when the agent CLI is missing or the worktree is gone (`scripts/agentcli.py:88,99-100`), and `step` re-raises (`scripts/run.py:862-865`).
After such a failure, a move recorded before the next step reads its line from the failed step's start, not from HEAD.
That step never ran its agent, so its start is usually HEAD and the effect is small.
It is still an edge of amendment 8 ("a move outside any step") that no test covers.

## 4. The picture

- **The maker's earlier edit made without a listing is still open** (`.xv/picture.md:278`, `:280`).
  This pass did not touch `.xv/picture.md` (`git diff 3b46a11..HEAD --stat`).
  The earlier packet's note stands: the edits to lines 72-79 in `e09ef67` were not listed in `may_not_files_needed`, and `protected_changed` was `[]`.
- **`.xv/picture.md:227` is now untrue for moves with a line.**
  The hunk is at `scripts/run.py:1288-1290`, which reads `line_text` and falls back to `move_test_name` only when there is no line.
  Proposed (it says "removed by `--slice-only`", which Sean Kennedy keeps or narrows, depending on the section 3 decision):
  ```
  A `covered` name whose last part is a test that the cleaner removed by a recorded `--slice-only` move does not stop.
  The test is found as a whole word in the move's `line_text`, or, for a move recorded before `--line`, read from its assertion with `names.move_test_name`.
  ```
- **`.xv/picture.md:77` does not say when `step_start` stops counting.**
  The hunk is at `scripts/record.py:256-257` and `scripts/run.py:890-891`.
  Proposed:
  ```
  The line is read from the open pairing's `start_commit`, which `xv pairing start` saves, else from `step_start`, which `xv step` saves before the agent runs, else from `HEAD`.
  `xv step` marks `step_start` ended once its checks are done, so a move between steps reads `HEAD`.
  ```
- **`.xv/picture.md:76` is now true.**
  "`--assertion` is a free note that nothing reads" holds for moves with a line (`scripts/run.py:1289-1290`).
- **`.xv/picture.md:51-52` are true only of old moves.**
  I propose the same text as on the earlier pass:
  ```
  For a move recorded before `--line` existed, it reads the move's assertion with `names.move_test_name`: one of `name`, `Class.name`, `Class > name`, `Class::name`, `Class#name` or `file::Class::name`, with an optional note in brackets that is not read.
  A move with a `--line` is checked by its line's text, and its assertion is not read.
  ```

## 5. The wall

The four removals from the last pass still stand (record `wall_recommendations`, all `accepted: false`):
`SliceOnlyAssertionFormTest.test_each_form_of_a_name_is_taken`, `…test_a_name_followed_by_a_note_in_brackets_is_taken_whichever_bracket`, `…test_a_name_that_is_in_no_file_when_the_step_began_is_refused_and_nothing_is_recorded`, and `RemovalCheckNamesTest.test_none_of_the_inputs_passes_while_the_test_is_still_in_its_file`, all in `tests/test_record.py`.
I read the three new tests (`tests/test_removal_line.py:138-161`, `:242-260`).
Each one guards behaviour that lasts: the coverage check's reader, and the move-between-steps rule.
None is marked slice-only, and I recommend no change to them.

## Scenario misses

None.
The outcome 1 miss is fixed: the coverage check reads `line_text` (`scripts/run.py:1288-1294`), and `tests/test_removal_line.py:156` covers it.
The amendment 8 miss is fixed: `start_commit` returns HEAD when `step_start` has ended (`scripts/record.py:256-257`), and `tests/test_removal_line.py:242` covers it.
The failed-step edge in section 3 (`scripts/run.py:890-891`) is left for the person, not counted as a miss.

## Door

**Door:** two-way. A revert undoes the code, and a leftover `ended` key is harmless.
**Blast radius:** narrow.

Binding decision 1 (`.xv/picture.md:331`) applies as on the last pass: this changes a check that agents are judged by, the scenario coverage check.

## Raw data

- Slice record: `.xv/slices/2026-11-19-removal-line.md`
- Diff this pass: `git diff 3b46a11..HEAD`. Whole slice: `git diff 2ebb304bf2504ae8d50a2c3104889055f7309772..HEAD`
- Wall: `xv wall diff 2026-11-19-removal-line` (baseline `64cfdd3`, empty)
- Boundary: `.xv/slices/2026-11-19-removal-line.boundary.md`

---
slice: 2026-11-25-build-moves
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 0
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: In a slice from a build, the test writer's stop names the build's changes to old tests apart from its own (#210)

Nothing stops for two people. Sean, as originator, has three things to look at:
1. One picture line to accept (check 4).
2. One open question: a build older than the base (check 1, note A). No test covers it.
3. The CHANGELOG line sits under the tagged v0.6.2 heading (check 1, note B).

## The scenario

In a slice from a build (`xv slice new --from <ref>`), the test writer's `unrecorded_move` stop still fires when the build changed or removed old tests, but now it says those files were changed by the build, not the test writer (1).
The test writer's own changes are listed apart from the build's, and a file both of them changed is in both lists (2).
A file with a recorded move is in neither list (3).
A slice with no build, or a build that changed no old test, stops as it does today (4).
There is a CHANGELOG line (5).
May ignore: a way to accept all of the build's moves with one command.

## The recording

`.xv/recordings/rec-build-moves.md`: in slice `2026-11-20-names`, the build renamed things in 32 test files, and the stop said "The scenario agent changed or removed old tests…" for all of them.
To replay the red and the green: `cd tests && python3 -m unittest test_from_build.BuildMovesNamedApartTest`.
It ran 8 tests with 5 failing at the red (record `checks.test-writer.red_output`), and 8 OK at HEAD (I ran it).
The whole suite, `python3 tests/run.py`, is OK: 1524 tests (I ran it).

## The boundary diagram

From `.xv/slices/2026-11-25-build-moves.boundary.md`, as given: modules touched are `scripts/orders` and `scripts/run`.
No modules, edges, outbound calls, tables or surface paths were added or removed.
There are no shape hints.

## What the suite asserts after

`BuildMovesNamedApartTest` (`tests/test_from_build.py:808-912`) has 8 new tests:
- A build-only change to `tests/test_store.py` is labelled the build's, and the question does not say "The test writer changed or removed" (1).
- A test-writer change to `tests/test_api.py` is labelled the test writer's, apart from the build's store change, and a store file both of them changed carries both labels (2).
- Recorded moves on both files give no stop, and with one build file recorded, only the other one stops (3).
- A build with no old-test change gives no stop, and with no build the old "The test writer changed or removed old tests" wording stays (4).

`tests/fake_agent.py:138-142` adds a `FAKE_WRITER_REPLACE` stand-in.
No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `shape_breadth: narrow` ("the test writer's stop computation, its tests, and one CHANGELOG line").

- `scripts/run.py:1169-1175` adds a new key, `checks.old_red_changed_build`, to the test-writer checks.
  It splits the list it already had using `wall.removed_lines`, a function `run.py` already reaches through `old_red_changed` (`scripts/run.py:1485-1492`).
  This sits inside the shape that `.xv/picture.md:244-246` already describes, so it is no new coupling.
- `scripts/orders.py:188-197` changes only the question text of the existing `unrecorded_move` order and what makes it fire.
  The order stays in `scripts/orders.py`, as decision 10 requires (`.xv/picture.md:366`).

**Note A: a build older than the base. This is an open question, not shown by a run.**
`scripts/run.py:1173-1175`:
```
checks["old_red_changed_build"] = [f for f in changed
                                   if wall.removed_lines(root, data["base"], f, build["commit"])]
checks["old_red_changed"] = [f for f in changed if wall.removed_lines(root, build["commit"], f, None)]
```
`changed` compares the base with the working tree (`scripts/wall.py:219`, `removed_lines(..., None)`).
The build list uses `base...build`, a three-dot diff, which runs from the merge-base to the build (`scripts/wall.py:208`).
Take a build branched before the base's last commits to a test file.
Lines that main added after the merge-base show up in `changed` as removed, but they are in neither split list.
If every changed file is like that, both lists are empty and the stop that fired before the change no longer fires.
Arguably that stop was a false alarm anyway, since a merge into main keeps main's lines.
Every test builds from the tip of main (`tests/test_from_build.py:39-54`), so none covers this case.
I did not call it a miss of outcome 4: "stops as it does today" (scenario 4) is written for a build that changed no old test, and here the build did not change these files.
Sean decides whether a file in `changed` that is in neither list should still stop.

**Note B: CHANGELOG placement.**
The line goes under `## 0.6.2, 2026-11-24` (`CHANGELOG.md:5-7`), but the base commit `84f20f5` is the `v0.6.2` tag (`git tag` lists `v0.6.2`), so the line sits in a version that has already shipped.
It also ends "Sean decided it, solo", while the 0.6.2 lines next to it use "(#205, decided by Sean Kennedy)" and "It moves no position on xtremevibing.com" (`CHANGELOG.md:9`).
This meets decision 1 (`.xv/picture.md:344`) under solo mode (decision 81, `docs/decisions.md:124`; `.xv/picture.md:335`).

## 2. Pitch

pitch_contradiction: no.
The change makes a stop's question accurate about who changed a test.
That serves "to vibe with discipline" (`.xv/pitch.md:7`) and contradicts none of "Who it is not for, and what it will never do" (`.xv/pitch.md:23-25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

The record has `moved_tests: []`, and `xv wall diff 2026-11-25-build-moves` shows `changed: []`, `deleted: []` and `fewer_assertions: []`.
The test diff (`tests/test_from_build.py:808-912`, `tests/fake_agent.py:138-142`) only adds lines.
Slice-only tests removed: none (`slice_only: []`). Kept: none.
May-not files the test writer's report allowed: none (`may_not_files_needed: []`).
Expected moves: none.

## 4. The picture

`.xv/picture.md:244-245` describe when `unrecorded_move` fires, but not that a build's changes are named apart from the test writer's.
I propose adding these lines after line 245:

```
  In a slice from a build, the question names the old test files the build changed or removed as the build's, not the test writer's, measured from the base to the build's commit.
  It lists the test writer's own changes apart from them, measured from the build's commit to the tree, and a file both changed is in both lists (`checks.old_red_changed_build`, `checks.old_red_changed`).
```

Nothing else in the picture becomes untrue: `.xv/picture.md:182` and `:185` (`build.commit`) still hold.

## 5. The wall

No recommendations.
All 8 new tests in `BuildMovesNamedApartTest` (`tests/test_from_build.py:808-912`) each guard one scenario outcome (`covered_kept` in the record), not a one-time change.
`test_with_no_build_the_writers_change_stops_as_the_test_writers` (`tests/test_from_build.py:904-912`) overlaps the no-build stop in `tests/test_run.py:227`.
It also pins the "The test writer changed or removed old tests" wording, which nothing else does, so it should stay on the wall.
No test that was on the wall before has become dead: `xv wall diff` shows no change.

## Door

**Door:** two-way. A revert restores the old question, and no data or contract moves. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-25-build-moves.md`
- Diff: `git diff 84f20f5eb0c66ecb9426f6f63ce0074847a0d3be..ff7a3f5`
- Wall: `xv wall diff 2026-11-25-build-moves`
- Boundary: `xv boundary --base 84f20f5eb0c66ecb9426f6f63ce0074847a0d3be`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:231.

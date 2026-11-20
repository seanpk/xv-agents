---
slice: 2026-11-19-pick-tests
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: none
moved_tests_count: 0
expected_moves: 0
door: two-way
blast_radius: tests
---

# Packet: Two prototype pick paths have tests

Nothing stops for two people. The merge is the originator's (Sean Kennedy), who also decides on two picture lines (check 4) and on whether the new conflict test should also check why it was refused (check 3).

## The scenario

1. `xv prototype pick --keep` on a variant that conflicts with the slice branch outside `.xv/` is refused, and the record does not change. The variant's uncommitted work is committed onto the variant's own branch first, so that branch's tip moves.
2. `xv prototype pick` without `--keep` and with a `--scenario-file` that does not exist is refused before anything changes. All three prototypes, their worktrees and their branches stay, and the record does not change.

May ignore: other prototype paths, and a CHANGELOG line.

This slice only adds tests. Both tests pass on the code as it was, so there is no red. The originator chose to keep them as green pins and skip the maker (`.xv/slices/2026-11-19-pick-tests.md`, stop `scenario_stopped`, pick 1: "This slice only adds tests: the two tests pin existing behavior, there is no red, and the maker has nothing to do").

## The recording

None (a defect started from words). To replay, run from `tests/`:
`python3 -m unittest test_prototypes.KeptPickTest.test_a_kept_pick_that_conflicts_with_the_slice_branch_is_refused_and_only_the_variant_tip_moves test_prototypes.KeptPickTest.test_a_pick_without_keep_with_a_missing_scenario_file_is_refused_and_changes_nothing`.
Both pass on HEAD (run by the guardian: `Ran 2 tests ... OK`). They also pass at the base, because no source file changed.

## The boundary picture

From `.xv/slices/2026-11-19-pick-tests.boundary.md`: modules touched: none; added and removed: none. Edges added and removed: none. Tables: none. Surface paths: none. Shape hints: none.
The diff (`git diff 07f5734..HEAD --stat`) touches only `tests/test_prototypes.py` (+38) and the slice's own `.xv/slices/` files.

## What the suite asserts after

- **Conflict on a `--keep` pick** (`tests/test_prototypes.py:565`): the slice branch commits a line to `pantry/store.py`, and variant b leaves a different uncommitted line in the same file. Then `pick --keep` fails. The record, the slice HEAD and the three branches are unchanged, and there is no traceback. `build` stays none and `kind` stays `prototype`. Variant b's branch tip has moved to a descendant of its old tip, and that tip holds the variant's line.
- **Missing `--scenario-file` without `--keep`** (`tests/test_prototypes.py:588`): the pick fails with no traceback. The record, the slice HEAD, the three branches and the worktree list are unchanged, and each `p1-proto-a/b/c` worktree is still there. `kind` stays `prototype`.
- No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none.
- The boundary picture lists no modules touched, no edges, no tables, no surfaces and no shape hints (`.xv/slices/2026-11-19-pick-tests.boundary.md`, "Shape hints: none").
- The only code change is 38 added lines in `tests/test_prototypes.py` (hunk `@@ -562,6 +562,44 @@ class KeptPickTest`). This matches the forecast's expected shape: "Expect changes only to tests under tests/** for the two pick paths ... no source change is expected" (record `forecast.shape_note`). Breadth is not wider than the forecast's `narrow`.

## 2. Pitch

pitch_contradiction: no.
- I read `.xv/pitch.md:25`, "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." Adding tests for refusals that already exist does not serve anyone the pitch excludes, and breaks no promise it makes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-19-pick-tests` reports `changed: []`, `deleted: []`, `fewer_assertions: []`. The record has `moved_tests: []`, `old_tests_to_move: []` and `may_not_files_needed: []`. The diff only adds lines to `tests/test_prototypes.py` and removes none.

Slice-only tests removed: none. Kept: none.

Notes on the new tests (for the originator; not stops):
- The conflict test does not check why the pick was refused. `tests/test_prototypes.py:576-577`: `p = self.pick("--keep", check=False)` / `self.assert_refused_and_nothing_changed(p)`. It never checks that stderr names the conflict. The code has three refusals that can come after the commit step: "holds nothing the slice branch does not have", "does not merge onto the slice branch" and "conflicts with the slice branch in ..." (`scripts/prototypes.py:271-286`). Any of them would satisfy this test, so it pins "refused after the commit", not "refused for the conflict". Scenario line 1 says "whose merge conflicts ... is refused". Something like `self.assertIn("conflicts with the slice branch", p.stderr)` would pin that.
- The missing-file test does not check the reason either (`tests/test_prototypes.py:592-594`). It is weaker in the same way, but the setup makes another refusal reason less likely, because the only fault in its input is the missing file.
- Both tests passed with no red, so neither has ever been seen to fail (record, stop `scenario_stopped`, cause: "tool: XV has no path for a slice that only adds tests").

## 4. The picture

picture_change: yes. Proposed edits, each one sentence per line:
- `.xv/picture.md:200` covers only `--keep`: "The pick refuses a missing `--scenario-file` before it changes anything, so a refused `--keep` leaves the slice branch, the record and all three prototypes as they were." The new test pins the same refusal without `--keep` (`tests/test_prototypes.py:588`). Proposed replacement:
  `  The pick, with or without `--keep`, refuses a missing `--scenario-file` before it changes anything, so the slice branch, the record and all three prototypes, their worktrees and their branches stay as they were.`
- The picture does not say what a refused conflicting `--keep` leaves behind. The code commits the variant's uncommitted work first (`scripts/prototypes.py:259-262`), and the new test pins that the variant's tip moves (`tests/test_prototypes.py:582-584`). Proposed new line after `.xv/picture.md:200`:
  `  A `--keep` pick commits the variant's uncommitted work onto the variant's own branch before it merges, so a pick refused for a conflict outside `.xv/` leaves the record and the slice branch as they were but moves that variant's branch tip.`

## 5. The wall

I have no recommendations. I looked at both new tests in the hunk `@@ -562,6 +562,44 @@`. Neither one guards a one-time change: each pins a lasting refusal (`scripts/prototypes.py:283-286`, `:307-309`). Neither repeats another test. `test_a_kept_pick_with_a_missing_scenario_file_is_refused_and_changes_nothing` (`tests/test_prototypes.py:551`) covers the `--keep` path, and the new test covers the path without `--keep`. Neither is marked slice-only (record `slice_only: []`), and no test that was on the wall before is made dead.

## Door

**Door:** two-way (a revert removes the 38 added test lines; no source, data or contract changed). **Blast radius:** tests.

## Raw data

- Slice record: `.xv/slices/2026-11-19-pick-tests.md`
- Diff: `git diff 07f5734397e770fdcb049a0eb78b318877d93cf6..HEAD`
- Wall: `xv wall diff 2026-11-19-pick-tests`
- Boundary: `.xv/slices/2026-11-19-pick-tests.boundary.md` (`xv boundary --base 07f5734397e770fdcb049a0eb78b318877d93cf6`)

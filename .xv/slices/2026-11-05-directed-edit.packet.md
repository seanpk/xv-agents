---
slice: 2026-11-05-directed-edit
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-05-directed-edit.md
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: The watch makes a directed change the person approved (#132), sixth pass

Needs a decision: none from two people. The shape is still the one the decision record accepted. There are no scenario misses and no wall recommendations. The merge is Sean's.

For Sean (not a stop):
- The fifth packet's finding C is closed. Fix A now has a test (check 3).
- The picture edits from the fifth packet still stand, unchanged (check 4).

## What changed since the fifth pass

- `653419c` (red) adds one test, `tests/test_record.py` `@@ -2076,6 +2076,22 @@`: `test_an_offer_run_from_the_main_checkout_checks_the_file_in_the_slices_worktree`. It also updates the wall baseline to `c127857` (`test_record.py` 386 → 389 assertions).
- The record adds amendment 5 (`.xv/slices/2026-11-05-directed-edit.md:79-81`) and settles the scenario stop.
- No source, brief or CHANGELOG line changed. `git diff c127857..HEAD -- scripts skills CHANGELOG.md` is empty.

## The scenario

A stop option can carry one directed edit, as exact old and new text that the person approves. There are four kinds: `changelog`, `test-rename`, `test-remove` and `doc`. `xv record answer --pick` then does the following:
- It makes the edit in its own commit, which names the person.
- It records a test edit as a move in the person's name.
- It renames the test in `slice_only` and `wall_recommendations`.
- It runs the suite and the orders, and writes a stop through `apply_verdict`.
- After the guardian, it adds a line to the packet in the same commit.

Amendments 1 to 4 add these:
- `scripts/suite.py`.
- `doc` refuses `.xv/` and `SKILL.md`.
- An edit may not hold a blank line.
- A test kind accepts only a whole test, with its decorators.
- A rename is refused when its old name appears elsewhere in the file, or when its new name is already in use.
- The packet line names no commit.
- The answer works in the slice's worktree.

Amendment 5 adds that `xv record offer` checks the edit against the file in the slice's worktree, wherever it is run from.

May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. To replay, run `cd tests && python3 -m unittest test_record.DirectedEditTest`. At HEAD `653419c` it ran 45 tests, OK. The whole suite (`python3 tests/run.py --jobs 4`) ran 837 tests, OK.

The settled answer to `scenario_stopped` records the red's before and after: the new test fails with the old line (`root = repo_root()`) and passes with `75c8e31`. I did not re-run it against the old line, because the guardian may not edit code.

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Module added: `scripts/suite`. Touched: `scripts/record`, `scripts/run`, `scripts/suite`.
- Edges added: `scripts/record → scripts/suite` and `scripts/run → scripts/suite`. None removed.
- Tables, surface paths and outbound calls: none.

`653419c` touches only a test file and the record.

## What the suite asserts after

`DirectedEditTest` asserts what it asserted in the fifth pass, plus one new test (`tests/test_record.py:2079-2093`). The test does the following:
- It commits `tests/test_only_here.py` on the slice branch.
- It asserts that the file is absent from the main checkout.
- It runs `xv record offer` with a `test-rename` from the main checkout (`cwd=self.repo`).
- It asserts that the offer exits 0 and that the stop has two options.
- It picks option 1 and asserts the renamed `def` is in the worktree's file.

## 1. Shape

shape_change: accepted, by `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`. It settled: "record does not import run; run_suite and its helpers move to scripts/suite.py". shape_breadth: narrow. The forecast expected `wide`.

- **Hint "a module was added" (`scripts/suite`).** It changes the shape, and the decision accepted it.
- **Hint "an edge between modules was added" (`record → suite`, `run → suite`).** It changes the shape, and the decision accepted it.
- **`653419c` stays inside it.** It changes only `tests/test_record.py` and the record (`git show --stat 653419c`).

## 2. Pitch

pitch_contradiction: no. The lines checked are unchanged from the fifth pass:
- `.xv/pitch.md:7`, "to vibe with discipline". The edit carries only the person's approved words.
- `.xv/pitch.md:11`, where the pitch changes when a second person agrees. `doc` refuses `.xv/` (`scripts/record.py:376`).
- `.xv/pitch.md:25`, "not for people or projects that will not trust agents".

`653419c` adds a test, and none of these lines bears on it.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `test_the_changelog_names_the_directed_edit`: `#132` is under `## Unreleased` | removed | slice-only, accepted by Sean | No. It is a slice-only removal |
| `tests/test_record.py` | `test_the_changelog_line_names_every_refusal_and_the_suite_module`: the `#132` line names every refusal | removed | slice-only, accepted by Sean | No. It is a slice-only removal |

Slice-only tests removed: `test_the_changelog_names_the_directed_edit`, `test_the_changelog_line_names_every_refusal_and_the_suite_module`. Kept: none.

`xv wall diff 2026-11-05-directed-edit` against the new baseline `c127857` shows nothing changed, deleted or with fewer assertions. The baseline moved at the red, from `23c54ff` (386) to `c127857` (389) (`.xv/slices/2026-11-05-directed-edit.wall.json` `@@ -46,7 +46,7 @@`). The 3 extra assertions are the new test's. No old test changed in `653419c`. `may_not_files` is empty.

**Finding C, closed.** The fifth packet said fix A had no test. Now `tests/test_record.py:2087-2089` runs the offer with `cwd=self.repo` on a test that exists only on the slice branch (`:2083`, `assertFalse(os.path.exists(...self.repo...))`). The settled answer records that this test fails with `root = repo_root()` and passes with `scripts/record.py:415` `root = slice_root(path)`.

## 4. The picture

`.xv/picture.md` is not in the slice's diff, so the fifth packet's proposed edits still stand as written:
- `.xv/picture.md:21`: 25 modules, 22 in `scripts/`, 65 edges, and "`record` and `run` reach `suite`".
- `.xv/picture.md:23`: what `suite` does, and what the offer and the answer do with a directed edit. Both read and edit the file in the slice's worktree, wherever they are run from (`scripts/record.py:415`, `:490`). Also, `xv record answer` is a caller of `apply_verdict` (`scripts/record.py:574`).
- `.xv/picture.md:27`: a directed test edit records a move by the person (`scripts/record.py:566`).
- `.xv/picture.md:36`: this is not a directed `doc` edit, because `doc` refuses `.xv/`.
- `.xv/picture.md:43`: an option may carry one directed edit.

`653419c` adds nothing to these. Binding decisions: `.xv/picture.md:64-78`. A test-only commit touches none of them.

## 5. The wall

No recommendations. What I looked at:
- The new test `test_an_offer_run_from_the_main_checkout_checks_the_file_in_the_slices_worktree` is not marked slice-only. It guards behaviour that amendment 5 names (`.xv/slices/2026-11-05-directed-edit.md:81`), so it joins the wall as it is.
- The two slice-only tests are already accepted off the wall (record `slice_only`, both `accepted: true`).
- No wall test is made dead.

## Door

**Door:** two-way. A revert removes the flags, the commit path, `scripts/suite.py` and the tests. The slice makes no directed edit itself. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. This pass: `git show 653419c`.
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `.xv/slices/2026-11-05-directed-edit.boundary.md`

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

# Packet: The watch makes a directed change the person approved (#132), fifth pass

Needs a decision: none from two people. The shape is still the one the decision record accepted. There are no scenario misses, and no new wall recommendations.

For Sean (not a stop):
- Fix A in `75c8e31` (the offer checks the slice's worktree) has no test. The brief and the CHANGELOG now state it as a rule (check 3, finding C).
- The picture edits you accepted still stand. This pass adds one line to them (check 4).

## What changed since the fourth pass

Only Sean's commit `75c8e31` and the uncommitted record update (status, budget, three log lines) changed. `git show 75c8e31 --stat` lists:
- `scripts/record.py`: 2 lines.
- `skills/watch/SKILL.md`: 1 line.
- `CHANGELOG.md`: 1 line.
- The record: two log lines.

Both of the fourth packet's findings for Sean are closed:
- **A, closed.** `scripts/record.py` `@@ -412,8 +412,8 @@`: `-    root = repo_root()` becomes `+    root = slice_root(path)`, and `check_edit(root, ...)` (`scripts/record.py:420`) now reads the file in the record's checkout. This matches the answer's `edit_root = slice_root(path)` (`scripts/record.py:490`). `root` is used for nothing else in `cmd_offer`.
- **B, closed.** `skills/watch/SKILL.md` `@@ -45,7 +45,7 @@` adds "A `test-rename` to a name the file already uses. The offer and the answer both work in the slice's worktree, wherever they are run from." The `#132` line in `CHANGELOG.md` `@@ -4,7 +4,7 @@` adds the same two points.

## The scenario

A stop option can carry one directed edit, as exact old and new text that the person approves. There are four kinds: `changelog`, `test-rename`, `test-remove` and `doc`. `xv record answer --pick` then does the following:
- It makes the edit in its own commit, which names the person.
- It records a test edit as a move in the person's name.
- It renames the test in `slice_only` and `wall_recommendations`.
- It runs the suite and the orders, and writes a stop through `apply_verdict`.
- After the guardian, it adds a line to the packet in the same commit.

The four amendments add these:
- `scripts/suite.py`.
- `doc` refuses `.xv/` and `SKILL.md`.
- An edit may not hold a blank line.
- A test kind accepts only a whole test, with its decorators.
- A rename is refused when its old name appears elsewhere in the file, or when its new name is already in use.
- The packet line names no commit.
- The answer works in the slice's worktree.

May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. To replay, run `cd tests && python3 -m unittest test_record.DirectedEditTest`. At HEAD `75c8e31` it ran 44 tests, OK. The whole suite (`python3 tests/run.py --jobs 4`) ran 836 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Module added: `scripts/suite`. Touched: `scripts/record`, `scripts/run`, `scripts/suite`.
- Edges added: `scripts/record → scripts/suite` and `scripts/run → scripts/suite`. None removed.
- Tables, surface paths and outbound calls: none.

`75c8e31` adds no import, module or edge.

## What the suite asserts after

`DirectedEditTest` (`tests/test_record.py:1474` onward) asserts the same things as in the fourth pass. `75c8e31` changes no test. Every offer in `DirectedEditTest` still runs from the worktree (`tests/test_record.py:1520-1523`, `cwd=self.wt`). Only the answer has a test run from the main checkout (`tests/test_record.py:2059`).

## 1. Shape

shape_change: accepted, by `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`. It settled: "record does not import run; run_suite and its helpers move to scripts/suite.py". shape_breadth: narrow. The forecast expected `wide`.

- **Hint "a module was added" (`scripts/suite`).** It changes the shape, and the decision accepted it.
- **Hint "an edge between modules was added" (`record → suite`, `run → suite`).** It changes the shape, and the decision accepted it.
- **`75c8e31` stays inside it.** The `scripts/record.py` hunk `@@ -412,8 +412,8 @@` swaps one function call (`repo_root()` for `slice_root(path)`). Both come from `xvlib`, which `record` already imported.

## 2. Pitch

pitch_contradiction: no. The lines checked are unchanged from the fourth pass:
- `.xv/pitch.md:7`, "to vibe with discipline". The edit carries only the person's approved words.
- `.xv/pitch.md:11`, where the pitch changes when a second person agrees. `doc` refuses `.xv/` (`scripts/record.py:376`).
- `.xv/pitch.md:25`, "not for people or projects that will not trust agents".

`75c8e31` touches none of these.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `test_the_changelog_names_the_directed_edit`: `#132` is under `## Unreleased` | removed | slice-only, accepted by Sean | No. It is a slice-only removal |
| `tests/test_record.py` | `test_the_changelog_line_names_every_refusal_and_the_suite_module`: the `#132` line names every refusal | removed | slice-only, accepted by Sean | No. It is a slice-only removal |

**Slice-only removals:** both are removed, and none is kept.

`xv wall diff` (baseline `23c54ff`) still shows `tests/test_record.py` going from 386 to 385 assertions. That is the second row, and it has no other cause. `75c8e31` changes no test file. `may_not_files` is empty.

**Finding C, for Sean.** Fix A has no test. The brief and the CHANGELOG now state it as a rule.
- Evidence: `skills/watch/SKILL.md` `@@ -45,7 +45,7 @@`, "+The offer and the answer both work in the slice's worktree, wherever they are run from." The test for the offer helper runs it with `cwd=self.wt` (`tests/test_record.py:1520-1523`). The only main-checkout test, `test_an_answer_run_from_the_main_checkout_edits_tests_and_commits_in_the_slices_worktree` (`tests/test_record.py:2059-2076`), also runs its `self.offer(*self.RENAME)` from the worktree.
- Failure if reverted: if `root = repo_root()` came back at `scripts/record.py:415`, the suite would stay green. An offer from the main checkout of a rename that exists only on the slice branch would again be refused as "found 0 times".
- This is not a scenario miss. Amendment 4, item 3 (`.xv/slices/2026-11-05-directed-edit.md:77`) names only `xv record answer --pick`. The rule for the offer is a brief and CHANGELOG line that Sean wrote.

## 4. The picture

The edits Sean accepted from the fourth packet still stand:
- `.xv/picture.md:21`: 25 modules, 22 in `scripts/`, 65 edges, and "`record` and `run` reach `suite`".
- `.xv/picture.md:23`: what `suite` does, what the offer and the answer do with a directed edit, and that `xv record answer` is a caller of `apply_verdict` (`scripts/record.py:574`).
- `.xv/picture.md:27`: a directed test edit records a move by the person (`scripts/record.py:566`).
- `.xv/picture.md:36`: this is not a directed `doc` edit, because `doc` refuses `.xv/`.
- `.xv/picture.md:43`: an option may carry one directed edit.

One addition from `75c8e31`. In the `.xv/picture.md:23` line on the offer, say that both `xv record offer` and `xv record answer --pick` read and edit the file in the slice's worktree, wherever they are run from (`scripts/record.py:415`, `root = slice_root(path)`; `:490`).

Binding decisions: `.xv/picture.md:64` (1) holds for `75c8e31`. It changes the watch's brief and has a `CHANGELOG.md` line, decided by Sean, solo. I found nothing else in `.xv/picture.md:64-78` that the commit touches.

## 5. The wall

No new recommendations. The two slice-only tests are already accepted off the wall (record `wall_recommendations`, both `accepted: true`). `75c8e31` adds or removes no test.

## Scenario misses

None. `75c8e31` changes no line a scenario point or amendment governs, apart from the offer's root. The scenario does not name that. The fourth pass's check of points 1 to 6 and amendments 1 to 4 against the red still holds: the red is 44 tests, OK, at `75c8e31`.

## Door

**Door:** two-way. A revert removes the flags, the commit path and `scripts/suite.py`. The slice makes no directed edit itself. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. This pass: `git show 75c8e31`.
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `.xv/slices/2026-11-05-directed-edit.boundary.md`

---
slice: 2026-10-27-wall-red-files
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: ci
---

# Packet: The wall sees old tests in a red file

Nothing stops this for two people. Sean, as the person who set the work going, has three things to decide: the picture edit (check 4); whether the slice's own check also has to see an old-test edit made before the baseline (finding 5.1); and the fact that this check change was decided by one person while `.xv/picture.md:60` asks for two (finding 5.3).

## The scenario

Today the CI wall (`xv wall check --base`) treats every file on `red.files` as covered, so an old test in a red file can be changed or deleted and nothing is reported. After the fix, if a red file existed at the base, only the tests the slice added count as the red. Every old test and assertion in that file must still be there unchanged, unless a recorded move names the file; otherwise the file is `unrecorded`. A red file that is new in the slice is still covered whole. Example: `tests/test_store.py`. Adding `test_renewal` passes. Changing `test_expiry`'s `30` to `31`, or deleting `test_expiry`, without a move fails. The record also says this changes a check, Sean decided it solo, and it gets a CHANGELOG line (#53). May ignore: nothing stated.

## The recording

None; it is a defect stated in words. To replay the red and the green: `cd tests && python3 -m unittest test_wall.WallRedFileTest`. Before (red, record `red.failure`): `AssertionError: Tuples differ: (0, []) != (1, ['tests/test_store.py'])`, 2 of 5 failing. After: I ran it and got `Ran 5 tests ... OK`. The maker and the cleaner each ran the whole suite: 301 tests OK.

## The boundary picture

From `.xv/slices/2026-10-27-wall-red-files.boundary.md`, as given: touched `scripts/wall`. No modules added or removed. No edges added or removed. No new outbound calls. No tables. No surface paths added or removed. Shape hints: none.

## What the suite asserts after

In `tests/test_wall.py`, `WallRedFileTest` (lines 97–152) runs a slice whose red file existed at the base and checks `xv wall check --base main`:
- Adding a test to that red file passes: exit 0, nothing unrecorded.
- Changing an old assertion in it (`("bread", 0)`) fails: exit 1, `tests/test_store.py` unrecorded.
- Deleting an old test from it fails: exit 1, `tests/test_store.py` unrecorded.
- The same old-assertion change with a recorded move naming the file passes.
- A red file new in the slice, changed after the baseline, with a recorded move, passes.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"`.
- The boundary picture lists no added modules, edges, tables, surfaces or outbound calls, and no shape hints (`.xv/slices/2026-10-27-wall-red-files.boundary.md:7`, `- none`; lines 12–19, 105–111).
- The diff adds one function inside `scripts/wall` (`scripts/wall.py:120`, `def removed_lines(root, base, rel)`), which uses `git` from the existing `xvlib` edge. It also changes one line, `scripts/wall.py:150`: `covered |= {f for f in red if f not in in_base or not removed_lines(root, base, f)} | recorded`.
- This stays within the shape the picture gives: "`wall` holds the test hash check" (`.xv/picture.md:23`). The CLI surface `xv wall check --base` (`.xv/picture.md:27`, `ci/github/xv-wall.yml:35`) keeps its flags and its JSON keys. It now fails on more inputs, and that is a check change, not a shape change.
- The breadth matches the forecast: `scripts/wall.py`, `tests/**` and a CHANGELOG line. The diff touches exactly those files, plus the slice's own `.xv/slices/` files.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7`, "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline.", and `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code." A stricter test wall fits the first line, and the change has nothing to do with the second. I found no line it contradicts.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Sources: the record has `moved_tests: []`. `xv wall diff 2026-10-27-wall-red-files` shows `changed: []`, `deleted: []`, `fewer_assertions: []`. `git diff 23f8dd5..HEAD -- tests/test_wall.py` is one hunk, `@@ -94,5 +94,63 @@`, which only adds lines. Under the new rule, this slice's own red file is covered.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

`.xv/picture.md:23` says "`wall` holds the test hash check". After this change, the CI form also reads a line diff against the base, and the picture never says how red files are covered. Proposed edit: add to the `wall` sentence, or to the shape bullet at `.xv/picture.md:26`: "In the CI form (`xv wall check --base`), a red file that existed at the base is covered only for lines the slice added. A changed or removed line in it is unrecorded unless a recorded move names the file. A red file new in the slice is covered whole." Sean accepts or rejects this; I have not written it.

## 5. Findings for the person who set the work going

1. **The slice's own check still misses the case; only CI sees it.** The scenario says "otherwise the file is `unrecorded`, in the CI form (`xv wall check --base`) as in the slice's own check" (record, Scenario). The fix only changes `check_against_base` (`scripts/wall.py:150`). The watch's step check calls `wall.check(root, data["id"], config)` (`scripts/run.py:594`), and that compares against the wall baseline, which is taken after the red. So if the scenario agent edits an old test in a red file before the baseline, the slice's run will not stop for it; the pull request's CI will. If "as in the slice's own check" means the slice's run must also catch it, that part is not done. If it only means "the same `unrecorded` result", it is. The words allow either reading.
2. **The rule is stricter than the scenario's words.** The scenario protects "every test and assertion that was in the file at the base". `removed_lines` (`scripts/wall.py:120–124`) counts any `-` line from `git diff --unified=0`. That includes imports, comments, whitespace and helpers. For example, changing `from x import a` to `from x import a, b` in an old red file now fails CI unless a move is recorded. This matches the maker's brief, "Every changed or deleted line in a test file that existed before you started is a move" (`skills/maker/SKILL.md:26`), and the scenario brief, "Do not change an assertion that is already there" (`skills/scenario/SKILL.md:27`). It is stated here because it will produce `unrecorded` on edits that touch no test.
3. **The check was changed by one person.** `.xv/picture.md:60`: "A change to ... a check an agent is judged by needs two people and a line in `CHANGELOG.md`." The CHANGELOG line is there (`CHANGELOG.md:7`, "This changes a check; Sean decided it, solo"). `.xv/picture.md:52` records `seats.two_people: solo`, and `CHANGELOG.md:3` says "A version line without two names is a draft." The line sits under `## Unreleased` (`CHANGELOG.md:5`), so it stays a draft until two people agree.
4. **The new-file test does not test the new rule.** `test_a_red_file_new_in_the_slice_is_covered_whole` (`tests/test_wall.py:142–152`) records a move and passes on the CI form. But a file that is not in the base never enters `tests_moved` (`scripts/wall.py:135`, `... and f in in_base and st in ("M", "D")`), so the red-coverage line never applies to it. The move it records is only needed by the since-baseline `check`. The test would pass at the base too, and it would also pass if the `f not in in_base` clause were removed: a new file's diff has no `-` lines, so it is covered anyway. Its name claims more than it asserts. The `f not in in_base` clause at `scripts/wall.py:150` changes no result.
5. **Wider reach, as intended.** `xv wall check --base` runs on every pull request in adopting repos (`ci/github/xv-wall.yml:35`, `README.md:313`). Any open slice branch whose red file changed an old line without a move will start failing CI after this merges. That is the purpose of the fix; it is listed so the effect on branches already open is not a surprise.

## Door

**Door:** two-way: a revert restores the old rule, and no data, record format or message is changed. **Blast radius:** ci.

## Raw data

- Slice record: `.xv/slices/2026-10-27-wall-red-files.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Wall: `xv wall diff 2026-10-27-wall-red-files`
- Boundary: `.xv/slices/2026-10-27-wall-red-files.boundary.md` (`xv boundary --base 23f8dd53788e`)

---
slice: 2026-10-27-scenario-rerun
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
door: two-way
blast_radius: small
---

# Packet: A scenario run after the maker keeps the red list and checks the right code

This is the third pass. Nothing stops it for two people, and the merge is Sean's. Both items Sean settled at the second stop are in. Two things need Sean's decision:

1. **`setup_failed` is now raised by `orders`.** Binding decision 10 says the command that failed raises it. Sean can move the fire into `run.py`, or amend decision 10.
2. **The scenario brief now says two things after the maker.** The new step 7 asks for every file. The report section still says "the test files you wrote or added to; `command` runs exactly those". Step 7 also sits under the `### With Playwright` heading.

Sean left the CHANGELOG lines and the move record for the renamed test to the watch at the merge. They are listed below so they are not missed.

## The scenario

#44, with (3) from #17. After the maker:
- A scenario report adds its red files to `red.files`.
- The red is checked against the code from before the maker, not HEAD.
- `--slice-only` counts only for a test on `slice_only`.

Settled by Sean on 2026-10-27:
- (a) Save the pre-maker commit once.
- (b) A failing setup in the check worktree is the `setup_failed` stop for the originator, quoting the setup's output, and `red_fails` is never `None` without a stop.
- (c) The scenario brief asks for the whole red after the maker.
- (d) Exact slice-only match, and the test is renamed.

May ignore: nothing stated.

## The recording

None (the defect is stated in words). Replay: `cd tests && python3 -m unittest test_record.ScenarioBriefTest.test_the_brief_asks_for_the_whole_red_after_the_maker test_run.RedFailsAfterTheMakerTest test_record.ScenarioRerunMergeTest test_record.SliceOnlyGateTest test_record.SliceOnlyMoveTest`
- **Before:** 2 failed. The record's `checks.scenario.red_output` shows `'setup_failed' not found in {}`.
- **After:** I ran them: 19 tests, OK.
- **Whole suite:** I ran it: 236 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-27-scenario-rerun.boundary.md`, as given:
- Touched: `scripts/orders`, `scripts/record`, `scripts/run`.
- Modules, edges, tables, surfaces and outbound calls added or removed: none.
- Shape hints: none.

## What the suite asserts after

- **The red list:**
  - Before the maker, a report replaces `red.files`.
  - After the maker, a report's files are added and a file is listed once.
  - The scenario brief contains "every file in the record's `red.files`" and "one command that runs all of them" (`tests/test_record.py:218`).
- **The red check after the maker:**
  - It runs at the pre-maker commit, and that holds across two reruns.
  - A red that passes there is not red.
  - Before the maker, the red still runs at HEAD.
  - Setup runs in the check worktree.
  - A failing setup fires `setup_failed` for the originator from `orders.verdict`, and the setup's output is in the question (`tests/test_run.py:235-244`).
- **`--slice-only`:** the marker is kept only when the file and the test name match exactly.

## 1. Shape

shape_change: no. shape_breadth: narrow, as the forecast expected (`"shape": "narrow"`). The boundary picture has no new module, edge, table or surface, and no shape hints. Everything stays inside the modules it touched:
- **The `pre_maker_commit` field.** It is set in `scripts/run.py:395-396`.
- **The temporary check worktree.** It is in `scripts/run.py:515-534`. The second pass covered it, and it has not changed since.
- **This pass:** two lines in `scripts/run.py:428-429` and two in `scripts/orders.py:86-87`.

**Findings for Sean:**
- **`setup_failed` is fired from the standing orders** (`scripts/orders.py:86-87`, against `.xv/picture.md:68`).
  - The new code at `scripts/orders.py:86-87`:
    ```
    if checks.get("setup_failed"):
        out.append(fire("setup_failed", "originator", checks["setup_failed"]))
    ```
  - Decision 10 (`.xv/picture.md:68`) says: "A stop raised because an action failed (`setup_failed`, `axis_not_named`) is not a standing order; the command that failed raises it."
  - Elsewhere, the command raises this stop itself: `cmd_slice_new`, `scripts/run.py:263-266`.
  - The test at `tests/test_run.py:235-244` asserts it through `orders.verdict`, so the scenario forced the placement.
  - Adding a fire to `orders.py` also changes a standing order, which needs a `CHANGELOG.md` line (`.xv/picture.md:59`; `scripts/orders.py` docstring, lines 6-8).
- **In-flight slices fall back to the wall baseline** (carried from the second pass). `scripts/run.py:517` reads `data.get("pre_maker_commit") or (data.get("wall_baseline") or {}).get("commit")`. This slice's record has no `pre_maker_commit`, because its first maker ran before the field existed.
- **The cleaner's shape proposal.** The "through the maker" test is written three times: `scripts/record.py:324`, `scripts/run.py:518`, and the guard at `scripts/run.py:395`. A shared helper would be a refactor inside the current modules, not a shape change.

## 2. Pitch

pitch_contradiction: no.
- I read `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (who uses it) and `:25` ("not for people or projects that will not trust agents … never be a teapot").
- The change tightens the watch's own checks for the same users (`scripts/orders.py:86-89`). No pitch line is touched.

## 3. Moved tests

`xv wall diff` shows nothing changed against baseline `6ff9750`. That baseline was taken again after both changes below, so the wall cannot see them. The source is `git diff 99ae369..HEAD -- tests/test_record.py`.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:274` `SliceOnlyMoveTest.test_a_move_with_slice_only_keeps_the_marker_and_a_plain_move_does_not` | A `--slice-only` move with nothing listed. Expects `slice_only: True`. | First lists `{file: tests/test_x.py, test: a}`, then expects `True`. | "a --slice-only move for a test not on slice_only is a plain move" (maker) | Yes, by (3). It asserts no less. Sean accepted it at both earlier stops. |
| `tests/test_record.py:282`, renamed from `test_removing_one_slice_only_test_from_a_file_that_stays_leaves_red_alone` to `test_a_plain_move_of_a_test_in_a_red_file_leaves_red_alone` | Body unchanged. | Body unchanged; only the name changed. | **No record.** Sean left this to the watch at the merge. | Yes. Sean asked for it in (d). It asserts no less. |

- **A weak old-pass test is left in.** `tests/test_run.py:228-233` (`test_a_failing_setup_is_not_a_red_that_counts_as_failing`) still passes on any exception. The new test at `:235` now covers the stop, so this is a note, not a gap.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

- **`.xv/picture.md:68` (decision 10) is now untrue.** `orders` raises `setup_failed`. Sean chooses one:
  - Keep the decision: `post_step` or `step` in `run.py` raises the stop, as `cmd_slice_new` does. Then the picture needs no edit.
  - Or amend the decision to: "…the command that failed raises it, except the after-maker red check, whose `setup_failed` the standing orders read from `checks.scenario.setup_failed`."
- **`.xv/picture.md:26` is incomplete.** Proposed addition: "The slice record keeps `pre_maker_commit`, HEAD before the maker's first run. After the maker, a scenario step checks the red in a temporary detached worktree at that commit, outside `.xv/worktrees/`, with the red files copied from HEAD and `worktrees.setup` run first. A failing setup there is the `setup_failed` stop."
- **The scenario brief contradicts itself after the maker** (not the picture, but decision 13 at `.xv/picture.md:71` governs briefs).
  - `skills/scenario/SKILL.md:35` asks for every file in `red.files` and one command for all of them.
  - `skills/scenario/SKILL.md:46` still says "`files` are the test files you wrote or added to; `command` runs exactly those".
  - Step 7 sits under `### With Playwright` (`skills/scenario/SKILL.md:29`), away from steps 1-6 under `## Make it red`.
- **`CHANGELOG.md:7-8` (left to the watch at the merge).**
  - Line 8 says the red is checked against "the wall baseline commit". Line 7 says it is checked against `pre_maker_commit`.
  - Line 7 says a failing setup "leaves `red_fails` unset". It does not say that this is now the `setup_failed` stop, or that the scenario brief changed. Both changes need a line (`.xv/picture.md:59`).

## Door

**Door:** two-way. A revert restores the old behaviour. The `pre_maker_commit` field left in records is ignored, and records stay valid YAML (`.xv/picture.md:67`). **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-27-scenario-rerun.md`. The cleaner made no change this pass, and the worktree's only uncommitted file is the boundary picture. The record and the diff agree.
- Diff: `git diff 99ae369ea03712578048ec10090c55dc5775b123..4f24552`. This pass alone: `git diff 65e4c3e..4f24552`.
- Wall: `xv wall diff 2026-10-27-scenario-rerun` (baseline `6ff9750`; nothing changed since).
- Boundary: `.xv/slices/2026-10-27-scenario-rerun.boundary.md` (`xv boundary --base 99ae369`).

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The behaviour is what Sean asked for in (b). Only where it lives breaks decision 10.

## From the cleaner

- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written twice, in scripts/record.py apply_report and scripts/run.py red_run. A shared helper in a common module would remove the duplication but is a new concept, so I left it for the packet.
- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written three times: scripts/record.py apply_report, and scripts/run.py red_run and its caller. A shared helper would remove the duplication but is a new concept, so it is left for the packet.
- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written three times: scripts/record.py apply_report, scripts/run.py red_run, and the pre_maker_commit guard. A shared helper in a common module would remove the duplication but is a new concept, so it is left for the packet.

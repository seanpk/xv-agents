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

This is the second pass. Nothing stops it for two people, and the merge is Sean's. Of the four things Sean settled at the last stop, (a) and (d) are done. (b) and (c) are each half done. Sean needs to decide on these, in this order:

1. **(b) A failing setup is not a stop. It passes silently.** `red_fails` becomes `None`, and no standing order reads `None`. This goes against binding decision 12.
2. **(c) The scenario brief was not changed.** The scenario agent still reports only the files it touched, with a command for those files alone. The record now keeps every old file, but `red.command` still runs only the newest ones.
3. **`CHANGELOG.md` has two lines for #44 that disagree** about which commit the red is checked against.
4. **A renamed old test has no move record.** Sean asked for the rename.

## The scenario

#44, with (3) from #17. After the maker:
- A scenario report adds its red files to `red.files`.
- The red is checked against the code from before the maker, not HEAD.
- `--slice-only` counts only for a test on `slice_only`.

Settled by Sean, 2026-10-27:
- (a) Save the pre-maker commit once and check the red against it, with a test of two reruns.
- (b) The check worktree runs `worktrees.setup`. A failing setup is the `setup_failed` stop, never a red.
- (c) After the maker, the scenario agent reports the whole red, and the record keeps every old file.
- (d) The `--slice-only` match uses the exact file and test name. Rename the test at `tests/test_record.py:276`.

May ignore: nothing stated.

## The recording

None (the defect is stated in words). Replay: `cd tests && python3 -m unittest test_record.ScenarioRerunMergeTest test_record.SliceOnlyGateTest test_run.RedFailsAfterTheMakerTest`.
- **Before:** 4 failed (record `checks.scenario.red_output`; the first is `test_the_check_worktree_runs_setup_first`).
- **After:** I re-ran them together with `SliceOnlyMoveTest`: 16 tests, OK.
- **Whole suite:** I ran it: 234 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-27-scenario-rerun.boundary.md`, as given:
- Touched: `scripts/record`, `scripts/run`.
- Modules, edges, tables, surfaces and outbound calls added or removed: none.
- Shape hints: none.

## What the suite asserts after

- **Before the maker:** a second report replaces `red.files`.
- **After the maker:** a report's files are added to `red.files` and a file is listed once. Nothing asserts `red.command`.
- **The red check after the maker:**
  - It runs at the pre-maker commit, and that commit holds across two reruns that add commits.
  - A red that passes there is not red.
  - Before the maker, the red still runs at HEAD.
  - Setup runs in the check worktree.
  - A failing setup is "not `True`". The test also passes if any exception is raised (`tests/test_run.py:228-233`).
- **`--slice-only`:** the marker is kept only when the file and the test name match exactly. A longer name, another file, or nothing listed gives a plain move.

## 1. Shape

shape_change: no. shape_breadth: narrow, which is what the forecast expected (`"shape": "narrow"`). The boundary picture has no new module, edge, table or surface, and no shape hints. Two changes are new, and both stay inside the current shape:
- **A new record field, `pre_maker_commit`.** It is set once in `pre_step` (`scripts/run.py:395-396`) and kept across the record reload (`scripts/run.py:355-356`). State stays in the slice file, as `.xv/picture.md:26` describes.
- **A temporary detached worktree for the red check.** It is created with `tempfile.mkdtemp(prefix="xv-red-")` … `git worktree add --detach` (`scripts/run.py:518-520`), outside `.xv/worktrees/`, and removed in `finally`. `tempfile` is in the standard library, so this keeps to `.xv/picture.md:61`.

**Findings for Sean:**
- **(b) A failing setup passes silently** (`scripts/run.py:526-528`, against `.xv/picture.md:70`).
  - `scripts/run.py:526-528` returns `None, "the worktree setup … failed"`, and `scripts/run.py:426` stores `red_fails = None`.
  - `scenario_not_red` fires only `if checks.get("red_fails") is False` (`scripts/orders.py:86`).
  - Nothing raises `setup_failed`. Today that stop is raised only in `cmd_slice_new` (`scripts/run.py:258-266`).
  - So the step goes on to the maker without a person. That goes against `.xv/picture.md:70`: "A check whose input is broken or that cannot run stops for a person; it never passes." It also misses Sean's (b), "a setup that fails is the `setup_failed` stop". Under `.xv/picture.md:68`, the command that failed raises that stop, not `orders`.
  - The test at `tests/test_run.py:228-233` cannot catch this. It accepts `None` or any exception.
- **(c) Half done: the files are kept, but the command covers only the newest files** (`scripts/record.py:327`, `skills/scenario/SKILL.md:44`).
  - `scripts/record.py:327`: `data["red"] = {**report["red"], "files": files}`.
  - The scenario brief still says "`files` are the test files you wrote or added to; `command` runs exactly those" (`skills/scenario/SKILL.md:44`).
  - So after a rerun, `red.files` lists every file, but `red.command`, the command the next agents are shown as "the red" (`scripts/prompt.py:64`), runs only the new ones.
  - Sean's (c) asks the scenario agent to report "every red file, and one command that runs all of them". That needs a brief change, which needs a `CHANGELOG.md` line (`.xv/picture.md:59`). Neither is in the diff.
- **In-flight slices fall back to the wall baseline.** `scripts/run.py:515`: `commit = data.get("pre_maker_commit") or (data.get("wall_baseline") or {}).get("commit")`. A slice whose first maker ran before this change has no `pre_maker_commit`. This slice is one; its record has none. For such a slice a second rerun gets the behaviour that (a) ruled out.
- **The cleaner's shape proposal: the "through the maker" test is written twice.** `any(s.get("step") == "maker" for s in data.get("spend") or [])` appears at `scripts/record.py:324` and `scripts/run.py:516`. Sharing it would be a refactor inside the current modules, not a shape change. It is relayed here for Sean.

## 2. Pitch

pitch_contradiction: no.
- Looked at `.xv/pitch.md:7`: "to vibe with discipline".
- Looked at `.xv/pitch.md:21`: who uses it.
- Looked at `.xv/pitch.md:25`: "not for people or projects that will not trust agents … never be a teapot".
- The change tightens the watch's own checks for the same users (`scripts/orders.py:86`). No pitch line is touched.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:268` `SliceOnlyMoveTest.test_a_move_with_slice_only_keeps_the_marker_and_a_plain_move_does_not` | A `--slice-only` move with nothing listed; expects `slice_only: True`. | First adds `{file: tests/test_x.py, test: a}` to `slice_only`, then expects `True`. | "a --slice-only move for a test not on slice_only is a plain move" (maker) | Yes, by (3). It asserts the same thing. `--assertion "a"` equals the listed `test`, so the exact match holds. Sean accepted it at the last stop ("1. yes"). |
| `tests/test_record.py:276` `test_removing_one_slice_only_test_from_a_file_that_stays_leaves_red_alone` → `test_a_plain_move_of_a_test_in_a_red_file_leaves_red_alone` | Same body: a `--slice-only` move with nothing listed; `red` unchanged. | Same body and assertions; only the name changed. | **No record.** The scenario agent made the change in commit `c3741f4`. | Yes. Sean's (d) asked for this rename. It asserts no less. |

- **Why the wall did not see the rename.** `xv wall diff` shows nothing changed (baseline `23e166c`). The wall baseline was taken again at the second scenario step, after the rename. The diff `git diff 99ae369..HEAD -- tests/test_record.py` shows it.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

- **`.xv/picture.md:26` is incomplete.** It says each slice has a worktree under `.xv/worktrees/` and that `worktrees.setup` runs before the forecaster. Proposed addition: "The slice record keeps `pre_maker_commit`, HEAD before the maker's first run. After the maker, a scenario step checks the red in a temporary detached worktree at that commit, outside `.xv/worktrees/`, with the red files copied from HEAD and `worktrees.setup` run first."
- **`.xv/picture.md:23` still holds.** `run` computes `red_fails` (`scripts/run.py:426`) and `orders` reads it (`scripts/orders.py:86`).
- **`CHANGELOG.md:7-8` (not the picture, but read with it).** Line 8, from the first pass, says the red is checked against "the wall baseline commit". Line 7 says it is checked against `pre_maker_commit`. Decision 1 (`.xv/picture.md:59`) makes this file the record of check changes. Sean should merge the two lines into one that is true.

## Door

**Door:** two-way. A revert restores the old behaviour. The `pre_maker_commit` field left in records is ignored, and records stay valid YAML (`.xv/picture.md:67`). **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-27-scenario-rerun.md`. The cleaner reports `committed: false`, but its change is in `b342d30` and the worktree is clean. The record and the diff agree.
- Diff: `git diff 99ae369ea03712578048ec10090c55dc5775b123..b342d30`
- Wall: `xv wall diff 2026-10-27-scenario-rerun` (baseline `23e166c`; nothing changed since)
- Boundary: `.xv/slices/2026-10-27-scenario-rerun.boundary.md` (`xv boundary --base 99ae369`)

## From the cleaner

- Shape proposal, for people: the "slice has been through the maker" test is written more than once (`scripts/record.py:324`, `scripts/run.py:516`). A shared helper is a new concept, so it was left for the packet.

## From the cleaner

- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written twice, in scripts/record.py apply_report and scripts/run.py red_run. A shared helper in a common module would remove the duplication but is a new concept, so I left it for the packet.
- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written three times: scripts/record.py apply_report, and scripts/run.py red_run and its caller. A shared helper would remove the duplication but is a new concept, so it is left for the packet.

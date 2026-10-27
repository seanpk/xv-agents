---
slice: 2026-10-27-scenario-rerun
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: small
---

# Packet: A scenario run after the maker keeps the red list and checks the right code

Nothing stops this change for two people. The merge is Sean's call. Four things need a decision from Sean first, in this order:
1. **The fix for (2) holds for one rerun only.** The scenario step rewrites the wall baseline to HEAD each time it runs, so a second rerun checks the red against the fixed code again.
2. **The baseline worktree skips `worktrees.setup`.** A red that cannot run there counts as red.
3. **The merged red keeps the old files but only the new command.**
4. **The slice-only gate matches test names by substring.**

## The scenario

Issue #44, plus part (3) from the guardian on #17. (1) Once the slice has been through the maker, a scenario report's red is added to `red.files` and the earlier files stay. Before the maker, the report still replaces `red`. (2) Once the slice has been through the maker, `red_fails`, which `scenario_not_red` reads, runs the red command against the wall baseline commit, not HEAD. (3) `--slice-only` keeps its marker only for a test on the record's `slice_only` list. Any other move is a plain move, and `accept_moves` fires for it. May ignore: nothing stated.

## The recording

None (defect stated in words). Replay: `cd tests && python3 -m unittest test_record.ScenarioRerunMergeTest test_record.SliceOnlyGateTest test_run.RedFailsAfterTheMakerTest`.
- Before: 5 of 9 fail (the record's `checks.scenario.red_output`).
- After: all pass. I re-ran them together with `test_record.SliceOnlyMoveTest`: 11 tests, OK.
- Whole suite: green after the maker and after the cleaner (229 tests, record `checks.cleaner.suite`).

## The boundary picture

From `.xv/slices/2026-10-27-scenario-rerun.boundary.md`, as given:
- Touched: `scripts/record`, `scripts/run`.
- Modules, edges, tables, surfaces and outbound calls added or removed: none.
- Shape hints: none.

## What the suite asserts after

- **Before the maker:** a second scenario report replaces `red.files`.
- **After the maker:** a report adds its files to `red.files`, keeps the earlier ones and lists a repeated file once. The command is not asserted.
- **Red check after the maker:** a red command that fails at the wall baseline and passes at HEAD counts as red. One that passes at the baseline is not red. Before the maker, the command still runs at HEAD. Only one rerun is exercised, and red files are not copied in the test (`tests/test_new.py` does not exist).
- **`--slice-only` moves:** a listed test keeps the marker. An unlisted test, or any test when nothing is listed, gives a plain move.
- **Moved:** `SliceOnlyMoveTest` now lists the test before its `--slice-only` move.

## 1. Shape

shape_change: no. shape_breadth: narrow, which is what the forecast expected (`"shape": "narrow"`).

- **The one new import is `tempfile`** (`scripts/run.py:26`), which is in the standard library. That keeps to `.xv/picture.md:61` ("standard library only").
- **A new runtime artefact inside the current shape.** After the maker, the scenario step now creates a temporary detached git worktree outside `.xv/worktrees/` and removes it when done (`scripts/run.py:514-524`, `tempfile.mkdtemp(prefix="xv-red-")` … `git worktree add --detach tmp commit` … `git worktree remove --force tmp`). This makes the picture incomplete (section 4); it does not change the shape.
- **The cleaner's shape proposal: the "through the maker" test is written twice.** `any(s.get("step") == "maker" for s in data.get("spend") or [])` appears at `scripts/record.py:324` and `scripts/run.py:512`. Sharing it would be a refactor inside the current modules. It is relayed here for Sean and is not a shape change.

**Findings for Sean (they do not stop the change for two people):**

- **(a) Part (2) holds for the first rerun only.** `scripts/run.py:421` runs `red_run` with the record's `wall_baseline.commit`. Then `scripts/run.py:426-428` (`wb = wall_baseline(root, data, config)` / `data["wall_baseline"] = wb`) runs on every scenario step. `scripts/wall.py:64,73` sets `"commit": head`. So after the first post-maker rerun, the baseline commit is the maker's HEAD. A second rerun then runs the red against code that already has the fix, and `scenario_not_red` fires again, which is the #44 defect. The red reads the baseline as "the slice's code from before the maker's first change". After the first rerun the commit is no longer that. No test covers two reruns. Re-baselining also resets what `xv wall diff` compares against. That behaviour is older than this slice, but this slice now depends on it.
- **(b) A red that cannot run at the baseline counts as red.** The temporary worktree is created at `scripts/run.py:516`. Only `red.files` are copied in (`scripts/run.py:517-520`), and `worktrees.setup` is never run. The picture says setup runs before the forecaster (`.xv/picture.md:26`). Two cases make the red fail for the wrong reason, so `red_fails` is `True` and `scenario_not_red` cannot fire:

  This goes against `.xv/picture.md:70`: "A check whose input is broken or that cannot run stops for a person; it never passes." It has no effect on this repo, which is standard library only and has no setup. Separately, a failed `git worktree add` raises (`check=True`, `scripts/run.py:516`). That stops the step rather than passing it.
- **(c) After the merge, the red's files and command disagree.** `scripts/record.py:327` builds `data["red"] = {**report["red"], "files": files}`. So `red.files` keeps x, y and z, while `command`, `failure` and `watch_first_green` come from the new report alone (here, only `tests.test_z`). The next agents are shown that pair as "the red" (`scripts/prompt.py:64`), and `cmd_move` edits the command assuming it covers the files (`scripts/record.py:183-190`). The scenario's "its files join `red.files` and the rest stay" can be read either way. Sean should say which reading is meant. `ScenarioRerunMergeTest` asserts only `files`.
- **(d) The slice-only gate matches by substring.** `scripts/record.py:175-176` checks `s["test"] in a.assertion`.
  - The moved test lists a test named `"a"` (`tests/test_record.py:270-271`), which matches almost any assertion text.

  The marker hides a move from `accept_moves` (`scripts/orders.py:159`). That makes this the gate the scenario asked to tighten. The match is only as tight as the cleaner's `--assertion "<the test>"` wording (`skills/cleaner/SKILL.md:39`).

## 2. Pitch

pitch_contradiction: no.
- **Looked at:** `.xv/pitch.md:7` ("vibe with discipline"), `.xv/pitch.md:21` (who uses it) and `.xv/pitch.md:25` (not for people who will not trust agents; never a teapot).

**Decision rule.** `.xv/picture.md:59` requires two people and a `CHANGELOG.md` line for a change to a check or standing order. The line is there (`CHANGELOG.md:7`, "This changes a check and a standing order; Sean decided it, solo"). The team is solo (`.xv/picture.md:51`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` `SliceOnlyMoveTest.test_a_move_with_slice_only_keeps_the_marker_and_a_plain_move_does_not` | `--slice-only` move with nothing listed; expects `slice_only: True` | first adds `{file: tests/test_x.py, test: a}` to `slice_only`, then expects `slice_only: True` | "a --slice-only move for a test not on slice_only is a plain move" | Yes, part (3). It asserts the same thing (54 → 54 assertions in the file, `xv wall diff`). It is the only recorded move, and the wall finds nothing unrecorded. |

- **A test that now exercises a different path.** `tests/test_record.py:276`, `test_removing_one_slice_only_test_from_a_file_that_stays_leaves_red_alone`, was not edited. It still passes `--slice-only` with nothing listed, so it now exercises a plain move. It still asserts `red` is unchanged, so it asserts no less, but its name no longer matches what it covers. This is probably the second of the "two existing tests will conflict with the gate" that the scenario reported. No move was recorded for it, because it did not change.

## 4. The picture

- **`.xv/picture.md:26` is incomplete.** It says each slice has a worktree under `.xv/worktrees/` and that `worktrees.setup` runs before the forecaster. Proposed addition: "After the maker, a scenario step runs the red in a temporary detached worktree at the wall baseline commit, outside `.xv/worktrees/`, with the red files copied from HEAD; `worktrees.setup` does not run there." If finding (b) is fixed, the end of that sentence changes.
- **`.xv/picture.md:23` ("`record` owns the slice record. `orders` holds the stop rules.") still holds.** `red_fails` is computed in `run` (`scripts/run.py:421`) and read by `orders` (`scripts/orders.py:86`), as before.

## Door

**Door:** two-way. A revert restores the old replace-the-red and red-at-HEAD behaviour. No data is migrated, and records written meanwhile stay valid YAML/JSON. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-27-scenario-rerun.md`. The cleaner's check says `committed: false`, but its rename is in `e957421` and the worktree is clean apart from the boundary file. The record and the diff agree on what changed.
- Diff: `git diff 99ae369ea03712578048ec10090c55dc5775b123..e957421`
- Wall: `xv wall diff 2026-10-27-scenario-rerun` (baseline `5e6a767`; `tests/test_record.py` changed, 54 → 54 assertions, none fewer, none unrecorded)
- Boundary: `.xv/slices/2026-10-27-scenario-rerun.boundary.md` (`xv boundary --base 99ae369`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- No new module, edge, table or surface.** The boundary picture has none, and its shape hints are empty.
- An adopting repo whose tests need setup, such as installed dependencies.
- A scenario that added a helper or fixture outside `red.files`.
- A listed `test_a` would mark a move whose assertion text mentions `test_ab`.
- Result:** the change makes the watch's own checks more exact for the same users. Nothing in it serves someone else or breaks a promise.
- Slice-only tests:** none removed (`slice_only: []`); none kept.

## From the cleaner

- Shape proposal, for people: The 'slice has been through the maker' test (any spend item with step == maker) is written twice, in scripts/record.py apply_report and scripts/run.py red_run. A shared helper in a common module would remove the duplication but is a new concept, so I left it for the packet.

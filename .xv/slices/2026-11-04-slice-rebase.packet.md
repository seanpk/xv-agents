---
slice: 2026-11-04-slice-rebase
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: contained
---

# Packet: A slice can be brought up to date with its base: #20

This is the third pass. Nothing stops for two people. The two repeated misses from the second pass are closed to the targets Sean set: 16 (whole-name exception) and 6 (hash at `--onto`). One new miss remains, under point **11**. The maker's rebase brief tells it to fix logical breaks while it resolves a conflict, but only the conflicted files are staged before `git rebase --continue`. Key 11 was sent back on the first pass, so the watch will read this as a repeat, and it goes to Sean. Sean also decides the four findings in check 1 that are not misses, and accepts the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice branch on a new base. With no `--onto`, the default comes from `resolve_base`. A conflict in a test file or in `.xv/picture.md` stops for the person. `CHANGELOG.md` and `.xv/estimation.md` keep both sides. The maker resolves any other conflict in a fresh context with a rebase part in its brief, looks for logical breaks, fixes what it can, and stops on what it cannot fix. `base`, `pre_maker_commit` and `cleaner_commit` move, and a dropped named commit stops. The wall is hashed again for the test files the slice did not touch. The suite runs again, and a red suite stops. The exception is a test the slice added to its own red, while the maker has not yet made the suite green (16). It works on closed slices too. A stop leaves the rebase in progress, with `--continue` and `--abort` (14).

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red (16).

## The recording

None, since this is a feature. Replay: `cd tests && python3 -m unittest test_slice_rebase`. Before the maker, 4 of the 5 tests added on this pass failed and 1 guarded the other side of 16 (record, scenario report). I ran it now and got `Ran 36 tests in 87.118s OK`. In the cleaner's run the whole suite was green (record `checks.cleaner.suite`). I did not rerun the whole suite.

## The boundary picture

Taken from `.xv/slices/2026-11-04-slice-rebase.boundary.md` as given:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Modules added or removed: none.
- Edges added or removed: none.
- Outbound calls added: none.
- Tables: none.
- Surface paths: none.
- Shape hints: none.

## What the suite asserts after

The 31 tests from the earlier passes are unchanged. This pass adds 5 (`tests/test_slice_rebase.py:455-524`):
- A failing test that the slice added to an old red file is excused before the maker: the rebase exits 0.
- An old test in that same red file, broken by the new base, still stops.
- A test whose name only contains a red file's name (`test_run_loop_x` against red file `test_run.py`) still stops.
- The slice weakens an old test, and main edits the same file elsewhere. After the clean rebase, `xv wall diff` still lists the file as `changed`.
- The same file conflicts, and the person resolves it and runs `--continue`. `xv wall diff` still lists it as `changed`.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider.
- The boundary picture adds no module, edge, table or outbound call. `xv slice rebase` is a new subcommand of the `xv` CLI surface (`.xv/picture.md:28`), in `run.py`, where `slice` lands (`.xv/picture.md:22`). Its stops are in `orders` (`.xv/picture.md:23`, `.xv/picture.md:73` decision 10).
- This pass adds `wall.hashes_at` (`scripts/wall.py:63-70`) and rewrites `own_red_names` and `in_own_red` (`scripts/run.py:421-434`). All three are inside existing modules, so this is not a shape change.
- Three findings carried from the earlier passes are still true (`scripts/run.py:359-382`). They are not misses; Sean decides them.
  - **Rebase stops never reach the record.** `rebase_stop` (`scripts/run.py:359-367`) puts `data["checks"]` in memory, prints the verdict and exits, and never calls `record.apply_verdict`. The picture says that function "writes the stop or the send-backs" (`.xv/picture.md:23`). Every other step calls it (`scripts/run.py:639`).
  - **The rebase maker skips the budget gate.** `scripts/run.py:382` calls `agentcli.with_caps` without `orders.budget_before`, which the picture says runs "before every step" (`.xv/picture.md:23`). The other steps call it at `scripts/run.py:588`.
  - **Spend from an aborted rebase is lost.** Maker spend sits in the rebase state until `rebase_finish` copies it, and `--abort` deletes that state (`scripts/run.py:534` `os.remove(rebase_state_path(root, a.id))`). So `spend.slice_spend` undercounts the budget (`.xv/picture.md:23`).
- New, not a miss: the own-red names come from every `def`, `test`, `it` or `fn` on a line the slice added to a red file (`scripts/run.py:428` regex). A helper the slice adds, such as `def slice_adds_a_failing_test_to_an_old_file`, joins the excused names. So does an old test in another file that shares a name with a test the slice added. `names_test` matches the whole name anywhere in `test_x (module.Class.test_x)` (`scripts/xvlib.py:350-353`), so an old `test_store.StoreTest.test_milk_today` broken by the new base is excused when the slice's red adds a `test_milk_today` anywhere. This follows Sean's target ("matched by whole name with xvlib.names_test", record stop 2026-11-05T06:12:07). I'm listing it because it is the edge of that target.
- New, not a miss: a test file that both sides changed is now hashed as it is at `--onto` (`scripts/run.py:481`). The baseline is retaken at each scenario step (`wall_baseline.commit` `bf1c228` is mid-slice). So a slice change made before that baseline, which the wall did not show before, shows as `changed` after a rebase, and can raise `unrecorded_move` again. This errs on the side of showing more, and it matches Sean's target ("hashes each test file as it is at the --onto ref").

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The line this could touch is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). That line still holds: the maker resolves code conflicts, and test-file and picture conflicts stay with a person (`skills/maker/rebase.md:7`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

The record has `moved_tests: []`. `xv wall diff 2026-11-04-slice-rebase` against baseline `bf1c228` shows `changed`, `deleted`, `added` and `fewer_assertions` all empty. Since the base, `tests/fake_agent.py` has only additions (24 lines, gated on `FAKE_REBASE_MODE` and `FAKE_PROMPT_LOG`), and `tests/test_slice_rebase.py` is new. With `may_not_files: []` and `old_tests_forced: []`, there are no may-not edits to list.

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. They are the same as the second pass, plus the own-red rule.
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - Add that `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:162`).
  - Add that `xv slice rebase` prints its stop without writing it to `stops` (`scripts/run.py:359-367`), or change the code first (check 1).
  - Add that `prompt.build` takes a `part`, which the rebase uses to add `skills/maker/rebase.md` to the maker's brief (`scripts/prompt.py:177`).
  - Add that `wall.baseline` takes `keep` and `skip`, and that `wall.hashes_at` hashes files at a ref (`scripts/wall.py:63-85`).
- `.xv/picture.md:27` (state is files), add:
  - A rebase moves `base` to the `--onto` commit and moves the named commits by subject (`scripts/run.py` `rebase_finish`, `data["base"] = state["onto"]`).
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json` (`scripts/run.py:342`).
  - After a rebase, the wall keeps the old hash for a test file only the slice touched, and hashes a file both sides touched at `--onto` (`scripts/run.py:477-484`).
  - A red suite whose failing tests all carry names the slice added to its red files does not stop until the maker has made the suite green (`scripts/run.py:489`).
- `.xv/picture.md:36` (maker line): the rebase brief adds "Do not touch a test file, `.xv/picture.md` or anything under `.xv/` to make a conflict go away" (`skills/maker/rebase.md:7`).

## 5. The wall

No recommendations. I looked at the 5 tests added on this pass and the 31 from earlier passes. None is marked slice-only (`slice_only: []`). Each one checks behaviour that lasts. None restates another: the three tests for 16 cover three different sides of the exception, and the two for 6 cover a clean merge and a resolved conflict. No old wall test is made dead, since `xv wall diff` shows nothing changed.

## Scenario misses

- 11: a fix the maker makes outside the conflicted files during a conflict replay breaks the rebase. The rebase brief tells the same run that resolves a conflict to "look for what the new base changed that breaks or contradicts what the slice does … Fix what you can" (`skills/maker/rebase.md:6`), and "Do not stage" (`skills/maker/rebase.md:5`). But `rebase_drive` stages only the conflicted files before `git rebase --continue` (`scripts/run.py:411` `git(["add", "-A", "--"] + files, root)`). git's `rebase --continue` refuses when tracked files have unstaged changes ("You must edit all merge conflicts and then mark them as resolved using git add"). So `scripts/run.py:416-417` raises `XVError`: exit 2 and a misleading message, where point 11 asks for a fix or a stop for the person. The rebase stays in progress, and the run's `maker_ran` and spend are lost, because the state file is written only at `rebase_stop`. I did not run this; git's refusal is from its `rebase --continue` check. No red test has the stand-in maker edit a second file in `resolve` mode, and that mode stages its own file (`tests/fake_agent.py` `os.system(f"git add {path}")`) (evidence: `scripts/run.py:411`, `skills/maker/rebase.md:5-6`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand, and nothing is migrated, published or sent. **Blast radius:** contained. Changes to existing paths are additive and off by default: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` and `FAKE_PROMPT_LOG` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff a387beea489d472c139d9df358421afafa06f8ab..be7d187`. This pass alone: `git diff bf1c228..be7d187`. The hand rebase onto main is `7e7f01f`.
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `xv boundary --base a387beea489d472c139d9df358421afafa06f8ab` (as `.xv/slices/2026-11-04-slice-rebase.boundary.md`)

## From the cleaner

- Shape proposal, for people: pull the wall rehash block of `rebase_finish` (`scripts/run.py:474-484`) out into a function of its own. It stays inside `run`, so it is not a shape change.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.

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

This is the second pass. There is no stop for two people. Four of the five misses from the first pass are closed: 5, 11, the deleted and added half of 6, and decision 1. Two misses remain, under points **16** and **6**. Both keys were sent back on the first pass, so the watch reads them as repeats, and they go to Sean as originator. Sean also decides four findings that are not misses (check 1) and accepts the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice branch on a new base (default from `resolve_base`). Conflicts in a test file or `.xv/picture.md` stop for the person. `CHANGELOG.md` and `.xv/estimation.md` keep both sides. The maker resolves other conflicts in a fresh context with a rebase part in its brief, and looks for logical breaks. `base`, `pre_maker_commit` and `cleaner_commit` move, and a dropped named commit stops. The wall is hashed again for test files the slice did not touch. The suite runs again. A red suite stops, except a test in the slice's own red before the maker has made the suite green (16). Closed slices work too. A stop leaves the rebase in progress, with `--continue` and `--abort` (14).
May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). Replay: `cd tests && python3 -m unittest test_slice_rebase`. Before the maker, the 7 tests added on this pass failed: 5 on the code, 2 guarding the other side of 16 (record, scenario report). I ran it now and got `Ran 31 tests in 75.729s OK`. The whole suite is 960 OK in the cleaner's run (record `checks.cleaner.suite_output`). I did not rerun the whole suite.

## The boundary picture

From `.xv/slices/2026-11-04-slice-rebase.boundary.md`, as given. Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`. Modules added or removed: none. Edges added or removed: none. Outbound added: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

There are 24 tests from the first pass (see the first packet, commit `5aaa0b6`), and this pass adds 7:
- An open slice whose own red still fails rebases clean (exit 0).
- The own red failing after the maker made the suite green stops.
- A failing test outside the own red stops, even before the maker.
- A dropped named commit stops after a `--continue` from a test-file conflict stop.
- `--continue` runs the maker to look for logical breaks.
- `--continue` stops when that maker cannot fix a problem.
- The rehashed wall still shows the slice's own deleted test file (`tests/test_red.py`) and the test files it added.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none (the forecast said `wide`, so this is not wider).
- No module, edge, table or outbound call is added (the boundary picture: all `none`). `xv slice rebase` is a new subcommand inside the `xv` CLI surface (`.xv/picture.md:27`), landing in `run.py` (`.xv/picture.md:22`). The new stops sit in `orders`, where the picture puts stop rules (`.xv/picture.md:23`).
- This pass adds `in_own_red` (`scripts/run.py:421`) and `wall.baseline(..., skip=())` (`scripts/wall.py:61`). Both are inside existing modules, so they are not a shape change. The cleaner proposed pulling the wall rehash block out of `rebase_finish` into a function of its own (record `checks.reports`, cleaner). That would also stay inside `run`, so it is not a shape change either.
- These three are carried from the first pass. They are still true and are not misses; Sean decides them (`.xv/picture.md:23`).
  - Rebase stops never reach the record. `scripts/run.py:359-366` `rebase_stop` puts `data["checks"] = {"rebase": checks}` in memory, prints the verdict and exits, with no `record.apply_verdict`. The picture says that function "writes the stop or the send-backs" (`.xv/picture.md:23`). So `xv record answer` and `decisions` never see a rebase stop.
  - The rebase maker skips the budget gate. `scripts/run.py:382` calls `agentcli.with_caps` and never calls `orders.budget_before`, while `.xv/picture.md:23` says that check runs "before every step". `budget_before` runs for every other step at `scripts/run.py:575`.
  - Spend from an aborted rebase is lost. Maker spend sits in the rebase state until `rebase_finish` copies it, and `--abort` deletes that state (`scripts/run.py:500` `os.remove(rebase_state_path(root, a.id))`). `spend` then undercounts the budget (`.xv/picture.md:23`, "`spend.slice_spend` is the count the slice budget uses").
- New, not a miss, not run: when the maker resolves a conflict, only the conflicted files are staged (`scripts/run.py:411` `git(["add", "-A", "--"] + files, root)`). Then `git rebase --continue` runs. The brief tells that same run to "look for what the new base changed … Fix what you can" (`skills/maker/rebase.md:6`). A fix in another file is left unstaged when git continues. No test has the stand-in maker edit a second file in `resolve` mode (`tests/fake_agent.py`, `resolve` branch). I did not run a case to see whether git refuses the continue or the fix lands in the later `rebase` record commit.

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The one line this could touch, "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`), still holds: the maker resolves code conflicts, and test-file and picture conflicts stay with a person.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`moved_tests: []`. `xv wall diff 2026-11-04-slice-rebase` against baseline `5aaa0b6` shows changed, deleted, added and fewer_assertions all empty. Since the base, `tests/fake_agent.py` has only additions (24 lines, gated on `FAKE_REBASE_MODE`). `tests/test_slice_rebase.py` is new, and this pass added 83 lines and removed none. `may_not_files: []` and `old_tests_forced: []`, so there are no may-not edits to list.

Slice-only tests removed: none. Kept: none.

## 4. The picture

Proposed edits for Sean to accept:
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue`, `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - Add that `orders` decides four stops after `rebase` (`rebase_conflict`, `rebase_dropped`, `rebase_stuck`, `rebase_suite_red`) (`scripts/orders.py:162` `if after == "rebase":`).
  - Add that `xv slice rebase` prints its stop without writing it to `stops` (`scripts/run.py:359-366`), or change the code first (check 1).
  - Add that `prompt.build` takes a `part`, which the rebase uses to add `skills/maker/rebase.md` to the maker's brief.
  - Add that `wall.baseline` takes `keep` (the hashes the slice changed or deleted) and `skip` (test files the slice added after the baseline) (`scripts/wall.py:61-71`).
- `.xv/picture.md:26` (state is files): add that a rebase moves `base` to the `--onto` commit and moves the named commits by subject. A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json` (`scripts/run.py:342`). After a rebase, a red suite whose failing tests are all in the slice's own red does not stop before the maker has made the suite green (`scripts/run.py:476`).
- `.xv/picture.md` Names, maker line: the rebase brief adds "Do not touch a test file, `.xv/picture.md` or anything under `.xv/` to make a conflict go away" (`skills/maker/rebase.md:7`).

## 5. The wall

No recommendations. I looked at the 7 tests added on this pass (listed above) and the 24 from the first pass. None is marked slice-only (`slice_only: []`). Each checks behaviour that lasts. None restates another: the two guard tests for 16 check the other side of the exception (after the maker, and outside the red). No old wall test is made dead (`xv wall diff`: nothing changed).

## Scenario misses

- 16: the exception covers more than "a test in the slice's own red", in two ways. The code excuses any failing test whose name contains a red file's stem (`scripts/run.py:424` `return any(f in name or os.path.splitext(os.path.basename(f))[0] in name for f in files)`). (a) Every test in a red file is excused, including old wall tests when the red file existed at the base. The repo already treats such a file as covered "only for the tests the slice added" (`.xv/picture.md:23`, `scripts/wall.py:185`). (b) It is a plain substring match, not the shared whole-name matcher `xvlib.names_test` (`.xv/picture.md:23`). So a red file `tests/test_run.py` (stem `test_run`) excuses a failure named `test_run_loop_x (test_other.T.test_run_loop_x)`. In both cases the new base breaks a test the slice did not write, the rebase exits 0, and `suite` is not updated (`scripts/run.py:476`). The red uses only a new one-test red file, `tests/test_own_red.py` (evidence: `scripts/run.py:424`, `scripts/run.py:476`, `own_red()` in `tests/test_slice_rebase.py`; to: scenario)
- 6: a test file that both the slice and the new base changed is hashed again, so the slice's change to it leaves the wall. `scripts/run.py:467-468` `theirs = … diff --name-only old_base onto` … `mine = set(… log --name-only onto..HEAD) - theirs` takes those files out of `keep`, so `wall.baseline` hashes their merged content. Failure: the slice weakens an assertion in an old wall test, and main edits another line of the same file. Git merges it clean, and `xv wall diff` then shows the file unchanged, so an unrecorded move is not flagged. The same happens to a test-file conflict once the person resolves it and runs `--continue`. Point 6 hashes again only "for test files the slice has not touched". No red test touches one file on both sides and then reads the wall (`test_a_dropped_commit_stops_after_continue_from_a_conflict_stop` uses `tests/test_shared.py` on both sides and does not check the wall). (evidence: the hunk cited; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand, and no data, contract or message is migrated or sent. **Blast radius:** contained. Changes to existing paths are additive and off by default: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gate in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff 66570aa785961973ad109e9db00dfc167a823e9b..79a37bd` (this pass alone: `git diff 5aaa0b6..79a37bd`)
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `xv boundary --base 66570aa785961973ad109e9db00dfc167a823e9b` (as `.xv/slices/2026-11-04-slice-rebase.boundary.md`)

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.

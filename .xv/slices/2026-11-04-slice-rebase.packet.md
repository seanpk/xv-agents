---
slice: 2026-11-04-slice-rebase
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: none
moved_tests: 0
expected_moves: 0
door: two-way
blast_radius: contained
---

# Packet: A slice can be brought up to date with its base: #20

This is the seventh pass, and nothing stops for two people. It is the first pass on point 21. The maker's one-line fix works for the case the red tests: `rebase_stop` now writes the budget saved before the rebase into the record in the tree (`scripts/run.py:379`), so `--continue` checks the last budget. Point 21 is wider than that line, though, and the code still misses it in three places. These go to the scenario:
- `--abort` drops a budget the person set during the stop.
- `--continue` drops the stopped commit's own record change.
- The rebase maker's brief reads the scenario from the old copy of the record that git replays.

Sean also has to decide on the carried check-1 findings and the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base, and `resolve_base` gives the default (points 1 and 15). A conflict in a test file or in `.xv/picture.md` stops for the person (2, 9). `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3). In a fresh context, the maker resolves other conflicts and fixes logical breaks, and it stops on what it cannot fix (11, 12). The record moves `base` and the named commits, and a dropped named commit stops (4, 5). The wall is hashed again (6). A red suite stops, except for the slice's own red before the maker has made the suite green (7, 16). It works on closed slices (10). A stop leaves the rebase in progress, and `--continue` or `--abort` picks it up again (14). Every file the maker changed is staged, and an edit to a test file or the picture stops (17). Stops go through `record.apply_verdict` (18). `budget_before` runs before the rebase maker (19). `--abort` keeps the maker's spend (20). **21 (new):** during the rebase, the record that counts is the one saved before it began. Every change goes to that record, and "No field is read from a copy of the record that git replays."

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). Replay: `cd tests && python3 -m unittest test_slice_rebase`. The red command in the record, `python3 -m unittest tests.test_slice_rebase`, fails from the repo root with `ModuleNotFoundError: No module named 'helpers'` (`tests/test_slice_rebase.py:8`). It runs only from `tests/` or through `tests/run.py`.

## The boundary picture

Taken as given from `.xv/slices/2026-11-04-slice-rebase.boundary.md` (base `f6d6dcae847e`):
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Modules, edges, outbound calls, tables and surface paths: none added or removed.
- Shape hints: none.

This pass (`git diff 005fbe5..HEAD`) changes 1 line of `scripts/run.py` and adds 2 tests and 1 helper to `tests/test_slice_rebase.py`.

## What the suite asserts after

The 51 tests from earlier passes are unchanged. This pass adds 2 (`tests/test_slice_rebase.py:741-774`):
- A conflicting commit holds a budget of $1 and spend of $2, and the last commit holds $10. After the stop and `--continue`, the run exits 0, the maker runs, the record's budget is 10, and there is no `budget_spent` stop.
- The reverse: the conflicting commit holds $10 and the last commit holds $1. `--continue` stops with `budget_spent`, the maker does not run, and the budget stays 1.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider. The boundary picture adds no module, edge, table or outbound call. This pass adds one assignment (`scripts/run.py:379`), which does not change the shape.

For Sean, not misses:
- **New.** The `--continue` path reads the budget from the tree's record every time (`scripts/run.py:577-580`). That is right only when `rebase_stop` wrote that record last. If the rebase exits with an error instead, the tree's record is still git's replayed copy: `scripts/run.py:459-460` `raise XVError(f"git rebase --continue failed: …")` writes no stop. The next `--continue` then takes that copy's budget, and finish writes it back (`scripts/run.py:506-507`). This is the pass-six miss on 19 again, through a narrower door. The `except Exception: pass` there is also against decision 12 (`.xv/picture.md:75`).
- **Carried from passes four to six, code unchanged** (`scripts/run.py:433-486`):
  - The "conflict markers remain" check cannot fire. `git add -A` (`scripts/run.py:451`) runs before `unmerged` (`scripts/run.py:455`).
  - On a replay with no conflict, the maker's edits are committed unchecked (`scripts/run.py:482-486`), including a test file or `.xv/picture.md`. Compare `.xv/picture.md:36`.
  - When point 17 fires, the `rebase_conflict` question calls the maker's edit a "conflict" (`scripts/orders.py:171-174`).
- Decision 1 (`.xv/picture.md:64`) is met (`CHANGELOG.md:7`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). This slice is consistent with it: the maker resolves code, and test files and the picture go to a person (`skills/maker/rebase.md:7`, `scripts/run.py:433-454`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- The record has no moves and no expected moves (`.xv/slices/2026-11-04-slice-rebase.md:15` `moved_tests: []`).
- `xv wall diff 2026-11-04-slice-rebase` against the baseline `005fbe5` (`.xv/slices/2026-11-04-slice-rebase.wall.json`) shows `changed`, `deleted`, `added` and `fewer_assertions` all empty.
- On this pass `tests/test_slice_rebase.py` only gains tests (`git diff 005fbe5..HEAD -- tests/`).
- There are no may-not edits to list (`may_not_files: []`, `.xv/slices/2026-11-04-slice-rebase.md:30`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. They carry pass six's edits forward, updated:
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:168-186`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:385`).
  - `orders.budget_before` checks before each rebase maker run, using the spend and budget saved when the rebase began, plus the rebase's own runs (`scripts/run.py:401-406`).
  - `prompt.build` takes a `part` (`scripts/prompt.py:200`).
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes at a ref (`scripts/wall.py:63`, `scripts/wall.py:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase in progress keeps the record it started from in the git dir as `xv-rebase-<id>.json` (`scripts/run.py:593-597`).
  - At a stop, that file's stops and budget are written over the replayed copy in the tree (`scripts/run.py:378-379`).
  - On finish they go into the record. On abort, only the maker's spend and the answered stops are written (`scripts/run.py:501-507`, `563-570`).
  - The named commits move by subject (`scripts/run.py:489-511`).
  - The wall keeps the old hash for a test file only the slice touched (`scripts/run.py:523-532`).
  - The slice's own red does not stop before the maker is green (`scripts/run.py:533-543`).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (check 1).

## 5. The wall

No recommendations. I looked at the 2 tests added on this pass (`tests/test_slice_rebase.py:743-770`). Neither is marked slice-only (`slice_only: []`). Both check lasting behaviour of 21, and each guards one direction of the same rule: a later larger budget must not stop, and a later smaller budget must stop. So neither restates the other. `xv wall diff` is empty, so no old wall test is made dead.

## Scenario misses

- 21: `--abort` loses a budget set with `xv record set` during the stop. Point 21 lists "a budget set with `xv record set`" among the changes applied to the saved record, and says "When the rebase finishes, or is aborted, that record is written into the tree". `xv record set` saves to the tree's record without a commit (`scripts/record.py:169`). `--abort` then runs `git rebase --abort` or `git reset --hard`, which throws that edit away (`scripts/run.py:559-562`). After that it writes back only `spend` and `stops`, never the budget (`scripts/run.py:567-570`). So a person who raises the budget at a `budget_spent` stop and then aborts loses the raise. No red test sets a budget and then aborts (`tests/test_slice_rebase.py:346`, `:673`, `:713`, `:726`). (evidence: `scripts/run.py:556-572`, `scripts/record.py:169`; to: scenario)
- 14: `--continue` drops the stopped commit's own change to the record, so the rebase that `--continue` should finish can stop again on a conflict that xv made itself. `scripts/run.py:582-583` runs `git checkout HEAD -- <record>` while git is stopped on commit k. HEAD is then the replayed commit k-1, so k is committed with k-1's record. On this slice, the first red commit `b2674dd` changes both `tests/test_slice_rebase.py` and the record, so a test-file conflict there hits this. The next commit that changes the record is replayed on the wrong parent. Every step rewrites the one-line `spend:` and appends to `## Log`, so I expect a git conflict in the record. The maker may not touch `.xv/` (`skills/maker/rebase.md:7`), and `scripts/run.py:450` leaves the record unstaged, so that conflict ends in `rebase_stuck`. I did not run this; my allowed commands do not include it. The lost change to the record follows from `checkout HEAD --` alone. The conflicting commits in the red change only the test file (`tests/test_slice_rebase.py:56-60`, `:772-774`). This also goes against point 21's rule that the saved record takes each change. (evidence: `scripts/run.py:582-583`, `git show --stat b2674dd`; to: scenario)
- 21: the rebase maker's brief reads git's replayed copy of the record, though point 21 says "No field is read from a copy of the record that git replays". `rebase_maker` builds the brief with `promptlib.build("maker", slice_id, root=root, …)` (`scripts/run.py:413`). That reads the scenario, the red and the answers from the tree's record (`scripts/prompt.py:205-207`, `:229` `answer_section(data, body)`). At a conflict in commit k, that is k's copy. `b2674dd`'s copy has none of points 14 to 21 (`git grep -E '^(1[4-9]|2[01])\. ' b2674dd -- .xv/slices/2026-11-04-slice-rebase.md` finds nothing), so a maker resolving a conflict there works to an older scenario. The rest of `rebase_maker`'s `data` (`scripts/run.py:401`) and the verdict input in `rebase_stop` (`scripts/run.py:377-383`) come from the same copy; only `stops`, `spend` and `budget` are replaced. No red test reads the maker's prompt during a replayed conflict. (evidence: `scripts/run.py:401`, `scripts/run.py:413`, `scripts/prompt.py:205-207`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand. Nothing is migrated, published or sent. **Blast radius:** contained. Existing paths change only in additive, off-by-default ways: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff f6d6dcae847edb89ef341924ea198b3e735a0f92..HEAD`. This pass alone: `git diff 005fbe5..HEAD`.
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md` (`xv boundary` from `f6d6dcae847e`)
- Runs, by the guardian on this pass: `python3 tests/run.py --jobs 4` gave `Ran 789 tests in shard 1/1 OK`, exit 0. It includes `tests/test_slice_rebase.py`. The record's red command, run from the repo root, gives `ImportError: Failed to import test module: test_slice_rebase` (`ModuleNotFoundError: No module named 'helpers'`).

## From the cleaner

- Shape proposal, for people, carried: the wall-rehash block of `rebase_finish` (`scripts/run.py:523-532`) could become its own function, perhaps in `wall.py`. That is a new seam, so it is left to people.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: rebase_finish in scripts/run.py is long; its wall-rehash block could become a function in wall.py, but that is a new seam, so it is left for the packet
- Shape proposal, for people: scripts/run.py rebase_finish is long (record move, wall rehash, suite check); it could split into three functions along those seams. Left alone as a restructure for a person to weigh.

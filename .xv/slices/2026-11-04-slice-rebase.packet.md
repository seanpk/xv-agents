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

This is the sixth pass, and nothing stops for two people. The fix for pass five's miss on **14** works: `--abort` drops the unanswered rebase stops. The fix for pass five's miss on **19** brings back the old-copy problem from pass four, this time for the budget. At a conflict stop, `--continue` reads the budget from the copy of the record that git replays in the tree. That copy can predate a raise. The check then uses the older, lower budget, and the finished record keeps it, which undoes the person's raise. This is the third pass with a miss on 19, so it goes to the scenario. Sean also has these to decide: the check-1 findings carried from earlier passes, and the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base, and `resolve_base` gives the default (1, 15). A test-file or `.xv/picture.md` conflict stops for the person (2, 9). `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3). The maker resolves other conflicts and fixes logical breaks in a fresh context, and stops on what it cannot fix (11, 12). The record moves `base` and the named commits, and a dropped named commit stops (4, 5). The wall is hashed again (6). A red suite stops, except for the slice's own red before the maker has made the suite green (7, 16). It works on closed slices (10). A stop leaves the rebase in progress, and `--continue` and `--abort` pick it up again (14). The maker's changed files are all staged, and a test-file or picture edit stops (17). Stops go through `record.apply_verdict` (18). `orders.budget_before` runs before the rebase maker, "as before every other step" (19). `--abort` keeps the maker's spend (20).

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). Replay: `cd tests && python3 -m unittest test_slice_rebase`. The guardian's runs are under Raw data. Before the maker, the 2 new tests for 19 and 14 failed with the record's `red.failure`: `AssertionError: 10 != 0` and `rebase_conflict stop still on the record after --abort`.

## The boundary picture

Taken as given from `.xv/slices/2026-11-04-slice-rebase.boundary.md` (base `f6d6dcae847e`):
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Modules, edges, outbound calls, tables and surface paths: none added or removed.
- Shape hints: none.

This pass (`git diff b1ecd24..HEAD`) changes only `scripts/run.py` and `tests/test_slice_rebase.py`. Commit `b1ecd24` moved the slice onto main and changed only the record and `wall.json`.

## What the suite asserts after

The 48 tests from earlier passes are unchanged. This pass adds 3 (`tests/test_slice_rebase.py:692-739`):
- 19: there is a budget stop on a conflict replay. The person raises the budget with `xv record set`, answers, resolves and runs `--continue`. The run exits 0, the maker runs, the record's budget is the raised one, and the record holds one `budget_spent` stop.
- 14: a test-file conflict stops, then `--abort`. The record's stops and status are as they were before the rebase. A second test does the same after a maker run and also checks that the maker's spend row is kept.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider.
- The boundary picture adds no module, edge, table or outbound call. This pass adds one helper, `without_open_rebase_stops` (`scripts/run.py:371-372`), which the cleaner pulled out of two copies. It also adds one read of the tree's record on `--continue` (`scripts/run.py:576-579`). Neither changes the shape.
- New on this pass, for Sean: the read at `scripts/run.py:576-579` swallows every error (`except Exception: pass`), as `tree_stops` does (`scripts/run.py:365-368`). Compare decision 12, "A check whose input is broken or that cannot run stops for a person; it never passes" (`.xv/picture.md:75`). A later `record.load` would probably still raise, so I list this as a finding and not as a miss.
Carried from passes four and five, unchanged in code, for Sean:

  - The "conflict markers remain" check cannot fire. `git add -A` (`scripts/run.py:450`) runs before `unmerged` (`scripts/run.py:454`), and `git add` marks a path resolved whatever it contains.
  - On a replay with no conflict, the maker's edits are committed unchecked (`scripts/run.py:482-485`). That includes a test file or `.xv/picture.md`, and this run of the maker skips `run.post_step`. Compare `.xv/picture.md:36`.
  - When point 17 fires, the `rebase_conflict` question calls the maker's staged edit a "conflict" (`scripts/orders.py:172-174`).
- Decision 1 (`.xv/picture.md:64`) is met. The CHANGELOG line is there (`CHANGELOG.md:7`), and it ends "Decided by Sean, solo", which fits `.xv/picture.md:56`.

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). This slice is consistent with it: the maker resolves code, and test files and the picture go to a person (`skills/maker/rebase.md:7`, `scripts/run.py:441-453`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- The record has no moves and no expected moves (`.xv/slices/2026-11-04-slice-rebase.md:15` `moved_tests: []`).
- `xv wall diff 2026-11-04-slice-rebase` against the baseline (`.xv/slices/2026-11-04-slice-rebase.md:14`, `b1ecd24`) shows `changed`, `deleted`, `added` and `fewer_assertions` all empty.
- `tests/test_slice_rebase.py` only gains tests on this pass (`tests/test_slice_rebase.py:692-739`, from `git show cd13408 -- tests/`).
- There are no may-not edits to list (`.xv/slices/2026-11-04-slice-rebase.md:30` `may_not_files: []`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. This list carries pass five's forward, with changes from this pass:
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:168-186`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:384`).
  - Before each rebase maker run, `orders.budget_before` checks the spend from when the rebase started plus the rebase's own runs. It checks against the budget from the start, or the one read again on `--continue` (`scripts/run.py:400-405`, `576-579`).
  - `prompt.build` takes a `part` (`scripts/prompt.py:200`).
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes at a ref (`scripts/wall.py:63`, `scripts/wall.py:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`: stops and answers, the spend and budget, and the maker's runs (`scripts/run.py:592-595`).
  - When the rebase finishes, these notes go into the record. When it is aborted, only the maker's spend and the answered stops are written, and unanswered rebase stops are dropped (`scripts/run.py:500-506`, `563-569`).
  - The named commits move by subject (`scripts/run.py:488-510`).
  - The wall keeps the old hash for a test file that only the slice touched, and hashes a file both sides touched at `--onto` (`scripts/run.py:523-531`).
  - Before the maker has made the suite green, a red suite does not stop when its failures are all tests the slice added to its red (`scripts/run.py:532-542`).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (check 1).

## 5. The wall

No recommendations. I looked at the 3 tests added on this pass (`tests/test_slice_rebase.py:692-739`). None is marked slice-only (`slice_only: []`). Each one checks lasting behaviour of 19 or 14. The two `--abort` tests take different branches: with no maker run the record is not written, and after a maker run it is (`scripts/run.py:564`). So neither restates the other. `xv wall diff` is empty, so no old wall test is made dead.

## Scenario misses

- 19: on `--continue` after a conflict stop, the budget check reads the budget from an old copy of the record, and the finished record keeps that old budget. `rebase_stop` writes only `stops` into the tree's record (`scripts/run.py:378`), and the rest of it is the replayed commit's copy. `--continue` reads the budget from it (`scripts/run.py:577`), the check uses it (`scripts/run.py:401-403`), and finish writes it back (`scripts/run.py:505-506`). On this slice, commit `d4b69ea` carries `"usd": 7.9` and HEAD carries `"usd": 17`. So a person-stop there, answered with `--continue` and no budget change, would stop with `budget_spent` against $7.90. Pushed through, it would put 7.9 back on the record, and every later `xv step` would check against that (`scripts/run.py:653`). Point 19 says "as before every other step", and the other steps read the record's current budget. The red sets the budget only before the slice's commits (`tests/test_slice_rebase.py:36-38`) or during the stop (`tests/test_slice_rebase.py:700`). This is the third pass in a row with a miss on 19. (evidence: `scripts/run.py:576-579`, `scripts/run.py:505-506`, `git grep '^budget:' d4b69ea HEAD -- .xv/slices/2026-11-04-slice-rebase.md`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand. Nothing is migrated, published or sent. **Blast radius:** contained. The changes to existing paths are additive and off by default: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff f6d6dcae847edb89ef341924ea198b3e735a0f92..HEAD`. This pass alone: `git diff b1ecd24..HEAD`.
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md` (`xv boundary` from `f6d6dcae847e`)
- Runs, by the guardian on this pass: `cd tests && python3 -m unittest test_slice_rebase` gave `Ran 51 tests in 99.427s OK`. `python3 tests/run.py --jobs 4` gave `Ran 787 tests in shard 1/1 OK`, exit 0.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: rebase_finish in scripts/run.py is long; its wall-rehash block could become a function in wall.py, but that is a new seam, so it is left for the packet

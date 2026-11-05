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

This is the eighth pass, and nothing stops for two people. All three misses from pass seven are fixed, and each fix has a red test:
- `--abort` keeps a budget set during the stop (`scripts/run.py:566-581`).
- `--continue` keeps the stopped commit's change to the record (`scripts/run.py:595`).
- The rebase maker's brief reads the record from before the rebase (`scripts/run.py:419-420`).

One miss is left on point 21, and it goes to the scenario. The brief reads the record as it was at `orig_head`, so it leaves out the answers a person gave during the rebase. Sean also needs to decide on the check-1 findings and the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base. With no `--onto`, `resolve_base` picks the base (points 1, 15).
- A conflict in a test file or in `.xv/picture.md` stops for the person (2, 9).
- `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3).
- The maker resolves other conflicts and fixes logical breaks, in a fresh context. It stops on what it cannot fix (11, 12).
- The record moves `base` and the named commits. A dropped named commit stops (4, 5).
- The wall is hashed again (6).
- A red suite stops, except for the slice's own red before the maker is green (7, 16).
- It works on closed slices (10).
- After a stop the rebase stays in progress, and `--continue` or `--abort` picks it up (14).
- Every file the maker changed is staged. An edit to a test file or the picture stops (17).
- Stops go through `record.apply_verdict` (18).
- `budget_before` runs before the rebase maker (19).
- `--abort` keeps the maker's spend (20).
- Point 21: during a rebase, the record that counts is the one saved before it began. Stops, answers, spend, a budget set with `xv record set`, and the moved commits all apply to it. "No field is read from a copy of the record that git replays."

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). Replay with `cd tests && python3 -m unittest test_slice_rebase`. I ran it: `Ran 56 tests … OK`. The record's red command, `python3 -m unittest tests.test_slice_rebase`, still fails from the repo root (`Ran 1 test … FAILED (errors=1)`, the `helpers` import at `tests/test_slice_rebase.py:8`).

## The boundary picture

Taken as given from `.xv/slices/2026-11-04-slice-rebase.boundary.md` (base `f6d6dcae847e`):
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

What this pass changes (`git diff 45de369..HEAD`):
- `scripts/run.py`: 22 lines.
- `scripts/prompt.py`: 4 lines. `build` takes `saved=None` (`scripts/prompt.py:200`, `:207`).
- `tests/test_slice_rebase.py`: 3 new tests.
- The cleaner's helper `record_rel` (`scripts/run.py:345-347`). The cleaner reported that it did not commit this; the watch's commit `e0eb998` carries it.

## What the suite asserts after

The 53 tests from earlier passes are unchanged. This pass adds 3 (`tests/test_slice_rebase.py:776-808`):
- **Abort keeps a raised budget.** The budget is spent and a test file conflicts. At the stop, a person sets `{"usd": 10}` with `xv record set`. `--abort` exits 0, no rebase is left in progress, and the record's budget is 10.
- **Continue keeps the stopped commit's record change.** One commit adds the conflicting test file and sets `note: a`, and the next sets `note: b`. After the stop, a hand resolution and `--continue`, the run exits 0, the record's `note` is `b`, and `base` is the new base.
- **The brief reads the last red.** The conflicting commit names no red, and a later commit names `tests.test_late_mark`. The rebase maker runs, and its prompt contains `tests.test_late_mark`.

Whole suite, run by me: `python3 tests/run.py --jobs 4` reports `Ran 792 tests in shard 1/1 OK`.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast expected `wide`, so this is not wider. The boundary picture adds no module, edge, table or outbound call. This pass adds one optional keyword (`scripts/prompt.py:200`) and one helper inside `run.py` (`scripts/run.py:345`). Neither changes the shape.

For Sean, not misses:
- **Carried from pass seven, and now on `--abort` too.** `--continue` (`scripts/run.py:590`) and now `--abort` (`scripts/run.py:567`) both take the budget from the record in the tree. That record holds the saved budget only when `rebase_stop` wrote it last (`scripts/run.py:384`). Two exits leave git's replayed copy of commit k in the tree instead: `raise XVError(f"git rebase --continue failed: …")` (`scripts/run.py:467`) writes no stop, and neither does a maker run that is killed. In both cases `--abort` writes that copy's budget over the record (`scripts/run.py:577-579`), and `--continue` writes it into the state. Point 21 says no field is read from that copy. I keep this with Sean, as in pass seven, because it needs an error exit, not a stop the scenario names.
- **New, not run.** `--continue` now restores the record from the index (`scripts/run.py:595`, `git checkout -- <record>`). The red test stages only the test file (`tests/test_slice_rebase.py:302-304`). The stop's question says only "Resolve it in the slice worktree and run …" (`scripts/orders.py:172-174`). Suppose a person stages with `git add -A` instead. Then the index takes the record that xv wrote at the stop (the stop, the budget, and the `set budget` log line), and commit k is committed with it. A later commit that appends to `## Log` may then conflict in the record. The maker may not stage the record (`scripts/run.py:457`), so that conflict ends in `rebase_stuck`. I could not run this, because my allowed commands do not include it.
- **Carried from passes four to seven, code unchanged** (`scripts/run.py:449-493`):
  - Staging comes before the check: `git add -A -- <edited>` (`scripts/run.py:458`) runs before `left = unmerged(root)` (`scripts/run.py:462`). So "conflict markers remain" can fire only for the record, which is left unstaged.
  - On a replay with no conflict, the maker's edits are committed without a check (`scripts/run.py:489-493`). That includes a test file or `.xv/picture.md`. Compare `.xv/picture.md:36`.
  - When point 17 fires, the `rebase_conflict` question calls the maker's edit a "conflict" (`scripts/orders.py:172-174`).
- Decision 1 (`.xv/picture.md:64`) is met (`CHANGELOG.md:7`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). This slice fits it: the maker resolves code, and test files and the picture go to a person (`skills/maker/rebase.md:7`, `scripts/run.py:449-460`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- No old wall test moved. `xv wall diff 2026-11-04-slice-rebase` against baseline `30a723e` shows `changed`, `deleted`, `added` and `fewer_assertions` all empty, and the record has `moved_tests: []` (`.xv/slices/2026-11-04-slice-rebase.md:15`).
- One assertion in the slice's own new red was amended in `9bf0820` (`tests/test_slice_rebase.py:798`). Before, it was `assertIn('note: "b"', <raw record text>)`; after, it is `assertEqual(self.record()["note"], "b")`. It now checks the parsed value, not how the value is written. Sean chose this at the `maker_stopped` stop (record log, 08:47:15). It is not an old test, and the behaviour it checks is the same.
- There are no may-not edits to list (`.xv/slices/2026-11-04-slice-rebase.md:30` `may_not_files: []`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. They carry pass seven's edits forward, with line numbers updated:
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:168-186`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:390`).
  - `orders.budget_before` checks before each rebase maker run (`scripts/run.py:409`).
  - `prompt.build` takes a `part` and a `saved` record text (`scripts/prompt.py:200`).
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes at a ref (`scripts/wall.py:63`, `:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`. These are the stops, spend, budget and named commits from before it began (`scripts/run.py:605-607`).
  - The rebase maker's brief is built from the record at the slice's old head (`scripts/run.py:419`).
  - At a stop, the saved stops and budget are written over the copy in the tree (`scripts/run.py:383-384`).
  - On finish they go into the record. On abort, the spend, the answered stops and a budget set during the stop are written back (`scripts/run.py:509-520`, `:576-581`).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (check 1).

## 5. The wall

No recommendations. I looked at the 3 tests added on this pass (`tests/test_slice_rebase.py:776-808`):
- None is marked slice-only (`slice_only: []`).
- Each guards a different part of point 21 or 14 that should last: the budget on abort, the record change on continue, and the source of the brief.
- `xv wall diff` is empty, so no old wall test is made dead.

## Scenario misses

- 21: the rebase maker's brief leaves out the answers given during the rebase. Point 21 says each change made during the rebase applies to the saved record, "stops, answers, …", and that this is the record that counts. The brief is built from `git show <orig_head>:<record>` (`scripts/run.py:419-420`, `scripts/prompt.py:207`), which is the record before the rebase, with none of the rebase's changes. `answer_section(data, body)` takes the latest answered stop from that copy (`scripts/prompt.py:155-161`). The answers do reach `state["stops"]` through `tree_stops` (`scripts/run.py:589`), but `rebase_maker` never passes them to the brief. So when a person answers a `rebase_stuck` or `budget_spent` stop and runs `--continue`, the next rebase maker run gets no "The person's answer" section. It may also get a stale answer from before the rebase, if no report came after it (`scripts/prompt.py:165-171`). No red test answers a stop during a rebase and then reads the maker's prompt; the brief test sets only `red` (`tests/test_slice_rebase.py:801-808`). (evidence: `scripts/run.py:419-420`, `scripts/prompt.py:155-161`, `scripts/prompt.py:207`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand. Nothing is migrated, published or sent. **Blast radius:** contained. Existing paths change only in additive, off-by-default ways: `prompt.build(part=None, saved=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff f6d6dcae847edb89ef341924ea198b3e735a0f92..HEAD`. This pass alone: `git diff 45de369..HEAD`.
- Wall: `xv wall diff 2026-11-04-slice-rebase` (baseline `30a723e`, all lists empty)
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md`
- Runs on this pass, by the guardian:
  - `python3 tests/run.py --jobs 4`: `Ran 792 tests in shard 1/1 OK`.
  - `cd tests && python3 -m unittest test_slice_rebase`: `Ran 56 tests … OK`.
  - `python3 -m unittest tests.test_slice_rebase` from the root: `FAILED (errors=1)`.

## From the cleaner

- Shape proposal, for people, carried: `rebase_finish` (`scripts/run.py:487-556`) is long. It could split along its seams: moving the record, hashing the wall (`:530-539`, perhaps into `wall.py`), and checking the suite. A new function boundary is a shape decision, so it is left to people.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: rebase_finish in scripts/run.py is long; its wall-rehash block could become a function in wall.py, but that is a new seam, so it is left for the packet
- Shape proposal, for people: scripts/run.py rebase_finish is long (record move, wall rehash, suite check); it could split into three functions along those seams. Left alone as a restructure for a person to weigh.

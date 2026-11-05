---
slice: 2026-11-04-slice-rebase
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: none
moved_tests: 0
expected_moves: 0
door: two-way
blast_radius: contained
---

# Packet: A slice can be brought up to date with its base: #20

This is the ninth pass. The code has not changed since pass eight. `git diff HEAD` shows only the record, where Sean added point 22. Point 22 takes the last pass-eight miss out of the slice: the brief reads the record from before the rebase (`scripts/run.py:419-420`). Nothing stops for two people, and I found no scenario miss. Sean (originator) decides three things:
- The error-exit gap on point 21. It is wider than pass eight said: stops are lost, as well as the budget.
- One new record gap: the stop and answer log lines are lost on `--continue`.
- The picture edits in check 4.

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base. With no `--onto`, `resolve_base` picks the base (points 1, 15).
- A conflict in a test file or in `.xv/picture.md` stops for the person (2, 9).
- `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3).
- The maker resolves other conflicts and fixes logical breaks, in a fresh context, and stops on what it cannot fix (11, 12, 17).
- The record moves `base` and the named commits. A dropped named commit stops (4, 5).
- The wall is hashed again (6).
- A red suite stops, except for the slice's own red before the maker is green (7, 16).
- The rebase works on closed slices (10).
- After a stop the rebase stays in progress, and `--continue` or `--abort` picks it up (14).
- Stops go through `apply_verdict` (18), and `budget_before` runs before the rebase maker (19). The maker's spend is kept on `--abort` (20).
- During a rebase, the record saved before it began is the one that counts (21). The brief may read the record from when the rebase began; answers given during the rebase are #138 (22).

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). To replay, run `cd tests && python3 -m unittest test_slice_rebase`. I ran it: `Ran 56 tests … OK`.

## The boundary picture

Taken as given from `.xv/slices/2026-11-04-slice-rebase.boundary.md` (base `f6d6dcae847e`):
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- No modules, edges, outbound calls, tables or surface paths are added or removed.
- Shape hints: none.

## What the suite asserts after

`tests/test_slice_rebase.py` holds 56 new tests, unchanged since pass eight. They cover:
- The default base and `--onto`.
- Test-file and picture conflicts stopping.
- CHANGELOG keeping both sides.
- The maker resolving conflicts and making logical fixes, and staging what it edits.
- The record's `base` and named commits moving, and a dropped commit stopping once.
- The wall rehash keeping the slice's own changes.
- The own-red exception, by whole test name.
- Closed slices.
- `--continue` and `--abort` and their refusals.
- Stops going through `apply_verdict`.
- `budget_before` with the saved budget, and a budget raised mid-rebase.
- Spend and answered stops kept on `--abort`.
- The stopped commit's record change kept on `--continue`.
- The brief reading the saved record.

`tests/fake_agent.py` gains a `FAKE_REBASE_MODE` stand-in maker and a prompt log. No old assertion moved. Whole suite, run by me: `python3 tests/run.py --jobs 4`, `Ran 792 tests in shard 1/1 OK`.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider. The boundary picture adds no module, edge, table or outbound call. The new functions sit inside `run.py`:
- `scripts/run.py:301-614`
- `wall.hashes_at` and the optional `keep`/`skip` on `baseline` (`scripts/wall.py:63-85`)
- the optional `part`/`saved` on `prompt.build` (`scripts/prompt.py:200`)

All of these stay inside the shape at `.xv/picture.md:21-23`.

For Sean, not misses:
- **Error exits read the replayed record (point 21), wider than pass eight said** (`scripts/run.py:588-590`). Pass eight named only the budget. The stops are lost as well. Two exits leave git's replayed copy of the record in the tree with no stop written:
  - `raise XVError(f"git rebase --continue failed: …")` (`scripts/run.py:466-467`), for example when a commit hook fails.
  - `agentcli.run` raising `agent CLI not found` (`scripts/agentcli.py:82`) from inside `rebase_maker` (`scripts/run.py:425`).

  After either one, `--continue` reads the stops and budget from that copy (`scripts/run.py:588`, `:590`). `rebase_finish` then writes those stops into the finished record (`scripts/run.py:509-512`). So every stop recorded after the commit being replayed is dropped, and an older budget is written. `--abort` takes its budget the same way (`scripts/run.py:567`, `:579`).

  Read strictly, point 21 covers this: "No field is read from a copy of the record that git replays." I do not mark it a miss for two reasons. Point 14 defines `--continue` at a stop, and this path starts from an error exit (exit 2, `.xv/picture.md:74`), not a stop. And passes seven and eight put it to Sean as not a miss. Sean may call it one. I could not run this path, because my allowed commands do not include `xv slice rebase`.
- **New: on `--continue`, the record's log loses the stop and the answer.** At a stop mid-rebase, `apply_verdict` writes `watch: stop (rebase_…)` into the tree's record without a commit (`scripts/record.py:619`, `scripts/run.py:390-396`). The person's `answered …` and `set budget` lines are written there too. `--continue` then runs `git checkout -- <record>` (`scripts/run.py:595`), and `rebase_finish` adds only `rebased onto …` (`scripts/run.py:527`). The stops and answers survive in the front matter through `tree_stops` (`scripts/run.py:588`), so point 21's list holds. Only the log's account of the stop is gone. `--abort` loses the same lines through `git rebase --abort` (`scripts/run.py:571`). No test reads the log after `--continue`.
- **Carried from pass eight, code unchanged** (`scripts/run.py:449-493`):
  - Suppose a person stages the record with `git add -A` before `--continue`. Then the record xv wrote at the stop is committed into commit k (`scripts/run.py:595` restores only from the index).
  - On a replay with no conflict, the maker's edits are committed without the test-file or picture check that point 17 gives the conflict path (`scripts/run.py:489-493` against `:459-461`). Compare `.xv/picture.md:36`.
  - "Conflict markers remain" can fire only for the record, because `git add -A` runs before `unmerged` (`scripts/run.py:458`, `:462`).
  - When point 17 fires, the `rebase_conflict` question calls the maker's edit a "conflict" (`scripts/orders.py:171-173`).
- **Binding decisions I checked** (`.xv/picture.md:61-79`):
  - Decision 1 (`.xv/picture.md:64`) is met by `CHANGELOG.md:7`.
  - Decision 10 (`.xv/picture.md:73`) is met: the four rebase orders live in `scripts/orders.py:168-186`, and `budget_spent` comes from `orders.budget_before` (`scripts/run.py:409`).
  - Decision 11 (`.xv/picture.md:74`) is met: a stop exits through `EXIT_STOP` (`scripts/run.py:401`).
  - Decision 3 (`.xv/picture.md:66`) is met: only the standard library is imported (`scripts/wall.py:20-25`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). The slice fits it:
- The maker resolves code (`skills/maker/rebase.md:5-6`).
- Test files and the picture go to a person (`skills/maker/rebase.md:7`, `scripts/run.py:449-461`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- No old wall test moved. `xv wall diff 2026-11-04-slice-rebase` against baseline `30a723e` returns empty lists for `changed`, `deleted`, `added` and `fewer_assertions`. The record has `moved_tests: []`.
- One assertion in the slice's own new red was amended at Sean's `maker_stopped` answer (record log, 08:47:15). Before, it was `assertIn('note: "b"', …)`; after, it is `assertEqual(self.record()["note"], "b")` (`tests/test_slice_rebase.py:798`). This is not an old test, and it checks the same behaviour.
- There are no may-not file edits to list (`.xv/slices/2026-11-04-slice-rebase.md:30` `may_not_files: []`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them.
- `.xv/picture.md:22`: `slice` in `run.py` also runs `xv slice rebase` (`--onto`, `--continue`, `--abort`).
- `.xv/picture.md:23`:
  - `orders` decides `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` after `rebase` (`scripts/orders.py:168-186`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:390`).
  - `orders.budget_before` checks before each rebase maker run (`scripts/run.py:409`).
  - `prompt.build` takes `part` and `saved` (`scripts/prompt.py:200`).
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes files at a ref (`scripts/wall.py:63`, `:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`: the stops, spend, budget and named commits from before it began (`scripts/run.py:605-607`).
  - At a stop, the saved stops and budget are written over the tree's copy (`scripts/run.py:383-384`).
  - On finish they go into the record. On abort, spend, answered stops and a budget set during the stop are written back (`scripts/run.py:509-520`, `:575-582`).
  - The rebase maker's brief reads the record at the old head (`scripts/run.py:419`; #138 for answers given during the rebase).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (check 1).

## 5. The wall

No recommendations. I looked at:
- The 56 new tests in `tests/test_slice_rebase.py`. None is marked slice-only (`slice_only: []`), and each guards a numbered point that should last.
- The `tests/fake_agent.py` additions, which are a stand-in agent, not tests.
- `xv wall diff`, which is empty, so no old wall test is made dead.

## Door

**Door:** two-way. A revert removes the subcommand, the four orders and the brief part. Nothing is migrated, published or sent. **Blast radius:** contained. Existing callers see only off-by-default parameters: `prompt.build(part=None, saved=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gate in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff f6d6dcae847edb89ef341924ea198b3e735a0f92..HEAD`. Since pass eight: `git diff HEAD` (the record only).
- Wall: `xv wall diff 2026-11-04-slice-rebase` (baseline `30a723e`, all lists empty)
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md`
- Runs on this pass, by the guardian:
  - `python3 tests/run.py --jobs 4`: 792 OK.
  - `cd tests && python3 -m unittest test_slice_rebase`: 56 OK.

## From the cleaner

- Shape proposal, for people, carried from passes four to eight: `rebase_finish` (`scripts/run.py:487-555`) is long. It could split along its seams: moving the record (`:496-529`), hashing the wall (`:530-539`, perhaps into `wall.py`), and checking the suite (`:540-552`). A new function boundary is a shape decision, so it is left to people.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: rebase_finish in scripts/run.py is long; its wall-rehash block could become a function in wall.py, but that is a new seam, so it is left for the packet
- Shape proposal, for people: scripts/run.py rebase_finish is long (record move, wall rehash, suite check); it could split into three functions along those seams. Left alone as a restructure for a person to weigh.

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

This is the fourth pass. Nothing stops for two people. Point 17, the third pass's miss on 11, is closed: every file the maker edited is staged, and edits to a test file or the picture stop. Point 20 holds. Points **18** and **19** are met only when git has finished replaying the commits. While a conflict stops git partway, the slice record in the worktree is an old copy, taken from the commit being replayed. So the budget check reads old spend and an old budget (19). The stop and any answer the person writes are also erased by `--continue` (18). Both are misses, sent to the scenario. Sean also decides three findings in check 1 that are not misses, and accepts the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base. The default base comes from `resolve_base` (15). A conflict in a test file or `.xv/picture.md` stops for the person (2, 9). `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3). The maker resolves other conflicts in a fresh context, with a rebase part in its brief. It fixes logical breaks and stops on what it cannot fix (11, 12). The record moves `base` and the named commits, and a dropped named commit stops (4, 5). The wall is hashed again (6). The suite runs, and a red suite stops, except for the slice's own red before the maker (7, 16). It works on closed slices (10). A stop leaves the rebase in progress, with `--continue` and `--abort` (14). Amended points 17–20:
- 17: every file the maker changed is staged, and an edit to a test file or the picture stops with `rebase_conflict`.
- 18: a stop is written through `record.apply_verdict`.
- 19: `orders.budget_before` runs before the rebase maker.
- 20: `--abort` keeps the maker's spend.

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None, since this is a feature. Replay: `cd tests && python3 -m unittest test_slice_rebase`. I ran it and got `Ran 44 tests in 91.068s OK`. Before the maker, all 8 tests added on this pass failed (record, scenario report 06:45:34). The cleaner reports the whole suite green. I did not rerun it.

## The boundary picture

Taken from `.xv/slices/2026-11-04-slice-rebase.boundary.md` as given:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Modules, edges, outbound calls, tables and surface paths: none added or removed.
- Shape hints: none.

## What the suite asserts after

The 36 tests from earlier passes are unchanged. This pass adds 8 (`tests/test_slice_rebase.py`, hunk after line 540):
- 17: the maker resolves a conflict and also fixes a second file. The rebase ends at exit 0, the fix is committed, the tree is clean, and `next` is `cleaner`. When the second file is `tests/test_store.py` or `.xv/picture.md`, the rebase stops with `rebase_conflict` and names the file.
- 18: a test-file conflict stop and a `rebase_stuck` stop are in the record's `stops`, unanswered, and `status` is `stopped`.
- 19: a spent budget stops with `budget_spent`, and the stand-in maker never runs. This holds on a clean replay and on a conflict.
- 20: the maker resolves one conflict, then a test-file conflict stops. `--abort` puts HEAD back, and the record's spend gains one `maker` row.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider.
- The boundary picture adds no module, edge, table or outbound call. This pass changes only `scripts/run.py` (`git diff 55f4b9b..HEAD -- scripts/`). The new pieces are the inner `for_a_person` closure and calls to `record.apply_verdict` and `orders.budget_before`, which the picture already names (`.xv/picture.md:23`).
- Three findings for Sean. None of them is a miss (`scripts/run.py:425-466`):
  - **The "conflict markers remain" check can never fire.** `scripts/run.py:431` `git(["add", "-A", "--"] + edited, root)` stages every conflicted file, and `git add` marks a path resolved whatever it contains. So `scripts/run.py:435` `left = unmerged(root)` is always empty. If the maker reports green but leaves markers, they are committed into the replay. Only a red suite would catch them, and only in a file the suite loads. The earlier passes had the same dead check (`git add -A -- files` before `unmerged`). It runs against "Read-only agents are checked, not trusted" (`.xv/picture.md:75`, decision 12).
  - **On a replay with no conflict, the maker's edits are committed unchecked.** `scripts/run.py:464-466` commits whatever the maker changed (`commit` runs `git add -A`, `scripts/run.py:103`), including a test file or `.xv/picture.md`. Point 17 covers only a conflict replay, so this is not a miss. The picture says "the maker may edit `.xv/picture.md` only when the scenario report names it in `may_not_files` … (`run.post_step`)" (`.xv/picture.md:36`), and the rebase path does not go through `post_step`. A test-file edit would still show on the wall: it lands in `mine` and keeps its old hash, so `unrecorded_move` would catch it. A picture edit would show nowhere.
  - **The stop calls a maker's edit a conflict.** When point 17 fires, `orders.py` says "the rebase stopped on a conflict in tests/test_store.py. Resolve it in the slice worktree" (`scripts/orders.py:166-168`). But that file has no conflict: the maker edited it, and `scripts/run.py:431` has already staged the edit. A bare `--continue` commits the edit into the replay. The question does not tell the person to look for, or undo, a staged edit.
- Unchanged since the third packet, and decided by Sean at the stall stop (06:14:43): the edges of the own-red name match (16, `scripts/run.py:515`) and the hash at `--onto` (6, `scripts/run.py:505-509`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). It still holds: the maker resolves code, and test files and the picture go to a person (`skills/maker/rebase.md:7`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

The record has `moved_tests: []`. `xv wall diff 2026-11-04-slice-rebase`, against baseline `b0d1712`, shows `changed`, `deleted`, `added` and `fewer_assertions` all empty. On this pass, `tests/fake_agent.py` only gains a `resolve_and_edit` branch, gated on `FAKE_REBASE_MODE`. `tests/test_slice_rebase.py` only gains tests. `tests/test_red.py` has not changed since the base. `may_not_files: []`, so there are no may-not edits to list.

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. The proposal that the stop is only printed is dropped, since 18 changed the code.
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:162`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:368`).
  - `orders.budget_before` also runs before each rebase maker run (`scripts/run.py:384`).
  - `prompt.build` takes a `part`, which the rebase uses to add `skills/maker/rebase.md`.
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes files as they are at a ref (`scripts/wall.py:63`, `scripts/wall.py:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase moves `base` to the `--onto` commit and moves the named commits by subject (`scripts/run.py:485`).
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`.
  - `--abort` restores the branch, then adds the maker runs' spend to the record, uncommitted (`scripts/run.py` `cmd_slice_rebase`).
  - The wall keeps the old hash for a test file only the slice touched, and hashes a file both sides touched at `--onto` (`scripts/run.py:505`).
  - Before the maker has made the suite green, a red suite whose failures are all tests the slice added to its red does not stop (`scripts/run.py:515`).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (see check 1).

## 5. The wall

No recommendations. I looked at the 8 tests added on this pass. None is marked slice-only (`slice_only: []`). Each one checks lasting behaviour of points 17–20, and none restates another: the two budget tests cover the clean path and the conflict path, and the two record tests cover two different orders. No old wall test is made dead, since `xv wall diff` is empty.

## Scenario misses

- 19: during a conflict replay, the budget check reads an old copy of the record. The slice record is committed in the slice's own commits. When git stops on a conflict in commit k, the worktree's `.xv/slices/<id>.md` is commit k's copy. `rebase_maker` reads that copy (`scripts/run.py:382` `data = record.load(root, slice_id)[1]`) and checks it (`scripts/run.py:384` `spent_out = orders.budget_before({**data, "spend": data["spend"] + unapplied})`). That copy holds the budget and spend from when commit k was made, not the slice's current ones. On this slice, commit `58a3745` (the first `make it work`, which touches `scripts/run.py`) has 4 spend rows totalling $1.72 and budget $7.9. HEAD has 19 rows totalling about $9.12 and budget $14. So a conflict in `scripts/run.py` that replays `58a3745` would check $1.72 against $7.9. A slice whose budget is spent would still start the maker, which point 19 forbids. The `with_caps` limits at `scripts/run.py:394-395` read the same old copy. The red test misses this because `spend_the_budget` commits the spend before the conflicting commit (`set_field` commits, then `shared_conflict`). (evidence: `scripts/run.py:382-384`, `git show 58a3745:.xv/slices/2026-11-04-slice-rebase.md`; to: scenario)
- 18: a stop raised while git is partway through is lost, with any answer. `rebase_stop` writes the stop into the same old copy of the record (`scripts/run.py:359-370`), and leaves it uncommitted while the rebase runs (`scripts/run.py:371`). The person runs `xv record show` and `xv record answer` on that copy, and `record.py` does not commit. Then `--continue` throws the copy away: `scripts/run.py:550` `git(["checkout", "HEAD", "--", … record …])`. Later replays bring in the newer copies of the record, and the finished record has neither the stop nor the answer. This hits `rebase_conflict`, `rebase_stuck` raised in `rebase_drive`, and `budget_spent` raised on a conflict replay. Point 18 asks for these to be recorded "so the person's answer can be recorded with an answer on the record". The red tests read the stop only while it is open. None answers it, runs `--continue`, and then reads the record. (evidence: `scripts/run.py:371`, `scripts/run.py:550`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand. Nothing is migrated, published or sent. **Blast radius:** contained. The changes to existing paths are additive and off by default: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff 73d8704034d14aaac5d68a76dc7dd6aa4f662d2b..HEAD`. This pass alone: `git diff b0d1712..HEAD`.
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md` (`xv boundary` from `73d8704034d1`)

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.

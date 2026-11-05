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

This is the fifth pass. Nothing stops for two people. The fourth pass's two misses are closed. The budget check now reads the spend and budget from before the rebase (19). Stops and answers live in the rebase's state file, so they survive `--continue` (18). Freezing the budget at the start causes a new miss on **19**: raising the budget at a rebase `budget_spent` stop has no effect, so `--continue` stops again every time. A second miss is on **14**: `--abort` now leaves an unanswered rebase stop open in the record, and `xv run`, `xv step` and `close` refuse until someone answers it. Both go to the scenario. Sean also decides the check-1 findings carried from pass four, and accepts the picture edits (check 4).

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice on a new base, and `resolve_base` gives the default (1, 15). A test-file or `.xv/picture.md` conflict stops for the person (2, 9). `CHANGELOG.md` and `.xv/estimation.md` keep both sides (3). The maker resolves other conflicts and fixes logical breaks in a fresh context, and stops on what it cannot fix (11, 12). The record moves `base` and the named commits, and a dropped named commit stops (4, 5). The wall is hashed again (6). A red suite stops, except for the slice's own red before the maker (7, 16). It works on closed slices (10). A stop leaves the rebase in progress, with `--continue` and `--abort` (14). Further points:
- 17: every file the maker changed is staged.
- 18: stops go through `record.apply_verdict`.
- 19: `orders.budget_before` runs before the rebase maker.
- 20: `--abort` keeps the maker's spend.

May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records, and an `--onto` ref whose own suite is red.

## The recording

None (a feature). Replay: `cd tests && python3 -m unittest test_slice_rebase`. I ran it, and the whole suite with `python3 tests/run.py --jobs 4`; results under Raw data. Before the maker, all 4 tests added on this pass failed (record, scenario report 07:06:20).

## The boundary picture

Taken from `.xv/slices/2026-11-04-slice-rebase.boundary.md` as given:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`.
- Modules, edges, outbound calls, tables and surface paths: none added or removed.
- Shape hints: none.

This pass (`git diff a426ff5..HEAD`) changes only `scripts/run.py` and `tests/test_slice_rebase.py`.

## What the suite asserts after

The 44 tests from earlier passes are unchanged. This pass adds 4 (`tests/test_slice_rebase.py:616-670`):
- 19: a budget spent after the conflicting commit still stops with `budget_spent` before the stand-in maker runs.
- 18: the person answers a stop, resolves the conflict, and runs `--continue`. The finished record then holds the stop once, with that answer. This is tested for a test-file `rebase_conflict`, a mid-rebase `rebase_stuck`, and a `budget_spent` stop raised on a conflict replay. That last test checks only the first `budget_spent` stop's answer. It does not check the exit code of `--continue`.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none. The forecast said `wide`, so this is not wider.
- The boundary picture adds no module, edge, table or outbound call. This pass adds one helper, `tree_stops` (`scripts/run.py:359-364`). It also adds four keys to the git-dir state file (`stops`, `first_stops`, `spend`, `budget`, `scripts/run.py:579`), which already holds the rebase's notes.
- New finding for Sean (not a miss): `tree_stops` swallows every error (`scripts/run.py:361-364` `except Exception: return fallback`). If the person's edit leaves the record unreadable, `--continue` and `--abort` quietly drop their answer and use the earlier stops. Decision 12 says such a check stops for a person ("A check whose input is broken or that cannot run stops for a person; it never passes", `.xv/picture.md:75`).
- Carried from pass four, unchanged in code, still for Sean (`scripts/run.py:440-448`, `scripts/run.py:473-479`):
  - The "conflict markers remain" check cannot fire. `git add -A` (`scripts/run.py:442`) runs before `unmerged` (`scripts/run.py:446`), and `git add` marks a path resolved whatever it contains.
  - On a replay with no conflict, the maker's edits are committed unchecked (`scripts/run.py:475-477`), including a test file or `.xv/picture.md`. Compare `.xv/picture.md:36`.
  - When point 17 fires, the `rebase_conflict` question calls the maker's staged edit a "conflict" (`scripts/orders.py:166-168`).
- Decided by Sean at the stall stop (06:14:43): the edges of the own-red name match (16, `scripts/run.py:455-468`) and the hash at `--onto` (6, `scripts/run.py:519-520`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The nearest line is "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). It still holds: the maker resolves code, and test files and the picture go to a person (`skills/maker/rebase.md:7`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

The record has `moved_tests: []`. `xv wall diff 2026-11-04-slice-rebase` against baseline `a426ff5` shows `changed`, `deleted`, `added` and `fewer_assertions` all empty. `tests/test_slice_rebase.py` only gains tests (`git diff a426ff5..HEAD -- tests/`). `may_not_files: []`, so no may-not edits are listed.

Slice-only tests removed: none. Kept: none.

## 4. The picture

These are proposed edits; Sean accepts them. They carry pass four's list forward, changed by this pass:
- `.xv/picture.md:22`: add `xv slice rebase` (with `--onto`, `--continue` and `--abort`) to what `slice` runs in `run.py`.
- `.xv/picture.md:23`:
  - `orders` decides four stops after `rebase`: `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red` (`scripts/orders.py:166-178`).
  - `record.apply_verdict` also writes the stop on `xv slice rebase` (`scripts/run.py:376`).
  - Before each rebase maker run, `orders.budget_before` checks the budget and spend as they were when the rebase started, plus the rebase's own runs (`scripts/run.py:393-395`). "Checks it before every step" is then only partly true.
  - `prompt.build` takes a `part` (`scripts/prompt.py:177`).
  - `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes at a ref (`scripts/wall.py:63`, `scripts/wall.py:73`).
- `.xv/picture.md:27` (state is files):
  - A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`: the stops and answers, the spend and the budget from the start, and the maker runs. It writes them into the record when it finishes or is aborted (`scripts/run.py:493-496`, `scripts/run.py:553-558`).
  - A rebase moves `base` and the named commits by subject (`scripts/run.py:480-500`).
  - The wall keeps the old hash for a test file only the slice touched, and hashes a file both sides touched at `--onto` (`scripts/run.py:515-521`).
  - Before the maker has made the suite green, a red suite whose failures are all tests the slice added to its red does not stop (`scripts/run.py:526-532`).
- `.xv/picture.md:36`: say whether the rebase maker may edit the picture on a replay with no conflict (check 1).

## 5. The wall

No recommendations. I looked at the 4 tests added on this pass (`tests/test_slice_rebase.py:616-670`). None is marked slice-only (`slice_only: []`). Each one checks lasting behaviour of 18 or 19 on a different order or path, and none restates another. No old wall test is made dead, since `xv wall diff` is empty.

## Scenario misses

- 19: a raised budget never reaches the rebase's check, so a rebase `budget_spent` stop cannot be passed with `--continue`. The check reads `state["budget"]` (`scripts/run.py:393-395`), which is set once when the rebase starts (`scripts/run.py:579` `"budget": data.get("budget")`). Nothing updates it afterwards: `--continue` refreshes only the stops (`scripts/run.py:564` `state["stops"] = tree_stops(...)`). Mid-rebase, the record that `xv record set … budget` wrote is also checked out from HEAD before the drive (`scripts/run.py:567`). After a `budget_spent` stop, `maker_ran` is still false. So `--continue` reaches `rebase_finish`, `rebase_maker` runs the same check on the same frozen numbers, and it stops with `budget_spent` again (`scripts/run.py:473-474`, `396-397`). The stop's own question says "Continue with a new budget" (`scripts/orders.py:84-85`). Point 19 says "as before every other step", and every other step reads the record's current budget (`scripts/run.py:638`). Point 14 says `--continue` "finishes the rebase". The only way through is `--abort`, then raise the budget, then rebase again. No red test raises the budget. `test_the_answer_to_a_budget_stop_raised_on_a_conflict_replay_is_on_the_finished_record` (`tests/test_slice_rebase.py:658-669`) never checks the `--continue` exit code, and reads only `stops[0]`. (evidence: `scripts/run.py:393-397`, `scripts/run.py:564-567`, `scripts/run.py:579`; to: scenario)
- 14: `--abort` no longer puts the record back as it was. It leaves the aborted rebase's unanswered stop open. `tree_stops` reads the stop that `rebase_stop` wrote, and when the stops differ from `first_stops`, `--abort` writes them into the record (`scripts/run.py:547`, `scripts/run.py:553-558`). `rebase_finish` drops unanswered rebase stops (`scripts/run.py:493`), but `--abort` keeps them. `status` is left as it was, not `stopped`. Then `xv step` and `xv run` exit 10 with "an earlier stop is unanswered" (`scripts/run.py:633-637`, `scripts/run.py:1033-1036`), and `close` refuses (`scripts/run.py:1050-1052`). Each time the question is about a rebase that no longer exists, and it says to resolve it and run `--continue`. Point 14 says `--abort` "puts the branch and the record back as they were before it started". Point 20 makes an exception only for spend. Point 18 is about answers, and an unanswered stop holds none. The red abort test (`tests/test_slice_rebase.py:673-692`) checks HEAD and spend, not stops. (evidence: `scripts/run.py:553-558`; to: scenario)

## Door

**Door:** two-way. Reverting the commits removes the subcommand. Nothing is migrated, published or sent. **Blast radius:** contained. The changes to existing paths are additive and off by default: `prompt.build(part=None)`, `wall.baseline(keep=None, skip=())`, and the `FAKE_REBASE_MODE` gates in the stand-in agent.

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff 73d8704034d14aaac5d68a76dc7dd6aa4f662d2b..HEAD`. This pass alone: `git diff a426ff5..HEAD`.
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `.xv/slices/2026-11-04-slice-rebase.boundary.md` (`xv boundary` from `73d8704034d1`)
- Runs, by the guardian on this pass: `cd tests && python3 -m unittest test_slice_rebase` gave `Ran 48 tests in 96.390s OK`. `python3 tests/run.py --jobs 4` gave `Ran 736 tests in shard 1/1 OK`, exit 0.

## From the cleaner

- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: Extract the wall rehash block of rebase_finish (scripts/run.py) into a function of its own: it is a clear unit, but a new function boundary is a shape decision, not a cleanup.
- Shape proposal, for people: rebase_finish in scripts/run.py is long; its wall-rehash block could become a function in wall.py, but that is a new seam, so it is left for the packet

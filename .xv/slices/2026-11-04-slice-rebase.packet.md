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

No stop for two people. Five misses send the slice back: four scenario points the red does not reach (16, 5 and 11 on the `--continue` path, 6), and binding decision 1 (no `CHANGELOG.md` line). Sean also decides three findings that are not misses (checks 1 and 4) and accepts the picture edits.

## The scenario

`xv slice rebase <id> [--onto <ref>]` replays the slice branch on a new base (default from `resolve_base`). Conflicts in a test file or `.xv/picture.md` stop for the person. `CHANGELOG.md` and `.xv/estimation.md` keep both sides. Other conflicts, and logical breaks that git does not show, go to the maker in a fresh context with a rebase part in its brief. The record's `base`, `pre_maker_commit` and `cleaner_commit` move, and a dropped named commit stops. The wall is hashed again for test files the slice did not touch. The suite runs again. A red suite stops, except for the slice's own red before the maker (point 16). Closed slices work too: a clean rebase leaves them closed, and a maker fix sends them to the cleaner. A stop leaves the rebase in progress, with `--continue` and `--abort` (point 14).
May ignore: `--merge`, trial repos (#21), prototype variant branches, old slice records.

## The recording

None (a feature). Replay: `cd tests && python3 -m unittest test_slice_rebase`. Before the maker, all 24 failed on `invalid choice: 'rebase'` (record `red`). Now 24 pass: I ran it, `Ran 24 tests in 59.604s OK`. The whole suite is 953 OK per the cleaner's run in the record. I did not rerun it.

## The boundary picture

From `.xv/slices/2026-11-04-slice-rebase.boundary.md`. Touched: `scripts/orders`, `scripts/prompt`, `scripts/run`, `scripts/wall`. Modules added or removed: none. Edges added or removed: none. Outbound added: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

`tests/test_slice_rebase.py` (24 tests, with the stand-in maker in `tests/fake_agent.py`). A clean rebase moves the branch and `base` to the default or to `--onto`, not to the merge base. The maker runs once, with "rebase" in its brief. Test-file and picture conflicts stop for the originator, and the agent does not run. CHANGELOG and estimation conflicts keep both sides. The maker resolves other conflicts and logical breaks, and `next` becomes `cleaner`. A stuck maker stops. A closed slice stays closed on a clean rebase and opens again on a resolved conflict. Named commits move, and a dropped one stops. The wall count rises for a test file added on main, and `moved_tests` is kept. A red suite stops. A stop leaves the rebase in progress. `--continue` finishes it (base, wall, suite). `--abort` restores the branch and the record. Both flags are refused with no rebase in progress. `worktrees.base` is the default. No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none (the forecast expected `wide`, so this is not wider).
- No module, edge, table or outbound call is added (the boundary picture: all `none`).
- `xv slice rebase` is a new subcommand inside the existing `xv` CLI surface (`.xv/picture.md:27` "Surfaces: the `xv` CLI"), and `slice` already lands in `run.py` (`.xv/picture.md:22`). It is not a new surface.
- The four new stops (`rebase_conflict`, `rebase_dropped`, `rebase_stuck`, `rebase_suite_red`) are in `scripts/orders.py:162` `if after == "rebase":`, where the picture puts stop rules (`.xv/picture.md:23` "`orders` holds the stop rules").
- Not a miss, for Sean to decide: the rebase stops never reach the record. `scripts/run.py:359-368` `rebase_stop` builds the verdict in memory, prints it and calls `reach`, then `sys.exit(EXIT_STOP)`. There is no `record.apply_verdict` and no save. The picture says that one function "writes the stop or the send-backs" (`.xv/picture.md:23`). So `xv record answer` finds no open stop for a rebase stop, and `decisions` never counts these stops. That may be on purpose, since `--abort` must put the record back (point 14), but nothing says so.
- Not a miss: the rebase maker run skips the budget gate. `scripts/run.py:382` applies `agentcli.with_caps` but never calls `orders.budget_before`. That gate runs before every other step (`scripts/run.py:564`). The picture says "`orders.budget_before` checks it before every step" (`.xv/picture.md:23`).

## 2. Pitch

pitch_contradiction: no. The pitch says nothing about rebasing. The only negative line, "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md`, "Who it is not for"), is untouched: the maker resolving a conflict is the agent writing code, with test-file and picture conflicts kept for a person.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`moved_tests: []`, and `xv wall diff` shows changed, deleted and added all empty against baseline `a671dab`. `tests/fake_agent.py` changed after the base (commit `2af37d8`, the scenario agent's red). It has 24 added lines, none removed, and no assertion. It is a new branch gated on `FAKE_REBASE_MODE` (`tests/fake_agent.py:28`), so no old test asserts less. `may_not_files: []` and `old_tests_forced: []`, so the packet lists no permitted may-not edits.

Slice-only tests removed: none. Kept: none.

## 4. The picture

Proposed edits for Sean to accept:
- `.xv/picture.md:22`: add `xv slice rebase` to what `slice` runs in `run.py`.
- `.xv/picture.md:23`: add that `orders` decides four stops after `rebase`, and that, unlike `xv step`/`xv run`/`xv record packet`, `xv slice rebase` prints its stop and reaches the seat without writing it to `stops` (`scripts/run.py:359-368`), or change the code first (check 1). Add that `prompt.build` takes a `part`, which the rebase uses to add `skills/maker/rebase.md` to the maker's brief (`scripts/prompt.py:177,203`). Add that `wall.baseline` takes `keep`, which holds the hashes of files the slice changed (`scripts/wall.py:61-68`).
- `.xv/picture.md:26` (state is files): add that a slice can be rebased. `base` moves to the `--onto` commit, the named commits move by subject, and a rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json` (`scripts/run.py:342` `rebase_state_path`).
- `.xv/picture.md:35` (what the maker may touch): the rebase brief adds "Do not touch a test file, `.xv/picture.md` or anything under `.xv/` to make a conflict go away" (`skills/maker/rebase.md:7`).

Not checked against a person's view: the cleaner reports that its edits were uncommitted. Commit `3ae09ad` ("record the cleaner's pass") carries them, and the record still has `cleaner_commit: null`.

## 5. The wall

No recommendations. I looked at all 24 new tests in `tests/test_slice_rebase.py`. Each checks behaviour that lasts, not a one-time wording change. None is marked slice-only (`slice_only: []`). None restates another: `test_a_stop_leaves_the_rebase_in_progress_in_the_slice_worktree` adds the in-progress and marker checks to the conflict-stop tests. No old wall test is made dead (`xv wall diff`: nothing changed).

## Scenario misses

- 16: the exception for the slice's own red before the maker is not built. After the rebase the suite stops on any red: `scripts/run.py:464-470` `suite, out = run_suite(root, config, state["onto"], slice_id)` … `if suite == "red": rebase_stop(...)`. Nothing excludes the red files or checks whether the maker has made the suite green. The record's own `watch_first_green` expects "a clean rebase of an open slice with its own red still failing exits 0". Every red test that rebases an open slice either runs `run_loop()` first (the maker is done) or has no red yet (evidence: `tests/test_slice_rebase.py` `rebase()` callers; to: scenario).
- 5: a dropped named commit does not stop when the rebase is continued after a different stop. Every `--continue` sets `continued`, which skips the `rebase_dropped` stop and clears the commit from the record, so a person who resolves a test-file conflict and continues never sees the drop. No red test combines a conflict stop with a dropped commit (evidence: `scripts/run.py:494` `state["continued"] = True`, `scripts/run.py:439` `if dropped and not state.get("continued"):`; to: scenario).
- 11: on `--continue`, no agent looks for logical breaks unless a later commit conflicts. After a test-file or picture stop, the maker's look is skipped. Point 14 lists only "the record's commits move, the wall is hashed again, and the suite runs" as the work `--continue` finishes. If that list was meant to leave out the look, the scenario should say so. No red test checks whether the maker runs on `--continue` (evidence: `scripts/run.py:423` `if not state["maker_ran"] and not state.get("continued"):`; to: scenario).
- 6: hashing the wall again erases the slice's own test-file deletions and its additions made after the baseline. An old hash is kept only for a file that still exists. So a test file the slice deleted drops out of the new baseline, and `xv wall diff`/`check` no longer report it as `deleted`. A test file the maker or cleaner added after the baseline is hashed in, so it no longer shows as `added`. The scenario says to hash again only "for test files the slice has not touched". The red checks only a file added on main (evidence: `scripts/wall.py:66-67` `for f, h in ((keep or {}).get("files") or {}).items(): if f in files:`; `test_the_wall_is_hashed_again_for_untouched_test_files_and_the_moves_are_kept`; to: scenario).
- decision 1: the slice adds four standing orders and a part of the maker's brief with its own may-not lines, with no line in `CHANGELOG.md`. The decision says "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`". Earlier slices add the line in their maker commit (e.g. `17bef83`). The repo runs solo for the two-people half (`.xv/picture.md:55`) (evidence: `.xv/picture.md:63`; `scripts/orders.py:162-180` `if after == "rebase":`; `skills/maker/rebase.md`; `CHANGELOG.md` absent from `git diff --stat 66570aa..HEAD`; to: maker).

## Door

**Door:** two-way: reverting the commits removes the subcommand, and no data, contract or message is migrated or sent. **Blast radius:** contained. Changes to existing paths are additive and default off: `prompt.build(part=None)`, `wall.baseline(keep=None)`, and the `FAKE_REBASE_MODE` gate in the stand-in agent.

Outside the misses, for Sean: the maker runs' spend sits only in the rebase state until `rebase_finish` writes it (`scripts/run.py:388` `state["runs"].append(...)`). `--abort` deletes that state and resets the record (`cmd_slice_rebase` abort path, `os.remove(rebase_state_path(...))`), so spend from an aborted rebase never reaches `spend` and the budget undercounts (`.xv/picture.md:23`, "`spend.slice_spend` is the count the slice budget uses").

## Raw data

- Slice record: `.xv/slices/2026-11-04-slice-rebase.md`
- Diff: `git diff 66570aa785961973ad109e9db00dfc167a823e9b..3ae09ad`
- Wall: `xv wall diff 2026-11-04-slice-rebase`
- Boundary: `xv boundary --base 66570aa785961973ad109e9db00dfc167a823e9b` (as `.xv/slices/2026-11-04-slice-rebase.boundary.md`)

---
slice: 2026-11-04-proto-start
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: A prototype variant is never dropped when the three start at once: #61

Nothing stops this for two people. Sean has three things to decide: the picture edit (check 4); a variant whose agent ran and then errored loses its spend (finding A); and the stop after a failed variant still does not name it (finding B, raised last time and still open). Sean merges.

## The scenario

On #55, `xv prototype start` ran three variants at once. Variant b never called its agent, and no error reached the person. What should now hold (`.xv/slices/2026-11-04-proto-start.md:42-50`):

1. One variant's git setup never overlaps another's. The agents still run at the same time.
2. A variant whose setup git refuses is recorded as not finished, with its error, in the side-by-side file. The other two still run. A second start runs it again.
3. (amended) Any other error in a variant's thread is handled the same way: an error after setup, or one that is not an `XVError`.
4. (amended) `xv prototype pick` refuses such a variant with a reason that says its setup or run failed, not that it ran out of budget.

May ignore: #58 (building in turns), prototypes applying their own stop (#117), and old prototype records, which keep their shape.

## The recording

There is none; the scenario starts from words. To replay: `cd tests && python3 -m unittest test_prototypes.PrototypesGitSetupTest`. At the red, 6 of 8 failed (`checks.scenario.red_output`). I ran it at HEAD `a2fc4bb` for this review: 8 tests, `OK`, 36.0s. The whole suite was green after the maker and after the cleaner: 672 OK (`checks.maker.suite_output`, `checks.cleaner.suite_output`). I did not rerun the whole suite.

## The boundary picture

From `.xv/slices/2026-11-04-proto-start.boundary.md`:

- **Touched:** `scripts/prototypes` only.
- **Added or removed:** no modules, edges, tables, surface paths or outbound calls.
- **Shape hints:** none.

## What the suite asserts after

Every assertion is new, in `tests/test_prototypes.py`:

- Each variant's git setup ends before or starts after every other variant's (`:144`).
- All three agents start before any one ends (`:157`).
- If git refuses b's setup:
  - Only a and c run.
  - b is in the record with no recording.
  - `index.lock` appears in b's section of the side-by-side file and in the slice record (`:164`).
  - A second start reruns only b, and then all three have recordings (`:180`).
- If b's worktree is gone after setup, b is recorded and its section reads `Not finished: <error>` (`:207`). The same holds if writing b's run log raises `IsADirectoryError` (`:212`).
- Picking b after either failure exits non-zero. The reason matches setup, failed or did not finish, and does not contain `budget` (`:226`, `:234`).
- The existing test at `:29` is unchanged. The new class sets it to `None`, so it does not run twice.

## 1. Shape

shape_change: no.

- The boundary picture has no new module, edge, table, surface or outbound call, and no shape hints (`.xv/slices/2026-11-04-proto-start.boundary.md:12-19`, `:110-116`, `:416` `"shape_hints": []`).
- `scripts/prototypes.py:42` `SETUP_LOCK = threading.Lock()` is a process-local lock. `threading` was already imported (`:23`), so it adds no dependency.
- `scripts/prototypes.py:192` adds an `error` key to every new `prototypes` entry in the record. It is `null` when the variant finished. This changes a field, not the shape: the record file and its readers stay the same. `pick` reads it with `.get` (`:247`), so old records without the key still load.
- **Breadth: `narrow`.** That matches the forecast's `"shape": "narrow"`: one script, plus its tests. The forecast's breadth line says "no record shape change", and the `error` key is a small one. The forecast predates amendment 4, and amendment 4 needs some way to tell why a variant failed. I list it so the person sees it. I do not count it as wider.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md`: "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." A failed variant now shows up instead of vanishing.
- Nothing touches "Who it is not for, and what it will never do".

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |

None. `xv wall diff 2026-11-04-proto-start` reports `changed: []`, `deleted: []` and `fewer_assertions: []`. Against base `c7b8bbf`, `tests/test_prototypes.py` only gains lines. The record has `moved_tests: []`.

Slice-only tests removed: none. Kept: none (the record's `slice_only` is `[]`).

## 4. The picture

`.xv/picture.md:26` describes prototypes ("A variant has finished when it has a recording and did not run out … A variant that ran out cannot be picked."). It says nothing about a variant that fails. Proposed addition after "A variant that ran out cannot be picked.":

> Each variant's git setup (worktree remove, branch delete, worktree add) runs one at a time under a lock in `prototypes`; the agents still run together. A variant whose setup or run raises any error is recorded with no recording and with its `error`, so it has not finished and a second start reruns it. The error goes into its section of the side-by-side file and the slice log. A variant with an `error` cannot be picked, and the refusal says its setup or run failed.

Evidence: `scripts/prototypes.py:50-62`, `:179-183`, `:192`, `:247-248`. If finding A stays as it is, the edit should also say that no spend is recorded for such a variant. That would qualify ":26 … on what is left of its budget".

## 5. The wall

No recommendations. I looked at all eight new tests (`tests/test_prototypes.py:144-240`). Each one guards lasting behaviour: serialised setup, agents running together, a failed variant kept and rerun, and the pick reason. None guards a one-time change.

`:164` and the helper `unfinished_b_is_recorded` (`:192`) overlap in what they check, but they are reached by different failures (refused setup, a vanished worktree, an `IsADirectoryError`). So neither restates the other.

## Findings for the person

- **A. A variant that errors after its agent ran loses its spend.** `agentcli.run` writes the run log only after the agent process has finished (`scripts/agentcli.py:75-89`). If the write fails, as `:212` makes it fail, the agent has already spent. `run_one` then records the error entry with no `spend` (`scripts/prototypes.py:60-62`), and `:183` `if p and not p.get("kept") and not p.get("error")` skips adding spend for errored variants. So the spend never reaches `data["spend"]`. Two effects follow:
  - Nothing counts it against b's prototype budget.
  - The rerun gets more than "what is left of its budget" (`.xv/picture.md:26`).

  A timeout does not raise, so it does not hit this path. An error after the agent ran does. No scenario line names spend, so this is not a miss.
- **B. The stop after a failed variant still does not name it.** This was noted at the last packet and is unchanged. A failed variant is not in `ran_out`, so the stop is `prototypes_ready` with "N prototype(s) are ready to pick from, or none." (`scripts/orders.py:281-285`). The person learns which variant failed only from the side-by-side file the stop points to. `tests/test_prototypes.py:185` answers that stop as two people before the second start.
- **C. A vanished worktree gets a misleading error.** In the `:207` case, `subprocess.run` with a missing `cwd` raises `FileNotFoundError`. `scripts/agentcli.py:81-82` turns that into "agent CLI not found: <python>", and that wrong reason is what the side-by-side file shows. This is older `agentcli` code. Point 3 asks for "its error", and the error recorded is this one.

## Door

**Door:** two-way. A revert removes the lock, the two catches and the pick reason. Records written in the meantime keep an `error` key, which old code ignores. **Blast radius:** small (only `xv prototype start` and `pick`).

## Raw data

- Slice record: `.xv/slices/2026-11-04-proto-start.md`
- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..a2fc4bb -- scripts tests`
- Wall: `xv wall diff 2026-11-04-proto-start`; baseline `.xv/slices/2026-11-04-proto-start.wall.json`
- Boundary: `.xv/slices/2026-11-04-proto-start.boundary.md`
- Run logs: `.git/xv/runs/2026-11-04-proto-start/` (08-maker.out, 09-cleaner.out)

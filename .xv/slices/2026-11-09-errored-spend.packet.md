---
slice: 2026-11-09-errored-spend
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: An errored prototype variant keeps its spend, and a gone worktree says so

No stop for two people: no shape change, no pitch contradiction, no scenario miss.
For the originator (Sean Kennedy): two picture edits (check 4), two wall recommendations (check 5), and one old test whose name the change made untrue (check 3).
The merge is the originator's.

## The scenario

1. A prototype variant whose agent ran and then errored keeps that run's spend in the record, and that spend counts against the variant's prototype budget, so a second `xv prototype start` gives it only what is left (#121).
2. A variant whose working folder is gone reports that the folder is missing, not "agent CLI not found" (#121).

May ignore: a timeout (which does not raise) and a harness that reports no spend.

## The recording

None; this slice started from words.
To replay the red and the green: `cd tests && python3 -m unittest test_prototypes.PrototypesErroredSpendTest`.
Before (at base): 3 failures, e.g. `AssertionError: 0 != 1 : b's agent ran and then errored; its run is in the record` and `1.0 != 0.4 ... b's budget of 1 dollar less the 0.6 it spent` (record `red`, `checks.scenario.red_output`).
After (HEAD b8b90e3): I ran the red together with `tests/test_prototype_errored_spend.py`: 9 tests, OK.
I did not rerun the whole suite; the cleaner's run reports it green (record `suite: green`, `checks.cleaner.suite_output`).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-09-errored-spend.boundary.md`), as given:

- Modules touched: `scripts/agentcli`, `scripts/prototypes`.
- Modules added or removed: none.
- Edges added or removed: none.
- New calls out of the process: none.
- Tables added or removed: none.
- Surfaces users meet, added or removed: none.
- Shape hints: none.

## What the suite asserts after

- When b's run log cannot be written after b's agent ran, b is recorded unfinished, and the record holds exactly one `prototype-b` spend row with `usd` 0.6 (`tests/test_prototypes.py:318`); the build's own test also checks b's `session` is kept (`tests/test_prototype_errored_spend.py:51`).
- On a second start, only b runs again, with a cap of its 1-dollar budget less what it spent (`tests/test_prototypes.py:326`, `tests/test_prototype_errored_spend.py:62`).
- An errored variant whose run spent past its budget has run out, and `prototype_budget_spent` stops with exit 10 (`tests/test_prototype_errored_spend.py:74`); this is beyond the scenario's words but follows `.xv/picture.md:150`.
- When b's worktree vanishes after setup, b's section and the slice record say "working folder" and never "agent CLI not found" (`tests/test_prototypes.py:338`, `:212`).
- At the unit level, `agentcli.run` with a missing `cwd` raises an `XVError` naming the folder; a missing CLI is still "agent CLI not found"; a run log that cannot be written raises `RanError` carrying the result (`tests/test_prototype_errored_spend.py:86-109`).

## 1. Shape

shape_change: no.
shape_breadth: narrow, as the forecast expected (record `forecast.shape: narrow`).

- The boundary picture shows no module, edge, table or surface added or removed, and no shape hints (boundary picture, "Shape hints: none", "Edges: added: none").
- `RanError` and `gone()` are new names inside `scripts/agentcli.py` (hunk `scripts/agentcli.py:16-30`), and `spend_of` is a new function inside `scripts/prototypes.py` (hunk `scripts/prototypes.py:70-75`); both stay inside the existing `prototypes -> agentcli` and `prototypes -> spend` edges, which `.xv/picture.md` already has (`scripts/run`/`prototypes` reach list at `.xv/picture.md:37`, boundary JSON edges).
- Note on reach, not shape: `agentcli.run` is shared by every agent call (callers at `scripts/run.py:534`, `:761`, `:833`, `:1427`, `:1509`, `scripts/listen.py:153`, `scripts/retro.py:182`, `evals/run.py:161`).
  The new `cwd` check (`scripts/agentcli.py:86-87`) and the new `RanError` on a failed log write (`scripts/agentcli.py:104-113`) apply to all of them.
  For a non-prototype step such as the maker (`scripts/run.py:534-536`), a log write failure now raises an `XVError` instead of an `OSError`, and its spend is still lost, since only `prototypes.run_one` reads `e.result` (`scripts/prototypes.py:64`).
  The scenario names only prototype variants, so this is not a miss; it is the same defect class left open on the slice's own steps.

## 2. Pitch

pitch_contradiction: no.

- I read `.xv/pitch.md` whole: the purpose ("makes it easy ... to vibe with discipline", `.xv/pitch.md:7`), who it serves (`.xv/pitch.md:21`), and what it is not for ("not for people or projects that will not trust agents to write production code. It will never be a teapot.", `.xv/pitch.md:25`).
- The change keeps an errored variant's spend and renames one error message (hunks `scripts/prototypes.py:58-67`, `scripts/agentcli.py:86-87`); neither serves anyone `.xv/pitch.md:25` excludes or does anything it rules out.
  The pitch is silent on prototype spend, and silence is not a contradiction.
- Binding decision 6, "Dollars are recorded only where a harness reports them, never estimated" (`.xv/picture.md:287`): kept. When a run's spend cannot be read, `spend_of` writes `"usd": None`, not an estimate (hunk `scripts/prototypes.py:70-75`).
- Binding decision 3, standard library only (`.xv/picture.md:278`): kept; no new imports in either script (whole diff).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_prototypes.py` | No such test; no base line changed | `PrototypesGitSetupTest.test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli` added (`tests/test_prototypes.py:212-218`): b's section lacks "agent CLI not found", has "working folder" and "p1-proto-b" | "the build (explore/errored-spend) added it for #121; no line at the base was changed or removed (#172)", recorded by Sean Kennedy | Yes for scenario point 2, but the red test at `tests/test_prototypes.py:338` already forces the same thing (see check 5) |

`xv wall diff`: changed `tests/test_prototypes.py`, assertions 49 -> 52, `fewer_assertions: []`, `unrecorded: []`; added `tests/test_prototype_errored_spend.py` (a new file, not a move of an old test).
Expected moves: none.
Slice-only tests removed: none. Kept: none (`slice_only: []`).
May-not files the scenario agent allowed: none (`may_not_files: []`).

A test on the wall whose text did not move but whose premise did:
- `tests/test_prototypes.py:220` `test_an_error_that_is_not_an_xverror_records_the_variant_not_finished_with_its_error` makes b's error by blocking the run log (`block_b_run_log`, `tests/test_prototypes.py:201-204`).
  At the base that raised an `OSError` out of `agentcli.run`, the non-`XVError` path its name promises.
  Now `agentcli.run` turns that `OSError` into `RanError`, an `XVError` subclass (hunk `scripts/agentcli.py:104-113`, `class RanError(XVError)` at `:19`).
  The test still passes, but it no longer exercises an error that is not an `XVError`, and I found no other test that does.
  It asserts the same lines as before; what it covers has narrowed, and its name is now untrue.

## 4. The picture

picture_change: yes.

- `.xv/picture.md:156` says a variant whose setup or run raises "is recorded with no recording and with its `error`", and says nothing of its spend.
  Proposed: add after that line, in the same list item (two-space indent):

  ```
    A variant whose agent ran before the error keeps that run's spend and session, and the spend counts against its own budget, so a second start gives it only what is left (#121).
  ```

- `.xv/picture.md:94` describes `agentcli.run` but not the two new behaviours every agent call now has (hunks `scripts/agentcli.py:86-87`, `:104-113`).
  Proposed: add after line 94:

  ```
    `agentcli.run` reports a working folder that is not there as gone, never as a missing agent CLI.
    When the agent ran but its run log cannot be written, `agentcli.run` raises `RanError`, which keeps the run's result.
  ```

## 5. The wall

- `tests/test_prototypes.py`, `PrototypesGitSetupTest.test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli`: mark slice-only.
  It restates the red test `PrototypesErroredSpendTest.test_a_variant_whose_working_folder_is_gone_says_the_folder_is_missing` (`tests/test_prototypes.py:338-344`): same `FAKE_GIT_VANISH=b`, same "agent CLI not found" absence, same "working folder" presence; its one extra assertion, the folder's path, is also in `GoneFolderTest.test_a_missing_working_folder_is_not_reported_as_a_missing_agent_cli` (`tests/test_prototype_errored_spend.py:91`).
- `tests/test_prototype_errored_spend.py`, `ErroredVariantSpendTest.test_a_second_start_gives_the_errored_variant_only_what_is_left_of_its_budget`: mark slice-only.
  It restates the red test `PrototypesErroredSpendTest.test_the_errored_variants_spend_counts_against_its_budget_on_the_second_start` (`tests/test_prototypes.py:326-336`): block b's log, start, unblock, answer "run b again", start, assert only b runs with its budget less its spend.

## Door

**Door:** two-way; a revert of `scripts/agentcli.py` and `scripts/prototypes.py` undoes it, and spend rows already written stay valid records of real runs. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-09-errored-spend.md`
- Diff: `git diff 4f6dcb707076f9b7a130b27302e6cafdd92e73e1..b8b90e3`
- Wall: `xv wall diff 2026-11-09-errored-spend`
- Boundary: `xv boundary --base 4f6dcb707076f9b7a130b27302e6cafdd92e73e1` (`.xv/slices/2026-11-09-errored-spend.boundary.md`)

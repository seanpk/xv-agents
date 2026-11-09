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

This is the second pass, after the maker restored the old test's non-XVError path and the cleaner removed the two accepted slice-only tests.
No stop for two people: no shape change, no pitch contradiction, no scenario miss.
For the originator (Sean Kennedy): one picture edit (check 4), which the restored test makes visible: a variant whose agent ran but whose output is not text keeps no spend row.
The merge is the originator's.

## The scenario

1. A prototype variant whose agent ran and then errored keeps that run's spend in the record, and that spend counts against the variant's prototype budget, so a second `xv prototype start` gives it only what is left (#121).
2. A variant whose working folder is gone reports that the folder is missing, not "agent CLI not found" (#121).

May ignore: a timeout (which does not raise) and a harness that reports no spend.

## The recording

None; this slice started from words.
To replay the red and the green: `cd tests && python3 -m unittest test_prototypes.PrototypesErroredSpendTest`.
Before (at base): 3 failures, for example `AssertionError: 0 != 1 : b's agent ran and then errored; its run is in the record` (record `red`, `checks.scenario.red_output`).
After (HEAD f741fde): I ran `test_prototypes.PrototypesErroredSpendTest`, `test_prototypes.PrototypesGitSetupTest` and `test_prototype_errored_spend`: 16 tests, OK.
I did not rerun the whole suite; the cleaner's run reports it green (record `suite: green`, `checks.cleaner.suite_output`, 1170 tests).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-09-errored-spend.boundary.md`), as given:

- Modules touched: `scripts/agentcli`, `scripts/prototypes`.
- Modules added or removed: none.
- Edges added or removed: none.
- New calls out of the process: none.
- Tables added or removed: none.
- Surfaces users meet, added or removed: none.
- Shape hints: none.

Since the first guardian pass (`git diff 27dd265..HEAD`), only `tests/test_prototypes.py`, `tests/test_prototype_errored_spend.py` and the slice record changed; no script changed.

## What the suite asserts after

- When b's run log cannot be written after its agent ran, b is recorded unfinished and the record holds one `prototype-b` spend row of 0.6 dollars (`tests/test_prototypes.py:325-331`); the new file also checks b's `session` is kept (`tests/test_prototype_errored_spend.py:51-60`).
- On a second start only b runs, with a cap of its 1-dollar budget less what it spent (`tests/test_prototypes.py:333-343`).
- An errored variant whose run passed its budget has run out, and `prototype_budget_spent` stops with exit 10 (`tests/test_prototype_errored_spend.py:62-69`).
- When b's worktree vanishes, b's section says "working folder" and neither it nor the slice record says "agent CLI not found" (`tests/test_prototypes.py:345-352`).
- At the unit level, `agentcli.run` with a missing `cwd` raises an `XVError` naming the folder, a missing CLI is still "agent CLI not found", and a run log that cannot be written raises `RanError` with the result (`tests/test_prototype_errored_spend.py:72-97`).
- An error that is not an `XVError` (b's agent prints bytes that are not text) still records b unfinished with its error (`tests/test_prototypes.py:227-232`), as at the base.

## 1. Shape

shape_change: no.
shape_breadth: narrow, as the forecast expected (record `forecast.shape: narrow`).

- The boundary picture shows no module, edge, table or surface added or removed, and no shape hints (boundary picture, "Shape hints: none", "Edges: added: none").
- `RanError` and `gone()` are new names inside `scripts/agentcli.py` (hunk `scripts/agentcli.py:19-30`), and `spend_of` is a new function inside `scripts/prototypes.py` (hunk `scripts/prototypes.py:70-75`); both sit on edges the picture already has (`.xv/picture.md:37`, boundary JSON `scripts/prototypes -> scripts/agentcli`, `-> scripts/spend`).
- Reach, not shape, carried from the first pass: the `RanError` on a failed log write (`scripts/agentcli.py:105-112`) applies to every agent call, but only `prototypes.run_one` reads `e.result` (`scripts/prototypes.py:64`), so other steps still lose spend on a log write failure.
  Sean's accept_moves answer already sends this to an issue (record `stops[2].new_info`: "file an issue for lost spend on other steps and wait for evidence").

## 2. Pitch

pitch_contradiction: no.

- I read `.xv/pitch.md` whole: its purpose ("to vibe with discipline", `.xv/pitch.md:7`), who uses it (`.xv/pitch.md:21`), and what it is not for ("not for people or projects that will not trust agents to write production code. It will never be a teapot.", `.xv/pitch.md:25`).
- Keeping an errored variant's spend and naming a gone folder (hunks `scripts/prototypes.py:58-67`, `scripts/agentcli.py:86-87`) serve no one `.xv/pitch.md:25` excludes; the pitch is silent on prototype spend, and silence is not a contradiction.
- Binding decision 6, "Dollars are recorded only where a harness reports them, never estimated" (`.xv/picture.md:290`): kept; `spend_of` writes `"usd": None` when spend cannot be read (hunk `scripts/prototypes.py:70-75`).
- Binding decision 3, standard library only (`.xv/picture.md:281`): kept; no new imports in either script (whole diff).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_prototypes.py` | `test_an_error_that_is_not_an_xverror_records_the_variant_not_finished_with_its_error`: `block_b_run_log()` (an `OSError` at the base); asserts b unfinished and `"prototype-b.out"` in the slice record | `make_b_raise_a_plain_error()`: b's agent prints `b'\xff\xfe'`, a `UnicodeDecodeError`; asserts b unfinished and `"codec"` in the slice record (hunk `tests/test_prototypes.py:212-232`) | "agentcli now turns the blocked run log into RanError, so the test no longer reached a non-XVError path; Sean's accept_moves answer has the maker restore it without changing what it asserts" | Yes: `RanError(XVError)` (hunk `scripts/agentcli.py:19`, `:105-112`) removed the old way to reach a non-XVError, and Sean's answer (record `stops[2].settled`) directs the restore |

- It does not assert less: the same `unfinished_b_is_recorded()` plus one `assertIn` that the record keeps b's error; only the error text it looks for changed (`tests/test_prototypes.py:227-232`).
  `xv wall diff`: `tests/test_prototypes.py` 49 -> 49 assertions, `fewer_assertions: []`.
- What the restored test drives is an agent that ran and then errored with no spend kept: the `UnicodeDecodeError` is raised inside `subprocess.run` in `agentcli.run`, which catches only `TimeoutExpired` and `FileNotFoundError` (`scripts/agentcli.py:89-99`), so no result exists and `ran["result"]` is never set (`scripts/prototypes.py:92`).
  I count this under the scenario's may-ignore "A harness that reports no spend", since output that is not text cannot report spend and decision 6 forbids an estimate (`.xv/picture.md:290`); it does make `.xv/picture.md:159` say more than is true (check 4).
- The build's added test `PrototypesGitSetupTest.test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli` was a recorded move (Sean Kennedy, #172) and is now removed as slice-only (`git diff 27dd265..HEAD -- tests/test_prototypes.py`, record `slice_only`).

Expected moves: none.
Slice-only tests removed: `tests/test_prototypes.py::PrototypesGitSetupTest.test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli`, `tests/test_prototype_errored_spend.py::ErroredVariantSpendTest.test_a_second_start_gives_the_errored_variant_only_what_is_left_of_its_budget`. Kept: none.
May-not files the scenario agent allowed: none (`may_not_files: []`).

## 4. The picture

picture_change: yes.

- `.xv/picture.md:159` says "A variant whose agent ran before the error keeps that run's spend and session".
  An agent that ran but printed output that is not text raises inside `agentcli.run` before a result exists (`scripts/agentcli.py:89-99`), and b keeps no spend row (`scripts/prototypes.py:64-66`, `:199`); the restored test drives exactly that run (`tests/test_prototypes.py:212-232`).
  Proposed: replace line 159 with these two lines, in the same list item (two-space indent):

  ```
    A variant whose agent ran before the error keeps that run's spend and session, and the spend counts against its own budget, so a second start gives it only what is left (#121).
    An agent whose output is not text raises before `agentcli.run` has a result, so that variant keeps no spend.
  ```

- The two lines Sean accepted in the first pass are in (`.xv/picture.md:95-96`, `:159`, commit 0b81be9); I found nothing else in the picture that the slice makes untrue (read `.xv/picture.md:88-100`, `:150-163`).

## 5. The wall

No new recommendation.
The two accepted slice-only tests are gone (`git diff 27dd265..HEAD`, `tests/test_prototypes.py`, `tests/test_prototype_errored_spend.py`).
I read each remaining new test against the red: `ErroredVariantSpendTest.test_a_variant_that_errors_after_its_agent_ran_keeps_that_runs_spend` adds the `session` assertion the red lacks (`tests/test_prototype_errored_spend.py:60`), `test_an_errored_variant_whose_run_passed_its_budget_has_run_out` covers the run-out stop (`:62-69`), and the three `GoneFolderTest` tests guard `agentcli.run` at the unit level (`:72-97`); none restates another.

## Door

**Door:** two-way; a revert of `scripts/agentcli.py` and `scripts/prototypes.py` undoes it, and spend rows already written stay true records of real runs. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-09-errored-spend.md`
- Diff: `git diff 4f6dcb707076f9b7a130b27302e6cafdd92e73e1..f741fde`
- Since the first pass: `git diff 27dd265..f741fde`
- Wall: `xv wall diff 2026-11-09-errored-spend`
- Boundary: `xv boundary --base 4f6dcb707076f9b7a130b27302e6cafdd92e73e1` (`.xv/slices/2026-11-09-errored-spend.boundary.md`)

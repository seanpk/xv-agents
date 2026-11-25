---
slice: 2026-11-25-failed-step
shape_change: no
shape_breadth: narrow
pitch_contradiction: no
change_misses_scenario: no
door: two-way
blast_radius: small
---

# Inspection: a failed step marks its start ended (#202)

## Needs a decision

1. **The new save writes the record as it was before the agent ran, also when the agent did run.**
   `scripts/run.py:862-867`:
   ```
   except BaseException:
       if scratch:
           drop_scratch(root, scratch)
   +   data["step_start"]["ended"] = True  # the agent never ran: a move reads HEAD, not this step's start
   +   record.save(path, data, body)
       raise
   ```
   The `except BaseException` also catches `RanError`, which `agentcli.run` raises after the agent ran, when its run log cannot be written (`scripts/agentcli.py:124`: "the agent ran, and its run log could not be written").
   It also catches `KeyboardInterrupt` while the agent is running.
   In both cases `data` is the copy loaded before the run.
   The normal path reloads first: "`data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` itself`" (`scripts/run.py`, the line after the hunk).
   Before this slice, the error path saved nothing, so anything the agent wrote with `xv record` (a move, a report) stayed.
   Now the save overwrites it.
   The comment "the agent never ran" is untrue on these two paths.
   The scenario may ignore "a step that fails after the agent ran" (record, May ignore), so this is not a scenario miss.
   But the change makes that case worse, where before it was left alone.
   For the person: accept it, or send it back to reload the record before marking it ended, or to mark it ended only on the could-not-run errors.

## The scenario

When `xv step` fails because the agent could not run (the CLI is missing, or the worktree is gone), `step_start` is marked ended (1).
A slice-only move recorded after that reads its line from `HEAD` (2).
There is a CHANGELOG line (3).
May ignore: a step that fails after the agent ran.

## Recording

None; the slice started from words.
Replay: `cd tests && python3 -m unittest test_record.FailedStepEndsItsStartTest` (run by the inspector: 2 tests, OK).

## Boundary diagram

From `.xv/slices/2026-11-25-failed-step.boundary.md`: touched `scripts/run`; modules, edges, outbound calls, tables and surfaces added or removed: none; shape hints: none.

## What the suite asserts after the change

- When the agent CLI is not installed, `xv step forecaster` exits non-zero, says "agent CLI not found", and the record's `step_start` has `ended: true` (`tests/test_record.py:483-485`).
- After that failed step, a test file grows from 1 line to 6, and `xv record move --slice-only --line 5` is accepted because line 5 is read from `HEAD` (`tests/test_record.py:487-492`).
- The "worktree is gone" half of outcome 1 has no test of its own.
  It goes through the same `except` (`agentcli.run` raises `gone(cwd)` inside the `try`), so the code covers it; only the CLI-missing path is exercised.

## Moved tests

None.
`xv wall diff 2026-11-25-failed-step`: `changed`, `deleted`, `added`, `fewer_assertions` all empty.
Record: `moved_tests: []`, `slice_only: []`, `may_not_files_needed: []`.
Slice-only removals: none.

## The five checks

### 1. Shape — no, narrow

The boundary diagram lists no added module, edge, outbound call, table or surface, and no shape hints.
The code change is two lines inside `step` in `scripts/run.py:865-866`, using `record.save`, which `run` already calls.
`.xv/picture.md:78-79` already describes `step_start` and its `ended` mark; the change applies that mark on one more path.
Breadth narrow, as the forecast expected ("the failed-step branch that marks step_start ended ... with one test and the CHANGELOG line").

### 2. Pitch — no contradiction

Read `.xv/pitch.md` whole.
The change makes a record field right after a failed run; it serves the same users and goes nowhere near "people or projects that will not trust agents to write production code" (`.xv/pitch.md`, "Who it is not for").

### 3. Moved tests

None; see above.

### 4. The picture — one edit

`.xv/picture.md:79` reads: "`xv step` marks `step_start` ended once its checks are done, so a move between steps reads `HEAD`."
After this slice it is incomplete: a step whose agent could not run marks it ended too (`scripts/run.py:865`).
Proposed text, after line 79:

```
  A step whose agent could not run (the agent CLI is missing, or the working folder is gone) also marks `step_start` ended before it fails, so a move after it reads `HEAD`.
```

If finding 1 is accepted as is, add a second line:

```
  A step that fails after its agent ran also marks `step_start` ended, and saves the record as it was before the run.
```

Binding decisions: 1 (CHANGELOG line) is met by `CHANGELOG.md:5-7`; 11 (exit codes) holds because the `except` still re-raises (`scripts/run.py:867`).

### 5. The wall

The two new tests in `FailedStepEndsItsStartTest` (`tests/test_record.py:460-492`) guard behaviour that should last, not a one-time change; they should join the wall.
No test on the wall is made dead.
No recommendations.

## Notes

- The new test's `setUp` opens `.xv/config.yml` without closing it (`tests/test_record.py:466`, `:469`); running the red prints four `ResourceWarning`s.
  No rule in `.xv/standards.md` covers it.

## The door

Two-way door: a revert of `scripts/run.py:865-866` undoes it; no data is migrated and no contract changes.
Blast radius: small.

## Raw data

- Diff: `git diff ae7929481b166143489f51e6194aaf375eca7bb6..HEAD -- scripts/run.py tests/test_record.py CHANGELOG.md`
- Wall: `xv wall diff 2026-11-25-failed-step`; baseline `.xv/slices/2026-11-25-failed-step.wall.json`
- Boundary: `.xv/slices/2026-11-25-failed-step.boundary.md`
- Maker and cleaner suite runs: record `checks.maker`, `checks.cleaner` (1526 tests, OK)

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:231.

---
slice: 2026-11-25-failed-step
shape_change: no
shape_breadth: narrow
pitch_contradiction: no
change_misses_scenario: no
expected_moves: 0
door: two-way
blast_radius: small
---

# Inspection: a failed step marks its start ended (#202)

## Needs a decision

1. **Accept the picture edit in check 4.**
   Nothing else is open.
   This is a re-pass after the person's answer to `expected_moves_wrong` (option 1: "reload the record before marking step_start ended").
   The maker's change since `6b3ab1e` does what that answer settled, `scripts/run.py:865-867`:
   ```
   -        data["step_start"]["ended"] = True  # the agent never ran: a move reads HEAD, not this step's start
   +        data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` before it failed
   +        if isinstance(data.get("step_start"), dict):
   +            data["step_start"]["ended"] = True  # a move reads HEAD, not this failed step's start
            record.save(path, data, body)
   ```
   The earlier finding 1 is closed: on `RanError` (`scripts/agentcli.py:124`) and on `KeyboardInterrupt`, the save now writes the record as it is on disk, with whatever the agent wrote, plus the `ended` mark.
   The reload is the same call the normal path makes (`scripts/run.py:871`: "`data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` itself`"), so both paths read the same file.
   The untrue comment "the agent never ran" is gone.

## The scenario

When `xv step` fails because the agent could not run (the CLI is missing, or the worktree is gone), `step_start` is marked ended (1).
A slice-only move recorded after that reads its line from `HEAD` (2).
There is a CHANGELOG line (3).
May ignore: a step that fails after the agent ran.

## Recording

None; the slice started from words.
Replay: `cd tests && python3 -m unittest test_record.FailedStepEndsItsStartTest` (run by the inspector on this pass: 2 tests, OK).

## Boundary diagram

From `.xv/slices/2026-11-25-failed-step.boundary.md`: touched `scripts/run`; modules, edges, outbound calls, tables and surfaces added or removed: none; shape hints: none.

## What the suite asserts after the change

- When the agent CLI is not installed, `xv step forecaster` exits non-zero, says "agent CLI not found", and the record's `step_start` has `ended: true` (`tests/test_record.py:483-485`).
- After that failed step, a test file grows from 1 line to 6, and `xv record move --slice-only --line 5` is accepted because line 5 is read from `HEAD` (`tests/test_record.py:487-492`).
- The "worktree is gone" half of outcome 1 has no test of its own; it goes through the same `except` (`agentcli.run` raises `gone(cwd)` inside the `try`).
- No test exercises the reload: a step that fails after its agent wrote with `xv record` is in the scenario's May ignore, so nothing guards that the agent's writes survive (`scripts/run.py:865`).

## Moved tests

None.
Record: `moved_tests: []`, `slice_only: []`, `may_not_files_needed: []`; the maker's and cleaner's wall checks on this pass show `changed`, `deleted`, `added`, `fewer_assertions` all empty.
Slice-only removals: none.

## The five checks

### 1. Shape — no, narrow

The boundary diagram lists no added module, edge, outbound call, table or surface, and no shape hints.
The change since the last pass replaces one line with three inside `step`'s `except` (`scripts/run.py:865-867`), using `record.load`, which `step` already calls at `scripts/run.py:871`.
`.xv/picture.md:78-79` already describes `step_start` and its `ended` mark.
Breadth narrow, as the forecast expected ("the failed-step branch that marks step_start ended ...").

### 2. Pitch — no contradiction

Read `.xv/pitch.md` on the earlier pass; this pass changes only how the record is saved on a failed step.
It serves the same users and goes nowhere near "people or projects that will not trust agents to write production code" (`.xv/pitch.md`, "Who it is not for").

### 3. Moved tests

None; see above.

### 4. The picture — one edit

`.xv/picture.md:79` reads: "`xv step` marks `step_start` ended once its checks are done, so a move between steps reads `HEAD`."
After this slice it is incomplete: a failed step marks it ended too (`scripts/run.py:867`).
Proposed text, after line 79:

```
  A step that fails, also when its agent could not run, marks `step_start` ended before it fails, so a move after it reads `HEAD`.
  It reloads the record first, so anything the agent wrote with `xv record` before the failure stays.
```

This replaces both lines proposed on the earlier pass; the second of those ("saves the record as it was before the run") is no longer true.
Binding decisions: 1 (CHANGELOG line) is met by `CHANGELOG.md:7`; 11 (exit codes) holds because the `except` still re-raises (`scripts/run.py:869`).

### 5. The wall

The two tests in `FailedStepEndsItsStartTest` (`tests/test_record.py:460-492`) guard behaviour that should last; they should join the wall.
No test on the wall is made dead.
No recommendations.

## Notes

- If `record.load` raises inside the `except` (`scripts/run.py:865`), for example because the agent left the record unreadable, that error is raised in place of the step's own, with the step's error chained as its context.
  Before this pass nothing was read there.
  No rule in `.xv/standards.md` covers it, and the scenario may ignore a step that fails after the agent ran.
- From the earlier pass, still true: the test's `setUp` opens `.xv/config.yml` without closing it (`tests/test_record.py:466`, `:469`), printing `ResourceWarning`s.

## The door

Two-way door: a revert of `scripts/run.py:865-868` undoes it; no data is migrated and no contract changes.
Blast radius: small.

## Raw data

- Diff: `git diff ae7929481b166143489f51e6194aaf375eca7bb6..HEAD -- scripts/run.py tests/test_record.py CHANGELOG.md`; this pass: `git diff 6b3ab1ecbc83..HEAD -- scripts/run.py`
- Wall: `xv wall diff 2026-11-25-failed-step`; baseline `.xv/slices/2026-11-25-failed-step.wall.json`
- Boundary: `.xv/slices/2026-11-25-failed-step.boundary.md`
- Maker and cleaner suite runs on this pass: record `checks.maker`, `checks.cleaner` (1526 tests, OK)

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:231.

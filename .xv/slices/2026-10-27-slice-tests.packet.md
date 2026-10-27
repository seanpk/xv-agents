---
slice: 2026-10-27-slice-tests
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: contained
---

# Packet: Tests a slice leaves behind fit the layout and do not go stale

Nothing stops this for two people. Sean, as the person who set the work going, has three findings to decide on before merging: (A) part (4) of the scenario, the cleaner removing slice-only tests, was not built; (B) the `red.command` rewrite does not match the form of red command this repo uses; (C) the scenario's report example has no `slice_only` field. The merge is yours.

## The scenario

From `.xv/slices/2026-10-27-slice-tests.md`, with Sean's answers at the stop (seanpk/xv-agents#17):

1. Scenario brief step 6 asks for new tests in the existing test file for the code under test. A new file is made only when none exists.
2. The scenario agent marks tests that only prove the slice did its job. Its report lists them as `slice_only: [{"file", "test", "why"}]`, and the record keeps that list.
3. `xv record move --to <path>` or `--deleted` updates `red.files` and `red.command`. Both the old path and its module name (`tests/test_x.py`, `tests.test_x`) are replaced. When the last red file is deleted, `red.files` is empty, `red.command` is null, and the log says why.
4. Sean: "the scenario only tests should be removed automatically unless an agent discovers a reason for keeping (any of) them." So after green, the cleaner removes each slice-only test as a recorded move marked slice-only. Those moves do not raise `accept_moves`, and the packet lists them on one line. A test an agent wants to keep stays, and the packet says why.

May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red and then the green: `git checkout eabfe92 && cd tests && python3 -m unittest test_slice_tests` fails 5 and errors 1 (quoted in the record, `checks.scenario.red_output`). At HEAD the same command passes. The whole suite was green for the maker and the cleaner (204 tests, record `checks.cleaner.suite`). I did not re-run it.

## The boundary picture

From `.xv/slices/2026-10-27-slice-tests.boundary.md`, as given: touched `scripts/record`. No modules added or removed, no edges added or removed, no new outbound calls, no tables, no surface paths. Shape hints: none.

Outside the module graph, the diff also touches `skills/scenario/SKILL.md` (one line, step 6) and `CHANGELOG.md` (one line).

## What the suite asserts after

`tests/test_slice_tests.py` is new, with 6 tests:
- A move `--to tests/test_store.py` rewrites `red.files` and changes `tests.test_x` to `tests.test_store` in `red.command`.
- A `--deleted` move drops the file and its module from both.
- Deleting the last red file leaves `files: []`, `command: null`, and a log line naming `red.command`.
- A move of a file that red does not name leaves red unchanged.
- `slice_only` from a scenario report lands in the record.
- Step 6 of the scenario brief no longer says "new files where you can", says "existing test file", and the brief mentions `slice_only`.

No old assertion moved.

## Findings for the person who set the work going

**A. Part (4) of the scenario is not built.** The record's scenario says the cleaner removes slice-only tests, those moves skip `accept_moves`, and the packet lists them on one line. None of that is in the diff:
- The cleaner brief is unchanged. `skills/cleaner/SKILL.md:38`, its tests step, has no slice-only removal.
- `scripts/orders.py:161-169` still fires `accept_moves` for any non-empty `moved_tests`. Nothing marks or exempts a slice-only move.
- The guardian's `skills/guardian/packet.md` has no slice-only line.
- No test covers any of these. The maker's own summary in the record names only parts (1) to (3).

The forecast expected this work: "close output listing removals for approval" (`forecast.breadth`). As built, the record fills a `slice_only` list that nothing reads (`scripts/record.py:317-318`). Decide whether to send this back to the scenario agent for part (4), or to narrow the scenario and open a follow-up.

**B. The `red.command` rewrite misses this repo's own command form.** `scripts/record.py:181` builds `module_of(f)` as `f[:-3].replace("/", ".")`, which gives `tests.test_x`. Lines 186 and 190 only replace tokens equal to that or to the path. Every red command in `.xv/slices/` has the form `cd tests && python3 -m unittest test_x`, a bare module. That includes this slice's own command, `cd tests && python3 -m unittest test_slice_tests`. So in this repo:
- A `--to` move updates `red.files` but leaves `red.command` naming the old module.
- A `--deleted` move of one of several files leaves the deleted module in the command.

In both cases the log says "red.command updated to match". The scenario's settled (2) names only the `tests.test_x` form, so the tests pass as written. But the scenario's stated aim is "so the guardian and the 'watch the first green run' line do not point at a deleted file", and here the command still points at it. Decide whether to widen (2) to cover the bare-module form.

**C. The scenario report example has no `slice_only`.** `skills/scenario/SKILL.md:27` asks for `slice_only` in the report. The report block at `skills/scenario/SKILL.md:46-49`, the section that says what the agent writes to the record, does not show the field. `.xv/picture.md:71` (decision 13) says every brief ends with "what it writes to the record". A fresh scenario agent copying the block will leave it out.

Smaller points:
- Moves that arrive through a report (`scripts/record.py:314`, `moved_tests` in a maker's or cleaner's report) carry no `to` or `deleted`, so they never update red. Only the CLI path does.
- `red.failure` and `red.watch_first_green` are not touched when a file moves. They are prose, so this may be fine.

## 1. Shape

shape_change: no. The boundary picture shows no new module, edge, outbound call, table or surface path, and no shape hints. The changes stay inside the current shape:
- `xv record move` gains `--to` and `--deleted` (`scripts/record.py:520-521`).
- The record gains a `slice_only` list field (`scripts/record.py:27,31`).

`.xv/picture.md:23` ("`record` owns the slice record") and `.xv/picture.md:27` (surfaces: the `xv` CLI, `skills/*/SKILL.md`) already cover all of these.

shape_breadth: narrow. The forecast said `wide` across four places. The diff reaches two of them (the brief, and the record and move code). It is narrower than forecast, not wider, because of finding A.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7-25`. The change keeps tests where an adopting team already looks for them, and keeps the red pointing at real files. That serves ".. to vibe with discipline" (`.xv/pitch.md:7`). Nothing in it serves people "that will not trust agents to write production code" (`.xv/pitch.md:25`). The pitch says nothing about test layout.

Binding decision 1 (`.xv/picture.md:59`): a brief change needs two people and a `CHANGELOG.md` line. The line is there (`CHANGELOG.md:7`, "Sean decided it, solo"), and the picture records `seats.two_people: solo` (`.xv/picture.md:51`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-27-slice-tests` reports changed, deleted, added and fewer_assertions all empty. The record's `moved_tests` is `[]`. `git diff 94cdf5f..HEAD -- tests/` shows only the new `tests/test_slice_tests.py`.

Slice-only tests in this slice: the scenario report named none, and the record has no `slice_only`. Under the new rule I would not mark any. `ScenarioBriefTest` guards the brief wording against regression, so it keeps value after the slice.

## 4. The picture

No edit proposed. I checked:
- `.xv/picture.md:23`: `record` owns the slice record. Still true.
- `.xv/picture.md:26`: state is files with front matter. A new field does not change that.
- `.xv/picture.md:27`: surfaces. No new ones.
- Names (`.xv/picture.md:30-38`): no new term. "Slice-only" is a record field, not a name the picture uses.

If finding A is built later and changes the cleaner's role or the `accept_moves` stop, `.xv/picture.md:23` and decision 10 (`.xv/picture.md:68`) should be re-read then.

## Door

**Door:** two-way. A revert removes the flags, the field and the brief line; no data is migrated, and old records simply lack `slice_only`. **Blast radius:** contained. The brief line does ship to adopters on the next release (`.xv/picture.md:25` covers `defaults/`; skills travel the same way).

## Raw data

- Slice record: `.xv/slices/2026-10-27-slice-tests.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..8c17baf`. The cleaner's rename (`mod` to `module_of`) is in `8c17baf`, although the cleaner reported it as uncommitted and `cleaner_commit` is null.
- Wall: `xv wall diff 2026-10-27-slice-tests`
- Boundary: `.xv/slices/2026-10-27-slice-tests.boundary.md` (`xv boundary --base 94cdf5f15f31`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- One brief line changes.

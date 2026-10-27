---
slice: 2026-10-27-slice-tests
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: Tests a slice leaves behind fit the layout and do not go stale

Nothing stops this for two people. This is the second pass. B and C from the first packet are built. Sean, as the person who set the work going, has three findings to decide on before merging:

- **E.** Slice-only removals will still raise the `accept_moves` stop. Nothing marks a move as slice-only.
- **F.** The cleaner brief's removal command drops a whole file from `red.files`, even when only one test was removed.
- **D.** Item D, moving the tests into `tests/test_record.py`, is not done.

The merge is yours.

## The scenario

From `.xv/slices/2026-10-27-slice-tests.md` (seanpk/xv-agents#17), with Sean's answers at both stops:

1. Step 6 of the scenario brief asks for new tests in the existing test file for the code under test. A new file is made only when none exists.
2. The scenario agent marks slice-only tests and reports them as `slice_only: [{"file", "test", "why"}]`. The record keeps that list.
3. `xv record move --to <path>` or `--deleted` updates `red.files` and `red.command`. Both module forms are covered: `tests.test_x` and the bare `test_x`. When the last red file is deleted, `red.files` is empty, `red.command` is null, and the log says why. The log says "updated" only when the command changed.
4. After green, the cleaner removes each slice-only test as a recorded move marked slice-only. There is no approval stop: those moves do not fire `accept_moves`. The packet lists the removals on one line, and names each kept test with the reason to keep it.

Also settled: (C) the report example shows `slice_only`, and (D) this slice's tests move into `tests/test_record.py` as a recorded move.

May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red, check out `1112e22` and run `cd tests && python3 -m unittest test_slice_tests`. It ran 12 tests with 6 failures (record, `checks.scenario.red_output`). At HEAD `99400d9`, I ran the same tests and all 12 pass. The whole suite was green for the maker and the cleaner: 210 tests (record, `checks.cleaner.suite`). I did not re-run the whole suite.

## The boundary picture

From `.xv/slices/2026-10-27-slice-tests.boundary.md`, as given:
- Touched: `scripts/record`.
- No modules, edges or outbound calls added or removed.
- No tables and no surface paths.
- Shape hints: none.

Outside the module graph, the diff touches:
- three briefs: `skills/scenario/SKILL.md`, `skills/cleaner/SKILL.md` and `skills/guardian/SKILL.md`;
- two lines of `CHANGELOG.md`.

## What the suite asserts after

`tests/test_slice_tests.py` is new in this slice and has 12 tests:
- **`--to`:** the move rewrites `red.files` and `red.command`, in both the `tests.test_x` form and the bare `test_x` form.
- **`--deleted`:** the move drops the file and its module from `red.files` and `red.command`, in both forms.
- **Last red file deleted:** `files` is `[]`, `command` is null, and the log names `red.command`.
- **A file red does not name:** moving it leaves red unchanged.
- **A command that names no module** (`make check`): the command is unchanged, and the log does not say "red.command updated".
- **The scenario report:** its `slice_only` list lands in the record.
- **The briefs:** step 6 says "existing test file" and no longer says "new files where you can". The report example contains `slice_only`. The cleaner brief contains `slice_only`, `slice-only` and `--deleted`. The guardian brief contains `slice-only`.

The brief tests are substring checks. They show that the words are present, not that the rule works. No test covers the `accept_moves` exemption, the slice-only marker, or the case where a slice-only test shares a file with other tests.

No old assertion moved.

## Findings for the person who set the work going

**E. Slice-only removals will still stop for approval.** Settled (4) says "So no approval stop … Those moves do not raise the `accept_moves` stop", and item (A) cites `scripts/orders.py:161-169`. That code is unchanged:
- `scripts/orders.py:159-167` reads `moved = data.get("moved_tests") or []`, then `if not out and (moved or picture):`, and fires `accept_moves` for any recorded move.
- The only slice-only marker is the prose prefix `--why "slice-only: <why>"` in `skills/cleaner/SKILL.md:39`.
- `scripts/record.py:174-175` stores `file`, `assertion`, `why`, `by` and `at`, with no marker field.

So the first time a cleaner follows the new brief, the slice stops for the originator. The maker and the scenario agent both say this is waiting for a decision: "marker undecided" and "untested until Sean says how a move is marked" (record log, 14:28 and 14:30). **Decide how a move is marked**, for example a `--slice-only` flag or the `why` prefix. Then send the slice back to the scenario agent.

**F. The cleaner's removal command drops a whole red file when only one test was removed.**
- `skills/cleaner/SKILL.md:39` tells the cleaner to remove one slice-only test with `xv record move <slice id> --file <file> --deleted --assertion "<the test>" …`.
- `--deleted` means "the file was removed" (`scripts/record.py:524`).
- `scripts/record.py:185-189` therefore removes `<file>` from `red.files` and its module from `red.command`.

New step 6 (`skills/scenario/SKILL.md:27`) puts new tests in the existing file. So a slice-only test will usually share a file with the slice's real red tests. Take `red.files: ["tests/test_record.py"]` and `red.command: "cd tests && python3 -m unittest test_record"`. Removing one slice-only test from that file leaves `red.files: []` and `red.command: null`, and the log says "no red file is left". That is the stale red the scenario exists to prevent ("so the guardian and the 'watch the first green run' line do not point at a deleted file", scenario (3)). **Decide** between two fixes:
- a separate way to record that one test was removed;
- a brief that uses `--deleted` only when the whole file goes.

**D. The tests did not move into `tests/test_record.py`.** Settled item (D) asks for it as a recorded move. The maker says "item D not done" (record log, 14:30). All 12 tests are still in a new file, `tests/test_slice_tests.py`, which is the opposite of new step 6 (`skills/scenario/SKILL.md:27`). `red.files` still names `tests/test_slice_tests.py`. Doing D would also be the first real use of `--to`. **Decide** whether to send this back or accept the new file.

Smaller points:
- **A misleading log line.** Take a red whose `command` is already null while other red files remain. A `--deleted` move logs "red.command is now null: no red file is left" (`scripts/record.py:186-189, 197-199`), but files are left. This is rare.
- **The packet template has no slice-only line.** `skills/guardian/packet.md` is unchanged and has no place for the slice-only line that `skills/guardian/SKILL.md:26` now asks for.
- **Report moves cannot update red.** A move that arrives through a report (`scripts/record.py:312-317`) has no `to` or `deleted`, so it never updates red. The cleaner brief uses the CLI, so this does not bite yet.

## 1. Shape

shape_change: no. The boundary picture shows no new module, edge, outbound call, table, surface path or shape hint. The changes stay inside the current shape:
- `xv record move` gains two flags (`scripts/record.py:523-524`).
- The record gains a `slice_only` list (`scripts/record.py:27, 31`).

The picture already covers all of this: "`record` owns the slice record" (`.xv/picture.md:23`), and the surfaces include "the `xv` CLI, `skills/*/SKILL.md`" (`.xv/picture.md:27`).

shape_breadth: narrow. The forecast said `wide`. The diff reaches `record.py` and three briefs. It does not reach `orders.py` (finding E) or the close output. Sean's answer at the scenario stop dropped the approval step. So the change is narrower than the forecast, not wider.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7-25`.
- Tests that stay where a team keeps them, and a red that points at real files, serve "to vibe with discipline" (`.xv/pitch.md:7`).
- Automatic removal of slice-only tests still trusts agents to change the test suite. It does not serve people "that will not trust agents to write production code" (`.xv/pitch.md:25`).

Binding decision 1 (`.xv/picture.md:59`) says a brief change needs two people and a `CHANGELOG.md` line. Both CHANGELOG lines are there (`CHANGELOG.md:7-8`, "Sean decided it, solo"), and `seats.two_people` is solo (`.xv/picture.md:51`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Where I looked:
- `git diff dcb0381..HEAD -- tests` (dcb0381 is the wall baseline): 63 lines added to `tests/test_slice_tests.py` and none removed.

Slice-only: none were removed and none were kept. The scenario agent marked none, and the record has no `slice_only` entries. One assertion fits the brief's own example of a slice-only check: `assertNotIn("new files where you can", step6)` (`tests/test_slice_tests.py:81`). It only proves that the old wording is gone. It sits inside a test whose other assertions guard the new wording, so I would keep the test.

## 4. The picture

No edit proposed. I checked these lines:
- `.xv/picture.md:23`: `record` owns the record, and `orders` holds the stop rules. Both are still true, because `orders.py` is untouched.
- `.xv/picture.md:26`: state is files with front matter. A new list field does not change that.
- `.xv/picture.md:27`: the surfaces. No new ones.
- `.xv/picture.md:30-38`: names. "Slice-only" is a record field and a brief term, not a name the picture uses.

If finding E is built in `orders.py`, re-read decision 10 (`.xv/picture.md:68`) then.

## Door

**Door:** two-way. A revert removes the flags, the field and the brief lines, and no data is migrated. **Blast radius:** adopters. The cleaner brief now tells every adopting repo's cleaner to delete tests after green (`skills/cleaner/SKILL.md:39`). Skills are a surface users meet (`.xv/picture.md:27`).

## Raw data

- Slice record: `.xv/slices/2026-10-27-slice-tests.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..99400d9` (working tree clean)
- Wall: `xv wall diff 2026-10-27-slice-tests`
- Boundary: `.xv/slices/2026-10-27-slice-tests.boundary.md` (`xv boundary --base 94cdf5f15f31`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- Three briefs change.
- `xv wall diff 2026-10-27-slice-tests`: changed, deleted, added and fewer_assertions are all empty.
- The record's `moved_tests`: `[]`.

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

Nothing stops this for two people. This is the third pass. E, F, D and G from the second stop are built, and so are A, B and C from the first. Sean, as the person who set the work going, has one finding to weigh before merging:

- **H.** Any agent can mark a move `--slice-only`. Nothing checks it against the record's `slice_only` list, so a move of a real old test that carries the flag skips the `accept_moves` stop.

The rest are small. The merge is yours.

## The scenario

From `.xv/slices/2026-10-27-slice-tests.md` (seanpk/xv-agents#17), with Sean's answers at all three stops:

1. Scenario brief step 6: new tests go in the existing test file for the code under test, and a new file is made only when none exists.
2. The scenario agent reports slice-only tests as `slice_only: [{"file", "test", "why"}]`, and the record keeps that list. The report example in the brief shows the field.
3. `xv record move --to <path>` / `--deleted` (the whole file is gone) updates `red.files` and `red.command`. It handles both module forms, `tests.test_x` and bare `test_x`. When the last red file is deleted, `red.files` is empty, `red.command` is null, and the log says why. The log says "updated" only when the command changed.
4. After green, the cleaner removes each slice-only test as a move recorded with `--slice-only`, unless it finds a reason to keep the test. Removing one test from a file that stays leaves `red` alone. Slice-only moves do not fire `accept_moves`, but any other move still does. The packet template lists the removed tests on one line and names each kept one with its reason.
5. (D) This slice's own tests live in `tests/test_record.py` and `tests/test_orders.py`.

May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red, check out `1c6f450` and run `cd tests && python3 -m unittest test_record test_orders`: 47 tests, 4 failures, the first `'accept_moves' != 'ready_to_merge'` (record, `checks.scenario.red_output`). At HEAD `20054fd` I ran the same command: 47 tests, OK. I also re-ran the whole suite with `cd tests && python3 -m unittest -q` (result below, under Raw data).

## The boundary picture

From `.xv/slices/2026-10-27-slice-tests.boundary.md`, as given:
- Touched: `scripts/orders`, `scripts/record`.
- No modules, edges or outbound calls added or removed.
- No tables and no surface paths.
- Shape hints: none.

Outside the module graph, the diff touches:
- three briefs: scenario, cleaner and guardian `SKILL.md`;
- the packet template `skills/guardian/packet.md`;
- three lines of `CHANGELOG.md`.

## What the suite asserts after

18 new tests, all in existing files:
- **`tests/test_orders.py` (3):**
  - Slice-only moves alone give `ready_to_merge`.
  - A slice-only move next to a plain move still gives `accept_moves`.
  - A slice-only move does not hide a picture change.
- **`tests/test_record.py`:**
  - **`--to`:** follows the file in `red.files` and `red.command`, in both module forms.
  - **`--deleted`:** drops the file, in both forms.
  - **Last red file deleted:** `files: []`, `command: null`, and the log names `red.command`.
  - **A file red does not name:** red is left alone.
  - **`make check`:** the command is unchanged, and the log does not say "red.command updated".
  - **The report's `slice_only`:** lands in the record.
  - **The `--slice-only` marker:** kept on the move; a plain move has none.
  - **Removing one slice-only test from a file that stays:** red is left alone.
  - **The briefs and template:** checked with substring tests (step 6 wording, `slice_only` in the report example, the cleaner's `slice_only` / `slice-only` / `--deleted`, the guardian's `slice-only`, the template's `slice-only`).

The brief and template tests show that the words are present, not that the rule works.

## Findings for the person who set the work going

**H. The slice-only exemption trusts the flag.**
- `scripts/record.py:174-176` stores `slice_only: True` for any move given `--slice-only`, without checking `--file` / `--assertion` against `data["slice_only"]`.
- `scripts/orders.py:159` then drops every such move from the `accept_moves` count: `moved = [m for m in data.get("moved_tests") or [] if not m.get("slice_only")]`.

So a cleaner or a maker that changes an old test can record the move with `--slice-only`, and the slice goes to `ready_to_merge` with no stop for that change. The guardian brief still lists every changed test (`skills/guardian/SKILL.md:26`), so the change shows in the packet, but nothing stops for it. The picture's rule is "Read-only agents are checked, not trusted" (`.xv/picture.md:70`). The cleaner is not read-only, so this does not break the rule; it is the same question for a writing agent. **Decide** whether to accept this as it stands or have `record move` refuse `--slice-only` for a file and test the record's `slice_only` does not name.

**Smaller points:**
- **D's move was not recorded.** Settled (D) asks for the move "as a recorded move with `--to`". The record shows `moved_tests: []` (`.xv/slices/2026-10-27-slice-tests.md:15`). The tests reached `tests/test_record.py` because the scenario re-reported red, not through `xv record move --to`. The file was new in this slice, so no old test moved and the wall is clean. The effect is that `--to` has still not been used on a real record.
- **pytest node ids are not followed.** `scripts/record.py:191, 196` match whole space-split tokens: the path, `tests.test_x`, or `test_x`. A red written as `python3 -m pytest tests/test_x.py::test_a` keeps the old path after `--to` or `--deleted`. pytest is the suite `xv init` picks for Python repos with `pyproject.toml` or `setup.py` (`scripts/run.py:686-687`). The scenario names only the path and module forms, so this is outside its scope.
- **A misleading log line.** If `red.command` is already null while other red files remain, a `--deleted` or `--to` move logs "red.command is now null: no red file is left" (`scripts/record.py:198-201`), even though files are left. This is rare. It was raised in the second packet and is unchanged.
- **A null command prints as `None`.** After the last red file is deleted, `red.command` is null (`scripts/record.py:191`). The prompt for later agents renders it with `red.get('command', '')` (`scripts/prompt.py:64`), which prints "command \`None\`".

## 1. Shape

shape_change: no. The boundary picture shows no new module, edge, outbound call, table, surface path or shape hint. The changes stay inside the current shape:
- `xv record move` gains three flags (`scripts/record.py:525-527`).
- The record gains a `slice_only` list (`scripts/record.py:27, 31`).
- One standing order narrows (`scripts/orders.py:159`).

The picture already covers all three: "`record` owns the slice record. `orders` holds the stop rules" (`.xv/picture.md:23`). The surfaces include "the `xv` CLI, `skills/*/SKILL.md`" (`.xv/picture.md:27`). The standing order stays in `orders.py` as a pure function of the record (`.xv/picture.md:68`).

shape_breadth: narrow. The forecast said `wide`. The diff reaches two scripts, three briefs and the template. It does not reach the close output, because Sean's answer at the scenario stop dropped the approval step. So the change is not wider than the forecast.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7-25`.
- Tests kept where the team keeps them, and a red that points at real files, serve "to vibe with discipline" (`.xv/pitch.md:7`).
- Removing slice-only tests automatically relies on trusting agents with the suite. That fits who the pitch is for and does not serve those "that will not trust agents to write production code" (`.xv/pitch.md:25`).

Binding decision 1 (`.xv/picture.md:59`) says a change to a brief or a standing order needs two people and a `CHANGELOG.md` line. All three lines are there (`CHANGELOG.md:7-9`, "Sean decided it, solo"), and the seat is solo (`.xv/picture.md:51`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Where I looked:
- `git diff 94cdf5f..HEAD -- tests`: only additions, plus `HOME` added to an import (`tests/test_record.py:5`), which changes no assertion.
- `tests/test_slice_tests.py`: added and removed inside the slice; see D above.

Slice-only tests removed: none. Kept: none. No scenario report in this slice named any (the record has no `slice_only` entries), so the cleaner removed nothing (record log, 15:28).

## 4. The picture

No edit proposed. I checked these lines:
- `.xv/picture.md:23`: `record` owns the record, and `orders` holds the stop rules. Both are still true.
- `.xv/picture.md:26`: state is files with front matter. A new list field does not change that.
- `.xv/picture.md:27`: the surfaces. No new ones; the flags sit on an existing command.
- `.xv/picture.md:30-38`: names. "Slice-only" joins "red" and "moved test", which the picture also leaves to the briefs.
- `.xv/picture.md:68`: decision 10. The exemption is in `orders.py`, as a pure function of the record.

## Door

**Door:** two-way. A revert removes the flags, the field, the exemption and the brief lines, and no data is migrated. **Blast radius:** adopters. Every adopting repo's cleaner is now told to delete tests after green (`skills/cleaner/SKILL.md:39`), with no stop for those deletions (`scripts/orders.py:159`).

## Raw data

- Slice record: `.xv/slices/2026-10-27-slice-tests.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..20054fd` (uncommitted: only the watch's boundary picture)
- Wall: `xv wall diff 2026-10-27-slice-tests`
- Boundary: `.xv/slices/2026-10-27-slice-tests.boundary.md` (`xv boundary --base 94cdf5f15f31`)
- Whole suite at HEAD: `cd tests && python3 -m unittest -q` exited 0 in my run. The cleaner's run: 216 tests, OK (record, `checks.cleaner.suite_output`).

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- `xv wall diff 2026-10-27-slice-tests`: changed, deleted, added and fewer_assertions are all empty.

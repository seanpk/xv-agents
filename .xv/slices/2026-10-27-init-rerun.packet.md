---
slice: 2026-10-27-init-rerun
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: init
---

# Packet: xv init runs again without crashing

Nothing needs two people. No old test moved and the picture needs no edit. The merge is up to the originator, Sean Kennedy.

## The scenario

You run `xv init` a second time in a repo that already has `.xv/config.yml`, to fill in a missing file. It should not crash. With `.xv/pitch.md` missing, the second run writes the starter pitch, keeps every existing file (config.yml unchanged, a custom picture.md untouched), prints its usual JSON and exits 0. Today it fails with `UnboundLocalError` on `runners`. (seanpk/xv-agents#40.) May ignore: nothing stated.

## The recording

There is no recording because the slice starts from words. To replay: `cd tests && python3 -m unittest test_init_rerun`.
- Before (base `94cdf5f`): fails. `scripts/run.py` line 919, `if len(runners) > 1:`, raises `UnboundLocalError` (output in the record, `checks.scenario.red_output`).
- After (HEAD `57c8865`): `Ran 1 test … OK`. I ran it in this pass. The watch reports the whole suite green: 199 tests at maker and at cleaner.

## The boundary picture

From `.xv/slices/2026-10-27-init-rerun.boundary.md`, as given:
- Touched: `scripts/run`. No modules added or removed. No new calls out of the process.
- Edges added: none. Edges removed: none.
- Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- New (`tests/test_init_rerun.py`, 7 assertions): run `xv init`, delete `pitch.md`, overwrite `picture.md`, then run `xv init` again. The second run exits 0 and its stdout is valid JSON. `pitch.md` exists again and is listed in `written`. `picture.md` keeps its content and is listed in `kept`. `config.yml` is byte-identical and is listed in `kept`.
- Old assertions: no old assertion changed. The other 41 wall files are unchanged since the baseline (`xv wall diff`: changed, deleted and added are all empty).

## 1. Shape

shape_change: no. shape_breadth: none (the forecast expected `narrow`, so this is not wider).
- The only production change is one line inside the existing `cmd_init` function: `scripts/run.py:891`, `+    runners = []`. It adds no module, layer, dependency, table, edge or surface. The boundary picture reports none of these and no shape hints.
- It sits inside the shape the picture describes: "`init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`" (`.xv/picture.md:22`). `xv init`'s own behaviour is unchanged when it writes config.yml (`.xv/picture.md:25`). The `if "config.yml" in written:` branch is untouched and still sets `runners` from `detect_tests`.
- Side effect to know about: on a rerun, `runners` stays `[]`, so the JSON never includes a `runners` key, even in a repo with several test runners (`scripts/run.py:919-920`, `if len(runners) > 1: out["runners"] = runners`). Before this change, the same rerun crashed. So this is not a lost behaviour, and it matches the scenario's "prints its usual JSON output". The test does not assert anything about `runners` or `test_run` on a rerun.

## 2. Pitch

pitch_contradiction: no.
- The change makes `xv init` usable again in a repo that has already adopted it. That serves "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`).
- It does nothing for someone the pitch excludes and does not touch "Who it is not for" (`.xv/pitch.md:25`).

## 3. Moved tests

None. The record has `moved_tests: []`. `xv wall diff 2026-10-27-init-rerun` reports `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []` against baseline `0336b80`, whose wall already counts `tests/test_init_rerun.py: 7`. The diff touches no file under `tests/` except the new red file (`git diff 94cdf5f..HEAD -- tests`).

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

## 4. The picture

No edit needed. The change makes no line of `.xv/picture.md` untrue:
- `.xv/picture.md:25` describes what `xv init` writes into `config.yml` and the allow list. Both still happen only on the first write.
- `.xv/picture.md:26` says `xv slice new` refuses a base without `config.yml`, `pitch.md` and `picture.md`. Rerunning `xv init` is now a working way to restore a missing one. The picture never said otherwise, so this is not a gap.

## Door

**Door:** two-way. Reverting the one line restores the old behaviour, and no data or contract changes. **Blast radius:** init.

## Raw data

- Slice record: `.xv/slices/2026-10-27-init-rerun.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..57c8865` (`scripts/run.py` +1, `tests/test_init_rerun.py` +38, plus record and wall files)
- Wall: `xv wall diff 2026-10-27-init-rerun`
- Boundary: `xv boundary --base 94cdf5f15f31c53d02fc8de787ce85889627e799` (saved at `.xv/slices/2026-10-27-init-rerun.boundary.md`)

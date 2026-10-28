---
shape_change: no
pitch_contradiction: no
door: two-way
---

# Packet: 2026-10-27-init-no-try

## Needs a decision

1. **Picture edit** (check 4): the picture does not mention `--no-try` or `test_run_skipped`. Proposed wording below. Yours to accept.
2. **Coverage gap carried from the last pass** (check 3): `tests/test_install.py:73` (`git status --porcelain` is empty after `xv init --trial`) now runs with `--no-try`. It no longer checks that the test try leaves the tree clean. It still passes. You decide whether a no_try = False case is needed.
3. **The xv-init skill**: `skills/xv-init/SKILL.md:32` reads a null `test_run` as "no command was guessed". With `--no-try`, `test_run` is absent and `test_run_skipped` is present (`scripts/run.py:1002-1005`). The skill does not mention the flag. That is harmless while only the suite passes `--no-try`. This pass adds the skipped note that your second stop asked for, so an agent can tell the two cases apart. Updating the skill is not in the slice.

## Scenario

Since #14, `xv init` runs the test command it guesses, once. That made the suite about 3× slower (#38). `xv init --no-try` skips that run. The test helpers pass the flag; `tests/test_init_tries.py` leaves it off, so the real try is still tested. Plain `xv init` is unchanged. Added at the second stop: the usage text names the flag, and with `--no-try` the output says that the try was skipped.

## Replay

No recording (feature). Red: `cd tests && python3 -m unittest test_init_tries`. I ran it here: 14 tests, OK, 19.3s. Whole suite: `cd tests && python3 -m unittest -q`. The maker reported 319 tests green, about 74s (it was about 130s). I did not re-run the whole suite. First green to watch: `xv init --no-try` prints a `test_run_skipped` note and runs no tests. Plain `xv init` reports `test_run` as before. `xv --help` shows `[--no-try]`.

## Boundary picture

From `.xv/slices/2026-10-27-init-no-try.boundary.md`: shape hints none; module touched `scripts/run`; modules added and removed: none; edges added and removed: none; nothing new calls out of the process.

## What the suite asserts after the change

- Without the flag, the test command runs (marker file written), and the output does not say "skip".
- With `--no-try`: the test command does not run (no marker, no failing tail), init exits 0, it still writes `config.yml`, `boundary-all.md` and `tests.timeout`, and the output contains "skip".
- `xv --help` and the docstring usage in `scripts/run.py` both name `--no-try` on the `xv init` line.
- Every other test that runs `xv init` through `RepoCase.xv` now gets `--no-try`.

## Moved tests

- `tests/helpers.py:24,43-46`: `RepoCase.xv` used to pass `init` through as given. Now it appends `--no-try` unless the class sets `no_try = False`. Recorded by Sean Kennedy and accepted at the second stop. The scenario forces it (the settled answer: "the slice is not done until the suite uses the flag"). No assertion text changed. Coverage is narrower only in `tests/test_install.py:73` (item 2 above).
- `xv wall diff 2026-10-27-init-no-try` against baseline b33b2f7: changed, deleted, added and fewer_assertions are all empty. Since the baseline, only `tests/test_init_tries.py` has new tests (the 3 red tests), and it sets `no_try = False`.

## The four checks

1. **Shape: no; breadth narrow, as forecast.** The boundary picture has no hints and no new edges or modules. The source change is one argparse flag (`scripts/run.py:1069-1070`), one branch in `cmd_init` (`scripts/run.py:1002-1005`), and two usage lines (`bin/xv:5`, `scripts/run.py:15`). It stays inside "`init` … land[s] in `run.py`" (`.xv/picture.md:22`). The forecast said narrow.
2. **Pitch: no.** The flag is a test-speed option for the suite. It does not touch "will not trust agents to write production code. It will never be a teapot." (`.xv/pitch.md:25`). The pitch says nothing about init's test try.
3. **Moved tests:** one, recorded and forced by the scenario (above). No test asserts less in its text. One test now covers less in effect (`tests/test_install.py:73`).
4. **The picture:** `.xv/picture.md:25` describes what `xv init` writes, and nothing describes the try or its opt-out. Proposed addition after line 25: "`xv init` runs the guessed test command once to check it (`test_run` in its output). `xv init --no-try` skips that and prints `test_run_skipped` instead. The suite's `RepoCase` passes `--no-try` by default; `tests/test_init_tries.py` opts out."

## The door

Two-way door: a revert removes the flag, the output key and the helper default, and no data or public contract outlives it (the new flag is additive). Blast radius: small.

## Raw data

- Diff: `git diff 8f9cdbee89d7193e0d5c675f4feabe11871a821d..HEAD` (bin/xv, scripts/run.py, tests/helpers.py, tests/test_init_tries.py)
- Boundary: `.xv/slices/2026-10-27-init-no-try.boundary.md`
- Wall: `.xv/slices/2026-10-27-init-no-try.wall.json`, `xv wall diff 2026-10-27-init-no-try`
- Record: `.xv/slices/2026-10-27-init-no-try.md`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- Slice-only: none (`slice_only: []`).

## From the cleaner

- Shape proposal, for people: Make the suite's shared xv init helper pass --no-try, with test_init_tries calling init bare, so the suite gets the speed-up the scenario asks for; it changes test call sites and needs a person's decision on how to tell the bare-init calls apart.

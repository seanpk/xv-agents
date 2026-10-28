---
shape_change: no
pitch_contradiction: no
door: two-way
---

# Packet: 2026-10-27-init-no-try

## Needs a decision

1. **Picture edit** (check 4): the picture does not mention `--no-try` or `test_run_skipped`. The proposed wording is below. It is yours to accept.
2. **Coverage gap** (check 3): `tests/test_install.py:72-73` runs `self.xv("init", "--trial")` and asserts that `git status --porcelain` is empty. Through `RepoCase.xv`, this now gets `--no-try` (`tests/helpers.py:43-46`). So it no longer checks that the test try leaves the tree clean. It still passes. You decide whether that needs a `no_try = False` case.
3. **The xv-init skill**: `skills/xv-init/SKILL.md:32` says "If `test_run` is null, no command was guessed: ask the person for one." With `--no-try`, `test_run` is absent and `test_run_skipped` is present (`scripts/run.py:1002-1005`). The skill does not mention either one. Because of the skipped note, an agent can tell the two cases apart, but the skill does not tell it to. Changing the skill is not in the slice.

## Scenario

Since #14, `xv init` runs the test command it guesses, once, and that made the suite about 3× slower (#38). `xv init --no-try` skips that run. The test helpers pass the flag. `tests/test_init_tries.py` leaves it off, so the real try is still tested. Plain `xv init` is unchanged. Added at the second stop: the usage text names the flag, and with `--no-try` the output says the try was skipped.

## Replay

There is no recording (this is a feature). Red: `cd tests && python3 -m unittest test_init_tries`. I ran it here: 14 tests, OK, 19.3s. Whole suite: `cd tests && python3 -m unittest -q`. The maker and the cleaner recorded 319 tests green in 76.2s and 75.3s (record `checks.maker` and `checks.cleaner`; it was about 130s). I did not re-run the whole suite.

First green to watch:
- `xv init --no-try` prints `test_run_skipped` and runs no tests.
- Plain `xv init` reports `test_run` as before.
- `xv --help` shows `[--no-try]`.

## Boundary picture

From `.xv/slices/2026-10-27-init-no-try.boundary.md` (lines 5-19 and 118-128, `shape_hints: []` at line 394):
- Module touched: `scripts/run`.
- Modules added or removed: none.
- Edges added or removed: none.
- Outbound calls added: none.

## What the suite asserts after the change

- Without the flag, the test command runs (a marker file is written), and the output does not say "skip".
- With `--no-try`:
  - init exits 0;
  - the test command does not run: no marker file, and no failing test's output;
  - it still writes `config.yml`, `boundary-all.md` and `tests.timeout`;
  - the output contains "skip".
- `xv --help` and the usage text at the top of `scripts/run.py` both name `--no-try` on the `xv init` line.
- Every other test that runs `xv init` through `RepoCase.xv` now gets `--no-try`. `git grep` finds no test that calls `xv init` directly with `sh(...)`, outside the helper.

## Moved tests

- `tests/helpers.py:24,43-46`: `RepoCase.xv` used to pass `init` on as given. Now it adds `--no-try` unless the class sets `no_try = False`. Sean Kennedy recorded this move (record `moved_tests`) and accepted it at the second stop. The scenario forces it: "the slice is not done until the suite uses the flag" (record, Scenario, second paragraph). No assertion text changed. Coverage is narrower only in `tests/test_install.py:73` (item 2 above).
- `xv wall diff 2026-10-27-init-no-try` against baseline b33b2f7: `changed`, `deleted`, `added` and `fewer_assertions` are all empty. The new tests are the 7 in `tests/test_init_tries.py:40-79`, and that class sets `no_try = False` (`tests/test_init_tries.py:14`).
- Slice-only: none (`.xv/slices/2026-10-27-init-no-try.md:16`, `slice_only: []`).

## The four checks

1. **Shape: no. Breadth: narrow, as forecast** (record `forecast.shape: narrow`). There are no shape hints and no new edges or modules (boundary, line 394). The source change:
   - one argparse flag (`scripts/run.py:1069-1070`);
   - one branch in `cmd_init` (`scripts/run.py:1002-1005`);
   - two usage lines (`bin/xv:5`, `scripts/run.py:15`).

   The change stays inside "`init` … all land in `run.py`" (`.xv/picture.md:22`).
2. **Pitch: no.** The flag only skips a check, and the suite is what uses it. It does not touch "not for people or projects that will not trust agents to write production code. It will never be a teapot." (`.xv/pitch.md:25`). The pitch says nothing about init's test try.
3. **Moved tests: one.** It is recorded and the scenario forces it (see above). No test's text asserts less. One test covers less in effect (`tests/test_install.py:73`).
4. **The picture: yes.** `.xv/picture.md:25` says what `xv init` writes, and nothing in the picture describes the try or a way to skip it. Proposed addition after line 25: "`xv init` runs the guessed test command once to check it (`test_run` in its output). `xv init --no-try` skips that and prints `test_run_skipped` instead. The suite's `RepoCase` passes `--no-try` by default; `tests/test_init_tries.py` opts out."

## The door

Two-way door: a revert removes the flag, the output key and the helper default. No data outlives it, and the flag only adds to the public contract (`scripts/run.py:1069-1070`). Blast radius: small.

## Raw data

- Diff: `git diff 8f9cdbee89d7193e0d5c675f4feabe11871a821d..HEAD` (bin/xv, scripts/run.py, tests/helpers.py, tests/test_init_tries.py)
- Boundary: `.xv/slices/2026-10-27-init-no-try.boundary.md`
- Wall: `.xv/slices/2026-10-27-init-no-try.wall.json`, `xv wall diff 2026-10-27-init-no-try`
- Record: `.xv/slices/2026-10-27-init-no-try.md`

## From the cleaner

- Shape proposal, for people: Make the suite's shared xv init helper pass --no-try, with test_init_tries calling init bare, so the suite gets the speed-up the scenario asks for; it changes test call sites and needs a person's decision on how to tell the bare-init calls apart.

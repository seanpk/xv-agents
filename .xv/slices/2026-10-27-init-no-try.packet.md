---
shape_change: no
pitch_contradiction: no
door: two-way
---

# Packet: 2026-10-27-init-no-try

## Needs a decision

1. **The picture edit you accepted has not been written.** You accepted it at the second and third stops (record, Scenario, paragraphs 3 and 4). `.xv/picture.md` still says nothing about init's test try or `--no-try`: a search for `try` and `test_run` finds no match in it. The wording is in check 4 below. Someone other than the guardian has to write it before the merge, or after it as a follow-up.
2. **The moved test is recorded twice.** `.xv/slices/2026-10-27-init-no-try.md:15` has two `moved_tests` entries for the one change to `tests/test_install.py`, at 04:17:30 and at 04:20:12, with the same reason. The change is one line (`tests/test_install.py:72`). Counting it once, two old tests moved, not three.

The third stop's ask is done. `tests/test_install.py:72` sets `self.no_try = False` before `self.xv("init", "--trial")`. So the `git status --porcelain` check now covers the test try again. That was the coverage gap in the last packet.

## Scenario

Since #14, `xv init` runs the test command it guesses, once, to check it. That made the suite about 3× slower (#38).

- `xv init --no-try` skips that run, and its output says the run was skipped.
- The usage lines name the new flag.
- Plain `xv init` works as before.
- The suite's `RepoCase` helper passes `--no-try`. The tests that check the try opt out: `tests/test_init_tries.py`, and the trial clean-tree test in `tests/test_install.py`.
- The xv-init skill stays as it is (third stop).

## Replay

There is no recording (this is a feature).

- Red: `cd tests && python3 -m unittest test_init_tries`. I ran it here with `test_install`: 17 tests, OK, 26.0s.
- Whole suite: `cd tests && python3 -m unittest -q`. The maker recorded 319 tests green (log, 04:20:12; it took about 130s before the change and about 74–76s after). I did not re-run the whole suite.

First green to watch:
- `xv init --no-try` prints `test_run_skipped` and runs no tests.
- Plain `xv init` reports `test_run` as before.
- `xv --help` and the docstring of `scripts/run.py` show `[--no-try]` on the `xv init` line.

## Boundary picture

From `.xv/slices/2026-10-27-init-no-try.boundary.md`:
- Shape hints: none.
- Module touched: `scripts/run`.
- Modules added or removed: none.
- Edges added or removed: none.
- Outbound calls added: none.
- Tables and surface paths: none.

## What the suite asserts after the change

- Without the flag:
  - the test command runs (a marker file is written);
  - the output does not say "skip".
- With `--no-try`:
  - init exits 0;
  - the test command does not run: no marker file, and no failing test's output;
  - init still writes `config.yml`, `boundary-all.md` and `tests.timeout`;
  - the output says "skip".
- `xv --help` and the docstring of `scripts/run.py` name `--no-try` on the `xv init` line.
- `xv init --trial` with the try on leaves `git status --porcelain` empty (`tests/test_install.py:72-74`).
- Every other test that runs `xv init` through `RepoCase.xv` now gets `--no-try`: `test_init.py`, `test_init_allow_list*.py`, `test_init_rerun.py`, and `test_install.py:94`. No test calls `xv init` with `sh(...)` outside the helper. `test_init_timeout.py` calls `try_test_command` directly, so the helper does not touch it.

## Moved tests

- `tests/helpers.py:24,43-46`, recorded by Sean Kennedy (record `moved_tests`, first entry). Before, `RepoCase.xv` passed `init` on as given. After, it adds `--no-try` unless `no_try` is False. The scenario forces it: "the slice is not done until the suite uses the flag" (record, Scenario, paragraph 2). No assertion text changed. Sean accepted it at the second stop.
- `tests/test_install.py:72`, recorded by the maker, twice (item 2 above). Before, the test ran `init --trial` through the helper, which since this slice adds `--no-try`. After, it sets `self.no_try = False` first. The third stop forces it: the test "runs with the test try on". It asserts no less than it did at the base. `xv wall diff`: 21 assertions before, 21 after, `fewer_assertions: []`.
- `xv wall diff 2026-10-27-init-no-try` (baseline 1549b95): `changed: [tests/test_install.py]`, `deleted` and `added` empty. The helper move and the 7 new tests in `tests/test_init_tries.py:40-79` came before that baseline, so the wall diff does not list them. The record covers the helper move, and the new tests are additions.
- Slice-only: none (`.xv/slices/2026-10-27-init-no-try.md:16`, `slice_only: []`).

## The four checks

1. **Shape: no. Breadth: narrow, as forecast** (record `forecast.shape: narrow`). The boundary picture has no shape hints and no new edges or modules. The source change:
   - one argparse flag (`scripts/run.py:1069-1070`);
   - one branch in `cmd_init` (`scripts/run.py:1002-1005`);
   - two usage lines (`bin/xv:5`, `scripts/run.py:15`).

   It stays inside "`init` … all land in `run.py`" (`.xv/picture.md:22`). In the tests, the spread is the one the forecast named: the helper plus the call sites that opt out.
2. **Pitch: no.** The flag only skips a check, and the suite is what uses it. It does not touch "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). The pitch says nothing about init's test try.
3. **Moved tests: two.** Both are recorded, both are forced by the scenario, and neither asserts less. One of them is recorded twice.
4. **The picture: yes.** `.xv/picture.md:25` says what `xv init` writes. Nothing in the picture describes the try or a way to skip it. Proposed addition after line 25: "`xv init` runs the guessed test command once to check it (`test_run` in its output). `xv init --no-try` skips that and prints `test_run_skipped` instead. The suite's `RepoCase` passes `--no-try` by default; tests that check the try set `no_try = False`."

## The door

Two-way door: a revert removes the flag, the output key and the helper default. No data outlives it, and the flag only adds to the CLI (`scripts/run.py:1069-1070`). Blast radius: small.

## Raw data

- Diff: `git diff 8f9cdbee89d7193e0d5c675f4feabe11871a821d..HEAD -- bin scripts tests`
- Boundary: `.xv/slices/2026-10-27-init-no-try.boundary.md`
- Wall: `.xv/slices/2026-10-27-init-no-try.wall.json`, `xv wall diff 2026-10-27-init-no-try`
- Record: `.xv/slices/2026-10-27-init-no-try.md`

## From the cleaner

- Shape proposal, for people: Make the suite's shared xv init helper pass --no-try, with test_init_tries calling init bare, so the suite gets the speed-up the scenario asks for; it changes test call sites and needs a person's decision on how to tell the bare-init calls apart.

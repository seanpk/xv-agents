---
slice: 2026-10-27-init-no-try
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: The suite skips xv init's test try where no test needs it

**Needs a decision (Sean, the originator):** the slice delivers only half the scenario. `xv init --no-try` exists, but no test helper or call site passes it, so the suite runs no faster than before: 316 tests in 129.9s after the maker and 129.7s after the cleaner (record, `checks.maker.suite_output` and `checks.cleaner.suite_output`), against the "about 130 seconds" the scenario starts from. The maker and the cleaner both left this open. Sean decides whether to send it back to the maker to change the call sites (which widens the slice past the forecast) or to accept it as it is and open a follow-up slice.

## The scenario

From `.xv/slices/2026-10-27-init-no-try.md:34`: "After the change, `xv init --no-try` does not run the test command. The test helpers pass `--no-try`, and the tests in `tests/test_init_tries.py` leave it off, so the real try is still tested. Without the flag, `xv init` works as it does today." The goal is the suite speed-up of #38. May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_init_tries`. At `6d20d52` (red) it fails 3 tests with `xv: error: unrecognized arguments: --no-try`. At HEAD it runs 11 tests and all pass (re-run by the guardian, 17.1s).

## The boundary picture

From `.xv/slices/2026-10-27-init-no-try.boundary.md`, as given: the only module touched is `scripts/run`. No modules or edges were added or removed, nothing new calls out of the process, no tables or surface paths were added or removed, and there are no shape hints.

## What the suite asserts after

- Without the flag, `xv init` still runs the test command: a sentinel test writes a marker file (`tests/test_init_tries.py:37-40`).
- With `--no-try`, init exits 0 and the marker is never written (`:42-46`).
- With `--no-try`, init still writes `config.yml` and `boundary-all.md` and reports `tests.timeout` (`:48-52`).
- With `--no-try` on a failing suite, the failure text does not appear in init's output (`:54-61`).
- No old assertion changed.

## 1. Shape

shape_change: no. shape_breadth: narrow, which is what the forecast expected.

- `scripts/run.py:1067-1068` adds one flag, `--no-try`, to the existing `xv init` command. `.xv/picture.md` (The shape, "Surfaces: the `xv` CLI, ...") already lists the CLI as a surface, and `.xv/picture.md` ("`init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`") places init in `run.py`. The flag stays inside the current shape. The boundary picture shows no new edge, module or surface path.
- Breadth. The forecast said that if the call sites change, the slice widens (record line 11, `breadth`). The call sites did not change, so the slice is narrow. But finishing the scenario would widen it: `tests/helpers.py` has no init helper, only a generic `xv()`. Bare `self.xv("init")` calls sit in seven other files: `tests/test_init.py:20,33,40,54`, `tests/test_init_allow_list.py:48,57,68,81,88`, `tests/test_init_allow_list_bare.py:39`, `tests/test_init_allow_list_split.py:48`, `tests/test_init_allow_list_prompt.py:45,69`, `tests/test_init_rerun.py:19,25` and `tests/test_install.py:72`. If the slice is sent back, expect a wider test diff than forecast. Whether that needs two people goes to Sean.

## 2. Pitch

pitch_contradiction: no. The pitch says xv-agents makes it "easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`). An opt-in flag that skips init's check changes nothing about whom the system serves or what it will never do (`.xv/pitch.md:25`). The default behaviour is unchanged (`scripts/run.py:1002-1003`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-27-init-no-try` reports nothing changed, deleted or added, and no file with fewer assertions. The record has `moved_tests: []`. The only test file in the diff is `tests/test_init_tries.py`, and its hunk at `@@ -25,6 +25,41 @@` only adds lines.

Slice-only tests removed: none. Kept: none.

## 4. The picture

`.xv/picture.md` (The shape) does not say that `xv init` runs the chosen test command once under `tests.timeout` and reports `test_run`. That gap predates this slice. With `--no-try`, the try becomes optional, and the picture is less complete without it. Proposed edit, after the sentence "`xv init` also writes a starter Claude Code `--allowedTools` list ...": "`xv init` then runs the chosen test command once, under `tests.timeout`, and reports the result as `test_run`; `xv init --no-try` skips the run and leaves `test_run` out of its output."

## Other findings

- **The usage text leaves out the new flag.** `bin/xv:5` and `scripts/run.py:15` still read `xv init [--trial [--repo]|--adopt]`. Only `xv init -h` shows `--no-try` (`scripts/run.py:1067-1068`). This makes the "Surfaces: the `xv` CLI" line in `.xv/picture.md` incomplete for anyone who reads the usage text.
- **`test_run` is left out rather than set to null.** `scripts/run.py:1002-1003` leaves `test_run` out of the output when `--no-try` is set. `skills/xv-init/SKILL.md:32` reads "If `test_run` is null, no command was guessed: ask the person for one". An agent that runs `--no-try` and reads a missing key as null would wrongly ask for a test command. The brief does not mention `--no-try` today, so nothing hits this yet. No test pins what an agent should read when the try was skipped: `tests/test_init_tries.py:48-52` does not assert on `test_run`.

## Door

**Door:** two-way. A revert removes one flag that is off by default and changes no data, migration or published output. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-27-init-no-try.md`
- Diff: `git diff 8f9cdbee89d7193e0d5c675f4feabe11871a821d..a121290`
- Wall: `xv wall diff 2026-10-27-init-no-try`
- Boundary: `.xv/slices/2026-10-27-init-no-try.boundary.md` (`xv boundary --base 8f9cdbee89d7`)

## From the cleaner

- Shape proposal, for people: Make the suite's shared xv init helper pass --no-try, with test_init_tries calling init bare, so the suite gets the speed-up the scenario asks for; it changes test call sites and needs a person's decision on how to tell the bare-init calls apart.

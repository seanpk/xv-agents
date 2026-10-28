---
slice: 2026-10-27-init-no-try
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: small
---

# Packet: The suite skips xv init's test try where no test needs it

**Needs a decision (Sean, the originator):** accept the one recorded move in `tests/helpers.py` and the proposed edit to the picture, or send them back. Neither stops the change for two people. Since the last packet, the scenario is complete: the shared helper passes `--no-try`, and the suite went from about 130s to about 74s for 316 tests. The merge is yours.

## The scenario

From `.xv/slices/2026-10-27-init-no-try.md`, Scenario: "After the change, `xv init --no-try` does not run the test command. The test helpers pass `--no-try`, and the tests in `tests/test_init_tries.py` leave it off, so the real try is still tested. Without the flag, `xv init` works as it does today." At the earlier guardian stop, Sean settled that "the slice is not done until the suite uses the flag ... The packet reports the suite time before and after." May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_init_tries`. At `6d20d52` it fails 3 tests with `xv: error: unrecognized arguments: --no-try`. At HEAD it passes all 11 tests (record, `checks.scenario.red_output`).

Suite time, before and after: 316 tests ran in 129.9s after the first maker pass, when no helper passed the flag (the earlier packet, from `checks.maker.suite_output`). They ran in 73.7s after this maker pass and 73.6s after this cleaner pass (record, `checks.maker.suite_output` and `checks.cleaner.suite_output`). The guardian re-ran `cd tests && python3 -m unittest -q` at HEAD: `Ran 316 tests in 74.048s`, `OK`.

## The boundary picture

From `.xv/slices/2026-10-27-init-no-try.boundary.md`, as given: the only module touched is `scripts/run`. No modules or edges were added or removed, nothing new calls out of the process, no tables or surface paths were added or removed, and there are no shape hints.

## What the suite asserts after

- Without the flag, `xv init` still runs the test command: a sentinel test writes a marker file (`tests/test_init_tries.py:39-42`).
- With `--no-try`, init exits 0 and never writes the marker (`:44-48`). It still writes `config.yml` and `boundary-all.md` and reports `tests.timeout` (`:50-54`). It does not print a failing suite's output (`:56-63`).
- Every other `RepoCase` test now calls `xv init --no-try` through the helper (`tests/helpers.py:24,43-46`). `InitTriesGuessesTest` opts out (`tests/test_init_tries.py:13`), so its pass, fail and module-count checks still run the real try.
- No assertion text changed, and no assertion count changed (`xv wall diff`: `fewer_assertions: []`).

## 1. Shape

shape_change: no. shape_breadth: narrow, as the forecast expected.

- `scripts/run.py:1067-1068` adds one flag to the existing `xv init`. `.xv/picture.md:22` places `init` in `run.py`, and `.xv/picture.md:27` lists "the `xv` CLI" as a surface. The flag stays inside that surface. The boundary picture shows no new module, edge or surface path.
- Breadth. The forecast said that if the call sites changed, the slice would widen (record, `forecast.breadth`). They did not. The change stays in the shared helper (`tests/helpers.py:43-46`) plus one class attribute (`tests/test_init_tries.py:13`). The bare `self.xv("init")` calls in seven other test files are untouched.

## 2. Pitch

pitch_contradiction: no. The pitch says xv-agents makes it "easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`). An opt-in flag, plus a faster suite for the people who work on xv-agents, touches neither whom it serves nor "It will never be a teapot" (`.xv/pitch.md:25`). Default `xv init` is unchanged (`scripts/run.py:1002-1003`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/helpers.py:24,43-46` | `RepoCase.xv` passed its args to `xv` unchanged. Every `xv init` from a test ran the real try. | When the class has `no_try = True` (the default), it appends `--no-try` to any call whose first arg is `init`. `test_init_tries.py:13` sets `no_try = False`. | "The test helpers pass --no-try so the suite skips init's test try; tests/test_init_tries.py sets no_try = False so the real try is still tested. No assertion changed." (Sean Kennedy, 2026-10-28T03:12:16) | Yes. The scenario names it: "The test helpers pass `--no-try`, and the tests in `tests/test_init_tries.py` leave it off." |

- **The test that now covers less.** `tests/test_install.py:72-73` runs `self.xv("init", "--trial")` and asserts that `git status --porcelain` is empty. Before, that init ran the fixture's test command, so this assertion also caught a try that left files in a trial repo. Now the helper adds `--no-try`, and nothing in the suite checks that the try leaves the tree clean. No assertion text changed; what the assertion covers did. `InitTriesGuessesTest` runs the try but never checks `git status`.
- **The wall did not see the move.** `xv wall diff` reports nothing changed. The red commit `c908f0b` re-took the baseline, with new hashes for `tests/helpers.py` and `tests/test_init_tries.py` in `.xv/slices/2026-10-27-init-no-try.wall.json`. The watch's `old_red_changed` check caught the change instead (record, stop `unrecorded_move`), and Sean recorded the move.
- The `test_init_tries.py` hunk only adds lines (`no_try = False` and four new tests). No old test in it moved.

Slice-only tests removed: none. Kept: none.

## 4. The picture

- `.xv/picture.md:25` describes what `xv init` writes, but not that it then runs the chosen test command once under `tests.timeout` and reports `test_run`. That gap predates this slice. The last packet proposed filling it, and the picture still lacks it. With `--no-try`, the try is now optional. Proposed edit, after the `--allowedTools` sentence on line 25: "`xv init` then runs the chosen test command once, under `tests.timeout`, and reports the result as `test_run`; `xv init --no-try` skips the run and leaves `test_run` out. The suite's `RepoCase` passes `--no-try` by default; tests that check the try set `no_try = False`."

## Other findings (carried from the last packet, still true at HEAD)

- **The usage text leaves out the flag.** `bin/xv:5` and `scripts/run.py:15` still read `xv init [--trial [--repo]|--adopt]`. Only `xv init -h` shows `--no-try` (`scripts/run.py:1067-1068`). Under `.xv/picture.md:27` ("Surfaces: the `xv` CLI"), the usage text is part of that surface, and it is now incomplete.
- **`test_run` is left out, not set to null.** With `--no-try`, `scripts/run.py:1002-1003` leaves `test_run` out of the output. `skills/xv-init/SKILL.md:32` reads "If `test_run` is null, no command was guessed: ask the person for one." An agent that ran `--no-try` and read the missing key as null would ask for a test command it doesn't need. `tests/test_init_tries.py:50-54` does not assert on `test_run`.

## Door

**Door:** two-way. A revert removes one flag that is off by default and one test-helper default. No data, migration or published output changes. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-27-init-no-try.md`
- Diff: `git diff 8f9cdbee89d7193e0d5c675f4feabe11871a821d..3ba8253`
- Wall: `xv wall diff 2026-10-27-init-no-try` (baseline re-taken at `c908f0b`; see Moved tests)
- Boundary: `.xv/slices/2026-10-27-init-no-try.boundary.md` (`xv boundary --base 8f9cdbee89d7`)

## From the cleaner

- Shape proposal, for people: Make the suite's shared xv init helper pass --no-try, with test_init_tries calling init bare, so the suite gets the speed-up the scenario asks for; it changes test call sites and needs a person's decision on how to tell the bare-init calls apart.

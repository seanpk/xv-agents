---
slice: 2026-10-25-init-tries-guesses
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: init
---

# Packet: xv init tries its guessed test command and roots

Nothing here needs two people. The four orders Sean gave at the last merge stop are all in the diff. The merge is Sean's. Two small findings are for Sean:

1. **The CHANGELOG line and the may-not list do not match.** The CHANGELOG says "`xv-init` gained a may-not line" (`CHANGELOG.md:8`). The new prohibition, "do not fix it yourself", sits inline at `skills/xv-init/SKILL.md:32`. The brief's `## May not` list (`skills/xv-init/SKILL.md:115-121`) is unchanged. Decision 13 says every brief "ends with its may-not list" (`.xv/picture.md:70`). Either add the line to that list or leave it inline. The CHANGELOG wording is the one Sean dictated (record, Scenario, order 4).
2. **The CHANGELOG line names only the may-not line.** The same brief also gained instructions for `test_run`, `modules` and `fixture_folders` (`skills/xv-init/SKILL.md:32,34`). The CHANGELOG opens with "Every change to a brief" (`CHANGELOG.md:3`). The #13 line next to it does describe its brief change (`CHANGELOG.md:7`).

## The scenario

`xv init` runs the test command it chose once, with a time limit. Its output says whether the command passed, failed (with the last lines of its output), or timed out. The output also gives the number of modules in `.xv/boundary-all.md` and lists the folders that look like fixtures and hold code. The skill tells the person about each. (#14)

Sean settled four points at the 2026-10-26 merge stop:

1. The fixture scan uses git's file list, so ignored folders are never listed. Add a test with an ignored folder.
2. Put `tests.timeout` back in the output, and narrow the pass assertion to `test_run`.
3. The skill covers a null `test_run` and warns about the run time.
4. Add a CHANGELOG line.

May ignore: fixing a failed command automatically.

## The recording

This is a feature, so there is no recording. To replay:

- Red at `51f0321`, green at `HEAD` (`0ec9693`): `cd tests && python3 -m unittest test_init_tries`. The guardian ran it at `HEAD`: 7 tests, OK.
- The record's red failure: `'.venv' unexpectedly found in '{ ... "fixture_folders": [".venv/examples", "examples"] }'`, and `'timeout' not found in {'paths': ..., 'command': ..., 'file_command': ''}`.
- The cleaner's whole-suite run: 133 tests, OK (record, `checks.cleaner`).
- No test covers the timed-out outcome. The scenario names no way to shorten the limit (`tests/test_init_tries.py:83-86`).

## The boundary picture

From `.xv/slices/2026-10-25-init-tries-guesses.boundary.md`, as given:

- **Modules touched:** `scripts/run`. None added or removed.
- **Edges:** none added, none removed. **Outbound added:** none.
- **Tables:** none. **Surface paths:** none added, none removed.
- **Shape hints:** none.

## What the suite asserts after

All 7 tests are in `tests/test_init_tries.py`. The file is new against base `f452d43`.

- **A passing command:** the output's `test_run` says pass, and says neither fail nor timed out (`:28-31`).
- **The timeout:** the output's `tests` still has a `timeout` key (`:33-34`).
- **A failing command:** one broken test makes `xv init` report the failure. Init still exits 0, the output says fail, and the tail carries the failing test's marker text (`:36-45`).
- **The module count:** the output gives a number next to "module". It equals the count of `- ` lines in `.xv/boundary-all.md` (`:47-52`).
- **Fixture folders:** `examples/` and `fixtures/` with `.py` files are named. `setups/` with only a `.txt` is not (`:54-64`).
- **An ignored folder:** a git-ignored `.venv/examples/lib.py` is not listed, and a tracked `examples/` still is (`:66-73`).
- **No fixture folders:** a repo without them names none (`:75-77`).

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`"shape": "narrow"`, record front matter).

  - The new import is `scripts/run.py:711` `from xvlib import tracked_files`. It uses the existing `run` → `xvlib` edge.
  - The test run calls `shell` (`scripts/run.py:728`), which already backs `run_suite` (`scripts/run.py:43-57`).
  - "`init` ... all land in `run.py`" (`.xv/picture.md:22`) still holds.
- **The fixture scan now matches the boundary's view.** `scripts/run.py:713` `for path in tracked_files(root):` reads `git ls-files -z --cached --others --exclude-standard` (`scripts/xvlib.py:322`). Last round's `os.walk` is gone.
- **Surfaces:** the JSON from `xv init` gains `test_run`, `modules` and `fixture_folders`, and `tests` is printed whole again (`scripts/run.py:797-802`). The skill text changes at `skills/xv-init/SKILL.md:32,34`. Both are existing surfaces, "the `xv` CLI, `skills/*/SKILL.md`" (`.xv/picture.md:27`).
- **`defaults/`** is untouched (`.xv/picture.md:25`).

## 2. Pitch

pitch_contradiction: no.

"xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`). Checking the guessed command and roots at init serves that. Nothing in the diff touches who it is for (`.xv/pitch.md:21`) or what it will never do (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_init_tries.py:28-31` | `assertNotRegex(<whole output>, r"fail\|timed out\|timeout")` | `assertNotRegex(<test_run only>, r"fail\|timed out")` | Sean's order 2 at the merge stop: "Narrow the assertion ... to the test-run outcome, not the whole output" (record, Scenario). The scenario agent made the change in red `51f0321`, not the maker. | Yes. It asserts less on purpose. The broad version forced `tests.timeout` out of the output in the last round. |

  - `.xv/slices/2026-10-25-init-tries-guesses.wall.json:43` is `fdc9e9e0…`, the same hash as the file at `HEAD`.
  - The file at `e3d4b25`, the baseline's `commit` field (`wall.json:30`), hashes to `c1bf0848…`.

## 4. The picture

No edit proposed. What I checked:

- The module count and layout (`.xv/picture.md:21-23`): no module was added.
- Outbound calls (`.xv/picture.md:24`): none added.
- `defaults/` (`.xv/picture.md:25`): untouched.
- Surfaces (`.xv/picture.md:27`): the same set.
- Names, users and the decisions that bind (`.xv/picture.md:13-17, 30-37, 55-74`): none made untrue.

Decision 1 (`.xv/picture.md:58`) is met. The brief change carries a CHANGELOG line, and "two people" is `solo` for this repo (`.xv/picture.md:50`).

## Door

**Door:** two-way. A revert removes the three output fields, the skill text and the CHANGELOG line. No data is migrated and nothing is sent to users. **Blast radius:** init.

## Raw data

- Slice record: `.xv/slices/2026-10-25-init-tries-guesses.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`. The code is in `scripts/run.py`, `skills/xv-init/SKILL.md`, `tests/test_init_tries.py` and `CHANGELOG.md`.
- Wall: `xv wall diff 2026-10-25-init-tries-guesses` (baseline `.xv/slices/2026-10-25-init-tries-guesses.wall.json`)
- Boundary: `.xv/slices/2026-10-25-init-tries-guesses.boundary.md` (`xv boundary --base f452d430f44f`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- Modules, edges and outbound calls:** only `scripts/run` is touched, and nothing is added (boundary picture).
- The diff's 772 lines (record, `diff_history`)** are mostly the slice's own files: the boundary, the packet, the record and the wall. Code, skill, tests and CHANGELOG come to about 130 lines (`git diff --stat`).
- This is the only change to a test. It is a test this slice wrote in its first round, not an old test from `main`. That is why the record has `moved_tests: []`.
- `xv wall diff` will not show it, because the wall's hash for the file is the post-red one:
- The maker's and cleaner's wall checks show `changed: []` and `fewer_assertions: []` (record, `checks`).
- The guardian could not run `xv wall diff` itself; the command needed approval.

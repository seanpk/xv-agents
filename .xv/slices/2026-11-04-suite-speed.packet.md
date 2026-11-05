---
slice: 2026-11-04-suite-speed
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 4
door: two-way
blast_radius: contributors
---

# Packet: The test suite runs each test once, in parallel (#131)

No stop for two people. Sean has three things to decide as the person who set the work going: the picture edit (check 4), one wall recommendation (check 5), and whether the agents' allow-list change in `.xv/config.yml` needs its own CHANGELOG words (check 4, under decision 1). After that, the merge is Sean's.

## The scenario

1. The suite command in `.xv/config.yml` runs every test once. No test runs again because its class inherits from another test class.
2. `python3 tests/run.py --shard i/n --jobs k`: shards 1/n to n/n together run every test once. `--jobs k` runs k processes at the same time. The runner exits non-zero on a failure, and `xv` reads the failing tests from its output as it does now.
3. `.xv/config.yml` runs the suite through the runner, with `--jobs`.
4. The `tests` CI workflow runs shards as a matrix on both Pythons, at the same time.
5. The maker and cleaner briefs say: run narrow while you work, and the whole suite once before the report.
6. The tests use only the standard library.

May ignore: a time target, pytest and other runners, adopters' suite commands, the suite run after the maker and cleaner, and making slow tests faster.

## The recording

None (a feature). To replay:
- Red/green: `cd tests && python3 -m unittest -q test_suite_runner`. At the base it fails (record `red.failure`); now it passes: `Ran 13 tests ... OK`.
- The record's watch-first-green: `python3 tests/run.py --shard 1/3 --jobs 2`, then 2/3 and 3/3. My run: 225 + 225 + 224 = 674 tests, all OK. That matches `Ran 674 tests in shard 1/1` from `python3 tests/run.py --jobs 4`, which ran four processes of 169/169/168/168 tests side by side, about 60 s each.

## The boundary picture

From `.xv/slices/2026-11-04-suite-speed.boundary.md`, as given: no shape hints; no modules touched, added or removed; no edges added or removed; no new outbound calls; no tables; no surface paths added or removed. The 23-module graph is the same before and after.

## What the suite asserts after

- New, `tests/test_suite_runner.py`, `RunnerTest`: against a small suite of its own, the runner runs every test once for 1/1, for 3 shards, and for `--jobs 3`. Each of 2 shards gets some tests. Two jobs really overlap (each test waits for the other's marker). A failure gives a non-zero exit, in the shard that has it. The failure prints as `FAIL: test_five (test_b.TestBCase.test_five)`, and a green run prints no `FAIL:`/`ERROR:` line.
- `NoRerunTest`: across the real `tests/`, no test id is collected twice, and no collected test method comes from a base test class.
- `WiringTest`: the CI workflow has no `max-parallel: 1` and no `needs:`, and every `tests/*.py` imports only the standard library or local modules.
- Moved: three base classes now hold setup only (`WatchLoopSetup`, `BudgetCapSetup`), so their subclasses no longer run the base's tests a second time. Assertion counts are unchanged (`xv wall diff`: 251/251, 11/11, 86/86).
- Point 2, "the same as it does now": `xv` reads failures from the last 4000 characters of the suite output (`scripts/run.py:48`, `(p.stdout + p.stderr)[-4000:]`; read at `scripts/run.py:466-469`). The runner prints each process's output in turn (`tests/run.py:62-66`), so the `FAIL:` lines from an earlier process come before the output of the later ones. On a green run each process printed 26–517 bytes (my `--jobs 4` run, 873 bytes in all). So the window keeps nearly what it kept before. This is an observation, not a miss.

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast expected wide; narrower does not stop).
- The boundary picture has no hints and no new edges (`.xv/slices/2026-11-04-suite-speed.boundary.md`, "Shape hints: none", "Edges: added: none").
- `tests/run.py` is new, but it is test tooling under `tests/`, not one of the 23 modules (`.xv/picture.md:21`). It imports only `argparse, os, subprocess, sys, tempfile, unittest` (`tests/run.py:7-12`).
- `.github/workflows/tests.yml:17` adds `shard: [1, 2, 3, 4]` and `:27` runs `python tests/run.py --shard ${{ matrix.shard }}/4 --jobs 2`. That workflow is already a listed surface (`.xv/picture.md:27`, "`.github/workflows/` (tests, weekly drift check)"). It changes inside the surface, not into a new one.
- `.xv/config.yml:22` `command: "python3 tests/run.py --jobs 4"` changes a value, not the shape. `defaults/config.yml` is not touched, so adopters are not reached (`.xv/picture.md:25`, "A change there reaches every new adopter").

## 2. Pitch

pitch_contradiction: no. The pitch is "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`). It excludes "people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). This change is internal to the repo's own suite and CI, and serves no one new. I looked at `.xv/pitch.md:7-25` and found nothing it contradicts.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_run.py:82-103, 814, 923, 974` | `AcceptedShapeChangeTest`, `EveryPathOneVerdictTest`, `PreStepBudgetStopTest` subclass `WatchLoopTest`, so each re-ran its tests | they subclass `WatchLoopSetup` (setUp and `record`, no tests); `WatchLoopTest(WatchLoopSetup)` keeps every test | "no test runs again through inheritance" | Yes, point 1. Named in `old_tests_forced`. 251/251 assertions. |
| `tests/test_budget_cap.py:21-63` | `BudgetCapTest` holds setUp, helpers and tests | `BudgetCapSetup` holds setUp and helpers; `BudgetCapTest(BudgetCapSetup)` holds the tests | the importing module re-collected `BudgetCapTest` | Yes, point 1. 11/11. |
| `tests/test_budget_cap_turns_session.py:9-12, 51` | `TurnsAndSessionTest`, `PrototypeBudgetsTest` subclass `BudgetCapTest`, imported by name | they subclass `BudgetCapSetup` | the red report names this file | Yes, point 1. Named in `old_tests_forced`. 86/86. See the flag below. |
| `tests/test_suite_runner.py` (cleaner) | 4 `WiringTest` text checks | removed | slice-only, accepted by Sean | Slice-only (`slice_only_marks`, pick 1). 32 → 20 assertions are the 4 removed tests. |

- Flag: `PrototypeBudgetsTest.setUp` (`tests/test_budget_cap_turns_session.py:54-60`) adds a prototype slice `p1` before its tests run. Before this change, `BudgetCapTest`'s whole-slice budget tests also ran a second time with `p1` present. That second run is gone. The scenario forces it (point 1), and no test file asserts less. But "the slice budget ignores a prototype slice next to it" is now checked only by `PrototypeBudgetsTest`'s own tests.
- Not moved, and correctly so: `old_tests_forced` named `tests/test_prototypes.py` `PrototypesGitSetupTest`. That class already sets the inherited test to `None` (`tests/test_prototypes.py:106`, `test_three_prototypes_side_by_side_then_a_pick_by_two_people = None  # not rerun here`), so it re-runs nothing, and `NoRerunTest` passes.
- Allowed may-not file (`may_not_files`): `tests/run.py`, new under the `tests/**` wall. It is the runner, not a test.
- `.xv/config.yml` (protected): the maker's edit was reverted (`d750b64`). The same suite line was committed as Sean's (`af17f45`), per the `no_report` answer.

Slice-only tests removed: `WiringTest.test_the_maker_and_cleaner_briefs_say_run_narrow_while_working_and_the_suite_once`, `WiringTest.test_the_config_suite_command_runs_the_runner_with_jobs`, `WiringTest.test_ci_runs_the_suite_in_shards_as_a_matrix_on_both_pythons`, `WiringTest.test_ci_does_not_run_the_whole_suite_unsharded`. Kept: none.

## 4. The picture

picture_change: yes (incomplete, nothing made untrue).
- `.xv/picture.md:21-27` (The shape) does not say how the repo's own suite runs. Proposed edit, after line 25: "This repo's suite runs through `tests/run.py --shard i/n --jobs k` (standard library; unittest output, one process per job, each printed in turn). `.xv/config.yml` runs `--jobs 4`. The `tests` workflow runs four shards on each Python, eight jobs at once. No test class that holds tests is the base of another, and `tests/test_suite_runner.py` `NoRerunTest` guards this."
- `.xv/picture.md:25` already says the allow list goes stale when the test command changes. This slice hit that: commit `2cd3be8` adds `Bash(python3 tests/run.py:*)` to the default and guardian lines by hand (`.xv/config.yml:34, 36`). No edit is needed; optionally cite `2cd3be8` as the example.
- Decision 1 (`.xv/picture.md:63`, "A change to a brief, a may-not list, ... needs two people and a line in `CHANGELOG.md`"). The brief changes (`skills/maker/SKILL.md:25`, `skills/cleaner/SKILL.md:37`) have their CHANGELOG line (`CHANGELOG.md:7`, "Decided by Sean, solo"; solo per `.xv/picture.md:55`). The allow-list widening for the maker, cleaner and guardian (`.xv/config.yml:34, 36`, commit `2cd3be8`) is not mentioned in that line. Sean decides whether an agent's allow list counts as "a may-not list". I do not count it as a miss, because the decision names may-not lists, not allow lists.
- Decisions 3 and 15 still hold. The runner is standard library only (`tests/run.py:7-12`). CI keeps `python: ["3.10", "3.13"]` (`.github/workflows/tests.yml:16`), and `sys.stdlib_module_names` (`tests/test_suite_runner.py:194`) exists from 3.10.

## 5. The wall

- `tests/test_suite_runner.py`, `WiringTest.test_ci_shards_run_at_the_same_time` (`:188-191`): mark it slice-only, so it should not join the wall. It checks CI workflow text only (`assertNotRegex(wf, r"max-parallel:\s*1\b")`, `assertNotIn("needs:", wf)`), and it also passes on the base workflow, which had neither. It is the same kind of check as the four Sean marked, and his answer settled that kind: "one-time text checks on briefs, config and CI stay off the wall" (record `stops[1].cause`).
- I looked at `RunnerTest`, `NoRerunTest` and `WiringTest.test_the_tests_import_only_the_standard_library`. They guard lasting behaviour (points 1, 2 and 6), so I leave them as they are. No test on the wall is made dead.

## Door

**Door:** two-way. A revert restores `cd tests && python3 -m unittest -q`, the single-job CI and the old class bases. No data, no public contract, nothing sent. **Blast radius:** contributors.

## Raw data

- Slice record: `.xv/slices/2026-11-04-suite-speed.md`
- Diff: `git diff 168693608141b7cca549d5e56eebd4a61e9bd3fb..106a443`
- Wall: `xv wall diff 2026-11-04-suite-speed`
- Boundary: `xv boundary --base 168693608141b7cca549d5e56eebd4a61e9bd3fb` (`.xv/slices/2026-11-04-suite-speed.boundary.md`)

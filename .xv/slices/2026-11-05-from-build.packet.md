---
slice: 2026-11-05-from-build
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A slice can start from a build that already exists: #113

This is the second guardian pass. No stop for two people. The slice goes back to the scenario agent on two misses. Points 12 and 14 hold when the second scenario pass comes before the maker. They break when it comes after the maker, and the red tests only the first case. That second case is how this slice itself came back to the scenario agent. Sean also decides three things:
- (A) The Opus scenario line is still in `.xv/config.yml`.
- (B) A session-mode scenario step leaves a checkout behind, and nothing lands the red written in it.
- (C) The record says the slice-only CHANGELOG test was removed, but it is back on HEAD.

## Scenario misses

- 12: A second scenario pass after the maker does not start at "the base with the red from the earlier passes". It applies `git diff <build> HEAD` to the base, and after the maker that diff holds the maker's source changes too. The maker usually edits files the build changed ("The maker starts from the build", point 7), so `git apply` fails. That raises `CalledProcessError`, which `main` does not catch (`scripts/run.py:1298` catches only `XVError`), so the step exits 1, not 2 (decision 11, `.xv/picture.md:74`), and leaves the scratch worktree behind (`scripts/run.py:702`). If the patch applies, the red's "must fail on the base" run (point 6) holds the maker's fix. `SecondScenarioPassTest` amends before the maker (`tests/test_from_build.py:312-320`). Read from the code, not run. (evidence: `scripts/run.py:778-781`: `earlier = … ["git", "diff", "--binary", build_commit(root, data), "HEAD", …]` then `["git", "apply", "--index", "-"] … check=True`; to: scenario)
- 14: After the maker, the unshared record copy still names a commit at the build. The copy drops only `build` and `branch` (`scripts/run.py:783`: `copy = dict(data, build="none", branch=data["base"])`). It keeps `pre_maker_commit`, which is the slice HEAD before the maker, the build plus the red (`scripts/run.py:848-849`). This slice's own record shows the field (`pre_maker_commit: d0aa00a…`). `RecordCopyTest.test_a_second_pass_copy_names_no_branch_or_commit_at_the_build` amends before the maker, so the field is not yet set when it runs. (evidence: `scripts/run.py:783`, `scripts/run.py:848-849`; to: scenario)

## The scenario

`xv slice new --from <ref>` opens a slice whose branch starts at a build that already exists. `base` stays the branch the slice merges into. The record says `build: {kind: exploration, ref}`, or `build: none` without `--from`.

By default the scenario agent writes the red at the base without the build (`build_shared: no`). `--share-build` names the build to it as a reference only, and needs `--from` (11). The red must fail on the base and then runs on the build. A failing test goes to the maker as a miss. If the whole red passes on the build, the slice goes to the cleaner.

The `xv-slice` and `watch` skills offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line.

Amendments 12-15:
- 12: a second pass starts at the base with the earlier red and lands without a conflict.
- 13: tests for `red_conflicts_with_build`, and for a build's test-file change stopping once.
- 14: the unshared record copy names no branch or commit at the build.
- 15: a session scenario step makes the base checkout and names it.

May ignore: a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

None; a feature starts from words. Replay: `cd tests && python3 -m unittest test_from_build`. On HEAD 36 tests pass, run by the guardian. The second red at `30c7653` failed 35 of 36 (record `checks.scenario.red_output`). Whole suite on HEAD: `python3 tests/run.py --jobs 4`, 828 tests, OK (run by the guardian). To see it by hand, follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

## What the suite asserts after

- **Flags:** `--from` starts the branch at the build and keeps `base`. A missing ref, an empty `--from` and a bare `--from` are each refused. `--share-build` without `--from` is refused and leaves no worktree, record or branch.
- **Where the scenario agent works:** without `--share-build` it runs in a checkout at the base. Its prompt names neither the build branch nor its sha. On the first pass and on a pre-maker second pass, its record copy names neither the branch nor a commit at the build. With `--share-build`, its prompt names the build as "reference only".
- **Where the slice goes:**
  - A red that passes on the base stops with `scenario_not_red`.
  - A red that fails on the build goes to the maker with no stop, and the maker's prompt names the failing tests.
  - A red that passes on the build sets `next: cleaner`, and the maker never runs.
- **New (12, 13, 15):**
  - A second pass before the maker sees the earlier red and lands on the slice branch with the build intact.
  - A red file that the build also adds stops with `red_conflicts_with_build`, and leaves the worktree clean.
  - A build's change to `tests/test_store.py` stops exactly once as `unrecorded_move` across scenario → maker → cleaner.
  - A session scenario step names a git checkout at the base with no build in it.
- **Skill wording:** the skill texts carry the offer.
- Old assertions that moved: none.

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast said wide).

- The boundary picture (`.xv/slices/2026-11-05-from-build.boundary.md`, Modules and Edges sections) lists no new module, edge, table, surface path or outbound call, and no shape hints.
- `build` and `build_shared` are fields in the existing slice file (`scripts/record.py:28`), and slice state already lives there (`.xv/picture.md:27`, "State is files: `.xv/slices/<id>.md`").
- `--from` and `--share-build` are flags on the existing `xv` CLI surface (`.xv/picture.md:28`).
- The scratch worktree at the base (`scripts/run.py:767`) follows the existing temporary detached worktree for the red check (`.xv/picture.md:27`). It is not a new layer.
- `red_conflicts_with_build` is raised in `scripts/orders.py:133-137` from what the record says failed (`cherry_pick_conflict`, `scripts/run.py:894`), as decision 10 allows (`.xv/picture.md:73`).

## 2. Pitch

pitch_contradiction: no.
- The pitch says "to vibe with discipline" (`.xv/pitch.md:7`). A slice from a build still writes its red without the build and requires it to fail on the base (`scripts/run.py:794-800`, `land_scratch` runs the red in the base checkout).
- The change serves no one that "Who it is not for" (`.xv/pitch.md:23`) excludes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `ChangelogTest.test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`: 5 assertions | Removed by the cleaner at `5721237`, then written again by the second scenario pass at `30c7653`; present on HEAD at `tests/test_from_build.py:467-477` | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | Not forced. A slice-only mark Sean accepted (`slice_only[0].accepted: true`) |

Slice-only tests removed: none on HEAD. The record's `moved_tests` says `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes` was removed, but it is back (`tests/test_from_build.py:467`), and the second cleaner pass left it. Kept: the same test, with no reason given to keep it.

- `xv wall diff` against the new baseline `30c7653` (record `wall_baseline.commit`) lists no changed, deleted or added file. That is why it does not show the re-added test (`tests/test_from_build.py:467`).
- `tests/fake_agent.py` only gains probes: `FAKE_CWD_LOG`, and `FAKE_RECORD_LOG` at `tests/fake_agent.py:37-41`. It removes nothing.
- `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`).

### For Sean

**A. The Opus scenario line is still in the diff.** `.xv/config.yml:35`: "# Slice F only, as Sean directed: the wide-slice test. Removed before the PR." Line 36 sets `scenario` to `"--model", "opus"`. At the `accept_moves` stop the record says "The Opus scenario line is removed before the PR". If it merges, every later scenario step in this repo runs on Opus.

**B. A session-mode scenario step leaks a checkout, and nothing lands the red written there.**
- `scripts/run.py:696` calls `scenario_scratch` inside the error message and then raises. Nothing calls `drop_scratch`, so every `xv step scenario` adds another `git worktree` under the temp dir.
- The person then writes the red in that checkout. `xv record report` and `xv orders --after scenario`, the commands the message names, do not cherry-pick it, run it on the base, or run it on the build. Only `land_scratch` does that (`scripts/run.py:794`), and only on the CLI path.
- `skills/watch/SKILL.md:62` says the red "must fail there; then it runs on the build" with no session caveat.
- Point 15 asks only that the checkout is made and named (`.xv/slices/2026-11-05-from-build.md:60`), so this is not a miss.

**C. The slice-only CHANGELOG test is on HEAD while the record says it was removed.** See section 3. The record and the diff disagree on this one test. Everything else agrees.

**D. Fixed since the first packet.**
- 1a, a second pass before the maker: `scripts/run.py:778-782`.
- 1b, tests for the new stop and for stopping once: `BuildConflictTest` (`tests/test_from_build.py:339-364`).
- 1d, the record copy's `branch`: `scripts/run.py:783`.
- 1e, the session-mode checkout: `scripts/run.py:696`.

1d and 1a are only partly fixed; see the two misses.

## 4. The picture

- `.xv/picture.md:27`, after "The branch starts from `--base`, else …": add "With `xv slice new --from <ref>` the branch starts at the build and `base` stays the merge target. The record holds `build` (`none`, or `{kind: exploration, ref}`) and `build_shared` (`yes`/`no`). `--share-build` needs `--from`."
- `.xv/picture.md:27`, the scenario-step sentences: add the following.
  - In a slice from a build, the scenario agent runs in a temporary detached worktree at the base, with the slice's earlier red applied (`scripts/run.py:767-782`).
  - It reads a record copy with `build: none` and `branch` set to the base, unless the build is shared (`scripts/run.py:783`).
  - The red runs there and the wall baseline is hashed there. The red commit is then cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build` for the originator (`scripts/run.py:794-816`, `scripts/orders.py:133-137`).
  - The red then runs on the build. Its failing tests go to `checks.scenario.red_on_build`, and `prompt` names them to the maker (`scripts/run.py:894-897`, `scripts/prompt.py:116-120`).
  - A session scenario step makes that checkout and names it in its message (`scripts/run.py:694-698`).
- `.xv/picture.md:27`, "After the maker, a scenario step checks the red in a temporary detached worktree at `pre_maker_commit`": add "except in a slice from a build, where the red runs in the scratch checkout at the base".
- `.xv/picture.md:23`, after "`orders.verdict` also returns `next`": add "after the scenario step, `next_step` returns `cleaner` when the red failed on the base and passes on the build (`scripts/orders.py:362-364`)."
- `.xv/picture.md:27`, the `unrecorded_move` sentence: add "In a slice from a build, a test file the build changed stops once. After an answered `unrecorded_move` stop names it, it is not listed again while it is as the build left it (`scripts/run.py:1192-1199`)."
- `## Names`: add "An exploration is a build made with an agent outside XV. A slice opens from it with `--from`, and the build is that ref."

## 5. The wall

- `tests/test_from_build.py` `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`: it should stay marked slice-only and off the wall. It checks one CHANGELOG line (`tests/test_from_build.py:467-477`; record `slice_only[0]`, accepted). It is back in the file after the cleaner removed it (`5721237`).

I also checked every other new test class in `tests/test_from_build.py` against points 1-15. Each guards a lasting flag, record field, routing rule or skill wording, so I recommend no other change. No test that was on the wall before this slice is made dead: `xv wall diff` lists no changed old test file.

## Door

**Door:** two-way. The change adds flags and two record fields with defaults, and migrates or deletes no data. A revert undoes it. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..20b84bc`; since the first packet, `git diff 5721237..20b84bc`
- Wall: `xv wall diff 2026-11-05-from-build`
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md` (`xv boundary --base 5d5e75fc7a73`)

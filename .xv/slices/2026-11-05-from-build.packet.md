---
slice: 2026-11-05-from-build
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A slice can start from a build that already exists: #113

This is the seventh guardian pass. Nothing stops for two people, and no scenario miss is open. The merge is Sean's.

Last pass's miss on point 13 is closed. The build's stop-once filter moved from `run` into `record` as `record.wall_for_build`. `xv record report` now calls it (`scripts/record.py:763-764`), and so does `xv step` (`scripts/run.py:1038`). A new red drives the session path, and it passes.

For Sean, still open from last pass:
- **A.** There are still two `#113` lines in the CHANGELOG (`CHANGELOG.md:13-14`).
- **B.** The red ref is never deleted.

One new item, read from the code and not run:
- **C.** If the build ref is gone, `xv record report` fails before it writes the wall check.

## The scenario

- **Opening the slice:** `xv slice new --from <ref>` starts the branch at the build, and `base` stays the merge target. The record holds `build` and `build_shared`. `--share-build` names the build to the scenario agent as a reference only, and is refused without `--from` (points 1, 4, 5, 11).
- **Running the red:** the scenario agent writes the red at the base, without the build. The red must fail on the base, then runs on the build.
  - A test that fails on the build goes to the maker as a miss, with no stop.
  - A red that passes on the build skips the maker (points 6-8).
- **The rest:** the skills write the scenario from what runs, and offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line (points 2, 3, 9, 10).
- **Amendments 12-15:**
  - A later pass starts at the base with the earlier red, and lands cleanly. Sean narrowed this to no rebase, and a rebase that finishes; `--abort` is #147.
  - `red_conflicts_with_build` is tested. A test file the build changed stops once.
  - The unshared copy names no commit at the build.
  - A session scenario step makes the base checkout and names it.
- **Sean's settled rules:**
  - The red lives on `refs/xv/<id>/red`, and `xv slice rebase` moves it or stops with `rebase_red_ref`.
  - The copy keeps no commit that is off the base.
- **May ignore:** a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

There is none: a feature starts from words.
- **Replay:** `cd tests && python3 -m unittest test_from_build`. I ran it on HEAD `f46c685`: "Ran 54 tests in 51.671s / OK".
- **Whole suite:** `python3 tests/run.py --jobs 4`. 1012 tests, OK, exit 0 (see "Suite run").
- **The red's failure** before the maker: "2 != 1 : the build's change to tests/test_store.py did not stop exactly once on the session path" (`.xv/slices/2026-11-05-from-build.md:13`).
- **By hand:** follow the record's `watch_first_green` (`.xv/slices/2026-11-05-from-build.md:13`). Run it once with `agents.maker: session`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`, base `52ffb8b`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Edges, outbound calls and tables: none added, none removed (`:9-19`).
- One shape hint: "a surface path was added or removed" (`:5-7`).

## What the suite asserts after

`tests/test_from_build.py` is new, with 54 tests:
- `xv slice new --from`: the branch, `base`, the record fields, and the refusals.
- The scenario agent runs at the base. Its prompt names the build only when the build is shared.
- The red runs on the base, then on the build. The slice goes to the maker with the misses named, or to the cleaner.
- A second pass starts from the red ref and lands cleanly. This holds after the maker, when the red edits a file the build changed, and after a rebase. A rebase that cannot move the ref stops and names it.
- `red_conflicts_with_build` fires. A test file the build changed stops once:
  - on the `xv step` path;
  - on the session path, through `xv record report` and `xv orders`. This one is new on this pass (`tests/test_from_build.py:674-701`).
- The record copy names no commit off the base. A session scenario step names its checkout. The skill wording is tested.

No old assertion changed. `tests/fake_agent.py` only gains fakes (see 3).

## 1. Shape

shape_change: no. shape_breadth: narrow; the forecast expected wide (`.xv/slices/2026-11-05-from-build.md:11`).

- **The hint "a surface path was added or removed":** it does not change the shape. The path is `/red`, the tail of the git ref `refs/xv/<id>/red` (`scripts/run.py:549`, `:907`). It is not a surface that users meet.
- **This pass's move:** `has_build`, `build_commit` and `wall_for_build` moved from `run` into `record` (`scripts/record.py:724-741`). `run` already reaches `record` (`.xv/picture.md:21`), and `record` adds only the stdlib `subprocess` (`scripts/record.py:15`). The boundary shows no edge added (`.xv/slices/2026-11-05-from-build.boundary.md:16-17`).
- **The new stops** are in `orders.py` (`scripts/orders.py:133-137`, `:189-192`). The new `next` rule is there too (`:375-378`). This holds decision 10 (`.xv/picture.md:74`).

## 2. Pitch

pitch_contradiction: no.
- "to vibe with discipline" (`.xv/pitch.md:7`): the red is still written without the build, and it must fail on the base. The build only changes where the maker starts (`scripts/prompt.py:116-120`).
- Nothing serves someone named in "Who it is not for" (`.xv/pitch.md:23-25`).

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes` | Removed | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | No. It is a slice-only mark Sean accepted (`.xv/slices/2026-11-05-from-build.md:16`). |
| tests/fake_agent.py | No `FAKE_CWD_LOG`, `FAKE_RECORD_LOG`, `FAKE_RED_ADDS_TO_OLD` or `FAKE_CLEANER_COMMITS` | The four fakes are added, and no line is removed | Sean Kennedy: "F's own red commits added these fakes; only lines added." (`.xv/slices/2026-11-05-from-build.md:15`) | Yes. The red uses each fake, and nothing asserts less. |

Slice-only tests removed: `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

- `xv wall diff 2026-11-05-from-build`, against the baseline `199b583`, shows nothing changed, deleted or added, and `fewer_assertions: []`. The baseline is the record's `wall_baseline` (`.xv/slices/2026-11-05-from-build.md:14`).
- This pass's red only adds a test (`git diff 5effbd4..HEAD -- tests/test_from_build.py`: `@@ -671,6 +671,35 @@`).
- `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`). No may-not file was allowed.

### For Sean

**A. Two `#113` lines in the CHANGELOG** (`CHANGELOG.md:13` and `CHANGELOG.md:14`). This is unchanged from last pass. Line 13 is the stale line that the rebase brought back, and it names only "New stop: `red_conflicts_with_build`". Line 14 is the line Sean directed, which also names `rebase_red_ref`. Decision 1 is met by line 14 (`.xv/picture.md:65`). Line 13 is a duplicate, and no test catches it, because the CHANGELOG test is slice-only and was removed.

**B. The red ref is never deleted.** It is written at `scripts/run.py:549` and `:907`, and no code runs `update-ref -d` (`grep -n update-ref scripts/*.py`). This is unchanged.

**C. The build ref is resolved at report time** (read from the code, not run). `record.wall_for_build` calls `build_commit`, and that calls `git rev-parse <build ref>^{commit}` (`scripts/record.py:728-729`, `:737`). The ref is resolved each time a test file is unrecorded, not stored at open.
- **What happens:** a person may delete the exploration branch after the slice opens. Then `xv record report` raises `XVError` from `xvlib.run` (`scripts/xvlib.py:276-277`). That happens after the report is saved (`scripts/record.py:757`) but before the wall check is saved (`:763-765`). So the record has the report and no wall result for that agent.
- **Where it applies:** `xv step` uses the same call (`scripts/run.py:1038`). Decision 12 says such a check "stops for a person; it never passes" (`.xv/picture.md:76`).
- **Scope:** points 1-15 and "May ignore" (`.xv/slices/2026-11-05-from-build.md:40-64`) say nothing about a build ref deleted after the slice opens, so this is not a miss.

## 4. The picture

`.xv/picture.md` is not in the diff. These edits carry over from last pass, with this pass's name changes:
- **`.xv/picture.md:27`, "The branch starts from `--base`, else …":** add "`--from <ref>` starts it at a build instead; `base` stays the branch it merges into, and the record holds `build: {kind: exploration, ref}` and `build_shared`." Also add a ref per slice, `refs/xv/<id>/red`, that holds the red at the base.
- **`.xv/picture.md:27`, the scenario step:** add "On a slice from a build, the scenario agent runs in a temporary worktree at the red ref's tip, or at the base. Its record copy names no commit off the base unless the build is shared. The red runs there, and the wall is hashed there. The red is cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build`. Then the red runs on the build, and the maker's prompt names the tests that fail" (`scripts/prompt.py:116-120`).
- **`.xv/picture.md:23`, `next`:** "after a scenario step whose red passes on the build, `next` is `cleaner`" (`scripts/orders.py:375-378`).
- **`.xv/picture.md:23`, "After `rebase`, `orders` decides …":** add `rebase_red_ref`, and "`xv slice rebase` moves `refs/xv/<id>/red` onto the new base, and stops when it cannot" (`scripts/orders.py:189-192`).
- **`.xv/picture.md:23`, "`xv record report` for the maker and the cleaner runs the expected-move and wall checks":** add "On a slice from a build, a test file the build changed stops once, on this path and on `xv step` (`record.wall_for_build`)" (`scripts/record.py:732-741`).
- **`.xv/picture.md:23`, "`record` owns the slice record":** add "and the build rules: `has_build`, `build_commit`, `wall_for_build`."

## 5. The wall

No recommendations. I looked at:
- **`xv wall diff`:** nothing changed since the baseline `199b583`, so no test that was on the wall is made dead.
- **The new session-path test** (`tests/test_from_build.py:674-701`): it drives `xv record report` and `xv orders`. Its sibling (`:647-673`) drives `xv step`. These are two code paths (`scripts/record.py:763`, `scripts/run.py:1038`), so it does not restate the sibling, and it stays on the wall.
- **The `SliceSkillTest` wording tests:** they stay on the wall: "a test of a brief sentence that matches a code rule stays on the wall" (`.xv/rules.md:35`).
- **The only slice-only test:** it is already removed.

## Door

**Door:** two-way. The change adds flags, two record fields with defaults, a git ref per slice, and two stops. It migrates or deletes no data, and a revert undoes it. A ref left behind is inert. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 52ffb8bda97ca1c704e685c76e860f40c98c75e0..HEAD`. This pass alone: `git diff 5effbd4..HEAD -- scripts tests`
- Wall: `xv wall diff 2026-11-05-from-build` (baseline `199b583`)
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md`

## Suite run

I ran `python3 tests/run.py --jobs 4` on HEAD `f46c685`: "Ran 1012 tests in shard 1/1 / OK", exit 0.

## From the cleaner

- Shape proposal, for people: prompt.py repeats record.has_build's isinstance(data.get('build'), dict) check; sharing it would add a record import to prompt.py, so left for the packet.

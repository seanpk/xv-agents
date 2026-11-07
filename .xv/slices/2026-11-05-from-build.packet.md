---
slice: 2026-11-05-from-build
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A slice can start from a build that already exists: #113

This is the sixth guardian pass, and the first since the rebase onto `52ffb8b`. Nothing stops for two people.

Last pass's two misses are closed. Sean narrowed point 12 to "no rebase, and a rebase that finishes", and moved `--abort` to #147. The CHANGELOG line now names `rebase_red_ref` (`CHANGELOG.md:10`). The Opus scenario line is out of `.xv/config.yml` (`b0d1d8f`).

The rebase brought in two new problems:
- **Miss on point 13 (to: scenario).** Main's change makes `xv record report` run the wall check. That session path skips the build's stop-once rule, so a test file the build changed stops after every session maker or cleaner report, not once.
- **For Sean (A).** The rebase left two `#113` lines in `CHANGELOG.md`. The stale one says "New stop: `red_conflicts_with_build`" only.

## Scenario misses

- 13: "A test shows that a test file the build changed stops once as a change with no record." This holds for `xv step` only. After the maker and the cleaner, `xv step` passes the wall result through `wall_for_build`. That function drops a file a person has already answered, while the file is still as the build left it (`scripts/run.py:1046`: `checks["wall"] = wall_for_build(root, data, wall.check_or_note(root, data["id"], config))`, and `scripts/run.py:1332-1341`). The session path came from main in this rebase, and it writes the raw result (`scripts/record.py:742`: `data["checks"].setdefault(a.agent, {})["wall"] = wall.check_or_note(root, data["id"], config)`). `orders` fires `unrecorded_move` on any `wall.unrecorded` (`scripts/orders.py:202-206`). So with `agents.maker: session` or `agents.cleaner: session`, the build's test-file change stops again on each `xv record report` + `xv orders`. The picture says the session path runs the same checks: "`xv record report` for the maker and the cleaner runs the expected-move and wall checks" (`.xv/picture.md:23`). The red drives only `self.step(...)` (`tests/test_from_build.py:660-672`). I found this by reading the code; I did not run the session path. (evidence: `scripts/record.py:742` against `scripts/run.py:1046`; to: scenario)

## The scenario

- **Opening the slice:** `xv slice new --from <ref>` starts the branch at the build, and `base` stays the merge target. The record holds `build` and `build_shared`. `--share-build` names the build to the scenario agent as a reference only, and is refused without `--from` (points 1, 4, 5, 11).
- **Running the red:** the scenario agent writes the red at the base, without the build. The red must fail on the base, then runs on the build.
  - A test that fails on the build goes to the maker as a miss, with no stop.
  - A red that passes on the build skips the maker (points 6-8).
- **The rest:** the skills write the scenario from what runs, and offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line (points 2, 3, 9, 10).
- **Amendments 12-15:**
  - A later pass starts at the base with the earlier red, and lands cleanly. This is narrowed to no rebase and a rebase that finishes; `--abort` is #147.
  - `red_conflicts_with_build` and the build's stop-once are tested.
  - The unshared copy names no commit at the build.
  - A session scenario step makes the base checkout and names it.
- **Sean's settled rules:**
  - The red lives on `refs/xv/<id>/red`, and each pass starts from its tip.
  - The copy keeps no commit that is off the base.
  - `xv slice rebase` moves the ref, and stops with `rebase_red_ref` if it cannot.
  - The session-mode leak and a hand-landed red are v0.5.
- **May ignore:** a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

There is none: a feature starts from words.
- **Replay:** `cd tests && python3 -m unittest test_from_build`. I ran it on HEAD `5effbd4`: "Ran 53 tests … OK".
- **Whole suite:** I ran `python3 tests/run.py --jobs 4` on HEAD: "Ran 1011 tests in shard 1/1 OK", exit 0. No test drives `xv record report` on a slice from a build.
- **The red:** it failed with "refs/xv/s1/red was not moved onto the new base" (`.xv/slices/2026-11-05-from-build.md:13`).
- **By hand:** follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`, base `52ffb8b`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- No module, edge, outbound call or table is added or removed (`:9-19`, `:116-119`).
- One shape hint: "a surface path was added or removed", for `/red` (`:5-7`, `:123`).

## What the suite asserts after

`tests/test_from_build.py` is new, with 53 tests:
- `xv slice new --from`: the branch, `base`, the record fields, and the refusals (`:134-191`).
- The scenario agent runs at the base, and its prompt names the build only when it is shared (`:193-237`).
- The red runs on the base, then on the build. The slice goes to the maker with the misses named, or to the cleaner (`:239-325`).
- A second pass starts from the red ref and lands cleanly. This holds after the maker, when the red edits a file the build changed, and after a clean rebase. A rebase that cannot move the ref stops and names it (`:327-645`).
- `red_conflicts_with_build`, and the build's test-file stop fires once on the `xv step` path (`:647-673`).
- The record copy names no commit off the base (`:675-738`).
- A session scenario step names its checkout (`:740-768`).
- The skill wording (`:770-823`).

No old assertion changed. `tests/fake_agent.py` only gains fakes (see 3).

## 1. Shape

shape_change: no. shape_breadth: narrow; the forecast expected wide (`.xv/slices/2026-11-05-from-build.md:11`).

- **The hint "`/red` added":** it does not change the shape. `/red` is the tail of a git ref name, `"refs/xv/" + data["id"] + "/red"` (`scripts/run.py:874-875`), not a route or page that users meet.
- **Modules and edges:** none is added (`.xv/slices/2026-11-05-from-build.boundary.md:9-19`). The new stops are in `orders.py` (`scripts/orders.py:134`, `:190`, `:377`).
- **The rebase resolution:** it kept the slice inside main's split. The helpers main moved to `record`, `packet` and `wall` are called there. The build rule stays in `run` as `wall_for_build` (`scripts/run.py:1332`). No new import edge appears (`.xv/slices/2026-11-05-from-build.boundary.md:18-19`).

## 2. Pitch

pitch_contradiction: no.
- "to vibe with discipline" (`.xv/pitch.md:7`): the red is still written without the build and must fail on the base. The build only changes where the maker starts (`scripts/run.py:899-923`).
- Nothing serves someone named in "Who it is not for" (`.xv/pitch.md:23-25`).

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes` | Removed | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | No. It is a slice-only mark Sean accepted (`.xv/slices/2026-11-05-from-build.md:16`). |
| tests/fake_agent.py | No `FAKE_CWD_LOG`, `FAKE_RECORD_LOG`, `FAKE_RED_ADDS_TO_OLD` or `FAKE_CLEANER_COMMITS`; 2 assertions | The four fakes are added, and no line is removed (`git diff 52ffb8b -- tests/fake_agent.py`: hunks `@@ -25,6 +25,22`, `@@ -81,6 +97,16`, `@@ -127,6 +153,11`); 7 assertions (`xv wall diff`) | Sean Kennedy: "F's own red commits added these fakes; only lines added. The wall rehash after the rebase took this red file from main, so they looked unrecorded." | Yes. The red uses each one: `FAKE_CWD_LOG` (`tests/test_from_build.py:64`), `FAKE_RED_ADDS_TO_OLD` (`:442`, `:557`), `FAKE_RECORD_LOG` (`:690-732`), `FAKE_CLEANER_COMMITS` (`:718`). Nothing asserts less. |

Slice-only tests removed: `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

- `xv wall diff 2026-11-05-from-build` against baseline `ef55e48` lists only `tests/fake_agent.py`, with no file asserting less.
- `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`). No may-not file was allowed.

### For Sean

**A. Two `#113` lines in the CHANGELOG** (`CHANGELOG.md:9` and `CHANGELOG.md:10`). Before the rebase, `bb42598` had one line, the one Sean directed. After the rebase, the maker's original line has come back above it (`git diff bb42598 HEAD -- CHANGELOG.md`). Line 9 names only "New stop: `red_conflicts_with_build`". Line 10 is the directed one. The red cannot catch this, because its CHANGELOG test is slice-only and was removed.

**B. The red ref is never deleted.** It is written at `scripts/run.py:549` and `:915`, and no code runs `update-ref -d` (`grep -n update-ref scripts/*.py`). This is unchanged from last pass.

## 4. The picture

`.xv/picture.md` is not in the diff. Sean said the picture edits wait for the last guardian pass. These are the edits:
- **`.xv/picture.md:27`, "The branch starts from `--base`, else …":** add "`--from <ref>` starts it at a build instead; `base` stays the branch it merges into, and the record holds `build: {kind: exploration, ref}` and `build_shared`." Also add `refs/xv/<id>/red` to the state list: "Each slice has a git branch `xv/<id>`…", plus a ref that holds the red at the base.
- **`.xv/picture.md:27`, the scenario step:** add "On a slice from a build, the scenario agent runs in a temporary worktree at the red ref's tip, or at the base. Its copy of the record names no commit off the base unless the build is shared. Its red runs there, the wall is hashed there, and the red is cherry-picked onto the slice branch. A conflict stops with `red_conflicts_with_build`. The red then runs on the build, and the maker's prompt names the tests that fail" (`scripts/run.py:845-923`, `scripts/prompt.py:116-120`).
- **`.xv/picture.md:23`, `next`:** "after a scenario step whose red passes on the build, `next` is `cleaner`" (`scripts/orders.py:377`).
- **`.xv/picture.md:23`, "After `rebase`, `orders` decides …":** add `rebase_red_ref`, and "`xv slice rebase` moves `refs/xv/<id>/red` onto the new base before the suite, and stops when it cannot" (`scripts/run.py:580-584`).
- **`.xv/picture.md:23`, "`xv record report` for the maker and the cleaner runs the expected-move and wall checks":** add "on a slice from a build, a test file the build changed stops once (`run.wall_for_build`)". This is true today on `xv step` only; see the miss.

## 5. The wall

No recommendations. I looked at:
- `xv wall diff`: no test that was on the wall before the slice is made dead, and `tests/fake_agent.py` only gains fakes.
- The new tests in `tests/test_from_build.py`. The `SliceSkillTest` wording tests (`:770-823`) stay on the wall: "a test of a brief sentence that matches a code rule stays on the wall" (`.xv/rules.md:35`). The second-pass classes (`:327`, `:354`, `:425`, `:527`) each start from a different state: no maker, after the maker, a red that edits a file the build changed, and after a rebase. None restates another.
- The only slice-only test, which is already removed.

## Door

**Door:** two-way. The change adds flags, two record fields with defaults, a git ref per slice, and two stops. It migrates or deletes no data, and a revert undoes it. A ref left behind is inert. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 52ffb8bda97ca1c704e685c76e860f40c98c75e0..HEAD`. Before the rebase: `git diff 5d5e75f bb42598`
- Wall: `xv wall diff 2026-11-05-from-build` (baseline `ef55e48`)
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md`

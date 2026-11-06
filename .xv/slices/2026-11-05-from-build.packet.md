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

This is the fifth guardian pass. Nothing stops for two people.

Sean's rule from the 20:30 answer is in: `xv slice rebase` moves the red ref onto the new base, and stops with `rebase_red_ref` when it cannot. Last pass's miss on point 12 is fixed for a rebase that finishes.

Two new misses go back:
- **Point 12 after `--abort`:** to the scenario agent. When a rebase has moved the red ref and then stops later, `--abort` puts the slice back on the old base but leaves the ref on the new one. The next pass then starts at the new main, not at the base.
- **Binding decision 1:** to the maker. `rebase_red_ref` is a new standing order, and the CHANGELOG line does not name it.

Sean also decides:
- (A) The Opus scenario line is still in `.xv/config.yml`.
- (B) The red ref is never deleted.
- (C) After a `rebase_red_ref` stop, `--continue` leads to a pass without the earlier red, and nothing says so.

## Scenario misses

- 12: When the red ref has moved and the rebase then stops, `--abort` leaves the ref on the new base, and the next pass starts there, not "at the base". `rebase_finish` moves the ref (`scripts/run.py:539-543`) before it runs the suite. A red suite then stops with `rebase_suite_red`, which offers "`xv slice rebase <id> --abort` to give it up" (`scripts/orders.py:175`). `--abort` resets the slice to `orig_head` (`scripts/run.py:609`), and the record keeps the old base. Nothing in the abort path (`scripts/run.py:599-620`) touches the ref. `red_held` takes the ref whenever the base is *an* ancestor of its tip (`scripts/run.py:828`). The old base is an ancestor of the new main, so the next pass starts at `<new main> + red` (`scripts/run.py:794`). Its "must fail on the base" run (`scripts/run.py:852`) and its wall baseline then see main's newer files. Its red commit is cherry-picked onto a slice branch that does not have them (`scripts/run.py:862`). No test aborts a rebase (`tests/test_from_build.py:527-644`). I found this by reading the code; I did not run it. (evidence: `scripts/run.py:828`: `if held and subprocess.run(["git", "merge-base", "--is-ancestor", base, held], …).returncode == 0: return held`, with `scripts/run.py:539-543` and `:599-620`; to: scenario)
- decision 1: The rule is "A change to … a standing order … needs … a line in `CHANGELOG.md`" (`.xv/picture.md:64`). This slice adds the standing order `rebase_red_ref` (`scripts/orders.py:184-187`). The slice's CHANGELOG line names only one new stop, "New stop: `red_conflicts_with_build`". It does not mention the red ref or how `xv slice rebase` moves it (`CHANGELOG.md:7`). The red has no CHANGELOG test: Sean accepted the gap on point 10, and its slice-only test was removed. (evidence: `CHANGELOG.md:7`, `scripts/orders.py:184-187`; to: maker)

## The scenario

- **Opening the slice:** `xv slice new --from <ref>` opens a slice at a build that already exists, and `base` stays the merge target. The record holds `build` and `build_shared`. `--share-build` names the build to the scenario agent as a reference only, and needs `--from` (point 11).
- **Running the red:** the scenario agent writes the red at the base, without the build. The red must fail on the base, then runs on the build.
  - A test that fails on the build goes to the maker as a miss.
  - A red that passes on the build sends the slice to the cleaner.
- **The rest:** the skills offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line.
- **Amendments 12-15:**
  - A later pass starts at the base with the earlier red, and lands cleanly.
  - `red_conflicts_with_build` and the build's test-file stop are tested.
  - The unshared copy names no commit at the build.
  - A session step makes the base checkout and names it.
- **Sean's settled rules:**
  - The red lives on `refs/xv/<id>/red`, and each pass starts from its tip.
  - The copy keeps no commit that is off the base.
  - `xv slice rebase` moves the ref onto the new base, and stops if it cannot.
- **May ignore:** a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

There is none: a feature starts from words.
- **Replay:** `cd tests && python3 -m unittest test_from_build`. I ran it on HEAD: 53 tests, OK.
- **Whole suite:** I ran `python3 tests/run.py --jobs 4` on HEAD: "Ran 845 tests in shard 1/1 OK".
- **The red:** it failed with "refs/xv/s1/red was not moved onto the new base" (record `red.failure`, `.xv/slices/2026-11-05-from-build.md:13`).
- **By hand:** follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- No module, edge, outbound call or table is added or removed (`:9-19`).
- One shape hint: "a surface path was added or removed", for `/red` (`:5-7`, `:119`).

## What the suite asserts after

Everything from the last pass still holds, and `RedRefRebaseTest` (`tests/test_from_build.py:527-644`) adds:
- A clean rebase moves the red ref onto the new base. The ref keeps the first red and does not have the build.
- A pass after the rebase starts at the new base with the earlier red in it. Its red lands on the slice branch with no conflict, and the ref moves on to it.
- When main adds its own `tests/test_red.py`, the rebase stops for the originator with an order from `orders.py` that names the ref. The ref is not dropped and keeps the first red.

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast said wide).

- **The hint "`/red` added":** it does not change the shape. `/red` is the tail of a git ref name, `"refs/xv/" + data["id"] + "/red"` (`scripts/run.py:820-821`), not a route or a page that users meet.
- **What this pass adds:** `move_red_ref` uses a temporary worktree, like the scenario scratch does (`scripts/run.py:499-515`). The rebase's stop rule is in `orders.py` (`scripts/orders.py:184-187`).
- **Modules and edges:** none is added (`.xv/slices/2026-11-05-from-build.boundary.md:9-19`).

## 2. Pitch

pitch_contradiction: no.
- "to vibe with discipline" (`.xv/pitch.md:7`): the red is still written without the build and must still fail on the base (`scripts/run.py:852`).
- Nothing serves someone named in "Who it is not for" (`.xv/pitch.md:25-27`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes` | Removed | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | No. It is a slice-only mark Sean accepted (`.xv/slices/2026-11-05-from-build.md:16`). |

Slice-only tests removed: `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

- `xv wall diff 2026-11-05-from-build` lists nothing changed, deleted or added since the baseline `89f8326` (`.xv/slices/2026-11-05-from-build.md:14`), and no file with fewer assertions.
- The record has `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`).

### For Sean

**A. The Opus scenario line is still in the diff** (`.xv/config.yml:35-36`). It reads "Slice F only, as Sean directed … Removed before the PR".

**B. The red ref is never deleted.** It is written at two places, `scripts/run.py:512` and `:861`, and no code runs `update-ref -d`. Sean put this in #147 at 19:55, and then picked option 2, which does not mention it (`.xv/slices/2026-11-05-from-build.md:24`).

**C. `--continue` after `rebase_red_ref` drops the earlier red silently.**
- The stop says "It stays on the old base. Run … --continue to go on without moving it" (`scripts/orders.py:185-187`).
- After that, `red_held` with the new base finds no ref (`scripts/run.py:828`), so the next pass starts at the new base with no earlier red. This is the path the last packet's miss described. Sean's rule only says the rebase stops (`.xv/slices/2026-11-05-from-build.md:24`, the 20:30 answer), so this is not a miss. But the stop does not tell the person what going on costs.

## 4. The picture

These are last pass's proposed edits, and they still stand. Sean said the picture edits wait for the last guardian pass.
- **`.xv/picture.md:27`, opening a slice:** add `--from`, `--share-build`, the `build` and `build_shared` fields, and `refs/xv/<id>/red`. The ref holds the red at the base.
- **`.xv/picture.md:27`, the scenario step for a slice from a build:** the step uses a temporary worktree at the tip of the red ref, or at the base (`scripts/run.py:794`). The unshared copy names no commit off the base. The red is cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build` (`scripts/run.py:862`). The red then runs on the build, and the maker's prompt names the tests that fail (`scripts/prompt.py:116-120`).
- **`.xv/picture.md:23`:** after a scenario step whose red passes on the build, `next` is `cleaner`.

New this pass:
- **`.xv/picture.md:23`:** in "After `rebase`, `orders` decides `rebase_conflict`, `rebase_dropped`, `rebase_stuck` and `rebase_suite_red`", add `rebase_red_ref`. Add a sentence after it: "On a slice from a build, `xv slice rebase` moves `refs/xv/<id>/red` onto the new base before it runs the suite, and stops with `rebase_red_ref` when the red does not apply there."

## 5. The wall

No recommendations. I looked at:
- `xv wall diff`: it lists no test that was on the wall before the slice, so none is made dead.
- The four new `RedRefRebaseTest` tests (`tests/test_from_build.py:575-644`): each guards a separate part of Sean's rebase rule (the move, the start, the landing, the stop), so none restates another.
- The only slice-only test, which is already removed.

## Door

**Door:** two-way. The change adds flags, two record fields with defaults, and one git ref per slice. It migrates or deletes no data, so a revert undoes it. Refs left behind are inert. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. Since the last packet: `git diff 89f8326..HEAD`
- Wall: `xv wall diff 2026-11-05-from-build`
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md`

## Directed edits after the guardian

- CHANGELOG.md (changelog): directed by Sean Kennedy

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

This is the fourth guardian pass. No stop for two people.

Sean's two rules from the 19:28 answer are in, and both last-pass misses are fixed for the cases the red tests:
- Point 12: the red lives on `refs/xv/<id>/red`, and a later pass starts from that ref's tip. Nothing is replayed from the slice branch.
- Point 14: the record copy now drops every commit that is not on the base.

One new miss goes back to the scenario agent:
- **Point 12 after a rebase.** `xv slice rebase` moves `base`. After that, the red ref is no longer on top of the base, so the next pass quietly starts at the new base **without** the earlier red. This is the path Sean planned: "rebase early only if F goes back to the scenario agent".

Sean also decides:
- (A) The Opus scenario line is still in `.xv/config.yml`.

## Scenario misses

- 12: After `xv slice rebase`, a second scenario pass does not start "at the base with the red from the earlier passes in it". The rebase writes the new base into the record, `data["base"] = state["onto"]` (`scripts/run.py:527`). `scenario_scratch` uses the red ref only when the base is an ancestor of it (`scripts/run.py:773-774`). The ref sits on the old base, so after the rebase that check fails. The pass then starts at the new base with no earlier red, and nothing says so. The new red is cherry-picked onto the slice branch, which already has the earlier red (`scripts/run.py:833`). If the agent writes `tests/test_from_build.py` again from scratch, that is an add/add conflict, and the slice stops with `red_conflicts_with_build`, a stop that blames the build. If there is no conflict, `update-ref` still moves the ref to a red without the earlier passes (`scripts/run.py:832`). No test in `tests/test_from_build.py` rebases, and `red_refs()` keeps only refs that descend from the test's fixed `main` (`tests/test_from_build.py:462`). The path is reachable here: Sean's 19:36 answer says "F is rebased onto main once, before the PR, or earlier if the guardian sends it back to the scenario agent" (`.xv/slices/2026-11-05-from-build.md:24`). I found this by reading the code; I did not run it. (evidence: `scripts/run.py:773-774`: `if held and subprocess.run(["git", "merge-base", "--is-ancestor", data["base"], held], …).returncode == 0: start = held`, with `scripts/run.py:527`; to: scenario)

## The scenario

- **Opening the slice:** `xv slice new --from <ref>` opens a slice whose branch starts at a build that already exists, and `base` stays the merge target. The record holds `build: {kind: exploration, ref}` (`none` without `--from`) and `build_shared`.
- **Writing and running the red:** the scenario agent writes the red at the base, without the build. `--share-build` names the build to it as a reference only, and needs `--from` (point 11). The red must fail on the base, then runs on the build. A test that fails on the build goes to the maker as a miss. If the whole red passes on the build, the slice goes to the cleaner.
- **The rest:** the skills offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line.
- **Amendments:**
  - Point 12: a second pass starts at the base with the earlier red and lands cleanly.
  - Point 13: tests for `red_conflicts_with_build`, and for a build's test-file change stopping once.
  - Point 14: the unshared copy names no branch or commit at the build.
  - Point 15: a session scenario step makes the base checkout and names it.
- **Sean's rules (19:28):** the red at the base lives on its own ref, and each later pass starts from its tip. The unshared copy keeps no commit that is not an ancestor of the base.
- **May ignore:** a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

There is none: a feature starts from words.
- **Replay:** `cd tests && python3 -m unittest test_from_build`. I ran it on HEAD: 49 tests, OK.
- **The red:** it failed on `patch failed: tests/test_store.py:46` (record `red.failure`).
- **Whole suite:** I ran `python3 tests/run.py --jobs 4` on HEAD: "Ran 841 tests in shard 1/1 OK". The cleaner's run also passed (record `checks.cleaner.suite_output`, `.xv/slices/2026-11-05-from-build.md:28`).
- **By hand:** follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- No module, edge, outbound call or table is added or removed.
- Shape hint: "a surface path was added or removed", for `/red` (section 1).

## What the suite asserts after

- **Flags:** `--from` starts the branch at the build and keeps `base`. A missing ref, an empty `--from` and a bare `--from` are each refused. `--share-build` without `--from` is refused and leaves nothing behind.
- **Where the scenario agent works:** in a checkout at the base. The build is not in its prompt or its record copy. With `--share-build`, the prompt names the build as "reference only".
- **Where the slice goes:**
  - A red that passes on the base stops.
  - A red that fails on the build goes to the maker, and the maker's prompt names the failing tests.
  - A red that passes on the build goes to the cleaner.
- **New this pass:**
  - The first pass leaves a ref at the base that holds the red and not the build.
  - A second pass starts at that ref's tip, and the ref then moves on to the new red.
  - The red can add a test to `tests/test_store.py` while the build changed a line two lines above it. In that case, the second pass:
    - starts at the base, with the earlier red and without the build's line;
    - lands on the slice branch with no crash and no `red_conflicts_with_build`, keeping the build, the first red and the second red;
    - leaves no checkout behind.
  - After a cleaner that committed, and for any record field (`explored_at`, a JSON `notes` value), the copy names no commit off the base.
- **Kept from earlier passes:**
  - the second pass after the maker;
  - `red_conflicts_with_build`;
  - the build's test-file change stopping once;
  - the session checkout;
  - the skill wording.

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast said wide).

- **The hint "a surface path was added", for `/red`:** it does not change the shape. The path is the tail of a git ref name, `return "refs/xv/" + data["id"] + "/red"` (`scripts/run.py:801`). It is not a route or a page that users meet.
- **The ref itself:** it is new git state in the same family as the slice branch `xv/<id>` and the `xv-rebase-<id>.json` notes in the git dir. The picture already lists both as state (`.xv/picture.md:27`). It is not a new kind of store.
- **Modules, edges and tables:** none is added (`.xv/slices/2026-11-05-from-build.boundary.md:11-19`, `:112-115`).
- **The `build` and `build_shared` fields** are in the existing slice file (`.xv/picture.md:27`, "State is files"). The `--from` and `--share-build` flags are on the existing `xv` CLI.

## 2. Pitch

pitch_contradiction: no.
- "to vibe with discipline" (`.xv/pitch.md:7`): the red is still written without the build, and must still fail on the base (`scripts/run.py:823`, `landed["base_run"] = shell(red["command"], scratch, 600)`).
- The change serves no one the pitch excludes in "Who it is not for" (`.xv/pitch.md:25-27`).

## 3. Moved tests

| File | Before | After | Why | Forced? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `ChangelogTest.test_unreleased_has_a_line_for_113_naming_each_brief_it_changes` | Removed | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | No. It is a slice-only mark that Sean accepted (`slice_only[0].accepted: true`). |

Slice-only removals: `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

- `xv wall diff 2026-11-05-from-build` lists no changed, deleted or added test file since the baseline `d186960`, and no file with fewer assertions (`.xv/slices/2026-11-05-from-build.md:14`, `wall_baseline`).
- `tests/fake_agent.py:90-99` and `:139-143` add two fake behaviours: `FAKE_RED_ADDS_TO_OLD` and `FAKE_CLEANER_COMMITS`. They remove no assertion.
- `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`).

### For Sean

**A. The Opus scenario line is still in the diff.** `.xv/config.yml:35-36` reads "# Slice F only, as Sean directed: the wide-slice test. Removed before the PR.", then `scenario: [… "--model", "opus" …]`. If it merges, every later scenario step in this repo runs on Opus.

**B. The red ref is never deleted.** Nothing in `scripts/` runs `update-ref -d` on `refs/xv/<id>/red` (only `scripts/run.py:832` writes it). A closed slice keeps its ref. A new slice with the same id and the same base would start its first pass from the old slice's red (`scripts/run.py:773-774`). No scenario line covers this, so it is not a miss.

**C. Since the last packet:**
- Last pass's miss on point 12 is fixed: there is no `git apply` replay any more (`scripts/run.py:770-776`). Tested at `tests/test_from_build.py:498-524`.
- Last pass's miss on point 14 is fixed: the copy rewrites every commit token that is not on the base to `-` (`scripts/run.py:791-796`). Tested at `tests/test_from_build.py:594-617`.
- Finding (C) of the last packet, a red landed by hand: the ref now moves before the cherry-pick (`scripts/run.py:832-833`). The agent's red is kept for the next pass even when it conflicts. The person's own resolution is not.
- The session-mode leak is a v0.5 issue, as Sean settled at 19:28 (`.xv/slices/2026-11-05-from-build.md:24`). The code is unchanged at `scripts/run.py:696`.

## 4. The picture

Proposed edits, all to `.xv/picture.md:27` unless a line says otherwise:
- **Opening a slice from a build.** After "The branch starts from `--base`, else …", add: "With `xv slice new --from <ref>` the branch starts at the build, and `base` stays the merge target. The record holds `build` (`none`, or `{kind: exploration, ref}`) and `build_shared` (`yes`/`no`). `--share-build` needs `--from`. A slice from a build also has a git ref, `refs/xv/<id>/red`, which holds its red at the base."
- **The scenario step for a slice from a build** (`.xv/picture.md:27`, the scenario-step sentences). Add:
  - The scenario agent runs in a temporary detached worktree. It starts at the tip of `refs/xv/<id>/red` when the base is an ancestor of that tip, and at the base otherwise (`scripts/run.py:770-776`).
  - Unless the build is shared, the agent's record copy has `build: none` and `branch` set to the base. Every commit it names that is not an ancestor of the base reads `-` (`scripts/run.py:784-796`).
  - The red runs there, and the wall baseline is hashed there. Its commit moves the ref (`scripts/run.py:832`). It is then cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build` for the originator (`scripts/orders.py`).
  - The red then runs on the build, and the maker's prompt names the tests that fail (`scripts/prompt.py`).
  - A session scenario step makes the checkout and names it (`scripts/run.py:696`).
- **The check after the maker.** After "a scenario step checks the red … at `pre_maker_commit`", add: "except in a slice from a build, where the red runs in the scratch checkout at the base".
- **Where the slice goes** (`.xv/picture.md:23`). After "`orders.verdict` also returns `next`", add: "After the scenario step, `next` is `cleaner` when the red failed on the base and passes on the build."
- **A build's test-file change.** At the `unrecorded_move` sentence, add: "In a slice from a build, a test file the build changed stops once."
- **`## Names`.** Add: "An exploration is a build made with an agent outside XV. A slice opens from it with `--from`."

## 5. The wall

No recommendations.
- `xv wall diff` lists no test that was on the wall before the slice, so none is made dead.
- The new tests in `RedOnItsOwnRefTest` (`tests/test_from_build.py:425-524`) and `RecordCopyTest` (`:594-617`) guard Sean's two settled rules on separate paths. The cleaner path and the any-field path are separate setups, so neither test restates another.
- The only slice-only test has already been removed.

## Door

**Door:** two-way. The change adds flags, two record fields with defaults and one git ref per slice. It migrates or deletes no data, so a revert undoes it. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. Since the last packet: `git diff 1ece1f7..HEAD`
- Wall: `xv wall diff 2026-11-05-from-build`
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md`

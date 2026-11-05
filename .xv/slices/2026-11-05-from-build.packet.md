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

This is the third guardian pass. No stop for two people.

The two misses from the second pass are fixed for the cases the red tests. The slice goes back to the scenario agent on two narrower misses, both read from the code:
- **Point 12:** a second pass crashes when the red edits a test file the build also changed.
- **Point 14:** the unshared record copy still keeps `cleaner_commit`.

Sean also decides:
- (A) The Opus scenario line is still in `.xv/config.yml`.
- (B) A session-mode scenario step still leaks its checkout, and nothing lands the red written there.
- (C) A red that a person lands by hand after `red_conflicts_with_build` is not replayed on a later pass.

## Scenario misses

- 12: A second pass does not start "at the base with the red from the earlier passes" when the red edits a test file the build also changed. Each earlier `xv(<id>): red` commit is replayed as its slice-branch diff, `git diff sha^ sha`, with plain `git apply`, which has no 3-way merge. On the slice branch that commit is a cherry-pick onto the build (`scripts/run.py:817`). When the build changed a line within three lines of the red's hunk, but not next to it, the cherry-pick merges cleanly, yet the diff's context lines hold the build's text, so `git apply` on the base rejects it. `check=True` raises `CalledProcessError`, which `main` does not catch (`scripts/run.py:1691` catches only `XVError`), so the step exits 1, not 2 (decision 11, `.xv/picture.md:74`). The raise comes inside `scenario_scratch`, after `git worktree add` (`scripts/run.py:770`) and outside the `try` around the agent run, so the checkout is left behind. Every red in the tests writes a new file, `tests/test_red.py` (`tests/test_from_build.py:65`, `:419`). The test where the build changes `tests/test_store.py` (`tests/test_from_build.py:430-431`) never has the red edit that file, though point 13 names exactly that kind of build. Read from the code, not run. (evidence: `scripts/run.py:782-785`: `["git", "diff", "--binary", f"{sha}^", sha, …]` then `["git", "apply", "--index", "-"] … check=True`; to: scenario)
- 14: After a cleaner that committed, the unshared record copy still names a commit at the build. The copy drops `build`, `branch` and `pre_maker_commit` (`scripts/run.py:787-790`) but keeps `cleaner_commit`. That field is the slice HEAD after the cleaner when the cleaner moved HEAD (`scripts/run.py:950-951`), or the cleaner's reported commit (`scripts/record.py:531`); either way the commit holds the build, the red and the maker's fix. The case is reachable: a guardian `scenario_miss` sends the slice back to the scenario agent after the cleaner, as it did on this slice (`.xv/slices/2026-11-05-from-build.md:24`, the stop at 23:03:29). `RecordCopyTest.test_a_second_pass_copy_after_the_maker_names_no_branch_or_commit_at_the_build` runs only the maker before the second pass (`tests/test_from_build.py:472-480`). (evidence: `scripts/run.py:788-790`, `scripts/run.py:950-951`; to: scenario)

## The scenario

`xv slice new --from <ref>` opens a slice whose branch starts at a build that already exists, and `base` stays the merge target. The record holds `build: {kind: exploration, ref}` (`none` without `--from`) and `build_shared`.

The scenario agent writes the red at the base without the build, unless `--share-build` is given, which names the build as a reference only and needs `--from` (11). The red must fail on the base, then runs on the build. A failing test goes to the maker as a miss. If the whole red passes, the slice goes to the cleaner.

The skills offer an exploration when the scenario will not settle. New stops go in `orders.py`, with a CHANGELOG line.

Amendments 12-15:
- 12: a second pass starts at the base with the earlier red and lands cleanly.
- 13: tests for `red_conflicts_with_build`, and for stopping once on a build's test-file change.
- 14: the unshared copy names no branch or commit at the build.
- 15: a session scenario step makes the base checkout and names it.

May ignore: a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

None; a feature starts from words. Replay: `cd tests && python3 -m unittest test_from_build`. The guardian ran it on HEAD: 41 tests, OK. The third red (`63664ee`) failed on `patch failed: pantry/store.py:44` (record `red.failure`). The guardian also ran the whole suite on HEAD with `python3 tests/run.py --jobs 4`: 833 tests, OK. To see it by hand, follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`:
- Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- No module, edge, outbound call, table or surface path is added or removed.
- Shape hints: none.

## What the suite asserts after

- **Flags:** `--from` starts the branch at the build and keeps `base`. A missing ref, an empty `--from` and a bare `--from` are each refused. `--share-build` without `--from` is refused and leaves nothing behind.
- **Where the scenario agent works:** it runs in a checkout at the base, and the build is not named in its prompt or its record copy. With `--share-build`, the prompt names the build as "reference only".
- **Where the slice goes:**
  - A red that passes on the base stops with `scenario_not_red`.
  - A red that fails on the build goes to the maker, and the maker's prompt names the failing tests.
  - A red that passes on the build goes to the cleaner, with no maker.
- **New this pass:**
  - A second pass after the maker has the earlier red in its checkout, but neither the build nor the maker's fix.
  - That red still fails on the base.
  - When the build and the maker both edit `pantry/store.py`, the second pass lands with no crash and no conflict, keeps the build and the maker's fix, and leaves no checkout behind.
  - The record copy after the maker names no branch or commit at the build.
- **Kept from earlier passes:**
  - `red_conflicts_with_build`.
  - The build's test-file change stops exactly once.
  - The session checkout is at the base.
  - The skill wording.
- Old assertions that moved: only the slice-only CHANGELOG test, now removed (section 3).

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast said wide).

- The boundary picture lists no new module, edge, table, surface path or outbound call, and no shape hints (`.xv/slices/2026-11-05-from-build.boundary.md:5-30`).
- `build` and `build_shared` are fields in the existing slice file (`scripts/record.py:28`; `.xv/picture.md:27`, "State is files").
- `--from` and `--share-build` are flags on the existing `xv` CLI surface (`.xv/picture.md:28`).
- This pass changes only how the scratch checkout replays the earlier red (`scripts/run.py:778-790`), inside the existing `run` module.

## 2. Pitch

pitch_contradiction: no.
- "to vibe with discipline" (`.xv/pitch.md:7`): a slice from a build still writes its red without the build, and requires the red to fail on the base (`scripts/run.py:808`, `landed["base_run"] = shell(red["command"], scratch, 600)`).
- No one excluded under "Who it is not for" (`.xv/pitch.md:23-25`) is served.

## 3. Moved tests

| File | Before | After | Why | Forced? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `ChangelogTest.test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`, 5 assertions | Removed (`git diff 829b4c8..HEAD`, the `ChangelogTest` hunk) | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | No; a slice-only mark Sean accepted (`slice_only[0].accepted: true`) |

Slice-only removals: `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

- `xv wall diff` shows `tests/test_from_build.py` going from 130 to 125 assertions. Those 5 are exactly the removed test, and the move is recorded.
- Finding C of the last packet is closed: the record and the diff now agree (`.xv/slices/2026-11-05-from-build.md:15`, the second move).
- `tests/fake_agent.py:36` adds a `texts` probe to the log. It asserts nothing and removes nothing.
- `old_tests_forced: []` and `may_not_files: []` (`.xv/slices/2026-11-05-from-build.md:29-30`).

### For Sean

**A. The Opus scenario line is still in the diff.** `.xv/config.yml:35-36`: "# Slice F only, as Sean directed: the wide-slice test. Removed before the PR.", then `scenario: [… "--model", "opus" …]`. The `accept_moves` answer says it is removed before the PR. If it merges, every later scenario step in this repo runs on Opus.

**B. A session-mode scenario step leaks a checkout, and the red written there is never landed.** This is unchanged since the last packet.
- `scripts/run.py:694-696` calls `scenario_scratch` inside the error message and raises. Nothing drops the checkout.
- Only `land_scratch` (`scripts/run.py:801`) cherry-picks the red and runs it on the base and on the build. The commands the message names, `xv record report` and `xv orders`, do neither.
- Point 15 asks only for the checkout and its name (`.xv/slices/2026-11-05-from-build.md:60`), so this is not a miss.

**C. A red landed by hand is not replayed.**
- `red_conflicts_with_build` tells the person to "Resolve it by hand" (`scripts/orders.py:133-137`), and `land_scratch` has aborted the cherry-pick (`scripts/run.py:820`).
- The replay keeps only commits whose subject is exactly `xv(<id>): red` (`scripts/run.py:778-780`). A red the person commits under any other subject is missing from the next pass's checkout.
- No scenario line says how the person lands it, so this is not a miss.

**D. Fixed since the last packet.**
- Miss 12, the second pass after the maker: only the red commits are replayed now (`scripts/run.py:778-786`). Tested at `tests/test_from_build.py:339-413`.
- Miss 14, `pre_maker_commit`: it is dropped from the copy (`scripts/run.py:790`). Tested at `tests/test_from_build.py:472-480`.

## 4. The picture

- `.xv/picture.md:27`, after "The branch starts from `--base`, else …": add "With `xv slice new --from <ref>` the branch starts at the build and `base` stays the merge target. The record holds `build` (`none`, or `{kind: exploration, ref}`) and `build_shared` (`yes`/`no`). `--share-build` needs `--from`."
- `.xv/picture.md:27`, the scenario-step sentences: add the following.
  - In a slice from a build, the scenario agent runs in a temporary detached worktree at the base. The slice's earlier `xv(<id>): red` commits are replayed there (`scripts/run.py:767-786`).
  - Unless the build is shared, the agent reads a record copy with `build: none`, `branch` set to the base and no `pre_maker_commit` (`scripts/run.py:787-790`).
  - The red runs there, and the wall baseline is hashed there. The red is then cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build` for the originator (`scripts/run.py:801-823`, `scripts/orders.py:133-137`).
  - The red then runs on the build. Its failing tests go to `checks.scenario.red_on_build`, and the maker's prompt names them (`scripts/prompt.py:116-120`).
  - A session scenario step makes that checkout and names it (`scripts/run.py:694-696`).
- `.xv/picture.md:27`, "After the maker, a scenario step checks the red … at `pre_maker_commit`": add "except in a slice from a build, where the red runs in the scratch checkout at the base".
- `.xv/picture.md:23`, after "`orders.verdict` also returns `next`": add "After the scenario step, `next_step` returns `cleaner` when the red failed on the base and passes on the build (`scripts/orders.py:362-364`)."
- `.xv/picture.md:27`, the `unrecorded_move` sentence: add "In a slice from a build, a test file the build changed stops once. Once a person has answered it, it is not listed again while it is as the build left it (`scripts/run.py:1199-1206`)."
- `## Names`: add "An exploration is a build made with an agent outside XV. A slice opens from it with `--from`, and the build is that ref."

## 5. The wall

No recommendations.
- The slice-only CHANGELOG test, the only test marked slice-only, is now removed from `tests/test_from_build.py`, so there is nothing left to keep off the wall.
- I checked the new classes against points 12 and 14: `SecondPassAfterTheMakerTest` (`tests/test_from_build.py:339`) and `RecordCopyTest`'s new test (`:472`). Each guards a lasting routing or isolation rule, and none restates another test.
- No test that was on the wall before this slice is made dead: `xv wall diff` lists only `tests/test_from_build.py`, which this slice added.

## Door

**Door:** two-way. The change adds flags and two record fields with defaults, and it migrates or deletes no data, so a revert undoes it. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..1ece1f7`. Since the last packet: `git diff 829b4c8..1ece1f7`
- Wall: `xv wall diff 2026-11-05-from-build`
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md`

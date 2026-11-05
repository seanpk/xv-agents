---
slice: 2026-11-05-from-build
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A slice can start from a build that already exists: #113

No stop for two people. Sean, who set the work going, decides three things: (1) a second scenario pass on a slice from a build probably conflicts with its own red (finding 1a); (2) the new stop `red_conflicts_with_build` and the wall-at-base design have no test (1b); (3) the Opus scenario line in `.xv/config.yml` is still in the diff, though it says it is "Removed before the PR" (1c). Then accept or edit the picture changes in section 4.

## The scenario

`xv slice new --from <ref>` opens a slice from a build that already exists. The branch starts at the build. `base` stays the branch the slice merges into. The record says `build: {kind: exploration, ref}`, or `build: none` when there is no `--from`. By default the scenario agent writes the red at `base` and its prompt does not name the build (`build_shared: no`). With `--share-build` the prompt names the build as a reference only. The red must fail on base and then runs on the build. Each failing test goes to the maker as a miss, with no stop. When the whole red passes on the build, the maker is skipped and the slice goes to the cleaner. The `xv-slice` skill writes the scenario from what runs, and offers a prototype or an exploration when the scenario will not settle. The `watch` skill may make the same offer after the scenario step. New stops go in `orders.py`, and CHANGELOG gets a line. Amendment 11: `--share-build` without `--from` is refused, and no slice opens.

May ignore: a kept prototype pick (#117); what a very large build means for the wall and the packet; old slice records; turning an open slice into an exploration.

## The recording

None; a feature starts from words. Replay: `cd tests && python3 -m unittest test_from_build` (28 tests, OK on HEAD, run by the guardian). Red at `2de5f71`/`d0aa00a` failed 28 of 29 (record `checks.scenario.red_output`). To see it by hand, follow the record's `watch_first_green`.

## The boundary picture

From `.xv/slices/2026-11-05-from-build.boundary.md`. Touched: `scripts/orders`, `scripts/prompt`, `scripts/record`, `scripts/run`. Modules added or removed: none. Edges added or removed: none. Outbound calls added: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- `xv slice new --from <ref>` starts the branch at the build and keeps `base` at main. The record says `exploration` and names the ref. With no `--from` the record says `build: none`. A missing ref, an empty `--from` and a bare `--from` are each refused. `--share-build` without `--from` is refused with "--share-build … needs … --from", and leaves no worktree, record or branch.
- Without `--share-build`, the scenario agent runs in a checkout at main without the build. Its prompt names neither the build branch nor the build's sha. With `--share-build`, the prompt names the build and says "reference only", "what the scenario says", and "not assume … look like the build".
- A red that passes on base stops with `scenario_not_red`, even when the build has the fix. A red that fails on the build goes to `maker` with no stop. The maker's prompt names the failing test, and the maker runs at the build with the red in it. A red that passes on the build sets `next: cleaner`, and `xv run` never runs the maker. `xv orders --after scenario` returns `cleaner` in that case. A slice with no build goes to the maker as before.
- The `xv-slice` and `watch` skill texts contain the offer wording.
- Old assertions that moved: none. The only move is the slice-only CHANGELOG test (section 3).

## 1. Shape

shape_change: no. shape_breadth: narrow (forecast: wide).

- `.xv/slices/2026-11-05-from-build.boundary.md:7-27` lists no new module, edge, table, surface path or outbound call, and no shape hints. Four existing modules are touched.
- The record gains `build` and `build_shared` (`scripts/record.py:28`). These are fields in the existing slice file, which is the current shape ("State is files: `.xv/slices/<id>.md` (front matter plus log)", `.xv/picture.md:27`).
- `xv slice new` gains `--from` and `--share-build` (`scripts/run.py:1610-1612`). These are flags on the existing `xv` CLI surface (`.xv/picture.md:28`).
- In a slice from a build, the scenario agent runs in a temporary detached worktree at base, and its red is cherry-picked onto the slice branch (`scripts/run.py:764-804`). This follows the existing pattern of temporary detached worktrees for the red check (`.xv/picture.md:27`, "a scenario step checks the red in a temporary detached worktree at `pre_maker_commit`"). It is not a new layer.
- The new stop `red_conflicts_with_build` lives in `scripts/orders.py:133-137`. It is raised from what the record says failed, as decision 10 allows (`.xv/picture.md:73`).

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`). An exploration happens outside XV, but the slice still writes the red at base without the build and still requires it to fail there (`scripts/run.py:876`). The wall is still hashed at base (`scripts/run.py:897-904`). The change serves no one and nothing that "Who it is not for" (`.xv/pitch.md:23`) excludes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_from_build.py | `ChangelogTest.test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`: 5 assertions on the #113 CHANGELOG line | removed (`git show 5721237`; wall 78 → 73 assertions) | cleaner: "It checks one CHANGELOG line, which has no value once the slice has merged; the mark was accepted" | Not forced. A slice-only mark that Sean accepted at the `slice_only_marks` stop |

Slice-only tests removed: `tests/test_from_build.py` `test_unreleased_has_a_line_for_113_naming_each_brief_it_changes`. Kept: none.

`xv wall diff` lists only `tests/test_from_build.py`, which matches the record. `old_tests_forced: []`, `may_not_files: []`. `tests/fake_agent.py` changed at the first red commit, before the wall baseline. It adds a `FAKE_CWD_LOG` probe and removes nothing (`tests/fake_agent.py:28-35`).

### Findings for the person who set the work going

**1a. A second scenario pass on a slice from a build starts without the earlier red.**
- Every scenario pass makes a fresh worktree at `data["base"]` (`scripts/run.py:767`: `git(["worktree", "add", "-q", "--detach", scratch, data["base"]], root)`). The red from the earlier pass lives only on the slice branch, so the scenario agent does not see it.
- If the agent rewrites the same red file, its commit adds that file a second time. The cherry-pick onto the slice branch then fails (`scripts/run.py:798`), and the slice stops with `red_conflicts_with_build`.
- The base run (`scripts/run.py:876`) and the wall baseline would also see only the new pass's files.
- A second pass happens after an amend or a `red_misses_point` send-back (`.xv/picture.md:27`, "sends the slice back to the scenario agent"). This slice had one (`.xv/slices/2026-11-05-from-build.md`, log 18:58:48, point 11). No test in `tests/test_from_build.py` runs two scenario passes on a slice from a build.
- Verdict: PLAUSIBLE. It is read from the code at `scripts/run.py:767` and `scripts/run.py:798`; there is no run that shows it.

**1b. The new stop and the design's wall rule have no test.**
- `red_conflicts_with_build` and `cherry_pick_conflict` appear only in `scripts/orders.py:133-137` and `scripts/run.py:882`. No file under `tests/` names them.
- Part (b) of Sean's design has no test either. The rule: the wall baseline is hashed at base, so a test file the build changed stops once (record `stops[2].settled`; `scripts/run.py:897-904`).
- Point 9 is met as written: the stop is in `orders.py`.

**1c. The diff still carries a config line marked for removal.**
- `.xv/config.yml:35`: "# Slice F only, as Sean directed: the wide-slice test. Removed before the PR." It is followed by an Opus `scenario:` agent line.
- If this merges, every later slice's scenario agent runs on Opus (`.xv/config.yml:36`, `"--model", "opus"`).

**1d. The scenario agent can still reach the build.**
- Point 4 holds as tested: the agent works in a checkout at base, and its prompt names neither the build ref nor its sha (`tests/test_from_build.py`, `BuildNotSharedTest`).
- But the record copy the agent reads still holds `branch: xv/<id>` (`scripts/run.py:775-778` drops only `build`). That branch is at the build. The agent's allowed commands include `git log`, `git diff` and `git show` on any ref (`.xv/config.yml:36`, `--allowedTools`).
- Nothing checks that the agent did not look. Decision 12 says "Read-only agents are checked, not trusted" (`.xv/picture.md:75`).

**1e. A session-mode scenario step skips the base checkout.**
- With `agents.scenario: session`, `scripts/run.py:693` raises before `scripts/run.py:699` makes the checkout at base.
- The person then runs the scenario agent in the slice worktree, which has the build in it. The new skill text does not say this (`skills/watch/SKILL.md:62`, "The scenario step runs the scenario agent in a checkout at `base`").

## 4. The picture

- `.xv/picture.md:27`, "The branch starts from `--base`, else …": add "With `xv slice new --from <ref>`, the branch starts at the build and `base` stays the merge target. The record holds `build` (`none`, or `{kind: exploration, ref}`) and `build_shared` (`yes`/`no`). `--share-build` needs `--from`."
- `.xv/picture.md:27`, the scenario-step sentences: add "In a slice from a build, the scenario agent runs in a temporary detached worktree at base. The red runs there and the wall baseline is hashed there. The red commit is then cherry-picked onto the slice branch, and a conflict stops with `red_conflicts_with_build` for the originator. The red then runs on the build. Its failing tests are recorded in `checks.scenario.red_on_build`, and `prompt` names them to the maker as misses. A red that passes on the build sends the slice to the cleaner."
- `.xv/picture.md:23`, "`orders.verdict` also returns `next`": add "after the scenario step, `next_step` returns `cleaner` when the red failed on base and passes on the build (`scripts/orders.py:362-364`)."
- `## Names`: add "An exploration is a build made with an agent outside XV. A slice opens from it with `--from`. The build is that ref."

## 5. The wall

I checked every new test in `tests/test_from_build.py` against the scenario's points and the diff, and the `slice_only` list. I recommend no change: the only slice-only test is already off the wall and removed. Each remaining test guards a lasting behaviour, either a flag, a record field, a routing rule or skill wording. No test that was on the wall before this slice is made dead (`xv wall diff`: only `tests/test_from_build.py` changed).

## Door

**Door:** two-way. The change adds flags and two record fields with defaults, and migrates or deletes no data. A revert undoes it. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-from-build.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..5721237`
- Wall: `xv wall diff 2026-11-05-from-build`
- Boundary: `.xv/slices/2026-11-05-from-build.boundary.md` (`xv boundary --base 5d5e75fc7a73`)

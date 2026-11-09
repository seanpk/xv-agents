---
slice: 2026-11-09-defects-tools
shape_change: accepted
accepted_by: .xv/decisions/2026-11-09-2026-11-09-defects-tools.md
pitch_contradiction: no
scenario_miss: no
picture_change: no
shape_breadth: narrow
moved_tests: 30
expected_moves: 0
door: two-way
blast_radius: CLI
---

# Packet: Rebase, session-mode red and wall-flag fixes from v0.5's tool gaps (guardian pass 2)

**Nothing here needs two people.**
The shape is the one Sean accepted (`.xv/decisions/2026-11-09-2026-11-09-defects-tools.md`), and nothing beyond it was added.
The merge belongs to the originator.
**For Sean as originator, two record items:**

- The record still says `"accepted": false` for all 16 wall recommendations that Sean accepted (check 5).
- Point 16's text still says `xv land-scenario`, which the decision replaced (check 3).

## The scenario

The 17 points are unchanged (`.xv/slices/2026-11-09-defects-tools.md:40-56`).
They cover session-mode red landing on a build slice (1–5), the rebase fixes (6, 8, 9) and the wall-flag forms (7).
They also cover the runner guard (10), `brief:` lines (11), one move told twice (12), `slice new` path checks and repeating `--ignore` (13, 14), the crowded-picture note (15), the docs (16), and `EXPLORE-NOTES.md` out of the merge (17).
The slice may ignore four things:

- why the runner dropped a file;
- old retro counts;
- looser move matching;
- diff3 markers.

## The recording

None; the slice states tool defects in words.
To replay the red, run `red.command` from the record.
I ran the whole suite with `python3 tests/run.py --jobs 4` on HEAD `af389fb`: "Ran 1162 tests in shard 1/1", "OK".
(The first pass ran 1178; the difference is the 16 removals.)

## The boundary picture

This is from `xv boundary` against `c6a1c95702e5`, as given (`.xv/slices/2026-11-09-defects-tools.boundary.md`), and it is unchanged since pass 1.

- Module added: `scripts/names`.
- Edges added: `scripts/record → scripts/names`, `scripts/run → scripts/names`.
- Nothing was removed. There are no tables and no surface paths.
- Shape hints: "a module was added", "an edge between modules was added".

## What the suite asserts after

Each of the 17 points is asserted by the red tests in the eight red files, as in pass 1.
Since pass 1, three things changed:

- The wall-baseline red test compares with a commit the test takes itself.
- The watch-brief doc test looks for `run.py land-scenario`.
- 16 build-added tests that restated red tests are gone.

The red tests they restated are all still present (`grep` in `tests/test_run.py`, `test_record.py`, `test_packet.py`, `test_tests_run.py`, `test_retro.py`: 4, 8, 2, 1 and 1 of the named tests found).
No line that existed at the base was removed from any test file (`git diff --numstat c6a1c95..HEAD -- tests/`: every test file shows 0 removed; `tests/run.py`, the runner, shows 3).

## 1. Shape

shape_change: accepted. shape_breadth: narrow.

- **Hint "a module was added" (`scripts/names`): this changes the shape, and the decision accepted it.**
  The decision record says "names.py is a leaf for name and command parsing".
- **Hint "an edge between modules was added" (`record → names`, `run → names`): this changes the shape, and the decision accepted it.**
  The edges go into the same leaf.
  The run-time subprocess `record → run.py land-scenario` (`scripts/record.py:824`) is also accepted ("record runs run.py land-scenario in a subprocess").
- **Nothing beyond the decision (`.xv/slices/2026-11-09-defects-tools.boundary.md`, unchanged; `git diff 39a1035..HEAD`).**
  Since pass 1, the commits touch only these files:
  - `.xv/picture.md`, `README.md:246`, `skills/watch/SKILL.md:104` and `CHANGELOG.md:7`;
  - two test files edited (`tests/test_from_build.py:1093`, `:1163`; `tests/test_briefs_picture.py:230`), and five test files with removals (`e9dea86`);
  - the decision record and slice files (`.xv/decisions/2026-11-09-2026-11-09-defects-tools.md`).
  No script changed, so there is no new module, edge, table or surface.
- The breadth is narrow, which matches the forecast's `"shape": "narrow"` (`.xv/slices/2026-11-09-defects-tools.md:13`).

## 2. Pitch

pitch_contradiction: no.

- I read `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code. It will never be a teapot."
- The pass-2 changes are docs, tests and the picture (`git diff 39a1035..HEAD`), made in a sortie by a person pairing with an agent. They serve the same users, and nothing there falls under `.xv/pitch.md:25`.

## 3. Moved tests

The rows from pass 1 still stand (`tests/run.py` and the build's seven files: added lines only, forced by points 1–15; the record's `moved_tests`, `.xv/slices/2026-11-09-defects-tools.md:17`).
The new moves since then:

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_from_build.py:1163` `test_the_report_takes_the_wall_baseline_at_the_base` | `assertEqual(baseline["commit"], self.record()["base"], …)` | `assertEqual(baseline["commit"], self.slice_base, …)`. `self.slice_base` is `git rev-parse HEAD` right after setUp's last commit (`tests/test_from_build.py:1093`) | "the old value was taken one commit too early (the maker's stop); the guardian asked for a value the tool does not supply" | Yes, point 1 ("takes the wall baseline at base"). The test now checks against a value from git, not one the tool supplies, so it does not assert less. The move is recorded (14:55:02), which closes pass 1's unrecorded-edit flag. |
| `tests/test_briefs_picture.py` `test_the_watch_brief_names_the_session_landing_and_the_wall_flag_forms` | `assertIn("xv land-scenario", text)` | `assertIn("run.py land-scenario", text)` | "bin/xv does not route land-scenario; Sean accepted naming it scripts/run.py land-scenario" | The decision forces it. Point 16's text still says `` `xv land-scenario` `` (`.xv/slices/2026-11-09-defects-tools.md:55`), and the decision says to name `scripts/run.py land-scenario` instead. I do not count this as a miss: naming `xv land-scenario` would document a command that `bin/xv` refuses. The scenario text was not amended, so a reader of the record sees two answers. |
| 16 build-added tests in `tests/test_recording.py`, `test_suite_runner.py`, `test_picture_lines.py`, `test_retro.py` and `test_record.py` (commit `e9dea86`) | present | removed | "restates a red test; the guardian recommended it slice-only and Sean accepted it" | Pass 1's §5 recommended exactly these 16, and Sean accepted them. Each restated a red test that is still present (see above). None was on the wall at the base: against the base, the files show 0 removed lines. |

`xv wall diff` flags only `tests/test_briefs_picture.py` as `fewer_assertions` (65 → 57).
The drop comes from the four slice-only removals. The wall baseline counts the build's tests: against the base, the file only gains lines (19 added, 0 removed).

Slice-only tests removed: `tests/test_briefs_picture.py` `test_readme_names_each_change`, `test_the_picture_names_the_build_commit_the_wall_flag_forms_and_the_landing_command`, `test_the_changelog_has_a_line_for_the_tool_fixes_under_unreleased` and `test_explore_notes_is_not_in_what_merges`. Kept: none.

The scenario agent's `may_not_files` allowed changes to:

- `.xv/picture.md` (point 16), and the change is there.
  Sean directed the rest of the picture edit in its own commit, `24b2df3`.

## 4. The picture

picture_change: no further edit.
Sean directed the pass-1 edits into `.xv/picture.md` (`24b2df3`), and I checked them against the tree:

- `.xv/picture.md:33-34`: "26 modules … `scripts/*.py` (23)" and "69 edges". The boundary lists 26 modules and 69 edges.
- `.xv/picture.md:41`, `:46` and `:175` name `names` and `names.covers_name_found`. `.xv/picture.md:144-145` say `scripts/run.py land-scenario` and "`bin/xv` does not route `land-scenario`".
- Every function the new lines cite exists (`.xv/picture.md:67`, `:225`):
  - `record.move_words` (`scripts/record.py:216`) and `record.cmd_report` (`scripts/record.py:807`);
  - `packet.note_crowded_picture_lines` (`scripts/packet.py:153`);
  - `orders.drop_edit` (`scripts/orders.py:420`).
- No `xv land-scenario` is left outside `.xv/slices/` (`grep -rn` over `*.md` and `*.py`).
- Each new line holds one sentence (`.xv/picture.md:41`, `:67`, `:129`, `:144-145`, `:225`).

## 5. The wall

No new recommendation.

- **For Sean, a record mismatch:** the record's `wall_recommendations` still shows `"accepted": false` for all 16 (`.xv/slices/2026-11-09-defects-tools.md:19`). The settled answer says "the wall recommendations are accepted" (`.xv/slices/2026-11-09-defects-tools.md:26`).
  - These 16 moves also have no `slice_only: true`, unlike the four earlier removals (`.xv/slices/2026-11-09-defects-tools.md:17`).
  - The tests are gone, so the suite is not affected. Only the record of which recommendations were accepted is wrong, so a retro would count all 16 as refused.
- I looked for wall tests that the scenario makes dead. I checked `tests/test_slice_rebase.py` against `.xv/picture.md:224` ("`git checkout -- <file>` drops it"), which still holds for tracked files. I also checked the single-value `--ignore` behaviour, which is unchanged. I found none to remove.
- The tests that pass 1 said to leave are still there: `SameMoveTest.test_the_same_assertion_in_two_files_is_two_moves`, and the class-form tests in `WallAnswerByFileTest` (`tests/test_record.py:994`).

## Door

**Door:** two-way. A revert undoes it; records opened meanwhile keep a `build.commit` key, which older code ignores. **Blast radius:** CLI.

## Raw data

- Slice record: `.xv/slices/2026-11-09-defects-tools.md`
- Diff: `git diff c6a1c95702e541b6b31ea7d49627e138d1e16a1b..af389fb` (since pass 1: `git diff 39a1035..af389fb`)
- Wall: `xv wall diff 2026-11-09-defects-tools`
- Boundary: `xv boundary --base c6a1c95702e541b6b31ea7d49627e138d1e16a1b` (`.xv/slices/2026-11-09-defects-tools.boundary.md`)
- Decision: `.xv/decisions/2026-11-09-2026-11-09-defects-tools.md`

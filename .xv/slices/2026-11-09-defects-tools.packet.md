---
slice: 2026-11-09-defects-tools
shape_change: yes
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 12
expected_moves: 0
door: two-way
blast_radius: CLI
---

# Packet: Rebase, session-mode red and wall-flag fixes from v0.5's tool gaps

**Needs a decision (two people; this repo runs solo, so Sean):** the shape change. It adds a module, `scripts/names.py`, and `record` now runs `run.py` in a subprocess. The breadth is narrow, the same as the forecast.
**For Sean as originator:** one test edit from the sortie with no move recorded for it, and an assertion that now compares the tool with itself (check 3). Also the picture edits (check 4), the wall recommendations (check 5), and the docs that name `xv land-scenario`, which `bin/xv` does not route.

## The scenario

There are 17 points (`.xv/slices/2026-11-09-defects-tools.md:39-55`):

- Session-mode `xv record report <id> scenario -` on a slice from a build lands the red, runs it at the base and on the build, and takes the wall baseline at the base. The next `xv step scenario` or `xv close` drops the checkout (1).
- A red that conflicts with the build stays on `refs/xv/<id>/red`, and the next scenario pass starts from it (2). `xv close` deletes the ref (3).
- `build.commit` is kept in the record, and a deleted build ref does not crash. With no build commit, the build's test files stay unrecorded (4).
- In session mode, a red joined unsafely is not kept (5).
- The rebase question says how to drop a new test file (6). A red file that main also changed keeps the slice's edits in the wall hash (8). A directed CHANGELOG edit replaces the old line after a rebase (9).
- `--accept-wall` and `--refuse-wall` take the forms the covers check takes. A bare name that two files share is refused (7).
- `tests/run.py` fails on a dropped file or on fewer tests run than collected (10).
- The cleaner reports `brief:` steps, and `retro counts` skips them (11). One move told twice is recorded once (12).
- `slice new` checks its paths first (13) and takes a repeating `--ignore` (14).
- The crowded-picture note: a second run leaves one note (15).
- The docs name what changed (16), and `EXPLORE-NOTES.md` stays out of what merges (17).

The slice may ignore:

- why `tests/run.py` dropped a file;
- rewriting old retro counts;
- looser move matching;
- diff3 markers that the maker sees.

## The recording

There is none; this slice is a set of tool defects stated in words.
Replay the red with the command in the record's `red.command` (`cd tests && python3 -m unittest test_from_build.SessionLandsTheRedTest …`).
Run the whole suite with `python3 tests/run.py --jobs 4`. On this run it ended "Ran 1178 tests in shard 1/1", "OK", with exit 0.

## The boundary picture

This is from `xv boundary` against `c6a1c95702e5`, as given (`.xv/slices/2026-11-09-defects-tools.boundary.md`).

- Modules touched: `scripts/names`, `orders`, `packet`, `record`, `retro`, `run`.
- Module added: `scripts/names`. None removed. No new outbound calls.
- Edges added: `scripts/record → scripts/names`, `scripts/run → scripts/names`. None removed.
- Tables: none. Surface paths: none added or removed.
- Shape hints: "a module was added", "an edge between modules was added".

## What the suite asserts after

In words: the new tests assert each of the 17 points.

- A session report on a build slice lands the red, runs it at the base and on the build, baselines the wall at the record's base, and keeps the red on its ref.
- `close` and the next scenario step drop the checkout, and `close` deletes `refs/xv/<id>/red`.
- A deleted build ref leaves the build's test files unrecorded instead of crashing.
- An unsafely joined red keeps the earlier red and stops.
- `rebase_conflict` names `rm` or `git rm -f` for a new file.
- After a rebase, the red file's edits stay in the wall hash, and a directed CHANGELOG edit replaces its line.
- The wall flags take `file::test` and the other covers forms, and refuse a shared bare name, naming each file.
- `tests/run.py` fails on a test file with no test and on fewer ran than collected.
- `brief:` lines are not counted.
- Moves that differ only by a comma or whitespace are one move.
- `slice new` refuses missing paths before it makes anything. Repeated `--ignore` values become bullets.
- The crowded-picture note is single, and it is stripped only at the start of a line.
- The briefs name the changes.

No old assertion was loosened. The only old file that lost lines is `tests/run.py`, which is the runner (`git diff --numstat`: 3 lines removed; every test file has 0 removed).

## 1. Shape

shape_change: yes. shape_breadth: narrow.

- **Hint "a module was added": this changes the shape.**
  `scripts/names.py` is new (`scripts/names.py:1-62`, "Name and command parsing that run.py and record.py both need (record does not import run)"). It holds `COVERS_SEPARATOR`, `covers_name_found` and `joined_unsafely`, moved out of `run.py` (the `scripts/run.py` hunks at `-1140,37` and `-1266,30`).
  The picture counts "25 modules, all flat Python files: `scripts/*.py` (22)" (`.xv/picture.md:33`), so this makes it 26 and 23.
  The picture already names `xvlib` as the home of "the shared test-name matcher `names_test`" (`.xv/picture.md:45`). The person decides whether a second shared home for name matching is wanted.
- **Hint "an edge between modules was added": this changes the shape, but only through the new module.**
  `record → names` and `run → names` are edges into a leaf with no imports of its own. `record` and `run` were already joined (`run → record`, `.xv/picture.md:37`), so no modules that were apart are now coupled through an import.
- **Not in the boundary picture, from the diff: `record` now runs `run.py`.**
  `scripts/record.py:820-826` is `subprocess.run([sys.executable, …"run.py"), "land-scenario", a.id], …)`, and its comment reads "record does not import run: the landing runs there".
  Until now the dependency ran one way (`run` imports `record`). At run time it now goes both ways. This is a new dependency direction, even though the import graph does not show it.
- **Surfaces users meet.** The CLI is the surface (`.xv/picture.md:193`).
  `--ignore` can now repeat (`scripts/record.py` and `scripts/run.py`, `action="append"`). The wall flags take new forms (`scripts/record.py:442`). The forecast expected both ("The expected shape change is the wall-flag forms and the repeating --ignore").
  A new subcommand, `land-scenario`, exists in `run.py` (`scripts/run.py:1841`), but `bin/xv` does not route it (`bin/xv:40-48`; the `COMMANDS` dict has no `land-scenario`). So it is not a user surface. The docs nonetheless call it `xv land-scenario` (check 4).
- **State.** The record gains `build.commit` (`scripts/run.py` hunk `-260,7`: `"commit": start`). It is a new key on an existing file, not a table.
- **Breadth.** The change is narrow: one leaf module, one subprocess edge, two CLI flag forms and one record key. That matches the forecast's `shape: narrow` (`.xv/slices/2026-11-09-defects-tools.md:13`). It is not wider.
- No decision on this slice accepts the shape (`decisions: []`, `.xv/slices/2026-11-09-defects-tools.md:27`), so the value is `yes`, not `accepted`.

## 2. Pitch

pitch_contradiction: no.

- I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot.").
- The change repairs the tool's own checks (wall, rebase, red landing). It serves the same people for the same purpose, and nothing in it does what `.xv/pitch.md:25` excludes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/run.py` (runner, 0 assertions) | Fails only when a worker fails | Also fails, naming the file, when a `test_*.py` gives no test id, and when the number of tests that ran is lower than the number collected (`tests/run.py:58-63`, `:84-86`) | "the build changed the runner for scenario point 10 (#154 item 3)" | Yes, point 10. It asserts more. |
| `tests/test_from_build.py` | 218 assertions | 262 | "the build … added tests …; no line at the base was changed or removed" | Yes, points 1–5. Removed lines against the base: 0. |
| `tests/test_record.py` | 455 | 480 | same | Yes, points 7 and 12. 0 lines removed. |
| `tests/test_slice_rebase.py` | 304 | 321 | same | Yes, points 6, 8 and 9. 0 lines removed. |
| `tests/test_recording.py` | 9 | 22 | same | Yes, points 13 and 14. 0 lines removed. |
| `tests/test_picture_lines.py` | 13 | 19 | same | Yes, point 15. 0 lines removed. |
| `tests/test_retro.py` | 59 | 60 | same | Yes, point 11. 0 lines removed. |
| `tests/test_suite_runner.py` | 20 | 25 | same | Yes, point 10. 0 lines removed. |
| `tests/test_from_build.py:1162` `test_the_report_takes_the_wall_baseline_at_the_base` (a red test, sortie commit 70bc825) | `assertEqual(baseline["commit"], self.main, …)` | `assertEqual(baseline["commit"], self.record()["base"], …)` | **No move names this edit.** The file's entry was recorded at 14:06:07, before the edit (70bc825 is 14:23 UTC), and it says "no line at the base was changed". The settled answer said "test edits are recorded as moves in Sean's name". | Yes, the old value was wrong (the maker's stop). **Flag:** the new assertion compares the tool's baseline with the tool's own record value. If both were wrong in the same way, it would still pass. The maker's other option, "HEAD of the repo after setUp", is an independent value. |

`tests/test_briefs_picture.py` drops from 65 to 57 assertions (`xv wall diff`: `fewer_assertions`). The drop is the four slice-only removals below. Against the base, the file only gained lines (19 added, 0 removed).

Slice-only tests removed: `tests/test_briefs_picture.py`: `test_readme_names_each_change`, `test_the_picture_names_the_build_commit_the_wall_flag_forms_and_the_landing_command`, `test_the_changelog_has_a_line_for_the_tool_fixes_under_unreleased`, `test_explore_notes_is_not_in_what_merges` (accepted at `slice_only_marks`; removed in sortie 5e05209). Kept: none.

The scenario agent's `may_not_files` allowed changes to:

- `.xv/picture.md`: line 104, the wall-flag forms; and lines 135–137, `xv close` deletes the ref, `build.commit`, the session landing (diff hunks `@@ -101,6` and `@@ -131,7`).

## 4. The picture

The change makes these lines untrue or incomplete. These are proposed edits; Sean accepts them.

- `.xv/picture.md:33-34`, "25 modules … `scripts/*.py` (22)" and "67 edges". Propose:
  - "26 modules, all flat Python files: `scripts/*.py` (23) and `evals/{run,grade,report}.py`."
  - Set the edge count from a regenerated `.xv/boundary-all.md`. The boundary picture adds two edges.
- `.xv/picture.md:37` and `:40`. Add a line:
  - "`names` holds `covers_name_found`, `COVERS_SEPARATOR` and `joined_unsafely`, which `record` and `run` both import."
- `.xv/picture.md:45` and `:165` say `run.covers_name_found`. Propose `names.covers_name_found`. `run` still re-exports it (`scripts/run.py:420`), but its home moved.
- `.xv/picture.md:137` names `xv land-scenario`, but `bin/xv` does not route that command (`bin/xv:40-48`). Typing it gives "unknown command". `README.md:246` and `skills/watch/SKILL.md:104` say the same. Propose:
  - "In session mode, `xv record report <id> scenario -` runs `scripts/run.py land-scenario` in a subprocess, which lands the red, runs it at the base and on the build, takes the wall baseline at the base, and drops the checkout."
  - "`bin/xv` does not route `land-scenario`."
- `.xv/picture.md:133`, "`build` (`none`, or `{kind: exploration, ref}`)". Propose `{kind: exploration, ref, commit}` (`scripts/run.py` hunk `-260,7`).
- `.xv/picture.md:159`, "A session scenario step makes that checkout and names it." Add:
  - "The next `xv step scenario` or `xv close` drops a checkout that no report landed (`scripts/run.py` hunks `-808` and `-1407`)."
- `.xv/picture.md:160`, the joined-red rule. Add:
  - "`xv record report` applies the same rule in session mode, with or without a build (`scripts/record.py` `cmd_report`)."
- `.xv/picture.md:63`, "One move is recorded once." Add:
  - "Two tellings that differ only in whitespace or commas are one move; `==` and `!=` stay two (`record.move_words`)."
- `.xv/picture.md:66`, "a second run replaces the note". Add:
  - "An old note is stripped only where it starts a line (`scripts/packet.py:158`)."
- `.xv/picture.md:122`, the runner. Add:
  - "It fails, naming the file, when a `test_*.py` gives no test, and when fewer tests ran than were collected."
- `.xv/picture.md:214` says "`git checkout -- <file>` drops it". Add:
  - "For a file the maker added, the question names `rm <file>` or `git rm -f <file>` and says `git status` shows it and `git diff` does not (`orders.drop_edit`)."
- `.xv/picture.md:54-56`, the rebase. Add:
  - "`xv slice rebase` runs git with `merge.conflictStyle=diff3`, and keeping both sides drops a base line that the other side edited."
  - "A red file that both sides changed is hashed at the replayed baseline commit (`scripts/run.py` hunks `-339` and `-615`)."
- The new behaviour of `tests/run.py` also bears on decision 12 (`.xv/picture.md:290`). The new ran-versus-collected check (`tests/run.py:84`) fails a run in which a class skips in `setUpClass` with `unittest.SkipTest`, because its tests never count as run (`tests/test_tests_run.py`, `SKIPPED_CLASS`). No test in this suite does that today (`grep SkipTest tests/` finds only strings in `test_record.py:2106-2109`). An adopter's or a future test that skips a whole class this way will turn the suite red. The picture should say so, so that it is a known rule and not a surprise.

## 5. The wall

These are restatements: tests the build added that restate a red test asserting the same thing. Each recommendation is `mark slice-only`, and the red test stays on the wall.

- `tests/test_recording.py` `SliceNewMissingFileTest.test_a_missing_recording_path_makes_no_worktree_and_no_branch` and `.test_a_missing_scenario_file_makes_no_worktree_and_no_branch`. They restate `tests/test_run.py` `SliceNewInputsTest.test_a_missing_recording_path_is_refused_before_any_branch_or_worktree` and `…scenario_file…`: same refusal, no branch, no worktree.
- `tests/test_recording.py` `SliceNewIgnoreRepeatTest.test_more_than_one_ignore_is_a_bullet_list_one_per_value_in_order`, `.test_a_single_ignore_works_as_before` and `.test_every_ignore_value_reaches_the_record_in_order`. They restate `tests/test_run.py` `test_a_repeated_ignore_gives_a_bullet_list_in_order` (an exact equality, which covers the order) and `test_a_single_ignore_stays_a_plain_paragraph`.
- `tests/test_suite_runner.py` `RunnerTest.test_a_test_file_that_gives_no_test_fails_the_run_and_is_named`. It restates `tests/test_tests_run.py` `TestsRunGuardsTheSuiteTest.test_a_test_file_that_gives_no_test_fails_the_run_and_is_named`, a helper-only file named in the output. `test_a_worker_that_exits_early_with_zero_fails_the_run` is a different case (`os._exit(0)`); leave it.
- `tests/test_picture_lines.py` `test_running_the_note_twice_leaves_exactly_one_note_naming_the_current_lines` and `test_the_old_note_is_stripped_only_at_the_start_of_a_line`. They restate `tests/test_packet.py` `CrowdedPictureNoteTest.test_a_second_run_leaves_exactly_one_note` and `test_a_note_quoted_inside_a_line_is_not_stripped`.
- `tests/test_retro.py` `test_a_step_the_brief_names_is_not_counted_as_a_rule_but_a_standard_is` (mocked `records`). It restates `ReworkSignalTest.test_counts_skip_a_brief_line_and_count_a_standard_by_its_heading`, the same rule end to end.
- `tests/test_record.py` `SameMoveTest.test_two_tellings_that_differ_by_a_comma_are_one_move`, `.test_two_tellings_that_differ_by_spacing_are_one_move` and `.test_equal_and_not_equal_are_two_moves`. They restate `SameMoveTwiceTest` (`test_a_dropped_comma_is_the_same_move`, `test_a_dropped_space_is_the_same_move`, `test_an_equal_and_a_not_equal_are_two_moves`). `test_the_same_assertion_in_two_files_is_two_moves` is new; leave it.
- `tests/test_record.py` `WallAnswerByFileTest.test_file_and_test_accepts_only_that_recommendation`, `.test_a_bare_name_two_files_share_is_refused_and_names_the_files`, `.test_a_bare_name_only_one_recommendation_has_is_still_taken` and `.test_an_ambiguous_name_in_the_hash_form_is_still_refused`. They restate `WallFlagFormsTest.test_file_then_test_picks_one_of_two_files_that_share_a_name`, `…refused_and_the_refusal_names_each_file_and_test`, `test_a_bare_name_still_works_when_one_recommendation_has_it` and `test_a_bare_name_two_files_share_is_refused_for_refuse_wall_too`.
  - The last one is misnamed: it passes a bare `test_same` to `--refuse-wall`, not a hash form (`tests/test_record.py:1092-1096`).
  - The class-form tests in `WallAnswerByFileTest` (colons, hash, dots, arrow) read the class from the file (`with_files`), while `WallFlagFormsTest` reads it from the recommendation's test text. That is a different path through `record.wall_matches` (`scripts/record.py:454-456`); leave them.

I looked for wall tests that the scenario makes dead. The picture's "`git checkout -- <file>` drops it" (`.xv/picture.md:214`) still holds for tracked files (`orders.drop_edit`), and the old single-`--ignore` behaviour is unchanged for one value. I found none to remove.

## Door

**Door:** two-way. A revert undoes it. The only leftover is a `build.commit` key in records opened meanwhile, which older code ignores. **Blast radius:** CLI.

## Raw data

- Slice record: `.xv/slices/2026-11-09-defects-tools.md`
- Diff: `git diff c6a1c95702e541b6b31ea7d49627e138d1e16a1b..d03306d`
- Wall: `xv wall diff 2026-11-09-defects-tools`
- Boundary: `xv boundary --base c6a1c95702e541b6b31ea7d49627e138d1e16a1b` (`.xv/slices/2026-11-09-defects-tools.boundary.md`)

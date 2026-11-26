---
slice: 2026-11-25-test-remove
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 21
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet: Taking the inspector's advice to remove a test removes it: --test-remove (#202)

No stop for two people. Three things need a decision from the originator:
- `--test-remove` works only when the recommendation says exactly `remove`, and the inspector brief never fixes that word (check 1, finding A).
- Removing the only test in a class looks like it gets through and leaves a broken file (finding B).
- The picture edit in check 4.

The changed watch brief also needs a second name on its CHANGELOG line (binding decision 1).

## The scenario

At `moves_to_accept`, `xv record answer --test-remove <test>` takes the inspector's advice and removes the whole test, with its decorators, from its file. It uses the same check as a `test-remove` directed edit (1).
The answer commits the removals and runs the suite (2).
A test already gone from its file is skipped. A test that cannot be removed cleanly makes the answer refused, and nothing is removed or recorded (3).
A test the answer does not name stays in its file (4).
`--accept-wall` and `--refuse-wall` still work. Each warns, naming the new way and #216. The watch brief and the README name only the new way (5).
Each test that a past record lists as accepted for removal, and that is still in its file, is removed. The originator settled that this is a one-time cleanup (6).
There is a CHANGELOG line. The originator settled that it has no test (7).
May ignore: a wall recommendation at any stop other than `moves_to_accept`.

## The recording

None; the slice starts from words. Replay the red and the green with `cd tests && python3 -m unittest test_record.TestRemoveFlagTest`. I ran it at HEAD `ba851c4`: 10 tests, OK. The red at `8b26373` failed 12 of 13; the 3 slice-only tests were removed later. I did not re-run the whole suite. The record says it is green: 1521 tests, cleaner pass.

## The boundary diagram

From `.xv/slices/2026-11-25-test-remove.boundary.md`, as given. Touched: `scripts/record`. Modules added or removed: none. Edges added or removed: none. Tables: none. Surface paths: none. Shape hints: none. The one user-facing change is a new CLI flag, `--test-remove`, on `xv record answer` (`scripts/record.py:1446`).

## What the suite asserts after

`TestRemoveFlagTest` (10 tests, `tests/test_record.py`) asserts:
- `--test-remove` removes the whole test with its decorators, commits it and runs the suite.
- A test already gone is skipped.
- An unclean removal is refused with nothing removed.
- A recommendation other than `remove` is refused.
- The flag is refused on another stop.
- A test the answer does not name stays.
- `--accept-wall` does what `--test-remove` does, and `--refuse-wall` does what unmark does; each warns.

15 older tests were removed under outcome 6, and 3 slice-only tests were removed by the cleaner.

## 1. Shape

shape_change: no. shape_breadth: narrow.
The boundary diagram shows no new module, edge, table or surface path, and lists no shape hints.
The change stays inside `scripts/record.py`: new `test_block` and `removal_edits` (`scripts/record.py:549-599`), and `make_directed_edit` now takes a list of edits (`scripts/record.py:757`).
That matches the forecast's `shape_note`: "one new flag on record answer that reuses the directed-edit removal check".
`removal_edits` calls `check_edit` with kind `test-remove` (`scripts/record.py:597`), which is the reuse the forecast expected.

Findings for the person (inside the shape; neither stops the change):
- **A. The `remove` word is not fixed anywhere an inspector reads** (`scripts/record.py:622`, `skills/inspector/SKILL.md:28`).
  `scripts/record.py:622`: `if recs[i].get("recommend") != "remove": raise XVError(... "the inspector did not recommend removing it")`.
  The inspector brief fixes only `mark slice-only` as an exact value. For removal it just says "a test that was on the wall before the slice should be removed" (`skills/inspector/SKILL.md:28`).
  An inspector that writes `"recommend": "remove from the wall"` makes `--test-remove` refuse its own advice.
  The tests use exactly `"remove"` (`tests/test_record.py:2860`), so they do not catch this.
  The same brief line still says `xv record answer --accept-wall` lists the test in `slice_only`, which names the deprecated flag.
  Changing that brief needs two people (`.xv/picture.md:348`, decision 1).
- **B. Removing the only test in a class looks like it is not refused** (`scripts/record.py:420-421`).
  `is_whole_test` accepts a block when the next non-blank line is at a lower indent (`scripts/record.py:420-421`), and `test_block` stops there (`scripts/record.py:567-574`).
  So removing a class's only method leaves `class X(...):` with no body, which Python cannot parse.
  The removal is committed, then the suite runs red. Outcome 3 says such a test "makes the answer refused, and nothing is removed".
  I found this by reading the code and did not run it. The maker hit the same case by hand and fixed it with `pass` (`tests/test_codex_step.py:94-95`).

## 2. Pitch

pitch_contradiction: no.
The pitch says: "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." (`.xv/pitch.md:25`).
The change makes a person's explicit answer carry out a removal they already accepted. It serves the same users, and it breaks no promise I found in `.xv/pitch.md`.
Binding decision 1 (`.xv/picture.md:348`): a change to a brief needs two people and a CHANGELOG line.
The watch brief changed (`skills/watch/SKILL.md:63`), and the CHANGELOG line names one person: "decided by Sean Kennedy" (`CHANGELOG.md:7`).
By `CHANGELOG.md:3`, "A version line without two names is a draft." It needs a second name before merge.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_agent_names.py | test_explore_notes_is_not_in_the_tree | removed | outcome 6 | yes; accepted for removal in an earlier record (checked) |
| tests/test_agent_names.py | test_no_brief_or_doc_opens_with_the_old_line | removed | outcome 6 | yes (checked) |
| tests/test_agent_names.py | test_boundary_picture_is_boundary_diagram | removed | outcome 6 | yes (checked) |
| tests/test_briefs_picture.py | test_the_changelog_does_not_say_the_maker_may_change_any_named_may_not_file | removed | outcome 6 | yes per the record; I did not find the earlier acceptance with my search |
| tests/test_cleaner_commit.py | test_the_brief_no_longer_tells_the_cleaner_to_commit_its_fix | removed | outcome 6 | yes (checked) |
| tests/test_cleaner_commit.py | test_the_readme_no_longer_says_the_pre_commit_hook_refuses_the_cleaners_unrecorded_move | removed | outcome 6 | yes (checked) |
| tests/test_codex_step.py | test_the_note_says_the_brief_is_not_the_whole_prompt_because_agents_md_and_skills_load | removed | outcome 6 | yes per the record; not found by my search |
| tests/test_codex_step.py | test_relies_on_has_a_line_for_the_codex_event_shape | removed; `CodexDocsTest` body is now `pass` | outcome 6 | yes per the record; not found by my search |
| tests/test_record.py | SliceOnlyAssertionFormTest.test_a_name_that_is_in_no_file_when_the_step_began_is_refused_and_nothing_is_recorded | removed | outcome 6 | yes (checked) |
| tests/test_record.py | SliceOnlyAssertionFormTest.test_each_form_of_a_name_is_taken | removed | outcome 6 | yes (checked) |
| tests/test_record.py | SliceOnlyAssertionFormTest.test_a_name_followed_by_a_note_in_brackets_is_taken_whichever_bracket | removed | outcome 6 | yes (checked) |
| tests/test_record.py | RemovalCheckNamesTest.test_none_of_the_inputs_passes_while_the_test_is_still_in_its_file | removed | outcome 6 | yes (checked) |
| tests/test_run.py | test_an_empty_covers_on_the_first_pass_still_stops | removed | outcome 6 | yes per the record; not found by my search |
| tests/test_run.py | RemovalNotMadeTest.test_a_slice_only_move_whose_assertion_names_a_double_colon_test_still_there_stops | removed | outcome 6 | yes (checked) |
| tests/test_suite_runner.py | test_ci_shards_run_at_the_same_time | removed | outcome 6 | yes per the record; not found by my search |

Each of these removals asserts less, and each is recorded. `xv wall diff` shows fewer assertions in all 7 files, with nothing unrecorded (record `checks.cleaner.wall.ok: true`).
The removals follow the originator's answer at `red_misses_scenario` (pick 1): "the tests that past slice records list as accepted for removal ... are removed".
"(checked)" means I found the test with `"accepted": true` in an earlier slice record. My search found 10 of the 15; the other 5 need a look from someone.
`tests/test_codex_step.py:91-95` leaves four blank lines and an empty `class CodexDocsTest(unittest.TestCase): pass`. No test remains in it.

Slice-only tests removed: test_the_tests_past_slices_accepted_for_removal_are_gone_from_their_files, test_the_watch_brief_and_the_readme_name_only_the_new_way, test_the_changelog_has_a_line_for_test_remove (all `tests/test_record.py`). Kept: none.
Changes to may-not files that the test writer allowed (`may_not_files_needed`): none.

## 4. The picture

`.xv/picture.md:147-150` is now incomplete. It says "Only a person's `--accept-wall <test>` accepts one, and only `--refuse-wall <test>` takes back one" and "Both flags take the test with its file".
It also says a refusal is given for "both on one test". The message is now "is both accepted and refused" (`scripts/record.py:625`), and it also covers `--test-remove` with `--refuse-wall`.
Proposed edit, replacing line 147 and adjusting 148-150:

```
  A person's `--test-remove <test>` takes a `remove` recommendation and removes the whole test, with its decorators, from its file, using the `test-remove` directed-edit check, in its own commit, then runs the suite.
  A named test already gone from its file is skipped; one that cannot be removed whole refuses the answer, and nothing is removed.
  `--accept-wall` and `--refuse-wall` are deprecated (#216) and print a warning naming the new way; `--accept-wall` on a `remove` recommendation removes the test as `--test-remove` does.
  An accepted `mark slice-only` recommendation is listed in `slice_only`, and refusing it later takes it out, matched on file and test; a new recommendation not named is refused, and an agent's report sets neither.
  The flags take the test with its file, in the forms the coverage check takes (`file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`); a bare name that two files share is refused, and the refusal names each `file::test`.
  Giving any of them on another kind of stop, or accepting and refusing one test in one answer, is refused.
  Each answered `moves_to_accept` stop keeps `accepted_wall` (which includes `--test-remove` names) and `refused_wall`.
```

Note: the current line 147 has more than one sentence's worth of clauses joined by semicolons. The proposed lines keep the house style but could be split further.

## 5. The wall

No recommendations.
I looked at:
- the 10 tests left in `TestRemoveFlagTest` (`tests/test_record.py`, added before the wall baseline `efc6d63`);
- the 3 slice-only marks (all accepted and removed);
- the old tests about `--accept-wall` and `--refuse-wall` that are still on the wall.
The deprecated flags still work, and `test_accept_wall_does_what_test_remove_does_and_warns` and `test_refuse_wall_does_what_unmark_does_and_warns` guard that, so none of these is dead.
Those two tests will become dead when #216 removes the flags, not in this slice.

## Door

**Door:** two-way. The code and the 15 test removals are git commits, and a revert brings them back. **Blast radius:** low.

## Raw data

- Slice record: `.xv/slices/2026-11-25-test-remove.md`
- Diff: `git diff 911f113209115d8a4e586a9f3d6efd095926baef..ba851c4aae2896f4aae1c9b773441a1a02f2ee46`
- Wall: `xv wall diff 2026-11-25-test-remove`
- Boundary: `xv boundary --base 911f113209115d8a4e586a9f3d6efd095926baef`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:233.

---
slice: 2026-10-30-covers-list
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 3
door: two-way
blast_radius: narrow
---

# Packet: A covers item may name more than one test

Nothing here stops the change for two people. The merge is Sean's. He has three things to decide: the picture edit (section 4), two slice-only marks he has not yet accepted (section 5), and the three slice-only removals (section 3). The two gaps sent back at the last stop are closed (below). I found no new gap that lets a covers name pass when it should stop.

**The gaps from the last two rounds, checked at HEAD `29b40b4`:**

- Empty test part. `scripts/run.py:557-558` now has `if not test.strip(): return False`, and it runs after both the `::` split and the `.` split. So `tests/test_red.py::`, `Red.` and `tests.test_red.Red.` match nothing, and the stop names them. Covered by `tests/test_run.py:381-395`.
- Brief and CHANGELOG. `skills/scenario/SKILL.md:61` and `CHANGELOG.md:7` now describe the non-string list item, the module prefix and the empty test part. The scenario's second amendment asked for this (slice record, lines 59-60).

**Edges on the strict side (they stop, they never pass). For information only:**

- The pytest form `file::Class::test` splits at its last `::` (`scripts/run.py:549`). The file part is then `tests/x.py::Class`, which is not a red file, so the slice stops. The scenario names only `file::test_name`.
- `module.test_function`, a module and a function with no class, reads its module as a class (`scripts/run.py:552-553`). That class is not found, so the slice stops.

**Outside the scenario. This was already true on main:** the last part of a name is matched as any whole word in a red file, not as a test definition (`scripts/run.py:559-560`, `(?<!\w)…(?!\w)`). So a covers `test` of `unittest` or `self` passes. `.xv/picture.md:26` describes it this way ("matches no whole word"). The slice does not widen it.

## The scenario

A covers item may name more than one test (#92). A `covers` item's `test` may be one name or a list. A string that joins names with `,` or `;` is read as that list. Each name must match a whole test name in a red file. The brief's example shows the list form, and `CHANGELOG.md` gets a line.

There are three amendments, all by Sean:

1. `Class.test_name` and `file::test_name` match only when both parts do.
2. A list item that is not a non-empty string stops. A module-prefixed dotted name matches only when the module is a red file that has the class and the test.
3. A name whose test part is empty after `::` or after the last dot stops. The brief and the CHANGELOG describe the amended behaviours.

May ignore: none.

## The recording

None; this is a feature. To replay: `cd tests && python3 -m unittest test_check test_run`. The round-three red failed before the maker (10 failures; see the record's scenario report). I re-ran it at HEAD `29b40b4`: 168 tests, OK. The record shows the whole suite green after the cleaner: 597 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-30-covers-list.boundary.md`, as given. It touches one module, `scripts/run`. Modules, edges, outbound calls, tables and surface paths: none added, none removed. Shape hints: none (`"shape_hints": []`).

## What the suite asserts after

- A list of names goes on to the maker when every name is a whole name in a red file. The slice stops, and the stop names the name, when the list is empty, when a name is in no red file, or when a name is only part of a longer name (`tests/test_run.py:309-324`).
- A string joined with `,` or `;` goes on to the maker when every name is found. If one name is missing, the slice stops and names it (`tests/test_run.py:325-336`).
- These go on to the maker: `Red.test_milk_today`, `tests/test_red.py::test_milk_today` and `tests.test_red.Red.test_milk_today`. These stop: a wrong class, a file or module that is not a red file, and a red file that lacks the test (`tests/test_run.py:337-380`).
- A list holding a number, `null` or `""` stops (`tests/test_run.py:354-365`).
- An empty test part stops whether it comes after `::`, after a dot, or after a red module and class, alone or in a list (`tests/test_run.py:381-395`).
- The brief's example has a `"test": [..]` list (`tests/test_check.py:57-60`).
- The old covers tests (`tests/test_run.py:267-299`) are unchanged.

## 1. Shape

shape_change: no.

- The boundary picture has no new module, edge, table, outbound call or surface, and no shape hints (`.xv/slices/2026-10-30-covers-list.boundary.md:12-13,18-19,108-114,406`).
- The diff adds two helpers inside `run.py`, `covers_names` and `covers_name_found` (`scripts/run.py:538-565`).
- `red_file_texts` now returns a dict keyed by path. Its other caller, `scenario_red_gaps`, takes `.values()` (`scripts/run.py:576`). This stays inside the check the picture already places in `run` (`.xv/picture.md:26`).
- `skills/scenario/SKILL.md:56,61` edits an existing surface and adds none (`.xv/picture.md:27`).

shape_breadth: narrow, as the forecast expected ("narrow": the brief, one check, and a CHANGELOG line).

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:23-25`: "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." The change makes an existing stop accept more forms and serves the same users. It breaks no promise in the pitch. Binding decision 1, "needs two people" (`.xv/picture.md:63`), is met under `seats.two_people: solo` (`.xv/picture.md:55`, `.xv/config.yml:48`), and the CHANGELOG line says "solo".

## 3. Moved tests

`xv wall diff 2026-10-30-covers-list` reports one changed file: `tests/test_check.py`, 18 assertions before and 12 after. Its baseline is `4ff1d70`, a commit inside this slice. Against the slice base `f9c5cb1`, `tests/test_check.py` only gains a test (`tests/test_check.py:57-60`). The three tests removed were written within this slice and were never on main. All three moves are recorded (`moved_tests`, by the cleaner).

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_check.py | `test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test` | removed | Reads only `## Unreleased`; breaks at the release (accepted by Sean) | Yes. It is a one-time line, and the mark was accepted at `accept_moves` |
| tests/test_check.py | `test_the_changelog_line_says_a_non_string_list_item_and_a_module_prefix_are_checked` | removed | Reads only `## Unreleased`; breaks at the release | Yes. It guards the one-time line that amendment 3 asked for |
| tests/test_check.py | `test_the_brief_says_a_non_string_list_item_and_a_module_prefix_are_checked` | removed | Guards one-time wording in the brief's covers paragraph | Partly. The brief paragraph (`skills/scenario/SKILL.md:61`) lasts, and after the removal nothing in the suite asserts that it describes the amended behaviours |

Slice-only tests removed: the three above, all in `tests/test_check.py`. Kept: none.

## 4. The picture

`.xv/picture.md:26` says "`covers` empty or with an item that names no test, or a `covers` test that matches no whole word in any red file." That is now incomplete. Proposed edit:

> "`covers` empty, or with an item whose `test` is not one name, a list of non-empty strings, or a string joined with `,` or `;`, or a `covers` name that matches no whole word in any red file. `Class.test`, `module.Class.test` and `file::test` match only when the file or module is a red file and the class is in a red file that has the test. A name whose test part is empty stops. The stop names the name that does not match."

## 5. The wall

- `tests/test_check.py`, `test_the_changelog_line_says_a_non_string_list_item_and_a_module_prefix_are_checked`: stay off the wall. It is in the record's `slice_only` list and reads only `## Unreleased`, so it breaks at the release. It is not yet in any `accepted_wall`.
- `tests/test_check.py`, `test_the_brief_says_a_non_string_list_item_and_a_module_prefix_are_checked`: stay off the wall. It is in the record's `slice_only` list and guards one-time wording in the brief. It is not yet in any `accepted_wall`.

I also looked at the 27 new tests in `tests/test_run.py:309-395` and the brief-example test at `tests/test_check.py:57-60`. Each guards behaviour that lasts, and none only restates another. No test that was on the wall before the slice is made dead: the old covers tests at `tests/test_run.py:267-299` still describe live behaviour.

## Door

**Door:** two-way. A revert restores the single-name check and the old brief example. A single string name still reads the same way, so old records still pass. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-covers-list.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..29b40b4`. This round only: `git diff 269f466..29b40b4`
- Wall: `xv wall diff 2026-10-30-covers-list`
- Boundary: `xv boundary --base f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5` (`.xv/slices/2026-10-30-covers-list.boundary.md`)

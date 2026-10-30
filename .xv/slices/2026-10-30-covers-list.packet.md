---
slice: 2026-10-30-covers-list
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: narrow
---

# Packet: A covers item may name more than one test

Nothing here stops the change for two people. Sean, as the person who set the work going, has three things to decide. The first is one gap where a covers name that names no test still goes on to the maker (just below). The second is the picture edit (section 4). The third is the CHANGELOG line, which does not yet describe the two amended behaviours (section 4).

**A gap worth a decision (not a stop):**

- **A dotted or `::` name with nothing after the separator passes.** In `scripts/run.py:549-561`:
  ```
  where, _, test = name.rpartition("::")
  ...
  module, _, test = name.rpartition(".")
  ...
  whole = re.compile(r"(?<!\w)" + re.escape(test) + r"(?!\w)")
  ```
  For `tests/test_red.py::` or `Red.`, `test` is `""`. The pattern then becomes `(?<!\w)(?!\w)`, which matches between any two non-word characters, such as the `):` in `def test_milk_today(self):`. So `tests/test_red.py::` goes on whenever that file is a red file, and `Red.` goes on whenever `class Red` is in a red file. Neither one names a test. I found this by reading the code; I did not run it, and no test covers it. It goes against `.xv/picture.md:74` ("A check whose input is broken … stops for a person; it never passes"), and against scenario point 1: "Each name must match a whole test name in a red file." It is the same kind of gap Sean sent back at the last `accept_moves` stop (binding decision 12).
- Edge, on the strict side (it stops, it does not pass): the pytest form `file::Class::test` splits at its last `::` (`scripts/run.py:550`). The file part then becomes `tests/x.py::Class`, which matches no red file, so the slice stops. The scenario names only `file::test_name`, so this is outside the scenario. It costs a stop on pytest repos.

## The scenario

A covers item may name more than one test (#92). In the scenario report, a `covers` item's `test` may be one name or a list. A string that joins names with `,` or `;` is read as a list. Each name must match a whole test name in a red file.

Amended (1): `Class.test_name` and `file::test_name` match only when both parts do. Amended (2), at the last guardian stop: a list item that is not a non-empty string stops before the maker (binding decision 12), and a dotted name with a module in front (`tests.test_store.Red.test_x`) matches only when the module is a red file that has the class and the test. The brief's example shows the list form, and `CHANGELOG.md` gets a line. May ignore: none.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest test_check test_run`. The second-round red failed at `2e6dcc0`: 3 failures on the code then, per the record's scenario report. I re-ran it at HEAD `269f466`: 161 tests, OK. The record shows the whole suite green after the maker and after the cleaner (590 tests).

## The boundary picture

From `.xv/slices/2026-10-30-covers-list.boundary.md`, as given: one module touched, `scripts/run`. No modules, edges, outbound calls, tables or surface paths were added or removed, and there are no shape hints.

## What the suite asserts after

- A list of names goes on to the maker when every name is a whole test name in a red file. If one name is missing, or is only part of a longer name, the slice stops and the stop names it. An empty list stops.
- A list holding a number, `null` or `""` stops (`tests/test_run.py:354-364`).
- A string joined with `,` or `;` goes on to the maker when every name is found. When one is missing, it stops and names that name.
- `Red.test_milk_today` and `tests/test_red.py::test_milk_today` go on to the maker. These stop: a wrong class, a file that is not a red file, and a red file that lacks the test.
- `tests.test_red.Red.test_milk_today` goes on to the maker. These stop: a module that is not a red file, a red module with the wrong class, and a red module and class with a test the file lacks (`tests/test_run.py:366-379`).
- The brief's example has a `"test": [..]` list. The CHANGELOG's Unreleased section has a #92 line that names covers and Sean.
- The old covers tests (`tests/test_run.py:267-299`) are unchanged.

## 1. Shape

shape_change: no. The boundary picture has no new module, edge, table, outbound call or surface, and no shape hints. The diff adds two helpers inside `run.py`: `covers_names` and `covers_name_found` (`scripts/run.py:538-563`). It also changes `red_file_texts` to return a dict keyed by path, and its one other caller, `scenario_red_gaps`, is updated (`scripts/run.py:574`). That is all inside the check the picture already places in `run` (`.xv/picture.md:26`). `skills/scenario/SKILL.md:56,61` edits an existing surface (`.xv/picture.md:27`) and adds none. shape_breadth is narrow, as forecast ("narrow").

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code." The change serves the same users (`.xv/pitch.md:21`) and breaks no promise in the pitch.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-30-covers-list` reports nothing changed, deleted or added, and no test with fewer assertions. The record's `moved_tests` is `[]`. Every hunk under `tests/` only adds lines (`tests/test_run.py:301-380`, `tests/test_check.py:57-68`).

Slice-only tests removed: none. Kept: `tests/test_check.py` `test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test`. It stays in the suite but off the wall. It guards this slice's CHANGELOG line until the release, and Sean accepted the mark at `accept_moves`.

## 4. The picture

- `.xv/picture.md:26` says "`covers` empty or with an item that names no test, or a `covers` test that matches no whole word in any red file." That is now incomplete. Proposed edit: "`covers` empty, or with an item whose `test` is not one name, a list of non-empty names, or a string joined with `,` or `;`, or a `covers` name that matches no whole test name in any red file. `Class.test`, `module.Class.test` and `file::test` match only when the file or module is a red file and the class is in a red file that has the test. The stop names the name that does not match."
- Not the picture, but the same evidence. `CHANGELOG.md:7` describes round one only. It says nothing about a non-string list item stopping or about a module prefix. `skills/scenario/SKILL.md:61` doesn't mention the `module.Class.test` form either, though the brief's own red command example uses dotted modules (`tests.test_expiring`, `skills/scenario/SKILL.md:54`). `.xv/picture.md:63` asks for a CHANGELOG line for a change to a check. The line exists, but it is behind the code.

## 5. The wall

- `tests/test_check.py`, `test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test`: stay off the wall. It reads only `## Unreleased` (`tests/test_check.py:65`) and guards a one-time CHANGELOG line, so it breaks at the release. Sean accepted this mark (`accepted_wall` in the record).

I also looked at the 19 new tests in `tests/test_run.py:309-379` and the brief-example test at `tests/test_check.py:57-60`. Each one guards behaviour that lasts, so I make no recommendation for them. No test that was on the wall before the slice is made dead.

## Door

**Door:** two-way. A revert restores the single-name check and the old brief example. A single string name still works, so old records still read. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-covers-list.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..269f466`. This round only: `git diff 2e6dcc0..269f466`.
- Wall: `xv wall diff 2026-10-30-covers-list`
- Boundary: `xv boundary --base f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5` (`.xv/slices/2026-10-30-covers-list.boundary.md`)
- The record says the cleaner did not commit (`checks.cleaner.committed: false`). Its `red_file_texts` change is in fact in `269f466`, "record the cleaner's pass" (`git show 269f466 -- scripts/run.py`).

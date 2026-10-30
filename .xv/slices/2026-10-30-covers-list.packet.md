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

Nothing here stops the change for two people. Sean, as the person who set the work going, decides three things: the picture edit (section 4), the CHANGELOG test's wall mark (section 5), and two gaps where the check lets through a covers name it should stop (just below).

**Gaps worth a decision (not stops):**

- **A list item that is not a string gets dropped, and the check passes.** `scripts/run.py:540-543`:
  ```
  parts = test if isinstance(test, list) else ...
  names = [p.strip() for p in parts if isinstance(p, str)]
  return names if names and all(names) else []
  ```
  `"test": ["test_milk_today", 5]` (or `null`) reads as `["test_milk_today"]` and goes on to the maker. `"test": ["test_milk_today", ""]` stops. The binding rule says broken input stops: `.xv/picture.md:74` "A check whose input is broken or that cannot run stops for a person; it never passes." No red test covers a non-string item.
- **A dotted name with a module in front matches on the class alone.** `scripts/run.py:551-553`:
  ```
  elif "." in name:
      klass, _, test = name.rpartition(".")
      klass = klass.rpartition(".")[2]
  ```
  `tests.test_store.Red.test_milk_today` goes on to the maker even though `test_store` is not a red file. The amendment says "A name with the right test under the wrong class or file does not match" (slice record, "Amended 2026-10-30"). This repo's own red command writes names in that dotted form (`test_run.WatchLoopTest`). The scenario only names `Class.test_name`, so this is a gap at the edge of the scenario, not a miss inside it.

## The scenario

A covers item may name more than one test (#92). In the scenario report, a `covers` item's `test` may be one name or a list of names, and each name must match a whole test name in a red file. A string that joins names with `,` or `;` is read as that list. Sean's amendment: `Class.test_name` or `file::test_name` matches only when both parts do. The file must be a red file that has the test, and the class must be in a red file that also has the test. The brief's report example shows the list form, and `CHANGELOG.md` gets a line. May ignore: none.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest test_run.WatchLoopTest test_check.ScenarioBriefTest`. It failed at `c5380d7` (7 failures, slice record `checks.scenario.red_output`) and passes at HEAD `4d544a6`: I re-ran it, 59 tests, OK. The record shows the whole suite green after the maker and after the cleaner (576 tests).

## The boundary picture

From `.xv/slices/2026-10-30-covers-list.boundary.md`, as given: touched `scripts/run`. Modules added and removed: none. Edges added and removed: none. Outbound calls added: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- A covers `test` given as a list goes on to the maker when every name is a whole test name in a red file. It stops, naming the name, when one name is in no red file or is only part of a longer name. An empty list stops.
- A string joined with `,` or `;` goes on to the maker when every name is found, and stops naming the missing one when one is not.
- `Red.test_milk_today` goes on to the maker, and `Ghost.test_milk_today` stops. `tests/test_red.py::test_milk_today` goes on to the maker. `tests/test_store.py::…` (not a red file) stops, and so does `tests/test_red.py::test_cheese_ghost`.
- The scenario brief's report example has a `"test": [ "…", "…" ]` list. `CHANGELOG.md`'s Unreleased section has a #92 line naming covers and Sean.
- The old covers tests (`tests/test_run.py:267-299`) are unchanged, so the single-name, missing, empty and part-of-a-longer-name stops still hold.

## 1. Shape

shape_change: no. The boundary picture has no new module, edge, table, outbound call or surface, and no shape hints. The diff touches only `scripts/run.py` inside `unreadable_input` and `red_file_texts`, plus two new helpers in the same file (`scripts/run.py:527-560`). That is all inside the `run` module the picture already describes (`.xv/picture.md:26`, "`red_misses_scenario` stops … when the check cannot read its input"). `skills/scenario/SKILL.md:56,61` changes the text of an existing surface (`.xv/picture.md:28` lists `skills/*/SKILL.md`) but adds no surface. shape_breadth is narrow, the same as the forecast ("narrow": the brief, one check, and a CHANGELOG line).

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:25` "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." The change lets the scenario agent name several tests per item and serves the same users (`.xv/pitch.md:21`). No promise is broken.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-30-covers-list` shows no files changed, deleted or added, and no tests with fewer assertions. The record's `moved_tests` is `[]`. The diff to `tests/` only adds lines (`tests/test_run.py:301-352`, `tests/test_check.py:57-68`).

Slice-only tests removed: none. Kept: none (the record's `slice_only` is `[]`).

## 4. The picture

`.xv/picture.md:26` now understates the check. It says "`covers` empty or with an item that names no test, or a `covers` test that matches no whole word in any red file." Proposed edit: "`covers` empty or with an item that names no test, or a `covers` name that matches no whole test name in any red file. A `covers` test may be one name, a list, or a string joined with `,` or `;`. `Class.test` and `file::test` match only when the class is in, or the file is, a red file that has the test, and the stop names the name that does not match."

## 5. The wall

- `tests/test_check.py`, `test_the_changelog_has_a_line_for_a_covers_item_naming_more_than_one_test`: recommend marking it slice-only, so it stays off the wall. It reads only `## Unreleased` (`tests/test_check.py:65` `unreleased = text.split("## Unreleased", 1)[1]…`) and guards a one-time CHANGELOG line, so it breaks when the release renames the section. Sean saw this option at the `red_misses_scenario` stop ("Send it back to mark the CHANGELOG test slice-only") and picked "go on". That pick moved the slice forward and did not settle the mark. Note that `tests/test_by_name.py:60` and `tests/test_slice_skill_readback.py:33` follow the same pattern and are on the wall.

I also looked at the twelve new tests in `tests/test_run.py:309-352` and the brief-example test at `tests/test_check.py:57-60`. Each guards a lasting behaviour, so I make no recommendation for them. No test on the wall before the slice is made dead: the old covers tests at `tests/test_run.py:267-299` still describe the single-name case.

## Door

**Door:** two-way. A revert restores the single-name check and the old brief example. No data, record format or public contract changes in a way old records can't read (a single string still works). **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-covers-list.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..4d544a6`
- Wall: `xv wall diff 2026-10-30-covers-list`
- Boundary: `xv boundary --base f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5` (`.xv/slices/2026-10-30-covers-list.boundary.md`)
- The record says the cleaner did not commit (`checks.cleaner.committed: false`, `cleaner_commit: null`), but its `covers_name_found` fix is in `4d544a6` "record the cleaner's pass" (`git show 4d544a6 -- scripts/run.py`).

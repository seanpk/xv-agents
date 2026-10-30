---
slice: 2026-10-29-red-covers-scenario
shape_change: yes
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: A red that leaves part of the scenario untested is caught before the maker

**Needs a decision from two people (solo here: Sean):** a narrow shape change. `run` now calls `check`, and `check` stops being only the guardian's module. The width matches the forecast's "narrow". Also for Sean: two places where the new check passes on input it cannot read (check 1, findings b and c), which `.xv/picture.md:72` says must stop instead.

## The scenario

1. The scenario agent's report names each item in the scenario with the test that covers it, and each item it did not cover with the reason. An uncovered item stops the slice for the originator before the maker runs (#64).
2. After the scenario step, a check lists each flag and `xv` command that the scenario (amendments included) writes in backticks and that no red file contains. Anything on the list stops the slice for the originator before the maker runs (retro candidate 1).
3. Test case: on the first red of `2026-10-29-stop-decisions` the check lists `--since`. On that slice's final red it lists nothing.

May ignore: items named in plain words without backticks. Point 1 covers those, not point 2.

## The recording

None: this is a feature. Replay the red and the suite:
- Red: `cd tests && python3 -m unittest test_check test_run`. At `8365f78` it fails 14 (5 failures, 9 errors), starting with `AttributeError: module 'check' has no attribute 'red_gaps'`. At HEAD it passes.
- Whole suite: `cd tests && python3 -m unittest -q`. I ran it at HEAD: `Ran 408 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-29-red-covers-scenario.boundary.md`, as given:
- Modules touched: `scripts/check`, `scripts/orders`, `scripts/run`. None added or removed. No new outbound calls.
- Edges added: **`scripts/run → scripts/check`**. None removed.
- Tables: none. Surfaces users meet: none in the boundary tool's terms. The scenario brief `skills/scenario/SKILL.md` (a surface per `.xv/picture.md:28`) gains two report fields, and the watch gains a new stop, `red_misses_scenario`.
- Shape hint: "an edge between modules was added".

## What the suite asserts after

- `check.red_gaps(scenario, red_texts)` lists each backticked flag that no red text contains. It reads every flag in a span and ignores flags written in plain words. It lists an `xv` command unless some red text contains all of its words, either as arguments or as text. It lists nothing when the scenario has no backticks (`tests/test_check.py` `RedGapsTest`, 7 cases).
- On frozen copies of the stop-decisions red files (`tests/data/stop-decisions-red/{first,final}`), read against the live `.xv/slices/2026-10-29-stop-decisions.md` scenario, the first red lists `--since` (and neither `--settles` nor `xv record offer`). The final red lists nothing.
- The scenario brief contains `` `covers` `` and `` `not_covered` `` (`ScenarioBriefTest`).
- End to end through the watch (`tests/test_run.py`, 7 cases): a backticked flag or `xv` command that no red file has stops for the originator before the maker, with exit 10 and the item named in the question. A flag added by amendment counts. If a red file has the flag, or the flag is in plain words, the slice goes on to the maker. A `not_covered` item stops and names the item and the reason. An empty `not_covered` goes on.
- No old assertion moved.

## 1. Shape

shape_change: **yes**, narrow (the forecast also said narrow).

- **Hint "an edge between modules was added" (`run → check`): this changes the shape.** Before this slice `run` and `check` were apart: `.xv/picture.md:21` lists everything `run` reaches, and `check` is not on the list. `.xv/picture.md:23` says "`boundary`, `packet` and `check` are the guardian's checks." After the change, the watch's loop calls `check` after every scenario step (`scripts/run.py:459`, `scripts/run.py:516` `import check`). This is a coupling between modules that were apart, and it changes what `check` is for.
- `check`'s own docstring no longer describes it: `scripts/check.py:2` "Read the project layer against the shared core. Changes nothing." `red_gaps` (`scripts/check.py:220`) reads a slice's scenario against its red files, not the project layer against the core, and its result now gates the watch. Which module a gate like this belongs in is for the two people to decide. Nothing in the binding decisions settles it: `.xv/picture.md:70` (decision 10) is satisfied, because the stop itself is raised in `scripts/orders.py:110-117` from what the record says.
- **Binding decision 12 (`.xv/picture.md:72`): "A check whose input is broken or that cannot run stops for a person; it never passes."** This is not a shape change, but it is a finding in three places:
  - a. `scripts/run.py:520-521` `if at < 0: return []`: when a record has no `## Scenario` heading, the check finds nothing to read and passes. The body template always writes that heading (`scripts/record.py` `BODY_TEMPLATE`), so this only happens to hand-edited records.
  - b. `scripts/run.py:460` `[n for n in (report.get("not_covered") or []) if isinstance(n, dict)]`: a report that leaves out `not_covered`, gives it as strings (`["the grocer share"]`), or gives it as a single string is quietly read as "nothing uncovered", and the slice goes on to the maker. An agent on another harness, or one that does not follow the new brief, will do exactly this.
  - c. Scenario point 1 asks the report to name each item **with the test that covers it**. Nothing reads `covers`: `scripts/run.py:459-460` sets only `red_gaps` and `not_covered`, and no file in `scripts/` mentions `covers` as a field. A report with neither `covers` nor `not_covered` goes on to the maker. The default fake agent sends no `covers`, and `test_a_flag_in_plain_words_does_not_stop` asserts that it goes on.
- How strictly the check reads a command: `scripts/check.py:231-232` counts `xv record answer` as covered when the words `record` and `answer` appear **anywhere** in a red file, even apart. Scenario point 2 says "appears in no red file". In a red file such as `test_record.py`, common words like `record` will nearly always be present, so a missing subcommand can slip through. `test_a_command_is_covered_by_its_words_as_arguments_or_as_text` asserts only the case where the command is covered.
- Everything else is inside the current shape. `orders.py` gains one order (`scripts/orders.py:110-117`). It is still a pure function of the record (`.xv/picture.md:70`). There are no new tables, outbound calls or modules (boundary picture).

## 2. Pitch

pitch_contradiction: **no**. The change adds a stop that hands a person a gap between the scenario and the red. That fits `.xv/pitch.md:7` "makes it easy … to vibe with discipline". It does not touch who the system is not for (`.xv/pitch.md:25` "not for people or projects that will not trust agents to write production code"). I read the whole pitch and found no line the change contradicts.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

No old test moved. Here is what I looked at:
- The record has `moved_tests: []` (`.xv/slices/2026-10-29-red-covers-scenario.md:15`). `xv wall diff 2026-10-29-red-covers-scenario` returns changed, deleted and `fewer_assertions` all `[]`.
- `tests/test_check.py` and `tests/test_run.py` (the red files) only gain lines. The one changed line is an import (`from helpers import HOME, RepoCase`, `tests/test_check.py:4`), which the wall exempts (`.xv/picture.md:23`).
- `tests/fake_agent.py` is not a red file. The scenario agent changed it (red commit `8365f78`) by adding the env-gated `FAKE_RED_TEXT` and `FAKE_NOT_COVERED` (`tests/fake_agent.py:37-51`). Without those variables it behaves as before, and it adds no assertion. The wall baseline was written after the scenario step and already includes this version (`.xv/slices/2026-10-29-red-covers-scenario.wall.json:13`), so the wall would not have flagged it either way.
- New fixtures: `tests/data/stop-decisions-red/**` holds 2,387 lines of frozen copies of the stop-decisions red files. `RedGapsTest` also reads the **live** `.xv/slices/2026-10-29-stop-decisions.md` (`tests/test_check.py:53-57`), so a later edit to that record's scenario would break the test.

Slice-only tests removed: none. Kept: none (the record's `slice_only` is `[]`).

## 4. The picture

Proposed edits to `.xv/picture.md`, for the originator to accept:
- `.xv/picture.md:21`: add `check` to the list of modules `run` reaches. The count "58 edges" becomes 59 once `.xv/boundary-all.md` is regenerated.
- `.xv/picture.md:23`: "`boundary`, `packet` and `check` are the guardian's checks" is no longer complete. Add: "`check.red_gaps` is also run by the watch after the scenario step."
- `.xv/picture.md:26`, the paragraph on the step lifecycle: add that after the scenario step, the watch stops with `red_misses_scenario` for the originator, with `next` staying on `scenario`. It does so when a flag or `xv` command written in backticks in the scenario (amendments included) is in no red file, or when the scenario report's `not_covered` names an item.
- Names section (`.xv/picture.md:30`, `## Names`): add the scenario report's `covers` and `not_covered` fields (`skills/scenario/SKILL.md:53-54`).
- `.xv/picture.md:61` (decision 1) is met in form: a brief and a check changed, and `CHANGELOG.md:11` has the line. That line already says "Sean decided it, solo", but the decision is what this packet asks for. It only becomes true once Sean accepts.

## Door

**Door:** two-way. A revert removes the check, the order and the two brief fields. No data is migrated and no message goes to users. **Blast radius:** adopters. The brief (`skills/scenario/SKILL.md`) and the new stop in `scripts/orders.py` reach every adopting repo on upgrade.

## Raw data

- Slice record: `.xv/slices/2026-10-29-red-covers-scenario.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..3317370`
- Wall: `xv wall diff 2026-10-29-red-covers-scenario`
- Boundary: `.xv/slices/2026-10-29-red-covers-scenario.boundary.md` (`xv boundary --base 5ec1d8640ff0`)

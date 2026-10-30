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

**Two people need to decide (this repo runs solo, so Sean decides): the shape changed again, narrowly, against what Sean settled.** The `run → check` edge is gone. In its place is a new `check → wall` edge, a re-export that exists only so `tests/test_check.py` can still call `check.red_gaps`. Sean settled that "red_gaps moves into scripts/wall.py … so the shape does not change" (`.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`, Settled). Everything else Sean asked for at the last stop is in place. One reading of "covers is read" is left for Sean (check 1, finding c).

## The scenario

1. The scenario agent's report names each item in the scenario with the test that covers it (`covers`), and each item it did not cover with the reason (`not_covered`). An uncovered item stops the slice for the originator before the maker runs (#64).
2. After the scenario step, a check lists each flag and `xv` command that the scenario, amendments included, writes in backticks and that no red file contains. Anything on the list stops the slice for the originator before the maker runs (retro candidate 1).
3. Test case: on the first red of `2026-10-29-stop-decisions` the check lists `--since`. On that slice's final red it lists nothing.
4. Amended by Sean on 2026-10-29:
   - `red_gaps` moves into `scripts/wall.py` so the shape does not change.
   - A record with no `## Scenario` heading stops the slice. So does a report whose `covers` or `not_covered` is missing or is not a list of items.
   - `covers` is read: each item names its test.
   - An `xv` command counts as covered only when its words appear together, in order, in a red file.

May ignore: items named in plain words without backticks.

## The recording

None: this is a feature. To replay:
- Red: `cd tests && python3 -m unittest -q test_wall test_run test_check`. The scenario agent's record says that at the second red, `dded614`, 9 run tests fail and 7 wall tests error. I did not re-run it at that commit. I ran it at HEAD (`c2d3beb`): `Ran 98 tests … OK`.
- Whole suite: `cd tests && python3 -m unittest -q`. I ran it at HEAD: `Ran 425 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-29-red-covers-scenario.boundary.md`, as given:
- Modules touched: `scripts/check`, `scripts/orders`, `scripts/run`, `scripts/wall`. None were added or removed, and there are no new outbound calls.
- Edges added: **`scripts/check → scripts/wall`**. None were removed. (The base has no `run → check` edge, and HEAD does not add one. `run` uses `wall`, an edge it already had.)
- Tables: none. Surfaces in the tool's terms: none. Two surfaces still change, though. The scenario brief (`skills/scenario/SKILL.md:53-58`) gains `covers` and `not_covered`, and the watch gains the stop `red_misses_scenario` (`scripts/orders.py:110-119`).
- Shape hint: "an edge between modules was added".

## What the suite asserts after

- `wall.red_gaps(scenario, red_texts)` lists each flag in backticks that no red text has. It does not read flags written in plain words. It lists an `xv` command unless a red text has the command's words in order, joined only by non-alphanumeric characters. A command whose words are apart or out of order is listed (`tests/test_wall.py` `RedGapsTest`, 7 cases). `tests/test_check.py` `RedGapsTest` makes the same kinds of assertions through `check.red_gaps`, 9 cases.
- On frozen copies of the stop-decisions red files (`tests/data/stop-decisions-red/{first,final}`), against the live `.xv/slices/2026-10-29-stop-decisions.md` scenario, the first red lists `--since` and the final red lists nothing.
- Through the watch (`tests/test_run.py`, 18 cases), each of these stops before the maker with exit 10:
  - a flag or `xv` command in backticks that no red file has, including one that came in by amendment;
  - a `not_covered` item;
  - a record with no `## Scenario` heading;
  - a report whose `covers` or `not_covered` is missing or not a list;
  - an empty `covers`;
  - a `covers` item that names no test;
  - a command whose words are apart or out of order in the red.

  A flag that a red file has, a flag in plain words, and an empty `not_covered` all go on to the maker.
- The scenario brief contains `` `covers` `` and `` `not_covered` `` (`ScenarioBriefTest`).
- No old assertion moved.

## 1. Shape

shape_change: **yes**, narrow (the forecast also said narrow).

- **a. Hint "an edge between modules was added" (`check → wall`): this changes the shape.** At the base, `check` and `wall` were apart. `.xv/picture.md:23` says "`wall` holds the test hash check" and "`boundary`, `packet` and `check` are the guardian's checks". The new edge comes from `scripts/check.py:220` `from wall import red_gaps  # noqa: E402,F401  (the check lives in wall, beside the other red-file checks)`. Nothing in `scripts/` calls `check.red_gaps`. The only caller is `tests/test_check.py` (`check.red_gaps(...)` in `RedGapsTest`), and `tests/test_wall.py` `RedGapsTest` already covers the same function in `wall`. The cleaner said the same in its report: "scripts/check.py re-exports wall.red_gaps only because tests/test_check.py still calls check.red_gaps" (record, `checks.reports`, cleaner 00:57). This goes against Sean's settled words "so the shape does not change" (decision record, Settled). It is narrow: one import line, no behaviour.
- **b. Decision 12 (`.xv/picture.md:72`), which the last packet raised, is now met for the cases Sean named.**
  - A record with no Scenario heading stops: `scripts/run.py:518`.
  - A missing, non-list or non-dict `not_covered` stops: `scripts/run.py:521-522`.
  - A missing, empty, non-list or test-less `covers` stops: `scripts/run.py:523-525`.
  - Command words must now come together and in order: `scripts/wall.py:203-205` (`r"[^A-Za-z0-9]+".join(...)`).
- **c. "covers is read" is met in its literal form only.** `scripts/run.py:524` `isinstance(c, dict) and c.get("item") and c.get("test")` checks that each item has a non-empty `test` string. Nothing checks that the named test exists in a red file. A report with `{"item": "x", "test": "test_that_does_not_exist"}` goes on to the maker. Sean's words were "covers is read: each item names the test that covers it" (decision record, Settled). Whether "names the test" means a test that exists is Sean's reading to give.
- Everything else stays inside the current shape. `orders.py` gains stops under the existing `after == "scenario"` branch (`scripts/orders.py:110-119`), and they are raised from what the record says (`.xv/picture.md:70`, decision 10). No tables, outbound calls or modules change.

## 2. Pitch

pitch_contradiction: **no**. The change adds a stop that hands a person a gap between the scenario and the red. That fits `.xv/pitch.md:7` "makes it easy … to vibe with discipline". It does not touch `.xv/pitch.md:25` "not for people or projects that will not trust agents to write production code". I read the whole pitch and found no line the change contradicts.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at:
- The record has `moved_tests: []` (`.xv/slices/2026-10-29-red-covers-scenario.md:15`).
- `xv wall diff 2026-10-29-red-covers-scenario` shows `changed`, `deleted`, `added` and `fewer_assertions` all empty (`.xv/slices/2026-10-29-red-covers-scenario.wall.json`, baseline `058959e`).
- The only removed line in a red file is the import at `tests/test_check.py:4` (`from helpers import RepoCase` → `from helpers import HOME, RepoCase`), which the wall exempts (`.xv/picture.md:23`).
- `tests/fake_agent.py` gains `FAKE_RED_TEXT`, `FAKE_NOT_COVERED`, `FAKE_REPORT_EXTRA` and `FAKE_REPORT_DROP`, and by default it now sends `covers` and an empty `not_covered` (`tests/fake_agent.py:45-50`). It asserts nothing.
- Still open from the last packet: both `RedGapsTest` classes read the **live** `.xv/slices/2026-10-29-stop-decisions.md` (`tests/test_check.py:53-57`, which `tests/test_wall.py` imports). A later edit to that record's scenario breaks them.

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

Proposed edits to `.xv/picture.md`, for the originator to accept:
- `.xv/picture.md:23`: "`wall` holds the test hash check" becomes "`wall` holds the test hash check and `red_gaps`, the check that each flag and `xv` command in backticks in the scenario is in a red file". If the `check → wall` edge stays, add that `check` re-exports it.
- `.xv/picture.md:21`: "58 edges" becomes 59 if the `check → wall` edge stays.
- `.xv/picture.md:26` (the step lifecycle): add that after the scenario step, the watch stops with `red_misses_scenario` for the originator (`scripts/orders.py:110-119`) when a flag or `xv` command in backticks in the scenario, amendments included, is in no red file; when the report's `not_covered` names an item; when the record has no `## Scenario` heading; or when the report's `covers` or `not_covered` is missing or malformed.
- `## Names` (`.xv/picture.md:30`): add the scenario report's `covers` and `not_covered` fields (`skills/scenario/SKILL.md:53-54`).

## Door

**Door:** two-way. A revert removes the check, the stops and the two brief fields. No data is migrated and no message goes to users. **Blast radius:** adopters. The scenario brief and the new stop reach every adopting repo on upgrade, and every adopter's scenario agent must now send `covers` and `not_covered` or its slices stop (`scripts/run.py:521-525`).

## Raw data

- Slice record: `.xv/slices/2026-10-29-red-covers-scenario.md`
- Decision: `.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..c2d3beb`
- Wall: `xv wall diff 2026-10-29-red-covers-scenario`
- Boundary: `.xv/slices/2026-10-29-red-covers-scenario.boundary.md` (`xv boundary --base 5ec1d8640ff0`)

## From the cleaner

- Shape proposal, for people: scripts/check.py re-exports wall.red_gaps only because tests/test_check.py still calls check.red_gaps; if that test moves to wall, drop the re-export and the new check -> wall import.

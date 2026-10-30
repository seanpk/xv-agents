---
slice: 2026-10-29-red-covers-scenario
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: A red that leaves part of the scenario untested is caught before the maker

**Nothing needs two people. The merge is Sean's, as the person who set the work going.** All three of Sean's requests from the merge stop are in:
- a `covers` test no longer passes when it is only part of a longer name;
- the helpers live in `tests/test_wall.py` and read a copy of the scenario;
- the `CHANGELOG.md` line names the new stop.

Two things are left for Sean: (1b) the `covers` match is "a whole word anywhere in a red file", which is looser than "a whole test name"; and the two picture edits in check 4.

## The scenario

After the scenario step, the slice stops for the person who set the work going, before the maker runs, when any of these is true:
- the scenario agent's report lists an item under `not_covered`;
- a flag or `xv` command written in backticks in the scenario (amendments included) appears in no red file. A command counts only when its words appear together and in order;
- the check cannot read its input:
  - the record has no `## Scenario` heading;
  - `covers` or `not_covered` is missing or is not a list of items;
  - `covers` is empty or has an item that names no test;
  - a `covers` test does not match a whole test name in any red file.

The test case: on the first red of `2026-10-29-stop-decisions` the check lists `--since`. On that slice's final red it lists nothing.

**May ignore:** items the scenario names in plain words, without backticks.

## The recording

None; this is a feature. Replay the red: `cd tests && python3 -m unittest test_run test_wall test_check`.
- Before the maker: FAIL, `0 != 10 : stop null` on `test_a_covers_test_that_is_only_part_of_a_longer_test_name_stops_before_the_maker` (record, `red.failure`).
- After: I re-ran it and got 93 tests OK.
- The whole suite: 420 tests OK (record, `checks.maker.suite_output`). I did not re-run the whole suite.

## The boundary picture

From `.xv/slices/2026-10-29-red-covers-scenario.boundary.md`, as given:
- Modules touched: `scripts/orders`, `scripts/run`, `scripts/wall`. None added or removed.
- Edges added: none. Removed: none.
- Tables: none. Surface paths: none. New outbound calls: none. Shape hints: none.

## What the suite asserts after

- **`wall.red_gaps`** (`tests/test_wall.py` `RedGapsTest`, 7 tests). It lists a backticked flag that no red text has. It does not list a flag a red text has, or one written in plain words. An `xv` command counts only when its words come together and in order. On the stop-decisions copy (`tests/data/stop-decisions-red/`), it lists `--since` on the first red and nothing on the final red.
- **Stops at the run level** (`tests/test_run.py:184-303`, 21 tests). Each of these stops before the maker for the originator, and the maker spends nothing:
  - a backticked flag in the scenario or an amendment that no red file has;
  - a missing `xv` command;
  - a `not_covered` item;
  - no `## Scenario` heading;
  - `not_covered` missing or not a list;
  - `covers` missing, not a list, empty, or with an item that names no test;
  - a `covers` test that is in no red file, on its own or next to found ones;
  - a `covers` test that is only part of a longer name (`test_milk` vs `test_milk_today`);
  - command words that are apart or out of order.
- **What goes on to the maker:** a flag a red file has, a flag in plain words, an empty `not_covered`, a found `covers` test, and command words together and in order.
- **The scenario brief** asks for `covers` and `not_covered` (`tests/test_check.py:50-55`).
- No old assertion moved (check 3).

## 1. Shape

shape_change: no. shape_breadth: none. The forecast expected narrow, so this is not wider than expected.

a. **No edges change, and the standing order sits where it should.**
- The boundary picture adds no edge and removes none. The new code calls `wall` and `record` from `run` (`scripts/run.py:535-543`). Both edges are already in `.xv/picture.md:21` ("`run` reaches … `record` … `wall`").
- `git diff 5ec1d86..HEAD -- scripts/check.py` is empty. So `.xv/picture.md:23` ("`boundary`, `packet` and `check` are the guardian's checks") still holds.
- The new order `red_misses_scenario` lives in `scripts/orders.py:110-119`, computed from `checks` in the record. That is where `.xv/picture.md:70` (decision 10) puts standing orders.
- It changes a brief and a check, so `.xv/picture.md:61` (decision 1) asks for two people and a `CHANGELOG.md` line. Sean decided it solo, twice (`.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`, `…-2.md`). `CHANGELOG.md:11` now names every stop, including "a `covers` item whose test is in no red file".
- The earlier test-side coupling is gone. `tests/test_wall.py:217-231` defines `stop_decisions_scenario` and `red_texts` itself and reads `tests/data/stop-decisions-red/scenario.md`. `tests/test_check.py` no longer has them. The copy has the same headings and the same 81-line span as `.xv/slices/2026-10-29-stop-decisions.md:32-112`.

b. **For Sean: the `covers` match is a whole word, not a whole test name.**
- `scripts/run.py:529`: `whole = re.compile(r"(?<!\w)" + re.escape(str(c["test"])) + r"(?!\w)")`. It is searched against the full text of each red file. This closes the case Sean named, `test_milk` against `test_milk_today` (`tests/test_run.py:279-281`).
- It still passes any word that appears in a red file. With the fake red, `{"item": "milk today", "test": "milk"}` or `"test": "Store"` passes, because `tests/fake_agent.py:34-35` writes `s.add('milk', …)` and `s = Store()`. The settled words are "A covers test must match a whole test name in a red file" (scenario, third amendment, point 1). The `CHANGELOG.md:11` line says the same, "the test must match a whole test name". The code is looser than both.
- The match is also too strict in the other direction. A dotted or path id such as `Red.test_milk_today` or `tests/test_red.py::test_milk_today` appears nowhere literally, so it stops the slice. That fails safe (`.xv/picture.md:72`, decision 12). But `skills/scenario/SKILL.md:58` does not say `test` must be the bare function name; only the example on `:53` shows one.
- Not a shape change. Sean decides whether "whole word" is close enough.

c. **The heading match is loose; low risk.** `scripts/run.py:518` and `:539` match `## Scenario` anywhere in the body. If there is no `\n## May ignore`, `:540` reads on into the log, and the backticked `xv record …` commands in the log become gaps. Either way the slice stops and nothing passes wrongly (decision 12). `scripts/record.py:43` writes `## May ignore` into every new record, and `scripts/run.py:279-282` refuses to amend a record without it.

## 2. Pitch

pitch_contradiction: no. I checked against these lines:
- `.xv/pitch.md:7`: "makes it easy … to vibe with discipline"
- `.xv/pitch.md:17`: "makes Xtreme Vibing executable and empirical"
- `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code"

The change adds a mechanical stop when a red leaves a named part of the scenario untested. That is more discipline, and it serves the same people. The pitch says nothing about scenario coverage, and silence is not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- `xv wall diff 2026-10-29-red-covers-scenario` against baseline `cdb35c0` reports changed `[]`, deleted `[]`, added `[]`, fewer_assertions `[]`, and the record has `moved_tests: []` (`.xv/slices/2026-10-29-red-covers-scenario.md:15`).
- Against the base `5ec1d86`, no removed or changed line in an old test file is an assertion. `tests/test_check.py:4` and `tests/test_wall.py:5` are import lines, `tests/test_wall.py:7` adds `DATA`, and every other change in `tests/test_check.py`, `tests/test_wall.py` and `tests/test_run.py` is an addition.
- `tests/fake_agent.py:45` is a helper, not a test. The default scenario report now carries `covers: [{"item": "milk today", "test": "test_milk_today"}]` and `not_covered: []`. So every existing run test that drives a scenario step now goes through the new check and passes it.

Slice-only tests removed: none. Kept: none.

## 4. The picture

Two edits, for Sean:
- **`.xv/picture.md:23`**, "`wall` holds the test hash check." This is now incomplete. Proposed: "`wall` holds the test hash check and `red_gaps`, which lists each flag and `xv` command written in backticks in the scenario that no red file has (a command's words together, in order)."
- **`.xv/picture.md:26`**, after the sentence on red commands joined by anything but `&&`. Now incomplete. Proposed addition: "After the scenario step, `red_misses_scenario` stops for the originator before the maker when the report lists a `not_covered` item, when `red_gaps` lists anything, or when the check cannot read its input: no `## Scenario` heading, `covers` or `not_covered` missing or not a list, `covers` empty or with an item that names no test, or a `covers` test that matches no whole word in any red file." (`scripts/orders.py:110-119`, `scripts/run.py:515-532`)

The shape section (`.xv/picture.md:19-28`) needs no module or edge edit (check 1a).

## Door

**Door:** two-way. A revert removes the order, the check and the brief lines. No data is migrated and no record field is renamed.

**Blast radius:** adopters. `skills/scenario/SKILL.md` and `scripts/orders.py` ship to every adopting repo. After an upgrade, any scenario report without `covers` and `not_covered` stops before the maker (`scripts/run.py:522-527`).

## Raw data

- Slice record: `.xv/slices/2026-10-29-red-covers-scenario.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..HEAD`
- Wall: `xv wall diff 2026-10-29-red-covers-scenario`
- Boundary: `xv boundary --base 5ec1d8640ff0da37a2634737f241cfd1a14821e2` (`.xv/slices/2026-10-29-red-covers-scenario.boundary.md`)
- Decisions: `.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`, `.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario-2.md`

## From the cleaner

- Shape proposal, for people: scripts/check.py re-exports wall.red_gaps only because tests/test_check.py still calls check.red_gaps; if that test moves to wall, drop the re-export and the new check -> wall import.

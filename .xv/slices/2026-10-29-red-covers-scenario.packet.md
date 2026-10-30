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

**Nothing needs two people. The merge is Sean's, as the person who set the work going.** Both things Sean asked for at the second shape stop are in. The `check → wall` edge is gone: `scripts/check.py` has no diff from the base, and the boundary picture adds no edge. A `covers` test found in no red file now stops the slice. Still for Sean: two picture edits (check 4), one loose match in the `covers` check (1c), and some test-only coupling left over from the move (1d).

## The scenario

After the scenario step, the slice stops for the person who set the work going, before the maker runs, when:
- the scenario agent's report lists an item under `not_covered`;
- a flag or `xv` command written in backticks in the scenario, amendments included, appears in no red file (a command's words must appear together and in order);
- the check cannot read its input: the record has no `## Scenario` heading, `covers` or `not_covered` is missing or is not a list of items, `covers` is empty or has an item that names no test, or a `covers` test appears in no red file.

The test case: on the first red of `2026-10-29-stop-decisions` the check lists `--since`, and on that slice's final red it lists nothing. **May ignore:** items the scenario names in plain words, without backticks. Those are left to the agent's `covers` list.

## The recording

None; this is a feature. Replay the red: `cd tests && python3 -m unittest test_run.WatchLoopTest.test_a_covers_item_whose_test_is_in_no_red_file_stops_before_the_maker test_run.WatchLoopTest.test_one_covers_item_with_a_missing_test_among_found_ones_stops_before_the_maker`. Before: FAIL with exit 0, no stop (record, `checks.scenario.red_output`). After: OK. I re-ran it with `test_wall.RedGapsTest`: 9 tests, OK. The whole suite: 419 tests OK (record, `checks.cleaner.suite_output`).

## The boundary picture

From `.xv/slices/2026-10-29-red-covers-scenario.boundary.md`, as given:
- Modules touched: `scripts/orders`, `scripts/run`, `scripts/wall`. None added or removed.
- Edges added: none. Removed: none. `run → wall` and `run → orders` were already there.
- Tables: none. Surface paths: none. New outbound calls: none.
- Shape hints: none.

## What the suite asserts after

- `wall.red_gaps(scenario, red_texts)` lists a backticked flag that no red text has. It does not list a flag that some red text has, or one written in plain words. An `xv` command counts as present only when its words are adjacent and in order. On the first stop-decisions red it lists `--since`; on the final red it lists nothing (`tests/test_wall.py` `RedGapsTest`, 7 tests).
- At the run level, each of these stops before the maker for the originator, with no maker spend: a backticked flag in the scenario or an amendment that no red file has; a missing `xv` command; a `not_covered` item; no `## Scenario` heading; `not_covered` missing or not a list; `covers` missing, not a list, empty, or with an item that names no test; a `covers` test that is in no red file, on its own or next to found ones; command words apart or out of order. A flag a red file has, a flag in plain words, an empty `not_covered`, a found `covers` test, and command words together and in order all go on to the maker (`tests/test_run.py:184-298`, 20 tests).
- The scenario brief asks for `covers` and `not_covered` (`tests/test_check.py` `ScenarioBriefTest`).
- No old assertion moved (check 3).

## 1. Shape

shape_change: no. shape_breadth: none. The forecast expected narrow, so this is not wider than expected.

a. **Edges.** The boundary picture adds no edge and removes none. The new code calls `wall` and `record` from `run` (`scripts/run.py:534-542`). Both edges exist in `.xv/picture.md:21` ("`run` reaches … `record` … `wall`"). The second stop's `check → wall` re-export is gone: `git diff 5ec1d86..HEAD -- scripts/check.py` is empty. So `.xv/picture.md:23` ("`boundary`, `packet` and `check` are the guardian's checks") still holds.

b. **A new standing order inside `orders`.** `red_misses_scenario` fires from `scripts/orders.py:110-119` and is computed from `checks` in the record. This is the place `.xv/picture.md:72` (binding decision 10) puts standing orders, so it is not a shape change. It is a change to a brief and to a check an agent is judged by, which `.xv/picture.md:61` (decision 1) says needs two people and a line in `CHANGELOG.md`. The line is at `CHANGELOG.md:11`, and Sean decided it solo twice (`.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`, `…-2.md`). The line leaves out the second amendment's stop. It lists the unreadable-input stops ("missing, not a list, or (for `covers`) empty or naming no test") but not "a `covers` test found in no red file", which `scripts/run.py:528-531` adds. Proposed addition to that sentence: "…, or naming a test no red file has".

c. **The `covers` check matches a substring, not a test.** `scripts/run.py:529`: `if not any(str(c["test"]) in t for t in texts):`. A `covers` test named `test_milk` passes when a red file has `test_milk_today`. A name like `red` or `test` passes against almost any red file. This meets the letter of Sean's settled words, "Each covers item's test must appear in one of the red files" (`.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario-2.md`). It is looser than "the test that covers it" (scenario, point 3 of the first amendment). Not a shape change. Sean decides whether the letter is enough.

d. **Test-only coupling left from the move.** `tests/test_check.py:50-62` still defines `DATA`, `stop_decisions_scenario()` and `red_texts()`, but no test in that file uses them now. `tests/test_wall.py:243` imports them: `from test_check import red_texts, stop_decisions_scenario`. Tests are not modules in the boundary picture, so this is not a shape change. It is the test-side mirror of the edge Sean removed. The cleaner's earlier proposal ("if that test moves to wall, drop the re-export and the new check -> wall import", record `checks.reports`, cleaner at 00:57) dealt with the code side only. Also, `stop_decisions_scenario()` reads the live record `.xv/slices/2026-10-29-stop-decisions.md` (`tests/test_check.py:55`), so if that record is edited, this test changes with it. The red files are snapshotted under `tests/data/stop-decisions-red/`; the scenario is not.

e. **Heading match is loose, and checked twice.** `scripts/run.py:518` (`"## Scenario" not in body`) and `scripts/run.py:538` (`body.find("## Scenario")`) both also match `### Scenario…` or the text anywhere in the body, the log included. If a record has no `\n## May ignore`, `scripts/run.py:539-542` reads to the end of the body, log included. Log lines carry backticked `xv record …` commands, so those would be listed as gaps. Either way the slice stops; nothing passes wrongly, which is consistent with `.xv/picture.md:72` (decision 12). `scripts/record.py:43` writes `## May ignore` into every new record, and `xv slice amend` refuses a record without it (`scripts/run.py:279-282`). So this is a low risk.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `.xv/pitch.md:17` ("makes Xtreme Vibing executable and empirical") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). The change adds a mechanical stop when a red leaves a named part of the scenario untested. That is more discipline, and it does not change who the system is for. The pitch says nothing about scenario coverage; silence is not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-29-red-covers-scenario` against baseline `02e240b`: changed `[]`, deleted `[]`, added `[]`, fewer_assertions `[]`. The record has `moved_tests: []`. Against the base `5ec1d86`, the only non-added line in an old test file is `tests/test_check.py:4` (`from helpers import RepoCase` → `from helpers import HOME, RepoCase`), an import line. `tests/fake_agent.py` is a helper, not a test. Its default scenario report now carries `covers: [{"item": "milk today", "test": "test_milk_today"}]` and `not_covered: []` (`tests/fake_agent.py:45`). So every existing run test that drives a scenario step now goes through the new check. That is why the suite still passes, not an assertion that moved.

Slice-only tests removed: none. Kept: none.

## 4. The picture

- `.xv/picture.md:23`, "`wall` holds the test hash check." This is now incomplete. Proposed: "`wall` holds the test hash check and `red_gaps`, which lists each flag and `xv` command written in backticks in the scenario that no red file has (a command's words together, in order)."
- `.xv/picture.md:26`, the scenario-step sentences (after "A red command joined at the top level…"). This is now incomplete. Proposed addition: "After the scenario step, `red_misses_scenario` stops for the originator before the maker when the report lists a `not_covered` item, when `red_gaps` lists anything, or when the check cannot read its input: no `## Scenario` heading, `covers` or `not_covered` missing or not a list, `covers` empty or with an item that names no test, or a `covers` test in no red file."
- `.xv/picture.md:20-27` (the shape) does not need a module or edge edit: the boundary picture adds none (check 1a).

## Door

**Door:** two-way. A revert removes the order, the check and the brief lines; no data is migrated and no record field is renamed. **Blast radius:** adopters. `skills/scenario/SKILL.md` and `scripts/orders.py` ship to every adopting repo, and after an upgrade, any scenario report without `covers` and `not_covered` stops before the maker (`scripts/run.py:521-527`).

## Raw data

- Slice record: `.xv/slices/2026-10-29-red-covers-scenario.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..HEAD`
- Wall: `xv wall diff 2026-10-29-red-covers-scenario`
- Boundary: `xv boundary --base 5ec1d8640ff0da37a2634737f241cfd1a14821e2` (`.xv/slices/2026-10-29-red-covers-scenario.boundary.md`)
- Decisions: `.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario.md`, `.xv/decisions/2026-10-29-2026-10-29-red-covers-scenario-2.md`

## From the cleaner

- Shape proposal, for people: scripts/check.py re-exports wall.red_gaps only because tests/test_check.py still calls check.red_gaps; if that test moves to wall, drop the re-export and the new check -> wall import.

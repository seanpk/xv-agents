---
slice: 2026-11-04-scenario-catches
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: The scenario agent catches more before the maker starts: #119, with #110 and #111

Nothing stops for two people. Points 2a and 2b are written into the briefs, but the code never acts on them, so the slice goes back (see Scenario misses). For Sean: one picture edit that depends on how 2b is met (§4), and one wall recommendation (§5).

## The scenario

Six points. (1) The scenario agent marks a one-time wording test slice-only. (2a) Its report names each old test the red forces to change, and the maker may change a named test without stopping and records the move. (2b) Its report names each may-not file the red needs changed; the maker may change those and no other file on that list; the guardian lists those changes. (3) A red case for each way a value can be wrong, plus a case where a read-only agent claims what only a person may give. (4) Each amendment the watch drafts names four things. (5) A `covers` item may name a point by number. (6) A CHANGELOG line for each brief change.
May ignore: the cleaner; naming an amendment's points by number; old slice records.

## The recording

None (a feature). Replay the red: `cd tests && python3 -m unittest test_briefs_picture.ScenarioCatchesTest test_run.WatchLoopTest.test_a_covers_item_that_is_a_points_number_covers_it test_run.WatchLoopTest.test_a_covers_item_that_starts_with_the_number_covers_the_point test_run.WatchLoopTest.test_a_number_covers_only_its_own_point test_run.WatchLoopTest.test_the_number_one_does_not_cover_point_ten test_run.WatchLoopTest.test_a_number_item_in_not_covered_still_stops_for_the_person`. Before: 16 failures (record `checks.scenario.red_output`). After: 16 tests OK (run by the guardian on HEAD 68db9f6). The whole suite is 891 OK, run by both the maker and the cleaner (record `checks.maker`, `checks.cleaner`).

## The boundary picture

From `.xv/slices/2026-11-04-scenario-catches.boundary.md`, used as given: only `scripts/run` is touched. No modules are added or removed, no edges are added or removed, no new calls go out of the process, no tables change, no surface paths change, and there are no shape hints.

## What the suite asserts after

- `ScenarioCatchesTest` (11 tests, `tests/test_briefs_picture.py:126-188`) searches the scenario, maker, guardian and watch briefs and `CHANGELOG.md` for paragraphs that hold the words of points 1–4 and 6. These are word-presence checks only. No test runs a maker step on a named old test or on a named may-not file.
- Five `WatchLoopTest` tests (`tests/test_run.py:492-522`): a covers item `"1"` or `"1. Whether a miss repeats"` covers point 1. `"1"` does not cover point 2 or point 10. A number in `not_covered` still stops for the person. The fixture points are placed through `xv slice amend` (`tests/test_run.py:197-201`, `:493`).
- No old assertion moved.

## 1. Shape

shape_change: no. The boundary picture shows no added modules, edges, tables or surfaces, and no shape hints. The one code change, `scripts/run.py:517-521`, stays inside `missed_points`, inside the shape described at `.xv/picture.md:26` ("A numbered point of the scenario or an amendment that is in neither `covers` nor `not_covered` sends the slice back"). The scenario report gains two keys, `old_tests_forced` and `may_not_files` (`skills/scenario/SKILL.md:62-63`), inside the existing `skills/*/SKILL.md` surface (`.xv/picture.md:27`). Nothing reads them yet (see misses). shape_breadth: narrow, the same as the forecast's `narrow`. The guardian brief edit (`skills/guardian/SKILL.md:26`) is not in the forecast's breadth list, but scenario point 2b asks for it.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code." Nothing here serves that group. It adds rules about what agents may do, which fits `.xv/pitch.md:7` ("to vibe with discipline"). The pitch says nothing about which files agents may edit.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-04-scenario-catches` shows `changed: [] deleted: [] fewer_assertions: []`. `git diff a6e023b..HEAD -- tests` removes no line; the test files only gained lines. The record has `moved_tests: []`.

The scenario agent asked for no may-not file. The record has no `may_not_files`, and no may-not file changed: `checks.maker.protected_changed: []`, `checks.cleaner.protected_changed: []`.

Slice-only tests removed: none. Kept: none (the record has `slice_only: []`).

## 4. The picture

- `.xv/picture.md:26`, the sentence on the covers check. Add: "A `covers` or `not_covered` item may name a point by its number: `"1"`, or an item that starts with the number and then a space or a dot. The number covers that point in the scenario and in every amendment alike." (`scripts/run.py:517`; the regex makes no distinction between the two.)
- `.xv/picture.md:35` says "The maker and the scenario agent … do not edit it [the picture] … Accepting a picture change is a person's (#88, #68, #90)." The maker brief now reads "Edit `.xv/picture.md`, unless the scenario agent's report names it as a may-not file the red needs changed" (`skills/maker/SKILL.md:54`). Under that line, one agent can let another edit the picture with no person involved. The code still stops such an edit (`scripts/run.py:424-428`: `.xv/picture.md` is in `protected` for the maker; `scripts/orders.py:168` raises `protected_changed`). Proposed edit, depending on Sean's call on miss 2b: either keep line 35 and narrow the maker brief to match the code, or rewrite line 35 to say "the maker edits it only when the scenario report names it, and the guardian lists the edit in the packet".
- `.xv/picture.md:23`, the sentence on `record`. Add that the scenario report now carries `old_tests_forced` and `may_not_files`, and say whether the record keeps them (today it does not; see misses).

Another finding for Sean, which is not a miss: the number match also covers amendment points (`scripts/run.py:517-521`, where `num not in numbers` is tested against every `POINT` from `## Scenario` to `## May ignore`, and amendments are written in that range by `scripts/run.py:279-284`). The May ignore line says "point 5 covers only the scenario's own points". So when both the scenario and an amendment have a point 1, a single `"1"` covers both, and the amendment's point 1 can go untested without a send-back.

## 5. The wall

- `tests/test_briefs_picture.py`, `ScenarioCatchesTest.test_the_changelog_has_a_line_for_each_brief_change`: mark it slice-only. It checks a one-time CHANGELOG line, the kind of test point 1 says is "always a `slice_only` test" (`skills/scenario/SKILL.md:28`). It reads only `## Unreleased` (`tests/test_briefs_picture.py:182-188`), so it fails the first time a release moves that section under a version heading.

I looked at the other ten `ScenarioCatchesTest` tests and the five `WatchLoopTest` tests. They guard rules that stay in force, so I would leave them as they are.

## Scenario misses

- point 2 (a): The maker may change "a named test", but the names never reach the maker. Only `slice_only` and `red` are kept from the scenario report (`scripts/record.py:474-488`). The record's scenario reports hold only `agent, status, summary, at` (`.xv/slices/2026-11-04-scenario-catches.md`, `checks.reports`). `scripts/prompt.py` passes no report keys to the maker (`scripts/prompt.py:97-110`). So `old_tests_forced` (`skills/scenario/SKILL.md:62`) is read by nothing, and the maker cannot tell a named test from an unnamed one (`skills/maker/SKILL.md:28`). (evidence: `git grep old_tests_forced` finds only the brief; to: scenario. No red test runs a maker against a named test.)
- point 2 (b): "The maker may change those files": the running system still stops it. `.xv/picture.md` stays in `protected` for the maker (`scripts/run.py:424-428`), and `scripts/orders.py:168` raises `protected_changed`. `may_not_files` (`skills/scenario/SKILL.md:63`) is not stored, so neither the maker nor the guardian can see what was named, and the guardian line (`skills/guardian/SKILL.md:26`, "its `may_not_files`") points at nothing. (evidence: the same `git grep` and the hunks above; to: scenario. The red only searches brief wording, `tests/test_briefs_picture.py:137-157`.)

## Door

**Door:** two-way: brief text, one regex and tests, with no data migrated and nothing sent to users; a revert undoes it. **Blast radius:** adopters (the briefs reach every adopting repo through `skills/`).

## Raw data

- Slice record: `.xv/slices/2026-11-04-scenario-catches.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..68db9f6`
- Wall: `xv wall diff 2026-11-04-scenario-catches`
- Boundary: `xv boundary --base a6e023bd0ffeed4f6ce45990c668742a8f758419`

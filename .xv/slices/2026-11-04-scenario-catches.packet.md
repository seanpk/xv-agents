---
slice: 2026-11-04-scenario-catches
shape_change: no
pitch_contradiction: yes
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: The scenario agent catches more before the maker starts: #119, with #110 and #111

**Needs a decision (two people; solo here, so Sean):** the scenario agent's report can now exempt *any* protected file from the maker's `protected_changed` check, including `.xv/pitch.md`, `.xv/config.yml` and the slice's own `wall.json`, not only `.xv/picture.md`. That lets one agent license another to write the pitch with no stop (§2). The last pass's misses on 2a and 2b are met. For Sean as well: three picture edits (§4), one wall recommendation (§5), and two smaller findings (§4).

## The scenario

Six points. (1) The scenario agent marks a one-time wording test slice-only. (2a) Its report names each old test the red forces to change. The maker may change a named test without stopping, and it records the move. (2b) Its report names each may-not file the red needs changed. The maker may change those files and no other file on that list, and the guardian lists those changes. (3) A red case for each way a value can be wrong, plus a case where a read-only agent claims what only a person may give. (4) Each amendment the watch drafts names four things. (5) A `covers` item may name a point by number. (6) A CHANGELOG line for each brief change.
May ignore: the cleaner; naming an amendment's points by number; old slice records.

## The recording

None (a feature). Replay the red: `cd tests && python3 -m unittest test_briefs_picture.ScenarioCatchesTest test_run.NamedByTheScenarioReachTheMakerTest test_run.WatchLoopTest.test_a_covers_item_that_is_a_points_number_covers_it test_run.WatchLoopTest.test_a_covers_item_that_starts_with_the_number_covers_the_point test_run.WatchLoopTest.test_a_number_covers_only_its_own_point test_run.WatchLoopTest.test_the_number_one_does_not_cover_point_ten test_run.WatchLoopTest.test_a_number_item_in_not_covered_still_stops_for_the_person`. Before: 21 of 27 failed (record `checks.scenario.red_output`). After: 27 OK (the guardian ran it on HEAD d282998). The maker and the cleaner each ran the whole suite: 902 OK (record `checks.maker`, `checks.cleaner`).

## The boundary picture

From `.xv/slices/2026-11-04-scenario-catches.boundary.md`, used as given. Touched: `scripts/prompt`, `scripts/record`, `scripts/run`. No modules or edges were added or removed. No new calls leave the process. There are no shape hints.

## What the suite asserts after

- `ScenarioCatchesTest` (11 tests, `tests/test_briefs_picture.py:126-188`): the scenario, maker, guardian and watch briefs and `CHANGELOG.md` contain the words of points 1–4 and 6.
- `NamedByTheScenarioReachTheMakerTest` (11 tests, `tests/test_run.py:941-1024`):
  - A scenario report's `old_tests_forced` and `may_not_files` are kept in the record.
  - An entry with a field that is missing, empty or of the wrong type is dropped, and so is a value that is not a list.
  - The same keys in a maker's report are dropped.
  - The maker's prompt shows the named tests and files, and the cleaner's prompt does not.
  - A named `.xv/picture.md` changed by the maker is not `protected_changed`. An unnamed file, a malformed name, or `.xv/rules.md` next to a named picture still is.
- Five `WatchLoopTest` tests (`tests/test_run.py:492-522`):
  - `"1"` or `"1. Whether a miss repeats"` covers point 1.
  - `"1"` does not cover point 2 or point 10.
  - A number in `not_covered` still stops for the person.
- No old assertion moved.

## 1. Shape

shape_change: no.
- The boundary picture shows no added modules, edges, tables or surfaces, and no hints (`.xv/slices/2026-11-04-scenario-catches.boundary.md:7`, `:12`, `:18`).
- The record gains two front-matter keys, `old_tests_forced` and `may_not_files` (`scripts/record.py:482-485`). They sit beside the `slice_only` key the picture already describes (`.xv/picture.md:23`), in the same file state (`.xv/picture.md:26`). That is inside the current shape.
- The prompt and post-step edits (`scripts/prompt.py:113-117`, `scripts/run.py:428-432`) stay inside functions that already existed.

shape_breadth: narrow, which matches the forecast's `narrow`. The forecast's breadth list names "the maker's may-not handling", which is where the `record`/`prompt`/`run` edits land.

## 2. Pitch

pitch_contradiction: yes. `.xv/pitch.md:11`: "An agent may tidy it; it may not write it. It changes when a second person agrees, and the change is written down in `.xv/decisions/`."

How the change opens that up:
- The maker's protected list includes the pitch: `scripts/run.py:424-425`, `protected = [... config.yml, slices/<id>.wall.json, pitch.md, picture.md, estimation.md, rules.md]`.
- The new exemption takes any file the record's `may_not_files` names: `scripts/run.py:430-432`, `named = {e["file"] for e in data.get("may_not_files") ...}` and `... f not in named]`.
- `may_not_files` comes only from the scenario agent's report (`scripts/record.py:482-485`). No check limits it to `.xv/picture.md`, and no person's answer is needed.
- The maker brief says the same: "you may change a file the report names, and no other file on this list" (`skills/maker/SKILL.md:54`). That list includes `.xv/pitch.md`.

So when the scenario agent names `.xv/pitch.md`, the maker can write the pitch, and the stop that used to catch it (`protected_changed`) no longer fires. A person would see it only through this packet's listing and the merge answer.

The same path reaches `.xv/config.yml` (the test command and allowed tools) and `.xv/slices/<id>.wall.json` (the wall baseline). Those are not pitch matters, but they come through the same opening.

Scenario point 2b asks for "those files" on the may-not list, with `.xv/picture.md` only as an example. Meeting it narrowly, with only the picture or only files a person accepted, may need an amendment. Sean's call.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-04-scenario-catches` shows `changed: [] deleted: [] fewer_assertions: []`, and the record has `moved_tests: []`. The test diff only adds lines.

May-not file changes that the scenario report allowed: none. The record has no `may_not_files` key, so the last scenario report named none. Also `checks.maker.protected_changed: []` and `checks.cleaner.protected_changed: []`, and the diff touches no file under `.xv/` other than this slice's own files.

Slice-only tests removed: none. Kept: none (the record has `slice_only: []`).

## 4. The picture

Proposed edits (Sean accepts them):
- **`.xv/picture.md:35`** says "The maker and the scenario agent … do not edit it [the picture] … Accepting a picture change is a person's." This is now untrue: the maker edits the picture when the scenario report names it (`skills/maker/SKILL.md:54`, `scripts/run.py:430-432`). Rewrite it as: "The maker may edit a may-not file the scenario report names in `may_not_files`; the guardian lists the edit in the packet; accepting it is still a person's." Narrow the wording to match however §2 is settled.
- **`.xv/picture.md:23`**, at `record`: add "The record keeps a scenario report's `old_tests_forced` and `may_not_files` (entries with non-empty string fields only); `xv prompt` shows them to the maker alone." (`scripts/record.py:482-485`, `scripts/prompt.py:113-117`.)
- **`.xv/picture.md:26`**, at the covers check and at `protected_changed`:
  - Add: "A `covers` or `not_covered` item may name a point by its number, `"1"` or an item that starts with the number."
  - Add: "For the maker, a file the record's `may_not_files` names is not `protected_changed`." (`scripts/run.py:521-525`, `scripts/run.py:428-432`.)

Two smaller findings for Sean (not misses):
- **A number covers amendment points too.** `scripts/run.py:521-525` tests `num not in numbers` against every `POINT` between `## Scenario` and `## May ignore`. `xv slice amend` writes amendments into that same range (`scripts/run.py:279-284`). So one `"1"` covers both the scenario's point 1 and an amendment's point 1. The record's May ignore line says "point 5 covers only the scenario's own points". The red's own fixtures place their points through `self.amend` (`tests/test_run.py:493`), so the tests rely on this.
- **A license can outlive its pass.** `scripts/record.py:482-485` replaces the lists only when a scenario report carries them as a list. A later scenario report that leaves out `may_not_files` keeps the earlier license in force. The brief asks for `[]` when there are none (`skills/scenario/SKILL.md:66`), but nothing enforces that.

## 5. The wall

- `tests/test_briefs_picture.py`, `ScenarioCatchesTest.test_the_changelog_has_a_line_for_each_brief_change`: mark it slice-only. It checks a one-time CHANGELOG line, which point 1 calls "always a `slice_only` test" (`skills/scenario/SKILL.md:28`). It also reads only `## Unreleased` (`tests/test_briefs_picture.py:182-188`), so it fails at the next release. (Already in the record's `wall_recommendations`, `accepted: false`.)

## Scenario misses

None. Last pass's 2a and 2b are met. For 2a, the record keeps `old_tests_forced` (`scripts/record.py:482`), and the maker's prompt shows each named test (`scripts/prompt.py:114`). For 2b, the record keeps `may_not_files`, and a named file is exempt from the maker's `protected_changed` while other protected files are not (`scripts/run.py:432`; `tests/test_run.py:1014`).

Points 1, 3, 4 and 6 are in the briefs and the CHANGELOG (`skills/scenario/SKILL.md:28,33`, `skills/watch/SKILL.md:50`, `CHANGELOG.md:7`). Point 5 is `scripts/run.py:521-525`. Point 3's case of an agent writing about itself is tested for the maker (`test_a_maker_that_writes_the_lists_about_itself_does_not_get_them_kept`).

## Door

**Door:** two-way. The change is brief text, two record keys, one prompt block and one check exemption. No data is migrated and nothing is sent to users, so a revert undoes it. **Blast radius:** adopters (the briefs and `scripts/` reach every adopting repo).

## Raw data

- Slice record: `.xv/slices/2026-11-04-scenario-catches.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..d282998`
- Wall: `xv wall diff 2026-11-04-scenario-catches`
- Boundary: `.xv/slices/2026-11-04-scenario-catches.boundary.md`

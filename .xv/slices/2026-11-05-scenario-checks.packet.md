---
slice: 2026-11-05-scenario-checks
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The checks after the scenario step stop less often for no reason: #120, #136, #140

Nothing stops this for two people. Sean Kennedy, who set the work going, has three things to decide: the picture edits (check 4), one wall recommendation (check 5), and three findings under "For the person": what the scenario means by a "new" flag, `xv` at the base in an adopting repo, and a red command that cannot run from the repo root. The merge is Sean's.

## The scenario

When this is done: (1) a `covers` name may start with a red file's path and be split by `::`, `.`, `#`, `/` or ` > `, and it matches when each part after the path is a whole name in that red file, in order; (2) a `red_gaps` name a person accepted at a stop is not raised again on that slice; (3) `wall.red_gaps` does not raise an `xv` command whose words are already a subcommand at the base and that has no new flag; a new flag, or a command missing at the base, is still raised; (4) after a send-back to the scenario agent, coverage from earlier passes stays, so an empty `covers` does not stop the slice, and each kept name must still name a test that exists; (5) after `xv slice amend` on a refactor slice, only the amendment's points need `covers` or `not_covered`; (6) the scenario brief says each red test sets every stand-in setting it depends on, and a test checks for that sentence; (7) `CHANGELOG.md` has the lines. The slice may ignore old slice records.

## The recording

None; this is a feature. To replay the red and the green: `cd tests && python3 -m unittest test_run.ScenarioChecksTest test_run.ScenarioChecksAtTheBaseTest test_run.ScenarioPointsAfterAmendTest test_by_name`. At HEAD: 39 tests ran, OK (12.5 s). The red command as the record has it, run from the repo root, fails to import `helpers` (see "For the person").

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-05-scenario-checks.boundary.md`), as given: modules touched: `scripts/run` and `scripts/wall`. No module added or removed. No edge added or removed. No new call out of the process. No tables. No surface path added or removed. Shape hints: none.

## What the suite asserts after

- The covers name forms: `path::Class.test`, `path::Class::test`, `Class#test`, `path#Class#test`, Go `TestX/sub` and Jest `x > Case > does y` (with spaces) go on to the maker. A later or middle part missing from the file stops. So do parts out of order, a path that is not a red file, an empty part, and a part that is only the front of a longer name (`tests/test_run.py`, `ScenarioChecksTest`).
- Send-back: an empty `covers` after a send-back goes on. A point covered on the earlier pass stays covered. A kept name whose test is gone stops. An empty `covers` on the first pass, or after a send-back with nothing kept, still stops.
- At the base: `xv slice amend` and `xv decisions` are not raised. A flag (`--rename`, `--expect-moves`), `xv ghost` and `xv slice ghost` are still raised. A gap a person accepted is not raised again. One they did not accept still is, including beside an accepted one (`ScenarioChecksAtTheBaseTest`).
- A refactor slice with an amendment needs only the amendment's point. A feature slice still needs its own points (`ScenarioPointsAfterAmendTest`).
- The scenario brief has the stand-in sentence (`tests/test_by_name.py`, `ByNameTest.test_the_scenario_brief_says_a_red_test_sets_every_stand_in_setting_its_result_depends_on`).
- No old assertion moved. The only removal is the slice-only CHANGELOG test (check 3).

## 1. Shape

shape_change: no. shape_breadth: narrow. That matches the forecast's `"shape": "narrow"` in the record's front matter.

- The boundary picture adds no module, edge, table, outbound call or surface, and it gives no shape hints (`.xv/slices/2026-11-05-scenario-checks.boundary.md`, "Shape hints: none", "Edges: added: none").
- `scripts/run.py:984-1004` (`xv_command_at_base`) is new. It runs `git archive <base> bin scripts`, pipes the output to the `tar` program, and runs the base's own `bin/xv <words> --help` in a subprocess. This is inside the current shape: `run` already shells out to git and to the agent CLIs (`.xv/picture.md:21-23`). `.xv/picture.md:66` (decision 3: "standard library only") is not broken in letter, because `tar` is not a Python package. But it is the first use of the `tar` binary in `scripts/` (`git grep '"tar"'` finds only `scripts/run.py:992`), and `tarfile` would keep this in-process. Not a shape change.
- `scripts/wall.py:212`: `red_gaps(scenario, red_texts, exists=None)` gets an optional callback. The `run → wall` edge already exists (`.xv/picture.md:21`).

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7`, "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline", and `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code". The change makes fewer stops that fire for no reason after the scenario step. It changes who the tool serves in no way, and it breaks no promise of the pitch.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_by_name.py` | `ChangelogLinesTest.test_the_unreleased_section_has_a_line_for_each_narrowed_stop_and_the_brief_change`: 4 assertions on the Unreleased CHANGELOG lines (#120, #136, #140, stand-in, accepted `red_gaps`, covers forms) | removed | Cleaner: "checks one CHANGELOG line, which has no value after the slice" | Not forced. It was marked slice-only, and Sean accepted the mark at the `slice_only_marks` stop (record `stops[1]`, `pick: 1`). |

`xv wall diff` gives `tests/test_by_name.py` 16 assertions before and 12 after. The baseline count of 16 was taken with the red's two tests in it (the base has 11 `self.assert` lines and HEAD has 12, by `grep -c` on `5d5e75f` and HEAD). The drop of 4 is all from the slice-only removal. Against the base, the file asserts one more thing.

Slice-only tests removed: `tests/test_by_name.py::ChangelogLinesTest.test_the_unreleased_section_has_a_line_for_each_narrowed_stop_and_the_brief_change`. Kept: none.

Expected moves: none (the record has no `expected` moves). Changes to may-not files that the scenario report allowed (`may_not_files`): none. Old tests the scenario forced (`old_tests_forced`): none. `tests/test_run.py` only gains lines over the base (`git diff 5d5e75f..HEAD -- tests/test_run.py`: 240 insertions, 0 deletions).

## 4. The picture

- `.xv/picture.md:27`, "`Class.test`, `module.Class.test` and `file::test` match only when the file or module is a red file and the class is in a red file that has the test", is now untrue. `scripts/run.py:937-962` (`covers_name_found`) drops the `class` declaration check and `names_test`. Proposed edit: "A `covers` name may start with a red file's path or module and is split by `::`, `.`, `#`, `/` or ` > `; it matches when each part after the path is a whole word in that red file, in order (`run.covers_name_found`)."
- `.xv/picture.md:27`, "`covers` empty" stops, is now incomplete (`scripts/run.py:813-815`, `with_kept_covers`). Proposed addition: "On a later scenario pass, the coverage kept from earlier passes (`checks.scenario.covers_kept`) is added to the report's `covers` before the check, so an empty `covers` does not stop when something was kept; each kept name is checked again against the red files."
- `.xv/picture.md:23`, "`wall` holds … `red_gaps`, which lists each flag and `xv` command written in backticks in the scenario that no red file has", is now incomplete (`scripts/wall.py:212-229`, `scripts/run.py:973-977`). Proposed addition: "…except an `xv` command that is a subcommand at the slice's base (run checks this with the base's own `bin/xv <words> --help`, from `git archive`), and a gap named in an answered `red_misses_scenario` stop that was not sent back."
- `.xv/picture.md:27`, "After an amend, the scenario agent writes a red as on a feature slice", is now incomplete (`scripts/run.py:898-899`). Proposed addition: "…and only the amendment's points need `covers` or `not_covered`."
- `.xv/picture.md:23`, "`xvlib` is the shared base (… the shared test-name matcher `names_test`)", is now incomplete. `covers_name_found` has its own whole-word matcher (`scripts/run.py:953-958`), and `names_test` is still used by `record.py:221` and `run.py:484`. Proposed addition: "`covers` names use `run.covers_name_found`."

## 5. The wall

- `tests/test_run.py`, `ScenarioChecksTest.test_an_empty_covers_on_the_first_pass_still_stops`: should be marked slice-only. It sends the same `FAKE_REPORT_EXTRA='{"covers": []}'` on a first pass and asserts a stop naming "covers". The wall already guards this with `test_an_empty_covers_stops_before_the_maker` (`tests/test_run.py:283-285`) and `test_an_empty_covers_list_stops_before_the_maker` (`tests/test_run.py:326-327`). Its sibling `test_an_empty_covers_after_a_send_back_still_stops_when_nothing_was_kept` covers the new path.
- I also looked at `test_a_covers_part_that_is_only_the_front_of_a_longer_name_stops` against `tests/test_run.py:295` and `test_a_covers_name_with_an_empty_part_between_separators_stops` against `tests/test_run.py:385`. Each one runs through the new path-prefix parsing, so they are not restatements. No old wall test is made dead: the suite was green after the maker and the cleaner (record `checks.maker.suite`, `checks.cleaner.suite`), and the old covers tests still assert behavior that holds.

## For the person

These name no scenario line or binding decision as missed. They are for Sean.

- **A "new flag" in point 3.** The scenario's examples of "a new flag on an existing command, such as `--rename` or `--expect-moves`" are flags that `xv slice new` already has at the base (`git show 5d5e75f:scripts/run.py:1516-1517`). The code raises every flag in backticks, whether the base has it or not (`scripts/wall.py:216-220` has no `exists` check). So `` `xv decisions --since <date>` `` still stops on `--since`, though `decisions.py:42` has it at the base. This matches the scenario's own examples and `test_a_new_flag_on_an_existing_command_is_still_raised`. If "new" was meant as "not at the base", that is an amendment, not a maker fix.
- **`xv` at the base in an adopting repo.** `xv_command_at_base` reads `bin/` and `scripts/` from the slice's base (`scripts/run.py:990-991`). In a repo that adopts xv, the base does not carry xv's source (`.xv/picture.md:25`, `defaults/` is copied into adopting repos). There, `git archive` fails, the function returns `False`, and every `xv` command is raised as before. This fails safe (`.xv/picture.md:75`, decision 12), but point 3 helps only this repo.
- **The red command cannot run from the repo root.** The record's `red.command`, `python3 -m unittest tests.test_run.ScenarioChecksTest …`, gives `ModuleNotFoundError: No module named 'helpers'` (4 errors in 0.000 s) when run from the repo root, and so it would fail at any commit. The record's own `checks.scenario.red_output` shows exactly that, and `red_fails: true` was recorded from it. So the record holds no evidence that the red failed for the reasons named. `.xv/picture.md:75` (decision 12: "A check whose input is broken or that cannot run stops for a person; it never passes") suggests the red check should have stopped on an import error. This is about xv's red check, not this diff; it may need its own issue.

## Door

**Door:** two-way. A revert of `scripts/run.py`, `scripts/wall.py`, `skills/scenario/SKILL.md` and the CHANGELOG line undoes it; no data migrated and no message sent. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-scenario-checks.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..1315c3c`
- Wall: `xv wall diff 2026-11-05-scenario-checks`
- Boundary: `xv boundary --base 5d5e75fc7a7371d74a3884cfbae919785adbb4e7` (`.xv/slices/2026-11-05-scenario-checks.boundary.md`)

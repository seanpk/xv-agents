---
slice: 2026-11-05-scenario-checks
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 5
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The checks after the scenario step stop less often for no reason: #120, #136, #140

Nothing here stops the slice for two people. Two scenario misses send it back to the scenario agent. Both are about amendment points: point 11, a removed test that the record names with extra words, and point 9, an adopting repo that has its own `bin/` and `scripts/`. Both misses fail toward a stop, never toward a pass. After that, Sean has the picture edits (check 4) and two smaller notes under "For the person". The merge is Sean's.

## Scenario misses

- Point 11 ("A `covers` name for a slice-only test that the cleaner removed, as the record shows, does not stop the slice"). Evidence: `scripts/run.py:935` builds the removed names by splitting each cleaner move's `assertion` on `COVERS_SEPARATOR` and keeping the last part. This slice's own record has the cleaner's move with the assertion `"ChangelogPointsEightToElevenTest.test_the_unreleased_section_has_a_line_for_the_flags_the_adopting_repo_and_the_slice_only_files; removed"` (`.xv/slices/2026-11-05-scenario-checks.md:15`, the fifth move). Its last part is `test_…_slice_only_files; removed`, which never equals the covers name's last part. So on the next scenario pass, a kept or reported `covers` name for that test stops the slice with "no red file has that test". That is the false stop point 11 removes. The red only uses a bare assertion (`tests/test_run.py:1477`, `"assertion": test`). **to: scenario**.
- Point 9 ("In a repo whose base does not hold xv's own source, points 3 and 8 check against the installed `xv`"). Evidence: `scripts/run.py:1008` runs `git archive <base> bin scripts` and falls back to the installed xv only when that fails. An adopting repo that has its own `bin/` and `scripts/` passes the archive step. The extracted tree then has no `bin/xv`, so `scripts/run.py:1023` exits non-zero and `xv_help_at_base` returns `None`. Every `xv` command and flag is then raised, as before this slice. The red covers only a base with no `scripts/` (`tests/test_run.py:1357`, `test_the_base_holds_no_xv_source`). **to: scenario**.

## The scenario

Points 1–7: a `covers` name may start with a red file's path and be split by `::`, `.`, `#`, `/` or ` > `. A `red_gaps` name a person accepted is not raised again. An `xv` command that exists at the base is not raised. Coverage from earlier passes stays after a send-back. A refactor amend needs only the amendment's points. The brief has a stand-in sentence. There is a CHANGELOG line. The 2026-11-05 amendment adds points 8–12: a flag the base's command already has is not raised (8). With no xv source at the base, the checks use the installed `xv` (9). `tests.slice_only_files` (default `CHANGELOG.md`) lets a mark be accepted with no stop and a log line, and a mark on any other file still stops (10). A `covers` name for a slice-only test the cleaner removed does not stop (11). A CHANGELOG line (12). The slice may ignore old slice records.

## The recording

None; this is a feature. Replay: `cd tests && python3 -m unittest test_by_name test_run.ScenarioChecksTest test_run.ScenarioChecksAtTheBaseTest test_run.AtAnAdoptingReposBaseTest test_run.SliceOnlyFilesTest test_run.RemovedSliceOnlyTestInCoversTest test_run.ScenarioPointsAfterAmendTest`. At HEAD it ran 67 tests: OK, in 22.3 s. The earlier packet's finding about the red command (an import error from the repo root) is settled: the command now starts with `cd tests &&`.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-05-scenario-checks.boundary.md`), as given. Modules touched: `scripts/record`, `scripts/run`, `scripts/wall`, `scripts/xvlib`. No module, edge, outbound call, table or surface path was added or removed. Shape hints: none.

## What the suite asserts after

- Covers name forms, send-back coverage, accepted gaps and refactor amend points: the same as the earlier packet (`ScenarioChecksTest`, `ScenarioPointsAfterAmendTest`).
- At the base: `xv slice amend` and `xv decisions` are not raised. A flag the base's command has is not raised. A flag it lacks (`--priority` on `xv slice new`), `xv ghost` and `xv slice ghost` are still raised (`ScenarioChecksAtTheBaseTest`).
- In a base with no `scripts/`, the installed `xv` decides the same things (`AtAnAdoptingReposBaseTest`).
- A slice-only mark whose `checks` is on `tests.slice_only_files` is accepted, and the log says so. A mark on another file still stops. An agent's report cannot set `accepted` (`SliceOnlyFilesTest`).
- A `covers` name for a slice-only test the cleaner removed does not stop, whether it is reported or kept (`RemovedSliceOnlyTestInCoversTest`).
- The three `WatchLoopTest` word-order tests assert the same stop or go as before, on `xv slice ghost`.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"` (record front matter).

- The boundary picture (`.xv/slices/2026-11-05-scenario-checks.boundary.md`) adds no module, edge, table, outbound call or surface. Shape hints: none.
- `scripts/run.py:1002-1030` reads the base with `git archive` and the standard library's `tarfile`, and runs the base's own `bin/xv <words> --help` in a subprocess. `run` already shells out to git and to the agent CLIs (`.xv/picture.md:21`). Using `tarfile` keeps `.xv/picture.md:66` (decision 3, "standard library only"), which settles the earlier packet's `tar` note. It is inside the current shape.
- `scripts/wall.py:212-230`: `red_gaps` gets the `exists` and `has_flag` callbacks over the existing `run → wall` edge.
- The new `tests.slice_only_files` key in `scripts/xvlib.py:223`, `defaults/config.yml:36-38` and `.xv/config.yml:24-26` is a config setting. It is not a new surface.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). The change only removes false stops after the scenario step. It serves the same people, and the stops it keeps still fail closed.

## 3. Moved tests

| File | Before | After | Why (record) | Forced? |
| --- | --- | --- | --- | --- |
| `tests/test_run.py` | `WatchLoopTest.test_a_command_whose_words_are_apart_in_the_red_stops_before_the_maker` on `xv slice amend` | the same stop on `xv slice ghost` | maker: `xv slice amend` exists at the base, so it is no longer raised | Yes, by points 3 and 8. The assertion is no weaker. Sean accepted it at `unrecorded_move` (stops[5]). |
| `tests/test_run.py` | `…words_are_out_of_order…stops_before_the_maker` on `xv slice amend` | the same on `xv slice ghost` | the same reason | Yes, the same |
| `tests/test_run.py` | `…words_are_together_in_order…goes_on_to_the_maker` on `xv slice amend` | the same on `xv slice ghost` | changed with the other two so all three agree | Not strictly forced: `amend` would still go on. It is harmless, and Sean accepted it. |

`xv wall diff`: `tests/test_by_name.py` has 14 assertions before and 13 after, all from the slice-only removal below. `tests/test_run.py` has no recorded drop.

Slice-only removed: `ChangelogLinesTest.test_the_unreleased_section_has_a_line_for_each_narrowed_stop_and_the_brief_change` and `ChangelogPointsEightToElevenTest.test_the_unreleased_section_has_a_line_for_the_flags_the_adopting_repo_and_the_slice_only_files` (`tests/test_by_name.py`). Kept: none.

May-not files the scenario report allowed (`may_not_files`): `.xv/config.yml`, which gained `slice_only_files: ["CHANGELOG.md"]` in 500f74f, added by the watch as Sean directed (`.xv/config.yml:24-26`). Also, `.xv/picture.md` changed in 8eb6c02, as Sean directed: the earlier packet's picture edits.

## 4. The picture

- `.xv/picture.md:23`, the `red_gaps` sentence, is incomplete. Add: "…nor a flag that the command it follows already has at the base (its `--help` text). The base is read with `git archive` and `tarfile`. When the base has no `bin` and `scripts`, the installed `xv` is used (`run.base_xv_dir`)." (`scripts/run.py:1002-1035`, `scripts/wall.py:222`)
- `.xv/picture.md:23`, the `slice_only_marks` sentences, are incomplete. Add: "A mark whose `checks` names a file listed in `tests.slice_only_files` (default `CHANGELOG.md`) is accepted by the watch with a log line, and it is not asked about. An agent's report cannot set `accepted` on its own mark." (`scripts/run.py:736-744`, `scripts/record.py:517-519`)
- `.xv/picture.md:27`, the `covers` sentences, are incomplete. Add: "A `covers` name whose last part is a slice-only test that the cleaner removed, by a recorded move, does not stop." (`scripts/run.py:935-941`)

## 5. The wall

- `tests/test_run.py`, `ScenarioChecksTest.test_an_empty_covers_on_the_first_pass_still_stops`: it should stay marked slice-only, as Sean accepted at `accept_moves` (record `wall_recommendations`). It restates `tests/test_run.py:283` and `:326`.
- I looked for any old wall test made dead by points 8–11. The three `WatchLoopTest` tests were moved, not killed (check 3). The suite was green after the maker and the cleaner (record `checks.maker.suite`, `checks.cleaner.suite`).

## For the person

- **The record's second slice-only mark is not marked `accepted`.** Sean accepted it in his answer to `red_misses_scenario`, which bundled `slice_only_marks` (`.xv/slices/2026-11-05-scenario-checks.md:24`, stops[3] `settled`). Yet its `slice_only` entry has no `accepted: true` (`.xv/slices/2026-11-05-scenario-checks.md:16`). It looks as if a bundled answer does not mark the bundled order's marks. That is xv at the base, not this diff. With this diff, `accept_listed_marks` (`scripts/run.py:736`) would accept it anyway, because `checks` is `CHANGELOG.md`.
- **Point 11 matches on the last name part only, in any file.** `scripts/run.py:941` lets any `covers` name pass when its last part equals a removed test's name, whatever its path or class. A wrong path or class before a removed name would not stop.

## Door

**Door:** two-way. A revert undoes it. `defaults/config.yml` reaches only new adopters (`.xv/picture.md:25`), no data is migrated, and no message is sent. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-scenario-checks.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`
- Wall: `xv wall diff 2026-11-05-scenario-checks`
- Boundary: `.xv/slices/2026-11-05-scenario-checks.boundary.md`

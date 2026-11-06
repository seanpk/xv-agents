---
slice: 2026-11-05-scenario-checks
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 5
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The checks after the scenario step stop less often for no reason: #120, #136, #140

Nothing stops the slice for two people. The two misses from the last packet (points 9 and 11) are now met, and I found no new miss. Sean has two things to decide in `accept_moves`: the picture edits in check 4, which the last packet proposed and the picture still lacks, and one note under "For the person". The merge is Sean's.

## The scenario

Points 1–7: a `covers` name may start with a red file's path and be split by `::`, `.`, `#`, `/` or ` > `. A `red_gaps` name a person accepted is not raised again. An `xv` command that exists at the base is not raised. Coverage from earlier passes stays after a send-back. A refactor amend needs only the amendment's points. The brief gets a sentence on stand-in settings. CHANGELOG gets a line. The 2026-11-05 amendment adds points 8–12:

- 8: a flag that the base's command already has is not raised.
- 9: when the base holds no xv source, the checks use the installed `xv`.
- 10: `tests.slice_only_files` (default `CHANGELOG.md`) accepts a mark with no stop and logs it. A mark on any other file still stops.
- 11: a `covers` name for a slice-only test that the cleaner removed does not stop.
- 12: a CHANGELOG line.

The slice may ignore old slice records.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest test_by_name test_run.ScenarioChecksTest test_run.ScenarioChecksAtTheBaseTest test_run.AtAnAdoptingReposBaseTest test_run.AtAnAdoptingReposBaseWithItsOwnBinAndScriptsTest test_run.SliceOnlyFilesTest test_run.RemovedSliceOnlyTestInCoversTest test_run.ScenarioPointsAfterAmendTest`. At HEAD (0010c0e) it ran 75 tests and passed, in 30.9 s. The whole suite, `python3 tests/run.py --jobs 4`, at HEAD: 860 tests, OK, exit 0.

## The boundary picture

This is from `xv boundary` (`.xv/slices/2026-11-05-scenario-checks.boundary.md`), as given. Modules touched: `scripts/record`, `scripts/run`, `scripts/wall`, `scripts/xvlib`. No module, edge, outbound call, table or surface path was added or removed. Shape hints: none.

## What the suite asserts after

- Covers name forms, send-back coverage, accepted gaps and refactor amend points (`ScenarioChecksTest`, `ScenarioPointsAfterAmendTest`).
- At the base, `xv slice amend` and `xv decisions` are not raised, and neither is a flag that the base's command has. A flag the command lacks (`--priority` on `xv slice new`) is still raised, and so are `xv ghost` and `xv slice ghost` (`ScenarioChecksAtTheBaseTest`).
- New since the last packet: the installed `xv` decides the same four cases in two kinds of base. One has no `scripts/` (`AtAnAdoptingReposBaseTest`, `tests/test_run.py:1369`). The other has its own `bin/` and `scripts/` but no `bin/xv` (`AtAnAdoptingReposBaseWithItsOwnBinAndScriptsTest`, `tests/test_run.py:1392`). Both classes share a base class with no tests, `AdoptingReposShared` (`tests/test_run.py:1344`), so `NoRerunTest` stands.
- A slice-only mark whose `checks` is on `tests.slice_only_files` is accepted, and the log says so. A mark on another file still stops. An agent's report cannot set `accepted` (`SliceOnlyFilesTest`).
- A `covers` name for a slice-only test that the cleaner removed does not stop, whether it is reported or kept. New since the last packet: this holds even when the move's assertion has words after a `;` (`tests/test_run.py:1554`, `:1558`). The words after the `;` never count as a name (`tests/test_run.py:1564`).
- The three `WatchLoopTest` word-order tests give the same stop or go as before, on `xv slice ghost`.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"` (record front matter, `.xv/slices/2026-11-05-scenario-checks.md:11`).

- The boundary picture adds no module, edge, table, outbound call or surface, and it has no shape hints (`.xv/slices/2026-11-05-scenario-checks.boundary.md:7`, `:12-13`, `:18-19`, `:114-115`, `:119-120`).
- The fix since the last packet stays inside `run`. At `scripts/run.py:1013-1014`, `+ if not os.path.isfile(os.path.join(tmp.name, "bin", "xv")): tmp = None`, so a base without `bin/xv` falls back to the installed xv. At `scripts/run.py:935`, `m["assertion"].split(";")[0]` drops the cleaner's trailing words. Neither adds an edge or a dependency.
- The base is still read with `git archive` and the standard library's `tarfile` (`scripts/run.py:1008-1012`). That keeps decision 3, "standard library only" (`.xv/picture.md:66`).
- `tests.slice_only_files` (`scripts/xvlib.py:223`, `defaults/config.yml:38`, `.xv/config.yml:26`) is a config setting, not a new surface.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy … to adopt Xtreme Vibing in a repo") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). The change removes false stops after the scenario step. It serves the same people. Point 9 now works in an adopting repo that has its own `bin/` and `scripts/`, which is the pitch's adopting repo.

## 3. Moved tests

| File | Before | After | Why (record) | Forced? |
| --- | --- | --- | --- | --- |
| `tests/test_run.py` | `WatchLoopTest.test_a_command_whose_words_are_apart_in_the_red_stops_before_the_maker` on `xv slice amend` | the same stop on `xv slice ghost` | maker: `xv slice amend` exists at the base, so it is no longer raised | Yes, by points 3 and 8. The test asserts no less. Sean accepted it at `unrecorded_move` (`.xv/slices/2026-11-05-scenario-checks.md:24`, stops[5]). |
| `tests/test_run.py` | `…words_are_out_of_order…stops_before_the_maker` on `xv slice amend` | the same on `xv slice ghost` | the same reason | Yes, the same |
| `tests/test_run.py` | `…words_are_together_in_order…goes_on_to_the_maker` on `xv slice amend` | the same on `xv slice ghost` | changed with the other two so all three agree | Not strictly: `amend` would still go on. It asserts no less, and Sean accepted it. |

`xv wall diff 2026-11-05-scenario-checks`, against baseline 1a00893: `changed: []`, `deleted: []`, `fewer_assertions: []`. Since the last packet, the four `AtAnAdoptingReposBaseTest` bodies moved into `check_…` helpers on `AdoptingReposShared` (`tests/test_run.py:1352-1366`). Those are this slice's own red tests, not wall tests, and each one asserts the same as before.

Slice-only removed: `ChangelogLinesTest.test_the_unreleased_section_has_a_line_for_each_narrowed_stop_and_the_brief_change` and `ChangelogPointsEightToElevenTest.test_the_unreleased_section_has_a_line_for_the_flags_the_adopting_repo_and_the_slice_only_files` (`tests/test_by_name.py`). Kept: none.

May-not files: the record's `may_not_files` is now `[]` (`.xv/slices/2026-11-05-scenario-checks.md:30`). Two may-not files still changed in the diff, both as Sean directed. `.xv/config.yml:24-26` gained `slice_only_files: ["CHANGELOG.md"]` in 500f74f. `.xv/picture.md` took the first packet's edits in 8eb6c02.

## 4. The picture

The last packet proposed these three edits, and `.xv/picture.md` at HEAD still lacks them: it has no `slice_only_files` and no "installed". The edits are restated here with the point 9 fix:

- `.xv/picture.md:23`, the `red_gaps` sentence, is incomplete. After "…from `git archive`)", add: "…nor a flag that the command it follows already has at the base (in its `--help` text). The base is read with `tarfile`. When the base has no `bin/xv`, the installed `xv` answers instead (`run.base_xv_dir`)." Evidence: `scripts/run.py:1002-1034`.
- `.xv/picture.md:23`, the `slice_only_marks` sentences, are incomplete. Add: "A mark whose `checks` names a file listed in `tests.slice_only_files` (default `CHANGELOG.md`) is accepted by the watch with a log line and is not asked about. An agent's report cannot set `accepted` on its own mark." Evidence: `scripts/run.py:736-744`.
- `.xv/picture.md:27`, the `covers` sentences, are incomplete. Add: "A `covers` name whose last part is a slice-only test that the cleaner removed by a recorded move does not stop. Only the move's assertion before a `;` is read." Evidence: `scripts/run.py:935-941`.

## 5. The wall

- `tests/test_run.py`, `ScenarioChecksTest.test_an_empty_covers_on_the_first_pass_still_stops`: it should stay marked slice-only, as Sean accepted at `accept_moves` (`.xv/slices/2026-11-05-scenario-checks.md:17`). It restates `tests/test_run.py:283` and `:326`.
- I also looked at the eleven tests added since the last packet (`tests/test_run.py:1344-1430`, `:1554-1567`). Each one guards a separate case of point 9 or point 11, so I recommend none of them. No old wall test is made dead (`xv wall diff`: `deleted: []`).

## For the person

- **The record's second slice-only mark is still not `accepted`.** Sean accepted it at three bundled `slice_only_marks` stops (`.xv/slices/2026-11-05-scenario-checks.md:24`). Yet its `slice_only` entry has no `accepted: true` (`.xv/slices/2026-11-05-scenario-checks.md:16`). The picture says "An answer marks every listed mark `accepted`" (`.xv/picture.md:23`). It looks as if a bundled answer does not mark the bundled order's marks. That is the base's code, not this diff. With this diff, `accept_listed_marks` (`scripts/run.py:736`) accepts the mark anyway, because its `checks` is `CHANGELOG.md`.
- **Point 11 matches on the last name part only, in any file.** At `scripts/run.py:940`, any `covers` name passes when its last part equals a removed test's name, whatever its path or class. This is unchanged from the last packet.

## Door

**Door:** two-way. A revert undoes it. `defaults/config.yml` reaches only new adopters (`.xv/picture.md:25`), no data is migrated, and no message is sent. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-scenario-checks.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD` (since the last packet: `git diff fa30e28..HEAD`)
- Wall: `xv wall diff 2026-11-05-scenario-checks`
- Boundary: `.xv/slices/2026-11-05-scenario-checks.boundary.md`

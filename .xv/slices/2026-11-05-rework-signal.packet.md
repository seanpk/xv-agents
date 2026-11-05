---
slice: 2026-11-05-rework-signal
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A retro is due when the same code needs rework: #114

**Needs a decision (originator):** no shape stop, no pitch stop and no scenario miss. Both earlier misses (points 1 and 4) are fixed and tested. Two things are left for you. First, the picture edits that waited for this last pass (section 4). Second, one question on point 1: as written, a rebase that needs a maker run also counts as a send-back (section 4, last bullet). The merge is yours.

## The scenario

1. When a slice closes, its record keeps `modules_touched` (what `xv boundary` lists as touched) and `maker_sendbacks` (how many times the slice went back to the maker). Sean settled at `accept_moves` (22:35) that this means the maker runs after the first, so a send-back through the scenario agent counts.
2. `xv retro due` gives a reason when one module was touched by at least `limits.rework_slices` closed slices since the last retro, each sent back to the maker at least once. The reason names the module and the slices.
3. `limits.rework_slices` is in `.xv/config.yml` and `defaults/config.yml`. The default is 3, and 0 turns it off.
4. For such a module, the retro proposes a `kind: refactor` candidate. `xv retro accept` on it prints `xv slice new --kind refactor` and opens no slice.
5. `CHANGELOG.md` has a line for the retro brief change.

May ignore: old records without the new fields, which count as never sent back.

## The recording

None, because this is a feature. To replay the red and the green: `cd tests && python3 -m unittest test_retro.ReworkSignalTest`. I ran it on this pass: 17 tests, OK. The recorded form `python3 -m unittest tests.test_retro.ReworkSignalTest` cannot import `helpers` from the repo root (record `checks.scenario.red_output`). Whole suite: 809 OK (record `checks.cleaner.suite_output`). I did not rerun it.

## The boundary picture

From `.xv/slices/2026-11-05-rework-signal.boundary.md`, as given:

- Touched: `scripts/record`, `scripts/retro`, `scripts/run`, `scripts/xvlib`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

## What the suite asserts after

- **Close:** a closed slice has `modules_touched == ["pantry/store"]` in the fixture. `maker_sendbacks` is 0 when the slice was never sent back. It is 1 after any one of these: the watch's send-back to the maker, a person's `--next maker`, or a person's `--next scenario` followed by a second maker run (`tests/test_retro.py:225-273`).
- **Due:** `due` names the module and all three slices. These do not count: slices never sent back, slices not closed, slices from before the last retro, and old records without the fields. Slices on different modules do not add up, and only the module they share is named (`tests/test_retro.py:133-184`).
- **Limit:** the default is 3 when the key is missing, a lower limit lowers it, and 0 turns it off (`tests/test_retro.py:186-205`).
- **Retro prompt and accept:** the prompt names a reworked module and asks for `kind: refactor`, and it leaves out modules reworked before the last retro. `accept` on a refactor candidate prints the step and opens nothing (`tests/test_retro.py:275-330`).
- No old assertion moved. Every changed test is new in `ReworkSignalTest`.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (record `forecast.shape: "narrow"`).

- `import boundary as b` in `close` (`scripts/run.py:1161`) is no new edge. The boundary picture has `edges_added: []`, and `.xv/picture.md:21` already says "`run` reaches ... `boundary`".
- `modules_touched`, `maker_sendbacks` (`scripts/run.py:1162-1167`) and `sent_back_to` (`scripts/record.py:389`) are fields in the file-backed record (`.xv/picture.md:27`, "No database. State is files"). They add no table.
- `limits.rework_slices` (`defaults/config.yml:69-71`, `scripts/xvlib.py:230-231`, `.xv/config.yml:57-58`) is a key in the existing `limits` block. It is no new surface.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code". The refactor candidate only prints a command for a person (`scripts/retro.py:247-250`). Nothing opens a slice on its own, and no new user is served.
- Binding decision 1 (`.xv/picture.md:64`, a brief change "needs two people and a line in `CHANGELOG.md`"). The retro brief changed (`skills/xv-retro/retro-brief.md:28,45`). The CHANGELOG line (`CHANGELOG.md:7`) says "Decided by Sean, solo", and the repo runs `two_people: solo` (`.xv/config.yml:48`). That is how the repo already meets decision 1, so it is not a miss.

## 3. Moved tests

`xv wall diff`: `tests/test_retro.py` has 58 assertions before and 57 after, from baseline `22e03ee`. Both moves are recorded slice-only removals of tests this slice added. No old test changed.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_retro.py | `test_the_default_limit_is_three_in_the_repo_and_in_the_defaults` asserted 3 in both config files | removed | cleaner: "pins this repo's own tunable config value, a one-time edit; the runtime default is guarded by test_without_the_key_the_limit_is_three" | Not forced. It is a slice-only removal, accepted by Sean at `accept_moves` (`accepted_wall`) |

Slice-only tests removed: `ReworkSignalTest.test_the_changelog_has_a_line_for_the_retro_brief_change` (the line stands at `CHANGELOG.md:7`) and `ReworkSignalTest.test_the_default_limit_is_three_in_the_repo_and_in_the_defaults` (the value stands at `.xv/config.yml:58` and `defaults/config.yml:71`). Kept: none.

`may_not_files`: `[]`. The `.xv/config.yml` line was added by the watch as Sean directed at `maker_stopped` (record `stops`, 18:52), not by the maker.

## 4. The picture

picture_change: yes. `.xv/picture.md:23` and `:31-43` become incomplete. The proposed edits, in words:

- **`.xv/picture.md:23`:** `run.close` writes `modules_touched` from `boundary.change` against the slice's base, and `maker_sendbacks` (`scripts/run.py:1161-1167`). A person's answer that sends work back keeps `sent_back_to: <step>` (`scripts/record.py:389`). `retro.reworked` finds the modules that at least `limits.rework_slices` closed, sent-back slices touched (`scripts/retro.py:91-99`). `due` and the retro prompt both use it on slices created since the last retro (`scripts/retro.py:84`, `:177-178`). `retro.accept` treats `kind: refactor` as print-only (`scripts/retro.py:247-250`).
- **Names (`.xv/picture.md:31-43`):** add that `maker_sendbacks` is the larger of two counts: maker spend rows minus one, and stops answered "sent back to the maker" or with `sent_back_to: maker` (`scripts/run.py:1163-1167`).
- **For the originator to settle, not a miss:** a rebase maker run writes a spend row with `step="maker"` (`scripts/run.py:427`), and its spend goes into the record when the rebase finishes (`.xv/picture.md:27`, "On finish they go into the record"). `close` counts every maker row (`scripts/run.py:1163`). So a slice that was rebased with a maker run, and never sent back, closes with `maker_sendbacks` of 1 or more, and it can make a module due. That fits Sean's settle ("the maker runs after the first"). It does not fit point 1's "went back to the maker" if a rebase is not rework. Either the Names entry says rebases count, or the scenario is amended to exclude them.

## 5. The wall

I looked at the 17 tests in `ReworkSignalTest` (`tests/test_retro.py:102-330`) and at the two recorded slice-only removals. The earlier recommendation, to mark `test_the_default_limit_is_three_in_the_repo_and_in_the_defaults` slice-only, was accepted, and that test is removed. I have no new recommendations. Each remaining test guards a distinct branch of `reworked`, `close` or `accept`. None of them pins a one-time edit, and none restates another.

## Door

**Door:** two-way. The record fields and the config key are additive, and a revert removes them. Old records without the fields already count as never sent back. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-rework-signal.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`
- Wall: `xv wall diff 2026-11-05-rework-signal` (baseline `.xv/slices/2026-11-05-rework-signal.wall.json`)
- Boundary: `.xv/slices/2026-11-05-rework-signal.boundary.md`
- Earlier guardian passes: record `stops` at 19:11 (`scenario_miss`, points 1 and 4) and 22:25 (`accept_moves`)

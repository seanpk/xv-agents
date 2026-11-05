---
slice: 2026-11-05-rework-signal
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

# Packet: A retro is due when the same code needs rework: #114

**Needs a decision:** one scenario miss on point 1. It uses the same key as the first pass's miss, so it may stop for you rather than go back. A send-back that goes through the scenario agent and then back to the maker is not counted in `maker_sendbacks`. This slice is an example: the maker was sent back twice and would close with `maker_sendbacks: 0`. One wall recommendation, repeated from the first pass, is still not accepted.

## The scenario

1. A closed slice's record keeps `modules_touched` (from `xv boundary`) and `maker_sendbacks`.
2. `xv retro due` gives a reason when one module was touched by at least `limits.rework_slices` closed slices since the last retro, each sent back to the maker. The reason names the module and the slices.
3. `limits.rework_slices` is in `.xv/config.yml` and `defaults/config.yml`. The default is 3, and 0 is off.
4. The retro proposes a `kind: refactor` candidate. `xv retro accept` prints `xv slice new --kind refactor` and opens no slice.
5. A CHANGELOG line.

May ignore: old records without the new fields.

## The recording

None (feature). To replay: `cd tests && python3 -m unittest test_retro.ReworkSignalTest`. That runs 17 tests, OK in 18 s. The recorded red command, `python3 -m unittest tests.test_retro.ReworkSignalTest`, fails from the repo root with `No module named 'helpers'`, the same as in the record's `checks.scenario.red_output`.

## The boundary picture

`.xv/slices/2026-11-05-rework-signal.boundary.md`: modules touched are `scripts/record`, `scripts/retro`, `scripts/run` and `scripts/xvlib`. No modules, edges, tables, surface paths or outbound calls are added or removed. Shape hints: none.

## What the suite asserts after

- A closed slice has `modules_touched` equal to what `xv boundary` lists (`pantry/store` in the fixture). It has `maker_sendbacks` 0 when the slice was never sent back, and 1 after either the watch's send-back or a person's `--next maker` answer.
- `due` names the module and its slices at 3 closed, sent-back slices. It does not count slices never sent back, not closed, from before the last retro, or old records without the fields. Slices on different modules do not add up, and only the module they share is named.
- The limit: the default is 3 when the key is missing, a lower limit lowers it, and 0 turns it off. The value 3 is in both config files.
- The retro prompt names a reworked module and asks for `kind: refactor`. It leaves out modules reworked before the last retro.
- `accept` on a refactor candidate prints the `slice new --kind refactor` step and opens nothing.
- The whole suite has 809 tests, OK (record `checks.cleaner.suite_output`).

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`forecast.shape: narrow`).

- The boundary picture lists `edges_added: []` and `modules_added: []`. The one import, `import boundary as b` in `close` (`scripts/run.py:1161`), is an edge that already exists: `.xv/picture.md:21` says "`run` reaches ... `boundary`", and `scripts/run.py:1096` already imports it.
- The new record fields `modules_touched`, `maker_sendbacks` and `sent_back_to` (`scripts/run.py:1162-1165`, `scripts/record.py:389`) are fields inside the existing file-backed record (`.xv/picture.md:27`, "No database"). They are not a table.
- The new config key `limits.rework_slices` (`defaults/config.yml:69-71`, `scripts/xvlib.py:230-231`) sits inside the existing `limits` block.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code") and `.xv/pitch.md:21`, which names the users. The change adds a retro signal and prints a command for a person to run (`scripts/retro.py:247-250`), so a person still decides on the refactor. It does not serve anyone new, and it breaks no promise.

## 3. Moved tests

- Slice-only removal: `ReworkSignalTest.test_the_changelog_has_a_line_for_the_retro_brief_change` was removed by the cleaner, with the reason "checks one CHANGELOG line, which has no value once the line exists". It is recorded (`moved_tests`, `slice_only: true`), and the CHANGELOG line it guarded is at `CHANGELOG.md:7`.
- No slice-only tests were kept.
- `may_not_files` in the scenario agent's report: `[]`. The repo's `.xv/config.yml` change (`.xv/config.yml:57-58`) was made by the watch as Sean directed, at the `maker_stopped` stop (record `stops`, answered 18:52).

## 4. The picture

`.xv/picture.md:23` becomes incomplete. Proposed additions, in words:

- At close, `run.close` writes `modules_touched` (from `boundary.change` against the slice's base) and `maker_sendbacks` into the record (`scripts/run.py:1161-1165`).
- A person's send-back answer keeps `sent_back_to: <step>` (`scripts/record.py:389`).
- `retro.reworked` finds the modules that at least `limits.rework_slices` closed, sent-back slices since the last retro touched (`scripts/retro.py:91-99`). Both `due` and the retro prompt use it. `retro.accept` treats `kind: refactor` as a candidate that only prints the `xv slice new --kind refactor` step (`scripts/retro.py:247-250`).

## 5. The wall

- `tests/test_retro.py` `ReworkSignalTest.test_the_default_limit_is_three_in_the_repo_and_in_the_defaults`: **mark slice-only.** Line 187-188 pins this repo's own tunable value in `.xv/config.yml`, which was a one-time edit. The runtime default is guarded by `test_without_the_key_the_limit_is_three` (line 190). This repeats the first pass's recommendation, which the record holds with `accepted: false`.

## Scenario misses


## Door

Two-way door: a revert removes the code, and the new record fields are additive. Blast radius: small.

## Raw data

- Diff: `git diff 5d5e75fc7a73..HEAD -- scripts defaults .xv/config.yml CHANGELOG.md skills tests`
- Boundary: `.xv/slices/2026-11-05-rework-signal.boundary.md`
- Wall: `xv wall diff 2026-11-05-rework-signal`, baseline `.xv/slices/2026-11-05-rework-signal.wall.json`
- First guardian pass: record `checks.guardian.misses` (points 1 and 4, both since fixed and tested at `tests/test_retro.py:250` and `:265`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- `xv wall diff`: `changed: []`, `deleted: []`, `fewer_assertions: []`. No old wall test changed.
- Point 1** ("`maker_sendbacks`, how many times the slice went back to the maker"). to: scenario.
- Where it fails: `scripts/run.py:1163-1165` counts only stops where `answer == "sent back to the maker"` or `sent_back_to == "maker"`.
- The scenario-agent path: when a guardian miss goes `to: scenario`, the watch writes `"sent back to the scenario"` (`scripts/record.py:565`), and the maker then reworks the slice. That rework is not counted. The same holds for a person's answer at the guardian or cleaner with `--next scenario`.
- The maker path: a person's `--next maker` at a scenario stop is not a send-back (`scripts/record.py:381-382`, where `next` comes later in `STEPS`).
- Evidence: this slice's own record (`.xv/slices/2026-11-05-rework-signal.md:24`, `stops`: `scenario_miss` answered "sent back to the scenario" at 19:11, then the maker ran again at 22:16). The `maker_stopped` stop at 18:49 also sent the slice to the scenario, before `sent_back_to` existed. Both rounds of rework would close with `maker_sendbacks: 0`.
- The red covers only a direct send-back to the maker (`tests/test_retro.py:237` and `tests/test_retro.py:250`).
- This is a judgment call on what "went back to the maker" means (`.xv/slices/2026-11-05-rework-signal.md:40`). If it means only a direct send-back to the maker, the scenario should say so.

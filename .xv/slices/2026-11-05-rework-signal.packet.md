---
slice: 2026-11-05-rework-signal
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A retro is due when the same code needs rework: #114

No shape or pitch stop. There are two scenario misses that the red does not cover, so the slice goes back to the scenario agent: (1) `xv retro run` asks for a refactor candidate on modules reworked *before* the last retro, so the request comes back at every later retro; (2) `maker_sendbacks` counts only the watch's own send-backs, not a person's answer that sends the slice back to the maker. Sean also decides on one wall recommendation (§5).

## The scenario

1. At close, a slice's record keeps `modules_touched` (what `xv boundary` lists) and `maker_sendbacks` (how many times the slice went back to the maker).
2. `xv retro due` gives a reason when at least `limits.rework_slices` closed slices since the last retro touched one module and each went back to the maker at least once. The reason names the module and the slices.
3. `limits.rework_slices` is in `.xv/config.yml` and `defaults/config.yml`. The default is 3; 0 turns it off.
4. For such a module, the retro proposes a candidate of kind `refactor`. `xv retro accept` on it prints `xv slice new --kind refactor` and opens no slice.
5. `CHANGELOG.md` has a line for the retro brief change.

May ignore: old slice records without the new fields, which count as never sent back.

## The recording

None (feature). To replay: `python3 -m unittest tests.test_retro.ReworkSignalTest` (run from `tests/`: `python3 -m unittest test_retro.ReworkSignalTest`). I ran it at HEAD `38c5fd1`: 15 tests, OK. The record says the whole suite was green at 807 after the cleaner.

## The boundary picture

From `.xv/slices/2026-11-05-rework-signal.boundary.md`, as given: touched `scripts/retro`, `scripts/run`, `scripts/xvlib`. No modules or edges added or removed, no outbound calls, no tables, no surface paths. Shape hints: none. `run → boundary` already existed (`.xv/picture.md:21`).

## What the suite asserts after

`ReworkSignalTest` (15 tests, `tests/test_retro.py:102-284`):
- `due` names the module and all three slices when three closed slices, each sent back, touched it.
- `due` gives no reason for a slice that was never sent back, for different modules, for a slice that is not closed, for slices from before the last retro, or for old records without the fields.
- Only the shared module is named.
- The limit: the default is 3 without the key, 2 is enough after `set_limit(2)`, and 0 turns it off. Both config files have `rework_slices: 3`.
- After a real `xv run` and `xv close` on the fixture, `modules_touched == ["pantry/store"]`. `maker_sendbacks` is 0, or 1 after a guardian `scenario_miss` send-back.
- The `retro.run` prompt names `pantry` and `kind: refactor`.
- `xv retro accept` on a `kind: refactor` candidate prints `xv slice new` and `--kind refactor`, and creates no branch and no slice file.

No old test changed: the diff of `tests/test_retro.py` against the base only adds lines.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast ("narrow"; record `forecast.shape`).
- The boundary picture has no edges, modules, tables or surfaces added. `run.close` calls `boundary.change` (`scripts/run.py:1161-1162`) over an edge already in the picture (`.xv/picture.md:21`, "`run` reaches … `boundary`"). Inside the current shape.
- Two new record fields (`scripts/run.py:1162-1163`) and one new config key (`defaults/config.yml:69-71`, `scripts/xvlib.py:230-231`). State is still files (`.xv/picture.md:27`), so no table is added. The defaults change reaches every new adopter (`.xv/picture.md:25`). That is within the shape, but it means adopters' retros get the new reason by default.
- A new candidate kind, `refactor`, in the retro brief (`skills/xv-retro/retro-brief.md:45`) and in `accept` (`scripts/retro.py:246-249`) reuses the slice kind that already exists (`.xv/picture.md:27`, "A refactor slice's scenario step…").

## 2. Pitch

pitch_contradiction: no. I checked it against `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." The change only adds a retro signal and prints a command a person runs; it serves the same users (`.xv/pitch.md:21`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_retro.py | `test_the_changelog_has_a_line_for_the_retro_brief_change`: an Unreleased line has `rework_slices` and `retro` | removed (49 → 48 assertions, `xv wall diff`) | cleaner: "checks one CHANGELOG line, which has no value once the line exists" | Not forced. It is a slice-only test written in this slice, marked and accepted by Sean at the `red_misses_scenario` stops. The CHANGELOG line it checked is present (`CHANGELOG.md:7`). |

Slice-only tests removed: `tests/test_retro.py` `ReworkSignalTest.test_the_changelog_has_a_line_for_the_retro_brief_change`. Kept: none.

No test that existed at the base changed. The two `["pantry"] → ["pantry/store"]` edits were to this slice's own red, made by the scenario agent as Sean settled at `maker_stopped`. `may_not_files`: none.

## 4. The picture

- `.xv/picture.md:23`, "`listen`, `retro`, `promote` and `prototypes` are the side loops." Proposed addition: "`run.close` writes `modules_touched` (from `boundary.change` against the slice's base) and `maker_sendbacks` (the watch send-backs to the maker) into the record. `retro.due` adds a reason per module when `limits.rework_slices` (default 3, 0 off) closed slices since the last retro, each sent back, touched it. `retro.run` then asks for a `kind: refactor` candidate, and `retro.accept` on one prints `xv slice new --kind refactor` and opens nothing."
- `.xv/picture.md:23`, "`boundary`, `packet` and `check` are the guardian's checks." This is now incomplete. Proposed: "…the guardian's checks; `close` also uses `boundary` for `modules_touched`."

## 5. The wall

- `tests/test_retro.py:186` `ReworkSignalTest.test_the_default_limit_is_three_in_the_repo_and_in_the_defaults`: mark it slice-only. Line 188 regex-matches `rework_slices: 3` in this repo's own `.xv/config.yml`. That is a value the repo is free to tune (`.xv/config.yml:57-58`), so the test guards the one-time edit the watch made "as Sean directed" (commit `2558e7e`), like the removed CHANGELOG test. The runtime default is already guarded by `test_without_the_key_the_limit_is_three` (`tests/test_retro.py:190`) through `DEFAULT_CONFIG` (`scripts/xvlib.py:230-231`).

## Scenario misses

- 4: `retro.run` passes every record to `reworked`, not only the ones since the last retro (`scripts/retro.py:178`: `reworked([d for d, _ in recs.values()], root)`, where `recs` at `scripts/retro.py:155` is all of `records(root)`; compare `due` at `scripts/retro.py:56`, which filters on `since`). A module that met the limit once is named in every later retro prompt with "propose a candidate with `kind: refactor`", even after a retro has dealt with it. It also lists slices that are not "such a module" under point 2's "since the last retro". The red's prompt test (`tests/test_retro.py:251`) has no earlier retro. (evidence: diff hunk `scripts/retro.py:177-178`; to: scenario)
- 1: `maker_sendbacks` counts only stops whose `answer` is the literal `"sent back to the maker"` (`scripts/run.py:1163`). Only the watch's own `send_back` writes that (`scripts/record.py:564`). A person's answer with `--next maker` sets `sent_back: true` but keeps their own answer text, and it records no target (`scripts/record.py:386-388`). So a slice a person sent back to the maker closes with `maker_sendbacks: 0`, against "how many times the slice went back to the maker". The red covers only the watch's path (`tests/test_retro.py:237-247`). (evidence: diff hunk `scripts/run.py:1163`; to: scenario)

## Door

**Door:** two-way. Reverting removes the code. Records closed in the meantime keep two extra fields, which nothing else reads. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-05-rework-signal.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..38c5fd1`
- Wall: `xv wall diff 2026-11-05-rework-signal` (tests/test_retro.py 49 → 48 assertions, recorded)
- Boundary: `.xv/slices/2026-11-05-rework-signal.boundary.md`

---
slice: 2026-11-04-retro-sighting
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: Retro accept adds a sighting to an Open learning, and writes no empty field

This is the third pass. There is no shape stop, no pitch stop and no scenario miss. Both of Sean's amendments are met. Point 6 now has a test, and point 7 is fixed and tested. One thing is left for the person: `promote`'s local accept still writes an empty `- miss:` or `- seen:` when the Open entry has none. Point 7 names only `from:`, so this is not a miss (see "Scenario misses").

## The scenario

1. A candidate with `sighting of: <Open title>` adds the repo and date to that entry's `seen:` and the candidate's slices to its `from:`. It writes no new entry.
2. The retro brief and `skills/xv-retro/SKILL.md` tell the retro to use `sighting of:`.
3. `xv retro accept` writes a standard or rule with no empty `from:` or `miss:`.
4. The field readers in `check.py` and `promote.py` do not take the next line as an empty field's value, so `xv check` flags a standard or rule that names no slice.
5. (Amendment) An unknown `sighting of:` title is refused with an error that names it, and nothing is written.
6. (Amendment) A sighting on an Open entry with no `from:` line adds a `from:` line with the candidate's slices, and a test shows it.
7. (Amendment) `xv promote local`, accepting an Open entry with no `from:`, writes no empty `from:` line.

May ignore: matching a candidate to an Open entry on its own, sightings of learnings already promoted, and old entries that already have an empty field.

## The recording

None (feature). To replay: `cd tests && python3 -m unittest test_retro_accept_fields test_retro_accept_brief_shape test_check`. I ran it on HEAD b301db6: 29 tests, OK. The scenario step recorded point 7 red before this pass's maker ran. The maker and the cleaner recorded the whole suite green (871 tests). I did not rerun the whole suite.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-retro-sighting.boundary.md`): the slice touches `scripts/check`, `scripts/promote` and `scripts/retro`. It adds or removes no module, edge, outbound call, table or surface path. Shape hints: none.

## What the suite asserts after

- A sighting of a known Open title leaves one entry. It adds the new repo@date to the end of `seen:`. It joins the candidate's slices to the existing `from:` with `; `, so there is still one `from:` line. `miss:`, `rule:` and the next section are unchanged.
- A sighting on an Open entry with no `from:` line writes `- from: s2, ...; s3, ...`. The file still has one entry, and `seen:` grows (`tests/test_retro_accept_fields.py:111-118`, new this pass).
- An unknown title raises `XVError` naming the title, and the file is unchanged, byte for byte.
- A bare standard or rule candidate is written with no `- from:` line and no `- miss:` line, and it keeps `- seen: [`.
- In `check.entries`, an empty `- from:` reads as `""`, not as the next line, and the entry gets the note "no slice".
- `promote`'s local accept does not take the next line for an empty `from:`. For an Open entry with no `from:`, it writes no `- from:` line and keeps the `- miss:` (`tests/test_retro_accept_brief_shape.py:72-76`, new this pass).
- Both retro skill files contain `` `sighting of:` ``.
- No old assertion moved.

## 1. Shape

shape_change: no.
- The boundary picture lists no added or removed modules, edges, tables or surfaces, and gives no shape hints (`.xv/slices/2026-11-04-retro-sighting.boundary.md`: "Shape hints: none", "Edges: added: none").
- `sighting of:` is a new field in a format that already exists, the retro packet (`skills/xv-retro/retro-brief.md:50`, `+- sighting of: <for open: ...>`). It sits on a surface the picture already names, "`skills/*/SKILL.md`" (`.xv/picture.md:27`). The change stays inside the current shape.
- This pass changes only `scripts/promote.py:240-241` (`from_line`) and two tests. Neither changes the shape.
- `shape_breadth: narrow`. The change is three modules on existing edges (boundary picture, "touched: scripts/check, scripts/promote, scripts/retro"), plus two skill files and one CHANGELOG line. The forecast expected `wide` and named these same places (`.xv/slices/2026-11-04-retro-sighting.md:11`, `breadth`: "retro accept ..., the field reader in scripts/check.py and scripts/promote.py, and the retro brief and skills/xv-retro/SKILL.md"), so the change is not wider than the forecast.

## 2. Pitch

pitch_contradiction: no.
- I checked the change against `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code." The change does nothing for that group.
- It serves `.xv/pitch.md:17`, which says that without xv-agents, "sharing learnings between teams would be high friction". A sighting now joins the existing learning instead of making a second entry.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-04-retro-sighting` shows nothing changed, deleted, added or with fewer assertions. The record has `moved_tests: []`. In `git diff 1177656..HEAD -- tests`, both test files only gain lines (+6, +9).

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- Nothing in `.xv/picture.md` becomes untrue. It says only that "`listen`, `retro`, `promote` and `prototypes` are the side loops" (`.xv/picture.md:23`). It does not describe what accept writes.
- Binding decision 1 (`.xv/picture.md:63`) is met. `CHANGELOG.md:7` has the Unreleased line, naming #108 and #49, "Decided by Sean, solo." The repo runs solo (`.xv/picture.md:55`). The CHANGELOG line does not mention point 7 (promote's `from:`), but point 7 changes no brief, may-not list, standing order or check, so decision 1 does not require it.
- Binding decision 4 (`.xv/picture.md:66`, "No count of sightings triggers a pull request") still holds. A sighting only makes `seen:` longer. I propose no edit.

## 5. The wall

No wall recommendations. Each new test guards behaviour that should last, and each comes from a scenario point: `test_check.py` (point 4), the three new tests in `test_retro_accept_brief_shape.py` (points 2, 4 and 7), and `test_standard_and_rule_leave_out_an_empty_from_and_miss` plus the six tests in `RetroAcceptSightingTest` (points 1, 3, 5 and 6). None restates another test, none is marked slice-only, and the scenario makes no old wall test dead.

The second-pass gap is closed. The `- added:` branch of the no-`from:` fix (`scripts/retro.py:200-201`) is now covered by `test_a_sighting_on_an_entry_with_no_from_line_adds_one_with_the_candidates_slices`. The last fallback, which inserts after the `###` heading when there is no `- added:` line (`scripts/retro.py:202-203`), still has no test. Every Open entry that `accept` writes has `- added:` (`scripts/retro.py:241`), so only a hand-written entry reaches that branch.

## Scenario misses

None. I checked each of points 1 to 7 against the diff and the passing red. Point 6: the test at `tests/test_retro_accept_fields.py:111` passes. Point 7: the diff hunk `scripts/promote.py:240-241` writes `from_line` only when `fields.get("from")` is set, and the test at `tests/test_retro_accept_brief_shape.py:72` passes.

Not a miss, for the person to weigh. `promote`'s local accept still writes `- miss: {fields.get('miss', fields.get('said', ''))}` and `- seen: {fields.get('seen', '')}` unconditionally (`scripts/promote.py:242`). An Open entry with no `miss:`/`said:` or no `seen:` is promoted with an empty `- miss: ` or `- seen: ` line. That is the same kind of field that point 3 removed from `xv retro accept`. Point 7 names only `from:`, and `check.py` now reads an empty field as `""` (`scripts/check.py:159`), so nothing is hidden. One more detail: when an entry has an empty `- miss:` line and a filled `- said:`, the empty `miss` now wins over `said`, because `fields.get('miss', ...)` returns `""` instead of falling back. Before, the reader took the next line as the value. `accept` never writes an empty `miss:` for Open (`scripts/retro.py:244`, `if c.get("miss")`), so only a hand-written entry can do this.

## Door

**Door:** two-way. A revert undoes the code. Entries already written to `.xv/learnings.md` stay as written; they are plain text that a person commits. `grep` finds no empty `from:`, `miss:`, `seen:` or `said:` line in `.xv/learnings.md`, `.xv/standards.md`, `.xv/rules.md` or `defaults/*.md`, so the reader change flags no existing entry. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-04-retro-sighting.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..b301db6`; this pass only: `git diff 1177656..b301db6`
- Wall: `xv wall diff 2026-11-04-retro-sighting`
- Boundary: `.xv/slices/2026-11-04-retro-sighting.boundary.md`
- Decision for amendments 6 and 7: `.xv/decisions/2026-11-04-2026-11-04-retro-sighting.md`
- Earlier packets: commits 6644ed9 (first pass) and 1177656 (second pass)

## From the cleaner

- Shape proposal, for people: scripts/retro.py add_sighting: the three-step 'from' insertion (empty line, after added, after heading) could become one small field-setter shared with accept's entry building; it is a new concept, so left for the packet.

---
slice: 2026-11-04-promote-fields
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: no
shape_breadth: narrow
moved_tests: 2
door: two-way
blast_radius: small
---

# Packet: Promotion copies only the fields that have text

No stop for two people. Sean Kennedy decides two things in `accept_moves`: the two moved tests (the record lists them as four moves), and one wall recommendation, which is to retire a moved test whose name now says the opposite of what it checks. The merge is the originator's.

## The scenario

1. `xv promote local --accept` copies every field that has text into the standard or rule and leaves out every empty one. No field is filled from another field. `rule:` becomes the heading, and `added:` gets today's date and the promoter's name.
2. When a sighting lands on an Open entry that has no `from:` and no `added:` line, its `from:` goes right after the `###` heading. A test shows this.

May ignore: standards and rules already written, the two Open entries that have `said:` but no `miss:`, and sharing an entry with no `miss:`, which `xv promote` keeps skipping.

## The recording

None: this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_promote`. Before the change it fails 5 of 16 tests, with `'- miss:' unexpectedly found in '- added: 2026-11-04 by Pat\n- from: …\n- miss: \n- seen: […]'` (record, `red`). After the change, `test_promote` and `test_retro_accept_brief_shape` give 25 tests, OK (my run). The whole suite gave 950 tests, OK, after the cleaner's edit (record, `checks.cleaner.suite`).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-promote-fields.boundary.md`): only `scripts/promote` is touched. No modules, edges, tables, surfaces or outbound calls are added or removed. Shape hints: none.

## What the suite asserts after

- `tests/test_promote.py`, `PromoteFieldsTest` (9 tests, new). For both standards and rules: an empty `miss:` is left out and `said:` is kept. A missing `miss:` stays missing. A `miss:` with text sits beside `said:`. Every empty field is left out, `from:` and `said:` included. Other fields with text, such as `shared:`, are copied. `rule:` is the heading and not a field. `added:` appears once and holds today and the promoter. `from:` and `seen:` are copied.
- `tests/test_promote.py`, `SightingFromPlacementTest` (1 test, new): this is scenario point 2. It passed before the change too (scenario report).
- Moved: two tests in `tests/test_retro_accept_brief_shape.py` now expect `said:` to be kept, and `miss:` no longer filled from it (see 3).

## 1. Shape

shape_change: no. shape_breadth: narrow. This matches the forecast's `narrow`, and the forecast's "breadth" sentence holds.
- The boundary picture has no new module, edge, table or surface, and no shape hints. Its edges for `scripts/promote` (→ `check`, → `xvlib`) are the ones `.xv/picture.md:21-23` describes.
- The only code change is inside `local_accept` (`scripts/promote.py:238-245`): `pairs = re.findall(...)`, `others = "".join(... if v.strip() and k not in ("rule", "added", "from", "seen"))`, `entry = f"\n### {rule}\n- added: {today()} by {by}\n{from_line}{others}{seen_line}"`. This is inside the current shape.
- One knock-on effect stays inside the shape. A `shared:` line on the learning is now copied into the standard or rule (`test_other_fields_with_text_are_copied`, `tests/test_promote.py:118`). `candidates` reads `^- (shared|adopts):` in standards and rules (`scripts/promote.py:106`), so a promoted entry whose learning was already shared now lists as `linked`. Before the change it did not.

## 2. Pitch

pitch_contradiction: no. I checked the change against "makes it easy for a team or an individual to adopt Xtreme Vibing… to vibe with discipline" (`.xv/pitch.md:7`) and against "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). It keeps the person's quoted words in a promoted rule, and touches nothing the pitch excludes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_retro_accept_brief_shape.py:58` `test_promote_local_prefers_the_entry_miss_over_said` | `assertNotIn("the words", text)` | `assertIn('- said: "the words"\n', text)` | "The scenario keeps said: beside miss: instead of dropping it." | Yes. Scenario point 1 says "copies every field that has text". |
| `tests/test_retro_accept_brief_shape.py:63` `test_promote_local_falls_back_to_said_when_the_entry_has_no_miss` | `assertIn('- miss: "the words"\n', text)` | `assertIn('- said: "the words"\n', text)` and `assertNotIn("- miss:", text.split("### do the thing")[1])` | "No field is filled from another… scoped to the promoted entry because the file holds other entries with miss:." | Yes. Scenario point 1 says "No field is filled from another field." |

Neither moved test asserts less: `xv wall diff` shows 18 assertions before and 19 after, and lists no file under `fewer_assertions`. Every change has a record; `unrecorded` is empty.

- **The record holds four moves for two changes.** The record's `moved_tests` has one entry at 04:27:11 for the first test, and three entries for the second test, at 04:27:11, 04:35:01 and 04:42:48. Each of the three has slightly different `assertion` text. The picture says "One move is recorded once" and "`accept_moves` counts moves by file and assertion" (`.xv/picture.md:23`). So the person will see four moves where the diff has two, and only the 04:42:48 wording matches the final hunk.
- **The test names are now wrong.** Both moved tests kept their names, and the names now say the opposite of what the tests assert. "prefers the entry miss over said" (`:58`) now checks that both fields are kept. "falls back to said when the entry has no miss" (`:63`) now checks that there is no fallback.

Slice-only tests removed: none. Kept: none (the record's `slice_only` is empty).
May-not files the scenario agent allowed: none (`may_not_files: []`).

## 4. The picture

No change proposed. I read `.xv/picture.md:23`, which says "`listen`, `retro`, `promote` and `prototypes` are the side loops", along with the shape and Names sections and binding decisions 1–15. None of them describes which fields promotion writes. `skills/xv-promote/SKILL.md:22` says "keeps its slices and sightings", and that is still true. No brief, may-not list, standing order or agent check changed, so decision 1 (`.xv/picture.md:63`) is not touched.

## 5. The wall

- `tests/test_retro_accept_brief_shape.py` `test_promote_local_falls_back_to_said_when_the_entry_has_no_miss`: **remove from the wall.** The scenario ends the behaviour the name describes ("No field is filled from another field"). After the move (hunk at `:63-66`), its assertions repeat `test_no_field_is_filled_from_another` (`tests/test_promote.py:92-95`) and `test_an_empty_miss_is_left_out_and_said_is_kept` (`tests/test_promote.py:85-90`).

I looked at the 10 new tests in `tests/test_promote.py`, and none is marked slice-only. Each one guards lasting behaviour that scenario point 1 or 2 names, so I leave them as they are.

## Door

**Door:** two-way. Reverting `scripts/promote.py:238-245` restores the old output. Standards and rules already promoted are not rewritten. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-04-promote-fields.md`
- Diff: `git diff 168693608141b7cca549d5e56eebd4a61e9bd3fb..e7a4ea4`
- Wall: `xv wall diff 2026-11-04-promote-fields`
- Boundary: `xv boundary --base 168693608141b7cca549d5e56eebd4a61e9bd3fb` (`.xv/slices/2026-11-04-promote-fields.boundary.md`)

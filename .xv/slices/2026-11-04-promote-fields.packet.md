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

This is the second guardian pass, after the cleaner renamed tests. Nothing stops for two people. Sean Kennedy has one thing to decide in `accept_moves`. The wall retirement he accepted at 05:12 names `test_promote_local_falls_back_to_said_when_the_entry_has_no_miss`. The cleaner then renamed that test, so the name no longer exists. The test is still in the file under a new name (see 3 and 5). The merge is the originator's.

## The scenario

1. `xv promote local` turns an Open entry into a standard or a rule. It copies every field that has text and leaves out every empty one. No field is filled from another field. `rule:` becomes the heading, and `added:` gets today's date and the promoter's name.
2. A sighting can land on an Open entry that has no `from:` line and no `added:` line. Its `from:` goes right after the `###` heading. A test shows this.

May ignore: standards and rules already written, the two Open entries that have `said:` but no `miss:`, and sharing an entry with no `miss:`, which `xv promote` keeps skipping.

## The recording

None, because this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_promote`. At the red commit `b13c4d2`, 5 of 16 tests failed with `'- miss:' unexpectedly found in '- added: 2026-11-04 by Pat\n- from: …\n- miss: \n- seen: […]'` (record, `red`). At HEAD `2575a84`, I ran `python3 -m unittest test_promote test_retro_accept_brief_shape`: 25 tests, OK. The whole suite passed after the cleaner's second pass: 950 tests, OK (record, `checks.cleaner.suite`).

## The boundary picture

From `.xv/slices/2026-11-04-promote-fields.boundary.md`, as given:
- Touched: `scripts/promote`.
- Modules, edges, tables, surfaces and outbound calls: none added and none removed.
- Shape hints: none.

## What the suite asserts after

- **New, `tests/test_promote.py` `PromoteFieldsTest`** (`:77-138`, 9 tests). For both standards and rules:
  - An empty `miss:` is left out and `said:` is kept.
  - A missing `miss:` stays missing.
  - A `miss:` with text sits beside `said:`.
  - Every empty field is left out, `from:` and `said:` included.
  - Other fields with text, such as `shared:`, are copied.
  - `rule:` is the heading, not a field.
  - `added:` appears once and holds today's date and the promoter.
  - `from:` and `seen:` are copied.
- **New, `SightingFromPlacementTest`** (`:140`). This is scenario point 2. It passed before the change too (scenario report).
- **Moved, `tests/test_retro_accept_brief_shape.py:58` and `:63`.** Both now expect `said:` to be kept, and `miss:` no longer filled from it. Both have been renamed to match (see 3).

## 1. Shape

shape_change: no. shape_breadth: narrow. This matches the forecast's `narrow`, and its breadth sentence holds: "Changes the field copy in promote.py local_accept … no other command or file expected to move."
- The boundary picture adds no module, edge, table or surface, and gives no shape hints. `scripts/promote` still reaches only `check` and `xvlib`, which fits `.xv/picture.md:21`.
- All the code is in one hunk, `scripts/promote.py:238-245`, inside `local_accept`:

  ```
  others = "".join(f"- {k}: {v}\n" for k, v in pairs
                   if v.strip() and k not in ("rule", "added", "from", "seen"))
  ```

  This is inside the current shape.
- Knock-on effect, inside the shape: a `shared:` line on a learning is now copied into the standard or rule (`tests/test_promote.py:118`). `candidates` reads `^- (shared|adopts):` (`scripts/promote.py:106`), so such an entry now lists as `linked`.
- Knock-on effect, inside the shape: a learning with only `said:` used to get `miss:` filled from it. Now it has no `miss:`, so `candidates` skips it for sharing (`scripts/promote.py:107`, `not e["miss"] and e["file"] != "learnings.md"`). The scenario's may-ignore covers this: "Sharing an entry with no miss: … xv promote keeps skipping it."

## 2. Pitch

pitch_contradiction: no. I checked the change against two lines of the pitch:
- "makes it easy for a team or an individual to adopt Xtreme Vibing … to vibe with discipline" (`.xv/pitch.md:7`)
- "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`)

The change keeps a person's quoted `said:` words in a promoted rule. It serves no one the pitch excludes.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_retro_accept_brief_shape.py:58`, was `test_promote_local_prefers_the_entry_miss_over_said`, now `test_promote_local_keeps_both_miss_and_said` | `assertNotIn("the words", text)` | `assertIn('- said: "the words"\n', text)` | maker: "The scenario keeps said: beside miss: instead of dropping it". cleaner: "The name said miss wins over said" | Yes. Point 1: "copies every field that has text". |
| `tests/test_retro_accept_brief_shape.py:63`, was `test_promote_local_falls_back_to_said_when_the_entry_has_no_miss`, now `test_promote_local_copies_said_and_does_not_fill_miss_from_it` | `assertIn('- miss: "the words"\n', text)` | `assertIn('- said: "the words"\n', text)` and `assertNotIn("- miss:", text.split("### do the thing")[1])` | maker: "no field is filled from another … scoped to the promoted entry". cleaner: "The name described the said-to-miss fallback the slice ended." | Yes. Point 1: "No field is filled from another field." |

Neither test asserts less. `xv wall diff` shows 18 assertions before and 19 after, with nothing under `fewer_assertions`. Every change has a record.

- **The cleaner renamed a test that was not in the answer.** The settled answer at 05:12:42 says: "The cleaner renames test_promote_local_prefers_the_entry_miss_over_said … Next is cleaner." The cleaner also renamed the `:63` test (hunk `-def test_promote_local_falls_back_to_said_when_the_entry_has_no_miss` / `+def test_promote_local_copies_said_and_does_not_fill_miss_from_it`). In the same answer, Sean accepted retiring that test from the wall (`accepted_wall: ["test_promote_local_falls_back_to_said_when_the_entry_has_no_miss"]`). The accepted name now matches no test, and the test stays in the file under its new name.
- **The record holds six moves for two changed tests**, against "One move is recorded once" (`.xv/picture.md:23`). The `:58` test (`tests/test_retro_accept_brief_shape.py:58`) has two moves: the maker at 04:27:11 and the cleaner's rename at 05:12:58. The `:63` test (`tests/test_retro_accept_brief_shape.py:63`) has four: the maker at 04:27:11, 04:35:01 and 04:42:48, and the cleaner's rename at 05:12:58. The maker's three differ only in the wording of the `assertion`. `accept_moves` counts moves by file and assertion (`.xv/picture.md:23`), so a person will see six moves where the diff has two.

Slice-only tests removed: none. Kept: none (`slice_only: []`).
May-not files the scenario agent allowed: none (`may_not_files: []`).

## 4. The picture

No change proposed. I read the shape section (`.xv/picture.md:21-26`), Names (`:33`), and binding decisions 1–15 (`:63-77`).
- `.xv/picture.md:23` lists `promote` only as a side loop. It does not describe which fields promotion writes, so nothing there becomes untrue.
- No brief, may-not list, standing order or agent check changed, so decision 1 (`.xv/picture.md:63`) is not touched.
- The change posts nothing in public, so decision 5 (`.xv/picture.md:67`) is not touched.

## 5. The wall

- **`tests/test_retro_accept_brief_shape.py` `test_promote_local_copies_said_and_does_not_fill_miss_from_it`: remove from the wall.** This is the test Sean already agreed to retire under its old name (`accepted_wall`, stop at 05:07:59). The cleaner's rename at `:63` left that acceptance naming a test that no longer exists, so the recommendation needs the new name. The reason is unchanged. After the move (hunk `:63-66`), its two assertions repeat `test_no_field_is_filled_from_another` (`tests/test_promote.py:92-95`) and `test_an_empty_miss_is_left_out_and_said_is_kept` (`tests/test_promote.py:85-90`).

I also looked at the 10 new tests in `tests/test_promote.py`. None is marked slice-only, and each guards lasting behaviour that scenario point 1 or 2 names, so I leave them as they are.

## Door

**Door:** two-way. Reverting `scripts/promote.py:238-245` restores the old output. The slice does not rewrite standards or rules that were already promoted. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-04-promote-fields.md`
- Diff: `git diff 168693608141b7cca549d5e56eebd4a61e9bd3fb..2575a84`
- Wall: `xv wall diff 2026-11-04-promote-fields`
- Boundary: `xv boundary --base 168693608141b7cca549d5e56eebd4a61e9bd3fb` (`.xv/slices/2026-11-04-promote-fields.boundary.md`)

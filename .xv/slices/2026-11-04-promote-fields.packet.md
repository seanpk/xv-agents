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

This is the third guardian pass. It follows the cleaner's deletion of the retired test. Nothing stops for two people, and there is no scenario miss. Sean Kennedy has two things to look at in `accept_moves`. First, `xv wall diff` flags `tests/test_retro_accept_brief_shape.py` as asserting less (18 to 17). That comes from the deletion Sean asked for on 05:33, and the deleted checks live on in `tests/test_promote.py` (see 3). Second, there is one edge case in the new field copy (see "For the person" under 1). The merge is the originator's.

## The scenario

1. `xv promote local` turns an Open entry into a standard or a rule. It copies every field that has text and leaves out every empty one. No field is filled from another field. `rule:` becomes the heading, and `added:` gets today's date and the promoter's name.
2. A sighting can land on an Open entry that has no `from:` line and no `added:` line. Its `from:` goes right after the `###` heading. A test shows this.

May ignore: standards and rules already written, the two Open entries that have `said:` but no `miss:`, and sharing an entry with no `miss:`.

## The recording

None, because this is a feature. To replay, run `cd tests && python3 -m unittest test_promote`. At the red commit `b13c4d2`, 5 of 16 tests failed (record, `red`). At HEAD `c28ec83`, I ran `python3 -m unittest test_promote test_retro_accept_brief_shape`: 24 tests, OK. The whole suite passed after the cleaner's last pass: 949 tests, OK (record, `checks.cleaner.suite`).

## The boundary picture

From `.xv/slices/2026-11-04-promote-fields.boundary.md`, as given. Touched: `scripts/promote`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none.

## What the suite asserts after

- When an entry's `miss:` is empty, the promoted standard or rule has no `- miss:` line, and it keeps `said:` word for word (`tests/test_promote.py:85`).
- When the entry has no `miss:`, promotion writes none: `said:` does not fill it (`:92`).
- A `miss:` with text is copied beside `said:` (`:97`, and the older `tests/test_retro_accept_brief_shape.py:58`).
- Every empty field is left out (`:104`, `:111`), and every other field with text is copied (`:118`).
- `rule:` becomes the heading and is not copied as a field (`:123`). `added:` appears once, with today's date and the promoter's name (`:127`). `from:` and `seen:` are copied (`:134`).
- A sighting on an entry with no `from:` and no `added:` puts `from:` right after the heading, and there is only one `from:` (`:141`).

## 1. Shape

shape_change: no. shape_breadth: narrow. This matches the forecast's `narrow`.

- The boundary picture shows `scripts/promote` touched, with no new edges, tables or surfaces, and no shape hints. The picture already names `promote` as a side loop (`.xv/picture.md:23`: "`listen`, `retro`, `promote` and `prototypes` are the side loops"). The diff stays inside `local_accept` (`scripts/promote.py:238-245`). It changes how the entry text is built and calls nothing new.
- The forecast's breadth sentence holds: "Changes the field copy in promote.py local_accept … plus tests; no other command or file expected to move." Point 2 needed no code change, only a test (`tests/test_promote.py:140-156`).

**For the person (not a stop):** at `scripts/promote.py:241-247`, `others` copies every field with text except `rule`, `added`, `from` and `seen`, and the code then appends `- check: none: judgement` for standards:

```
+    others = "".join(f"- {k}: {v}\n" for k, v in pairs
+                     if v.strip() and k not in ("rule", "added", "from", "seen"))
     ...
     if to == "standards":
         entry += "- check: none: judgement\n"
```

So if an Open entry already has a `- check:` line with text, the promoted standard gets two `check:` lines. This follows the scenario as written ("copies every field that has text"), and no test covers it. It is not a scenario miss.

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code. It will never be a teapot." The change only alters which lines a local promotion writes to `.xv/rules.md` or `.xv/standards.md`. It serves no new user and breaks no promise in the pitch.

## 3. Moved tests

The only changed wall file is `tests/test_retro_accept_brief_shape.py`. `xv wall diff` shows 18 assertions before and 17 after, and lists the file under `fewer_assertions`. The record has seven moves, which come to two net changes:

- **`test_promote_local_prefers_the_entry_miss_over_said`, now `test_promote_local_keeps_both_miss_and_said`** (`:58`). Before: `assertIn("- miss: what went wrong\n")` and `assertNotIn("the words")`. After: the same `miss` check, plus `assertIn('- said: "the words"\n')`. The maker's reason: the scenario keeps `said:` beside `miss:`. Scenario point 1 forces it ("copies every field that has text"). It does not assert less. The cleaner renamed it, which Sean asked for at the 05:12 stop. It now asserts the same thing as the new `tests/test_promote.py:97` `test_a_miss_with_text_is_copied_beside_said`. Sean kept it at the 05:12 stop, so I make no recommendation.
- **`test_promote_local_falls_back_to_said_when_the_entry_has_no_miss`, deleted** (after it was renamed to `test_promote_local_copies_said_and_does_not_fill_miss_from_it`). Before: `assertIn('- miss: "the words"\n')`. After: the test is gone. Scenario point 1 forces this ("No field is filled from another field"). This deletion is where the file asserts less. The record (05:34:11) and Sean's answer at 05:33 cover it. Its checks after the move (said kept, no miss) live in `tests/test_promote.py:92` and `:85`. Nothing in this file is lost without a record.

The record's moves at 04:27:11, 04:35:01 and 04:42:48 are intermediate states of that same deleted test. No move lacks a record (`unrecorded: []`).

Slice-only: none listed (`slice_only: []`). May-not files allowed by the scenario agent: none (`may_not_files: []`).

## 4. The picture

picture_change: no. I looked at `.xv/picture.md:23`, which names `promote` as a side loop, and at `.xv/picture.md:66`, which is decision 4, on learnings as issues. The change makes neither untrue, and the picture does not describe which fields promotion copies.

For the person, outside the picture: the standards template at `.xv/standards.md:13` shows `- miss: <what went wrong without it>` and no `said:`. After this slice, a promoted standard can carry `said:` and no `miss:` (`tests/test_promote.py:85`). Whether to add `said:` to that template is for a person to decide. I do not write to `.xv/standards.md`.

## 5. The wall

No recommendations this pass. The recommendation from the last pass (retire `test_promote_local_copies_said_and_does_not_fill_miss_from_it`) was accepted (record `wall_recommendations`, `accepted: true`) and carried out by the cleaner's deletion. I found no new test in `tests/test_promote.py` that guards a one-time change or only restates another one, so none should be marked slice-only. `SightingFromPlacementTest` (`:140`) guards behaviour that point 2 asks to keep, so it belongs on the wall.

## Door

Two-way door: a revert of `scripts/promote.py` and the tests undoes the change. Entries promoted in the meantime are ordinary lines in git-tracked files. Blast radius: small.

## Raw data

- Diff: `git diff 168693608141b7cca549d5e56eebd4a61e9bd3fb..HEAD -- scripts tests`
- Boundary: `.xv/slices/2026-11-04-promote-fields.boundary.md`
- Wall: `xv wall diff 2026-11-04-promote-fields`; baseline `.xv/slices/2026-11-04-promote-fields.wall.json`
- Record: `.xv/slices/2026-11-04-promote-fields.md` (`moved_tests`, `stops`, `checks.cleaner`)

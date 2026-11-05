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

This is the second pass. No shape stop, no pitch stop, no scenario miss. The maker fixed both misses from the first pass. One thing needs the person's eye: the fix for an Open entry with no `from:` line (`scripts/retro.py:200-203`) has no test, so nothing on the wall guards it (see check 5).

## The scenario

1. A candidate with `sighting of: <Open title>` adds the repo and date to that entry's `seen:` and the candidate's slices to its `from:`, and writes no new entry.
2. The retro brief and `skills/xv-retro/SKILL.md` tell the retro to use `sighting of:`.
3. `xv retro accept` writes a standard or rule with no empty `from:` or `miss:`.
4. The field readers in `check.py` and `promote.py` do not take the next line as an empty field's value, so `xv check` flags a standard or rule that names no slice.
5. (Amendment) An unknown `sighting of:` title is refused with an error naming it, and nothing is written.

The slice may ignore: matching a candidate to an Open entry it was not told about, sightings of learnings already promoted, and old entries that already have an empty field.

## The recording

None (feature). To replay: `cd tests && python3 -m unittest test_retro_accept_fields test_check test_retro_accept_brief_shape`. It failed on `pre_maker_commit` 6b17c7e (9 failures, from the record). It passes on HEAD 193d507: I ran it, 27 tests OK. The maker and the cleaner both recorded the whole suite green after the second pass (869 tests). I did not rerun the whole suite.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-retro-sighting.boundary.md`): it touches `scripts/check`, `scripts/promote` and `scripts/retro`. It adds or removes no modules, edges, outbound calls, tables or surface paths. It gives no shape hints.

## What the suite asserts after

- A sighting of a known Open title leaves one entry in the file. It adds the new repo@date to the end of `seen:` and joins the candidate's slices to the existing `from:`, so there is still one `from:` line. `miss:`, `rule:` and the next section do not change.
- An unknown title raises `XVError` naming the title, and the file stays the same, byte for byte.
- A bare standard or rule candidate is written with no `- from:` line and no `- miss:` line. It keeps `- seen: [`.
- In `check.entries`, an empty `- from:` reads as `""`, not as the next line, and the entry gets the note "no slice".
- `promote`'s local accept does not take the next line as the value of an empty `from:`.
- Both retro skill files contain `` `sighting of:` ``.
- No old assertion moved.
- Not asserted: a sighting on an Open entry that has no `from:` line (see check 5).

## 1. Shape

shape_change: no.
- The boundary picture lists no added or removed modules, edges, tables or surfaces, and gives no shape hints (`.xv/slices/2026-11-04-retro-sighting.boundary.md`: "Shape hints: none", "Edges added: none").
- `sighting of:` is a new field in a format that already exists, the retro packet (`skills/xv-retro/retro-brief.md:50`, `+- sighting of: <for open: ...>`). It lives on a surface the picture already names, "`skills/*/SKILL.md`" (`.xv/picture.md:52`). That is a change inside the current shape.
- The second pass adds four lines inside `add_sighting` (`scripts/retro.py:200-203`) and one line to `CHANGELOG.md`. Neither changes the shape.
- `shape_breadth: narrow`: three modules on existing edges, plus two skill files. The forecast expected `wide` and listed these same places ("retro accept ..., the field reader in scripts/check.py and scripts/promote.py, and the retro brief and skills/xv-retro/SKILL.md"), so the change is not wider than forecast.

## 2. Pitch

pitch_contradiction: no.
- I checked the change against `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code." The change does nothing for that group.
- It serves `.xv/pitch.md:17`, which says that without xv-agents "sharing learnings between teams would be high friction". A sighting now joins the existing learning instead of making a second entry.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-04-retro-sighting` shows nothing changed, deleted or with fewer assertions. The record has `moved_tests: []`. In `git diff a6e023b..HEAD -- tests` the three red files only gain lines, and `git diff e962f1d..HEAD -- tests` is empty: the second pass touched no test.

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- Nothing in `.xv/picture.md` becomes untrue. It says only that "`listen`, `retro`, `promote` and `prototypes` are the side loops" (`.xv/picture.md:48`). It does not describe what accept writes.
- Binding decision 1 (`.xv/picture.md:88`) is now met. `CHANGELOG.md:7` adds the Unreleased line, naming #108 and #49 and saying "Decided by Sean, solo." The repo runs solo (`.xv/picture.md:80`, "`seats.two_people: solo`"), which is how the other Unreleased lines are decided too (`CHANGELOG.md:8`).
- Binding decision 4 (`.xv/picture.md:91`, "No count of sightings triggers a pull request") still holds. A sighting only makes `seen:` longer. I propose no edit.

## 5. The wall

No wall recommendations. Each new test (`tests/test_check.py`, `tests/test_retro_accept_brief_shape.py`, `tests/test_retro_accept_fields.py`: `test_standard_and_rule_leave_out_an_empty_from_and_miss` and the five tests in `RetroAcceptSightingTest`) guards behaviour the change should keep, from a scenario point. None restates another test, none is marked slice-only, and the scenario makes no old wall test dead.

For the person: the second pass's fix has no test. In `git diff e962f1d..HEAD -- scripts/retro.py`, lines 200-203 add the `- from:` line after `- added:` or, failing that, after the `###` header:

```
+            if not re.search(r"^- from:", new, re.M):
+                new = re.sub(r"^(- added:.*\n)", lambda x: x.group(1) + "- from: " + c["from"] + "\n", ...)
+            if not re.search(r"^- from:", new, re.M):
+                new = re.sub(r"^(###.*\n)", lambda x: x.group(1) + "- from: " + c["from"] + "\n", ...)
```

Reading it, it covers the first pass's miss: `accept` writes an Open entry with no `from:` when the candidate has none (`scripts/retro.py:242`, `if c.get("from"):`). But every sighting fixture has a `from:` line (`tests/test_retro_accept_fields.py:65`, `- from: s1, the stop`), and the red still runs 27 tests, as it did before the second pass. If this branch broke, the slices would be dropped again with no error and no test would fail. The new code meets point 1, so this is not a miss. Whether to add a test is the person's call.

## Scenario misses

None. I checked both misses from the first pass against HEAD. The point 1 miss (a sighting dropped its slices when the entry had no `from:` line) is fixed by the diff hunk `scripts/retro.py:200-203`, quoted in check 5. The decision 1 miss (no `CHANGELOG.md` line) is fixed by the diff hunk `CHANGELOG.md:7`. I checked each of points 1 to 5 against the diff and the passing red, and found no other line missed.

Not a miss, for the person to weigh. It is unchanged from the first pass: `promote`'s local accept still writes an empty `- from: {fields.get('from', '')}` (`scripts/promote.py:240`) when the Open entry it promotes has none. Point 3 names only `xv retro accept`. Since this slice, `xv check` reads that empty field as `""` and flags it, so nothing is hidden.

## Door

**Door:** two-way. A revert undoes the code. Entries already written to `.xv/learnings.md` stay as written; they are plain text that a person commits. `grep` finds no empty field in `.xv/learnings.md`, `.xv/standards.md`, `.xv/rules.md` or `defaults/*.md`, so the reader change flags no existing entry. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-04-retro-sighting.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..193d507`; second pass only: `git diff e962f1d..193d507`
- Wall: `xv wall diff 2026-11-04-retro-sighting`
- Boundary: `.xv/slices/2026-11-04-retro-sighting.boundary.md`
- First-pass packet: commit 6644ed9

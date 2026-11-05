---
slice: 2026-11-04-retro-sighting
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: Retro accept adds a sighting to an Open learning, and writes no empty field

There are no shape or pitch stops. Two misses send the slice back to the maker: a sighting silently drops the candidate's slices when the Open entry has no `from:` line (point 1), and the brief change has no `CHANGELOG.md` line (binding decision 1). Nothing else needs a decision; the merge is the originator's.

## The scenario

1. A candidate with `sighting of: <Open title>` adds the repo and date to that entry's `seen:` and the candidate's slices to its `from:`, and writes no new entry.
2. The retro brief and `skills/xv-retro/SKILL.md` tell the retro to use `sighting of:`.
3. `xv retro accept` writes a standard or rule with no empty `from:` or `miss:`.
4. The field readers in `check.py` and `promote.py` do not take the next line as an empty field's value, so `xv check` flags a standard or rule that names no slice.
5. (Amendment) An unknown `sighting of:` title is refused with an error naming it, and nothing is written.

The slice may ignore: matching a candidate to an Open entry without being told which one, sightings of learnings that were already promoted, and old entries that already have an empty field.

## The recording

None (feature). To replay: `cd tests && python3 -m unittest test_retro_accept_fields test_check test_retro_accept_brief_shape`. It failed on `pre_maker_commit` 6b17c7e (9 failures, from the record) and passes on HEAD e962f1d (27 tests OK, which I ran). The maker and the cleaner both recorded the whole suite green (869 tests).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-retro-sighting.boundary.md`): it touches `scripts/check`, `scripts/promote` and `scripts/retro`. It adds or removes no modules, no edges, no outbound calls, no tables and no surface paths. It gives no shape hints.

## What the suite asserts after

- For a sighting of a known Open title, the file still holds one entry. The new repo@date is added to the end of `seen:`. The candidate's slices are joined to the existing `from:`, so there is still one `from:` line. `miss:`, `rule:` and the next section are unchanged.
- An unknown title raises `XVError` naming the title, and the file is unchanged byte for byte.
- A bare standard or rule candidate is written with no `- from:` and no `- miss:` line, but keeps `- seen: [`.
- In `check.entries`, an empty `- from:` reads as `""` (not the next line), and the entry gets the note "no slice".
- `promote` local accept does not read the next line as an empty `from:`.
- Both retro skill files contain `` `sighting of:` ``.
- No old assertion moved.

## 1. Shape

shape_change: no.
- The boundary picture lists no added or removed modules, edges, tables or surfaces, and gives no shape hints (`.xv/slices/2026-11-04-retro-sighting.boundary.md`, "Shape hints: none", "Edges added: none").
- The new `sighting of:` field (`skills/xv-retro/retro-brief.md:50`, `+- sighting of: <for open: ...>`) is a new field in an existing file format, the retro packet. It sits on a surface the picture already names, "`skills/*/SKILL.md`" (`.xv/picture.md:27`). That is a change inside the current shape.
- `shape_breadth: narrow`: three modules, all on existing edges, plus two skill files. That matches the forecast's `breadth` list ("retro accept ..., the field reader in scripts/check.py and scripts/promote.py, and the retro brief and skills/xv-retro/SKILL.md"), so it is no wider than the forecast's `wide`.

## 2. Pitch

pitch_contradiction: no.
- I checked the change against `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code." The change does nothing for that group.
- It supports `.xv/pitch.md:17`: "sharing learnings between teams would be high friction".

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

In `git diff a6e023b..HEAD -- tests`, the three test files only gain lines. `xv wall diff` shows nothing changed, deleted or with fewer assertions, and the record has `moved_tests: []`.

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- Nothing in `.xv/picture.md` becomes untrue. `.xv/picture.md:23` says only that "`retro`, `promote` ... are the side loops", and does not describe what accept writes.
- Binding decision 4 (`.xv/picture.md:66`, "No count of sightings triggers a pull request") still holds. A sighting only lengthens `seen:`, and `check.py`'s "seen twice" note puts the promotion in front of a person (`scripts/check.py`, `entries`, unchanged). So I propose no edit to `.xv/picture.md:23` or `:66`.

## 5. The wall

No recommendations. I read every new test in the diff: `tests/test_check.py:46`, `tests/test_retro_accept_brief_shape.py:67,72`, `tests/test_retro_accept_fields.py:51` and the five tests in `RetroAcceptSightingTest`. Each guards lasting behaviour from a scenario point, and none restates another. None is marked slice-only, and the scenario makes no old wall test dead.

## Scenario misses

- 1: A sighting can lose the candidate's slices without any error. `add_sighting` replaces a filled `from:` (`scripts/retro.py:196`) or an empty one (`scripts/retro.py:199`, `re.sub(r"^- from:[ \t]*$", ...)`). When the Open entry has no `from:` line at all, neither pattern matches, so the candidate's `from` is dropped and nothing is raised. `accept` writes Open entries that way itself when a candidate has no `from` (`scripts/retro.py:238`, `if c.get("from"):`). This is the form point 3 calls "as it already does for Open entries". Such an entry then also stays flagged "no slice" by `xv check` even after a sighting has named slices. The red's fixture always has `- from: s1, the stop` (`tests/test_retro_accept_fields.py`, `SIGHTING_LEARNING`), so this case is untested. (evidence: diff hunk `scripts/retro.py:195-199`; to: maker)
- decision 1: `.xv/picture.md:63` says "A change to a brief ... needs two people and a line in `CHANGELOG.md`". The slice changes the retro brief (`skills/xv-retro/retro-brief.md:24` and `:50`, the new instruction and the new packet field) and `skills/xv-retro/SKILL.md:25`, but `CHANGELOG.md` is not in the diff, so Unreleased has no line. `.xv/rules.md` makes this the maker's job: "A change to a brief, a may-not list, a standing order, or a check gets a line in `CHANGELOG.md` under Unreleased, naming the issue and who decided". (evidence: `git diff a6e023b..HEAD --stat` lists no `CHANGELOG.md`; to: maker)

Not a miss, for the person to weigh: `promote`'s local accept still writes an empty field, `- from: {fields.get('from', '')}` (`scripts/promote.py:240`), when the Open entry it promotes has none. Point 3 names only `xv retro accept`. Since this slice, `xv check` reads that empty field as `""` and flags it, so nothing is hidden. It is the same untidy write that #49 reported.

## Door

**Door:** two-way. A revert undoes the code. Entries already written to `.xv/learnings.md` stay as written, and they are plain text a person commits. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-04-retro-sighting.md`
- Diff: `git diff a6e023bd0ffeed4f6ce45990c668742a8f758419..e962f1d`
- Wall: `xv wall diff 2026-11-04-retro-sighting`
- Boundary: `xv boundary --base a6e023bd0ffeed4f6ce45990c668742a8f758419` (`.xv/slices/2026-11-04-retro-sighting.boundary.md`)

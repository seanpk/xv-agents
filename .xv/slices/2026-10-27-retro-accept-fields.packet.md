---
slice: 2026-10-27-retro-accept-fields
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: narrow
---

# Packet: xv retro accept keeps the candidate's fields (third pass)

Nothing stops this for two people. All three points Sean settled at the second guardian stop are in the diff, and each has a test. Three notes for Sean Kennedy, the originator, are below; none is a stop. The `.xv/learnings.md` template line is Sean's own commit (`faf1781`), because the maker may not write under `.xv/`. The maker's last pass changed no code.

## The scenario

`xv retro accept <packet> <n> --by <name>` writes an Open entry in `.xv/learnings.md` that keeps the candidate's `from`, `miss`, `said` and `rule` and says who accepted it. `seen:` is `owner/repo@date` from the origin remote, or the folder name when there is no remote, for open entries, standards and rules (seanpk/xv-agents#43).

Settled at the first guardian stop: `rule:` falls back to the title, and `xv promote local --accept` keeps the miss.

Settled at the second guardian stop (record, Scenario, last paragraph):
1. Both learnings templates show the `added:` and `miss:` lines.
2. Every empty field is left out of the entry, `from:` and `miss:` included.
3. `promote local` writes the entry's `miss:` first and falls back to `said:` only when there is no miss.

May ignore: nothing stated.

## The recording

None; this is a defect from words. To replay, run the red: `cd tests && python3 -m unittest test_retro_accept_brief_shape`. At `b66c580` it failed 4 of 6, as the record's `red_output` shows. At HEAD I ran `python3 -m unittest test_retro_accept_brief_shape test_retro_accept_fields test_retro`: 14 tests, OK. The record says the whole suite is green after the cleaner (208 tests, OK). I did not run the whole suite again.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-27-retro-accept-fields.boundary.md`):
- Touched: `scripts/promote` and `scripts/retro`. (The uncommitted change to that file adds `scripts/promote` to the touched list.)
- Modules, edges and outbound calls added or removed: none.
- Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- A candidate with all four fields keeps `from`, `miss`, `said` and `rule` verbatim, and the entry names the `--by` person. `seen:` reads the origin remote, whether HTTPS or SSH, and falls back to the folder name. Standards and rules write `seen:` the same way.
- A brief-shaped candidate (`from` and `miss`, no `said` or `rule`) writes no `said:` line. Its `rule:` is the title and its `miss:` is kept. `promote local` then keeps that miss.
- A candidate with only a title and a kind writes no empty `- x:` line, and no `from:` or `miss:` line at all.
- `promote local` on an entry that has both `miss` and `said` writes the miss and leaves out the said. On an entry with no miss, it writes the said, quotes included.
- The fenced templates in `defaults/learnings.md` and `.xv/learnings.md` each contain `- added: ` and `- miss: `.

## 1. Shape

`shape_change: no`. `shape_breadth: narrow`, the same as the forecast's `"shape": "narrow"`.

- The boundary picture has no shape hints and no new edges. `retro` already called `promote`, and `promote` already called `xvlib`. The new `git` import comes from `xvlib` (`scripts/retro.py:25`), which `.xv/picture.md:23` calls "the shared base (config, git, record paths)".
- `git config --get remote.origin.url` (`scripts/retro.py:198`) reads local config only. No new outbound call, so `.xv/picture.md:24` holds.
- The forecast's breadth note said "the rest of retro.py and xv promote should not move". `scripts/promote.py:241` moved by one line. Settled point 3 asked for exactly that, citing `scripts/promote.py:241`. It is still narrow.
- `defaults/learnings.md:9,11` changed. `defaults/` reaches every new adopter (`.xv/picture.md:25`), but the change is template text, not structure.

## 2. Pitch

`pitch_contradiction: no`. I checked:
- `.xv/pitch.md:7`: adopting XV "in a repo".
- `.xv/pitch.md:17`: without xv-agents, "sharing learnings between teams would be high friction". An `owner/repo` sighting and a kept `miss` help a learning travel.
- `.xv/pitch.md:25`: who it is not for. The diff does not touch it.

## 3. Moved tests

None. No test that existed at the base `94cdf5f` changed: `git diff 94cdf5f..HEAD -- tests` adds `tests/test_retro_accept_fields.py` and `tests/test_retro_accept_brief_shape.py`, and both are new in this slice. `xv wall diff` reports changed, deleted, added and fewer_assertions all `[]`. The record has `moved_tests: []`.

- The red commit `b66c580` grew `test_retro_accept_brief_shape.py`, a file this slice created, from 5 assertions to 13 (`.wall.json`). It added four tests, and its one removed line was an import (`from helpers import RepoCase`, now `from helpers import HOME, RepoCase`). Nothing asserts less.

Slice-only removals: none (`slice_only: []`).

## 4. The picture

No edit proposed. I looked at:
- The shape section (`.xv/picture.md:21-27`): `retro` and `promote` are still the side loops on `xvlib` (`.xv/picture.md:23`).
- Names (`.xv/picture.md:30-38`): nothing about learnings fields or `seen:`.
- Decision 4 (`.xv/picture.md:62`): learnings travel as issues, and nothing here changes that.

The picture does not describe the entry format, so this change makes nothing in it untrue.

## Notes for the originator

1. **Standards and rules still write an empty `from:` or `miss:`.** Settled point 2 cited the open branch (then `scripts/retro.py:202-203`), and that branch is fixed. The standard and rule branch still writes both lines unconditionally:
   ```
   scripts/retro.py:211  entry = (f"\n### {c['title']}\n- added: {today()} by {by}\n- from: {c.get('from', '')}\n"
   scripts/retro.py:212           f"- miss: {c.get('miss', '')}\n- seen: [{repo}@{today()}]\n")
   ```
   The field pattern `^- (\w+):\s*(.+)$` (`scripts/check.py:159`) lets `\s*` cross the newline. An empty `from:` therefore reads the `miss:` line as its value, and `scripts/check.py:177` does not add "no slice: delete at the next retro". This was already the case at the base, and the slice did not touch it. The brief's shape lists `from` and `miss` for every candidate (`skills/xv-retro/retro-brief.md:45-46`), so it is unlikely to happen. Whether "the entry" in point 2 covers these two kinds is for you to say.
2. **`said:` is written as the candidate gave it.** `scripts/retro.py:208` writes `- said: {c['said']}`, with no quotes added. The template shows `- said: "<the words, verbatim>"` (`defaults/learnings.md:12`). The quotes appear only if the retro agent wrote them. No parser depends on them. With no miss, `promote local` copies the said exactly as written (asserted by `test_promote_local_falls_back_to_said_when_the_entry_has_no_miss`).
3. **Existing entries promote as before.** The two Open entries in `.xv/learnings.md:21-32` have `said:` and no `miss:`. Under the new `fields.get('miss', fields.get('said', ''))` (`scripts/promote.py:241`), they still promote with the said as their miss.

## Door

**Door:** two-way. A revert restores the old writer and templates. Entries already accepted are committed text that a person can edit. `scripts/check.py:160` (`([\w.-]+)@(\d{4}-\d{2}-\d{2})`) reads `seanpk/xv-agents@date` as `xv-agents`, the same name the old entries carry. Repos set up with `xv init` from this version keep the new template lines (`.xv/picture.md:25`); a revert does not reach them. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-27-retro-accept-fields.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..HEAD`. This pass's change is `git diff eac56b0..HEAD -- scripts defaults tests .xv/learnings.md`.
- Wall: `xv wall diff 2026-10-27-retro-accept-fields` (baseline `eac56b0`)
- Boundary: `.xv/slices/2026-10-27-retro-accept-fields.boundary.md`
- Packet template: `skills/guardian/packet.md` is outside the worktree and I could not read it. This packet follows the shape of the earlier passes' packets.

## From the cleaner

- Shape proposal, for people: put the `owner/repo` parse of `remote.origin.url` (the regex plus the basename fallback) in one `xvlib` helper. `scripts/retro.py:198-200` repeats `scripts/run.py:753-755`. It is a new shared function, so it is not a cleanup.

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The same commit moved the wall baseline from `5452321` to `eac56b0` and reset that file's hash. That is why `xv wall diff` shows nothing.

## From the cleaner

- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 now repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.
- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.
- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.

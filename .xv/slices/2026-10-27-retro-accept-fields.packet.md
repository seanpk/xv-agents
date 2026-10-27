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

# Packet: xv retro accept keeps the candidate's fields (second pass)

Nothing stops this for two people. The fix for the stop on 2026-10-27 is in: a candidate in the brief's shape no longer writes empty lines, and promotion keeps its miss. One part of Sean's settled scenario is not done. The learnings templates still show the old entry format (finding 1). Sean Kennedy, the originator, decides that before merge.

## The scenario

`xv retro accept <packet> <n> --by <name>` writes an Open entry that keeps the candidate's `from`, `miss`, `said` and `rule` and says who accepted it. It writes `seen:` as `owner/repo@date` from the origin remote, or the folder name if there is no remote. Standards and rules write `seen:` the same way (seanpk/xv-agents#43). Settled at the guardian's stop (record, Scenario, second paragraph): an empty field is left out, `rule:` falls back to the title, `xv promote local --accept` keeps the miss, and the templates `defaults/learnings.md` and `.xv/learnings.md` show the `added:` and `miss:` lines. May ignore: nothing stated.

## The recording

None; this is a defect from words. To replay: `cd tests && python3 -m unittest test_retro_accept_brief_shape` (the red) and `python3 -m unittest test_retro_accept_fields`. The red at `9bd5fc3` failed 2 of 2. The record quotes `miss: - rule: ` in the promoted standard. I re-ran the red at HEAD and both tests pass. The record says the whole suite is green (204 tests, OK, after the cleaner). I did not re-run the whole suite.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-27-retro-accept-fields.boundary.md`):
- Touched: `scripts/retro`.
- Modules, edges and outbound calls added or removed: none.
- Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- A candidate with all four fields keeps `from`, `miss`, `said` and `rule` verbatim. `seen:` is `seanpk/xv-agents@<today>` from an HTTPS remote and `repo@<today>` with no remote.
- Standards and rules get `seen: [seanpk/xv-agents@<today>]` from an SSH remote.
- The open entry contains the `--by` name (`assertIn("pat", …)` on the whole file).
- A candidate in the brief's shape (`kind`, `from`, `miss` only) writes no `- said:` line. Its `rule:` is the title, and its `miss:` is kept.
- `promote.local_accept` on that entry writes a standard titled with the rule, and its `miss:` is the candidate's miss.

## 1. Shape

shape_change: no. shape_breadth: narrow, as the forecast said (`"shape": "narrow"`).

- The boundary picture has no shape hints, edges or outbound calls. The only new import is `git` from `xvlib` (`scripts/retro.py:25`). `.xv/picture.md:23` names `xvlib` as "the shared base (config, git, record paths)", so this stays inside the current shape.
- `git config --get remote.origin.url` (`scripts/retro.py:198`) reads local config. It does not call out of the process, so `.xv/picture.md:24` still holds.
- The forecast's breadth said the `kind == "open"` branch and the `seen:` writer would change, and the rest of `retro.py` and `xv promote` would not. The diff matches that: `scripts/retro.py:198-206` changed and `scripts/promote.py` did not.

## 2. Pitch

pitch_contradiction: no. I checked:
- `.xv/pitch.md:7`, adopting XV "in a repo".
- `.xv/pitch.md:17`, "sharing learnings between teams would be high friction". An `owner/repo` sighting and kept fields make an entry easier to share.
- `.xv/pitch.md:25`, who it is not for. Nothing in the diff touches it.

## 3. Moved tests

None. `xv wall diff 2026-10-27-retro-accept-fields` reports changed, deleted, added and fewer_assertions all `[]`, and the record has `moved_tests: []`. The diff `94cdf5f..HEAD` touches only two test files, both new: `tests/test_retro_accept_fields.py` and `tests/test_retro_accept_brief_shape.py`.

Slice-only removals: none. The record has no `slice_only` list.

## 4. The picture

No edit proposed. I looked at:
- The shape section, `.xv/picture.md:21-27`. `retro` is still a side loop on `xvlib`.
- Names, `.xv/picture.md:30-38`. It has no term for learnings fields or `seen:`.
- Decision 4, `.xv/picture.md:62`, learnings travel as issues. This diff does not change that.

The picture does not describe the entry format, so nothing in it becomes untrue.

## Other findings (for the originator)

1. **The settled scenario's template change was not made.** The record, Scenario, second paragraph, says: "The learnings templates, `defaults/learnings.md` and `.xv/learnings.md`, show the `added:` and `miss:` lines that accept now writes." Neither file is in `git diff 94cdf5f..HEAD`.
   - `defaults/learnings.md:8-12` and `.xv/learnings.md:7-13` still show `from / said / rule / seen`, with no `added:` and no `miss:`.
   - The writer now emits both, at `scripts/retro.py:202-203`: `- added: {today()} by {by}` and `- miss: {c.get('miss', '')}`.
   - No test covers the templates, so the suite stays green without them.
   - `defaults/` reaches every new adopter (`.xv/picture.md:25`). New repos will see a template that does not match what accept writes.
2. **Under `xv promote local`, a candidate's `said` now beats its `miss`.** When the candidate carries `said`, `scripts/promote.py:241` writes `- miss: {fields.get('said', fields.get('miss', ''))}`. The promoted standard's `miss:` becomes the verbatim quote, not what happened.
   - Before this change, `said` held the miss (old `scripts/retro.py` line `- said: \"{c.get('miss', '')}\"`), so promotion carried the miss.
   - The brief-shaped test has no `said`, so it does not reach this case. The full-field test does not promote.
   - It matters only for candidates that carry `said`, and the retro brief's shape (`skills/xv-retro/retro-brief.md:43-50`) does not list it.
3. **An empty `miss:` still breaks the parse.** `scripts/retro.py:203` writes `- miss: ` even when the candidate has no `miss`. The field pattern `^- (\w+):\s*(.+)$` (`scripts/retro.py:117`, `scripts/promote.py:238`) lets `\s*` cross the newline. A later read would then take `rule:`'s line as the miss, the same failure this slice fixed for `said`. The same holds for an empty `from:` (`scripts/retro.py:202`). The brief's shape lists `from` and `miss` for every candidate (`skills/xv-retro/retro-brief.md:45-46`), so this is unlikely, but no check enforces it.
4. **`said:` loses its quotes.** The old line wrote `- said: "{miss}"`. The new `scripts/retro.py:205` writes `- said: {c['said']}` as given. The template's `said: "<the words, verbatim>"` (`defaults/learnings.md:10`) holds only if the candidate quoted its text. I found no parser that depends on the quotes.

## Door

**Door:** two-way. A revert restores the old writer. Entries already accepted are text that people commit, and `scripts/check.py:160` (`([\w.-]+)@(\d{4}-\d{2}-\d{2})`) reads `xv-agents@date` and `seanpk/xv-agents@date` as the same repo. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-27-retro-accept-fields.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..5c82d83`; this pass's change is `git diff 3e351e2..5c82d83 -- scripts tests`
- Wall: `xv wall diff 2026-10-27-retro-accept-fields` (baseline `5452321`)
- Boundary: `.xv/slices/2026-10-27-retro-accept-fields.boundary.md`
- Packet template `skills/guardian/packet.md` sits outside the worktree and I could not read it. This packet follows the shape of the first pass's packet (`3e351e2`).

## From the cleaner

- Shape proposal, for people: put the `owner/repo` parse of `remote.origin.url` (the regex plus the basename fallback) in one `xvlib` helper. `scripts/retro.py:198-200` repeats `scripts/run.py:753-755`.

## From the cleaner

- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 now repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.
- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.

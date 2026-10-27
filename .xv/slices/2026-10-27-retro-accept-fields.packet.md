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

# Packet: xv retro accept keeps the candidate's fields

Nothing stops this for two people. One finding needs the originator (Sean Kennedy) before merge. The retro brief's candidate shape has no `said:` or `rule:` field. An open candidate in that shape now gets empty `said:` and `rule:` lines, and a later `xv promote` accept turns them into a standard whose `miss:` is the text `- rule:`. Before this change, that same entry carried the miss through. See "Other findings".

## The scenario

`xv retro accept <packet> <n> --by <name>` writes an Open entry in `.xv/learnings.md` that keeps the candidate's `from`, `miss`, `said` and `rule`, says who accepted it, and writes `seen:` as `owner/repo@date` from the origin remote. With no remote, it falls back to the folder name. Standards and rules accepted the same way also write `seen:` as `owner/repo@date` (seanpk/xv-agents#43). May ignore: nothing stated.

## The recording

None; a defect from words. Replay: `cd tests && python3 -m unittest test_retro_accept_fields`. At red (`aee6590`) 3 of 4 failed. The record quotes the failure: `'- miss: the guess was never run\n' not found`. At HEAD all 4 pass (I re-ran them). Per the record, the whole suite is green: 202 tests, OK.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-27-retro-accept-fields.boundary.md`): touched `scripts/retro`. Modules added or removed: none. Edges added or removed: none. Outbound calls added: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- An open candidate with `from`, `miss`, `said` and `rule` keeps all four, verbatim, in the learnings entry.
- An origin remote `https://github.com/seanpk/xv-agents.git` gives `seen: [seanpk/xv-agents@<today>]`. With no remote it gives `seen: [repo@<today>]`, the folder name.
- The open entry contains the `--by` name. The assertion is `assertIn("pat", …)` on the whole file, which is loose but true here.
- An SSH remote `git@github.com:seanpk/xv-agents.git` gives `seen: [seanpk/xv-agents@<today>]` for both standards and rules.
- No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"`.

- The boundary picture shows no shape hints, no new edges and no new outbound calls. The only new import is `git` from `xvlib` (`scripts/retro.py:25`). `retro` already imported `xvlib`, and `.xv/picture.md:23` names `xvlib` as "the shared base (config, git, record paths)". This is inside the current shape.
- `git config --get remote.origin.url` (`scripts/retro.py:198`) is a local read, not a call out of the process. `.xv/picture.md:24` (outbound calls) still holds.
- The cleaner flagged a duplication: `scripts/retro.py:198-200` repeats the parse at `scripts/run.py:753-755`. Pulling it into one `xvlib` helper would be a small shape proposal, and it is left for the originator. It is not a shape change in this slice.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo"), `:17` ("sharing learnings between teams would be high friction") and `:25` (not for people who won't trust agents; never a teapot). The change makes local learnings carry their own fields and an `owner/repo` name, which serves `:17`. Nothing in the diff touches `:25`.

## 3. Moved tests

None. `xv wall diff 2026-10-27-retro-accept-fields` reports changed, deleted, added and fewer_assertions all `[]`. The record has `moved_tests: []`. The only test file in `git diff 94cdf5f..HEAD` is the new `tests/test_retro_accept_fields.py`.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

## 4. The picture

No edit proposed. I looked at the shape section (`.xv/picture.md:21-27`, where `retro` is a side loop on `xvlib`, which is still true) and at Names (`:30-38`, which has no term for `seen:` or learnings fields). Nothing in the picture describes the learnings entry format or how a repo name is taken, so nothing in it becomes untrue.

## Other findings (for the originator)

1. **Open candidates in the brief's shape now lose their miss on promotion.** Diff hunk `scripts/retro.py:202-204`:
   ```
   + f"- miss: {c.get('miss', '')}\n- said: {c.get('said', '')}\n- rule: {c.get('rule', '')}\n"
   ```
   The retro writes candidates in the shape at `skills/xv-retro/retro-brief.md:42-50`: `kind`, `from`, `miss`, `check`, `adopts`, `into`. That shape has no `said` or `rule`, so the common case writes `- said: ` and `- rule: ` with nothing after them. The field pattern `^- (\w+):\s*(.+)$` (`scripts/retro.py:117`, `scripts/check.py:159`, `scripts/promote.py:238`) lets `\s*` cross the newline. So `said` reads as `- rule: `, and `rule` disappears. `promote.local_accept` then writes `- miss: {fields.get('said', fields.get('miss', ''))}` (`scripts/promote.py:241`), and the promoted standard's miss becomes `- rule: `. Before this change, `said` held the miss and `rule` held the title, so promotion carried them. I worked this out from the code; I could not run a probe outside the worktree. The test feeds a candidate with all four fields, so the suite does not see this case. The options are for the originator: omit empty fields, fall back to the old values, or add `said`/`rule` to the retro brief's candidate shape. That last one is a brief change, which is for two people under `.xv/picture.md:59`.
2. **The learnings template no longer matches what accept writes.** The same hunk adds `- added:` and `- miss:` lines to open entries. The format shown at `defaults/learnings.md:8-12` (copied into every adopter, `.xv/picture.md:25`) and at this repo's `.xv/learnings.md:7-13` has neither. The proposed edit is to add both lines to the two templates, or to drop them from the writer.
3. **`said:` loses its quotes.** The old line wrote `- said: "{miss}"`. The new line writes the candidate's `said` as given, so the template's `said: "<the words, verbatim>"` quoting holds only if the candidate quoted it. The test's candidate did. I found no parser that depends on the quotes.

## Door

**Door:** two-way. A revert restores the old writer. Entries already accepted are person-committed text, and `check.py:160` reads both `repo@date` and `owner/repo@date` as the same repo. **Blast radius:** narrow.

## Raw data

- Slice record: `.xv/slices/2026-10-27-retro-accept-fields.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..dd38e22`
- Wall: `xv wall diff 2026-10-27-retro-accept-fields`
- Boundary: `xv boundary --base 94cdf5f15f31c53d02fc8de787ce85889627e799`

## From the cleaner

- Shape proposal, for people: Extract the `owner/repo` parse of remote.origin.url (regex plus basename fallback) into one xvlib helper: scripts/retro.py:198-200 now repeats scripts/run.py:753-755. It is a new shared function, so it is not a cleanup.

---
slice: 2026-10-25-diff-count
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: diff_growing counts only the maker's files

**Needs a decision from Sean (originator; two people is `solo`):** this changes what the `diff_growing` standing order measures, but the diff has no `CHANGELOG.md` line. Decision 1 in the picture asks for one. Nothing stops this for two people. Otherwise the merge is Sean's.

## The scenario

`diff_lines`, which the `diff_growing` stop and `limits.max_diff_lines` read after the maker and the cleaner, counts only files outside `.xv/`. A packet or boundary file the guardian writes between two maker runs does not make the diff look like it grew (seanpk/xv-agents#24). The slice may ignore what `max_diff_lines` means beyond leaving out `.xv/`.

## The recording

None; the slice started from words. To replay: `cd tests && python3 -m unittest test_diff_count`. Before the fix it failed with `75 != 12` (maker) and `276 != 12` (cleaner, after a 200-line packet). I re-ran it on this HEAD: `Ran 2 tests ... OK`.

## The boundary picture

From `.xv/slices/2026-10-25-diff-count.boundary.md`, as given: touched `scripts/run`. No modules or edges were added or removed, no outbound calls, no tables, no surfaces. Shape hints: none.

## What the suite asserts after

- New, `tests/test_diff_count.py`: after the forecaster, scenario and maker run on a fixture slice, the maker's `diff_lines` is 12. That is the 10 lines of `tests/test_red.py` plus 1 added and 1 deleted line in `pantry/store.py`, so the slice record under `.xv/` is not counted.
- New: a 200-line `.xv/slices/s1.packet.md` is committed before the cleaner runs, and the cleaner's `diff_lines` is still 12.
- No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast ("One filter in diff_lines … plus a test in tests/**", `.xv/slices/2026-10-25-diff-count.md:11`).

- The change is one pathspec inside `post_step`, `scripts/run.py:369-370`:
  ```
  +        stat = git(["diff", "--numstat", data.get("base") or head_before,
  +                    "--", ".", f":(exclude){XV_DIR}"], root)
  ```
  It adds no module, edge, table or surface (boundary picture: all "none"). It stays inside the shape the picture describes: "`orders` holds the stop rules" (`.xv/picture.md:23`). `orders.py` is untouched.
- `XV_DIR` was already imported (`scripts/run.py:32`), so no new dependency.

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`). A stop that no longer fires on the guardian's own files fits that line. The change does not touch who the system is for (`.xv/pitch.md:21`, `.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | — | — | — | — |

Evidence: `git diff f452d43..HEAD -- tests` shows only the new `tests/test_diff_count.py`. The record has `moved_tests: []`, and the wall check at both maker and cleaner has `changed: [], deleted: [], fewer_assertions: [], ok: true` (`.xv/slices/2026-10-25-diff-count.md:26`). I could not run `xv wall diff` myself because the permission was not granted, so this row rests on the git diff and the record.

## 4. The picture

No edit proposed. The picture never says how the diff is measured. I checked the shape (`.xv/picture.md:19-28`), the names (`.xv/picture.md:30-37`) and the binding decisions (`.xv/picture.md:56-72`), and this change makes none of them untrue.

## Findings for the originator

1. **No CHANGELOG line for a change to a check.** Decision 1 says: "A change to … a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:58`). The maker is judged by `diff_growing` (`scripts/orders.py:105-114`), and this slice changes what that order reads (`scripts/run.py:369-370`). The slice diff does not touch `CHANGELOG.md`. The repo has a precedent: the smaller `xv promote draft` slice got a line under "Unreleased" (`CHANGELOG.md:7`). Sean decides whether this is "a check an agent is judged by" and, if so, who writes the line.
2. **History straddling the change.** `diff_history` adds new counts to the old ones (`scripts/run.py:374`), and `diff_growing` compares the last two (`scripts/orders.py:106`). A slice in flight when this merges has an old count that includes `.xv/` and a new one that doesn't. Its next comparison can only shrink, so it misses a real doubling rather than firing a false one. This needs no action; it is noted so a quiet stop on an open slice isn't a surprise.
3. **The record's own counts predate the fix.** The recorded `diff_lines` 162 (maker) and 163 (cleaner) (`.xv/slices/2026-10-25-diff-count.md:26`) match the whole diff, including `.xv/` (`git diff --stat`: 162 insertions). The watch that ran the steps counted with the old code. Those numbers are not evidence about the fix; the new test is.
4. `docs/decisions.md:113` ("'The diff keeps growing' is measured across the maker's runs") doesn't say which files count. This optional addition would not bind (`.xv/picture.md:74`): one clause saying `.xv/` is left out.

## Door

**Door:** two-way. Reverting the one pathspec undoes it, and no data or contract moves. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-25-diff-count.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`
- Wall: `xv wall diff 2026-10-25-diff-count`
- Boundary: `xv boundary --base f452d430f44f6c01e611f705f5b709b80231291b` (as given in `.xv/slices/2026-10-25-diff-count.boundary.md`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- stat = git(["diff", "--numstat", data.get("base") or head_before], root)

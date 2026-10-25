---
slice: 2026-10-24-promote-draft
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: xv promote draft: whole-word titles, any stack, one date, attribution

Nothing here stops the change for two people. The merge is the originator's (Sean). Three things need Sean's eye:

1. `promote.stack` is now read but never used.
2. The new `promote.attribution` key is not in the briefs that list the `promote:` keys.
3. Sean's own agent allow-list commit is part of this diff.

## The scenario

`xv promote draft` gives a title cut at a word boundary, "Applies to: any" when no `--applies-to` is passed, a draft file name with one date, and a body that ends with the assistant's attribution line (seanpk/xv-agents#13). Settled at the scenario stop: a new setting `promote.attribution`, empty by default. When it is set, every draft body ends with that line. This repo sets it to `🤖 Claude on behalf of Sean`. The slice may ignore `post` and `tally`.

## The recording

None; the work started from words. To replay: `cd tests && python3 -m unittest test_promote_draft`. Before the change: 4 of 6 failed (`AssertionError: 2 != 1 : 2026-10-24-2026-10-20-stop-before-a.md`). After: 6 of 6 pass (rerun by the guardian). The whole suite is green, 126 tests (cleaner's run in the record).

## The boundary picture

From `xv boundary`, as given (`.xv/slices/2026-10-24-promote-draft.boundary.md`):

- Touched: `scripts/promote`. No modules added or removed.
- Edges added or removed: none. No new outbound calls.
- Tables: none. Surface paths: none added or removed.
- Shape hints: none.

## What the suite asserts after

New file `tests/test_promote_draft.py`, 6 tests:

- A 105-character rule gives a title cut to the whole words that fit in 90 characters.
- With `promote.stack: ["python"]` set and no `--applies-to`, both the body's "Applies to" section and the sighting line say `any`.
- An explicit `--applies-to rust` still wins.
- An entry headed `2026-10-20: ...` gives a draft file name with exactly one date, today's.
- With `promote.attribution` set, the last line of the body is that line, for both a new draft and a sighting on an existing issue.
- With it unset, the body does not contain "Claude".

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast ("narrow", confined to the promote draft path).

- The boundary picture shows only `scripts/promote` touched, with no edges, tables or surfaces added. All of this fits the picture's shape, where `promote` is one of the side loops (`.xv/picture.md:23`).
- **The new config key reaches every new adopter.** `defaults/config.yml:81` adds `+  attribution: ""`. The picture says "`defaults/` is the starter `.xv/` that `xv init` copies into every adopting repo. A change there reaches every new adopter" (`.xv/picture.md:25`). The key is empty by default, and `scripts/promote.py:154-155` (`if s["attribution"]: body = ... + s["attribution"]`) adds nothing when it is empty. Adopters see no change in behaviour. This is a new knob inside an existing file, not a new surface.
- **Outside the forecast's breadth, but authored by a person: the agent allow list.** `.xv/config.yml:34-36` adds `"--allowedTools", "Bash(cat:*),...,Bash(git rm:*),Bash(git mv:*),...,Bash(xv record move:*)..."` to `default`, `forecaster` and `guardian`. This came in Sean's commit `45db322` ("config allow list"), not from the maker. It changes no module or edge. It does let every agent in this repo run `git rm` and `git mv`, including the guardian, whose brief allows it to write only the packet. The picture's binding decision 12 covers this: "Read-only agents are checked, not trusted" (`.xv/picture.md:71`). For Sean: confirm this line belongs in this slice's merge.

## 2. Pitch

pitch_contradiction: no.

- What I looked at: the pitch's purpose ("makes it easy for a team or an individual to adopt Xtreme Vibing", `.xv/pitch.md:7`), its sharing aim ("sharing learnings between teams would be high friction", `.xv/pitch.md:17`), and its never-list (`.xv/pitch.md:25`).
- Related binding decision: "Nothing is posted in public without a person's approval" (`.xv/picture.md:64`). The draft path still writes `"status": "draft"` (`scripts/promote.py:156`) and posts nothing.

## 3. Moved tests

None. The wall shows no changed, deleted or added files against baseline `45db322` (record `checks.maker.wall` and `checks.cleaner.wall`: `changed: [], deleted: [], fewer_assertions: [], unrecorded: []`). `git diff 45db322..HEAD -- tests/` shows only the new red file, `tests/test_promote_draft.py`. `moved_tests: []` in the record agrees. I could not run `xv wall diff` here because it needed an approval this run did not have, so these figures come from the record and from git.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Findings for the originator (these do not stop the change):

- **`promote.stack` is now read but unused.** The diff removes `-    applies = applies or ", ".join(s["stack"])` (`scripts/promote.py`, hunk at `@@ -134`). `"stack": p.get("stack") or []` remains at `scripts/promote.py:55`, and no other script reads it. The scenario asks for exactly this behaviour ("Applies to: any" when no `--applies-to` is passed). But the brief that sets the key now gives a reason that no longer holds: "The stacks it is built on ... so a learning that only means something on one stack is marked" (`skills/xv-init/SKILL.md:85`). Changing that brief needs two people (`.xv/picture.md:60`). The maker was right to leave it alone.
- **The new key is missing from the briefs that list the `promote:` keys.** `skills/xv-init/SKILL.md:87` still lists "`include_name`, `name`, `description`, `stack`" without `attribution`. `CHANGELOG.md` has no entry for it. No binding rule requires one for an added key: decision 14 covers renames only (`.xv/picture.md:73`).

## 4. The picture

No edit proposed. What I checked:

- The shape section (`.xv/picture.md:20-28`): `promote` as a side loop, and `defaults/` reaching adopters. Both stay true.
- The names section (`.xv/picture.md:30-37`).

The picture names no `promote:` config keys, so neither the new key nor the unused `stack` makes it untrue. The stale lines are in `skills/xv-init/SKILL.md:85,87`, which is a brief, not the picture.

## Door

**Door:** two-way. Reverting the commits undoes it; nothing is migrated or posted, and the default config key is empty. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-24-promote-draft.md`
- Diff: `git diff 948efd1159971b567b82e3bc8045c8c6542e5300..a382595`
- Wall: `xv wall diff 2026-10-24-promote-draft` (baseline `45db3228429a`, 25 files)
- Boundary: `.xv/slices/2026-10-24-promote-draft.boundary.md` (`xv boundary --base 948efd115997`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The change makes learning drafts cleaner to share and marks drafts written by an agent. That serves line 17 and touches nothing on line 25.
- The binding decisions: 4, learnings travel as issues (`:63`); 5, no public post without approval (`:64`); 9, YAML with JSON values (`:68`). The new key is a JSON string in YAML.

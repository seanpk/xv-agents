---
slice: <slice id>
shape_change: no
pitch_contradiction: no
picture_change: no
moved_tests: 0
door: two-way
blast_radius: <one word>
---

# Packet: <slice title>

<One or two lines: what needs a decision, by whom. If nothing does, say the merge is the originator's.>

## The scenario

<The scenario in words, and what this slice may ignore. Words first, so a picture cannot stand in for a scope.>

## The recording

<The recording for a defect, or the command that replays the red and the green. Before and after.>

## The boundary picture

<From `xv boundary`, as given: the modules touched, edges added and removed, tables, surfaces users meet. Mermaid is fine.>

## What the suite asserts after

<In words: the new scenario, and each old assertion that moved.>

## 1. Shape

shape_change: <yes|no>. <Each finding with its citation.>

## 2. Pitch

pitch_contradiction: <yes|no>. <Each finding quotes the pitch line.>

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |

## 4. The picture

<Each line of `.xv/picture.md` this change makes untrue or incomplete, and the proposed edit.>

## Door

**Door:** <one-way|two-way>. **Blast radius:** <one word>.

## Raw data

- Slice record: `.xv/slices/<id>.md`
- Diff: `git diff <base>..<head>`
- Wall: `xv wall diff <id>`
- Boundary: `xv boundary --base <base>`

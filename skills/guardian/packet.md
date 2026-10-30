---
slice: <slice id>
shape_change: no            # yes, no, or accepted (then accepted_by names the decision record)
accepted_by: <.xv/decisions/file.md, only with shape_change: accepted>
pitch_contradiction: no
scenario_miss: no           # yes when a scenario line or a binding decision is missed; list it under Scenario misses
picture_change: no
shape_breadth: none
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

Slice-only tests removed: <the tests, on one line, or none>. Kept: <each kept slice-only test, with the reason to keep it, or none>.

## 4. The picture

<Each line of `.xv/picture.md` this change makes untrue or incomplete, and the proposed edit.>

## 5. The wall

<Each new test that should join the wall or leave it, and each test already on the wall that should be removed: the file, the test, the recommendation, and the citation. Or say what you looked at.>

## Scenario misses

<Only with `scenario_miss: yes`. One line for each scenario line or binding decision the change misses: `- <point, such as 2 or amendment 1, item 3, or decision 4>: <what is missed> (evidence: <a test, a run, or a diff hunk>; to: maker|scenario)`. `to` is your call on whether the red covers the line. Add `amend: yes` when meeting the miss would change the scenario. Or leave the section out.>

## Door

**Door:** <one-way|two-way>. **Blast radius:** <one word>.

## Raw data

- Slice record: `.xv/slices/<id>.md`
- Diff: `git diff <base>..<head>`
- Wall: `xv wall diff <id>`
- Boundary: `xv boundary --base <base>`

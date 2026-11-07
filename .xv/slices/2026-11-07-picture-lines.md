---
id: 2026-11-07-picture-lines
title: One sentence per line in the picture
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-07
branch: xv/2026-11-07-picture-lines
base: d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50
next: forecaster
build: none
build_shared: no
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: []
stops: []
decisions: []
prototypes: []
overrides: []
checks: {}
---
# One sentence per line in the picture

## Scenario

1. Each sentence in `.xv/picture.md` starts on its own line. The extra lines of a list item are indented two spaces, so they stay in the item.
2. When the lines are joined again, the picture's text is the same as before, word for word. A check shows this.
3. The briefs that write the picture (guardian, maker, watch, `xv-init`) state the rule: one sentence per line, and list-item lines indented two spaces. A repo that adopts xv gets the rule too.
4. `xv-check` finds the same things in the new picture as it did before.
5. A `CHANGELOG.md` line names the rule.
6. When a step leaves a picture line that holds more than one sentence, the packet gets a note naming the line. It is a note, not a stop. A sentence end counts only outside backticks, and only as a full stop and a space followed by a capital letter.

## May ignore

The other .xv files (learnings.md, rules.md, estimation.md) stay as they are. Pictures in other repos that already use xv. Retro candidate 1 (when picture edits happen at rebase); decide it after a few rebases on the new picture.

## Recording

None. A feature starts from words.

## Log
- 2026-11-07T15:18:16+00:00 watch: slice opened by Sean Kennedy

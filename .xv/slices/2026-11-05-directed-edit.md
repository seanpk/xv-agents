---
id: 2026-11-05-directed-edit
title: "The watch makes a directed change the person approved (#132)"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-directed-edit
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: forecaster
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
# The watch makes a directed change the person approved (#132)

## Scenario

# The watch makes a directed change the person approved: #132

What happened: a change the person had already decided went back through an agent and the guardian, even when it was one line. On slice `2026-11-04-promote-fields`, renaming a test took 18 minutes and $0.87, and deleting a test retired from the wall took 18 minutes and $0.72. The comment on #132 adds evidence from slices B, D, E and I, and three times the watch's own wording drifted, caught each time by an agent or a check.

What should happen:

1. A stop option can carry a directed change: the exact edit, as old text and new text. The person approves that diff, not a description of it. Any edit the watch would have to word itself goes to an agent.
2. Only four kinds are allowed: a line in `CHANGELOG.md`; renaming a test or removing a test, in a file under the wall's `tests.paths`; and a line in a Markdown doc that names what the code already does. Any other edit goes to an agent.
3. When the person picks the option, the watch makes exactly that edit, in its own commit. The commit message names the person who directed it. A test edit is recorded as a move in the person's name.
4. A test rename also updates every record entry that names the test (`slice_only`, `wall_recommendations`, `covers`), in the same commit.
5. After the edit, the suite and `xv orders` run. If the guardian has not run yet, it reviews the edit in its normal pass. If it has run, it does not run again, and the packet gets a line for each edit made after it, naming the edit and who directed it.
6. The watch's brief states the rule: the person approved every word, and the edit changes no behavior. The watch never words a change itself. The four kinds in point 2 are where xv-agents starts. The brief's may-not line changes to match, and `CHANGELOG.md` gets a line for it.

## May ignore

Removing a retired wall test when a person accepts its retirement: J (#120) does that in code. A doc line whose sentence matches a rule in the code and so also needs a test: the test still goes to an agent. Directed edits outside the four kinds, including any edit to source, and kinds an adopter repo might add.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T10:40:30+00:00 watch: slice opened by Sean Kennedy

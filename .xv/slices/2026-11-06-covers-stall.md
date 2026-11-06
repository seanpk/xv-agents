---
id: 2026-11-06-covers-stall
title: "A missed point goes back with text the check accepts, and stops a person only on a real stall"
kind: defect
status: open
set_by: Sean
created: 2026-11-06
branch: xv/2026-11-06-covers-stall
base: 859d2262950dbf5235c68b263de288780436bfea
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
# A missed point goes back with text the check accepts, and stops a person only on a real stall

## Scenario

When the scenario step leaves a numbered point out of both `covers` and `not_covered`, the watch sends the slice back, and the scenario agent can fix it on the next pass. A person is stopped only when the agent truly cannot cover a point.

1. The send-back hands the scenario agent, for each missed point, an `item` string the check will accept, ready to put in `covers` or `not_covered`: the point's number and its text, as the scenario has it.
2. The send-back says that every point of the scenario and its amendments goes in `covers` or `not_covered` on each pass, not only the points of the newest amendment.
3. The coverage check removes Markdown marks (backticks, `*`, `_`) from both the point and the `item` before it compares them. An item "The doc kind refuses a file under .xv/" covers the point "The `doc` kind refuses a file under `.xv/`".
4. A point missed again right after a send-back for that same point goes back once more. The person who set the work going is stopped as `red_misses_point` only on the third miss in a row.
5. Only the send-backs of the run of passes that ends now count toward that stop. A send-back from before an amendment or before a person's answer does not count. A point sent back two passes ago, then covered, then missed again, goes back; it does not stop the person.
6. The change to the `red_misses_point` trigger has a `CHANGELOG.md` line.

## May ignore

The guardian's scenario_miss repeat check: it also uses sent_back (scripts/orders.py:274), and its behavior stays the same. Other ways the text match can fail, such as a reworded point. A refactor slice's own points: they have no red.

## Recording

.xv/recordings/2026-11-06-covers-stall.md

## Log
- 2026-11-06T19:34:08+00:00 watch: slice opened by Sean

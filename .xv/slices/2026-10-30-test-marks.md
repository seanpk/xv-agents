---
id: 2026-10-30-test-marks
title: A person sees which tests stay on the wall and which leave it
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-test-marks
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: forecaster
forecast: null
budget: null
red: null
wall_baseline: null
moved_tests: []
slice_only: []
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
# A person sees which tests stay on the wall and which leave it

## Scenario

A person sees which tests stay on the wall and which leave it (#87, #89).

1. The person accepts the slice-only marks (#89). After the scenario step, a new order seated for the person who set the work going fires only when the scenario report marks slice-only tests. It lists each marked test with the scenario agent's reason. The person accepts the marks, or unmarks a test so it joins the wall. The answer is recorded like any other stop. A slice with no marks adds no stop. The watch's stop table and the README's list the new order.
2. The guardian says which new tests should join the wall or leave it (#87). `skills/guardian/SKILL.md` has a fifth check, for three kinds of recommendation: a test marked slice-only should stay; a new test that was not marked should not join the wall; a test that was on the wall before the slice should be removed. The packet has a section for them. They reach the person who set the work going in `accept_moves`, not two people, and the record keeps which ones the person accepted. The places that say the guardian has four checks say five.

This adds a standing order and changes a brief and the packet template, so `CHANGELOG.md` gets a line.

## May ignore

Rewording the site. Moving slice-only tests out of the cleaner.

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T01:07:13+00:00 watch: slice opened by Sean Kennedy

---
id: 2026-10-30-stop-words
title: "The stops, the briefs and the picture say what the method says"
kind: feature
status: open
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-stop-words
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
# The stops, the briefs and the picture say what the method says

## Scenario

The stops, the briefs and the picture say what the method says since 2026-10-29 (#85, #86, #88 with #68, #90).

1. An accepted shape change does not stop again (#85). A shape change that matches a decision already accepted on the same slice does not stop the slice again. A shape that differs from it still stops for two people. The guardian's other findings reach the person who set the work going at the merge stop.
2. A stall names the stall (#86). The question for `repeated_failure` and `diff_growing` names the stall on this slice and the four choices: continue, reshape the slice, raise the budget, or bring in a second person. It no longer says "The shape conversation opens". The maker still stops and still may not renovate. The glossary row for the shape conversation (`README.md:26`) says it opens on a shape change, and before and after a burst. The stop tables (`skills/watch/SKILL.md`, `README.md`), `skills/maker/SKILL.md` and `docs/briefs.md` say the same.
3. A picture proposal says so (#86). `accept_moves` says "The guardian proposes a change to the picture", not "the picture changed".
4. The maker and the scenario agent may read the picture (#88, #68). The maker may read `.xv/picture.md` and may not edit it. Its brief tells it to pull the binding decisions before it writes code. The scenario agent's brief gets the same line.
5. The watch may change the picture when a person directs it (#90). `skills/watch/SKILL.md` says "edit the pitch, or edit the picture unless a person directs it". The edit is its own commit, the message names the person who directed it, and the slice log records it. Accepting a picture change stays a person's.

This changes standing orders' words, a may-not list and several briefs, so `CHANGELOG.md` gets a line.

## May ignore

Rewording the site. Any stop for a check that cannot run (D7).

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T01:07:13+00:00 watch: slice opened by Sean Kennedy

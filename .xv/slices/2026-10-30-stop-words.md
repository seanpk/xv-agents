---
id: 2026-10-30-stop-words
title: "The stops, the briefs and the picture say what the method says"
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-stop-words
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 450000, "turns": null, "usd": 2.5, "basis": ["2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 260000, "turns": null, "usd": 3.25, "basis": ["2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}], "wall_s": 1400, "shape": "narrow", "breadth": "Wide across files (watch and maker skills, scenario and maker briefs, README, docs/briefs, CHANGELOG) but narrow in method: stop wording, no re-stop on an accepted shape change, and watch may edit the picture when directed; accept_moves and the picture rules have reopened before, so a reopen would push both keys toward the stop-decisions rows."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 2477, "cache_read": 25528, "cache_write": 18070, "tokens": 20551, "usd": 0.0051, "turns": 3, "wall_s": 12.5, "session": "36aa7b36-66ba-4521-be2a-375ef0a5dfb3", "step": "forecaster", "at": "2026-10-30T01:07:33+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-stop-words/01-forecaster.out"}]
stops: [{"at": "2026-10-30T01:07:33+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-stop-words budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~450k tokens and opus ~260k tokens, from the two same-key stop-rule rows; the stop-decisions reopen history is the main risk.", "at": "2026-10-30T01:07:33+00:00"}], "forecaster": {"at": "2026-10-30T01:07:33+00:00", "wrote": []}}
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
- 2026-10-30T01:07:33+00:00 forecaster: done: Forecast sonnet ~450k tokens and opus ~260k tokens, from the two same-key stop-rule rows; the stop-decisions reopen history is the main risk.
- 2026-10-30T01:07:33+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-stop-words budget ... --by <name>`).

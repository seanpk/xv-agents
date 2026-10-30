---
id: 2026-10-30-stop-words
title: "The stops, the briefs and the picture say what the method says"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-10-29
branch: xv/2026-10-30-stop-words
base: 5ec1d8640ff0da37a2634737f241cfd1a14821e2
next: maker
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 450000, "turns": null, "usd": 2.5, "basis": ["2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}, {"harness": "claude", "model": "opus", "tokens": 260000, "turns": null, "usd": 3.25, "basis": ["2026-10-29-stop-decisions", "2026-10-29-settled-forward"]}], "wall_s": 1400, "shape": "narrow", "breadth": "Wide across files (watch and maker skills, scenario and maker briefs, README, docs/briefs, CHANGELOG) but narrow in method: stop wording, no re-stop on an accepted shape change, and watch may edit the picture when directed; accept_moves and the picture rules have reopened before, so a reopen would push both keys toward the stop-decisions rows."}
budget: {"tokens": 1000000, "usd": 8, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_packet.py"], "command": "python3 -m unittest tests.test_packet", "failure": "AssertionError: Lists differ: [\"front matter shape_change must be yes or no, found 'accepted'\"] != []", "watch_first_green": "A packet with shape_change: accepted lints clean and does not stop the slice for two people again; one with shape_change: yes or pitch_contradiction: accepted is still refused or still stops. Watch that a slice with a shape beyond the accepted one gets marked yes by the guardian, not accepted."}
wall_baseline: {"commit": "71381bf1fcb9f591b7e0ed99246579e955c670f8", "count": 47, "digest": "572f08b9e7f9e5e9", "file": ".xv/slices/2026-10-30-stop-words.wall.json"}
moved_tests: []
slice_only: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 2477, "cache_read": 25528, "cache_write": 18070, "tokens": 20551, "usd": 0.0051, "turns": 3, "wall_s": 12.5, "session": "36aa7b36-66ba-4521-be2a-375ef0a5dfb3", "step": "forecaster", "at": "2026-10-30T01:07:33+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-stop-words/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 14, "tokens_out": 2415, "cache_read": 160150, "cache_write": 27513, "tokens": 29942, "usd": 0.1502, "turns": 8, "wall_s": 20.3, "session": "839f3b87-a927-4a3d-96de-9d6db2e94e8f", "step": "scenario", "at": "2026-10-30T01:16:02+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-stop-words/02-scenario.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 22, "tokens_out": 4468, "cache_read": 362617, "cache_write": 34457, "tokens": 38947, "usd": 0.2188, "turns": 14, "wall_s": 31.2, "session": "11a11d2a-9264-4c02-97b7-aea316de5057", "step": "scenario", "at": "2026-10-30T01:21:10+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-10-30-stop-words/03-scenario.out"}]
stops: [{"at": "2026-10-30T01:07:33+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-stop-words budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "A: Understood and budget prop accepted", "also": [], "options": [{"text": "$8 and 1M tokens", "settles": "The budget is $8 and 1M tokens: the forecast plus room for one send-back.", "amends": false}, {"text": "$5.75 and 710K tokens, the forecast", "settles": "The budget is $5.75 and 710K tokens, as forecast.", "amends": false}, {"text": "$11 and 1.4M tokens", "settles": "The budget is $11 and 1.4M tokens: room for several send-backs.", "amends": false}], "recommended": 1, "answered_at": "2026-10-30T01:15:42+00:00", "pick": 1, "settled": "The budget is $8 and 1M tokens: the forecast plus room for one send-back.", "new_info": "none", "cause": "decision: a budget is the person's", "budget_change": {"from": null, "to": {"tokens": 1000000, "usd": 8}}}, {"at": "2026-10-30T01:16:02+00:00", "step": "scenario", "order": "scenario_stopped", "seat": "originator", "question": "The scenario stopped (ambiguous_scenario): How should the watch tell that a shape change matches a decision already accepted on the same slice? (1) a shape_id slug in the packet front matter, recorded in the stop and compared; (2) shape_breadth equality with an answered shape_or_pitch stop, no new key; (3) the answerer marks the shape accepted at the stop and the watch skips while the packet is unchanged since that answer.", "answered_by": ["Sean Kennedy"], "answer": "A: 1", "also": [], "options": [{"text": "The guardian writes shape_change: accepted", "settles": "The guardian's packet may set shape_change to accepted when the slice's shape has nothing beyond a shape change already accepted in a decision record on this slice; it names that decision record. shape_or_pitch fires on yes, not on accepted. A shape beyond the accepted one is yes and still stops for two people.", "amends": true}, {"text": "xv saves the boundary when a shape is accepted", "settles": "When a shape_or_pitch stop is answered, xv saves the slice's boundary (modules and edges) on the record. On a later pass, shape_or_pitch fires only when the boundary has a module or edge not in the saved one, or the guardian names a shape change that is not in the boundary.", "amends": true}, {"text": "A shape id in the packet", "settles": "The guardian's packet names each shape change with a short id in its front matter. The answered stop keeps the ids, and a later shape_or_pitch fires only for an id not already accepted on this slice.", "amends": true}], "recommended": 1, "answered_at": "2026-10-30T01:20:39+00:00", "pick": 1, "settled": "The guardian's packet may set shape_change to accepted when the slice's shape has nothing beyond a shape change already accepted in a decision record on this slice; it names that decision record. shape_or_pitch fires on yes, not on accepted. A shape beyond the accepted one is yes and still stops for two people.", "new_info": "none", "cause": "watch: the scenario the watch drafted from #85 did not say how a match is told"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet ~450k tokens and opus ~260k tokens, from the two same-key stop-rule rows; the stop-decisions reopen history is the main risk.", "at": "2026-10-30T01:07:33+00:00"}, {"agent": "scenario", "status": "stopped", "summary": "Point 1 does not say how a shape change is recognised as matching an accepted decision; the record carries only shape_change yes/no.", "stop": {"reason": "ambiguous_scenario", "question": "How should the watch tell that a shape change matches a decision already accepted on the same slice? (1) a shape_id slug in the packet front matter, recorded in the stop and compared; (2) shape_breadth equality with an answered shape_or_pitch stop, no new key; (3) the answerer marks the shape accepted at the stop and the watch skips while the packet is unchanged since that answer."}, "at": "2026-10-30T01:16:02+00:00"}, {"agent": "scenario", "status": "red", "summary": "Packet lint refuses shape_change: accepted; the settled rule allows it for shape_change only.", "at": "2026-10-30T01:21:10+00:00"}], "forecaster": {"at": "2026-10-30T01:07:33+00:00", "wrote": []}, "scenario": {"at": "2026-10-30T01:21:10+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": "=========================================================\nERROR: test_packet (unittest.loader._FailedTest.test_packet)\n----------------------------------------------------------------------\nImportError: Failed to import test module: test_packet\nTraceback (most recent call last):\n  File \"/home/sean/.local/share/mise/installs/python/3.15.2/lib/python3.15/unittest/loader.py\", line 141, in loadTestsFromName\n    module = __import__(module_name)\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-10-30-stop-words/tests/test_packet.py\", line 5, in <module>\n    from helpers import HOME  # noqa: F401\n    ^^^^^^^^^^^^^^^^^^^^^^^^\nModuleNotFoundError: No module named 'helpers'\n\n\n----------------------------------------------------------------------\nRan 1 test in 0.000s\n\nFAILED (errors=1)\n", "old_red_changed": []}}
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

### Amended 2026-10-29 by Sean Kennedy

At the scenario agent's stop, Sean settled how an accepted shape is told apart (point 1):

The guardian's packet may set `shape_change` to `accepted` when the slice's shape has nothing beyond a shape change already accepted in a decision record on this slice; it names that decision record. `shape_or_pitch` fires on `yes`, not on `accepted`. A shape beyond the accepted one is `yes` and still stops for two people.

## May ignore

Rewording the site. Any stop for a check that cannot run (D7).

## Recording

None. A feature starts from words.

## Log
- 2026-10-30T01:07:13+00:00 watch: slice opened by Sean Kennedy
- 2026-10-30T01:07:33+00:00 forecaster: done: Forecast sonnet ~450k tokens and opus ~260k tokens, from the two same-key stop-rule rows; the stop-decisions reopen history is the main risk.
- 2026-10-30T01:07:33+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-10-30-stop-words budget ... --by <name>`).
- 2026-10-30T01:07:42+00:00 watch: offered 3 options for budget_not_set
- 2026-10-30T01:15:42+00:00 Sean Kennedy: set budget
- 2026-10-30T01:15:42+00:00 Sean Kennedy: answered budget_not_set: A: Understood and budget prop accepted
- 2026-10-30T01:15:42+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-10-30T01:16:02+00:00 scenario: stopped: Point 1 does not say how a shape change is recognised as matching an accepted decision; the record carries only shape_change yes/no.
- 2026-10-30T01:16:02+00:00 watch: stop (scenario_stopped) for originator: The scenario stopped (ambiguous_scenario): How should the watch tell that a shape change matches a decision already accepted on the same slice? (1) a shape_id slug in the packet front matter, recorded in the stop and compared; (2) shape_breadth equality with an answered shape_or_pitch stop, no new key; (3) the answerer marks the shape accepted at the stop and the watch skips while the packet is unchanged since that answer.
- 2026-10-30T01:17:06+00:00 watch: offered 3 options for scenario_stopped
- 2026-10-30T01:20:39+00:00 Sean Kennedy: answered scenario_stopped: A: 1
- 2026-10-30T01:20:39+00:00 watch: scribe: wrote settled, new_info, cause for scenario_stopped as the scribe of Sean Kennedy
- 2026-10-30T01:20:39+00:00 Sean Kennedy: amended the scenario
- 2026-10-30T01:21:10+00:00 scenario: red: Packet lint refuses shape_change: accepted; the settled rule allows it for shape_change only.

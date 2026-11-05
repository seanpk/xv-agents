---
id: 2026-11-04-promote-fields
title: Promotion copies only the fields that have text
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-04
branch: xv/2026-11-04-promote-fields
base: 168693608141b7cca549d5e56eebd4a61e9bd3fb
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 250000, "turns": null, "usd": 1.3, "basis": ["2026-10-27-retro-accept-fields", "2026-11-04-retro-sighting", "2026-11-04-proto-start"]}, {"harness": "claude", "model": "opus", "tokens": 200000, "turns": null, "usd": 2.3, "basis": ["2026-10-27-retro-accept-fields", "2026-11-04-retro-sighting", "2026-11-04-proto-start"]}], "wall_s": 1800, "shape": "narrow", "breadth": "Changes the field copy in promote.py local_accept and the from: insertion for sightings on an Open entry with no from: or added: line, plus tests; no other command or file expected to move."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3659, "cache_read": 15238, "cache_write": 37984, "tokens": 41647, "usd": 0.0096, "turns": 3, "wall_s": 18.2, "session": "606fa957-9152-4ab6-9aa8-2386cbad76f2", "step": "forecaster", "at": "2026-11-05T04:14:46+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-04-promote-fields/01-forecaster.out"}]
stops: [{"at": "2026-11-05T04:14:46+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-promote-fields budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "One clean pass per agent: claude/sonnet 250k tokens and $1.30, claude/opus 200k tokens and $2.30, about 1800 s wall; reopen risk unpriced.", "at": "2026-11-05T04:14:46+00:00"}], "forecaster": {"at": "2026-11-05T04:14:46+00:00", "wrote": []}}
---
# Promotion copies only the fields that have text

## Scenario

# Promotion copies only the fields that have text: #127

What happened: `xv promote local` writes `- miss:` and `- seen:` lines whatever the Open entry holds (`scripts/promote.py`, `local_accept`), and fills `miss:` from `said:` when the entry has no `miss:` line. An Open entry with an empty `miss:` line and a filled `said:` line was promoted to a rule with an empty `- miss: ` and no `said:` text, so the rule lost its reason. `miss:` (what went wrong) and `said:` (the person's words, quoted) are different fields in the learnings template. Separately, a sighting on an Open entry with no `from:` line and no `- added:` line puts the `from:` line after the `###` heading, and no test covers that.

Example, run on the code of PR #128. Before, in `.xv/learnings.md` under Open:

```
### 2026-10-20: A forecast runs low when answers at a stop add work
- added: 2026-10-20 by Sean Kennedy
- from: 2026-10-20-bulk-add, the budget stop
- miss:
- said: "the answer at the stop added two scenario points and nobody raised the budget"
- rule: when an answer adds work, raise the budget in the same answer
- seen: [xv-agents@2026-10-20, xv-agents@2026-10-27]
```

After promotion to a rule, in `.xv/rules.md`:

```
### when an answer adds work, raise the budget in the same answer
- added: 2026-11-04 by Sean Kennedy
- from: 2026-10-20-bulk-add, the budget stop
- miss: 
- seen: [xv-agents@2026-10-20, xv-agents@2026-10-27]
```

What should happen:

1. When `xv promote local` turns an Open entry into a standard or a rule, it copies every field that has text and leaves out every empty one. No field is filled from another field. Two fields change on the way: `rule:` becomes the heading, and `added:` gets today's date and the name of the person who promoted it.
2. Take a sighting on an Open entry that has no `from:` line and no `- added:` line. The `from:` line goes right after the `###` heading, with the candidate's slices. A test shows this.

## May ignore

Standards and rules already in .xv/standards.md and .xv/rules.md: the slice does not rewrite them. The two Open entries that have said: but no miss: the slice does not write their miss:. Sharing an entry with no miss: to other repos: xv promote keeps skipping it.

## Recording

None. A feature starts from words.

## Log
- 2026-11-05T04:14:23+00:00 watch: slice opened by Sean Kennedy
- 2026-11-05T04:14:46+00:00 forecaster: done: One clean pass per agent: claude/sonnet 250k tokens and $1.30, claude/opus 200k tokens and $2.30, about 1800 s wall; reopen risk unpriced.
- 2026-11-05T04:14:46+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-04-promote-fields budget ... --by <name>`).

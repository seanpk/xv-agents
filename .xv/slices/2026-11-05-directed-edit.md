---
id: 2026-11-05-directed-edit
title: "The watch makes a directed change the person approved (#132)"
kind: feature
status: working
set_by: Sean Kennedy
created: 2026-11-05
branch: xv/2026-11-05-directed-edit
base: 5d5e75fc7a7371d74a3884cfbae919785adbb4e7
next: scenario
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 430000, "turns": null, "usd": 2.8, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-11-04-retro-sighting", "2026-11-04-suite-speed"], "note": "guide has no turns column"}, {"harness": "claude", "model": "opus", "tokens": 270000, "turns": null, "usd": 3.2, "basis": ["2026-11-04-orders-home", "2026-11-04-refactor-kind", "2026-11-04-retro-sighting", "2026-11-04-suite-speed"], "note": "guide has no turns column"}], "wall_s": 4000, "shape": "wide", "breadth": "Watch stop option and directed-edit commit path, record rewrites for test renames (slice_only, wall_recommendations, covers), packet line for post-guardian edits, brief may-not line, and a CHANGELOG line; wide across watch, record and brief."}
budget: {"tokens": 850000, "usd": 6.5, "set_by": "Sean Kennedy"}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 4539, "cache_read": 26146, "cache_write": 30029, "tokens": 34572, "usd": 0.0085, "turns": 3, "wall_s": 21.7, "session": "8733534d-8174-4a5e-8fc0-6218efa8415b", "step": "forecaster", "at": "2026-11-05T10:40:55+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-05-directed-edit/01-forecaster.out"}]
stops: [{"at": "2026-11-05T10:40:55+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-directed-edit budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "Do 3. But since it's wide, let's have an opus agent do the scenario (same plan as F)", "also": [], "options": [{"text": "430,000 tokens, $3.20: the forecast as it is", "settles": "budget is 430k tokens / $3.20", "amends": false}, {"text": "600,000 tokens, $4.50: the forecast plus room for one send-back", "settles": "budget is 600k tokens / $4.50", "amends": false}, {"text": "850,000 tokens, $6.50: room for two send-backs", "settles": "budget is 850k tokens / $6.50", "amends": false}], "recommended": 2, "answered_at": "2026-11-05T10:43:12+00:00", "pick": 3, "settled": "budget is 850k tokens / $6.50", "new_info": "the scenario agent runs on Opus for this slice only, by a config line removed before the PR", "cause": "decision: wide shape, budget with room for two send-backs"}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast from four wide claude rows: sonnet about 430k tokens and $2.80, opus about 270k tokens and $3.20; reopens at accept_moves or shape stops are the main risk.", "at": "2026-11-05T10:40:55+00:00"}], "forecaster": {"at": "2026-11-05T10:40:55+00:00", "wrote": []}}
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
- 2026-11-05T10:40:55+00:00 forecaster: done: Forecast from four wide claude rows: sonnet about 430k tokens and $2.80, opus about 270k tokens and $3.20; reopens at accept_moves or shape stops are the main risk.
- 2026-11-05T10:40:55+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-05-directed-edit budget ... --by <name>`).
- 2026-11-05T10:41:05+00:00 watch: offered 3 options for budget_not_set
- 2026-11-05T10:43:12+00:00 Sean Kennedy: answered budget_not_set: Do 3. But since it's wide, let's have an opus agent do the scenario (same plan as F)
- 2026-11-05T10:43:12+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-05T10:43:12+00:00 Sean Kennedy: set budget

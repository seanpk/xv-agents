---
id: 2026-11-02-own-the-result
title: Briefs lead with Own the result
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-02
branch: xv/2026-11-02-own-the-result
base: 3e5bf091aa27720b9f9374f3f2f9dba05888d1e1
next: forecaster
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 53000, "turns": null, "usd": 0.3, "basis": ["2026-10-30-readback", "2026-10-27-package-imports", "2026-10-27-init-rerun"], "note": "Scenario, maker and cleaner. Median of three clean single-pass rows. The guide has no turn counts."}, {"harness": "claude", "model": "opus", "tokens": 35000, "turns": null, "usd": 0.4, "basis": ["2026-10-30-readback", "2026-10-27-package-imports", "2026-10-27-init-rerun"], "note": "Guardian. Median of three clean single-pass rows. The guide has no turn counts."}], "wall_s": 350, "shape": "narrow", "breadth": "Wording only: 15 brief opener lines, docs/briefs.md, .xv/picture.md item 13, CHANGELOG, three CI pins and README version mentions; no change to what any agent does."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "haiku", "tokens_in": 0, "tokens_out": 0, "cache_read": 0, "cache_write": 0, "tokens": 0, "usd": 0.0, "turns": 1, "wall_s": 0.4, "session": "86c33c73-5148-4613-9795-2306ece83af4", "step": "forecaster", "at": "2026-11-02T20:56:03+00:00", "exit": 1, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-02-own-the-result/01-forecaster.out"}, {"harness": "claude", "model": "haiku", "model_id": "haiku", "tokens_in": 0, "tokens_out": 0, "cache_read": 0, "cache_write": 0, "tokens": 0, "usd": 0.0, "turns": 1, "wall_s": 0.4, "session": "b562c554-2d91-468d-be56-a04334fff8d3", "step": "forecaster", "at": "2026-11-02T21:03:05+00:00", "exit": 1, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-02-own-the-result/02-forecaster.out"}, {"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 4, "tokens_out": 3956, "cache_read": 25640, "cache_write": 23998, "tokens": 27958, "usd": 0.007, "turns": 3, "wall_s": 19.6, "session": "07e0950c-c0b9-4b7d-a1c4-4331fc43e0ba", "step": "forecaster", "at": "2026-11-02T21:10:03+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-02-own-the-result/03-forecaster.out"}]
stops: [{"at": "2026-11-02T20:56:03+00:00", "step": "forecaster", "order": "no_report", "seat": "originator", "question": "The forecaster ended without a report. Read its log and decide whether to re-run it.", "answered_by": ["Sean Kennedy"], "answer": "try to run with claude again", "also": ["budget_not_set"], "options": [{"text": "Re-auth Claude Code, then re-run the forecaster", "settles": "Sean refreshes the Claude OAuth session; the watch re-runs xv step forecaster 2026-11-02-own-the-result.", "amends": false}, {"text": "Skip the CLI forecaster: Sean sets a budget from a rough estimate now", "settles": "Sean sets the budget himself without a forecast report; next is scenario. The forecaster no_report stop is answered by going to scenario with a person-set budget.", "amends": false}, {"text": "Set aside until Claude auth works", "settles": "The slice stays open at next: forecaster; no further step runs until Sean says so.", "amends": false}], "recommended": 1, "answered_at": "2026-11-02T21:03:04+00:00", "pick": 1, "settled": "Sean refreshes the Claude OAuth session; the watch re-runs xv step forecaster 2026-11-02-own-the-result.", "new_info": "none", "cause": "environment: Claude OAuth had expired; retry after re-auth"}, {"at": "2026-11-02T21:03:05+00:00", "step": "forecaster", "order": "no_report", "seat": "originator", "question": "The forecaster ended without a report. Read its log and decide whether to re-run it.", "answered_by": ["Sean Kennedy"], "answer": "oh, you have to run it through claude-sk set the path to ~/.claude-sk", "also": ["budget_not_set"], "options": [{"text": "Sean runs claude auth login (or equivalent), then re-run the forecaster", "settles": "Sean refreshes Claude OAuth locally; the watch re-runs xv step forecaster.", "amends": false}, {"text": "Run this slice's steps as Cursor session subagents (no config change): xv prompt, subagent, xv record report, xv orders", "settles": "Workers for this slice run in Cursor fresh contexts via the session path without editing .xv/config.yml; start with the forecaster that way, then budget_not_set.", "amends": false}, {"text": "Set aside until Claude auth works", "settles": "The slice stays open at next: forecaster; no further step runs until Sean says so.", "amends": false}], "recommended": 1, "answered_at": "2026-11-02T21:09:43+00:00", "pick": 1, "settled": "Sean refreshes Claude OAuth locally; the watch re-runs xv step forecaster.", "new_info": "use CLAUDE_CONFIG_DIR=~/.claude-sk (claude-sk) for xv step on this machine", "cause": "environment: default Claude config dir had expired OAuth; ~/.claude-sk is valid"}, {"at": "2026-11-02T21:10:03+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-02-own-the-result budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "no-report", "summary": "ended without an xv-report block"}, {"agent": "forecaster", "status": "no-report", "summary": "ended without an xv-report block"}, {"agent": "forecaster", "status": "done", "summary": "Text-only reword of 15 brief openers and docs; forecast from three clean single-pass rows per key (sonnet ~53k tokens, opus ~35k), with reopen risk unpriced.", "at": "2026-11-02T21:10:03+00:00"}], "forecaster": {"at": "2026-11-02T21:10:03+00:00", "wrote": []}}
---
# Briefs lead with Own the result

## Scenario

# Briefs lead with Own the result (#107)

When this is done, someone checking out the repo sees:

1. Each of the 15 brief openers names Own the result first, then keeps the stop line — form: `Own the result: even when agents write all of the code, a person is responsible for what it does. An agent may stop. It may not decide.` plus any agent-specific rest that was already there. The "The one rule:" label is gone from those openers.
2. `docs/briefs.md` ("Every brief") and `.xv/picture.md` item 13 say the same: Own the result opens each brief; the stop line stays.
3. `CHANGELOG.md` has a line for the reword that names who agreed it (#107).
4. The three CI example pins and the README checkout/pin mentions that still say `v0.4.0` say `v0.4.1`.

## May ignore

The Go-and-see third stop and scripts/orders.py; renaming the README The one rule section; cutting the actual v0.4.1 git tag (person does that after merge); other open issues.

## Recording

None. A feature starts from words.

## Log
- 2026-11-02T20:55:58+00:00 watch: slice opened by Sean Kennedy
- 2026-11-02T20:56:03+00:00 forecaster: ended without an xv-report block
- 2026-11-02T20:56:03+00:00 watch: stop (no_report) for originator: The forecaster ended without a report. Read its log and decide whether to re-run it.
- 2026-11-02T20:56:15+00:00 watch: offered 3 options for no_report
- 2026-11-02T21:03:04+00:00 Sean Kennedy: answered no_report: try to run with claude again
- 2026-11-02T21:03:04+00:00 watch: scribe: wrote settled, new_info, cause for no_report as the scribe of Sean Kennedy
- 2026-11-02T21:03:05+00:00 forecaster: ended without an xv-report block
- 2026-11-02T21:03:05+00:00 watch: stop (no_report) for originator: The forecaster ended without a report. Read its log and decide whether to re-run it.
- 2026-11-02T21:08:24+00:00 watch: offered 3 options for no_report
- 2026-11-02T21:09:43+00:00 Sean Kennedy: answered no_report: oh, you have to run it through claude-sk set the path to ~/.claude-sk
- 2026-11-02T21:09:43+00:00 watch: scribe: wrote settled, new_info, cause for no_report as the scribe of Sean Kennedy
- 2026-11-02T21:10:03+00:00 forecaster: done: Text-only reword of 15 brief openers and docs; forecast from three clean single-pass rows per key (sonnet ~53k tokens, opus ~35k), with reopen risk unpriced.
- 2026-11-02T21:10:03+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-02-own-the-result budget ... --by <name>`).

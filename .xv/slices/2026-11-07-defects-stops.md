---
id: 2026-11-07-defects-stops
title: "A red that cannot run stops the slice, and an answered stop stays answered"
kind: defect
status: stopped
set_by: Sean Kennedy
created: 2026-11-07
branch: xv/2026-11-07-defects-stops
base: 1f325dd57c3e12eef670800ea39d10166aa2b4fa
next: forecaster
build: {"kind": "exploration", "ref": "explore/defects-stops"}
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 500000, "turns": null, "usd": 2.9, "basis": ["2026-11-07-picture-lines", "2026-11-05-directed-edit", "2026-10-30-stop-words", "2026-10-29-red-covers-scenario"], "note": "Mean of the four basis rows is about 484k tokens and $2.86. Rows run 361k to 570k tokens and $2.15 to $3.36. No turns column in the guide. The picture-lines row shows the re-fire this slice fixes, so the forecast keeps one reopen band."}, {"harness": "claude", "model": "opus", "tokens": 300000, "turns": null, "usd": 3.5, "basis": ["2026-11-07-picture-lines", "2026-11-05-directed-edit", "2026-10-30-stop-words", "2026-10-29-red-covers-scenario"], "note": "Rows run 177k to 1,007k tokens and $2.14 to $12.86. The 1,007k and $12.86 row ran its scenario on opus, which this slice does not do, so the forecast sits near the median of the rest. Guardian passes are the cost driver: each accept_moves send-back reruns one."}], "wall_s": 3000, "shape": "narrow", "breadth": "The scenario step's red check and the stop-answer re-fire path, plus the decision 12 picture and a CHANGELOG line. Tests move with it, but the source change should stay in a few files."}
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
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 3443, "cache_read": 62155, "cache_write": 36538, "tokens": 39987, "usd": 0.0097, "turns": 4, "wall_s": 17.3, "session": "fac7ee36-edb4-457e-ad62-d2b652022c94", "step": "forecaster", "at": "2026-11-07T20:07:10+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-07-defects-stops/01-forecaster.out"}]
stops: [{"at": "2026-11-07T20:07:10+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-defects-stops budget ... --by <name>`).", "answered_by": [], "answer": null, "also": [], "budget_seen": null}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast claude/sonnet ~500k tokens, $2.9, ~2400 s; claude/opus ~300k tokens, $3.5. Shape narrow, reopen risk unpriced in the fix itself.", "at": "2026-11-07T20:07:10+00:00"}], "forecaster": {"at": "2026-11-07T20:07:10+00:00", "wrote": []}}
---
# A red that cannot run stops the slice, and an answered stop stays answered

## Scenario

1. A red that fails before any test runs is not a failing red. This means exit code 126 or 127, or the runner's own words that a test file could not load or that no tests were found. The scenario step stops with `red_cannot_run` for the person who set the work going, naming the error, and `next` stays `scenario`.
2. The runner words cover all 11 runners that `failing_tests` reads. A general error name (`ImportError`, `No such file or directory`) counts only when the output names no real failing test.
3. A red that runs its tests and some fail is a failing red, as now, even when its output prints a general error name.
4. When one test file cannot load and other tests fail for real, the step still stops.
5. An answer that bundles `slice_only_marks` accepts the slice-only marks, the same as an answer to that stop does.
6. After a directed edit, the stop the answer closed does not fire again, and neither does any stop bundled with it. This includes `ready_to_merge`. The answer's `--next` stands. Checks the edit can change, such as the suite, still run.
7. Decision 12 in the picture names a red that cannot run.
8. A `CHANGELOG.md` line names the new stop and the two fixes.
9. `EXPLORE-NOTES.md` is not in what merges.

## May ignore

- Runners other than the 11 that failing_tests reads.
- Runner output in a language other than English, or words that change when a runner is upgraded. A learnings note covers the upgrade case.
- A red that hangs or times out.
- The defects-tools items (#147, #148, #154). They have their own slice.

## Recording

.xv/recordings/2026-11-07-directed-edit-refire.md

## Log
- 2026-11-07T20:06:40+00:00 watch: slice opened by Sean Kennedy
- 2026-11-07T20:07:10+00:00 forecaster: done: Forecast claude/sonnet ~500k tokens, $2.9, ~2400 s; claude/opus ~300k tokens, $3.5. Shape narrow, reopen risk unpriced in the fix itself.
- 2026-11-07T20:07:10+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-defects-stops budget ... --by <name>`).

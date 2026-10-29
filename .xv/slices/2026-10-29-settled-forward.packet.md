---
slice: 2026-10-29-settled-forward
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: none
moved_tests: 1
door: two-way
blast_radius: contained
---

# Packet: Some stops ask for --settled when the answer moves the slice forward

No two-person stop. The originator needs to decide three things: (a) the new rule is wider than the scenario's point 2 and lets a budget stop raised *after* the maker through; (b) it also lets through a `setup_failed` stop raised after the scenario agent ran, and the two-person `prototypes_ready` pick; (c) the README line, the watch brief and the picture still state the old `--settled` rule. The merge is the originator's.

## The scenario

From `.xv/slices/2026-10-29-settled-forward.md` (#82):

1. When a setup fails (`setup_failed`) or a prototype stops, the work has not started, so any `--next` moves forward. No `--settled` is needed.
2. A budget stop raised before its step ran is the same: `--next <that step>` moves forward and needs no `--settled`.
3. `xv record stop` takes `--step`, and the tests use it. They no longer edit the record text to add a step.
4. A test runs the README's general answer line (`README.md:295`), not only its words.

May ignore: `cmd_answer` is 68 lines, and two test lines read `p =self.xv`. Those are the cleaner's to handle under the standards.

## The recording

None (a feature). Replay the red and the green with `cd tests && python3 -m unittest test_record.SettledForwardTest test_record.FifthAmendmentTest`. Before the change: 9 of 12 fail with `xv record: error: unrecognized arguments: --step scenario` (record `checks.scenario.red_output`). After: 12 tests OK (run by the guardian). The record says the whole suite ran green (387 OK) after the maker and again after the cleaner.

## The boundary picture

From `.xv/slices/2026-10-29-settled-forward.boundary.md`, as given: touched `scripts/record`; modules added/removed none; edges added/removed none; new outbound calls none; tables none; surface paths none; shape hints none.

## What the suite asserts after

- `xv record stop --step <s>` saves `step` on the stop.
- A `setup_failed` stop answered `--next forecaster` or `--next scenario` without `--settled` succeeds, and `next` moves there.
- A stop at step `prototype` (`axis_not_named`) answered `--next scenario` without `--settled` succeeds.
- A `budget_spent` stop at `maker` answered `--next maker` succeeds without `--settled`. Answered `--next scenario`, it still needs `--settled`.
- A `scenario_stopped` stop at `maker` answered `--next maker` still needs `--settled`.
- The README's general answer line runs once its placeholders are filled, on a `scenario_stopped` stop at `scenario` with `--next maker`.
- Moved: `FifthAmendmentTest.stop_saved_at` now sets the step with `--step` instead of editing the record text (see 3).

## 1. Shape

shape_change: no. shape_breadth: none.

- The boundary picture shows one touched module (`scripts/record`), with no new edges, tables, surfaces or shape hints. The diff stays inside `record.py`: one optional CLI flag at `scripts/record.py:634` (`s.add_argument("--step", ...)`), one stored key at `scripts/record.py:223-224`, and one condition at `scripts/record.py:298-301`. The picture names `record` as the owner of the slice record (`.xv/picture.md:19` section, "`record` owns the slice record"). The change stays within that shape. The forecast said `narrow`, and this is no wider.
- `xv record stop --step` adds a flag to an existing command on the `xv` CLI surface (`.xv/picture.md`, "Surfaces: the `xv` CLI"). It adds no new command, so it is not a new surface.

## 2. Pitch

pitch_contradiction: no.

- I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). The change drops a person's `--settled` line only where the scenario says no work has run. It adds no new user or purpose. The pitch says nothing about when `settled` is required.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` `FifthAmendmentTest.stop_saved_at` (helper) | `record stop` without a step, then `assertIn('{"at":', text)` on the raw record, rewrites the text to insert `"step"`, then `assertEqual(show()["stops"][-1]["step"], step)` | `record stop ... --step step`, then the same `assertEqual(... ["step"], step)` | "Forced by point 3 of the scenario: tests no longer edit the record text to add a step. Settled by Sean Kennedy at red_check." | Yes. Point 3 says the tests "no longer edit the record text to add a step". The only assertion dropped is the `assertIn('{"at":'` precondition for the text edit, which no longer exists. The behavioural assertion on `step` is kept, so the helper asserts no less. |

- `xv wall diff 2026-10-29-settled-forward` reports `changed: []`. Its baseline `884fa7c` comes before the move: `git diff --stat 884fa7c..HEAD -- tests` shows `tests/test_record.py | 7 +------`, from commit `de57f38`, which also rewrote `.xv/slices/2026-10-29-settled-forward.wall.json` (6 lines). So the wall's digest was retaken after the move, and the record's `moved_tests` entry is the only trace of it. The move is recorded, so nothing is unrecorded. Note that the wall did not catch this one.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

- `.xv/picture.md:26` says "it must carry `settled` when `--next` is the stop's saved step or an earlier one, or when the pick is `other`." After `scripts/record.py:298-301` that is no longer true for `setup_failed`, for any stop at step `prototype`, or for `budget_spent` with `--next` equal to its step. Proposed edit: add "except a stop raised before its work started (`setup_failed`, a prototype stop, or a budget stop answered `--next` its own step), which needs no `settled` for any `--next`."
- `.xv/picture.md:26` also says "A decision file and its `decisions` entry keep `settled` with the person's words." See finding (b-2) below: a `prototypes_ready` pick can now carry no `settled`. Adjust that sentence to match whatever the originator decides on (b-2).

## Findings for the originator

**(a) The budget rule covers more than the scenario's point 2.** The scenario says "A budget stop raised *before its step ran*." The code has no before-or-after test:

```
scripts/record.py:299-300
+    not_started = (stop["order"] == "setup_failed" or stop.get("step") == "prototype"
+                   or (stop["order"] == "budget_spent" and a.next == stop.get("step")))
```

The after-maker check also fires `budget_spent` (`scripts/orders.py:131-136`, `if after == "maker": ... fire("budget_spent", ...)` "and the suite is not green"). `scripts/run.py:391-394` saves it with `"step": agent` (= `maker`) and keeps `next` on `maker`. So once the maker has run and left the suite red, `--next maker` reruns the maker with no `settled`. That is a send-back to the step that stopped, which the rule exists to catch (`CHANGELOG.md:7`: "`--settled` is required only when `--next` sends the work back (to the step that stopped or an earlier one)"). No test covers the after-maker case. The two kinds can be told apart: the pre-step stop at `scripts/run.py:342` has no `budget_seen`, and the post-step stop at `scripts/run.py:394-397` has one. The record's forecast breadth also said "pre-step budget stops".

**(b-1) `setup_failed` is not always raised before work starts.** Point 1's reason is "the work has not started yet". That is true for the worktree setup (`scripts/run.py:263`, `"step": "setup"`). But `scripts/orders.py:107-109` also fires `setup_failed` `if after == "scenario"`, when the red check could not run (`old_red_unchecked`, or `checks["setup_failed"]` from `scripts/run.py:451`). That stop is saved at step `scenario`, after the scenario agent has written tests. Under the new rule, `--next scenario` or `--next forecaster` from that stop needs no `settled`. The scenario's words ("`setup_failed`") allow this; its reason does not. The originator should say which they meant.

**(b-2) A two-person prototype pick no longer needs `settled`.** `stop.get("step") == "prototype"` matches every stop `scripts/prototypes.py:197` writes, including `prototypes_ready` (`scripts/orders.py:228`, seat `two_people`). Before, `stopped_at = "prototype"` is not in `STEPS` (`scripts/record.py:33`), so any `--next` counted as a send-back and needed `settled`. Now a two-person pick answered without `--pick` and without `--settled` records no `settled`. That contradicts `.xv/picture.md:26` ("A decision file and its `decisions` entry keep `settled` with the person's words"). Point 1 does say "a prototype stops", so this may be intended. No test covers `prototypes_ready`.

**(c) The written rule now trails the code.** `README.md:295` still says "`--settled` is required when `--next` sends the work back to the step that stopped or earlier", and so does the watch brief at `skills/watch/SKILL.md:50`. Neither names the new exceptions, and the diff touches neither file. `CHANGELOG.md:7` records the #80 rule as "a standing order's effect" that changed two briefs. This slice relaxes it with no CHANGELOG line. `.xv/picture.md:61` (decision 1): "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`." Whether the `--settled` check is one of those is for the originator to say. The repo runs solo (`.xv/picture.md`, "a one-person team (`seats.two_people: solo`)").

**(d) Point 4's test exercises the line weakly.** `tests/test_record.py:862-872` runs the README line on a `scenario_stopped` stop at `scenario` with `--next maker`. That is a forward move, which needed no `settled` even before this slice. It proves the line parses and runs, which is what point 4 asks. It does not exercise the line's `--settled` clause.

## Door

**Door:** two-way. Reverting `scripts/record.py` undoes it. Stops already saved with `step` keep a key the code already reads (`stop.get("step")`). **Blast radius:** contained.

## Raw data

- Slice record: `.xv/slices/2026-10-29-settled-forward.md`
- Diff: `git diff cafedce2750c9b8bfed996553f0f139df2563608..e9ecba8`
- Wall: `xv wall diff 2026-10-29-settled-forward` (baseline `884fa7c`, which comes before the move, see 3)
- Boundary: `.xv/slices/2026-10-29-settled-forward.boundary.md` (`xv boundary --base cafedce2750c9b8bfed996553f0f139df2563608`)

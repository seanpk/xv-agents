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

Second pass, after the amendment. No two-person stop. The originator decides two things. (a) In the watch's own flow the `budget_spent` exception never fires: `xv record offer` writes `budget_seen` onto the stop, and the code uses a missing `budget_seen` to spot the stop raised before its step ran (finding 1.1). (b) `prototype_budget_spent` is raised after variants ran, yet it passes as "work not started" (finding 1.2). The picture also still states the old rule (section 4). The merge is the originator's.

## The scenario

Issue #82. As amended on 2026-10-29 by Sean Kennedy at the accept_moves stop: `xv record answer` needs no `--settled` for stops raised before any work of their step started. Those are a `setup_failed` stop saved at step `setup`; a prototype stop other than `prototypes_ready`; and a `budget_spent` stop raised before its step ran, answered with `--next` that step. Three stops keep the rule: `setup_failed` raised after the scenario step, the `prototypes_ready` pick, and the budget stop raised after the maker left the suite red. `xv record stop` takes `--step`, and tests use it instead of editing the record text. A test runs the README's general answer line. README.md:295, the watch brief and the picture name the exceptions, and CHANGELOG.md has a line for them.

May ignore: `cmd_answer` is 68 lines, and two test lines read `p =self.xv`.

## The recording

None (a feature). To replay: `cd tests && python3 -m unittest test_record.SettledForwardTest`. Red at `0098722` plus the scenario's second red: 10 of 11 failed (record `checks.scenario.red_output`). Green now: 16 of 16 in `SettledForwardTest` and `FifthAmendmentTest`. Whole suite: `Ran 391 tests ... OK` (run by me this pass).

## The boundary picture

From `.xv/slices/2026-10-29-settled-forward.boundary.md`, as given: touched `scripts/record`. No modules, edges, outbound calls, tables or surface paths added or removed. Shape hints: none.

## What the suite asserts after

- `xv record stop --step <s>` saves `step` on the stop.
- `setup_failed` at step `setup` goes to `forecaster` or `scenario` with no `--settled`. A prototype stop (`axis_not_named`) goes to `scenario` with no `--settled`.
- A real pre-step budget stop, raised by `xv step maker` with the budget spent, goes to `maker` with no `--settled`. Going to `scenario` still needs it.
- The rule still holds for `budget_spent` saved at `maker` by `record stop`, `setup_failed` at `scenario`, `prototypes_ready` going to `scenario`, and `scenario_stopped` at `maker`.
- The README answer line, the watch brief and a CHANGELOG line name `setup_failed`, `budget_spent` and `prototypes_ready`. The README answer line runs with its placeholders filled.
- Moved: `FifthAmendmentTest.stop_saved_at` now sets the step with `--step` (section 3).

## 1. Shape

shape_change: no. shape_breadth: none.

- The boundary picture shows one touched module and no new edge, table or surface (`.xv/slices/2026-10-29-settled-forward.boundary.md`, "Edges: added: none"). A new flag on an existing command sits inside the `xv` CLI surface (`.xv/picture.md:27`): `scripts/record.py:637` `+    s.add_argument("--step", help="the step the stop was raised at")`. This is inside the current shape, as the forecast expected ("narrow", record `forecast.shape`).

Findings for the originator. These are not shape changes.

- **1.1 In the prescribed flow, the `budget_spent` exception is dead.** `scripts/record.py:298-303`:
  ```
  +    # ... the watch's
  +    # pre-step budget stop is the one budget_spent stop saved without budget_seen
  +                   or (stop["order"] == "budget_spent" and "budget_seen" not in stop
  ```
  But `xv record offer` adds the field to every open stop: `scripts/record.py:262` `stop.setdefault("budget_seen", data.get("budget"))`. The watch brief says to offer before ending its turn on any stop (`skills/watch/SKILL.md:34-38`, "Before you end your turn on a stop, put the choices on the record: xv record offer ..."). So in the real flow it goes: the pre-step stop (`scripts/run.py:341`), then the offer, which writes `budget_seen`, then `record answer --next maker`. At the answer `not_started` is False and `sends_back` is True, so `--settled` is required. The test never offers (`tests/test_record.py` `stop_before_step`, then `answer`), so it passes. In practice `--pick <n>` fills `settled` from the option (`scripts/record.py:294`), so nobody is blocked today. The exception works only when no offer was made, and the code comment is untrue after an offer.
- **1.2 `prototype_budget_spent` counts as "not started".** The code passes any prototype stop but `prototypes_ready`: `scripts/record.py:301` `+                   or (stop.get("step") == "prototype" and stop["order"] != "prototypes_ready")`. That matches the amendment's list ("a prototype stop other than `prototypes_ready`"). But `prototype_budget_spent` is raised at step `prototype` after the variants ran (`scripts/prototypes.py:197`, `scripts/orders.py:220`: "ran out of its budget during its run"). That is work started, against the amendment's own rule ("only for stops raised before any work of their step started") and the README's reason ("because their work has not started", `README.md:295`). Its answer, a budget raise and then a rerun, now needs no `--settled`. The originator says which reading holds.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing ... to vibe with discipline") and `.xv/pitch.md:25` (not for people who will not trust agents to write production code). The change loosens one record check for three stop kinds. It does not change who the system serves or what it is for. The pitch says nothing about `--settled`.

Binding decision 1 (`.xv/picture.md:61`) needs a CHANGELOG line for a change to a brief or a check. One was added: `CHANGELOG.md:9` "+- Some stops need no `--settled` ... This changes the watch's brief and a check; Sean decided it, solo (#82)". Solo is the declared seat (`.xv/picture.md:53`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:760` `FifthAmendmentTest.stop_saved_at` | Wrote the step into the record text by `text.replace('{"at":', '{"step": ...')`, plus `assertIn('{"at":', text)` | `record stop ... --step step`; still asserts `stops[-1]["step"] == step` | "Forced by point 3 of the scenario: tests no longer edit the record text to add a step. Settled by Sean Kennedy at red_check." | Yes. Point 3 asks for it word for word. The dropped `assertIn` only guarded the text edit, so nothing about behaviour is asserted less. Sean accepted the move at accept_moves. |

`xv wall diff` shows no changed, deleted or added old tests against its baseline `0098722`, which already includes this move. The move shows only in `git diff cafedce..HEAD`, and the record has it. No unrecorded change, and no test asserts less.

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- `.xv/picture.md:26` ends "...it must carry `settled` when `--next` is the stop's saved step or an earlier one, or when the pick is `other`." That is now incomplete, and the amended scenario asks the picture to name the exceptions. Proposed edit: append "except for stops raised before their work started: `setup_failed` saved at step `setup`, a prototype stop other than `prototypes_ready`, and a `budget_spent` stop raised before its step ran, answered with `--next` that step (#82)." Adjust it to whatever the originator decides on 1.1 and 1.2.
- `.xv/picture.md:26` (or `:23`, for `record`) could also note that `xv record stop` takes `--step`, as `xv step` does when it saves a stop.

## Door

**Door:** two-way: the change touches no data and no public contract beyond one added optional flag, and a revert undoes it. **Blast radius:** contained.

## Raw data

- Slice record: `.xv/slices/2026-10-29-settled-forward.md`
- Diff: `git diff cafedce2750c9b8bfed996553f0f139df2563608..48780a8`
- Wall: `xv wall diff 2026-10-29-settled-forward`
- Boundary: `xv boundary --base cafedce2750c9b8bfed996553f0f139df2563608`

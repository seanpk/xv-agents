---
slice: 2026-10-27-prototype-budgets
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: prototypes
---

# Packet: A prototype that runs out of budget comes back to a person (third pass)

This is the third pass. Everything Sean settled at the second stop (B, C, D and the small points) is in the code, and a test covers each one. There is no shape change and no pitch contradiction, so nothing here goes to two people. Sean decides two things:

- **The picture edit in section 4.**
- **The flaky test, for the record.** The watch stopped once with `cleaner_broke_suite` (`.xv/slices/2026-10-27-prototype-budgets.md:69`): `test_a_variant_that_ran_out_sends_the_slice_back_to_the_person_who_set_it_going` failed, and passed on the rerun. The cleaner saw that variant b's cap was missing (`:71`). I reran the whole suite: 312 OK. A likely cause, not proven: the three variant threads (`scripts/prototypes.py:124-128`) run `git branch -D` and `git worktree add` in the same repo at the same moment (`:50-51`, the second with `check=True`). If one of them fails, that thread dies before it calls the agent and leaves nothing in `out`. The variant then shows "No recording", and `:180-181` (`if n not in out: continue`) leaves it out of `ran_out`. Base ran the threads the same way, so this is not new. With this slice, though, a later start reruns that variant (B). Sean answered the stop "ok" and asked for priority on the issue that speeds up the suite.

Done since the second packet:

- **B.** A variant counts as finished only when it has a recording and did not run out (`scripts/prototypes.py:119`, `kept = {n ... if (prev.get(n) or {}).get("recording") and n not in prev_out}`). A new `--axis` keeps none (`:83`, `:117-118`). Tests: `test_a_second_start_reruns_a_variant_that_ran_within_budget_but_left_no_recording` and `test_a_second_start_with_a_new_axis_reruns_all_three_and_keeps_none`.
- **C.** The stop now says "ran out of its budget during its run" or "was not run" (`scripts/orders.py:207-209`, from `ran_during`, `scripts/prototypes.py:189`). Test: `test_the_stop_words_a_run_out_during_the_run_and_one_already_over_at_the_start_apart`.
- **D.** The stop stays seated `originator` (`scripts/orders.py:214`). It now says that a budget raise is answered alone, and that a pick, `none` included, is for two people unless the repo runs solo. `pick` keeps its two-people rule (`scripts/prototypes.py:220-222`, unchanged). Tests: `test_the_person_who_set_it_going_answers_a_budget_raise_alone` and `test_the_stop_says_a_pick_is_for_two_people_unless_the_repo_runs_solo`.
- **Small.** The stop says "answer this stop, and then run `xv prototype start`" (`scripts/orders.py:215-216`). The log line now reads "a pick is for two people unless the repo runs solo" (`scripts/prototypes.py:204`). The test comment is corrected (`tests/test_budget_cap_turns_session.py`, last comment line). Each one has a test.

Still open from the second packet, for the record only:

- A pick made from the budget stop is still written to the decision record under the order `prototypes_ready` (`scripts/prototypes.py:244`).
- A rerun variant starts again from HEAD (`scripts/prototypes.py:51`), with only the dollars left in its budget (`:59`; the tests expect 1.95 and 1.8 of 3).
- The cleaner's proposal: the over-budget check is written twice (`scripts/prototypes.py:120-121` and `:185`).
- `xv record answer` closes an `originator` stop with any one name (`scripts/record.py:236`, where only `two_people` is checked). The alone test answers as "pat" and does not check that pat set the work going. This holds for every originator stop, not only this one.

## The scenario

Sean's words: "whenever a prototype runs out of budget, it should come back to you for a decision. you cannot pick anything if no prototype was built, but you should be able to stop the prototype exploration."

- When a variant has spent its budget, before the start or during its own run, the others still run. Then `prototype_budget_spent` stops for the originator, naming each variant that ran out and what it spent.
- The choices are: raise its budget, answer, and start again; pick a variant that finished; or pick `none`. A variant that ran out cannot be picked. When all three ran out, `none` is the only pick.
- A variant has finished when it has a recording and did not run out. A second start reruns every variant that has not finished and keeps the finished ones. A new `--axis` keeps none.
- `prototype_budgets_not_set` is raised by `scripts/orders.py`. This changes standing orders. Sean decided it, solo, and it has a CHANGELOG line (`CHANGELOG.md:7`).

May ignore: nothing stated.

## The recording

None; this is a feature. To replay it, run `cd tests && python3 -m unittest test_budget_cap_turns_session.PrototypeBudgetsTest`. The guardian reran it at HEAD: 29 OK, which includes the four `BudgetCapTest` tests it imports. The whole suite: 312 OK. The record's red for this pass had 16 failures out of 29.

## The boundary picture

From `.xv/slices/2026-10-27-prototype-budgets.boundary.md`, as given:

- Modules touched: `scripts/orders` and `scripts/prototypes`. None added or removed.
- No edges, tables or surface paths added or removed. No new calls out of the process. Shape hints: none.

## What the suite asserts after

`PrototypeBudgetsTest` gains 16 tests:

- A variant over its budget stops the slice for the originator. The stop names its spend, `prototype_budgets` and `none`, and the others still run. When all three are over, nothing runs and `pick none` abandons the slice.
- After a raise, a second start runs only the raised variant, with what is left of its budget. It keeps b and c: branches, recordings, record entries and side-by-side rows. A variant whose budget was not raised is not run, and the stop names its spend.
- The missing-budgets stop has the same question as `orders.evaluate`, and no agent runs.
- A variant whose own run costs 1.2 against a budget of 1 raises `prototype_budget_spent`. It cannot be picked, though it has a branch. Once its budget is raised, it alone reruns.
- A variant that ran within its budget but left no recording is rerun. A new axis reruns all three.
- The stop words the two kinds of run-out apart, says to answer before starting again, and says a pick is for two people unless solo. One name answers the raise, and one name cannot pick `none` (this test config is not solo). The log line says the same.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The boundary picture shows no new modules, edges, tables or surfaces ("Edges: added: none"). The `prototypes → orders` edge was already there.
- The new order `prototype_budget_spent` (`scripts/orders.py:205-219`) fits "`orders` holds the stop rules" (`.xv/picture.md:23`). The new record keys `checks.prototype.ran_out` and `ran_during` (`scripts/prototypes.py:191`) fit "State is files" (`.xv/picture.md:26`).
- Moving the `prototype_budgets_not_set` question out of `prototypes.py` (`scripts/prototypes.py:94-101`) brings the code into line with `.xv/picture.md:69`.
- The forecast expected `"shape": "wide"` (`.xv/slices/2026-10-27-prototype-budgets.md:11`). The change touches two modules plus a CHANGELOG line (`CHANGELOG.md:5-7`), which is narrower than forecast.

## 2. Pitch

pitch_contradiction: no.

- Checked against "to vibe with discipline" (`.xv/pitch.md:7`) and "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
- The change sends a spent budget to a person and lets no agent choose (`scripts/orders.py:214`, `fire("prototype_budget_spent", "originator", ...)`). It serves no one the pitch excludes.

## 3. Moved tests

| File | Before | After | Why | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- `xv wall diff 2026-10-27-prototype-budgets` gives `changed: []`, `deleted: []` and `fewer_assertions: []`. The record has `moved_tests: []` (`.xv/slices/2026-10-27-prototype-budgets.md:15`).
- In `tests/test_budget_cap_turns_session.py`, two existing lines change, and neither is an assertion: the import gains `FAKE` (`:9`), and the closing comment is reworded as Sean asked (settled point "Small", record `:38`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

- `.xv/picture.md:26` describes `prototype_budgets` but not what happens when a variant spends its budget. Proposed addition after "a variant's spend counts only against its own budget.":

  "A variant has run out when its spend, before the start or after its own run, reaches its budget. The others still run, and then `prototype_budget_spent` stops for the originator, naming each variant that ran out and its spend. The originator answers a budget raise alone; a pick, `none` included, is for two people unless the repo runs solo. A variant has finished when it has a recording and did not run out. A second `xv prototype start` reruns every variant that has not finished, from HEAD, on what is left of its budget, and keeps the finished ones. A new `--axis` keeps none. A variant that ran out cannot be picked."
- `.xv/picture.md:69` (binding decision 10) stays true and now matches the code. No edit.
- `.xv/picture.md:60` (binding decision 1): this slice changes standing orders. The repo runs solo (`.xv/picture.md:52`), and `CHANGELOG.md:7` says "Sean decided it, solo". No edit.

## Door

**Door:** two-way. A revert undoes it. No data is migrated and nothing is sent to users. Older code ignores the new keys `checks.prototype.ran_out` and `ran_during`. **Blast radius:** prototypes.

## Raw data

- Slice record: `.xv/slices/2026-10-27-prototype-budgets.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Wall: `xv wall diff 2026-10-27-prototype-budgets`
- Boundary: `.xv/slices/2026-10-27-prototype-budgets.boundary.md`
- Earlier packets: this file in the earlier commits of `xv/2026-10-27-prototype-budgets`

## From the cleaner

- Shape proposal, for people: The over-budget key check (tokens/usd/turns against budget) is written twice in prototypes.start, before and after the run; a small helper would remove it, but that is a new concept, so left for the packet.

## From the cleaner

- Shape proposal, for people: The over-budget key check (tokens/usd/turns against budget) is written twice in prototypes.start, before and after the run; a small helper would remove it, but that is a new concept, so left for the packet.
- Shape proposal, for people: The over-budget key check (tokens/usd/turns against budget) is written twice in prototypes.start, before and after the run; a small helper would remove it, but that is a new concept, so left for the packet.
- Shape proposal, for people: The over-budget key check (tokens/usd/turns against budget) is written twice in prototypes.start, before and after the run; a small helper would remove it, but that is a new concept, so left for the packet.

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

# Packet: A prototype that runs out of budget comes back to a person (second pass)

This is the second pass. The first packet's finding A, a variant that runs out during its own run, is fixed (`scripts/prototypes.py:177-185`), and three new tests cover it. There is no shape change and no pitch contradiction, so nothing here goes to two people. Sean decides four things:

- **B. A second start now never reruns a variant that has a branch and did not run out.** `scripts/prototypes.py:117` gives `kept = {n for n in NAMES if (prev.get(n) or {}).get("branch") and n not in prev_out}`, and `:121-123` run only the variants that are neither kept nor stopped. `run_one` makes the branch before the agent runs (`scripts/prototypes.py:51`). So a variant that ran within its budget but left no recording is kept on every later start. It shows "No recording" (`:163`), can never be rebuilt, and still counts as pickable by `pick` (`:226-227` check only `ran_out` and the branch). The same holds for `xv prototype start <id> --axis "<new axis>"` after the prototypes are built: no variant reruns, and the kept rows keep their old `axis_position` (`:140`) under the new axis heading (`:133`). Before the slice, a second start rebuilt every variant that was not over budget (base `for n, p in zip(NAMES, positions) if n not in stopped`). The scenario says "keeps the variants that finished". It does not say whether a variant with no recording finished, or what a new axis does. No test covers either case.
- **C. The stop says a variant "was not run" when it did run.** `scripts/orders.py:207` gives `what = "; ".join(f"variant {n} spent {spent} and was not run" ...)`. For the case this pass was for, a variant whose own run passed its budget, the person reads "variant a spent usd 1.2 of 1 and was not run". Variant a ran, and it has a branch and a recording. The test checks only for `"a"` and `"1.2"` in the question (`tests/test_budget_cap_turns_session.py:276-277`).
- **D. The stop goes to the originator, but two of its three answers need two people.** `prototype_budget_spent` is seated `"originator"` (`scripts/orders.py:211`). `pick` still refuses one name unless the repo runs solo (`scripts/prototypes.py:217-219`, `if len(set(who)) < 2 and not solo(config): raise XVError("the pick is for two people ...")`), and that covers `pick none` too. This repo is solo (`.xv/picture.md:52`), so it does not show here. An adopting team that is not solo gets a stop for one person that only two people can close by picking. The scenario's "come back to you for a decision" does not settle which is meant.
- **The picture edit in section 4.**

The standing-order change was already decided by Sean, solo, and has its CHANGELOG line (`CHANGELOG.md:7`).

Smaller points, for the record only:

- The stop tells the person to raise a budget and run `xv prototype start` again (`scripts/orders.py:212-213`). It does not say to answer the stop first, and `start` refuses while a stop is unanswered (`scripts/prototypes.py:79-82`). The record's `watch_first_green` does say "answer the stop".
- A pick made from the budget stop is written to the decision record under the order `prototypes_ready` (`scripts/prototypes.py:241`).
- The log still says "the pick is for two people" when the stop is for the originator (`scripts/prototypes.py:201`).
- A rerun variant starts again from HEAD in a fresh worktree (`scripts/prototypes.py:48-51`), with only the dollars left in its budget (`:59`; the test expects 1.8 of 3 after 1.2, `tests/test_budget_cap_turns_session.py:300`). Its first run's work is discarded.
- `tests/test_budget_cap_turns_session.py:305` still says "the new cases are the three above". There are now nine.

## The scenario

Sean's words: "whenever a prototype runs out of budget, it should come back to you for a decision. you cannot pick anything if no prototype was built, but you should be able to stop the prototype exploration."

- When a variant has spent its budget, the others still run. Then the slice stops for the originator, naming each variant that ran out and what it spent.
- The choices are: raise that variant's budget and start again, pick a variant that finished, or pick `none`. When all three ran out, `none` is the only pick.
- A second start runs only the variants that ran out, on their raised budgets. It keeps the finished variants with their worktrees, recordings and side-by-side rows.
- `prototype_budgets_not_set` is raised by `scripts/orders.py`.
- Settled at the first guardian stop: a variant whose own run passes its budget counts as ran out. It is named in the stop, it cannot be picked, and it reruns once its budget is raised.

May ignore: nothing stated.

## The recording

None; this is a feature. To replay it, run `cd tests && python3 -m unittest test_budget_cap_turns_session.PrototypeBudgetsTest`. The guardian reran it at HEAD: 22 OK. That count includes the four `BudgetCapTest` tests it imports. The guardian also reran the whole suite: 305 OK. The record has the red for this pass: 9 failures, `'two_people' != 'originator'`.

## The boundary picture

From `.xv/slices/2026-10-27-prototype-budgets.boundary.md`, as given:

- Modules touched: `scripts/orders` and `scripts/prototypes`. None added or removed.
- No edges added or removed. No tables. No surface paths. No new calls out of the process.
- Shape hints: none.

## What the suite asserts after

`PrototypeBudgetsTest` gains nine tests:

- A variant already over its budget stops the slice for the originator. The stop names its spend, `prototype_budgets` and `none`, and the others still run.
- When all three are over, nothing runs, and `pick none` sets the slice to abandoned.
- A second start, after a raise, runs only the raised variant, with the dollars it has left. It keeps b and c: branches, recordings, record entries and side-by-side rows.
- A variant whose budget was not raised does not run again, and the stop names its spend.
- The missing-budgets stop has the same question as `orders.evaluate`'s `prototype_budgets_not_set`, and no agent runs.
- New in this pass: a variant whose run costs 1.2 against a budget of 1 raises `prototype_budget_spent` for the originator. It cannot be picked, though it has a branch. Once raised, it alone reruns with 1.8, and b's and c's recordings stay.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The boundary picture shows no new modules, edges, tables or surfaces (`.xv/slices/2026-10-27-prototype-budgets.boundary.md`, "Edges: added: none"). `prototypes → orders` already existed: `scripts/prototypes.py:27` (`import orders`) is not in the diff.
- The new stop order `prototype_budget_spent` (`scripts/orders.py:205-214`) fits "`orders` holds the stop rules" (`.xv/picture.md:23`). The new record key `checks.prototype.ran_out` (`scripts/prototypes.py:188`) fits "State is files" (`.xv/picture.md:26`).
- Moving the `prototype_budgets_not_set` question out of `prototypes.py` (`scripts/prototypes.py:93-97`) brings the code into line with `.xv/picture.md:69`.
- The cleaner proposed a helper for the over-budget check, which is written twice (`scripts/prototypes.py:118-119` and `:183`). That would be a function inside one module, not a shape change.
- Breadth: the change touches two modules and adds one CHANGELOG line (`CHANGELOG.md:5-7`). The forecast expected `"shape": "wide"`, so this is narrower than forecast.

## 2. Pitch

pitch_contradiction: no.

- What I checked against: "to vibe with discipline" (`.xv/pitch.md:7`), and "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
- The change sends a budget stop to a person and lets no agent decide (`scripts/orders.py:211`, `fire("prototype_budget_spent", "originator", ...)`). It serves no one the pitch excludes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- `xv wall diff 2026-10-27-prototype-budgets` reports `changed: []`, `deleted: []` and `fewer_assertions: []`. The record has `moved_tests: []` (`.xv/slices/2026-10-27-prototype-budgets.md:15`).
- The diff to `tests/test_budget_cap_turns_session.py` changes one existing line, the import of `FAKE` beside `BudgetCapTest` (`:9`). It changes no assertion. Every other change adds lines.

Slice-only tests removed: none. Kept: none.

## 4. The picture

- `.xv/picture.md:26` describes `prototype_budgets` but not what happens when one is spent. Proposed addition after "a variant's spend counts only against its own budget.": "A variant has run out when its spend, before the start or after its own run, reaches its budget. Then the others still run, and `prototype_budget_spent` stops for the originator, naming each variant that ran out and its spend. A second `xv prototype start` reruns only those variants, from HEAD, on their raised budgets, and keeps every other variant that has a branch. A variant that ran out cannot be picked." If B is decided differently, word "keeps every other variant that has a branch" to match.
- `.xv/picture.md:69` (binding decision 10) stays true and now matches the code. No edit.
- `.xv/picture.md:60` (binding decision 1): this slice changes standing orders, which needs two people. The repo runs solo (`.xv/picture.md:52`), and `CHANGELOG.md:7` records "Sean decided it, solo". No edit.

## Door

**Door:** two-way. A revert undoes it. No data is migrated and nothing is sent to users. Older code ignores the new key `checks.prototype.ran_out`. **Blast radius:** prototypes.

## Raw data

- Slice record: `.xv/slices/2026-10-27-prototype-budgets.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Wall: `xv wall diff 2026-10-27-prototype-budgets`
- Boundary: `.xv/slices/2026-10-27-prototype-budgets.boundary.md`
- Previous packet: this file at commit `3914508`

## From the cleaner

- Shape proposal, for people: The over-budget key check (tokens/usd/turns against budget) is written twice in prototypes.start, before and after the run; a small helper would remove it, but that is a new concept, so left for the packet.

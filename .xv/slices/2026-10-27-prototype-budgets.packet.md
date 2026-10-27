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

# Packet: A prototype that runs out of budget comes back to a person

Sean decides three things. First, the new stop only fires when a variant was already over its budget before `xv prototype start` began. A variant that runs out during the start does not fire it (finding A). Second, the picture edit in section 4. Third, the standing-order change: Sean has already made it solo, and it has its CHANGELOG line. No shape change and no pitch contradiction, so nothing here goes to two people.

## Finding A: the stop does not fire when a variant runs out during a real run

- `scripts/prototypes.py:117-119` decides whether a variant ran out from the spend recorded *before* the run: `over = {n: [k for k in ("tokens", "usd", "turns") if budgets[n].get(k) and spent[n][k] >= budgets[n][k]] ...}`. Then `scripts/prototypes.py:174` builds `ran_out` from `stopped`, and `stopped` comes from that `over`. The run's own spend is added at `:160-163`, after that decision.
- `scripts/prototypes.py:116` and `:119`: `kept = {n for n in NAMES if (prev.get(n) or {}).get("branch")}` and `stopped = {n for n in NAMES if n not in kept and over[n]}`. `run_one` creates the branch before the agent runs (`git(["worktree", "add", "-q", "-b", branch, wt, "HEAD"], root)`), so every variant that ran has a branch.
- Example: three variants start with nothing spent. Variant a hits its `--max-budget-usd` cap during the run, and b and c finish. Variant a has a branch and is over budget, but `ran_out` is `{}`. The stop is `prototypes_ready` for two people, not `prototype_budget_spent` for the originator. On a second start, a is in `kept`, so it is never run again and never reported. `pick` refuses only a variant with no branch (`if variant != "none" and not next(...).get("branch")`), so a can be picked. The scenario says "A variant that ran out cannot be picked".
- The tests never cover this case. Each new test records the spend with `proto_spent` before the first start, when no variant has a branch (`tests/test_budget_cap_turns_session.py:65-68`, used at `:179`, `:189-190`, `:203` and the other new tests).
- The record's `watch_first_green` asks for exactly the real case ("Start three prototypes with one variant over its budget and see the stop come back to you"). Watching it on a real harness will show whether this happens.

## The scenario

Sean's words: "whenever a prototype runs out of budget, it should come back to you for a decision. you cannot pick anything if no prototype was built, but you should be able to stop the prototype exploration." When a variant has spent its budget, the others still run. Then the slice stops for the originator, naming each variant that ran out and what it spent. The choices are: raise that variant's budget and start again, pick a variant that finished, or pick `none`. When all three ran out, `none` is the only pick. A second start runs only the variants that ran out, on their raised budgets, and keeps the finished ones with their worktrees, recordings and side-by-side rows. `prototype_budgets_not_set` is raised by the rule in `scripts/orders.py`, not by a copy in `xv prototype start`. May ignore: nothing stated.

## The recording

None; this is a feature. To replay the red, then the green: `cd tests && python3 -m unittest test_budget_cap_turns_session.PrototypeBudgetsTest`. At `pre_maker_commit` 77c6a09, 6 of 19 fail (`'two_people' != 'originator'`). At HEAD, 19 OK (rerun by the guardian). The whole suite passed, 302 OK (from the cleaner's run in the slice record; the guardian did not rerun it).

## The boundary picture

From `.xv/slices/2026-10-27-prototype-budgets.boundary.md`, as given: modules touched are `scripts/orders` and `scripts/prototypes`. No modules added or removed. No edges added or removed. No tables. No surface paths added or removed. No new calls out of the process. Shape hints: none.

## What the suite asserts after

`PrototypeBudgetsTest` has six new tests:

- A variant already over its budget stops for the originator. The stop names what it spent, `prototype_budgets` and `none`, and the other two still run.
- When all three are over, nothing runs, the stop goes to the originator, and `pick none` sets the slice to abandoned.
- A second start, after a raise, runs only the raised variant, with the dollars it has left (1.95).
- A second start keeps b's and c's branches, recordings, record entries and side-by-side rows.
- A variant whose budget was not raised is not run again, and the stop names what it spent.
- The missing-budgets stop has the same question as `orders.evaluate`'s `prototype_budgets_not_set`, and no agent runs.

No old assertion moved.

## 1. Shape

shape_change: no.

- The boundary picture shows no new modules, edges, tables or surfaces. `prototypes → orders` already exists (`.xv/picture.md:21` lists `orders` among `run`'s reach, and the "after" edges list includes `scripts/prototypes → scripts/orders`).
- One new stop order, `prototype_budget_spent` (`scripts/orders.py:205-214`), and one new record key, `checks.prototype.ran_out` (`scripts/prototypes.py:175`). Both fit the current shape: "`orders` holds the stop rules" (`.xv/picture.md:23`), and state is files (`.xv/picture.md:26`).
- Moving the `prototype_budgets_not_set` question out of `prototypes.py` (`scripts/prototypes.py:93-96`) brings the code into line with "The standing orders all live in `scripts/orders.py`" (`.xv/picture.md:69`).
- Breadth is narrow: the boundary picture touches only `scripts/orders` and `scripts/prototypes`, and the diff adds one line to `CHANGELOG.md:5-7`. The record's forecast says `"shape": "wide"`, so this is narrower than expected.

## 2. Pitch

pitch_contradiction: no.

The pitch says xv-agents exists "to vibe with discipline" (`.xv/pitch.md:7`) and "is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). The change sends a budget stop to a person. It does not let an agent decide or serve anyone the pitch excludes. The pick still needs two names unless the repo runs solo (`scripts/prototypes.py` `pick`: `if len(set(who)) < 2 and not solo(config): raise XVError("the pick is for two people ...")`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-27-prototype-budgets` reports `changed: []`, `deleted: []`, `fewer_assertions: []`. The record has `moved_tests: []`. The diff to `tests/test_budget_cap_turns_session.py` only adds lines (`:6-7`, `:160-251`).

Slice-only tests removed: none. Kept: none.

## 4. The picture

- `.xv/picture.md:26` describes `prototype_budgets` but does not say what happens when one is spent. Proposed addition after "a variant's spend counts only against its own budget.": "When a variant has spent its budget, the others still run and `prototype_budget_spent` stops for the originator, naming each variant that ran out. A second `xv prototype start` runs only those variants, on raised budgets, and keeps the finished ones. A variant that ran out cannot be picked." If finding A is fixed first, word it to match.
- `.xv/picture.md:69` (binding decision 10) stays true and now matches the code, because the `prototype_budgets_not_set` question exists only in `scripts/orders.py`. No edit needed.
- `.xv/picture.md:60` (binding decision 1): this slice changes a standing order. It has its CHANGELOG line (`CHANGELOG.md:5-7`, "Sean decided it, solo"), and the repo runs solo (`.xv/picture.md:52`). No picture edit, but the solo decision is on the record for whoever reads it later.
- Small wording drift, no picture edit: `scripts/prototypes.py:188` still logs "the pick is for two people", even when the stop goes to the originator.

## Door

**Door:** two-way. A revert undoes it. No data is migrated, nothing is sent to users, and the new record key `ran_out` is ignored by older code. **Blast radius:** prototypes.

## Raw data

- Slice record: `.xv/slices/2026-10-27-prototype-budgets.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Wall: `xv wall diff 2026-10-27-prototype-budgets`
- Boundary: `xv boundary --base 23f8dd53788ee9f656f572e730e497e3b0a298bc` (`.xv/slices/2026-10-27-prototype-budgets.boundary.md`)

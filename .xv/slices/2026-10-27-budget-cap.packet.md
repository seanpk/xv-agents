---
slice: 2026-10-27-budget-cap
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
door: two-way
blast_radius: broad
---

# Packet: The budget caps the whole slice, red or green

Nothing here stops the change for two people. Sean has these to decide:

- **One settled point is still not in the diff.** `prototype_budgets_not_set` is still raised in `scripts/prototypes.py`, not `scripts/orders.py` (record line 39, part 4).
- **A pick after a budget-stopped variant may crash.** The stopped variant is still listed as a prototype with no branch, and `xv prototype pick` deletes that branch by name.
- **Four doc and brief lines still say the budget covers the maker only.** One of them is in the watch's brief.
- **Two moved tests**, both forced by the scenario, neither asserting less. One test's name now says the opposite of what it asserts.
- **Three picture edits.**

The other three points settled at the guardian's third stop are done: the after-maker count, decision 49 / `README.md:247` / the retro, and the log and side-by-side line. The merge is Sean's.

## The scenario

Before each step, the watch compares the slice's spend with the budget. Prototype spend does not count. A Claude step gets the dollars left as `--max-budget-usd` and the turns left as `--max-turns`. When dollars, tokens or turns are used up, the step does not run, and `budget_spent` stops for the originator whatever the suite says. This applies to `session` steps too. The after-maker `budget_spent` check uses the same count. A raised budget lets the slice go on.

A prototype slice takes `prototype_budgets`, one budget for each of a, b and c, free to differ. Each variant is capped at its own budget less its own spend. A variant that has spent its budget does not run, and the others do. The log and the side-by-side file name the stopped variant. `xv prototype start` stops for the originator until the budgets are set.

Sean settled this solo at three stops (record lines 35, 37 and 39). May ignore: nothing stated.

## The recording

None; this is a feature. To replay:

- Run the red command (record line 13). At HEAD: 2 tests, OK.
- Run the whole suite (`cd tests && python3 -m unittest -q`). At HEAD, rerun by the guardian: 224 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-27-budget-cap.boundary.md`, as given:

- Modules touched: `agentcli`, `orders`, `prototypes`, `retro`, `run`, `spend`. None added or removed.
- Edges: none added or removed. New outbound calls: none.
- Tables: none. Surfaces: none added or removed.
- Shape hints: none.

## What the suite asserts after

- **`tests/test_budget_cap.py` (4 tests):**
  - With $0.80 of $1 spent, the next step gets a 0.2 cap.
  - With $1.05 spent and the suite green, no agent runs and `budget_spent` names 1.05.
  - At the token cap, no agent runs.
  - After a raise to $2, the step runs with 0.95.
- **`tests/test_budget_cap_turns_session.py`, turns and session:**
  - With 12 of 30 turns spent, the next step gets `--max-turns 18`.
  - With all 30 spent, the step stops at `budget_spent`.
  - A `session` step with the budget spent stops at `budget_spent`.
- **The same file, prototypes:**
  - With no budgets set, `prototype start` exits 10 for the originator.
  - Each variant is capped at its own budget less its own spend.
  - A variant at its budget gets no agent call.
  - The log and the side-by-side row name the stopped variant.
  - Slice spend does not shrink a variant's cap.
- **`tests/test_orders.py:38-44`:** with $0.6, $1.0 and $0.5 spent across three steps of a $2 budget and the suite red, the after-maker check fires `budget_spent`.

## 1. Shape

`shape_change: no`. `shape_breadth: narrow`.

- **No new module, edge, table or surface.** The boundary picture lists none and gives no shape hints. The flat-module shape at `.xv/picture.md:21` holds.
- **The standing-order rule is met as the team works.** `.xv/picture.md:59` asks for two people and a CHANGELOG line; `.xv/picture.md:51` says solo. The lines are `CHANGELOG.md:7-9`.

### Findings inside the shape, for Sean

- **`prototype_budgets_not_set` is not in `scripts/orders.py`.**
  - Record line 39, part 4: "The `prototype_budgets_not_set` stop lives in `scripts/orders.py`, as `budget_not_set` does."
  - It is still raised inline at `scripts/prototypes.py:92-102`. `scripts/orders.py` has no such order.
  - `.xv/picture.md:68`: "The standing orders all live in `scripts/orders.py`."
  - The stopped variant still gets a `data["prototypes"]` row, with `"branch": p.get("branch")`, which is `None` because it never ran (`scripts/prototypes.py:153`).
  - `pick` runs `git(["branch", "-D", p["branch"]], root, check=False)` on every row (`scripts/prototypes.py:203`). A `None` in the argv is a `TypeError` inside `subprocess.run`, which `check=False` does not catch.
  - The stopped variant is also a valid pick, because `names` is built from the same rows (`scripts/prototypes.py:196`).
  - Not run by the guardian, and no test covers a pick after a stopped variant.
- **When all three variants are stopped, the stop goes to two people, not the person who sets budgets.** No thread runs and `ready` is 0. `prototypes_ready` then fires for `two_people`: "0 prototype(s) are ready to pick from" (`scripts/orders.py:193-197`). Only the originator sets `prototype_budgets` (record line 37). The scenario is silent on this case.
- **Doc and brief lines still say maker only, or "and not green".** Record line 39, part 2 asked only for decision 49, `README.md:247` and the retro, and those are done. These four are now untrue:
  - `docs/decisions.md:114`, decision 77: "The retro's 'overran' compares the maker's spend with the budget, as the budget order does." `scripts/retro.py:64` now uses `slice_spend`.
  - `README.md:306`: "the maker's run is capped by it."
  - `README.md:276`: "The budget is spent and the suite is not green." `budget_spent` now also fires before any step, green or not (`scripts/orders.py:50-59`, `scripts/run.py:339`).
  - `skills/watch/SKILL.md:54`: the same row in the watch's brief. A brief change needs two people and a CHANGELOG line (`.xv/picture.md:59`).
  - `prototype_budgets` is missing from `docs/slice-record.md`, which `README.md:264` calls "The field list".
  - `prototype_budgets_not_set` is missing from the stops tables at `README.md:274-292` and in `skills/watch/SKILL.md`.
- **One assertion is loose.** `tests/test_budget_cap_turns_session.py:79` asserts `assertIn("budget", stop["order"])`, which `budget_spent` or `budget_not_set` would also pass. The order is named `prototype_budgets_not_set` in `CHANGELOG.md:7` and record line 37.

## 2. Pitch

`pitch_contradiction: no`.

- I read `.xv/pitch.md:7`, `:17`, `:21` and `:25`.
- A cap on every step, with a person deciding to spend more, fits "to vibe with discipline" (`.xv/pitch.md:7`).

## 3. Moved tests

`xv wall diff` against baseline `0b4adbd` lists one changed file, `tests/test_spend.py`: 13 assertions before, 13 after, none deleted, none added. The record's `moved_tests` has two entries. The `tests/test_prototypes.py` move came before the wall baseline was reset at `0b4adbd`, so the wall diff does not show it. The record has it. The scenario's own red files are `tests/test_orders.py` and `tests/test_budget_cap_turns_session.py`: they gained tests and are not moves.

| Test | Before | After | Maker's reason | Forced? |
| --- | --- | --- | --- | --- |
| `tests/test_prototypes.py:29-30`, `test_three_prototypes_side_by_side_then_a_pick_by_two_people` | went straight to `xv run p1` | sets `prototype_budgets` {a,b,c: $1} first; the assertions are unchanged | `prototype start` stops until the budgets are set | Yes, record line 37. Asserts no less. |
| `tests/test_spend.py:36-41`, `test_the_budget_covers_the_makers_steps` | `(["usd"], 4000)`: the guardian's row is left out | `(["tokens", "usd"], 103999)`: the guardian's row counts | the budget counts every step's spend | Yes, record line 35, part 1, and line 39, part 1. Asserts no less, and now also checks tokens. |

- **The moved test's name is now wrong.** `tests/test_spend.py:36` is still called `test_the_budget_covers_the_makers_steps`, but it now asserts that the budget covers every step.

Slice-only removals: none (`slice_only: []`).

## 4. The picture

Three edits are proposed for Sean. The guardian does not write to the picture.

- **`.xv/picture.md:23`** says "`orders` holds the stop rules" and "`spend` … owns the one per-row token count". Add: "`spend.slice_spend` is the one count the slice budget uses: every step except the prototypes. `orders.budget_before` checks it before every step, `session` steps too. The after-maker check and the retro use the same count."
- **`.xv/picture.md:26`** says state is files. Add: "The record holds `prototype_budgets`, one budget for each of a, b and c, in the shape of `budget` and free to differ. A variant's spend counts only against its own budget."
- **`.xv/picture.md:38`**, under Names. Add: "'The budget' is the slice budget and covers every step after the pick. 'Prototype budgets' are the per-variant ones."

`.xv/picture.md:68` (decision 10) needs no edit if the code follows Sean's answer and moves `prototype_budgets_not_set` into `orders.py`. That move is code, not a picture edit.

## Door

**Door:** two-way. A revert restores the maker-only cap, and a `prototype_budgets` field left in a record is ignored. No data is migrated, and no exit code changes (`.xv/picture.md:69`). **Blast radius:** broad. Every step and every prototype run, in every repo that takes the update, can now stop before it runs, and the retro's overrun count changes (`scripts/retro.py:64`).

## Raw data

- Slice record: `.xv/slices/2026-10-27-budget-cap.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..HEAD`, plus the uncommitted `.boundary.md`
- Wall: `xv wall diff 2026-10-27-budget-cap`
- Boundary: `.xv/slices/2026-10-27-budget-cap.boundary.md`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- Wider than the forecast's list of modules, still narrow.**
- The forecast's breadth named run, agentcli and orders (record line 11).
- `prototypes`, `retro` and `spend` came in with Sean's answers (record lines 35, 39).
- Sean answered `diff_growing` with "yes, all" (record line 23).
- Everything stays inside existing modules, so it is not wider than "narrow".
- The maker's last report does not claim this part.
- A budget-stopped variant can break the pick.**
- The new field and the new stop are not documented.**
- The pitch says nothing about budgets or prototypes.

## From the cleaner

- Shape proposal, for people: Extract a helper in run.py that appends a stop to the record, sets status, logs and saves; the new budget stop block, the setup_failed block and the post-step stop block repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: Extract a helper that appends a stop to the record, sets status, logs and saves; run.py's new budget stop block, the setup_failed block and the post-step stop block, and prototypes.py's two stop blocks repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: prototypes.py repeats orders.budget_before's 'any of tokens/usd/turns reached the budget' test per variant; one shared 'budget reached' predicate would need a new concept, so it is left.

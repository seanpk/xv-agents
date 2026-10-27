---
slice: 2026-10-27-budget-cap
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 3
door: two-way
blast_radius: broad
---

# Packet: The budget caps the whole slice, red or green

Nothing here stops the change for two people. Both points settled at the guardian's fourth stop are now in the diff (record line 42): the pick no longer crashes, and a test asserts the exact order name. Sean has these to decide:

- **The `prototype_budgets_not_set` in `scripts/orders.py` never reaches a person.** `xv prototype start` still raises its own copy first, with different wording. The orders rule only runs after the variants have run, and by then the budgets are set.
- **Doc and brief lines still say the budget covers only the maker, or only a red suite.** Record line 42 leaves these to the watch at the merge. They are listed below so none are missed.
- **Three moved tests.** All are recorded, all are forced by the scenario, and none asserts less.
- **Three picture edits.**
- **Two edge cases the scenario does not cover:** all three variants stopped, and a second `prototype start`.

The merge is Sean's.

## The scenario

Before each step, the watch compares the slice's spend with the budget. Prototype spend does not count. A Claude step gets the dollars left as `--max-budget-usd` and the turns left as `--max-turns`. When dollars, tokens or turns are used up, the step does not run, and `budget_spent` stops for the originator whatever the suite says. The same applies to `session` steps and to the after-maker check. A raised budget lets the slice go on.

A prototype slice takes `prototype_budgets`, one budget each for a, b and c, free to differ. Each variant is capped at its own budget less its own spend. A variant that has spent its budget stops alone, and the log and the side-by-side file name it. A stopped variant cannot be picked, and picking another variant does not crash. `prototype start` stops for the originator until the budgets are set (record lines 34-42). May ignore: nothing stated.

## The recording

None; this is a feature. To replay at HEAD, both rerun by the guardian:

- The red command (record line 13): 33 tests, OK.
- The whole suite, `cd tests && python3 -m unittest -q`: 229 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-27-budget-cap.boundary.md`, as given:

- **Modules touched:** `agentcli`, `orders`, `prototypes`, `retro`, `run`, `spend`. None added or removed.
- **Edges and outbound calls:** none added or removed.
- **Tables:** none. **Surfaces:** none added or removed.
- **Shape hints:** none.

## What the suite asserts after

- **`tests/test_budget_cap.py`:**
  - With $0.80 of $1 spent, the next step is capped at 0.2.
  - With $1.05 spent and the suite green, no agent runs and `budget_spent` names the spend.
  - At the token cap, no agent runs.
  - After a raise, the step runs with what is left.
- **`tests/test_budget_cap_turns_session.py:17-45`:**
  - With 12 of 30 turns spent, the step gets `--max-turns 18`.
  - With all 30 spent, the step stops at `budget_spent`.
  - A `session` step with the budget spent stops at `budget_spent`.
- **The same file, `:75-156`:**
  - With no prototype budgets, `start` exits 10 for the originator, with the exact order `prototype_budgets_not_set` (`:121`).
  - Each variant is capped at its own budget less its own spend.
  - A spent variant gets no agent call, and the log and the side-by-side row name it.
  - Picking the stopped variant exits 2 with no traceback (`:128-137`).
  - Picking another variant exits 0 and leaves no proto branches (`:139-148`).
  - Slice spend does not shrink a variant's cap.
- **`tests/test_orders.py:38-44`:** the after-maker check counts every step's spend.
- **`tests/test_orders.py:129-137`:** `orders` fires `prototype_budgets_not_set` for the originator on a prototype slice with no budgets, and does not fire it once all three are set.

## 1. Shape

`shape_change: no`. `shape_breadth: narrow`.

- **No shape change.** The boundary picture shows no new module, edge, table or surface, and no shape hints. The flat-module shape at `.xv/picture.md:21` holds.
- **The forecast named three modules; six are touched** (`.xv/slices/2026-10-27-budget-cap.md:11`). `prototypes`, `retro` and `spend` came in with Sean's answers (`.xv/slices/2026-10-27-budget-cap.md:36`, `:40`). All six are existing modules (`.xv/picture.md:21`), so the change is narrow, as forecast.
- **The standing-order rule is met as this team works.** `.xv/picture.md:59` asks for a CHANGELOG line, and `.xv/picture.md:51` says the team runs solo. The lines are at `CHANGELOG.md:7-9`.

### Findings inside the shape, for Sean

- **The settled point about `orders.py` is met in form, not in effect.**
  - Record line 40, part 4, and record line 42, part 2: "The `prototype_budgets_not_set` stop lives in `scripts/orders.py`, as `budget_not_set` does."
  - The rule was added at `scripts/orders.py:193-197`, but `scripts/orders.py` is consulted only at `scripts/prototypes.py:165`. That is after the variants have run.
  - The inline copy at `scripts/prototypes.py:92-102` returns before that whenever a budget is missing. So the stop a person sees is still the one built in `prototypes.py`, with different wording: no owner name, and a different example.
  - `tests/test_budget_cap_turns_session.py:121` passes on the inline copy. `tests/test_orders.py:129-133` tests the orders copy, which `xv prototype start` never reaches.
  - Two copies of one standing order sit against `.xv/picture.md:68`: "The standing orders all live in `scripts/orders.py`."
  - The cleaner raised the same point and left it as a behaviour call (`.xv/slices/2026-10-27-budget-cap.md:27`, the cleaner's last report).
- **When all three variants are stopped, the stop goes to two people** (`scripts/orders.py:199-203`).
  - No variant runs, so `ready` is 0, and `prototypes_ready` fires for `two_people`: "0 prototype(s) are ready to pick from" (`scripts/orders.py:199-203`).
  - Only the originator sets `prototype_budgets` (`.xv/slices/2026-10-27-budget-cap.md:38`).
  - The scenario does not cover this case, and the guardian did not run it (`.xv/slices/2026-10-27-budget-cap.md:34-42`).
- **A second `prototype start` may make a rebuilt variant unpickable** (`scripts/prototypes.py:153`, `scripts/prototypes.py:199`).
  - `start` appends rows to `data["prototypes"]` and never clears them (`scripts/prototypes.py:153`).
  - The new refusal reads the first row for the variant: `next(p for p in data["prototypes"] if p["name"] == variant)` (`scripts/prototypes.py:199`).
  - Example: variant a stops at its budget, the budget is raised, and `start` runs again. The old row has no branch (`scripts/prototypes.py:153`), so the pick refuses a, even though a was rebuilt.
  - The guardian did not run this, and the scenario does not cover a second start (`.xv/slices/2026-10-27-budget-cap.md:34-42`).
- **Doc and brief lines that are now untrue** (`.xv/slices/2026-10-27-budget-cap.md:42` assigns these to the watch at the merge). They are still in the tree:
  - `docs/decisions.md:114`, decision 77: "The retro's 'overran' compares the maker's spend with the budget." `scripts/retro.py:64` now uses `slice_spend`.
  - `README.md:276` and `skills/watch/SKILL.md:54`: "The budget is spent and the suite is not green." `budget_spent` now also fires before any step, green or red (`scripts/orders.py:50-59`, `scripts/run.py:339`). The second line is in a brief, so its change needs a CHANGELOG line (`.xv/picture.md:59`).
  - `README.md:306`: "the maker's run is capped by it." Every Claude step now is (`scripts/run.py:358-359`).
  - `prototype_budgets` and `prototype_budgets_not_set` are missing from `docs/slice-record.md`, `README.md` and `skills/watch/SKILL.md` (each has 0 matches by grep).

## 2. Pitch

`pitch_contradiction: no`.

- I read `.xv/pitch.md:7`, `:17`, `:21` and `:25`. None of them speaks to budgets or prototypes.
- A cap on every step, which only a person can raise, fits "to vibe with discipline" (`.xv/pitch.md:7`).

## 3. Moved tests

`xv wall diff` against baseline `a17f135` lists no changed, deleted or added test files, and no file with fewer assertions. All three recorded moves came before that baseline, so the record is the source here. The red files, `tests/test_orders.py` and `tests/test_budget_cap_turns_session.py`, only gained tests, so they are not moves.

| Test | Before | After | Reason given | Forced? |
| --- | --- | --- | --- | --- |
| `tests/test_prototypes.py:28-30`, `test_three_prototypes_side_by_side_then_a_pick_by_two_people` | went straight to `xv run p1` | sets `prototype_budgets` to $1 for each of a, b and c first; assertions unchanged | `start` stops until the budgets are set (maker) | Yes, record line 38. Asserts no less. |
| `tests/test_spend.py:42` | `(["usd"], 4000)`: the guardian's row is left out | `(["tokens", "usd"], 103999)`: the guardian's row counts | the budget counts every step (maker) | Yes, record line 36 part 1 and line 40 part 1. Asserts no less, and now also checks tokens. |
| `tests/test_spend.py:37`, the name | `test_the_budget_covers_the_makers_steps` | `test_the_budget_counts_every_steps_spend_the_guardians_too`; no assertion changed | the old name said the opposite (scenario) | Yes, record line 42 part 3. |

Slice-only removals: none (`slice_only: []`).

## 4. The picture

Three edits are proposed for Sean to accept. The guardian does not write to the picture.

- **`.xv/picture.md:23`** says "`orders` holds the stop rules" and that `spend` owns the one token count. Add: "`spend.slice_spend` is the count the slice budget uses: every step except the prototypes. `orders.budget_before` checks it before every step, `session` steps too. The after-maker check and the retro use the same count."
- **`.xv/picture.md:26`**, the record files. Add: "The record holds `prototype_budgets`, one budget for each of a, b and c, in the shape of `budget` and free to differ. A variant's spend counts only against its own budget."
- **`.xv/picture.md:38`**, Names. Add: "'The budget' is the slice budget and covers every step after the pick. 'Prototype budgets' are the per-variant ones."

`.xv/picture.md:68` (decision 10) stays true only if the inline copy in `prototypes.py` goes. That is a code change, not a picture edit (see the first finding).

## Door

**Door:** two-way. A revert restores the maker-only cap. A `prototype_budgets` field left in a record is then ignored. No data is migrated, and no exit code changes (`.xv/picture.md:69`). **Blast radius:** broad. In every repo that takes the update, every step and every prototype run can now stop before it runs, and the retro's overrun count changes (`scripts/retro.py:64`).

## Raw data

- Slice record: `.xv/slices/2026-10-27-budget-cap.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..HEAD` (working tree clean)
- Wall: `xv wall diff 2026-10-27-budget-cap`
- Boundary: `.xv/slices/2026-10-27-budget-cap.boundary.md`

## From the cleaner

The cleaner's last pass left three shape proposals for people:

- **Two copies of the not-set stop.** `prototype_budgets_not_set` is built in both `orders.evaluate` and `prototypes.start`, with different wording. Making `start` rely on `orders` alone is a behaviour call.
- **One "budget reached" test, written twice.** `prototypes.start` repeats `spend.budget_state`'s check (have tokens, usd or turns reached the budget?) for each variant.
- **One stop sequence, repeated.** A helper that appends a stop, sets the status, logs and saves would serve `run.py`'s budget stop block and `prototypes.py`'s two stop blocks.

## From the cleaner

- Shape proposal, for people: Extract a helper in run.py that appends a stop to the record, sets status, logs and saves; the new budget stop block, the setup_failed block and the post-step stop block repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: Extract a helper that appends a stop to the record, sets status, logs and saves; run.py's new budget stop block, the setup_failed block and the post-step stop block, and prototypes.py's two stop blocks repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: prototypes.py repeats orders.budget_before's 'any of tokens/usd/turns reached the budget' test per variant; one shared 'budget reached' predicate would need a new concept, so it is left.
- Shape proposal, for people: prototype_budgets_not_set is built in both orders.evaluate and prototypes.start with different wording; making start rely on orders alone would change what `xv prototype start` does on its own, so it is a behaviour/shape call for the packet.
- Shape proposal, for people: prototypes.start repeats spend.budget_state's 'any of tokens/usd/turns reached the budget' test per variant; one shared 'budget reached' predicate would be a new concept, so it is left.
- Shape proposal, for people: A helper that appends a stop to the record, sets status, logs and saves would serve run.py's budget stop block and prototypes.py's two stop blocks; it needs a new concept, so it is left.

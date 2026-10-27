---
slice: 2026-10-27-budget-cap
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: broad
---

# Packet: The budget caps the whole slice, red or green

Nothing stops this for two people. Sean, as the person who set the work going, has four things to decide: one picture edit, two older docs that now say the opposite of the code, two budget paths the change did not reach (prototypes, and agents run in the session), and a `turns` budget that now means two different things. The merge is Sean's.

## The scenario

Before each step, the watch compares the slice's whole spend so far with the budget. A Claude step gets `--max-budget-usd` set to the dollars left. When no dollars are left, or the tokens spent have reached the token cap, the step does not run. Instead `budget_spent` stops for the originator, whatever the suite says, and names what is spent. A raised budget lets the slice go on from the step it stopped before. The scenario says this changes a standing order, and that Sean decided it solo, with a CHANGELOG line (#34, #36). May ignore: nothing stated.

## The recording

None; this is a feature. Replay the red and green with `cd tests && python3 -m unittest test_budget_cap`: 4 failing at `9902f20`, 4 passing at HEAD. The whole suite, `cd tests && python3 -m unittest -q`: 202 tests, OK, rerun by the guardian at `ed16f3f`.

## The boundary picture

From `.xv/slices/2026-10-27-budget-cap.boundary.md`, as given:

- Modules touched: `scripts/agentcli`, `scripts/orders`, `scripts/run`. None added or removed.
- Edges added or removed: none. New outbound calls: none.
- Tables: none. Surfaces added or removed: none.
- Shape hints: none.

## What the suite asserts after

`tests/test_budget_cap.py`, new, 4 tests, with a stand-in `claude` that logs its argv:

- With a $1 budget and $0.80 spent, the scenario step's Claude call carries `--max-budget-usd 0.2`.
- With $1.05 spent and the suite green, `xv step guardian` exits 10 with `budget_spent` for `originator`. The question contains `1.05`, and no agent is called.
- With 1000 tokens spent against a 1000-token cap, `xv step maker` exits 10 with `budget_spent`, and no agent is called.
- After a stop at $1.05 of $1, raising the budget to $2 and answering the stop lets `xv step guardian` run with `--max-budget-usd 0.95`.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow. That matches the forecast's `narrow`, which named these three modules plus tests and a CHANGELOG line.

- **No new module, edge, table or surface.** The boundary picture lists none and has no shape hints. The 22 modules and flat layout in `.xv/picture.md:21` still hold.
- **The new rule sits where the picture puts stop rules.** It is `budget_before` in `scripts/orders.py:50-60` and reads only the record, as `.xv/picture.md:23` ("`orders` holds the stop rules") and `.xv/picture.md:68` ("The standing orders all live in `scripts/orders.py`, a pure function of the record and the config") describe. So it is inside the current shape.
- **It is a second way into the orders.** It is called from `scripts/run.py:343` before the step, not through `evaluate`:
  ```
  +    budget_stop = orders.budget_before(data)
  +    if budget_stop:
  ```
  So `xv orders <id> --after <step>` never evaluates it. This is the path `scripts/run.py:339-341` sends agents marked `session` down, and those steps get no budget check before they run. Sean decides whether that matters.
- **The standing-order rule is met.** `.xv/picture.md:59` needs two people and a CHANGELOG line, and `.xv/picture.md:51` has `two_people: solo`. The CHANGELOG line is at `CHANGELOG.md:7`. The record's `decisions:` is empty; the decision is recorded only in the CHANGELOG and the scenario text.

Findings inside the shape, for Sean:

- **Two docs now say the opposite of the code.** At `scripts/run.py:358` the diff drops the maker-only guard on the caps and passes every step's spend: `argv = agentcli.with_caps(argv, data.get("budget"), spendlib.totals(data.get("spend") or [])["usd"])`. The removed lines were `if agent == "maker":` and `argv = agentcli.with_caps(argv, data.get("budget"))`. `docs/decisions.md:70` (decision 49) still says "The budget covers the maker's steps. The other agents' spend is recorded but does not count against it." `README.md:247` still says "The maker's run gets the budget as hard caps." Neither file is in the diff. `.xv/picture.md:75` says decisions.md does not bind, so this is out-of-date documentation, not a contradiction.
- **The retro still counts only the maker against the budget.** `scripts/retro.py:63-64` reads "the budget covers the maker's steps, as the budget order counts it" and totals only `step == "maker"`. The new order counts every step (`scripts/orders.py:53`: `spent = totals(data.get("spend") or [])`). So a slice stopped by the new rule shows up in the retro as `stopped: budget_spent`, but not as "overran its budget", unless the maker alone overran.
- **Two `budget_spent` checks now measure differently.** The after-maker one is kept at `scripts/orders.py:119-125`. It uses `budget_state`, which counts maker-only spend and includes `turns`. The new before-step one counts all spend and checks only `tokens` and `usd` (`scripts/orders.py:54`: `for k in ("tokens", "usd")`). Both fire under the same order name.
- **A `turns` budget is now a per-step cap on every step.** `with_caps` now runs on every step, so `--max-turns <budget.turns>` goes to every Claude and Grok step (`scripts/agentcli.py:56-57`, called from `scripts/run.py:358`). The whole slice's turns are never checked before a step. The scenario says nothing about turns.
- **Prototypes still get the whole budget each.** `scripts/prototypes.py:59` still calls `agentcli.with_caps(argv, budget)` without the spend so far. `scripts/prototypes.py:102` starts one thread per variant, each with the full `data.get("budget")`, and none passes through `budget_before`. The scenario names this problem: "each step may spend the whole budget by itself".
- **The cleaner's open proposal touches this code.** Its shape proposal (extract the add-a-stop-and-save helper) covers the new block at `scripts/run.py:343-352`, which repeats the setup_failed sequence. It rides in "From the cleaner".

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7`, `:17`, `:21` and `:25`. The change limits what agents spend on a slice and keeps a person on the decision to spend more. That fits "to vibe with discipline" (`.xv/pitch.md:7`). The pitch says nothing about budgets.

## 3. Moved tests

`xv wall diff 2026-10-27-budget-cap` against baseline `76d45a1` lists no test changed, deleted or added, and no test with fewer assertions. The record's `moved_tests` is `[]`. `tests/test_agentcli.py:9-18` calls `with_caps` without the new `spent_usd` argument and still asserts `--max-budget-usd 2`, unchanged, because the argument defaults to 0 (`scripts/agentcli.py:47`). `tests/test_orders.py:36` (after-maker `budget_spent`) is also unchanged.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

## 4. The picture

One line is incomplete. `.xv/picture.md:23` says "`orders` holds the stop rules" and does not say that one of them now runs before a step, from `run`, and not through `orders.evaluate` (`scripts/run.py:343`). Proposed edit for Sean: add "One of them, `budget_before`, runs before each step from `run.step`; the rest run after the step through `evaluate`."

The budget's measure is not in the picture. `.xv/picture.md:23` and `:38` mention the budget only for its token count, which is unchanged. Decision 49, which this change reverses, is in `docs/decisions.md` and not in the picture (see Shape).

## Door

**Door:** two-way. A revert restores the maker-only cap. No data is migrated, and stops already written to records stay readable. **Blast radius:** broad. Every step of every slice with a budget, in every repo that updates, can now stop before it runs.

## Raw data

- Slice record: `.xv/slices/2026-10-27-budget-cap.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..ed16f3f`
- Wall: `xv wall diff 2026-10-27-budget-cap`
- Boundary: `xv boundary --base 94cdf5f15f31c53d02fc8de787ce85889627e799`, kept at `.xv/slices/2026-10-27-budget-cap.boundary.md`

## From the cleaner

- Shape proposal, for people: Extract a helper in run.py that appends a stop to the record, sets status, logs and saves; the new budget stop block, the setup_failed block and the post-step stop block repeat that sequence. It needs a new concept, so it is left for the packet.

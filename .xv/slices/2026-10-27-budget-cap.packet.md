---
slice: 2026-10-27-budget-cap
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: broad
---

# Packet: The budget caps the whole slice, red or green

Nothing here stops the change for two people. Sean has these to decide:

- Two of the four things settled at the guardian's stop are not in the diff. The after-maker `budget_spent` check still counts only the maker. Decision 49, the README and the retro still say the budget covers the maker.
- A prototype variant that has spent its budget is dropped without a stop or a log line.
- `prototype_budgets_not_set` is a new stop raised outside `scripts/orders.py`.
- One moved test.
- Three picture edits.

The merge is Sean's.

## The scenario

Before each step, the watch compares the slice's spend with the budget. A Claude step gets the dollars left as `--max-budget-usd` and the turns left as `--max-turns`. When dollars, tokens or turns are used up, the step does not run, and `budget_spent` stops for the originator whatever the suite says. Steps marked `session` get the same check before they run. A raised budget lets the slice go on.

A prototype slice takes one budget per variant, set with `xv record set <id> prototype_budgets '{"a":…,"b":…,"c":…}'`. Each variant is capped at its own budget less its own spend. A variant that has spent its budget stops alone. Prototype spend does not count against the slice budget. `xv prototype start` stops for the originator until the per-variant budgets are set.

Settled by Sean, solo, at two stops (record lines 35 and 37). May ignore: nothing stated.

## The recording

None; this is a feature. To replay, run the red command in the record (`.xv/slices/2026-10-27-budget-cap.md:13`): 8 tests, all failing at `b8baebc`, all passing at HEAD. The whole suite (`cd tests && python3 -m unittest -q`) ran 222 tests, OK, rerun by the guardian on the working tree.

## The boundary picture

From `.xv/slices/2026-10-27-budget-cap.boundary.md`, as given:

- Modules touched: `scripts/agentcli`, `scripts/orders`, `scripts/prototypes`, `scripts/run`. None added or removed.
- Edges added or removed: none. New outbound calls: none.
- Tables: none. Surfaces: none added or removed.
- Shape hints: none.

## What the suite asserts after

`tests/test_budget_cap.py` has 4 tests, from the first pass. They check:

- the dollars-left cap (0.2 of $1)
- no step at $1.05 spent with the suite green
- no step at the token cap
- a raised budget going on with 0.95 left

`tests/test_budget_cap_turns_session.py` has 8 tests, all new. Each uses a stand-in `claude` that logs its argv.

- With a 30-turn budget and 12 turns spent, the next step gets `--max-turns 18`.
- With all 30 turns spent, the step exits 10 at `budget_spent` and no agent is called.
- A step marked `session` with the budget spent exits 10 at `budget_spent`, not with the "run it in the session" error.
- With no `prototype_budgets`, `prototype start` exits 10 for `originator` and no agent is called. The order is only checked to contain "budget" (`tests/test_budget_cap_turns_session.py:79`).
- Budgets of a $1, b $2.50 and c $0.75 give caps of 1.0, 2.5 and 0.75.
- Each variant's cap is its budget less its own spend only.
- A variant that has spent its budget gets no agent call, and b and c still run.
- Slice-step spend does not shrink a variant's cap.

## 1. Shape

`shape_change: no`. `shape_breadth: narrow`.

- **No new module, edge, table or surface.** The boundary picture lists none and has no shape hints. The 22 flat modules in `.xv/picture.md:21` still hold.
- **The breadth is past the forecast's list but still narrow.** The forecast's breadth named three modules: watch/run, agentcli and orders (`.xv/slices/2026-10-27-budget-cap.md:11`). `scripts/prototypes` is a fourth (`scripts/prototypes.py:92-118`). It came in after the forecast, with Sean's answer at the guardian's stop (`.xv/slices/2026-10-27-budget-cap.md:35`, part 3). Sean answered `diff_growing` with "yes, all" (`.xv/slices/2026-10-27-budget-cap.md:23`). The forecast called it narrow, and it is still narrow.
- **The new record field is not a new surface.** `prototype_budgets` is set with the existing `xv record set`. Surfaces are the `xv` CLI and the skills (`.xv/picture.md:27`), and no command was added.
- **A new stop sits outside the orders file.** `scripts/prototypes.py:92-102` raises `prototype_budgets_not_set` inline. `.xv/picture.md:68` says "The standing orders all live in `scripts/orders.py` … A stop raised because an action failed (`setup_failed`, `axis_not_named`) is not a standing order; the command that failed raises it." The stop mirrors `budget_not_set`, which is a standing order at `scripts/orders.py:95-97`. It is raised beside `axis_not_named` (`scripts/prototypes.py:84-90`). Sean decides which kind it is. If it is the `axis_not_named` kind, the picture line names it (see 4).
- **The standing-order rule is met.** `.xv/picture.md:59` asks for two people and a CHANGELOG line, and `.xv/picture.md:51` says `two_people: solo`. The lines are at `CHANGELOG.md:7-8`. The record's `decisions:` list is empty.

### Findings inside the shape, for Sean

- **"One count everywhere" is half done.** The record says: "the before-step check and the after-maker `budget_spent` check both count every step's spend" (`.xv/slices/2026-10-27-budget-cap.md:35`, part 1). The before-step check counts every step except prototypes (`scripts/orders.py:50-52`, `slice_spend`). The after-maker check is unchanged. It still calls `budget_state(data)` (`scripts/orders.py:125`), which defaults to `steps=("maker",)` (`scripts/spend.py:187-190`). So does `xv spend budget` (`scripts/spend.py:221`). Two checks fire the same order name with different counts. The maker's report does not claim this part.
- **The docs and the retro were not brought into line.** The record says: "`docs/decisions.md` decision 49, `README.md:247` and the retro's budget count (`scripts/retro.py:63-64`) say what the code does" (`.xv/slices/2026-10-27-budget-cap.md:35`, part 4). None of the three is in the diff.
  - `docs/decisions.md:70` still reads "The budget covers the maker's steps. The other agents' spend is recorded but does not count against it."
  - `README.md:247` still reads "The maker's run gets the budget as hard caps."
  - `README.md:276` still lists the order as "The budget is spent and the suite is not green".
  - `README.md:306` still says "the maker's run is capped by it".
  - `scripts/retro.py:63-64` still counts `step == "maker"` only, so a slice stopped by the new check is not reported as "overran its budget".
- **A variant that spent its budget leaves no trace of why.** `scripts/prototypes.py:116-118` drops the variant's thread:
  ```
  +            if not any(budgets[n].get(k) and spent[n][k] >= budgets[n][k] for k in ("tokens", "usd", "turns"))]
  ```
  No stop is appended and no log line is written. The side-by-side table then shows "No recording. This prototype cannot be compared with the others." (`scripts/prototypes.py:144-145`), and `data["prototypes"]` gets a row with empty fields (`scripts/prototypes.py:150`). The pick still goes to two people with two prototypes, and nothing says one was cut for budget. The scenario says the variant "stops alone" (record line 35, part 3) but does not say who is told.
- **The new stop is not in the field list or the stops table.** `prototype_budgets` is missing from `docs/slice-record.md`, which README.md:264 names as "The field list". `prototype_budgets_not_set` is missing from the stops table at `README.md:274-292`.
- **One assertion is loose.** `tests/test_budget_cap_turns_session.py:79` asserts `assertIn("budget", stop["order"])`. It would also pass if the stop were `budget_spent` or `budget_not_set`. The scenario and `CHANGELOG.md:7` name the order `prototype_budgets_not_set`.

## 2. Pitch

`pitch_contradiction: no`. I read `.xv/pitch.md:7`, `:17`, `:21` and `:25`. The change limits what agents spend and keeps a person on the choice to spend more, which fits "to vibe with discipline" (`.xv/pitch.md:7`). The pitch says nothing about budgets or prototypes.

## 3. Moved tests

`xv wall diff 2026-10-27-budget-cap` against baseline `4073674` lists one file changed, none deleted or added, and none with fewer assertions (12 before, 12 after). The record's `moved_tests` names the same file. `slice_only` is empty.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_prototypes.py:28-30`, `test_three_prototypes_side_by_side_then_a_pick_by_two_people` | went straight to `xv run p1` | first runs `xv record set p1 prototype_budgets {a,b,c: {usd: 1}} --by pat`, then the same assertions | "`xv prototype start` stop[s] for the person until prototype_budgets are set" | Yes. Record line 37: "`xv prototype start` stops for the person … when they are not set." The test asserts no less. |

Slice-only removals: none.

## 4. The picture

Three lines are now incomplete. The proposed edits are for Sean; the guardian does not write to the picture.

- `.xv/picture.md:23`, "`orders` holds the stop rules". Add: "One of them, `budget_before`, runs before every step from `run.step`, session steps too; the rest run after the step through `evaluate`. The slice budget counts every step's spend except the prototypes'."
- `.xv/picture.md:26`, state is files. Add that the record holds `prototype_budgets`, one budget per variant (a, b, c), each with the same keys as `budget` and free to differ.
- `.xv/picture.md:68`, decision 10. If Sean keeps `prototype_budgets_not_set` in `prototypes.py`, add it to the list after "(`setup_failed`, `axis_not_named`)". If not, the stop moves to `orders.py`; that change is code, not a picture edit.

Decision 49 is in `docs/decisions.md`. Per `.xv/picture.md:75` it does not bind, so it is not a picture edit (see Shape).

## Door

**Door:** two-way. A revert restores the maker-only cap, and a `prototype_budgets` field left in a record is ignored. No data is migrated, and no public contract or exit code changes (`.xv/picture.md:69`). **Blast radius:** broad. Every step and every prototype run of every slice with a budget, in every repo that updates, can now stop before it runs.

## Raw data

- Slice record: `.xv/slices/2026-10-27-budget-cap.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..HEAD`, plus the uncommitted `.boundary.md`
- Wall: `xv wall diff 2026-10-27-budget-cap`
- Boundary: `.xv/slices/2026-10-27-budget-cap.boundary.md`

## From the cleaner

- Shape proposal, for people: extract a helper that appends a stop, sets status, logs and saves. The sequence repeats in `scripts/run.py:339-348`, the setup_failed block, the post-step stop block and `scripts/prototypes.py:84-102`.
- Shape proposal, for people: one shared "budget reached" check. `scripts/prototypes.py:118` repeats the test in `scripts/orders.py:59`.

## From the cleaner

- Shape proposal, for people: Extract a helper in run.py that appends a stop to the record, sets status, logs and saves; the new budget stop block, the setup_failed block and the post-step stop block repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: Extract a helper that appends a stop to the record, sets status, logs and saves; run.py's new budget stop block, the setup_failed block and the post-step stop block, and prototypes.py's two stop blocks repeat that sequence. It needs a new concept, so it is left for the packet.
- Shape proposal, for people: prototypes.py repeats orders.budget_before's 'any of tokens/usd/turns reached the budget' test per variant; one shared 'budget reached' predicate would need a new concept, so it is left.

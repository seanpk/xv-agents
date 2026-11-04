---
slice: 2026-11-04-orders-home
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: no
shape_breadth: none
moved_tests: 1
door: two-way
blast_radius: stops
---

# Packet: Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109

This is the third pass. It comes after Sean's 18:56 answer (pick 1: tests for A and B, the four source-text tests go to `slice_only` so the cleaner removes them, and the watch makes the picture edits) and his 19:04 answer (the coverage is accepted). Nothing stops for two people. The originator decides one thing: **the four tests Sean listed in `slice_only` are still on the wall.** The cleaner did not remove them and gave no reason to keep them (check 3). Everything else Sean asked for at 18:56 is done: A and B now have tests, and the picture edits are in. The merge is the originator's.

## The scenario

The stop rules move into `scripts/orders.py`. Whether a miss repeats is read from the record alone (1). `xv step`, `xv run`, `xv record packet` and the session path write the same facts, and one function applies what `orders` returns, `next` included (2). There is one shared definition of allowed values and one shared test-name matcher, and the wall-flag block is split out of `cmd_answer` (3). An accepted shape does not stop again as wider than forecast, `accept_moves` counts moves rather than entries, and the docs say `yes`, `no` or `accepted` (4). The pre-step `budget_spent` stop is marked, and `prototype_budget_spent` needs `--settled` (5). Accepted slice-only marks survive a scenario re-run and are not asked about again (6). A test fails when the docs miss an allowed packet value (7). A move is recorded once and keeps its slice-only flag (8). The `docs/slice-record.md` changes are in, and `who` is a list in new decisions (9).

Settled on this slice (the record's `stops`): A, an answer that sends the work back does not accept the shape. B, `apply_verdict` adds no second open stop of the same order. C, the prototype path, waits for #117. The breadth of an accepted shape and the wall-mark gap go to a new issue (18:56).

May ignore: the new stops for #20, #15, #113 and #117; old slice records; brief wording unless a moved rule makes a brief untrue.

## The recording

None: this is a feature. To replay, run the red command (in the record's `red.command`). I ran it at HEAD `0cd8b46`: 32 tests, OK. At `9ef4bdf`, before the maker, it had 19 failures and 3 errors (`checks.scenario.red_output`). Whole suite: 856 OK, from the record's `checks.cleaner` at 19:42. No script has changed since then (`git diff 482b628..HEAD` touches only `.xv/picture.md`, the record and two test files), so I did not run it again.

## The boundary picture

From `.xv/slices/2026-11-04-orders-home.boundary.md`, as given. Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`, `scripts/xvlib`. Modules, edges, tables, surface paths and outbound calls added or removed: none. Shape hints: none.

## What the suite asserts after

Everything the last packet listed still holds. This pass adds:

- A `shape_wider_than_forecast` stop answered with `sent_back` does not accept the shape: a wider breadth still fires the stop (`tests/test_orders.py:492-497`).
- `xv record answer` on that stop with `--next maker` sets `sent_back: true`. With `--next close` it does not (`tests/test_record.py:1401-1415`).
- `apply_verdict` run twice with the same stop leaves one open stop and status `stopped`. An answered stop of the same order can open again. A stop of another order opens beside an open one (`tests/test_record.py:1417-1437`).

## 1. Shape

shape_change: no. The boundary picture has no new module, edge, table, surface or outbound call, and no shape hints (`.xv/slices/2026-11-04-orders-home.boundary.md`: "Edges / added: none / removed: none"). `record` already reached `orders` and `packet` (`.xv/picture.md:21`). This pass changes no script: `git diff 482b628..HEAD` shows changes only to `.xv/picture.md`, `tests/test_orders.py` and `tests/test_record.py`, plus the record. Breadth is `none`, against a `wide` forecast.

Findings inside the shape, for the originator:

- **A and B are now tested.** This closes the last packet's two gaps. The tests are listed above. They passed before they were written, because the maker had already fixed both. The scenario agent said so (`checks.reports`, scenario at 18:57: "green guards, not reds").
- **The side effect of B has no test.** When a stop of the same order is already open, `scripts/record.py:583-590` keeps the old stop's `question` and `also` and drops the new wording. `test_applying_the_same_stop_twice_leaves_one_open_stop` (`tests/test_record.py:1420`) uses the same question both times, so it does not show this.

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`), and "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). This pass adds only tests and the picture edits Sean asked for. It changes no user, no audience and no promise.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`AcceptWallFlagTest`) | `assertEqual(data["decisions"][0]["who"], "pat")` | `assertEqual(data["decisions"][0]["who"], ["pat"])` | "scenario point 9: new decisions write who as a list" | Yes. Point 9 says "New decisions write `who` as a list". The assertion count did not drop (last packet). Sean accepted it at 18:14. |

`moved_tests` still lists this move twice (17:26:59 and 17:35:27). `accept_moves` counts it once (`scripts/orders.py:232`, a set of `(file, assertion)`). This pass moved no old test. `xv wall diff` is empty, but note that the wall baseline was taken again at the red commit `4d8e6de` (`wall_baseline.commit: acb6ade`, with `tests/test_record.py` going from 253 to 259 assertions in `.xv/slices/2026-11-04-orders-home.wall.json`). So `xv wall diff` now shows only changes after this pass's red, and the record is the only source for the earlier move.

**Slice-only removals: none. All four listed tests were kept, and nobody gave a reason.** Sean's 18:56 settled line says "The four OneHomeTest source-text tests Sean accepted as slice-only are listed in slice_only, so the cleaner removes them." They are still there at HEAD:

- `tests/test_orders.py:453` `test_run_and_record_no_longer_work_out_a_repeat`
- `tests/test_orders.py:460` `test_the_allowed_values_of_the_packet_fields_are_defined_once`
- `tests/test_orders.py:465` `test_the_test_name_matcher_is_shared`
- `tests/test_orders.py:468` `test_the_wall_flags_are_not_handled_inside_cmd_answer`

The cleaner brief says to remove each test in `slice_only` "unless you find a reason to keep it", and to report the reason if it keeps one (`skills/cleaner/SKILL.md:39`). The 19:42 cleaner report says "maker's test changes and slice_only list not checked", and it records no move. The record has no `xv record move --slice-only` for them. So no reason to keep them exists anywhere. As long as they stay, they forbid any later `(?!\w)` in `record.py`, any `"--accept-wall"` text in `cmd_answer`, and any `miss_repeat` string in `run.py` or `record.py`.

## 4. The picture

No edit proposed. The five edits from the last packet are in `.xv/picture.md:23` and `.xv/picture.md:26` (commit `acb6ade`). I checked them against the code. The `sent_back` rule matches `scripts/orders.py:227-228` and `scripts/record.py:362-363`. The note that it "adds no second open stop of the same order" matches `scripts/record.py:583`. "`budget_spent` stop that `xv step` marks `pre_step`" and "`prototype_budget_spent`" match `scripts/record.py:352-355`. This pass adds only tests, and none of them makes a picture line untrue.

## 5. The wall

The same four tests: they are in `slice_only`, Sean accepted them at 18:14 and 18:56, and they should stay off the wall (`tests/test_orders.py:453-470`). I name them again because a guardian report replaces `wall_recommendations` and keeps `accepted` only for the tests it names (`scripts/record.py:489-496`). The new tests in this pass guard behaviour that point 4 and finding B need, so I have nothing to add about them. No wall test is dead.

## Door

**Door:** two-way. A revert undoes it. New records gain `sent_back`, `pre_step`, `report_n`, `packet` and `accepted` keys and a list `who`; old readers do not break on them. **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-11-04-orders-home.md`
- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..0cd8b46`. This pass alone is `git diff 482b628..0cd8b46`. The working tree is clean.
- Wall: `xv wall diff 2026-11-04-orders-home` (empty: the baseline is the red commit)
- Boundary: `.xv/slices/2026-11-04-orders-home.boundary.md`

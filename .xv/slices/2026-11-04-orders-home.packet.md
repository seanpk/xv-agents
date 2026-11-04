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

This is the fourth pass. It follows Sean's 20:02 answer (pick 1), which sent the slice back so the cleaner would remove the four tests in `slice_only` and change nothing else. The cleaner removed them, plus the `source` helper they used, and recorded each removal. Nothing stops for two people, and no scenario point is missed. **Nothing is left open from the earlier packets.** One thing to know before merging: scenario points 1 and 3 now have no test of their own. The code still meets both (check 3). Sean accepted that trade at 18:14 and 18:56. The merge is the originator's.

## The scenario

The stop rules move into `scripts/orders.py`. Whether a miss repeats is read from the record alone (1). `xv step`, `xv run`, `xv record packet` and the session path write the same facts, and one function applies what `orders` returns, `next` included (2). There is one shared definition of allowed values and one shared test-name matcher, and the wall-flag block is split out of `cmd_answer` (3). An accepted shape does not stop again as wider than forecast, `accept_moves` counts moves rather than entries, and the docs say `yes`, `no` or `accepted` (4). The pre-step `budget_spent` stop is marked, and `prototype_budget_spent` needs `--settled` (5). Accepted slice-only marks survive a scenario re-run and are not asked about again (6). A test fails when the docs miss an allowed packet value (7). A move is recorded once and keeps its slice-only flag (8). The `docs/slice-record.md` changes are in, and `who` is a list in new decisions (9).

Settled on this slice (the record's `stops`): A, an answer that sends the work back does not accept the shape. B, `apply_verdict` adds no second open stop of the same order. C, the prototype path, waits for #117. The breadth of an accepted shape and the wall-mark gap go to a new issue (18:56). The four source-text tests are removed (20:02).

May ignore: the new stops for #20, #15, #113 and #117; old slice records; brief wording unless a moved rule makes a brief untrue.

## The recording

None: this is a feature. To replay, run the red command (in the record's `red.command`). I ran it at HEAD `eda0be4`: 28 tests, OK. That is 32 at the last pass minus the four removed tests. `python3 -m unittest -q test_orders`: 62 OK. The whole suite gave 852 OK in the record's `checks.cleaner` at 20:12. That is the same code: `git diff 901445e..HEAD -- scripts tests` touches only `tests/test_orders.py`. So I did not run the whole suite again.

## The boundary picture

From `.xv/slices/2026-11-04-orders-home.boundary.md`, as given. Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`, `scripts/xvlib`. Modules, edges, tables, surface paths and outbound calls added or removed: none. Shape hints: none.

## What the suite asserts after

Everything the last packet listed still holds, except the four source-text checks. The suite no longer reads the source of `run.py`, `record.py` or `packet.py` to check that:

- `miss_repeat` or `missed_repeat` is absent;
- `("yes", "no"` appears at most once;
- `(?!\w)` is absent from `record.py`;
- `--accept-wall` is absent from `cmd_answer`.

Diff hunk `tests/test_orders.py:453-470` at `901445e`, now deleted.

## 1. Shape

shape_change: no. The boundary picture has no new module, edge, table, surface or outbound call, and no shape hints (`.xv/slices/2026-11-04-orders-home.boundary.md`: "Edges / added: none / removed: none"). This pass changes no script: `git diff 901445e..HEAD -- scripts tests` shows only the `tests/test_orders.py` removals. Breadth is `none`, against a `wide` forecast.

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`). This pass removes four tests the person had already marked slice-only. It changes no user, no audience and no promise.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`AcceptWallFlagTest`) | `assertEqual(data["decisions"][0]["who"], "pat")` | `assertEqual(data["decisions"][0]["who"], ["pat"])` | "scenario point 9: new decisions write who as a list" (maker) | Yes. Point 9 says "New decisions write `who` as a list". Sean accepted it at 18:14. `moved_tests` still holds it twice (17:26:59 and 17:35:27); `accept_moves` counts it once. |
| `tests/test_orders.py` `OneHomeTest.source` | a helper that reads `scripts/<name>` | removed | "dead helper left by the slice-only removals" (cleaner, 20:02:28) | Not a test and asserts nothing. No caller is left: `grep` for `self.source` in `tests/` finds nothing. |

**Slice-only removals:** all four removed, none kept: `test_run_and_record_no_longer_work_out_a_repeat`, `test_the_allowed_values_of_the_packet_fields_are_defined_once`, `test_the_test_name_matcher_is_shared`, `test_the_wall_flags_are_not_handled_inside_cmd_answer`. Each is recorded `slice_only: true` (cleaner, 20:02:26 to 20:02:28). `xv wall diff`: `tests/test_orders.py` assertions 106 → 100, all of them recorded.

**Points 1 and 3 now have no test of their own, but the code still meets them.** At HEAD:

- `grep miss_repeat|missed_repeat` in `scripts/run.py` and `scripts/record.py` finds nothing (point 1).
- `ALLOWED` and `YES_NO` are defined once, at `scripts/packet.py:40-41` (point 3). The other `("yes", "no")`, at `scripts/xvlib.py:70`, is the front-matter dump rule, from before this slice, and not an allowed-values list.
- `names_test` is at `scripts/xvlib.py:350`. Its callers are `scripts/record.py:196` and `scripts/run.py:567`. The `(?!\w)` left at `scripts/run.py:569` matches a class name, not a test name.
- The wall flags are handled in their own function at `scripts/record.py:292-302`, outside `cmd_answer` (`scripts/record.py:319`).

From now on, nothing stops a later change from bringing any of these back.

## 4. The picture

No edit proposed. `.xv/picture.md:23` names `names_test` in `xvlib`, `ALLOWED` and `YES_NO` in `packet`, and the repeat rule in `orders`. The code still matches each one (check 3). Removing tests changes no name, user, flow or binding decision.

## 5. The wall

Nothing to recommend. The four slice-only tests are gone from the code (`tests/test_orders.py` at `eda0be4`), so they no longer need a "stay off the wall" line. This pass adds no test, and no wall test is dead.

## Door

**Door:** two-way. A revert undoes it. New records gain `sent_back`, `pre_step`, `report_n`, `packet` and `accepted` keys and a list `who`; old readers do not break on them. **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-11-04-orders-home.md`
- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..eda0be4`. This pass alone is `git diff 901445e..eda0be4`. The working tree is clean.
- Wall: `xv wall diff 2026-11-04-orders-home` (`tests/test_orders.py` 106 → 100, recorded)
- Boundary: `.xv/slices/2026-11-04-orders-home.boundary.md`

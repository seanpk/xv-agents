---
slice: 2026-11-04-orders-home
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: none
moved_tests: 1
door: two-way
blast_radius: stops
---

# Packet: Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109

This is the second pass, after Sean's answer at 18:14 (pick 1: fix A and B). Nothing stops for two people. The originator decides three things. First, whether A and B can go in with no test of the new behaviour (check 1). Second, the picture edits, which still wait from the last packet (check 4). Third, the four wall marks, restated so they are kept (check 5). The merge is the originator's.

## The scenario

The stop rules move into `scripts/orders.py`. Whether a miss repeats is read from the record alone (1). `xv step`, `xv run`, `xv record packet` and the session path write the same facts, and one function applies what `orders` returns, `next` included (2). There is one shared definition of allowed values, one shared test-name matcher, and the wall-flag block is split out of `cmd_answer` (3). An accepted shape does not stop again as wider than forecast; `accept_moves` counts moves, not entries; the docs say `yes`, `no` or `accepted` (4). The pre-step `budget_spent` stop is marked, and `prototype_budget_spent` needs `--settled` (5). Accepted slice-only marks survive a scenario re-run and are not asked about again (6). A test fails when the docs miss an allowed packet value (7). A move is recorded once and keeps its slice-only flag (8). The `docs/slice-record.md` changes are in, and `who` is a list in new decisions (9).

Settled since the last packet (the record's `stops`, `accept_moves`, answered 2026-11-04T18:14:36): A, a send-back answer does not accept the shape. B, `xv record packet` adds no second open stop of the same order. C, the prototype path, waits for #117. D, the CHANGELOG line stays. E and F, old records, stay out of scope.

May ignore: the new stops for #20, #15, #113 and #117; old slice records; brief wording unless a moved rule makes a brief untrue.

## The recording

None: this is a feature. To replay: `cd tests && python3 -m unittest test_orders.OneHomeTest test_record.OneHomeRecordTest test_packet.PacketFieldDocsTest test_run.EveryPathOneVerdictTest.test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path test_run.PreStepBudgetStopTest.test_the_stop_xv_step_raises_before_a_step_is_answered_without_settled_once_the_budget_is_raised`. At `9ef4bdf` (pre-maker) it had 18 failures (`checks.scenario.red_output`). At HEAD `eaf1f0f` I ran it: 26 tests, OK. Whole suite: 850 OK after the second maker pass, from the record's `checks.cleaner` at 18:38. I did not run the whole suite again.

## The boundary picture

From `.xv/slices/2026-11-04-orders-home.boundary.md`, as given. Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`, `scripts/xvlib`. Modules added or removed: none. Edges added or removed: none. Tables: none. Surface paths: none. Outbound calls added: none. Shape hints: none.

## What the suite asserts after

- `orders.verdict` ignores a stale `miss_repeat` or `missed_repeat` flag. A miss is a repeat only when a watch send-back for it sits before the current report.
- `run.py` and `record.py` hold no repeat logic, no inline `("yes", "no"` tuple and no inline `(?!\w)` matcher, and `cmd_answer` does not handle `--accept-wall`. These checks read source text.
- `shape_wider_than_forecast` does not fire when `shape_change` is `accepted`, or when a stop of that order was answered "go on". It still fires when neither holds. No test answers that stop with a send-back (finding A below).
- `accept_moves` says "1 old test(s) moved" for two entries with the same file and assertion.
- An accepted slice-only mark is kept across a scenario re-run and not asked about again; only a new mark is asked about.
- A move recorded by both `xv record move` and a report is one entry, and it keeps `slice_only`.
- A new decision's `who` is a list. When an old record has a string `who`, `xv decisions` and `xv prompt` still exit 0.
- `prototype_budget_spent` and a hand-raised `budget_spent` need `--settled`. The pre-step stop that `xv step` raises does not.
- The packet template, the README and the `docs/` tables name every allowed value of `shape_change` and `pitch_contradiction`. `docs/slice-record.md` names `accepted_wall`, `refused_wall`, `settled`, `ready_to_merge` and the list.
- A repeated scenario miss leaves the same verdict on `xv step`, on `xv run`, and on `xv record report` plus `xv record packet`: an open `scenario_miss` stop for the originator, status `stopped`, next `guardian`.
- Moved: `AcceptWallFlagTest` now expects `who == ["pat"]` where it expected `"pat"`.

## 1. Shape

shape_change: no. The boundary picture shows no module, edge, table, surface or outbound call added or removed, and no shape hints (`.xv/slices/2026-11-04-orders-home.boundary.md`, "Edges: added: none / removed: none"). `record` already reached `packet` and `orders` (`.xv/picture.md:21`, "`record` reaches `orders` and `packet`"). The second pass (`git diff c8c25ca..HEAD`) touches only `scripts/orders.py` and `scripts/record.py`, inside functions that already exist. Breadth is `none`. The forecast said `wide`, so nothing is wider than forecast.

Findings inside the shape, for the originator:

- **A is fixed, but nothing tests it.** `scripts/orders.py:227-228` now reads `... s.get("answer") and not s.get("sent_back")`, and `scripts/record.py:362-363` sets `stop["sent_back"] = True` when `sends_back`. When I read `cmd_answer` (`scripts/record.py:356-357`), `--next maker` or `--next scenario` on a guardian-step stop marks the stop sent back. `--next close`, or no `--next`, counts as accepting. That matches Sean's settled line. The only test of the rule is still the "go on" answer (`tests/test_orders.py:479-485`). `git diff c8c25ca..HEAD` changes no test file, so the fix can regress silently.
- **An accepted shape stays accepted, however wide it later grows.** This is left over from A. `scripts/orders.py:227-228` does not compare the breadth that was accepted with the breadth now: the stop stores no breadth. Here is how it plays out. Two people accept `narrow` against a `none` forecast. A later pass reports `wide`. No `shape_wider_than_forecast` stop fires. Scenario point 4 says "a shape the person accepted", and Sean's settled line names only send-backs, so this is not a miss. I raise it so it can be weighed. Nothing tests it either way.
- **B is fixed, but nothing tests it.** `scripts/record.py:583-590`: `already = any(s.get("order") == st["order"] and not s.get("answer") ...)`. When that is true, no stop and no log line are added, while `status` and `next` are still set. `git diff c8c25ca..HEAD` adds no test for it. A side effect: when a stop of that order is already open, it keeps its earlier `question` and `also`, and the new verdict's wording is dropped.
- **The new stop key `sent_back` has the same name as the function `orders.sent_back`** (`scripts/orders.py:36`), which reads something different: the watch's own send-back stops, by `keys`. The stop row of `docs/slice-record.md` does not list the key. Point 9 asks only for `accepted_wall`, `refused_wall` and `settled`, so this is not a miss.

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`), and "xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). The change moves stop rules inside the watch, and the second pass only narrows when a shape stop counts as accepted. It changes no user, no audience and no promise.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`AcceptWallFlagTest`) | `assertEqual(data["decisions"][0]["who"], "pat")` | `assertEqual(data["decisions"][0]["who"], ["pat"])` | "scenario point 9: new decisions write who as a list" | Yes. Point 9 says "New decisions write `who` as a list". The assertion count is the same, 253 before and after (`xv wall diff`), so it asserts no less. Sean accepted it at 18:14. |

The record's `moved_tests` still lists this move twice (17:26:59 and 17:35:27). Both entries were written before `same_move` existed (`scripts/record.py`, `same_move`). `accept_moves` counts it once (`scripts/orders.py:232`, a set of `(file, assertion)`). The second pass changed no test (`xv wall diff`: only `tests/test_record.py`, no deletions, no drop in assertions).

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

The last packet's edits are still open (Sean: "Picture edits wait for the next packet"). Here they are again, updated for A and B:

- `.xv/picture.md:23` currently says "`xv step` and `xv record packet` apply it: they set `next` and record an answered stop with seat `watch`. The same miss on a later pass stops for the originator." Proposed: "`orders.verdict` also returns `next`. One function, `record.apply_verdict`, writes the stop or the send-backs, and `next`, on `xv step`, `xv run` and `xv record packet`; it adds no second open stop of the same order. `record.guardian_facts` turns the packet into the record's fields on every path. A watch send-back keeps `report_n` and `packet`, and a miss is a repeat when an earlier pass sent back the same key. `xv prototype` still applies its own stop (#117)."
- `.xv/picture.md:23`, the `slice_only_marks` sentence. Add: "An answer marks every listed mark `accepted`. An accepted mark is kept when the scenario runs again and is not asked about again."
- `.xv/picture.md:23`, the shape stops. Add: "`shape_wider_than_forecast` does not fire when `shape_change` is `accepted`, or when a stop of that order was answered without sending work back (the answer marks a send-back `sent_back`). `accept_moves` counts moves by file and assertion. One move is recorded once."
- `.xv/picture.md:26` currently says "a prototype stop other than `prototypes_ready`, and a `budget_spent` stop raised before its step ran, answered with `--next` that step (#82)". Proposed: "a prototype stop other than `prototypes_ready` and `prototype_budget_spent`, and the `budget_spent` stop that `xv step` marks `pre_step`, answered with `--next` that step (#82, #84)". Also add: "a decision's `who` is a list (an old record may hold a string)."
- `.xv/picture.md:23`, "`xvlib` is the shared base". Add the shared test-name matcher `names_test`, and that `packet` holds the allowed field values (`ALLOWED`, `YES_NO`).

## 5. The wall

Sean accepted these four marks at 18:14 (`accepted_wall` on the `accept_moves` stop). I restate them because a guardian report replaces `wall_recommendations` and keeps `accepted` only for tests it names again (`scripts/record.py:489-496`). If this report left them out, the record would drop them. Each one reads source text to guard a one-time refactor (`tests/test_orders.py`, `OneHomeTest`):

- `test_run_and_record_no_longer_work_out_a_repeat`: mark slice-only. The repeat-flag behaviour tests in `OneHomeTest` guard the behaviour.
- `test_the_allowed_values_of_the_packet_fields_are_defined_once`: mark slice-only. `PacketFieldDocsTest.test_the_code_allows_accepted_for_shape_change_only` guards the values.
- `test_the_test_name_matcher_is_shared`: mark slice-only. It forbids any `(?!\w)` in `record.py`, for any later use.
- `test_the_wall_flags_are_not_handled_inside_cmd_answer`: mark slice-only. `AcceptWallFlagTest` guards `--accept-wall`.

The second pass made no wall test dead: `xv wall diff` shows one changed file, with no deletions and no drop in assertions. The cleaner noted that accepting a "mark slice-only" recommendation does not add the test to `slice_only` (`checks.reports`, cleaner at 18:38). `git grep wall_recommendations scripts/` finds no code that turns one into a mark. That was already true before this slice.

## Door

**Door:** two-way. A revert undoes it. New records gain `sent_back`, `pre_step`, `report_n`, `packet` and `accepted` keys and a list `who`, and old code reads none of these in a way that breaks. **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-11-04-orders-home.md`
- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..eaf1f0f`. The second pass alone is `git diff c8c25ca..eaf1f0f`. The working tree is clean.
- Wall: `xv wall diff 2026-11-04-orders-home`
- Boundary: `xv boundary --base c7b8bbff58fc46160ba83d08d0e899d7beffaaf2` (`.xv/slices/2026-11-04-orders-home.boundary.md`)

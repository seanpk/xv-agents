---
slice: 2026-10-30-scenario-miss
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 3
door: two-way
blast_radius: watch-loop
---

# Packet: A slice that misses its own scenario goes back without a stop

There is no shape or pitch stop. The change misses one line of the scenario, amendment 3. The send-back itself is now decided in `orders.evaluate`, as amendment 3 asks. The stall check is not: whether a miss is a repeat is still worked out in `scripts/record.py` and `scripts/run.py`, and `orders` takes their answer over its own. The record.py copy is the one that makes the "same point, other words" stop work for `xv record packet`. The `orders` rule alone would miss that repeat, and if the watch records the packet before the report, it would call a first miss a repeat.

## The scenario

A slice that misses its own scenario, or breaks a decision that binds, goes back without a stop (#96). Points 1 to 7 are unchanged from the last packet:

1. The packet carries `scenario_miss` and a misses section.
2. A miss sends the slice back to the maker or to the scenario agent, and neither `accept_moves` nor `ready_to_merge` fires.
3. A numbered point that is in neither `covers` nor `not_covered` goes back to the scenario agent.
4. Each send-back is recorded and shown in `xv prompt` and `xv decisions`.
5. The slice still stops for a spent budget, a repeated miss, or `amend: yes`.
6. The template shows the fields.
7. The wording is "old test files that existed at the base" (#102).

The amendments:

- Amendment 1 settles the format.
- Amendment 2 asks for three things: the send-back as a standing order in `orders.py`, a repeat keyed by point, and the brief rule.
- Amendment 3 (`.xv/slices/2026-10-30-scenario-miss.md:68`) asks for more: "The send-back is decided by `orders.evaluate` itself … `scripts/record.py` and `scripts/run.py` only apply what `orders` returns and decide nothing themselves."

May ignore: none.

## The recording

None: this is a feature. Replay the red with `cd tests && python3 -m unittest test_orders.SendBackFromOrdersTest`. It failed at the scenario step with `('ready_to_merge', 'originator') != ('scenario_miss', 'originator')` (slice record `checks.scenario.red_output`). It passes at HEAD.

## The boundary picture

From `.xv/slices/2026-10-30-scenario-miss.boundary.md`, as given (working tree):

- Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`.
- Added edges: `scripts/record → scripts/orders` (new since the last packet) and `scripts/record → scripts/packet`.
- Nothing else changed: no modules, outbound calls, tables or surface paths were added or removed.
- Shape hint: "an edge between modules was added".

## What the suite asserts after

- **`orders.verdict`, called directly** (`tests/test_orders.py:326-401`):
  - A guardian miss gives a non-blocking `scenario_miss` fire with `send_back` `{"to": "maker", "misses": ["2"]}` and no stop.
  - Any miss marked `to: scenario` sends the slice to the scenario agent.
  - `amend: yes`, the same point worded differently after a watch send-back, a shape change, and a spent budget each stop, and none of them sends anything back.
  - After the scenario step, missed points give a `red_misses_point` send-back to the scenario agent, and the same point again stops.
- **`xv record packet` then `xv orders`** (`tests/test_record.py:1281-1333`): the guardian report is recorded first in each test. A miss sets `next: maker` with no open stop. `amend: yes` stops, and so does a second packet with the same point in other words.
- **`xv step`, end to end, and the packet lint:** both still covered as in the last packet (`tests/test_run.py:348-474`, `tests/test_packet.py:57-124`).
- **Suite at HEAD plus the uncommitted boundary file:** `cd tests && python3 -m unittest -q` was run by the guardian. The result: 599 tests ran in 235 s, OK, exit 0.

## 1. Shape

shape_change: no.

- **Hint, `scripts/record → scripts/orders` (boundary "Edges", `scripts/record.py:18` `import orders`).** This is not a shape change.
  - `orders` is "a pure function of the record and the config" (`.xv/picture.md:72`). Its imports are `spend` and `xvlib` only (`scripts/orders.py:20-21`), so the new edge makes no cycle.
  - The scenario asks for this edge: "`scripts/record.py` and `scripts/run.py` only apply what `orders` returns" (`.xv/slices/2026-10-30-scenario-miss.md:68`).
  - It makes `.xv/picture.md:21` incomplete (see 4).
- **Hint, `scripts/record → scripts/packet`.** This is not a shape change: `xv record packet` already read the packet (`.xv/picture.md:23`). Same judgment as the last packet.
- **Breadth.** Narrow. The forecast also said narrow (`.xv/slices/2026-10-30-scenario-miss.md:11`, `"shape": "narrow"`). Four existing scripts were touched.

## 2. Pitch

pitch_contradiction: no.

- Looked at `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code").
- The send-back runs with no person. People still stop the slice for an amendment, a stall or a spent budget (`scripts/orders.py:221-235`). The pitch is silent on routing.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:76-84` | The fake guardian's packet had no `scenario_miss` line | It writes `scenario_miss: no`. With `FAKE_SCENARIO_MISS` set, it writes `yes` and a `## Scenario misses` line | The send-back tests need a packet with a miss. Sean accepted it at `unrecorded_move` (04:52:15) | Yes. It is a fixture and asserts nothing, so nothing asserts less |

- `git diff f9c5cb1..HEAD -- tests` removes only the two `tests/fake_agent.py` lines shown above. Every other test file only gains lines.
- `xv wall diff 2026-10-30-scenario-miss` (baseline `a2fc6bb`, `.xv/slices/2026-10-30-scenario-miss.md:14`) shows nothing changed, deleted, added, or with fewer assertions.

Slice-only tests removed: `tests/test_orders.py` `test_the_scenario_step_names_old_test_files_that_existed_at_the_base_not_red_files` and `tests/test_run.py` `test_the_old_red_check_that_cannot_run_names_old_test_files_that_existed_at_the_base`, both accepted at the 05:52:28 `accept_moves` stop. Kept: none.

## 4. The picture

Proposed edits. The originator accepts them; the guardian does not write them.

- **`.xv/picture.md:21`** ("`record` and `evals/report` reach `spend`"): add "`record` reaches `orders` and `packet`" and change the edge count from 58 to 60.
- **`.xv/picture.md:23`** ("`orders` holds the stop rules"): add how the send-back works:
  - When no stop blocks, `orders` returns a non-blocking send-back with seat `watch`, naming `to` and the misses. After the guardian it is `scenario_miss`; after the scenario step it is `red_misses_point` (`scripts/orders.py:287-297`).
  - `xv step` and `xv record packet` apply it. They set `next` and record an answered stop with seat `watch` and `keys` (`scripts/record.py:505-514`).
  - The same key on a later pass stops for the originator (`scripts/orders.py:133`, `scripts/orders.py:232-235`).
- **`.xv/picture.md:26`**, after the `red_misses_scenario` sentence: add that a numbered point that is in neither `covers` nor `not_covered` goes back to the scenario agent. Only `xv step` and `xv run` compute this (`scripts/run.py:468`).
- **`.xv/picture.md:33`**: add "`scenario_miss` is `yes` or `no`, optional; a missing one reads as `no`."
- **`.xv/picture.md:39`**: add `watch` as the seat on a send-back the watch answered itself (`scripts/record.py:509`). It is not a seat a person fills.

## 5. The wall

- **`tests/test_orders.py:250`, `OrdersTest.test_a_scenario_miss_beside_a_shape_change_still_stops_for_two_people`: mark it slice-only so it stays off the wall.**
  - It asserts only that the stop is `shape_or_pitch` for a record with `scenario_miss: yes` and `shape_change: yes`.
  - `tests/test_orders.py:379`, `test_orders_sends_nothing_back_beside_a_shape_change`, asserts the same stop on the same record, with a miss listed, and also that nothing is sent back. So the first test only restates the second.
- Looked at the other tests this slice adds (`tests/test_orders.py:239-258`, `:326-401`; `tests/test_packet.py:57-124`; `tests/test_record.py:1281-1333`; `tests/test_run.py:348-474`; `tests/test_briefs_picture.py:35-37`). I have no recommendation for any of them.

## 6. Findings for the person

- **Two copies of the repeat rule, with different windows.**
  - `orders.sent_back` ignores watch stops at or after the last guardian report (`scripts/orders.py:36-41`).
  - `record.sent_back` counts every watch stop (`scripts/record.py:499-502`). It is used at `scripts/run.py:469` and `scripts/run.py:521`.
  - `cmd_packet` passes `after=None`, which counts every watch stop (`scripts/record.py:538`).
  - `orders` uses the outside answer whenever it is set (`scripts/orders.py:133`, `scripts/orders.py:228`, `checks.get("miss_repeat") or …`).
  - Failure cases:
    - Two packets in a row with no report between them, as `tests/test_record.py:1326-1333` does. `orders` alone would not see the first send-back, because it falls after the report. Only `scripts/record.py:538` makes that test stop.
    - On the session path, the watch runs `xv record packet` and then `xv record report`. The first send-back now falls before the newest report. `checks.guardian.miss_repeat` is `[]`, so `xv orders --after guardian` falls back to `orders.sent_back`, counts that send-back, and stops with "The same scenario miss came back" on a first miss.
  - The watch brief does not say which comes first: it names `xv record report` and `xv orders` but not `xv record packet` (`skills/watch/SKILL.md:85`). The red never exercises the window, because `with_report` sets no `at` (`tests/test_orders.py:18-20`).
  - The cleaner raised the same duplication (slice record, cleaner `shape_proposals` at 07:13:46).
- **The scenario-step send-back still runs only under `xv step` and `xv run`.** `missed_points` is computed only in `post_step` (`scripts/run.py:468`). The session path (`skills/watch/SKILL.md:85`) never computes it. This is unchanged since the last packet.
- **Points are matched by text, and amendment 3 is not numbered.** `missed_points` matches item text (`scripts/run.py:550`). This slice's scenario agent named points by number ("Points 1-7 of the scenario", slice record `checks.scenario.unreadable`). Amendment 3 has no numbered line, so `POINT` (`scripts/run.py:531`) never checks it.
- **Decision 1** (`.xv/picture.md:63`). Looked at: the line is at `CHANGELOG.md:7`. It does not mention that `orders` now returns a send-back the way callers apply it, but it covers what users see.

## Scenario misses

- amendment 3: `scripts/record.py` and `scripts/run.py` still decide whether a miss is a repeat, which decides between a send-back and a stall stop. Their answer takes precedence over the rule in `orders.py`, against "decide nothing themselves" and decision 10 (`.xv/picture.md:72`). (evidence: `scripts/record.py:538` `checks["miss_repeat"] = sorted({m["ref"] for m in found} & orders.sent_back(data, "scenario_miss", None))`; `scripts/run.py:469` and `scripts/run.py:521` via `record.sent_back`; `scripts/orders.py:228` `repeat = checks.get("miss_repeat") or …`; the red passes with these copies in place; to: scenario)

## Door

**Door:** two-way. The change is code, briefs and docs only. `scenario_miss` and the watch-seat stops are additive in the record, and a revert undoes them. **Blast radius:** watch-loop.

## Raw data

- Slice record: `.xv/slices/2026-10-30-scenario-miss.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..bb00a06` plus the uncommitted boundary file
- Wall: `xv wall diff 2026-10-30-scenario-miss`
- Boundary: `.xv/slices/2026-10-30-scenario-miss.boundary.md` (`xv boundary --base f9c5cb172de9`)

## From the cleaner

- Shape proposal, for people: "The repeat check is computed twice: run.py (missed_repeat, miss_repeat via record.sent_back) and orders.evaluate (via orders.sent_back). record.sent_back duplicates orders.sent_back without the `after` filter. Dropping the run.py and record.py copies would leave one rule in orders.py, but needs a decision on how `after` filters stops, so it is left for the packet."

## From the cleaner

- Shape proposal, for people: The guardian send-back is computed twice: scripts/run.py post_step/step and scripts/record.py cmd_packet each build misses, amend, repeat and the maker/scenario target, and the target expression is written out twice. A shared helper for 'what a packet's misses send back to' would remove it but is a new concept, so it is left for the packet.
- Shape proposal, for people: The repeat check is computed twice: run.py (missed_repeat, miss_repeat via record.sent_back) and orders.evaluate (via orders.sent_back). record.sent_back duplicates orders.sent_back without the `after` filter. Dropping the run.py and record.py copies would leave one rule in orders.py, but needs a decision on how `after` filters stops, so it is left for the packet.

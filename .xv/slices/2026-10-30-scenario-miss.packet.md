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

The change misses one line of the scenario: amendment 2, item 1. The send-back is still not a standing order in `scripts/orders.py`. The choice to send back, and where to, is now made in two places outside it, `scripts/record.py` and `scripts/run.py`, and those two copies already disagree on a spent budget. Sean sent this same point back at the last `accept_moves` stop. That was an answered stop, not a watch send-back, so the stall check (point 5) cannot see this as a repeat. There is no shape or pitch stop.

## The scenario

A slice that misses its own scenario, or breaks a decision that binds, goes back without a stop (#96). (1) The packet carries `scenario_miss` and a misses section. (2) A miss sends the slice back to the maker or the scenario agent, and `accept_moves` and `ready_to_merge` do not fire. (3) A numbered scenario point that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent. (4) Each send-back is recorded and shown in `xv prompt` and `xv decisions`. (5) The slice still stops when the budget is spent, when the same miss comes back, or for `amend: yes`. (6) The template shows the fields. (7) The wording is "old test files that existed at the base" (#102).

- Amendment 1 settles the `## Scenario misses` format, how lint treats misses, `amend: yes`, and the `xv decisions` rows.
- Amendment 2: (1) the send-back is a standing order in `scripts/orders.py`, read from the record, so every path sees a miss; (2) a repeated miss is matched by its point or decision number alone; (3) the scenario brief states the covers/not_covered rule.

May ignore: none.

## The recording

None: this is a feature. Replay the red with `cd tests && python3 -m unittest test_orders test_packet test_run test_record test_briefs_picture`. It failed at 3642430 (`'ready_to_merge' != 'scenario_miss'`). The guardian ran the whole suite at HEAD plus the uncommitted boundary file with `cd tests && python3 -m unittest -q`. The result is under "What the suite asserts after".

## The boundary picture

From `.xv/slices/2026-10-30-scenario-miss.boundary.md`, as given:

- Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`.
- Added edge: `scripts/record → scripts/packet`. No modules, outbound calls, tables or surface paths were added or removed.
- Shape hint: "an edge between modules was added".

## What the suite asserts after

- **Packet lint.** `packet.lint` rejects a `scenario_miss` value other than `yes` or `no`, and accepts a packet without the field. `packet.fix` moves a miss with no point or decision, or no evidence, to "Dropped". With no miss left, `scenario_miss` becomes `no`. A miss's ref is its point or decision number: "Point 2 is not met…" and "2: …" give the same key.
- **Orders.** With a miss there is no stop, and neither `accept_moves` nor `ready_to_merge` fires. A shape change still goes to two people. A spent budget stops with `budget_spent`.
- **`xv record packet`, then `xv orders`.** A miss sets `next: maker` with no open stop, and `xv orders` raises none. `amend: yes` stops with `scenario_miss`, and so does the same point worded differently in a second packet.
- **`xv step`.** The same as above end to end. The maker's `xv prompt` shows the miss, and `xv decisions` shows `scenario_miss` and `red_misses_point` rows.
- **Scenario step.** A numbered point in neither `covers` nor `not_covered` goes back to the scenario agent, and the same point again stops. A point in `not_covered` still stops.
- **Briefs.** The scenario brief states the covers/not_covered rule. The template and the guardian brief name the fields.
- **Old assertions.** None changed. Two slice-only tests were removed (see 3).
- **Suite run at HEAD.** `cd tests && python3 -m unittest -q` ran 590 tests: OK (the cleaner's run, slice record `checks.cleaner.suite_output`, and the guardian's own run).

## 1. Shape

shape_change: no.

- **The hint (`scripts/record → scripts/packet`, boundary picture "Edges").** Not a shape change. `xv record packet` already read the guardian's packet front matter (`.xv/picture.md:23`, "`accepted` holds only when … (`xv run`, `xv record packet`)"). Now it also parses the misses section, through `packet.misses` (`scripts/record.py:532`, `import packet as packetlib`, a function-local import as at `scripts/run.py:507`). The data coupling was already there; the code coupling is new. It does make `.xv/picture.md:21` incomplete (see 4).
- **Record state.** `scenario_miss` in the record and stops with `"seat": "watch"` (`scripts/record.py:504-513`) are state in the slice file. That is inside "State is files" (`.xv/picture.md:26`).
- **Breadth.** Narrow, the same as the forecast's `"shape": "narrow"` (`.xv/slices/2026-10-30-scenario-miss.md:11`).

## 2. Pitch

pitch_contradiction: no.

- Looked at `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Sending a slice back without a person when it misses its own scenario keeps people at the stops for amendments, stalls and budget. The pitch is silent on routing.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:76-84` | The fake guardian's packet had no `scenario_miss` line | It always writes `scenario_miss: no`, or `yes` plus a `## Scenario misses` line when `FAKE_SCENARIO_MISS` is set | The send-back tests need a packet with a miss. Sean accepted it at `unrecorded_move` and again at `accept_moves` (amendment 2) | Yes, for a packet with a miss. It asserts nothing, so nothing asserts less |

- `git diff f9c5cb1..HEAD -- tests` shows only added lines in `tests/test_orders.py`, `tests/test_packet.py`, `tests/test_record.py`, `tests/test_run.py` and `tests/test_briefs_picture.py`. No old assertion changed.
- `xv wall diff` (baseline 11e80bd) shows `tests/test_orders.py` going from 76 to 73 assertions and `tests/test_run.py` from 181 to 179. Both drops are the slice-only removals below, recorded by the cleaner (`moved_tests`, 06:16:38).

Slice-only tests removed: `tests/test_orders.py` `test_the_scenario_step_names_old_test_files_that_existed_at_the_base_not_red_files` and `tests/test_run.py` `test_the_old_red_check_that_cannot_run_names_old_test_files_that_existed_at_the_base`. Kept: none.

## 4. The picture

Proposed edits. The originator accepts them; the guardian does not write them.

- `.xv/picture.md:21` ("`record` and `evals/report` reach `spend`"): add "`record` reaches `packet` (`xv record packet` reads the misses)". Change the edge count to 59.
- `.xv/picture.md:23` ("`orders` holds the stop rules"): add that after the guardian, a packet with `scenario_miss: yes` and a kept `## Scenario misses` line, and no shape or pitch stop, sends the slice to the maker, or to the scenario agent when a miss says `to: scenario`. A repeated miss (same point or decision number), `amend: yes`, or a spent budget stops instead. Also say where the send-back is decided: today that is `record.cmd_packet` and `run.step` (`scripts/record.py:538`, `scripts/run.py:401`), not `orders`.
- `.xv/picture.md:26`, after the `red_misses_scenario` sentence: add that a numbered point of the scenario or an amendment that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent. The same point again stops with `red_misses_point`. This is checked only on `xv step` and `xv run` (`scripts/run.py:473`).
- `.xv/picture.md:33`: add "`scenario_miss` is `yes` or `no`, optional; a missing one reads as `no`."
- `.xv/picture.md:39`: the seats are `originator`, `two_people` and `chief_engineer`. Add that `watch` is the seat on a send-back the watch recorded and answered itself (`scripts/record.py:508`). It is not a seat a person fills.

## 5. The wall

- Looked at every test this slice adds (`tests/test_orders.py:231-258`, `tests/test_packet.py:57-124`, `tests/test_record.py:1281-1333`, `tests/test_run.py:348-474`, `tests/test_briefs_picture.py:35-37`). Each guards a behaviour that should hold after the slice. None restates another or guards a one-time change. The two #102 rewording tests were already marked slice-only, accepted, and removed (slice record `wall_recommendations`, `accepted: true`). No recommendation this pass.

## 6. Findings for the person

- **The two send-back copies disagree on a spent budget.** `scripts/record.py:538-539` sends back on `found and not miss_amend and not miss_repeat` and no shape or pitch, but does not check the budget. `scripts/run.py:401-411` sends back only when `orders.verdict` raised no stop, so a spent budget blocks it there. On `xv record packet` with the budget spent, the record gets both of these:
  - a watch send-back ("sent back to the maker", `next: maker`);
  - then `budget_spent` from `xv orders` (`scripts/orders.py:209-213`).
  The cleaner flagged the duplication (slice record `checks.reports`, cleaner `shape_proposals`).
- **The scenario-step send-back runs only under `xv step` and `xv run`.** `missed_points` is computed only in `post_step` (`scripts/run.py:473-474`). The session path (`xv record report` then `xv orders`, `skills/watch/SKILL.md:85`) never computes it, so point 3 does not hold there. Other scenario-step checks, such as `red_gaps`, have the same gap from before this slice.
- **Points are matched by their text, but agents name them by number.** `scripts/run.py:555` counts a point as covered only when an item contains its text, contains its first 40 characters, or is a 4-character-or-longer substring of it.
  - The scenario brief says only that each point "must appear" (`skills/scenario/SKILL.md:61`). It does not say how to name it.
  - This slice's own scenario agent named points by number: "Settled 1: …" and "Points 1-7 of the scenario …" (slice record `checks.scenario.unreadable`). Items like those fail the match, go back once, then stop as `red_misses_point`.
  - Amendment 2, item 2 keys a guardian miss by number. The scenario-step check does not.
- **Decision 1.** `.xv/picture.md:63` asks for two people and a CHANGELOG line. The line is at `CHANGELOG.md:7` and says "Sean decided it, solo"; the repo runs solo (`.xv/picture.md:55`). Looked at; nothing is missing.

## Scenario misses

- amendment 2, item 1: the send-back is not a standing order in `scripts/orders.py`; `orders.evaluate` names no send-back, and the choice to send back and where to is made in `scripts/record.py:538-542` and `scripts/run.py:401-411`, against decision 10 (`.xv/picture.md:72`, "The standing orders all live in `scripts/orders.py`") (evidence: `scripts/record.py:538-539` `if found and not checks["miss_amend"] and not checks["miss_repeat"] … send_back(...)`; `tests/test_record.py:1305` passes with the rule outside `orders.py`; to: scenario)

## Door

**Door:** two-way. Code, briefs and docs only. `scenario_miss` and the watch-seat stops are additive in the record, and a revert undoes them. **Blast radius:** watch-loop.

## Raw data

- Slice record: `.xv/slices/2026-10-30-scenario-miss.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..b2021fe`
- Wall: `xv wall diff 2026-10-30-scenario-miss`
- Boundary: `.xv/slices/2026-10-30-scenario-miss.boundary.md` (`xv boundary --base f9c5cb172de9`)

## From the cleaner

- Shape proposal, for people: The guardian send-back is computed twice: scripts/run.py post_step/step and scripts/record.py cmd_packet each build misses, amend, repeat and the maker/scenario target, and the target expression is written out twice. A shared helper for 'what a packet's misses send back to' would remove it but is a new concept, so it is left for the packet.

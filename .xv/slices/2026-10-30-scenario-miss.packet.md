---
slice: 2026-10-30-scenario-miss
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: watch-loop
---

# Packet: A slice that misses its own scenario goes back without a stop

Sean decides three things: (1) the send-back routing sits in `scripts/run.py`, not in `scripts/orders.py`, which binding decision 10 asks for, and so `xv record packet` and the session path never see a miss; (2) the scenario-point match is a text match that the scenario brief does not explain; (3) the recorded move in `tests/fake_agent.py` does not do what the settled text says. There is no shape or pitch stop. The merge is the originator's.

This packet follows the guardian brief as this run gave it, which is the brief at the base. That brief has no `scenario_miss` field, so this packet has none. A missing field reads as `no`.

## The scenario

A slice that misses its own scenario, or breaks a decision that binds, goes back without a stop (#96). (1) The packet carries `scenario_miss` and a misses section. (2) A miss sends the slice back to the maker or the scenario agent, and `accept_moves` and `ready_to_merge` do not fire. (3) A numbered scenario point that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent. (4) Each send-back is recorded and shown in `xv prompt` and `xv decisions`. (5) The slice still stops when the budget is spent, when the same miss comes back, or when meeting the miss needs `amend: yes`. (6) The template shows the fields. (7) The wording says "old test files that existed at the base" (#102). Amendment 1 settles the `## Scenario misses` format, how lint treats misses, `amend: yes`, and the `xv decisions` rows. The slice may ignore nothing.

## The recording

None: this is a feature. To replay: `cd tests && python3 -m unittest test_orders test_packet test_run`. It was red at f959636. At HEAD the guardian ran it: 197 tests, OK. The maker and the cleaner each ran the whole suite green (588 tests).

## The boundary picture

From `.xv/slices/2026-10-30-scenario-miss.boundary.md`, as given: modules touched are `scripts/orders`, `scripts/packet` and `scripts/run`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none.

## What the suite asserts after

- `packet.lint` rejects a `scenario_miss` value other than yes or no and accepts a packet without the field.
- `packet.fix` moves a miss with no point or decision, or no evidence, to "Dropped". With no miss left, `scenario_miss` becomes `no`.
- The template and the guardian brief name the fields.
- With a miss: orders raise no stop and fire neither `accept_moves` nor `ready_to_merge`. A shape change still goes to two people. A spent budget stops with `budget_spent`.
- End to end: the slice goes to the maker with no open stop, and the maker's `xv prompt` shows the miss. A second identical miss stops for the originator, and so does `amend: yes`. `xv decisions` shows `scenario_miss` and `red_misses_point` rows.
- A scenario point that is not covered goes back to the scenario agent, and the same point again stops. A point in `not_covered` still stops.
- Both "old test files" messages are worded as point 7 asks.
- Old assertions: none changed. `tests/fake_agent.py` moved (below).

## 1. Shape

shape_change: no.

- The boundary picture lists no added module, edge, table, surface or outbound call, and no shape hints (`.xv/slices/2026-10-30-scenario-miss.boundary.md`, "Shape hints: none"). The three modules touched are ones `run` already reaches (`.xv/picture.md:21`).
- The new record field `scenario_miss` and the new recorded stops with `"seat": "watch"` (`scripts/run.py:570`) are state in the slice file. That is inside "State is files" (`.xv/picture.md:26`), so it is not a shape change. It does add a seat value the picture does not list (see 4).
- Breadth is narrow, the same as the forecast's `"shape": "narrow"` (`.xv/slices/2026-10-30-scenario-miss.md:11`, `forecast`).

## 2. Pitch

pitch_contradiction: no.

- Looked at `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` (not for people who will not trust agents; never a teapot). Sending a slice back without a person when it misses its own scenario serves the discipline and keeps people at the stops for amendments, stalls and budget. The pitch is silent on routing.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:76-84` | The fake guardian's packet had no `scenario_miss` line | It always writes `scenario_miss: no`, or `yes` plus a `## Scenario misses` line when `FAKE_SCENARIO_MISS` is set | The send-back tests need a packet with a miss. Sean accepted it at the `unrecorded_move` stop | Partly. A packet with a miss is forced. Writing `scenario_miss: no` when the variable is unset is not forced |

- The settled text says "unset, the packet is as before" (slice record, `stops[1].settled`). The diff does not match it. `tests/fake_agent.py:79-81` writes `scenario_miss: %s` with `"no"` on every run. Since Sean's answer makes the field optional, no end-to-end test now sends a packet without the field through `post_step` (`scripts/run.py:521-522`). That path is covered only by the lint unit test (`tests/test_packet.py`, `test_scenario_miss_must_be_yes_or_no`, last assertion). The fake does not assert less; its coverage moved.
- `git diff f9c5cb1..HEAD -- tests/test_orders.py tests/test_packet.py tests/test_run.py` shows only added lines: no old assertion changed. `xv wall diff` (baseline 7d1d71a) lists nothing changed, deleted or added. That baseline comes after the fake_agent change, so the record is the only place the move is kept.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

Proposed edits. The originator accepts them; the guardian does not write them.

- `.xv/picture.md:26`: after "After the scenario step, `red_misses_scenario` stops …", add: a numbered point of the scenario or an amendment that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent without a stop. The send-back is recorded as an answered stop with seat `watch` and order `red_misses_point`. The same point on the next pass stops for the originator. After the guardian, a packet with `scenario_miss: yes` and a kept `## Scenario misses` line, and no other stop, sends the slice to the maker, or to the scenario agent when a miss says `to: scenario`. The slice stops instead for a repeated miss, for `amend: yes`, or for a spent budget.
- `.xv/picture.md:33`: add "`scenario_miss` is `yes` or `no`, optional; missing reads as `no`."
- `.xv/picture.md:39`: the seats are listed as `originator`, `two_people` and `chief_engineer`. Add that `watch` appears as the seat on a send-back the watch recorded and answered itself (`scripts/run.py:570`). It is not a seat a person fills.
- `.xv/picture.md:23` ("`orders` holds the stop rules"): if decision 10 stays as it is (see 6), say that the no-stop send-back is computed in `run.py`'s `step`.

## 5. The wall

- `tests/test_orders.py:260` `test_the_scenario_step_names_old_test_files_that_existed_at_the_base_not_red_files` and `tests/test_run.py:476` `test_the_old_red_check_that_cannot_run_names_old_test_files_that_existed_at_the_base`: mark both slice-only. Each guards the one-time rewording of point 7 (#102) (`scripts/orders.py:105` and `scripts/run.py:468`, `-…red files…` / `+…old test files that existed at the base…`). Their `assertNotIn("red files")` guards a rename, not a behaviour.

## 6. Findings for the person (decisions that bind)

- **Decision 10, the routing is outside `orders.py`.** `.xv/picture.md:72` says "The standing orders all live in `scripts/orders.py`, a pure function of the record and the config." The watch's table now lists the send-back as a row of its standing orders (`skills/watch/SKILL.md:78-79`). But the choice to send back, and where to, is made in `scripts/run.py:401-411` (`elif agent == "scenario" and checks.get("missed_points")` and `elif agent == "guardian" and checks.get("misses")`). The misses are read only in `post_step` (`scripts/run.py:521-526`). Consequences:
  - `xv record packet` copies only `shape_change` and `pitch_contradiction` (`scripts/record.py:503`).
  - The session path (`xv record report` then `xv orders`, `skills/watch/SKILL.md:85`) never reads `scenario_miss`. A packet that lists misses there ends in `ready_to_merge` (`scripts/orders.py:234`, `if not out and not miss`).
- **The scenario-point match is undocumented and loose.** `scripts/run.py:555` counts a point as covered only in three cases: a `covers` or `not_covered` item contains the point's text, contains its first 40 characters, or is a substring of it that is at least 4 characters long. The scenario brief still says only `"item": "<an item the scenario names>"` (`skills/scenario/SKILL.md:56`, `:61`). It does not say that each numbered point must appear, or how to word it. Decision 2 (`.xv/picture.md:64`) says each brief "works as the whole prompt of a fresh context". Two effects:
  - A paraphrased item, such as "point 1: scenario_miss in front matter", fails the match. The slice goes back once and then stops as a stall.
  - A short generic item, such as "the guardian", matches any point that contains it.
- **A repeated miss depends on its wording.** `MISS_REF` (`scripts/packet.py:36`) keeps everything after the number up to the first `:`, `;` or `(`. So `- Point 1 is not met (evidence: …)` has the ref `point 1 is not met`. A second pass worded "Point 1 is still not met" does not match the repeat test at `scripts/run.py:526`. It is sent back again, and only the budget stops it (point 5). The template's `- 2: …` form avoids this (`skills/guardian/packet.md:59`).
- **Decision 1.** `.xv/picture.md:63` requires two people and a CHANGELOG line for a change to standing orders, a check or a brief. The line is at `CHANGELOG.md:7`. The repo runs solo (`.xv/picture.md:55`), and the line says "Sean decided it, solo". Looked at; nothing is missing.

## Door

**Door:** two-way. Code, briefs and docs only. The new `scenario_miss` field and the `watch`-seat stops are additive in the record, and a revert undoes them. **Blast radius:** watch-loop.

## Raw data

- Slice record: `.xv/slices/2026-10-30-scenario-miss.md`
- Diff: `git diff f9c5cb172de9480a62d1620c2a7e623ee4b0b5c5..701542c`
- Wall: `xv wall diff 2026-10-30-scenario-miss`
- Boundary: `.xv/slices/2026-10-30-scenario-miss.boundary.md` (`xv boundary --base f9c5cb172de9`)

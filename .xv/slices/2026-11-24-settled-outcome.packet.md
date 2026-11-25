---
slice: 2026-11-24-settled-outcome
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 2
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A settled not-covered outcome does not stop again (#205), re-pass 3

This is a re-pass over `3d23ad4..HEAD`, the changes from pairing 2 (`bcaea71`).
No shape stop and no pitch stop.
Pairing 2 closed four of the five leftovers from the last packet.
For the person:
- A second slice-new test was moved in pairing 2, with a record. It now reaches the case of point 2 that it was meant to cover. See check 3.
- Still open: decision 1 needs a second name on the CHANGELOG line (`CHANGELOG.md:7`: "decided by Sean Kennedy").

## The scenario

A not-covered outcome that a person settled does not stop again on a later test-writer pass.
1. An outcome settled in an answer does not stop again, however the later pass words it.
2. The same holds when the outcome was settled in an answer to another stop that bundled `red_misses_scenario`.
3. An outcome nobody settled still stops, on the same pass as a settled one.
4. A line in `CHANGELOG.md` (Sean settled that no test covers it).
5. Amendment to point 2: a send-back settles N only with `xv record answer --no-test N`.

May ignore: an outcome that the scenario amends after the answer.

## The recording

`.xv/recordings/rec-settled-outcome.md`.
To replay the red, run `cd tests && python3 -m unittest test_run.TestWriterChecksTest`. On HEAD I got `Ran 37 tests ... OK`.
I ran `python3 tests/run.py` on HEAD and got `Ran 1516 tests in shard 1/1 ... OK`.

## The boundary diagram

From `.xv/slices/2026-11-24-settled-outcome.boundary.md`: the modules touched are `scripts/record` and `scripts/run`. No modules, edges, tables or surface paths were added or removed. Shape hints: none.

## What the suite asserts after (new on this pass)

- `xv record answer --no-test seven` fails, its error names `--no-test 7`, and the stop stays unanswered (`tests/test_run.py:1580-1587`).
- Point 2 after a stop of another order: `unrecorded_move` is the stop on pass 1, and 7 fires with it. The person answers with `--bundle red_misses_scenario` and no send-back. On pass 2, 7 does not fire (`tests/test_run.py:1615-1628`).

## 1. Shape

shape_change: no.
- This pass adds one refusal to an existing flag (`scripts/record.py:612-614`: `if not re.match(r"\s*\d+\b", n): raise XVError(...)`). It adds no module, edge, table, stop key or flag. The boundary diagram has no shape hints.
- shape_breadth: narrow. The forecast expected narrow (`.xv/slices/2026-11-24-settled-outcome.md:13`: `"shape_breadth": "narrow"`).

## 2. Pitch

pitch_contradiction: no.
I checked the new refusal against `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` (who the pitch is not for).
Before this pass, a `--no-test` value with no number was recorded but settled nothing. Now it is refused (`scripts/record.py:614`). That fits "discipline".

## 3. Moved tests

Two moves, both of tests that this slice added, both in pairings, both with a record. Expected moves: none.
- Pairing 1, `test_a_not_covered_outcome_under_another_stop_still_stops_when_the_answer_does_not_bundle_it`. Nothing changed since the last packet. It went from 1 recorded stop to "7 is in `fired`". It is forced by point 3 (`.xv/slices/2026-11-24-settled-outcome.md:47`).
- Pairing 2, `test_a_not_covered_outcome_bundled_under_another_stop_is_settled_by_an_answer_without_a_send_back` (`.xv/slices/2026-11-24-settled-outcome.md:17`, `moved_tests[1]`, by Sean Kennedy).
  - Before: the setup used a `slice_only` mark, so `red_misses_scenario` was itself the stop. Pass 2 asserted `assertNotIn("did not cover 7", ...)` and `assertEqual(self.count_red_misses(), before)`.
  - After: the setup uses `FAKE_SCENARIO_EDITS_OLD`. It asserts that `unrecorded_move` is the stop (`tests/test_run.py:1622`) and that 7 fires with it (`tests/test_run.py:1623`). Pass 2 keeps `assertNotIn("did not cover 7", p.stdout)` (`tests/test_run.py:1628`). The `count_red_misses` assertion is gone.
  - Reason: "point 2 says an outcome settled in an answer to another stop that bundled red_misses_scenario does not stop again; the old setup did not reach that case".
  - Is it forced: yes. Point 2 is about another stop (`.xv/slices/2026-11-24-settled-outcome.md:46`: "the answer to another stop that bundled `red_misses_scenario`"). The old setup never reached that case.
  - Does it assert less? No. `xv wall diff` gives 584 → 587 for `tests/test_run.py`, with no `fewer_assertions`. With `unrecorded_move` as the stop, `count_red_misses` would stay the same whether 7 fired or not, so dropping it loses nothing. `assertNotIn` at `:1628` carries the check.
- These tests are not blind. I checked that they test behaviour. The bundled test and the pairing 1 test differ only in `--bundle`. One expects 7 on pass 2 and the other does not, so together they need `scripts/run.py:1332`. The refusal test checks the exit, the message, and that the stop has no answer. None restates the code.

Slice-only tests removed: none. Kept: none. `may_not_files_needed`: none.

## 4. The picture

- `.xv/picture.md:228`. Replace it with these lines:
  ```
    A `not_covered` outcome is settled by an earlier answered stop that did not send the slice back, when that stop is `red_misses_scenario` or the answer bundled `red_misses_scenario`.
    Every `red_misses_scenario` question that fired with such a stop counts (`fired_questions`).
    An outcome that starts with a number matches by that number, so "7", "7. A line" and "7. A line." are one outcome (`run.settled_outcome_numbers`).
    An answer that names an outcome with `xv record answer --no-test <N>` settles N, even when it sends the slice back; the flag repeats.
    `--no-test` refuses a value that does not start with an outcome number.
  ```
  The last line is new on this pass (`scripts/record.py:612-614`).
- `.xv/picture.md:133`, a new line after it: `  A stop keeps `fired_questions`, the questions of every `red_misses_scenario` that fired with it; an answer given with `--no-test <N>` keeps `no_test`.`

## 5. The wall

I checked the new test (`tests/test_run.py:1580-1587`) and the moved bundled test (`tests/test_run.py:1615-1628`). Both guard rules that keep holding: the refusal at `scripts/record.py:612-614` and point 2. Both should stay on the wall. No recommendations.

## Scenario misses

None.
Point 2 after another stop: `tests/test_run.py:1615-1628` passes on HEAD.
Point 4: `CHANGELOG.md:7` now names both ways an answer settles an outcome, and the refusal.
Point 5: the refusal at `scripts/record.py:612-614` uses the same pattern as `run.outcome_number` (`scripts/run.py:1319`: `r"\s*(\d+)\b"`). So every value that is accepted settles its number.

## Other findings for the person

- Closed by pairing 2. I checked each one in the diff:
  - The watch brief usage line now has `[--no-test <N>]` (`skills/watch/SKILL.md:56`).
  - `--no-test` with no number is refused (`scripts/record.py:612-614`).
  - The bundled test reaches the other-order case (`tests/test_run.py:1622`).
  - The CHANGELOG mentions bundled answers (`CHANGELOG.md:7`: "to a `red_misses_scenario` stop or to another stop that bundled it").
- Still open: decision 1 needs a second name on the CHANGELOG line (`.xv/picture.md:339`: "needs two people and a line in `CHANGELOG.md`"; `CHANGELOG.md:7`: "decided by Sean Kennedy"). The change touches the watch brief (`skills/watch/SKILL.md:56`), and decision 1 covers briefs.

## Door

**Door:** two-way. Reverting the commits removes the flag, its refusal, the number match and `fired_questions`. The old code ignores the extra stop keys. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-24-settled-outcome.md`
- Diff of this pass: `git diff 3d23ad4eb743..HEAD`
- Whole slice: `git diff 82a218f104bde75596fec4773887dc118aa50337..HEAD`
- Wall: `xv wall diff 2026-11-24-settled-outcome`
- Boundary: `.xv/slices/2026-11-24-settled-outcome.boundary.md`

## Pairings

- Pairing 1: Sean Kennedy with the watch (a session that was not named), because: agents went around three times on one test setup. Commits: 4cea58180b. Resumed at cleaner. Spend: not read (no session was named when the pairing opened); it is not in the slice's actual. Not blind (written or changed in the pairing): tests/test_run.py.
- Pairing 2: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: four small leftovers from the inspector: brief usage line, --no-test check, bundled test setup, CHANGELOG wording. Commits: bcaea71e32. Resumed at inspector. Spend: 17259 tokens (in 20, out 5272, cache write 11967; cache read 1283345 not counted), 10 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_run.py.

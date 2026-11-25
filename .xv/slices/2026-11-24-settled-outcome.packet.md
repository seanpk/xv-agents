---
slice: 2026-11-24-settled-outcome
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 0
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A settled not-covered outcome does not stop again (#205), re-pass

This is a re-pass over `10b2f1c..ea2595e`.
The earlier miss is fixed: a second not-covered outcome in one stop is now settled by an answer that does not send the slice back.
The fix goes too far, and that sends the slice back to the test writer.
An answer to another stop now settles every not-covered outcome that fired with that stop, even when the answer did not bundle `red_misses_scenario`.
So an outcome that no person settled no longer stops, which breaks point 3.
One new test does not reach the case it is named for.
No shape stop and no pitch stop.
Decision 1 still needs a second name on the CHANGELOG line (see the earlier packet's finding; nothing here changes it).

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
Replay the red with `cd tests && python3 -m unittest test_run.TestWriterChecksTest`. On HEAD it gives `Ran 35 tests ... OK`.
The whole suite on HEAD with `python3 tests/run.py` gives `Ran 1514 tests ... OK`.

## The boundary diagram

From `.xv/slices/2026-11-24-settled-outcome.boundary.md`: the modules touched are `scripts/record` and `scripts/run`. No modules, edges, tables or surface paths were added or removed. Shape hints: none.

## What the suite asserts after (new on this pass)

- Two not-covered outcomes, 7 and 8, stop together in one stop. An answer that does not send the slice back settles both, so neither stops again (`tests/test_run.py:1592`).
- A not-covered outcome 7 that fires on the same pass as a slice-only mark is settled by an answer with `--bundle red_misses_scenario` (`tests/test_run.py:1605`).
- No old assertion changed.

## 1. Shape

shape_change: no.
- This pass adds one key, `fired_questions`, to each stop (`scripts/record.py:1140-1141`). It sits beside the keys a stop already keeps (`also`, `bundle`; `.xv/picture.md:133`). It adds no module, edge or table. The boundary diagram has no shape hints.
- shape_breadth: narrow, the same as on the earlier pass. The forecast expected narrow (`.xv/slices/2026-11-24-settled-outcome.md:13`: `"shape_breadth": "narrow"`).

## 2. Pitch

pitch_contradiction: no.
I checked the change against `.xv/pitch.md:7` ("to vibe with discipline") and against who the pitch is not for (`.xv/pitch.md:25`). Neither line is touched. Note that settling a question the person never saw (see the miss below) works against "with discipline". It is a scenario miss, not a pitch contradiction.

## 3. Moved tests

None. `xv wall diff 2026-11-24-settled-outcome` gives `changed: []`, `deleted: []` and `fewer_assertions: []`. The new diff adds 30 lines to `tests/test_run.py` and removes none. The record has `moved_tests: []`.

Slice-only tests removed: none. Kept: none. `may_not_files_needed`: none.

## 4. The picture

- `.xv/picture.md:228`. This replaces the proposal in the earlier packet; when the miss below is fixed, its wording should follow the fix:
  ```
    A `not_covered` outcome is settled by an earlier answered stop that did not send the slice back, when that stop is `red_misses_scenario` or the answer bundled `red_misses_scenario`; every `red_misses_scenario` question that fired with the stop counts (`fired_questions`).
    An outcome that starts with a number matches by that number, so "7", "7. A line" and "7. A line." are one outcome (`run.settled_outcome_numbers`).
    An answer that names an outcome with `xv record answer --no-test <N>` settles N, even when it sends the slice back; the flag repeats.
  ```
- `.xv/picture.md:133`, a new line after it: `  A stop keeps `fired_questions`, the questions of every `red_misses_scenario` that fired with it; an answer given with `--no-test <N>` keeps `no_test`.`

## 5. The wall

I checked the two new tests (`tests/test_run.py:1592-1619`) against the scenario.
`test_a_second_not_covered_outcome_in_one_stop_is_settled_by_an_answer_without_a_send_back` guards a rule that keeps holding. It should join the wall.
`test_a_not_covered_outcome_bundled_under_another_stop_is_settled_by_an_answer_without_a_send_back` is aimed wrong; see Other findings. It should be fixed, not marked slice-only.
No old wall test is dead. No recommendations.

## Scenario misses

- 3: an outcome that no person settled stops again, but this pass makes it not stop when it fired under a stop of another order and the answer did not bundle `red_misses_scenario`. Evidence: `scripts/record.py:1140-1141` stores every `red_misses_scenario` question on the stop, whatever the stop's order: `"fired_questions": [f["question"] for f in v["fired"] if f["order"] == "red_misses_scenario"]`. `scripts/run.py:1330-1335` settles every number in those questions whenever the answer did not send back (`if not s.get("sendback"): questions = list(s.get("fired_questions") or [])`). It never reads the answer's `bundle`. An answer records which orders it answered in `bundle` (`scripts/record.py:1374`: `--bundle`, "comma-separated orders the same reply answered"). The watch shows the person only the stop's own question (`skills/watch/SKILL.md:33`: "which order fired, which seat it is for, and the question"). Here is a case that reaches it: at the test-writer step, `unrecorded_move` fires before `red_misses_scenario` (`scripts/orders.py:188-205`), and both are for the originator. `verdict` picks the first stop with the highest seat (`scripts/orders.py:471`, `max(blocking, key=lambda f: SEAT_RANK[f["seat"]])`), so `unrecorded_move` is the stop and "did not cover 7" rides in `fired_questions`. The person answers the old-test question with `--next maker` and no `--bundle`. On a later test-writer pass, 7 does not stop. Before this pass, 7 would have stopped, because only a `red_misses_scenario` stop's own question was read. No red test answers such a stop without `--bundle red_misses_scenario` and then checks that the outcome still stops. (to: test-writer)

## Other findings for the person

- `test_a_not_covered_outcome_bundled_under_another_stop_is_settled_by_an_answer_without_a_send_back` (`tests/test_run.py:1605-1619`) never puts `red_misses_scenario` under another stop. `red_misses_scenario` for 7 fires before `slice_only_marks` (`scripts/orders.py:203-205` comes before `219`), both are for the originator, and `max` keeps the first (`scripts/orders.py:471`). So the stop is `red_misses_scenario` with "did not cover 7" as its own question. The test checks the same case as `test_a_settled_outcome_reported_by_its_number_alone_does_not_stop_again`. The test writer's report says so: "A second test for a bundled red_misses_scenario under another stop passes already" (record log, 2026-11-24T23:05:41). To reach the case, the other stop has to come first, for example `unrecorded_move` via `old_red_changed`.
- From the earlier packet, still open: decision 1 needs a second name on the CHANGELOG line (`.xv/picture.md:339`, `CHANGELOG.md:3`). `--no-test` with no leading number is recorded but settles nothing (`scripts/run.py:1336-1338`). The usage line of the watch brief (`skills/watch/SKILL.md:56`) does not list `--no-test`.

## Door

**Door:** two-way. A revert removes the flag, the number match and `fired_questions`. The old code ignores the extra stop keys. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-24-settled-outcome.md`
- Diff of this pass: `git diff 10b2f1c3db181c8ee09ba3f1ab2580bf8c2feb27..ea2595e19039824f00f1c30e5958a36508f636c7`
- Whole slice: `git diff 82a218f104bde75596fec4773887dc118aa50337..HEAD`
- Wall: `xv wall diff 2026-11-24-settled-outcome`
- Boundary: `.xv/slices/2026-11-24-settled-outcome.boundary.md`

## Pairings

- Pairing 1: Sean Kennedy with the watch (a session that was not named), because: agents went around three times on one test setup. Commits: 4cea58180b. Resumed at cleaner. Spend: not read (no session was named when the pairing opened); it is not in the slice's actual. Not blind (written or changed in the pairing): tests/test_run.py.

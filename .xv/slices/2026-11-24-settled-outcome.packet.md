---
slice: 2026-11-24-settled-outcome
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 1
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: A settled not-covered outcome does not stop again (#205), re-pass 2

This is a re-pass over `ea2595e..3d23ad4`.
The point 3 miss from the last pass is fixed.
`fired_questions` now settles outcomes only when the answered stop is `red_misses_scenario` or the answer bundled it.
No shape stop and no pitch stop.
For the person:
- One slice-new test was moved in pairing 1. It now checks that 7 fires, not that a stop is recorded. The scenario allows this; see check 3.
- No test answers a stop of another order with `--bundle red_misses_scenario` and checks that 7 is settled. The code does handle that case.
- Decision 1 still needs a second name on the CHANGELOG line. Nothing on this pass changes that.

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
To replay the red, run `cd tests && python3 -m unittest test_run.TestWriterChecksTest`. On HEAD it gives `Ran 36 tests ... OK`.
The cleaner's whole-suite run gives `Ran 1515 tests ... OK` (record, `checks.cleaner.suite_output`).

## The boundary diagram

From `.xv/slices/2026-11-24-settled-outcome.boundary.md`: the modules touched are `scripts/record` and `scripts/run`. No modules, edges, tables or surface paths were added or removed. Shape hints: none.

## What the suite asserts after (new on this pass)

- 7 is not covered. The stop is `unrecorded_move`, and 7 rides along as an extra fire. The person answers with no `--bundle` and no send-back. On the next pass, `red_misses_scenario` for 7 is in the fired list again (`tests/test_run.py:1620-1635`).
- The test also checks that its setup really makes `unrecorded_move` the stop (`tests/test_run.py:1627`: `self.assertEqual(json.loads(p.stdout)["stop"]["order"], "unrecorded_move")`). The earlier setup missed this case.

## 1. Shape

shape_change: no.
- This pass changes one condition in `settled_outcome_numbers` (`scripts/run.py:1331-1333`). It adds no module, edge, table or stop key. The boundary diagram has no shape hints.
- shape_breadth: narrow. The forecast expected narrow (`.xv/slices/2026-11-24-settled-outcome.md:13`: `"shape_breadth": "narrow"`).

## 2. Pitch

pitch_contradiction: no.
I checked the change against `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` (who the pitch is not for).
The fix keeps an outcome open until a person answers its question (`scripts/run.py:1332`: `if "red_misses_scenario" in [s.get("order"), *(s.get("bundle") or [])]:`). That works with "discipline", not against it.

## 3. Moved tests

One test was moved. It is a test that this slice added: it is not in base `82a218f`, but it is in the wall baseline `8305b16`.
- `tests/test_run.py` `test_a_not_covered_outcome_under_another_stop_still_stops_when_the_answer_does_not_bundle_it`, moved by Sean Kennedy in pairing 1 (record `moved_tests`).
  - Before: on pass 2, `self.assertIn("did not cover 7", p.stdout)` and `self.assertEqual(self.count_red_misses(), before + 1)`. The setup used a `slice_only` mark. With that mark, `red_misses_scenario` was itself the stop, so the test never reached its case.
  - After: the setup uses `FAKE_SCENARIO_EDITS_OLD`, and the test asserts that `unrecorded_move` is the stop (`tests/test_run.py:1627`). On pass 2 it asserts that `red_misses_scenario` for 7 is in `fired` (`tests/test_run.py:1634-1635`).
  - Reason: "point 3 says an unsettled outcome still fires red_misses_scenario; unrecorded_move stays primary, so 7 fires as also and is not recorded as its own stop". Sean picked this in the stop answered 2026-11-25T02:41:19, option 1.
  - Is it forced: yes. Point 3 says the outcome "still fires `red_misses_scenario`" (`.xv/slices/2026-11-24-settled-outcome.md:47`). It does not say the outcome becomes the stop. `unrecorded_move` fires again on pass 2 and wins, so `red_misses_scenario` cannot be counted as a recorded stop.
  - Does it assert less? Partly. `xv wall diff` gives 584 → 583 assertions for `tests/test_run.py` (`fewer_assertions`). The test no longer checks that a stop is recorded. Nothing checks that pass 2's stop keeps "did not cover 7" in `fired_questions`. A later bundled answer needs that key to settle 7.
- This test was written in a pairing and is not blind. Its assertions check behaviour; none restates the code. Without this pass's change at `scripts/run.py:1332`, an answer with no `--bundle` would settle 7 and pass 2 would fail. The test writer's red at 2026-11-25T02:35:53 records that failure.

Slice-only tests removed: none. Kept: none. `may_not_files_needed`: none.

## 4. The picture

- `.xv/picture.md:228`. Replace it with these lines; the code now matches them:
  ```
    A `not_covered` outcome is settled by an earlier answered stop that did not send the slice back, when that stop is `red_misses_scenario` or the answer bundled `red_misses_scenario`.
    Every `red_misses_scenario` question that fired with such a stop counts (`fired_questions`).
    An outcome that starts with a number matches by that number, so "7", "7. A line" and "7. A line." are one outcome (`run.settled_outcome_numbers`).
    An answer that names an outcome with `xv record answer --no-test <N>` settles N, even when it sends the slice back; the flag repeats.
  ```
- `.xv/picture.md:133`, a new line after it: `  A stop keeps `fired_questions`, the questions of every `red_misses_scenario` that fired with it; an answer given with `--no-test <N>` keeps `no_test`.`

## 5. The wall

I checked the moved test (`tests/test_run.py:1620-1635`) against point 3. It guards a rule that keeps holding, so it should stay on the wall. No recommendations.

## Scenario misses

None.
Point 3: `tests/test_run.py:1620-1635` passes on HEAD. It needs the `bundle` check at `scripts/run.py:1332`.
Point 2, after a stop of another order: `scripts/run.py:1332` takes `fired_questions` when `bundle` holds `red_misses_scenario`. See the first finding below for the test gap.

## Other findings for the person

- No test reaches point 2 after a stop of another order. `test_a_not_covered_outcome_bundled_under_another_stop_is_settled_by_an_answer_without_a_send_back` (`tests/test_run.py:1606-1619`) still uses the `slice_only` setup. In that setup `red_misses_scenario` is itself the stop, as the last packet said. The moved test proves `FAKE_SCENARIO_EDITS_OLD` reaches the other-order case (`tests/test_run.py:1627`). The bundled test could use that setup and answer with `--bundle red_misses_scenario`.
- Still open from the earlier packets:
  - Decision 1 needs a second name on the CHANGELOG line (`.xv/picture.md:339`, `CHANGELOG.md:7`: "decided by Sean Kennedy").
  - `--no-test` with no leading number is recorded but settles nothing (`scripts/run.py:1338-1340`).
  - The watch brief's usage line (`skills/watch/SKILL.md:56`) does not list `--no-test`. Line 61 tells the watch to pass it.
- `CHANGELOG.md:7` says an outcome is settled "in a `red_misses_scenario` answer". It does not mention an answer to another stop that bundles `red_misses_scenario`, which this slice also settles (`scripts/run.py:1332`).

## Door

**Door:** two-way. Reverting the commits removes the flag, the number match and `fired_questions`; the old code ignores the extra stop keys. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-24-settled-outcome.md`
- Diff of this pass: `git diff ea2595e19039824f00f1c30e5958a36508f636c7..HEAD`
- Whole slice: `git diff 82a218f104bde75596fec4773887dc118aa50337..HEAD`
- Wall: `xv wall diff 2026-11-24-settled-outcome`
- Boundary: `.xv/slices/2026-11-24-settled-outcome.boundary.md`

  - Why: agents went around three times on one test setup.
  - Commits: 4cea58180b. The slice resumed at the cleaner.
  - Spend: not read, because no session was named when the pairing opened. It is not in the slice's actual spend.
  - Not blind (written or changed in the pairing): `tests/test_run.py`. Check 3 covers it.

## Pairings

- Pairing 1: Sean Kennedy with the watch (a session that was not named), because: agents went around three times on one test setup. Commits: 4cea58180b. Resumed at cleaner. Spend: not read (no session was named when the pairing opened); it is not in the slice's actual. Not blind (written or changed in the pairing): tests/test_run.py.
- Pairing 2: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: four small leftovers from the inspector: brief usage line, --no-test check, bundled test setup, CHANGELOG wording. Commits: bcaea71e32. Resumed at inspector. Spend: 17259 tokens (in 20, out 5272, cache write 11967; cache read 1283345 not counted), 10 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_run.py.

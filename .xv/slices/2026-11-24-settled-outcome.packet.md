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

# Packet: A settled not-covered outcome does not stop again (#205)

One scenario miss sends the slice back to the test writer.
When one test-writer pass leaves two or more outcomes not covered, the stop keeps only the first one's question.
So an answer that does not send the slice back settles only that first number, and the others stop again.
That is point 2's case without a send-back, and #205's own pattern.
No shape stop and no pitch stop.
Separately, decision 1 needs a second person: the slice changes a brief and a check.

## The scenario

A not-covered outcome that a person settled does not stop again on a later test-writer pass.
1. An outcome settled in an answer does not stop again, however the later pass words it ("7", "7. A line in CHANGELOG.md", "7. A line in CHANGELOG.md.").
2. The same holds when the outcome was settled in an answer to another stop that bundled `red_misses_scenario`.
3. An outcome nobody settled still stops, on the same pass as a settled one.
4. A line in `CHANGELOG.md`. Sean settled that no test covers it.
5. Amendment to point 2: an answer that sends the slice back settles N only when it names N with `xv record answer --no-test N` (the flag can repeat). A send-back without the flag still stops again. The watch brief says to pass `--no-test`.

May ignore: an outcome that the scenario amends after the answer.

## The recording

`.xv/recordings/rec-settled-outcome.md` has two slices from main where outcome 7, and points 5 and 13, stopped again three times after Sean settled them.
Replay the red with `cd tests && python3 -m unittest test_run.TestWriterChecksTest`. It failed on the base (`unrecognized arguments: --no-test 7`). On HEAD it passes.
I ran the whole suite on HEAD with `python3 tests/run.py`: `Ran 1512 tests ... OK`.

## The boundary diagram

From `.xv/slices/2026-11-24-settled-outcome.boundary.md`: modules touched are `scripts/record` and `scripts/run`. No modules, edges, tables or surface paths were added or removed. No shape hints.

## What the suite asserts after

- An outcome settled by an answer that did not send the slice back does not stop again whether the later pass words it as "7", "7. …" or "7. ….". A different number, "17", still stops.
- An unsettled outcome, 8, stops on the same pass where a settled 7 does not.
- An answer that sends the slice back with `--no-test 7` (direct or bundled) settles 7 however it is later worded. `--no-test 7 --no-test 8` settles both. `--no-test 7` leaves 8 stopping.
- A bundled send-back without `--no-test` stops again when 7 comes back. The old test `test_a_not_covered_item_the_person_sent_back_stops_again_when_reported_again` is unchanged.
- `skills/watch/SKILL.md` contains `xv record answer` and `--no-test`.
- No old assertion changed.

## 1. Shape

shape_change: no.
- The boundary diagram shows no added module, edge, table or surface (`.xv/slices/2026-11-24-settled-outcome.boundary.md`, "Shape hints: none").
- The new flag is one more option on an existing command (`scripts/record.py:1373`: `s.add_argument("--no-test", dest="no_test", action="append", metavar="N", …)`). Each stop gets one more key, `no_test` (`scripts/record.py:648`: `stop["no_test"] = [...]`). Both fit the shape that already exists: the record keys `bundle` and `sendback_to` (`.xv/picture.md:133`), and the answer flags `--bundle` and `--accept-wall`.
- shape_breadth: narrow. The forecast was narrow, but its note expected only "the red_misses_scenario settled-outcome check, its tests, and one CHANGELOG line". The flag in `scripts/record.py` and the brief paragraph in `skills/watch/SKILL.md:61` came from amendment 5, which was made after the forecast. Neither widens the shape.

## 2. Pitch

pitch_contradiction: no.
The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`). Stopping the person fewer times on a question they already settled serves that line. Nothing in the change touches "who it is not for" (`.xv/pitch.md:25`).

## 3. Moved tests

None. `xv wall diff 2026-11-24-settled-outcome` reports `changed: []`, `deleted: []` and `fewer_assertions: []`. `git diff 82a218f..HEAD -- tests` removes no lines. The record has `moved_tests: []` and `old_tests_to_move: []`.

Slice-only tests removed: none. Kept: none. `may_not_files_needed`: none.

## 4. The picture

- `.xv/picture.md:228` is now incomplete: outcomes are matched by number, and `--no-test` settles them even on a send-back. Proposed replacement:
  ```
    A `not_covered` outcome named in an earlier answered `red_misses_scenario` stop does not stop again, unless that answer sent the slice back (`sendback`).
    An outcome that starts with a number matches by that number, so "7", "7. A line" and "7. A line." are one outcome (`run.settled_outcome_numbers`).
    An answer that names an outcome with `xv record answer --no-test <N>` settles N, even when it sends the slice back; the flag repeats.
  ```
- `.xv/picture.md:133` lists the keys an answer keeps. Proposed new line after it: `  An answer given with `--no-test <N>` keeps `no_test`, a list of the outcomes it settled as having no test.`
- If the miss below is fixed by keeping every fired question on the stop (`scripts/record.py:1137-1138`), `.xv/picture.md:228` should also say that each outcome bundled into the stop is settled, not only the first.

## 5. The wall

I checked the twelve new tests in `tests/test_run.py:1484-1589` against the scenario. Each one guards an ongoing rule: a check, a flag, or a brief line, the same kind as the brief tests already on the wall. None guards a one-time change, and none only restates another. No old wall test is dead: the one the amendment protects is unchanged. No recommendations.

## Scenario misses

- 2 (without a send-back): an outcome bundled as the second or a later `red_misses_scenario` fire on one pass is not settled when a person answers that stop without sending it back. It stops again on the next pass. Evidence: `scripts/record.py:1137-1138` stores only the primary fire's `"question": st["question"]` and puts the others in `"also": [f["order"] for f in v["fired"] if f is not st]`, so outcome 8's text is lost. `scripts/run.py:1331` (`nums.update(re.findall(r"did not cover (\d+)\b", s.get("question") or ""))`) reads only that one question. `scripts/orders.py:203-205` fires one `red_misses_scenario` per not-covered outcome. The same happens when the primary stop is another order that bundles `red_misses_scenario` (for example `slice_only_marks`, `unrecorded_move`): its question has no "did not cover", so no number is settled. The old text match had the same blind spot. No red test has two not-covered outcomes in one stop answered without a send-back; `test_an_unsettled_outcome_still_stops_on_the_same_pass_as_a_settled_one` settles 7 on an earlier pass. (to: test-writer)

## Other findings for the person

- Decision 1: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:339`). This slice changes the watch brief (`skills/watch/SKILL.md:61`) and the `red_misses_scenario` check (`scripts/run.py:1183-1186`). The CHANGELOG line names one person: "(#205, decided by Sean Kennedy)" (`CHANGELOG.md:7`). It is under `## Unreleased`, and the file says "A version line without two names is a draft" (`CHANGELOG.md:3`). A second name is needed before release.
- `--no-test` takes any string and quietly ignores one that does not start with a number. `scripts/run.py:1332-1334`: `for n in s.get("no_test") or []: if outcome_number(n): ...`. `scripts/record.py:648` stores it without checking it. A typo such as `--no-test seven` is recorded as settled but settles nothing, and the outcome stops again. Decision 12 (`.xv/picture.md:366`) covers broken check input; this is answer input, so it is a note, not a miss.
- The usage line of the watch brief (`skills/watch/SKILL.md:56`) lists `[--bundle …]` but not `[--no-test <N>]`. The flag is only in the new paragraph at line 61.

## Door

**Door:** two-way. A revert removes the flag and the number match; a stop that kept a `no_test` key is ignored by the old code. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-24-settled-outcome.md`
- Diff: `git diff 82a218f104bde75596fec4773887dc118aa50337..10b2f1c3db181c8ee09ba3f1ab2580bf8c2feb27`
- Wall: `xv wall diff 2026-11-24-settled-outcome`
- Boundary: `xv boundary --base 82a218f104bde75596fec4773887dc118aa50337`

---
slice: 2026-10-30-test-marks
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: workflow
---

# Packet: A person sees which tests stay on the wall and which leave it (second pass)

Nothing here stops the change for two people. Three things need Sean, as the person who set the work going:

1. **Your slice-only decision was lost.** At the last stop you accepted that `test_the_guardian_brief_has_five_checks` is marked slice-only. The record's `slice_only` is `[]`. The scenario re-run at `c718f14` replaced the list with its own report, `slice_only: []`. That also dropped the earlier mark on the README test (record history at `c718f14`: `-slice_only: [{... "test_the_readme_says_five_checks_not_four" ...}]`, `+slice_only: []`). The code does this at `scripts/record.py:436-437`: every scenario report overwrites `slice_only`. An `xv record unmark` is undone the same way the next time the scenario runs. So the cleaner kept the test, and it is now in the wall baseline (`wall_baseline.commit: c05e27e`).
2. **Your usual answer still accepts every recommendation.** `r["accepted"] = r in named or not named` (`scripts/record.py:340`). If the answer names no test, for example "B: 1" (how every stop on this record was answered), every recommendation is set accepted. The amendment says "an answer does not set every one accepted" (record, Amended 2026-10-29, item 1). The match only looks for the test's name in the words of the answer (`:337-338`). So "accept test_keep_me, refuse test_drop_me" accepts both. The text of a picked option's `settled` is never read either. The test avoids both cases: it says "refuse the other" (`tests/test_record.py:940`).
3. **Binding decision 1 has no decision entry.** This changes a standing order and two briefs, which "needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:61`). The line is there (`CHANGELOG.md:7`, "Sean decided it, solo"). But the record's `decisions` is `[]`, and with shape and pitch both `no`, no order raises the two-people stop.

The merge is Sean's.

## The scenario

1. After the scenario step, a new order for the person who set the work going fires only when the scenario marks slice-only tests. It lists each marked test with its reason. The person accepts the marks or unmarks a test so it joins the wall. No marks means no stop. The watch's stop table and the README's list the new order.
2. The guardian has a fifth check, wall recommendations, and the packet has a section for them. The recommendations reach the person in `accept_moves`, and the record keeps which ones they accepted. The docs say "five checks".
3. Amended: an `accept_moves` answer accepts only the recommendations it names, and records the rest as refused. `xv record unmark <id> --test <name>` takes a test off `slice_only`. A move whose assertion starts with a marked name keeps its `slice_only` flag.

## The recording

None: this is a feature. To replay it, run `cd tests && python3 -m unittest test_orders test_record.WallChoicesTest`. It was red at `c718f14`: 9 failures and 3 errors, `invalid choice: 'unmark'` (`checks.scenario.red_output`). At HEAD `d55c1fd` I ran it: 40 tests, OK. After the cleaner, the whole suite was 408 tests, OK (`checks.cleaner.suite_output`).

## The boundary picture

From `.xv/slices/2026-10-30-test-marks.boundary.md`, as given: it touches `scripts/orders` and `scripts/record`. It adds or removes no module, edge, outbound call, table or surface path. Shape hints: none.

## What the suite asserts after

- **Slice-only marks.** After the scenario step, marks raise an `originator` stop that names each test and its reason and says "unmark". No marks means no stop (`tests/test_orders.py` `test_slice_only_marks_…`, `test_no_slice_only_marks_…`, `test_unmarking_…`).
- **Wall recommendations.** An open recommendation raises `accept_moves`. An accepted or refused one gives `ready_to_merge` (`test_a_wall_recommendation_waits…`, `test_accepted_…`, `WallChoicesTest.test_a_refused_…`). `apply_report` keeps the guardian's `wall_recommendations` (`test_the_record_keeps_…`).
- **Answers and marks.** An answer naming one of two recommendations accepts that one and refuses the other. `unmark` takes off one mark and fails on an unmarked test. A move whose assertion starts with a marked name keeps the flag, and one for another test does not (`tests/test_record.py` `WallChoicesTest`).
- **Docs.** The stop tables, `docs/slice-record.md`, the guardian brief (five checks) and the packet template (`## 5. `) say the new things.
- **Not asserted:** an answer that names no test, an answer that names a test in order to refuse it, and a scenario re-run keeping earlier marks or unmarks.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`forecast.shape: "narrow"`).

- No new module, edge, table or surface (boundary picture, above). Shape hints: none.
- The new order is in `scripts/orders.py:114-120`, where binding decision 10 puts every standing order (`.xv/picture.md:70`).
- `wall_recommendations` (`scripts/record.py:27`, `:31`) is a new field in the slice file. "State is files" (`.xv/picture.md:26`), so it adds no table.
- `xv record unmark` (`scripts/record.py:170-178`, `:648-652`) is a new subcommand on an existing surface, "the `xv` CLI" (`.xv/picture.md:27`). It changes nothing in the shape.

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:7` ("vibe with discipline") and the not-for line at `.xv/pitch.md:25`. The change gives a person more say over the wall and serves no one the pitch excludes.

## 3. Moved tests

`xv wall diff 2026-10-30-test-marks` (baseline `c05e27e`): nothing changed, deleted or added, and no file has fewer assertions.

| File | Before | After | Why (record) | Forced? |
| --- | --- | --- | --- | --- |
| `tests/test_orders.py` | `test_the_readme_says_five_checks_not_four` (added by this slice at `58ac3df`) | removed at `3c5362b` | "guards a one-time wording change from four to five in the README" (cleaner) | Not forced. Sean accepted it at the last `accept_moves` (record, stop 3, `settled`). |

- **Slice-only tests removed:** `test_the_readme_says_five_checks_not_four`. The `moved_tests` entry still has no `slice_only: true`, and the mark it would match is gone (finding 1). So `scripts/orders.py:190` counts it as an ordinary old-test move again.
- **Kept:** `test_the_guardian_brief_has_five_checks` (`tests/test_orders.py:237`). The cleaner had no mark to act on, so it kept the test without giving a reason to keep it (finding 1).
- **Wall re-based mid-slice:** the baseline moved from `28dfb65` to `58ac3df` to `c05e27e` (`.xv/slices/2026-10-30-test-marks.md`, `wall_baseline`, and its history at `606efa8` and `c718f14`). `c05e27e` is after the first pass, so the slice's own first-round tests now count as wall tests. Removing one of them now needs a recorded move.

## 4. The picture

picture_change: yes. Proposed edits:

- **`.xv/picture.md:23`** ("`orders` holds the stop rules"): add that `slice_only_marks` stops for the originator after the scenario step when the record lists `slice_only` tests, and that the guardian's `wall_recommendations` go to the originator in `accept_moves`.
- **`.xv/picture.md:26`** (state in the slice file): add that the record keeps `slice_only` and `wall_recommendations`, each with `accepted` and `refused` flags, set from the words of the `accept_moves` answer. Also add that `xv record unmark` removes a mark, and that a scenario report replaces the whole `slice_only` list.
- **`.xv/picture.md:16`** (seats): no change. The new order uses `originator`.

## 5. The wall

I read the 17 tests this slice adds (`tests/test_orders.py:161-252`, `tests/test_record.py:916-981`) and the record's `slice_only` list.

- **`tests/test_orders.py::test_the_guardian_brief_has_five_checks` should stay off the wall.** It is still there and is now in the baseline. Its `assertNotIn("four checks", text)` guards the one-time wording change. Its heading assert is repeated by `test_the_fifth_check_names_the_three_recommendations`, which splits on `## The five checks`. Sean already accepted this (record, stop 3, `settled`).
- **No test that was on the wall before the slice should be removed.** `xv wall diff` shows no change to a pre-slice test.
- **The six `WallChoicesTest` tests and the docs-table tests stay.** I make no recommendation for them.

This run's prompt carried the four-check brief from the main checkout. This section follows the slice's own brief (`skills/guardian/SKILL.md` check 5).

## Door

**Door:** two-way. A revert undoes the order, the subcommand, the record field and the docs. Old code ignores records that already hold `wall_recommendations`. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md` (history: `git log -p 5ec1d86..HEAD -- .xv/slices/2026-10-30-test-marks.md`)
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..d55c1fd`
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `c05e27e`)
- Boundary: `.xv/slices/2026-10-30-test-marks.boundary.md`

## From the cleaner

- Shape proposal, for people: A shared helper for matching a test name inside a string, now written twice in scripts/record.py (cmd_move and cmd_answer) with slightly different regexes; it would be a new concept, so left for the packet.

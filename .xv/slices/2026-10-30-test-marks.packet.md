---
slice: 2026-10-30-test-marks
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 3
door: two-way
blast_radius: workflow
---

# Packet: A person sees which tests stay on the wall and which leave it (sixth pass)

Nothing here needs two people. The merge is Sean's. All three changes in the fifth amendment are in the code and have tests (C, E and F from the fifth pass are fixed). These need a decision from Sean:

1. **The accepted slice-only mark is gone from the record again.** `slice_only` is `[]` (`.xv/slices/2026-10-30-test-marks.md:16`). The amendments say it holds `test_the_guardian_brief_has_five_checks` at the merge stop (`:54`, `:63`). See finding I.
2. **Two amendments now disagree.** One says every unflagged recommendation is refused (`:53`). The other says only `--refuse-wall` refuses (`:88`). The code follows the first. See finding J.
3. **Nothing has run live yet.** There is no `slice_only_marks` stop and no `wall_recommendations` in this record. The first green run is still owed.
4. Small items carried over: D, G, H.

## The scenario

There are two parts (#87, #89):

1. After the scenario step, `slice_only_marks` stops for the person who set the work going whenever there are slice-only marks. The person accepts them, or runs `xv record unmark`.
2. The guardian has a fifth check, the wall. Its recommendations reach the same person in `accept_moves`. Only `--accept-wall` accepts one, and only `--refuse-wall` takes back an earlier acceptance. Each answered `accept_moves` stop keeps `accepted_wall` and `refused_wall`.

New this pass (`.xv/slices/2026-10-30-test-marks.md:86-90`):

- The record never takes `refused` from a guardian report.
- A wall flag on any other kind of stop is an error.
- Naming the same test with both flags is an error.

It may ignore rewording the site, and moving slice-only tests out of the cleaner.

## The recording

None; this is a feature. To replay the red: `cd tests && python3 -m unittest test_record test_orders`. I ran the whole suite at HEAD `62c7723` (`cd tests && python3 -m unittest -q`): `Ran 438 tests in 100.467s`, `OK`.

**The first green run is still owed.** The record has no `slice_only_marks` stop in `stops` and no `wall_recommendations` field (`.xv/slices/2026-10-30-test-marks.md:15-27`). The watch running this slice is not this branch's code. Before merging, try three things:

- Answer a `ready_to_merge` stop with `--accept-wall X`. It should exit 2, and the stop should stay open.
- On an `accept_moves` stop, give `--accept-wall X --refuse-wall X`. It should exit 2.
- Re-run the guardian with `"refused": true` in its report. Nothing should show as refused.

## The boundary picture

Taken as given from `.xv/slices/2026-10-30-test-marks.boundary.md`. It touches `scripts/orders` and `scripts/record` (`:11`). No modules, edges, tables, surfaces or outbound calls are added or removed (`:12-19`, `:106-114`). Shape hints: none (`:7`).

## What the suite asserts after

- Everything from the fifth pass still holds:
  - `slice_only_marks` fires only when there are marks, `unmark` removes one, and a scenario re-run keeps the marks.
  - `--accept-wall` accepts only the tests it names. `--refuse-wall` takes back an earlier acceptance. The answer's words are never read.
  - Each answered `accept_moves` stop keeps its own `accepted_wall` and `refused_wall`.
- New this pass (`tests/test_record.py:1190-1245`):
  - A guardian report that marks its own recommendation `refused` changes nothing.
  - A guardian re-run cannot refuse what the person accepted.
  - `--accept-wall` or `--refuse-wall` on a `scenario_stopped` stop exits non-zero, names the flag, and leaves the stop unanswered.
  - Both flags on one test exits non-zero, names the test, accepts nothing, and leaves the stop unanswered.
- No test line was removed this pass. `git diff f1ac8d5..HEAD -- tests` only adds lines.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`.xv/slices/2026-10-30-test-marks.md:11`, `"shape": "narrow"`).

- The boundary picture has no new module, edge, table or surface, and no shape hints (`.xv/slices/2026-10-30-test-marks.boundary.md:7`, `:18-19`).
- This pass changes only `scripts/record.py:336-345` (checking the flags in `cmd_answer`) and `:458-465` (the guardian branch of `apply_report`). `record` "owns the slice record" (`.xv/picture.md:23`).
- The two new errors are refusals on an existing surface, the `xv` CLI (`.xv/picture.md:27`). They exit 2, which matches "2 an error or a refusal" (`.xv/picture.md:71`).

## 2. Pitch

pitch_contradiction: no. I checked three lines:

- `.xv/pitch.md:7`: "to vibe with discipline".
- `.xv/pitch.md:21`: who adopts it.
- `.xv/pitch.md:25`: "not for people or projects that will not trust agents to write production code".

None of them conflicts with an agent being unable to answer for the person, or with contradictory flags being refused.

## 3. Moved tests

No test that existed at the base `5ec1d86` changed. `xv wall diff 2026-10-30-test-marks` (baseline `f1ac8d5`) reports nothing changed, deleted, added or with fewer assertions. The three recorded moves are all on tests born in this slice:

| File | Before → after | Why (the record) | Forced? |
| --- | --- | --- | --- |
| tests/test_orders.py | `test_the_readme_says_five_checks_not_four` → removed (cleaner) | "a one-time wording change" | Sean accepted it (`.xv/slices/2026-10-30-test-marks.md:43`) |
| tests/test_record.py | `test_an_answer_that_names_one_recommendation_accepts_only_that_one` (the words accept one) → removed (maker) | "the answer's words are never read" | Yes (`:53`). `AcceptWallFlagTest` covers the flag |
| tests/test_orders.py | `test_the_guardian_brief_has_five_checks` → removed (cleaner) | "accepted as slice-only" | Yes (`:43`, `:63`) |

Slice-only tests removed: `tests/test_orders.py::test_the_guardian_brief_has_five_checks`. Kept: none.

**Finding D (carried): two problems in the record's moves.**

- The cleaner's slice-only move at 02:38:15 has no `slice_only: true` (`.xv/slices/2026-10-30-test-marks.md:15`). So `scripts/orders.py:190` counts it as an old moved test.
- The maker's move is recorded twice, at 02:06:23 and 02:08:07 (`.xv/slices/2026-10-30-test-marks.md:15`).

The missing flag follows from finding I. `scripts/record.py:188-192` sets the flag only when the test is listed in `slice_only`, and the list is empty.

**Finding I (new): the accepted mark was wiped a second time, with no log line.** The red commit `7ff0b66` (scenario step, 03:43) changed the record's line 16 from `slice_only: [{"file": "tests/test_orders.py", "test": "test_the_guardian_brief_has_five_checks", ...}]` to `slice_only: []`. No `unmark` line appears in the log (`:180`). This branch's `apply_report` keeps the marks already in the record (`scripts/record.py:453-457`, `kept + report["slice_only"]`), and a test covers that. So the wipe probably came from the `xv` the watch runs, not from this diff. I cannot prove that from here. Either way, amendments 2.2 and 3.3 are unmet in this record (`.xv/slices/2026-10-30-test-marks.md:54`, `:63`).

## 4. The picture

- `.xv/picture.md:23` says what `record` and `orders` own, but not the choices this slice adds. Proposed addition: "After the scenario step, `slice_only_marks` lists slice-only marks for the person who set the work going. They accept the marks or run `xv record unmark`. Marks survive a scenario re-run. The guardian's `wall_recommendations` go to the same person in `accept_moves`. Only a person's `--accept-wall <test>` accepts one, and only `--refuse-wall <test>` refuses one; an agent's report sets neither. Giving either flag on another kind of stop, or both flags on one test, is refused. Each answered `accept_moves` stop keeps `accepted_wall` and `refused_wall`."
- `.xv/picture.md:26` ends "A decision file and its `decisions` entry keep `settled` with the person's words." Proposed addition: "An answer to `ready_to_merge` also writes a decision."

**Finding J (new, for Sean): amendments 2 and 5 disagree on what refuses.**

- `.xv/slices/2026-10-30-test-marks.md:53`: "Every other recommendation on that stop is recorded as refused."
- `:88`: "Only `--refuse-wall` in a person's answer refuses a recommendation."

The code follows `:53`. `scripts/record.py:352-359` sets `r["refused"] = True` on every recommendation that is not accepted. `tests/test_record.py:1024` (`test_an_answer_with_no_flag_refuses_every_recommendation`) pins that. So the answer "B: 1" with no flags refuses every open recommendation, and `scripts/orders.py:192` never asks about them again. Sean decides which line binds. If `:88` binds, an unflagged recommendation should stay open.

**Finding G (carried, docs rather than the picture):**

- `docs/slice-record.md:30` gives the stop shape without `accepted_wall` or `refused_wall`.
- `:31` says decisions are written "when two people decided". A `ready_to_merge` answer now writes one too (`scripts/record.py:363`).

**Finding H (carried):**

- `"who": ",".join(who)` (`scripts/record.py:367`) writes `who` as a string, but `docs/slice-record.md:31` and older records use a list.
- `slice_only_marks` asks again about marks already accepted after every scenario re-run (`scripts/orders.py:114-117`).

## Door

**Door:** two-way. A revert removes the field, the two flags, the subcommand and the wording. Decision entries already written with a string `who` stay in the records. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..62c7723`. This pass alone: `git diff f1ac8d5..62c7723 -- scripts tests`
- Lost mark: `git show 7ff0b66 -- .xv/slices/2026-10-30-test-marks.md`
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `f1ac8d5`)
- Boundary: `.xv/slices/2026-10-30-test-marks.boundary.md`

## From the cleaner

- Shape proposal, for people: a shared helper for matching a test name inside a string. `scripts/record.py` does this in `cmd_move` (a regex prefix match at `:188-190`) and in `cmd_answer`/`apply_report` (set lookups at `:343`, `:460-461`).
- Shape proposal, for people: move the `accept_moves` wall-flag block out of `cmd_answer` (`scripts/record.py:336-359`) into its own function.

## From the cleaner

- Shape proposal, for people: A shared helper for matching a test name inside a string, now written twice in scripts/record.py (cmd_move and cmd_answer) with slightly different regexes; it would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py now does it in cmd_move (regex prefix match) and cmd_answer (known-set lookup). It would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py does it in cmd_move (regex prefix match) and cmd_answer/apply_report (known-set lookup). It would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py does it in cmd_move (regex prefix match) and cmd_answer/apply_report (known-set lookup). It would be a new concept, so left for the packet.
- Shape proposal, for people: cmd_answer has grown a long accept_moves block for wall flags; splitting it into its own function is a seam worth proposing, left for the packet.

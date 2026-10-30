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

# Packet: A person sees which tests stay on the wall and which leave it (fifth pass)

Nothing here needs two people; the merge is Sean's. The last two amendments are met: findings A and B from the fourth pass are fixed and tested. What is left for Sean:

1. **None of this has run live yet.** No `slice_only_marks` stop and no wall recommendation is in this slice's record, so the first green run below is still owed (§ The recording).
2. **A guardian report can still mark a recommendation `refused`** (finding C, carried over). It is the last place an agent can answer for the person.
3. Small items: D to H.

## The scenario

There are two parts (#87, #89). (1) After the scenario step, `slice_only_marks` stops for the originator whenever slice-only marks exist. The person accepts the marks or runs `xv record unmark`. (2) The guardian brief gets a fifth check, the wall. Its recommendations reach the originator in `accept_moves`, and the record keeps which ones the person accepted. The amendments say: acceptance is per test, by `--accept-wall` only, and the answer's words are never read. An acceptance survives a guardian re-run and later answers unless `--refuse-wall` names the test. Each answered stop keeps `accepted_wall` and `refused_wall`. A `ready_to_merge` answer is recorded as a decision (`.xv/slices/2026-10-30-test-marks.md:36-82`). May ignore: rewording the site, and moving slice-only tests out of the cleaner.

## The recording

None; this is a feature. Replay the red with `python3 -m unittest tests.test_record tests.test_orders`. I ran the whole suite at HEAD `355e8f6` (`cd tests && python3 -m unittest -q`): `Ran 431 tests in 99.564s`, `OK`.

**First green run still owed.** `slice_only` has held a mark since 02:28 (`.xv/slices/2026-10-30-test-marks.md:16`). Yet `stops` has no `slice_only_marks` entry, and the record has no `wall_recommendations` field at all (`:15-23`). The watch running this slice is the old one. Before merging: answer an `accept_moves` stop with `--accept-wall X`, then answer a later stop with `--refuse-wall X`. The later stop should show `refused_wall: ["X"]`, and the earlier stop should keep `accepted_wall: ["X"]`.

## The boundary picture

As given in `.xv/slices/2026-10-30-test-marks.boundary.md`: it touches `scripts/orders` and `scripts/record`. It adds no modules, edges, tables, surfaces or outbound calls. Shape hints: none (`:5-7`).

## What the suite asserts after

- `slice_only_marks` fires after the scenario step when there are marks, and not when there are none. `xv record unmark` removes one mark. A scenario re-run keeps the marks already in the record.
- An unanswered wall recommendation fires `accept_moves`. `--accept-wall` accepts only the tests it names, the words are never read, and an unknown name is refused. A guardian report cannot set `accepted`, and a guardian re-run keeps what the person accepted.
- New this pass (`tests/test_record.py:1087-1190`): a later answer with no flag, or with a different flag, keeps an earlier acceptance. `--refuse-wall` refuses an earlier acceptance and leaves the others alone. The words never refuse. Each answered `accept_moves` stop keeps `accepted_wall` and `refused_wall`, which are empty lists when no flag was given, and an earlier stop keeps its own lists.
- This pass removed no test line: `git diff 36a13e0..HEAD -- tests` adds 107 lines and removes none.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`.xv/slices/2026-10-30-test-marks.md:11`, `"shape": "narrow"`).

- The boundary picture shows no new module, edge, table or surface, and no shape hints (`.xv/slices/2026-10-30-test-marks.boundary.md:7`).
- The new order sits in `scripts/orders.py:114-120`. That is where the standing orders live (`.xv/picture.md:70`).
- `--refuse-wall`, the per-stop lists and `unmark` are in `scripts/record.py:171` and `:336-352`. `record` "owns the slice record" (`.xv/picture.md:23`).
- The new flags extend the `xv` CLI, which is already a surface (`.xv/picture.md:27`).

## 2. Pitch

pitch_contradiction: no. I checked `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (who uses it) and `:25` ("not for people or projects that will not trust agents to write production code"). Letting a person accept or refuse wall changes by name goes against none of them.

## 3. Moved tests

No test that existed at the base `5ec1d86` changed. `xv wall diff` measures against the baseline `f5528b6` and reports nothing changed, deleted or with fewer assertions. All three recorded moves are on tests born in this slice:

| File | Before → after | Why (the record) | Forced? |
| --- | --- | --- | --- |
| tests/test_orders.py | `test_the_readme_says_five_checks_not_four` → removed (cleaner) | "a one-time wording change" | Sean accepted it (`.xv/slices/2026-10-30-test-marks.md:43`) |
| tests/test_record.py | `test_an_answer_that_names_one_recommendation_accepts_only_that_one` (the words accept one) → removed (maker) | "the answer's words are never read" | Yes, `:53`; `AcceptWallFlagTest` covers the flag |
| tests/test_orders.py | `test_the_guardian_brief_has_five_checks` → removed (cleaner) | "accepted as slice-only" | Yes, `:43`, `:63` |

Slice-only tests removed: `tests/test_orders.py::test_the_guardian_brief_has_five_checks`. Kept: none.

**Finding C (carried): a guardian report can still set `refused`.** In `scripts/record.py:453`, the guardian re-run builds each item as `[{**r, "accepted": r.get("test") in kept} ...]`. That copies every key from the agent's report and overrides only `accepted`. A report item that carries `"refused": true` lands in the record. Then `scripts/orders.py:192` (`if not r.get("accepted") and not r.get("refused")`) never puts it to the person. The record shows a refusal nobody gave. This goes against `.xv/picture.md:72`: "Read-only agents are checked, not trusted."

**Finding D (carried): the record's moves are off.** The cleaner's slice-only move at 02:38:15 has no `slice_only: true` (`.xv/slices/2026-10-30-test-marks.md:15`), even though the test is in `slice_only` (`:16`). So `scripts/orders.py:190` counts it as an old moved test and puts it to Sean as one. The maker's move is also recorded twice, at 02:06:23 and 02:08:07 (`:15`).

**Finding E (new): the wall flags work on `accept_moves` stops only, and anywhere else they are silently dropped.** The lists and the validation sit under `if stop["order"] == "accept_moves":` (`scripts/record.py:336`). Pass `--accept-wall X` on any other stop and nothing is checked or recorded. The amendment reads "Each answered stop keeps two lists" (`.xv/slices/2026-10-30-test-marks.md:82`), but other stops get no lists. Sean decides whether "each answered stop" meant each `accept_moves` stop.

**Finding F (new): naming a test with both flags accepts it.** `r["accepted"] = test in stop["accepted_wall"] or (...)` (`scripts/record.py:347-348`) lets accept win, and the stop records the name in both lists. Nothing refuses the contradiction.

## 4. The picture

- `.xv/picture.md:23` names what `record` and `orders` own, but not the choices this slice adds. Proposed addition: "After the scenario step, `slice_only_marks` lists slice-only marks for the originator, who accepts them or runs `xv record unmark`; marks survive a scenario re-run. The guardian's `wall_recommendations` go to the originator in `accept_moves`. Only `xv record answer --accept-wall <test>` accepts one, and only `--refuse-wall <test>` takes back an earlier acceptance. Each answered `accept_moves` stop keeps `accepted_wall` and `refused_wall`."
- `.xv/picture.md:26` ends "A decision file and its `decisions` entry keep `settled` with the person's words." Proposed addition: "An answer to `ready_to_merge` also writes a decision."

**Finding G (doc, not the picture):** `docs/slice-record.md:30` gives the stop shape without `accepted_wall` or `refused_wall`. `:31` says decisions are written "when two people decided", which is no longer the only case (`scripts/record.py:356`).

**Finding H (carried):**

- `"who": ",".join(who)` (`scripts/record.py:360`) turns `who` from a list into a string in every decision entry. `docs/slice-record.md:31` and older records use a list.
- `slice_only_marks` asks again about marks already accepted, after every scenario re-run (`scripts/orders.py:114-120`).

## Door

**Door:** two-way. The change adds a record field, two flags, a subcommand and doc wording, and a revert undoes all of it. Decision entries already written with a string `who` stay in the records. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..355e8f6`; this pass alone: `git diff 36a13e0..355e8f6 -- scripts tests`
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `f5528b6`)
- Boundary: `.xv/slices/2026-10-30-test-marks.boundary.md`
- From the cleaner (a shape proposal, for people): a shared helper for matching a test name inside a string. `scripts/record.py` matches names in `cmd_move` (regex prefix) and in `cmd_answer` and `apply_report` (set lookup).

## From the cleaner

- Shape proposal, for people: A shared helper for matching a test name inside a string, now written twice in scripts/record.py (cmd_move and cmd_answer) with slightly different regexes; it would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py now does it in cmd_move (regex prefix match) and cmd_answer (known-set lookup). It would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py does it in cmd_move (regex prefix match) and cmd_answer/apply_report (known-set lookup). It would be a new concept, so left for the packet.

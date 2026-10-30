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

# Packet: A person sees which tests stay on the wall and which leave it (fourth pass)

Nothing here needs two people; the merge is Sean's. The third amendment is half met. Sean has two findings to decide:

1. **A later `accept_moves` answer refuses what was accepted earlier.** A guardian re-run now keeps an acceptance, but the next answer without the flag turns it into a refusal (§3, finding A).
2. **The accepted names are not kept on the stop.** Amendment 3, item 2 asks for this, and the code does not do it. An accepted recommendation that a later guardian report leaves out is lost from the record (§3, finding B).

The other findings are small (C to F).

## The scenario

There are two parts (#87, #89). (1) After the scenario step, `slice_only_marks` stops for the originator whenever slice-only marks exist. It lists each mark with its reason; the person accepts the marks or unmarks a test. A slice with no marks adds no stop. The stop tables list the order. (2) The guardian brief gets a fifth check, the wall, and the packet a fifth section. The recommendations reach the originator in `accept_moves`, and the record keeps which ones they accepted. "Four checks" becomes five wherever it appears.

Amendments: (1) acceptance is per recommendation; `xv record unmark`; a move whose assertion starts with a marked name keeps `slice_only`. (2) `--accept-wall <test>`, and the words are never read; the guardian-brief test is in `slice_only` at merge; a merge answer is recorded as a decision. (3) Only `--accept-wall` accepts, and the guardian's report never does. The accepted names are kept on the stop and survive a guardian re-run. The scenario report marks `test_the_guardian_brief_has_five_checks` (`.xv/slices/2026-10-30-test-marks.md:59-63`). May ignore: rewording the site, and moving slice-only tests out of the cleaner.

## The recording

None; this is a feature. Replay the red with `cd tests && python3 -m unittest test_orders test_record`. Before the maker's fourth pass it failed on `test_a_guardian_rerun_keeps_what_the_person_accepted_with_the_flag` (record `red.failure`). I ran the whole suite (`cd tests && python3 -m unittest -q`) at HEAD `36a13e0`: `Ran 419 tests in 97.445s`, `OK`.

**First green run still owed.** No `slice_only_marks` stop is in the record. Yet `slice_only` has held a mark since the scenario report at 02:28:44 (`.xv/slices/2026-10-30-test-marks.md:16`, `:23`), so the watch driving this slice was not running the new order. Nobody has watched it live yet.

## The boundary picture

From `.xv/slices/2026-10-30-test-marks.boundary.md`, as given: it touches `scripts/orders` and `scripts/record`. It adds and removes no modules, edges, tables, surface paths or outbound calls. Shape hints: none.

## What the suite asserts after

- `slice_only_marks` fires after the scenario step when there are marks, listing each test and reason. It does not fire when there are none (`tests/test_orders.py`, the `SliceOnlyMarks` tests).
- An unaccepted wall recommendation fires `accept_moves`. The docs and stop tables name the new order, and the brief and packet template have a fifth check or section.
- `xv record unmark` removes one mark. A prefix-matched move keeps `slice_only`.
- `--accept-wall` accepts only the tests it names and refuses the rest, the answer's words are never read, and an unknown name is refused (`tests/test_record.py:1008-1049`).
- New this pass: a guardian report cannot set `accepted`. A guardian re-run keeps what the person accepted and cannot accept anything new (`tests/test_record.py:1059-1081`).
- A scenario re-run keeps earlier marks. A `ready_to_merge` answer writes a decision.
- No test that existed at the base changed: `git diff 5ec1d86..HEAD --stat -- tests` shows 291 insertions and 0 deletions.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`"shape": "narrow"`, `.xv/slices/2026-10-30-test-marks.md:11`).

- The boundary picture has no added modules, edges, tables, surfaces or outbound calls, and no shape hints (`.xv/slices/2026-10-30-test-marks.boundary.md:7`, "Shape hints: none").
- The new order is in `scripts/orders.py:114-120`, where the standing orders live (`.xv/picture.md:70`). `wall_recommendations`, `unmark` and `--accept-wall` are in `scripts/record.py`, which "owns the slice record" (`.xv/picture.md:23`).
- The new flag and subcommand extend the `xv` CLI, which is already a surface (`.xv/picture.md:27`). They do not add a new one.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (who uses it) and `:25` ("not for people or projects that will not trust agents to write production code"). Giving a person a say over which tests join the wall goes against no line of the pitch.

## 3. Moved tests

No test that existed at the base `5ec1d86` changed. All three recorded moves are on tests born in this slice. `xv wall diff` measures against the baseline retaken at `cfe5d0e`, and shows `tests/test_orders.py` going from 48 to 46 assertions.

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_orders.py | `test_the_readme_says_five_checks_not_four` | removed by the cleaner | "guards a one-time wording change" | Sean accepted it at the first `accept_moves` (`.xv/slices/2026-10-30-test-marks.md:43`). |
| tests/test_record.py | `test_an_answer_that_names_one_recommendation_accepts_only_that_one`: the words accept one | removed by the maker | "the answer's words are never read" | Yes: `.xv/slices/2026-10-30-test-marks.md:53`. `AcceptWallFlagTest` now covers it. The record lists this move twice, at 02:06:23 and 02:08:07 (`:15`). |
| tests/test_orders.py | `test_the_guardian_brief_has_five_checks`: asserts `## The five checks` and no "four checks" | removed by the cleaner, 48 → 46 assertions | "accepted as slice-only" | Yes: Sean accepted the mark (`:43`, `:63`). The heading is still asserted indirectly by `test_the_fifth_check_names_the_three_recommendations`, which splits on it. |

Slice-only tests removed: `tests/test_orders.py::test_the_guardian_brief_has_five_checks`. Kept: none.

**Finding A: a later `accept_moves` answer turns an earlier acceptance into a refusal.** In `scripts/record.py:342-345`, every answer rewrites every recommendation:

```python
        for r in recs:
            r["accepted"] = r.get("test") in (a.accept_wall or [])
            if not r["accepted"]:
                r["refused"] = True
```

`accept_moves` also fires on moved tests or a picture change alone (`scripts/orders.py:193`), and this slice has fired it three times that way. Suppose Sean passes `--accept-wall test_keep_me` once. The guardian re-run keeps it (`scripts/record.py:445-446`). Then Sean answers the next `accept_moves` with just `B: 1`. Now `test_keep_me` has `accepted: false, refused: true`. Amendment 3 says the accepted names "are kept" (`.xv/slices/2026-10-30-test-marks.md:62`), and the scenario says "the record keeps which ones the person accepted" (`:37`). No test covers a second answer.

**Finding B: the `--accept-wall` names are not kept on the stop.** Amendment 3, item 2: "The names accepted with `--accept-wall` are kept on the stop" (`:62`). `cmd_answer` writes `answered_by`, `answer`, `answered_at`, `pick`, `settled`, `new_info`, `cause`, `why` and `bundle` onto the stop (`scripts/record.py:322-328`). It never writes `a.accept_wall`. The only place an acceptance lives is the recommendation item. A guardian re-run rebuilds that list from its own report alone (`scripts/record.py:446-447`). So if the new report leaves out a recommendation the person accepted, the acceptance is gone from the record.

**Finding C: a guardian report can still set `refused`.** `{**r, "accepted": ...}` at `scripts/record.py:446` copies every key from the report and overrides only `accepted`. A report that carries `"refused": true` therefore lands in the record. `scripts/orders.py:192` then never puts that item to the person, and the record shows it as refused by someone who never saw it. That goes against `.xv/picture.md:72`: "Read-only agents are checked, not trusted." Separately, `scripts/record.py:343-345` never clears `refused`, so an item refused once and accepted later carries both flags.

**Finding D: the record's moves are off.** The cleaner's slice-only move at 02:38:15 has no `slice_only: true` (`.xv/slices/2026-10-30-test-marks.md:15`), even though the test is in `slice_only` (`:16`) and the assertion starts with its name (`scripts/record.py:188-192`). So `scripts/orders.py:190` counts it as an old moved test and puts it to Sean as one. The maker's move is also recorded twice (`:15`). I cannot tell from the record whether the cleaner passed `--slice-only`.

**Carried from the third pass, unchanged:**

- **E.** `"who": ",".join(who)` (`scripts/record.py:353`) changes `who` from a list to a string for every decision entry, while `docs/slice-record.md:31` and older records use a list.
- **F.** `slice_only_marks` asks again about marks the person has already accepted, after every scenario re-run (`scripts/orders.py:114-120`). Its question says "the scenario agent marked" even for marks that a person added.

## 4. The picture

- `.xv/picture.md:23` names what `record` and `orders` own, but not the two choices this slice adds. Proposed addition: "After the scenario step, `slice_only_marks` lists slice-only marks for the originator, who accepts them or runs `xv record unmark`; marks survive a scenario re-run. The guardian's `wall_recommendations` go to the originator in `accept_moves`; only `xv record answer --accept-wall <test>` accepts one, every other is recorded as refused, and a guardian re-run keeps what was accepted."
- `.xv/picture.md:26` ends "A decision file and its `decisions` entry keep `settled` with the person's words." Proposed addition: "An answer to `ready_to_merge` also writes a decision." Add "and `who` is a comma-joined string" only if Sean keeps finding E as built.
- `.xv/picture.md:23` "`boundary`, `packet` and `check` are the guardian's checks" stays true. The picture never counted the checks.

## Door

**Door:** two-way. The change adds a record field, a flag, a subcommand and doc wording, and a revert undoes all of it. One leftover: decision entries written with a string `who` stay in the records. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..36a13e0`. This pass alone: `git diff cfe5d0e..36a13e0`.
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `cfe5d0e`, retaken mid-slice)
- Boundary: `.xv/slices/2026-10-30-test-marks.boundary.md`
- From the cleaner (a shape proposal, for people): a shared helper for matching a test name inside a string. `scripts/record.py` does that matching in two places: `cmd_move` (`:188-190`, regex prefix) and `cmd_answer` (`:338-343`, set lookup).

## From the cleaner

- Shape proposal, for people: A shared helper for matching a test name inside a string, now written twice in scripts/record.py (cmd_move and cmd_answer) with slightly different regexes; it would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py now does it in cmd_move (regex prefix match) and cmd_answer (known-set lookup). It would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py does it in cmd_move (regex prefix match) and cmd_answer/apply_report (known-set lookup). It would be a new concept, so left for the packet.

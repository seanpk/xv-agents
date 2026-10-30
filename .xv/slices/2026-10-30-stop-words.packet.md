---
slice: 2026-10-30-stop-words
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: none
moved_tests: 2
door: two-way
blast_radius: stops
---

# Packet: The stops, the briefs and the picture say what the method says

Nothing stops this for two people. The merge is Sean's (originator). The second pass did items 1 and 2 of the 2026-10-29 merge-stop amendment and left items 3 and 4 undone. Four findings need Sean's decision:

1. **Item 3 is not done: the guardian's brief still forbids `accepted` and never names `accepted_by`.** The amendment says "The guardian's brief and its may-not list both allow `accepted` for `shape_change`" (slice record, Amended 2026-10-29, item 3). The diff leaves `skills/guardian/SKILL.md:37`, "each `yes` or `no`, nothing else. `shape_change` may be `accepted` …; name that record", and `skills/guardian/SKILL.md:49`, "Set a fixed field to anything but `yes` or `no`". The check reads only a front-matter key (`scripts/run.py:517` `rel = pdata.get("accepted_by")`). The brief says "name that record" without naming the key, and the template `skills/guardian/packet.md` has no `accepted_by` line and says `shape_change: <yes|no>`. So a guardian that follows its brief either never writes `accepted`, or writes it with the record named in the body, and then the value is read as `yes`. That is safe, but #85 (scenario point 1) cannot happen through the brief. No test covers the guardian brief: `tests/test_briefs_picture.py` covers only the maker, scenario and watch briefs.
2. **Item 4 is not done: the moved test's name still says the opposite of what it checks.** `tests/test_orders.py:56` is `def test_a_stall_opens_the_shape_conversation(self):`, and it asserts `assertIn("reshape the slice", …)`. The amendment (item 4) says "The moved test's name says what it checks."
3. **`xv record packet` still trusts `accepted`.** `scripts/record.py:445-448`: `allowed = ("yes", "no", "accepted") if field == "shape_change" …` then `data[field] = value`, with no `accepted_by` check. `skills/guardian/SKILL.md:53` says "the watch attaches with `xv record packet`". A packet attached that way puts `accepted` on the record unchecked, and `shape_or_pitch` does not fire on it (`scripts/orders.py`, fires on `== "yes"`). That goes against the amendment's "Otherwise it is read as `yes`" (item 1) and `.xv/picture.md:72` "Read-only agents are checked, not trusted." The check exists only where `run.py` copies the fields (`scripts/run.py:502`).
4. **The `xv guard` test cannot tell "read as yes" from "no packet".** `tests/test_run.py` `test_xv_guard_with_no_slice_record_reads_accepted_as_yes` asserts only `stop.order == "shape_or_pitch"`. A guard run with no packet gives the same order (`scripts/run.py:772` `data["shape_change"] = data["pitch_contradiction"] = "yes"`). Neither the packet nor the record is checked. The guard line itself (`scripts/run.py:765`, `in ("yes", "no") else "yes"`) is unchanged from the base, so the behaviour is right today, but this test would not catch it going wrong.

## The scenario

The stops, the briefs and the picture say what the method says (#85, #86, #88/#68, #90):
1. A shape change a decision record on this slice already accepted does not stop again. The packet says `shape_change: accepted` with `accepted_by: .xv/decisions/<file>.md`. That holds only when the record is in the slice's `decisions` list and its `order` is `shape_or_pitch`; otherwise it is read as `yes`. `xv guard` with no slice record always reads `accepted` as `yes`.
2. A stall names itself and four choices (continue, reshape the slice, raise the budget, bring in a second person), not "The shape conversation opens".
3. `accept_moves` says "The guardian proposes a change to the picture".
4. The maker and the scenario agent may read the picture and not edit it, and they pull the binding decisions first.
5. The watch may edit the picture when a person directs it, in its own commit that names that person.

May ignore: rewording the site, and stops for checks that cannot run (D7).

## The recording

None; a feature starts from words. Replay: `cd tests && python3 -m unittest test_run.AcceptedShapeChangeTest test_packet test_orders test_briefs_picture`. I ran it: 67 tests, OK. The whole suite is green per the record (`checks.cleaner`, 433 tests, OK). I did not rerun the whole suite.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-30-stop-words.boundary.md`), as given. Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`. Nothing added or removed: no modules, edges, outbound calls, tables or surface paths. Shape hints: none. The new `accepted_by_listed_decision` (`scripts/run.py:515`) uses `record.read_doc`, and `run → record` is an edge that already exists.

## What the suite asserts after

- Packet lint accepts `shape_change: accepted` and refuses `pitch_contradiction: accepted` (`tests/test_packet.py`).
- `shape_or_pitch` does not fire on `accepted`, still fires on `yes`, and still fires for `accepted` + `pitch_contradiction: yes`, with a question that names only the pitch (`tests/test_orders.py`).
- Through `xv run`, `accepted` is kept, and goes on to `ready_to_merge`, only when `accepted_by` names a listed `shape_or_pitch` decision. With no `accepted_by`, an unlisted file, a missing file or a decision of another order, it becomes `yes` and stops for two people (`tests/test_run.py` `AcceptedShapeChangeTest`).
- `xv guard` with no slice record ends at `shape_or_pitch` (finding 4).
- Every stall question names the four choices and drops "The shape conversation opens". `accept_moves` names the guardian's picture proposal (`tests/test_orders.py`).
- The maker, scenario and watch briefs say what scenario points 4 and 5 require (`tests/test_briefs_picture.py`).
- Not tested: the guardian brief (finding 1), `xv record packet` with `accepted` (finding 3).

## 1. Shape

shape_change: no. Breadth none; the forecast was narrow.

- The boundary picture has no new module, edge, outbound call, table or surface path, and no hints. The stop rules stay in `scripts/orders.py`, as `.xv/picture.md:70` requires.
- The packet front matter gains a value (`accepted`) and a key (`accepted_by`). CI (`ci/github/xv-guardian.yml`) and the evals read that contract, but this is a change inside an existing surface (`.xv/picture.md:27`, "skills/*/SKILL.md, three GitHub Actions examples"), not a new surface. `xv guard` still reads `accepted` as `yes` (`scripts/run.py:765`), so `ci/github/xv-guardian.yml:8` stays true.
- The evals grader compares only to `yes`/`no` (`evals/grade.py:285`, `evals/grade.py:294`), so it would score an `accepted` packet as neither flagged nor clean. No eval scenario produces `accepted` today.
- The cleaner's proposal (one shared allowed-values definition for `scripts/packet.py:41` and `scripts/record.py:445`) would add an import edge, so it is left to people. It is not in this diff.

## 2. Pitch

pitch_contradiction: no. I checked `.xv/pitch.md:7` "to vibe with discipline", `.xv/pitch.md:21` (who uses it) and `.xv/pitch.md:25` (not for). Nothing in the diff serves someone the pitch excludes or breaks a promise it makes. The pitch says nothing about who stops for a shape change.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_orders.py:56` `test_a_stall_opens_the_shape_conversation` | `assertIn("shape conversation", question)` | `assertIn("reshape the slice", question)` | Point 2 removes "The shape conversation opens" | Yes, point 2. It asserts no less: one substring before and after. The name was not changed (finding 2). The record lists this move twice, by Sean Kennedy at 01:53:38 and by the maker at 01:55:19, so `accept_moves` would count it as 2 (`scripts/orders.py` `moved = [m for m in data.get("moved_tests") …]`). |
| `tests/fake_agent.py:62-68` fake guardian | always wrote `shape_change: no` to `<sid>.packet.md` | `shape_change` from `FAKE_SHAPE_CHANGE`, extra lines from `FAKE_PACKET_EXTRA`, and writes `.xv/slices/pr-packet.md` when `sid == "pr-packet"` | The `accepted_by` tests need such packets. Sean accepted it at `unrecorded_move` (02:57:46) | Yes, scenario point 1 as amended. With both variables unset it writes the same packet as before, so no existing test asserts less. The `report(... packet=f".xv/slices/{sid}.packet.md")` line still names the old path in the `pr-packet` case. Nothing reads it in the guard path. |

Slice-only tests removed: none (`slice_only: []`). Kept: none.

`xv wall diff 2026-10-30-stop-words` shows no changed, deleted or added files and `fewer_assertions: []` against baseline `2d0e876`. That baseline comes after both moves, so the record is the source for the two rows above. Unrecorded changes: none.

## 4. The picture

I propose these edits; I have not made them:

- `.xv/picture.md:33` (Names, "shape change"): add "A packet's `shape_change` is `yes`, `no` or `accepted`. `accepted` holds only when the packet's `accepted_by` names a `shape_or_pitch` decision record listed on this slice; otherwise, and always in `xv guard` with no slice record, it is read as `yes` (#85)."
- `.xv/picture.md:23` (`orders` holds the stop rules): add "The stall stops (`repeated_failure`, `diff_growing`) put four choices to the originator: continue, reshape the slice, raise the budget, or bring in a second person (#86)."
- `.xv/picture.md:58-75` (Decisions that bind): nothing says who may edit the picture. Add: the maker and the scenario agent read it and do not edit it, and the watch edits it only when a person directs it, in its own commit naming that person (`skills/watch/SKILL.md:86`; #88, #68, #90).
- `.xv/picture.md:72` (decision 12): true for `xv run`/`xv step` and `xv guard` after this change, but not for `xv record packet` (finding 3).

Other docs this diff leaves stale (they are not the picture): `docs/slice-record.md:27` still says "`yes` or `no`". `README.md:254` says the packet "says `yes` or `no` to a shape change". `README.md:303` and the `CHANGELOG.md:7` entry do not mention `accepted_by` or the downgrade to `yes`. `.xv/picture.md:61` (decision 1) asks for a CHANGELOG line for a changed check.

## Door

**Door:** two-way. No data is migrated, and reverting the commits restores the old stops and briefs. The briefs reach adopters through `xv install`, but no message goes to users. **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-10-30-stop-words.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..HEAD`
- Wall: `xv wall diff 2026-10-30-stop-words` (baseline `2d0e876`, `.xv/slices/2026-10-30-stop-words.wall.json`)
- Boundary: `.xv/slices/2026-10-30-stop-words.boundary.md`
- Red run: the command above, 67 tests OK. Suite: the record's `checks.cleaner`, 433 tests OK.
- I could not read the template at the checkout root's `skills/guardian/packet.md` (permission). I used the worktree's copy, `skills/guardian/packet.md`.

## From the cleaner

- Shape proposal, for people: the `shape_change` allowed-values check is written out twice, in `scripts/packet.py:41` and `scripts/record.py:445`. One shared helper in xvlib would remove the copy, but it adds a new function.

## From the cleaner

- Shape proposal, for people: One shared definition of the allowed values for shape_change (yes, no, accepted) and pitch_contradiction (yes, no), for scripts/packet.py:41, scripts/record.py:445, scripts/run.py:502 and scripts/run.py:750, which now each write the tuple out. It needs a new shared constant that record.py and run.py import from packet.py or xvlib, so it is not a cleanup.
- Shape proposal, for people: The `shape_change` allowed-values check is duplicated in scripts/packet.py:41 and scripts/record.py:445; one shared helper in xvlib would remove the copy, but it adds a new function, so it is left for a person.

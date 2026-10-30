---
slice: 2026-10-30-test-marks
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: workflow
---

# Packet: A person sees which tests stay on the wall and which leave it (third pass)

Nothing here needs two people. Sean, as the person who set the work going, has three findings to decide:

1. **An agent can accept its own wall recommendation.** The record copies `accepted` from the guardian's report, so a recommendation can skip `accept_moves` altogether (§3, finding A).
2. **The second amendment's item 2 is not true yet.** The record's `slice_only` is `[]`, and `test_the_guardian_brief_has_five_checks` is not in it (§3, finding B).
3. **A send-back loses what was accepted.** Each guardian run replaces `wall_recommendations`, and no stop keeps the `--accept-wall` names, so earlier acceptances are gone after a re-run (§3, finding C).

The other findings are small (D, E). The merge is Sean's.

## The scenario

There are two parts (#87, #89). (1) After the scenario step, a new order, `slice_only_marks`, stops for the person who set the work going whenever slice-only marks exist. The stop lists each marked test with its reason, and the person accepts the marks or unmarks a test so it joins the wall. A slice with no marks adds no stop. The stop tables list the new order. (2) The guardian brief gains a fifth check, the wall, and the packet a fifth section. The recommendations reach the originator in `accept_moves`, and the record keeps which ones they accepted. Every place that said "four checks" now says five.

Amendment 1: answers are per recommendation, not all accepted. `xv record unmark <id> --test <name>` takes a test off `slice_only`. A move whose assertion starts with a marked name keeps the flag. Amendment 2: `--accept-wall <test>` is repeated once per accepted recommendation, and the answer's words are never read. `test_the_guardian_brief_has_five_checks` is in `slice_only` by the merge stop. The merge answer is recorded as a decision. The slice may ignore rewording the site and moving slice-only tests out of the cleaner.

## The recording

None; this is a feature. To replay the red: `cd tests && python3 -m unittest test_orders test_record`. At the base it fails with `xv record: error: unrecognized arguments: --accept-wall test_keep_me` (record `red.failure`). The whole suite (`cd tests && python3 -m unittest -q`) ran 417 tests with OK at the cleaner's pass (record `checks.cleaner.suite_output`). The guardian's own run at HEAD `3b3ef8c` gave the same result: `Ran 417 tests in 96.943s` and `OK`.

## The boundary picture

From `.xv/slices/2026-10-30-test-marks.boundary.md`, as given: touched `scripts/orders` and `scripts/record`. No modules or edges were added or removed, nothing new calls out of the process, and no tables or surface paths changed. Shape hints: none.

## What the suite asserts after

- `slice_only_marks` fires for the originator after the scenario step when marks exist, and lists each test and reason. It does not fire with no marks (`tests/test_orders.py:166-196`).
- An unaccepted wall recommendation fires `accept_moves`, and an accepted one does not (`tests/test_orders.py:198-207`). The guardian's report fills `wall_recommendations` (`:209`).
- The docs: the slice-record doc, both stop tables, the guardian brief's five checks and the packet template's `## 5.` section (`tests/test_orders.py:220-251`).
- `xv record unmark` removes one mark, and fails on a test that is not marked. A move whose assertion starts with a marked name keeps `slice_only` (`WallChoicesTest`).
- `--accept-wall` accepts only the named tests and refuses the rest, the words are never read, and an unknown name is refused. Scenario re-runs keep earlier marks. A `ready_to_merge` answer writes a decision, with `who` as a string (`AcceptWallFlagTest`, `tests/test_record.py` +169 lines).
- No test that existed at the base changed: `git diff 5ec1d86..HEAD -- tests/` is 264 insertions and 0 deletions.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`"shape": "narrow"` in the record's `forecast`).

- The boundary picture has no added modules, edges, tables, surfaces or outbound calls, and no shape hints (`.xv/slices/2026-10-30-test-marks.boundary.md`, "Shape hints: none", "Edges: added: none").
- The new order is in `scripts/orders.py` (`scripts/orders.py:114-120`), where the picture says the standing orders live (`.xv/picture.md:23` "`orders` holds the stop rules"; `.xv/picture.md:70`, binding decision 10). This is inside the current shape.
- The new record field `wall_recommendations` and the `unmark` subcommand are in `scripts/record.py` (`scripts/record.py:27,31,182-190,651-655`). `record` owns the slice record (`.xv/picture.md:23`), so these are also inside the shape.
- A new CLI flag and subcommand on the `xv` surface (`.xv/picture.md:27`): this extends a surface that already exists. It does not add one.

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `.xv/pitch.md:21` (who uses it) and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot."). The slice gives a person a say over which tests join the wall. No line of the pitch says the system will not do that, and it serves no one the pitch excludes.

## 3. Moved tests

No test that existed at the base `5ec1d86` changed (`git diff 5ec1d86..HEAD --stat -- tests/`: `tests/test_orders.py | 95 +++`, `tests/test_record.py | 169 +++`). `xv wall diff` compares against a baseline retaken inside the slice (`d5997e4`), so it reports the moves below as wall changes. Both moved tests were born in this slice.

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_orders.py | `test_the_readme_says_five_checks_not_four` (added by this slice's scenario agent) | removed by the cleaner | "guards a one-time wording change from four to five in the README" | Sean accepted the removal at the first `accept_moves` (record stop at 01:31:14, `settled`). There is no `slice_only` flag on the move (`.xv/slices/2026-10-30-test-marks.md:15`). |
| tests/test_record.py | `test_an_answer_that_names_one_recommendation_accepts_only_that_one` asserted that the answer's *words* accept one recommendation | removed by the maker; 195 → 191 assertions (`xv wall diff`) | "the second amendment says the answer's words are never read; --accept-wall decides" | Yes: `.xv/slices/2026-10-30-test-marks.md:53` "The answer's words are never read to decide it." The behaviour is now asserted by `test_accept_wall_accepts_the_named_test_and_refuses_the_rest` and `test_the_words_of_the_answer_are_never_read_to_accept_a_test`. The record lists this move twice, at 02:06:23 and 02:08:07 (`.xv/slices/2026-10-30-test-marks.md:15`). |

Slice-only tests removed: none. Kept: none, because `slice_only` is `[]` (`.xv/slices/2026-10-30-test-marks.md:16`).

**Finding A: the guardian's report can set its own recommendation accepted.** At `scripts/record.py:444-446`:

```python
    if agent == "guardian" and isinstance(report.get("wall_recommendations"), list):
        data["wall_recommendations"] = [{**r, "accepted": bool(r.get("accepted"))}
```

If the report carries `"accepted": true`, it lands in the record. `scripts/orders.py:192` then skips that recommendation (`if not r.get("accepted") and not r.get("refused")`). If it is the only pending item, `accept_moves` never fires (`tests/test_orders.py:204` asserts exactly this, for an `accepted: True` item). That conflicts with `docs/core.md:13` ("No agent … accepts its own change") and `.xv/picture.md:72` ("Read-only agents are checked, not trusted"). The fix in words: the report's `accepted` and `refused` should be dropped, so that only `xv record answer --accept-wall` sets them.

**Finding B: amendment 2, item 2 is unmet in the record.** `.xv/slices/2026-10-30-test-marks.md:54` says `test_the_guardian_brief_has_five_checks` "is in the record's `slice_only` when the slice reaches the merge stop". The record has `slice_only: []` (`:16`). The code now keeps marks across scenario re-runs (`scripts/record.py:440-443`), but no step put this mark in, and no step after the guardian will. The test is still in `tests/test_orders.py:237`, so as things stand it joins the wall.

**Finding C: a send-back loses the record of what was accepted.** `scripts/record.py:445` replaces `wall_recommendations` wholesale on every guardian report. `scripts/record.py:337-345` writes `accepted` and `refused` onto those items, and does not keep the `--accept-wall` names on the stop. Once a later guardian run replaces the list, nothing in the record shows what the person accepted. The scenario says "the record keeps which ones the person accepted" (`.xv/slices/2026-10-30-test-marks.md:37`). Also, at `:343-345`, an item refused at one answer and accepted at a later one keeps `refused: true` beside `accepted: true`.

**Finding D: decision entries changed shape, and the scenario forces only part of it.** At `scripts/record.py:353`, `"who": ",".join(who)` turns `who` from a list into a string for *every* decision entry, two-people ones included. The scenario asks only that a merge answer is recorded (`:55`). The test forcing the string is `tests/test_record.py:1072`. Existing records hold lists (`.xv/slices/2026-10-29-stop-decisions.md:24` `"who": ["Sean Kennedy"]`), so the records now mix both shapes. `docs/slice-record.md:31` does not say which. I found no reader of `who` in `scripts/`.

**Finding E: `slice_only_marks` asks again after every scenario run.** `scripts/orders.py:114-120` fires whenever `slice_only` is non-empty after a scenario step. Marks now survive re-runs (`scripts/record.py:440-443`), so marks the person already accepted are put to them again on each send-back. The question also says "the scenario agent marked", including for marks a person added. The scenario says the stop fires "when the scenario report marks slice-only tests" (`.xv/slices/2026-10-30-test-marks.md:36`).

## 4. The picture

- `.xv/picture.md:23` lists what `record` and `orders` own, but has no line for the two choices this slice adds: `slice_only` marks put to the originator after the scenario, and wall recommendations put to them in `accept_moves`. Proposed: add to the shape paragraph: "After the scenario step, `slice_only_marks` lists the marked tests for the originator, who accepts them or runs `xv record unmark`. Marks survive a scenario re-run. The guardian's `wall_recommendations` go to the originator in `accept_moves`, and `xv record answer --accept-wall <test>` accepts one. Every other recommendation is recorded as refused."
- `.xv/picture.md:26` ends "A decision file and its `decisions` entry keep `settled` with the person's words." Proposed: add "An answer to `ready_to_merge` also writes a decision, and the entry's `who` is a comma-joined string." (The second half applies only if Sean keeps finding D as built.)
- `.xv/picture.md:23` "`boundary`, `packet` and `check` are the guardian's checks": still true. The guardian now has five checks (`docs/core.md:10`), and the picture never counted them, so no edit is needed.

## Door

**Door:** two-way. The change adds a record field, a flag, a subcommand and doc wording, and a revert undoes all of it. Decision entries written with a string `who` stay in the records after a revert. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..3b3ef8c`
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `d5997e4`, retaken mid-slice)
- Boundary: `.xv/slices/2026-10-30-test-marks.boundary.md`
- From the cleaner: the code that matches a test name inside a string is written twice, in `cmd_move` (`scripts/record.py:200-202`, regex prefix) and `cmd_answer` (`:337-345`, set lookup). The cleaner left it as a shape proposal.

## From the cleaner

- Shape proposal, for people: A shared helper for matching a test name inside a string, now written twice in scripts/record.py (cmd_move and cmd_answer) with slightly different regexes; it would be a new concept, so left for the packet.
- Shape proposal, for people: A shared helper for matching a test name inside a string; scripts/record.py now does it in cmd_move (regex prefix match) and cmd_answer (known-set lookup). It would be a new concept, so left for the packet.

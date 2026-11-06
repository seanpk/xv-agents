---
slice: 2026-11-06-covers-stall
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: watch-loop
---

# Packet: A missed point goes back with text the check accepts, and stops a person only on a real stall

Nothing stops this for two people. Sean, as the person who set the work going, has four things to decide: the picture edit (check 4), the duplicate move entry (check 3), whether the kept-coverage reset in `run.py` should stay as written (check 3, finding B), and the wall recommendation (check 5).

## The scenario

A numbered scenario point that is in neither `covers` nor `not_covered` goes back to the scenario agent. The send-back gives the agent each missed point as an `item` the check will accept (1). It says that every point of the scenario and its amendments goes in on every pass (2). The match ignores backticks, `*` and `_` in both the point and the item (3). The person is stopped as `red_misses_point` only on the third miss in a row (4). Only the send-backs since the last amendment, the last answer from a person, or the last pass that covered the point count toward that stop (5). A `CHANGELOG.md` line records the change (6).

The slice may ignore the guardian's `scenario_miss` repeat check, which also uses `sent_back`. It may also ignore other ways the text match can fail, and a refactor slice's own points.

## The recording

`.xv/recordings/2026-11-06-covers-stall.md` lists every `red_misses_point` stop on slice 2026-11-05-directed-edit at 859d226. In that run the agent dropped the backticks, the second miss stopped Sean, and Sean then accepted 16 points by hand. To replay the red and the green: `cd tests && python3 -m unittest test_run.WatchLoopTest`, at 078304a (red) and at HEAD (green). The guardian reran it at HEAD 044b7eb: "Ran 100 tests in 87.374s, OK". The record shows the suite green after the maker and after the cleaner (933 tests, `checks.cleaner.suite_output`).

## The boundary picture

From `.xv/slices/2026-11-06-covers-stall.boundary.md`, as given. Touched: `scripts/orders` and `scripts/run`. Modules added or removed: none. Edges added or removed: none. New outbound calls: none. Tables: none. Surface paths: none. Shape hints: none.

## What the suite asserts after

- A missed point goes back with no stop on the first and second miss. The third miss in a row stops the originator with `red_misses_point`.
- A run of misses is broken by a pass that covered the point, by an amendment, or by a person's answer. After a break, the next miss goes back again.
- An item without backticks, `*` or `_` covers a point that has them, and the reverse also holds. An item that changes a word still does not cover the point.
- The scenario prompt after a send-back holds the point's text exactly as the scenario has it. It says "every point", "each pass", "amendments" and `not_covered`.
- `CHANGELOG.md` under Unreleased names `red_misses_point`.
- Moved: the second miss no longer stops (`test_run.py`). In `test_orders.py`, the orders now stop after two earlier send-backs, where one used to be enough.

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast's "narrow".

- The boundary picture shows no added module, edge, table, surface or outbound call, and no shape hints (`.xv/slices/2026-11-06-covers-stall.boundary.md:7`, under "Shape hints": "none"; edges added: none). The two touched modules, `orders` and `run`, already had their edge: "`run` reaches ... `orders`" (`.xv/picture.md:21`).
- The record gains a new front-matter key, `amended_at_report`, written by `xv slice amend` (`scripts/run.py:269`) and read by `orders.miss_run` (`scripts/orders.py:59`). State stays in the same file, and `.xv/picture.md:27` says "State is files: `.xv/slices/<id>.md` (front matter plus log)". This adds a field inside the current shape. It is not a shape change.
- The forecast expected changes to the coverage match, the send-back wording, the counter, tests and a CHANGELOG line. The diff touches only those. The guardian's `scenario_miss` repeat check is untouched: it still calls `sent_back` (`scripts/orders.py`, the `after == "guardian"` branch is not in the diff), as the forecast's breadth note asked.

## 2. Pitch

pitch_contradiction: no.

- The change keeps the person in charge and only stops them less often on a mechanical miss. The pitch says xv-agents "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`). Nothing in "Who it is not for, and what it will never do" (`.xv/pitch.md:23-25`) is touched.
- Binding decision 1 says "A change to ... a standing order ... needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:65`). `red_misses_point` is a standing order, and the CHANGELOG has the line (`CHANGELOG.md:7`, "Decided by Sean, solo"). The repo runs `two_people: solo` (`.xv/config.yml:51`). This meets the decision as this repo runs it.
- Binding decision 10 says the standing orders are "a pure function of the record and the config" (`.xv/picture.md:74`). `miss_run` reads only `data` (`scripts/orders.py:51-74`), so this holds.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_run.py` | `test_the_same_missed_point_on_the_next_pass_stops_for_the_person`: the 2nd pass exits 10, the stop's seat is `originator`, and one stop is open | `test_..._goes_back_again` (`tests/test_run.py:572`): the 2nd pass does not exit 10, no stop is open, and `next` is `scenario`. The old stop moved to `test_the_third_miss_in_a_row_of_the_same_point_stops_for_the_person` (`:581`), which also checks `order` | Point 4. Sean accepted it at the `unrecorded_move` stop, 19:47:34 | Yes. Point 4 reverses the old assertion, and the stop is still asserted, one miss later and more strictly. It does not assert less |
| `tests/test_orders.py:445` | `test_orders_stops_when_the_same_uncovered_point_comes_back`: 1 earlier send-back means a stop | `..._a_third_time`: 2 earlier send-backs (`stops=[prior, dict(prior)]`) mean a stop. The same assertions, 108 → 108 (`xv wall diff`) | Point 4, by the maker | Yes. It does not assert less |

- **A. Duplicate move entry.** `moved_tests` in the record lists the `tests/test_orders.py` move twice (19:55:00 and 19:57:58), with the same assertion and reason. The picture says "One move is recorded once" (`.xv/picture.md:23`). `accept_moves` counts moves by file and assertion (`.xv/picture.md:23`), so this one move may count twice. The record should hold it once.
- **B. Kept coverage now resets when `next` is `maker`.** No moved test covers this, and the scenario does not ask for it in words. `scripts/run.py:805-807` now drops `checks.scenario.covers_kept` whenever the record's `next` is `maker` when the scenario step runs. Without this, point 5's "then covered, then missed again" could not happen, because kept coverage would cover the point. The red's case (`test_a_point_sent_back_twice_then_covered_then_missed_again_goes_back`, `tests/test_run.py:592`) runs `xv step scenario` by hand while `next` is `maker` (`scenario_covering`, `tests/test_run.py:460-466`). In the loop, the scenario step runs only with `next: scenario` (after an amendment, a guardian `scenario_miss`, or an answer), and kept coverage still applies there. So this branch is reached only by a hand-run step. Point 5's third sentence is met in the test, and in the loop it is vacuous, because the point stays covered. The miss count's own reset, a pass that did not miss the key (`scripts/orders.py:66-72`), does not depend on this branch. Sean should say whether to keep the branch.
- `xv wall diff` lists only `tests/test_orders.py` (108 → 108 assertions, `fewer_assertions: []`). `tests/test_run.py` is the red file. The wall baseline does not list it, and the `unrecorded_move` stop covered its move.
- The scenario agent's report allowed no may-not file (`.xv/slices/2026-11-06-covers-stall.md:30`, `may_not_files: []`).

Slice-only tests removed: none. Kept: `tests/test_run.py::test_the_changelog_has_a_line_for_the_red_misses_point_trigger`. It checks one CHANGELOG line and was accepted by the watch under `tests.slice_only_files`. The cleaner has not removed it (`cleaner_commit: null`). It can go once the line is in a release.

## 4. The picture

picture_change: yes. These are proposed edits for Sean to accept.

- `.xv/picture.md:23` says: "A watch send-back keeps `report_n` and `packet`, and a miss is a repeat when an earlier pass sent back the same key. The same miss on a later pass stops for the originator." This is now true only for `scenario_miss`. Proposed: "For `scenario_miss`, a miss is a repeat when an earlier pass sent back the same key, and the repeat stops for the originator. For `red_misses_point`, `orders.miss_run` counts the send-backs of the same point in an unbroken run of scenario reports. The third miss in a row stops for the originator. A pass that covered the point, an amendment (`amended_at_report`, written by `xv slice amend`), or a person's answer ends the run."
- `.xv/picture.md:27` says: "On a later scenario pass, the coverage kept from earlier passes (`checks.scenario.covers_kept`) is added to the report's `covers` before the check". Add: "except when the record's `next` is `maker` (a pass that went on to the maker ends the run)" (`scripts/run.py:805-807`). Whether this clause stays depends on Sean's call on finding B.
- `.xv/picture.md:27` says: "A numbered point of the scenario or an amendment that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent". Add: "The match ignores backticks, `*` and `_` in both the point and the item (`run.norm`). The send-back lists each missed point as `<number>. <text>`, an item the check accepts, and says every point goes in on each pass."
- `.xv/picture.md:27`, record state: add `amended_at_report`, the report count at the last amendment, to what the slice record holds.

## 5. The wall

- `tests/test_run.py::test_the_changelog_has_a_line_for_the_red_misses_point_trigger`: it should stay marked slice-only and stay off the wall. It guards a one-time CHANGELOG line (`CHANGELOG.md:7`, and the record's `slice_only` entry, "a one-time wording change"). Once the line moves under a release heading, this test's `## Unreleased` read (`tests/test_run.py:670-673`) fails.
- I also looked at the other ten new tests in `tests/test_run.py:572-668` and the moved test in `tests/test_orders.py:445`. Each guards behavior that lasts and does not restate another test. The two mark tests cover opposite directions (point marks at `:635`, item marks at `:641`). No test that was on the wall before the slice is made dead: the old second-miss test was renamed and reversed, not left dead.

## Door

**Door:** two-way. A revert restores the old trigger and match, and old records without `amended_at_report` read it as 0. **Blast radius:** watch-loop.

## Raw data

- Slice record: `.xv/slices/2026-11-06-covers-stall.md`
- Diff: `git diff 859d2262950dbf5235c68b263de288780436bfea..044b7eb`
- Wall: `xv wall diff 2026-11-06-covers-stall`
- Boundary: `xv boundary --base 859d2262950dbf5235c68b263de288780436bfea` (`.xv/slices/2026-11-06-covers-stall.boundary.md`)
- Recording: `.xv/recordings/2026-11-06-covers-stall.md`

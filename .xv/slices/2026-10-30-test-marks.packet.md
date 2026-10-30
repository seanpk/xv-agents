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

# Packet: A person sees which tests stay on the wall and which leave it

Nothing here stops the change for two people under the orders. Four things need Sean, as the person who set the work going:

1. **Binding decision 1.** This changes a standing order and two briefs. Under that decision it needs two people and a CHANGELOG line (`.xv/picture.md:61`). The repo runs solo (`.xv/picture.md:53`). The CHANGELOG line is there (`CHANGELOG.md:9`, "Sean decided it, solo (#87, #89)"), but the record's `decisions` is `[]`, and no order will raise the two-people stop, because shape and pitch are both `no`.
2. **Accepting a recommendation accepts all of them.** Answering `accept_moves` marks every wall recommendation `accepted`, whatever the answer says (`scripts/record.py:323`). The record cannot keep "which ones the person accepted", as scenario step 2 asks. No test covers it.
3. **The stop asks for an unmark the tool cannot do.** It tells you to "unmark a test" (`scripts/orders.py:119`), but `xv record set` refuses list fields (`scripts/record.py:130-131`) and nothing removes an item from `slice_only`.
4. **This slice's own slice-only removal was never put to you.** It was also recorded without its slice-only flag. See check 3.

The merge is Sean's.

## The scenario

A person sees which tests stay on the wall and which leave it (#87, #89).

1. After the scenario step, a new order for the person who set the work going fires only when the scenario report marks slice-only tests. It lists each one with its reason. The person accepts the marks or unmarks a test so it joins the wall. The answer is recorded. With no marks, there is no stop. The watch's stop table and the README list the new order.
2. The guardian gets a fifth check that makes three kinds of wall recommendation, and the packet gets a section for them. The recommendations reach the person in `accept_moves`, and the record keeps which ones they accepted. Docs that said "four checks" now say five. `CHANGELOG.md` gets a line.

May ignore: rewording the site, and moving slice-only tests out of the cleaner.

## The recording

None: this is a feature. Replay the red and the green with `cd tests && python3 -m unittest test_orders`. It was red at `606efa8` (8 failures, 2 errors, from the record's `checks.scenario.red_output`). It is green at HEAD `3c5362b`: I ran 34 tests, OK. After the cleaner, the whole suite was 402 tests, OK (`checks.cleaner.suite_output`).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-30-test-marks.boundary.md`), as given:

- Touched: `scripts/orders`, `scripts/record`.
- No modules, edges, outbound calls, tables or surface paths added or removed.
- Shape hints: none.

## What the suite asserts after

- After the scenario step, slice-only marks raise an `originator` stop. The question names each marked test and its reason and contains "unmark". With no marks there is no stop (`tests/test_orders.py:166`, `:176`, `:179`).
- A wall recommendation that is not accepted raises `accept_moves` for the originator, and an accepted one gives `ready_to_merge` (`:198`, `:204`).
- `record.apply_report` keeps the guardian's `wall_recommendations`, and the field is a list field (`:209`). `docs/slice-record.md` names it (`:220`). The watch's and the README's stop tables say "slice-only" (`:224`).
- The guardian brief has "## The five checks", no "four checks", and a fifth item naming slice-only, "should not join the wall" and "removed". The packet template has "## 5. " (`:237`, `:242`, `:249`).
- Not asserted:
  - That answering `accept_moves` sets `accepted` (`scripts/record.py:323-325`).
  - Any way to unmark a test. `test_unmarking_…` (`tests/test_orders.py:179`) builds a record that already has the test missing (`self.scenario_done([b])  # the person unmarked test_file_is_ts`). It calls no unmark action.
- Old assertions moved: one, a slice-only removal (check 3).

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"`.

- `.xv/slices/2026-10-30-test-marks.boundary.md` shows no new module, edge, outbound call, table or surface. Shape hints: none.
- The new order is inside `orders`, which "holds the stop rules" (`.xv/picture.md:23`). Binding decision 10 also puts every standing order in `scripts/orders.py` (`.xv/picture.md:70`), and the diff respects that (`scripts/orders.py:114-120`).
- The new record field `wall_recommendations` (`scripts/record.py:27`, `:31`) is more state in the slice file. "State is files: `.xv/slices/<id>.md`" (`.xv/picture.md:26`), so it is not a new table.
- The changed briefs are content inside an existing surface, "`skills/*/SKILL.md`" (`.xv/picture.md:27`). No surface is added.

## 2. Pitch

pitch_contradiction: no.

- I checked the change against `.xv/pitch.md:7`: "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline". I also checked the not-for line at `.xv/pitch.md:25`.
- The change adds a person's say over which tests join the wall. Nothing in it serves people "that will not trust agents to write production code", and it breaks no promise in the pitch.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_orders.py` (`3c5362b`, old `:249-252`) | `test_the_readme_says_five_checks_not_four`: `assertNotIn("four checks", README)`, `assertNotIn("its four findings", README)` | removed (wall: 50 → 48 assertions) | "guards a one-time wording change from four to five in the README; no value once the wording is changed" (cleaner) | Not forced. It is a slice-only removal and asserts less by design. |

- **Slice-only tests removed:** `tests/test_orders.py::test_the_readme_says_five_checks_not_four`.
- **Kept:** none. The record's `slice_only` lists only the one test removed above (`.xv/slices/2026-10-30-test-marks.md`, `slice_only`).
- **Never accepted by the person.** The test is in the record's `slice_only`, but the `slice_only_marks` stop never fired for it. The record's `stops` has only `budget_not_set` and `red_check`, because the maker wrote the order after the scenario step had run. Nothing now asserts the README's "five checks" wording (`README.md:23`, `:41`, `:50`).
- **Recorded without the slice-only flag.** The cleaner gave `--assertion "test_the_readme_says_five_checks_not_four; removed"`. `cmd_move` sets `slice_only` only when the assertion equals the test name exactly (`scripts/record.py:176-179`), so the record's `moved_tests` entry has no `slice_only: true`. The `accept_moves` order will therefore count it as an ordinary old-test move (`scripts/orders.py:190`). It still goes to Sean, not to two people.
- `xv wall diff` shows no unrecorded change: one file changed (`tests/test_orders.py`), and it is recorded (`.xv/slices/2026-10-30-test-marks.md`, `checks.cleaner.wall.unrecorded: []`).

## 4. The picture

picture_change: yes. Proposed edits:

- **`.xv/picture.md:23`** ("`orders` holds the stop rules"): add that after the scenario step, `slice_only_marks` stops for the originator when the scenario report lists `slice_only` tests, and that the guardian's `wall_recommendations` go to the originator through `accept_moves`.
- **`.xv/picture.md:26`** (the state in the slice file): add that the record keeps the scenario's `slice_only` marks and the guardian's `wall_recommendations`. Each recommendation has an `accepted` flag, and today any answer to `accept_moves` sets it on all of them (`scripts/record.py:323-325`).
- **`.xv/picture.md:16`** (the seats): no change. The new stop uses the existing `originator` seat.

## 5. The wall

I looked at the 12 tests this slice added in `tests/test_orders.py:166-251` and at the record's `slice_only` list.

- **`tests/test_orders.py::test_the_readme_says_five_checks_not_four` stays off the wall.** It was marked slice-only and removed (`3c5362b`), and the record's reason holds: it guards a one-time wording change.
- **`tests/test_orders.py::test_the_guardian_brief_has_five_checks` should not join the wall.** Mark it slice-only.
  - Its `assertNotIn("four checks", text)` (`:240`) guards the same one-time four-to-five wording that the cleaner removed the README test for.
  - Its `assertIn("## The five checks", text)` (`:239`) is restated by `test_the_fifth_check_names_the_three_recommendations`, which splits on that heading (`:243`) and fails if the heading is missing.
- **No test on the wall before the slice should be removed.** The suite is green with the README and briefs saying "five", so no old test asserts "four checks".

## Door

**Door:** two-way. A revert undoes the order, the record field and the docs. Records that already hold `wall_recommendations` keep a field the old code ignores. **Blast radius:** workflow.

## Raw data

- Slice record: `.xv/slices/2026-10-30-test-marks.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..3c5362b`
- Wall: `xv wall diff 2026-10-30-test-marks` (baseline `58ac3df`)
- Boundary: `xv boundary --base 5ec1d8640ff0da37a2634737f241cfd1a14821e2`, saved in `.xv/slices/2026-10-30-test-marks.boundary.md`

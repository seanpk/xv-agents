---
slice: 2026-10-27-wall-red-files
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: ci
---

# Packet: The wall sees old tests in a red file (third pass)

Nothing stops this for two people. Sean, as the person who set the work going, has these to decide:
- The picture edit (check 4).
- The move in `tests/fake_agent.py` is now recorded. Accept it or send it back (check 3).
- **New:** the rule reads only removed lines. A line *added* to an old test in a red file, such as a skip decorator or an early `return`, disables that test and passes both checks (finding 5.1).
- The JavaScript `import` matcher also skips dynamic `import(...)` call lines, which is wider than "`import ... from ...`, `import "..."`" (finding 5.2).
- The check was changed by one person, again (finding 5.3).

The second packet's findings on `require`, `tests/fake_agent.py` and the check that could not run are fixed in this pass. I checked each one; the evidence is under check 3 and finding 5.4.

## The scenario

Today the CI wall (`xv wall check --base`) treats every file on `red.files` as covered, so an old test in a red file can be changed or deleted and nothing is reported. After the fix, a red file that existed at the base is covered only for the tests the slice added. An old test or assertion that changed, with no recorded move naming the file, makes the file `unrecorded`. A red file new in the slice is covered whole. Sean settled more at two stops:
- The scenario step makes the same comparison and stops for the originator before the maker runs.
- Blank, comment and import lines are skipped. Import lines are matched per file type, and only when the whole line is an import, from one table. A file type with no matchers skips no import line. A line that only contains `require` counts.
- The `tests/fake_agent.py` change is recorded as a move.
- When the scenario-step check cannot run, the slice stops.

May ignore: nothing stated.

## The recording

None; a defect stated in words. To replay, run the record's red command: `cd tests && python3 -m unittest test_wall.WallRedFileTest && python3 -m unittest test_run.WatchLoopTest.test_an_old_assertion_changed_in_a_red_file_stops_before_the_maker test_run.WatchLoopTest.test_a_scenario_step_whose_old_red_check_cannot_run_stops_before_the_maker`. I ran it at HEAD and got `Ran 14 tests ... OK`, then `Ran 2 tests ... OK`. The cleaner reports the whole suite at 312 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-27-wall-red-files.boundary.md`, as given:
- Touched: `scripts/orders`, `scripts/run`, `scripts/wall`.
- Modules, edges, tables, surface paths and outbound calls: none added and none removed (lines 11–19, 103–111).
- Shape hints: none (line 7).

## What the suite asserts after

`tests/test_wall.py` `WallRedFileTest` runs `xv wall check --base main` against a red file that existed at the base.
- These pass with exit 0 and nothing unrecorded:
  - adding a test;
  - a changed old assertion when a recorded move names the file;
  - a widened Python `from` import, or a removed blank line;
  - a changed JavaScript `import ... from` line or `const x = require(...)` line;
  - a changed Ruby `require` line;
  - a changed Go `import` line.
- These fail with exit 1 and name the file:
  - a changed old assertion, or a deleted old test;
  - a changed `expect(() => require("./config")).toThrow(...)` line;
  - a `require = ...` line in a Python file;
  - an `import` line in a `.xyz` file, a type with no matchers.
- A red file new in the slice gives `(0, [], [])` for `(returncode, unrecorded, tests_moved)`.

`tests/test_run.py` `WatchLoopTest` adds two tests:
- If the fake scenario agent edits an old assertion in `tests/test_store.py`, the watch exits 10 and stops for the originator. The question names the file, and no maker step runs.
- If the record's `base` is emptied, the scenario step exits 10 and stops for the originator. The question mentions `base`, and no maker step runs.

## 1. Shape

`shape_change: no`. `shape_breadth: narrow`. The forecast also said narrow.
- The boundary picture adds no module, edge, table, surface or outbound call, and has no shape hints (`.xv/slices/2026-10-27-wall-red-files.boundary.md:7,11–19`).
- `scripts/wall.py:120–153` adds `IMPORT_MATCHERS`, `not_code`, `removed_lines` and `old_red_changed` inside `wall`, which "holds the test hash check" (`.xv/picture.md:23`).
- `scripts/run.py:451–455,585–592` calls them over the `run → wall` edge, which already exists (`.xv/picture.md:21`).
- `scripts/orders.py:102–107` reads `checks["old_red_changed"]` and `checks["old_red_unchecked"]` from the record. It raises `unrecorded_move` and `setup_failed` from what the record says failed, which `.xv/picture.md:69` allows.
- The forecast's breadth said "recording, moves, and other checks should not move" (record, `forecast.breadth`). `run` and `orders` changed because of Sean's stop answers, which came after the forecast. Those changes stay inside the current shape.

## 2. Pitch

`pitch_contradiction: no`. I read two lines:
- `.xv/pitch.md:7`, "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." A stricter wall serves "with discipline".
- `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code." This change does not touch it.

No pitch line is contradicted.

## 3. Moved tests

| File | Before | After | Maker's reason | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:32–38` | `red={"files": ["tests/test_red.py"], ...` | `red={"files": red_files, ...}`. `red_files` defaults to `["tests/test_red.py"]`, and a `FAKE_SCENARIO_EDITS_OLD` branch edits `tests/test_store.py` and sets it to that file | "The slice's own check needs a stand-in scenario agent that edits an old red file … No assertion was weakened." (record `moved_tests`, 22:54) | Yes. Sean's 5.1 (first stop) needs a scenario stand-in that edits an old red file. The default path reports the same list as before, and no assertion is removed. |

- The move is now recorded. `recorded_files` (`scripts/wall.py:103–104`) puts `tests/fake_agent.py` into `covered` (`scripts/wall.py:179`), so the CI form no longer reports it. This fixes the second packet's finding 5.2.
- Against the base, the diffs of `tests/test_wall.py` and `tests/test_run.py` only add lines. The edits between passes rewrote tests this slice had added, not old ones.
- No test asserts less.

## 4. The picture

- `.xv/picture.md:23` says "`wall` holds the test hash check." Proposed addition: "In the CI form (`xv wall check --base`), a red file that existed at the base is covered only for the tests the slice added. A removed or changed line in it, other than a blank, comment or import line (matched per file type in `IMPORT_MATCHERS`), makes it unrecorded unless a recorded move names the file. A red file new in the slice is covered whole."
- `.xv/picture.md:26` lists what the scenario step checks. Proposed addition: "The scenario step also compares each red file that existed at the base with the base. Old test code changed or removed with no move naming the file stops for the originator (`unrecorded_move`) before the maker. If the comparison cannot run, it stops with `setup_failed`."

Sean accepts or rejects these. I have not written them.

## 5. Findings for the person who set the work going

1. **Lines added to an old test go unseen.** `scripts/wall.py:146` keeps only lines that start with `-`: `if l.startswith("-") and not l.startswith("---") and not not_code(rel, l)`. A pure addition inside an old test therefore leaves the file covered, in the CI form (`scripts/wall.py:179`) and in the scenario-step check (`scripts/wall.py:153`). Three examples:
   - an added `@unittest.skip("later")` above the old `test_use_refuses_more_than_there_is` in `tests/test_store.py`;
   - an added `return` as the first line of its body;
   - a second `def test_use_refuses_more_than_there_is(self): pass` at the end of the class, which Python binds over the first.

   The slice's own assertion-count wall does not catch it either: its baseline is taken after the scenario step, so the scenario's edit is part of the baseline (record `wall_baseline` at `7536775`). The scenario says "Every test and assertion that was in the file at the base must still be there, unchanged, at HEAD" (record, Scenario, line 34). Whether a skipped or shadowed old test is "unchanged" is Sean's call. No test covers it.
2. **The JavaScript `import` matcher also skips dynamic `import(...)` lines.** `scripts/wall.py:121`: `JS_IMPORT = r"import\b.*|..."`. Sean listed "`import ... from ...`, `import "..."`" (record, Scenario, line 38). `import\b.*` also fullmatches a test line such as `import("./config").catch((e) => expect(e.message).toBe("missing"));`. Changing or deleting that line in an old red `.js` or `.ts` file passes. The same holds for Go `import\b.*` (`scripts/wall.py:128`), but Go only allows `import` at the top of a file, so this matters only for JavaScript and TypeScript.
3. **The check was changed by one person.**
   - `.xv/picture.md:60`: "A change to … a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
   - `CHANGELOG.md:7` has the line, ending "Sean decided it, solo".
   - `CHANGELOG.md:3`: "A version line without two names is a draft."
   - `.xv/picture.md:52`: `seats.two_people: solo`.
4. **Fixed since the second packet. I checked each fix.**
   - `require`: an assertion that only contains `require` now counts (`scripts/wall.py:121`, which only matches `(const|let|var) x = require(...)`). `test_a_line_that_only_contains_require_in_a_red_file_counts` covers it.
   - When the check cannot run (no `base`, or `ImportError`), `scripts/run.py:589,592` returns `None`. `scripts/run.py:453–455` then sets `old_red_unchecked`, and `scripts/orders.py:106–107` stops with `setup_failed`, as `.xv/picture.md:71` requires. Only the no-`base` branch has a test.
5. **Destructured `require` counts as code.** In `scripts/wall.py:121`, `(const|let|var)\s+\S+\s*=\s*require\(` needs the name to have no spaces. So a changed `const { expect } = require("chai");` in an old red file is reported as `unrecorded`. This is stricter than Sean's list and fails closed. It will cost adopters a recorded move or an explanation.
6. **Wider reach, as intended.** `xv wall check --base` runs on every pull request in adopting repos (`ci/github/xv-wall.yml:35`). After this merges, an open slice branch fails CI if it changed an old test line in a red file without a move.

## Door

**Door:** two-way. A revert restores the old rule, and no data, record format or message to users changes. **Blast radius:** ci.

## Raw data

- Slice record: `.xv/slices/2026-10-27-wall-red-files.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Third pass only: `git diff 7536775..HEAD`
- Wall: `xv wall diff 2026-10-27-wall-red-files`
- Boundary: `.xv/slices/2026-10-27-wall-red-files.boundary.md`
- Packet shape: the template at `skills/guardian/packet.md` is outside the worktree, and reading it was refused. This packet follows the shape of the earlier packets.

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- `xv wall diff 2026-10-27-wall-red-files` shows `changed: []`, `deleted: []` and `fewer_assertions: []`, because every test edit came before the wall baseline.
- Slice-only tests removed: none (`slice_only: []`). Kept: none.

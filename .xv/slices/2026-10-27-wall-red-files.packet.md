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

# Packet: The wall sees old tests in a red file (second pass)

Nothing stops this for two people. Sean, as the person who set the work going, has these to decide:
- The picture edit (check 4).
- `tests/fake_agent.py` changed an old line with no record and is not on `red.files`, so the CI form of the wall would report it (finding 5.2).
- The `require` exemption is wider than "a `require` line" and lets some assertions through (finding 5.1).
- The check was again changed by one person (finding 5.3).

## The scenario

Today the CI wall (`xv wall check --base`) treats every file on `red.files` as covered, so an old test in a red file can be changed or deleted and nothing is reported. After the fix, if a red file existed at the base, only the tests the slice added are the red; every old test and assertion must still be there unchanged unless a recorded move names the file, or the file is `unrecorded`. A red file new in the slice is covered whole. Sean settled three more points at the last stop. (5.1) The slice's own run makes the same comparison after the scenario step and stops for the originator before the maker. (5.2) A blank, comment, import or `require` line is not a move, so "a new import passes, a changed assertion fails". (5.4) The new-file test asserts what its name says. May ignore: nothing stated.

## The recording

None; a defect stated in words. To replay: `cd tests && python3 -m unittest test_wall.WallRedFileTest && python3 -m unittest test_run.WatchLoopTest.test_an_old_assertion_changed_in_a_red_file_stops_before_the_maker`. Red (record `red.failure`): `Tuples differ: (1, ['tests/test_store.py']) != (0, [])`, 2 of 7 failing. I ran it at HEAD: `Ran 7 tests ... OK`, then `Ran 1 test ... OK`. The maker and the cleaner each ran the whole suite: 304 tests OK.

## The boundary picture

From `.xv/slices/2026-10-27-wall-red-files.boundary.md`, as given. Touched: `scripts/orders`, `scripts/run`, `scripts/wall`. No modules added or removed. No edges added or removed (`run → wall` already exists). No new outbound calls, no tables, no surface paths. Shape hints: none.

## What the suite asserts after

`tests/test_wall.py` `WallRedFileTest` (lines 97–161) runs `xv wall check --base main` on a slice whose red file `tests/test_store.py` existed at the base:
- Adding a test passes (exit 0, nothing unrecorded).
- Changing an old assertion fails (exit 1, `tests/test_store.py` unrecorded), and so does deleting an old test.
- The same change with a recorded move naming the file passes.
- Widening `from datetime import date` to add `timedelta` passes. So does removing a blank line.
- A red file new in the slice passes with `unrecorded == []` and `tests_moved == []`.

`tests/test_run.py:133` `test_an_old_assertion_changed_in_a_red_file_stops_before_the_maker`: when the fake scenario agent edits an old assertion in `tests/test_store.py`, the watch exits 10 and stops for the originator, the question names the file, and no maker step is spent.

## 1. Shape

shape_change: no. shape_breadth: narrow. The forecast said `"shape": "narrow"`.
- The boundary picture has no added modules, edges, tables, surfaces or outbound calls, and no shape hints (`.xv/slices/2026-10-27-wall-red-files.boundary.md:7`, `- none`; lines 16–19).
- `scripts/wall.py:120–137` adds `NOT_CODE`, `removed_lines` and `old_red_changed` inside `wall`, which "holds the test hash check" (`.xv/picture.md:23`). `scripts/run.py:451,581–588` calls them over the existing `run → wall` edge (`.xv/picture.md:21`). `scripts/orders.py:102–105` adds a firing condition for the existing `unrecorded_move` order inside `orders`, which "holds the stop rules" (`.xv/picture.md:23`). The new check is computed in `run` and read from `checks` by `orders`, the same way `red_joined` is (`scripts/orders.py:98`), which keeps `orders` a pure function (`.xv/picture.md:69`).
- The breadth is wider than the forecast's words: "recording, moves, and other checks should not move" (record, `forecast.breadth`). The scenario-step stop in `scripts/run.py` and `scripts/orders.py` was added because Sean settled 5.1, after the forecast. It is still inside the current shape.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7`, "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline.", and `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code." A stricter wall fits line 7. Line 25 is not touched. I found no line this contradicts.

## 3. Moved tests

| File | Before | After | Why | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:32–38` | `red={"files": ["tests/test_red.py"], ...` | `red={"files": red_files, ...`, plus a `FAKE_SCENARIO_EDITS_OLD` branch that edits `tests/test_store.py` | No record: `moved_tests: []`, and the file is not on `red.files` | Yes in substance: 5.1 needs a fake scenario agent that edits an old red file. Nothing is asserted here and the default path is unchanged. But the line change is unrecorded (finding 5.2). |

Sources: `moved_tests: []`. `xv wall diff 2026-10-27-wall-red-files` shows `changed: []`, `deleted: []`, `fewer_assertions: []`, because every test edit was made before the wall baseline. `git diff 23f8dd5..HEAD --name-status -- tests` lists `M tests/fake_agent.py`, `M tests/test_run.py` and `M tests/test_wall.py`. The diffs of `test_run.py` and `test_wall.py` against the base only add lines.

The second scenario pass rewrote `test_a_red_file_new_in_the_slice_is_covered_whole` (`git diff 09f147f..4003dc1 -- tests/test_wall.py`). Before: it edited the file after the baseline, recorded a move, and asserted only `returncode == 0`. After: no post-baseline edit and no move, and it asserts `(0, [], [])` for `(returncode, unrecorded, tests_moved)`. That test was added in this slice, so this is not a move of an old test. Sean directed it (5.4), and it now asserts more.

Slice-only tests removed: none (`slice_only: []`). Kept: none.

## 4. The picture

- `.xv/picture.md:23` says "`wall` holds the test hash check". Proposed addition: "In the CI form (`xv wall check --base`), a red file that existed at the base is covered only for the tests the slice added. A changed or removed line in it, other than a blank, comment, import or `require` line, is unrecorded unless a recorded move names the file. A red file new in the slice is covered whole."
- `.xv/picture.md:26` lists what the scenario step checks (the red run, the `&&` rule). Proposed addition: "The scenario step also compares each red file that existed at the base with the base. If old test code was changed or removed and no move names the file, it stops for the originator (`unrecorded_move`) before the maker."

Sean accepts or rejects these. I have not written them.

## 5. Findings for the person who set the work going

1. **The `require` exemption lets assertions through.** `scripts/wall.py:120`: `NOT_CODE = re.compile(r"^-\s*(#.*|//.*|import\b.*|from\s+\S+\s+import\b.*|.*\brequire\b.*|)$")`. The `.*\brequire\b.*` branch matches any removed line that contains the word `require`, not only a `require` line. An old Jest assertion `expect(() => require("./config")).toThrow("missing")` in an old red file can be changed or deleted, and neither the CI form (`scripts/wall.py:163`) nor the scenario-step check (`scripts/wall.py:133–137`) reports it. Sean settled on "an import or `require` line" (record, Scenario, 5.2). The comment and `require` branches have no test. Only the import and blank-line cases do (`tests/test_wall.py:142,147`).
2. **`tests/fake_agent.py` would fail this slice's own CI wall.** It existed at the base, it changed an old line (`tests/fake_agent.py:38`), it is not on `red.files`, and no move names it. `check_against_base` puts every `M` file under `tests/**` that existed at the base into `tests_moved` (`scripts/wall.py:146`). It is not covered (`scripts/wall.py:163`), so `xv wall check --base 23f8dd5` would list it as `unrecorded`. Two things kept the slice's run from seeing it: the change came before the wall baseline, and the new scenario-step check only reads red files (`scripts/run.py:588`). This repo's `.github/workflows/` does not run the wall; adopters do (`ci/github/xv-wall.yml:35`). It needs a recorded move or a place on `red.files`.
3. **The check was changed by one person.** `.xv/picture.md:60`: "A change to ... a check an agent is judged by needs two people and a line in `CHANGELOG.md`." The line exists under `## Unreleased` (`CHANGELOG.md:7`, "Sean decided it, solo"). `CHANGELOG.md:3`: "A version line without two names is a draft." `.xv/picture.md:52` records `seats.two_people: solo`.
4. **The new scenario-step check passes when it cannot run.** `scripts/run.py:585–588` returns `[]` on `ImportError` and when the record has no `base`. `.xv/picture.md:71`: "A check whose input is broken or that cannot run stops for a person; it never passes." `wall_baseline` follows the same pattern (`scripts/run.py:594`). The import cannot fail in practice because `wall.py` sits next to `run.py`, but the no-base branch passes silently.
5. **The new-file test now matches its name but still is not part of the red.** `tests/test_wall.py:151–161` asserts that a new red file is never in `tests_moved`. That was already true at the base: `scripts/wall.py:146` only counts files `in in_base`. The `f not in in_base` clause at `scripts/wall.py:163` still changes no result.
6. **Wider reach, as intended.** `xv wall check --base` runs on every pull request in adopting repos (`ci/github/xv-wall.yml:35`). After this merges, any open slice branch whose red file changed an old test line without a move will fail CI.

## Door

**Door:** two-way. A revert restores the old rule, and no data, record format or message to users changes. **Blast radius:** ci.

## Raw data

- Slice record: `.xv/slices/2026-10-27-wall-red-files.md`
- Diff: `git diff 23f8dd53788ee9f656f572e730e497e3b0a298bc..HEAD`
- Second pass only: `git diff 09f147f..HEAD`
- Wall: `xv wall diff 2026-10-27-wall-red-files`
- Boundary: `.xv/slices/2026-10-27-wall-red-files.boundary.md`
- Packet shape: the template at `skills/guardian/packet.md` was outside the worktree and its read was denied, so this follows the first pass's packet.

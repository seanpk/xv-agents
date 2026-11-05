---
slice: 2026-11-04-refactor-kind
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-04-refactor-kind.md
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: workflow
---

# Packet: A slice kind for refactors, and test moves a person expects: #15

Third pass. Nothing stops for two people, and nothing goes back: the maker met both misses from the second pass. Sean decides three things at the merge: the picture edits (section 4), one wall recommendation that is still open (section 5), and one new finding for the person: a test file the slice added is no longer an expected move.

## The scenario

`xv slice new --kind refactor` opens a slice whose scenario step writes no red. The step runs the suite, stops when the suite is not green, and otherwise records the green suite as the oracle (points 1–2). The maker may rename and restructure what the scenario names, and a latent bug goes through `xv slice amend` (3–4). `--expect-moves imports|renames` and `--rename Old=New` name the test changes the person expects. A script, not the agent, decides whether a move fits, and a move that fits is recorded and listed with no `accept_moves` stop (5–9). The new stops are decided in `scripts/orders.py` (10). The packet carries `expected_moves: <n>` (11). When that field is wrong, the slice stops with `expected_moves_wrong` for the originator, on every slice kind (12). An amend on a refactor slice gets a red that must fail (13). The maker's brief (14) and the `xv-slice` skill (15) say all of this. The slice may ignore other move kinds, #114, and old slice records.

## The recording

None: this is a feature. Replay the red with `cd tests && python3 -m unittest test_refactor_kind test_orders test_refactor_skills`. Replay the whole suite with `python3 tests/run.py --jobs 4`. I ran both on HEAD `606c75b`, and the working tree differs from it only in the boundary file: the red ran 110 tests, OK (140 s); the whole suite ran 736 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-04-refactor-kind.boundary.md`, as given (now drawn from base `73d8704`; the content matches the second pass):

- Modules touched: `moves`, `orders`, `prompt`, `record`, `run`, `wall`. **Added: `scripts/moves`.** Removed: none.
- Edges added: `moves → wall`, `moves → xvlib`, `run → moves`. Removed: none.
- Tables: none. Surface paths: none added. No new outbound calls.

## What the suite asserts after

- A refactor slice's scenario step writes no red and goes on to the maker. A red suite at the start stops with `suite_not_green_at_start`. After an amend, the scenario step writes a red, and that red must fail (`AmendedRefactorCase`).
- An import-only change by the maker or by the cleaner is recorded as `expected` and reaches `ready_to_merge` with no `accept_moves` stop. So is a named rename to a new path. These still stop: a kind the slice did not expect, an unnamed rename, a changed assertion, and a hand-recorded move.
- **New this pass:** an expected move stays in the record after the scenario step runs again and the cleaner runs (`tests/test_refactor_kind.py:280-294`, `RerunScenarioCase`).
- When the packet's `expected_moves` is missing, not a number, or wrong, the slice stops with `expected_moves_wrong` for the originator, on a feature slice too. A count that matches does not stop.
- The maker's brief and the `xv-slice` skill have the refactor lines (six wording tests, on the wall by Sean's choice).
- The CHANGELOG line is no longer checked by a test: the cleaner removed the slice-only `ChangelogTest` (`606c75b`).

## 1. Shape

shape_change: accepted (`.xv/decisions/2026-11-05-2026-11-04-refactor-kind.md`: "scripts/moves.py joins the shape, as the forecast named it").

- Hint "a module was added": it is `scripts/moves.py` (diff `scripts/moves.py:1-94`), the module the decision accepted.
- Hint "an edge between modules was added": the three edges are `run → moves`, `moves → wall` and `moves → xvlib`. They are the same three the decision covered. No edge joins two modules that were apart.
- What changed since the second pass stays inside `moves.find`: it now compares with `data["base"]` (`scripts/moves.py:72-75`) and keeps held expected entries (`scripts/moves.py:77-92`). The cleaner made one equivalent edit that reads the base once (`scripts/moves.py:83`). The CHANGELOG line also changed. None of this is a shape change.
- Breadth **narrow**. `moves` is a leaf with one caller (`scripts/run.py:736-741`), and it adds no table and no outbound call. The forecast says `"shape": "wide"`, so the breadth is not wider than forecast.

## 2. Pitch

pitch_contradiction: no. I checked `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Moves that a script decides, and a green suite as the oracle, fit the discipline line. No pitch line names refactors.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` (helper; diff `@@ -65,6 +65,13 @@`, `@@ -74,11 +81,13 @@`) | The fake guardian's packet had no `expected_moves` line | It writes `expected_moves: $FAKE_PACKET_EXPECTED_MOVES` (default `0`; `omit` leaves the line out). New maker branches make an import move and a rename move | Point 11's tests need a packet with the field missing or wrong. Sean accepted it at `unrecorded_move` (03:58:21) | Yes. Every packet is now checked (`scripts/run.py:530`). The file has no assertions, so it asserts no less |
| `tests/test_refactor_skills.py` (`606c75b`, `@@ -44,12 +44,4 @@`) | `ChangelogTest`: 2 assertions that the refactor CHANGELOG line names `expected_moves_wrong` | Removed. `xv wall diff`: 13 → 11 assertions | Slice-only, by the cleaner: "checks a one-time wording change to a CHANGELOG line" | Slice-only; Sean accepted the mark at 06:55:02 |

Expected moves (0): none; no `moved_tests` entry is marked `expected`. Slice-only tests removed: `tests/test_refactor_skills.py` `ChangelogTest.test_the_changelog_line_for_the_refactor_kind_names_the_expected_moves_wrong_stop`. Kept: none. May-not files allowed by the scenario report: none (`may_not_files: []`).

`xv wall diff` against baseline `0557cbc` lists only `tests/test_refactor_skills.py`. `git diff 0557cbc HEAD -- tests/test_refactor_skills.py` is empty, because the baseline hashes the working tree after the red, and the red was committed after `0557cbc` (`scripts/wall.py:60-67`). This behaviour is older than this slice.

## 4. The picture

picture_change: yes. These are the second pass's edits, with line numbers moved by the rebase and one clause added for the base. They are for Sean to accept:

- `.xv/picture.md:21`: "24 modules … `scripts/*.py` (21)", and 63 edges. Add "`run` reaches `moves`; `moves` reaches `wall` and `xvlib`."
- `.xv/picture.md:23`: add a role for `moves`: "after the maker and the cleaner, `moves` compares each test file that changed since the wall baseline, or that the record already holds as expected, with the slice's base, against `expect_moves` and `renames`. It records a fit as a move marked `expected`, which replaces a hand-recorded entry for the same file." Extend "`accept_moves` counts moves by file and assertion" with "except moves marked `expected` (`scripts/orders.py:242-243`)". Add "after the guardian, `expected_moves_wrong` stops for the originator when the packet's `expected_moves` does not match the record (`scripts/orders.py:227-230`)."
- `.xv/picture.md:27`: add the refactor kind: "A refactor slice's scenario step runs no agent until the scenario is amended. It runs the suite, and `suite_not_green_at_start` stops for the originator unless the suite is green. After an amend, the scenario agent writes a red as on a feature slice (`scripts/run.py:356-357`)."
- `.xv/picture.md:33` (Names): add "`expected_moves` in a packet's front matter is the record's count of expected moves."

## 5. The wall

I looked at the 34 tests in `tests/test_refactor_kind.py` (this pass adds `RerunScenarioCase`), the 7 left in `tests/test_refactor_skills.py`, and the 9 new tests in `tests/test_orders.py`. One recommendation is open from the second pass (`accepted: false`), and I restate it:

- `tests/test_refactor_kind.py`, `ExpectedMovesStopCase.test_a_packet_whose_expected_moves_matches_does_not_stop_with_it` (lines 235-238): mark it slice-only. It has the same setup as `RefactorKindCase.test_expected_moves_reach_the_merge_stop_without_accept_moves` (lines 145-149): `--expect-moves imports`, `FAKE_MAKER_IMPORT_MOVE=1`, `FAKE_PACKET_EXPECTED_MOVES=1`. It also makes the same `ready_to_merge` assertion, so it only restates that test.

No test that was on the wall before the slice is made dead.

## Findings for the person

These are not scenario misses, so none of them sends the slice back.

- **A test file the slice added is no longer an expected move.** `moves.find` reads "before" from the slice's base (`scripts/moves.py:74-75`). For a file that is not at the base, `git show` fails, and `xvlib.git(..., check=False)` returns `""` (`scripts/xvlib.py:279-280`). So `code_lines(rel, "")` never equals the file's code (`scripts/moves.py:84`). Suppose the maker adds only an import line to a red file the scenario agent wrote, for example the amendment's red on a refactor slice (point 13). That change is no longer `expected`, and `wall.check` lists it as unrecorded (`scripts/wall.py:107-116`). Before this pass, when `find` compared with the wall baseline, the change counted as expected. The new behaviour errs toward a stop, and point 8 speaks of old tests. I read this from the code and did not run it.
- The second pass's two findings (the session path skips both new checks, and an amended refactor slice must account for its refactor points) go to a v0.5 issue, as Sean settled at `budget_spent` (06:47:54). The imports and renames findings from the first pass stand, as point 8 allows (decision record).

## Door

**Door:** two-way. The changes are code and briefs only. The new record fields (`expect_moves`, `renames`, `expected` on a move) add to the record, and a revert undoes them. **Blast radius:** workflow. On every slice kind, a packet without a correct `expected_moves` now stops after the guardian (`scripts/orders.py:227-230`).

## Raw data

- Slice record: `.xv/slices/2026-11-04-refactor-kind.md`
- Diff: `git diff 73d8704034d14aaac5d68a76dc7dd6aa4f662d2b..HEAD`. This pass's code changes are in `507bd1e` (maker) and `606c75b` (cleaner)
- Wall: `xv wall diff 2026-11-04-refactor-kind`
- Boundary: `.xv/slices/2026-11-04-refactor-kind.boundary.md` (`xv boundary --base 73d8704034d1`)
- Decision: `.xv/decisions/2026-11-05-2026-11-04-refactor-kind.md`

## From the cleaner

- Shape proposal, for people: scripts/run.py: refactor_scenario repeats the tail of step (save, verdict, apply_verdict, commit_step, reach). A shared helper for that tail would remove the copy, but it is a new function with a new concept, so left for the packet.
- Shape proposal, for people: scripts/run.py: refactor_scenario repeats the tail of step (save, verdict, apply_verdict, commit_step, reach). A shared helper for that tail would remove the copy, but it is a new function with a new concept, so left for the packet.
- Shape proposal, for people: scripts/record.py and scripts/run.py both declare --expect-moves and --rename for slice new; one shared declaration would be a new helper, so left as the existing --kind pattern.

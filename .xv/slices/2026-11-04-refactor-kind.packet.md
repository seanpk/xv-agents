---
slice: 2026-11-04-refactor-kind
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-04-refactor-kind.md
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: workflow
---

# Packet: A slice kind for refactors, and test moves a person expects: #15

Second pass. Nothing here stops for two people: the only shape change is `scripts/moves.py`, which Sean accepted in `.xv/decisions/2026-11-05-2026-11-04-refactor-kind.md`. Two misses go back. First, an expected move drops out of the record when the scenario step runs again after the maker (point 7, to the scenario agent). Second, the CHANGELOG line does not name the new standing order `expected_moves_wrong` (decision 1, to the maker). Sean also has two findings to look at, below.

## The scenario

`xv slice new --kind refactor` opens a slice whose scenario step writes no red. It runs the suite, stops when the suite is not green, and otherwise records that green suite as the oracle (points 1–2). The maker may rename and restructure what the scenario names. A latent bug goes through `xv slice amend` (3–4). `--expect-moves imports|renames` and `--rename Old=New` say which test changes the person expects. A script, not the agent, decides whether a move fits. A move that fits is recorded and listed with no `accept_moves` stop (5–9). The new stops are in `scripts/orders.py` (10). The packet carries `expected_moves: <n>` (11). If the field is wrong, the slice stops with `expected_moves_wrong` for the originator, on every slice kind (12). An amend on a refactor slice gets a red that must fail (13). The maker's brief (14) and the `xv-slice` skill (15) describe all of this. The slice may ignore other move kinds, #114, and old slice records.

## The recording

None: this is a feature. Replay the red with `cd tests && python3 -m unittest test_refactor_kind test_orders test_refactor_skills`. I ran it: 109 tests, OK (131 s). I did not rerun the whole suite. The record shows it green after the maker and after the cleaner (`suite: green`).

## The boundary picture

From `.xv/slices/2026-11-04-refactor-kind.boundary.md`, as given. It is the same as on the first pass:

- Modules touched: `moves`, `orders`, `prompt`, `record`, `run`, `wall`. **Added: `scripts/moves`.** Removed: none.
- Edges added: `moves → wall`, `moves → xvlib`, `run → moves`. Removed: none.
- Tables: none. Surface paths: none added. No new outbound calls.

## What the suite asserts after

- A refactor slice's scenario step writes no red and goes on to the maker. A red suite at the start stops it with `suite_not_green_at_start`.
- After an amend, a refactor slice's scenario step writes a red, and that red fails (`AmendedRefactorCase`).
- An import-only change by the maker or by the cleaner is recorded as `expected` and reaches `ready_to_merge` with no `accept_moves` stop. A named rename to a new path is recorded the same way. These still stop: a kind the slice did not expect, an unnamed rename, a changed assertion, and a hand-recorded move.
- If the packet's `expected_moves` is missing, not a number, or wrong, the slice stops with `expected_moves_wrong` for the originator, also on a feature slice. A matching count does not stop.
- The maker's brief has a refactor point and keeps "No refactor, no rename". The `xv-slice` skill offers `--kind refactor`, `--expect-moves` and `--rename`.
- No old assertion moved. The `tests/test_orders.py` diff removes no lines. `xv wall diff` against baseline `8f79e34` shows no test file changed, deleted or added.

## 1. Shape

shape_change: accepted (`.xv/decisions/2026-11-05-2026-11-04-refactor-kind.md`, order `shape_or_pitch`, listed in the record's `decisions`).

- Hint "a module was added": this is `scripts/moves.py` (diff `scripts/moves.py:1-86`). The decision says "scripts/moves.py joins the shape, as the forecast named it." Nothing goes beyond it.
- Hint "an edge between modules was added": the edges are `run → moves`, `moves → wall` and `moves → xvlib`, the same three edges the decision covered. No edge joins two modules that were apart.
- What changed since the decision stays inside the current shape: a new order in `scripts/orders.py:226-230`, the amend branch in `scripts/run.py:356`, and wording in two skills.
- Breadth **narrow**. `moves` is a leaf with one caller (`scripts/run.py:736-743`, `expected_moves`), and it adds no table and no outbound call. The record's forecast says `"shape": "wide"`, so this is not wider than forecast.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Script-decided moves and a green-suite oracle fit the discipline line. No pitch line names refactors.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` (helper; diff `@@ -65,6 +65,13 @@` and `@@ -74,11 +81,13 @@`) | The fake guardian's packet had no `expected_moves` line | The packet writes `expected_moves: $FAKE_PACKET_EXPECTED_MOVES` (default `0`; `omit` leaves the line out). New maker branches make an import move and a rename move. | Point 11's tests need a packet with the field missing or wrong. Sean accepted it at `unrecorded_move` (03:58:21). | Yes. Every packet is now checked (`scripts/run.py:530`). The file is a helper with no assertions, so it asserts no less. The new branches only add. |

Expected moves (0): none in the record. Slice-only tests removed: none. Kept: none (`slice_only: []`; Sean unmarked the six wording tests at 05:36:49). May-not files allowed by the scenario report: none.

## 4. The picture

picture_change: yes. Proposed edits, for Sean to accept:

- `.xv/picture.md:21`: make it 24 modules, `scripts/*.py` (21) and 63 edges. Add "`run` reaches `moves`; `moves` reaches `wall` and `xvlib`."
- `.xv/picture.md:23`: add a role for `moves`: "after the maker and the cleaner, `moves` compares each changed test file since the wall baseline against the slice's `expect_moves` and `renames`, and records a fit as a move marked `expected`. That entry replaces a hand-recorded one for the same file." Extend "`accept_moves` counts moves by file and assertion" with "except moves marked `expected` (`scripts/orders.py:242-243`)". Add "after the guardian, `expected_moves_wrong` stops for the originator when the packet's `expected_moves` does not match the record (`scripts/orders.py:226-230`)."
- `.xv/picture.md:26`: add the refactor kind. "A refactor slice's scenario step runs no agent until the scenario is amended. It runs the suite, and `suite_not_green_at_start` stops for the originator unless the suite is green. After an amend, the scenario agent writes a red as on a feature slice (`scripts/run.py:356`)."
- `.xv/picture.md:33` (Names): add "`expected_moves` in a packet's front matter is the record's count of expected moves."

## 5. The wall

I looked at the 33 tests in `tests/test_refactor_kind.py`, the 7 in `tests/test_refactor_skills.py`, and the 8 new tests in `tests/test_orders.py`. One recommendation:

- `tests/test_refactor_kind.py`, `ExpectedMovesStopCase.test_a_packet_whose_expected_moves_matches_does_not_stop_with_it` (lines 235-238): mark it slice-only. It sets up the same run as `RefactorKindCase.test_expected_moves_reach_the_merge_stop_without_accept_moves` (lines 145-149): `--expect-moves imports`, `FAKE_MAKER_IMPORT_MOVE=1`, `FAKE_PACKET_EXPECTED_MOVES=1`. It also asserts the same `ready_to_merge`. So it only restates that test, and each end-to-end run costs seconds.

No test that was on the wall before the slice is made dead.

## Findings for the person

None of these is a scenario miss, so none of them sends the slice back.

- **The session path skips both new checks.** `packet_expected_moves` runs only in `post_step` (`scripts/run.py:530`). `xv record packet` (`scripts/record.py:572-586`) never fills `packet_problems`, so a session guardian never meets `expected_moves_wrong`. The same goes for `moves.apply`, which runs only in `post_step` (`scripts/run.py:513`). A session maker's import move is never marked expected. The packet lint already had this reach before the slice. Point 12 says "on every slice kind", not "on every path".
- **On an amended refactor slice, the scenario agent must account for the refactor points too.** After an amend, `scripts/run.py:356` sends the whole scenario to the agent. `missed_points` and `not_covered` count every numbered point (`.xv/picture.md:26`), and points like "rename X" have no red. So such a slice will usually stop at `red_misses_scenario`, or the agent will claim it covers them. Point 13 asks for "a red for the amendment as on a feature slice", and the diff does exactly that.
- These two findings from the first pass still stand, and the decision kept them as point 8 allows: an `imports` move can point an old test at other code (`scripts/moves.py:29`), and a rename also rewrites names inside strings (`scripts/moves.py:37`).

## Scenario misses

- 7: an expected move drops out of the record when the scenario step runs again after the maker. Each scenario step resets the wall baseline to HEAD (`scripts/run.py:494-496`, `wall.baseline`). `moves.find` compares only against that baseline (`scripts/moves.py:54`). `moves.apply` then replaces every `expected` entry with what it finds (`scripts/moves.py:84-86`). The sequence: the maker makes an import or rename move, it is recorded as expected, and the slice goes back to the scenario agent (this slice did that four times). On the next maker or cleaner pass the move is already in the baseline, so its entry is dropped. The old test still differs from `base`, and the record and the packet's `expected_moves` no longer list it. No red reruns the scenario after an expected move. I read this from the code and did not run it. (evidence: `scripts/run.py:494`, `scripts/moves.py:54`, `scripts/moves.py:84-86`; to: scenario)
- decision 1: the CHANGELOG line does not name the new standing order `expected_moves_wrong` (point 12). It still says the check "lists a packet problem". It also leaves out that an amend on a refactor slice gets a red (point 13), and the `xv-slice` skill's new question (point 15). Decision 1 (`.xv/picture.md:63`) needs "a line in `CHANGELOG.md`" for a change to a standing order or a brief. (evidence: `CHANGELOG.md:7`; to: maker)

## Door

**Door:** two-way. The changes are code and briefs only. The new record fields add to the record, and a revert undoes them. **Blast radius:** workflow. On every slice kind, a packet without a correct `expected_moves` now stops after the guardian (`scripts/orders.py:226-230`). That includes slices whose guardian ran on the old template.

## Raw data

- Slice record: `.xv/slices/2026-11-04-refactor-kind.md`
- Diff: `git diff 66570aa785961973ad109e9db00dfc167a823e9b..HEAD`
- Wall: `xv wall diff 2026-11-04-refactor-kind`
- Boundary: `.xv/slices/2026-11-04-refactor-kind.boundary.md` (`xv boundary --base 66570aa78596`)
- Decision: `.xv/decisions/2026-11-05-2026-11-04-refactor-kind.md`

## From the cleaner

- Shape proposal, for people: scripts/run.py: refactor_scenario repeats the tail of step (save, verdict, apply_verdict, commit_step, reach). A shared helper for that tail would remove the copy, but it is a new function with a new concept, so left for the packet.
- Shape proposal, for people: scripts/run.py: refactor_scenario repeats the tail of step (save, verdict, apply_verdict, commit_step, reach). A shared helper for that tail would remove the copy, but it is a new function with a new concept, so left for the packet.
- Shape proposal, for people: scripts/record.py and scripts/run.py both declare --expect-moves and --rename for slice new; one shared declaration would be a new helper, so left as the existing --kind pattern.

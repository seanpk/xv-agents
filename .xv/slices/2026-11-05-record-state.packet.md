---
slice: 2026-11-05-record-state
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-05-record-state.md
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: moderate
---

# Packet: Accepted answers and the rebase record stay right: #120, #136, #138

This is the fourth guardian pass, after the pass Sean asked for at `accept_moves` (2026-11-06 19:28:02). There is no stop for two people: the shape has not changed since pass two, and its edges are the ones Sean chose at `shape_or_pitch`. There are no scenario misses. **Sean, as originator:**

- **Three of the four things settled at 19:28:02 are done:**
  - the one packet-check function
  - the clean-replay question wording
  - the removal of the two slice-only CHANGELOG tests
- **The fourth, the Opus line, is still in `.xv/config.yml:35-36`.** It falls to the watch before the PR.
- **Accept the picture edits (section 4).** They were held for the last guardian pass.
- **One gap found by reading (section 3):** when the maker adds a new test file on a clean replay, the new question's "drop it" command does not work.

## The scenario

The full text is in `.xv/slices/2026-11-05-record-state.md`, under "Scenario".

1. An accepted `shape_wider_than_forecast` keeps its breadth. It fires again when a later pass is wider.
2. Accepting a "mark slice-only" wall recommendation lists the test in `slice_only`.
3. `xv record report` and `xv record packet` run the move and packet checks that `xv step` runs.
4. `moves.find` compares a test file the slice added with the file as the scenario step left it.
5. The rebase maker's brief reads the record of truth, with the answers given at rebase stops.
6. On a clean replay, a maker edit to a test file or the picture stops with `rebase_conflict`.
7. After an error mid-rebase, `--continue` and `--abort` read the stops and budget from the record of truth.
8. The log keeps the stop and answer lines written mid-rebase.
9. A staged record stays out of the replayed commit. The marker check runs before `git add -A`. Point 6's question names the maker's edit.
10. There is a CHANGELOG line for each new or changed stop.
11. *(amended)* Point 6's edit is not committed before the person sees it, and `git diff` shows it.
12. *(amended)* The guardian brief gives `mark slice-only` as the exact value.
13. *(amended)* `--refuse-wall` takes a test accepted earlier out of `slice_only`, matched on the file and the test.
14. *(amended)* There is a CHANGELOG line for the guardian brief change.

May ignore: old slice records, and a rebase onto a branch that is not clean.

## The recording

None, because this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_record test_refactor_kind test_slice_rebase test_orders`.

- **Before:** the first red had 19 failures, and the amendment's red had 29 (`checks.scenario.red_output`: "Ran 336 tests … FAILED (failures=29)").
- **After:** I ran the red command on this pass: "Ran 334 tests in 315.224s … OK". That is 336 less the two slice-only tests the cleaner removed (`git diff 9da7d1b..HEAD -- tests/test_orders.py`).
- **Whole suite:** green at 828 tests after the cleaner (`checks.cleaner.suite_output`: "Ran 828 tests in shard 1/1 OK").

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-05-record-state.boundary.md`). It is the same as on passes two and three.

- **Touched:** `scripts/moves`, `orders`, `packet`, `record`, `run` and `wall`.
- **Edges added:** `scripts/record → scripts/moves` and `scripts/record → scripts/wall`.
- **Edge removed:** `scripts/run → scripts/moves`.
- **Unchanged:** no modules, tables, surface paths or outbound calls were added or removed.

The shape hints are "an edge between modules was added" and "an edge between modules was removed".

## What the suite asserts after

This is the same as pass three, less the two CHANGELOG tests the cleaner removed.

- **Shape stop:** an answered stop covers only breadths up to its own (`tests/test_record.py` `RecordStateTest`).
- **Slice-only through `accept_moves`:**
  - Accepting a "mark slice-only" recommendation lists the test, and a later `--refuse-wall` takes it out.
  - A same-named entry in another file stays.
- **Session path:** `xv record report` and `xv record packet` fire `unrecorded_move` and `expected_moves_wrong` as `xv step` does.
- **Added test files** (`tests/test_refactor_kind.py`): they compare with the newest scenario pass.
- **Rebase** (`tests/test_slice_rebase.py`):
  - Answers reach the maker's brief.
  - A clean-replay edit to a test file or the picture stops, and the edit is in `git diff`, not in `HEAD`.
  - `--continue` and `--abort` keep the true stops, budget and log lines, including on a second stop of the same order.
  - A staged record stays out of the replayed commit, and leftover markers stop the rebase.
- **Guardian brief:** the fifth check contains `` `mark slice-only` `` (`tests/test_orders.py:470-472`).
- **Changed since pass three, with no new assertion:**
  - `packet.packet_checks` is reached through the existing `cmd_packet` and `post_step` tests.
  - The new wording of the `rebase_conflict` question is not asserted word for word.

## 1. Shape

shape_change: accepted. shape_breadth: narrow. The forecast said `wide`, so the change is not wider than forecast.

- **The edges are the ones Sean chose.** `record → moves`, `record → wall` (added) and `run → moves` (removed) come from the boundary picture. Sean's decision chose them: "the shared checks live in packet, moves or wall, which both reach" (`.xv/decisions/2026-11-05-2026-11-05-record-state.md:16`).
- **Since pass three** (`git diff 9da7d1b..HEAD -- scripts`; `scripts/packet.py:135-140`):
  - `packet.packet_checks` is added (`scripts/packet.py:135-140`). It calls `fix` and `expected_moves_problems`, both in `packet`, and adds no import.
  - `record.cmd_packet` (`scripts/record.py:609`) and `run.post_step` (`scripts/run.py:915`) now call it. Both already reached `packet`.
  - The `rebase_conflict` question wording changes (`scripts/orders.py:173-175`).
  - All of this is inside the current shape: "`record` owns the slice record. `orders` holds the stop rules" (`.xv/picture.md:23`).

## 2. Pitch

pitch_contradiction: no.

- I read the diff against "to vibe with discipline" (`.xv/pitch.md:7`). The change keeps a person's answers, refusals and log lines true, and leaves a person's test or picture edit for them to keep or drop.
- I also read it against "Who it is not for, and what it will never do" (`.xv/pitch.md:23-25`). The change serves no one outside the pitch.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`ScenarioMissStandingOrderTest.packet`) | a hand-written packet with no `expected_moves` | the same packet with `expected_moves: 0` | Point 3: `xv record packet` now runs the packet checks, and a missing count stops with `expected_moves_wrong` | Yes: `scripts/record.py:609` runs `packet_checks`, which includes `expected_moves_problems` (`scripts/packet.py:138`). The assertion count is unchanged. |
| `tests/test_run.py:967` (`test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path`) | the same | the same, with `expected_moves: 0` | The same reason, point 3 | Yes, by the same hunk |

Sean accepted both at 2026-11-05 22:42:26 and at 2026-11-06 19:28:02.

`xv wall diff 2026-11-05-record-state` (baseline `e20f9b8`) lists one changed file: `tests/test_orders.py`, with 112 assertions before and 109 after. That is the two slice-only removals below. Both are recorded as cleaner moves at 19:33:43, and the cleaner check lists `unrecorded: []`.

Slice-only tests removed, all from `tests/test_orders.py` and all accepted by Sean (record `slice_only`, `"accepted": true`): `test_the_unreleased_lines_for_120_136_138_name_each_changed_stop`, `test_an_unreleased_line_for_120_136_138_names_each_new_or_changed_stop` and `test_an_unreleased_line_names_the_guardian_brief_and_mark_slice_only`. Kept: none.

Changes to may-not files that the scenario report allowed (`may_not_files`): none.

**Outside the tests, for Sean:**

- **Settled at 19:28:02 and done** (`scripts/packet.py:135-140`, `scripts/orders.py:173-175`):
  - The repeated packet checks are now one function, `packet.packet_checks` (`scripts/packet.py:135-140`). `scripts/record.py:609` and `scripts/run.py:915` both call it.
  - The clean-replay question now reads "The edit is uncommitted in the slice worktree: run {resume} to keep it, `git checkout -- <file>` to drop it, {undo}" (`scripts/orders.py:173-175`).
- **Settled, for the watch, not done yet.** `.xv/config.yml:35-36` still adds the `scenario:` line with `"--model", "opus"` and the comment "Slice J2 only … Removed before the PR". The settlement at 19:28:02 reads: "The watch removes the Opus line before the PR."
- **"Drop it" fails for a new test file** (`scripts/run.py:443-446`, `scripts/orders.py:174`).
  - On a clean replay, the files left for the person come from `changed_files(root, "HEAD")`. That function includes untracked files (`scripts/run.py:95-97`, `:553`).
  - `rebase_stop` runs `git add -A`, then `git reset -q -- <left>` (`scripts/run.py:443-446`). So a test file the maker newly added goes back to untracked.
  - For that file, `git checkout -- <file>` fails ("did not match any file(s) known to git"), and `git diff` does not list it. Only `git status` shows it.
  - The tests cover an edit to a file that is already tracked (`tests/test_slice_rebase.py`). Point 11's "`git diff` … shows the edit" holds for that case.
  - I read point 6's "a maker edit to a test file" as covering the tracked case the red pins. So this is a wording gap for a rare case, not a miss.
- **Still standing from earlier passes** (`scripts/record.py:327`, `scripts/moves.py:63`):
  - `--accept-wall` and `--refuse-wall` take a test name alone, so two recommendations with the same name in different files are answered together (`scripts/record.py:327`, `:338-339`). The `slice_only` match itself is on file and test (`:342-351`), as point 13 asks.
  - Point 4 finds the scenario's commits by the subject `xv(<id>): red` (`scripts/moves.py:63`).

## 4. The picture

Proposed edits to `.xv/picture.md`, for Sean to accept. They are pass three's edits, with this pass's two changes added.

- **Edges** (`.xv/picture.md:21`):
  - "`run` reaches `moves`" → "`record` reaches `moves` and `wall`; `run` reaches `moves` through `record`".
  - "`record` reaches `orders` and `packet`" → "`record` reaches `orders`, `packet`, `moves` and `wall`".
  - "63 edges" → "64": two added and one removed (`.xv/slices/2026-11-05-record-state.boundary.md:19-20`).
- **Shape stop** (`.xv/picture.md:23`): after "answered without sending work back", add "at a breadth no narrower than the current one; the stop records `breadth`, and a stop with no `breadth` covers any" (`scripts/orders.py:262-270`).
- **Moves** (`.xv/picture.md:23`):
  - After "with the slice's base", add "and a test file the slice added with its newest `red` commit" (`scripts/moves.py:58-72`).
  - Add: "`xv record report` for the maker and the cleaner runs the expected-move and wall checks. `packet.packet_checks` is the one place where `xv step` and `xv record packet` run the packet lint and the `expected_moves` count" (`scripts/packet.py:135-140`).
- **Wall recommendations** (`.xv/picture.md:23`): after "only `--refuse-wall <test>` takes back one accepted earlier", add "an accepted `mark slice-only` recommendation is listed in `slice_only`, and refusing it later takes it out, matched on file and test" (`scripts/record.py:342-351`).
- **Rebase** (`.xv/picture.md:23`, `:27`):
  - "The rebase maker's brief reads the record at the old head (#138 for answers given during the rebase)" → "… with the stops, budget and log lines from the rebase applied".
  - Add: after an error mid-rebase, `--continue` and `--abort` read the notes' stops and budget (`scripts/run.py:369-372`, `tree_record_of_truth`).
  - Add: a staged record is put back before `--continue` (`scripts/run.py:656-657`).
  - Add: leftover markers stop as `rebase_stuck` before staging (`scripts/run.py:514-516`).
- **Rebase may-not** (`.xv/picture.md:36`): "on a replay with no conflict the check is missing (#138)" → "on a replay with no conflict it stops with `rebase_conflict` too. The edit is left uncommitted in the worktree, and the question says `--continue` keeps it and `git checkout -- <file>` drops it" (`scripts/run.py:443-448`, `scripts/orders.py:173-175`).

## 5. The wall

No recommendations this pass. I looked at:

- every test added since the base that is still in the tree: `RecordStateTest`, `AddedTestFileMoveCase`, the new `SliceRebaseTest` tests and `GuardianFiveChecksTest.test_the_fifth_check_gives_mark_slice_only_as_the_exact_value`
- the record's `slice_only` list
- `.xv/rules.md:35`

What I found:

- Pass three's two "stay off the wall" recommendations were accepted at 19:28:02. Their tests are now removed (`git diff 9da7d1b..HEAD -- tests/test_orders.py`), so there is nothing left to recommend for them.
- No remaining new test only guards a one-time change. The brief test matches a code rule, and ".xv/rules.md:35: … a test of a brief sentence that matches a code rule stays on the wall".
- No test on the wall before the slice is made dead by this scenario.

## Door

**Door:** two-way. The change is code, tests, CHANGELOG lines, a brief sentence and a config line. The new record fields (`breadth`, `slice_only` entries and the rebase notes) are additive, so a revert undoes the change.

**Blast radius:** moderate. It changes every adopter's `xv slice rebase`, `xv record report`, `xv record packet` and `--refuse-wall`. On the session path, a packet with no `expected_moves` now stops (`scripts/packet.py:138`).

## Raw data

- Slice record: `.xv/slices/2026-11-05-record-state.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. Since the last packet: `git diff 9da7d1b..HEAD`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-record-state.md`
- Wall: `xv wall diff 2026-11-05-record-state`
- Boundary: `.xv/slices/2026-11-05-record-state.boundary.md`

## From the cleaner

- Shape proposal, for people: One function in packet.py that runs the packet lint, the expected_moves count and the dropped-findings count, and returns what goes into checks. record.cmd_packet and run.post_step now repeat that sequence. Extracting it is a new shared function, so it is left for the packet.

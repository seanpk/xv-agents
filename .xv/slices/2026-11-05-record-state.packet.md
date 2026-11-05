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

This is the second guardian pass. No stop for two people: the new edges are the ones Sean chose at `shape_or_pitch`. **Sean, as originator:**

- Accept the picture edits (section 4).
- Take the Opus scenario line out of `.xv/config.yml` before the PR.
- Weigh four gaps found by reading, listed under 3.

The two misses from the first pass (points 4 and 8) are fixed in code. No test covers either one.

## The scenario

Ten points (`.xv/slices/2026-11-05-record-state.md`, "Scenario"):

1. An accepted `shape_wider_than_forecast` keeps its breadth. It fires again when a later pass is wider.
2. Accepting a "mark slice-only" wall recommendation lists the test in `slice_only`.
3. `xv record report` and `xv record packet` run the move and packet checks `xv step` runs.
4. `moves.find` compares a test file the slice added with the file as the scenario step left it.
5. The rebase maker's brief reads the record of truth, including answers given at rebase stops.
6. A maker edit to a test file or the picture on a clean replay stops with `rebase_conflict`.
7. After an error mid-rebase, `--continue` and `--abort` read stops and budget from the record of truth.
8. The log keeps the stop and answer lines written mid-rebase.
9. A staged record stays out of the replayed commit. The marker check runs before `git add -A`. Point 6's question names the maker's edit.
10. A CHANGELOG line for each new or changed stop.

May ignore: old slice records, and a rebase onto a branch that is not clean.

## The recording

None: this is a feature. To replay the red and the green, run `cd tests && python3 -m unittest test_record test_refactor_kind test_slice_rebase test_orders`.

- Before: 19 failures (`red.failure` in the record).
- After: I ran the red command on this pass: "Ran 324 tests … OK". The record's maker and cleaner checks say the whole suite is green, 818 tests (`checks.cleaner.suite_output`).

## The boundary picture

As `xv boundary` gives it (`.xv/slices/2026-11-05-record-state.boundary.md`):

- Touched: `scripts/moves`, `orders`, `packet`, `record`, `run`, `wall`.
- **Edges added:** `scripts/record → scripts/moves` and `scripts/record → scripts/wall`.
- **Edge removed:** `scripts/run → scripts/moves`.
- The `record → run` edge from the first pass is gone.
- No modules, tables, surface paths or outbound calls were added or removed.

Shape hints: "an edge between modules was added", "an edge between modules was removed".

## What the suite asserts after

- **Shape stop.** It records `breadth`. An answered stop covers only breadths up to its own, so a wider packet fires it again (`tests/test_record.py` `RecordStateTest`).
- **Slice-only marks.** An accepted "mark slice-only" recommendation is listed in `slice_only`. Refused, "stay on the wall", self-accepted and kindless recommendations are not.
- **Session path.** `xv record report` for the maker or cleaner records expected moves and finds an unrecorded move for the orders. `xv record packet` stops with `expected_moves_wrong` when the count is missing or wrong, and moves an uncited finding out of the count.
- **Added test files.** An import-only edit to a test file the slice added is an expected move. A changed assertion in that file still stops (`tests/test_refactor_kind.py` `AddedTestFileMoveCase`).
- **Rebase** (`tests/test_slice_rebase.py`):
  - An answer given at a stop reaches the maker's brief.
  - A maker edit to a test file or the picture on a clean replay stops with `rebase_conflict`.
  - `--continue` and `--abort` after an error keep the true stops and budget.
  - The log keeps the stop and answer lines after `--continue` and after `--abort`.
  - A staged record stays out of the replayed commit.
  - Leftover markers stop the rebase, and an unstaged resolution goes on.
- **Not asserted.** The two repeat cases fixed after the first pass have no test: a second scenario pass on an added file (point 4), and two same-order rebase stops (point 8). The commits since the red (`git diff afce46d..HEAD -- tests/`) only remove the slice-only test and add `expected_moves: 0` to two packets.

## 1. Shape

shape_change: accepted. shape_breadth: narrow. The forecast said `wide`, so the shape is not wider than forecast.

- **`record → moves` and `record → wall` (added)** (`scripts/record.py:18`, `scripts/record.py:21`).
  - Why: `scripts/record.py:18` `import moves` and `scripts/record.py:21` `import wall`. `record.expected_moves` (`scripts/record.py:545-551`) calls `moves.apply`. `cmd_report` calls `wall.check_or_note` (`scripts/record.py:564`).
  - This adds dependencies, so it is a shape change. Sean already chose it. The decision says "the shared checks live in packet, moves or wall, which both reach" (`.xv/decisions/2026-11-05-2026-11-05-record-state.md:16`). The option it settled says "move out of run into a module both can reach (packet_expected_moves into packet; expected_moves and the wall check into moves or wall)" (record, stop `shape_or_pitch`, option 1).
- **`run → moves` (removed).** `run` now reaches `moves` only through `record.expected_moves` (`scripts/run.py:891`). Removing a direct edge follows from moving the check out of `run`, so it is inside the same decision.
- **Placement, not shape.** `expected_moves` went into `record` (`scripts/record.py:545`), not into `moves` or `wall` as the option named. `run → record` already existed, so this adds no edge. In `moves`, it would have needed a new `moves → record` edge to save the record.
- **Inside the shape.** The rest stays inside the shape `.xv/picture.md:21` describes:
  - `packet.expected_moves_problems` (`scripts/packet.py:135-146`) and `wall.check_or_note` (`scripts/wall.py:140-145`) are new functions in modules that existed.
  - The record fields are additive: `breadth` on a stop (`scripts/record.py:647-648`), `slice_only` entries (`scripts/record.py:342-346`), and `stopped`, `staged_record` and `log` in the rebase notes (`scripts/run.py:435-439`).

## 2. Pitch

pitch_contradiction: no. I read the diff against "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`) and against "Who it is not for, and what it will never do" (`.xv/pitch.md:25`). The change keeps people's answers and log lines through a rebase and runs the same checks on the session path. It serves no one outside the pitch and breaks no promise in it.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`ScenarioMissStandingOrderTest.packet`) | hand-written packet with no `expected_moves` | the same packet with `expected_moves: 0` | Point 3: `xv record packet` now runs the packet checks, and a missing count stops with `expected_moves_wrong`, which hid the `scenario_miss` asserted | Yes. `scripts/record.py:606` adds `expected_moves_problems` to `packet_problems`. Assertions 275 → 275. |
| `tests/test_run.py:967` (`test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path`) | the same | the same, with `expected_moves: 0` | The same, point 3 | Yes, the same hunk. Assertions 251 → 251. |

Slice-only tests removed: `tests/test_orders.py` `test_the_unreleased_lines_for_120_136_138_name_each_changed_stop`, which Sean accepted at 18:57:55 (assertions 111 → 108, `xv wall diff`). Kept: none.

Changes to may-not files that the scenario report allowed (`may_not_files`): none. `xv wall diff` lists no unrecorded change.

**Outside the tests, for Sean:**

- **The Opus config line is still in the diff.** `.xv/config.yml:35-36` adds a `scenario:` line on `--model opus`, commented "Slice J2 only … Removed before the PR." It is in commit `f74a6ac`, so a merge would carry it.
- **The rebase commits the maker's edit.** On a clean replay, the `maker_edited` stop (`scripts/run.py:547`) runs `rebase_stop`. With no git rebase running, `rebase_stop` commits everything as "the rebase stopped" (`scripts/run.py:441-442`, `commit` runs `git add -A`). So the maker's test or picture edit is committed by the time the person sees the question.
  - The question says "Look at the change in the slice worktree" (`scripts/orders.py:173-175`). `git diff` there shows nothing; only `git show HEAD` does.
  - On `--continue`, `maker_ran` is already set (`scripts/run.py:478`, `540`), so the edit stays on the branch under that subject. `--abort` resets it away.
  - On a conflict replay, the edit stays staged and uncommitted (`scripts/run.py:513`, mid-rebase `rebase_stop` does not commit). So the two stops differ in this one way.
- **Point 2 depends on an exact string.** `answer_wall` lists a test only when the recommendation is exactly `"mark slice-only"` (`scripts/record.py:342`). The guardian brief never gives that value: it says "say it should be marked slice-only" (`skills/guardian/SKILL.md:28`), and its only example value is `"stay off the wall"`.
- **A refused recommendation stays in `slice_only`.** A later `--refuse-wall` sets only `r["refused"]` (`scripts/record.py:346-347`) and leaves the entry in `slice_only`. The picture says "only `--refuse-wall <test>` takes back one accepted earlier" (`.xv/picture.md:23`). A test taken back this way is still removed by the cleaner. The duplicate check also matches on `test` alone, not on `file` (`scripts/record.py:342-343`).
- **The point 4 fix depends on a commit subject.** It finds the scenario's commits by the subject `xv(<id>): red` (`scripts/moves.py:63`), which `run.py:1041-1044` writes. A scenario commit with another subject falls back to the first add (`scripts/moves.py:68-71`).
- **The same packet checks appear twice.** The lint, the expected-moves count and the dropped-findings count are repeated in `record.cmd_packet` (`scripts/record.py:603-609`) and `run.post_step` (`scripts/run.py:906-911`). The cleaner proposed one function in `packet` (record, `checks.reports`, cleaner at 22:26:38).

## 4. The picture

Proposed edits to `.xv/picture.md`, for Sean to accept:

- **Edges** (`.xv/picture.md:21`): "`run` reaches `moves`" → "`record` reaches `moves` and `wall`; `run` reaches `moves` through `record`". "`record` reaches `orders` and `packet`" → "`orders`, `packet`, `moves` and `wall`". "63 edges" → 64 (2 added, 1 removed).
- **Shape stop** (`.xv/picture.md:23`): "`shape_wider_than_forecast` does not fire … when a stop of that order was answered without sending work back" → add "at a breadth no narrower than the current one. The stop records `breadth`, and a stop with no `breadth` covers any" (`scripts/orders.py:262-270`).
- **Moves** (`.xv/picture.md:23`): "with the slice's base" → add "and a test file the slice added with its newest `red` commit" (`scripts/moves.py:58-72`). Add: `xv record report` for the maker and the cleaner runs the expected-move and wall checks, and `expected_moves_wrong` also fires on `xv record packet` (`scripts/record.py:560-565`, `606`).
- **Wall recommendations** (`.xv/picture.md:23`): after "Only a person's `--accept-wall <test>` accepts one", add "an accepted `mark slice-only` recommendation is listed in `slice_only`" (`scripts/record.py:342-346`).
- **Rebase brief and notes** (`.xv/picture.md:27`): "The rebase maker's brief reads the record at the old head (#138 for answers given during the rebase)" → "with the stops, budget and log lines from the rebase applied" (`scripts/run.py:466-468`). Add three things:
  - After an error mid-rebase, `--continue` and `--abort` read the notes' stops and budget (`scripts/run.py:369-386`).
  - A staged record is put back before `--continue` (`scripts/run.py:647-649`).
  - Leftover markers stop as `rebase_stuck` before staging (`scripts/run.py:507-509`).
- **Rebase may-not** (`.xv/picture.md:36`): "on a replay with no conflict the check is missing (#138)" → "on a replay with no conflict it stops with `rebase_conflict` too, and the question names the maker's edit" (`scripts/run.py:544-547`, `scripts/orders.py:171-175`).

## 5. The wall

I looked at the tests the red added (`RecordStateTest` in `tests/test_record.py`, `AddedTestFileMoveCase` in `tests/test_refactor_kind.py`, and the new tests in `tests/test_slice_rebase.py`) and at the record's `slice_only` list.

- Each new test guards lasting behaviour of `orders`, `record`, `moves` or the rebase, not a one-time change, and none restates another.
- The one slice-only test is already removed.
- No wall test is dead under this scenario.

No recommendations.

## Door

**Door:** two-way. The change is code, tests, a CHANGELOG line and a config line, and the new record fields are additive, so a revert undoes it. **Blast radius:** moderate. Every adopter's `xv slice rebase`, `xv record report` and `xv record packet` change, and a packet with no `expected_moves` now stops on the session path (`scripts/record.py:606`).

## Raw data

- Slice record: `.xv/slices/2026-11-05-record-state.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-record-state.md`
- Wall: `xv wall diff 2026-11-05-record-state`
- Boundary: `.xv/slices/2026-11-05-record-state.boundary.md` (`xv boundary --base 5d5e75fc7a7371d74a3884cfbae919785adbb4e7`)

## From the cleaner

- Shape proposal, for people: One function in packet.py that runs the packet lint, the expected_moves count and the dropped-findings count, and returns what goes into checks. record.cmd_packet and run.post_step now repeat that sequence. Extracting it is a new shared function, so it is left for the packet.

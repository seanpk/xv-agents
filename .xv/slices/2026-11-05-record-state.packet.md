---
slice: 2026-11-05-record-state
shape_change: yes
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: moderate
---

# Packet: Accepted answers and the rebase record stay right: #120, #136, #138

Three things need a decision. **Two people** (Sean, solo): `record` now imports `run`, so the two modules import each other (shape). **The maker**: two scenario points are missed when the work repeats: a second rebase stop of the same order (point 8), and a scenario step that ran twice (point 4). **Sean, before the PR**: the Opus line for the scenario agent in `.xv/config.yml` is still in the diff.

## The scenario

Ten points (record, `.xv/slices/2026-11-05-record-state.md`, "Scenario"). (1) An accepted `shape_wider_than_forecast` keeps its breadth and fires again if a later pass reports a wider shape. (2) Accepting a "mark slice-only" wall recommendation lists the test in `slice_only`. (3) `xv record report` and `xv record packet` run the move and packet checks `xv step` runs. (4) For a test file the slice added, `moves.find` compares with the file as the scenario step left it. (5) The rebase maker's brief reads the record of truth, including answers given at rebase stops. (6) A maker edit to a test file or the picture on a clean replay stops with `rebase_conflict`. (7) After an error mid-rebase, `--continue` and `--abort` read stops and budget from the record of truth. (8) The slice log keeps the stop and answer lines written mid-rebase, after `--continue` and `--abort`. (9) A record the person staged is not committed into the replayed commit, the marker check runs before `git add -A`, and point 6's question names the maker's edit. (10) A CHANGELOG line for each new or changed stop.

May ignore: old slice records, and a rebase onto a branch that is not clean.

## The recording

None: this is a feature. Replay the red and the green with `cd tests && python3 -m unittest test_record test_refactor_kind test_slice_rebase test_orders`. Before: 19 failures (the record's `red.failure`). After: green. The record says the maker and cleaner checks found the whole suite green: 819 tests, then 818 after the slice-only removal. I did not run the suite again.

## The boundary picture

As `xv boundary` gives it (`.xv/slices/2026-11-05-record-state.boundary.md`): touched `scripts/moves`, `scripts/orders`, `scripts/record`, `scripts/run`. **Edge added: `scripts/record → scripts/run`.** No edges removed, no modules added or removed, no new outbound calls, no tables, no surface paths. Shape hint: "an edge between modules was added".

## What the suite asserts after

- The shape stop records `breadth`. An answered stop covers only a breadth up to its own, and a wider packet fires the stop again (`tests/test_record.py`).
- An accepted "mark slice-only" recommendation appears in `slice_only` (`tests/test_record.py`).
- `xv record report` (maker or cleaner) raises `unrecorded_move` and records expected moves. `xv record packet` raises `expected_moves_wrong` when `expected_moves` is missing or wrong (`tests/test_record.py`).
- An import-only edit to a test file the slice added is an expected move, and a changed assertion in that file still stops (`tests/test_refactor_kind.py` `AddedTestFileMoveCase`).
- Rebase (`tests/test_slice_rebase.py`):
  - The answer given at a stop reaches the maker's brief.
  - A maker edit to a test file or the picture on a clean replay stops with `rebase_conflict`, and the question names the maker.
  - `--continue` and `--abort` after an error keep the true budget and the answered stop.
  - The log keeps one stop line and its answer.
  - A staged record stays out of the replayed commit.
  - Leftover markers stop the rebase, and an unstaged resolution goes on.
- Old assertions that moved: two hand-written packets now carry `expected_moves: 0` (see 3).

## 1. Shape

shape_change: yes. shape_breadth: narrow. The forecast said `wide`, so this is not wider than forecast.

- **New edge `record → run` (a shape change).** `scripts/record.py:548-555` (`cmd_report`) and `scripts/record.py:593-600` (`cmd_packet`) import run inside the function: `import run as runlib`, then call `runlib.expected_moves`, `runlib.wall_check` and `runlib.packet_expected_moves`. `run` already imports `record` (`scripts/run.py:32`), so the two modules now import each other.
  - The picture lists `record`'s edges: "`record` and `evals/report` reach `spend`. `record` reaches `orders` and `packet`" (`.xv/picture.md`, The shape). It puts `record` below `run`: "`record` owns the slice record" while `run` reaches most of the others.
  - This adds a dependency and reverses a layer. It is narrow: three call sites in two commands (`scripts/record.py:550`, `scripts/record.py:594`).
  - The maker had another option. `packet_expected_moves` (`scripts/run.py:1119-1131`) reads only the packet and the record, so it could have gone in `packet`, which `record` already reaches.
- No other hint. The boundary picture shows no tables, surfaces, modules or outbound calls added. New record fields are additive: `breadth` on a shape stop (`scripts/record.py:638-639`), `slice_only` entries from `answer_wall` (`scripts/record.py:340-343`), and `staged_record`/`stopped`/`log` in the rebase notes (`scripts/run.py:430-435`). The notes live in the git dir. These are changes inside the current shape.

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md`: "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline", and "Who it is not for, and what it will never do". It keeps people's answers and log lines through a rebase and runs the same checks on the session path. Nothing serves someone outside the pitch or breaks a promise it makes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`ScenarioMissStandingOrderTest.packet`) | hand-written packet with no `expected_moves` | same packet with `expected_moves: 0` | Point 3: `xv record packet` now runs the packet checks, and a missing `expected_moves` stops with `expected_moves_wrong`, which hid the `scenario_miss` asserted | Yes: `scripts/record.py:593-597` adds `packet_expected_moves` to `packet_problems`. Assertions 275 → 275, so nothing is weaker. |
| `tests/test_run.py:967` (`test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path`) | same | same with `expected_moves: 0` | same, point 3 | Yes, same hunk. Assertions 251 → 251. |

Slice-only tests removed: `tests/test_orders.py` `test_the_unreleased_lines_for_120_136_138_name_each_changed_stop` (Sean accepted the mark at 18:57:55; assertions 111 → 108). Kept: none.

Changes to may-not files the scenario report allowed (`may_not_files`): none. `xv wall diff` lists no unrecorded change.

**Outside the tests, for Sean:**

- `.xv/config.yml:35-36` adds a `scenario:` agent line on `--model opus`, commented "Slice J2 only, as Sean directed: the wide-slice test. Removed before the PR." It is still in the slice's diff (commit `f74a6ac`), so a merge would carry it.
- `answer_wall` matches only the exact string `"mark slice-only"` (`scripts/record.py:340`). The guardian brief never names that string: its only example is `"recommend": "stay off the wall"` (`skills/guardian/SKILL.md:59`), and its prose says "say it should be marked slice-only". So point 2 works only when a guardian happens to write those exact words.
- `answer_wall` adds to `slice_only` on accept, but a later `--refuse-wall` does not take the entry out. It only sets `r["refused"] = True` (`scripts/record.py:337-345`). The picture says "only `--refuse-wall <test>` takes back one accepted earlier" (`.xv/picture.md`, The shape). A test taken back this way stays in `slice_only`, so the cleaner still removes it.
- The duplicate check matches on `test` alone, not on `file` (`scripts/record.py:341`). A test with the same name in another file that is already listed would stop this one from being added.

## 4. The picture

Proposed edits to `.xv/picture.md`, for Sean to accept:

- **The shape, edges.** "`record` reaches `orders` and `packet`" → add `run`, from `xv record report` and `xv record packet`, and note that `record` and `run` now import each other (or drop this if the edge is refused at the shape stop).
- **The shape, shape stop.** "`shape_wider_than_forecast` does not fire ... when a stop of that order was answered without sending work back" → "... answered without sending work back, at a breadth no narrower than the current one. The stop records `breadth`, and a stop with no `breadth` covers any" (`scripts/orders.py:262-267`).
- **The shape, wall recommendations.** After "Only a person's `--accept-wall <test>` accepts one", add: an accepted `mark slice-only` recommendation is listed in `slice_only` (`scripts/record.py:340-343`).
- **The shape, moves.** After "with the slice's base", add: "a test file the slice added is compared with the commit that added it" (`scripts/moves.py:58-66`).
- **The shape, session path.** "`expected_moves_wrong` stops ... after the guardian" → now also on `xv record packet`. `xv record report` for the maker and cleaner runs `expected_moves` and the wall check (`scripts/record.py:548-555`).
- **The shape, rebase brief.** "The rebase maker's brief reads the record at the old head (#138 for answers given during the rebase)" → it now reads it with the stops, budget and log lines from the rebase (`scripts/run.py:461-464`).
- **The shape, rebase notes.** Add: after an error mid-rebase, `--continue` and `--abort` read stops and budget from the rebase's notes (`scripts/run.py:379`). A staged record is put back before `--continue` (`scripts/run.py:644-646`). Leftover conflict markers stop as `rebase_stuck` before staging (`scripts/run.py:503-505`).
- **Names.** "on a replay with no conflict the check is missing (#138)" → "on a replay with no conflict it stops with `rebase_conflict`, and the question names the maker's edit" (`scripts/run.py:540-543`, `scripts/orders.py:171-175`).

## 5. The wall

I looked at the tests the red added in `tests/test_record.py`, `tests/test_refactor_kind.py` and `tests/test_slice_rebase.py`, and at the record's `slice_only` list. Each new test guards a lasting behaviour of `orders`, `record`, `moves` or the rebase, not a one-time change. None restates another. The one slice-only test is already removed. No old wall test is dead under this scenario. No recommendations.

## Scenario misses

- 8: when one rebase raises two stops of the same order and seat (every rebase stop is `originator`), and the person answers the first and aborts at the second, the first stop's log line is lost while its answer line stays. `tree_record_of_truth` drops every line containing `stop (<order>) for <seat>:`, not only the open stop's own line. The red covers one stop only (`stopped_and_answered`). I found this by reading, not by running it (evidence: scripts/run.py:381 `unanswered = [f"stop ({s['order']}) for {s['seat']}:" for s in stops`, scripts/run.py:383 `return stops, budget, [l for l in log if not any(u in l for u in unanswered)]`; to: maker)
- 4: when the scenario step ran more than once on a test file it added, `before()` returns the file at the first commit that added it, not as the scenario step left it, so a second scenario pass's edits make the maker's import-only change look like a code change and `unrecorded_move` stops. Reruns are a real path (`RerunScenarioCase`), and `pre_maker_commit` holds the file as the last scenario step left it. The red covers one pass only (`AddedTestFileMoveCase`). I found this by reading (evidence: scripts/moves.py:65 `return git(["show", f"{added[-1]}:{rel}"], root, check=False)`; to: maker)

## Door

**Door:** two-way. Code, tests, a CHANGELOG line and a config line, and the new record fields are additive. A revert undoes it. **Blast radius:** moderate. Every adopter's `xv slice rebase`, `xv record report` and `xv record packet` change. A packet with no `expected_moves` now stops on the session path (`scripts/record.py:593-597`).

## Raw data

- Slice record: `.xv/slices/2026-11-05-record-state.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`
- Wall: `xv wall diff 2026-11-05-record-state`
- Boundary: `.xv/slices/2026-11-05-record-state.boundary.md` (`xv boundary --base 5d5e75fc7a7371d74a3884cfbae919785adbb4e7`)

---
slice: 2026-11-07-defects-stops
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: A red that cannot run stops the slice, and an answered stop stays answered

No stop for two people.
The merge is Sean's, after `accept_moves`: two recorded moves, three wall recommendations, five picture edits.
One finding needs a call before the merge: `tests/test_run.py` defines `RedCannotRunTest` twice, so the first class (six tests over the 24 runner samples in `tests/data/cannot-run/`) never runs (§5).

## The scenario

1. A red that fails before any test runs (exit 126 or 127, or the runner's own words that a file could not load or no tests were found) stops the scenario step with `red_cannot_run` for the originator, naming the error; `next` stays `scenario`.
2. The runner words cover the 11 runners `failing_tests` reads; a general error name counts only when no real failing test is named.
3. A red whose tests run and fail is a failing red, even if it prints a general error name.
4. One file that cannot load beside real failures still stops.
5. An answer that bundles `slice_only_marks` accepts the marks.
6. After a directed edit, the stop the answer closed and any stop bundled with it (`ready_to_merge` included) do not fire again; the answer's `--next` stands; the suite still runs.
7. Decision 12 in the picture names a red that cannot run.
8. A `CHANGELOG.md` line names the new stop and the two fixes.
9. `EXPLORE-NOTES.md` is not in what merges.

May ignore: runners other than those 11, non-English runner output and words that change between runner versions, a red that hangs, and the defects-tools items (#147, #148, #154).

## The recording

`.xv/recordings/2026-11-07-directed-edit-refire.md`: on slice 2026-11-07-picture-lines, a directed `changelog` edit at `accept_moves` re-fired the same `accept_moves`, so Sean answered it twice.
Replay the red and the green: `cd tests && python3 -m unittest test_run.RedCannotRunTest test_run.AnsweredStopStaysAnsweredTest test_run.DefectsStopsDocsTest`.
I ran it at HEAD f89ab0e: 30 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-07-defects-stops.boundary.md`, as given:

- touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/suite`
- modules added/removed: none
- edges added: `scripts/suite → scripts/xvlib`; removed: none
- tables: none; surfaces users meet: none; new out-of-process calls: none
- shape hint: "an edge between modules was added"

## What the suite asserts after

- `run.red_cannot_run(code, output)` returns a reason for exit 126/127, for any of the runner words in `RUNNER_WORDS` (11 runners), or for a general error name when `failing_tests` finds no real failure. Otherwise it returns `None` (`scripts/run.py:75`).
- The scenario step sets `red_fails` to `None` and records `red_cannot_run` (`scripts/run.py:992-995`). `orders` fires `red_cannot_run` for the originator (`scripts/orders.py:159-164`), and `next` stays `scenario`. Tests: `WatchLoopTest.test_a_red_that_cannot_run_is_not_a_failing_red_and_stops_the_scenario_step`, plus 24 `RedCannotRunTest` tests run through `xv step scenario`, one for each of the 15 synthetic runner cases.
- `xv record answer --bundle slice_only_marks` accepts the marks (`scripts/record.py:534`).
- `orders.verdict(..., closed=)` drops the orders the answer closed (`scripts/orders.py:417-419`). `make_directed_edit` passes the answered order and its bundle (`scripts/record.py:593`). At the scenario step, a red suite counts as green when every failing test is one of the slice's own red tests (`scripts/record.py:586-591`).
- `failing_tests`, `own_red_names` and `in_own_red` moved from `run.py` to `suite.py` without changes. `run.py` dropped the `names_test` import, which it no longer used.

## 1. Shape

shape_change: no.

- Hint "an edge between modules was added" (`scripts/suite → scripts/xvlib`) does not change the shape. `.xv/picture.md:46` already names `xvlib` as "the shared base", and `xvlib` imports no project module, so the edge adds no cycle and joins no modules that were apart. The edge comes from the three helpers moving into `suite` (`scripts/suite.py:9-48`). `record` reaches them through `suite`, so the rule "`record` does not import `run`" in `skills/watch/SKILL.md:48` still holds.
- No module, table, surface or outbound call was added (boundary picture).
- `shape_breadth: narrow`, as the forecast expected ("the source change should stay in a few files"). Four source files changed: `scripts/orders.py` +11, `record.py` +16, `run.py` ±80, `suite.py` +43.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:7`: "xv-agents makes it easy … to vibe with discipline". A new stop for a red that cannot run serves that line, and it adds no new user or purpose.
- `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code") is untouched: the change adds a stop for a person and removes none.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py:1940` `test_a_stop_after_the_edit_is_written_to_the_record_and_can_be_answered` | A CHANGELOG edit at `ready_to_merge` asserted that `ready_to_merge` fires again, and that `status == "ready"` | A rename edit at `ready_to_merge` asserts that `accept_moves` fires, is logged, and can be answered; the `status == "ready"` assertion is gone | Point 6; Sean accepted it at the scenario stop (21:36:06) | Yes: point 6 says `ready_to_merge` does not fire again. Dropping `status` fits, because the new stop is `accept_moves`, not the merge stop. The old claim moved to the new `test_a_directed_edit_at_the_merge_stop_does_not_ask_again_and_the_next_stands` (`tests/test_record.py` hunk at +1961). |
| `tests/test_run.py` `RedCannotRunTest` runner-word cases | A `setattr` loop at the wall baseline | 15 plain methods, `test_runner_words_stop_00_…` to `_14_…` | Sean's answer B at the scenario stop | Not forced by the scenario. Sean settled it so the covers check can name each case. It is the slice's own red, not an old test. |

`xv wall diff`: `test_record.py` 410 → 425 assertions; `test_run.py` 437 → 464; `fewer_assertions` is empty.
The scenario agent's report allowed one change to a may-not file: `.xv/picture.md` ("decision 12 must name a red that cannot run"). The diff changes only that line (`.xv/picture.md:283`).
Slice-only tests removed: `DefectsStopsDocsTest.test_the_changelog_names_the_new_stop_and_the_two_fixes`. Kept: none.

## 4. The picture

Five lines become untrue or incomplete. Proposed edits:

- `.xv/picture.md:34` "66 edges" becomes "67 edges", because the boundary picture now lists 67 edges.
- `.xv/picture.md:47` "`suite` runs `tests.command` for `run` and `record`." Add a line after it:
  `suite` also holds `failing_tests`, `own_red_names` and `in_own_red`, which `run` and `record` both import.
- `.xv/picture.md:69` "it adds no second open stop of the same order". Add a line after it:
  After a directed edit, `orders.verdict` does not fire the order the answer closed or any order bundled with it, `ready_to_merge` included, and the answer's `--next` stands.
  At the scenario step, a directed edit counts the suite green when every failing test is one of the slice's own red tests.
- `.xv/picture.md:95` "An answer marks every listed mark `accepted`." becomes:
  An answer to `slice_only_marks`, or an answer that bundles it, marks every listed mark `accepted`.
- `.xv/picture.md:153` (the `scenario_stopped` line). Add a line after it:
  A red that fails before any test runs (exit 126 or 127, a runner's own words that a file could not load or no tests were found, or a general error name with no real failing test) stops the scenario step for the originator (`red_cannot_run`), and `next` stays `scenario`.

## 5. The wall

**A test class that never runs (needs a call).**
`tests/test_run.py:56` `class RedCannotRunTest(unittest.TestCase)` is defined again at `tests/test_run.py:1836` (`class RedCannotRunTest(WatchLoopSetup)`). The second definition replaces the first in the module.
The red run lists only the second class's tests: 30 tests, none of them `test_every_runner_failing_tests_parses_has_a_cannot_run_sample`, `test_every_runner_has_a_sample_its_own_words_catch`, `test_a_runners_own_words_stop_it_even_when_other_tests_fail_for_real`, `test_a_generic_error_name_stops_a_red_only_when_no_real_test_failed`, `test_a_no_such_file_from_a_real_failing_test_is_a_failing_red`, or `test_exit_126_and_127_cannot_run`.
So nothing that runs reads the 24 files in `tests/data/cannot-run/`, and nothing checks that `RUNNER_WORDS` covers exactly the runners in `failing_tests`. Yet the comment at `scripts/run.py:49-50` says the words "come from real output (tests/data/cannot-run)". I do not know whether those six tests would pass, because they have never run.
This is not a scenario miss: the 15 synthetic runner cases in the second class cover point 2 for all 11 runners. The choice is the originator's: send it to the maker to rename the first class so it runs, or remove the class and its data.

Recommendations (go in `accept_moves`):

- `tests/test_run.py` `DefectsStopsDocsTest.test_decision_12_in_the_picture_names_a_red_that_cannot_run`: **mark slice-only**. It checks the wording of one picture line once (`tests/test_run.py:2041-2046`), like the CHANGELOG test the cleaner already removed. On the wall it would fail on any later rewording of decision 12.
- `tests/test_record.py:1371` `OneHomeRecordTest.test_a_bundled_answer_marks_the_slice_only_marks_accepted`: **mark slice-only**. It restates `AnsweredStopStaysAnsweredTest.test_an_answer_that_bundles_slice_only_marks_accepts_them` (`tests/test_run.py:1978`): the same `--bundle slice_only_marks` answer, the same `accepted` assertion.
- `tests/test_record.py:1381` `OneHomeRecordTest.test_an_answer_to_another_order_without_the_bundle_leaves_the_marks_unaccepted`: **mark slice-only**. It restates `AnsweredStopStaysAnsweredTest.test_an_answer_that_does_not_bundle_them_leaves_them_unaccepted` (`tests/test_run.py:1986`).

No test that was on the wall before the slice is made dead.

Point 9 check: `EXPLORE-NOTES.md` is not in `git diff 1f325dd..HEAD` and not in the tree at HEAD. It was added in 34d3526 and deleted in 756e480, so it stays in the branch history unless the merge squashes.

## Door

**Door:** two-way. Reverting the slice's commits undoes the new stop and the re-fire fix; no data or public contract moves. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-07-defects-stops.md`
- Diff: `git diff 1f325dd57c3e12eef670800ea39d10166aa2b4fa..f89ab0e`
- Wall: `xv wall diff 2026-11-07-defects-stops`
- Boundary: `.xv/slices/2026-11-07-defects-stops.boundary.md` (`xv boundary --base 1f325dd57c3e`)

---
slice: 2026-11-07-defects-stops
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: A red that cannot run stops the slice, and an answered stop stays answered

This is the second guardian pass, after the amendment (point 10) and the maker's and cleaner's second passes.
No stop for two people.
No scenario miss.
The decision is Sean's, in `accept_moves`: one recorded move of an old test, no new wall recommendations, and one picture edit (§4).
The finding from the first pass is fixed: `tests/test_run.py` now defines `RedCannotRunTest` once (§5).

## The scenario

1. A red that fails before any test runs (exit 126 or 127, or the runner's own words that a file could not load or that no tests were found) stops the scenario step with `red_cannot_run` for the originator, naming the error, and `next` stays `scenario`.
2. The runner words cover the 11 runners that `failing_tests` reads. A general error name counts only when no real failing test is named.
3. A red whose tests run and fail is a failing red, even when it prints a general error name.
4. One file that cannot load beside real failures still stops the step.
5. An answer that bundles `slice_only_marks` accepts the marks.
6. After a directed edit, the stop the answer closed and any stop bundled with it (`ready_to_merge` included) do not fire again. The answer's `--next` stands, and the suite still runs.
7. Decision 12 in the picture names a red that cannot run.
8. A `CHANGELOG.md` line names the new stop and the two fixes.
9. `EXPLORE-NOTES.md` is not in what merges.
10. (Amended 2026-11-08) A suite test parses every `.py` file under `tests/` and `scripts/` and fails when a file defines a top-level class or function name twice, or when a class defines a method name twice. The build's first `RedCannotRunTest` class gets its own name, and its six tests run and pass.

May ignore: runners other than those 11, runner output that is not in English or that changes between runner versions, a red that hangs, and the defects-tools items (#147, #148, #154).

## The recording

`.xv/recordings/2026-11-07-directed-edit-refire.md`: on slice 2026-11-07-picture-lines, a directed `changelog` edit at `accept_moves` fired the same `accept_moves` again, so Sean answered it twice.
To replay it: `cd tests && python3 -m unittest test_one_name test_run.RedCannotRunSamplesTest test_run.RedCannotRunTest test_run.AnsweredStopStaysAnsweredTest test_run.FailingTestsTest`.
I ran that at HEAD 66ebb2a: 42 tests, OK. All six `RedCannotRunSamplesTest` tests ran and passed.
Whole suite (`python3 tests/run.py --jobs 4`) at HEAD 66ebb2a: 1080 tests, OK, exit 0.

## The boundary picture

From `.xv/slices/2026-11-07-defects-stops.boundary.md`, used as given:

- touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/suite`
- modules added or removed: none
- edges added: `scripts/suite → scripts/xvlib`; edges removed: none
- tables: none; surfaces users meet: none; new calls out of the process: none
- shape hint: "an edge between modules was added"

No source file has changed since the first pass (`git diff a84f93a..HEAD -- scripts` is empty).

## What the suite asserts after the change

- `run.red_cannot_run(code, output)` gives a reason for exit 126 or 127, for any of the `RUNNER_WORDS` (11 runners), or for a general error name when `failing_tests` finds no real failure. Otherwise it gives `None` (`scripts/run.py:75-87`).
- The scenario step sets `red_fails` to `None` and records `red_cannot_run` (`scripts/run.py:992-995`). `orders` then fires `red_cannot_run` for the originator (`scripts/orders.py:159-164`). Tests: `RedCannotRunTest` (24 tests through `xv step scenario`, including the 15 runner cases) and `RedCannotRunSamplesTest` (6 tests over the 24 real runner samples in `tests/data/cannot-run/`).
- `xv record answer` with `slice_only_marks` in its bundle accepts the marks (`scripts/record.py:534`).
- `orders.verdict(..., closed=)` drops the orders the answer closed (`scripts/orders.py:417-419`), and `make_directed_edit` passes it the answered order and its bundle (`scripts/record.py:593`). At the scenario step, a red suite counts as green when every failing test is one of the slice's own red tests (`scripts/record.py:586-591`).
- `OneNameOneDefinitionTest` (`tests/test_one_name.py:47-79`) parses `tests/**/*.py` and `scripts/**/*.py` with `ast`. It fails on a repeated top-level name, or a repeated method within one class, and names the file, the name and both line numbers. It does not see names inside a function body or names set at run time.
- `failing_tests`, `own_red_names` and `in_own_red` moved unchanged from `run.py` to `suite.py`.

## 1. Shape

shape_change: no.

- The hint "an edge between modules was added" (`scripts/suite → scripts/xvlib`) does not change the shape. `.xv/picture.md:45` names `xvlib` as "the shared base", and the edge comes from the three helpers that moved into `suite` (`scripts/suite.py:9-48`). The picture already counts it ("67 edges", `.xv/picture.md:34`; the boundary picture lists 67).
- Point 10 adds a test file (`tests/test_one_name.py`) and no module, table, surface or outbound call (boundary picture: no modules added, `touched` lists no test module).
- `shape_breadth: narrow`, as the forecast expected ("the source change should stay in a few files"). Four source files changed, and none changed on this pass.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:7` "to vibe with discipline": a stop for a red that cannot run, and a repo-wide check for names defined twice, both serve this line.
- `.xv/pitch.md:25` "not for people or projects that will not trust agents to write production code": not touched, because the change adds a stop for a person and removes none.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` `DirectedEditTest.test_a_stop_after_the_edit_is_written_to_the_record_and_can_be_answered` (hunk `@@ -1892,27 +1920,42 @@`) | A CHANGELOG edit at `ready_to_merge` asserts that `ready_to_merge` fires again and that `status == "ready"` | A rename at `ready_to_merge` asserts that `accept_moves` fires, is logged, and can be answered | Point 6; Sean accepted it (2026-11-07T21:36:06) | Yes. Point 6 says `ready_to_merge` does not fire again. The old claim moved into the new `test_a_directed_edit_at_the_merge_stop_does_not_ask_again_and_the_next_stands` (hunk `@@ -1598,6 +1598,34 @@`). |

These are not old tests, but the record lists them as moves:

- The `RedCannotRunTest` runner cases changed from a `setattr` loop to 15 plain methods, as Sean settled at answer B (`tests/test_run.py:1836`, the methods `test_runner_words_stop_00_…` to `_14_…`). That class is the slice's own red; the base has no `RedCannotRunTest`.
- The rename `RedCannotRunTest` → `RedCannotRunSamplesTest` (`tests/test_run.py:56`) is the build's class, which is not at the base or in the wall baseline c91cc5f. The record has no move for it, and it needs none.

`xv wall diff`: `test_record.py` 410 → 422 assertions; `test_run.py` 437 → 462; `fewer_assertions` is empty.
The scenario agent's report allowed one change to a may-not file: `.xv/picture.md` ("decision 12 must name a red that cannot run"). The decision 12 line is at `.xv/picture.md:287`. The other picture lines in the diff are the five edits Sean directed at `accept_moves` (commit 94b4b11).
Slice-only tests removed (all four were accepted by Sean): `DefectsStopsDocsTest.test_the_changelog_names_the_new_stop_and_the_two_fixes`, `DefectsStopsDocsTest.test_decision_12_in_the_picture_names_a_red_that_cannot_run` (with its class), `OneHomeRecordTest.test_a_bundled_answer_marks_the_slice_only_marks_accepted`, `OneHomeRecordTest.test_an_answer_to_another_order_without_the_bundle_leaves_the_marks_unaccepted`. Kept: none.

## 4. The picture

One line is now incomplete.
`.xv/picture.md:124` records a guard on the suite's own shape ("No test class that holds tests is the base of another, and `tests/test_suite_runner.py` `NoRerunTest` guards this.").
Point 10 adds a second such guard, at `tests/test_one_name.py:47`, and the picture does not name it.
Proposed line, added after `.xv/picture.md:124`:

  No `.py` file under `tests/` or `scripts/` defines a top-level class or function name twice, or one method name twice in a class, and `tests/test_one_name.py` `OneNameOneDefinitionTest` guards this.

The five edits from the first pass are in place as worded (`.xv/picture.md:34`, `48`, `71-72`, `98`, `157`), and so is decision 12 (`.xv/picture.md:287`).

## 5. The wall

The first pass's finding is fixed. `tests/test_run.py:56` is now `class RedCannotRunSamplesTest`, and `tests/test_run.py:1836` keeps `RedCannotRunTest`. `OneNameOneDefinitionTest.test_no_file_under_tests_or_scripts_defines_a_name_twice` passes, and the six sample tests run and pass (`python3 -m unittest -v test_run.RedCannotRunSamplesTest`: 6 ok). The comment at `scripts/run.py:49-50` says the runner words "come from real output (tests/data/cannot-run)", and a test that runs now checks that.

I make no new wall recommendations.
I looked at the three `OneNameOneDefinitionTest` tests (`tests/test_one_name.py:47-79`): the first is a lasting guard for the whole repo, and the other two test the scanner itself, so none of them guards a one-time change.
I also looked at `RedCannotRunSamplesTest` beside the 15 runner cases in `RedCannotRunTest`: one reads real runner output and the other runs synthetic output through `xv step scenario`, so neither only restates the other.
The three slice-only marks from the first pass were accepted and removed. No test that was on the wall before the slice is made dead.

Point 9 check: `EXPLORE-NOTES.md` is not in `git diff 1f325dd..HEAD` and not in `git ls-files` at HEAD. It was added in 34d3526 and deleted in 756e480, so it stays in the branch history unless the merge squashes.

## Door

**Door:** two-way: reverting the slice's commits undoes the new stop, the re-fire fix and the name check, and no data or public contract changes. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-07-defects-stops.md`
- Diff: `git diff 1f325dd57c3e12eef670800ea39d10166aa2b4fa..66ebb2a`; since the first packet: `git diff a84f93a..66ebb2a`
- Wall: `xv wall diff 2026-11-07-defects-stops`
- Boundary: `.xv/slices/2026-11-07-defects-stops.boundary.md`

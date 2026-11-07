# Exploration notes: defects-stops

Branch `explore/defects-stops`, from main at d87a59c. Built outside the slice process.

## What changed, per issue

### #141 a red that cannot run
- `scripts/run.py`: new `red_cannot_run(code, output)` and a `CANNOT_RUN` pattern. When the red command exits non-zero and its output shows it never ran its tests (import error, `_FailedTest`, no tests collected or found, command not found, exit 126 or 127, build or setup failed), `post_step` records `checks.scenario.red_cannot_run` and leaves `red_fails` as `None`.
- `scripts/orders.py`: `red_cannot_run` fires `scenario_stopped` for the originator, naming the error. `next` stays `scenario` (existing `next_step` behaviour for a stop after scenario).
- A red that runs and some tests fail is unchanged.

### #143 bundled answer and slice-only marks
- `scripts/record.py` `cmd_answer`: marks are accepted when the stop's order is `slice_only_marks` or `slice_only_marks` is in the answer's `--bundle`.

### #151 directed edit re-fires the closed stop
- `scripts/orders.py`: `verdict(data, after, config, closed=())` drops fired orders named in `closed`.
- `scripts/record.py` `make_directed_edit`: passes the answered stop's order plus its bundle as `closed`. The suite still runs; the closed stop does not re-fire, and the answer's `--next` stands (nothing overwrites it).

## Choices to review
- #141 detection is a text pattern over the red's output, not a per-runner parse. It covers unittest, pytest, jest/vitest, go, cargo, rspec, but it can misfire if a real failing test prints, say, "ImportError" in its own output. The pattern is deliberately broad (it errs toward stopping). A tighter option: require that `failing_tests(output)` finds no real test name besides `_FailedTest`.
- #141 uses the existing `scenario_stopped` order, not a new one. A new order would need a CHANGELOG line and a rules entry either way (the issue says it takes a CHANGELOG line; I did not edit it).
- #151 closes by order name: any fired order equal to the answered stop's order (or bundled) is skipped, regardless of whether the edit could have changed its cause. Other orders still fire.
- #151 exempts `ready_to_merge`: an existing test (`test_a_stop_after_the_edit_is_written_to_the_record_and_can_be_answered`) says an edit made at the merge stop raises a fresh merge stop, since the edit changes what would merge. I kept that. The person may want it otherwise.
- #143 and #151 closed-set include the bundle, so a bundled order is also not re-fired after a directed edit.

## Open questions
- Should the scenario-step stop for #141 be its own order name so `xv-retro` and the rules can count it separately?
- Does `.xv/picture.md` decision 12 need a sentence naming "red that cannot run"? Not edited here.

## Tests added
- `tests/test_run.py`, `WatchLoopTest`: `test_a_red_that_cannot_run_is_not_a_failing_red_and_stops_the_scenario_step`, `test_a_red_that_runs_its_tests_and_some_fail_is_still_a_failing_red`.
- `tests/test_record.py`, `OneHomeRecordTest`: `test_a_bundled_answer_marks_the_slice_only_marks_accepted`, `test_an_answer_to_another_order_without_the_bundle_leaves_the_marks_unaccepted`.
- `tests/test_record.py`, `DirectedEditTest`: `test_a_directed_edit_does_not_fire_again_the_stop_its_answer_closed_and_the_next_stands`.
- The three fix tests were confirmed to fail on main before the fix.

## Running tests
Individual test files import `helpers`, so run them from `tests/` (`cd tests && python3 -m unittest test_record...`) or use `python3 tests/run.py --jobs 4`.

## Final suite count
1028 tests (1023 on main + 5 new), OK.

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
- #151 closes by order name: any fired order equal to the answered stop's order (or bundled) is skipped, regardless of whether the edit could have changed its cause. Other orders still fire.
- #143 and #151 closed-set include the bundle, so a bundled order is also not re-fired after a directed edit.

## Answered by Sean (2026-11-07)

1. **Should the #141 stop be its own order?** Yes. It is now `red_cannot_run` (seat originator, `next` stays `scenario`), in `scripts/orders.py`. Orders are not registered anywhere else in `scripts/` or `tests/` (each is just a `fire(...)` call; `xv-retro` counts stops by the name in the record), so nothing else needed the name. The slice that opens from this build owes the CHANGELOG line (not edited here).
2. **Tighter detection for #141.** Done in `scripts/run.py`:
   - exit 126 or 127: cannot run, as before;
   - `RUNNER_WORDS`, one entry per runner `failing_tests` parses (11), anywhere in the output: cannot run, even when other tests fail for real (one file that cannot load makes part of the red give no evidence);
   - `GENERIC_ERRORS` (`ModuleNotFoundError`, `ImportError`, `SyntaxError`, `LoadError`, `Cannot find module`, `command not found`, `No such file or directory`) count only when `failing_tests` finds no real failing name; a `_FailedTest` name is not real.
   A red for a missing-folder defect that prints `No such file or directory` while its tests fail is now a failing red.
3. **#151: ready_to_merge exception.** Removed from `make_directed_edit`: the answered stop and its bundle never re-fire after a directed edit, `ready_to_merge` included, and the answer's `--next` stands. The old test now uses `accept_moves` (a test-rename edit adds a moved test with a record, so the edit really causes it).

### Per-runner words and where they came from

All run for real on this machine (scratch folder under /tmp/claude-1000/xvr, nothing global): unittest and pytest 9.2 (python 3.14), jest, vitest 5.1, mocha, jasmine 7.0, Playwright (node 26, no browsers needed for a load or no-tests failure), RSpec 3.13 (ruby 3.4, with the erb gem it needs), minitest, go 1.27, cargo 1.99 (rustup into the scratch folder). Samples are in `tests/data/cannot-run/<runner>-{load,none}.txt`, stack frames trimmed, paths rewritten to /work. No runner had to be taken from docs.

| runner | words | note |
|---|---|---|
| unittest | `_FailedTest`, `Failed to import test module`, `Ran 0 tests`, `NO TESTS RAN` | load sample also has a real FAIL |
| pytest | `ERROR collecting`, `Interrupted: N errors during collection`, `collected 0 items`, `no tests ran` | |
| jest | `Test suite failed to run`, `No tests found, exiting` | |
| vitest | `Failed Suites`, `No test files found` | a file that cannot load prints `FAIL  file [ file ]` under `Failed Suites` |
| go | `[build failed]`, `[setup failed]`, `no packages to test`, `matched no packages` | load sample also has a real `--- FAIL`. `[no test files]` is not a word: it prints on a good red |
| RSpec | `An error occurred while loading`, `errors occurred outside of examples`, `No examples found`, `0 examples, 0 failures` | |
| Jasmine | `No specs found` | a spec file that cannot load prints only Node's error, none of Jasmine's words (it never starts). That case rides the generic names, which hold because no test ran |
| minitest | `0 runs, 0 assertions` | a file that cannot load prints a Ruby `LoadError` only; generic |
| mocha | `Exception during run:`, `No test files found` | |
| cargo | `could not compile`, `no test target named` | `running 0 tests` is not a word: every empty target and doc-test prints it on a good red |
| Playwright | `Error: No tests found` | a spec that cannot load prints only `Error: Cannot find module`; generic |

Only RSpec's, go's and unittest's load samples carry a real failing test next to the broken file. Jest's default reporter names no failing test, so `failing_tests` finds none there (existing behaviour; its load case is caught by its own words).

## Open questions
- Does `.xv/picture.md` decision 12 need a sentence naming "red that cannot run"? Not edited here.
- The runner words are exact strings from these versions. A runner upgrade that rewords one (Jest and Vitest have before) lets the red count as failing again if no generic name is printed. The sample test only catches a missing runner, not a reworded one. Worth a note in the learnings, or a recheck when a runner is bumped?
- Jasmine, Playwright and minitest have no words of their own for a file that cannot load, so a red there that has a generic name AND a real failing test elsewhere counts as failing. Neither runner runs anything after a load failure in the cases tried, so this should not arise, but I only tried CommonJS, ESM and syntax errors.
- The `red_cannot_run` stop owes a CHANGELOG line (and a rules or picture mention if the slice wants one): not edited here, as asked.

## Tests added
- `tests/test_run.py`, `WatchLoopTest`: `test_a_red_that_cannot_run_is_not_a_failing_red_and_stops_the_scenario_step`, `test_a_red_that_runs_its_tests_and_some_fail_is_still_a_failing_red`.
- `tests/test_record.py`, `OneHomeRecordTest`: `test_a_bundled_answer_marks_the_slice_only_marks_accepted`, `test_an_answer_to_another_order_without_the_bundle_leaves_the_marks_unaccepted`.
- `tests/test_record.py`, `DirectedEditTest`: `test_a_directed_edit_does_not_fire_again_the_stop_its_answer_closed_and_the_next_stands`.
- The three fix tests were confirmed to fail on main before the fix.

### Added in the 2026-11-07 round
- `tests/test_run.py`, new `RedCannotRunTest` (6 tests): `test_every_runner_failing_tests_parses_has_a_cannot_run_sample` (reads the runner names from the `failing_tests` docstring, expects 11, and a sample plus a `RUNNER_WORDS` entry for each, so a runner added later fails here until it has both), `test_every_runner_has_a_sample_its_own_words_catch`, `test_a_runners_own_words_stop_it_even_when_other_tests_fail_for_real`, `test_a_generic_error_name_stops_a_red_only_when_no_real_test_failed`, `test_a_no_such_file_from_a_real_failing_test_is_a_failing_red` (real unittest and pytest output), `test_exit_126_and_127_cannot_run`.
- `tests/test_run.py` `WatchLoopTest`: the cannot-run test now expects `red_cannot_run`; the failing-red test also asserts no `red_cannot_run`.
- `tests/test_record.py` `DirectedEditTest`: new `test_a_directed_edit_at_the_merge_stop_does_not_ask_again_and_the_next_stands`; `test_a_stop_after_the_edit_is_written_to_the_record_and_can_be_answered` now uses `accept_moves` from a rename edit.
- Red first: before the code change, `RedCannotRunTest` failed (no `RUNNER_WORDS`; the good-red samples counted as cannot-run; the generic-name cases wrong), the `red_cannot_run` stop test failed with `'scenario_stopped' != 'red_cannot_run'`, and both #151 tests failed (the merge-stop test returned a second stop, exit 10 not 0; the rewritten test saw `ready_to_merge` fire again beside `accept_moves`). Each was seen failing on the old code, then passing.

## Running tests
Individual test files import `helpers`, so run them from `tests/` (`cd tests && python3 -m unittest test_record...`) or use `python3 tests/run.py --jobs 4`.

## Final suite count
1035 tests (1023 on main + 5 new + 7 in the 2026-11-07 round), OK.

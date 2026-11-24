# Recording: a settled not-covered outcome stops again on later test writer passes (#205)

Taken from two slice records on main (d4011e4). Each section is one stop, in order, with the fields the record keeps. The scenario step was called `scenario` then; it is the test writer now.

## Slice `2026-11-19-removal-line`

Outcome 7 (a CHANGELOG line) was first settled at 02:26:48, in an answer that sent the slice back. It fired again at 02:34:23, 03:13:20 and 03:22:56, each time worded a little differently. Sean gave a standing answer at 03:13:20.

### 2026-11-20T02:26:48+00:00: `red_misses_scenario`, bundled: red_misses_scenario

- question: The scenario agent did not cover 3. A removal committed before its move is recorded is taken (the pairing case): The record keeps no 'step began' commit and the command reads HEAD today; the scenario does not say how the start commit is found, so I could not write a test without guessing.
- answer: 1
- pick: 1
- settled: Amendment 8: the start commit is step_start, or the open pairing's start_commit, else HEAD; outcome 7 (the CHANGELOG line) has no test
- sendback: True
- sendback_to: scenario
- bundle: ["red_misses_scenario"]

### 2026-11-20T02:34:23+00:00: `red_misses_scenario`

- question: The scenario agent did not cover 7. A line in CHANGELOG.md: settled by Sean Kennedy: outcome 7 has no test
- answer: 1
- pick: 1
- settled: Outcome 7 has no test, as settled at the last stop

### 2026-11-20T03:13:20+00:00: `red_misses_scenario`

- question: The scenario agent did not cover 7. A line in CHANGELOG.md.: Settled by Sean Kennedy at the red_misses_scenario stop: outcome 7 has no test.
- answer: for this slice, answer 1 for me when this same outcome-7 stop comes back
- pick: 1
- settled: Outcome 7 has no test, as settled twice before

### 2026-11-20T03:22:56+00:00: `red_misses_scenario`

- question: The scenario agent did not cover 7: A CHANGELOG.md line is a one-time wording change; the cleaner/guardian check reads the file, and no test pins it.
- answer: 1, by Sean's standing answer for this slice: "for this slice, answer 1 for me when this same outcome-7 stop comes back"
- pick: other
- settled: Outcome 7 has no test, as settled before

## Slice `2026-11-20-names`

Points 5 and 13 were settled at the `unrecorded_move` stop at 21:54:46, which bundled `red_misses_scenario` and sent the slice back. `red_misses_scenario` fired again inside `red_cannot_run` at 22:07:32, and on its own at 22:46:13.

### 2026-11-20T21:54:46+00:00: `unrecorded_move`, bundled: red_misses_scenario, slice_only_marks

- question: The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py, tests/test_allowed_commands_prompt.py, tests/test_answer_in_prompt.py, tests/test_briefs_picture.py, tests/test_budget_cap.py, tests/test_budget_cap_turns_session.py, tests/test_by_name.py, tests/test_check.py, tests/test_diff_count.py, tests/test_from_build.py, tests/test_init_allow_list.py, tests/test_init_allow_list_bare.py, tests/test_init_allow_list_prompt.py, tests/test_init_allow_list_split.py, tests/test_kept_pick.py, tests/test_listen.py, tests/test_names_upgrade.py, tests/test_orders.py, tests/test_packet.py, tests/test_pairing.py, tests/test_pairing_build.py, tests/test_picture_lines.py, tests/test_prototypes.py, tests/test_record.py, tests/test_refactor_kind.py, tests/test_removal_line.py, tests/test_repass.py, tests/test_retro.py, tests/test_run.py, tests/test_slice_rebase.py, tests/test_spend.py, tests/test_suite_red_quote.py. Revert them, or record why the scenario forces it.
- answer: sure, 1 is fine
- pick: 1
- settled: The 32 test files are the build's renames, recorded one move per file by Sean Kennedy. The test writer adds a test that --next test-writer is accepted. Point 5's old scratch file is covered by the build's OldScratchFileTest, and point 13's word scan is the inspector's to check by reading. Amendment 16: ci/github/xv-listener.yml keeps its name. The README upgrade-notes test is slice-only. Next is scenario.
- sendback: True
- sendback_to: test-writer
- bundle: ["red_misses_scenario", "slice_only_marks"]

### 2026-11-20T22:07:32+00:00: `red_cannot_run`, bundled: red_misses_scenario

- question: The red command cannot run: it failed before any test ran (ERROR: test_agent_names (unittest.loader._FailedTest.test_agent_names); ImportError: Failed to import test module: test_agent_names). That is not a failing red, so the record holds no evidence the red fails for the reasons the scenario names. Fix the command or the test files so the tests run, then run the scenario step again.
- answer: 1
- pick: 1
- settled: The red command runs from tests/ (cd tests && python3 -m unittest test_agent_names), per .xv/rules.md. Point 5's scratch file and point 13's word scan stay not covered, as settled at the last stop. Next is scenario.
- sendback: True
- sendback_to: test-writer
- bundle: ["red_misses_scenario"]

### 2026-11-20T22:46:13+00:00: `red_misses_scenario`, bundled: red_misses_scenario

- question: The scenario agent did not cover the test writer's old scratch file xv-scenario-scratch-<id>.json is still read with a warning (part of 5): Settled by Sean: the build's OldScratchFileTest covers it; the red cannot set up a build without touching source.
- answer: answer 1 when this same stop comes back
- pick: 1
- settled: Point 5's old scratch file is covered by the build's OldScratchFileTest, and point 13's word scan is the inspector's to check by reading, as settled before; this stop re-fired on settled points (#205). Next is maker.

## What should have happened

After a person answered a stop for an outcome, a later test writer pass that lists the same outcome in `not_covered` raises no new `red_misses_scenario` for it, however the pass words it. An outcome no one settled still stops.

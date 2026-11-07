# Exploration notes: explore/g-kept-pick

An exploration build for #117 (the kept-pick half) and #121, made outside XV's slice process. It is a working build to write a scenario from, not a release. The slice that opens from it does the picture, the CHANGELOG line, the docs and the decision record with the person.

## What runs

### #117: a slice may start from a kept pick

`xv prototype pick <id> --variant a|b|c --by <name>,<name> --scenario-file <file> --keep [--share-build]`

- `--keep` keeps the pick's branch (`xv/<id>-proto-<v>`) as the build this slice starts from. Without `--keep` the pick works as before: all three are discarded.
- Work the prototype left uncommitted in its worktree is committed on its branch first (`xv(<id>): prototype <v>, kept as the build`). Its copy of the slice record is left out.
- The branch is merged onto the slice branch (`xv(<id>): keep prototype <v> as the build`, a `--no-ff` merge). The slice's `base` does not change; it stays the branch the slice merges into.
- The record gets `build: {"kind": "kept_pick", "ref": "xv/<id>-proto-<v>", "variant": "<v>", "commit": "<sha>"}` and `build_shared: yes|no`. The kept variant's entry in `prototypes` gets `kept: true`. The decision and the log line say "picked b, kept as the build".
- The other two prototypes are discarded as before. The kept one's worktree, its context, is removed too; only its branch stays (Decision 72: the maker is a new context).
- From there the slice runs the way #113's slices from an exploration do, using F's code unchanged: the scenario agent writes the red in a checkout at the base, the red must fail there, then it is cherry-picked onto the slice branch and run on the build. A test that fails there goes to the maker with no stop. A red that passes there skips the maker.
- `record.build_commit` uses the kept pick's recorded `commit` when there is one, so a deleted or moved branch does not break the wall check.
- When the build is not shared, the scenario agent's record copy also has `prototypes: []` and no `prototype_sessions`. Before this change the copy listed the kept branch name and its run command.
- Refused: `--keep` with `none`; `--share-build` without `--keep`; a kept pick whose branch is gone or holds nothing the slice branch lacks (its worktree was removed with the work uncommitted). A refusal changes nothing in the record.
- From the #117 comment: the `prototypes_ready` stop now says the pick may be thrown away or kept (`--keep`). It also names each variant that did not finish, with its error, and says a second `xv prototype start` runs it again (`orders.unfinished`).
- `skills/watch/SKILL.md`: the prototype section gives `--keep` and says to ask the people whether to keep the pick. The "slice from a build" section now covers a kept pick too.

### #121: errored variant spend, and a vanished worktree

- `agentcli.run` builds its result before it writes the run log. If the log write fails, it raises `agentcli.RanError`, an `XVError` that carries `result`.
- `prototypes.run_one` keeps the result of an agent that ran: from `RanError.result`, or from a holder that `build_one` fills right after the run. An errored entry then carries `spend` and `session`. The spend loop records a `prototype-<v>` row for an errored variant that has spend, so it counts against that variant's budget. A second start then gives it only what is left. A run that takes it past its budget sends it to `ran_out` as usual.
- `agentcli.run` checks that `cwd` exists. If it is missing, before the run or when `FileNotFoundError` is raised, it says "the working folder is gone: <path>" instead of "agent CLI not found". `prototypes.build_one` makes the same check first. In the real vanish case the earlier failure was a bare `[Errno 2] No such file or directory: '<wt>'` from git, raised before the agent CLI.

## Design choices to review

1. **Kept in place, not as a new slice.** The prototype slice already turns into the feature slice at the pick, so the kept pick stays in the same slice: same id, same branch, a merge of the pick's branch. Another way would be `xv slice new --from xv/<id>-proto-<v>`, a new slice. That works today with no change, but it records `kind: exploration`.
2. **A merge commit, not a reset.** The slice branch already carries the record, the axis and the side-by-side commits, so the build is brought in with a `--no-ff` merge. The build commit is an ancestor of the slice branch, as it is for `--from`. `xv slice rebase` will flatten that merge as git does. The wall check still compares against the recorded `commit`.
3. **The project layer stays as the slice has it.** Any `.xv/` file the prototype changed is set back to the slice branch's copy during the merge, except `.xv/prototypes/<id>/<v>/`, its recording and script. So a prototype that "bent" the picture or the config does not bring that edit in with the build. An exploration from `--from` has no such filter. Should the two match?
4. **The kind is `kept_pick`.** The issue says "none, a kept pick, or an exploration". `kept_pick` reads plainly, and `xv prototype` keeps its name.
5. **The kept branch stays after close.** Nothing deletes `xv/<id>-proto-<v>` at close or merge, the same as the exploration ref. Should `xv close` delete it?
6. **`--share-build` on the pick**, mirroring `xv slice new --share-build`, was cheap to add.
7. **The blind copy drops `prototypes` for every unshared build**, not only kept picks. For an exploration that list is empty anyway.

## Open questions for the person

- The prototype brief (`skills/maker/prototype.md`) still says "Your version is discarded when the pick is made, whichever it is" and "Nothing you write is a candidate for the main line." With a kept pick, the first is no longer always true. That is a brief change (binding decision 1: two people and a CHANGELOG line), so I left it alone. Should the prototype agent be told its version may be kept? Being told might change how it builds.
- `xv prototype start` still runs on a slice whose pick was made, and it would delete the kept branch (`git branch -D`). Should it refuse once `kind` is no longer `prototype`?
- The `prototypes_ready` question changed, and so did the watch brief: a CHANGELOG line is owed. Do the README, `docs/decisions.md` decision 71 ("every prototype is discarded at the pick") and the picture's `build` line change in the slice? I did not edit them; they are outside this build's allowed edits.
- `prototype_budget_spent` does not list unfinished variants; only `prototypes_ready` does, as the #117 comment asked. Should it list them too?
- `agentcli.RanError` is caught only in the prototype path. `xv step` would still lose the spend of an agent whose run log could not be written. That is outside #121's scope; does it need its own issue?

## Tests added

`tests/test_prototype_errored_spend.py` (new):
- `ErroredVariantSpendTest.test_a_variant_that_errors_after_its_agent_ran_keeps_that_runs_spend`
- `ErroredVariantSpendTest.test_a_second_start_gives_the_errored_variant_only_what_is_left_of_its_budget`
- `ErroredVariantSpendTest.test_an_errored_variant_whose_run_passed_its_budget_has_run_out`
- `GoneFolderTest.test_a_missing_working_folder_is_not_reported_as_a_missing_agent_cli`
- `GoneFolderTest.test_a_missing_agent_cli_is_still_reported_as_one`
- `GoneFolderTest.test_a_run_log_that_cannot_be_written_keeps_the_result`

`tests/test_prototypes.py`:
- `PrototypesGitSetupTest.test_a_vanished_worktree_is_reported_as_a_missing_working_folder_not_a_missing_agent_cli`

`tests/test_kept_pick.py` (new):
- `KeepThePickTest`: `test_a_kept_pick_is_recorded_as_the_build_with_its_branch_and_commit`, `test_the_kept_branch_stays_and_the_other_two_are_discarded`, `test_the_slice_branch_has_the_kept_build_and_not_the_others`, `test_the_base_stays_the_branch_the_slice_merges_into`, `test_the_decision_and_the_log_say_the_pick_was_kept`, `test_a_pick_not_kept_discards_all_three_and_has_no_build`, `test_keep_with_none_is_refused`, `test_share_build_without_keep_is_refused`, `test_keep_with_share_build_records_build_shared_yes`, `test_a_kept_pick_whose_branch_holds_nothing_is_refused_and_changes_nothing`
- `PrototypeCommitsItsOwnWorkTest.test_work_the_prototype_committed_itself_is_kept_too`
- `PrototypeBendsTheLayerTest.test_the_project_layer_stays_as_the_slice_has_it`
- `RedOnTheKeptPickTest`: `test_the_scenario_agent_runs_at_the_base_without_the_kept_build`, `test_the_scenario_agent_is_not_told_where_the_kept_build_is`, `test_a_shared_kept_pick_is_named_to_the_scenario_agent_as_a_reference_only`, `test_a_red_that_fails_on_the_kept_build_goes_to_the_maker_with_no_stop`, `test_the_maker_works_from_the_kept_build_in_a_new_context`
- `KeptPickHasTheFixTest.test_a_red_that_passes_on_the_kept_build_skips_the_maker`
- `PickStopWordsTest`: `test_the_pick_stop_says_the_pick_may_be_kept_as_the_build`, `test_the_pick_stop_names_each_variant_that_did_not_finish_and_its_error`, `test_the_pick_stop_names_no_failure_when_all_finished`

`tests/fake_agent.py`: the prototype fake takes `FAKE_PROTO_BUILDS`, `FAKE_PROTO_FIX=<v>`, `FAKE_PROTO_EDITS_LAYER=<v>` and `FAKE_PROTO_COMMITS=<v>`.

## Suite

`python3 tests/run.py --jobs 4` ends with `Ran 1051 tests in shard 1/1` and `OK`: main's 1023 plus 28 new tests (6 + 1 + 21).

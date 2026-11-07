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

## Answered by Sean (2026-11-07)

1. **Brief (G1).** Do not tell the prototype agent its version may be kept. Remove only the words that became untrue, and say that people pick on how it feels in use, not on the code. Not applied here (a brief change); the exact sentences are under "Draft for G1" below.
2. **`xv prototype start` after the pick (G2).** It refuses once `kind` is no longer `prototype`: "<id> is no longer a prototype slice (it is feature), so it builds no more prototypes". It changes nothing, so it can never delete a kept branch (`prototypes.start`).
3. **`.xv/` edits from a build (G3).** Both build paths drop them, and the slice log names each dropped file ("dropped from the build, which may not change the files people own: ..."). Kept pick: as before, except the prototype's own `.xv/prototypes/<id>/<v>/` folder, which stays; the log line is new. `xv slice new --from <ref>`: new. Every `.xv/` file that differs between the base and the build ref is set back to the base's copy (a file the build added is removed), before the slice's own record is written, so the record files `xv slice new` writes are kept. Both paths use one function, `xvlib.drop_layer_edits` (and `xvlib.dropped_line` for the words). Reason: decision 78.
4. **Kept branch at close (G4).** `xv close` deletes `xv/<id>-proto-<v>` when the build is a kept pick and its recorded commit is already in the slice branch. A `--from` ref is never deleted.
5. **Decision 71 (G5).** Replaced by a new decision. Draft under "Draft for G5" below. Not applied (docs/ is outside this build).
6. **`prototype_budget_spent` (G6).** Lists each unfinished variant and its error, with `orders.unfinished`, as `prototypes_ready` does.
7. **Spend lost in `xv step` when a run log cannot be written (G7).** Ignore it: too rare to file. No issue, no code.

Round 3 (Sean's answers to the three open questions):

8. **The dropped-files log line.** A list of file names is enough. The line now also names the build commit (short hash) the dropped content lives in: "dropped from the build, which may not change the files people own: <files> (the build's copy: `git show <hash>:<file>`)". Both paths pass the commit to `xvlib.dropped_line(dropped, commit)`: the recorded pick commit for the kept pick, the resolved `--from` commit for `xv slice new --from`.
9. **A base that moved on.** A file is named as dropped only when the build changed it since the merge-base of the build and the base. `xvlib.drop_layer_edits` now restores every `.xv/` file that differs between the base and the build (so the tree is right), but returns, and so names, only the files in the diff from the merge-base. A file that differs only because the base moved on takes the base's copy with no log line. `xv slice new --from` passes `git merge-base <base> <build>` as `since`. Kept pick: the same case (a prototype branch behind the slice branch on `.xv/`) can arise, since people may commit to `.xv/` on the slice branch while the prototypes build. It was already handled there: the kept pick always compared with `git merge-base HEAD <pick>`, and a merge keeps the slice branch's copy of a file only it changed. So no code change; a guard test shows it.
10. **Pick `none`.** Stays `kind: prototype`, and `xv prototype start` still runs on it. Kept; a guard test added (none existed).

## Draft for G1: the prototype brief (`skills/maker/prototype.md`)

Two sentences go. Nothing is added that says the version may be kept.

Paragraph 1, old:

> You are not building the product. Your version is discarded when the pick is made, whichever it is.

New:

> You are not building the product. People will pick among the three on how each feels in use, not on the code.

Build step 2, old:

> 2. There is no test wall here. You may change what you need, tests included. Nothing you write is a candidate for the main line.

New:

> 2. There is no test wall here. You may change what you need, tests included. People judge the version by using it, not by reading its code.

## Draft for G5: a decision that replaces 71

Next free number in `docs/decisions.md` is 92 (the last is 91).

New decision, to add after 91 in a new section or at the end:

> 92. **At the pick, the people choose: throw every prototype away, or keep the pick as the build its slice starts from.** Replaces 71. Without `--keep`, nothing changes from 71: every worktree and branch is removed, the picked one too; the recordings stay in the slice record as evidence. With `--keep`, the pick's branch is merged onto the slice branch (`xv/<id>: keep prototype <v> as the build`), the record says `build: {kind: kept_pick, ref, variant, commit}`, and the other two are removed. The slice then runs as one opened with `xv slice new --from`: the scenario agent writes the red blind at the base, the red must fail there, and it then runs on the build. The pick is restated as the scenario either way, and the maker is a new context (72 stands). The build's edits to `.xv/` are dropped and named in the log, as for `--from` (78): files people own change only through people. The pick takes two names and may name a user who took part. A prototype slice that has been picked is no longer a prototype slice, so `xv prototype start` refuses on it. `xv close` deletes the kept branch, since xv made it and its commits are in the slice branch; it never deletes a `--from` ref. The prototype agent is not told its version may be kept: people pick on how it feels, and a version built to be kept would be built differently.

One-line marker to add at the end of 71:

> *Replaced by 92: the pick may now be kept as the build.*

Other lines that will need to change (not edited here):

- `README.md`, the stops table, line 326: `| Prototypes ready to pick from | two people |` becomes `| Prototypes ready to pick from; the pick is thrown away or kept as the build | two people |`.
- `README.md`, the method block ("Build to find out", about line 99-100): generated from the map; run `bin/publish-readme.py` (#117 says it is stale).
- `README.md`, the `xv slice new` description if it names `--from`: add "the build's edits to `.xv/` are dropped and named in the slice log".
- `.xv/picture.md`, the line that starts "No database. State is files" (about line 27): change "The record holds `build` (`none`, or `{kind: exploration, ref}`)" to "(`none`, `{kind: exploration, ref}`, or `{kind: kept_pick, ref, variant, commit}`)"; after "With `xv slice new --from <ref>` the branch starts at the build" add "and every `.xv/` file the build changed is set back to the base's copy, the files named in the log"; after "A variant that ran out cannot be picked." add "`xv prototype pick --keep` merges the pick's branch onto the slice branch as the build; the other two are removed. `xv prototype start` refuses once `kind` is not `prototype`. `xv close` deletes a kept pick's branch, never a `--from` ref." Also add `prototype_budget_spent` to the sentence that says it names each variant that ran out: "and each variant that did not finish, with its error".
- `skills/watch/SKILL.md` (done in this build) and `skills/maker/prototype.md` (G1 above).

## New open questions

- A `.xv/` file the build changed and the base changed too (both moved) is named as dropped and takes the base's copy. The log says the build's copy is in the commit, but not that the base also changed it. Enough?
- The kept pick restores `.xv/` files by diffing the slice branch with the pick (merge in progress), so a file the slice branch changed and the prototype did not is restored to the same copy, a no-op. Nothing to decide, but the picture should say it compares with the merge-base only for the names.

## Tests added

Round 3 (red before the fix, run on the round-2 code: the four behaviour tests failed; the two guards passed):

`tests/test_from_build.py`:
- `ProjectLayerFromBuildTest.test_the_log_line_names_the_build_commit_the_dropped_content_lives_in` (red: no hash in the line)
- `BaseMovedOnFromBuildTest.test_a_file_the_base_changed_takes_the_bases_copy_and_is_not_named` (red: the moved file was named)
- `BaseMovedOnFromBuildTest.test_a_build_that_changed_no_project_file_logs_no_drop_though_the_base_moved` (red: a drop line was logged)

`tests/test_kept_pick.py`:
- `KeptPickLogNamesTheCommitTest.test_the_log_line_names_the_build_commit_the_dropped_content_lives_in` (red: no hash)
- guard: `SliceMovedOnBeforeTheKeptPickTest.test_a_project_file_only_the_slice_branch_changed_is_kept_and_not_named` (passes before and after)
- guard: `PickNoneGuardTest.test_a_pick_of_none_stays_a_prototype_slice_and_start_still_runs_on_it` (passes before and after)

Round 2 (all fail on the code before the fix unless marked as a guard):

`tests/test_kept_pick.py`:
- `AfterTheKeptPickTest.test_a_second_prototype_start_is_refused_and_the_kept_branch_stays` (red: start ran and deleted the branch)
- `AfterTheKeptPickTest.test_close_deletes_the_kept_branch_its_commits_are_in_the_slice_branch` (red: the branch stayed)
- `PrototypeBendsTheLayerTest.test_the_log_names_each_project_file_the_build_brought_and_was_dropped` (red: no log line)
- `BudgetStopListsUnfinishedTest.test_the_budget_stop_names_each_variant_that_did_not_finish_and_its_error` (red: not listed)

`tests/test_from_build.py`, `ProjectLayerFromBuildTest`:
- `test_the_build_s_edits_to_the_project_layer_are_not_in_the_slice` (red: the edits were kept)
- `test_the_log_names_each_dropped_file` (red: no log line)
- guards, which pass before and after: `test_the_slice_s_own_record_is_kept`, `test_close_does_not_delete_the_ref_people_made`, `test_a_build_that_changed_no_project_file_logs_no_drop`

Round 1:

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

`python3 tests/run.py --jobs 4` ends with `Ran 1066 tests in shard 1/1` and `OK`: main's 1023 plus 43 new tests (28 in round 1, 9 in round 2, 6 in round 3).

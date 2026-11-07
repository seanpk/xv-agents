# Exploration notes: `explore/defects-tools`

Built outside XV's slice process, from main at d87a59c. Covers #147, #148 and #154. Not a finished release: no CHANGELOG, picture or learnings edits. Open a slice from it with `xv slice new --from explore/defects-tools`.

## What changed, per item

### #147

- **Point 1, a session-mode scenario step leaves its checkout and nothing lands the red.** `xv step scenario` in session mode now keeps the checkout's path (and the slice's HEAD then) in a small file in the worktree's git dir. `xv record report <id> scenario -` on a slice from a build runs `xv land-scenario <id>` (a new subcommand of run.py, because record must not import run; the report goes on its stdin), which calls `run.land_session_scenario`: it lands the red (the same `land_scratch` the agent path uses), runs it on the base and on the build, takes the wall baseline at the base, saves `checks.scenario` (so `xv orders --after scenario` sees `red_conflicts_with_build`, `red_fails`, and the rest), and drops the checkout. A second `xv step scenario` drops the earlier checkout; `xv close` drops one left over.
- **Point 2, a hand-landed red is not replayed.** After F the red is kept on `refs/xv/<id>/red` before the cherry-pick, so a conflict stop already leaves it there and a later pass starts from it. The commit-subject replay the issue describes is gone. What I changed: the `red_conflicts_with_build` question now says the red is on that ref and a later pass starts from it. A test shows the ref survives the conflict stop and the next pass starts from it.
- **Comment 1, the red ref is never deleted.** `close()` deletes `refs/xv/<id>/red`.
- **Comment 2, a deleted build ref breaks `xv record report`.** `xv slice new --from` now stores the build's commit in the record (`build.commit`). `record.build_commit` reads it, falls back to the ref, and returns "" when neither resolves. `wall_for_build` then leaves the files unrecorded and adds a `note`, so `xv orders` fires `unrecorded_move`: it stops for a person and never passes (decision 12). No crash, and the wall check is saved.

### #148

- **1, the "drop it" command for a new file.** `rebase_stop` finds which of the maker's edited files are new (not in HEAD) and passes `maker_new`. The `rebase_conflict` question says `rm <file>` (or `git rm -f <file>` if staged) for a new file and `git checkout -- <file>` for a tracked one, and notes that `git status` shows a new file and `git diff` does not.
- **2, `--accept-wall` / `--refuse-wall` match on the test name alone.** The flags take `file::test`. A bare name still works when one recommendation has it. A bare name that two files share is refused, naming each `file::test`, rather than answered together.

### #154

- **1, rebase rehashes a red file from main.** For a file both main and the slice touched, the wall hash is now taken at the baseline commit as replayed on the new base (it was the bare new base). The slice's own red edits stay in the hash, and main's edits come in with it.
- **2, rebase replays a directed CHANGELOG edit as a new line.** The rebase runs with `merge.conflictStyle=diff3`, and the union-file resolver reads the base side: a base line the other side edited or dropped is not kept from this side. The edited line replaces the old one.
- **3, `tests/run.py` said OK with a file missing.** I could not reproduce the drop. The runner now fails when a `test_*.py` file in the folder gave no test id, and when the workers' "Ran N tests" total is not the number collected for the shard. This guards the symptom; the cause is unknown.
- **5, one move recorded twice.** `same_move` compares assertions with whitespace and commas removed.
- **6, `xv slice new` with a missing `--recording` path.** It now checks `--recording` and `--scenario-file` are files before it makes the worktree and branch, and refuses with a message.

## Answered by Sean (2026-11-07)

- **#154 item 4, one name for a brief step.** Answered: a step the brief tells the cleaner to do is reported as `brief: slice-only removal`; a real standard is cited by its exact `###` heading text from `.xv/standards.md`. Changed: `retro.counts()` skips rules that start with `brief:` as it skips `baseline` (after the `.xv/standards.md:` prefix is stripped). Old `.xv/retro/*.counts.json` files are not rewritten. Not done here, for the slice (skills/ untouched). Sentences the cleaner brief (`skills/cleaner/SKILL.md`) needs:
  - In the `applied` format line (now `"rule": ".xv/standards.md: <the rule> | baseline: <smell>"`): "`rule` is the exact `###` heading text of the standard from `.xv/standards.md`, `baseline: <smell>` for a baseline smell, or exactly `brief: slice-only removal` for a step this brief told you to take. Never reword a heading, and never name a brief step as a standard."
  - In the "Slice-only tests" step, after the removal command: "Report each removal in `applied` as `{"rule": "brief: slice-only removal", "where": "<file>"}`. It is a step of this brief, not a standard, and `xv retro counts` does not count it."
- ~~**#147 point 1, session-mode `joined_unsafely` red.**~~ (answered above) Answered: yes, do what the CLI path does. Changed: `xv record report <id> scenario` keeps the red from before the report when the reported command is joined with `;`, `||`, `|`, `&` or a newline; the landing (`xv land-scenario`) then sets `checks.scenario.red_joined`, and `xv orders --after scenario` fires `scenario_stopped`. The check (`joined_unsafely`) and the covers parser moved to a new `scripts/names.py` that run.py and record.py both import (record still does not import run). For a slice not from a build, session mode has no landing, so `red_joined` is not set there (the earlier red is still kept); see open questions.
- **#148 item 2, names in the wall flags.** Answered: keep the ambiguous-bare-name refusal, and accept the forms the covers check takes. Changed: `record.wall_matches` uses `COVERS_SEPARATOR` and `covers_name_found` (now in `names.py`) against the recommendation's file text: `file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`, a path prefix. Class and module parts must be in that file. An exact test name still matches first; a bare name two files share is still refused, naming each `file::test`.
- **Keep diff3 for the whole rebase.** Answered: yes. No change.
- **Added by the coordinator: `xv slice new --ignore` repeats.** Only the last value reached "## May ignore". Now each `--ignore` is kept, in order, and written as paragraphs separated by a blank line; a single one is as before. For the slice: README and the xv-slice skill may need a line saying `--ignore` repeats.

For the slice that opens from this build (not edited here): README, the watch/xv-slice/cleaner briefs and the picture need the `build.commit` field, the `file::test` (and other forms) of `--accept-wall` / `--refuse-wall`, `xv land-scenario`, `brief:` names, and the repeating `--ignore`. CHANGELOG, learnings, standards and retro are the slice's.

- **Session mode on a slice not from a build, a joined red (answered 2026-11-07).** Answered: `xv record report <id> scenario -` sets `checks.scenario.red_joined` itself (and `red_fails` to null) when the reported red is joined unsafely and the slice has no build, so `xv orders --after scenario` fires `scenario_stopped` as on the CLI path and on a slice from a build. record.py still does not import run.py.
- **A wall-flag path prefix naming a different file (answered 2026-11-07).** Answered: no change. Ambiguity is still refused, so it fails loud.
- **Repeated `xv slice new --ignore` (answered 2026-11-07).** Answered: with more than one value, "## May ignore" is a Markdown bullet list (`- <value>`), one per value, in order. A single `--ignore` is a plain paragraph as before. This replaces the blank-line paragraphs above.

No open questions remain from this round.

## Left for a person

- **#154 item 4, the cleaner names one rule many ways.** Not fixed. Options: (a) the cleaner skill cites a rule by the exact heading of the line in `.xv/standards.md`, and says what to write for a baseline smell; (b) `xv retro counts` maps each `applied` rule to the nearest standards heading (a fuzzy match, with a miss kept as its own row); (c) the cleaner report gets a fixed `rule_id` field beside the free text, and counts group on it. The question: which, and whether the old counts files are rewritten.
- **#147 point 1, session-mode `joined_unsafely` red.** On the agent path a refused red (parts joined other than with `&&`) is reset to the earlier red before the maker sees it. In session mode `apply_report` has already stored the report's red, and I did not add the reset. Question: should `xv record report` restore the earlier red there?
- **#147 point 1, no verdict or commit on the session path.** `xv record report` saves the checks; it does not apply the verdict or commit the record, as before. `xv orders` gives the verdict.

## Choices to review

- A bare `--accept-wall` name two files share is now an error, not "answer both". The issue said "still take a bare name when only one recommendation has it"; the two-file case is my reading.
- `same_move` ignores commas and whitespace only. `==` and `!=` stay different. Wider matching would merge real different moves.
- `build.commit` is a new field in the record. The picture and the README do not name it. Old records have none and fall back to the ref.
- The rebase's `-c merge.conflictStyle=diff3` applies to every conflict in that rebase, including the maker's; the maker sees diff3 markers in conflicted files. `conflict_markers` and `keep_both_sides` handle the `|||||||` line.
- The `red_conflicts_with_build` wording (above) is a new sentence in a stop's question.
- README, the watch brief and the picture were not touched. A slice that changes what `xv record` accepts (the `file::test` flag) should change README and the briefs that state it; see the rule in `.xv/rules.md`.

## Tests added

- `tests/test_slice_rebase.py`: `test_a_directed_changelog_edit_replaces_the_old_line_in_a_rebase_not_adds_one_beside_it`, `test_a_red_edit_to_a_file_main_also_changed_stays_in_the_wall_after_a_rebase`, `test_the_question_for_a_new_test_file_the_maker_added_says_how_to_drop_it`, `test_the_question_for_an_edited_test_file_still_names_git_checkout`.
- `tests/test_record.py`: class `WallAnswerByFileTest` (6 tests), class `SameMoveTest` (4 tests).
- `tests/test_recording.py`: class `SliceNewMissingFileTest` (2 tests).
- `tests/test_suite_runner.py`: `test_a_test_file_that_gives_no_test_fails_the_run_and_is_named`, `test_a_worker_that_exits_early_with_zero_fails_the_run`.
- `tests/test_from_build.py`: `test_the_conflict_stop_says_the_red_is_kept_on_its_ref_and_a_later_pass_starts_from_it` (in `BuildConflictTest`); classes `SessionScenarioReportTest` (6 tests), `SessionScenarioConflictTest` (1 test), `CloseRedRefTest` (3 tests), `BuildRefDeletedTest` (4 tests).

Each was run against the code before the fix and failed there.

### Tests added on 2026-11-07

- `tests/test_retro.py`: `test_a_step_the_brief_names_is_not_counted_as_a_rule_but_a_standard_is`.
- `tests/test_from_build.py` (`SessionScenarioReportTest`): `test_a_red_joined_with_a_semicolon_is_not_kept_and_the_stop_fires`, `test_a_red_joined_unsafely_restores_the_earlier_red`.
- `tests/test_record.py` (`WallAnswerByFileTest`): five form tests (`colons`, `hash`, `dots`, `file_and_class`, `arrow`), plus `test_a_class_form_the_file_does_not_have_names_nothing` and `test_an_ambiguous_name_in_the_hash_form_is_still_refused`. The last two guard rules that already held, so they passed before the fix; the other five failed before it.
- `tests/test_recording.py`: class `SliceNewIgnoreRepeatTest`: `test_every_ignore_value_reaches_the_record_in_order` failed before the fix; `test_a_single_ignore_works_as_before` guards the old behaviour and passed.

Every behaviour test other than those two guards was run against the code before its fix and failed there.

### Tests added on 2026-11-07 (second round)

- `tests/test_from_build.py`: class `SessionScenarioNoBuildJoinedTest`: `test_a_joined_red_sets_red_joined_and_the_stop_fires` (failed before the fix), `test_a_red_joined_with_and_and_is_kept_and_sets_no_red_joined` (guard, passed before).
- `tests/test_recording.py` (`SliceNewIgnoreRepeatTest`): `test_more_than_one_ignore_is_a_bullet_list_one_per_value_in_order` (failed before the fix); `test_a_single_ignore_works_as_before` now also checks a single value has no bullet.

## Final suite count

`python3 tests/run.py --jobs 4` ends with OK: Ran 1056 tests (1023 at main d87a59c plus 33 new). After the 2026-11-07 changes: Ran 1068 tests, OK. After the second round: Ran 1071 tests, OK.

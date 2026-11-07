---
status: checked
checked_by: Sean Kennedy
generated_by: outsider read
date: 2026-10-24
---

# The shared operating picture

This picture is written one sentence per line, and a list item's extra lines line up with the item's text.

## What an outsider sees
A toolkit for running software changes through AI agents with people kept in charge.
It has two parts: prompts ("skills") for seven agents (watch, forecaster, scenario, maker, cleaner, guardian, listener) and five person-facing skills, plus a standard-library Python CLI, `xv`, that does the checkable work: it keeps a per-change record, hashes the tests (the "wall"), computes stop conditions, and runs the agents headless or in CI.
Its stated rule is "an agent may stop, it may not decide" (README).
It is also the tool its own team uses to try XV on other repos (v0.2.0 came from one trial).
One known user so far (2026-10-24).

## Users
The people who use xv-agents directly are the team XV describes: people building software for users.
They could be a team of professionals, or a non-technical person with an idea.
Sean Kennedy sits with them.

- The seats inside a team: the person who set the work going, the two people, the chief engineer (`scripts/orders.py`, `defaults/config.yml`).
- The end users of an adopting system are indirect, reached only through the listener (Sentry, PostHog, feedback files).

## The shape
- Runs on agent harnesses: Claude Code, opencode, Grok.
  Codex runs as a step (first run 2026-11-04, the scenario-defect eval, 6/6): the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`, `session_of` takes its `thread_id`, and `evals/harnesses.json` has a `codex` entry on `gpt-6.1-terra` with the sandbox off; AGENTS.md and the skills still load, so the brief is not the whole prompt.
  Cursor reads the same skill format and has not been run (README).
  `xv init` gives Claude Code agent lines a starter Bash allow list; other harnesses' lines are left as written.
  `xv prompt` shows each Claude Code agent its own line's Bash rules as the commands it may run, with cautions: chain only listed forms, no extra flags in front, no pipe to an unlisted program.
- 25 modules, all flat Python files: `scripts/*.py` (22) and `evals/{run,grade,report}.py`.
  `.xv/boundary-all.md` shows 66 edges between them.
  `record` and `run` reach `suite`.
  `record` reaches `moves` and `wall`; `run` reaches `moves` through `record`; `moves` reaches `wall` and `xvlib`.
  `run` reaches most of the others: `agentcli`, `boundary`, `orders`, `packet`, `prompt`, `prototypes`, `record`, `retro`, `spend`, `wall` and `xvlib`.
  `orders` reaches `spend` and `xvlib`.
  `record` and `evals/report` reach `spend`.
  `record` reaches `orders`, `packet`, `moves` and `wall`.
- `bin/xv` is the only entry point.
  It maps each command name to one script and runs it.
  `init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`, the largest script.
  `slice` also runs `xv slice rebase` (`--onto`, `--continue`, `--abort`).
- Roughly: `xvlib` is the shared base (config, git, record paths, and the shared test-name matcher `names_test`; `covers` names use `run.covers_name_found`).
  `record` owns the slice record, and the build rules: `has_build`, `build_commit` and `wall_for_build`.
  `suite` runs `tests.command` for `run` and `record`.
  `xv record offer` can put one directed edit on an option, and refuses one that does not fit its kind (`skills/watch/SKILL.md` lists the refusals).
  `xv record answer --pick` on that option makes the edit, runs the suite and the orders, and commits the file, the record and, after the guardian, the packet line, in the person's name (`record.make_directed_edit`).
  Both the offer and the answer read and edit the file in the slice's worktree, wherever they are run from.
  `orders` holds the stop rules.
  After `rebase`, `orders` decides `rebase_conflict`, `rebase_dropped`, `rebase_stuck`, `rebase_suite_red` and `rebase_red_ref`; `record.apply_verdict` writes a rebase stop as it does any other, and `orders.budget_before` checks before each rebase maker run.
  On a slice from a build, `xv slice rebase` moves `refs/xv/<id>/red` onto the new base before it runs the suite, and stops with `rebase_red_ref` when the red does not apply there.
  `prompt.build` takes `part` (the rebase part of the maker's brief) and `saved` (the record from before the rebase).
  `wall.baseline` takes `keep` and `skip`, and `wall.hashes_at` hashes files at a ref.
  `shape_or_pitch` fires on `yes`, not on `accepted`; `accepted` holds only when `accepted_by` names a decision in the slice's `decisions` list with `order: shape_or_pitch` (`xv run`, `xv record packet`), and `xv guard` always reads it as `yes`.
  `shape_wider_than_forecast` does not fire when `shape_change` is `accepted`, or when a stop of that order was answered without sending work back, at a breadth no narrower than the current one; the stop records `breadth`, and a stop with no `breadth` covers any (the answer marks a send-back `sent_back`).
  `accept_moves` counts moves by file and assertion, except moves marked `expected` (`scripts/orders.py`).
  After the maker and the cleaner, `moves` compares each test file that changed since the wall baseline, or that the record already holds as expected, with the slice's base and a test file the slice added with its newest `red` commit, against `expect_moves` and `renames`.
  It records a fit as a move marked `expected`, which replaces a hand-recorded entry for the same file.
  After the guardian, `expected_moves_wrong` stops for the originator when the packet's `expected_moves` does not match the record.
  One move is recorded once.
  `xv record report` for the maker and the cleaner runs the expected-move and wall checks.
  `packet.packet_checks` is the one place where `xv step` and `xv record packet` run the packet lint and the `expected_moves` count.
  It also writes a note, not a stop, naming each `.xv/picture.md` line that holds more than one sentence (`packet.crowded_picture_lines`); a second run replaces the note.
  When no stop blocks, `orders` also returns a send-back with seat `watch`, naming where the slice goes and the misses: `scenario_miss` after the guardian, `red_misses_point` after the scenario step.
  `orders.verdict` also returns `next`.
  After the scenario step, `next` is `cleaner` when the red failed on the base and passes on the build.
  One function, `record.apply_verdict`, writes the stop or the send-backs, and `next`, on `xv step`, `xv run`, `xv record packet`, and `xv record answer` after a directed edit; it adds no second open stop of the same order.
  `record.guardian_facts` turns the packet into the record's fields on every path.
  For `scenario_miss`, a miss is a repeat when an earlier pass sent back the same key, and the repeat stops for the originator.
  For `red_misses_point`, `orders.miss_run` counts the send-backs of the same point in an unbroken run of scenario reports.
  The third miss in a row stops for the originator.
  A pass that covered the point, an amendment (`amended_at_report`, written by `xv slice amend`), or a person's answer ends the run.
  `xv prototype` still applies its own stop (#117).
  `wall` holds the test hash check and `red_gaps`, which lists each flag and `xv` command written in backticks in the scenario that no red file has (a command's words together, in order), except an `xv` command that is a subcommand at the slice's base (run checks this with the base's own `bin/xv <words> --help`, from `git archive`), nor a flag that the command it follows already has at the base (in its `--help` text), and a gap named in an answered `red_misses_scenario` stop that was not sent back.
  The base is read with `tarfile`.
  When the base has no `bin/xv`, the installed `xv` answers instead (`run.base_xv_dir`).
  In the CI form (`xv wall check --base`), a red file that existed at the base is covered only for the tests the slice added.
  A removed or changed line in it, other than a blank, comment or import line (matched per file type in `IMPORT_MATCHERS`), makes it unrecorded unless a recorded move names the file.
  A red file new in the slice is covered whole.
  `spend` reads harness logs and owns the one per-row token count (`row_tokens`) that the budget, the guide, the retro and the eval report use.
  `spend.slice_spend` is the count the slice budget uses: every step except the prototypes.
  `orders.budget_before` checks it before every step, `session` steps too; the after-maker check and the retro use the same count.
  `agentcli` and `prompt` build and run the agent calls.
  `agentcli.run` gives every agent CLI a closed stdin when the prompt is in argv.
  `boundary`, `packet` and `check` are the guardian's checks.
  `packet` also holds the allowed field values (`ALLOWED`, `YES_NO`).
  `listen`, `retro`, `promote` and `prototypes` are the side loops.
  `run.close` writes `modules_touched`, from `boundary.change` against the slice's base, and `maker_sendbacks`.
  A person's answer that sends work back keeps `sent_back_to: <step>`.
  `retro.reworked` finds the modules that at least `limits.rework_slices` closed, sent-back slices touched; `due` and the retro prompt both use it on slices created since the last retro.
  `retro.accept` only prints the `xv slice new --kind refactor` command for a candidate of kind `refactor`.
  After the scenario step, `slice_only_marks` lists slice-only marks for the person who set the work going; they accept the marks or run `xv record unmark`.
  An answer marks every listed mark `accepted`.
  An accepted mark is kept when the scenario runs again and is not asked about again.
  A mark whose `checks` names a file listed in `tests.slice_only_files` (default `CHANGELOG.md`) is accepted by the watch with a log line and is not asked about.
  An agent's report cannot set `accepted` on its own mark.
  The guardian's `wall_recommendations` go to the same person in `accept_moves`.
  Only a person's `--accept-wall <test>` accepts one, and only `--refuse-wall <test>` takes back one accepted earlier; an accepted `mark slice-only` recommendation is listed in `slice_only`, and refusing it later takes it out, matched on file and test; a new recommendation not named is refused, and an agent's report sets neither.
  Giving either flag on another kind of stop, or both on one test, is refused.
  Each answered `accept_moves` stop keeps `accepted_wall` and `refused_wall`.
  `decisions` reads every slice record through `retro.records()` and counts answered stops per order: picks equal to the recommendation, `new_info: none`, and causes.
  `record.apply_report` keeps a scenario report's `old_tests_forced` and `may_not_files`, and a report without them clears them.
  `prompt` shows them to the maker only, and only the picture from `may_not_files`.
  `recording` and `playwright_agents` serve the scenario agent.
  `install` and `adapt` handle distribution.
- Outbound calls: `evals/grade`, `boundary`, `check`, `listen`, `recording`.
  The docs add the agent CLIs, `gh`, and the fetched harness doc pages.
- `defaults/` is the starter `.xv/` that `xv init` copies into every adopting repo.
  A change there reaches every new adopter.
  `xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian lines, built from the test command it chose, so the written `config.yml` differs from `defaults/config.yml`.
  Changing the test command later does not change the list, and `xv prompt` then shows the agent that stale list as its allowed commands.
  `xv init` runs the guessed test command once to check it (`test_run` in its output).
  `xv init --no-try` skips that and prints `test_run_skipped` instead.
  The suite's `RepoCase` passes `--no-try` by default; `tests/test_init_tries.py` and the `--trial` test in `tests/test_install.py` opt out.
  `worktrees:` may be a path or a block with `path`, `base`, `setup` and `teardown`; `{worktree}` is substituted already shell-quoted.
- This repo's suite runs through `tests/run.py --shard i/n --jobs k` (standard library; unittest output, one process per job, each printed in turn).
  `.xv/config.yml` runs `--jobs 4`.
  The `tests` workflow runs four shards on each Python, eight jobs at once.
  No test class that holds tests is the base of another, and `tests/test_suite_runner.py` `NoRerunTest` guards this.
- No database.
  State is files: `.xv/slices/<id>.md` (front matter plus log), `.xv/decisions/`, `estimation.md`, `learnings.md`, `config.yml`.
  The slice record also holds `amended_at_report`, the report count at the last amendment.
  Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`.
  The branch starts from `--base`, else `worktrees.base`, else `origin/HEAD`, else HEAD.
  With `xv slice new --from <ref>` the branch starts at the build, and `base` stays the merge target.
  The record holds `build` (`none`, or `{kind: exploration, ref}`) and `build_shared` (`yes` or `no`).
  `--share-build` needs `--from`.
  A slice from a build also has a git ref, `refs/xv/<id>/red`, which holds its red at the base.
  `xv slice new` refuses a base without a committed `.xv/config.yml`, `pitch.md` and `picture.md`.
  The worktree's own config, from the base, gives `worktrees.setup`, which runs before the forecaster, and `worktrees.teardown`, which runs at close.
  Both run under `tests.timeout`, and a timed-out command keeps its output.
  A prototype slice's record holds `prototype_budgets`, one budget for each of a, b and c, in the shape of `budget` and free to differ; a variant's spend counts only against its own budget.
  A variant has run out when its spend, before the start or after its own run, reaches its budget.
  The others still run, and then `prototype_budget_spent` stops for the originator, naming each variant that ran out and its spend.
  The originator answers a budget raise alone; a pick, `none` included, is for two people unless the repo runs solo.
  A variant has finished when it has a recording and did not run out.
  A second `xv prototype start` reruns every variant that has not finished, from HEAD, on what is left of its budget, and keeps the finished ones.
  Each variant's git setup (worktree remove, branch delete, worktree add) runs one at a time under a lock in `prototypes`; the agents still run together.
  A variant whose setup or run raises any error is recorded with no recording and with its `error`, so it has not finished and a second start reruns it.
  The error goes into its section of the side-by-side file and the slice log.
  A variant with an `error` cannot be picked, and the refusal says its setup or run failed.
  A new `--axis` keeps none.
  A variant that ran out cannot be picked.
  After the maker, a scenario step checks the red in a temporary detached worktree at `pre_maker_commit`, saved before the maker's first run, with the red files copied from HEAD and `worktrees.setup` run first; in a slice from a build, it runs in the scratch checkout at the base instead.
  In a slice from a build, the scenario agent runs in a temporary detached worktree that starts at the tip of `refs/xv/<id>/red` when the base is an ancestor of that tip, and at the base otherwise.
  Unless the build is shared, the agent's record copy has `build: none`, `branch` set to the base, and no commit that is not an ancestor of the base.
  The red runs there, and the wall baseline is hashed there.
  Its commit moves the ref, and it is cherry-picked onto the slice branch; a conflict stops with `red_conflicts_with_build` for the originator.
  The red then runs on the build, and the maker's prompt names the tests that fail.
  A session scenario step makes that checkout and names it.
  A red command joined at the top level by anything but `&&` (`;`, `||`, `|`, `&` or a new line, outside quotes) is not run and not kept as the slice's red; the scenario step stops for the originator (`scenario_stopped`), and `next` stays `scenario`, so the scenario agent rewrites it with `&&`.
  After the scenario step, `red_misses_scenario` stops for the originator before the maker when the report lists a `not_covered` item, when `red_gaps` lists anything, or when the check cannot read its input: no `## Scenario` heading, `covers` or `not_covered` missing or not a list, `covers` empty, or with an item whose `test` is not one name, a list of non-empty strings, or a string joined with `,` or `;`, or a `covers` name that matches no whole word in any red file.
  On a later scenario pass, the coverage kept from earlier passes (`checks.scenario.covers_kept`) is added to the report's `covers` before the check, except when the record's `next` is `maker` (a pass that went on to the maker ends the run), so an empty `covers` does not stop when something was kept; each kept name is checked again against the red files.
  A `covers` name whose last part is a slice-only test that the cleaner removed by a recorded move does not stop; only the move's assertion before a `;` is read.
  A `covers` name may start with a red file's path or module and is split by `::`, `.`, `#`, `/` or ` > `; it matches when each part after the path is a whole word in that red file, in order (`run.covers_name_found`); a name whose test part is empty stops, and the stop names the name that does not match.
  A numbered point of the scenario or an amendment that is in neither `covers` nor `not_covered` sends the slice back to the scenario agent (`xv step` and `xv run` compute this).
  The match ignores backticks, `*` and `_` in both the point and the item (`run.norm`).
  The send-back lists each missed point as `<number>. <text>`, an item the check accepts, and says every point goes in on each pass.
  A `covers` item that is a number, or starts with one, covers the scenario's own point with that number.
  It never covers an amendment's point (`run.missed_points`).
  After the scenario step, `unrecorded_move` stops for the originator before the maker when any test file that existed at the base, under `tests.paths` or in the red, lost or changed a line other than a blank, comment or import, unless a recorded move names the file.
  In a slice from a build, a test file the build changed stops once.
  The maker and the cleaner record a move in their own names (`--by maker`, `--by cleaner`).
  The scenario agent records none: it says what it moved in its report, and the stop puts it before the person.
  A person's name reaches the record only through an answer at a stop (#93).
  A directed test edit records a move with `by` set to the person, through that answer (#132).
  Any step that stops, other than at `ready_to_merge`, or ends with no report keeps `next` on itself.
  So a `--resume` answer must name `--next`, and it must carry `settled` when `--next` is the stop's saved step or an earlier one, or when the pick is `other`, except for stops raised before their work started: `setup_failed` saved at step `setup`, a prototype stop other than `prototypes_ready` and `prototype_budget_spent`, and the `budget_spent` stop that `xv step` marks `pre_step`, answered with `--next` that step (#82, #84).
  `xv record stop` takes `--step`, as `xv step` saves one.
  A decision file and its `decisions` entry keep `settled` with the person's words.
  An answer to `ready_to_merge` also writes a decision.
  A decision's `who` is a list (an old record may hold a string).
  A rebase in progress keeps its notes in the git dir as `xv-rebase-<id>.json`: the stops, spend, budget and named commits from before it began.
  At a stop, the saved stops and budget are written over the tree's copy of the record.
  On finish they go into the record; on abort, spend, answered stops and a budget set during the stop are written back.
  The rebase maker's brief reads the record at the old head, with the stops, budget and log lines from the rebase applied.
  After an error mid-rebase, `--continue` and `--abort` read the notes' stops and budget.
  A staged record is put back before `--continue`.
  Leftover conflict markers stop as `rebase_stuck` before staging.
  A refactor slice's scenario step runs no agent until the scenario is amended.
  It runs the suite, and `suite_not_green_at_start` stops for the originator unless the suite is green.
  After an amend, the scenario agent writes a red as on a feature slice, and only the amendment's points need `covers` or `not_covered`.
- Surfaces: the `xv` CLI, `skills/*/SKILL.md`, three GitHub Actions examples in `ci/github/`, and `.github/workflows/` (tests, weekly drift check).
- `evals/` holds a small "pantry" fixture app, scenarios, and recorded runs on three harnesses.

## Names
- "Originator", "the person who set the work going" and `set_by` appear to mean the same seat.
  Someone other than `set_by` may answer an `originator` stop, so a teammate can pick up the work; `answered_by` records who (#62).
- "Slice" is the unit of change.
  "Record" is the slice file.
  "Packet" is the guardian's output (the listener's is "the packet from production").
  `expected_moves` in a packet's front matter is the record's count of expected moves.
- "The wall" is the test hash check.
  "The shape" means the system's structure, but also "shape change" in a packet.
  Both senses are used.
  `shape_change` is `yes`, `no` or `accepted`; `pitch_contradiction` is `yes` or `no` (#85).
  `scenario_miss` is `yes` or `no` and optional; a missing one reads as `no` (#96).
- The shape conversation opens on a shape change, and before and after a burst.
  A stall (`repeated_failure`, `diff_growing`) is not a shape conversation; it puts four choices to the person who set the work going: continue, reshape the slice, raise the budget, or bring in a second person (#86).
- The maker and the scenario agent read the picture and pull its binding decisions; they do not edit it, with one exception: the maker may edit `.xv/picture.md` only when the scenario report names it in `may_not_files`.
  No other protected file is exempt (`run.post_step`).
  The guardian lists the edit.
  The rebase maker may not edit a test file or `.xv/picture.md`: on a conflict replay such an edit stops with `rebase_conflict`, and on a replay with no conflict it stops with `rebase_conflict` too.
  The edit is left uncommitted in the worktree, and the question says `--continue` keeps it and `git checkout -- <file>` drops it.
  The watch edits it only when a person directs it, in its own commit naming that person.
  This is not a directed `doc` edit, because that kind refuses `.xv/`.
  Accepting a picture change is a person's (#88, #68, #90).
- "Picture" is `.xv/picture.md`, but the guardian's packet carries a "boundary picture".
  These are different things.
- "Skill" and "agent" are used almost interchangeably.
  A skill is the file.
  An agent is a fresh context running it.
- Hyphen means skill and space means command (`xv-init` and `xv init`).
  The README states this.
- "Seat": `originator`, `two_people`, `chief_engineer`.
  `watch` is the seat on a send-back the watch made itself; no person fills it.
- `maker_sendbacks` is the larger of two counts: the maker's spend rows minus one, and the stops answered "sent back to the maker" or with `sent_back_to: maker`.
  A maker run inside `xv slice rebase` counts too (Sean, 2026-11-05).
- "Tokens" in a budget, forecast, guide row or retro means input + output + cache write, with no cache reads, since 2026-10-26 (#28).
  Guide rows from before then counted cache reads and are not rewritten.
- "The budget" is the slice budget and covers every step after the pick.
  "Prototype budgets" are the per-variant ones (2026-10-27, #34, #36).
- `settled` is what an answer made true, written by the watch as the person's scribe; the person's words stay in `answer`.
  An offer is the numbered options the watch puts on an open stop (`xv record offer`), each with the `settled` text it would record (2026-10-29, #80).
  An option may carry one directed edit (#132).
- An exploration is a build made with an agent outside XV.
  A slice opens from it with `--from`.

## Where the code and the docs disagree
Settled with Sean on 2026-10-24.
The code is right in each case; the README is behind.
- README line 38 says the method has not run on a real change; 0.2.0 came from a real init, and a first slice is running in a trial repo.
  The Status section was brought up to date by slice 2026-10-24-readme-drift.
- The README's generated block is written from https://xtremevibing.com/map/ by `bin/publish-readme.py` in seanpk/xtremevibing.com.
  Edit it there, not here.

## Questions an outsider would ask
Answered by Sean on 2026-10-24.
- Run under XV? Yes, from 2026-10-24.
- Harnesses: Sean mostly uses Claude Code.
  Any harness that reads skills must stay possible.
- `evals/results/runs/` belongs in the repo: the runs are evidence for the evals.
- Who triages learning issues on this repo: Sean.
- Who decides: a one-person team (`seats.two_people: solo`), Sean as chief engineer.

## Vision
Through use, xv-agents is becoming the set of agents that help teams vibe with discipline: hold XV's values, adhere to its principles, and easily implement its practices.
At the same time, the shared learnings from people and teams using xv-agents will help XV itself get better.

## Decisions that bind
Drafted from the repo's docs; Sean cut and added on 2026-10-24.

1. A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`.
   (`CHANGELOG.md`, opening)
2. Each skill is in the open Agent Skills format, for any harness, and each brief works as the whole prompt of a fresh context.
   (`README.md:3`, `docs/briefs.md`)
3. The scripts are Python 3.10 or later, standard library only.
   `bin/xv` is the one entry point.
   (`README.md:200`, `docs/decisions.md` 3)
4. Learnings travel as issues on this repo.
   Adopt an open learning before inventing one.
   No count of sightings triggers a pull request; two people decide.
   (`docs/positions.md`)
5. Nothing is posted in public without a person's approval.
   (`docs/positions.md`)
6. Dollars are recorded only where a harness reports them, never estimated.
   (`docs/decisions.md` 19, 48)
7. Agent run logs stay local and are never committed.
   (`docs/decisions.md` 17)
8. In docs read on GitHub, file references are relative Markdown links.
   (commit `a242c96`)
9. Records and front matter are YAML whose values are JSON, so every file is valid YAML.
   The config parser fails loudly on what it cannot read.
   (`docs/decisions.md` 1, 2)
10. The standing orders all live in `scripts/orders.py`, a pure function of the record and the config.
    A stop raised because an action failed (`setup_failed`, `axis_not_named`) is not a standing order; the command that failed raises it, or `orders` raises it from what the record says failed.
    (`docs/decisions.md` 10, 11)
11. Exit codes are a contract with CI: 10 a person must act, 0 nothing left, 2 an error or a refusal.
    (`docs/decisions.md` 12)
12. A check whose input is broken or that cannot run stops for a person; it never passes.
    Read-only agents are checked, not trusted.
    (`docs/decisions.md` 13, 51, 78)
13. Every brief opens with Own the result, keeps the stop line, ends with its may-not list, what it writes to the record, and when to stop, and points to files rather than restating them.
    (`docs/briefs.md`, "Every brief")
14. A version that renames anything in `.xv/` carries its upgrade steps in `CHANGELOG.md`.
    (`docs/decisions.md` 74)
15. Python 3.10 through 3.13 are supported; CI tests both.
    (`.github/workflows/tests.yml`)

The builder's other choices are in [`docs/decisions.md`](../docs/decisions.md); they do not bind on their own.

## In motion
Nothing (2026-10-24).
Sean and Claude work on this repo one change at a time.

## Runtime budgets
None yet (2026-10-24).
Set them when use shows one is needed.

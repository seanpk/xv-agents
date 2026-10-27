# Changelog

Every change to a brief, a may-not list, a standing order, or a check an agent is judged by, with who agreed it. A change to an agent is Decide from evidence: two people, written down short. A version line without two names is a draft.

## Unreleased

- `xv boundary` tries the importing file's own folder first only when that folder has no `__init__.py`, so a bare import inside a package resolves the way Python does and flat scripts are unchanged. This changes a check the guardian reads; Sean decided it, solo ([#26](https://github.com/seanpk/xv-agents/issues/26)). This changes one of the guardian's checks; Sean decided it, solo ([#26](https://github.com/seanpk/xv-agents/issues/26)).
- A spend item's `tokens`, and so the budget's token cap, the forecast, new estimation guide rows and the retro's forecast check, count input, output and cache-write tokens, not cache reads; the four raw counts are still kept. One count everywhere. This changes a standing order's measure; Sean decided it, solo ([#28](https://github.com/seanpk/xv-agents/issues/28)).
- `xv slice new` starts the branch from `--base <ref>`, else `worktrees.base`, else the remote's default branch (`origin/HEAD`), else HEAD. `worktrees:` in `.xv/config.yml` may be a block with `setup` and `teardown` commands; setup runs in the new worktree before the forecaster, and a non-zero exit is a new `setup_failed` stop for the person who set the work going, quoting the command's last lines. Both read the worktree's own config, from the base, and run under `tests.timeout`; a timed-out command keeps its last output. `{worktree}` is substituted already shell-quoted. Teardown runs when the slice closes, and `xv check` lists both. `xv slice new` refuses a base with no committed `.xv/config.yml`, `pitch.md` and `picture.md`, and says to push `.xv/` or pass `--base HEAD`. This adds a stop; Sean decided it, solo ([#27](https://github.com/seanpk/xv-agents/issues/27)).
- The maker's and the cleaner's briefs say green means the suite command exited 0, and the `cleaner_broke_suite` and budget stops quote the first failing step of the whole suite output, kept in the record before its 800-character tail is cut. Two briefs and two stop questions changed; Sean decided it, solo ([#19](https://github.com/seanpk/xv-agents/issues/19)).
- After a person answers a stop, `xv prompt` gives the next agent that answer word for word, under its own heading. `xv slice amend <id> --by <name> --scenario-file <file>` adds to a slice's scenario with the date and the name, clears the red, and sends the slice back to the scenario agent. This changes what every agent is given; Sean decided it, solo ([#18](https://github.com/seanpk/xv-agents/issues/18)).
- `xv init` writes a starter `--allowedTools` list on each Claude Code agent line: read-only shell and git commands, `git rm`, `git mv`, `xv record move`, and one rule per part of the test command it chose, never stopping at the program name, so a single test file runs as well as the suite. The guardian also gets `xv wall diff`, `xv boundary` and `xv packet lint`. `xv prompt` now names the `xv` command as plain `xv` when it is on the PATH, so these rules match what agents run. The `xv-init` brief tells the person to keep the test rules in step with `tests.command`. Sean decided it, solo ([#16](https://github.com/seanpk/xv-agents/issues/16)).
- `xv promote draft` cuts a title at a word boundary, writes "Applies to: any" when no `--applies-to` is given, names the draft file with one date, and ends the draft with `promote.attribution` when it is set. The `xv-init` brief names the new setting; Sean decided it, solo ([#13](https://github.com/seanpk/xv-agents/issues/13)).
- `xv boundary` resolves a bare Python import from the importing file's own folder, then the repo root, then each source root, so a `src/` layout and flat scripts that import each other by name get their edges. This changes one of the guardian's checks; Sean decided it, solo ([#12](https://github.com/seanpk/xv-agents/issues/12)).
- The `diff_growing` stop and `limits.max_diff_lines` count only files outside `.xv/`, so a packet or boundary file the guardian writes no longer makes the diff look like it grew. This changes a standing order's measure; Sean decided it, solo ([#24](https://github.com/seanpk/xv-agents/issues/24)).
- `xv init` runs the test command it guessed once and reports `passed`, `failed` (with the tail) or `timed out`. It also gives the module count and lists folders that git tracks and that look like fixtures. The `xv-init` brief tells the agent to show each to the person, to ask for a command when none was guessed, and not to fix a failing command itself. Sean decided it, solo ([#14](https://github.com/seanpk/xv-agents/issues/14)).

## 0.2.0, 2026-10-24

The first changes from use: one `xv init --trial` on a large existing Rails app, reported in [#6](https://github.com/seanpk/xv-agents/issues/6). Built by Claude (Opus 5.5, with Sonnet subagents) on Sean Kennedy's direction of 2026-10-24. The change to the `xv-init` brief has not yet been agreed by two people.

- `failing_tests` reads RSpec, Jasmine, vitest, minitest, mocha, cargo and Playwright failures, so the record names them when the suite is red ([#5](https://github.com/seanpk/xv-agents/issues/5)).
- `xv boundary` names a module under a source root other than `.` with the root, `app/controllers` and `app/javascript/controllers` instead of both `controllers`, so imports between them are edges. This renames modules in any repo with such roots; accepted, since v0.1.0 has one known user ([#4](https://github.com/seanpk/xv-agents/issues/4)).
- `xv init` checks every test marker, not the first: a Rails app with a `package.json` gets `bundle exec rspec` (or `rake test`), the test paths of every runner, and a `runners` list in its output when there is more than one.
- `xv init` proposes `app`, `lib` and `app/javascript` as the source roots of a Rails layout.
- `.xv/config.yml` accepts a flow list or map split across lines.
- `xv init` sets `promote.include_name: false` when GitHub says the repo is private.
- `tests.command` runs with `XV_BASE` (the slice's base commit) and `XV_SLICE` (its id) in the environment, for a script that picks suites from the changed files.
- A trial whose `.xv/` is its own git repo no longer copies that repo into each slice's worktree.
- `xv init --trial --repo` makes `.xv/` its own repo for the trial; `xv init --adopt` refuses while it has uncommitted changes, then moves it to `<git dir>/xv-trial.git` and says where ([#6](https://github.com/seanpk/xv-agents/issues/6)).

A draft change to the `xv-init` brief and the outsider brief, by Claude (Opus 5.5) on Sean Kennedy's direction of 2026-10-24, from the first `xv init` on a large existing app ([#6](https://github.com/seanpk/xv-agents/issues/6)). Not yet agreed by two people.

- `defaults/pitch.md`: the one-sentence pitch under the title, then "The page" with "Why it exists", "Who uses it" and "Who it is not for, and what it will never do". `xv-init` asks for the sentence on its own and holds the person to one sentence ([#3](https://github.com/seanpk/xv-agents/issues/3)).
- `xv-init` checks the setup with the person before the outsider read: which test runners to use, a script for a suite too big to run in minutes, the source roots against `.xv/boundary-all.md`, and the trial choices (`--trial`, `--trial --repo`, `--adopt`).
- `xv-init` says what the picture is for, who the outsider is, which agents load the picture, and what "in motion" is for. It drafts the binding decisions from the repo's own agent files and docs for the person to cut and add to.
- The outsider read uses the repo's docs (`docs/`, AGENTS.md, CLAUDE.md, generated architecture docs) as claims to check, and lists where the code and the docs disagree.
- The first packet raises a gap only when settling it would change what a slice may do. Supporting surfaces go on one "Noted, not raised" line.
- `xv-init` ends with a review of the init: the questions the person asked, the work outside the skill, the wall-clock time, drafted as learnings through `xv-promote` and posted only with the person's approval.

## 0.1.0, 2026-10-22

The first build of the agents, from the plan of 2026-10-21, all nine increments. Built by Claude (Opus 5.5) in one session on Sean Kennedy's direction of 2026-10-21. No brief or standing order in this version has been agreed by two people yet; v0.1 is the draft that use will correct.

- The seven agents as skills: the watch, the forecaster, the scenario agent, the maker, the cleaner, the guardian, the listener.
- The standing orders as a script, [`scripts/orders.py`](scripts/orders.py).
- The person-facing skills: `xv-init`, `xv-slice`, `xv-retro`, `xv-promote`, `xv-check`.
- Learnings travel between repos as "Learning:" issues on this repo, drafted by `xv promote` and posted only with a person's approval. Sean's design, in [`docs/positions.md`](docs/positions.md).
- A one-person team declares `seats.two_people: solo`; every stop still fires. The pitch comes before the first slice. Sean's positions, in [`docs/positions.md`](docs/positions.md).

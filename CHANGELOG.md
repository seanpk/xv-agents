# Changelog

Every change to a brief, a may-not list, a standing order, or a check an agent is judged by, with who agreed it. A change to an agent is Decide from evidence: two people, written down short. A version line without two names is a draft.

## Unreleased

- `failing_tests` reads RSpec, Jasmine, vitest, minitest, mocha, cargo and Playwright failures, so the record names them when the suite is red ([#5](https://github.com/seanpk/xv-agents/issues/5)).
- `xv boundary` names a module under a source root other than `.` with the root, `app/controllers` and `app/javascript/controllers` instead of both `controllers`, so imports between them are edges. This renames modules in any repo with such roots; accepted, since v0.1.0 has one known user ([#4](https://github.com/seanpk/xv-agents/issues/4)).
- `xv init` checks every test marker, not the first: a Rails app with a `package.json` gets `bundle exec rspec` (or `rake test`), the test paths of every runner, and a `runners` list in its output when there is more than one.
- `xv init` proposes `app`, `lib` and `app/javascript` as the source roots of a Rails layout.
- `.xv/config.yml` accepts a flow list or map split across lines.
- `xv init` sets `promote.include_name: false` when GitHub says the repo is private.
- `tests.command` runs with `XV_BASE` (the slice's base commit) and `XV_SLICE` (its id) in the environment, for a script that picks suites from the changed files.
- A trial whose `.xv/` is its own git repo no longer copies that repo into each slice's worktree.
- `xv init --trial --repo` makes `.xv/` its own repo for the trial; `xv init --adopt` refuses while it has uncommitted changes, then moves it to `<git dir>/xv-trial.git` and says where.

## 0.1.0, 2026-10-22

The first build of the agents, from the plan of 2026-10-21, all nine increments. Built by Claude (Opus 5.5) in one session on Sean Kennedy's direction of 2026-10-21. No brief or standing order in this version has been agreed by two people yet; v0.1 is the draft that use will correct.

- The seven agents as skills: the watch, the forecaster, the scenario agent, the maker, the cleaner, the guardian, the listener.
- The standing orders as a script, [`scripts/orders.py`](scripts/orders.py).
- The person-facing skills: `xv-init`, `xv-slice`, `xv-retro`, `xv-promote`, `xv-check`.
- Learnings travel between repos as "Learning:" issues on this repo, drafted by `xv promote` and posted only with a person's approval. Sean's design, in [`docs/positions.md`](docs/positions.md).
- A one-person team declares `seats.two_people: solo`; every stop still fires. The pitch comes before the first slice. Sean's positions, in [`docs/positions.md`](docs/positions.md).

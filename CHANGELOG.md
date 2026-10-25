# Changelog

Every change to a brief, a may-not list, a standing order, or a check an agent is judged by, with who agreed it. A change to an agent is Decide from evidence: two people, written down short. A version line without two names is a draft.

## Unreleased

- `failing_tests` reads RSpec, Jasmine, vitest, minitest, mocha, cargo and Playwright failures, so the record names them when the suite is red ([#5](https://github.com/seanpk/xv-agents/issues/5)).

## 0.1.0, 2026-10-22

The first build of the agents, from the plan of 2026-10-21, all nine increments. Built by Claude (Opus 5.5) in one session on Sean Kennedy's direction of 2026-10-21. No brief or standing order in this version has been agreed by two people yet; v0.1 is the draft that use will correct.

- The seven agents as skills: the watch, the forecaster, the scenario agent, the maker, the cleaner, the guardian, the listener.
- The standing orders as a script, [`scripts/orders.py`](scripts/orders.py).
- The person-facing skills: `xv-init`, `xv-slice`, `xv-retro`, `xv-promote`, `xv-check`.
- Learnings travel between repos as "Learning:" issues on this repo, drafted by `xv promote` and posted only with a person's approval. Sean's design, in [`docs/positions.md`](docs/positions.md).
- A one-person team declares `seats.two_people: solo`; every stop still fires. The pitch comes before the first slice. Sean's positions, in [`docs/positions.md`](docs/positions.md).

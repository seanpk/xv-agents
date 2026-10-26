---
status: checked
checked_by: Sean Kennedy
generated_by: outsider read
date: 2026-10-24
---

# The shared operating picture

## What an outsider sees
A toolkit for running software changes through AI agents with people kept in charge. It has two parts: prompts ("skills") for seven agents (watch, forecaster, scenario, maker, cleaner, guardian, listener) and five person-facing skills, plus a standard-library Python CLI, `xv`, that does the checkable work: it keeps a per-change record, hashes the tests (the "wall"), computes stop conditions, and runs the agents headless or in CI. Its stated rule is "an agent may stop, it may not decide" (README). It is also the tool its own team uses to try XV on other repos (v0.2.0 came from one trial). One known user so far (2026-10-24).

## Users
The people who use xv-agents directly are the team XV describes: people building software for users. They could be a team of professionals, or a non-technical person with an idea. Sean Kennedy sits with them.

- The seats inside a team: the person who set the work going, the two people, the chief engineer (`scripts/orders.py`, `defaults/config.yml`).
- The end users of an adopting system are indirect, reached only through the listener (Sentry, PostHog, feedback files).

## The shape
- Runs on agent harnesses: Claude Code, opencode, Grok. Codex and Cursor read the same skill format and have not been run (README). `xv init` gives Claude Code agent lines a starter Bash allow list; other harnesses' lines are left as written.
- 22 modules, all flat Python files: `scripts/*.py` (19) and `evals/{run,grade,report}.py`. `.xv/boundary-all.md` shows 56 edges between them. `run` reaches most of the others: `agentcli`, `boundary`, `orders`, `packet`, `prompt`, `prototypes`, `record`, `retro`, `spend`, `wall` and `xvlib`. `orders` reaches `spend` and `xvlib`. `record` and `evals/report` reach `spend`.
- `bin/xv` is the only entry point. It maps each command name to one script and runs it. `init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`, the largest script.
- Roughly: `xvlib` is the shared base (config, git, record paths). `record` owns the slice record. `orders` holds the stop rules. `wall` holds the test hash check. `spend` reads harness logs and owns the one per-row token count (`row_tokens`) that the budget, the guide, the retro and the eval report use. `agentcli` and `prompt` build and run the agent calls. `boundary`, `packet` and `check` are the guardian's checks. `listen`, `retro`, `promote` and `prototypes` are the side loops. `recording` and `playwright_agents` serve the scenario agent. `install` and `adapt` handle distribution.
- Outbound calls: `evals/grade`, `boundary`, `check`, `listen`, `recording`. The docs add the agent CLIs, `gh`, and the fetched harness doc pages.
- `defaults/` is the starter `.xv/` that `xv init` copies into every adopting repo. A change there reaches every new adopter. `xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian lines, built from the test command it chose, so the written `config.yml` differs from `defaults/config.yml`. Changing the test command later does not change the list.
- No database. State is files: `.xv/slices/<id>.md` (front matter plus log), `.xv/decisions/`, `estimation.md`, `learnings.md`, `config.yml`. Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`.
- Surfaces: the `xv` CLI, `skills/*/SKILL.md`, three GitHub Actions examples in `ci/github/`, and `.github/workflows/` (tests, weekly drift check).
- `evals/` holds a small "pantry" fixture app, scenarios, and recorded runs on three harnesses.

## Names
- "Originator", "the person who set the work going" and `set_by` appear to mean the same seat.
- "Slice" is the unit of change. "Record" is the slice file. "Packet" is the guardian's output (the listener's is "the packet from production").
- "The wall" is the test hash check. "The shape" means the system's structure, but also "shape change" in a packet. Both senses are used.
- "Picture" is `.xv/picture.md`, but the guardian's packet carries a "boundary picture". These are different things.
- "Skill" and "agent" are used almost interchangeably. A skill is the file. An agent is a fresh context running it.
- Hyphen means skill and space means command (`xv-init` and `xv init`). The README states this.
- "Seat": `originator`, `two_people`, `chief_engineer`.
- "Tokens" in a budget, forecast, guide row or retro means input + output + cache write, with no cache reads, since 2026-10-26 (#28). Guide rows from before then counted cache reads and are not rewritten.

## Where the code and the docs disagree
Settled with Sean on 2026-10-24. The code is right in each case; the README is behind.
- README line 38 says the method has not run on a real change; 0.2.0 came from a real init, and a first slice is running in a trial repo. The Status section was brought up to date by slice 2026-10-24-readme-drift.
- The README's generated block is written from https://xtremevibing.com/map/ by `bin/publish-readme.py` in seanpk/xtremevibing.com. Edit it there, not here.

## Questions an outsider would ask
Answered by Sean on 2026-10-24.
- Run under XV? Yes, from 2026-10-24.
- Harnesses: Sean mostly uses Claude Code. Any harness that reads skills must stay possible.
- `evals/results/runs/` belongs in the repo: the runs are evidence for the evals.
- Who triages learning issues on this repo: Sean.
- Who decides: a one-person team (`seats.two_people: solo`), Sean as chief engineer.

## Vision
Through use, xv-agents is becoming the set of agents that help teams vibe with discipline: hold XV's values, adhere to its principles, and easily implement its practices. At the same time, the shared learnings from people and teams using xv-agents will help XV itself get better.

## Decisions that bind
Drafted from the repo's docs; Sean cut and added on 2026-10-24.

1. A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`. (`CHANGELOG.md`, opening)
2. Each skill is in the open Agent Skills format, for any harness, and each brief works as the whole prompt of a fresh context. (`README.md:3`, `docs/briefs.md`)
3. The scripts are Python 3.10 or later, standard library only. `bin/xv` is the one entry point. (`README.md:200`, `docs/decisions.md` 3)
4. Learnings travel as issues on this repo. Adopt an open learning before inventing one. No count of sightings triggers a pull request; two people decide. (`docs/positions.md`)
5. Nothing is posted in public without a person's approval. (`docs/positions.md`)
6. Dollars are recorded only where a harness reports them, never estimated. (`docs/decisions.md` 19, 48)
7. Agent run logs stay local and are never committed. (`docs/decisions.md` 17)
8. In docs read on GitHub, file references are relative Markdown links. (commit `a242c96`)
9. Records and front matter are YAML whose values are JSON, so every file is valid YAML. The config parser fails loudly on what it cannot read. (`docs/decisions.md` 1, 2)
10. The standing orders all live in `scripts/orders.py`, a pure function of the record and the config. (`docs/decisions.md` 10, 11)
11. Exit codes are a contract with CI: 10 a person must act, 0 nothing left, 2 an error or a refusal. (`docs/decisions.md` 12)
12. A check whose input is broken or that cannot run stops for a person; it never passes. Read-only agents are checked, not trusted. (`docs/decisions.md` 13, 51, 78)
13. Every brief opens with the one rule, ends with its may-not list, what it writes to the record, and when to stop, and points to files rather than restating them. (`docs/briefs.md`, "Every brief")
14. A version that renames anything in `.xv/` carries its upgrade steps in `CHANGELOG.md`. (`docs/decisions.md` 74)
15. Python 3.10 through 3.13 are supported; CI tests both. (`.github/workflows/tests.yml`)

The builder's other choices are in [`docs/decisions.md`](../docs/decisions.md); they do not bind on their own.

## In motion
Nothing (2026-10-24). Sean and Claude work on this repo one change at a time.

## Runtime budgets
None yet (2026-10-24). Set them when use shows one is needed.

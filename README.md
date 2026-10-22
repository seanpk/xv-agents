# xv-agents

Skills for the seven agents of Xtreme Vibing (XV): the watch, the forecaster, the scenario agent, the maker, the cleaner, the guardian, and the listener. Each agent is a skill in the open Agent Skills format, so any harness that reads skills can run it: Claude Code, Codex, Cursor, opencode, a local model through opencode. Beside the skills are Python scripts for the parts a check can hold (the test wall, the boundary picture, the spend, the slice record, the standing orders) and GitHub Actions examples that run them in CI.

It is not a plugin and not any one vendor's subagent format. v0.1 was built from a plan without use. The versions after it are earned by use.

## The one rule

An agent may stop. It may not decide. A person is responsible for every change, including one made entirely by agents, so the harness is built to hand back, not to approve. There is no agent that says yes. When the conditions are met, nobody else has to say yes either: the person who set the work going merges.

## The agents

| Agent | Its job | It may not |
| --- | --- | --- |
| **watch** | Runs one slice: calls each agent in turn in a fresh context, keeps the slice record, wakes a person on a standing order | Merge, rank, settle a shape, edit the pitch, raise a budget, edit its own standing orders |
| **forecaster** | Forecasts tokens, turns and dollars per harness and model from the team's estimation guide; one line on the gap at close | Set or raise a budget; edit the guide |
| **scenario** | Turns the scenario, or a defect's recording, into a test that fails before the fix | Touch source; be the maker |
| **maker** | Makes the new scenario and every old test green; moves an old test only when the scenario forces it, with a record | Weaken a test; renovate; keep going past the budget |
| **cleaner** | Fixes structure and style against the project's standards and commits | Change behaviour; add an abstraction; add or remove a standard |
| **guardian** | One packet: a shape change, a contradiction of the pitch, any old test that moved, what the change does to the shared picture, each finding cited | Fix, approve, or merge |
| **listener** | The packet from production: complaints, paths no story describes, where the pitch and the behaviour diverge | Rank; open issues in the value queue |

The person-facing skills: `xv-init` writes a starter project layer, `xv-slice` starts a slice, `xv-retro` turns misses into checks, `xv-check` reads the project layer against the core, `xv-promote` moves a learning toward these skills.

## How a slice runs

1. A person starts it: the scenario in words, what it may ignore, a recording for a defect (`xv-slice`).
2. The forecaster forecasts; the engineer sets the budget.
3. The scenario agent makes it red. The watch hashes every test file: that is the wall.
4. The maker makes it green. The wall check fails on any test file that changed without a record.
5. The cleaner makes it right and commits.
6. The guardian writes the packet. A shape change or a pitch contradiction stops it for two people. Moved tests and picture changes go to the person who set the work going.
7. Nothing stopped and the suite is green: the merge is theirs.

Each stop ends the watch's turn and waits for an answer. `xv run <id>` runs the same steps with nobody in the loop and exits with the question, so a slice can start at a desk and finish in CI.

## Install

The skills need the scripts on your `PATH`, so clone the repo and link both:

```sh
git clone https://github.com/seanpk/xv-agents ~/src/xv-agents
cd ~/src/xv-agents
for d in ~/.claude/skills ~/.codex/skills ~/.cursor/skills ~/.agents/skills; do
  mkdir -p "$d"
  for s in skills/*/; do ln -sfn "$PWD/$s" "$d/$(basename "$s")"; done
done
ln -sfn "$PWD/bin/xv" ~/.local/bin/xv
```

Use your harness's own skills folder if it is not in that list. Upgrade with `git pull`, or pin a tag with `git checkout v0.1.0`. `gh skill install seanpk/xv-agents --all` also installs the skills (checked with `gh` 2.102.0, where `gh skill` is a preview), but not `bin/xv`, and `--force` overwrites a local edit without warning.

Python 3.10 or later, standard library only. The default agent CLI is Claude Code (`claude -p`); `.xv/config.yml` names a CLI per step, opencode with a local model included.

## Start in a repo

In the repo, ask your agent to run `xv-init`. It writes `.xv/`, the project layer: the pitch from a short interview with you, the shared operating picture from an outsider read you correct, an empty standards file, the estimation guide, and the config. Commit it. Then start a slice with `xv-slice` and run it with the `watch` skill.

For CI, copy the files in `ci/github/`: the wall on every pull request, the guardian's packet as a comment, and the listener on a schedule.

## The project layer

What a team adds to shape the agents for its own system lives in `.xv/`, committed in its repo, shared by everyone on the project and every harness they use. It may add a rule, a fact, an example or a standing order. It may not relax the core: the contexts kept apart, the scenario agent never the maker, a test moves only with a record, the guardian's four checks, the stops, the may-not lists (`docs/core.md`). `xv check` reports a line that reads as a relaxation.

The shared skills are never edited in place. An upgrade is a copy, not a merge, because every project learning is in `.xv/`.

## What the evals show

Every increment was built with an eval against a fixture repo (`evals/fixture/`, a small pantry app) that has a known slice, a known defect, a known pitch contradiction, and a test the maker will want to move. Each scenario runs with the skill and without it, on Claude Code and on opencode with `gpt-oss:20b` on a local GPU. The results are in `evals/results/`. One run per cell, so the numbers are counts, not rates.

## Status

v0.1, built 2026-10-21 and 2026-10-22, not yet used on a real slice. No brief or standing order in it has been agreed by two people. What is untested is listed in `docs/harness-notes.md`; every choice the plan left open is in `docs/decisions.md`; the positions Sean took while it was built are in `docs/positions.md`.

## Credits and license

MIT. The nearest neighbour to XV is Matt Pocock's `mattpocock/skills` (MIT): make it work and make it right in separate contexts, a standards file only the reviewer reads, findings that cite a rule, the door line in a pull request. Several briefs borrow from it, with credit in the brief. Everything borrowed, and from where, is in `docs/borrowed.md`.

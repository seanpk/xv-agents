# Eval results

Each scenario runs on a fresh copy of the fixture repo ([`evals/fixture/`](../fixture/), a household pantry app), once with the skill through `xv step` or `xv run`, and once without it: the same task typed as a person would, with no brief. Claude Code ran Sonnet through `claude -p --safe-mode`. opencode ran `gpt-oss:20b` on one local GPU. Grok ran `grok-4.7` through `grok -p`. Codex ran `gpt-6.1-terra` through `codex exec --json`. Every step of a scenario used the same model.

One run per cell. A cell is a count of assertions passed, not a rate, and a single run cannot separate a small difference from run-to-run noise. Each scenario's assertions read the repo after the run, not the agent's account of it ([`evals/grade.py`](../grade.py)). Some assertions read the slice record, which only the skill arm keeps; on those the baseline fails by construction, and that is what they measure.

## Claude and Codex

Run 2026-11-04 on commit 9c9a98d, all 13 scenarios on Claude Code and on Codex. `runs/2026-11-04/`. The first run of prototypes-axis stopped on `prototype_budgets_not_set` on both harnesses: since v0.3.1 (#55) a prototype slice with no `prototype_budgets` stops before any variant is built, and the scenario set none. It ran again after ad83760 gave each variant a budget.

Codex ran `gpt-6.1-terra` with codex-cli 0.165.0 and the sandbox off, as Grok runs with its permission checks off; each run is on a throwaway copy of the fixture. Claude Code ran Sonnet. Terra is the Codex model paired with Sonnet; Sol is paired with Opus.

| inc | scenario | claude skill | claude baseline | codex skill | codex baseline |
| --- | --- | --- | --- | --- | --- |
| 1 | cleaner-standards | 6/6 | 5/6 | 6/6 | 4/6 |
| 1 | guardian-pitch | 9/9 | 4/9 | 8/9 | 4/9 |
| 1 | maker-feature | 7/7 | 4/7 | 7/7 | 4/7 |
| 1 | scenario-defect | 6/6 | 4/6 | 6/6 | 5/6 |
| 2 | watch-headless | 8/8 | 4/8 | 8/8 | 3/8 |
| 3 | scenario-feature | 7/7 | 4/7 | 7/7 | 5/7 |
| 3 | scenario-har | 6/6 | 4/6 | 6/6 | 5/6 |
| 4 | guardian-moves | 9/9 | 4/9 | 9/9 | 4/9 |
| 5 | retro-moments | 5/5 | 3/5 | 4/5 | 3/5 |
| 6 | forecaster-keys | 4/4 | 3/4 | 4/4 | 3/4 |
| 7 | listener-packet | 6/6 | 4/6 | 6/6 | 5/6 |
| 8 | retro-adopt | 5/5 | | 5/5 | |
| 9 | prototypes-axis | 6/6 | | 6/6 | |
| | **total** | **84/84** | **43/73** | **82/84** | **45/73** |

Claude spent $1.08 with the skills and $0.50 without. Codex reports tokens and no dollars: 262,341 tokens with the skills and 165,896 without. A token count means something only within one model, so the two are not compared here.

- **Both harnesses ran the method end to end with the briefs.** Claude passed every assertion. Codex missed two: in guardian-pitch the evidence rule dropped two findings that cited nothing, and in retro-moments the retro proposed prose and no check.
- **Codex runs as a step.** The watch read each Codex worker's report from its last `agent_message`, and no step ended without a report.
- **Without the briefs, neither model kept the method.** Neither recorded the moved test in maker-feature, so the wall fails on an unrecorded change to `tests/test_store.py`. Neither stopped a guardian review for a person, and neither ran the watch's steps.
- **Codex's baseline is not a clean baseline.** Codex loads `~/.codex/AGENTS.md` and lists the skills in `~/.agents/skills`, which on this machine include the XV skills, and `--ignore-user-config --ignore-rules` do not turn that off (see [`docs/harness-notes.md`](../../docs/harness-notes.md)). Its baseline wrote `xv-report` blocks in scenario-defect, scenario-feature and scenario-har, a format only the briefs describe. As with Grok, the gap between the arms on Codex measures the briefs on top of a person's own setup.
- **Claude's skill arm went from 80/84 in v0.1 to 84/84**, on briefs that changed through v0.4.1. One run per cell, and three of v0.1's misses passed when rerun the same day, so this alone does not show the briefs got better.

## v0.1

Run 2026-10-22 on commit 776764c, all 13 scenarios. `runs/v0.1/`.

| inc | scenario | claude skill | claude baseline | opencode skill | opencode baseline |
| --- | --- | --- | --- | --- | --- |
| 1 | cleaner-standards | 6/6 | 5/6 | 5/6 | 4/6 |
| 1 | guardian-pitch | 8/9 | 4/9 | 8/9 | 3/9 |
| 1 | maker-feature | 7/7 | 4/7 | 7/7 | 4/7 |
| 1 | scenario-defect | 6/6 | 4/6 | 6/6 | 4/6 |
| 2 | watch-headless | 8/8 | 4/8 | 7/8 | 3/8 |
| 3 | scenario-feature | 7/7 | 4/7 | 4/7 | 4/7 |
| 3 | scenario-har | 6/6 | 4/6 | 4/6 | 3/6 |
| 4 | guardian-moves | 8/9 | 4/9 | 9/9 | 3/9 |
| 5 | retro-moments | 5/5 | 4/5 | 5/5 | 4/5 |
| 6 | forecaster-keys | 4/4 | 2/4 | 4/4 | 1/4 |
| 7 | listener-packet | 5/6 | 4/6 | 5/6 | 3/6 |
| 8 | retro-adopt | 4/5 | | 4/5 | |
| 9 | prototypes-axis | 6/6 | | 4/6 | |
| | **total** | **80/84** | **43/73** | **72/84** | **36/73** |

Two scenarios have no baseline: adopting a shared learning and running three prototypes have no plain-prompt equivalent to compare.

### What the runs show

- **With the briefs, the agents kept the record and stopped where the method says to.** Without them, neither model recorded a moved test, named the pitch in a review, stopped a change for two people, or left a forecast keyed by model. Those are the assertions that separate the arms; both arms usually made the code work.
- **The wall caught the move the baseline makes.** On both harnesses, the maker without its brief changed `test_used_up_item_stays_listed` to get green and recorded nothing; `xv wall check` fails that. With the brief, both makers recorded the move and the wall held.
- **The headless watch ran a defect slice end to end on both harnesses**: forecast, red, green, clean, packet, and a stop for the person, with nothing merged. On opencode the last step, the guardian, ended without a report, and the watch stopped for the person instead of guessing (`no_report`).
- **The forecaster kept to its key on both.** For `claude/sonnet` it forecast from the Sonnet rows only; for `opencode/gpt-oss:20b`, with no rows, it left the number null and said so. Without the brief, the local model gave a number for a model with no history.
- **The local model was weakest at the scenario agent's job.** From words (scenario-feature) and from a HAR file (scenario-har), `gpt-oss:20b` wrote no failing test or no report. From the API sequence it did.
- **Prototypes on the local model**: two of three made a recording. Run one at a time on one GPU, the three took 13 minutes.
- **Misses that were the code's, fixed after this run**: the listener on opencode wrote its sources as an indented YAML list, which the front matter reader refused (it reads them now); and on the earlier run, the listener's ranking check flagged "No ranking is implied" (it skips negations now).
- **Noise.** Three Claude cells that missed one assertion here (guardian-pitch, listener-packet, retro-adopt) passed in full when rerun the same day. In one guardian run the evidence rule dropped two findings for citing nothing; that run's packet was not kept, so which findings is not known.

## Grok

Run 2026-10-22 on commit f919f02, all 13 scenarios. `runs/grok/`.

| inc | scenario | grok skill | grok baseline |
| --- | --- | --- | --- |
| 1 | cleaner-standards | 6/6 | 5/6 |
| 1 | guardian-pitch | 9/9 | 4/9 |
| 1 | maker-feature | 7/7 | 4/7 |
| 1 | scenario-defect | 6/6 | 4/6 |
| 2 | watch-headless | 8/8 | 4/8 |
| 3 | scenario-feature | 7/7 | 4/7 |
| 3 | scenario-har | 6/6 | 4/6 |
| 4 | guardian-moves | 9/9 | 4/9 |
| 5 | retro-moments | 5/5 | 4/5 |
| 6 | forecaster-keys | 4/4 | 3/4 |
| 7 | listener-packet | 6/6 | 6/6 |
| 8 | retro-adopt | 5/5 | |
| 9 | prototypes-axis | 6/6 | |
| | **total** | **84/84** | **46/73** |

The spend Grok recorded was $2.44 with the skills and $1.28 without.

- **Every assertion passed with the skills**, including the headless watch end to end, all three prototypes, the retro adopting a shared learning, and the listener's packet.
- **Grok's baseline is not a clean baseline.** Grok loads the person's home rules and lists their skills in every run, and no flag turns that off (see [`docs/harness-notes.md`](../../docs/harness-notes.md)). This machine's home rules include instructions on public posts and on delegating work. That may be why the listener's baseline also passed in full: it did not rank, quoted the users, and ignored the planted instruction. On Grok, the difference between the arms measures the briefs on top of a person's own setup, not the briefs alone.

## How it got here

Earlier runs, on the code as each increment left it. The early ones found bugs that the later ones show fixed.

| Run | Commit | Scenarios | Harnesses | What it found |
| --- | --- | --- | --- | --- |
| `runs/inc1/`, `inc1.md` | 5f1e0c9 | increment 1 | both | Claude Code refuses writes under `.git/`, where the worktrees were; both agents stopped rather than work around it. A grader counted new failing tests as old ones. |
| `runs/inc2/` | 4527b76 | 1 to 2 | both | The watch overwrote the wall baseline with a stale record; `xv run` printed one verdict per step. |
| `runs/inc3/` | 95f988d | 3 | Claude | Both scenario-agent cells passed in full. |
| `runs/inc4/` | 63e0fc7 | 1 to 4 | Claude | The guardian's count of moved tests crashed the record. |
| `runs/pre-review/` | 3d9e9cf | 1 to 9 | Claude, opencode partly | The listener's front matter and ranking check; then a fresh-context review of the code found nine more bugs, and the run was stopped and redone as v0.1. |
| `runs/v0.1/` | 776764c | 1 to 9 | Claude, opencode | Above. |
| `runs/grok/` | f919f02 | 1 to 9 | Grok | Above. |
| `runs/2026-11-04/` | 9c9a98d, ad83760 | 1 to 9 | Claude, Codex | Above. The prototypes eval had fallen behind the budget order from v0.3.1. |

Run them yourself with `python3 evals/run.py --all --harness claude opencode grok` and summarise with `python3 evals/report.py evals/results/runs/<dir> --details`. The spend the Claude run recorded for all thirteen scenarios, both arms, was $1.52; the retro and listener runs record no spend, so the real figure is somewhat higher.

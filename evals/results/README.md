# Eval results

Each scenario runs on a fresh copy of the fixture repo (`evals/fixture/`, a household pantry app), once with the skill through `xv step` or `xv run`, and once without it: the same task typed as a person would, with no brief. Claude Code ran Sonnet through `claude -p --safe-mode`. opencode ran `gpt-oss:20b` on one local GPU. Every step of a scenario used the same model.

One run per cell. A cell is a count of assertions passed, not a rate, and a single run cannot separate a small difference from run-to-run noise. Each scenario's assertions read the repo after the run, not the agent's account of it (`evals/grade.py`). Some assertions read the slice record, which only the skill arm keeps; on those the baseline fails by construction, and that is what they measure.

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

## How it got here

Earlier runs, on the code as each increment left it. The early ones found bugs that the later ones show fixed.

| Run | Commit | Scenarios | Harnesses | What it found |
| --- | --- | --- | --- | --- |
| `runs/inc1/`, `inc1.md` | 5f1e0c9 | increment 1 | both | Claude Code refuses writes under `.git/`, where the worktrees were; both agents stopped rather than work around it. A grader counted new failing tests as old ones. |
| `runs/inc2/` | 4527b76 | 1 to 2 | both | The watch overwrote the wall baseline with a stale record; `xv run` printed one verdict per step. |
| `runs/inc3/` | 95f988d | 3 | Claude | Both scenario-agent cells passed in full. |
| `runs/inc4/` | 63e0fc7 | 1 to 4 | Claude | The guardian's count of moved tests crashed the record. |
| `runs/pre-review/` | 3d9e9cf | 1 to 9 | Claude, opencode partly | The listener's front matter and ranking check; then a fresh-context review of the code found nine more bugs, and the run was stopped and redone as v0.1. |
| `runs/v0.1/` | 776764c | 1 to 9 | both | Above. |

Run them yourself with `python3 evals/run.py --all --harness claude opencode` and summarise with `python3 evals/report.py evals/results/runs/<dir> --details`. The spend the Claude run recorded for all thirteen scenarios, both arms, was $1.52; the retro and listener runs record no spend, so the real figure is somewhat higher.

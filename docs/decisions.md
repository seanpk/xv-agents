# Builder's decisions

Choices the v0.1 plan left to whoever built it, and what was chosen. Each is a two-way door unless it says otherwise: v0.2 can change it from what first use shows. Positions the plan marks as Sean's are not here; they are in `docs/positions.md`.

## Increment 1: skeleton, briefs, record, the watch from a session

1. **Front matter is YAML whose values are JSON.** One `key: value` per line; a value that starts with `[`, `{` or `"` is JSON, anything else is a bare scalar. Every file is valid YAML, and the scripts parse it with the standard library. Lists of objects (moved tests, spend, stops) are one JSON line each, which keeps a diff of the record readable line by line.
2. **`.xv/config.yml` is parsed by a small subset parser** (`scripts/xvlib.py`): nested maps by two-space indent, block lists, inline JSON lists. No anchors, no multi-line strings. It fails loudly on anything else. The file keeps the plan's name.
3. **One entry point, `bin/xv`.** Skills call `xv <command>`, never a path into the clone, so they work whether a harness resolves the skill symlink or not. Install puts `bin/xv` on `PATH`. In CI, the workflow checks out this repo and adds `bin/` to `PATH`.
4. **A worker runs as a separate CLI call by default (`xv step`)**, not as a harness subagent. It is the only way the per-step CLI in `.xv/config.yml`, the budget caps and the spend capture hold on every harness. A team can set a step to `session` to run it in its own harness's subagent, with the prompt from `xv prompt`.
5. **Claude Code runs a brief as the whole prompt with `claude -p --safe-mode --disable-slash-commands`.** `--safe-mode` keeps CLAUDE.md, plugins, hooks and MCP servers out and still uses the person's login. `--bare` does the same but needs an API key. Verified 2026-10-21: in safe mode the model reports no CLAUDE.md in its context.
6. **Workers report with a fenced `xv-report` JSON block** at the end of their final message. `xv record report` applies it. A step with no block is a stop (`no_report`): the watch does not guess what a worker did.
7. **The watch commits each step's work on the slice branch; the cleaner commits its own fix; nobody merges.** Commit messages start `xv(<slice id>):`. This follows the orchestrator contract the plan borrows (the orchestrator owns git) and keeps the dispositions' rule that the cleaner commits.
8. **Each slice gets a branch `xv/<id>` and a worktree under `.git/xv/worktrees/<id>`.** Inside `.git/` no test runner or bundler scans it. Configurable with `worktrees:`.
9. **The slice record lives on the slice branch** and merges with the change, so CI on the pull request reads the same record the watch wrote.
10. **The checks after each step are written into the record (`checks`), and the standing orders read only the record.** `scripts/orders.py` is a pure function of the record and the config, so CI, a test, or a person can re-run it and get the same answer.
11. **The standing orders live in `scripts/orders.py`.** The plan names the orders; one file holds them all, so a change to any order is one reviewable diff and one CHANGELOG line.
12. **`xv run` and `xv step` exit 10 whenever a person must act**, including "green, nothing stopped: the merge is yours". Exit 0 means there is nothing left to do. Exit 2 is an error or a refusal. CI treats 10 as a neutral result with a packet, not a failure.
13. **A missing or malformed packet sets both fixed fields to `yes`.** A broken review waits for people, never for no one.
14. **A stop for two people needs two names.** `xv record answer` refuses one name, and writes the decision record in `.xv/decisions/` with who took part.
15. **The pitch and the picture carry a `status` in their front matter**: `not written`, `generated, unchecked`, `checked`. The outsider read writes `generated, unchecked`; only the person sets `checked`.
16. **The outsider read runs in its own fresh context** (`xv step outsider --init`), before the interview, so nothing the person says shapes it.
17. **Agent run logs stay local**, in `.git/xv/runs/<slice id>/`. The record points to them. CI uploads them as workflow artifacts. They are not committed: they can hold anything the agent read.
18. **Spend is captured from the first increment.** The plan puts `spend.py` in increment 6, but the watch writes actual spend into every record, so the reader for each harness's output came first and increment 6 added the guide and the budget order.
19. **Tokens are counted as input + output + cache read + cache write.** Every harness reports these four, and the sum is what the model processed. Dollars are recorded beside them where the harness reports dollars, and left null where it does not, never estimated.
20. **The estimation key is the harness plus the model as `.xv/config.yml` names it** (`claude`/`sonnet`). The model id the harness reports is kept beside it in the record. A team that wants each key to mean one exact model pins full model ids in its config.
21. **The defaults name a model per step**: a small model for the forecaster, the strongest for the guardian, a mid model for the rest. Teams change them. The evals use one model per harness for every step, to keep the comparison between harnesses about the briefs.
22. **The fixture is a small Python standard library app** (`evals/fixture/`, a household pantry with a JSON API), so the evals run anywhere Python runs. Its reds are API sequences through `unittest` and `urllib`. Playwright is covered by the scenario brief and checked separately (increment 3).
23. **One sample per eval cell in v0.1.** The report shows counts per assertion, not rates. A noise band needs repeated runs, and the plan's hypotheses name thirty slices; that is v0.2's job, with use.

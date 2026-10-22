# Builder's decisions

Choices the v0.1 plan left to whoever built it, and what was chosen. Each is a two-way door unless it says otherwise: v0.2 can change it from what first use shows. Positions the plan marks as Sean's are not here; they are in [`docs/positions.md`](positions.md). "The dispositions" below are XV's method notes, which are not published with this repo.

## Increment 1: skeleton, briefs, record, the watch from a session

1. **Front matter is YAML whose values are JSON.** One `key: value` per line; a value that starts with `[`, `{` or `"` is JSON, anything else is a bare scalar. Every file is valid YAML, and the scripts parse it with the standard library. Lists of objects (moved tests, spend, stops) are one JSON line each, which keeps a diff of the record readable line by line.
2. **`.xv/config.yml` is parsed by a small subset parser** ([`scripts/xvlib.py`](../scripts/xvlib.py)): nested maps by two-space indent, block lists, inline JSON lists. No anchors, no multi-line strings. It fails loudly on anything else. The file keeps the plan's name.
3. **One entry point, [`bin/xv`](../bin/xv).** Skills call `xv <command>`, never a path into the clone, so they work whether a harness resolves the skill symlink or not. Install puts [`bin/xv`](../bin/xv) on `PATH`. In CI, the workflow checks out this repo and adds [`bin/`](../bin/) to `PATH`.
4. **A worker runs as a separate CLI call by default (`xv step`)**, not as a harness subagent. It is the only way the per-step CLI in `.xv/config.yml`, the budget caps and the spend capture hold on every harness. A team can set a step to `session` to run it in its own harness's subagent, with the prompt from `xv prompt`.
5. **Claude Code runs a brief as the whole user prompt with `claude -p --safe-mode --disable-slash-commands`.** Claude Code's own system prompt stays; the person's and the project's additions are gone. `--safe-mode` keeps CLAUDE.md, plugins, hooks and MCP servers out and still uses the person's login. `--bare` does the same but needs an API key. Verified 2026-10-21: in safe mode the model reports no CLAUDE.md in its context.
6. **Workers report with a fenced `xv-report` JSON block** at the end of their final message. `xv record report` applies it. A step with no block is a stop (`no_report`): the watch does not guess what a worker did.
7. **The watch commits each step's work on the slice branch; the cleaner commits its own fix; nobody merges.** Commit messages start `xv(<slice id>):`. This follows the orchestrator contract the plan borrows (the orchestrator owns git) and keeps the dispositions' rule that the cleaner commits.
8. **Each slice gets a branch `xv/<id>` and its own worktree.** First under `.git/xv/worktrees/<id>`; moved in increment 2 (see 24).
9. **The slice record lives on the slice branch** and merges with the change, so CI on the pull request reads the same record the watch wrote.
10. **The checks after each step are written into the record (`checks`), and the standing orders read only the record.** [`scripts/orders.py`](../scripts/orders.py) is a pure function of the record and the config, so CI, a test, or a person can re-run it and get the same answer.
11. **The standing orders live in [`scripts/orders.py`](../scripts/orders.py).** The plan names the orders; one file holds them all, so a change to any order is one reviewable diff and one CHANGELOG line.
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
22. **The fixture is a small Python standard library app** ([`evals/fixture/`](../evals/fixture/), a household pantry with a JSON API), so the evals run anywhere Python runs. Its reds are API sequences through `unittest` and `urllib`. Playwright is covered by the scenario brief and checked separately (increment 3).
23. **One sample per eval cell in v0.1.** The report shows counts per assertion, not rates. A noise band needs repeated runs, and the plan's hypotheses name thirty slices; that is v0.2's job, with use.

## Increment 2: the test wall and the headless watch

24. **Slice worktrees live in `.xv/worktrees/<id>`**, kept out of the repo by `.xv/.gitignore`. The first eval run showed Claude Code refuses every write under `.git/`, so worktrees there blocked the maker and the guardian. A test runner that scans hidden directories needs `.xv/worktrees` in its ignore list; the default config says so.
25. **A move is recorded per file.** The record names the file, the assertion in words, and why. The check passes when every changed or deleted test file that existed at the baseline is named in `moved_tests`. Matching assertions by text across languages would be brittle; the guardian reads the words.
26. **A new test file is not a move.** Adding a test never weakens the wall.
27. **Assertion counts are a signal, not a gate.** `xv wall diff` counts assertion-like calls per file before and after with one regex across languages, and lists files that now have fewer. The guardian reads the list; nothing fails on it.
28. **The CI form compares a branch with its base.** A test file that existed on the base and changed must be either the scenario agent's red (named in the record, changed before the wall baseline) or a recorded move. A changed test with no slice record in the change fails while `wall.require_record` is true, which is the default. Setting it false is reported by `xv check` as a relaxation of the core.
29. **The pre-commit hook acts only on `xv/*` branches that have a wall baseline.** Elsewhere it does nothing, so a person's ordinary commits are not in its way. The watch commits with `--no-verify`, because it runs the same check itself just before.
30. **The cleaner records a move with `xv record move` before it commits**, since it commits and the hook would refuse. `xv record move` only appends.
31. **`xv run` prints the verdict as JSON with the record, the worktree and the packet**, and exits 10 on a stop. `XV_NO_COMMIT=1` keeps the watch from committing, for CI checkouts.

## Increment 3: the scenario agent on Playwright

32. **A recording becomes a first-draft red through `xv recording to-test`.** It reads an API sequence (the JSON shape the fixture uses), a HAR file, or the network part of a Playwright trace, and writes a Python `unittest` or a Playwright `request` test that replays it. Expected values come only from the recording's `expected` field. Where there is none, as in every HAR file, the draft fails on purpose until the scenario agent writes the expected value from the scenario's words.
33. **The healer is removed by `xv playwright install`**, which runs `npx playwright init-agents` and then deletes the healer's agent file and, for opencode, its entry in `opencode.json`. It refuses to finish if it finds no healer to remove, so a renamed file in a later Playwright is not missed silently.
34. **On Claude Code, a scenario agent that needs the Playwright MCP server cannot run in `--safe-mode`.** Checked: safe mode drops MCP servers even when `--mcp-config` names them. Such a step uses `--setting-sources project --strict-mcp-config --mcp-config .mcp.json`, and the person's CLAUDE.md then loads; `--bare` with an API key avoids both. The default config keeps safe mode, because an API sequence needs no browser.
35. **"Watch the first green" rides in the last stop of a feature slice.** The scenario agent's note goes into the question the person gets with the merge. A case they only notice by watching sends the slice back with `--next scenario`.
36. **The fixture has no browser page in v0.1.** The Playwright output of the converter was checked once by hand: generated from the fixture's recording, run with `npx playwright test` against the fixture's API, it failed on the defect. The evals cover the API-sequence and HAR paths on both harnesses.

## Increment 4: the guardian's packet

37. **`xv boundary` parses imports itself**: Python's own parser for `.py`, a regex for JavaScript, TypeScript, Ruby and Go. A module is the first path component under a source root in `.xv/config.yml`. The picture of a change runs the same parser on the base and the working tree, so the two sides compare. The whole-repo picture for `xv-init` uses dependency-cruiser's graph when it is installed in the repo, and never downloads it.
38. **The boundary picture gives shape hints, not a verdict**: a module added or removed, an edge between modules added or removed, a module that now calls out of the process, a table or a surface path added or removed. The guardian says for each hint whether it changes the shape, and cites it.
39. **Tables and surface paths come from the added and removed lines of the diff**, by regex: SQL statements and common migration calls, and string literals that look like paths. Cheap and wrong in checkable ways, which is the point.
40. **The evidence rule is enforced by a script.** After the guardian stops, `xv packet lint --fix` moves any finding in the four check sections that cites no line, file, rule, quote or hunk to "Dropped by the evidence rule" at the end. It stays visible and does not count. A packet whose fixed fields are not `yes` or `no` sets both to `yes`.
41. **The packet carries `door`, `shape_breadth` and `picture_change` in its front matter** beside the two fixed fields, so the standing orders can read the picture change and a shape wider than the forecast.
42. **`xv guard` is the guardian on a pull request.** If the change carries one slice record, it runs that slice's guardian step with `XV_NO_COMMIT=1`. Otherwise it reviews the diff against the base with the same brief and the same orders. The CI example posts the packet as a comment, has no permission to approve, and fails its check only when the stop is for two people.

## Increment 5: the cleaner's standards and the retro

43. **A retro is due for a slice that stopped, overran, or shares a stop with another slice** since the last retro. The routine stops (the merge, accepting moves, setting the budget) do not count. An overrun is against the first budget, before any raise, or more than one and a half times the token forecast. "The same guardian finding twice" is read as the same standing order firing on two slices; findings in prose are not matched.
44. **The watch does not start a retro on its own.** `xv close` says when one is due and why, and the person runs it with the `xv-retro` skill. A retro costs a run; the person decides when.
45. **A retro candidate is dropped by the script** when its `from:` line names no slice the records have, or a moment whose words do not appear in that record. Dropped candidates stay visible at the end of the retro packet.
46. **Fire and override counts come from the records.** A fire is a standard named in the cleaner's `applied` list. An override is a person's `xv record override <id> --rule ... --why ...`. A rule with at least five fires and an override rate above `limits.override_rate` (25% by default) is flagged for retirement.
47. **A standard enters the file only through a person's command.** `xv retro accept` and `xv retro standard` write the entry with its date, slice, miss and `seen:` list; the person commits it. The cleaner's candidate standards and shape proposals ride in the packet's "From the cleaner" section, which the watch appends after the guardian.

## Increment 6: the forecaster

48. **`spend.py` reads three sources**: the JSON `claude -p --output-format json` prints, a Claude Code session transcript with its subagent transcripts, and `opencode session export`. Codex is not read in v0.1; its tokens are recorded as zero and its dollars as null, never guessed.
49. **The budget covers the maker's steps.** The other agents' spend is recorded but does not count against it: the budget is the engineer's limit on the work, and the work is the maker's. On Claude Code the watch passes the budget as `--max-budget-usd` and `--max-turns`; on opencode, which has no cap, the watch's check after the step is the cap.
50. **Wall clock is the watch's own clock around each CLI call**, the same measure on every harness. It overwrites what a harness reports, so wall clock compares across all of them.
51. **The read-only agents are checked, not trusted.** If the forecaster changes any file, or the guardian changes anything but its packet, the step stops for the person who set the work going.
52. **New estimation rows ride in the next packet.** The guardian's prompt lists the rows appended since the slice's base, so a person sees them and can revert one.

## Increment 7: the listener

53. **Gathering is a script**, `xv listen gather`: Sentry's issues API, a PostHog HogQL query and its recordings list, and plain-text feedback files the config names, all with the standard library. CI then needs no MCP server and no login; in a person's session the listener may also use Sentry's or PostHog's MCP tools. The two API calls follow the vendors' documented endpoints and were not run against a live account in v0.1.
54. **"Refuses to rank" is checked by a script.** `xv listen lint` fails a packet that uses ordering or recommending words outside a quoted user line ("top 3", "priority:", "fix first", "recommend"), or whose seat is not the chief engineer. The CI example fails on it.
55. **The packet reaches the chief engineer as a pull request that adds the file**, with them as reviewer, and through `reach.command` if the team set one. Not as an issue: opening an issue in the value queue is a small act of ranking. The packet never blocks.
56. **The raw data stays out of the repo.** `.xv/listen/` is ignored; only the packet is committed. Feedback can carry personal data the packet should not.
57. **User feedback is data, never instructions.** The brief says so, and the eval plants an instruction in the feedback to check it.

## Increment 8: xv-check and xv-promote

The cross-repo mechanism is Sean's, in [`docs/positions.md`](positions.md). The choices below are how it was built.

58. **A learning issue is marked by its title, "Learning: ...", not by a label.** People without write access to the shared repo cannot set labels from the CLI, so a script cannot rely on one. Maintainers may add `learning` and `stack:` labels by hand.
59. **A sighting is a block with a fixed heading**, `### Sighting: <repo> · <date> · id <8 hex>`, in the issue body or a comment, so `xv promote tally` can count distinct repos. The id is a hash of the repo's remote URL: a repo that leaves its name out is still counted once.
60. **Drafts and posts are files in `.xv/promote/`.** A draft is reviewed and edited by the person; `xv promote post --approved-by <name>` is the only command that writes in public, and it keeps a copy of what it posted, with the approver, in `.xv/promote/posted/`. The person commits both, so a repo's public posts are in its own history.
61. **The local entry is linked to the issue** (`shared:` or `adopts:`), and `xv check entries` notes it, so the local copy is removed once a release carries the learning.
62. **Stacks are a free-text "Applies to" line and `promote.stack` in the config.** No structure in the skills until use asks for it.
63. **The shared repo's side is a tally and a skill section, not a script that edits briefs.** Writing a learning into a brief is a change to an agent: two people and a CHANGELOG line.
64. **Local promotion is a person's command**: `xv promote local --accept <entry> --to standards|rules --by <name>` moves an Open learning seen twice and logs it under Promoted.
65. **`xv check relaxations` matches phrases**, so it can raise a false alarm; the skill says to read each hit. A miss is worse than a false alarm here.
66. **The drift check reads each harness's public docs page** for the exact sentences in [`docs/relies-on.md`](relies-on.md), ignoring case and whitespace. This repo's CI runs it weekly and opens an issue for a sentence that is gone.
67. **`xv adapt` names generated files `xv-<agent>`** and marks each with the skill's digest, so a generated file never shadows a skill and `xv check` can tell current from stale.

## Increment 9: parallel prototypes

68. **The person names the axis; the three positions default to the ones XV's method names**: the minimum the scenario allows, one that refuses an assumption, one that puts a different object at the centre. A team can pass its own three. Exactly three: more and people review a gallery.
69. **Each prototype gets its own branch and worktree from the slice branch, and its own context.** They run in parallel threads; `--serial` or `prototypes.serial` in the config runs them one at a time, as on one local GPU.
70. **Each prototype makes its own recording**: a script it writes and runs, which shows what a user sees through the scenario's steps. The watch copies the three recordings into the slice branch and lays them side by side in `.xv/slices/<id>.prototypes.md`.
71. **Every prototype is discarded at the pick, the picked one too.** Their worktrees and branches are removed; the recordings stay in the slice record as evidence. The pick takes two names and may name a user who took part. The restated scenario replaces the record's scenario, the old one stays in the log, and the slice goes to the forecaster as a feature.
72. **A maker that runs in a prototype's context stops the slice.** With `xv step` every step is a new CLI call, so this cannot happen by default; the check is there for a team that runs steps in its own session.

## After the review of v0.1

A fresh context reviewed the repo against the plan on 2026-10-22. Its correctness findings were fixed; what it found missing is decided here.

73. **The record's home is the file in v0.1.** The plan allows a pull request or an issue as the home "through record.py adapters". v0.1 ships the file home and `xv record export`, which renders the record as a pull request body one way. Two-way adapters wait for a team that keeps its records elsewhere: `record_home` is read by nothing yet.
74. **No migration code yet.** Nothing in `.xv/` has been renamed, so there is nothing to migrate. A version that renames a file will carry its steps in [`CHANGELOG.md`](../CHANGELOG.md); `xv init` already adds new default files without touching existing ones.
75. **The Open list's dated prune is a listing, not a deletion.** `xv promote local` lists Open learnings seen once and not since 90 days; a person deletes or keeps each.
76. **"The diff keeps growing" is measured across the maker's runs.** The maker stops itself on a growing diff; the watch also fires when the diff more than doubles between two runs of the maker on one slice, and when it passes `limits.max_diff_lines` if the team set one.
77. **One token count everywhere**: input, output, cache read and cache write, in the guide, the budget and the retro (see 19). The retro's "overran" compares the maker's spend with the budget, as the budget order does.
78. **The files people own are checked after every working step.** If the scenario agent, the maker or the cleaner changes `.xv/config.yml`, the slice's wall baseline, the pitch, the picture, the rules or the estimation guide, the slice stops. The wall's own inputs can no longer be edited by the agent it checks.
79. **A retro candidate's moment must name a field or a stop the record has, or quote words the record holds.** A slice id and any word was too loose.
80. **The estimation rows ride in the next packet by name**: the guardian lists every row no earlier packet has listed.

## After the newcomer review

81. **Solo mode keeps every stop and changes only who answers.** With `seats.two_people: solo`, a two-person stop still fires and still ends the watch's turn. One name answers it; the decision record says one person decided. The question tells them to write down what they weighed. `xv check` lists the setting as a declared relaxation and does not fail on it.
82. **The pitch is checked by code before a slice starts.** `xv slice new` refuses while `.xv/pitch.md` is missing or says `status: not written`.
83. **"The same failure repeats" is measured, not only reported.** The watch reads the failing test names from the suite's output (unittest, pytest, Jest, Go) after each maker run, and fires when two runs in a row fail on the same tests.
84. **The guardian's CI job never calls an approve, and that is a promise of the workflow, not of GitHub.** A workflow token with `pull-requests: write` can approve when the repo allows GitHub Actions to create and approve pull requests. The guardian example says to keep that setting off. The listener example pushes its branch and opens the pull request only when the setting allows it; otherwise it says which branch to open one from.
85. **The standing orders are enforced by code when the watch runs headless, and by the watch's brief when it runs in a session.** `xv step` runs the orders itself, so a session watch that uses `xv step` gets them too. A step set to `session` has the watch run `xv orders` after it, and an agent can skip a command. Teams that rely on the stops should run the working steps through `xv step`, which is the default.

## Grok in the benchmark

86. **Grok is the third harness**, as a person has it installed: `grok -p` with `grok-4.7`, JSON output, tools approved, and no subagents, since the Claude workers have no subagent tool either. Grok cannot leave out the person's home rules and skills (see [`docs/harness-notes.md`](harness-notes.md)), so on Grok the brief is not the whole prompt. Isolating it would mean a second `GROK_HOME` holding a copy of the person's login; the evals do not do that.
87. **A harness whose prompt is a flag's value keeps the pair together.** The turn cap goes before `-p`, not between `-p` and the prompt.

## Install, and a trial before adopting

88. **`xv install` replaces the shell loop.** User scope links each skill into the skills folder of every agent that is installed, found by its home folder (`$CLAUDE_CONFIG_DIR` or `~/.claude`, `~/.codex`, `~/.cursor`, `~/.grok`, `~/.agents`), and `xv` into `~/.local/bin`. It creates no folder for an agent that is not there, takes `--into` for any other, and never replaces a folder it did not make. Links mean `git pull` upgrades every agent at once.
89. **Project scope copies, and marks each copy.** A link into one person's clone would break for everyone else, so `--scope project` copies the skills into the repo's own agent folders with `.xv-installed` (the version and a digest). A reinstall replaces an unedited copy and refuses an edited one; `xv check` lists each copy as current, stale, or edited, and says when a user install also exists. The scripts are not copied into the repo: `xv` comes from a user install, and CI checks this repo out.
90. **`gh skill` and `npx skills` are named, not used.** Both copy skills from a GitHub repo and neither installs `xv`; xv-agents does not depend on either.
91. **A trial keeps `.xv/` out of git with `.git/info/exclude`**, which changes no file in the repo, rather than a `.gitignore` line, which would have to be committed. Any ignore rule works: a trial is detected by git ignoring `.xv/config.yml`. A slice's worktree starts from a commit without `.xv/`, so `xv slice new` copies the project layer into it, and `xv close` brings the record, the packet and the new estimation rows back to the main checkout. `xv init --adopt` removes the exclude line.

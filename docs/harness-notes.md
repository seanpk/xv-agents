# Harness notes

What was checked on each harness while building v0.1, against the unknowns the plan listed. Each line says how it was checked and when. A line that says "not checked" is a guess, and `xv check drift` cannot watch it.

Versions: Claude Code 2.1.302, opencode 2.0.32 with Ollama serving `gpt-oss:20b`, codex-cli 0.163.0, gh 2.x with `gh skill` in preview. Checked 2026-10-21.

## Can a brief be the whole prompt of a fresh context?

- **Claude Code: yes.** `claude -p --safe-mode --disable-slash-commands` starts with CLAUDE.md, skills, plugins, hooks and MCP servers off, and still uses the person's login. Asked directly, the model reported no CLAUDE.md in its context. `--bare` does the same but needs `ANTHROPIC_API_KEY`; a login session is not read. Checked by running it.
- **opencode: partly.** `opencode run` cannot drop its own system prompt, so the brief arrives as the user message after opencode's. It reads `AGENTS.md` from the project. The fixture has none. Checked: a run in a repo with no `AGENTS.md` gets about 17,800 input tokens of opencode's own prompt before the brief.
- **codex: not checked.** `codex exec` takes a prompt and has `--json` and `--output-last-message`.

## How does a harness start a fresh context from inside a session?

- **Claude Code**: the Agent tool (a subagent). The watch does not depend on it: `xv step` shells out to a CLI on every harness, so the context is fresh by construction. A team can set a step to `session` to use its harness's subagent instead.
- **opencode**: a subagent through its task tool. Not checked; `xv step` covers it.

## Which CLIs run headless with a prompt and return an exit code?

- `claude -p ... "<prompt>"`: yes. `--output-format json` returns one JSON object with `result`, `session_id`, `num_turns`, `duration_ms`, `total_cost_usd`, `usage` and `modelUsage`. Checked.
- `opencode run --auto --format json --model ollama/<model> "<prompt>"`: yes. It prints one JSON event per line; each carries `sessionID`. Checked.
- `codex exec`: has the flags. Not run.

## Where does each harness write usage, for `spend.py`?

- **Claude Code**: the JSON result above, per run. Session transcripts are `.jsonl` files under `$CLAUDE_CONFIG_DIR/projects/<project>/`; each assistant line carries `message.usage` and `message.model`, and one API message can appear on several lines, so `spend.py` counts each message id once. Transcripts carry tokens, not dollars. Checked.
- **opencode**: `opencode session export <id>` prints JSON whose `info` has `tokens` (`input`, `output`, `reasoning`, `cache.read`, `cache.write`), `cost`, the model, and the start and end times. Its `messages` count the turns. A local model reports a cost of 0. Checked.
- **codex**: not checked. `spend.py` records tokens as zero and dollars as null for a harness it cannot read, and the wall clock from the watch.

## Is a pre-commit hook plus a CI check enough wall without tool-level hooks?

v0.1 uses three layers on every harness: the maker's brief forbids an unrecorded move in words, `xv wall check` runs after the maker and the cleaner and stops the slice, and the same check runs as a pre-commit hook on slice branches and in CI (`ci/github/xv-wall.yml`). No harness-specific hook is needed. Whether the words add anything over the checks is for the evals and for use to say.

## Claude Code refuses writes under `.git/`

Found by the first eval run, 2026-10-21. Slice worktrees were first placed under `.git/xv/worktrees/`. Claude Code treats every path under `.git/` as sensitive and denied the guardian's write of its packet and the maker's edit of a test file. Both agents stopped and reported the denial instead of finding a way around it. Worktrees moved to `.xv/worktrees/`, which `.xv/.gitignore` keeps out of the repo.

## Playwright test agents

See increment 3 below.

## `npx skills add` and `gh skill install`

See increment 8 below.

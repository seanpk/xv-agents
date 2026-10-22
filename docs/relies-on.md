# What the briefs and scripts rely on

Sentences from each harness's own docs that a brief or a script in this repo depends on. `xv check drift` fetches each page and reports a sentence that is gone, so a harness that moves under the skills is noticed before a slice fails on it. Quoted 2026-10-21. A gone sentence is a question for this repo, not for an adopting one.

Each entry is one line: `- <what depends on it> | <url> | "<the sentence, verbatim>"`. The check ignores case and collapses whitespace.

- the forecaster's budget cap, `agentcli.with_caps` | https://code.claude.com/docs/en/cli-reference | "Stop the run once estimated spend on API calls reaches this amount (print mode only)."
- the turn cap, `agentcli.with_caps` | https://code.claude.com/docs/en/cli-reference | "Limit the number of agentic turns (print mode only)."
- a brief as the whole prompt, the default `agents:` config | https://code.claude.com/docs/en/cli-reference | "Start with all customizations disabled to troubleshoot a broken configuration: CLAUDE.md, skills, plugins, hooks, MCP servers"
- the scenario agent with the Playwright MCP server | https://code.claude.com/docs/en/cli-reference | "Only use MCP servers from --mcp-config , ignoring all other MCP configurations."
- the scenario agent's planner and generator, and leaving out the healer | https://playwright.dev/docs/test-agents | "Playwright comes with three Playwright Test Agents out of the box: 🎭 planner , 🎭 generator and 🎭 healer ."
- `xv playwright install` | https://playwright.dev/docs/test-agents | "npx playwright init-agents --loop = opencode"
- `spend.py` reading opencode's events | https://opencode.ai/docs/cli/ | "--format Format: default (formatted) or json (raw JSON events)"
- the opencode `agents:` config | https://opencode.ai/docs/cli/ | "--auto Auto-approve permissions that are not explicitly denied"

---
kind: init packet
date: 2026-10-24
---

# The first packet: the outsider read against the pitch

Places where the pitch and what the code does disagree, for a person to settle. Not resolved here.

1. **Non-technical people.** The pitch says non-technical people adopt xv-agents to create software (`.xv/pitch.md`, "Who uses it"). Every entry point needs a terminal, git, Python 3.10, an agent CLI and a test command (`README.md:365`, `skills/xv-init/SKILL.md` step 1), and the README is written for developers. Is this a promise the code must keep now, so a slice that adds developer-only steps contradicts the pitch, or a direction that belongs in the vision?

2. **"Easy" to adopt.** The pitch says xv-agents makes it easy to adopt XV (`.xv/pitch.md`, the pitch). The one recorded adoption took about 5.5 hours of wall clock and needed setup outside the skill (seanpk/xv-agents#6). This init needed two hand fixes: the detected test command failed, and the default source roots showed two modules (`.xv/config.yml`, `tests.command`, `source.roots`). Does "easy" bind a slice now, for example so the guardian flags a change that adds an init step?

Noted, not raised: the evals and their fixture app, the weekly drift workflow, `xv adapt`, `xv install`, the listener's Sentry and PostHog calls.

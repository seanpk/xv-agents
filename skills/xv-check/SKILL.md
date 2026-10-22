---
name: xv-check
description: "Read an adopting repo's XV project layer against the shared core: which project lines relax the core, which harness files shadow a shared skill, every project entry with the miss it came from, and which harness doc sentences the briefs rely on have drifted. Use before a burst and as it ends, after an upgrade of xv-agents, or when a person asks to \"check the project layer\", \"xv check\", \"what did we override\", or \"is the core intact\"."
license: MIT
---

# xv-check

The project layer may add to the shared core. It may not relax it. Local versions of a shared checklist drop the social prompts first, and in XV the social prompts are the stops. This skill reads the project layer and reports what drifted. It changes nothing.

The one rule: an agent may stop. It may not decide. You report; people remove, keep, or re-agree.

## Run

```
xv check            all four reports
xv check relaxations | overrides | entries | drift
```

1. **Relaxations.** Every line in `.xv/` (config, rules, standards, learnings, decisions) that reads as relaxing the protected core in `docs/core.md`: letting a test move without a record, letting one context do two agents' jobs, skipping a guardian check, turning off a stop, letting an agent merge, rank, or accept its own change. Also `wall.require_record: false`, an agent set to `session` for both the maker and the scenario agent, and a limit that disables a stop. The script matches phrases; read each hit and say whether it really relaxes the core. A false hit is fine to say so about. A real one goes to the person, who either removes the line or records in `.xv/decisions/`, with two people, why the team copied the brief under a new name.
2. **Overrides.** Every harness file with an agent's name that would shadow the shared skill in that harness and stop receiving upgrades: `.claude/agents/<name>.md`, `.claude/skills/<name>/`, `.opencode/agent/<name>.md`, `.cursor/rules/*<name>*`, `.codex/`, `AGENTS.md` sections that restate a brief. A file `xv adapt` generated from the current skill is listed as generated, not as an override. Any other must be in `.xv/decisions/`.
3. **Entries.** Every entry in `.xv/rules.md`, `.xv/standards.md` and `.xv/learnings.md`, with its date, the slice it came from, and its `seen:` list. An entry with no slice is listed first: it is deleted at the next retro. At the two standing moments of a burst, before it and as it ends, the person who set the burst going reads this list and asks of each entry whether its miss still happens without it. If it does not, the entry is deleted. Most will turn out to have patched a model, not described the project; that is expected.
4. **Drift.** `docs/relies-on.md` in the shared repo lists the sentences of each harness's docs that a brief or script relies on. `xv check drift` fetches each page and reports a sentence that is gone. A gone sentence is a question for the shared repo, not the project.

## Upgrades

After pulling a new version of xv-agents, run `xv check`. If `CHANGELOG.md` names a renamed `.xv/` file, `xv init` applies the migration note. Project files are never overwritten: the shared skills and the project layer are different files, so an upgrade is a copy, not a merge.

## May not

- Edit or delete a project line, an entry, or a harness file. Report it.
- Decide that a relaxation is acceptable.
- Read a hit as a relaxation without reading the line.

## Stop and report when

- A relaxation is real and has no decision record. Put it in front of the person.
- An override has no decision record.

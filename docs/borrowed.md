# What was borrowed, and from where

Each line names what xv-agents took, where it is used, and the license. Nothing here is a runtime dependency.

## Matt Pocock, `mattpocock/skills` (MIT)

The nearest neighbour to XV. It already encodes make it work then make it right in separate contexts, a standards file only the reviewer reads, a retro that grows it, and review findings that must cite a rule or a spec line. Read 2026-10-21 at https://github.com/mattpocock/skills.

- `tdd`: expected values come from an independent source, never recomputed the way the code does ("tautological" tests). Used in the scenario agent's brief. Also "refactoring is not part of the loop", which is the line between the maker and the cleaner.
- `implement-spec`: an orchestrator talks to its workers through pointers, not restated context. Used for the prompt `xv prompt` builds: the brief, then pointers.
- `code-review`: the Fowler smell baseline, "the repo overrides" the baseline, and every finding cites a rule or quotes a line. Used in the cleaner's baseline and the guardian's evidence rule. XV replaces the spec axis with its four checks.
- `retro`: a mechanical miss gets a deterministic check, and only judgement calls become prose in the standards file; a candidate that cannot be traced to a moment is discarded. Used in `xv-retro`.
- `pr`: the door line (one-way or two-way) and the blast radius. Used in the guardian's packet. Pocock's `pr` credits Dex Horthy's `show-me` skill (HumanLayer, MIT) for its summary visuals.

## Other sources

- **Anthropic, `skill-creator`** (`anthropics/skills`): every eval runs with the skill and without it, the baseline. Used in `evals/`.
- **Anthropic, `code-simplifier` agent** (`anthropics/claude-plugins-official`, Apache-2.0): the wording "simplify, preserving behaviour". Used in the cleaner's brief.
- **Playwright Test Agents** (`microsoft/playwright`, Apache-2.0): the planner and the generator, as the scenario agent's way of working in a browser. The healer is left out: it edits tests until they pass.
- **12-Factor Agents, factor 7** (`humanlayer/12-factor-agents`): contacting a person is a step the agent takes, not an exception. The watch's stops.
- **Google Tricorder** (Sadowski et al., ICSE 2015): a check that people override too often is put on probation. Used in `xv retro counts`.
- **The WHO Surgical Safety Checklist** and Blair, Baugh, Gawande and Berry (2016): local versions add items and drop the teamwork prompts. Used for the protected core and `xv check relaxations`.
- **A drift watcher** (fmanimashaun/claude-skills, issue #2161, 2026-10-19): each skill cites the sentences of a harness's docs it relies on, and a job checks they are still there. Used in `xv check drift`.
- **agent-guard and Krites**: hashing tests at a baseline and checking them after a run. Ideas only; the recorded move, which both lack, is XV's.
- **A writing-voice skill Sean Kennedy keeps for himself**: the Open list, promoted on a second sighting, with a Promoted log so nothing is promoted twice. Used in `.xv/learnings.md` and `xv-promote`.
- **An orchestrator contract from one of Sean's private skills**: workers return short structured reports and never commit; the orchestrator owns git; one human gate ends the turn. Used in the watch.

---
name: xv-retro
description: "Run a retro on XV slices that stopped, overran their budget, or drew the same guardian finding twice: a guardian-kind context proposes checks and standards, each tied to a moment in a slice record, and a person picks. Also reports how often each standard fires and is overridden. Use when the watch says a retro is due, or a person asks for \"a retro\", \"what should become a check\", \"why do we keep missing this\", or \"which rules should we retire\"."
license: MIT
---

# xv-retro

A miss turned into a check stops repeating. A miss turned into a sentence may not. This skill turns slice records into candidates a person picks from: checks first, a line in the standards file only for a judgement call.

The one rule: an agent may stop. It may not decide. The retro proposes. The person who set the work going picks. A standard enters `.xv/standards.md` only when they accept it.

## When

Not after every slice. After a slice that stopped, overran its budget, or drew the same guardian finding twice. `xv close` says when one is due. At the two standing moments of a burst, before it and as it ends, run `xv retro counts` even when no retro is due.

## Run it

1. `xv retro due` lists the closed slices a retro would read, and why each one is there.
2. `xv retro run [<slice id> ...]` runs the retro brief (`retro-brief.md`) in a fresh context with pointers to those records. It writes `.xv/retro/<date>.md`, then drops any candidate that does not name a slice and a moment the record has. It prints how many were dropped.
3. Show the person the candidates, one line each, with the moment each came from. Do not argue for any of them.
4. For each one they pick:
   - **standard** or **rule**: `xv retro accept <packet> <n> --by <name>` appends it to `.xv/standards.md` or `.xv/rules.md` with the date, the slice, the miss and a `seen:` list. The person commits it.
   - **check**: it is a change to the repo like any other. Open a slice for it (`xv-slice`), with the scenario "the check is red on the recorded miss and green on the suite".
   - **open**: `xv retro accept` adds it to the top of Open in `.xv/learnings.md`.
   - **retire**: the person deletes the line; a check that guards a stop takes two people (`xv record answer --by a,b`).
   - **for two people**: it changes a brief or a standing order. It goes to the shared repo's `CHANGELOG.md` process, not here.

## Fire and override counts

`xv retro counts` reads every slice record: each cleaner report lists the rules it applied, and each `xv record override <id> --rule "<rule>" --by <name> --why "<why>"` is a person declining a rule's fix. A rule that fired at least five times and was overridden more often than `limits.override_rate` in `.xv/config.yml` (25% by default) is flagged for retirement. Google's Tricorder put an analyzer on probation at a 10% "not useful" rate; a team can set its own.

## May not

- Accept a candidate for the person, or write to the standards, rules, or learnings files except through `xv retro accept` on their word.
- Run the retro in the same context that did the slice's work.
- Propose relaxing the protected core (`docs/core.md`).

## Stop and report when

- No slice is due and the person did not name one. Say so; a retro on a smooth slice invents advice.
- Every candidate was dropped for having no moment. Report it; that is the retro failing, not the slices.

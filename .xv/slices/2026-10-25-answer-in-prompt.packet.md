---
slice: 2026-10-25-answer-in-prompt
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: The next agent sees the person's answer; xv slice amend

Nothing here stops the change for two people. Sean, as the person who set the work going, has three things to decide: (a) the answer is carried to every later agent, not only the next one; (b) no `CHANGELOG.md` line, though every agent's prompt input changed; (c) an edit to the picture. The merge is Sean's.

## The scenario

After a person answers a stop, the next agent's prompt (`xv prompt`) carries that answer word for word, under its own heading. `xv slice amend <id> --by <name> --scenario-file <f>` appends the text to the scenario with the date and the name, clears `red`, and sets `next` to `scenario`. (seanpk/xv-agents#18; Sean approves any brief change, solo.)

May ignore: amending may-ignore, the budget, or the kind.

## The recording

None, because a feature starts from words. Replay: `cd tests && python3 -m unittest test_answer_in_prompt`. Before the change, 4 of 5 tests fail (`'2 ok (…)' not found in the maker prompt`; `invalid choice: 'amend'`). After it, all 5 pass. I re-ran this and got `Ran 5 tests … OK`. The cleaner recorded the whole suite green: 131 tests.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-25-answer-in-prompt.boundary.md`), as given: touched `scripts/prompt`, `scripts/run`. No modules added or removed, no edges added or removed, no new outbound calls, no tables, no surface paths. No shape hints.

## What the suite asserts after

- After a stop is answered, `xv prompt maker` contains the answer verbatim, with a heading containing "answer" above it.
- With no answered stop, the prompt has no answer.
- `xv slice amend` keeps the old scenario text and puts the new text after it, with today's date and the amender's name within 200 characters. It sets `red` to null and `next` to `scenario`.
- Amend leaves `kind`, `budget` and `title` alone, and leaves exactly one `## May ignore` heading.
- Amend without `--by` fails, and not with "invalid choice".

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast expected `narrow`).

- `scripts/run.py:813-820` adds a subcommand, `xv slice amend`. It goes to `run.py`, where `slice` already lands (`.xv/picture.md:22`: "`init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`"). The `xv` CLI is already a surface (`.xv/picture.md:27`). This adds a verb to an existing surface, not a new surface.
- `scripts/run.py:33` adds an import of `today` from `xvlib`. The `run` → `xvlib` edge already exists.
- `scripts/prompt.py:101-109`: `answer_section` reads `data["stops"]`, the record data `prompt` already loads. No new dependency.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:7`: "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." Putting the person's answer in front of the agent, and giving people a recorded way to change scope, serves this line.
- `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code") does not bear on this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at:
- `git diff --stat 0950a03..HEAD -- tests`: only `tests/test_answer_in_prompt.py` (new, +78). That file is the red.

I could not run `xv wall diff` in this session: permission was denied.

### For Sean (not stops)

- **The answer goes to every later agent, not only the next one.** At `scripts/prompt.py:103-106`, `answered = [s for s in … if s.get("answer")]` … `st = answered[-1]`. Nothing checks whether a step has run since the answer, and `scripts/prompt.py:138` adds the section to every agent's prompt. In this slice, the `budget_not_set` answer ("yes, run them (the same budget as before …)") would go into the scenario, maker, cleaner and guardian prompts. The scenario says "the next agent's prompt". The test only checks the maker right after the answer, so the suite does not pin this either way.
- **No `CHANGELOG.md` line.** `.xv/picture.md:58`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`." `scripts/prompt.py:138` changes the input every agent gets, though not any `SKILL.md`. The scenario says "Sean approves any brief change, solo", which reads as if Sean expected it to count. The diff touches no `CHANGELOG.md`.
- **`amend` does not check status.** `scripts/run.py:222-238` sets `next` to `scenario` on any slice, including a `closed` one. The scenario does not ask for a guard.
- **No docs updated.** `docs/slice-record.md:17` says `next` is set by "the watch", and `:20` says `red` is set by "the scenario agent". `xv slice amend` now sets both. `skills/xv-slice/SKILL.md` and the README do not mention `amend`.

## 4. The picture

Nothing in `.xv/picture.md` becomes untrue. The diff makes two places incomplete. Proposed edits, for Sean to accept:

- `.xv/picture.md:39-42` ("Where the code and the docs disagree"): add "README line 211 says `xv prompt` builds the agent's input from the skill's body and pointers, and 'Nothing is restated that the agent can read itself.' Since 2026-10-25-answer-in-prompt, the prompt also restates the latest answered stop word for word (`scripts/prompt.py:101`)." Or, if Sean prefers, fix the README in a later slice and leave the picture as it is.
- `.xv/picture.md:22`: optionally name `slice new` and `slice amend` as the two `slice` verbs, so readers know a person can change a running slice's scope.

## Door

**Door:** two-way. A revert removes the prompt section and the subcommand. No data is migrated, and records amended before a revert keep valid Markdown. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-25-answer-in-prompt.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`
- Wall: `xv wall diff 2026-10-25-answer-in-prompt` (baseline `0950a037`, 26 files)
- Boundary: `xv boundary --base f452d430f44f6c01e611f705f5b709b80231291b`, saved at `.xv/slices/2026-10-25-answer-in-prompt.boundary.md`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- `xv boundary` reports no added edges, modules, tables or surfaces, and no shape hints.
- The record's `moved_tests: []`.
- The wall check after the maker and after the cleaner: `changed: [], deleted: [], added: [], fewer_assertions: [], unrecorded: [], ok: true`.

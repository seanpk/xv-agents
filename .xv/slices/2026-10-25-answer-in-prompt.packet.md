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

Nothing here needs two people. Sean, as the person who set the work going, has three things to decide. Two of the three items settled at the last accept stop are not in the diff: the README line 211 edit and the `CHANGELOG.md` line. An answer given in the same second as the last report never reaches any agent. The merge is Sean's.

## The scenario

After a person answers a stop, the next agent's prompt (`xv prompt`) includes that answer word for word, under its own heading. `xv slice amend <id> --by <name> --scenario-file <f>` appends the text to the scenario with the date and the name, clears `red`, and sets `next` to `scenario`. Settled by Sean on 2026-10-26: (1) the answer goes only to the next agent, and a test shows the agent after that one does not get it; (2) update README line 211; (3) add a `CHANGELOG.md` line under Unreleased.

May ignore: amending may-ignore, the budget, or the kind.

## The recording

None, because a feature starts from words. Replay: `cd tests && python3 -m unittest test_answer_in_prompt`. Red (record): `'2 ok (…)' unexpectedly found in the cleaner prompt`. I re-ran it now: `Ran 6 tests … OK`. Whole suite: `Ran 132 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-25-answer-in-prompt.boundary.md`, as given: it touches `scripts/prompt` and `scripts/run`. No modules, edges, outbound calls, tables or surface paths were added or removed, and there are no shape hints.

## What the suite asserts after

- After a stop is answered, `xv prompt maker` contains the answer verbatim, under a heading containing "answer".
- With no answered stop, the prompt has no answer.
- After the maker reports, `xv prompt cleaner` no longer carries the answer (new this round, `tests/test_answer_in_prompt.py:29-42`).
- `xv slice amend` keeps the old scenario text and puts the new text after it, with today's date and the amender's name nearby. It sets `red` to null and `next` to `scenario`. It leaves `kind`, `budget`, `title` and the single `## May ignore` alone. It fails without `--by`.

## For Sean (not stops)

1. **The README line was not changed.** Item (2) of the settled scenario asks for an edit to `README.md:211`: "Nothing is restated that the agent can read itself." `git diff --stat f452d430..HEAD -- README.md` is empty. The line is now untrue: `scripts/prompt.py:142` puts `answer_section(data)` into every prompt, and that section restates `stops[].answer` from the record.
2. **There is no `CHANGELOG.md` line.** Item (3) asks for one, and `.xv/picture.md:58` requires one: "A change to a brief, … needs two people and a line in `CHANGELOG.md`." `git diff --stat f452d430..HEAD -- CHANGELOG.md` is empty, and `CHANGELOG.md:5-7` (Unreleased) still has only the promote entry.
3. **An answer in the same second as a report is lost.** `scripts/prompt.py:109`: `if any((r.get("at") or "") >= since for r in …reports…): return ""`. Both timestamps are to the second, and `>=` treats a report from the same second as coming after the answer. This slice's own record shows the case: the forecaster reported at `2026-10-25T04:26:16+00:00`, and Sean answered `budget_not_set` at `2026-10-25T04:26:16+00:00`. Under this code, the scenario agent, which ran next, would not get "yes, run them …". The scenario says the next agent gets the answer. The new test (`tests/test_answer_in_prompt.py:29-42`) uses timestamps far apart, so it does not catch this.

Also noted, with no decision needed: the cleaner reported that its commit was refused (`checks.reports[-1]`, `cleaner_commit: null`). Its edit to `scripts/prompt.py:103-109` is nonetheless in HEAD, in `b14d42b` ("record the cleaner's pass"), and the worktree is clean. The record and the diff agree on the code.

## 1. Shape

shape_change: no. shape_breadth: narrow (the forecast expected `narrow`).

- `scripts/prompt.py:101-114` adds `answer_section`, which reads `stops` and `checks.reports` from the record data `build` already loads. It adds no new import and no new edge.
- `scripts/run.py:816-820` adds the verb `xv slice amend`. Per `.xv/picture.md:22`, "`init`, `slice`, `run`, … all land in `run.py`", and the `xv` CLI is already a surface (`.xv/picture.md:27`). This is a new verb on an existing surface.
- `scripts/run.py:33` adds an import of `today` from `xvlib`, an edge that already exists.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:7`: "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." Putting a person's answer in front of the agent that has to act on it, and giving people a recorded way to change scope, both serve this line.
- `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot.") does not bear on this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at:
- `git diff 272b369..HEAD --stat -- tests` (the wall baseline): `tests/test_answer_in_prompt.py | 16 +++`, with 0 lines removed. That is the new class `AnswerReachesOnlyTheNextAgentTest`, the red.

## 4. The picture

Sean's settled scenario says the picture needs no edit once README line 211 is updated. That README edit is not in the diff (finding 1 above), so the picture is incomplete as things stand:

- `.xv/picture.md:39-40`, "Where the code and the docs disagree … the README is behind": while `README.md:211` stays as it is, add "README line 211 says the prompt restates nothing the agent can read itself. Since 2026-10-25-answer-in-prompt, `xv prompt` also restates the latest answered stop, until an agent reports after it (`scripts/prompt.py:101`)." Fixing the README instead makes this edit unnecessary.
- `.xv/picture.md:70`, decision 13 ("points to files rather than restating them"): this decision is about briefs, and the answer section belongs to the prompt's pointers, not the brief. If Sean wants that boundary on record, add "the prompt may carry the latest answer to a stop, for the next agent only."

## Door

**Door:** two-way. A revert removes the prompt section and the `amend` verb. No data is migrated, and a record amended before a revert stays valid Markdown. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-25-answer-in-prompt.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..b14d42b`
- Wall: `xv wall diff 2026-10-25-answer-in-prompt` (baseline `272b369`, 26 files)
- Boundary: `xv boundary --base f452d430f44f6c01e611f705f5b709b80231291b`, saved at `.xv/slices/2026-10-25-answer-in-prompt.boundary.md`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The watch's diff-growth stop (226 to 737 lines) counted record, boundary and packet files. Under `scripts/` the code diff is +41/−2 (`git diff --stat`).
- The record's wall checks after the maker and after the cleaner: `changed: [], deleted: [], fewer_assertions: [], unrecorded: [], ok: true`. The record has `moved_tests: []`.
- I could not run `xv wall diff 2026-10-25-answer-in-prompt` in this session because permission was refused.

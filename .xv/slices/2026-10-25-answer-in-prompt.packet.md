---
slice: 2026-10-25-answer-in-prompt
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: The next agent sees the person's answer; xv slice amend

Nothing here needs two people, and nothing new needs a decision from Sean. The same-second fix Sean settled at the second accept stop is in the diff and has a test. There is one small note below (an agent that ends without a report does not clear the answer). The README line 211 edit and the `CHANGELOG.md` line are still missing, and Sean has moved both to the watch for when the pull request is opened. The merge is Sean's.

## The scenario

After a person answers a stop, the next agent's prompt (`xv prompt`) includes that answer word for word, under its own heading. `xv slice amend <id> --by <name> --scenario-file <f>` appends the text to the scenario with the date and the name, clears `red`, and sets `next` to `scenario`. Sean settled these on 2026-10-26:

- First accept stop: the answer goes only to the next agent.
- Second accept stop: an answer given in the same second as the last report still reaches the next agent, because order in the record decides. The README and CHANGELOG edits are the watch's work at pull request time.

May ignore: amending may-ignore, the budget, or the kind.

## The recording

None, because a feature starts from words. Replay: `cd tests && python3 -m unittest test_answer_in_prompt`. Red (record): the answer was "not found in '# The maker ...'" for the same-second case. I re-ran it now: `Ran 7 tests … OK`. Whole suite: `Ran 133 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-25-answer-in-prompt.boundary.md`, as given: it touches `scripts/prompt` and `scripts/run`. No modules, edges, outbound calls, tables or surface paths were added or removed, and there are no shape hints.

## What the suite asserts after

- After a stop is answered, `xv prompt maker` contains the answer verbatim, under a heading containing "answer".
- With no answered stop, the prompt has no answer.
- After the maker reports, `xv prompt cleaner` no longer carries the answer.
- New this round (`tests/test_answer_in_prompt.py:44-66`): a report and an answer stamped with the same second, with the report first in the record. `xv prompt maker` still carries the answer.
- `xv slice amend` keeps the old scenario text and puts the new text after it, with today's date and the amender's name nearby. It sets `red` to null and `next` to `scenario`. It leaves `kind`, `budget`, `title` and the single `## May ignore` alone. It fails without `--by`.

## For Sean (not stops)

1. **The same-second fix is in, and it uses order in the log.** At `scripts/prompt.py:110`, `given` is the index of the last log line containing ` answered <order>: `. At `scripts/prompt.py:111-117`, a report stamped strictly later clears the answer. A report stamped in the same second clears it only if its log line (`- <at> <agent>: `) comes after `given`. This slice's own record is the case from the scenario: the forecaster's line at `04:26:16` comes before `Sean Kennedy: answered budget_not_set` at `04:26:16`, so the scenario agent would get the answer. If no log line is found for the answer (`given = -1`), any same-second report clears it. That is the cautious default.
2. **An agent that ends without a report does not clear the answer.** At `scripts/record.py:281-284`, the `no-report` entry is appended without an `at`. At `scripts/prompt.py:112-113`, `at = r.get("at") or ""` never compares later than `since`. Concretely: if the maker crashes after an answer, the next maker or cleaner still sees the answer. That fits "the agent that acts on it gets it", but strictly it is not "only the next agent to run". You may want this. No test covers it.
3. **The README and CHANGELOG are still unchanged.** `README.md:211` still says "Nothing is restated that the agent can read itself." `.xv/picture.md:58` (decision 1) requires a `CHANGELOG.md` line for a change to what an agent is given. Neither file is in `git diff --stat f452d430..HEAD`. Sean's second settlement in the record moved both to the watch at pull request time. This is a reminder that they still have to land, not a finding against the slice.

## 1. Shape

shape_change: no. shape_breadth: narrow, as the forecast expected.

- `scripts/prompt.py:101-121`: `answer_section(data, body)` reads `stops`, `checks.reports` and now the log body. `build` already loaded all three through `read_doc` (`scripts/prompt.py:130`, where the old code used to discard the body as `_`). It adds no import and no edge.
- `scripts/run.py:222-238,816-820`: `xv slice amend` is a new verb on a surface that already exists. `.xv/picture.md:22` says "`init`, `slice`, `run`, … all land in `run.py`", and `.xv/picture.md:27` lists the `xv` CLI as a surface.
- `scripts/run.py:33`: this adds `today` to an existing `xvlib` import.

## 2. Pitch

pitch_contradiction: no.

- `.xv/pitch.md:7`: "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." Putting the person's answer in front of the agent that acts on it, and giving people a recorded way to change scope, both serve this line.
- `.xv/pitch.md:25` (not for people who will not trust agents with production code; never a teapot) does not bear on this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at:
- `git diff --stat 102c2229..HEAD` (the wall baseline in `wall_baseline`): `tests/test_answer_in_prompt.py | 24 +++`, with 0 lines removed. That is the new same-second test, the red from commit `ff009d0`.

## 4. The picture

No edit is proposed. In the record's first settlement, Sean said: "Update README line 211 … With that, the picture needs no edit." The second settlement gives the README edit to the watch at pull request time. Until it lands, `README.md:211` and the code disagree, and that is the kind of gap `.xv/picture.md:39-40` tracks. If the pull request opens without the README edit, add a line there: "README line 211 says the prompt restates nothing the agent can read itself; `xv prompt` also restates the latest answered stop for the next agent (`scripts/prompt.py:101`)."

## Door

**Door:** two-way. A revert removes the prompt section and the `amend` verb. No data is migrated, and a record amended before a revert stays valid Markdown. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-10-25-answer-in-prompt.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..6e7d337` (the worktree is clean)
- Wall baseline: `.xv/slices/2026-10-25-answer-in-prompt.wall.json` (commit `102c222`, 26 files)
- Boundary: `.xv/slices/2026-10-25-answer-in-prompt.boundary.md`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The record's wall check after the maker and after the cleaner: `changed: [], fewer_assertions: [], unrecorded: [], ok: true`, and `moved_tests: []`.
- I could not run `xv wall diff 2026-10-25-answer-in-prompt` in this session because the command needs approval. The two sources above agree.

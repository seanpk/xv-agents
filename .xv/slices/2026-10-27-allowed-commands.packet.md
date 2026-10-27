---
slice: 2026-10-27-allowed-commands
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: every-agent
---

# Packet: Each agent's prompt says which commands it may run

Second pass, after the send-back for Sean's two settled points. Nothing here stops the change for two people. The merge is Sean's. Two things need Sean before merge:

1. **The CHANGELOG line describes the old wording.** It still says "no chained command", which the code no longer says (finding 1.2).
2. **The picture edit** from the first packet is still unwritten (section 4).

## The scenario

`xv prompt <agent> <id>` reads the Bash rules from the agent's own `--allowedTools` in `.xv/config.yml` (its own line, or the default line) and lists them as plain commands. It adds three cautions: a chain is allowed only when every part is a listed form, no extra flags in front of a listed form (`python3 -W ignore -m unittest`), and no pipe to an unlisted program. A `Bash(cmd *)` rule is listed without the `*`, the same as `Bash(cmd:*)`. A line with no `--allowedTools`, or a harness other than Claude Code, gets no list. The CHANGELOG line is there; Sean decided it, solo (#48). Settled at the first guardian stop: (1) chains of listed forms stay allowed, (2) strip the space-star. May ignore: nothing stated.

## The recording

None; this is a feature. To replay, run `cd tests && python3 -m unittest test_allowed_commands_prompt`. At HEAD `af54623` it runs 8 tests, OK (I ran it). The whole suite at HEAD passed 228 tests OK in the cleaner's run (slice record, `checks.cleaner.suite_output`). I did not re-run the whole suite.

## The boundary picture

Taken as given from `.xv/slices/2026-10-27-allowed-commands.boundary.md`:
- Modules touched: `scripts/prompt`. None added or removed. No new outbound callers.
- Edges added: none. Edges removed: none. `prompt → agentcli` already existed.
- Tables: none. Surface paths: none added or removed.
- Shape hints: none.

## What the suite asserts after

`tests/test_allowed_commands_prompt.py` is a new file with 8 tests:
- The default line's Bash rules appear as plain commands.
- `Read` and the text `Bash(` do not appear.
- The prompt contains the `python3 -W ignore -m unittest` example and the words chain, pipe and approval.
- The prompt says "every part" and does not say "do not chain" (:60).
- `Bash(git status *)` is listed as `` `git status` ``, with no star (:66).
- A seat with its own line gets its own list, not the default's.
- A line with no `--allowedTools` gets no list.
- A non-Claude harness gets no list.

No old assertion changed.

## 1. Shape

shape_change: no. shape_breadth: narrow, as the forecast expected.

- 1.1 The boundary picture shows no added module, edge, table or surface, and no shape hints. The change stays inside `prompt`, which already "build[s] and run[s] the agent calls" (`.xv/picture.md:23`). The new code is `scripts/prompt.py:54-94`. It reads config through the existing `agentcli.argv_for` and is called from `build` (`scripts/prompt.py:193-194`), plus one CHANGELOG line (`CHANGELOG.md:7`).
- 1.2 **The CHANGELOG contradicts the code. This is not a shape change, but decision 1 depends on the line.** `CHANGELOG.md:7` says the list comes "with three cautions: no chained command, no extra flags in front of a listed form, no pipe to an unlisted program". The code now says `"- Chain commands (`&&`, `;`, `||`) only when every part of the chain is one of those forms.\n"` (`scripts/prompt.py:91`). The line also does not mention the `Bash(cmd *)` form (`scripts/prompt.py:68`). Decision 1 requires a CHANGELOG line for a change to what an agent is given (`.xv/picture.md:59`), and this line describes the version that was sent back. The test file's closing comment has the same stale wording, "no chained command" (`tests/test_allowed_commands_prompt.py:96`). The cleaner reported this and left it alone (record log, 18:15:39).
- 1.3 **The settled point is only partly tested.** Sean asked to "Test the wording against this repo's suite command" (record, Scenario, settled point 1). Test :60 checks that "every part" is present and "do not chain" is absent. Its fixture line lists `cd tests` and `python3 -m unittest` (`tests/test_allowed_commands_prompt.py:7`), but the fixture's suite command is `python3 -m unittest discover -s tests -t .` (record, `checks.scenario.red_output`), which is not a chain. No test renders a prompt whose suite command is `cd tests && python3 -m unittest -q` (`.xv/config.yml:22`). The wording at `scripts/prompt.py:91` does allow that command as written.
- 1.4 Lesser, carried from the first packet. Rules are found only after the exact flag `--allowedTools`, in one comma-joined argv item (`scripts/prompt.py:61-67`). A hand-written line with `--allowed-tools`, space-separated rules, or a comma inside a rule (`Bash(git log --format=%H,%s:*)`) gets no list or a broken one, and nothing reports it. This matches what `xv init` writes, so the starter config is fine.
- 1.5 Observed in this run, outside the diff. My own config line lists `Bash(cat:*)` (`.xv/config.yml:36`). Still, `cat` on the packet template at `/home/sean/Making/Personal/xv-agents/skills/guardian/packet.md` was blocked, because Claude Code limits reads to the worktree. The new section says "Any other form waits for an approval" (`scripts/prompt.py:94`), which suggests the listed forms never wait. A listed command on a path outside the checkout still waits. I could not read the template, so this packet follows the first packet's shape.

## 2. Pitch

pitch_contradiction: no.

- What I looked at: `.xv/pitch.md:7`, "makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline", and `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code". Telling headless agents which forms run without approval fits line 7. The change serves no new user and breaks no promise.
- `.xv/picture.md:48`, "Any harness that reads skills must stay possible": non-Claude lines get no section (`scripts/prompt.py:61`), so they are unchanged.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Evidence: `xv wall diff 2026-10-27-allowed-commands` reports changed [], deleted [], added [] and fewer_assertions [] against baseline `b043c03`. The record has `moved_tests: []`. The two tests added after the send-back (:60, :66) are in the same new file, and the scenario agent wrote them before the maker ran (record log, 18:05:26).

Slice-only tests removed: none. Kept: none (the record's `slice_only: []`).

## 4. The picture

The two edits proposed in the first packet are not in `.xv/picture.md`. The diff does not touch it. They still apply, updated for the new wording:

- `.xv/picture.md:20`, "`xv init` gives Claude Code agent lines a starter Bash allow list". Proposed addition: "and `xv prompt` shows each Claude Code agent its own line's Bash rules as the commands it may run, with cautions: chain only listed forms, no extra flags in front, no pipe to an unlisted program".
- `.xv/picture.md:25`, "Changing the test command later does not change the list". Proposed addition: "and the prompt shows the agent that stale list as its allowed commands".

## Door

**Door:** two-way. A revert removes the section, and no data, contract or message leaves the repo. **Blast radius:** every-agent. It reaches every Claude Code seat's prompt, here and in every adopter who updates.

## Raw data

- Slice record: `.xv/slices/2026-10-27-allowed-commands.md`
- Diff: `git diff 99ae369ea03712578048ec10090c55dc5775b123..af54623`. The worktree was clean when this pass started.
- Wall: `xv wall diff 2026-10-27-allowed-commands`
- Boundary: `.xv/slices/2026-10-27-allowed-commands.boundary.md`

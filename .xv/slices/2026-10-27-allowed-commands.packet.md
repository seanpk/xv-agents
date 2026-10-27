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

Nothing here stops the change for two people. The merge is Sean's, as originator. One finding needs Sean's attention before merge: the new caution against chaining contradicts the suite command that the same prompt gives every agent (see finding 1.2). There is also a picture edit to accept.

## The scenario

`xv prompt <agent> <id>` reads the Bash rules from that agent's own `--allowedTools` in `.xv/config.yml` (its own line, or the default line) and lists them as plain commands. It also gives three cautions: no other command chained before a listed form, no extra flags in front of one (`python3 -W ignore -m unittest` is not `python3 -m unittest`), and no pipe to an unlisted program. A line with no `--allowedTools`, or a harness other than Claude Code, gets no list. CHANGELOG line, Sean solo (#48). May ignore: nothing stated.

## The recording

None; this is a feature. Replay the red and the green with `cd tests && python3 -m unittest test_allowed_commands_prompt`. It fails at base `99ae369` and passes at HEAD `d0835ad`. Whole suite at HEAD: 226 tests OK (cleaner's run, recorded in the slice record).

## The boundary picture

From `.xv/slices/2026-10-27-allowed-commands.boundary.md`, as given:
- Modules touched: `scripts/prompt`. None added or removed. No new outbound callers.
- Edges added: none. Edges removed: none. (`prompt.py` now imports `re`, which is in the standard library, and calls `agentcli.argv_for`/`harness_of`. `prompt → agentcli` already existed.)
- Tables: none. Surface paths: none added or removed.
- Shape hints: none.

## What the suite asserts after

New file `tests/test_allowed_commands_prompt.py`, with six tests:
- The default line's Bash rules appear as plain commands (`cd tests`, `python3 -m unittest`, `git diff`, `cat`, `xv wall diff`).
- Non-Bash tools (`Read`) and the `Bash(` syntax do not appear.
- The prompt has the `python3 -W ignore -m unittest` example and the words chain, pipe and approval.
- A seat with its own line gets its own list and not the default's, and the other way round.
- A line with no `--allowedTools` gets no list.
- A non-Claude harness gets no list.

No old assertion moved.

## 1. Shape

shape_change: no.

- 1.1 The boundary picture shows no module, edge, table or surface added or removed, and no shape hints (`.xv/slices/2026-10-27-allowed-commands.boundary.md`, "Shape hints: none", "Edges added: none"). The change stays inside `prompt`, which `.xv/picture.md:23` says already "build[s] and run[s] the agent calls". Breadth is narrow, as forecast: one prompt builder (`scripts/prompt.py:54-94`), the reader is the existing `agentcli.argv_for`, and one CHANGELOG line (`CHANGELOG.md:7`).
- 1.2 **Contradiction inside the prompt (not a shape change; Sean should decide before merge).** `scripts/prompt.py:91` adds `"- Do not chain another command before it or after it (`&&`, `;`, `||`).\n"`. The same prompt's pointers still give `- Whole suite: `{tests['command']}`` (`scripts/prompt.py:115`), and this repo's `tests.command` is `"cd tests && python3 -m unittest -q"` (`.xv/config.yml:22`). The red command is chained the same way (`prompt.py:108`; the record's `red.command`). So the maker, cleaner and guardian are told to run a chained command and also told never to chain. The scenario forbids only "no *other* command chained before it", meaning an unlisted one. Both halves of this chain are listed (`Bash(cd tests:*)`, `Bash(python3 -m unittest:*)`, `.xv/config.yml:34`). The code's wording is broader than the scenario's. The test at `tests/test_allowed_commands_prompt.py:51` checks only that the word "chain" is present, so it cannot catch this.
- 1.3 Lesser: rules are found only by the exact flag `--allowedTools` followed by one comma-joined string (`scripts/prompt.py:61-68`). That matches what `xv init` writes (`scripts/run.py:846`). A hand-written line that uses `--allowed-tools`, space-separated rules, or several argv items after the flag gets no section, and nothing says so. Rules in the newer `Bash(cmd *)` form would be listed with the `*` included (`prompt.py:68`, the regex strips only `:*`).

## 2. Pitch

pitch_contradiction: no.

- What I looked at: `.xv/pitch.md:7`, "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline", and `.xv/pitch.md:25`, "not for people or projects that will not trust agents to write production code". The change helps headless runs finish without waiting on approvals, which fits line 7. It serves no new user and breaks no promise.
- Related binding lines in the picture: `.xv/picture.md:48`, "Any harness that reads skills must stay possible". Non-Claude lines get no section (`prompt.py:61`), so they are unchanged. `.xv/picture.md:59` (decision 1) says that a change to what an agent is given needs two people and a CHANGELOG line. The CHANGELOG line is there (`CHANGELOG.md:7`), and `seats.two_people: solo` (`.xv/picture.md:51`) makes Sean alone the two people.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-10-27-allowed-commands`: changed [], deleted [], added [], fewer_assertions [], against baseline `1177fed`. The record's `moved_tests: []`.

Slice-only tests removed: none. Kept: none (the record's `slice_only: []`).

Placement note: `skills/scenario/SKILL.md:27` says "Write the new tests in the existing test file for the code under test; make a new test file only when none exists." There is no `test_prompt.py`, but `tests/test_init_allow_list_prompt.py` already tests `--allowedTools` together with `xv prompt`. The new tests went into a new file (`tests/test_allowed_commands_prompt.py`, new in the diff). Whether that is the right home is Sean's call.

## 4. The picture

- `.xv/picture.md:20` says "`xv init` gives Claude Code agent lines a starter Bash allow list". This is now incomplete: the allow list also feeds the prompt. Proposed: add "and `xv prompt` lists that line's Bash rules to the agent as the commands it may run, with cautions against chaining, extra flags and unlisted pipes".
- `.xv/picture.md:25` says "Changing the test command later does not change the list." This is still true, but the consequence is now visible to agents: a stale list is shown to them as their allowed commands. Proposed: add "and the prompt shows the agent that stale list".

## Door

**Door:** two-way. A revert removes the section, and no data, contract or message leaves the repo. **Blast radius:** every-agent. It reaches each Claude Code seat's prompt in this repo and in every adopter who updates.

## Raw data

- Slice record: `.xv/slices/2026-10-27-allowed-commands.md`
- Diff: `git diff 99ae369ea03712578048ec10090c55dc5775b123..d0835ad`. The cleaner's edit is committed in `d0835ad`, so the worktree has nothing uncommitted beyond the boundary file.
- Wall: `xv wall diff 2026-10-27-allowed-commands`
- Boundary: `xv boundary --base 99ae369ea03712578048ec10090c55dc5775b123`

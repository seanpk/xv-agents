---
slice: 2026-10-25-init-allow-list
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: xv init writes a starter allow list

No stop for two people. The merge is Sean's. Three findings need Sean's decision first. The first one matters most: the starter list gives the default seat and the guardian `Bash(python3:*)` in any repo with a `tests/` folder.

## Needs a decision (the person who set the work going)

1. **The test rule is cut at `python3`, not at `python3 -m unittest`.** The scenario asks for rules "as this repo's `.xv/config.yml` does (`Bash(cd tests:*)`, `Bash(python3 -m unittest:*)`)". The cut in `test_rules`:
   `scripts/run.py:718` `is_arg = w.startswith("-") and not (i and words[i - 1] == "-m")`
   `scripts/run.py:719` `if keep and not re.match(r"\w+=", keep[-1]) and (is_arg or "/" in w or w in (".", "discover")):`
   Traced by hand, on `python3 -m unittest`: the word `-m` counts as an argument because the word before it is `python3`, so the loop stops after `python3`. The results:
   - `python3 -m unittest` and `python3 -m pytest -q` give `python3`.
   - `PYTHONPATH=src python3 -m unittest discover …` gives `PYTHONPATH=src python3`.
   - `go test ./...` gives `go test`.

   The fallback adds `python3 -m unittest` to every repo with a `tests/` folder, whatever its language (`scripts/run.py:795-796`). So a Go or npm repo with `tests/` also gets the rule. The default seat and the guardian both get it (`scripts/run.py:734`). `Bash(python3:*)` allows `python3 -c …`, which can run anything. For the guardian, that cancels the read-only list. That works against `.xv/picture.md:69`: "Read-only agents are checked, not trusted."

   The suite does not catch this. It checks that each part of a command is covered (`tests/test_init_allow_list_split.py:21-33`, `rule_allows` and `unallowed_parts`). Nothing checks that a rule is narrow. I could not run `xv init` in a scratch repo in this session, because ad-hoc Python was refused. The trace is from the code; replay it with the steps below.
2. **The `PYTHONPATH=src` case is neither split into its own rule nor handed to the person.** The scenario says: "Cover a leading `PYTHONPATH=src` the same way, or say in the skill that the person checks it." The code keeps the variable glued to the next word: `keep[-1]` matching `\w+=` never cuts (`scripts/run.py:719`). The result is one rule, `Bash(PYTHONPATH=src python3:*)`. No skill changed: the diff touches no `skills/` file. The test comment says "a leading VAR=value … is a part of its own" (`tests/test_init_allow_list_split.py:52`), but its splitter splits only on `&&`, `||` and `;` (`:33`). Whether Claude Code matches a rule that starts with a variable assignment is still unchecked, as in the last packet.
3. **Rules come from every detected runner and the fallback, not only the chosen command.** The call is `allow_lists(text, [command] + [r["command"] for r in runners] + fallback)` (`scripts/run.py:796`). The scenario says "the test command it detected". This widening is what lets finding 1 reach repos that are not Python.

Smaller, for Sean:
- The old red's closing comment is now untrue: "the guardian's adds only the test command" (`tests/test_init_allow_list.py:97`). The guardian now also gets the three `xv` commands. No assertion is wrong.
- The cleaner proposed sharing the parsing and matching helpers duplicated between the two test files (`allowed`/`covers` at `tests/test_init_allow_list.py:15-29`, `entries_of`/`rule_allows` at `tests/test_init_allow_list_split.py:14-28`) in `tests/helpers.py`. It left this for the packet because it is a new shared piece.

## The scenario

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`. The default seat gets read-only shell and git commands, `git rm`, `git mv`, `xv record move` and the test command. The forecaster gets the read-only part only. The guardian gets the read-only part plus the test command.

Sean widened it on 2026-10-26:
1. Split the test command into parts, one rule each, so a single file runs as well as the suite. Cover `PYTHONPATH=src`, or say in the skill that the person checks it.
2. The guardian also gets `xv wall diff`, `xv boundary` and `xv packet lint`.
3. Add `rg`, `wc`, `sed -n`, `diff`, `git ls-files`, `git grep` and `git rev-parse` to the read-only list.
4. Add a CHANGELOG line, Sean, solo.

May ignore: other harnesses, and lint and type commands. (#16)

## The recording

None; this is a feature from words. To replay the red: `cd tests && python3 -m unittest test_init_allow_list_split`. It was red at `7f5bafa` and is green now: 5 tests OK, run in this session. To replay finding 1: in a scratch git repo with a `tests/` folder, run the worktree's `bin/xv init`, then read `.xv/config.yml` lines 34-36 and look for `Bash(python3:*)`.

## The boundary picture

From `.xv/slices/2026-10-25-init-allow-list.boundary.md`, as given:
- Touched: `scripts/run`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

## What the suite asserts after

Whole suite: 136 tests, OK, run in this session.
- Every part of a `PYTHONPATH=src` command, split on `&&`, `||` and `;`, is covered by some rule for the default seat and the guardian.
- `bundle exec rspec spec/a_spec.rb`, `go test ./pkg` and `python3 -m unittest tests.test_a` are covered.
- All three seats carry the seven added read-only rules.
- Only the guardian carries `xv wall diff`, `xv boundary` and `xv packet lint`.
- `CHANGELOG.md` has an Unreleased line naming the allow list, Sean, and solo.
- The earlier file still asserts the base read-only and move rules, that the forecaster has no move or test rule, and that commented-out lines get no list.
- Nothing asserts that a rule is narrow (finding 1) or that Claude Code accepts any rule (finding 2).

## 1. Shape

shape_change: no. Breadth: narrow, as forecast.
- The code adds three constants and two functions (`scripts/run.py:706-743`) and two lines in `cmd_init` (`:795-796`). `.xv/picture.md:22` already puts `init` in `run.py`.

## 2. Pitch

pitch_contradiction: no.
- I checked `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code").

## 3. Moved tests

None.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

- Under `tests/`, `git log f452d43..HEAD` shows two commits, both "red": `c8b8006` adds `test_init_allow_list.py` and `7f5bafa` adds `test_init_allow_list_split.py`. Neither file is touched after its red commit.
- Their sha256 today matches the wall baseline in `.xv/slices/2026-10-25-init-allow-list.wall.json`: `05867476…` and `c50ed098…`.

## 4. The picture

- `.xv/picture.md:25` says "`defaults/` is the starter `.xv/` that `xv init` copies". It is now incomplete. Proposed addition: "`xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian lines, built from the detected test commands, so the written `config.yml` differs from `defaults/config.yml`." This was proposed last time and picked at the accept stop. It is not in the worktree's picture yet.
- `.xv/picture.md:20`, proposed addition: "Claude Code seats start with a Bash allow list; other harnesses' lines are left as written."
- `.xv/picture.md:69` ("Read-only agents are checked, not trusted") stays true as written. Finding 1 is where the change strains it.

## Door

**Door:** two-way. A revert removes the writer, but configs already written by `xv init` keep their lists until someone edits them. **Blast radius:** adopters.

## Raw data

- Slice record: `.xv/slices/2026-10-25-init-allow-list.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`. The code is all in `scripts/run.py`; the CHANGELOG line is `CHANGELOG.md:7`.
- Wall: `.xv/slices/2026-10-25-init-allow-list.wall.json` and `checks.maker.wall` and `checks.cleaner.wall` in the record. `xv wall diff 2026-10-25-init-allow-list` was refused here.
- Boundary: `.xv/slices/2026-10-25-init-allow-list.boundary.md`
- Run logs: `.git/xv/runs/2026-10-25-init-allow-list/`

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The boundary picture has no shape hints. Its only touched module is `scripts/run`, and it adds or removes no edge, table or surface.
- The diff grew from 227 to 829 lines (the record's `diff_growing` stop). Most of that is slice files under `.xv/slices/`. Code and tests are 244 lines (`checks.cleaner.diff_lines`).
- The forecast expected moved init tests. None moved.
- A starter permission list serves discipline. The pitch is silent on how wide the list may be. Finding 1 cuts against a binding decision in the picture, not against the pitch.
- The maker's and the cleaner's wall checks in the record show `changed: []`, `fewer_assertions: []` and `unrecorded: []`.
- `xv wall diff` was refused in this session, the same as last time.

## From the cleaner

- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers (allowed/entries_of, covers/rule_allows); a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.

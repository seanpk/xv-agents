---
slice: 2026-10-25-init-allow-list
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: adopters
---

# Packet: xv init writes a starter allow list (fourth pass)

No stop for two people. The merge is Sean's. Points 1 and 2 from the third accept stop are met. In this session, plain `xv wall diff` ran under this repo's rules, and the absolute path did not. Point 3 is only half met. Two findings need Sean's decision.

## Needs a decision (the person who set the work going)

1. **The test that always skips still always skips.** Sean's point 3 said to make `test_a_python_repo_gets_no_rule_for_other_runners` (`tests/test_init_allow_list_bare.py:76-87`) "run and assert". It is unchanged. It still touches `package.json` and still calls `self.skipTest("detection chose another runner: " + command)` (`:82-83`). In this session, `-v` shows "skipped 'detection chose another runner: npm test'", and the whole suite ends `OK (skipped=1)`. A new test does what the old one meant to: `test_a_python_repo_with_other_markers_gets_no_rule_for_other_runners` (`tests/test_init_allow_list_prompt.py:63-76`) adds `pyproject.toml` so that Python wins detection. It asserts and passes. The old test was probably left alone because editing it would count as a moved test. Sean can keep the dead test, delete it, or have it fixed. Any of these is a test move for Sean to accept.
2. **The CHANGELOG line does not mention the brief change or the prompt change.** "A change to a brief … needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:58`). This repo calls the `xv-init` skill a brief: `CHANGELOG.md:8` says "The `xv-init` brief names the new setting". This pass adds a step to that brief (`skills/xv-init/SKILL.md:32`, "If the person changes `tests.command`, change the test rules in each agent's `--allowedTools` …"). It also changes what `xv prompt` tells every agent on every harness (`scripts/prompt.py:78`, `xv = "xv" if shutil.which("xv") else …`). The slice's one line (`CHANGELOG.md:7`) covers neither.

Smaller, for Sean:
- **Plain `xv` relies on the agent's shell having it on the PATH.** `scripts/prompt.py:78` checks for `xv` on the PATH where `xv prompt` runs. The agent runs the command later, in the harness's own shell. If that shell's PATH is different (a login profile, or a CI step that sets PATH only for the watch), `xv` is not found. The absolute path never had this failure. No test covers this. The red only checks the name in the prompt (`tests/test_init_allow_list_prompt.py:53-61`).
- **The new step in the skill does not say how to write a rule.** `skills/xv-init/SKILL.md:32` tells the person to change the test rules but does not give Sean's limits. The scenario (`.xv/slices/2026-10-25-init-allow-list.md:36`) says: one rule per part, and never stop at a program name. If the person writes `Bash(python3:*)` by hand, that undoes the bare-name rule that `tests/test_init_allow_list_bare.py` protects. Nothing checks a list a person edits by hand.
- **Carried from the last packet, unchanged:** the guardian's test rule plus `acceptEdits` still lets it write a file that the test command then runs (`.xv/config.yml:36`, `scripts/run.py:736`). Claude Code's own reading of the `PYTHONPATH=src` rule is still untested (`scripts/run.py:718-726`).
- **This repo's own guardian line does not have the third `xv` rule.** Its `xv` rules are `Bash(xv record move:*)`, `Bash(xv wall diff:*)` and `Bash(xv boundary:*)` (`.xv/config.yml:36`). Starter configs now also get `Bash(xv packet lint:*)` (`scripts/run.py:709`). This repo's line is missing it, so `xv packet lint` asked for approval in this session. The slice does not touch this repo's config.
- The cleaner proposed, a third time, putting the duplicated test helpers in `tests/helpers.py`. `entries_of` is now defined in three places: `tests/test_init_allow_list_split.py:14`, `tests/test_init_allow_list_bare.py:15` and `tests/test_init_allow_list_prompt.py:15`.

## The scenario

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`. The default seat gets read-only commands, `git rm`, `git mv`, `xv record move` and the test rules. The forecaster gets the read-only list only. The guardian gets the read-only list, the test rules, `xv wall diff`, `xv boundary` and `xv packet lint`. Test rules come only from the chosen command, one per part, and never stop at a program name.

What Sean added at the third stop (2026-10-26):
1. `xv prompt` names plain `xv` when it is on the PATH.
2. The skill's test command step says to change the test rules when the person changes `tests.command`.
3. The always-skipping test must run and assert.

May ignore: other harnesses, and lint and type commands. (#16)

## The recording

None; this is a feature from words.

To replay the red: `cd tests && python3 -m unittest test_init_allow_list_prompt -v`. Before this pass it failed with "no starter rule matches `/tmp/…/bin/xv wall diff`". In this session it ran 3 tests, all OK.

A live check from this session, under this repo's guardian line (`.xv/config.yml:36`): `/home/sean/.local/bin/xv wall diff …` asked for approval, and `xv wall diff …` ran.

## The boundary picture

From `.xv/slices/2026-10-25-init-allow-list.boundary.md`, as given:
- Touched: `scripts/prompt` and `scripts/run`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

## What the suite asserts after

Whole suite: 143 tests, OK, 1 skipped (the test in finding 1). Run in this session.

Added in this pass:
- With `xv` on the PATH, the `xv` command that `xv prompt guardian` names, followed by `wall diff`, `boundary` or `packet lint`, matches a starter guardian rule.
- A repo with `tests/`, `pyproject.toml`, `package.json` and a `Gemfile` gets a Python command. Its default and guardian seats get no `npm`, `bundle` or `go` rule.
- The skill's test command step names `--allowedTools`.

Unchanged from the last pass:
- No rule is a bare program name.
- A Go repo with `tests/` gets no Python rule.
- `PYTHONPATH=src` gets a rule for the rest of the command.
- Every part of a compound command is covered, and single-file runs are covered.
- The read-only list is the wider one, and only the guardian gets the three `xv` rules.
- The CHANGELOG line is there.

Not asserted:
- `xv record move` for the default seat under the prompt's name.
- The case where `xv` is not on the PATH.

## 1. Shape

shape_change: no. Breadth: narrow, as forecast.
- This pass changes one line in `scripts/prompt.py:78`. `.xv/picture.md:23` already says `prompt` builds the agent calls.
- The rest of the code (`scripts/run.py:706-744`, `:796`) sits in `run.py`, where `.xv/picture.md:22` puts `init`.

## 2. Pitch

pitch_contradiction: no.
- I checked `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code").

## 3. Moved tests

`xv wall diff 2026-10-25-init-allow-list` since the baseline `9538f77`: changed, deleted and added are all empty, and `fewer_assertions` is empty. This pass moved no old test.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_init_allow_list_split.py:71` | Each subTest kept the files the earlier subTests created. | Each subTest starts with `git clean -fdxq`. Same assertions, 9 before and 9 after. | Rules now come only from the chosen command, so markers built up across subTests changed which runner was chosen. | Yes, by Sean's second-stop point 2. Sean accepted it at the third stop (`.xv/slices/2026-10-25-init-allow-list.md:38`). |

- Not moved, but asked for: `tests/test_init_allow_list_bare.py:76-87` (finding 1).

## 4. The picture

Sean accepted these at earlier stops, and the watch adds them at merge (`.xv/slices/2026-10-25-init-allow-list.md:38`). They are not in the worktree's picture yet:
- `.xv/picture.md:25` ("`defaults/` is the starter `.xv/` that `xv init` copies"). Add: "`xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian lines, built from the test command it chose. So the written `config.yml` differs from `defaults/config.yml`. If the person changes the test command, the `xv-init` skill says to change the test rules by hand."
- `.xv/picture.md:20`. Add: "Claude Code seats start with a Bash allow list; other harnesses' lines are left as written."
- `.xv/picture.md:69`, if Sean wants the cost written down. Add: "The guardian's starter allow list includes the test command, so its read-only status rests on the watch's write check."

New in this pass:
- `.xv/picture.md:23` (`agentcli` and `prompt` build and run the agent calls). Add: "`xv prompt` names `xv` plainly when it is on the PATH, so allow rules such as `Bash(xv wall diff:*)` match. Otherwise it names `$XV_HOME/bin/xv`."

## Door

**Door:** two-way. A revert removes the writer and the prompt change. Configs that `xv init` has already written keep their lists until someone edits them. **Blast radius:** adopters.

## Raw data

- Slice record: `.xv/slices/2026-10-25-init-allow-list.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`. This pass is `129adfd..686cc1a`: `scripts/prompt.py`, `skills/xv-init/SKILL.md` and the new `tests/test_init_allow_list_prompt.py`. There are no uncommitted changes except the regenerated boundary file.
- Wall: `xv wall diff 2026-10-25-init-allow-list` (baseline `9538f77`). Also `checks.maker.wall` and `checks.cleaner.wall` in the record.
- Boundary: `.xv/slices/2026-10-25-init-allow-list.boundary.md`
- Run logs: `.git/xv/runs/2026-10-25-init-allow-list/`

## From the cleaner

- Shape proposal, for people: `tests/test_init_allow_list*.py` duplicate the helpers that parse the allowed tools and match the rules (`entries_of`, `rule_allows` and their twins). A shared helper in `tests/helpers.py` would remove the duplication. It is a new shared piece, so the cleaner left it for the packet.

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The boundary picture shows no new edges, tables or surfaces, and no shape hints.
- Naming `xv` plainly and adding a step to a skill fall inside all three. The pitch says nothing about permission lists.

## From the cleaner

- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers (allowed/entries_of, covers/rule_allows); a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.
- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers; a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.
- Shape proposal, for people: tests/test_init_allow_list*.py duplicate the allowed-tools parsing and rule-matching helpers (entries_of, rule_allows and their twins); a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.

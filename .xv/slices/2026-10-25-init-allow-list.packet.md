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

# Packet: xv init writes a starter allow list (third pass)

No stop for two people. The merge is Sean's. All four points from the second accept stop are met in the code. Two findings need Sean's decision first. The first one matters most: the `xv` rules do not match the way `xv prompt` tells agents to call `xv`.

## Needs a decision (the person who set the work going)

1. **The `xv` rules never match how agents call `xv`.** The starter rules are `Bash(xv record move:*)`, `Bash(xv wall diff:*)`, `Bash(xv boundary:*)` and `Bash(xv packet lint:*)` (`scripts/run.py:708-709`, `MAKER_TOOLS` and `GUARDIAN_TOOLS`). But `xv prompt` gives agents an absolute path: `xv = shutil.which("xv") or os.path.join(XV_HOME, "bin", "xv")` and then "The `xv` command: `{xv}`" (`scripts/prompt.py:78-79`). This run's prompt says "The `xv` command: `/home/sean/.local/bin/xv`". So the agent runs `/home/sean/.local/bin/xv wall diff …`, and no `Bash(xv …:*)` prefix matches it. That happened in this session: `xv wall diff` was refused, even though this repo's `.xv/config.yml:36` carries `Bash(xv wall diff:*)`. The last guardian's packet also reports `xv wall diff` refused. The maker's `xv record move` should fail the same way. The scenario promises that an agent can run commands "as `xv prompt` gives it". No test runs a rule against a command that `xv prompt` writes.
2. **The allow list does not follow a test command the person changes.** `allow_lists` runs once, on the command `xv init` chose (`scripts/run.py:796`, `text = allow_lists(text, command)`). Next, the skill asks the person to pick the command when there is more than one runner: "one, several joined with `&&`, or a script" (`skills/xv-init/SKILL.md:32`). One example is a Rails app that picks `bundle exec rspec && npm test`, or a repo that picks a script. Either way the agents get no rule for the new parts, and the skill says nothing about the allow list. Sean narrowed the rules to the chosen command on purpose. That makes this gap the only path to a working list in a repo with more than one runner. The skill, the code or neither could close it. That choice is Sean's.

Smaller, for Sean:
- **A new test never runs.** `test_a_python_repo_gets_no_rule_for_other_runners` (`tests/test_init_allow_list_bare.py:76-87`) touches `tests/`, `src/` and `package.json`. Detection then picks `npm test`, because `package.json` is the only marker and `tests/` counts as its folder (`scripts/run.py:614-615`). So the test always skips. This session ran the red with `-v` and got: "skipped 'detection chose another runner: npm test'". The suite's `OK (skipped=1)` is this test. It asserts nothing.
- **A rule that is not a bare name can still run anything.** The bare-name test checks names against a list (`tests/test_init_allow_list_bare.py:10-11`, `RUNS_ANYTHING`), not what each rule can reach. The guardian keeps the test rule (`scripts/run.py:736`) and runs with `--permission-mode acceptEdits` (`.xv/config.yml:36`). So it can write a file that `python3 -m unittest`, `npm test` or `go test` then runs. "Read-only agents are checked, not trusted" (`.xv/picture.md:69`) still holds, but the watch's write check enforces it, not the allow list. Sean chose to give the guardian the test command. This only names what that choice costs.
- **Claude Code's handling of the `PYTHONPATH=src` rule is untested.** `test_rules` writes two rules for a leading `NAME=value`: `PYTHONPATH=src python3 -m unittest` and `python3 -m unittest` (`scripts/run.py:718-726`). The test checks that some rule exists for the rest (`tests/test_init_allow_list_bare.py:89-103`). It does not check that Claude Code accepts the full command under either rule. Sean allowed either a rule or a note in the skill. The maker chose the rule, and no skill changed.
- The cleaner proposed again that the helpers duplicated across the three allow-list test files go into `tests/helpers.py`. `entries_of` appears in both `tests/test_init_allow_list_split.py:14` and `tests/test_init_allow_list_bare.py:15`. The cleaner left it, because a shared helper is a new shared piece.

## The scenario

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`. The default seat gets read-only commands, `git rm`, `git mv`, `xv record move` and the test command's rules. The forecaster gets the read-only list only. The guardian gets the read-only list, the test rules, `xv wall diff`, `xv boundary` and `xv packet lint`.

At the second accept stop (2026-10-26), Sean added:
1. No rule stops at a program name.
2. Rules come only from the chosen test command.
3. A leading `NAME=value` gets a rule for the rest of the command, or a note in the skill.
4. Fix the stale comment at `tests/test_init_allow_list.py:97`.

May ignore: other harnesses, and lint and type commands. (#16)

## The recording

None; this is a feature from words. To replay the red: `cd tests && python3 -m unittest test_init_allow_list_bare -v`. In this session it ran 4 tests: 3 OK and 1 skipped (see above). The red's watch-first: run `xv init` in a scratch repo with `src/` and `tests/`, then in a Go repo with `tests/`. To replay finding 1: run any agent step and look for a refused `/…/bin/xv wall diff` or `/…/bin/xv record move` in the run log.

## The boundary picture

From `.xv/slices/2026-10-25-init-allow-list.boundary.md`, as given:
- Touched: `scripts/run`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

## What the suite asserts after

Whole suite: 140 tests, OK, 1 skipped. Run in this session.
- In each layout (Python, Python with `src/`, Go, Go with `tests/`, Ruby, Node, empty), no seat's rule is a bare runner name such as `python3`, `go`, `npm` or `bundle`.
- A Go repo with a `tests/` folder gets `go test` as its command and no `python`, `bundle` or `npm` rule.
- With `src/`, some rule covers the command without `PYTHONPATH=src`, for the default seat and the guardian.
- Every `&&`, `||` or `;` part of the detected command is covered.
- In single-runner repos, single-file runs for rspec, go and unittest are covered.
- Every seat gets the wider read-only list, and only the guardian gets the three `xv` rules.
- `CHANGELOG.md` names the change under Unreleased.
- Not asserted: a Python repo that also has `package.json` (the test skips), and any rule matching a command `xv prompt` writes.

I traced `test_rules` by hand on the detection table's other commands (`scripts/run.py:608-616`). `cargo test` gives `cargo test`. `python3 -m pytest -q` gives `python3 -m pytest`. `bundle exec rake test` gives `bundle exec rake test`. None is a bare name.

## 1. Shape

shape_change: no. Breadth: narrow, as forecast.
- The code adds three constants and two functions (`scripts/run.py:706-744`) and one call in `cmd_init` (`:796`). `.xv/picture.md:22` already puts `init` in `run.py`. The boundary picture shows no shape hints, and no new edges, tables or surfaces.

## 2. Pitch

pitch_contradiction: no.
- I checked `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code"). A starter permission list fits all three. The pitch says nothing about how wide the list may be.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_init_allow_list_split.py:71` | Each subTest kept the files the earlier subTests created. | Each subTest starts with `git clean -fdxq`. No assertion changed; 9 before, 9 after (`checks.maker.wall`). | Rules now come only from the chosen command. Gemfile, `go.mod` and `tests/` built up across subTests, so detection chose `bundle` and the go and unittest cases could not pass. | Yes, by Sean's point 2. The test no longer covers a repo with several runners, but Sean removed that behaviour. It does not assert less about what remains. |

- The scenario agent also edited `tests/test_init_allow_list.py:97-98` in the red commit `52dd4d9`. This was Sean's point 4, and only the comment changed. The wall baseline was taken after it, so `xv wall diff` does not list it.

## 4. The picture

- `.xv/picture.md:25` says "`defaults/` is the starter `.xv/` that `xv init` copies". That is now incomplete. Proposed addition: "`xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian lines, built from the test command it chose, so the written `config.yml` differs from `defaults/config.yml`. Changing the test command later does not change the list." Sean picked this at both earlier accept stops. It is not in the worktree's picture yet.
- `.xv/picture.md:20`, proposed addition: "Claude Code seats start with a Bash allow list; other harnesses' lines are left as written."
- `.xv/picture.md:69`, proposed addition, if Sean wants the cost written down: "The guardian's starter allow list includes the test command, so its read-only status rests on the watch's write check."

## Door

**Door:** two-way. A revert removes the writer, but configs already written by `xv init` keep their lists until someone edits them. **Blast radius:** adopters.

## Raw data

- Slice record: `.xv/slices/2026-10-25-init-allow-list.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`. The code is all in `scripts/run.py`; the CHANGELOG line is `CHANGELOG.md:7`.
- The cleaner's report says its edit is uncommitted (`checks.cleaner.committed: false`), but the edit is in HEAD at `67c045c`, "record the cleaner's pass". The content matches the report.
- Wall: `.xv/slices/2026-10-25-init-allow-list.wall.json` (baseline `7ae36ed`), and `checks.maker.wall` and `checks.cleaner.wall` in the record.
- Boundary: `.xv/slices/2026-10-25-init-allow-list.boundary.md`
- Run logs: `.git/xv/runs/2026-10-25-init-allow-list/`

## From the cleaner

- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers. A shared helper in tests/helpers.py would remove the duplication, but it is a new shared piece, so the cleaner left it for the packet.

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- `xv wall diff` was refused in this session (finding 1). The table comes from `checks.maker.wall` and `checks.cleaner.wall` in the record: one file changed, recorded, `fewer_assertions: []`, `unrecorded: []`.

## From the cleaner

- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers (allowed/entries_of, covers/rule_allows); a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.
- Shape proposal, for people: tests/test_init_allow_list.py and tests/test_init_allow_list_split.py duplicate the allowed-tools parsing and rule-matching helpers; a shared helper in tests/helpers.py would remove it, but it is a new shared piece, so it is left for the packet.

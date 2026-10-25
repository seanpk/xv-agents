---
shape_change: no
pitch_contradiction: no
---

# Packet: xv init writes a starter allow list

## Needs a decision (the person who set the work going)

1. **The scenario's last sentence has no test, and the change only partly meets it.** The scenario says "A headless agent with the starter config can run the test command as `xv prompt` gives it." `xv prompt` gives an agent two commands: the whole suite (`scripts/prompt.py:71`) and the red (`scripts/prompt.py:64`). The allow list covers only the suite command, as one literal prefix:
   `scripts/run.py:712` `test = [command] if command else []`
   `scripts/run.py:717` `tools = ",".join(f"Bash({t}:*)" for t in seats[seat])`
   The red command is written by the scenario agent and need not start with the suite command. This slice's own red, `cd tests && python3 -m unittest test_init_allow_list`, would not match `Bash(python3 -m unittest discover -s tests -t .:*)`. Narrower runs fail too: `go test ./pkg/x` does not match `Bash(go test ./...:*)`. The tests check this with a string-prefix helper (`tests/test_init_allow_list.py:22-29`, `covers`). Claude Code matches a rule against each part of a compound command, so a string-prefix check proves nothing about what a headless agent can actually run. This repo's own hand-made config allows `Bash(cd tests:*)` and `Bash(python3 -m unittest:*)` as two separate rules (`.xv/config.yml:34`). The watch's `watch_first_green` asked exactly this question ("Check that the test command is allowed in a form a headless agent could actually run"). Nobody tested it.
   - Not tested (plausible): with a `src/` layout, the detected command starts with `PYTHONPATH=src ` (`scripts/run.py:627,637`). The rule becomes `Bash(PYTHONPATH=src python3 -m unittest discover -s tests -t .:*)`. Whether Claude Code matches a rule that starts with an env-var assignment was not checked.
2. **The guardian's starter list leaves out commands its own brief tells it to run.** The guardian seat gets `READ_ONLY_TOOLS + test` (`scripts/run.py:713-714`). The guardian brief tells it to run `xv wall diff <id>`, and `xv boundary` and `xv packet lint` are the guardian's checks (`.xv/picture.md:23`). This repo's own config adds `Bash(xv wall diff:*)` and `Bash(xv boundary:*)` to the guardian (`.xv/config.yml:36`). This guardian run was itself refused `xv wall diff`. The scenario asked for "only the read-only part, plus the test command", so the maker followed the words. The gap is in the scenario, not the code.
3. **The read-only list is shorter than the one this repo uses.** `READ_ONLY_TOOLS` (`scripts/run.py:706`) leaves out `rg`, `wc`, `sed -n`, `diff`, `git ls-files`, `git grep` and `git rev-parse`, which `.xv/config.yml:34-36` allows. In a headless run, each missing command is a refused tool call.

None of these stops the change for two people.

## The scenario in words

`xv init` writes a starter `--allowedTools` list into each Claude Code agent line of `.xv/config.yml`:
- the default seat gets read-only shell and git commands, `git rm`, `git mv`, `xv record move` and the detected test command;
- the forecaster gets the read-only part only;
- the guardian gets the read-only part plus the test command.

Out of scope: other harnesses, and lint and type commands. (seanpk/xv-agents#16)

## Recording / replay

There is no recording; the scenario is written in words. To replay: in a scratch repo with no `.xv/`, run `xv init`, then read lines 34-36 of `.xv/config.yml`. To see the gap in finding 1, try running the red command form (`cd tests && python3 -m unittest <file>`) under `claude -p` with that config.

## Boundary picture

`.xv/slices/2026-10-25-init-allow-list.boundary.md` (from `xv boundary`): one module touched, `scripts/run`. Modules, edges, outbound calls, tables and surface paths: none added or removed. Shape hints: none.

## What the suite asserts after the change

- The default agent line has `--allowedTools` with each read-only and maker entry as `Bash(<prefix>:*)`, and some entry is a string prefix of the detected test command.
- The forecaster's list has the read-only entries, no maker entries, and no entry covering the test command.
- The guardian's list has the read-only entries, no maker entries, and covers the test command.
- With a `Gemfile` and `spec/`, the detected command is `bundle exec rspec`, and both the default and guardian lists cover it.
- Commented-out non-Claude example lines get no `--allowedTools`.
- Nothing asserts that a real Claude Code permission check accepts the command, or that the red command is covered (finding 1).

The suite was green in the watch's runs (131 tests, maker and cleaner steps in the record). I could not run it myself: the command was refused in this session.

## Moved tests

None. `git diff --stat f452d43..HEAD` under `tests/` shows one new file, `tests/test_init_allow_list.py`, and `git diff c8b8006..HEAD -- tests` is empty, so the red was not touched after it was written. The record's wall check from both the maker and the cleaner reports `changed: [] deleted: [] fewer_assertions: [] unrecorded: []` and `ok: true`. `moved_tests: []` in the record. The forecast expected moved init tests; none moved.

## The four checks

**1. Shape: no. Breadth: narrow (matches the forecast's `narrow`).**
- The boundary picture shows no new module, edge, table, outbound call or surface path, and no shape hints. The diff adds two constants and a function to `scripts/run.py` (`scripts/run.py:706-722`) and one call in `cmd_init` (`scripts/run.py:774`). `.xv/picture.md:22` already places `init` in `run.py`.
- The written config is something adopters read, but the picture's surfaces list (`.xv/picture.md:27`) names the CLI, the skills and CI, not the config's contents. Adding a flag inside the existing agent lines stays inside the current shape.
- Reach: the change touches every new adopter's starter config, the same reach as `defaults/` (`.xv/picture.md:25`). It applies only when `config.yml` is freshly written (`scripts/run.py:765`), so existing configs are left alone.

**2. Pitch: no contradiction.**
- Checked against `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `.xv/pitch.md:21` (teams and non-technical people) and `.xv/pitch.md:25` (not for people who will not trust agents to write production code). Narrowing what headless agents may run serves discipline and contradicts no line.
- Also checked the binding decisions: `.xv/picture.md:60` (standard library only: the change uses only `json`, already imported), `.xv/picture.md:66` (values stay JSON in YAML: `json.dumps(tools)` at `scripts/run.py:718`), and `.xv/picture.md:47` (any harness must stay possible: lines that are not Claude are skipped, `scripts/run.py:716`).

**3. Moved tests:** none (see above).

**4. The picture: needs a small edit.**
- `.xv/picture.md:25` says `defaults/` is the starter `.xv/` that `xv init` copies. Proposed addition: "`xv init` also writes a starter Claude Code `--allowedTools` list onto the default, forecaster and guardian agent lines, built from the detected test command, so the written `config.yml` differs from `defaults/config.yml`."
- `.xv/picture.md:20` could note: "Claude Code seats start with a narrow Bash allow list. Other harnesses' lines are left as written."

## The door

Two-way door: a revert removes the writer. Configs already written by `xv init` keep their lines, and adopters can edit them. Blast radius: **adopters** (new inits only).

## Raw data

- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD`. Code is in `scripts/run.py` only.
- Boundary: `.xv/slices/2026-10-25-init-allow-list.boundary.md`
- Wall: `.xv/slices/2026-10-25-init-allow-list.wall.json`, plus the `checks.maker.wall` and `checks.cleaner.wall` fields in the record. `xv wall diff` was refused in this session.
- Red and suite output: `checks.scenario.red_output`, `checks.maker.suite_output` and `checks.cleaner.suite_output` in the record.
- Run logs: `.git/xv/runs/2026-10-25-init-allow-list/`

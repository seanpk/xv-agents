---
slice: 2026-10-25-init-tries-guesses
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: init
---

# Packet: xv init tries its guessed test command and roots

Nothing stops this for two people. Four findings go to Sean, who set the work going and decides on the merge. They are listed from most to least needing a decision:

1. **Does `xv-init` count as a brief?** The skill gains a may-not line, "do not fix it yourself" (`skills/xv-init/SKILL.md:32`). Decision 1 says "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:58`). The diff does not touch `CHANGELOG.md`. The picture lists `xv-init` among the five person-facing skills, not the seven agents (`.xv/picture.md:11`). If you count it as a brief, it needs a CHANGELOG line.
2. **The fixture scan walks the disk, not git.** It can list folders that git ignores, such as `.venv` or a nested `node_modules`.
3. **A test assertion caused a field to be dropped.** `tests.timeout` no longer appears in init's output, and the scenario did not ask for that.
4. **The skill does not cover two outcomes:** `test_run: null`, and a run that blocks for up to 900 seconds.

## The scenario

`xv init` runs the test command it chose once, with a time limit. Its output says whether the command passed, failed (with the last lines of its output), or timed out. The output also gives the number of modules in `.xv/boundary-all.md` and lists any folder that looks like a fixture (named `fixture`, `fixtures`, `examples` or `setups`, and holding code). The skill tells the person about each. (seanpk/xv-agents#14)

May ignore: fixing a failed command automatically.

## The recording

This is a feature, so there is no recording. To replay:

- Red at `5f42e9e`, green at `HEAD`: `cd tests && python3 -m unittest test_init_tries`.
- At `HEAD` it ran 5 tests and all passed (run by the guardian).
- The record's red failure: `Regex didn't match: 'fail' not found in '{ "written": [...], "kept": [], "tests": {...} }'`.
- The timed-out outcome is not covered by any test. The scenario names no way to shorten the limit (record, `watch_first_green`).

## The boundary picture

From `.xv/slices/2026-10-25-init-tries-guesses.boundary.md`, as given:

- **Modules touched:** `scripts/run`. None added or removed.
- **Edges:** none added, none removed. **Outbound added:** none.
- **Tables:** none.
- **Surface paths:** added `/x`. None removed.
- **Shape hint:** "a surface path was added or removed". Check 1 explains why this is not a real surface.

## What the suite asserts after

All five tests are new, in `tests/test_init_tries.py`:

- When the guessed command passes, the output says "pass" and contains none of `fail`, `timed out` or `timeout`.
- When one test fails, `xv init` still exits 0. The output says "fail" and contains the failing test's marker text, which comes from the tail.
- The output gives a number next to "module", and it equals the count of `- ` lines in `.xv/boundary-all.md`.
- `examples/` and `fixtures/` folders that hold `.py` files are named. A `setups/` folder that holds only `.txt` is not named.
- A repo with no fixture-like folder names none.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast's `"shape": "narrow"` (record front matter).

- **Hint "a surface path was added", `/x`:** this does not change the shape. It is a false positive from a string literal used for glob matching, not a route: `scripts/run.py:714-715` `dirs[:] = sorted(d for d in dirs if d not in (".git", XV_DIR)` / `and not match_any(os.path.normpath(os.path.join(rel_dir, d)) + "/x", exclude))`.
- **Modules and edges:** only `scripts/run` is touched, and no edges or outbound calls were added (boundary picture). Running a shell command from `run.py` is not new: `scripts/run.py:43` `def shell(cmd, cwd, timeout=900, env=None)` already backs `run_suite`. "`init` ... all land in `run.py`" (`.xv/picture.md:22`) stays true.
- **Surfaces:** `xv init`'s JSON gains `test_run`, `modules` and `fixture_folders`, and `tests` loses `timeout` (`scripts/run.py:796-801`). `skills/xv-init/SKILL.md:32,34` change wording. Both are existing surfaces, "the `xv` CLI, `skills/*/SKILL.md`" (`.xv/picture.md:27`), so this is within the current shape. `defaults/` is untouched (`.xv/picture.md:25`).
- **Possible brief change, for Sean (see finding 1 above):** `skills/xv-init/SKILL.md:32` adds "if it failed or timed out, show the tail and ask about the command, and do not fix it yourself". Decision 1 (`.xv/picture.md:58`) requires two people and a `CHANGELOG.md` line for a change to "a brief, a may-not list". The diff has no `CHANGELOG.md` change (`git diff --stat` lists 5 files, and `CHANGELOG.md` is not one).
  - `scripts/run.py:712` `for dirpath, dirs, _ in os.walk(root):` and `:717` `if any(f.endswith(CODE_EXTS) for _, _, fs in os.walk(dirpath) for f in fs):` walk every folder on disk.
  - The boundary lists files with `git ls-files ... --exclude-standard` (`scripts/boundary.py:194`), so it never sees folders that git ignores.
  - The default exclude is `["node_modules/**", "vendor/**", ".git/**", ".xv/**"]` (`defaults/config.yml:27`). It has no `.venv`, `build` or `dist`. `match_any` is plain `fnmatch` (`scripts/xvlib.py:328`), so `node_modules/**` does not match `packages/web/node_modules/...`.
  - Failure case: a Python repo with a `.venv/`, or a monorepo with nested `node_modules`. Any installed package that has an `examples/` or `fixtures/` folder with code shows up in `fixture_folders`. The skill then says "tell the person about each and ask whether it belongs in `source.exclude`" (`skills/xv-init/SKILL.md:34`), which asks about folders the boundary already ignores. No test covers an ignored folder.

## 2. Pitch

pitch_contradiction: no.

The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo" (`.xv/pitch.md:7`). Checking the guessed command and roots at init serves that. Nothing in the change touches who it is for (`.xv/pitch.md:21`) or what it will never do (`.xv/pitch.md:25`).

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

  - `tests/test_init_tries.py` hashes to `c1bf0848…`, the same as in `.xv/slices/2026-10-25-init-tries-guesses.wall.json:43`.
  - `tests/test_init_tries.py:30` `self.assertNotRegex(out, r"fail|timed out|timeout")` also matches the config key `"timeout": 900` that init used to print.
  - To pass it, the maker stopped printing it: `scripts/run.py:796` `out = {..., "tests": {k: v for k, v in tests.items() if k != "timeout"}}`.
  - The scenario asks for nothing to be removed from the output. No other test or skill reads `tests.timeout` from init's output (grep of `tests/*.py`, `skills/*/SKILL.md` and `README.md` found none). So the cost is small, but the output lost a field because an assertion was too broad.

## 4. The picture

No edit proposed.

  - The module count and list (`.xv/picture.md:21`) are unchanged: no module was added.
  - "`init` ... land in `run.py`" (`.xv/picture.md:22`) is still true.
  - Outbound calls (`.xv/picture.md:24`): the boundary shows none added.
  - `defaults/` (`.xv/picture.md:25`) is untouched.
  - Surfaces (`.xv/picture.md:27`) are the same set.
  - Names, users and decisions (`.xv/picture.md:13-17, 30-37, 55-74`) are not made untrue.
- **Optional:** if Sean wants the picture to record that `xv init` now runs the adopter's test command once, it would fit as a clause on `.xv/picture.md:22`. Nothing currently in the picture is wrong without it.

## 5. Usability (not requested; same evidence rule)

  - `scripts/run.py:726-727` `timeout = int(tests.get("timeout") or 900)` / `code, text = shell(command, root, timeout)`, with `timeout: 900` the default (`defaults/config.yml:23`).
  - The run happens on every `xv init`, including a re-run where `config.yml` was kept.
  - On a repo whose suite is slow, a person waits up to 15 minutes in silence. The skill's advice for that case ("A big suite", `skills/xv-init/SKILL.md:33`) only comes after init returns.
  - `scripts/run.py:723-725` returns `None` when no command was guessed.
  - The skill names only "`passed`, `failed` ... or `timed out`" (`skills/xv-init/SKILL.md:32`), so an agent running the skill has no instruction for null.
  - Decision 12 says a check that cannot run "stops for a person; it never passes" (`.xv/picture.md:69`). Null does not pass, but nothing tells the agent to raise it.

## Door

**Door:** two-way. Reverting the commit removes the output fields and the skill text, and no data is migrated. **Blast radius:** init.

## Raw data

- Slice record: `.xv/slices/2026-10-25-init-tries-guesses.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..HEAD` (5 files: `scripts/run.py`, `skills/xv-init/SKILL.md`, `tests/test_init_tries.py`, and the record and wall files)
- Wall: `xv wall diff 2026-10-25-init-tries-guesses` (baseline in `.xv/slices/2026-10-25-init-tries-guesses.wall.json`)
- Boundary: `.xv/slices/2026-10-25-init-tries-guesses.boundary.md` (`xv boundary --base f452d430f44f`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The fixture scan does not match how the boundary sees the repo.**
- What I compared:**
- The record has `moved_tests: []`.
- The maker's and cleaner's wall checks show `changed: []`, `deleted: []`, `added: []`, `fewer_assertions: []`, `unrecorded: []` against baseline `dae3f44`.
- `git diff --stat 5f42e9e..HEAD -- tests` is empty.
- I could not run `xv wall diff` myself because the command needed approval. The comparison above uses the watch's recorded wall checks and the hash instead.
- A new test that shaped the code beyond the scenario, for Sean:**
- What I looked at:**
- `xv init` can block for up to `tests.timeout` before printing anything.**
- `test_run: null` is not covered by the skill.**

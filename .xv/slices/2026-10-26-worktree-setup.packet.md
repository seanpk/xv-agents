---
slice: 2026-10-26-worktree-setup
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: A slice starts from the right base, and the project sets up its worktree

Nothing stops this for two people. Sean, as the person who set the work going, decides three things: the new default base can skip a `.xv/` that is committed but not pushed (finding 1.1); the default config's teardown example cannot work as written (1.2); and whether `setup_failed` sits with decision 10 (4.3). After that, the merge is his.

## The scenario

`.xv/config.yml` gains a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new <id> --base <ref>` starts the slice branch from that ref. Without the flag it uses `worktrees.base`. With neither, it uses `origin/HEAD`, or HEAD when there is no remote. The record's `base` is that commit. `setup` runs in the new worktree before the forecaster, with `{worktree}` replaced by its path. A non-zero exit is a stop for the originator, and the question quotes the command's last lines. `teardown` runs the same way when the slice closes. `xv check` lists both commands, and `defaults/config.yml` shows the block commented out. (seanpk/xv-agents#27; Sean approves the new stop, solo.)

May ignore: `worktrees.path`, and removing the worktree itself.

## The recording

None; this is a feature. To replay the red and the green: `cd tests && python3 -m unittest test_worktree_setup`. At the base, 10 of the 12 tests fail (`red_output` in the record). At HEAD, all 12 pass, and the whole suite passes 179 tests (`checks.cleaner.suite_output`).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-26-worktree-setup.boundary.md`), as given:

- Modules touched: `scripts/check`, `scripts/run`, `scripts/xvlib`. None added, none removed.
- Edges added: none. Edges removed: none. New outbound calls: none.
- Tables: none. Surface paths: none added or removed.
- Shape hints: none.

The diff also touches `defaults/config.yml` (comments only), `CHANGELOG.md` (one line) and the new `tests/test_worktree_setup.py`.

## What the suite asserts after

- `--base <ref>` makes that ref the record's `base` and the branch's parent. `worktrees.base` is used without the flag, and the flag beats the config.
- With neither, and with a remote whose `origin/HEAD` is behind the local HEAD, the base is `origin/HEAD`. With no remote, the base is HEAD.
- `setup` runs with the worktree as its working directory, with `{worktree}` filled in, and before any agent spend is recorded.
- A failing `setup` leaves exactly one open stop for the `originator`, whose question contains the command's stderr, and status `stopped`.
- `teardown` runs at close with the worktree's path. A slice with no teardown still closes.
- `xv check` prints both commands.
- `defaults/config.yml` has the commented `worktrees:`, `base:`, `setup:` and `teardown:` lines.
- No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `shape: "narrow"`. The forecast listed `xv slice new (--base, setup stop), teardown on close, xv check listing, defaults/config.yml and their tests`, and the diff touches exactly those, plus `CHANGELOG.md`.

- **No new module, edge, table or surface path.** The boundary picture's "Shape hints: none" and "Edges added: none" match the shape at `.xv/picture.md:21` ("22 modules … 54 edges"). `check` now imports `worktrees_config` from `xvlib` (`scripts/check.py:24`). That edge already exists (`scripts/check --> scripts/xvlib`).
- **Running a configured shell command is not new.** `scripts/run.py:187` runs `subprocess.run(command, shell=True, cwd=wt, …)`. `tests.command` already runs that way (`scripts/run.py:45`, `shell=True`). This stays inside the shape.
- **New config keys and a new flag on an existing command.** These are `worktrees.{path,base,setup,teardown}` (`scripts/xvlib.py:296-299`) and `--base` (`scripts/run.py:934`). The surfaces stay the ones listed at `.xv/picture.md:27` ("the `xv` CLI"), so this is not a new surface. The old scalar `worktrees: <path>` still reads the same (`scripts/xvlib.py:298`, `{"path": w}`).

Findings inside the shape:

**1.1 The guard checks that `.xv/` is committed to HEAD, but the branch now starts from `origin/HEAD`.** `scripts/run.py:204-206` still refuses only when `.xv/` is uncommitted, and its message says "the slice branch starts from HEAD". Then `scripts/run.py:210` uses `base = resolve_base(root, a.base or wcfg.get("base"))`, which picks `refs/remotes/origin/HEAD` when it exists (`scripts/run.py:174-177`). A concrete case: an adopter runs `xv init`, commits `.xv/`, does not push, and runs `xv slice new`. The worktree is made from `origin/HEAD`, which has no `.xv/config.yml`, pitch or picture. The record is written into it, but nothing the agents check against is there. I read this from the code. I could not replay it, because this session may not run ad-hoc scripts. No test covers it: `tests/test_worktree_setup.py:50-60` pushes everything before the extra commit, and that commit is an empty `later` commit. The scenario asked for `origin/HEAD`. What the guard and its message should say is the originator's call.

**1.2 The default teardown example cannot work as written.** `defaults/config.yml:24` reads `#   teardown: "docker compose -p {worktree} down"`. `{worktree}` becomes an absolute path (`scripts/run.py:186`), and Docker Compose rejects a project name that starts with `/`. A teardown failure only prints to stderr (`scripts/run.py:583-586`), and `xv close` carries on. An adopter who uncomments the example gets a close that looks clean and a compose project left running. `defaults/` reaches every new adopter (`.xv/picture.md:25`, "A change there reaches every new adopter").

**1.3 `{worktree}` is substituted without shell quoting.** At `scripts/run.py:186`, `command.replace("{worktree}", wt)` goes straight into `shell=True`. A repo path with a space splits into two arguments. The tests use `/tmp/xv-test-…` paths, which have no spaces (`tests/helpers.py:26`).

**1.4 Setup has no timeout.** `scripts/run.py:187` has none, while the suite runner passes `timeout=timeout` (`scripts/run.py:45`). A setup that hangs (`npm ci` with no network, for example) hangs `xv slice new` with no stop raised.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo"), `:21` (who uses it) and `:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot."). Starting slices from the shared branch and setting up each worktree serves `:7`. The change serves no one `:21` and `:25` exclude, and it breaks no promise.

## 3. Moved tests

None. `xv wall diff 2026-10-26-worktree-setup` against baseline `f58c9a3` reports `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []`. The record has `moved_tests: []`. `git diff 3ca97d4..HEAD --stat -- tests/` shows only the new `tests/test_worktree_setup.py` (126 lines), which the scenario agent wrote as the red.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

## 4. The picture

- **`.xv/picture.md:26`** ("Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`"). This is now incomplete. Proposed addition: "The branch starts from `--base`, else `worktrees.base`, else `origin/HEAD`, else HEAD. `worktrees.setup` runs in the new worktree before the forecaster, and `worktrees.teardown` runs at close." Source: `scripts/run.py:172-178`, `:243`, `:583`.
- **`.xv/picture.md:25`** (`defaults/` … "`xv init` also writes …"). This is incomplete. Proposed addition: "`worktrees:` may be a path or a block (`path`, `base`, `setup`, `teardown`). The default shows the block commented out." Source: `defaults/config.yml:14-24`, `scripts/xvlib.py:296-299`.
- **4.3 `.xv/picture.md:67`** ("The standing orders all live in `scripts/orders.py`, a pure function of the record and the config"). The new `setup_failed` stop is raised in `scripts/run.py:248`, not in `orders.py`. One stop already does the same: `axis_not_named` at `scripts/prototypes.py:85`. The originator chooses one of two edits. Either the decision is reworded so that stops raised when an action fails (setup, the prototype axis) are not standing orders, or `setup_failed` belongs in `orders.py`. Either way, the line no longer matches the code.

## Door

**Door:** two-way. Reverting the commits restores starting from HEAD and drops the config keys. A `worktrees:` block left in a config would then load as a dict where a path is expected, so it should be removed with the revert. **Blast radius:** adopters. Once released, every adopter with an `origin/HEAD` starts slices from it instead of their local HEAD (`scripts/run.py:174-177`).

## Raw data

- Slice record: `.xv/slices/2026-10-26-worktree-setup.md`
- Diff: `git diff 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2..HEAD`
- Wall: `xv wall diff 2026-10-26-worktree-setup`
- Boundary: `xv boundary --base 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2` (`.xv/slices/2026-10-26-worktree-setup.boundary.md`)

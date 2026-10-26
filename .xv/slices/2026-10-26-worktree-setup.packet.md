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

This is the second pass, after Sean's answer at the accept stop. Nothing stops it for two people. All four settled points are in the code and tested. Sean decides three things: whether the new guard should check more than file presence, since a stale but present `.xv/` on `origin/HEAD` still gets through and setup and teardown then read different configs (1.1); whether a timed-out setup should quote its output (1.2); and whether the CHANGELOG line should mention the new refusal (1.4). The picture edits and the rewording of decision 10 were already settled as the watch's at the merge (4). After that, the merge is his.

## The scenario

`.xv/config.yml` can hold a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new --base <ref>` beats `worktrees.base`. Without either, the base is `origin/HEAD`, or HEAD when there is no remote. `setup` runs in the new worktree before the forecaster, with `{worktree}` replaced by the worktree's path. A non-zero exit is a `setup_failed` stop for the originator, and the stop's question quotes the command's last lines. `teardown` runs the same way at close. `xv check` lists both commands, and `defaults/config.yml` shows the block commented out.

Settled on 2026-10-26 by Sean:

1. Refuse a base that has no committed `.xv/config.yml`, `pitch.md` or `picture.md`, and say to push or to pass `--base HEAD`. Remove "starts from HEAD" from the old message.
2. Give the defaults a teardown example that works with an absolute path.
3. Shell-quote `{worktree}`.
4. Run setup and teardown under `tests.timeout`. A setup that times out is `setup_failed`.

May ignore: `worktrees.path`, and removing the worktree itself.

## The recording

None; this is a feature. To replay:

- The red for this pass: `cd tests && python3 -m unittest test_worktree_setup_settled`. Five of its six tests fail at `39a7a33` (`checks.scenario.red_output`).
- At HEAD, `python3 -m unittest test_worktree_setup_settled test_worktree_setup` ran 18 tests, OK. I ran it in this pass.
- The maker's and the cleaner's whole-suite runs: 185 tests, OK (`checks.cleaner.suite_output`).

## The boundary picture

From `.xv/slices/2026-10-26-worktree-setup.boundary.md`, as given:

- Modules touched: `scripts/check`, `scripts/run`, `scripts/xvlib`. None added, none removed.
- Edges added: none. Edges removed: none. New outbound calls: none. Tables: none. Surface paths: none.
- Shape hints: none.

This pass touched only `scripts/run.py`, `defaults/config.yml` (one comment line) and the new `tests/test_worktree_setup_settled.py` (`git diff 39a7a33..HEAD --stat`).

## What the suite asserts after

From the first pass, unchanged:

- `--base`, `worktrees.base` and `origin/HEAD` choose the base, in that order, and HEAD is used with no remote.
- `setup` runs in the worktree before any spend is recorded.
- A failing setup is one open `setup_failed` stop for the originator, whose question quotes the command's stderr.
- Teardown runs at close.
- `xv check` lists both commands.
- The defaults show the block.

New in this pass:

- When `.xv/` is committed locally but `origin/HEAD` lacks it, `slice new` exits non-zero, says "push" and "--base HEAD", and makes no worktree.
- `--base HEAD` gets past that refusal.
- The uncommitted-layer refusal no longer says "starts from HEAD".
- A worktree path with a space reaches both setup and teardown as one argument.
- A setup that outlasts `tests.timeout` is one open `setup_failed` stop for the originator, and the status is `stopped`.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast's `"shape": "narrow"` and its breadth line ("xv slice new (--base, setup stop), teardown on close, xv check listing, defaults/config.yml and their tests"). Both passes touch only those, plus `CHANGELOG.md`.

- **No new module, edge, table or surface.** The boundary picture shows "Edges added: none" and "Shape hints: none", which matches `.xv/picture.md:21` ("22 modules … 54 edges").
- **The base guard calls git through `subprocess`,** at `scripts/run.py:218` (`["git", "cat-file", "-e", f"{base}:{XV_DIR}/{name}"]`). It is the same kind of local git call as `resolve_base` at `scripts/run.py:180`, so it is not a new outbound call.
- **Setup and teardown now go through the existing `shell()` helper** (`scripts/run.py:192`, `code, out = shell(command, wt, tests_timeout(config))`), the same path `tests.command` takes (`scripts/run.py:63`). This stays inside the shape.

Findings inside the shape, for the originator:

**1.1 The guard checks that the base has the files, not that they are the ones the person sees. Setup and teardown can then read different configs.** The guard at `scripts/run.py:216-221` only checks that `config.yml`, `pitch.md` and `picture.md` exist at the base. The pitch check before it reads the main checkout's working tree (`scripts/run.py:205`, `pitch_status(root)`). Setup reads the main checkout's config (`scripts/run.py:201`, `config = load_config(root)`, then `:254`). Teardown reads the slice worktree's config, which comes from the base (`scripts/run.py:562-563`, `root = slice_root(...)`, `config = load_config(root)`, then `:594`). Here is a concrete case. An adopter has pushed `.xv/` once. They then add a `worktrees:` block with `setup` and `teardown`, and edit the pitch, committing both locally without pushing. `xv slice new` passes every guard and starts from `origin/HEAD`. Setup runs from the local config. The agents work against the older pitch, picture and config in the worktree. At close, teardown is read from the worktree's config, which has none, so it silently does not run. The same holds if the pushed pitch still has `status:` other than written. The settled point (1) asked only for presence, so the maker met it as written. Whether the guard should also compare the base's `.xv/` with HEAD's, or whether setup should read the worktree's config, is Sean's call. Neither test file covers it.

**1.2 A setup that times out does not quote its output.** On a timeout, `shell()` returns only `f"timed out after {timeout}s"` (`scripts/run.py:49-50`) and drops what the command had printed. The stop's question then quotes that one line. The scenario says "the question quotes the command's last lines". The test sets up a marker for this, `setup: "echo SLOW-START-9921; sleep 5"` (`tests/test_worktree_setup_settled.py:80`), but never asserts it (`:83-87` check only the stop's order, seat and status). This is the same helper `tests.command` uses, so changing it touches the suite runner too.

**1.3 `{worktree}` is quoted for you, and the defaults do not say so.** `scripts/run.py:191` replaces `{worktree}` with `shlex.quote(wt)`. A user who writes the natural `cd "{worktree}"` gets `cd "'/path/s1'"`, a path with literal quote marks in it. The default's comment says only "{worktree} is its path" (`defaults/config.yml:20`), and the defaults reach every new adopter (`.xv/picture.md:25`). The new teardown example (`defaults/config.yml:24`, `rm -rf {worktree}/node_modules`) is unquoted and works, including with a space. I read this from the code; no test writes a quoted `{worktree}`.

**1.4 The CHANGELOG line describes the first pass only.** `CHANGELOG.md:7` does not mention two changes. First, `xv slice new` now refuses a base without a committed `.xv/` (`scripts/run.py:216-221`), where it used to start from HEAD; an adopter who never pushed `.xv/` hits this on their first slice after upgrading. Second, setup and teardown are limited by `tests.timeout`. Decision 1 (`.xv/picture.md:58`) asks for a CHANGELOG line for "a standing order, or a check". The new stop already has its line; the refusal and the time limit do not.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo"), `:21` (engineering teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot."). Refusing a base without `.xv/`, and naming the fix (`scripts/run.py:220-221`, "push .xv/ … or pass --base HEAD"), serves `:7`. Nothing in this pass reaches someone `:25` excludes or breaks a promise.

## 3. Moved tests

None. `xv wall diff 2026-10-26-worktree-setup` against baseline `39a7a33` reports `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []`, and the record has `moved_tests: []`. `git diff 3ca97d4..HEAD --stat -- tests/` shows two new files and nothing else: `tests/test_worktree_setup.py` (126 lines, the first red) and `tests/test_worktree_setup_settled.py` (91 lines, this pass's red).

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

## 4. The picture

Sean settled these as the watch's at the merge. The wording below takes this pass into account.

- **`.xv/picture.md:26`** ("Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`") is now incomplete. Add: "The branch starts from `--base`, else `worktrees.base`, else `origin/HEAD`, else HEAD. `xv slice new` refuses a base without a committed `.xv/config.yml`, `pitch.md` and `picture.md`. `worktrees.setup` runs in the new worktree before the forecaster, and `worktrees.teardown` runs at close, both under `tests.timeout`." Source: `scripts/run.py:177-183`, `:216-221`, `:254`, `:594`.
- **`.xv/picture.md:25`** (`defaults/` …) is incomplete. Add: "`worktrees:` may be a path or a block with `path`, `base`, `setup` and `teardown`. `{worktree}` is substituted shell-quoted." Source: `defaults/config.yml:14-24`, `scripts/run.py:191`.
- **`.xv/picture.md:67`** (decision 10, "The standing orders all live in `scripts/orders.py`") still does not match the code: `setup_failed` is raised at `scripts/run.py:259`. Sean settled the rewording: a stop raised because an action failed is not a standing order.

## Door

**Door:** two-way. A revert restores starting from HEAD and drops the guard and the config keys. Any `worktrees:` block left in a config must be removed along with it, because the old `worktrees_dir` reads `worktrees:` as a path. **Blast radius:** adopters. Once released, every adopter with an `origin/HEAD` starts slices from it, and anyone who never pushed `.xv/` is refused until they push or pass `--base HEAD` (`scripts/run.py:180-182`, `:216-221`).

## Raw data

- Slice record: `.xv/slices/2026-10-26-worktree-setup.md`
- Diff: `git diff 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2..HEAD`; this pass alone: `git diff 39a7a33..HEAD`
- Wall: `xv wall diff 2026-10-26-worktree-setup`
- Boundary: `xv boundary --base 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2` (`.xv/slices/2026-10-26-worktree-setup.boundary.md`)

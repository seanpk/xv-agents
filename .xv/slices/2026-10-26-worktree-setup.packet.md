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

This is the third pass, after Sean's second answer. Nothing here stops it for two people. Both settled points are in the code and tested. One thing needs Sean's decision before the merge: the change to the timeout output in `shell()` breaks `xv init`'s `timed out` result, and no test catches it (1.1). The CHANGELOG line, the defaults note and the picture edits were already settled as the watch's at the merge (4). After that, the merge is his.

## The scenario

`.xv/config.yml` can hold a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new --base <ref>` beats `worktrees.base`. Without either, the base is `origin/HEAD`, or HEAD when there is no remote. `setup` runs in the new worktree before the forecaster, with `{worktree}` replaced by the worktree's path. A non-zero exit is a `setup_failed` stop for the originator, quoting the command's last lines. `teardown` runs the same way at close. `xv check` lists both, and `defaults/config.yml` shows the block commented out.

Settled on 2026-10-26: refuse a base with no committed `.xv/` layer files and say to push or pass `--base HEAD`; give the defaults a teardown example that works; shell-quote `{worktree}`; run setup and teardown under `tests.timeout`.

Settled on 2026-10-27 (this pass): (1) setup and teardown both read the worktree's `.xv/config.yml`, which comes from the base; (2) a timed-out command keeps its output, and the same helper runs `tests.command`.

May ignore: `worktrees.path`, and removing the worktree itself.

## The recording

None; this is a feature. To replay:

- This pass's red: `cd tests && python3 -m unittest test_worktree_setup_settled`. Two of its eight tests fail at `4140647` (`checks.scenario.red_output`).
- At HEAD, `python3 -m unittest test_worktree_setup_settled test_worktree_setup` ran 20 tests, OK. I ran it in this pass.
- The whole suite: 187 tests, OK, from the maker's and the cleaner's runs (`checks.cleaner.suite_output`). I did not rerun it.

## The boundary picture

From `.xv/slices/2026-10-26-worktree-setup.boundary.md`, as given: it touches `scripts/check`, `scripts/run` and `scripts/xvlib`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none.

This pass touched only `scripts/run.py` (two hunks) and `tests/test_worktree_setup_settled.py` (+25 lines), per `git diff 4140647..HEAD`.

## What the suite asserts after

From the earlier passes, unchanged: the base comes from `--base`, then `worktrees.base`, then `origin/HEAD`, then HEAD. Setup runs before any spend. A failing setup is one open `setup_failed` stop for the originator, quoting its output. Teardown runs at close. `xv check` lists both commands. The defaults show the block. A base without a committed `.xv/` is refused, and `--base HEAD` gets past that. A path with a space reaches setup and teardown as one argument. A setup that outlasts `tests.timeout` is `setup_failed`.

New in this pass:

- When the main checkout's `worktrees.setup` differs from the base's, setup runs the base's (`tests/test_worktree_setup_settled.py:95-102`).
- A setup that times out leaves a stop whose question says "timed out" and, after "its last output:", contains what the command printed before the limit (`:104-112`).

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow. That matches the forecast's `"shape": "narrow"`. This pass stays inside its breadth line ("xv slice new (--base, setup stop), teardown on close, …"). The boundary picture reports "Edges added: none" and "Shape hints: none", so it agrees with `.xv/picture.md:21` (22 modules, 54 edges).

Findings inside the shape, for the originator:

**1.1 `xv init` no longer reports a timed-out test command as `timed out`.** `shell()` now returns `f"{written[-4000:]}\ntimed out after {timeout}s"` (`scripts/run.py:49-52`). That text never starts with "timed out": it starts with the command's output, or with `\n` when there was none. `try_test_command` still tests `text.startswith("timed out")` (`scripts/run.py:803-804`). So every timeout falls through to `{"result": "failed", "exit": 124, "tail": …}`. `xv init` puts that result in its output (`scripts/run.py:914`). The xv-init brief says `test_run` is "`passed`, `failed` …, or `timed out`" (`skills/xv-init/SKILL.md:32`), so an adopter whose suite is slow is now told it failed. No test catches this: `tests/test_init_tries.py:86` says "A timeout is not covered here". The settled point said only that a timed-out test run quotes its output, so the maker met it as written. I read this from the code; my attempt to replay it in Python needed an approval I did not have. Whether to fix the match (for example `code == 124 and "timed out after" in text`) and add a test is Sean's call.

**1.2 One part of the previous 1.1 is still open, and Sean did not settle it.** The pitch check reads the main checkout's working tree (`scripts/run.py:207`, `pitch_status(root)`). The base guard checks only that the files exist at the base (`scripts/run.py:216-221`). The agents then work against the base's pitch and picture. So a pitch edited and committed locally but not pushed passes the check, while the slice is judged against the older pushed pitch. Setup and teardown now agree (`scripts/run.py:256-257`, `:597`), which closes the config half of the earlier finding. I list this only so it is not lost.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo"), `:21` (engineering teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot."). Running the base's own setup, and showing what a timed-out setup printed, both serve `:7`. Nothing reaches someone `:25` excludes. Finding 1.1 makes `xv init` less clear for a slow suite. That is a defect against the brief, not against a line of the pitch.

## 3. Moved tests

None. `xv wall diff 2026-10-26-worktree-setup` against the baseline `4140647` reports `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []`, and the record has `moved_tests: []`. Against the slice base, `git diff 3ca97d4..HEAD --stat -- tests/` shows two new files and nothing else: `tests/test_worktree_setup.py` (+126) and `tests/test_worktree_setup_settled.py` (+116).

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

## 4. The picture

Sean settled these as the watch's at the merge. The wording below includes this pass.

- **`.xv/picture.md:26`** ("Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`") is incomplete. Add: "The branch starts from `--base`, else `worktrees.base`, else `origin/HEAD`, else HEAD. `xv slice new` refuses a base without a committed `.xv/config.yml`, `pitch.md` and `picture.md`. The worktree's own config, from the base, gives `worktrees.setup`, which runs before the forecaster, and `worktrees.teardown`, which runs at close. Both run under `tests.timeout`, and a timed-out command keeps its output." Source: `scripts/run.py:179-185`, `:216-221`, `:256-257`, `:597`, `:49-52`.
- **`.xv/picture.md:25`** (`defaults/` …) is incomplete. Add: "`worktrees:` may be a path or a block with `path`, `base`, `setup` and `teardown`. `{worktree}` is substituted already shell-quoted." Source: `defaults/config.yml:14-24`, `scripts/run.py:193`.
- **`.xv/picture.md:67`** (decision 10, "The standing orders all live in `scripts/orders.py`") still does not match the code: `setup_failed` is raised at `scripts/run.py:262`. Sean settled the rewording: a stop raised because an action failed is not a standing order.

## Door

**Door:** two-way. A revert restores starting from HEAD and the old timeout text. Any `worktrees:` block in a config must be removed along with it, because the old `worktrees_dir` reads `worktrees:` as a path. **Blast radius:** adopters. Once this is released, every adopter with an `origin/HEAD` starts slices from it. Anyone who never pushed `.xv/` is refused. Anyone running `xv init` with a slow suite is told it failed (1.1).

## Raw data

- Slice record: `.xv/slices/2026-10-26-worktree-setup.md`
- Diff: `git diff 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2..HEAD`; this pass alone: `git diff 4140647..HEAD`
- Wall: `xv wall diff 2026-10-26-worktree-setup`
- Boundary: `xv boundary --base 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2` (`.xv/slices/2026-10-26-worktree-setup.boundary.md`)

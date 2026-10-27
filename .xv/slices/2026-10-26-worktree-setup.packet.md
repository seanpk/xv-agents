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

This is the fourth pass, after Sean's third answer. Nothing here stops it for two people. The settled point is in the code and tested: `xv init` reports a slow suite as `timed out` again. One thing needs Sean's attention before the merge: the "watch on first green" step for this pass cannot be done through `xv init`, because of an older defect (1.1). The CHANGELOG line, the defaults note and the picture edits were already settled as the watch's at the merge (4). After that, the merge is his.

## The scenario

`.xv/config.yml` can hold a `worktrees:` block with `base`, `setup` and `teardown`. `xv slice new --base <ref>` beats `worktrees.base`. Without either, the base is `origin/HEAD`, or HEAD when there is no remote. `setup` runs in the new worktree before the forecaster, with `{worktree}` replaced by the worktree's path. A non-zero exit is a `setup_failed` stop for the originator, quoting the command's last lines. `teardown` runs the same way at close. `xv check` lists both, and `defaults/config.yml` shows the block commented out.

Settled on 2026-10-26: refuse a base with no committed `.xv/` layer files; give the defaults a teardown example that works; shell-quote `{worktree}`; run setup and teardown under `tests.timeout`. Settled on 2026-10-27 (first): setup and teardown read the base's config; a timed-out command keeps its output.

Settled on 2026-10-27 (this pass): `xv init` reports a test command that outlasts `tests.timeout` as `{"result": "timed out", "after_s": <limit>}`, as before this slice, and a test covers it. The pitch check reading the main checkout's pitch is its own issue, not this slice's (record, scenario section).

May ignore: `worktrees.path`, and removing the worktree itself.

## The recording

None; this is a feature. To replay:

- This pass's red: `cd tests && python3 -m unittest test_init_timeout`. Both tests failed at `adfe1c6` (`checks.scenario.red_output`: `'result': 'failed', 'exit': 124`).
- The whole suite at HEAD: `cd tests && python3 -m unittest -q` ran 189 tests in 114s, OK. I ran it in this pass.

## The boundary picture

From `.xv/slices/2026-10-26-worktree-setup.boundary.md`, as given: it touches `scripts/check`, `scripts/run` and `scripts/xvlib`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none.

This pass touched one line of `scripts/run.py` (`:803`) and added `tests/test_init_timeout.py` (+31), per `git diff 18034d1..HEAD`.

## What the suite asserts after

From the earlier passes, unchanged: the base comes from `--base`, then `worktrees.base`, then `origin/HEAD`, then HEAD. A base without a committed `.xv/` is refused, and `--base HEAD` gets past that. Setup runs the base's config, in the worktree, before any spend. A path with a space reaches setup and teardown as one argument. A failing or timed-out setup is one open `setup_failed` stop for the originator, quoting what the command wrote. Teardown runs at close. `xv check` lists both commands. The defaults show the block.

New in this pass: `try_test_command`, the function whose result `xv init` prints as `test_run` (`scripts/run.py:914`), returns `{"result": "timed out", "after_s": 1}` for a command that outlasts a 1-second limit, both when it wrote a line first and when it wrote nothing (`tests/test_init_timeout.py:17-22`).

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow. That matches the forecast's `"shape": "narrow"`. This pass is one changed condition in `scripts/run.py:803` (`text.startswith("timed out")` becomes `text.endswith(f"timed out after {timeout}s")`), inside the `scripts/run` module the boundary picture lists as touched. The boundary picture reports "Edges added: none" and "Shape hints: none", so it agrees with `.xv/picture.md:21`.

The cleaner proposed pulling the setup stop out of `cmd_slice_new` into a helper (`checks.reports`, cleaner, 2026-10-27T13:14). That would be a new function inside `scripts/run`, not a new module or edge, so it is not a shape change. The cleaner made no change for it.

The fix holds: `shell()` ends every timeout with `\ntimed out after {timeout}s` (`scripts/run.py:52`). `try_test_command` passes the same `int` limit to `shell()` that it matches against (`:801-803`), and it is the only reader of that text (`grep "timed out"` over `scripts/`, `evals/`, `bin/` and `skills/`; `scripts/agentcli.py:78` has its own text).

Findings inside the shape, for the originator:

**1.1 The watch step for this pass cannot be done through `xv init`.** The red's note says to "set tests.timeout low in a config and run `xv init`" (`tests/test_init_timeout.py:28-31`; record `red.watch_first_green`). With a config already in place, `runners` is never bound: it is set only inside `if "config.yml" in written:` (`scripts/run.py:891-892`), and it is read at `:919` (`if len(runners) > 1:`). That line runs after `test_run` is computed and before anything is printed, so `xv init` crashes without showing `test_run`. A fresh init writes the defaults' timeout, so you can't lower the limit first. The defect is older than this slice (`git show 3ca97d4:scripts/run.py`, lines 839 and 866), and the slice's diff does not touch it. The note itself calls it "a separate defect", but nothing in the record files it. Whether to file it, and how to watch this green another way (for example, a Python call to `try_test_command` as the test does), is Sean's call.

**1.2 Carried, not this slice's.** The pitch check reads the main checkout's pitch (`scripts/run.py:207`), while the agents read the base's. Sean put this in its own issue (record, third settled paragraph). I list it only so it is not lost.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo"), `:21` (engineering teams and non-technical people) and `:25` ("not for people or projects that will not trust agents to write production code. It will never be a teapot."). With this pass, an adopter with a slow suite is told it timed out, not that it failed. That serves `:7`. Nothing reaches someone `:25` excludes.

## 3. Moved tests

None. `xv wall diff 2026-10-26-worktree-setup` against the baseline `18034d1` reports `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []`, and the record has `moved_tests: []`. `tests/test_init_timeout.py` is the red. It is in the baseline the watch re-took (`.xv/slices/2026-10-26-worktree-setup.wall.json:22`, 2 assertions). Against the slice base, `git diff 3ca97d4..HEAD --stat` shows three new test files and no changed ones: `tests/test_worktree_setup.py` (+126), `tests/test_worktree_setup_settled.py` (+116) and `tests/test_init_timeout.py` (+31).

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

One unchanged note is now out of date: `tests/test_init_tries.py:86` says "A timeout is not covered here". It is covered in `tests/test_init_timeout.py`. It is a comment, not an assertion.

## 4. The picture

Sean settled these as the watch's at the merge. This pass adds nothing new to them, because it puts back the behaviour from before the slice.

- **`.xv/picture.md:26`** ("Each slice has a git branch `xv/<id>` and a worktree under `.xv/worktrees/`") is incomplete. Add: "The branch starts from `--base`, else `worktrees.base`, else `origin/HEAD`, else HEAD. `xv slice new` refuses a base without a committed `.xv/config.yml`, `pitch.md` and `picture.md`. The worktree's own config, from the base, gives `worktrees.setup`, which runs before the forecaster, and `worktrees.teardown`, which runs at close. Both run under `tests.timeout`, and a timed-out command keeps its output." Source: `scripts/run.py:179-185`, `:216-223`, `:256-257`, `:597`, `:49-52`.
- **`.xv/picture.md:25`** (`defaults/` …) is incomplete. Add: "`worktrees:` may be a path or a block with `path`, `base`, `setup` and `teardown`. `{worktree}` is substituted already shell-quoted." Source: `defaults/config.yml:14-24`, `scripts/run.py:193`.
- **`.xv/picture.md:67`** (decision 10, "The standing orders all live in `scripts/orders.py`") still does not match the code: `setup_failed` is raised at `scripts/run.py:262`. Sean settled the rewording: a stop raised because an action failed is not a standing order.

The CHANGELOG line still describes only the first pass (`CHANGELOG.md:7`): it leaves out the base refusal, the quoting and the time limit. Sean settled it as the watch's at the merge.

## Door

**Door:** two-way. A revert restores starting from HEAD and the old timeout text. Any `worktrees:` block in a config must be removed along with it, because the old `worktrees_dir` reads `worktrees:` as a path. **Blast radius:** adopters. Once this is released, every adopter with an `origin/HEAD` starts slices from it, and anyone who never pushed `.xv/` is refused.

## Raw data

- Slice record: `.xv/slices/2026-10-26-worktree-setup.md`
- Diff: `git diff 3ca97d4f62a4cc76d2487d83b96e9a6a7ca457e2..HEAD`; this pass alone: `git diff 18034d1..HEAD`
- Wall: `xv wall diff 2026-10-26-worktree-setup`
- Boundary: `.xv/slices/2026-10-26-worktree-setup.boundary.md`

## From the cleaner

- Shape proposal, for people: cmd_slice_new now holds base check, worktree add, record write and the setup-failure stop; extracting the setup-stop into a helper would be a new function boundary, left for the guardian to judge.

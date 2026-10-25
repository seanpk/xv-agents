---
shape_change: no
pitch_contradiction: no
shape_breadth: none
door: two-way
---

# Packet: xv boundary finds Python edges in src layouts and flat scripts

This is the second packet, written after the maker's pass on your accept_moves answer (`.xv/slices/2026-10-24-boundary-imports.md:58`). It replaces the first one.

## Needs a decision

1. **The fix has still not been shown working on this repo.** The scenario says "On this repo, `.xv/boundary-all.md` shows `run` -> `agentcli`, `orders`, `prompt`, `record`, `spend`" (`.xv/slices/2026-10-24-boundary-imports.md:32`). The slice's boundary picture still has `"edges": []` (`.xv/slices/2026-10-24-boundary-imports.boundary.md:103`), and `xv boundary --all --json` from this worktree also returns `"edges": []`. The cause: `/home/sean/.local/bin/xv` resolves to `/home/sean/Making/Personal/xv-agents/bin/xv`, the main checkout, so it runs main's unfixed `scripts/boundary.py` rather than this branch's. A slice that changes `boundary` cannot be checked by its own boundary picture. The unit tests are the only evidence. To replay the scenario's second sentence, run `xv boundary --all` once this is on main.
2. **The CHANGELOG line is still to write.** Decision 1 reads: "A change to … a check an agent is judged by needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:60`), and `boundary` is one of "the guardian's checks" (`.xv/picture.md:23`). You said "the CHANGELOG line goes in the PR" (`.xv/slices/2026-10-24-boundary-imports.md:58`). The diff does not touch `CHANGELOG.md`. Add the line when you open the PR.
3. **The order you settled on misses one src-layout case.** The new order tries the importing file's own folder first (`scripts/boundary.py:112-113`: `prefixes = [here + "/" if here else "", ""] + [d + "/" for d in root_dirs if d]`), as settled at `.xv/slices/2026-10-24-boundary-imports.md:34`. Python does this only for a directory that is on `sys.path`. Inside a package, `import store` is absolute. Take `src/api/main.py` with a sibling `src/api/store.py` and a package `src/store/`. Python imports `src/store`, but the resolver picks `src/api/store.py`. That file is in the same module, so the `src/api` → `src/store` edge is missed. No test covers this, and this repo has no packages, so nothing here is affected. Decide whether that's acceptable for now.

## The scenario

In a `src/` layout, and in flat scripts that import each other by bare name, `xv boundary` shows an edge for every import between modules. A bare import is resolved by trying the importing file's folder first, then the repo root, then each source root, so `import run` inside `evals/` resolves to `evals/run.py`. May ignore: JavaScript, Ruby and Go imports, and dependency-cruiser. (seanpk/xv-agents#12)

## Recording / replay

There is no recording. To replay, run `cd tests && python3 -m unittest test_boundary_python_edges test_boundary_python_order`. In this run, 5 tests passed. The whole suite also passed: `Ran 125 tests … OK`.

## Boundary picture

From `.xv/slices/2026-10-24-boundary-imports.boundary.md`: touched `scripts/boundary`. No modules, edges, outbound calls, tables or surface paths were added or removed, and there are no shape hints. Item 1 explains why the edge set here is not evidence. The diff adds no import line to `scripts/boundary.py`. The only new coupling is that `graph` now reads `config["source"]["roots"]` (`scripts/boundary.py:140`), a key that `source_files` and `module_of` already read (`scripts/boundary.py:49`, `:64`).

## What the suite asserts after the change

- **Flat scripts.** Under the root `scripts`, `import agentcli`, `from orders import …` and `from record import …` in `run.py` give exactly the three edges `run`→`agentcli`, `run`→`orders` and `run`→`record`. `import os` gives none (`tests/test_boundary_python_edges.py:14-24`).
- **src layout.** `from store.db import get` and `import store` (a package with `__init__.py`), both in `src/api/main.py`, give the edge `src/api`→`src/store` (`tests/test_boundary_python_edges.py:26-38`).
- **Order.** `import run` in `evals/other.py` resolves to `evals/run.py`, not `scripts/run.py`. When both `run.py` and `scripts/run.py` exist, the repo-root one wins (`tests/test_boundary_python_order.py:9-19`).

## Moved tests

None. `xv wall diff 2026-10-24-boundary-imports` reports `changed: []`, `deleted: []` and `fewer_assertions: []` against baseline `3abb00a`. It also reports one added file, `tests/test_boundary_python_order.py`, with 2 tests. `tests/test_boundary_python_edges.py` (the red, 3 tests) is new too, but it was added before the baseline. `git diff 948efd1..HEAD -- tests/` shows no other test file. The record says `moved_tests: []` (`.xv/slices/2026-10-24-boundary-imports.md:15`), which agrees.

## The four checks

1. **Shape: no. Breadth: none.** The picture's shape is "22 modules, all flat Python files" with `bin/xv` as the one entry point (`.xv/picture.md:21-22`), and neither changes. The forecast expected "the Python import-edge resolution in boundary and its tests under tests/ to move", with breadth narrow (`.xv/slices/2026-10-24-boundary-imports.md:11`), and that is all the code diff touches. Against the base, the `.xv/config.yml` hunk (the allow list) is now byte-identical to main's, apart from main's later `promote.attribution` line, which this branch does not touch. You said "the allow list is fixed on main" (`.xv/slices/2026-10-24-boundary-imports.md:58`), so it adds nothing when merged.
2. **Pitch: no.** I checked the diff against `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `:21` (who uses it) and `:25` (who it is not for). The change makes the guardian's evidence true for Python repos. It adds no user and breaks no promise.
3. **Moved tests: none.** See above.
4. **The picture: an edit is proposed.** `.xv/picture.md:21` says "`xv boundary` does not resolve bare imports … so `.xv/boundary-all.md` shows no edges for this repo until that is fixed." After merge, that sentence is untrue. Proposed wording: "`xv boundary` resolves bare Python imports: the importing file's folder, then the repo root, then each source root (slice 2026-10-24-boundary-imports)." After merge, replace the hand list of real edges with the regenerated `.xv/boundary-all.md`. The hand list leaves out the evals edges, such as `evals/run` → `agentcli`, `grade`, `spend`, `xvlib` (`evals/run.py:33-36`) and `evals/grade` → `xvlib` (`evals/grade.py:17`).

Also: the record says `cleaner_commit: null` (`.xv/slices/2026-10-24-boundary-imports.md:17`), but commit `fea3796` contains the first cleaner's edit (`scripts/boundary.py`, +2/−1). The second cleaner changed nothing. This only affects the bookkeeping; the diff is complete and the tree is clean.

## The door

Two-way door: reverting `scripts/boundary.py` undoes it. No data, public contract or message to users changes. Blast radius: small. Boundary pictures for Python repos with bare imports will start showing edges, and so "edge added" hints, after the release.

## Raw data

- Diff: `git diff 948efd1159971b567b82e3bc8045c8c6542e5300..HEAD`. The code is `scripts/boundary.py` (+11/−6). The tests are 2 new files. The rest is `.xv/config.yml` and the `.xv/slices/` files.
- Boundary picture: `.xv/slices/2026-10-24-boundary-imports.boundary.md`
- Wall: `xv wall diff 2026-10-24-boundary-imports`, with the baseline in `.xv/slices/2026-10-24-boundary-imports.wall.json`
- Agent logs: `.git/xv/runs/2026-10-24-boundary-imports/` (paths in the record's `spend`)
- I could not read the packet template `skills/guardian/packet.md` because permission was refused. This packet follows the shape the guardian brief describes.

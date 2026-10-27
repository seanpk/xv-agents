---
slice: 2026-10-27-package-imports
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: A bare import inside a package resolves the way Python does

Sean Kennedy, as the person who set the work going, has nothing to decide beyond the merge. The one shape hint is a false positive (see 1). The change alters a check the guardian uses, so binding decision 1 applies; the CHANGELOG line is there and names Sean as the solo decider (see 1).

## The scenario

When `src/api/main.py` sits in a package (`src/api/__init__.py` exists) and has a sibling `src/api/store.py`, then `import store` resolves to the package `src/store`, and the boundary picture shows the edge `src/api` → `src/store`. When `src/api/` has no `__init__.py` (flat scripts, like this repo's `scripts/`), the sibling `src/api/store.py` still wins, as it did before. (seanpk/xv-agents#26.) May ignore: nothing stated.

## The recording

None. This is a defect slice, but it started from words. To replay the red and the green:

- Red: `git checkout be31667 && cd tests && python3 -m unittest test_boundary_package_imports` fails with `AssertionError: 'src/api/store.py' != 'src/store/__init__.py'` and `[] != [['src/api', 'src/store']]` (slice record, `red.failure` and `checks.scenario.red_output`).
- Green: at HEAD the same command gives `Ran 3 tests ... OK`. I re-ran it. The whole suite gave `Ran 201 tests ... OK` for both the maker and the cleaner (record `checks.maker.suite_output`, `checks.cleaner.suite_output`).

## The boundary picture

This is as given in `.xv/slices/2026-10-27-package-imports.boundary.md`:

- Modules touched: `scripts/boundary`. Added: none. Removed: none. Now calling out of the process: none.
- Edges added: none. Edges removed: none. That leaves 56 edges among 22 modules, the same as `.xv/picture.md:21`.
- Tables: none added or removed.
- Surface paths: added `/__init__.py`. Removed: none.
- Shape hints: "a surface path was added or removed".

## What the suite asserts after

- New, `tests/test_boundary_package_imports.py`:
  - In a package, `resolve("store", "src/api/main.py", …)` returns `src/store/__init__.py`, not the sibling.
  - `graph` gives exactly one edge, `src/api` → `src/store`.
  - With no `__init__.py`, `resolve` still returns the sibling `src/api/store.py`.
- Old assertions: none moved. The wall diff against baseline `0a38187` shows `changed: []`, `deleted: []`, `added: []` and `fewer_assertions: []`.

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast's `"shape": "narrow"`.

- **Hint "a surface path was added or removed" does not change the shape.** The `SURFACE` regex `[\"'](/[A-Za-z0-9_\-/{}:<>.]*)[\"']` (`scripts/boundary.py:40`) matched the string literal in the new line `scripts/boundary.py:113`: `in_package = bool(here) and here + "/__init__.py" in files`. That literal is a file-name suffix, not a route or anything a user meets. The surfaces in `.xv/picture.md:27` (the `xv` CLI, `skills/*/SKILL.md`, `ci/github/`, `.github/workflows/`) are untouched.
- **No module, edge, table or outbound call is added or removed** (boundary picture: all "none"). The diff to `scripts/boundary.py` is one line replaced by two in `resolve()` (`scripts/boundary.py:113-114`). That is inside `boundary`, one of "the guardian's checks" (`.xv/picture.md:23`).
- **Binding decision 1 applies, and is met as recorded.** It reads "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`" (`.xv/picture.md:59`). Every guardian's boundary picture runs through `resolve()`, so this changes what the guardian sees. The new line at `CHANGELOG.md:7` says: "This changes one of the guardian's checks; Sean decided it, solo". With `seats.two_people: solo` (`.xv/picture.md:51`), that is the recorded form. I am flagging it so the person who set the work going sees it; it is not a stop.
- **Behaviour the scenario does not state.** Inside a package, a bare import that matches only the sibling now resolves to nothing, i.e. it is treated as third-party. Here is why. At `scripts/boundary.py:114`, with `in_package` true, `prefixes` becomes `[""] + [root + "/"]`, so `src/api/store.py` is never tried for the name `store`. This matches Python 3, where an implicit relative import fails. No edge is lost, because a sibling is always in the same module (`module_of`, `scripts/boundary.py:62-77`). Explicit relative imports (`from . import store`, `from .store import x`) are not affected. `py_imports` turns them into repo-absolute names such as `src.api.store` (`scripts/boundary.py:95-97`), and the `""` prefix finds `src/api/store.py`. I read this from the code. I did not run a probe, because running the probe was not approved.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7-25`.

- The change makes the guardian's boundary check more accurate for adopters' Python packages. That serves "xv-agents makes Xtreme Vibing executable and empirical" (`.xv/pitch.md:17`).
- It touches nothing in "Who it is not for, and what it will never do" (`.xv/pitch.md:25`).

## 3. Moved tests

No old tests moved. The slice record has `moved_tests: []`. `xv wall diff 2026-10-27-package-imports` shows `changed: []`, `deleted: []` and `fewer_assertions: []`. The only file added under `tests/**` is the red, `tests/test_boundary_package_imports.py`, which is new, so nothing in it asserts less. The earlier package-import fixture in `tests/test_boundary_python_edges.py:36` (`"src/store/__init__.py"`) is unchanged and still passes in the green suite.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

## 4. The picture

No edit proposed. What I checked:

- `.xv/picture.md:21` says "22 modules, all flat Python files … 56 edges". That still holds: the boundary picture shows 22 modules and no edges added or removed.
- `.xv/picture.md:23` names `boundary` as one of the guardian's checks. Still true.
- `.xv/picture.md:27` lists the surfaces. Unchanged.

## Door

**Door:** two-way. Reverting `scripts/boundary.py:113-114` brings back the old resolution; no data, contract or message is involved. **Blast radius:** small.

One thing for whoever merges: `boundary.py` ships to adopters, so after release their next boundary pictures may show new cross-package edges. Those edges were always there and were hidden before.

## Raw data

- Slice record: `.xv/slices/2026-10-27-package-imports.md`
- Diff: `git diff 94cdf5f15f31c53d02fc8de787ce85889627e799..HEAD` (`scripts/boundary.py`, `CHANGELOG.md`, `tests/test_boundary_package_imports.py`, the slice record and its wall file)
- Wall: `xv wall diff 2026-10-27-package-imports`
- Boundary: `.xv/slices/2026-10-27-package-imports.boundary.md` (`xv boundary --base 94cdf5f15f31c53d02fc8de787ce85889627e799`)

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The picture does not describe how imports are resolved, so nothing in it becomes untrue.

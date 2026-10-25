---
slice: 2026-10-24-readme-drift
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: docs
---

# Packet: README matches the stop table, the status and xv adapt

Nothing here needs two people. The merge is Sean's, and three things need Sean's decision first: (a) the throwaway red is still in the diff, and the scenario says Sean removes it before the merge; (b) a `.xv/config.yml` change to the agents' allow lists rides in this slice, outside the scenario and the forecast; (c) a proposed edit to `.xv/picture.md` §"Where the code and the docs disagree".

## The scenario

The README stop table names every order `scripts/orders.py` fires, with a row in words for each order and no order ids. The README Status line says 0.2.0 came from a real init. The README mentions `xv adapt`. The slice may ignore the generated block between the `xv:method` markers. The red is for this slice only, and Sean removes it before the merge (the slice record, "Scenario").

## The recording

None; this slice started from words. To replay: `cd tests && python3 -m unittest test_readme_drift`. At the red commit `4b21ba2` it fails 3 of 3 (the record's `checks.scenario.red_output`). At HEAD it passes 3 of 3, and the whole suite passes 123 tests. I ran both in this pass.

## The boundary picture

From `.xv/slices/2026-10-24-readme-drift.boundary.md` (xv boundary, base `948efd1`): no modules touched, added or removed. No edges added or removed. No new outbound calls, no tables, no surface paths. Shape hints: none. That matches the diff, which touches no Python module under `scripts/` or `evals/`.

## What the suite asserts after

The suite asserts everything it asserted at the baseline, plus the throwaway `tests/test_readme_drift.py`. That file asserts three things. Every order id that `scripts/orders.py` fires (with each `<step>_stopped` folded into one `agent_stopped`) matches a row of the README stop table through a regex map of its words. The Status section contains "0.2.0" and "real init". The README contains "xv adapt". No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: none.

- The boundary picture has no hints and no new edges, tables or surfaces (`.xv/slices/2026-10-24-readme-drift.boundary.md`, "Shape hints: none"). The change is inside the shape described at `.xv/picture.md:19-28`.
- `README.md:113` adds one prose line about `xv adapt`. `README.md:284-287` adds four rows to the stop table. `README.md:395` rewrites the Status line. These are docs and do not change the shape. The new rows match the code. `scripts/orders.py:52` sends `<step>_stopped` to `two_people` when the reason is `shape`, as the new row at `README.md:285` says. `scripts/orders.py:66`, `:130` and `:132` match rows 284, 286 and 287. `scripts/adapt.py:9-12` supports "for a step set to `session`; `xv step` does not need it".
- The forecast expected "edits only to the README stop table, the Status line, and the xv adapt mention" (record front matter, `forecast.breadth`). The diff also changes `.xv/config.yml:34-36` (commit `fcfd98a`, "config allow list; Sean's answer in the scenario"). It adds `--allowedTools "Bash(cat:*),…,Bash(git rm:*),Bash(git mv:*),…,Bash(xv record move:*),…"` to the `default`, `forecaster` and `guardian` agent lines. This is not a shape change: `.xv/config.yml` is this repo's own config, not `defaults/`, so it does not reach adopters (`.xv/picture.md:25`). It is outside the scenario, though, and it merges with this slice. **For Sean:** confirm the commit is yours and that it should land under this slice's name, not on its own. It gives the read-only forecaster and guardian `git rm` and `git mv`. `.xv/picture.md:71` says read-only agents are "checked, not trusted", and `read_only_broken` (`scripts/orders.py:60-63`) still catches a write. So the change is consistent with that decision, but it is still a change to what agents may run. The record's `protected_changed` checks are empty for every agent step, so no agent made the change.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7-25` against the diff. The change makes the README true to the code, which serves "makes Xtreme Vibing executable and empirical, and so usable and shareable" (`.xv/pitch.md:17`). Nothing in the diff serves anyone in "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`), or does anything the pitch rules out.

## 3. Moved tests

None. The wall baseline is `fcfd98a`, 25 files. The record's wall check after the maker and after the cleaner shows `changed: []`, `deleted: []`, `added: []`, `fewer_assertions: []`, `unrecorded: []`, `ok: true` (record `checks.maker.wall`, `checks.cleaner.wall`). `moved_tests: []` in the record agrees. This run had no approval for `xv wall diff`, so these figures come from the record's wall check, not a fresh run.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| (none) | | | | |

These are not moved tests, but Sean should decide on them:

- **The throwaway red is still in the diff.** `tests/test_readme_drift.py:1` says "Throwaway red for slice 2026-10-24-readme-drift. Sean removes it before the merge." The scenario says the same. If it is merged, `tests/test_readme_drift.py:63` (`self.assertIn(oid, WORDS, …)`) fails the suite on every future order added to `scripts/orders.py` until someone edits the map by hand. Under `.xv/picture.md:60`, that new check could only be dropped with two people.

## 4. The picture

picture_change: yes. Proposed edits to `.xv/picture.md` §"Where the code and the docs disagree", for Sean to accept:

- `.xv/picture.md:42` ("The README stop table leaves out `cleaner_broke_suite`, `cleaner_touched_standards` and `budget_not_set`…"): no longer true after `README.md:284-287`. Delete the line.
- `.xv/picture.md:43` ("The README does not mention `xv adapt`."): no longer true after `README.md:113`. Delete the line.
- `.xv/picture.md:41` ("README 'Status' and line 38 say the method has not run on a real slice…"): half true after the change. Status is fixed (`README.md:395`), but `README.md:38` still says "none of it has run on a real change yet". Line 38 is outside the `xv:method` markers (they open at `README.md:40`), so this slice did not have to leave it. The scenario named only Status, so the maker stayed in scope. Proposed wording: "README line 38 says the method has not run on a real change; 0.2.0 came from a real init, and a first slice is running in a trial repo. The Status section was brought up to date by slice 2026-10-24-readme-drift."

A note for Sean, not a picture edit: `README.md:395` still opens "v0.1, built 2026-10-21 and 2026-10-22; 0.2.0 came from…", while `CHANGELOG.md:5` heads "0.2.0, 2026-10-24". Someone skimming the README may take v0.1 as the current version.

## Door

**Door:** two-way. A revert of the README and config hunks undoes it, with no data, contract or message to users. **Blast radius:** docs.

## Raw data

- Slice record: `.xv/slices/2026-10-24-readme-drift.md`
- Diff: `git diff 948efd1159971b567b82e3bc8045c8c6542e5300..HEAD` (`0c4903b`), with `.xv/slices/2026-10-24-readme-drift.boundary.md` untracked
- Wall: `xv wall diff 2026-10-24-readme-drift`; baseline `.xv/slices/2026-10-24-readme-drift.wall.json`
- Boundary: `xv boundary --base 948efd1159971b567b82e3bc8045c8c6542e5300`

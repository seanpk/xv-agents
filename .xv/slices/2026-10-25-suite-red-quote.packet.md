---
slice: 2026-10-25-suite-red-quote
shape_change: no
pitch_contradiction: no
picture_change: no
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: Stops quote the failing step; green means exit 0

This is the second pass. Nothing here stops it for two people, and the merge is Sean's. Both findings from the first packet are fixed. The `CHANGELOG.md` line is in. The failing step is now taken from the whole suite output, before the 800-character cut. Two smaller points are left for Sean, below: only the cleaner stop has a long-output test, and the diff grew because of record files, not code.

## The scenario

When the suite is red after the maker or the cleaner, the `cleaner_broke_suite` stop and the budget stop quote the failing step in their question. The maker's and the cleaner's briefs say green means the suite command exited 0. Settled at the merge stop on 2026-10-26, Sean: find the root. Take the first failing step from the whole output before it is cut, and keep it in the record. Add a test with output longer than 800 characters. Add a `CHANGELOG.md` line. (seanpk/xv-agents#19; Sean, solo.)

May ignore: `xv init` asking for lint and format; a summary-line convention for suite scripts.

## The recording

None; the scenario is in words. Replay: `cd tests && python3 -m unittest test_suite_red_quote`.
- Before, the red from the record: `'FAIL: test_total (test_cart.CartTest.test_total)' not found in "The suite is not green after the cleaner's pass. Failing: FAILED (failures=1)"`.
- After: `Ran 4 tests ... OK`. I re-ran it on this worktree.
- Whole suite: `Ran 130 tests ... OK`. I re-ran it here, and it matches `checks.cleaner.suite_output` in the record.

## The boundary picture

From `.xv/slices/2026-10-25-suite-red-quote.boundary.md`, as given:
- Modules touched: `scripts/orders`, `scripts/run`.
- Added or removed: no modules, edges, outbound calls, tables or surface paths.
- Shape hints: none.

The diff also edits `skills/maker/SKILL.md` and `skills/cleaner/SKILL.md`. These are surfaces (`.xv/picture.md:27`), but no surface file was added or removed.

## What the suite asserts after

`tests/test_suite_red_quote.py` asserts four things:
- A red cleaner suite stops with `cleaner_broke_suite`, and the question contains the `FAIL: ...` line.
- A red maker suite with the budget spent stops with `budget_spent`, and the question contains the same line.
- Both briefs say green is exit 0.
- New: a real `xv step` run whose suite prints a `FAIL:` header followed by more than 800 characters of traceback still gets a `cleaner_broke_suite` question that contains the header.

No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast (`forecast.shape: "narrow"`).

- **No new edges.** `scripts/run.py:365` (`checks["failing_step"] = orders.first_failing_step(out) if suite == "red" else ""`) calls `orders` from `run`. That edge already exists (`.xv/picture.md:21`, "`run` → ... `orders`"), and the boundary picture shows no edges added.
- **The orders stay pure.** `first_failing_step` and `failing_clause` (`scripts/orders.py:31-40`) read only their arguments, as the binding decision requires: "a pure function of the record and the config" (`.xv/picture.md:67`).
- **One new record key, `checks.<agent>.failing_step`, a JSON string.** It adds to the record and renames nothing, so `.xv/picture.md:71` (upgrade steps for a rename) does not apply. Old records that lack the key fall back to `suite_output` (`scripts/orders.py:39`). This is inside the record's current shape.
- **Wider than the forecast's words, not its shape.** The forecast's breadth named only the briefs and the stop questions. The root fix Sean asked for adds one line in `scripts/run.py` and the `CHANGELOG.md` line. That stays narrow.

## 2. Pitch

pitch_contradiction: no. I checked `.xv/pitch.md:7` ("vibe with discipline"), `:21` (who uses it) and `:25` (who it is not for). The change makes a stop tell the person who set the work going what failed, and that serves the people the pitch names. The pitch says nothing about stop wording.

## 3. Moved tests

| File | Before | After | Why | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I checked:
- `git diff --stat e9aada2..HEAD -- tests` shows only `tests/test_suite_red_quote.py`, the scenario's own red file. It grew by the long-output test (+46/−1, the import line).
- Its sha256 today, `f920a670…`, equals the baseline hash in `.xv/slices/2026-10-25-suite-red-quote.wall.json:55`.

## 4. The picture

**No edit proposed for this slice.** The picture does not list record fields or stop wording, and `.xv/picture.md:23` ("`orders` holds the stop rules") is still true. Decision 1 is now met (`.xv/picture.md:58`):
- Two briefs (`skills/maker/SKILL.md:9`, `skills/cleaner/SKILL.md:37`) and two stop questions (`scripts/orders.py:111`, `:144`) changed.
- `CHANGELOG.md:7` adds the Unreleased line naming Sean, solo.
- `seats.two_people: solo` (`.xv/picture.md:50`) covers the two-people part.

**Already stale, and not caused by this slice.** `.xv/picture.md:21` says `xv boundary` "does not resolve bare imports ... so `.xv/boundary-all.md` shows no edges for this repo until that is fixed". The boundary picture for this slice does show the edges, for example `scripts/run --> scripts/orders`. Sean may want to cut that sentence.

## Other findings

**Only the cleaner stop has a long-output test.** `LongOutputTest` (`tests/test_suite_red_quote.py:77-99`) drives only `cleaner_broke_suite`. The budget stop shares `failing_clause` (`scripts/orders.py:111`), and `scripts/run.py:365` fills `failing_step` for the maker too, so it should behave the same. No test asserts that on a long output, though.

**"Failing:" when there is no suite at all.** With no `tests.command`, `run_suite` returns `None, "no tests.command in .xv/config.yml"` (`scripts/run.py:56`). `budget_spent` still fires, because `suite != "green"` (`scripts/orders.py:109`). The question then reads `Failing: no tests.command in .xv/config.yml`, because `failing_clause` falls back to the last line of `suite_output` (`scripts/orders.py:34`, `:39`). That is accurate, but it is labelled "Failing". The `cleaner_broke_suite` stop excludes `None`, so only the budget stop has this.

**Runners other than unittest get the summary line.** `first_failing_step` matches only `FAIL:` and `ERROR:` (`scripts/orders.py:34`). Pytest or jest output therefore quotes the last line. The slice's "may ignore" list covers this ("a summary-line convention for suite scripts").

**The diff grew because of record files, not code.** The `diff_growing` stop counted 179 → 717 lines (record `checks.maker.diff_history`). `git diff --stat f452d43..HEAD` puts 598 of those lines in `.xv/slices/` (the boundary picture, record, packet and wall.json). Code and briefs are about 23 lines, and the test is 99. Sean answered "go on". This is context for that answer, not a new finding.

**Record vs. diff, on who committed.** The cleaner reported "commit blocked by approval prompt, change left uncommitted", and the record has `cleaner_commit: null`. The cleaner's rename `failing_step` → `failing_clause` is nevertheless in commit `27b5ea7` ("record the cleaner's pass"). The record and the diff agree on what changed. They differ only on who committed it, the same as in the first pass.

## Door

**Door:** two-way. A revert restores the old question text and brief lines. The new record key is extra, and old code ignores it. **Blast radius:** small. The briefs reach adopters through `xv install`, but they only state the exit-code rule the watch already enforces (`scripts/run.py:59`).

## Raw data

- Slice record: `.xv/slices/2026-10-25-suite-red-quote.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..27b5ea7`. Uncommitted: only the regenerated boundary picture.
- Wall: `xv wall diff 2026-10-25-suite-red-quote` (not run here; see check 3)
- Boundary: `.xv/slices/2026-10-25-suite-red-quote.boundary.md`
- Packet shape: I could not read the template at `skills/guardian/packet.md` (permission needed), so this follows the first pass's packet for the same slice.

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- The record has `moved_tests: []`.
- The wall checks after the maker and after the cleaner show `changed: []`, `fewer_assertions: []` and `unrecorded: []`.
- I could not run `xv wall diff`: the command needed approval. The record and git stand in for it.

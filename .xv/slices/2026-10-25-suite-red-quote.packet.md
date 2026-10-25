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

Nothing stops this for two people. The merge is Sean's. Two things need Sean first: the change edits two briefs and two standing-order questions but adds no `CHANGELOG.md` line, which a binding decision requires; and the quote often falls back to the summary line in a real run, because the watch keeps only the last 800 characters of the suite output.

## The scenario

When the suite is red after the maker or the cleaner, the `cleaner_broke_suite` stop and the budget stop quote the failing step from `suite_output` in their question, so the person does not have to open the record to see what failed. The maker's and cleaner's briefs say green means the suite command exited 0, not what the end of its output looks like. (seanpk/xv-agents#19; Sean approves the brief change, solo.)

May ignore: `xv init` asking for lint and format; a summary-line convention for suite scripts.

## The recording

None; the scenario is in words. Replay: `cd tests && python3 -m unittest test_suite_red_quote`. Before (red, from the record): `AssertionError: 'FAIL: test_total (test_cart.CartTest.test_total)' not found in "The suite is not green after the cleaner's pass."`. After: `Ran 3 tests ... OK` (I re-ran it on this worktree). Whole suite: 129 tests, OK, after both the maker and the cleaner (record `checks.maker.suite`, `checks.cleaner.suite`).

## The boundary picture

From `.xv/slices/2026-10-25-suite-red-quote.boundary.md`, as given: one module touched, `scripts/orders`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none.

The diff also touches `skills/maker/SKILL.md` and `skills/cleaner/SKILL.md`. These are surfaces (`.xv/picture.md:27`, "Surfaces: ... `skills/*/SKILL.md`"), but no file was added or removed.

## What the suite asserts after

- New, `tests/test_suite_red_quote.py`: if the cleaner's suite is red, the stop is `cleaner_broke_suite` and its question contains the `FAIL: ...` line from `suite_output`. If the maker's suite is red and the budget is spent, the stop is `budget_spent` and its question contains the same line. The maker and cleaner briefs each match `exit(s|ed)? ... 0`.
- No old assertion moved.

## 1. Shape

shape_change: no. shape_breadth: narrow, the same as the forecast ("shape": "narrow").

- The boundary picture shows no added edges and no shape hints. The new code is one pure function, `failing_step`, inside `orders.py` (`scripts/orders.py:31-35`), called from two existing stops (`scripts/orders.py:105-106`, `scripts/orders.py:138`). The orders stay "a pure function of the record and the config" (`.xv/picture.md:67`).
- The changed files match what the forecast expected: "edits to the maker and cleaner briefs ... and to the question text of the cleaner_broke_suite and budget stops" (record, `forecast.breadth`).

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:7` ("vibe with discipline"), `:21` (who uses it) and `:25` (who it is not for). It changes what a stop says to the person who set the work going, and it serves that person. The pitch says nothing about stop wording, and silence is not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

Sources checked: `moved_tests: []` in the record. The wall check after the maker and after the cleaner shows `changed: []`, `deleted: []`, `fewer_assertions: []`, `unrecorded: []`. `git diff --stat 018c344..HEAD -- tests` shows only the new `tests/test_suite_red_quote.py`. I could not run `xv wall diff` here because the command needed approval, so the record's wall checks and git stand in for it.

## 4. The picture

No edit proposed. I looked at `.xv/picture.md:23`, which says `orders` holds the stop rules, and that is still true. I also looked at the binding decisions at `:58-72`, and none of them becomes untrue.

**Binding decision not met, for Sean:** `.xv/picture.md:58`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
- The diff changes two briefs (`skills/maker/SKILL.md:9`, `skills/cleaner/SKILL.md:37`).
- It also changes the question of two standing orders (`scripts/orders.py:105-106`, `:138`).
- `git diff f452d43..HEAD -- CHANGELOG.md` is empty.
- The two-people half is covered by `seats.two_people: solo` (`.xv/picture.md:50`) and "Sean approves the brief change, solo" (record, Scenario).
- The `CHANGELOG.md` line is missing. Under "Unreleased" it would read like the #13 line and name Sean, solo.

## Other findings

**The quote degrades to the summary line on a real run.** `scripts/run.py:364`: `checks["suite"], checks["suite_output"] = suite, (out or "")[-800:]`. `failing_step` looks for a `FAIL:`/`ERROR:` line only in those 800 characters. If it finds none, it falls back to the last line (`scripts/orders.py:33-34`), which for unittest is `FAILED (failures=N)`. Once a traceback is longer than about 800 characters, the `FAIL:` header has been cut away, so the question says `Failing: FAILED (failures=1)`. That names no step.
- The record shows the cut. The scenario's own `red_output`, kept to the same 800 characters, starts mid-rule (`"==================\nFAIL: test_cleaner_broke_suite..."`) and ends `FAILED (failures=4)`. Only one of the four failures survived.
- When the window holds several `FAIL:` lines, `next(...)` picks the first one in the window. That is not the run's first failure.
- The new test passes because its `SUITE_OUTPUT` (`tests/test_suite_red_quote.py:11-20`) is shorter than 800 characters.
- `checks["failing"]` (`scripts/run.py:365`) is parsed from the full output, and it is already in the record when these stops fire.

This is for Sean to weigh against the scenario's "so the person sees what failed". I have not fixed it.

**The brief now matches the code.** `scripts/run.py:59`: `return ("green" if code == 0 else "red"), out`. The new brief lines (`skills/maker/SKILL.md:9`, `skills/cleaner/SKILL.md:37`) describe what the watch already does.

**Record vs. diff.** The cleaner reported "commit blocked by approval prompt, change left uncommitted" (record `checks.reports`, cleaner), and the record has `cleaner_commit: null` and `committed: false`. The cleaner's rename of `l` to `line` (`scripts/orders.py:33-34`) is nevertheless in commit `b1fbacc` ("record the cleaner's pass"), which the watch made. The record and the diff agree on what changed. They differ only on who committed it.

## Door

**Door:** two-way. A revert restores the old question text and the old brief lines. No data, contract or message to users is involved. **Blast radius:** small. The briefs ship to adopters through `xv install`, but the new wording only states the exit-code rule the watch already enforces.

## Raw data

- Slice record: `.xv/slices/2026-10-25-suite-red-quote.md`
- Diff: `git diff f452d430f44f6c01e611f705f5b709b80231291b..b1fbacc` (no uncommitted source changes; the only untracked file is the boundary picture)
- Wall: `xv wall diff 2026-10-25-suite-red-quote` (not run here; see check 3)
- Boundary: `xv boundary --base f452d430f44f6c01e611f705f5b709b80231291b` → `.xv/slices/2026-10-25-suite-red-quote.boundary.md`

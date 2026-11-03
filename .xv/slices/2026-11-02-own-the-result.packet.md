---
slice: 2026-11-02-own-the-result
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: no
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: Briefs lead with Own the result

Nothing here stops for two people, and no scenario point is missed. This is the second guardian pass. The first pass found one miss: the watch brief's dropped sentence. Sean's amendment allows that drop, so the miss is gone. Sean has two notes to look at before 0.4.1 is cut: the CHANGELOG line names one person, and the CI pins point at a tag that does not exist yet.

## The scenario

All 15 brief openers start with `Own the result: even when agents write all of the code, a person is responsible for what it does. An agent may stop. It may not decide.` Each keeps the agent-specific rest it already had, and the "The one rule:" label is gone. Under the amendment of 2026-11-02 (record, "Amended"), the watch brief may drop "A person is responsible for every change, including one made entirely by agents." `docs/briefs.md` ("Every brief") and `.xv/picture.md` item 13 say the same thing. `CHANGELOG.md` has a line naming who agreed the reword (#107). The CI pins and README mentions say `v0.4.1`.
May ignore: the Go-and-see third stop, `scripts/orders.py`, renaming the README "The one rule" section, cutting the v0.4.1 tag, and other issues.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest test_briefs_picture`. I ran it at HEAD afe5b5d: 12 tests, OK. At `pre_maker_commit` 2c7a26b the red failed (record, scenario `red_output`). The cleaner ran the whole suite green, 649 tests (record, cleaner `suite_output`). Since then the only code change is one added test in the red file (`git diff 83b4172..HEAD -- tests`).

## The boundary picture

Taken as given from `.xv/slices/2026-11-02-own-the-result.boundary.md`:
- Shape hints: none.
- Modules touched, added or removed: none.
- Edges added or removed: none.
- Tables: none. Surfaces: none.

Every changed file outside `.xv/slices/` is Markdown, a CI example YAML, or `tests/test_briefs_picture.py` (`git diff --stat`).

## What the suite asserts after

`OwnTheResultTest` in `tests/test_briefs_picture.py` has 7 tests:
- In each of the 15 briefs, the first line holding the stop line starts with the Own the result sentence.
- In 10 briefs, that line is exactly the Own the result sentence plus the rest the brief had before (`OPENER_RESTS`). The watch brief is left out because the amendment lets it drop its sentence. The cleaner, forecaster, listener and scenario briefs are left out because they had no rest. Their diff hunks show the line equal to the bare sentence.
- No brief contains "The one rule:".
- The "Every brief" section of `docs/briefs.md` says "Own the result opens each brief" and "stop line".
- Picture item 13 names Own the result and the stop line.
- `CHANGELOG.md` has an Unreleased section that names Own the result, #107 and Sean.
- The three CI files pin `ref: v0.4.1` and none contains `v0.4.0`. The README says `git checkout v0.4.1` and pin `` `v0.4.1` ``.

The five `PictureInTheBriefsTest` tests are unchanged.

## 1. Shape

shape_change: no. shape_breadth: none.
- The boundary picture has no shape hints, no new modules and no new edges (`.xv/slices/2026-11-02-own-the-result.boundary.md:7`, `:11-14`, `:18-19`).
- No file under `scripts/`, `bin/` or `evals/` changed, so the change stays inside the shape at `.xv/picture.md:19`.
- The breadth is within the forecast's `shape: narrow`. The forecast's breadth line names exactly these files (`.xv/slices/2026-11-02-own-the-result.md:11`).

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code." The new opener still has agents writing all of the code and puts responsibility for the result on a person. That matches the README's existing wording (`README.md:42`: "Even when agents write all of the code, a person is responsible for what it does"). The pitch makes no promise that the change breaks.

## 3. Moved tests

None.
- `xv wall diff 2026-11-02-own-the-result` shows `changed: []`, `deleted: []` and `fewer_assertions: []`. The record has `moved_tests: []` (`.xv/slices/2026-11-02-own-the-result.md:15`).
- From the base, the test diff only adds lines after `tests/test_briefs_picture.py:42` (hunk `@@ -42,5 +42,87 @@`).
- Since the wall baseline 83b4172, the scenario agent added `test_each_opener_keeps_its_agent_specific_rest_after_the_stop_line` to the red file (`tests/test_briefs_picture.py:57`, `tests/test_briefs_picture.py:83`), and it removes nothing. `xv wall diff` does not list that addition, because the file is the slice's red file.

Slice-only: 2 marked, both kept. `test_ci_pins_and_readme_mentions_say_v0_4_1` guards a one-time pin bump. `test_changelog_has_an_unreleased_line_for_the_reword_naming_107` breaks when cutting 0.4.1 renames the Unreleased section. (record `slice_only`; Sean accepted both at the `scenario_stopped` answer.)

## 4. The picture

No edit proposed.
- `.xv/picture.md:75` (item 13) was already changed in this slice by commit 09f3228, at Sean's direction (log 2026-11-03T03:19:51), and now matches `docs/briefs.md` "Every brief". The first packet asked Sean to confirm that wording. That request still stands, because a watch commit wrote it.
- `.xv/picture.md` no longer contains "one rule" anywhere (grep).
- Item 14 (`.xv/picture.md:76`, upgrade steps when `.xv/` renames something) does not apply, because nothing under `.xv/` is renamed.

## 5. The wall

- `tests/test_briefs_picture.py` `test_ci_pins_and_readme_mentions_say_v0_4_1`: keep the slice-only mark, so it stays off the wall. It asserts `ref: v0\.4\.1` and `assertNotIn("v0.4.0", text)` (diff hunk). The next release's pin bump will break it.
- `tests/test_briefs_picture.py` `test_changelog_has_an_unreleased_line_for_the_reword_naming_107`: keep the slice-only mark, so it stays off the wall. It needs `^## Unreleased\n` (diff hunk). Cutting 0.4.1, which the scenario's May ignore leaves to the person, turns that heading into a version heading.

## Other findings for the originator

- **The CHANGELOG line names one person.**
  - `CHANGELOG.md:3`: "A change to an agent is Decide from evidence: two people, written down short. A version line without two names is a draft."
  - The new line, `CHANGELOG.md:7`, reads "agreed by Sean Kennedy". It has no solo note like 0.4.0's "decided by Sean solo" (`CHANGELOG.md:11`) and none of the "Sean decided it, solo" endings the 0.4.0 entries use (`CHANGELOG.md:13`).
  - It also leaves out the "It moves no position on xtremevibing.com." line those entries carry.
  - Under Unreleased this is a draft. It needs a second name or a solo note before 0.4.1 is cut.
- **The CI examples pin a tag that does not exist yet.** `ci/github/xv-guardian.yml:37`, `ci/github/xv-listener.yml:28` and `ci/github/xv-wall.yml:26` say `ref: v0.4.1`, and `README.md` says `git checkout v0.4.1`. Anyone who copies them before the tag is cut gets a failed checkout. The scenario leaves cutting the tag out of scope, so the gap lasts from the merge until the tag exists.

## Scenario misses

None.

What I checked. Point 1 with the amendment: all 15 opener hunks start with the sentence. The 10 briefs that had a rest keep it word for word (`tests/test_briefs_picture.py:83` passes). `skills/watch/SKILL.md:11` drops only the sentence the amendment allows (`.xv/slices/2026-11-02-own-the-result.md:47`). Point 2: `docs/briefs.md:7` and `.xv/picture.md:75` both say Own the result opens each brief and the stop line stays. Point 3: `CHANGELOG.md:7` names #107 and Sean Kennedy. Point 4: a grep outside `tests/`, `CHANGELOG.md` and `.xv/slices/` finds `v0.4.0` only at `.xv/retro/2026-10-30.md:37`, a past retro and not a pin. Binding decision 13 (`.xv/picture.md:75`) is now true.

## Door

**Door:** two-way. A revert restores the openers, the docs, the pins and the picture line. Nothing is migrated or sent to users. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-02-own-the-result.md`
- Diff: `git diff 3e5bf091aa27720b9f9374f3f2f9dba05888d1e1..HEAD` (HEAD afe5b5d)
- Wall: `xv wall diff 2026-11-02-own-the-result`
- Boundary: `.xv/slices/2026-11-02-own-the-result.boundary.md`
- Earlier packet (first pass): commit 83b4172

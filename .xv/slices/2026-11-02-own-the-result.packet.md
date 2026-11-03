---
slice: 2026-11-02-own-the-result
shape_change: no
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: none
moved_tests: 0
door: two-way
blast_radius: small
---

# Packet: Briefs lead with Own the result

Nothing here stops for two people. One scenario miss sends the slice back: the watch brief lost its agent-specific rest. Sean decides two wall recommendations and one CHANGELOG note.

## The scenario

All 15 brief openers now start with `Own the result: even when agents write all of the code, a person is responsible for what it does. An agent may stop. It may not decide.` Each keeps its agent-specific rest, and the "The one rule:" label is gone. `docs/briefs.md` ("Every brief") and `.xv/picture.md` item 13 say the same thing. `CHANGELOG.md` has a line for the change that names who agreed it (#107). The three CI example pins and the README pin mentions say `v0.4.1`.
May ignore: the Go-and-see third stop, `scripts/orders.py`, renaming the README "The one rule" section, cutting the v0.4.1 tag, and other issues.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest test_briefs_picture.OwnTheResultTest`. At `pre_maker_commit` 2c7a26b it fails 37 times (record, scenario `red_output`). At HEAD it passes all 6 tests (run by me). The cleaner ran the whole suite green, 649 tests (record, cleaner `suite_output`).

## The boundary picture

From `.xv/slices/2026-11-02-own-the-result.boundary.md`, as given. Shape hints: none. Modules touched, added or removed: none. Edges added or removed: none. No module now calls out of the process. Every changed file is Markdown, a CI example YAML, or a test (`git diff --stat`: 25 files, no `scripts/` or `bin/` file).

## What the suite asserts after

`OwnTheResultTest` adds 6 tests in `tests/test_briefs_picture.py`:

- In each of the 15 briefs, the first line holding the stop line starts with the Own the result sentence.
- No brief contains "The one rule:".
- `docs/briefs.md` "Every brief" says "Own the result opens each brief" and "stop line", and no longer says "the one rule opens".
- Picture item 13 names Own the result and the stop line.
- `CHANGELOG.md` has an Unreleased section naming Own the result, #107 and Sean.
- The three CI files pin `ref: v0.4.1` and contain no `v0.4.0`; the README says `git checkout v0.4.1` and pin `` `v0.4.1` ``.

No old assertion moved.

## 1. Shape

shape_change: no. The boundary picture shows no shape hints, no new modules and no new edges (`.xv/slices/2026-11-02-own-the-result.boundary.md`, "Shape hints: none", "Edges: added: none"). No code changed, so this sits inside the shape described at `.xv/picture.md:19`. Breadth is none, inside the forecast's "narrow" (record `forecast.shape`).

## 2. Pitch

pitch_contradiction: no. I checked the change against `.xv/pitch.md:25`: "xv-agents is not for people or projects that will not trust agents to write production code." The new opener keeps agents writing code and puts responsibility for the result on a person. That is the same idea as the README's own section (`README.md:42`, "Even when agents write all of the code, a person is responsible for what it does"). No promise in the pitch is broken.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |

None. `xv wall diff 2026-11-02-own-the-result` shows `changed: []`, `deleted: []` and `fewer_assertions: []`, and the record's `moved_tests` is `[]`. The only test-file change adds `OwnTheResultTest` to `tests/test_briefs_picture.py` (hunk `@@ -42,5 +42,62 @@`) and removes no line.

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- `.xv/picture.md:75` (item 13) is already changed in this slice by commit 09f3228, "picture item 13 opens with Own the result, as Sean directed", after the maker stopped (log 2026-11-03T03:19:51, Sean answered `maker_stopped`: 1). The new text: "Every brief opens with Own the result, keeps the stop line, …". I propose no further edit. Sean should confirm that the committed wording is the one he meant, because a watch commit wrote it, not his own hand.
- I searched `.xv/picture.md` for "one rule" and found nothing else that is now untrue.

## 5. The wall

- `tests/test_briefs_picture.py` `test_ci_pins_and_readme_mentions_say_v0_4_1`: recommend marking it slice-only. It guards a one-time version bump (scenario point 4; hunk lines `+    def test_ci_pins_and_readme_mentions_say_v0_4_1` … `self.assertIn("pin \`v0.4.1\`", readme)`). The next release's pin change will break it.
- `tests/test_briefs_picture.py` `test_changelog_has_an_unreleased_line_for_the_reword_naming_107`: recommend marking it slice-only. It requires an `## Unreleased` section (hunk line `+        m = re.search(r"^## Unreleased\n(.*?)(?=^## |\Z)"`). When the person cuts 0.4.1, that heading becomes a version heading, which is the scope the scenario leaves to them, and the test fails.

## Other findings for the originator

- **The CHANGELOG line names one person.** `CHANGELOG.md:3` says "A change to an agent is Decide from evidence: two people, written down short. A version line without two names is a draft." The new line reads "agreed by Sean Kennedy" (hunk `@@ -2,6 +2,10 @@`). Under Unreleased that is a draft. Before 0.4.1 is cut, it needs a second name or a solo note like 0.4.0's "decided by Sean solo" (`CHANGELOG.md:11`).
- **The CI examples pin a tag that does not exist yet.** `ci/github/xv-guardian.yml:37`, `ci/github/xv-listener.yml:28` and `ci/github/xv-wall.yml:26` now say `ref: v0.4.1`. Until the person cuts the tag, anyone who copies an example gets a checkout failure. The scenario puts cutting the tag out of scope ("May ignore"), so the gap lasts from merge until the tag exists.

## Scenario misses

- 1: The watch brief dropped its agent-specific rest. Before: `The one rule: an agent may stop. It may not decide. A person is responsible for every change, including one made entirely by agents.` After (`skills/watch/SKILL.md:11`): `Own the result: … An agent may stop. It may not decide.` The sentence "A person is responsible for every change, including one made entirely by agents." is gone. Point 1 says "plus any agent-specific rest that was already there". The dropped sentence largely repeats the new Own the result sentence, but the scenario asks for it to be kept. The red does not check the rest: `test_each_of_the_15_brief_openers_names_own_the_result_first` only asserts `startswith(OWN)`. (evidence: diff hunk on `skills/watch/SKILL.md`; to: scenario)

## Door

**Door:** two-way. A revert restores the openers, the docs, the pins and the picture line, and nothing is migrated or sent to users. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-02-own-the-result.md`
- Diff: `git diff 3e5bf091aa27720b9f9374f3f2f9dba05888d1e1..HEAD` (HEAD d57291e)
- Wall: `xv wall diff 2026-11-02-own-the-result`
- Boundary: `.xv/slices/2026-11-02-own-the-result.boundary.md` (`xv boundary --base 3e5bf091aa27`)

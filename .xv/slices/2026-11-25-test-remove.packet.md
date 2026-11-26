---
slice: 2026-11-25-test-remove
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 22
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet (re-pass after pairing 1): Taking the inspector's advice to remove a test removes it: --test-remove (#202)

This re-pass covers `ba851c4..74ef83b`: the pairing's commits `84b532b` and `98f461c`.
No stop for two people. One scenario miss sends the slice back:
- Removing every test of a class in one answer is not refused, and leaves a class with no body (scenario miss 1).

Decisions for the originator:
- Two brief lines are now stale (check 1, finding C). Changing them needs two people (`.xv/picture.md:348`).
- The CHANGELOG line still has one name (check 2).
- The picture edit in check 4.

Earlier finding A (the exact word `remove`) is resolved: `--test-remove` now takes every kind of advice (`scripts/record.py:644`).
Earlier finding B (the only test in a class) is resolved for one test (`scripts/record.py:605-607`), but not for two tests in one class (miss 1).

## Scenario misses

- outcome 3: removing every test of a class in one answer is not refused, and leaves the class with no body; the originator settled that the only test in a class is refused (record log, 04:04:49 correction). Evidence: `scripts/record.py:605` checks each test against the file before any removal, and `scripts/record.py:779` applies the removals one after another. to: test-writer
   Detail:
   `scripts/record.py:597-607`: `removal_edits` reads each file again for each test (`text = f.read()`) and calls `leaves_empty_block(text, old)` against the file as it is now, not as it will be after the other removals.
   `scripts/record.py:773-779`: `make_directed_edit` then applies the edits one after another with `text.replace(old, new, 1)`, and checks nothing between them.
   So `--test-remove test_a --test-remove test_b` on a class holding only those two tests passes both checks.
   For `test_a`, the next line is `def test_b` at the same indent, so `leaves_empty_block` returns false (`scripts/record.py:431`).
   For `test_b`, the line before is the last line of `test_a`'s body, at a deeper indent, so `opens` is false (`scripts/record.py:430`).
   Both are removed and committed, and `class X(...):` is left with no body, which Python cannot parse.
   I found this by reading the code; I did not run it.
   `test_the_only_test_in_a_class_is_refused_and_nothing_is_removed` (`tests/test_record.py:2938`) removes one test from a two-test class and the only test from another class, so it does not cover this.
   to: test-writer (no red covers it).

## The scenario

Unchanged from the earlier packet.
At `moves_to_accept`, `xv record answer --test-remove <test>` removes the whole test, with its decorators, using the `test-remove` directed-edit check (1); it commits and runs the suite (2); a gone test is skipped, and an unclean removal refuses the answer with nothing removed (3); an unnamed test stays (4); `--accept-wall` and `--refuse-wall` still work and warn (5); the leftover accepted tests are removed (6); there is a CHANGELOG line (7).
The pairing carried the originator's answer at `moves_to_accept`, which the watch reverted by mistake and logged as a correction (record log, 04:04:49): every kind of advice removes the test, the only test in a class is refused, and the inspector brief names `--test-remove`.

## The recording

None. Replay with `cd tests && python3 -m unittest test_record.TestRemoveFlagTest`.
I ran it at `74ef83b`: 14 tests, OK. I did not run the whole suite. The record says the cleaner's run after the pairing was green (1525 tests).

## The boundary diagram

From `.xv/slices/2026-11-25-test-remove.boundary.md`, as given: touched `scripts/record`; no module, edge, table or surface path added or removed; no shape hints.
The pairing added one function, `leaves_empty_block` (`scripts/record.py:424-431`), inside the same module.

## What the suite asserts after

`TestRemoveFlagTest` now has 14 tests. The pairing added four:
- `--test-remove` removes a test whose advice was `mark slice-only` (`tests/test_record.py:2924`).
- `--accept-wall` on a `mark slice-only` advice removes the test (`tests/test_record.py:2932`).
- Naming the only test in a class refuses the answer, and the other named test is not removed either; HEAD and `moved_tests` are unchanged (`tests/test_record.py:2938`).
- A class with a docstring keeps it when its only test goes (`tests/test_record.py:2958`).

These tests were written in the pairing, so they are not blind. I checked each against the code.
None restates the code: each drives the CLI and reads the file, HEAD or the record.
- **D. The docstring test accepts a stop** (`tests/test_record.py:2965`: `self.assertIn(p.returncode, (0, 10), ...)`).
  Exit 10 means the answer raised a stop (`scripts/record.py:820-821`), which a red suite run does.
  So if the removal left the class unparseable, this test would still pass; it asserts only that the docstring is there and the test is gone.
  The same `(0, 10)` form is in `tests/test_record.py:2927` and `2935`.

No test reaches the new refusal in `check_edit` (`scripts/record.py:511-512`), the `xv record offer` path.
`removal_edits` raises its own refusal before it calls `check_edit` (`scripts/record.py:605-608`), so an answer never reaches line 511.
No test covers a `stay off the wall` advice, which the CHANGELOG names (`CHANGELOG.md:7`); the code treats every kind the same (`scripts/record.py:644`).

## 1. Shape

shape_change: no. shape_breadth: narrow.
The boundary diagram shows no new module, edge, table or surface path, and no shape hints.
The pairing's code change stays in `scripts/record.py`: `leaves_empty_block`, two uses of it, and a dropped refusal (`scripts/record.py:424-431`, `511-512`, `605-607`, `637-639` before).
It is still the forecast's shape: "one new flag on record answer that reuses the directed-edit removal check".

Findings for the person (inside the shape):
- **C. Two brief lines no longer say what the code does** (`skills/watch/SKILL.md:63`, `skills/watch/SKILL.md:49`).
  `skills/watch/SKILL.md:63`: "`--test-remove` takes the inspector's advice to remove a test". It now takes every kind of advice (`scripts/record.py:644`).
  `skills/watch/SKILL.md:49` lists what `xv record offer` refuses for a `test-remove`. It does not name the new refusal of the only test in a class (`scripts/record.py:511-512`).
  The picture sends readers to that list: "`skills/watch/SKILL.md` lists the refusals" (`.xv/picture.md:58`).
- **E. Accepting a `mark slice-only` advice now removes the test and also lists it in `slice_only`** (`scripts/record.py:644`, `653-657`).
  The `slice_only` entry then names a test that is no longer in its file.
  The inspector brief still asks for `recommend` as exactly `mark slice-only` (`skills/inspector/SKILL.md:28`), and it dropped the reason (the `slice_only` listing) in this diff.
  The listing still happens, so the exact word still matters. The brief no longer says why.

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md` again against the pairing's diff.
"xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
Removing a test on any kind of accepted advice is still a person's explicit answer, and it serves the same users.

Binding decision 1 (`.xv/picture.md:348`): a change to a brief needs two people and a CHANGELOG line.
This slice now changes two briefs, the watch's and the inspector's (`skills/inspector/SKILL.md:28`).
The CHANGELOG line names them, but one person: "decided by Sean Kennedy" (`CHANGELOG.md:7`).
The heading moved from `0.6.5, 2026-11-26` to `Unreleased` (`CHANGELOG.md:5`), which fits "A version line without two names is a draft" (`CHANGELOG.md:3`).
It needs a second name before it gets a version.

## 3. Moved tests

The 15 outcome-6 removals and the 3 slice-only removals are as in the earlier packet; the pairing changed none of them.
Five of the 15 still need someone to confirm the earlier acceptance; my search did not find it (earlier packet, check 3).
One move is new:

| File | Before | After | Why (record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_codex_step.py | `class CodexDocsTest(unittest.TestCase): pass`, with no test | removed (`tests/test_codex_step.py:93-96` before) | "the class held no test after the outcome-6 removals; an empty class is dead code" (Sean Kennedy, pairing 1) | Not by a scenario line; it follows from outcome 6 and asserts nothing |

The move asserts nothing less: the class held no assertion.
It also takes away the blank lines left by the earlier removal (`tests/test_codex_step.py:93` before).
`xv wall diff` in the record shows nothing unrecorded (`checks.cleaner.wall.ok: true`). In `tests/test_record.py` the assertion count went from 550 to 556, which is the pairing's new tests.

Slice-only tests removed: test_the_tests_past_slices_accepted_for_removal_are_gone_from_their_files, test_the_watch_brief_and_the_readme_name_only_the_new_way, test_the_changelog_has_a_line_for_test_remove (all `tests/test_record.py`). Kept: none.
Changes to may-not files that the test writer allowed (`may_not_files_needed`): none.

## 4. The picture

`.xv/picture.md:147-150` is still out of date, and the edit the earlier packet proposed needs two changes: every kind of advice now removes the test, and the only test in a class is refused.
Proposed lines, replacing 147-150:

```
  A person's `--test-remove <test>` takes the inspector's advice on that test, of any kind, and removes the whole test, with its decorators, from its file.
  It uses the `test-remove` directed-edit check, commits the removal, and runs the suite.
  A named test already gone from its file is skipped.
  A named test that cannot be removed whole, or that is the only test in its class, refuses the answer, and nothing is removed.
  `--accept-wall` and `--refuse-wall` are deprecated (#216) and print a warning that names the new way.
  `--accept-wall <test>` does what `--test-remove <test>` does, and `--refuse-wall <test>` does what `xv record unmark <test>` does.
  An accepted `mark slice-only` recommendation is listed in `slice_only`, and refusing it later takes it out, matched on file and test.
  A new recommendation not named is refused, and an agent's report sets neither.
  The flags take the test with its file, in the forms the coverage check takes (`file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`).
  A bare name that two files share is refused, and the refusal names each `file::test`.
  Giving any of them on another kind of stop, or accepting and refusing one test in one answer, is refused.
  Each answered `moves_to_accept` stop keeps `accepted_wall`, which includes the `--test-remove` names, and `refused_wall`.
```

If miss 1 is fixed, the fourth line should also say that removing every test of a class in one answer is refused.

Note: `.xv/picture.md:147` holds more than one sentence, joined by semicolons, and so does `.xv/picture.md:233`.

## 5. The wall

No recommendations.
I looked at the four new tests in `TestRemoveFlagTest` (`tests/test_record.py:2924-2967`).
Each guards a behaviour that stays after the slice (outcomes 1, 3 and 5), and none only restates another test.
`test_accept_wall_on_a_mark_slice_only_recommendation_removes_the_test` becomes dead when #216 removes `--accept-wall`, not in this slice.

## Door

**Door:** two-way. The code, the brief line and the test removals are git commits, and a revert brings them back. **Blast radius:** low.

## Raw data

- Slice record: `.xv/slices/2026-11-25-test-remove.md`
- Diff since the earlier packet: `git diff ba851c4aae2896f4aae1c9b773441a1a02f2ee46..74ef83b09d2346256c54979a770a3a158175c289`
- Whole diff: `git diff 911f113209115d8a4e586a9f3d6efd095926baef..HEAD`
- Wall: `xv wall diff 2026-11-25-test-remove`
- Boundary: `xv boundary --base 911f113209115d8a4e586a9f3d6efd095926baef`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:233.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: three send-backs; the three changes left (every advice kind, the only test in a class, the inspector brief line) are small and settled. Commits: 84b532bb6c, 98f461cc4a. Resumed at cleaner. Spend: 32747 tokens (in 34, out 11698, cache write 21015; cache read 4252400 not counted), 17 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_codex_step.py, tests/test_record.py.
- Pairing 2: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: the inspector found the only-test-in-a-class check misses removing every test of a class in one answer; Sean chose a language-neutral rule instead: a red suite after the removals undoes them and refuses the answer. Commits: ed56797d16, 32008509ea. Resumed at cleaner. Spend: 17783 tokens (in 22, out 6786, cache write 10975; cache read 3006025 not counted), 11 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_record.py.

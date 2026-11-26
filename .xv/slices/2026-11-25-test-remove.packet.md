---
slice: 2026-11-25-test-remove
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 23
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet (re-pass after pairing 2): Taking the inspector's advice to remove a test removes it: --test-remove (#202)

This re-pass covers `74ef83b..73b8c2f`: pairing 2's commits `ed56797` and `3200850`.
No stop for two people, and no scenario miss.

Decisions for the originator:
- F. With no `tests.command`, every `--test-remove` answer is now refused (check 1).
- G. One new test's check on the failing test's name passes from the file path alone (what the suite asserts).
- Pairing 2 dropped the Python-only check for the only test in a class. The 04:04:49 correction is now met only where an empty class turns the suite red (scenario, below).
- Still open from the earlier pass: brief line C, the CHANGELOG's second name, and the picture edit in check 4.

Earlier miss 1 is resolved: removing every test of a class leaves a file Python cannot parse, the suite goes red, and every removal is undone (`scripts/record.py:777-785`).
I ran it: `test_removing_every_test_in_a_class_is_undone_and_refuses_the_answer` passes.
Earlier finding D is resolved: a refused answer exits 2 (`scripts/record.py:1491-1492`), so the `(0, 10)` checks at `tests/test_record.py:2927`, `2935` and `2965` now fail if a removal leaves the suite red.

## Scenario misses

None.
I checked outcome 3 and the originator's 04:04:49 correction ("the only test in a class is refused") against pairing 2's diff.
The `leaves_empty_block` check is gone (`scripts/record.py:424-431` before).
The red-suite undo takes its place (`scripts/record.py:777-785`).
For Python, the only test in a class with no docstring still gets refused, because the empty class is a syntax error.
In a language where an empty class or block still runs, it would be removed.
The originator chose this in the pairing ("Sean chose a language-neutral rule instead", pairing 2 why, and record log 04:50:54).
It is not in a stop's `settled` and not in an amendment, so the person may want to settle it there.

## The scenario

Unchanged from the earlier packet.
At `moves_to_accept`, `xv record answer --test-remove <test>` removes the whole test, with its decorators, using the `test-remove` directed-edit check (1); it commits and runs the suite (2); a gone test is skipped, and an unclean removal refuses the answer with nothing removed (3); an unnamed test stays (4); `--accept-wall` and `--refuse-wall` still work and warn (5); the leftover accepted tests are removed (6); there is a CHANGELOG line (7).

## The recording

None. Replay with `cd tests && python3 -m unittest test_record.TestRemoveFlagTest`.
I ran it at `73b8c2f`: 15 tests, OK.
I ran the whole suite (`python3 tests/run.py`): 1526 tests, OK.

## The boundary diagram

From `.xv/slices/2026-11-25-test-remove.boundary.md`, as given: touched `scripts/record`; no module, edge, table or surface path added or removed; no shape hints.
Pairing 2 removed `leaves_empty_block` and its two uses, and added an undo inside `make_directed_edit` (`scripts/record.py:757-785`), all in the same module.

## What the suite asserts after

`TestRemoveFlagTest` now has 15 tests.
Pairing 2 replaced one test with two, sharing a helper `assert_refused_and_nothing_removed` (`tests/test_record.py:2938-2947`).
The helper checks that the answer is refused (not exit 0 or 10), that the error says "the suite is not green" and names a failing test, and that the file is as before.
It also checks that HEAD is unchanged, the test file has no uncommitted change, the stop has no answer, and `moved_tests` is empty.
- Removing a test that another test calls turns the suite red and is undone; the error names `test_uses_base` (`tests/test_record.py:2949-2958`).
- Removing both tests of a class is undone (`tests/test_record.py:2960-2972`).

These tests are not blind; I checked each against the code. Each drives the CLI and reads the file, HEAD or the record.
- **G. The failing name in the second test checks itself** (`tests/test_record.py:2972`: `self.assert_refused_and_nothing_removed(wt, source, head, p, "test_store")`).
  The error always names the file: "the suite is not green after removing the tests from {file}" (`scripts/record.py:783`), and the file is `tests/test_store.py` (`tests/test_record.py:2854`).
  So `assertIn("test_store", p.stderr)` passes even when the failing list is empty.
  The first test's `test_uses_base` is a real check, so the failing list is covered once.

No test covers a `moves_to_accept` answer in a repo with no `tests.command` (finding F).

## 1. Shape

shape_change: no. shape_breadth: narrow.
The boundary diagram shows no new module, edge, table or surface path, and no shape hints.
`make_directed_edit` already ran the suite after a directed edit (`scripts/record.py:776`); pairing 2 adds an undo and a refusal on its result.
It is still the forecast's shape: "one new flag on record answer that reuses the directed-edit removal check".

Findings for the person (inside the shape):
- **F. With no suite command, every removal is refused** (`scripts/record.py:777`: `if stop["order"] == "moves_to_accept" and data["suite"] != "green":`).
  `run_suite` returns `None` when `.xv/config.yml` has no `tests.command` (`scripts/suite.py:69-70`).
  `None != "green"`, so the answer is undone and refused with "the suite is not green".
  The standing orders treat a missing suite as no failure: `if checks.get("suite") not in (None, "green"):` (`scripts/orders.py:317`).
  Before pairing 2, such an answer removed the test.
- **H. The undo also undoes an offered edit picked in the same answer, and the error calls it a removal** (`scripts/record.py:736`: `edits = ([edit] if edit else []) + answer_wall(...)`; `scripts/record.py:783`: "after removing the tests from").
  A `--pick` of a `test-rename` or `changelog` edit at `moves_to_accept` that turns the suite red is undone too, and the message calls it a removal.
- **C (still open). The watch brief's line does not say what the code does** (`skills/watch/SKILL.md:63`: "`--test-remove` takes the inspector's advice to remove a test").
  It takes every kind of advice (`scripts/record.py:644`), and it does not say that a red suite undoes the removals.
  `skills/watch/SKILL.md:49` is accurate again: pairing 2 removed the `check_edit` refusal it did not list (`scripts/record.py:511-512` before).
- **E (unchanged).** Accepting a `mark slice-only` advice removes the test and also lists it in `slice_only` (`scripts/record.py:644`, `653-657`).

## 2. Pitch

pitch_contradiction: no.
I read pairing 2's diff against `.xv/pitch.md`.
"xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
Undoing a removal that breaks the suite keeps a person's answer from leaving a red suite. It serves the same users.

Binding decision 1 (`.xv/picture.md:348`): a change to a brief needs two people and a CHANGELOG line.
Pairing 2 rewrote the CHANGELOG line (`CHANGELOG.md:7`); it still has one name, "decided by Sean Kennedy", under `Unreleased` (`CHANGELOG.md:5`).
It needs a second name before it gets a version, as `CHANGELOG.md:3` says.
The line now says "before, such an answer closed the stop with no stop" (`CHANGELOG.md:7`). I did not run the old code to check that.

## 3. Moved tests

The 15 outcome-6 removals, the 3 slice-only removals and the pairing-1 `CodexDocsTest` removal are as in the earlier packets.
Five of the 15 still need someone to confirm the earlier acceptance (first packet, check 3).
One move is new:

| File | Before | After | Why (record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_record.py | `test_the_only_test_in_a_class_is_refused_and_nothing_is_removed`: names `test_other` (a two-test class) and `test_alone` (a one-test class); asserts refusal, `test_alone` and "only test in its class" in stderr, file, HEAD and `moved_tests` unchanged | `test_removing_every_test_in_a_class_is_undone_and_refuses_the_answer`: names both tests of one class; asserts refusal, "the suite is not green", `test_store` in stderr, file, HEAD, test-file status, open stop and `moved_tests` unchanged (`tests/test_record.py:2960-2972`) | "Sean chose a language-neutral rule in pairing 2: a red suite after the removals undoes them and refuses the answer, in place of the Python-only check" (record log 04:50:54) | Yes: outcome 3 and the 04:04:49 correction, under the originator's new rule |

It asserts less in two places.
It no longer names the refused test: `test_alone` became `test_store`, which the path always gives (finding G).
It no longer mixes a removable test with a refused one; both named tests are now undone together.
It asserts more in two places: the test file has no uncommitted change, and the stop stays open.

`xv wall diff`: the same seven files changed as before, with nothing added or deleted. `tests/test_record.py` went from 556 to 562 assertions since the earlier pass, which is the pairing's new tests.

Slice-only tests removed: test_the_tests_past_slices_accepted_for_removal_are_gone_from_their_files, test_the_watch_brief_and_the_readme_name_only_the_new_way, test_the_changelog_has_a_line_for_test_remove (all `tests/test_record.py`). Kept: none.
Changes to may-not files that the test writer allowed (`may_not_files_needed`): none.

## 4. The picture

`.xv/picture.md:147-150` is still out of date.
Proposed lines, replacing 147-150 (the earlier packet's edit, with the fourth line changed and a fifth added):

```
  A person's `--test-remove <test>` takes the inspector's advice on that test, of any kind, and removes the whole test, with its decorators, from its file.
  It uses the `test-remove` directed-edit check, commits the removal, and runs the suite.
  A named test already gone from its file is skipped.
  A named test that cannot be removed whole refuses the answer, and nothing is removed.
  When the suite is not green after the removals, in any language, every removal is undone and the answer is refused, naming the failing tests.
  `--accept-wall` and `--refuse-wall` are deprecated (#216) and print a warning that names the new way.
  `--accept-wall <test>` does what `--test-remove <test>` does, and `--refuse-wall <test>` does what `xv record unmark <test>` does.
  An accepted `mark slice-only` recommendation is listed in `slice_only`, and refusing it later takes it out, matched on file and test.
  A new recommendation not named is refused, and an agent's report sets neither.
  The flags take the test with its file, in the forms the coverage check takes (`file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`).
  A bare name that two files share is refused, and the refusal names each `file::test`.
  Giving any of them on another kind of stop, or accepting and refusing one test in one answer, is refused.
  Each answered `moves_to_accept` stop keeps `accepted_wall`, which includes the `--test-remove` names, and `refused_wall`.
```

If finding F is fixed, the fifth line should say what happens with no `tests.command`.

Note: `.xv/picture.md:147` holds more than one sentence, joined by semicolons, and so does `.xv/picture.md:233`.

## 5. The wall

No recommendations.
I looked at the two new tests (`tests/test_record.py:2949-2972`).
Each guards the undo that stays after the slice (outcome 3), and neither only restates the other: one breaks the suite with a failing test, the other with a file that will not parse.

## Door

**Door:** two-way. The code, the brief lines and the test removals are git commits, and a revert brings them back. **Blast radius:** low.

## Raw data

- Slice record: `.xv/slices/2026-11-25-test-remove.md`
- Diff since the earlier packet: `git diff 74ef83b09d2346256c54979a770a3a158175c289..73b8c2f626d89f477c5a610fd581248b8a92a477`
- Whole diff: `git diff 911f113209115d8a4e586a9f3d6efd095926baef..HEAD`
- Wall: `xv wall diff 2026-11-25-test-remove`
- Boundary: `xv boundary --base 911f113209115d8a4e586a9f3d6efd095926baef`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:233.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: three send-backs; the three changes left (every advice kind, the only test in a class, the inspector brief line) are small and settled. Commits: 84b532bb6c, 98f461cc4a. Resumed at cleaner. Spend: 32747 tokens (in 34, out 11698, cache write 21015; cache read 4252400 not counted), 17 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_codex_step.py, tests/test_record.py.
- Pairing 2: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: the inspector found the only-test-in-a-class check misses removing every test of a class in one answer; Sean chose a language-neutral rule instead: a red suite after the removals undoes them and refuses the answer. Commits: ed56797d16, 32008509ea. Resumed at cleaner. Spend: 17783 tokens (in 22, out 6786, cache write 10975; cache read 3006025 not counted), 11 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_record.py.

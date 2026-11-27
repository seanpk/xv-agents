---
slice: 2026-11-25-test-remove
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 24
expected_moves: 0
door: two-way
blast_radius: low
---

# Packet (re-pass after pairing 3): Taking the inspector's advice to remove a test removes it: --test-remove (#202)

This re-pass covers `73b8c2f..a0c3e8f`: pairing 3's commits `d6f1d23` and `a1e36ba`, and the cleaner's `a0c3e8f`.
No stop for two people, and no scenario miss.

Decisions for the originator:
- Still open: finding H (the undo also undoes a picked edit, and the error calls it a removal), finding E, the CHANGELOG's second name, and the picture edit in check 4.
- The 04:04:49 correction is still met only where an empty class turns the suite red (earlier packet; unchanged by pairing 3).

All three of pairing 3's fixes are in, and I checked each:
- Earlier finding F is resolved. The undo now fires only on `data["suite"] == "red"` (`scripts/record.py:777`), and `run_suite` returns `None` with no `tests.command` (`scripts/suite.py:69-70`).
  The new test `test_with_no_test_command_the_removal_stands` (`tests/test_record.py:2974-2985`) would have failed before: the old `!= "green"` refused this answer.
  Its `assertIsNone(self.show(wt)["suite"])` also fails if the config edit did not take, so it does not pass by accident.
- Earlier finding G is resolved. The helper now asserts `f"(failing: {failing}"` (`tests/test_record.py:2941`), and the second test passes `"tests.test_store"` (`tests/test_record.py:2972`).
  The error's file part reads `tests/test_store.py`, with a slash, so only the failing list can give `(failing: tests.test_store`.
- Earlier finding C is resolved. `skills/watch/SKILL.md:63` now says "of any of its three kinds" and "when the suite is red after the removals, every removal is undone and the answer is refused".

## Scenario misses

None.
I checked outcomes 2 and 3 against pairing 3's diff: the removal still commits and runs the suite, and a red suite still undoes it (`scripts/record.py:777-786`).

## The scenario

Unchanged from the earlier packet.
At `moves_to_accept`, `xv record answer --test-remove <test>` removes the whole test, with its decorators, using the `test-remove` directed-edit check (1); it commits and runs the suite (2); a gone test is skipped, and an unclean removal refuses the answer with nothing removed (3); an unnamed test stays (4); `--accept-wall` and `--refuse-wall` still work and warn (5); the leftover accepted tests are removed (6); there is a CHANGELOG line (7).

## The recording

None. Replay with `cd tests && python3 -m unittest test_record.TestRemoveFlagTest`.
I ran it at `a0c3e8f`: 16 tests, OK.
I ran the whole suite (`python3 tests/run.py`): 1527 tests, OK.

## The boundary diagram

From `.xv/slices/2026-11-25-test-remove.boundary.md`, as given: touched `scripts/record`; no module, edge, table or surface path added or removed; no shape hints.
Pairing 3 changed one condition and one message in `make_directed_edit` (`scripts/record.py:777-784`), in the same module.

## What the suite asserts after

`TestRemoveFlagTest` now has 16 tests.
The refusal helper now checks that the error says "the suite is red" and lists the named failing test (`tests/test_record.py:2938-2947`).
The new test checks that with no `tests.command` the removal stands: the answer succeeds, the test is gone from its file, and the record's `suite` is `None` (`tests/test_record.py:2974-2985`).
It does not check that the removal was committed; `test_test_remove_removes_the_whole_test_and_commits_it` checks that only with a suite.

I checked the pairing's tests as not blind.
Each drives the CLI and reads the file or the record; none restates the code.

## 1. Shape

shape_change: no. shape_breadth: narrow.
The boundary diagram shows no new module, edge, table or surface path, and no shape hints.
It is still the forecast's shape: "one new flag on record answer that reuses the directed-edit removal check".

Findings for the person (inside the shape):
- **H (still open). The undo also undoes an offered edit picked in the same answer, and the error calls it a removal** (`scripts/record.py:736`: `edits = ([edit] if edit else []) + answer_wall(...)`; `scripts/record.py:784`: `"the suite is red after removing the tests from {file}"`).
  Pairing 3 changed "not green" to "red" and left the rest of the message as it was.
- **E (unchanged).** Accepting a `mark slice-only` advice removes the test and also lists it in `slice_only` (`scripts/record.py:644`, `653-657`).

## 2. Pitch

pitch_contradiction: no.
I read pairing 3's diff against `.xv/pitch.md`.
"xv-agents is not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
Letting a removal stand in a repo with no suite serves the same users, and it matches the standing orders: `if checks.get("suite") not in (None, "green"):` (`scripts/orders.py:317`).

Binding decision 1 (`.xv/picture.md:348`): a change to a brief needs two people and a CHANGELOG line.
Pairing 3 changed a brief again (`skills/watch/SKILL.md:63`) and rewrote the CHANGELOG line (`CHANGELOG.md:7`).
The line still has one name, "decided by Sean Kennedy", under `Unreleased`, and needs a second before it gets a version (`CHANGELOG.md:3`).

## 3. Moved tests

The earlier 23 moves are as in the earlier packets; five of the outcome-6 removals still need someone to confirm the earlier acceptance (first packet, check 3).
One move is new:

| File | Before | After | Why (record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_record.py | `assert_refused_and_nothing_removed`: `assertIn("the suite is not green", p.stderr)`; `assertIn(failing, p.stderr)`, with `"test_store"` in the second test | `assertIn("the suite is red", p.stderr)`; `assertIn(f"(failing: {failing}", p.stderr)`, with `"tests.test_store"` (`tests/test_record.py:2940-2941`, `2972`) | "the inspector found the failing-name check passed from the file path alone; it now checks the failing list, and the message says red, since a missing suite no longer refuses" (record log 01:17:45, pairing 3) | Yes: outcome 3 and earlier finding F |

It asserts more: the failing list must name the test, in both tests that use the helper.

`xv wall diff`: the same seven files changed as before, with nothing added or deleted. `tests/test_record.py` went from 562 to 565 assertions since the earlier pass, which is the new test.

Slice-only tests removed: test_the_tests_past_slices_accepted_for_removal_are_gone_from_their_files, test_the_watch_brief_and_the_readme_name_only_the_new_way, test_the_changelog_has_a_line_for_test_remove (all `tests/test_record.py`). Kept: none.
Changes to may-not files that the test writer allowed (`may_not_files_needed`): none.

## 4. The picture

`.xv/picture.md:147-150` is still out of date.
The earlier packet's proposed lines stand, with its fifth line replaced by these two:

```
  When the suite is red after the removals, in any language, every removal is undone and the answer is refused, naming the failing tests.
  A repo with no `tests.command` has no suite to run, so the removal stands.
```

The second line follows `CHANGELOG.md:7` and `scripts/record.py:777`.

## 5. The wall

No recommendations.
I looked at the new test (`tests/test_record.py:2974-2985`).
It guards a rule that stays after the slice (with no suite, a removal stands), and no other test covers that case.

## Door

**Door:** two-way. The code, the brief line and the test changes are git commits, and a revert brings them back. **Blast radius:** low.

## Raw data

- Slice record: `.xv/slices/2026-11-25-test-remove.md`
- Diff since the earlier packet: `git diff 73b8c2f626d89f477c5a610fd581248b8a92a477..HEAD`
- Whole diff: `git diff 911f113209115d8a4e586a9f3d6efd095926baef..HEAD`
- Wall: `xv wall diff 2026-11-25-test-remove`
- Boundary: `xv boundary --base 911f113209115d8a4e586a9f3d6efd095926baef`

Note: the picture should hold one sentence per line; more than one sentence on .xv/picture.md:233.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: three send-backs; the three changes left (every advice kind, the only test in a class, the inspector brief line) are small and settled. Commits: 84b532bb6c, 98f461cc4a. Resumed at cleaner. Spend: 32747 tokens (in 34, out 11698, cache write 21015; cache read 4252400 not counted), 17 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_codex_step.py, tests/test_record.py.
- Pairing 2: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: the inspector found the only-test-in-a-class check misses removing every test of a class in one answer; Sean chose a language-neutral rule instead: a red suite after the removals undoes them and refuses the answer. Commits: ed56797d16, 32008509ea. Resumed at cleaner. Spend: 17783 tokens (in 22, out 6786, cache write 10975; cache read 3006025 not counted), 11 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_record.py.
- Pairing 3: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: the inspector's re-pass found three small fixes: a repo with no tests.command refuses every removal; the watch brief line does not say every kind or the undo; one test's failing-name check passes from the file path alone. Commits: d6f1d23b00, a1e36ba842. Resumed at cleaner. Spend: 19772 tokens (in 26, out 4428, cache write 15318; cache read 1031586 not counted), 13 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_record.py.

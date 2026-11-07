---
slice: 2026-11-07-picture-lines
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 5
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: One sentence per line in the picture

No shape or pitch stop, and no scenario miss; the merge is Sean's.
This is the second guardian pass, after the cleaner's second pass. The four findings from the first pass are closed (see "Since the first pass").
Three things are still open for Sean:
(a) Sean accepted the two picture edits from the first packet, but neither is in `.xv/picture.md` yet;
(b) the fix that adds the packet note only once has no test;
(c) the indent test stays on the wall as a hard rule, even though Sean took the sentence test off the wall to keep a crowded line from being a stop.

## The scenario

Each sentence of `.xv/picture.md` goes on its own line, with the same words as before.
A list item's extra lines line up with the item's text: two spaces after `-`, three after `1.`, four after `10.` (amendment 8).
The guardian, maker, watch and `xv-init` briefs state the rule.
`xv-check` finds the same things as before.
A CHANGELOG line names the rule.
When a picture line holds more than one sentence, the packet gets a note naming that line. It is a note, not a stop.
A list marker is not a sentence end (amendment 7).
May ignore: the other `.xv` files, pictures in other repos, and retro candidate 1.

## The recording

None, because this is a feature.
To replay the red and the green, run `cd tests && python3 -m unittest test_picture_lines`. I ran it on HEAD: 15 tests, OK.
The record's red command, `python3 -m unittest tests.test_picture_lines`, fails from the repo root with `ModuleNotFoundError: No module named 'helpers'`, and the recorded `red_output` is that error (`.xv/slices/2026-11-07-picture-lines.md:30`).
So the "red fails" check passed on an import error. It did not pass on the named assertions. This was raised in the first packet and is still true. It is a tooling matter, not a miss in this slice.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-07-picture-lines.boundary.md`), as given:
- touched: `scripts/packet`, `scripts/record`, `scripts/run`
- modules added or removed: none
- edges added or removed: none
- tables: none
- surfaces added or removed: none
- shape hints: none

## What the suite asserts after

- Each list item's extra lines in the repo's own `.xv/picture.md` line up with the item's text. A nested list keeps its own indent (`tests/test_picture_lines.py:29-41`).
- `xv-check` finds a relaxing sentence whether it sits on its own line or inside a paragraph.
- Each of the four briefs says "one sentence per line" and "line(s/d) up with the item's text".
- `xv record packet` names a crowded picture line by its number and raises no stop. Each of these does not count as a sentence end: a full stop inside backticks, one with no capital after it, one with no space after it, and a list marker. A numbered item that holds two sentences is named.
- No assertion that was on the wall before the slice moved. The only file that changed is the slice's own red file, which lost its five slice-only tests (see section 3).

## 1. Shape

shape_change: no.
The boundary picture adds no module, edge, table or surface, and has no shape hints (boundary JSON: `"edges_added": []`, `"shape_hints": []`).
`scripts/packet.py:135` `crowded_picture_lines(root)` reads `.xv/picture.md` inside the `packet` module. `.xv/picture.md:84` already names `packet` as one of "the guardian's checks", so this couples nothing that was apart.
`packet_checks` gains a `root` argument (`scripts/packet.py:168`), and both of its callers pass it (`scripts/record.py:805`, `scripts/run.py:1056`). These are the two callers that `.xv/picture.md:62` names.
Breadth: narrow, as the forecast expected (`forecast.shape: "narrow"`, `.xv/slices/2026-11-07-picture-lines.md:13`).

## 2. Pitch

pitch_contradiction: no.
The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." (`.xv/pitch.md:7`).
The rule reaches adopting repos through `skills/xv-init/SKILL.md:71`. It adds a rule for how to write the picture. It is not something the pitch rules out (`.xv/pitch.md:25`).
The pitch says nothing about the picture's format, and silence is not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none outside the slice's red file | | | | |

Slice-only tests removed: `test_joined_again_the_picture_says_the_same_words_as_at_the_base`, `test_an_unreleased_line_names_one_sentence_per_line_in_the_picture`, `test_no_picture_line_holds_more_than_one_sentence`, `test_xv_check_finds_the_same_in_the_new_picture_as_in_the_old` and `test_the_picture_has_item_continuation_lines_at_all`, all in `tests/test_picture_lines.py`, all accepted by Sean (record `slice_only`, `.xv/slices/2026-11-07-picture-lines.md:18`). Kept: none.

- `xv wall diff 2026-11-07-picture-lines` flags `tests/test_picture_lines.py` under `fewer_assertions` (19 → 13).
  The 6 assertions it lost are exactly the five removed tests (one each, plus two in the CHANGELOG test). The cleaner also removed the helpers that only those tests used: `BASE`, `base_picture`, `sentences_in` and the `subprocess` import (`git diff f222166..HEAD -- tests/test_picture_lines.py`). No remaining test changed.
  The removed checks still hold on HEAD.
  - Same words: `git diff --word-diff=porcelain d87a59c..HEAD -- .xv/picture.md` shows 0 changed words.
  - One sentence per line: every `\. [A-Z]` match in the picture is a list marker at `.xv/picture.md:252-286`.
  - Same `xv-check` result: `git diff 06351ba..HEAD --stat` does not list `.xv/picture.md`, and the first pass ran these tests green at `06351ba` ("20 tests, OK on HEAD", first packet, `.xv/slices/2026-11-07-picture-lines.packet.md` at `e556a4e`).
- The scenario agent allowed one may-not file (`may_not_files`, `.xv/slices/2026-11-07-picture-lines.md:32`): `.xv/picture.md`, "the red needs the picture's list-item extra lines lined up with the item text (three spaces after 1., four after 10.), with the same words".
  The diff rewraps it and changes no words (the word diff above).

## 4. The picture

- Both edits below are the first pass's proposals. Sean accepted them ("the guardian's two picture lines accepted", settled answer, `.xv/slices/2026-11-07-picture-lines.md:26`). Neither is in the picture: `.xv/picture.md` is unchanged since `06351ba`. They still need a person to direct the watch to make them (`.xv/picture.md:204`).
- `.xv/picture.md:62` says "`packet.packet_checks` is the one place where `xv step` and `xv record packet` run the packet lint and the `expected_moves` count." Since `scripts/packet.py:174-175`, it also writes the picture-line note.
  Proposed edit: add one line after it.
  "It also writes a note, not a stop, naming each `.xv/picture.md` line that holds more than one sentence (`packet.crowded_picture_lines`); a second run replaces the note."
- The picture does not state its own form (`.xv/picture.md:8-15`).
  Proposed edit: add one line under the title.
  "This picture is written one sentence per line, and a list item's extra lines line up with the item's text."

## 5. The wall

No recommendations this pass. The five slice-only tests are already gone (section 3). The tests that remain (the indent test, the `xv-check` test, the four brief tests and the nine packet-note tests) guard rules that last.

For Sean to decide, not a recommendation: `test_a_list_items_extra_lines_line_up_with_the_items_text` (`tests/test_picture_lines.py:29-41`) stays on the wall and asserts on this repo's own picture.
Sean took the sentence test off the wall because "a crowded picture line is a note, not a stop; on the wall it would turn the suite red in this repo" (`.xv/slices/2026-11-07-picture-lines.md:18`).
The indent test does what that reason objects to: a later picture edit with one extra line out of line turns the suite red.
The scenario does not call a misaligned line a note (`.xv/slices/2026-11-07-picture-lines.md:53`), so keeping the test is consistent with the scenario. If that is what Sean wants, nothing changes.

## Other findings for Sean

- **The once-only note has no test.**
  The maker replaced appending with replacing (`scripts/packet.py:158`, which strips the old note before adding the new one), as Sean's answer asked: "the packet note is added once however often packet_checks runs" (`.xv/slices/2026-11-07-picture-lines.md:26`).
  The settled answer is not a scenario point, so this is not a miss.
  The test file still runs `xv record packet` only once per test (`tests/test_picture_lines.py:84-93`), so nothing guards against the double note coming back.
- **The strip pattern is not tied to the start of a line.**
  `scripts/packet.py:158` removes the note's opening words anywhere in the packet, along with the blank lines before them and the rest of that line.
  If a guardian quotes those words in a finding, the next `packet_checks` run deletes the rest of that line from the packet.
  Nothing in this repo's packets does that today.
- **The briefs give two of the three widths.**
  The briefs say "two spaces after `-`, three after `1.`", and leave out "four after `10.`" (`skills/guardian/SKILL.md:27`, `skills/maker/SKILL.md:17`, `skills/watch/SKILL.md:107`, `skills/xv-init/SKILL.md:71`).
  The phrase "lined up with the item's text" covers the third width, and amendment 8 asks only for that phrase (`.xv/slices/2026-11-07-picture-lines.md:53`).

## Since the first pass

- Two slice-only tests left in the file: removed with the other three (section 3).
- The CHANGELOG stated the replaced indent rule: fixed by Sean's directed edit (`CHANGELOG.md:7`, commit `1150dab`), which now states amendments 7 and 8.
- Binding decision 1 against "solo": `.xv/picture.md:243` records "a one-person team (`seats.two_people: solo`)", so a "solo" decision meets decision 1 (`.xv/picture.md:252`) in this repo.
- The note could be added twice: fixed in code (`scripts/packet.py:158-164`), but there is no test (see above).

## Door

**Door:** two-way. A revert restores the picture's line breaks, the four briefs and the packet function, and no data or public contract changes. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-07-picture-lines.md`
- Diff: `git diff d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50..08dd663`
- Wall: `xv wall diff 2026-11-07-picture-lines`
- Boundary: `xv boundary --base d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50` (`.xv/slices/2026-11-07-picture-lines.boundary.md`)
- Red and green: `cd tests && python3 -m unittest test_picture_lines`

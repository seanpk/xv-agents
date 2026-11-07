---
slice: 2026-11-07-picture-lines
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: One sentence per line in the picture

No shape or pitch stop. Four things are for Sean, the person who set the work going, before the merge:
(a) two slice-only tests are still in the file, and both will fail on a later slice;
(b) the CHANGELOG line states the indent rule that amendment 8 replaced;
(c) binding decision 1 asks for two people on a brief change, and the CHANGELOG says "solo";
(d) the packet note can be added twice.

## The scenario

Each sentence of `.xv/picture.md` goes on its own line, with the same words as before.
A list item's extra lines line up with the item's text (amendment 8).
The guardian, maker, watch and `xv-init` briefs state the rule.
`xv-check` finds the same things as before.
A CHANGELOG line names the rule.
When a picture line holds more than one sentence, the packet gets a note naming the line; it is a note, not a stop.
A list marker is not a sentence end (amendment 7).
May ignore: the other `.xv` files, pictures in other repos, retro candidate 1.

## The recording

None; this is a feature.
Replay the red and the green with `cd tests && python3 -m unittest test_picture_lines`: 20 tests, OK on HEAD (run by the guardian).
The red command in the record, `python3 -m unittest tests.test_picture_lines` from the repo root, fails with `ModuleNotFoundError: No module named 'helpers'` on any commit.
The record's `red_output` is that ImportError (`.xv/slices/2026-11-07-picture-lines.md:30`, `checks.scenario.red_output`), so the watch's "red fails" check passed on an import error, not on the named assertions.
The scenario's report says "6 tests fail for the named reasons"; the recorded output does not show that.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-07-picture-lines.boundary.md`), as given:
- touched: `scripts/packet`, `scripts/record`, `scripts/run`
- modules added or removed: none
- edges added or removed: none
- tables: none
- surfaces added or removed: none
- shape hints: none

## What the suite asserts after

- The repo's own `.xv/picture.md` has no line with more than one sentence (outside fences and backticks, list markers excluded).
  Each list item's extra lines line up with its text.
  Some lines are continuation lines.
- The picture, joined again, has the same words as at the base commit `d87a59c` (slice-only).
- `xv-check` finds the same relaxations in the base picture and in the new one, and finds a relaxing sentence on its own line as well as in a paragraph.
- Each of the four briefs says "one sentence per line" and "line(s/d) up with the item's text".
- The Unreleased CHANGELOG section names one sentence per line in the picture (slice-only).
- `xv record packet` on a picture with a crowded line names that line number in the packet and raises no stop.
  A full stop inside backticks, one with no capital after it, one with no space after it, and a list marker do not count.
- No old assertion moved: `xv wall diff 2026-11-07-picture-lines` reports `changed: []`, `deleted: []`, `fewer_assertions: []`.

## 1. Shape

shape_change: no.
The boundary picture adds no module, edge, table or surface, and has no shape hints (boundary JSON: `"edges_added": []`, `"surfaces": {"added": [], "removed": []}`, `"shape_hints": []`).
`scripts/packet.py:135` `crowded_picture_lines(root)` reads `.xv/picture.md` from the slice root.
This is a file read inside the existing `packet` module, which `.xv/picture.md:84` already names as one of "the guardian's checks", so no coupling between modules that were apart.
`packet_checks(path, data, root=None)` gains one argument, and its two callers pass it (`scripts/record.py:805`, `scripts/run.py:1056`); the picture names these as the two callers (`.xv/picture.md:62`).
Breadth: narrow, as the forecast expected (record `forecast.shape: "narrow"`, `.xv/slices/2026-11-07-picture-lines.md:13`): four briefs, one packet function, one CHANGELOG line, and the picture rewrap.

## 2. Pitch

pitch_contradiction: no.
The pitch says what the system is for: "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." (`.xv/pitch.md`, the line under the title).
The rule reaches adopting repos through `skills/xv-init/SKILL.md:71` ("Write the picture with one sentence per line…").
That adds a writing rule, not something the pitch says the system will never do ("It will never be a teapot.", `.xv/pitch.md`, "Who it is not for").
The pitch says nothing about picture format; silence is not a contradiction.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

`xv wall diff 2026-11-07-picture-lines`: changed, deleted and added all empty, `fewer_assertions: []`; the record's `moved_tests: []`.

Slice-only tests removed: none.
Kept: both slice-only tests are still in `tests/test_picture_lines.py`, and I find no reason to keep either.
The cleaner's report says "two slice-only tests not yet removed" (`.xv/slices/2026-11-07-picture-lines.md:86`).
- `test_joined_again_the_picture_says_the_same_words_as_at_the_base` compares today's picture with the picture at the fixed `BASE = "d87a59c…"` (`tests/test_picture_lines.py:12`, `:69-71`).
  The first later slice that changes one word of `.xv/picture.md` fails it, even though it is off the wall.
- `test_an_unreleased_line_names_one_sentence_per_line_in_the_picture` reads the first `## ` section and asserts it is `Unreleased` and names the rule (`tests/test_picture_lines.py:116-120`).
  The first release that cuts `## Unreleased` into a version heading fails it.

The may-not file the scenario agent allowed (record `may_not_files`, `.xv/slices/2026-11-07-picture-lines.md:32`):
- `.xv/picture.md`, "the red needs the picture's list-item extra lines lined up with the item text (three spaces after 1., four after 10.), with the same words".
  The diff rewraps it (`git diff d87a59c..HEAD -- .xv/picture.md`, +301/−56).
  The words-same test passes on HEAD, so the edit is whitespace and line breaks only.

## 4. The picture

- `.xv/picture.md:62` says "`packet.packet_checks` is the one place where `xv step` and `xv record packet` run the packet lint and the `expected_moves` count."
  After `scripts/packet.py:163-171` it also adds the picture-line note.
  Proposed edit: add a line after it, "It also adds a note, not a stop, naming each `.xv/picture.md` line that holds more than one sentence (`packet.crowded_picture_lines`)."
- The picture does not state its own form (`.xv/picture.md:8-11`, the title and "What an outsider sees", say nothing of it).
  Proposed edit: add one line under the title or in "Names", "This picture is written one sentence per line; a list item's extra lines line up with the item's text."
  This lets a reader who opens only the picture find the rule that `skills/xv-init/SKILL.md:71` now gives adopting repos.

Both proposals are one sentence per line, as `skills/guardian/SKILL.md:27` now asks.

## 5. The wall

Recommendations (in the report's `wall_recommendations`):
- `tests/test_picture_lines.py` `test_joined_again_the_picture_says_the_same_words_as_at_the_base`: stay off the wall (record `slice_only`, accepted; `tests/test_picture_lines.py:69-71`).
  Remove it before merge, for the reason in section 3.
- `tests/test_picture_lines.py` `test_an_unreleased_line_names_one_sentence_per_line_in_the_picture`: stay off the wall (record `slice_only`, accepted; `tests/test_picture_lines.py:116-120`).
  Remove it before merge, for the reason in section 3.
- `tests/test_picture_lines.py` `test_xv_check_finds_the_same_in_the_new_picture_as_in_the_old`: mark slice-only.
  It compares relaxations in the picture at the fixed `BASE` with today's picture (`tests/test_picture_lines.py:82-84`).
  It guards this rewrap once, and a later picture edit that adds or removes a sentence `xv-check` reads fails it.
  The lasting guard is `test_xv_check_sees_a_relaxing_sentence_on_its_own_line_as_in_a_wrapped_paragraph` (`:86-89`).
- `tests/test_picture_lines.py` `test_the_picture_has_item_continuation_lines_at_all`: mark slice-only.
  It asserts that the rewrap produced some indented lines (`tests/test_picture_lines.py:65-67`, comment "must now run over").
  This is a one-time check of this rewrap; the lasting form is guarded by `test_a_list_items_extra_lines_line_up_with_the_items_text` (`:51-63`).

For Sean to decide, not a recommendation: `test_no_picture_line_holds_more_than_one_sentence` (`tests/test_picture_lines.py:46-49`) joins the wall as a hard failure on the repo's own picture.
Scenario point 6 says a crowded picture line "is a note, not a stop" (`.xv/slices/2026-11-07-picture-lines.md:45`).
With this test on the wall, a step that leaves a crowded line in this repo makes the suite red, which stops the maker or the cleaner before the note can appear.
In this repo the note can then fire only after the last suite run; in adopting repos it is the only guard.
That may be what Sean wants. If so, nothing changes.

## Other findings for Sean

- **CHANGELOG states the replaced indent rule.**
  `CHANGELOG.md:7`: "a list item's extra lines are indented two spaces."
  Amendment 8 replaced that with "line up with the item's text: two spaces after `- `, three after `1. `, four after `10. `" (`.xv/slices/2026-11-07-picture-lines.md:52`), and the picture now uses three and four (maker report, `.xv/slices/2026-11-07-picture-lines.md:85`).
  The line also does not say that a list marker is not a sentence end (amendment 7).
  I did not mark this a scenario miss: point 5 asks only that the line "names the rule", and it does name one sentence per line, and amendment 8 is scoped to points 1 and 3.
  A directed `changelog` edit (`xv record offer … --kind changelog`) would fix it without a send-back.
- **Binding decision 1 and "solo".**
  `.xv/picture.md:252`: "A change to a brief, a may-not list, a standing order, or a check an agent is judged by needs two people and a line in `CHANGELOG.md`."
  This slice changes four briefs and the watch's may-not list (`skills/watch/SKILL.md:107`), and adds a packet check.
  `CHANGELOG.md:7` ends "Decided by Sean, solo."
  The CHANGELOG line is there, but the second person is not.
  The change does not break the decision; merging it with one person would.
  Earlier Unreleased lines say "solo" too (`CHANGELOG.md:8-10`), so this may already be accepted practice; the picture does not record that.
- **The note can be added twice.**
  `scripts/packet.py:153-161` (`note_crowded_picture_lines`, `open(path, "a")`) appends the note to the packet file on every call, and nothing checks whether a note is already there.
  `packet_checks` runs both in `xv step` after the guardian (`scripts/run.py:1056`) and in `xv record packet` (`scripts/record.py:805`).
  If one packet goes through both, or `xv record packet` is run twice, it gets two identical notes.
  No test covers a second run (`tests/test_picture_lines.py:128-137` runs `record packet` once).
- **Briefs give two of the three widths.**
  The four briefs say "two spaces after `-`, three after `1.`" (`skills/guardian/SKILL.md:27`, `skills/maker/SKILL.md:17`, `skills/watch/SKILL.md:107`, `skills/xv-init/SKILL.md:71`).
  They leave out amendment 8's "four after `10.`".
  The phrase "lined up with the item's text" covers it, and the test asks only for that phrase (`tests/test_picture_lines.py:98`).
  I note it so a person who reads only the brief knows why the picture has four-space lines at items 10 to 15.

## Door

**Door:** two-way: a revert restores the picture, the briefs and the packet function; no data or public contract changes. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-07-picture-lines.md`
- Diff: `git diff d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50..06351ba`
- Wall: `xv wall diff 2026-11-07-picture-lines`
- Boundary: `xv boundary --base d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50` (`.xv/slices/2026-11-07-picture-lines.boundary.md`)
- Red and green: `cd tests && python3 -m unittest test_picture_lines`

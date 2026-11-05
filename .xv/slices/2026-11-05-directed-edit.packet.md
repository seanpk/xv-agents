---
slice: 2026-11-05-directed-edit
shape_change: yes
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: The watch makes a directed change the person approved (#132)

Needs a decision from two people (this repo runs solo, so Sean): one shape change. `record` now imports `run`, which makes an import cycle, and `xv record answer` now edits files, commits, and runs the suite. There are also three scenario misses that go back. Separately, Sean should decide whether the `doc` kind may touch a brief, the pitch or the picture.

## The scenario

A stop option can carry a directed edit, given as exact old and new text, which the person approves word for word. There are four kinds: a line in `CHANGELOG.md`, a test rename, a test removal (both in a file under `tests.paths`), and a line in a Markdown doc. Picking the option makes the edit in its own commit, which names the person. A test edit is recorded as a move in the person's name, and a rename also renames the test in `slice_only` and `wall_recommendations`. The suite and the orders then run. After the guardian has run, the packet gets a line for each edit and the guardian does not run again. The watch's brief states the rule. The amendment (2026-11-05) drops `covers` and fixes the surface: `xv record offer --edit/--old/--new/--kind`, then `xv record answer --pick`.
May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. Replay: `cd tests && python3 -m unittest test_record.DirectedEditTest`. It failed at `ed9844d` (unrecognized arguments, 36 failures) and passes at HEAD: I ran it, and all 24 tests passed.

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Touched: `scripts/record`. No modules were added or removed, and no outbound calls were added.
- Edge added: `scripts/record → scripts/run`. No edges were removed.
- Tables: none. Surface paths: none.
- Shape hint: "an edge between modules was added".

## What the suite asserts after

`DirectedEditTest` (24 tests, `tests/test_record.py:1473-1790`) asserts the following:
- An offer with an edit changes nothing until it is picked.
- The offer refuses an old text that is missing, found twice, or empty; a missing file; a kind that does not fit the file or is not on the list; a missing flag; an edit with no `--option` before it; a rename that changes more than the name; and a removal whose new text is not empty.
- A pick makes exactly the edit, in one commit that holds only the edited file and the record and is directed by the person. Unrelated dirty files are left alone.
- A test rename or removal is recorded as a move by the person, and a rename is renamed in `slice_only` and `wall_recommendations` in that commit.
- Picking option 2 makes no edit.
- After the edit, the suite result is recorded (green or red) and the verdict is printed, with exit 10 on a stop.
- After the guardian, the packet gets one line naming the file, the kind, the person and the sha, and `next` is not `guardian`. Before the guardian, no packet is written.
- The watch brief states the rule and has the new may-not line.

No old assertion changed: the only hunk against base in `tests/test_record.py` is `@@ -1468,3 +1468,329 @@`, which only adds lines.

## 1. Shape

shape_change: yes. shape_breadth: narrow; the forecast expected `wide`, so it is not wider.

- **New edge `record → run`: this changes the shape.** `scripts/record.py:505` `import run as runlib  # run imports this module`. `run` already imports `record` (`scripts/run.py:32`), so this makes a cycle, which the code works around with a lazy import. The picture lists what `record` reaches and `run` is not among them (`.xv/picture.md:21`: "`record` reaches `orders` and `packet`"). It also says "`record` owns the slice record" (`.xv/picture.md:23`). With this edge, `record` reaches into the largest script to run `tests.command`.
- **`xv record answer` gets a new job (same CLI surface, `.xv/picture.md:28`).** It now writes a repo file, runs `git commit` (`scripts/record.py:524-526`), and runs the suite. Until now a command under `record` only wrote the record; commits came from `run` (`scripts/run.py:106`). The command is not a new surface. Its new flags (`--edit/--old/--new/--kind`, `scripts/record.py:948-949`) extend the existing `offer`.

## 2. Pitch

pitch_contradiction: no. I checked the change against "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`) and "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). A directed edit is a person's own wording, so it does not cut against either line.

One thing is for the person, not a contradiction. The pitch file says of itself: "It changes when a second person agrees, and the change is written down in `.xv/decisions/`" (`.xv/pitch.md:11`). But the `doc` kind fits every `.md` except `CHANGELOG.md` (`scripts/record.py:334` `fits = rel.endswith(".md") and rel != "CHANGELOG.md"`). So one person's pick at an originator stop can commit an edit to `.xv/pitch.md`. The same pick can edit a brief or may-not list (`skills/*/SKILL.md`) with no `CHANGELOG.md` line and no second person, against binding decision 1 (`.xv/picture.md:64`). The watch brief still says the watch may not "Edit a standing order, a brief, or a check" (`skills/watch/SKILL.md:101`). The next line makes a directed edit "the one edit it makes" (`skills/watch/SKILL.md:102`). The brief does not say which line wins for a directed `doc` edit to a brief. Amendment item 2 does say "another Markdown file", so the code matches the words Sean wrote. Whether to exclude `.xv/pitch.md`, `.xv/picture.md`, `.xv/standards.md` and `skills/` is Sean's call.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `DirectedEditTest.test_the_changelog_names_the_directed_edit`: `#132` appears under `## Unreleased` | removed (`08d1417`; `xv wall diff`: 322 → 321 assertions) | slice-only: a one-time CHANGELOG wording check, accepted by Sean (`slice_only_marks`, pick 1) | Not forced; it is a slice-only removal |

Slice-only tests removed: `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit`. Kept: none.
No moves were recorded as expected. `may_not_files` is empty, so no may-not file was allowed.

Not a test, but outside the slice's work: the `.xv/config.yml` hunk at line 37 adds the `scenario:` line that runs on Opus, marked "removed before the PR". It is still in the diff.

## 4. The picture

- `.xv/picture.md:21`: add "`record` reaches `run` (a lazy import, for `run_suite`; `run` also reaches `record`)".
- `.xv/picture.md:23`, after "`record` owns the slice record": add that `xv record offer` can put a directed edit on an option, refused unless it fits one of the four kinds. Add that `xv record answer --pick` on that option makes the edit, commits only that file and the record, names the person in the message, runs the suite and the orders, and adds a packet line after the guardian.
- `.xv/picture.md:27`, "The maker and the cleaner record a move in their own names … A person's name reaches the record only through an answer at a stop": add that a directed test edit records a move in the person's name through `xv record answer --pick`.
- `.xv/picture.md:36`, "The watch edits it only when a person directs it, in its own commit naming that person": say whether a directed `doc` edit is how that happens, given that the `doc` kind currently admits `.xv/picture.md` (`scripts/record.py:334`).
- `.xv/picture.md:43`, the definition of an offer: add that an option may carry one directed edit.

## 5. The wall

- `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit`: should stay marked slice-only, which keeps it off the wall. It checked one `#132` line in `CHANGELOG.md` (removed hunk in `08d1417` at `@@ -1789,11`), and the record's `slice_only` entry was accepted by Sean.

Also checked: the 24 kept `DirectedEditTest` tests (`tests/test_record.py:1473-1790`). Each guards behavior that lasts, and none only restates another. The two brief-wording tests guard the brief's rule, which stays, rather than a one-time line. No test that was on the wall before the slice is made dead.

## Scenario misses

- amendment 1, item 3: "runs the suite and the standing orders and prints the verdict, as `xv step` does". `xv step` writes the verdict through `record.apply_verdict` (`scripts/run.py:720`; `.xv/picture.md:23`, "One function, `record.apply_verdict`, writes the stop…"). The directed path only prints it and exits 10 (`scripts/record.py:537-540` `v = orders.verdict(...)`, `emit(v, True)`, `sys.exit(10)`). A stop that fires after a directed edit is never written as an open stop, so `xv record offer` and `xv record answer` cannot act on it, and a send-back or `next` from the verdict is dropped (evidence: `scripts/record.py:537-540`; the red only checks the printed verdict, `test_after_the_edit_the_suite_and_the_orders_run_and_the_verdict_is_printed`; to: scenario)
- 2: "renaming a test or removing a test… Any other edit goes to an agent". The check that the old text is a test is `TEST_DECL` (`scripts/record.py:281`), which matches any `def`, so `def setUp(self):` or a helper passes as a "test". Two edits outside the four kinds get through. (a) A `test-remove` of `def setUp…` or a helper, or of only a test's `def` line, is accepted (`scripts/record.py:349`). Removing only the `def` line merges the body into the test above it and changes its assertions. (b) A `test-rename` of `def setUp(self):` to `def setup(self):`, or of `test_x` to `helper_x`, is accepted (`scripts/record.py:346-348`). That turns a test off and records it as a rename. Both change behavior, against point 6, "the edit changes no behavior" (evidence: `scripts/record.py:281`, `:346-349`; no red test covers a non-test declaration or a partial removal; to: scenario)
- 2: "a line in `CHANGELOG.md`… a line in a Markdown doc". For `changelog` and `doc`, the offer checks only that the old text is found exactly once (`scripts/record.py:331-344`). A multi-line old text, such as a whole `## Unreleased` section or a whole doc, is accepted, but the rename check refuses a newline (`:346`) (evidence: `scripts/record.py:331-344`; no red test covers a multi-line `changelog` or `doc` edit; to: scenario)

What `watch_first_green` asked about: a rename whose old name is a prefix of another test's name does not catch the longer name. `rename_in_record` compares the whole last dotted part (`scripts/record.py:499` `test.rsplit(".", 1)[-1] == old_name`).

## Door

**Door:** two-way. A revert removes the flags and the commit path, and the slice itself makes no directed edit. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..08d1417`
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `xv boundary --base 5d5e75fc7a7371d74a3884cfbae919785adbb4e7` (`.xv/slices/2026-11-05-directed-edit.boundary.md`)

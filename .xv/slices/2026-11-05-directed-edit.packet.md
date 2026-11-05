---
slice: 2026-11-05-directed-edit
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-05-directed-edit.md
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: The watch makes a directed change the person approved (#132), second pass

Needs a decision: none from two people. The shape is the one Sean set in the decision record: a new `scripts/suite.py`, imported by `record` and `run`. One scenario miss goes back to the scenario agent: a `test-remove` of a decorated test leaves the decorator behind, so it now decorates the next test. Three items for Sean: the packet line is written after the commit and stays uncommitted; the brief and the CHANGELOG line do not name the second amendment's refusals; and the Opus line in `.xv/config.yml` is still in the diff.

## The scenario

A stop option can carry a directed edit, given as exact old and new text, which the person approves word for word. There are four kinds: `changelog`, `test-rename`, `test-remove` (in `tests.paths`) and `doc`. `xv record answer --pick` makes the edit in its own commit, which names the person. A test edit is recorded as a move in the person's name, and a rename also updates the test's name in `slice_only` and `wall_recommendations`. Then the suite and the orders run. After the guardian has run, the packet gets a line and `next` does not go back to the guardian. Second amendment: `record` does not import `run`, because the suite run moves to `scripts/suite.py`. The `doc` kind refuses `.xv/` and `SKILL.md`. Changelog and doc edits may span lines but may not hold a blank line. Test kinds take only a whole test. A stop after the edit is written through `record.apply_verdict`.
May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. Replay: `cd tests && python3 -m unittest test_record.DirectedEditTest`. The record shows the red failing at `6f1e327` (68 failures, 1 error) and the suite green after the maker and after the cleaner (`checks.cleaner.suite: green`, 826 tests).

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Module added: `scripts/suite`. Touched: `scripts/record`, `scripts/run`, `scripts/suite`.
- Edges added: `scripts/record → scripts/suite` and `scripts/run → scripts/suite`. None removed. The earlier `record → run` edge is gone.
- Tables: none. Surface paths: none. Outbound: none added.
- Shape hints: "a module was added", "an edge between modules was added".

## What the suite asserts after

`DirectedEditTest` (`tests/test_record.py:1474` onward) asserts the following:
- An offer with an edit changes nothing until a person picks it.
- The offer refuses these edits:
  - an old text that is missing, found twice, or empty
  - a missing file, a kind that does not fit the file, or a kind not on the list
  - a missing flag, or an edit with no `--option` before it
  - a rename that changes more than the name, or a rename to or from a non-test (`setUp`, a helper)
  - a removal whose new text is not empty, or that is only part of a test
  - a `doc` edit under `.xv/` or to any `SKILL.md`
  - a changelog or doc edit that holds a blank line (multi-line edits with no blank line pass)
- A pick makes exactly the edit, in one commit that holds only that file and the record and is directed by the person.
- A test edit is a move in the person's name. A rename updates `slice_only` and `wall_recommendations` in that commit.
- The suite result is recorded (green or red). A stop after the edit is written to the record (`ready_to_merge` at `guardian`) and can be answered.
- After the guardian, the packet gets one line and `next` is not `guardian`. Before the guardian, no packet is written.
- `record` does not import `run`. Both import `suite`, and `suite` passes the slice base and id.
- The watch brief states the rule and has the new may-not line.

## 1. Shape

shape_change: accepted, by `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`. shape_breadth: narrow. The forecast expected `wide`, so this is not wider.

- **"a module was added" (`scripts/suite`): this changes the shape, and the decision accepted it.** The new module is `scripts/suite.py:1-30`, holding `shell`, `tests_timeout` and `run_suite`, moved verbatim from `scripts/run.py:45-68` at base. The decision's settled line says: "run_suite and its helpers move to scripts/suite.py".
- **"an edge between modules was added" (`record → suite`, `run → suite`): this changes the shape, and the decision accepted it.** The edges come from `scripts/record.py:21` `from suite import run_suite` and `scripts/run.py:34` `from suite import run_suite, shell, tests_timeout`. The decision says "record does not import run", and no `import run` remains in `record`.
- **`xv record answer` now edits a repo file, commits, and runs the suite and the orders.** This adds no edge (`git` already came from `xvlib`). At base, `record` ran only `git show` (`scripts/record.py:724` at base). Now it runs `git commit` (`scripts/record.py` hunk `@@ -419,9 +512,61 @@`, `make_directed_edit`). The first packet named this as a shape change. The decision refused only the `record → run` import, and it requires that "a stop after a directed edit is written through record.apply_verdict", which assumes the answer runs the orders. The commit is in Sean's amendment ("makes the edit and commits only that file and the record"). So I read it as accepted. If Sean does not, `shape_change` should be `yes`.

## 2. Pitch

pitch_contradiction: no. I checked against `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents…"). A directed edit is a person's own words, so it serves neither against. The first packet's concern was that a `doc` edit could reach `.xv/pitch.md` without a second person (`.xv/pitch.md:11`). That is closed: the code now refuses paths under `.xv/` (`scripts/record.py` `check_edit`: `not rel.startswith(XV_DIR + os.sep)`), and the test is `test_the_doc_kind_refuses_a_file_under_xv_and_any_skill_md`.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `DirectedEditTest.test_the_changelog_names_the_directed_edit`: `#132` appears under `## Unreleased` | removed in `08d1417` | slice-only: a one-time CHANGELOG wording check, accepted by Sean (`slice_only_marks`, pick 1) | Not forced; it is a slice-only removal |

Slice-only tests removed: `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit`. None were kept.
Against base, `tests/test_record.py` only adds lines (`@@ -1,3 +1,4 @@` adds `import ast`; `@@ -1468,3 +1469,500 @@` adds the class). `xv wall diff 2026-11-05-directed-edit` lists nothing changed, deleted, added or with fewer assertions since the wall baseline `6f1e327`. No moves were expected. `may_not_files` is empty.

Outside the tests: `.xv/config.yml` `@@ -34,6 +34,8 @@` still adds the `scenario:` line on Opus, marked "removed before the PR".

## 4. The picture

- `.xv/picture.md:21`: the counts "24 modules … `scripts/*.py` (21)" and "63 edges" go to 25 modules, 22 scripts and 65 edges. Add "`record` and `run` reach `suite`". `.xv/boundary-all.md` is now stale.
- `.xv/picture.md:23`:
  - Add that `suite` runs `tests.command` (`run_suite`, `shell`, `tests_timeout`) for `run` and `record` (`scripts/suite.py:1-30`).
  - Add that `xv record offer` can put one directed edit on an option. The offer refuses it unless it fits one of the four kinds: a whole test only for the test kinds, no blank line for changelog and doc, and no `.xv/` or `SKILL.md` for doc.
  - Add that `xv record answer --pick` makes the edit, commits that file and the record naming the person, runs the suite and the orders, and adds a packet line after the guardian (`scripts/record.py` hunk `@@ -419,9 +512,61 @@`, `make_directed_edit`).
  - In "One function, `record.apply_verdict`, writes … on `xv step`, `xv run` and `xv record packet`", add `xv record answer` after a directed edit.
- `.xv/picture.md:27`, "A person's name reaches the record only through an answer at a stop": add that a directed test edit records a move with `by` set to the person, through that answer.
- `.xv/picture.md:36`, "The watch edits it only when a person directs it, in its own commit naming that person": say this is not a directed `doc` edit, because that kind refuses `.xv/`.
- `.xv/picture.md:43`, the definition of an offer: add that an option may carry one directed edit.

## 5. The wall

- `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit` should stay marked slice-only, so it stays off the wall. It checked one `#132` line in `CHANGELOG.md` and was removed in `08d1417`. The record's `slice_only` entry is `accepted: true`.

## Scenario misses

- Amendment 2, item 4: "A `test-remove` must remove the whole test, its declaration and its body; the offer refuses a removal of only part of it." The problem is a decorated test (`@unittest.skip`, `@mock.patch`, `@pytest.mark…`). `is_whole_test` requires the old text's first line to match `TEST_DECL`, the `def` (`scripts/record.py` `check_edit` hunk: `if not old.endswith("\n") or not lines or not TEST_DECL.match(lines[0])`). So a removal that includes the decorator is refused. A removal of only the `def` and its body is accepted, because only the lines after the old text are checked. The decorator stays and now applies to the next test, which can skip it or patch it. That breaks point 6, "the edit changes no behavior". This repo's suite has no decorated tests, but adopters' suites do. Evidence: `scripts/record.py` `is_whole_test`; no red test has a decorated test. to: scenario.

## For Sean (not misses)

- **The packet line is never committed.** `make_directed_edit` commits the file and the record, then writes the packet line (`scripts/record.py` hunk `@@ -419,9 +512,61 @@`: `git(["commit", …])` runs before `with open(packet, "w")`). The packet is left dirty until some later commit picks it up. The amendment says the commit holds "only that file and the record" (amendment 1, item 3), so Sean must choose: a second commit, or the packet in the same commit.
- **The brief and the CHANGELOG line describe the first amendment only.**
  - `skills/watch/SKILL.md` `@@ -39,6 +39,14 @@` lists the refusals and says "prints the verdict". It does not say that `doc` refuses `.xv/` and `SKILL.md`, that a blank line is refused, that test kinds take only a whole test, or that a stop is written to the record.
  - The `CHANGELOG.md` line (`@@ -4,6 +4,7 @@`) has the same gaps. It also does not name `scripts/suite.py`.
  - Binding decision 1 (`.xv/picture.md:64`) asks for a CHANGELOG line for a brief change. The line exists but is out of date.
- **A rename only checks the name.** A rename of a test whose name is used elsewhere in the file (for example `self.test_x()`, or a skip list) is not checked. Nothing in the red covers this.

## Door

**Door:** two-way. A revert removes the flags, the commit path and `scripts/suite.py`, and the slice itself makes no directed edit. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`, and since the first packet, `git diff 24ced79..HEAD`
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `.xv/slices/2026-11-05-directed-edit.boundary.md`

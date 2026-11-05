---
slice: 2026-11-05-directed-edit
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-05-directed-edit.md
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: The watch makes a directed change the person approved (#132), third pass

Needs a decision: none from two people. The shape is still the one in the decision record. Three scenario misses go back:
- The packet line does not name the commit. Amendment 1, item 4 asks for it, and amendment 3, item 2 makes it impossible, so this needs Sean to amend the scenario.
- A rename onto a name the file already uses is accepted.
- The edit, the suite and the commit use the checkout the command runs in, not the slice's checkout.

For Sean: an unrecorded assertion drop, a kept slice-only test, and the Opus line in `.xv/config.yml`.

## The scenario

A stop option can carry one directed edit, as exact old and new text that the person approves word for word. There are four kinds: `changelog`, `test-rename`, `test-remove` and `doc`. `xv record answer --pick` makes the edit in its own commit, which names the person. A test edit is a move in the person's name, and a rename also updates `slice_only` and `wall_recommendations`. Then the suite and the orders run, and a stop is written through `apply_verdict`. After the guardian, the packet gets a line in the same commit.
- Amendment 2: `suite.py` holds the suite run, and `record` does not import `run`. A `doc` edit refuses `.xv/` and `SKILL.md`. A changelog or doc edit may not hold a blank line. Test kinds take only a whole test.
- Amendment 3: a removal takes the test's decorators with it, and one that leaves a decorator behind is refused. The packet line goes in the edit's commit. A rename is refused when the old name appears elsewhere in the file. The brief and the CHANGELOG line name every refusal.

May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. Replay with `cd tests && python3 -m unittest test_record`. On this pass at HEAD `52b3a68` it ran 180 tests, OK. The record has the red failing (`FAILED (failures=84, errors=2)`), and the whole suite green after the maker and after the cleaner (833 tests).

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Module added: `scripts/suite`. Touched: `scripts/record`, `scripts/run`, `scripts/suite`.
- Edges added: `scripts/record → scripts/suite` and `scripts/run → scripts/suite`. None removed.
- Tables: none. Surface paths: none. No new outbound calls.
- Shape hints: "a module was added" and "an edge between modules was added".

This pass, `git diff e71de17..HEAD`, changes only `scripts/record.py`, `skills/watch/SKILL.md`, `CHANGELOG.md`, `tests/test_record.py` and the record. It adds no module and no edge.

## What the suite asserts after

`DirectedEditTest` (`tests/test_record.py:1474` onward) asserts everything the second packet listed. The new tests add these:
- A decorated test is removed with its decorators, and a removal that starts at the `def` under a decorator is refused (`:1933`).
- After the guardian, the packet line is in the edit's commit (`:1990`).
- A rename is refused when the old name appears elsewhere in the file (`:1993`).
- The brief and the `#132` CHANGELOG line name every refusal and `scripts/suite.py`.

The packet-line test no longer asserts the commit sha (see Moved tests).

## 1. Shape

shape_change: accepted, by `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`. Its settled line says "record does not import run; run_suite and its helpers move to scripts/suite.py". shape_breadth: narrow. The forecast expected `wide`, so this is not wider.

- **"a module was added" (`scripts/suite`).** This changes the shape, and the decision accepted it. `scripts/suite.py:1-30` holds `shell`, `tests_timeout` and `run_suite`, moved verbatim out of `scripts/run.py` (`@@ -42,31 +43,6 @@`).
- **"an edge between modules was added".** This changes the shape, and the decision accepted it. The edges come from `scripts/record.py:21` `from suite import run_suite` and `scripts/run.py:34` `from suite import run_suite, shell, tests_timeout`. No `import run` remains in `record`.
- **The third pass is inside that shape.** The `record.py` hunks add `decorator_start` and rework `is_whole_test` and the rename check. They import nothing new.

## 2. Pitch

pitch_contradiction: no. I checked against these lines:
- `.xv/pitch.md:7`, "makes it easy … to vibe with discipline".
- `.xv/pitch.md:11`, where the pitch "changes when a second person agrees". A `doc` edit can't reach it: `check_edit` requires `not rel.startswith(XV_DIR + os.sep)`.
- `.xv/pitch.md:25`, "not for people or projects that will not trust agents".

A directed edit carries the person's own words, so none of these is broken.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `test_the_changelog_names_the_directed_edit`: `#132` is under `## Unreleased` | removed | slice-only, accepted by Sean | No. It is a slice-only removal |
| `tests/test_record.py` | `test_after_the_guardian_the_packet_gets_a_line_…`: the line holds `changelog`, `pat`, `shas[0][:7]` | the line holds `changelog`, `pat` | **No move recorded.** The only mention is the scenario report's summary: "the packet line can no longer hold its own commit's sha" | Amendment 3, item 2 forces it. The test now asserts less, and the dropped assertion is amendment 1, item 4's "and the commit" (see Scenario misses) |

Neither test was on the wall: `xv wall diff` lists nothing changed, deleted or with fewer assertions since baseline `e71de17`. The second row's evidence is `git diff e71de17..HEAD -- tests/test_record.py`, which removes `for word in ("changelog", "pat", shas[0][:7]):`.

Slice-only tests removed: `DirectedEditTest.test_the_changelog_names_the_directed_edit`. Kept: `DirectedEditTest.test_the_changelog_line_names_every_refusal_and_the_suite_module` (`tests/test_record.py:2082`). Sean accepted its slice-only mark, but the cleaner did not remove it, and no reason to keep it is on record.

`may_not_files` is empty. Outside the tests, `.xv/config.yml` `@@ -34,6 +34,8 @@` still has the Opus `scenario:` line, which is marked "removed before the PR".

## 4. The picture

- **`.xv/picture.md:21`:**
  - Change the counts to 25 modules, `scripts/*.py` (22) and 65 edges.
  - Add "`record` and `run` reach `suite`".
- **`.xv/picture.md:23`:**
  - Add that `suite` runs `tests.command` for `run` and `record` (`scripts/suite.py:23-30`).
  - Add that `xv record offer` can put one directed edit on an option, and refuses one that does not fit its kind. The refusals are listed in `skills/watch/SKILL.md` `@@ -39,6 +39,16 @@`.
  - Add that `xv record answer --pick` makes the edit, runs the suite and the orders, and commits the file, the record, and the packet line after the guardian, in the person's name (`scripts/record.py` hunk `@@ -419,9 +534,62 @@`, `make_directed_edit`).
  - In "One function, `record.apply_verdict`, writes … on `xv step`, `xv run` and `xv record packet`", add `xv record answer` after a directed edit.
- **`.xv/picture.md:27`, "A person's name reaches the record only through an answer at a stop":** add that a directed test edit records a move with `by` set to the person, through that answer.
- **`.xv/picture.md:36`, "The watch edits it only when a person directs it":** say this is not a directed `doc` edit, because that kind refuses `.xv/`.
- **`.xv/picture.md:43`, the definition of an offer:** add that an option may carry one directed edit.

## 5. The wall

- `tests/test_record.py` `DirectedEditTest.test_the_changelog_line_names_every_refusal_and_the_suite_module` should stay marked slice-only, so it stays off the wall. It checks one `#132` CHANGELOG line (`tests/test_record.py:2082-2087`), and Sean accepted the mark (`slice_only_marks`, answered 20:29:55).
- `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit` should stay marked slice-only. It was removed, and its `slice_only` entry is `accepted: true`.

## Scenario misses

- Amendment 1, item 4: "the file, the kind, who directed it, and the commit". The packet line is `- {file} ({kind}): directed by {by}` (`scripts/record.py` `make_directed_edit`) and names no commit. The red dropped `shas[0][:7]`. Amendment 3, item 2 puts the packet in that same commit, so the line cannot hold its own sha. One option: the line names the commit by its message instead. (evidence: `git diff e71de17..HEAD -- tests/test_record.py`, the removed `for word in ("changelog", "pat", shas[0][:7]):`; to: scenario) amend: yes
- Point 6, "the edit changes no behavior", and amendment 1, item 2, "a rename that changes more than the test's name". The rename check counts only the old name: `if len(re.findall(rf"(?<!\w){re.escape(name)}(?!\w)", text)) != 1`. A rename to a name already defined in the same class is accepted. Python keeps the later `def`, so one test silently leaves the suite. The suite stays green, and the move in the person's name keeps the wall quiet. (evidence: `scripts/record.py` `check_edit` hunk `@@ -288,10 +334,71 @@`; no red test renames onto an existing name; to: scenario)
- Point 3, "the watch makes exactly that edit, in its own commit". `cmd_answer` sets `root = repo_root()`, the checkout the command runs in, but `load` finds the record "in this checkout, or in the slice's worktree" (`scripts/xvlib.py:311-319`). So when the answer runs from the main checkout, `check_edit` and `make_directed_edit` read and write `os.path.join(root, file)` there, `run_suite(root, …)` tests that checkout, and `git commit` runs there with the record's path under `.xv/worktrees/<id>/`. The same function already writes the decision to `slice_root(path)` (`scripts/record.py:526`). Every `DirectedEditTest` call uses `cwd=self.wt`, so the red never runs the answer from the main checkout. I found this by reading the code and did not run it. (evidence: `scripts/record.py` `make_directed_edit` hunk `@@ -419,9 +534,62 @@`, `full = os.path.join(root, file)` and `git([...], root)`; to: scenario)

## Door

**Door:** two-way. A revert removes the flags, the commit path and `scripts/suite.py`, and the slice makes no directed edit itself. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. This pass: `git diff e71de17..HEAD`.
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `.xv/slices/2026-11-05-directed-edit.boundary.md`

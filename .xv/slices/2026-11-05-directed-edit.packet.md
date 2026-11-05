---
slice: 2026-11-05-directed-edit
shape_change: accepted
accepted_by: .xv/decisions/2026-11-05-2026-11-05-directed-edit.md
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: The watch makes a directed change the person approved (#132), fourth pass

Needs a decision: none from two people. The shape is still the one the decision record accepted. No scenario misses: amendment 4 closes the three misses from the third pass, and each fix has a test.

For Sean (not a stop):
- `xv record offer` still checks an edit against the checkout it runs in, not the slice's worktree (check 3, finding A).
- The brief and the CHANGELOG line do not name amendment 4's refusal, a rename onto a name already in use (finding B).
- The picture needs edits (check 4).

## The scenario

A stop option can carry one directed edit: exact old and new text, which the person approves word for word. There are four kinds: `changelog`, `test-rename`, `test-remove` and `doc`. `xv record answer --pick` makes the edit in its own commit, and the commit names the person. A test edit is recorded as a move in the person's name. A rename also updates `slice_only` and `wall_recommendations`. Then the suite and the orders run, and a stop is written through `apply_verdict`. If the guardian has already run, the packet gets a line in the same commit.

The amendments add these:
- `scripts/suite.py`, and `record` does not import `run`.
- `doc` refuses `.xv/` and `SKILL.md`.
- No blank lines in a `changelog` or `doc` edit.
- Test kinds accept only a whole test, decorators included.
- A rename is refused when its old name appears elsewhere in the file.
- Amendment 4: the packet line names no commit. A rename onto a name the file already uses is refused. The answer edits, runs the suite and commits in the slice's worktree, wherever it is run from.

May ignore: retiring a wall test (#120), a doc line that also needs a test, and edits outside the four kinds.

## The recording

None, because this is a feature. To replay, run `cd tests && python3 -m unittest test_record.DirectedEditTest`. At HEAD `8ac15d9` it ran 44 tests, OK. The whole suite (`python3 tests/run.py --jobs 4`) ran 836 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-05-directed-edit.boundary.md`, as given:
- Module added: `scripts/suite`. Touched: `scripts/record`, `scripts/run`, `scripts/suite`.
- Edges added: `scripts/record → scripts/suite` and `scripts/run → scripts/suite`. None removed.
- Tables, surface paths and outbound calls: none.

Since the last packet (`git diff bc974f0..HEAD`), only these changed:
- `scripts/record.py`: 9 lines.
- `tests/test_record.py`.
- `.xv/config.yml`: the slice-only Opus `scenario:` line is removed, as the third packet asked.
- The record files.

## What the suite asserts after

`DirectedEditTest` (`tests/test_record.py:1474` onward) asserts everything the earlier packets listed. The fourth pass adds these:
- The packet line is exactly `- CHANGELOG.md (changelog): directed by pat`, with no sha and no "commit".
- A rename onto a test in the same class, a test in another class, or a name used as an attribute is refused.
- A rename to a name that only begins another name is accepted.
- An answer run from the main checkout edits the file, runs the suite (red, from a failing test that exists only in the worktree) and commits in the slice's worktree. The main checkout's file, HEAD and status stay untouched.

## 1. Shape

shape_change: accepted, by `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`. It settled: "record does not import run; run_suite and its helpers move to scripts/suite.py". shape_breadth: narrow. The forecast expected `wide`, so this is not wider.

- **Hint "a module was added" (`scripts/suite`).** It changes the shape, and the decision accepted it. `scripts/suite.py` imports only `os` and `subprocess`.
- **Hint "an edge between modules was added".** It changes the shape, and the decision accepted it.
  - `scripts/record.py` adds `+from suite import run_suite`.
  - `scripts/run.py` adds `+from suite import run_suite, shell, tests_timeout`.
  - No `import run` is added to `record`.
- **This pass stays inside that shape.** The `scripts/record.py` hunks `@@ -395,6 +395,8 @@`, `@@ -485,7 +487,8 @@` and `@@ -564,7 +567,7 @@` change no import.

## 2. Pitch

pitch_contradiction: no. I checked against three lines:
- `.xv/pitch.md:7`, "makes it easy … to vibe with discipline". A directed edit carries only the person's approved words, so it fits.
- `.xv/pitch.md:11`, where the pitch "changes when a second person agrees". A `doc` edit cannot reach it: `check_edit` requires `not rel.startswith(XV_DIR + os.sep)` (`scripts/record.py:376`).
- `.xv/pitch.md:25`, "not for people or projects that will not trust agents". The slice neither adds nor removes that trust.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` | `test_the_changelog_names_the_directed_edit`: `#132` is under `## Unreleased` | removed | slice-only, accepted by Sean | No. It is a slice-only removal |
| `tests/test_record.py` | `test_the_changelog_line_names_every_refusal_and_the_suite_module`: the `#132` line names every refusal | removed (cleaner, 22:37:01) | slice-only, accepted by Sean | No. It is a slice-only removal |

**Slice-only removals:** both are removed: `DirectedEditTest.test_the_changelog_names_the_directed_edit` and `DirectedEditTest.test_the_changelog_line_names_every_refusal_and_the_suite_module`. None is kept.

The evidence agrees:
- `xv wall diff` (baseline `23c54ff`) shows `tests/test_record.py` going from 386 to 385 assertions. The `-` hunk at `@@ -2144,13 +2145,6 @@` accounts for it: the second row.
- No test that existed before the slice changed: `tests/test_record.py` has only two hunks since the base, `@@ -1,3 +1,4 @@` (an import) and `@@ -1468,3 +1469,687 @@` (the new `DirectedEditTest`), and `git diff --numstat` gives `685 0`.
- The one other change since the baseline is to a red test the slice wrote. In `@@ -2043,7 +2043,8 @@`, `self.commit_all(what)` becomes `if text != base: self.commit_all(what)`. The scenario agent made it after Sean answered `maker_stopped` (log 22:20:08, 22:21:28). The `self.refused(...)` assertion still runs for every case, so the test asserts no less.

`may_not_files` is empty, and the diff changes no may-not file outside the slice's scope.

**Finding A, for Sean.** `cmd_offer` checks an edit against the checkout it runs in. The answer checks it against the slice's worktree.
- Evidence: `scripts/record.py:415-419`, `root = repo_root()` … `check_edit(root, config, i, o["edit"])`. Compare `scripts/record.py:490-491`, `edit_root = slice_root(path)`.
- Failure: an offer run from the main checkout reads the main checkout's file, because `check_edit` opens `os.path.join(root, file)` (`scripts/record.py:368`, `full = os.path.normpath(os.path.join(root, file))`). A rename of a test, or a change to a CHANGELOG line, that exists only on the slice branch is refused there as "found 0 times". An old text that differs between the two checkouts can pass the offer and then be refused at the answer.
- No test covers this: every offer in the red runs with `cwd=self.wt` (`tests/test_record.py:1520-1521`, `return self.xv("record", "offer", "s1", ...`).
- The record's `watch_first_green` runs the pick from the main checkout (`.xv/slices/2026-11-05-directed-edit.md:13`, "`xv record answer s1 --pick 1` run outside the worktree"). No scenario line says where the offer reads, so this is not a scenario miss.

**Finding B, for Sean.** The brief and the CHANGELOG line do not name amendment 4's refusal or its worktree rule.
- Evidence: the brief's "The offer also refuses these." paragraph (`skills/watch/SKILL.md` `@@ -39,6 +39,16 @@`) and the `#132` line in `CHANGELOG.md` `@@ -4,6 +4,7 @@`. Neither names "a rename onto a name already used in the file" (`scripts/record.py:398-399`), or that the answer works in the slice's worktree.
- Amendment 3, item 4 asked them to name the refusals "of both amendments", so this is not a miss. But the brief's list now reads as complete, and it is not. The CHANGELOG test that would have caught it is gone, because it was slice-only (`@@ -2144,13 +2145,6 @@`, `-    def test_the_changelog_line_names_every_refusal_and_the_suite_module(self):`).

## 4. The picture

- **`.xv/picture.md:21`:** change "24 modules … `scripts/*.py` (21)" to 25 and 22, and "63 edges" to 65, and add "`record` and `run` reach `suite`".
- **`.xv/picture.md:23`:**
  - Add that `suite` runs `tests.command` for `run` and `record` (`scripts/suite.py`).
  - Add that `xv record offer` can put one directed edit on an option and refuses one that does not fit its kind (`scripts/record.py:360-401`).
  - Add that `xv record answer --pick` makes the edit, runs the suite and the orders, and commits the file, the record and, after the guardian, the packet line. It does this in the slice's worktree, in the person's name (`make_directed_edit`, `scripts/record.py:555-593`).
  - In "One function, `record.apply_verdict`, writes … on `xv step`, `xv run` and `xv record packet`", add `xv record answer` after a directed edit (`scripts/record.py:574`).
- **`.xv/picture.md:27`, "A person's name reaches the record only through an answer at a stop":** add that a directed test edit records a move with `by` set to the person, through that answer (`scripts/record.py:565-566`).
- **`.xv/picture.md:36`, "The watch edits it only when a person directs it, in its own commit naming that person":** say that this is not a directed `doc` edit, because that kind refuses `.xv/` (`scripts/record.py:376`).
- **`.xv/picture.md:43`, the definition of an offer:** add that an option may carry one directed edit.

Checked against "Decisions that bind":
- `.xv/picture.md:64` (1) holds: the brief and its may-not list changed, there is a `CHANGELOG.md` line, and the decision is by Sean, solo, under `seats.two_people: solo`.
- `.xv/picture.md:74` (11) holds: `make_directed_edit` exits 10 on a stop (`scripts/record.py:592-593`).

## 5. The wall

- `tests/test_record.py` `DirectedEditTest.test_the_changelog_line_names_every_refusal_and_the_suite_module` should stay marked slice-only, so it stays off the wall. It checked one `#132` CHANGELOG line. The cleaner removed it (`@@ -2144,13 +2145,6 @@`), and its `slice_only` entry is `accepted: true`.
- `tests/test_record.py` `DirectedEditTest.test_the_changelog_names_the_directed_edit` should stay marked slice-only. It was removed, and its `slice_only` entry is `accepted: true`.

## Scenario misses

None. I checked each point and amendment against the code and the red.

The third pass's three misses are closed. The packet line is closed by amendment 4, item 1 and `scripts/record.py:584` (`+ f"- {file} ({kind}): directed by {by}\n"`). The rename onto a used name is closed by `scripts/record.py:398-399` (`if re.search(rf"(?<!\w){re.escape(names[1])}(?!\w)", text):`). The worktree miss is closed by `scripts/record.py:490-491` (`edit_root = slice_root(path)`), which is passed on at `:541`. Each has its own fourth-pass test (see "What the suite asserts after").

I read binding decisions 1 to 15 (`.xv/picture.md:64-78`). The slice breaks none of them.

## Door

**Door:** two-way. A revert removes the flags, the commit path and `scripts/suite.py`. The slice makes no directed edit itself. **Blast radius:** watch. `skills/watch/SKILL.md` and `xv record` reach every adopter once released.

## Raw data

- Slice record: `.xv/slices/2026-11-05-directed-edit.md`
- Decision: `.xv/decisions/2026-11-05-2026-11-05-directed-edit.md`
- Diff: `git diff 5d5e75fc7a7371d74a3884cfbae919785adbb4e7..HEAD`. This pass: `git diff bc974f0..HEAD`.
- Wall: `xv wall diff 2026-11-05-directed-edit`
- Boundary: `.xv/slices/2026-11-05-directed-edit.boundary.md`

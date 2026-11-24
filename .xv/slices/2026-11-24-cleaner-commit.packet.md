---
slice: 2026-11-24-cleaner-commit
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 2
expected_moves: 0
door: two-way
blast_radius: small
---

# Packet: The watch commits the cleaner's work, as it does the maker's (#206)

No two-person stop fires: no shape change, no pitch contradiction, every scenario line is met.
For Sean, as the person who set the work going:
the change edits the cleaner's brief and its may-not list, which binding decision 1 says needs two people and a CHANGELOG line (`.xv/picture.md:336`).
The CHANGELOG line is there but names nobody (`CHANGELOG.md:7`), and `CHANGELOG.md:3` says "A version line without two names is a draft".
Neither fixed field below routes this to two people, so getting the second name is on you.
Also yours: two behaviour notes on the commit step (check 1), one picture edit (check 4), two wall marks (check 5).

## The scenario

The watch commits the cleaner's work, as it does the maker's (#206).

1. The cleaner's brief says to leave its changes uncommitted, because the watch commits them after its checks. Its may-not list has "Commit, merge, or push".
2. The cleaner still records each test move with `xv record move`. The brief says the wall check after the step stops on a move with no record, not the pre-commit hook.
3. `cleaner_commit` names the commit `xv step` makes after the cleaner (`xv(<id>): record the cleaner's pass`), and stays empty when the cleaner changed nothing. The report has no `commit` field. A report that still sends one is not refused.
4. README, the docs and the picture no longer say the cleaner commits. New decision 94 says the watch commits each step's work. Decision 7 stays as history.
5. A line in `CHANGELOG.md`.

May ignore: old records where `cleaner_commit` is empty, and harnesses with no allow-list.

## The recording

None (a defect started from words). Replay the red: `cd tests && python3 -m unittest test_cleaner_commit`.
At the base, 13 of 16 failed (record `checks.test-writer.red_output`).
At HEAD: 15 tests, OK (I ran it). Whole suite: `python3 tests/run.py`, 1501 tests, OK (I ran it).
The record's `watch_before_merge` still applies: run one slice with a real cleaner and check that its edit stays uncommitted until `xv(<id>): record the cleaner's pass`.

## The boundary diagram

From `.xv/slices/2026-11-24-cleaner-commit.boundary.md`:
- Modules touched: `scripts/record`, `scripts/run`.
- Added or removed: none.
- Edges added or removed: none.
- Outbound calls added: none.
- Tables: none. Surface paths: none.
- Shape hints: none.

## What the suite asserts after

- When a cleaner leaves an edit uncommitted, `xv step cleaner` commits it as `xv(s1): record the cleaner's pass` and leaves a clean tree. `cleaner_commit` names that commit.
- When the cleaner changes nothing, `cleaner_commit` stays empty and HEAD does not move.
- A report that sends `commit: <sha>` is not refused, and the sha is not stored.
- The cleaner brief says "uncommitted" and "the watch commits", and its May not section has "- Commit, merge, or push.". The brief still names `xv record move`, names the "wall check", and no longer mentions the pre-commit hook or "Commit your fix". Its report example has no `"commit"`.
- No line of README, `docs/briefs.md`, `docs/core.md`, `docs/slice-record.md`, `docs/harness-notes.md` or `.xv/picture.md` says the cleaner commits. The `cleaner_commit` row says "watch".
- A decision numbered above 93 says the watch commits each step's work, and decision 7 still says "the cleaner commits its own fix".
- Old tests: they assert the same things. `tests/fake_agent.py` gained a new way for the fake cleaner to leave its edit (check 3).

## 1. Shape

shape_change: no. shape_breadth: narrow, which matches the forecast's `narrow`.

- Diagram: no module, edge, table or surface was added or removed, and there are no shape hints (`.xv/slices/2026-11-24-cleaner-commit.boundary.md`, "Shape hints: none").
  The new git call in `record.load` (`scripts/record.py:81`) uses `subprocess`, which `record` already uses for git (`scripts/record.py:287`, `scripts/record.py:909`). It is not a new dependency.
- The agent set and the step order stay as they were. Commits move from the cleaner to `commit_step` (`scripts/run.py:1417-1421`), and the watch already owns git for the other steps (`docs/decisions.md:16`, decision 7). This fits the current shape.
- Note for the person: when the cleaner changes nothing, the watch no longer commits the step's record edits (spend, checks, log) (`scripts/run.py:1417-1420`).
  The hunk:
  `if agent == "cleaner" and not checks.get("committed"): ... if not code_changed: return`.
  Before the slice, `commit_step` always committed them as `record the cleaner's pass`. Now they stay uncommitted in the worktree until the inspector's `packet` commit, or, if the cleaner step stops, until a person's answer commits them.
  The red forces this: `tests/test_cleaner_commit.py:60` asserts `self.head() == before`.
  The scenario only asks that `cleaner_commit` stay empty (outcome 3), so a record-only commit with another subject would also meet it. Your call whether a dirty record between steps is acceptable.
- Note for the person: nothing checks that the cleaner obeyed its new "Commit, merge, or push" may-not line.
  `checks["committed"]` is still computed (`scripts/run.py:1220`), but only `commit_step` reads it. If a cleaner commits anyway, the watch then commits only the record under `record the cleaner's pass`, and `cleaner_commit` names that record-only commit, not the fix.
  The old path still exercises this: `tests/fake_agent.py:181-185` (`FAKE_CLEANER_COMMITS`) with `tests/test_from_build.py:850-852`, which checks only that `cleaner_commit` is set.
  The maker's may-not line has the same status, so this is a gap the cleaner now shares, not a new kind of gap.
- `record.load` now runs `git log` on each load of a record that has a cleaner spend row and an empty `cleaner_commit` (`scripts/record.py:71-72`). Each load-and-save then writes the result back.
  There are 32 `load` call sites in `scripts/`. Old records with an empty field are in the may-ignore list, so this is a cost to watch, not a miss.

## 2. Pitch

pitch_contradiction: no.
I checked the change against "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`) and against "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`).
Moving the commit from the cleaner to the watch serves neither a new user nor a new purpose, and it breaks no promise the pitch makes.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py:186-189, 226-227` | The fake cleaner's report sent `commit=None`. It could only commit its edit (`FAKE_CLEANER_COMMITS`). | `commit=os.environ.get("FAKE_CLEANER_REPORT_COMMIT")`, which is `None` when unset, so old tests get the same report. New `FAKE_CLEANER_LEAVES` edits `pantry/store.py` without committing. | Sean Kennedy, answer 1 to `unrecorded_move`: points 1 and 3 need a cleaner that leaves its edit uncommitted, and a report that still sends `commit` | Yes. Outcomes 1 and 3 need both paths. It is a fixture, not an assertion, so nothing asserts less. |
| `tests/test_cleaner_commit.py:133-140` (at `f4b3ce3`) | `TheChangelogTest`: the Unreleased section names #206, the cleaner and "watch commits" | removed | cleaner: slice-only, checks one CHANGELOG line | Yes, as a slice-only removal. Assertions 30 → 28 (`xv wall diff`). |

Slice-only tests removed: `tests/test_cleaner_commit.py::TheChangelogTest.test_an_unreleased_line_says_the_watch_commits_the_cleaners_work`. Kept: none.

`may_not_files_needed` allowed `.xv/picture.md` for the maker. The maker did not change it: `git diff d4011e47..HEAD --stat` lists no `.xv/picture.md`, and the picture test passes without an edit. There are no unrecorded moves: `xv wall diff` lists only `tests/test_cleaner_commit.py`, which is recorded.

## 4. The picture

No picture line says the cleaner commits (`tests/test_cleaner_commit.py` `test_no_readme_doc_or_picture_line_says_the_cleaner_commits` passes). The shape section is incomplete in two places:

- `.xv/picture.md:54` describes `record` as owning the slice record. It does not say that `record` now finds `cleaner_commit` from git history (`scripts/record.py:71-83`). Proposed line, after line 54:
  `  `record.load` fills an empty `cleaner_commit` by finding the slice's `xv(<id>): record the cleaner's pass` commit between `base` and HEAD (`record.cleaner_pass_commit`).`
- The picture's shape section (`.xv/picture.md:27`) does not say which commit the watch makes after each step (`scripts/run.py:1412-1421`), or that the cleaner commits nothing. Proposed lines, in the shape list near line 92:
  `- The watch commits each step's work, the cleaner's too (`run.commit_step`, decision 94).`
  `  After the cleaner it commits only when a file outside `.xv/` changed; otherwise HEAD stays and the record's edits wait for the next commit.`

## 5. The wall

- `tests/test_cleaner_commit.py`, `TheDocsDoNotSayTheCleanerCommitsTest.test_the_readme_no_longer_says_the_pre_commit_hook_refuses_the_cleaners_unrecorded_move`: mark slice-only.
  It asserts that one old README sentence is gone. `test_no_readme_doc_or_picture_line_says_the_cleaner_commits` already covers that sentence, because its pattern includes `the cleaner is the one worker that commits` (`tests/test_cleaner_commit.py:93-94`). So this test only restates the other one.
- `tests/test_cleaner_commit.py`, `TheCleanerBriefTest.test_the_brief_no_longer_tells_the_cleaner_to_commit_its_fix`: mark slice-only.
  It asserts that three old phrasings are gone (`"commit the fix"`, `"Commit your fix"`, `"make it right` and one line per rule"`), which guards a one-time wording change.
  The lasting rule is held by `test_the_may_not_list_has_commit_merge_or_push` and `test_the_brief_says_to_leave_changes_uncommitted_for_the_watch_to_commit_after_its_checks`.
- I found no old wall test that the scenario makes dead. `tests/test_from_build.py:852` still asserts something true: `cleaner_commit` is set after a cleaner that committed.

## Door

**Door:** two-way. A revert restores the old brief and commit step, and no data migrates. `record.load` back-fills `cleaner_commit` only when the field is empty. **Blast radius:** small.

## Raw data

- Slice record: `.xv/slices/2026-11-24-cleaner-commit.md`
- Diff: `git diff d4011e47fc52d2c5fbf8fdb6b80f6e0543cbf462..3421d2acab71c7be98c0cb60c482bfa5d8d22000`
- Wall: `xv wall diff 2026-11-24-cleaner-commit`
- Boundary: `.xv/slices/2026-11-24-cleaner-commit.boundary.md` (`xv boundary --base d4011e47fc52`)
- Red at HEAD: `cd tests && python3 -m unittest test_cleaner_commit`, 15 tests, OK.

## Directed edits after the inspector

- CHANGELOG.md (changelog): directed by Sean Kennedy

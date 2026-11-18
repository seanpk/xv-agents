---
slice: 2026-11-18-report-tree
shape_change: no
pitch_contradiction: no
change_misses_scenario: yes
picture_change: yes
shape_breadth: narrow
moved_tests_count: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: What an agent reports is checked against the tree (#183)

No stop for two people: no shape change and no pitch contradiction.
This re-pass reviews only pairing 1 (`cb2b7cab0bfb..HEAD`): seven lines in `record.test_names` and three tests.
The last packet's miss is met: every `::` or `#` name is now cut at the last separator, and a part that is not a plain name stops as "could not be read".
`Red::`, `Red#`, `Red::test_x[1]` and `tests/milk-red.py::Red::test_milk_today` now stop while the test is there.
One decision 12 miss is left, in the prose path, and it predates the pairing: a slice-only move whose assertion is a sentence that does not end in a plain name and holds no `::` or `#` keeps the whole sentence as its one name, so the check passes without looking. My earlier packets did not name it. It sends the slice back.
The originator gets four picture edits to accept; edit 4 is updated for this pass. No wall recommendation.

## The scenario

What an agent reports is checked against the tree.

1. After the cleaner step, an accepted `slice_only` test still in its file stops the step with `removal_not_made` for the originator, naming the file and the test. The exception is a test the cleaner's report says it kept, with the reason. A removal that was made passes.
2. After any step, a recorded move marked `--slice-only` or `--deleted` whose test or file is still there stops with `removal_not_made`, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last block of the whole run through the harness's reader before it stops with `no_report`. A run with no block anywhere still stops with `no_report`.
4. A CHANGELOG.md line.
5. (amended) The cleaner's report has a `kept` list, and the cleaner's brief tells it to write that list. Only a test in `kept` with a `why` is exempt.
6. (amended) The check finds a test by its name anywhere in its file (`def`, `it("…")` title, `Class > test`). A name it cannot read stops with `removal_not_made`; it never passes (decision 12).
7. (amended) For Claude Code, the fallback in outcome 3 reads the session transcript, found by the result's `session_id`.

May ignore: old slice records; a harness whose reader cannot see earlier messages.

## The recording

None: this defect starts from words.
Replay: `cd tests && python3 -m unittest test_run.RemovalNotMadeTest test_run.ClaudeWholeRunReportTest`.
I ran it on HEAD: 32 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-18-report-tree.boundary.md`, as given.
Modules touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/spend`. Nothing added or removed: no modules, edges, tables, surfaces or outbound calls. No shape hints.
This pass changes only `scripts/record.py:893-903`.

## What the suite asserts after

What the last packet listed still holds. Pairing 1 adds:
- An accepted slice-only test named `tests/milk-red.py::Red::test_milk_today` (a `-` in the path) stops the cleaner with `removal_not_made`, naming `tests/test_red.py` and `test_milk_today`, while the test is there.
- An accepted slice-only entry `Red::` stops the cleaner, naming `tests/test_red.py`, with "could not be read" in the question.
- A slice-only move whose assertion is the sentence `removed tests/milk-red.py::Red::test_milk_today as slice-only` stops the next step while the test is there.

These three tests were written in the pairing by the session that wrote the code, so they are not blind.
I read each against the code: each sets an input and asserts the stop the watch prints; none restates `test_names` or checks itself.
None of them checks the pass side (the dash form passing once the test is removed); the `Red::` and `Red#` pass tests from the last pass cover the cut itself (`tests/test_run.py:2279-2285`).

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The diff is `scripts/record.py:897-903`: a prose word pick, a `re.split` on every `::` or `#` name, and a `re.fullmatch` that returns `[]` for a part that is not a plain name. No import, edge, module, table or surface. Inside the current shape.
- The forecast's `shape_note` says the change "turns wide only if the reader change reaches more than the claude harness" (`.xv/slices/2026-11-18-report-tree.md:13`). The reader change reaches Claude Code, codex and opencode, as the last packet said; I call it narrow because the boundary picture shows no added or removed edge (`.xv/slices/2026-11-18-report-tree.boundary.md`).
- The cleaner's proposal to reuse `names.COVERED_SEPARATOR` (`scripts/names.py:10`) is still open. The pairing kept a pattern of its own (`scripts/record.py:899-900`), so the repo still has three ways to read a test name (`.xv/picture.md:47`).

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code").
A removal check that stops on a name it cannot read serves the first line. The pitch says nothing else about this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` | at the first packet, `FAKE_NO_REPORT` printed one plain line | with `FAKE_EARLIER_REPORT` also set, it prints two codex `agent_message` events with no block | the move on 2026-11-18T04:04:25 names `FAKE_EARLIER_REPORT` as a mode "off unless set". Unchanged this pass. | Yes, as before. |
| `tests/test_run.py` | `RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check` | removed | "checks one CHANGELOG line, a one-time wording change" (cleaner, `slice_only`). Unchanged this pass. | Yes, as before. |

Slice-only tests removed: `tests/test_run.py::RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check`. Kept: none.
Pairing 1 changes no old test: `git diff cb2b7cab0bfb..HEAD -- tests/test_run.py` only adds three tests at `tests/test_run.py:2287-2302`.
`xv wall diff 2026-11-18-report-tree` (baseline `58cf9c6`): changed `tests/test_run.py`, 538 to 542 assertions; deleted, added and `fewer_assertions` empty. `may_not_files_needed`: none.

## 4. The picture

Edits 1-3 are unchanged from the last packet. Edit 4 is updated for this pass.

1. `.xv/picture.md:29` says "the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`". Replace that clause with:
   `the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`, or, when that message has none, from the last earlier `agent_message` that has one (`record.extract_run_report`)`
2. Proposed line after `.xv/picture.md:29`, indented two spaces:
   `For Claude Code, whose `--output-format json` holds only the last message, `record.extract_run_report` reads the earlier messages from the session transcript that the result's `session_id` names (`spend.claude_transcript`, `spend.claude_session_texts`).`
3. Proposed lines after `.xv/picture.md:63`, indented two spaces:
   `After every `xv step`, and after `xv record report` for any agent except a scenario on a slice from a build, `record.removals_not_made` looks in the tree for each removal the record names; `removal_not_made` then stops for the originator, naming what is still there.`
   `After the cleaner, that covers each accepted `slice_only` test, unless the cleaner's report lists it under `kept` with a `why`.`
   `After any step, it covers each move marked `slice_only` or `removal_named` whose test is still in its file, and each move marked `deleted` whose file is still there.`
   `xv record move --slice-only` marks the move `removal_named`, and `--deleted` marks it `deleted`.`
   `A name the check cannot read is listed as "the test name could not be read", and that stops too.`
4. `.xv/picture.md:47` names `names_test` as "the shared test-name matcher". This change adds another. Proposed lines after `.xv/picture.md:47`, indented two spaces:
   `The removal check reads names with `record.test_names`, which keeps the part after the last `>`, the part after the last `::` or `#`, and the last `.` part of a dotted name.`
   `A part after `::` or `#` that is not a plain name cannot be read, and the check stops on it.`
   `It finds names with `record.test_still_there`, which matches a name as a whole word anywhere in its file.`

## 5. The wall

No recommendation.
I looked at the three new tests at `tests/test_run.py:2287-2302`. Each guards an input the last packet named as a miss (a `-` in the path, an empty part after `::`, a `::` name inside a prose assertion). None restates an older test: the older `::` tests use only names the old pattern matched (`tests/test_run.py:2263-2285`).

## Scenario misses

- Amendment 6 and decision 12: a slice-only move whose assertion is prose with no `::` or `#` and no plain last word passes without being checked. Decision 12 says a check whose input "cannot run stops for a person; it never passes" (`.xv/picture.md:340`). Traced on `scripts/record.py:892-909` with the assertion `removed Red.test_milk_today as slice-only`, the same sentence shape as the pairing's new test (`tests/test_run.py:2299-2300`) with a dotted name in place of the `::` one. No word holds `::` or `#`, so `seg` stays the whole sentence (`:897-899`). The last word `slice-only` is not `\w+`, so no short name is added (`:906-908`). `names` is the whole sentence, which is never in the file, so `test_still_there` returns false and `removals_not_made` passes while `test_milk_today` is still there. `removed Red.test_milk_today.` (a full stop) falls through the same way. A `#` used in prose for something other than a name picks the wrong word: `removed Red.test_milk_today for #183` reads `183`, which is not in the file, so it passes too (`:897-903`). This predates the pairing; the pairing's prose line only handles sentences that hold `::` or `#`. The cleaner's brief asks for `--assertion "<the test>"` (`skills/cleaner/SKILL.md:39`), so a sentence is off-brief, but decision 12 also says "Read-only agents are checked, not trusted" (`.xv/picture.md:342`), and `prose=True` exists because the assertion may be a sentence (`scripts/record.py:950`). I traced this by reading the code; the commands I may run allow no probe that does not edit the tree. (evidence: `scripts/record.py:892-909`, `:950`; the red's prose tests use only `Red.test_milk_today` alone, whose last word is a plain name after the `.` split, or a `::` sentence, `tests/test_run.py:2203`, `:2299`; to: scenario)

For the person, not a miss: as the last packet said, a prose assertion such as "removed the CHANGELOG test" adds `test`, which is in almost every test file, so the step stops for nothing. That error stops; it never passes.

## Door

**Door:** two-way. A revert removes the order, the reader fallback, the brief's `kept` field and the name cut. The record additions, `deleted` and `removal_named` on a move, are optional keys older code ignores. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-18-report-tree.md`
- Diff: `git diff 5c2600c69d4d50853dcd288bd6278c48bd808657..HEAD`; this pass: `git diff cb2b7cab0bfb..HEAD` (commits `5422f07`, `5fbdd72`)
- Wall: `xv wall diff 2026-11-18-report-tree` (baseline `58cf9c6`)
- Boundary: `xv boundary --base 5c2600c69d4d50853dcd288bd6278c48bd808657` (`.xv/slices/2026-11-18-report-tree.boundary.md`)
- Red on HEAD: 32 tests, OK. Whole suite on HEAD: `python3 tests/run.py --jobs 4`, 1383 tests, OK.

## From the cleaner

- Shape proposal, still open: share the item/part event parsing between `extract_report` and `extract_run_report` in `scripts/record.py`.
- Shape proposal, still open: have `test_names` reuse `names.COVERED_SEPARATOR` for the `::` and `#` forms instead of its own pattern.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: Sean picked option 1 at change_misses_scenario: decision 12, a :: or # name the check cannot read must stop, not pass; a small fix in test_names with two tests, then a guardian re-pass. Commits: 5422f07f5f, 5fbdd7272a. Resumed at guardian. Spend: 10091 tokens (in 10, out 4048, cache write 6033; cache read 465550 not counted), 5 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_run.py.

## From the cleaner

- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py; it needs a shared reader and a rework of extract_report, so it is left for the packet.
- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py (needs a shared reader and a rework of extract_report).
- Shape proposal, for people: Have test_names in scripts/record.py reuse names.COVERED_SEPARATOR for the `::`/`#` forms instead of its own regex; it changes how names are cut, so it is not a cleanup.

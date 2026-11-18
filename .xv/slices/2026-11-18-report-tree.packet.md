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
This re-pass reviews only the changes after the second packet (`e27be006ebd4..HEAD`).
That change adds two lines to `record.test_names` and six tests.
The last packet's miss is met for the forms it named: `Red::test`, `Red#test`, `file::test` and `file::Class::test` are now found.
One narrower decision 12 miss is left. A `::` or `#` name that the new pattern does not match keeps its whole text. That text is never in the file, so the check passes. It sends the slice back.
The originator also gets four picture edits to accept. One of them is updated for this change. This pass makes no wall recommendation.

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
The scenario agent recorded this pass's red as failing on `test_a_slice_only_test_named_with_class_and_double_colon_is_found_still_there` (record `red.failure`).
I ran it on HEAD: 29 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-18-report-tree.boundary.md`, as given.
Modules touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/spend`. Nothing was added or removed: no modules, edges, tables, surfaces or outbound calls. No shape hints. This pass changes only `scripts/record.py`, at lines 896-897.

## What the suite asserts after

What the last packet listed still holds. This pass adds the following:
- An accepted slice-only test named `Red::test_milk_today`, `Red#test_milk_today`, `tests/test_red.py::Red::test_milk_today` or `tests/test_red.py::test_milk_today` stops the cleaner with `removal_not_made` while the test is in `tests/test_red.py`. The stop names that file and `test_milk_today`.
- With the `Red::` and `Red#` forms, the cleaner passes once the test is removed.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- This pass's diff is `scripts/record.py:896-897`: a `re.fullmatch` and a `re.split` inside `test_names`. It adds no import, edge, module, table or surface. It is inside the current shape.
- The last packet's note on the forecast still holds. Its `shape_note` said the change "turns wide only if the reader change reaches more than the claude harness". The reader change reaches Claude Code, codex and opencode. I call it narrow because nothing in the boundary moved.
- The cleaner has a new shape proposal: `test_names` could reuse `names.COVERED_SEPARATOR` (`scripts/names.py:10`) instead of its own pattern. With `xvlib.names_test`, `names.covered_name_found` and now `record.test_names`, the repo has three ways to read a test name (`.xv/picture.md:47`).

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code").
Finding more test-name forms in the removal check serves the first line. The pitch says nothing else about this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` | at the first packet, `FAKE_NO_REPORT` printed one plain line | with `FAKE_EARLIER_REPORT` also set, it prints two codex `agent_message` events with no block | the move recorded on 2026-11-18T04:04:25 names `FAKE_EARLIER_REPORT` as a mode "off unless set". It did not change in this pass. | Yes, as the last packet said. |
| `tests/test_run.py` | `RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check` | removed | "checks one CHANGELOG line, a one-time wording change" (cleaner, `slice_only`). It did not change in this pass. | Yes, as the first packet said. |

Slice-only tests removed: `tests/test_run.py::RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check`. Kept: none.
This pass changes no old test. The diff to `tests/test_run.py:2263-2285` only adds six tests.
I ran `xv wall diff 2026-11-18-report-tree` against the new baseline `58cf9c6`. Changed, deleted, added and `fewer_assertions` are all empty. `tests/test_run.py` is a red file, and its wall count went from 532 to 538 (`.xv/slices/2026-11-18-report-tree.wall.json`). `may_not_files_needed`: none.

## 4. The picture

The originator still holds the last packet's four edits. Edits 1-3 are unchanged; see the last packet, or the list below. Edit 4 is updated for this pass.

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
4. `.xv/picture.md:47` names `names_test` as "the shared test-name matcher". This change adds another. Proposed line after `.xv/picture.md:47`, indented two spaces:
   `The removal check reads names with `record.test_names`, which keeps the part after the last `>`, `::` or `#`, and the last `.` part of a dotted name.`
   `It finds them with `record.test_still_there`, which matches a name as a whole word anywhere in its file.`

## 5. The wall

No recommendation this pass.
I looked at the six new tests in `tests/test_run.py:2263-2285`. Each one guards a different name form, and each form is one the picture says the repo takes (`.xv/picture.md:123`). None of them restates an older test: before this pass, the red covered only `>`, `.`, a JS title and unreadable names (`tests/test_run.py:2255-2261`, `:2305-2317`).

## Scenario misses

- Decision 12 and amendment 6: a `::` or `#` name that the new pattern does not match still passes without being checked. Decision 12 says a check whose input "cannot run stops for a person; it never passes" (`.xv/picture.md:340`). The fix only splits when the whole name matches `[\w./]*(?:::|#)[\w.]+(?:(?:::|#)[\w.]+)*` (`scripts/record.py:896-897`). Otherwise `test_names` keeps the whole text as the one name. At `:902` the `.` split adds no short name, because the last part is not `\w+`. `test_still_there` (`scripts/record.py:907-913`) does not find the name, and `removals_not_made` reads that as "removed" and passes. I traced two inputs. First, `Red::` or `Red#`, which have no name after the separator. They are the `::` and `#` forms of the unreadable `Red >`, which stops (`tests/test_run.py:2305-2309`); `Red::` passes instead. Second, `tests/milk-red.py::Red::test_milk_today`, the `file::Class::test` form the picture lists (`.xv/picture.md:123`). The `-` in the path is outside `[\w./]`, so the name is not split, and the check passes while the test is still there. Pytest parameter ids (`Red::test_x[1]`) and a prose move assertion that holds a `::` name (`:901`) fall through in the same way. I traced these by reading the code, because the commands I may run allow no probe that does not edit the tree. The cleaner's proposal to split with `names.COVERED_SEPARATOR` would also catch the first input: its last part would be empty, so the name would be listed as unreadable. (evidence: `scripts/record.py:896-913`; the red covers only names that match the pattern, `tests/test_run.py:2263-2285`; to: scenario)

For the person, not a miss: as the last packet said, on a slice-only move `prose=True` also adds the last word of the assertion (`scripts/record.py:901`). A prose assertion such as "removed the CHANGELOG test" adds `test`, which is in almost every test file, so the step stops for nothing. That error stops; it never passes.

## Door

**Door:** two-way. A revert removes the order, the reader fallback, the brief's `kept` field and this name split. The record additions, `deleted` and `removal_named` on a move, are new optional keys that older code ignores. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-18-report-tree.md`
- Diff: `git diff 5c2600c69d4d50853dcd288bd6278c48bd808657..HEAD`; this pass: `git diff e27be006ebd4..HEAD`
- Wall: `xv wall diff 2026-11-18-report-tree` (baseline `58cf9c6`)
- Boundary: `xv boundary --base 5c2600c69d4d50853dcd288bd6278c48bd808657` (`.xv/slices/2026-11-18-report-tree.boundary.md`)
- Red on HEAD: 29 tests, OK. Whole suite on HEAD: `python3 tests/run.py --jobs 4`, 1380 tests, OK.

## From the cleaner

- This pass: nothing applied.
- Shape proposal, still open: share the item/part event parsing between `extract_report` and `extract_run_report` in `scripts/record.py`.
- Shape proposal, new: have `test_names` reuse `names.COVERED_SEPARATOR` for the `::` and `#` forms instead of its own pattern. The cleaner says "it changes how names are cut, so it is not a cleanup".

## From the cleaner

- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py; it needs a shared reader and a rework of extract_report, so it is left for the packet.
- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py (needs a shared reader and a rework of extract_report).
- Shape proposal, for people: Have test_names in scripts/record.py reuse names.COVERED_SEPARATOR for the `::`/`#` forms instead of its own regex; it changes how names are cut, so it is not a cleanup.

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: Sean picked option 1 at change_misses_scenario: decision 12, a :: or # name the check cannot read must stop, not pass; a small fix in test_names with two tests, then a guardian re-pass. Commits: 5422f07f5f, 5fbdd7272a. Resumed at guardian. Spend: 10091 tokens (in 10, out 4048, cache write 6033; cache read 465550 not counted), 5 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_run.py.

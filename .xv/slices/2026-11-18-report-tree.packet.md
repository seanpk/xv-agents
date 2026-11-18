---
slice: 2026-11-18-report-tree
shape_change: no
pitch_contradiction: no
change_misses_scenario: no
picture_change: yes
shape_breadth: narrow
moved_tests_count: 2
expected_moves: 0
door: two-way
blast_radius: watch
---

# Packet: What an agent reports is checked against the tree (#183)

No stop for two people: no shape change and no pitch contradiction.
This re-pass covers only `d84d3a95fe19..HEAD`: six lines in `record.test_names` (`scripts/record.py:897-903`) and three tests (`tests/test_run.py:2304-2317`).
The three sentences the last packet named now stop while the test is there.
The miss is not fully met. A prose sentence whose last word is a plain word that is not the test, such as `removed Red.test_milk_today as asked`, still checks the wrong word and passes. A `#` inside a word, as in `issue#183`, does the same. This sends the slice back.
The originator gets four picture edits to accept. Edit 4 is updated for this pass. There is no wall recommendation.

## The scenario

What an agent reports is checked against the tree.

1. After the cleaner step, an accepted `slice_only` test still in its file stops the step with `removal_not_made` for the originator, naming the file and the test. The exception is a test the cleaner's report says it kept, with the reason. A removal that was made passes.
2. After any step, a recorded move marked `--slice-only` or `--deleted` whose test or file is still there stops with `removal_not_made`, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last block of the whole run through the harness's reader before it stops with `no_report`. A run with no block anywhere still stops with `no_report`.
4. A CHANGELOG.md line.
5. (amended) The cleaner's report has a `kept` list, and the cleaner's brief tells it to write that list. Only a test in `kept` with a `why` is exempt.
6. (amended) The check finds a test by its name anywhere in its file (`def`, `it("…")` title, `Class > test`). If it cannot read a name, it stops with `removal_not_made`. It never passes (decision 12).
7. (amended) For Claude Code, the fallback in outcome 3 reads the session transcript, found by the result's `session_id`.

May ignore: old slice records; a harness whose reader cannot see earlier messages.

## The recording

None: this defect starts from words.
Replay: `cd tests && python3 -m unittest test_run.RemovalNotMadeTest test_run.ClaudeWholeRunReportTest`.
I ran it on HEAD: 35 tests, OK.

## The boundary picture

Taken as given from `.xv/slices/2026-11-18-report-tree.boundary.md`.
Modules touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/spend`. Nothing is added or removed: no modules, edges, tables, surfaces or outbound calls. There are no shape hints.
This pass changes only `scripts/record.py:897-903`.

## What the suite asserts after

Everything the last packet listed still holds. This pass adds three slice-only moves whose assertion is a sentence. Each one stops the next step with `removal_not_made` for the originator, naming `tests/test_red.py`, while `test_milk_today` is still in it:
- `removed Red.test_milk_today as slice-only` (the last word is not a plain name),
- `removed Red.test_milk_today.` (it ends in a full stop),
- `removed Red.test_milk_today for #183` (a `#` with nothing before it).

The scenario agent wrote these in a send-back; the record logs `scenario: red` at 18:26:10 before `maker: green`. My prompt still lists `tests/test_run.py` as not blind, because pairing 1 touched it. I read each test against the code. Each one sets an input and asserts the stop the watch prints, and none restates `test_names`. They assert the file name only, not "could not be read" (`tests/test_run.py:2165-2170`), so they would also pass if the right name were found. That is weaker, but not a miss.
None checks a sentence that ends in a plain word other than the test's name. That is the hole below.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The diff is `scripts/record.py:897-903`: two early `return []` lines in the prose branch. It adds no import, edge, module, table or surface, so it stays inside the current shape.
- The cleaner's proposal to reuse `names.COVERED_SEPARATOR` (`scripts/names.py:10`) is still open. The repo still has three ways to read a test name (`.xv/picture.md:47`).

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25`. A removal check that stops more often on a sentence it cannot read serves the first line. The pitch says nothing else about this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` | at the first packet, `FAKE_NO_REPORT` printed one plain line | with `FAKE_EARLIER_REPORT` also set, it prints two codex `agent_message` events with no block | `FAKE_EARLIER_REPORT` is a mode "off unless set" (move at 2026-11-18T04:04:25). Unchanged this pass. | Yes, as before. |
| `tests/test_run.py` | `RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check` | removed | "checks one CHANGELOG line, a one-time wording change" (cleaner, `slice_only`). Unchanged this pass. | Yes, as before. |

Slice-only tests removed: `tests/test_run.py::RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check`. Kept: none.
This pass changes no old test. `git diff d84d3a95fe19..HEAD -- tests/test_run.py` only adds the helper `prose_move` and three tests.
`xv wall diff 2026-11-18-report-tree` shows that the wall baseline moved to `4634fa4` this pass (`.xv/slices/2026-11-18-report-tree.wall.json`: commit `58cf9c6` → `4634fa4`, `tests/test_run.py` 538 → 545). Against that baseline, changed, deleted, added and `fewer_assertions` are all empty. `may_not_files_needed`: none.

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
   `In a move's assertion, which may be a sentence, it reads the first word that holds `::` or `#`, or else the last word.`
   `A sentence whose last word is not a plain name, or whose `::` or `#` word starts with the separator, cannot be read.`
   `It finds names with `record.test_still_there`, which matches a name as a whole word anywhere in its file.`

## 5. The wall

No recommendation.
I looked at the three new tests at `tests/test_run.py:2304-2317`. Each one guards an input the last packet named as a miss. None restates an older test: the older prose tests use only `Red.test_milk_today` alone or a `::` sentence (`tests/test_run.py:2203`, `:2299`).

## Scenario misses

  I traced `scripts/record.py:897-913` with `removed Red.test_milk_today as asked`. No word holds `::` or `#`, so `word` is `None` (`:898`). The last word `asked` matches `[\w.]*\w`, so the new guard does not return (`:899-900`). `names` becomes the whole sentence plus `asked` (`:910-913`). Neither is in `tests/test_red.py`, so `test_still_there` is false and `removals_not_made` passes while `test_milk_today` is still there.
  `removed Red.test_milk_today for issue#183` falls through the same way. `issue#183` holds `#` but does not start with it (`:901`), so it is cut to `183` (`:904-905`), which matches a plain name and is not in the file.
  The last packet named this class: "A `#` used in prose for something other than a name picks the wrong word … so it passes too". The fix stops only a word that starts with the separator, and a sentence whose last word is not plain.
  The new reds cover exactly the three sentences that packet quoted (`tests/test_run.py:2310-2317`), so the red does not cover this line.
  Meeting it fully likely means the scenario has to say which prose the check may read: for example, an assertion that is not one name stops, or the brief's form `--assertion "<the test>"` (`skills/cleaner/SKILL.md:39`) is the only one read.
  I traced this by reading the code. The commands I may run allow no probe that does not edit the tree.
  (evidence: `scripts/record.py:897-913`; `tests/test_run.py:2304-2317`; to: scenario; amend: yes)

For the person, not a miss: the new guard also stops on a correct removal when the assertion is a test title that ends in punctuation (`it("handles a user's name.")`), or holds `#` at the start of a word (`shows #1 first`), or is wrapped in backticks. Each of these returns `[]` (`scripts/record.py:899-902`) and stops "could not be read" even after the test is gone. That error stops; it never passes.

## Door

**Door:** two-way. A revert removes the order, the reader fallback, the brief's `kept` field and the name cut. The record additions, `deleted` and `removal_named` on a move, are optional keys older code ignores. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-18-report-tree.md`
- Diff: `git diff 5c2600c69d4d50853dcd288bd6278c48bd808657..HEAD`; this pass: `git diff d84d3a95fe19..HEAD` (code in `af071bb`, tests in `cb1856c`)
- Wall: `xv wall diff 2026-11-18-report-tree` (baseline now `4634fa4`)
- Boundary: `.xv/slices/2026-11-18-report-tree.boundary.md`
- Red on HEAD: 35 tests, OK. I did not run the whole suite this pass. The cleaner reports it green (record, 18:44:09).

## From the cleaner

- Shape proposal, still open: share the item/part event parsing between `extract_report` and `extract_run_report` in `scripts/record.py`.
- Shape proposal, still open: have `test_names` reuse `names.COVERED_SEPARATOR` for the `::` and `#` forms instead of its own pattern.
- This pass: "nothing needed fixing" (record, 18:44:09).

## Dropped by the evidence rule

These findings cite no line, rule or hunk, so they do not count.

- Amendment 6 and decision 12: a prose slice-only assertion that ends in a plain word other than the test's name still passes without checking the test. Decision 12 says a check whose input "cannot run stops for a person; it never passes" (`.xv/picture.md:340`).

## Pairings

- Pairing 1: Sean Kennedy with Claude (claude-session session 009e989d-2ceb-45ce-b5a4-beec83f9774d), because: Sean picked option 1 at change_misses_scenario: decision 12, a :: or # name the check cannot read must stop, not pass; a small fix in test_names with two tests, then a guardian re-pass. Commits: 5422f07f5f, 5fbdd7272a. Resumed at guardian. Spend: 10091 tokens (in 10, out 4048, cache write 6033; cache read 465550 not counted), 5 turns, usd not reported. Not blind (written or changed in the pairing): tests/test_run.py.

## From the cleaner

- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py; it needs a shared reader and a rework of extract_report, so it is left for the packet.
- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py (needs a shared reader and a rework of extract_report).
- Shape proposal, for people: Have test_names in scripts/record.py reuse names.COVERED_SEPARATOR for the `::`/`#` forms instead of its own regex; it changes how names are cut, so it is not a cleanup.

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
This re-pass reviews only the changes after the first packet (`c66eabf1ad68..HEAD`).
Two of the first packet's three misses are met: the session path and the cleaner's `kept` list.
One miss is left, a narrower form of the decision 12 miss: test names written with `::` or `#` are not split, so the check finds nothing and passes. It sends the slice back.
The originator also gets four picture edits to accept. This pass makes no wall recommendation.

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
Replay: `cd tests && python3 -m unittest test_run.RemovalNotMadeTest test_run.ClaudeWholeRunReportTest`. Before the change it failed (`checks.scenario.red_output`: 23 tests, 13 failures). I ran it on HEAD: 23 tests, OK.
I ran the whole suite on HEAD, `python3 tests/run.py --jobs 4`. The result is under Raw data.

## The boundary picture

From `.xv/slices/2026-11-18-report-tree.boundary.md`, as given.
Modules touched: `scripts/orders`, `scripts/record`, `scripts/run`, `scripts/spend`. `scripts/spend` is new since the first packet. No modules, edges, tables, surfaces or outbound calls were added or removed. No shape hints.

## What the suite asserts after

What the first packet listed still holds. The re-pass adds:
- On the session path (`xv record report`, then `xv orders --after <agent>`), a cleaner that left an accepted slice-only test in place stops with `removal_not_made`. A cleaner that removed it, or listed it in `kept` with a `why`, passes. A maker after a slice-only move whose test is still there stops.
- `Red > test_milk_today` is found while the test is in the file, and passes once it is removed. A JS `it("…")` title in the file stops, and a title that is gone passes.
- A slice-only entry `Red >`, and a slice-only move whose assertion is `;`, both stop with "could not be read".
- The cleaner brief's report example has `kept` with `file`, `test` and `why`, and the brief's text names `kept`.
- With a Claude-shaped wrapper: a report in an earlier transcript message is read. A transcript with no block, and a `session_id` with no transcript, both stop with `no_report`.
- The no-report test now runs two codex `agent_message` events with no block. It asserts both are in the run log and the step stops with `no_report`.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The boundary picture shows no new edge, module, table, surface or outbound call. `scripts/record` already imported `scripts/spend` at the base (`row_tokens`). The new `claude_session_texts, claude_transcript` imports (`scripts/record.py:24`) add no edge.
- `removals_not_made` moved from `scripts/run.py` to `scripts/record.py:914`, and `run.post_step` now calls `record.removals_not_made` (`scripts/run.py:1220`). That uses the existing `run → record` edge. `record` still does not import `run` (`scripts/record.py:963` keeps its subprocess comment). This is inside the current shape.
- The forecast's `shape_note` said the change "turns wide only if the reader change reaches more than the claude harness". It now reaches Claude Code (`scripts/record.py:744-752`), codex and opencode. Amendment 7 asked for the Claude part. I call it narrow because nothing in the boundary moved. The originator should know that, read literally, the forecast's condition is met.
- The cleaner's first-pass shape proposal (sharing the event loop between `extract_report` and `extract_run_report`) was still not made. The second loop is now at `scripts/record.py:762-773`.

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Reading a Claude session transcript for the agent's own report serves the first line and does not contradict the second. The pitch says nothing else about this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` | at the first packet: `FAKE_NO_REPORT` printed one plain line | with `FAKE_EARLIER_REPORT` also set, it prints two codex `agent_message` events with no block. The default is unchanged (diff `tests/fake_agent.py:16-20`). | the move Sean Kennedy recorded on 2026-11-18T04:04:25 names `FAKE_EARLIER_REPORT` as a mode "off unless set". The re-pass extends that mode under `FAKE_NO_REPORT` and records no new move. | Yes. The originator's answer to `change_misses_scenario` asked to "rewrite that test as a real multi-message run with no xv-report block in any message". This is a helper with no assertions. `xv wall diff` shows no change, because the file is a red file. |
| `tests/test_run.py` | `RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check` | removed | "checks one CHANGELOG line, a one-time wording change" (cleaner, `slice_only`). It did not change since the first packet. | Yes, as the first packet said. |

Slice-only tests removed: `tests/test_run.py::RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check`. Kept: none.
`xv wall diff 2026-11-18-report-tree` against the new baseline `c585ca6`: changed, deleted and added are all empty. `fewer_assertions` is empty. `may_not_files_needed`: none.
The change to `skills/cleaner/SKILL.md:39` and `:59` changes a brief. Binding decision 1 asks for two people and a CHANGELOG line (`.xv/picture.md:313`). The CHANGELOG line says "The cleaner's brief asks for the `kept` list" (`CHANGELOG.md:7`). Amendment 5 says the repo runs solo.

## 4. The picture

The first pass proposed these edits. The originator held them for this pass. Here they are again, updated.

1. `.xv/picture.md:29` says "the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`". Replace that clause with:
   `the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`, or, when that message has none, from the last earlier `agent_message` that has one (`record.extract_run_report`)`
2. `.xv/picture.md:28` names Claude Code as a harness, and the picture says nothing of how its report is read. Proposed line after `.xv/picture.md:29`, indented two spaces:
   `For Claude Code, whose `--output-format json` holds only the last message, `record.extract_run_report` reads the earlier messages from the session transcript that the result's `session_id` names (`spend.claude_transcript`, `spend.claude_session_texts`).`
3. The shape section has no line for the new order. Proposed lines after `.xv/picture.md:63`, indented two spaces:
   `After every `xv step`, and after `xv record report` for any agent except a scenario on a slice from a build, `record.removals_not_made` looks in the tree for each removal the record names; `removal_not_made` then stops for the originator, naming what is still there.`
   `After the cleaner, that covers each accepted `slice_only` test, unless the cleaner's report lists it under `kept` with a `why`.`
   `After any step, it covers each move marked `slice_only` or `removal_named` whose test is still in its file, and each move marked `deleted` whose file is still there.`
   `xv record move --slice-only` marks the move `removal_named`, and `--deleted` marks it `deleted`.`
   `A name the check cannot read is listed as "the test name could not be read", and that stops too.`
4. `.xv/picture.md:47` names `names_test` as "the shared test-name matcher". This change adds a second one. Proposed line after `.xv/picture.md:47`, indented two spaces:
   `The removal check reads names with `record.test_names` and finds them with `record.test_still_there`, which matches the name as a whole word anywhere in its file.`

## 5. The wall

No recommendation this pass.
The first pass recommended marking `RemovalNotMadeTest.test_a_run_with_no_report_block_in_any_message_still_stops_with_no_report` slice-only. The originator refused it, and the test was rewritten (`tests/test_run.py:2228-2235`). It now builds a run of two `agent_message` events with no block and asserts both are in the log. The existing `tests/test_run.py:923-929` does not cover that case, so the old reason is gone.
I also looked at the 11 new tests in `tests/test_run.py:2242-2333` and the 3 `ClaudeWholeRunReportTest` tests (`tests/test_run.py:2394-2410`). Each one guards a lasting behaviour that amendments 5-7 name.

## Scenario misses

- Decision 12 and amendment 6: a slice-only test named in the `::` or `#` form passes without being checked. Decision 12 says a check whose input "cannot run stops for a person; it never passes" (`.xv/picture.md:340`). `test_names` cuts at `>` and splits only on `.` (`scripts/record.py:895`, `:899`). It adds a short name only when the text is `[\w.]+`. So `Red::test_milk_today`, `Red#test_milk_today` and `tests/test_red.py::Red::test_milk_today` each give one whole name. That name never appears in the file. `test_still_there` (`scripts/record.py:911`) then returns False, which is read as "removed", and the step passes. These are the test forms the picture says the coverage check and `--accept-wall` take (`.xv/picture.md:123`: "`file::test`, `file::Class.test`, `Class#test`, `module.Class.test`, `Class > test`"). The repo already has a splitter for them, `names.COVERED_SEPARATOR` (`scripts/names.py:10`), which `scripts/record.py:484` uses. The scenario agent writes `slice_only` `test` as free text (`skills/scenario/SKILL.md:64`). (evidence: `scripts/record.py:895-911`; the red covers only `.`, `>`, a JS title and the unreadable `Red >` and `;`, `tests/test_run.py:2255-2297`; to: scenario)

For the person, not a miss: on a slice-only move, `prose=True` also adds the last word of the assertion (`scripts/record.py:899`). The cleaner's brief asks for `--assertion "<the test>"` (`skills/cleaner/SKILL.md:39`). But a prose assertion such as "removed the CHANGELOG test" would add `test`, which is in almost every test file, so the step would stop for nothing. That error stops; it never passes.

## Door

**Door:** two-way. A revert removes the order, the reader fallback and the brief's `kept` field. The record additions, `deleted` and `removal_named` on a move, are new optional keys that older code ignores. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-18-report-tree.md`
- Diff: `git diff 5c2600c69d4d50853dcd288bd6278c48bd808657..HEAD`; this pass: `git diff c66eabf1ad68..HEAD`
- Wall: `xv wall diff 2026-11-18-report-tree`
- Boundary: `xv boundary --base 5c2600c69d4d50853dcd288bd6278c48bd808657` (`.xv/slices/2026-11-18-report-tree.boundary.md`)
- Whole suite on HEAD: `python3 tests/run.py --jobs 4`, 1374 tests, OK (exit 0).

## From the cleaner

- This pass: one baseline fix, a duplicate `spend` import (`scripts/record.py:24`). No shape proposals.
- From the first pass, still open: share the item/part event parsing between `extract_report` and `extract_run_report`.

## From the cleaner

- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py; it needs a shared reader and a rework of extract_report, so it is left for the packet.

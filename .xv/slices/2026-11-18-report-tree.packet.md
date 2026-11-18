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
Three scenario misses send the slice back. Two concern outcome 1 (session steps, and the cleaner brief has no `kept` field). One concerns binding decision 12 (test names the new matcher cannot read pass without a stop).
The originator also gets one wall recommendation and three picture edits to accept.

## The scenario

What an agent reports is checked against the tree.

1. After the cleaner step, an accepted `slice_only` test still in its file stops the step with `removal_not_made` for the originator, naming the file and the test. The exception is when the cleaner's report says it kept the test and why. A removal that was made passes.
2. After any step, a recorded move marked `--slice-only` or `--deleted` whose test or file is still there stops with `removal_not_made`, naming the file and the test.
3. When a step's last message has no `xv-report` block, the step reads the last block of the whole run through the harness's reader before it stops with `no_report`. The core still names no agent. A run with no block anywhere still stops with `no_report`.
4. A CHANGELOG.md line.

May ignore: old slice records; a harness whose reader cannot see earlier messages (it stops with `no_report`, as now).

## The recording

None: this defect starts from words.
Replay: `cd tests && python3 -m unittest test_run.RemovalNotMadeTest`. Before the change it failed with 6 failures (the record's `red_output`). I ran it on HEAD: 9 tests, OK. The whole suite was green after the maker and after the cleaner (the record's `checks.maker.suite`, `checks.cleaner.suite`). I ran `python3 tests/run.py --jobs 4` on HEAD: 1360 tests, OK.

## The boundary picture

From `.xv/slices/2026-11-18-report-tree.boundary.md`, as given.
Modules touched: `scripts/orders`, `scripts/record`, `scripts/run`. No modules added or removed. No edges added or removed. No new outbound calls. No tables. No surfaces added or removed. No shape hints.

## What the suite asserts after

- After `xv step cleaner`, an accepted slice-only test still in its file stops with `removal_not_made` (exit 10, seat originator) and names the file and the test. A test the cleaner removed passes. A test the report lists under `kept` with a non-empty `why` passes. A `kept` entry with an empty `why` still stops.
- After `xv step maker`, a recorded `--slice-only` move whose test is still there stops. So does a `--deleted` move whose file is still there. After the guardian, a slice-only move whose test is gone does not stop.
- A scenario step whose report is in an earlier codex `agent_message`, with a last message that has none, is read and does not stop with `no_report`.
- A scenario step with no block stops with `no_report`.
- The fake agent (`tests/fake_agent.py`) gains three modes: `FAKE_EARLIER_REPORT`, `FAKE_CLEANER_REMOVES`, `FAKE_CLEANER_REPORT_EXTRA`. Each is off unless set.

## 1. Shape

shape_change: no. shape_breadth: narrow.

- The boundary picture shows no new edge, module, table, surface or outbound call, and no shape hints. The three touched modules already have their roles: `.xv/picture.md:54` says "`orders` holds the stop rules", and `record` and `run` are already the record owner and the step runner (`.xv/picture.md:48`, `.xv/picture.md:45`).
- One new standing order, `removal_not_made`, is in `scripts/orders.py:255-259`. It reads only `checks`, so it stays inside binding decision 10 (`.xv/picture.md:335`). This is a change inside the current shape.
- The forecast's `shape_note` says the change "turns wide only if the reader change reaches more than the claude harness". The new reader `extract_run_report` (`scripts/record.py:742-764`) reads codex `agent_message` events and opencode text parts. It does not reach Claude Code: `--output-format json` gives only the final `result` (`.xv/config.yml:37`). That is the case the scenario lets the slice ignore. Codex and opencode were already parsed in the same function family at the base (`scripts/record.py:714-728`). For opencode, `extract_report` already joins every text part, so the new opencode branch finds nothing the old reader missed. I call this narrow because no module or edge was added. The originator should know that, read literally, the forecast's condition is met (the change reaches codex).
- The cleaner proposed one shape change: sharing the item/part event parsing between `extract_report` and `extract_run_report` (the record's `checks.reports[cleaner].shape_proposals`). It was not made. The two functions now hold two copies of the event loop: `scripts/record.py:715-727` and `scripts/record.py:749-760`.

## 2. Pitch

pitch_contradiction: no.
I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline") and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Checking an agent's report against the tree serves the first line and does not contradict the second. The pitch says nothing else about this change.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` | `report()` printed one `xv-report` block; the fake cleaner only reported | three env modes, each off unless set; default output unchanged (diff `tests/fake_agent.py:21-27`, `:181-197`) | "the red for outcomes 1-3 needs a fake cleaner that removes a slice-only test, extra report fields, and a report in an earlier message" (Sean Kennedy; answered `unrecorded_move` with option 1) | Yes. Outcomes 1-3 need a cleaner that removes a test, a `kept` field, and a multi-message run. It is a helper with no assertions, so nothing asserts less. |
| `tests/test_run.py` | `RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check` | removed; assertions 507 → 506 (`xv wall diff`) | "checks one CHANGELOG line, a one-time wording change" (cleaner, `slice_only`) | Yes. It was an accepted slice-only mark that checks `CHANGELOG.md`, listed in `tests.slice_only_files` (`.xv/config.yml:26`). |

Slice-only tests removed: `tests/test_run.py::RemovalNotMadeTest.test_the_changelog_has_a_line_for_the_removal_check`. Kept: none.
The record's `old_tests_to_move` named `tests/test_codex_step.py::CodexReportTest.test_a_report_in_an_earlier_message_is_not_the_report_when_the_last_has_none`, to move only if the fallback went into `extract_report`. It went into a separate reader (`scripts/record.py:742`), and the file is not in the diff. `may_not_files_needed`: none.

## 4. The picture

1. `.xv/picture.md:29` says "the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`". That is now incomplete. Proposed replacement for that sentence:
   `the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`, and, when that message has none, from the last earlier `agent_message` that has one (`record.extract_run_report`).`
2. The shape section has no line for the new order. Proposed lines after `.xv/picture.md:63`:
   `After every `xv step`, `run.removals_not_made` looks in the tree for each removal the record names, and `removal_not_made` stops for the originator naming what is still there.`
   `After the cleaner, that covers each accepted `slice_only` test, unless the cleaner's report lists it under `kept` with a `why`.`
   `After any step, it covers each move marked `slice_only` whose test is still in its file, and each move marked `deleted` whose file is still there.`
   `xv record move --deleted` marks the move `deleted`.`
3. `.xv/picture.md:47` names `names_test` as "the shared test-name matcher". The change adds a second matcher, `run.test_still_there` (`scripts/run.py:1224-1229`), which only finds `def|func|fn|function <name>`. If the matcher stays, add:
   `run.test_still_there finds a test only as `def`, `func`, `fn` or `function` followed by its name.`

## 5. The wall

- `tests/test_run.py::RemovalNotMadeTest.test_a_run_with_no_report_block_in_any_message_still_stops_with_no_report`: **mark slice-only**. It repeats the existing `tests/test_run.py:923-929`, which already runs `xv step scenario` with `FAKE_NO_REPORT=1` and asserts `no_report`. Its one difference, `FAKE_EARLIER_REPORT=""`, is an empty string, which `tests/fake_agent.py:22` treats as off. The run is the same plain-stdout run. It never builds a multi-message run with no block in any message, which is the case outcome 3's last sentence names.

I looked at the other eight new `RemovalNotMadeTest` tests (`tests/test_run.py:2147-2226`) and the base wall test `tests/test_codex_step.py:43`. I make no recommendation for them. The codex test still holds because `extract_report` keeps its last-message behaviour for `scripts/run.py:544`, `scripts/run.py:768` and `scripts/prototypes.py:99`.

## Scenario misses

- 1 and 2: the check runs only on the `xv step` path. `removals_not_made` is called only from `run.post_step` (`scripts/run.py:1220`). A step set to `session` in `.xv/config.yml` reports through `xv record report` and then `xv orders --after <agent>` (`skills/watch/SKILL.md:126`). `record.cmd_report` (`scripts/record.py:877-907`) runs the move and wall checks for the maker and the cleaner but never sets `checks[<agent>].removal_not_made`. So on that path a slice-only test the cleaner left in place, or a removal recorded but not made, goes through with no stop. "After any step" includes session steps: `.xv/picture.md:103` says "before every step, `session` steps too". (evidence: `scripts/record.py:877-907` has no call; every new red test goes through `xv step`, `tests/test_run.py:2159-2163`; to: scenario)
- 1: the "kept" exception reads a field the cleaner is never told to write. `removals_not_made` honours a keep only as `report["kept"]` entries with `file`, `test` and a `why` (`scripts/run.py:1234-1235`). The cleaner's brief says only "If you keep one, leave it and report the test and your reason to recommend keeping it, for the packet" (`skills/cleaner/SKILL.md:39`). Its report block has no `kept` key (`skills/cleaner/SKILL.md:56-60`). A cleaner that follows its brief and keeps a test with a reason will still be stopped. Meeting the outcome needs a change to the cleaner's brief. Binding decision 1 says that needs two people and a CHANGELOG line (`.xv/picture.md:313`). (evidence: `skills/cleaner/SKILL.md:39`, `:56-60`; `scripts/run.py:1234`; to: scenario; amend: yes)
- Decision 12: test names the matcher cannot read count as removed, with no stop. Decision 12 says "A check whose input is broken or that cannot run stops for a person; it never passes" (`.xv/picture.md:340`). `test_still_there` returns False, which means "removed, passes", for any test it cannot find as `def|func|fn|function <name>` (`scripts/run.py:1229`). The name also comes from `split(".")[-1]` or the last word of the move's assertion (`scripts/run.py:1245`, `:1254`). So a slice-only test named in a form the coverage check accepts, such as `Class > test` (`.xv/picture.md:123`), or a JS `it("…")` test, or a move whose assertion is prose, passes without being checked. (evidence: `scripts/run.py:1224-1229`, `:1254`; the red uses only a Python `def`; to: scenario)

## Door

**Door:** two-way. A revert removes the order and the reader fallback. The only record addition, `deleted: true` on a move, is a new optional key that older code ignores. **Blast radius:** watch.

## Raw data

- Slice record: `.xv/slices/2026-11-18-report-tree.md`
- Diff: `git diff 5c2600c69d4d50853dcd288bd6278c48bd808657..HEAD`
- Wall: `xv wall diff 2026-11-18-report-tree`
- Boundary: `xv boundary --base 5c2600c69d4d50853dcd288bd6278c48bd808657` (`.xv/slices/2026-11-18-report-tree.boundary.md`)

## From the cleaner

- Shape proposal, for people: Share the item/part event parsing between extract_report and extract_run_report in scripts/record.py; it needs a shared reader and a rework of extract_report, so it is left for the packet.

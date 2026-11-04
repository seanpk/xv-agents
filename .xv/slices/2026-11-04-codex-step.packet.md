---
slice: 2026-11-04-codex-step
shape_change: no
shape_breadth: narrow
pitch_contradiction: no
scenario_miss: no
door: two-way
blast_radius: small
---

# Packet: Codex runs as a step, and #115

I could not read the packet template at `skills/guardian/packet.md`, because it is outside the worktree and the read was not permitted. This packet follows the sections the brief lists.

## Needs a decision

Nothing stops this change for two people. These go to Sean as the person who set the work going:

1. **The relies-on line watches the command, not the event shape** (scenario point 5). `docs/relies-on.md:13`:
   `- \`spend.py\` and the report reader reading Codex's \`agent_message\` events | https://developers.openai.com/codex/noninteractive | "codex exec --json"`
   The quoted sentence is only `"codex exec --json"`. If Codex renamed `agent_message`, `item.completed` or `thread_id`, that sentence would still be on the page and `xv check drift` would not report anything. The red only checks that the line exists and parses (`tests/test_codex_step.py:96-103`, `:106-113`), so it passes with this quote. I have not marked this as a scenario miss because the line literally exists, but it does less than point 5's wording says it should ("so `xv check drift` watches it"). Your call: accept it, or ask for a quote that names the event shape, if the page has one.
2. **The README claims more than the slice has shown.** `README.md:3` now says "Codex now runs headless as a step". Every test in the slice uses events built by hand (`tests/test_codex_step.py:17-25`). The forecaster said no Codex agent runs on this slice. A real step run is still the record's `watch_first_green`. Before this, Codex had only been run by hand (`docs/harness-notes.md:24`, `.xv/picture.md:20`).
3. **Picture edit**, proposed below (check 4).
4. **Two wall recommendations**, below (check 5).

## The scenario in words

When this is done, a step run with `codex exec --json` gets its `xv-report` from the last `agent_message` applied to the record. The eval runner's final message for Codex is that last `agent_message`. `evals/harnesses.json` has a `codex` entry on `gpt-6.1-terra` with the sandbox off, and its note says the brief is not the whole prompt. The README (`:3` and `:392`) and decision 48 say what is now true. `docs/relies-on.md` has a line for the Codex event shape. `session_of` returns the `thread_id`. The slice may ignore running the evals, a clean Codex baseline, Codex dollars, #112 and Cursor.

## Recording

None, because this is a feature. To replay it: `cd tests && python3 -m unittest test_codex_step`. I ran it: 11 tests, OK. The real check is the record's `watch_first_green`: run a real `codex exec --json` step.

## Boundary picture

From `xv boundary` (`.xv/slices/2026-11-04-codex-step.boundary.md`):
- Touched: `evals/grade`, `scripts/agentcli`, `scripts/record`.
- No modules, edges, outbound calls, tables or surface paths added or removed.
- Shape hints: none.

The diff agrees. Each code change is a branch added inside an existing function:
- `evals/grade.py:226-239`: `final_text` returns the last `agent_message`.
- `scripts/agentcli.py:114-121`: `session_of` returns `thread.started.thread_id`.
- `scripts/record.py:410-424`: `extract_report` reads the last `agent_message`.

The rest is JSON and docs: `evals/harnesses.json:44-55`, `README.md:3,392`, `docs/decisions.md:69`, `docs/relies-on.md:13`.

## What the suite asserts after the change

- In Codex events, the report is taken from the last `agent_message` only. A report in an earlier message does not count if the last message has none.
- `xv record report` on a Codex event log applies the report, moved tests included.
- `session_of("codex", …)` is the `thread_id`, or None when there is no thread.
- `final_text` is the last `agent_message`.
- The `codex` harness entry is `codex exec --json` on `gpt-6.1-terra`, has `--dangerously-bypass-approvals-and-sandbox` and `{prompt}`, and `harness_of`/`model_of` read it as `("codex", "gpt-6.1-terra")`. Its note names "not the whole prompt", `AGENTS.md` and skills.
- `docs/relies-on.md` has exactly one Codex `agent_message` line with a URL and a quoted sentence. `xv check drift --offline --json` lists exactly one Codex `spend.py` item.

The cleaner reports the whole suite green, 664 tests OK. I did not rerun it.

## Moved tests

`xv wall diff` shows one file changed since the baseline `615a6f2`: `tests/test_codex_step.py`, assertions 28 → 21 (`fewer_assertions`). Both moves are recorded (`moved_tests`).

- **Slice-only removals:** `CodexDocsTest.test_readme_no_longer_says_codex_was_not_run` and `CodexDocsTest.test_decision_48_says_spend_reads_codex_events_and_codex_reports_no_dollars`. The cleaner removed both (the `tests/test_codex_step.py:93` hunk, -14 lines, against baseline `615a6f2`), and Sean accepted both marks at the `red_misses_scenario` and `slice_only_marks` stops. None was kept.

The scenario agent added `CodexDriftTest` between the two red commits. It is an addition, not a move. The suite now asserts less only because of the two accepted removals. No old test changed outside this slice's own red file.

## The five checks

### 1. Shape: no, narrow, which matches the forecast

- The boundary picture has no shape hints and no edges, modules, tables or surfaces added or removed (`.xv/slices/2026-11-04-codex-step.boundary.md`, "Shape hints: none", "Edges: added: none").
- The picture already counts Codex as a harness that `spend.py` reads (`.xv/picture.md:20`), and `agentcli.KNOWN` already listed `codex` (`scripts/agentcli.py:16`). The change finishes a harness the shape already names; it does not add a dependency.
- `evals/harnesses.json:44-55` adds an eval config entry. That is not a surface the picture lists (`.xv/picture.md:27`).
- The breadth is narrow, as the forecast said ("each change is additive, and the claude, opencode and grok paths should not move").
- One edge case in `scripts/record.py:416-418,422-424`: in event-per-line output, any `item.type == "agent_message"` event now wins over opencode text parts. opencode events carry `part`, and Claude and Grok JSON is handled earlier (`scripts/record.py:401-406`), so I found no path that moves.

### 2. Pitch: no

The pitch says xv-agents is "not for people or projects that will not trust agents to write production code" (`.xv/pitch.md:25`). Adding a harness serves the same users. The sandbox-off flag (`evals/harnesses.json:52`) applies to eval runs on a throwaway fixture. The pitch says nothing about sandboxing, and silence is not a contradiction.

### 3. Moved tests

Both moves are the slice-only ones above, and both are recorded. Nothing is unrecorded (`checks.cleaner.wall.unrecorded: []`).

### 4. The picture: an edit is proposed

- **`.xv/picture.md:20`** says "Codex has been run headless by hand (2026-11-03, `docs/harness-notes.md`), and `spend.py` reads its `--json` events." That is now incomplete. Proposed wording: "Codex can run as a step: the watch reads its `xv-report` from the last `agent_message` of `codex exec --json`, `session_of` takes its `thread_id`, and `evals/harnesses.json` has a `codex` entry on `gpt-6.1-terra` with the sandbox off; AGENTS.md and the skills still load, so the brief is not the whole prompt." Add "(not yet run as a step)" until `watch_first_green` is seen.
- **`.xv/picture.md:28`** ("recorded runs on three harnesses") is still true. No Codex runs were recorded, and running the evals was excluded.
- **Binding decision 2** (`.xv/picture.md:64`, "each brief works as the whole prompt of a fresh context") is not broken. The Codex note (`evals/harnesses.json:54`) says the harness adds context, as Grok's and opencode's notes do (`evals/harnesses.json:33,69`).
- **Binding decision 6** (`.xv/picture.md:68`) holds: decision 48 now says Codex dollars are null (`docs/decisions.md:69`).
- **Binding decision 8** (`.xv/picture.md:70`, "file references are relative Markdown links"): `README.md:392` adds a bare `` `spend.py` ``. It names a script, not a path, so I do not count it as a breach. It is for you to judge.

### 5. The wall

- `tests/test_codex_step.py`, `CodexDocsTest.test_relies_on_has_a_line_for_the_codex_event_shape` (`:96-103`): I recommend marking it slice-only. It only restates `CodexDriftTest.test_xv_check_drift_offline_lists_the_codex_event_shape_line` (`:106-113`), which reads the same line through the drift reader. It is also the kind of doc-wording pin whose two siblings were marked slice-only.
- `tests/test_codex_step.py`, `CodexHarnessEntryTest.test_the_note_says_the_brief_is_not_the_whole_prompt_because_agents_md_and_skills_load` (`:88-92`): I recommend marking it slice-only. It pins the wording of one note (`evals/harnesses.json:54`) that was written once, the same reason Sean accepted for the README and decision-48 tests.

No test on the wall before the slice is made dead by the scenario.

## Scenario misses

None. Points 1, 2, 3 and 6 are met and tested. Point 4 is met (`README.md:3,392`, `docs/decisions.md:69`). Point 5 is met as worded, with the caveat in "Needs a decision" item 1.

## The door

Two-way door: a revert removes the branches, the JSON entry and the doc lines, and no data, contract or message is touched. Blast radius: small.

## Raw data

- Diff: `git diff 704f635e0b022b847e338a744d9415165be7fd20..HEAD`
- Boundary: `.xv/slices/2026-11-04-codex-step.boundary.md`
- Wall: `xv wall diff 2026-11-04-codex-step`, baseline `.xv/slices/2026-11-04-codex-step.wall.json`
- Runs: `.git/xv/runs/2026-11-04-codex-step/`

## From the cleaner

- Shape proposal, for people: The agent_message parse is now in evals/grade.py:final_text and scripts/record.py:extract_report; a shared codex-events reader in scripts/agentcli.py (next to session_of) would hold the event shape in one place, but it is a new helper, so left for the packet.

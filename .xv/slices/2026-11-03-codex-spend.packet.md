---
slice: 2026-11-03-codex-spend
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: narrow
moved_tests: 1
door: two-way
blast_radius: steps
---

# Packet: spend.py reads Codex output

Nothing stops this for two people. Three things are for Sean, as the person who set the work going:

1. **A real Codex run is still owed before merge.** Sean's answer to `red_misses_scenario` settled: "one real Codex run through the new agentcli with stdin open is checked before merge" (`.xv/slices/2026-11-03-codex-spend.md`, `stops[2].settled`). Nothing in the record or the diff shows it was done. Until it is, the test with a fake CLI is the only evidence for point 5.
2. **The notes give Codex the wrong verdict.** `docs/harness-notes.md:12` says "**codex: yes.**" under "Can a brief be the whole prompt of a fresh context?" In the same line it says "`AGENTS.md` and the skills still load with `--ignore-user-config --ignore-rules`." By the file's own scale, that answer is not yes: opencode is "partly" because "It reads `AGENTS.md` from the project" (`docs/harness-notes.md:10`), and Grok is "no" because it loads rules and lists skills (`docs/harness-notes.md:11`). This bears on `.xv/picture.md:64` (decision 2: "each brief works as the whole prompt of a fresh context"). Point 4 asked the notes to say what was checked, and they do, so this is not a scenario miss. Only the one-word verdict looks wrong.
3. **Point 3's command.** The scenario says `` `xv spend codex-result <file>` `` (`.xv/slices/2026-11-03-codex-spend.md:41`). The code adds `codex-result` as a reader under `xv spend read` (`scripts/spend.py:237`, `:249-250`), so the working command is `xv spend read codex-result <file>`, and `xv spend codex-result <file>` as written exits with a usage error. The red reads the point as "called like the other readers" (`tests/test_spend.py:73`), and the point's own words are "the same as the other readers". I read it as met. Confirm that reading.

Apart from these, merging is the originator's call.

## The scenario

When this is done (`.xv/slices/2026-11-03-codex-spend.md:39-43`):

1. A `codex exec --json` step records a spend row with harness `codex`. Tokens are added up from the usage on each `turn.completed`, `session` is the `thread_id`, `turns` is the number of turns, and `usd` is empty.
2. Cached input goes in `cache_read`, not `tokens_in`. Output includes reasoning. Settled at `scenario_stopped`: reasoning is already inside `output_tokens` and is not added again.
3. `xv spend codex-result <file>` reads a saved run, like the other readers.
4. `docs/harness-notes.md` says what was checked on 2026-11-03.
5. An agent CLI gets a closed stdin, and a Codex step started with stdin open finishes.

May ignore: Codex dollars, a Codex budget cap, a clean Codex baseline (a separate CODEX_HOME), Codex in `evals/harnesses.json`, and #112.

Not covered by tests, as Sean accepted: the content of point 4 and the real run in point 5. The hand checks of 2026-11-03 stand for both, plus the real run owed before merge.

## The recording

None, because this is a feature. Replay the red and the green with `cd tests && python3 -m unittest test_spend`. Before (`63a2d8c`): `AttributeError: module 'spend' has no attribute 'from_codex_result'`, and the stdin test got code 124. After (HEAD): ran 9 tests, OK (I re-ran it). Whole suite at HEAD: 653 tests, OK (I re-ran it).

## The boundary picture

From `xv boundary` (`.xv/slices/2026-11-03-codex-spend.boundary.md`), as given:

- Touched: `scripts/agentcli`, `scripts/spend`
- Modules added or removed: none. Edges added or removed: none. New outbound calls: none.
- Tables: none. Surface paths: none added or removed.
- Shape hints: none.

## What the suite asserts after

- `from_codex_result` adds up the turns of a two-turn fixture: `tokens_in` 700 (input minus cached), `tokens_out` 150 (reasoning not added), `cache_read` 2300, `tokens` 850, session `019a-thread-0001`, turns 2, usd `None` (`tests/test_spend.py:54-59`).
- A fake `codex` CLI run through `agentcli.run` and `spend.from_run` gives the same codex row (`tests/test_spend.py:61-70`).
- `xv spend read codex-result <file>` exits 0 and prints the codex row (`tests/test_spend.py:72-79`).
- `agentcli.run` gives a CLI that reads stdin an EOF even when the parent's stdin stays open and silent (`tests/test_spend.py:81-95`).
- No old assertion moved. The one removal is the slice-only notes test (below).

## 1. Shape

shape_change: no. The boundary picture shows no module, edge, table, outbound call or surface path added or removed, and no shape hints. Within the existing shape:

- `codex-result` is a new choice under the existing `xv spend read` (`scripts/spend.py:237`). The `xv` CLI is already a surface (`.xv/picture.md:27`), and adding a reader choice stays inside it.
- `agentcli.run` now passes `stdin=subprocess.DEVNULL` whenever the prompt goes in argv (`scripts/agentcli.py:71-76`). That changes what every harness's step sees, not only Codex. It stays inside "`agentcli` and `prompt` build and run the agent calls" (`.xv/picture.md:23`). Every caller already uses `capture_output` (`scripts/run.py:308,363,797,868`, `scripts/listen.py:153`, `scripts/retro.py:158`, `scripts/prototypes.py:62`, `evals/run.py:161`), so none was interactive.

shape_breadth: narrow. It touches two modules and one doc, which is not wider than the forecast's "wide".

## 2. Pitch

pitch_contradiction: no. I checked `.xv/pitch.md:7` ("makes it easy for a team or an individual to adopt Xtreme Vibing in a repo") and `.xv/pitch.md:25` (not for people who will not trust agents to write production code; never a teapot). Reading spend from one more harness serves the first line and touches neither part of the second.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| tests/test_spend.py | `test_harness_notes_say_what_was_checked_on_codex`: the notes do not say "codex: not checked", and they name 2026-11-03, `codex exec --json`, `turn.completed`, `AGENTS.md`, `--ignore-user-config` and `--ignore-rules` (removed in `cf637e7`) | removed | "Only proves the notes were written on 2026-11-03; no value once they exist." (cleaner, recorded move, slice-only) | Not forced. It is a slice-only removal that Sean accepted at `red_misses_scenario` |

`xv wall diff` lists only `tests/test_spend.py`, with 24 assertions before and 21 after. The three fewer are exactly the three assertion lines of the removed test, and the record covers it. No unrecorded change.

Slice-only tests removed: `tests/test_spend.py::test_harness_notes_say_what_was_checked_on_codex`. Kept: none.

## 4. The picture

- `.xv/picture.md:20`: "Codex and Cursor read the same skill format and have not been run (README)." This is no longer true for Codex. Proposed edit: "Codex has been run headless by hand (2026-11-03, `docs/harness-notes.md`), and `spend.py` reads its `--json` events. Cursor reads the same skill format and has not been run."
- `.xv/picture.md:23`, the `spend` and `agentcli` sentences: incomplete. Proposed addition: "`agentcli.run` gives every agent CLI a closed stdin when the prompt is in argv." That is a lasting behaviour change for every harness (`scripts/agentcli.py:71-72`).
- `.xv/picture.md:64` (decision 2): the change does not break it. But depending on how Sean settles item 2 above, the picture may want to say that a Codex brief is not the whole prompt, as it already implies for opencode and Grok.

Outside the picture, these lines are now untrue. They do not bind (`.xv/picture.md:79`), so they are only for Sean to note:

- `docs/decisions.md:69` (48): "Codex is not read in v0.1; its tokens are recorded as zero". `scripts/spend.py:182-183` now reads Codex.
- `README.md:3` and `README.md:392`: "codex has the flags and was not run".
- `docs/relies-on.md` has no line for the Codex event shape that `scripts/spend.py:84-108` now relies on (`turn.completed`, `usage.cached_input_tokens`, `thread.started`). So `xv check drift` will not notice if that shape changes, as it does for opencode's events (`docs/relies-on.md:13`).
- `scripts/agentcli.py:95` (`session_of`) has no Codex branch, so the run result's `session` is `None` for Codex. The spend row still gets the `thread_id` from `scripts/spend.py:108`. `scripts/prototypes.py:70` stores `result.get("session")`, though, so a Codex prototype would never match `reused_prototype_context` at `scripts/run.py:474`. Prototypes are outside this scenario.

## 5. The wall

No recommendations. I looked at:

- Each of the four new tests, none of them marked: `test_codex_result_adds_the_turns_and_keeps_cache_out_of_input`, `test_a_codex_step_records_a_codex_row`, `test_xv_spend_reads_a_saved_codex_run` and `test_the_agent_cli_gets_a_closed_stdin` (`tests/test_spend.py:54-95`). Each guards lasting behaviour: the reader, the `harness_of` and `from_run` dispatch, the CLI choice, and the closed stdin. The second repeats the first one's numbers, but it goes through `agentcli.run` and `from_run`, which the first does not.
- The only slice-only test, which is already removed and does not need to stay marked.
- Wall tests that mention stdin or the notes: `tests/fake_agent.py:10` and `tests/helpers.py:14` still hold, and none is made dead.

## Door

**Door:** two-way. A revert undoes it: no data is migrated, and the CLI only gains a choice. **Blast radius:** steps. The stdin change reaches every agent step on every harness.

## Raw data

- Slice record: `.xv/slices/2026-11-03-codex-spend.md`
- Diff: `git diff 882af07d4ace445d77fa52dc5bf535f0b89c277c..cf637e7`
- Wall: `xv wall diff 2026-11-03-codex-spend`
- Boundary: `xv boundary --base 882af07d4ace445d77fa52dc5bf535f0b89c277c` (`.xv/slices/2026-11-03-codex-spend.boundary.md`)
- Whole suite at HEAD, re-run by the guardian with `cd tests && python3 -m unittest -q`: ran 653 tests in 250.9s, OK.

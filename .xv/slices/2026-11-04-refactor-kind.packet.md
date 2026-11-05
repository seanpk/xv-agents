---
slice: 2026-11-04-refactor-kind
shape_change: yes
pitch_contradiction: no
scenario_miss: yes
picture_change: yes
shape_breadth: narrow
moved_tests: 1
expected_moves: 0
door: two-way
blast_radius: workflow
---

# Packet: A slice kind for refactors, and test moves a person expects: #15

Needs a decision by two people (solo here: Sean): a new module, `scripts/moves.py`, joins the shape. The forecast named it, and no decision record accepts it. One scenario miss goes back: a move the cleaner makes in an expected kind still stops at `accept_moves` (point 7). Three more findings are for Sean: the `expected_moves` check does not stop anything; an `imports` move can point an old test at different code with no stop; an amend on a refactor slice gets no red.

## The scenario

`xv slice new --kind refactor` opens a slice whose scenario step writes no red. It runs the suite, stops when the suite is not green, and otherwise records that green suite as the oracle (points 1–2). In a refactor slice the maker may rename and restructure what the scenario names, and a latent bug goes through `xv slice amend` (3–4). `--expect-moves imports|renames` and `--rename Old=New` name the test changes the person expects. After each step a script, not the agent, decides whether a move fits. A move that fits is recorded with no `accept_moves` stop, and any other move still stops (5–9). Each new stop is decided in `scripts/orders.py` (10). Amendment 11: the packet has `expected_moves: <n>`, and the check after the guardian lists a problem when the field is missing, not a whole number, or not equal to the record's count. The slice may ignore other move kinds, #114, and old slice records.

## The recording

None: this is a feature. Replay the red with `cd tests && python3 -m unittest test_refactor_kind test_orders`. I ran it: 90 tests, OK (88 s). The whole suite was green after the maker and after the cleaner (957 tests, record `checks.maker.suite`, `checks.cleaner.suite`). I did not rerun it.

## The boundary picture

From `.xv/slices/2026-11-04-refactor-kind.boundary.md`, as given:

- Modules touched: `moves`, `orders`, `prompt`, `record`, `run`, `wall`. **Added: `scripts/moves`.** Removed: none.
- Edges added: `moves → wall`, `moves → xvlib`, `run → moves`. Removed: none.
- Tables: none. Surface paths: none added. The `xv slice new` CLI gains a flag value and two flags (`scripts/record.py:757-761`, `scripts/run.py:1191-1195`). These extend an existing surface (`.xv/picture.md:27`).
- No new outbound calls.

## What the suite asserts after

- A refactor slice opens, and its scenario step writes no red and goes to the maker. A red suite at the start stops it with `suite_not_green_at_start` for the originator (`tests/test_orders.py`). The end-to-end test only asserts that some stop fired.
- The maker's prompt for a refactor slice says "refactor slice" and names `xv slice amend`. A feature slice's prompt does not.
- `--expect-moves` takes only `imports` and `renames`. `--rename` needs `Old=New`.
- An import-only change by the maker is recorded as expected and reaches `ready_to_merge` with no `accept_moves` stop. A named rename to a new path is recorded too. Each of these stops with `unrecorded_move`: an unexpected kind, an unnamed rename, a changed assertion, and a rename on an imports-only slice. A hand-recorded move beside an expected one still stops at `accept_moves`.
- `packet_problems` lists a problem when `expected_moves` is missing, not a number, or wrong (0 or 2 against 1). It lists none when the field matches, including 0 against 0.
- No old assertion moved. `xv wall diff` shows no changed, deleted or added test files since the baseline, and the `test_orders.py` diff adds tests only.

## 1. Shape

shape_change: yes.

- Hint "a module was added" **changes the shape**. `scripts/moves.py` is new (diff `scripts/moves.py:1-85`), and `.xv/picture.md:21` counts "23 modules … `scripts/*.py` (20)". The forecast named it ("a new moved-test comparison script"), but the slice's `decisions` list is empty, so the shape is not `accepted`.
- Hint "an edge between modules was added" **changes the shape** only through the new module: `run → moves`, `moves → wall`, `moves → xvlib`. No edge joins two modules that were apart before. `run` already reaches `wall` (`.xv/picture.md:21`).
- Breadth **narrow**. `moves` is a leaf called from one place (`scripts/run.py:736-744`, `expected_moves`) and adds no table or outbound call. The forecast said `wide`, so this is not wider than the forecast.
- The cleaner's proposal (record `checks.reports`, cleaner): `refactor_scenario` copies the tail of `step` (`scripts/run.py:410-434`: save, verdict, apply_verdict, commit_step, reach). This is inside the shape. It is listed so a person sees the copy.

## 2. Pitch

pitch_contradiction: no. I checked the slice against `.xv/pitch.md:7` ("to vibe with discipline"), `:21` (who uses it) and `:25` ("not for people or projects that will not trust agents to write production code"). A refactor kind with a green-suite oracle and script-decided moves fits the discipline line, and no line names refactors.

## 3. Moved tests

| File | Before | After | Why (the record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/fake_agent.py` (helper, guardian branch, diff `@@ -74,11 +81,13 @@`) | The fake packet had no `expected_moves` line | It writes `expected_moves: $FAKE_PACKET_EXPECTED_MOVES` (default `0`; `omit` leaves the line out) | Point 11's tests need a packet with the field missing or wrong. Sean accepted it at `unrecorded_move` (record `stops`, 03:58:21). | Yes. `scripts/run.py:530` now checks every packet, so every old guardian test needs the field. It asserts nothing less: it is a helper with no assertions. The new `FAKE_MAKER_IMPORT_MOVE` and `FAKE_MAKER_RENAME_MOVE` branches only add. |

Expected moves (0): none. Slice-only tests removed: none. Kept: none. May-not files allowed by the scenario report (`may_not_files`): none.

## 4. The picture

picture_change: yes. Proposed edits, for Sean to accept:

- `.xv/picture.md:21`: change "23 modules … `scripts/*.py` (20) … 60 edges" to 24 modules, 21 scripts and 63 edges, and add "`run` reaches `moves`; `moves` reaches `wall` and `xvlib`."
- `.xv/picture.md:23`: add a role. "`moves` compares each moved test file after the maker and the cleaner against the slice's `expect_moves` (`imports`, `renames`) and `renames` pairs, and records a fit as a move marked `expected`." Change "`accept_moves` counts moves by file and assertion" to add "…except moves marked `expected` (`scripts/orders.py:238-239`)". Add that a recorded move's `from` also covers the old path (`scripts/wall.py:104`).
- `.xv/picture.md:26`: add the refactor kind. "A refactor slice's scenario step runs no agent. It runs the suite, and `suite_not_green_at_start` stops for the originator unless the suite is green. The checks after the scenario (`red_misses_scenario`, `unrecorded_move` before the maker) have nothing to read there."
- `.xv/picture.md:33` (Names): add "`expected_moves` in the packet's front matter is the record's count of expected moves; a wrong or missing one is a `packet_problems` entry."

## 5. The wall

I looked at the 23 tests in `tests/test_refactor_kind.py` and the 5 new tests in `tests/test_orders.py`. None was marked slice-only. Each guards behaviour that lasts: the kind, the flags, the move kinds, the new stop, and the packet count. None is a one-time wording check or only a restatement of another test. No test on the wall before the slice is made dead. No recommendations.

## Findings for the person

These name no scenario line or binding decision that is missed, so they are not sent back.

- **The `expected_moves` check stops nothing.** `scripts/run.py:530` (`checks["packet_problems"] = lint["problems"] + packet_expected_moves(packet, data)`) writes the list, and no code in `scripts/` reads `packet_problems`. `git grep packet_problems` finds only `run.py:530,533`. A guardian that miscounts expected moves still reaches `ready_to_merge`. Amendment 11 asks only that the check "lists a problem", so this is met. The stop option Sean picked (record `stops`, 03:25:49) said "The packet check refuses a packet whose count differs". Compare `.xv/picture.md:74` (decision 12, "Read-only agents are checked, not trusted").
- **An `imports` move can point an old test at different code with no stop.** `scripts/moves.py:29` drops every line that matches the import pattern before comparing (`return [l for l in lines if l and not (imports and re.fullmatch(imports, l))]`). So `from pantry.store import Store` → `from pantry.fake import Store` counts as an expected move. Every assertion still passes, against other code. Point 8 allows exactly "only import or require lines … change", so this is by design, but such a test could now assert less in effect.
- **A `renames` move also rewrites the named names inside strings and expected values.** `scripts/moves.py:37` replaces whole words across the whole file, so with `--rename Foo=Bar`, a change from `assertEqual(x.kind, "Foo")` to `"Bar"` counts as expected. Point 8 ("changes only in the names the slice renames") allows it.
- **An amend on a refactor slice gets no red.** `xv slice amend` sets `data["red"] = None` and `next = "scenario"` (`scripts/run.py:289-290`). For `kind: refactor`, `step` goes straight to `refactor_scenario` (`scripts/run.py:356-357`), which writes no red and passes on a green suite. So a latent bug fixed "only through `xv slice amend`" (point 4) gets fixed with no failing test first.
- **Only `xv prompt` carries the lift of "no refactor, no rename", not the maker's brief.** `skills/maker/SKILL.md:30` is unchanged ("No refactor, no rename"), and the lift is added in `scripts/prompt.py:177-194`. A harness that loads the skill as the whole prompt sees only the ban (`.xv/picture.md:64`, decision 2, "each brief works as the whole prompt of a fresh context"). It fails safe: the maker refactors less.
- **The person-facing `xv-slice` skill still lists three kinds.** `skills/xv-slice/SKILL.md:30` has `--kind feature|defect|prototype` and no `--expect-moves` or `--rename`, so a person opening a slice through the skill is not offered the refactor kind.

## Scenario misses

- 7 (with 6): a move the cleaner makes in an expected kind is not marked expected and stops at `accept_moves`. The refactor lines reach the maker only (`scripts/prompt.py:179`, `if agent != "maker" or …: return ""`). The cleaner's brief still says to record every test move by hand before its commit (`skills/cleaner/SKILL.md:38`), and the pre-commit hook refuses an unrecorded one (`scripts/wall.py` `hook`). `moves.find` then skips any file recorded by hand (`scripts/moves.py:56`, `61`, `68`), and `orders` counts that entry (`scripts/orders.py:238-239`). So when the cleaner tidies an import in an old test on an `--expect-moves imports` slice, the agent has decided the move is not expected, and `accept_moves` fires. No red test has the cleaner make a move. (evidence: diff hunks above; to: scenario)

## Door

**Door:** two-way: code and briefs only. New record fields are additive, and old records keep their shape. A revert undoes it. **Blast radius:** workflow. Every guardian packet on every slice kind is now checked for `expected_moves` (`scripts/run.py:530`).

## Raw data

- Slice record: `.xv/slices/2026-11-04-refactor-kind.md`
- Diff: `git diff 66570aa785961973ad109e9db00dfc167a823e9b..HEAD`
- Wall: `xv wall diff 2026-11-04-refactor-kind`
- Boundary: `.xv/slices/2026-11-04-refactor-kind.boundary.md` (`xv boundary --base 66570aa78596`)

## From the cleaner

- Shape proposal, for people: scripts/run.py: refactor_scenario repeats the tail of step (save, verdict, apply_verdict, commit_step, reach). A shared helper for that tail would remove the copy, but it is a new function with a new concept, so left for the packet.

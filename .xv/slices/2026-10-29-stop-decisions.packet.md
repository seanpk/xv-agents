---
slice: 2026-10-29-stop-decisions
shape_change: yes
pitch_contradiction: no
picture_change: yes
shape_breadth: narrow
moved_tests: 0
door: two-way
blast_radius: adopters
---

# Packet: A stop keeps the decision, not only the answer

**Needs a decision.** The two-people seat (Sean, solo per `.xv/picture.md:52`) has to rule on the shape change: one new module (`scripts/decisions`) and one new `xv` command. Sean already accepted that shape at the last stop (`.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`, record lines 78-84). Since then the only new shape is the edge `decisions → retro`, which amendment 2 asked for. Sean, as originator, also has six points below that do not stop the change. The biggest is (a): every `--resume` answer now needs `--settled`.

## The scenario

There are four issues in this slice.

- **#80.** `xv record offer` puts numbered options on the open stop. Each option carries its `settles` text and an `--amends` mark, and the stop records a `recommended` index. `xv record answer` takes `--pick`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle`, and keeps `budget_change`. `xv prompt` passes on `settled`. `xv decisions [--since]` counts stops per order. The watch brief uses `offer` and sends amending decisions through `xv slice amend`.
- **#62.** An `originator` stop may be answered by a name other than `set_by`.
- **#42.** The scenario agent writes the red in the form `settled` names, or stops.
- **#73.** A step that stops, or ends with no report, keeps `next` on itself.

Amended 2026-10-29 by Sean, three changes:

1. A pick counts as taken only when it equals `recommended`.
2. `xv decisions` reads records through `retro.records()`.
3. `xv record answer --resume` refuses an answer with no `--next`, and the watch brief says so.

May ignore: the watch answering stops by itself, backfilling old records, and #64.

## The recording

None, because this is a feature. To replay: `cd tests && python3 -m unittest -q test_record test_answer_in_prompt test_run`. The red at the record's last scenario step had 25 failures out of 103 tests (`checks.scenario.red_output`). The green at HEAD `a8656ee`: I re-ran the whole suite and got `Ran 362 tests … OK`.

## The boundary picture

From `.xv/slices/2026-10-29-stop-decisions.boundary.md`, as given:

- Touched: `scripts/decisions`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Module added: `scripts/decisions`. None removed. No new outbound calls.
- Edges added: `scripts/decisions → scripts/retro` and `scripts/decisions → scripts/xvlib`. None removed.
- Tables: none.
- Surface paths: none detected. The diff does add a CLI command (`bin/xv:45`, `"decisions": "decisions.py"`) and changes two briefs (`skills/watch/SKILL.md`, `skills/scenario/SKILL.md`).

## What the suite asserts after

- **`offer`.** `xv record offer` stores the options in order, each with `settles` and `amends`, plus `recommended` or null. It refuses an option with no `--settles`, and a `--settles` or `--amends` with no `--option` before it.
- **`answer`.**
  - It keeps the words verbatim, and `--pick n` sets `settled` from the option.
  - `--pick other` needs `--settled`, and so does `--next` (`tests/test_record.py:477`).
  - `cause` must be one of the five values.
  - The log names the watch as the scribe.
  - `bundle` is stored as a list, and a budget moved since the stop gives `budget_change`.
  - `--resume` without `--next` is refused.
- **#62.** An `originator` stop answered by someone other than `set_by` is accepted. This test passed at base too, so it is a guard.
- **`xv decisions`.** It counts only new-style stops, and `--since` filters them. A pick counts as taken only when it equals `recommended`. With no recommendation, nothing counts as taken. It skips records `retro` skips.
- **`xv prompt`.** The prompt shows `settled`, not the raw answer. The brief texts are checked for `offer`, `--settles`, `xv slice amend`, the `--resume`/`--next` rule and "does not swap in a test".
- **`next`.** After an `unrecorded_move` stop on the maker, `next` is `maker`. After a scenario run with no report, `next` is `scenario` and the exit code is 10.
- No old assertion moved (section 3).

## 1. Shape

shape_change: **yes**, breadth **narrow**. The forecast expected `wide` (record `forecast.shape`), so this is not wider than forecast.

- **Hint "a module was added": changes the shape.** `scripts/decisions.py` is new (58 lines), and `bin/xv:45` gives it a command. `.xv/picture.md:21` counts the modules ("22 modules … `scripts/*.py` (19)"), and `.xv/picture.md:27` names the `xv` CLI as a surface. The decision record above already accepts this.
- **Hint "an edge between modules was added": inside the shape.** `decisions → xvlib` reaches "the shared base" (`.xv/picture.md:23`). `decisions → retro` (`scripts/decisions.py:15`, `from retro import records`) is the reuse amendment 2 asked for. It removes the duplicate record reader that the first pass flagged. `retro` is a side loop (`.xv/picture.md:23`), so `decisions` now loads `retro`'s imports (`agentcli`, `promote`, `prompt`, `spend`) when it runs. That is a dependency, not a new coupling between parts that were apart.
- **Record format: inside the shape.** The stops get new keys: `options`, `recommended`, `pick`, `settled`, `new_info`, `cause`, `why`, `bundle`, `budget_change`, plus a transient `budget_seen` (`scripts/record.py:222`, `:260`, `:305-306`). They are additive, and older code ignores them.

## 2. Pitch

pitch_contradiction: **no**. I read `.xv/pitch.md:7` ("vibe with discipline"), `:17` ("executable and empirical … shareable"), `:21` (who uses it) and `:25` (who it is not for; "never be a teapot"). Counting decisions per order with `xv decisions` serves "empirical" (`:17`). Keeping `settled` so the next agent can act without the chat serves "discipline" (`:7`). The change serves no one new and does nothing the pitch rules out.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at:

- The record has `moved_tests: []` (`.xv/slices/2026-10-29-stop-decisions.md:15`).
- `xv wall diff 2026-10-29-stop-decisions` (baseline `30761c7`) has `changed`, `deleted`, `added` and `fewer_assertions` all empty. The cleaner's wall check agrees (`.xv/slices/2026-10-29-stop-decisions.md:27`, `checks.cleaner.wall`).
- `git diff 5d061c1..HEAD -- tests` only appends classes to `tests/test_record.py`, `tests/test_answer_in_prompt.py` and `tests/test_run.py`. It also adds a `FAKE_NO_REPORT` branch to `tests/fake_agent.py:15-17`.

Slice-only tests removed: none. Kept: none.

## 4. The picture

Proposed edits for Sean. I do not write to the picture.

- `.xv/picture.md:21`: "22 modules … `scripts/*.py` (19) … 56 edges" becomes 23 modules, 20 scripts and 58 edges (two added, none removed, per the boundary picture).
- `.xv/picture.md:23`: add "`decisions` reads every slice record through `retro.records()` and counts answered stops per order: picks that took the recommendation, `new_info: none`, and causes."
- `.xv/picture.md:26`: the last sentence says only the unsafely joined red keeps `next` on `scenario`. Generalize it: a step that stops (any order except `ready_to_merge`) or ends with no report keeps `next` on that step (`scripts/run.py:392-393`). Every `--resume` answer must then name `--next` (`scripts/record.py:283`).
- `.xv/picture.md:31` ("'Originator' … and `set_by` appear to mean the same seat"): after #62, someone other than `set_by` may answer an `originator` stop. Say so.
- Names (`.xv/picture.md:30-39`): add "`settled` is what an answer made true, written by the watch as the person's scribe; the raw words stay in `answer`. An offer is the numbered options put on an open stop."

## For the originator (do not stop the change)

- **(a) Every resumed answer now needs `--settled`, so the offered text is never used on resume.**
  - `scripts/record.py:283` refuses `--resume` without `--next`.
  - `scripts/record.py:295` refuses any `--next` without `--settled`. It checks `a.settled`, not the `settled` filled from the option at `:292`.
  - So `--pick 1 --next maker --resume` is refused even though option 1 has `settles` text. The scenario says "With `--pick <n>` and no `--settled`, it is the offered option's text" (record line 51). That now holds only for answers without `--resume`.
  - The scenario requires `--settled` "when the answer sends work back" (record line 58), but `:295` treats every `--next` as sending work back, including going forward to `close`. `tests/test_record.py:477-482` pins that reading.
  - The watch brief understates this. `skills/watch/SKILL.md:50` says `--settled` is required "when the answer sends work back or the pick is `other`". `:45` still shows `[--next <step>]` as optional, while `:48` says it is required.
- **(b) The README's answer examples are now refused.** `README.md:189` (`xv record answer … --answer "merge" --resume`) and `README.md:295` (`… --answer "<their words>" --resume`) have no `--next`, so `scripts/record.py:283` exits 2 on them. The README is not in the diff.
- **(c) The CHANGELOG line misses the amendment's brief change.** `CHANGELOG.md:7` describes #80/#62/#42/#73 but not the rule that `--resume` needs `--next`, which the watch brief now carries (`skills/watch/SKILL.md:48`). Every brief change needs a line (`.xv/picture.md:60`).
- **(d) The decision record cannot be read without the chat.** `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md:10-11` holds only "1: 1 / 2: 1". The solo stop asked to "write down what you weighed". What was decided lives only in the scenario amendment (record lines 78-84). This is the gap #80 sets out to close.
- **(e) `budget_change` is missed for stops raised by `xv step`.** Stops appended at `scripts/run.py:394` carry no `budget_seen`. For those stops, `budget_change` is recorded only if the watch ran `offer` first (`scripts/record.py:260`, `:305-307`). The scenario asks for it "when the answer moved the budget" (record line 55). This was also flagged on the first pass.
- **(f) The scribe log line says more than was written.** `scripts/record.py` logs "wrote settled, new_info and cause" when any one of the three was given, so a pick-only answer is logged as having all three.

## Door

**Door:** two-way. A revert undoes the code and the two briefs. Extra keys on stops written in the meantime are ignored by older code, and the `.xv/decisions/` file is plain text. **Blast radius:** adopters. The watch and scenario briefs are a surface every adopting repo runs (`.xv/picture.md:27`), and every answer in their watch loop now needs `--next` and `--settled`.

## Raw data

- Slice record: `.xv/slices/2026-10-29-stop-decisions.md`
- Diff: `git diff 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d..a8656ee`
- Wall: `xv wall diff 2026-10-29-stop-decisions`
- Boundary: `xv boundary --base 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d` (`.xv/slices/2026-10-29-stop-decisions.boundary.md`)
- Decision on the shape: `.xv/decisions/2026-10-29-2026-10-29-stop-decisions.md`

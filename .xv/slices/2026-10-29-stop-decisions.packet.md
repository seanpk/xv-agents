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

**Needs a decision.** Two people (or Sean, solo per `.xv/picture.md:52`): the shape change, which is one new module and one new `xv` command. Sean, as originator, has three questions. (a) `next` now stays on *every* stopped step, including after decision stops where the work is done. (b) What "pick taken" counts in `xv decisions`. (c) The picture edits in section 4.

## The scenario

There are four issues in one slice. #80: `xv record offer` puts numbered options on the open stop. Each option has the `settled` text it would record and an `--amends` mark, and the stop holds the watch's `recommended` index. `xv record answer` takes `--pick`, `--settled`, `--new-info`, `--cause`, `--why` and `--bundle`, and the stop keeps them along with any `budget_change`. `xv prompt` passes `settled`, not the raw words. `xv decisions [--since]` counts stops per order. The watch brief uses `offer` and routes amending decisions through `xv slice amend`. #62: an `originator` stop may be answered by a name other than `set_by`. #42: the scenario brief writes the form of red that `settled` names, or stops. #73: a step that stops or ends with no report keeps `next` on that step.

May ignore: the watch answering stops by itself; backfilling old records (`xv decisions` counts only new-style stops); #64.

## The recording

None, because this slice is a feature. To replay the red and the green: `cd tests && python3 -m unittest test_record test_run test_answer_in_prompt`, at `70e9197` (red: `invalid choice: 'offer'`) and at `HEAD` (green). The whole suite at HEAD: `Ran 355 tests … OK`, which I re-ran.

## The boundary picture

From `xv boundary` (`.xv/slices/2026-10-29-stop-decisions.boundary.md`), as given:

- Touched: `scripts/decisions`, `scripts/prompt`, `scripts/record`, `scripts/run`.
- Module added: `scripts/decisions`. None removed. No new outbound calls.
- Edge added: `scripts/decisions → scripts/xvlib`. None removed. Total edges after: 57.
- Tables: none. Surface paths: none detected. The diff also adds a command to the CLI map (`bin/xv:45`, `"decisions": "decisions.py"`) and changes two briefs (`skills/watch/SKILL.md`, `skills/scenario/SKILL.md`).

## What the suite asserts after

- `xv record offer` stores the options in order, with `settles` and `amends`, and `recommended` (or null). It refuses an option with no `--settles`, and a `--settles`/`--amends` with no `--option` before it.
- `xv record answer --pick n` keeps the words verbatim and sets `pick`, `settled` (taken from the option's text), `new_info`, `cause` and `why`. It writes no `recommended_by`. `--pick other` and `--next` each require `--settled`. `cause` must be one of the five. The log names the watch as scribe. `--bundle` is stored as a list. A budget moved between the stop and the answer gives `budget_change`.
- An originator stop answered by `sam`, who is not `set_by`, is accepted (#62). This passed at base too; it is a guard.
- `xv decisions` counts new-style stops per order, skips stops without `pick`/`settled`, and `--since` hides earlier stops.
- `xv prompt maker` shows `settled`, not the raw answer. The scenario brief mentions `settled`, "lint rule" and "does not swap in a test". The watch brief mentions `xv record offer`, `--settles` and `xv slice amend`.
- After an `unrecorded_move` stop on the maker, `next` is `maker`. After a scenario run with no report, `next` is `scenario` and the exit code is 10.
- No old assertion moved (section 3).

## 1. Shape

shape_change: **yes**, breadth **narrow**. The forecast expected `wide` (record front matter `forecast.shape`), so this is not wider than forecast.

- **Hint "a module was added": changes the shape.** `scripts/decisions.py` is new (61 lines), and `bin/xv:45` maps a new command to it. The picture counts the modules ("22 modules … `scripts/*.py` (19)", `.xv/picture.md:21`) and names the `xv` CLI as a surface (`.xv/picture.md:27`). Both are now one larger. The brief lists a new module and a new user surface as shape changes.
- **Hint "an edge between modules was added": inside the shape.** `decisions → xvlib` is an edge to "the shared base (config, git, record paths)" (`.xv/picture.md:23`), which every script already reaches.
- **Coupling, inside the shape but duplicated.** `.xv/picture.md:23` says "`record` owns the slice record". `scripts/decisions.py:22-26` globs `.xv/slices/*.md` and reads the records itself, as `scripts/retro.py:30-42` (`records()`) already does. Its skip list is narrower than retro's. It does not skip `packet-<date>.md`, which `scripts/listen.py:148` writes into the same folder. It has no `try/except` around `read_doc` and no `data.get("id")` check. So one unreadable front matter in any `.xv/slices/*.md` makes `xv decisions` exit 2, where `retro` skips the file. I have not reproduced this, because `xv decisions` is not on my command list.
- **Record format, inside the shape.** New stop keys: `options`, `recommended`, `pick`, `settled`, `new_info`, `cause`, `why`, `bundle` and `budget_change`. There is also one key the scenario does not name: `budget_seen`, written on every stop by `xv record stop` (`scripts/record.py:222`) and by `offer` (`scripts/record.py:261`), and popped on answer. Stops raised by `xv step` (`scripts/run.py:342`, `:394`) do not get `budget_seen`. For those stops, `budget_change` is recorded only if the watch ran `offer` first. The scenario asks for `budget_change` "when the answer moved the budget" (record, "The offer and the answer").

## 2. Pitch

pitch_contradiction: **no**. I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `:17` ("makes Xtreme Vibing executable and empirical"), `:21` (who uses it) and `:25` (not for people who will not trust agents; "never be a teapot"). Recording a decision's options, pick and cause, and counting them with `xv decisions`, falls under "empirical" (`:17`). The change serves no one new and does nothing the pitch rules out.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| none | | | | |

What I looked at: the record has `moved_tests: []`. `xv wall diff 2026-10-29-stop-decisions` (baseline `70e9197`) shows `changed`, `deleted`, `added` and `fewer_assertions` all empty. `git diff 5d061c1..HEAD -- tests` only adds: new classes appended to `tests/test_record.py` (after line 401), `tests/test_answer_in_prompt.py` (after line 115) and `tests/test_run.py` (after line 255). `tests/fake_agent.py:15-17` adds a `FAKE_NO_REPORT` branch that only runs when that variable is set.

Slice-only tests removed: none. Kept: none.

## 4. The picture

Proposed edits for Sean to accept or reject. I do not write to the picture.

- `.xv/picture.md:21`: "22 modules … `scripts/*.py` (19) … 56 edges" becomes 23 modules, 20 scripts and 57 edges.
- `.xv/picture.md:23`: add "`decisions` reads every slice record, as `retro` does, and counts answered stops per order: picks, `new_info: none` and causes."
- `.xv/picture.md:26`: the last sentence says only the unsafely joined red keeps `next` on `scenario`. Generalize it: any step that stops (every order except `ready_to_merge`) or ends with no report keeps `next` on that step (`scripts/run.py:392-393`).
- `.xv/picture.md:31`: "'Originator', 'the person who set the work going' and `set_by` appear to mean the same seat". After #62, an `originator` stop may be answered by someone other than `set_by`, so the seat is not always the `set_by` person. Say so.
- Names (`.xv/picture.md:30-39`): add "`settled` is what an answer made true, written by the watch as the person's scribe. The raw words stay in `answer`. An offer is the numbered options put on an open stop."

## For the originator (do not stop the change)

- **(a) `next` stays put after decision stops too.** `scripts/run.py:392-393`:
  ```
  if st["order"] != "ready_to_merge" and not checks.get("red_joined"):
      data["next"] = agent
  ```
  This applies to every order, including ones raised after a step did its work: `shape_change`/`pitch_contradiction` after the guardian, `budget_spent` after the maker, and the `red_check` this very slice hit. `xv run` reruns whatever `next` names (`scripts/run.py:630-647`). So an answer given with `--resume` and no `--next` now reruns the same step and spends again; before this change it went on. Going on needs `--next <step>`, and `--next` now requires `--settled` (`scripts/record.py:291-293`). The watch brief still shows `[--next <step>]` as optional and does not say this (`skills/watch/SKILL.md`, the new `xv record answer` line). The scenario's wording ("When a step stops … `next` stays on that step", record line 76) matches the code literally. Its reason ("so a later step cannot start on missing work") fits `no_report` and `unrecorded_move`, but not stops where the work is done. No test answers a decision stop and then runs.
- **(b) "How often the pick was taken."** The scenario defines `recommended` as "the index of the watch's pick" (record line 45) and asks `xv decisions` for "how often the pick was taken" (record line 62). `scripts/decisions.py:37` counts any numbered pick (`isinstance(st.get("pick"), int)`), not `pick == recommended`. A person who picks option 2 against a recommendation of 1 counts as "pick taken". The tests do not tell the two readings apart (`tests/test_record.py`, `DecisionsReportTest`).
- **(c) The CHANGELOG line names the decision.** `CHANGELOG.md:7` says "This changes two briefs and a standing order's effect; Sean decided it, solo". `.xv/picture.md:60` requires two people and a line for a brief change, and the repo runs solo (`.xv/picture.md:52`). The record's `decisions` is `[]`. The authority is Sean's own scenario ("This changes a brief, so `CHANGELOG.md` gets a line"). Sean should confirm the line at merge.

## Door

**Door:** two-way. A revert undoes the code and the briefs, and the extra keys on stops written meanwhile are ignored by older code. **Blast radius:** adopters. The watch and scenario briefs reach every adopting repo, and every new stop now carries `budget_seen`.

## Raw data

- Slice record: `.xv/slices/2026-10-29-stop-decisions.md`
- Diff: `git diff 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d..9a38629`
- Wall: `xv wall diff 2026-10-29-stop-decisions`
- Boundary: `xv boundary --base 5d061c1f1a5a5b18b5fe7a3b8c5ad50e8bcc436d` (`.xv/slices/2026-10-29-stop-decisions.boundary.md`)

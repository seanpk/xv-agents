# Exploration notes: pairing

Branch `explore/pairing`, from `main` at 5017bdb. A working build of the scenario as Sean agreed it (draft 2, 2026-11-11), made outside XV's slice process, so the scenario can be written from what runs. Open the slice with `xv slice new --from explore/pairing`. Not a release: nothing under `.xv/`, no `docs/decisions.md` and no `CHANGELOG.md` was edited; their drafts are below.

## What runs

New module `scripts/pairing.py`, routed in `bin/xv` as `xv pairing`.

### 1. Opening a pairing

`xv pairing start <id> --by <name> --why "<why>" [--session <id or transcript>] [--agent <name>]`

- It answers the open stop as a pairing: `answered_by` is the person, `answer` is `pairing: <why>`, `pick` is `pairing`, `settled` says who paired with whom and why, and the stop gets `pairing: <n>`.
- At a send-back it answers nothing (the watch already answered it); it marks the send-back with `pairing: <n>`. A slice is at a send-back when its last stop is the watch's and no step has reported since.
- It writes a `pairings` entry: `n`, `by`, `agent`, `session` (`{harness, id, transcript}`), `why`, `started_at`, `start_head`, `order`, `step`, `opened_at` (`stop` or `send-back`), `amendments_at_start`, and `prefix`.
- It sets `status: pairing`, logs the opening, commits the record as `xv(<id>): pairing <n> opened by <name> with <agent>`, and prints the commit prefix.
- The session comes from `--session` (a transcript path or a session id), else from `CLAUDE_CODE_SESSION_ID`. The transcript is found at `$CLAUDE_CONFIG_DIR/projects/*/<id>.jsonl` (or `~/.claude/...`). With no session, the pairing still opens, and the log says its spend cannot be read.
- It refuses: a name that is not `set_by`; a slice with no open stop or send-back; a slice where a pairing is already open; a closed or abandoned slice; an empty `--why`; a stop for two people unless the repo runs solo.

### 2. While a pairing is open

- `xv step`, `xv run`, `xv close`, the start of `xv slice rebase`, and `xv record report` refuse with exit 2 and name the pairing: number, who with whom, since when, why, and how to end it (`record.refuse_in_pairing`).
- `xv record move` records the move in the person's name and with `pairing: <n>`. A `--by` that names anyone else is refused.
- `xv record set` and `xv record add` refuse the `pairings` field.
- The watch skill says the watch's session does the work at the person's direction, starts each commit with `pairing (<name> with <agent>):`, and still may not merge, approve, accept a move or a picture change, set a budget, or answer a stop for the person.
- The pre-commit wall hook and `xv wall check` let a test the open pairing added to an old file through. A line the open pairing removed or changed with no move still fails the hook.

### 3. Tests that are not blind

- `xv pairing end` lists each test file (under `tests.paths`, or a red file) that the pairing added or changed and that still exists, in the entry's `not_blind`. The log says they are not blind and that the guardian checks them in a fresh context.
- The packet line names them.
- `xv prompt guardian <id>` names them as not blind and asks the guardian to check each as it checks the code, a self-referential assertion included. Other agents' prompts do not.
- The scenario agent's red is untouched: `red` stays as it was.

### 4. Ending a pairing

`xv pairing end <id> --next maker|cleaner|guardian|scenario`

- `--next close` is refused: the guardian runs fresh after a pairing. Any other step outside the four is refused.
- `--next scenario` is refused unless the body holds more `### Amended` sections than when the pairing opened (`xv slice amend`).
- It refuses uncommitted work (anything but the slice's own `.xv/slices/<id>.*` files) and names each file.
- It writes `ended_at`, `end_head`, `next`, `commits` (the pairing's commits, not the `xv(<id>):` ones), `unprefixed` (commits without the prefix), `not_blind`, `spend` and `spend_note`.
- It appends to the answered stop's `settled` that the pairing ended and where the slice resumes, so the next agent's prompt says so. When `--next` is the stop's step or earlier, the stop gets `sent_back` and `sent_back_to`, as `xv record answer` does.
- It sets `next`, sets `status: working`, logs the end, and commits the record (and the packet, when there is one) as `xv(<id>): pairing <n> ended, resumes at <step>`.
- The spend: it sums the pair session's Claude Code transcript (and its subagents) for the turns logged from `started_at` to the end of the second the pairing ended in (`spend.from_claude_session` with `since` and `until`). The row goes into `spend` with `step: pairing`, so `slice_spend`, the budget check, and the guide row count it.
- When the spend cannot be read (no session, a harness with no reader, no transcript, no turns in the window), `spend` is null, `spend_note` says why, and the log and the packet say so.
- The output gives the budget state; when the budget is spent it says the next step stops for the originator. The next `xv step` raises `budget_spent` before it runs.

### 5. Moves in a pairing

- `xv pairing end` refuses while a test file that existed at `start_head` lost or changed a line (other than blank, comment or import) with no move recorded in this pairing, and names each file. A move recorded before the pairing does not cover a change made in it.
- A move recorded in the pairing is in the person's name (point 2).
- A test the pairing only added, to a new or an old file, needs no move. `wall.check` does not count an old file whose every change since the baseline lies inside pairings. A change after the pairing ended counts again. The CI form (`xv wall check --base`) covers a pairing's `not_blind` file with no removed line.

### 6. The packet

- `packet.note_pairings` writes `## Pairings` with one line per pairing: who with whom, the session, why, the commits, the resume step, the spend (tokens with in, out and cache write; cache read named as not counted; turns; usd or "not reported"), the tests that are not blind, and any commit without the prefix. An open pairing's line says "Open since".
- It runs in `packet.packet_checks`, so `xv step guardian` and `xv record packet` both write it, and in `xv pairing end` when a packet exists. A second run replaces the section. A packet with no pairing is left as it is.

### 7. Docs

- `skills/watch/SKILL.md`: a new section, "A pairing"; two may-not lines now say "outside a pairing"; "Writes to the slice record" names `xv pairing`.
- `README.md`: the watch's row in the agent table, a paragraph under "The stops", and a line under "The budget and the spend".
- `docs/slice-record.md`: the `pairing` status and the `pairings` field.
- `bin/xv` help lists `xv pairing`.
- The picture, the decision and the CHANGELOG line are drafts below.

## Design choices to review

1. **The session is found from `CLAUDE_CODE_SESSION_ID`, or named with `--session`.** The record keeps `{harness, id, transcript}`. Alternative: always require `--session`, or keep only the id and find the transcript at the end.
2. **A pairing opens with no session found.** The spend is then unreadable, and the log says so at start and at end. Alternative: refuse to open without a readable session, so no pairing spend is ever lost.
3. **The spend window is cut by timestamps.** It counts turns logged from `started_at` to the end of the second the pairing ended in, including the pair session's subagents. Alternative: cut by the transcript's line count at start and at end, which does not depend on clocks.
4. **Only Claude Code transcripts are read.** A Codex, Grok or opencode pair has its spend recorded as "not read". Alternative: add readers for those harnesses' session logs.
5. **Opening answers the stop with the same fields as `xv record answer`, plus `pick: pairing`.** It writes no `cause`, `new_info` or decision record, even for a solo two-people stop. Alternative: make `--cause` and `--new-info` required on `xv pairing start`, or write a decision record for a two-people stop.
6. **A stop for two people is refused unless the repo runs solo.** The person answers it with `xv record answer` first. Alternative: let the pairing answer it with two names.
7. **"At a send-back" means the last stop is the watch's and no step has reported since.** Alternative: allow a pairing at any time the slice is not running.
8. **`--next guardian` after the guardian already ran runs a full guardian pass again.** Alternative: a short re-pass (#178, which the scenario lets us ignore).
9. **"A test written or changed in a pairing" is the diff from `start_head` to `end_head`, filtered to `tests.paths` and the red files, without deleted files.** Alternative: read it from the pairing's commits only, or include deleted files.
10. **A test the pairing only added needs no move, and the wall does not stop on it.** `wall.check` skips an old test file whose changes since the baseline all lie inside pairings (and, in an open pairing, removed no line). Alternative: treat a pairing like the maker, so any change to an old test file needs a move.
11. **The commit prefix is checked, not enforced.** `xv pairing end` lists commits without it in the record and the packet, and does not refuse. Alternative: refuse the end until each commit has the prefix.
12. **`xv slice rebase` and `xv record report` also refuse during a pairing,** besides `xv step`, `xv run` and `xv close`. Alternative: refuse only the two commands the scenario names.
13. **The guardian's prompt names the tests that are not blind.** This adds a line to what the guardian is told, not to its brief. Alternative: leave the prompt as it is and rely on the record and the packet.
14. **The budget is not checked during a pairing.** It is checked before the next step, as for any step, and `xv pairing end` says when it is spent. Alternative: stop at `xv pairing end` itself when the budget is spent.
15. **`xv pairing end` refuses uncommitted work.** The slice's own `.xv/slices/<id>.*` files are not counted. Alternative: commit everything left as the last pairing commit.
16. **`pairings` is not in the record's fixed `FIELDS`.** Old records do not gain an empty `pairings: []`; readers use `data.get("pairings")`. Alternative: add it to `FIELDS`, so every record shows it.
17. **`status` is `pairing` while a pairing is open.** Alternative: keep `working` and read the open pairing from `pairings`.
18. **`--next maker` after a pairing at a maker stop counts as a send-back to the maker,** so `maker_sendbacks` counts it at close. Alternative: never mark a pairing's resume as a send-back.

## Questions for Sean

1. Should `xv pairing start` refuse when it cannot find a transcript to read the spend from, rather than open and note it?
2. Is cutting the spend window by timestamps good enough, or should it use the transcript's line count at start and end?
3. Should a pairing be able to answer a two-people stop when two names are given, or must that stop be answered first?
4. Should `xv pairing end` refuse commits without the `pairing (<name> with <agent>):` prefix, or only list them as now?
5. Is a test the pairing only added to an old file not a move (as built), or should it need a move like the maker's?
6. Should the guardian's prompt name the tests that are not blind, or is the record and the packet enough?
7. Is refusing `xv slice rebase` and `xv record report` during a pairing right, beyond `xv step`, `xv run` and `xv close`?
8. Should a pairing's spend rows get their own guide row key, or count under the session's model like any step?
9. The watch's session outside a pairing still has no spend on record (#175): should the pairing window be the only part of the watch's session that counts?

## Drafts

### Picture lines (`.xv/picture.md`)

In "The shape", replace the module count and edge count:

```
- 27 modules, all flat Python files: `scripts/*.py` (24) and `evals/{run,grade,report}.py`.
  `.xv/boundary-all.md` shows 74 edges between them.
```

In "The shape", after the line "`names` holds `covers_name_found`, ...", add:

```
  `pairing` reaches `record`, `packet`, `spend`, `wall` and `xvlib`, and no module imports it.
```

In "The shape", after "`init`, `slice`, `run`, `step`, `close` and `guard` all land in `run.py`, the largest script.", add:

```
  `pairing` lands in `pairing.py`.
```

In "The shape", under "Roughly", after the directed-edit lines, add:

```
  `xv pairing start` answers the open stop as a pairing, or opens at the watch's own send-back when no step has reported since, and writes a `pairings` entry in the record.
  Only the person who set the work going opens one, and a stop for two people is answered first unless the repo runs solo.
  While a pairing is open, `record.refuse_in_pairing` refuses `xv step`, `xv run`, `xv close`, the start of `xv slice rebase`, and `xv record report`.
  A move recorded while a pairing is open is in the person's name and carries the pairing's number.
  `xv pairing end` refuses uncommitted work, and an old test file that lost or changed a line in the pairing with no move recorded in it.
  `--next` is `maker`, `cleaner` or `guardian`; `scenario` needs an amendment made since the pairing opened, and `close` is refused.
  It reads the pair session's Claude Code transcript from the pairing's start to its end (`spend.from_claude_session` with `since` and `until`) and adds a spend row with `step: pairing`, which `spend.slice_spend` counts.
  When the spend cannot be read, the record's `spend_note`, the log and the packet say why.
  A test file the pairing added or changed is listed in `not_blind`, and `xv prompt guardian` names it.
  `wall.check` does not count a test file whose changes since the baseline all lie inside pairings, unless an open pairing removed a line from it.
  `packet.note_pairings` writes one line per pairing under `## Pairings`, from `packet.packet_checks` and from `xv pairing end`.
```

In "The shape", in the state paragraph, after "The slice record also holds `amended_at_report`, the report count at the last amendment.", add:

```
  The slice record also holds `pairings`, one entry per pairing, and `status` is `pairing` while one is open.
```

In "Names", add:

```
- A pairing is the person who set the work going working on a slice with the watch's own session, at an open stop or a send-back (#146).
  It was first called a sortie.
  In a pairing, and only there, the watch does an agent's work, at the person's direction.
```

### The decision (`docs/decisions.md`, a new section)

```
## Pairing

92. **In a pairing, and only there, the watch does an agent's work.** At an open stop or a send-back, the person who set the work going may pair with the watch's own session: `xv pairing start` answers the stop as a pairing, and `xv step` and `xv run` refuse until `xv pairing end`. Pairing works because the person and the watch both have the slice's context; handing work to a fresh agent is what had not worked (Sean, 2026-11-11). It is for when handoffs to agents have not worked, or when what is left is too small for a pass through the loop. The watch still may not merge, approve, accept a move or a picture change, set a budget, or answer a stop for the person. A test written or changed in a pairing is not blind, so the record and the packet say so and the guardian runs fresh after: a pairing ends at the maker, the cleaner or the guardian, never at close, and at the scenario agent only after an amendment. A move recorded in a pairing is in the person's name. The pair session's spend for the time the pairing was open counts in the slice's actual and its budget; when it cannot be read, the log and the packet say so. Only the person who set the work going pairs; stand-ins and handoff come later.
```

### The CHANGELOG line (`CHANGELOG.md`, under Unreleased)

```
- A pairing (#146). At an open stop or a send-back, the person who set the work going pairs with the watch's own session: `xv pairing start <id> --by <name> --why "<why>"` answers the stop as a pairing and writes a `pairings` entry, and `xv step`, `xv run`, `xv close` and `xv slice rebase` refuse until `xv pairing end <id> --next maker|cleaner|guardian` (`scenario` after an amendment; `close` is refused). The watch's may-not list changes: in a pairing, and only there, it writes and changes tests and code at the person's direction, each commit starting with `pairing (<name> with <agent>):`; it still may not merge, approve, accept a move or a picture change, set a budget, or answer a stop for the person. A move recorded in a pairing is in the person's name, and `xv pairing end` refuses while an old test changed or removed in it has no move. A test written or changed in a pairing is not blind: the record, the packet and the guardian's prompt say so, and the guardian runs fresh after. The pair session's spend while the pairing was open, read from its Claude Code transcript, counts in the slice's actual and the budget; when it cannot be read, the log and the packet say so. The packet gets one line per pairing under `## Pairings`. Decided by Sean, solo. It moves no position on xtremevibing.com.
```

## Tests added

- `tests/test_pairing.py`: 42 tests in six classes.
  - `StartTest` (11): point 1, the session lookup, and the refusals.
  - `WhileOpenTest` (7): points 2 and 5, the loop's refusals and moves in the person's name.
  - `EndTest` (11): point 4, the resume step, the spend window, the budget check, and unreadable spend.
  - `NotBlindTest` (6): points 3 and 5, `not_blind`, the guardian's prompt, the move check, and the wall.
  - `PacketTest` (5): point 6, the `## Pairings` lines.
  - `DocsTest` (2): point 7, the watch skill and the README.

## Suite

`python3 tests/run.py --jobs 8`: 1225 tests, OK (1183 on main, plus 42).

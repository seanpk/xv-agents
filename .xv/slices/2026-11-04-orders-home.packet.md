---
slice: 2026-11-04-orders-home
shape_change: no
pitch_contradiction: no
scenario_miss: no
picture_change: yes
shape_breadth: none
moved_tests: 1
door: two-way
blast_radius: stops
---

# Packet: Every stop rule is decided in orders.py: #105, with #103, #84, #99 and #109

Nothing stops for two people. The originator decides four things: whether an answered `shape_wider_than_forecast` stop should quiet that stop whatever the answer was (check 1, finding A); the picture edits (check 4); the four wall marks (check 5); and whether the CHANGELOG line can say "Decided by Sean, solo" before any decision exists (finding D).

## The scenario

The stop rules move into `scripts/orders.py`. Whether a miss repeats is read from the record alone (1). `xv step`, `xv run`, `xv record packet` and the session path write the same facts, and one function applies what `orders` returns, `next` included (2). There is one shared definition of allowed values, one shared test-name matcher, and the wall-flag block is split out of `cmd_answer` (3). An accepted shape does not stop again as wider than forecast; `accept_moves` counts moves, not entries; the docs say `yes`, `no` or `accepted` (4). The pre-step `budget_spent` stop is marked, and `prototype_budget_spent` needs `--settled` (5). Accepted slice-only marks survive a scenario re-run and are not asked about again (6). A test fails when the docs miss an allowed packet value (7). A move is recorded once and keeps its slice-only flag (8). The `docs/slice-record.md` changes are in, and `who` is a list in new decisions (9).

May ignore: the new stops for #20, #15, #113 and #117; old slice records; brief wording unless a moved rule makes a brief untrue.

## The recording

None: this is a feature. To replay: `cd tests && python3 -m unittest test_orders.OneHomeTest test_record.OneHomeRecordTest test_packet.PacketFieldDocsTest test_run.EveryPathOneVerdictTest.test_a_repeated_scenario_miss_gets_the_same_verdict_on_every_path test_run.PreStepBudgetStopTest.test_the_stop_xv_step_raises_before_a_step_is_answered_without_settled_once_the_budget_is_raised`. At `9ef4bdf` (pre-maker), 18 failures (the record's `checks.scenario.red_output`). At HEAD, I ran it myself: 26 tests, OK. Whole suite: 850 OK (the record's `checks.cleaner`).

## The boundary picture

From `.xv/slices/2026-11-04-orders-home.boundary.md`, as given. Touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`, `scripts/xvlib`. Modules added or removed: none. Edges added or removed: none. Tables: none. Surface paths: none. Outbound calls added: none. Shape hints: none.

## What the suite asserts after

- `orders.verdict` ignores a stale `miss_repeat` or `missed_repeat` flag. A miss counts as a repeat only when a watch send-back for it sits before the current report.
- `run.py` and `record.py` no longer contain repeat logic, an inline `("yes", "no"` tuple, an inline `(?!\w)` matcher, or `--accept-wall` handling inside `cmd_answer`. These are source-text checks.
- `shape_wider_than_forecast` does not fire when `shape_change` is `accepted` or when a stop of that order has any answer. It still fires when neither holds.
- `accept_moves` says "1 old test(s) moved" for two entries with the same file and assertion.
- An accepted slice-only mark is kept across a scenario re-run and not asked about again; only a new mark is asked about.
- A move recorded by both `xv record move` and a report is one entry, and it keeps `slice_only`.
- A new decision's `who` is a list; an old string `who` still lets `xv decisions` and `xv prompt` exit 0.
- `prototype_budget_spent`, and a hand-raised `budget_spent`, need `--settled`. The pre-step stop `xv step` raises does not.
- The packet template, the README and the `docs/` tables name every value the packet lint allows for `shape_change` and `pitch_contradiction`. `docs/slice-record.md` names `accepted_wall`, `refused_wall`, `settled`, `ready_to_merge` and the list.
- A repeated scenario miss leaves the same verdict on `xv step`, `xv run`, and `xv record report` plus `xv record packet`: open `scenario_miss` for the originator, `stopped`, next `guardian`.
- Moved: `AcceptWallFlagTest` now expects `who == ["pat"]` where it expected `"pat"`.

## 1. Shape

shape_change: no. The boundary picture shows no module, edge, table, surface or outbound call added or removed, and no shape hints (`.xv/slices/2026-11-04-orders-home.boundary.md`, "Edges: added: none / removed: none"). `record` already reached `packet` and `orders` (`.xv/picture.md:21`, "`record` reaches `orders` and `packet`"), so `import packet as packetlib` at module top (`scripts/record.py:19`) only moves an existing import. Breadth is `none`: everything sits inside the current shape. The forecast said `wide`, so nothing is wider than forecast.

Findings inside the shape, for the originator:

- **A. Any answer quiets the two-person shape stop for the rest of the slice.** `scripts/orders.py:227-229`: `accepted_shape = data.get("shape_change") == "accepted" or any(s.get("order") == "shape_wider_than_forecast" and s.get("answer") for s in data.get("stops") or [])`. Scenario point 4 asks this only for "a shape the person accepted". The rule doesn't read what the answer was or the breadth it was given at. Say two people answer "narrow it" with `--next maker`, and the next guardian pass reports `wide` against a `none` forecast. No `shape_wider_than_forecast` stop fires. The new test only covers the answer "go on" (`tests/test_orders.py`, `test_a_shape_wider_stop_the_person_already_answered_does_not_stop_again`).
- **B. `xv record packet` now records stops, not only send-backs.** `scripts/record.py:552-553` calls `apply_verdict`, which appends an open stop and sets `status` (`scripts/record.py:577-590`). Before, `cmd_packet` recorded only send-backs (the removed `for f in orders.evaluate(...)` block). Scenario point 2 asks for this. Nothing in `cmd_packet` checks for a stop that is already open, though. If someone attaches a packet with `xv record packet` after `xv step guardian` has already applied a verdict, a second open stop is appended. The guardian brief tells the watch to attach the packet that way (`skills/guardian/SKILL.md:54`). This is plausible and untested.
- **C. The prototype path still applies its own verdict.** `scripts/prototypes.py:194-200` builds and appends its own stop and sets `next = "prototype"` without going through `record.apply_verdict`. Scenario point 2 lists only `xv step`, `xv run`, `xv record packet` and the session path, so this is not a miss. It does mean "one small function applies what orders returns" is not true across the repo.

## 2. Pitch

pitch_contradiction: no. The pitch says "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline" (`.xv/pitch.md:7`) and "It will never be a teapot" (`.xv/pitch.md:25`). This change moves stop rules inside the watch. It changes no user, no audience and no promise.

## 3. Moved tests

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_record.py` (`AcceptWallFlagTest`, line 1268) | `assertEqual(data["decisions"][0]["who"], "pat")` | `assertEqual(data["decisions"][0]["who"], ["pat"])` | "scenario point 9: new decisions write who as a list" | Yes: point 9, "New decisions write `who` as a list". Same assertion count (253 before and after, `xv wall diff`). It asserts no less. |

The record lists this move twice (`moved_tests`, at 17:26:59 and 17:35:27, same file and assertion). That is the duplicate point 8 removes. The second entry came in with the maker's report, written by code without `same_move`. The new code does not rewrite existing entries, but `accept_moves` will count it once (`scripts/orders.py:232`, a set of `(file, assertion)`).

Slice-only tests removed: none. Kept: none (`slice_only: []`).

## 4. The picture

- `.xv/picture.md:23`, "`xv step` and `xv record packet` apply it: they set `next` and record an answered stop with seat `watch`. The same miss on a later pass stops for the originator." Proposed: "`orders.verdict` also returns `next`. One function, `record.apply_verdict`, writes the stop or the send-backs and `next` on `xv step`, `xv run` and `xv record packet`. `xv record packet` now records stops too. A watch send-back keeps `report_n` and `packet`. A miss is a repeat when an earlier pass sent back the same key. `record.guardian_facts` turns the packet into the record's fields on every path." Also add that `xv prototype` still applies its own stop (finding C).
- `.xv/picture.md:23`, "After the scenario step, `slice_only_marks` lists slice-only marks ...; they accept the marks or run `xv record unmark`." Add: "An answer marks every listed mark `accepted`. An accepted mark is kept when the scenario runs again and is not asked about again."
- `.xv/picture.md:23`, the shape stops. Add: "`shape_wider_than_forecast` does not fire when `shape_change` is `accepted` or when a stop of that order has been answered. `accept_moves` counts moves by file and assertion. One move is recorded once."
- `.xv/picture.md:26`, "a prototype stop other than `prototypes_ready`, and a `budget_spent` stop raised before its step ran". Proposed: "a prototype stop other than `prototypes_ready` and `prototype_budget_spent`, and the `budget_spent` stop `xv step` marks `pre_step`, answered with `--next` that step". Also append to "An answer to `ready_to_merge` also writes a decision": "; a decision's `who` is a list (old records may hold a string)."
- `.xv/picture.md:23`, "`xvlib` is the shared base". Add the shared test-name matcher `names_test`, and that `packet` holds the allowed field values (`ALLOWED`, `YES_NO`).

## 5. The wall

Not marked slice-only, and I recommend marking them. Each one reads source text to guard a one-time refactor rather than behaviour (`tests/test_orders.py`, `OneHomeTest`):

- `test_run_and_record_no_longer_work_out_a_repeat`: asserts `miss_repeat` and `missed_repeat` are absent from `run.py` and `record.py`. The behaviour is already guarded by `test_a_repeat_flag_left_in_the_checks_is_not_read_as_a_repeat_of_a_scenario_miss` and `..._of_a_missed_point`.
- `test_the_allowed_values_of_the_packet_fields_are_defined_once`: counts `("yes", "no"` in three files. `PacketFieldDocsTest.test_the_code_allows_accepted_for_shape_change_only` guards the values themselves.
- `test_the_test_name_matcher_is_shared`: forbids any `(?!\w)` in `record.py`, for any later use.
- `test_the_wall_flags_are_not_handled_inside_cmd_answer`: inspects the source of `cmd_answer`. `--accept-wall` behaviour is guarded by `AcceptWallFlagTest`.

No test on the wall before the slice is made dead. `xv wall diff` shows one changed file, with no deletions and no drop in assertions.

## Other findings

- **D. The CHANGELOG records a decision that has not been made.** `CHANGELOG.md:7` (added): "... Decided by Sean, solo." The record's `decisions` is `[]`. Changing a standing order needs two people and a line in `CHANGELOG.md` (`.xv/picture.md:63`, decision 1), and the repo runs solo (`.xv/picture.md:55`). The line is under "Unreleased", which reads as a draft (`CHANGELOG.md:3`, "A version line without two names is a draft"). But an agent wrote a person's decision before the person answered (`.xv/picture.md:26`, "A person's name reaches the record only through an answer at a stop (#93)").
- **E. "Which send-backs count" has two branches.** `scripts/orders.py:41-46`: `earlier()` uses `report_n` when the stop has it, and otherwise the old timestamp rule. This slice's own `red_misses_point` send-back has no `report_n`, so it falls back to the timestamp rule. Old records are in "may ignore", so this is not a miss of point 1, but there are two rules until old records age out. The `packet` comparison only tells passes apart when the packet path changes. `xv step` always uses `.xv/slices/<id>.packet.md` (`scripts/run.py:484`).
- **F. Old pre-step `budget_spent` stops lose their exemption.** `scripts/record.py:355` now reads `stop.get("pre_step")` instead of a missing `budget_seen`. An open pre-step stop saved by the old code, answered after merge with `--next` its step, will now need `--settled`. Old records are in "may ignore".

## Door

**Door:** two-way. A revert undoes it. New records gain `who` as a list, `report_n`, `packet`, `pre_step` and `accepted` keys, and old code has no reader that breaks on them (`git grep '"who"' scripts/` finds only writers). **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-11-04-orders-home.md`
- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..6b88774` (working tree clean apart from the boundary file; the cleaner's `run.py` edit is in `6b88774`, despite its report saying it was not committed)
- Wall: `xv wall diff 2026-11-04-orders-home`
- Boundary: `xv boundary --base c7b8bbff58fc46160ba83d08d0e899d7beffaaf2` (`.xv/slices/2026-11-04-orders-home.boundary.md`)

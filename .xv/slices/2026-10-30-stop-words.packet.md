---
shape_change: no
pitch_contradiction: no
shape_breadth: none
picture_change: yes
moved_tests: 1
door: two-way
blast_radius: stops
---

# Packet: 2026-10-30-stop-words

## Needs a decision

1. **`shape_change: accepted` is taken on the guardian's word, and nothing checks it against a decision record.** The scenario says it applies only to a shape "already accepted in a decision record on this slice" (slice record, Amended 2026-10-29). In the diff, every reader accepts the value without looking for that record: `scripts/packet.py:41` `allowed = ("yes", "no", "accepted") if field == "shape_change" ...`, `scripts/record.py:445`, `scripts/run.py:502` `data[field] = v if v in ("yes", "no") or (field == "shape_change" and v == "accepted") else "yes"`, and `scripts/orders.py:175` fires only on `== "yes"`. Lint does not check that the packet names a decision record, or that one exists. This slice has `decisions: []`, yet a packet for it saying `accepted` would lint clean and reach `ready_to_merge`. That conflicts with `.xv/picture.md:72`: "Read-only agents are checked, not trusted." One packet line from a read-only agent now removes the two-person stop.
2. **In CI the value gets past the two-person stop where no decision record can exist.** `xv guard` without a slice record builds `data = {"id": "pull-request", ...}` with no decisions (`scripts/run.py:744`), then keeps `accepted` (`scripts/run.py:750` `ok = ("yes", "no", "accepted") if field == "shape_change" ...`). A PR packet that says `accepted` exits 0, not 10. `ci/github/xv-guardian.yml:8` still promises "A packet that says shape_change or pitch_contradiction only fails a check, so the merge waits for two people."
3. **The guardian's brief now contradicts itself.** `skills/guardian/SKILL.md:37` says "each `yes` or `no`, nothing else" and then, in the next sentence, "`shape_change` may be `accepted`". Its may-not list is unchanged: `skills/guardian/SKILL.md:49` "Set a fixed field to anything but `yes` or `no`". A guardian that follows its may-not list can never write `accepted`, and one that writes it breaks its may-not list. The red's brief tests (`tests/test_briefs_picture.py`) do not cover the guardian brief.

## The scenario

The stops, the briefs and the picture now say what the method says (#85, #86, #88/#68, #90):
1. A shape change already accepted on the slice does not stop again: `shape_change: accepted`.
2. A stall names the stall and four choices, not "the shape conversation opens".
3. `accept_moves` says the guardian proposes a change to the picture.
4. The maker and the scenario agent may read the picture but not edit it.
5. The watch may edit the picture when a person directs it.

May ignore: rewording the site, and stops for checks that cannot run (D7).

## Recording

None. This is a feature slice and starts from words. To replay: `cd tests && python3 -m unittest test_packet test_orders test_briefs_picture`. I ran it: 39 tests, OK.

## Boundary picture

From `xv boundary` (`.xv/slices/2026-10-30-stop-words.boundary.md`). Modules touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`. Nothing added or removed: no modules, edges, outbound calls, tables or surface paths. Shape hints: none.

## What the suite asserts after the change

- Packet lint accepts `shape_change: accepted` and refuses `pitch_contradiction: accepted` (`tests/test_packet.py`).
- `shape_or_pitch` does not fire on `accepted` and still fires on `yes`. With `accepted` plus `pitch_contradiction: yes`, it still stops for two people, and the question names only the pitch (`tests/test_orders.py:158-176`).
- Every stall question (maker-reported stop, same tests failing twice, a diff that more than doubled, a diff past the team limit) names continue, reshape the slice, raise the budget and second person, and drops "The shape conversation opens" (`tests/test_orders.py:178-212`).
- `accept_moves` says "The guardian proposes a change to the picture" (`tests/test_orders.py:214`).
- The maker brief lets it read the picture but not edit it, and has it pull the binding decisions before it writes code. The scenario brief reads the picture. The watch brief may edit the picture when a person directs it, in its own commit naming that person (`tests/test_briefs_picture.py`).
- Untested: that `accepted` needs a decision record (finding 1); the guardian brief (finding 3); `xv guard` handling `accepted` (finding 2).

## Moved tests

| Test | Before | After | Reason | Forced? |
|---|---|---|---|---|
| `tests/test_orders.py:56` `test_a_stall_opens_the_shape_conversation` | `assertIn("shape conversation", question)` | `assertIn("reshape the slice", question)` | Scenario point 2 removes "The shape conversation opens" | Yes. Scenario point 2 says the question "no longer says 'The shape conversation opens'". It asserts no less: one substring before and after, and `xv wall diff` gives 47 → 47 assertions with `fewer_assertions: []`. |

- The test's name now says the opposite of what it asserts: `tests/test_orders.py:56` `def test_a_stall_opens_the_shape_conversation(self):` checks that the stall question names the four choices.
- The record lists this move twice: once by Sean Kennedy (01:53:38) and once by the maker (01:55:19), with the same assertion and reason. `accept_moves` counts entries (`scripts/orders.py:184` `moved = [m for m in data.get("moved_tests") ...]`), so it would say "2 old test(s) moved" for one test.
- Slice-only: none (`.xv/slices/2026-10-30-stop-words.md`, `slice_only: []`).
- `xv wall diff` shows only `tests/test_orders.py` changed since the baseline. Unrecorded changes: none.

## The four checks

### 1. Shape: no (breadth none; forecast narrow)

The boundary picture has no new module, edge, outbound call, table or surface path, and no shape hints. The changed surfaces are inside the ones `.xv/picture.md:27` already names: the `xv` CLI, `skills/*/SKILL.md` and the CI examples. The stop rules stay in `scripts/orders.py`, as `.xv/picture.md:70` requires.

The packet front matter's set of values grows from yes/no to yes/no/accepted. That is a contract that CI (`ci/github/xv-guardian.yml`) and the evals read, but it is a change inside an existing surface, not a new one. The evals grader still compares to `yes` and `no` only (`evals/grade.py:285`, `evals/grade.py:294`), so an `accepted` packet scores as not flagged and not clean.

The cleaner's proposal (one shared definition of the allowed values, now written out at `scripts/packet.py:41`, `scripts/record.py:445`, `scripts/run.py:502` and `scripts/run.py:750`) would add an import edge. It is not in this diff.

### 2. Pitch: no

I checked against `.xv/pitch.md:7`, "to vibe with discipline", and `.xv/pitch.md:25`. The pitch says nothing on who stops for a shape change. Finding 1 weakens the discipline that `.xv/pitch.md:7` names, but the pitch does not promise that check in words, so I record no contradiction here; finding 1 cites the picture instead.

### 3. Moved tests

One test, forced by the scenario, asserting no less, and recorded twice. See the table above.

### 4. The picture: these edits are proposed, not made

- `.xv/picture.md:33` (Names, "shape change"): add "A packet's `shape_change` is `yes`, `no` or `accepted`. `accepted` means a shape a decision record on this slice already accepted, and it does not stop (#85)." The picture leaves the value out today.
- `.xv/picture.md:23` (orders holds the stop rules): add "The stall stops (`repeated_failure`, `diff_growing`) put four choices to the originator: continue, reshape the slice, raise the budget, or bring in a second person (#86)."
- `.xv/picture.md:58-75` (Decisions that bind): nothing says who may edit the picture. After `skills/watch/SKILL.md:86` "edit the picture unless a person directs it. A picture edit a person directs is its own commit, the message names the person who directed it, and the slice log records it", add a line that the maker and scenario agent read the picture and do not edit it, and that the watch edits it only when a person directs it (#88, #68, #90).
- `.xv/picture.md:72` (decision 12): if `accepted` stays trusted, write the exception into the decision. Otherwise, the check that finding 1 asks for makes this line true again.

Other docs the diff leaves stale (not the picture): `docs/slice-record.md:27` says "`yes` or `no`", and `README.md:254` says the packet "says `yes` or `no` to a shape change".

## Security

Covered by findings 1 and 2. A read-only agent, steered by the diff it reviews or by its own mistake, can now clear the two-person stop by writing one front-matter value. Nothing checks that value against a record a person made. Before this change, the only values that left out two people were `no` and `no`, and those are what a guardian reports when it finds nothing.

## The door

Two-way door: no data is migrated, and reverting the commits restores the earlier stops and briefs. The briefs do reach adopters through `xv install`, but nothing is sent to users. Blast radius: **stops**.

## Raw data

- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..HEAD`
- Boundary: `.xv/slices/2026-10-30-stop-words.boundary.md`
- Wall: `xv wall diff 2026-10-30-stop-words`; baseline `1e15135`, `.xv/slices/2026-10-30-stop-words.wall.json`
- Red and suite runs: the slice record `checks.maker` and `checks.cleaner` (405 tests, OK)
- Packet template `skills/guardian/packet.md` was not readable from this worktree, so I took this packet's shape from the brief's own list.

## From the cleaner

- Shape proposal, for people: One shared definition of the allowed values for shape_change (yes, no, accepted) and pitch_contradiction (yes, no), for scripts/packet.py:41, scripts/record.py:445, scripts/run.py:502 and scripts/run.py:750, which now each write the tuple out. It needs a new shared constant that record.py and run.py import from packet.py or xvlib, so it is not a cleanup.

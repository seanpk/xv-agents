---
shape_change: no
pitch_contradiction: no
scenario_miss: no
door: two-way
---

# Packet: A prototype variant is never dropped when the three start at once: #61

## Needs a decision

Nothing stops this for two people. For the person who set the work going:

- **A picture edit** (check 4): the shape section does not yet say that variant setup is serialised or what happens when git refuses one.
- **Two things the slice leaves open** (check 1 notes, not misses): only git *setup* failures are caught, so any other exception in `run_one` still drops a variant silently; and the stop after a refusal is `prototypes_ready` for two people, which does not name the variant that did not finish.

## The scenario in words

On #55, `xv prototype start` ran three variants at once. Variant b never called its agent, and no error reached the person. Two things should now hold:

1. One variant's git setup (worktree remove, branch delete, worktree add) never overlaps another variant's setup. The agents still run at the same time.
2. If git refuses one variant's setup, that variant is recorded as not finished with its error, the side-by-side file shows the error, the other two still run, and a second `xv prototype start` runs it again.

May ignore: #58 (building the variants in turns), prototypes applying their own stop (#117), old prototype records.

## Recording / replay

There is no recording; the scenario starts from words. To replay: `cd tests && python3 -m unittest test_prototypes.PrototypesGitSetupTest`. I ran it during this review: 4 tests passed, `OK`, in 19.6s. A fake `git` (`tests/test_prototypes.py:62-84`) logs the start and end of each worktree/branch command and sleeps 0.3s inside it. With `FAKE_GIT_REFUSE=b` it fails b's `worktree add` with `fatal: Unable to create '.git/index.lock': File exists.`

## Boundary picture

From `.xv/slices/2026-11-04-proto-start.boundary.md`: touched `scripts/prototypes` only. Added or removed modules: none. Added or removed edges: none. Tables: none. Surface paths: none. Outbound calls: none. Shape hints: none.

## What the suite asserts after the change

- Each variant's git-setup span lies wholly before or after every other variant's span (`tests/test_prototypes.py:141`).
- All three agents start before any agent ends (`:154`).
- If b's setup is refused: only a and c call their agents; the record lists a, b and c; b has no recording; b's section of `p1.prototypes.md` contains `index.lock`; and so does the slice record (`:161`).
- After a refused b, an answered stop and a second start, only b runs, and all three then have recordings (`:177`).
- The existing side-by-side and pick test (`:29`) is unchanged. The new class sets it to `None`, so it does not run twice.

The whole suite was green after the maker and after the cleaner (668 OK, per the record's `checks.maker` and `checks.cleaner`).

## Moved tests

None. `xv wall diff 2026-11-04-proto-start` reports `changed: []`, `deleted: []`, `added: []`, `fewer_assertions: []`. The baseline is the red commit `1d1f8c2`. Against base `c7b8bbf`, `tests/test_prototypes.py` only gains lines (`git diff` shows 129 insertions and no deletions). The record has `moved_tests: []`. Slice-only: none; the record's `slice_only` is `[]`.

## The five checks

### 1. Shape: no

- The boundary picture shows no added module, edge, table, surface or outbound call, and no shape hints. `.xv/slices/2026-11-04-proto-start.boundary.md`, "Edges: added: none", "Shape hints: none".
- `scripts/prototypes.py:42` adds `SETUP_LOCK = threading.Lock()`. This is a process-local lock inside a module that already uses `threading` (`:23`), so it is not a new dependency or coupling.
- Breadth is `narrow`, which matches the forecast's `"shape": "narrow"`: one script, 19 changed lines.
- **Note, not a shape change: the catch covers setup only.** `scripts/prototypes.py:49-57` catches `XVError` around the three setup commands. Everything after that in the thread is still unguarded: `git rev-parse` (`:66`), `promptlib.brief`, `agentcli.run` (`:68`) and any non-`XVError` exception. If any of them raises, the thread dies, `out[name]` stays unset, and the variant is dropped with no error. That is the #61 symptom by another route. The scenario's point 2 only names "when git refuses one variant's setup", so this is not a miss. The person may want a follow-up.
- **Note: the lock does not cover the agents' own git commands.** `SETUP_LOCK` serialises setup against setup only. Variant a's agent can already be running git in its worktree while b's setup runs (`:50` comment: "the agents still run together"). The #61 record says the lock cause "is not confirmed". If the collision comes from there, it will now show up as a recorded `Not finished` instead of a silent drop (`:172-174`).

### 2. Pitch: no contradiction

- `.xv/pitch.md`: "xv-agents makes it easy for a team or an individual to adopt Xtreme Vibing in a repo: to vibe with discipline." Making a refused variant visible instead of silent serves this.
- The change does nothing the pitch's "Who it is not for, and what it will never do" line rules out.

### 3. Moved tests

None; see above. No old test asserts less.

### 4. The picture: change proposed

`.xv/picture.md`, "The shape", the bullet that begins "No database. State is files". After "A second `xv prototype start` reruns every variant that has not finished, from HEAD, on what is left of its budget, and keeps the finished ones.", add:

> Each variant's git setup (worktree remove, branch delete, worktree add) runs one at a time under a lock in `prototypes`; the agents still run together. A variant whose setup git refuses is recorded with no branch and no recording, so it has not finished. Its error goes into its section of the side-by-side file and the slice log, and no spend is recorded for it. Evidence: `scripts/prototypes.py:49-57`, `:172-176`.

The edit is also needed because the picture's definition of "finished" ("has a recording and did not run out") is what makes the refused variant rerun. The slice depends on that definition without restating it.

### 5. The wall

No recommendations. All four new tests in `tests/test_prototypes.py:141-188` guard lasting behaviour: serialised setup, concurrent agents, a refused variant kept, and the rerun. None of them guards a one-time change. None restates `:29`, which never makes git refuse anything.

## Other findings for the person

- **The stop after a refusal does not name it.** With b refused, `ran_out` is empty and `prototypes_ready` is 2. So `orders` fires `prototypes_ready` for two people: "2 prototype(s) are ready to pick from, or none." (`scripts/orders.py:281-284`). Nothing in that question says b did not finish or that a second start would rerun it. The person learns of it only by opening the side-by-side file the stop points to. The test reflects this: `tests/test_prototypes.py:182` answers that two-people pick stop with `--by pat,sam --answer "run b again"` before the second start. On a solo repo the originator answers it. Scenario point 2 asks only that the side-by-side file show the error, which it does, so this is not a miss.
- **Wrong reason if someone picks b.** A refused variant is recorded with `"branch": None` (`scripts/prototypes.py:56`). Picking it hits the existing guard, which refuses with "prototype b stopped at its budget and has nothing to pick" (`scripts/prototypes.py:240`). The refusal is right; the reason it gives is wrong.
- **The error is not in the record's `prototypes` entry.** It is only in the log line (`scripts/prototypes.py:174`, `record.log_line(... "variant {n} not finished: ...")`) and the side-by-side file; the `prototypes` entry (`:179-185`) has no `error` key. This fits the scenario's "may ignore … old prototype records, which keep their shape". A tool reading the record cannot tell a refused variant from one whose agent wrote no recording.

## Scenario misses

None. Point 1 is covered by `tests/test_prototypes.py:141` (no overlap) and `tests/test_prototypes.py:154` (agents together). Point 2 is covered by `tests/test_prototypes.py:161` (a and c run, b recorded without a recording, error in the side-by-side file and the record) and `tests/test_prototypes.py:177` (a second start reruns b only). No decision that binds is broken: `.xv/picture.md:65` (standard library only) holds, since `scripts/prototypes.py:42` uses `threading`; `.xv/picture.md:72` (standing orders live in `scripts/orders.py`) holds, since the diff does not touch `scripts/orders.py`.

## The door

Two-way door: a revert removes the lock and the catch, and no data, contract or message changes. Blast radius: small (only `xv prototype start`).

## Raw data

- Diff: `git diff c7b8bbff58fc46160ba83d08d0e899d7beffaaf2..HEAD -- scripts tests`
- Boundary: `.xv/slices/2026-11-04-proto-start.boundary.md`
- Wall: `xv wall diff 2026-11-04-proto-start`; baseline `.xv/slices/2026-11-04-proto-start.wall.json`
- Run logs: `.git/xv/runs/2026-11-04-proto-start/` (04-maker.out, 05-cleaner.out)

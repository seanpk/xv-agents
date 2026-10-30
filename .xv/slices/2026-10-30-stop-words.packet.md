---
slice: 2026-10-30-stop-words
shape_change: no
pitch_contradiction: no
picture_change: yes
shape_breadth: none
moved_tests: 2
door: two-way
blast_radius: stops
---

# Packet: The stops, the briefs and the picture say what the method says

Nothing stops this for two people. The merge is Sean's. Three things need Sean's decision: the picture edit (section 4), the docs that still say `yes` or `no` or "the picture changed" (section 1, items 3 and 4), and one gap in point 1 (section 1, item 2). All three amendments from the last merge stop are done. The guardian brief allows `accepted` and names `accepted_by`. The stall test is renamed. `xv record packet` now runs the `accepted_by` check.

## The scenario

There are five points (#85, #86, #88 with #68, #90):

1. A packet may say `shape_change: accepted` when `accepted_by` names a `shape_or_pitch` decision listed on this slice. Without one, it is read as `yes`. `xv guard` always reads it as `yes`.
2. A stall names the stall and four choices: continue, reshape the slice, raise the budget, or bring in a second person. It no longer says "The shape conversation opens".
3. `accept_moves` says "the guardian proposes a change to the picture".
4. The maker and the scenario agent may read the picture but may not edit it.
5. The watch may edit the picture when a person directs it, in its own commit.

May ignore: rewording the site, and any stop for a check that cannot run (D7).

## The recording

None; this is a feature. To replay the red and the green: `cd tests && python3 -m unittest test_run.AcceptedShapeChangeTest test_orders`. Whole suite: `cd tests && python3 -m unittest -q`. On HEAD `503cd1f` the whole suite ran 439 tests, OK.

## The boundary picture

From `.xv/slices/2026-10-30-stop-words.boundary.md`, as given. Modules touched: `scripts/orders`, `scripts/packet`, `scripts/record`, `scripts/run`. No modules, edges, outbound calls, tables or surface paths were added or removed. Shape hints: none. The new call, `run` → `record.accepted_by_listed_decision`, uses the existing `scripts/run → scripts/record` edge.

## What the suite asserts after

- **Packet lint:** `shape_change: accepted` lints clean. `pitch_contradiction: accepted` is refused.
- **Stop rules:** `shape_or_pitch` does not fire on `accepted`, and fires on `yes`. An `accepted` shape does not hide `pitch_contradiction: yes`.
- **`xv run` and `xv record packet`:** each keeps `accepted` only with a listed `shape_or_pitch` `accepted_by`. It reads `accepted` as `yes` when `accepted_by` is missing, names an unlisted file, names a missing file, or names a decision of another order.
- **`xv guard`:** with no slice record, it reads `accepted` as `yes`.
- **Stall wording:** all three stall questions (maker-reported, same tests failing twice, growing diff or diff past the limit) name the four choices and not "The shape conversation opens".
- **`accept_moves` wording:** it says "The guardian proposes a change to the picture".
- **Brief text:** the maker and scenario briefs may read the picture and pull the binding decisions. The watch brief may edit the picture when a person directs it. The guardian brief allows `accepted` and names `accepted_by`.

## 1. Shape

shape_change: no. shape_breadth: none (the forecast was narrow).

- **No new structure.** The boundary picture adds no module, edge, table or surface. The briefs are an existing surface (`.xv/picture.md:27`: "Surfaces: the `xv` CLI, `skills/*/SKILL.md`…"). The slice rewords them inside that surface.
  - `accepted_by` is a new key in the packet's front matter, read by `scripts/record.py:438-447`. It adds no module or edge.
  - The new behaviour lives in the modules the picture already gives the job to: "`orders` holds the stop rules" and "`record` owns the slice record" (`.xv/picture.md:23`).
- **Point 1 is not complete: an accepted shape can still stop for two people.** `scripts/orders.py:179-183` fires `shape_wider_than_forecast` for two people whenever the packet's `shape_breadth` is wider than the forecast, whatever `shape_change` says:
  ```
  fc = (data.get("forecast") or {}).get("shape")
  actual = (data.get("checks") or {}).get("guardian", {}).get("shape_breadth")
  if fc in BREADTH and actual in BREADTH and BREADTH[actual] > BREADTH[fc]:
  ```
  The scenario says a shape change matching an accepted decision "does not stop the slice again" (slice record, Scenario point 1). Take a slice forecast `none`, whose accepted shape is `narrow`. Its next packet says `accepted` with `shape_breadth: narrow`, and it stops for two people again. No test covers an accepted shape combined with a breadth. Whether the guardian should report breadth as `none` for an accepted shape is not written down anywhere. That is a question for Sean.
- **`accept_moves` reads wrong for an accepted shape.** When `shape_change` is `accepted`, the question still says "the shape did not" (`scripts/orders.py:193`: `"…; the shape did not. Accept them from the packet, "`). That is untrue for an accepted shape change.
- **Docs still say the fixed fields are `yes` or `no`** (`docs/slice-record.md:27`, `docs/decisions.md:55`, `README.md:254`, `skills/guardian/packet.md:34`):
  - `docs/slice-record.md:27`: "`shape_change`, `pitch_contradiction` | the guardian's packet | `yes` or `no`". The record may now hold `accepted`.
  - `docs/decisions.md:55`: "A packet whose fixed fields are not `yes` or `no` sets both to `yes`".
  - `README.md:254`: "says `yes` or `no` to a shape change and a pitch contradiction".
  - `skills/guardian/packet.md:34`: "shape_change: <yes|no>". The template's front matter (`skills/guardian/packet.md:3-9`) has no `accepted_by` line.

  Binding decision 13 says a brief "points to files rather than restating them" (`.xv/picture.md:73`). The guardian brief points to this template, and the template contradicts the brief.
- **"The picture changed" survives outside the question.** Point 3 changed the question only (`scripts/orders.py:191`). The rows naming the same stop still say "the picture changed" in four places: `skills/watch/SKILL.md:67`, `README.md:277`, `README.md:108` and `README.md:149`, the last two in the diagrams.
- **The guardian brief's fields line is malformed.** `skills/guardian/SKILL.md:37`: "the two fixed fields the watch reads, `shape_change` and `pitch_contradiction`, `pitch_contradiction` is `yes` or `no`; …". The edit left a comma splice where a colon or full stop belongs.
- **Not a shape change, already raised by the cleaner three times.** The allowed-values tuple is written out at `scripts/packet.py:41`, `scripts/record.py:457` and `scripts/run.py:502-505`, and `scripts/run.py:753` keeps its own `("yes", "no")`. The three versions can drift apart.

## 2. Pitch

pitch_contradiction: no. I read `.xv/pitch.md:7` ("makes it easy … to vibe with discipline"), `.xv/pitch.md:17`, `.xv/pitch.md:21` and `.xv/pitch.md:25` ("not for people or projects that will not trust agents to write production code"). Nothing in the diff serves someone the pitch excludes or breaks a promise it makes.

The binding decisions the change touches all hold:
- **Decision 1** (`.xv/picture.md:61`): a brief, may-not list or standing-order change gets a `CHANGELOG.md` line. It does (`CHANGELOG.md:7`), and the repo is solo (`.xv/picture.md:53`).
- **Decision 12** (`.xv/picture.md:72`): "Read-only agents are checked, not trusted." `accepted` from the guardian is checked against the record and the decision file before it counts (`scripts/record.py:438-447`, `scripts/run.py:502`), and `xv guard` never trusts it (`scripts/run.py:753`).

## 3. Moved tests

`xv wall diff` against the wall baseline `04c718a` shows one change: `tests/test_run.py`, 113 → 111 assertions. That is the slice-only removal below. From the base `5ec1d86`, the old tests that changed are the two rows below. All other test changes are additions.

| File | Before | After | Why (the maker's record) | Forced by the scenario? |
| --- | --- | --- | --- | --- |
| `tests/test_orders.py:56-59` | `test_a_stall_opens_the_shape_conversation`: `assertIn("shape conversation", question)` | `test_a_stall_question_offers_to_reshape_the_slice`: `assertIn("reshape the slice", question)` | Point 2 removes "The shape conversation opens"; the rename was Sean's amendment at the 03:17 stop | Yes. It still has one assertion. Three new tests assert all four choices and the absence of the old words (`tests/test_orders.py:178-213`). It asserts no less. |
| `tests/fake_agent.py:63-68` | The fake guardian always wrote `shape_change: no` | It takes `FAKE_SHAPE_CHANGE` and `FAKE_PACKET_EXTRA`, and writes `pr-packet.md` for `xv guard`. With both unset, it writes the same text to the same path as before | The `accepted_by` tests need these packets; Sean accepted it at the `unrecorded_move` stop | Yes, for the `accepted_by` and `xv guard` tests. It is a fixture with no assertions. |

The record lists five move entries for these two changes plus the slice-only removal (slice record line 15). The stall assertion is recorded twice, once by Sean at 01:53 and once by the maker at 01:55. The cleaner's entry has no `slice_only` flag, so `scripts/orders.py:184` (`if not m.get("slice_only")`) will count it. The `accept_moves` question will then say "5 old test(s)" for two real moves.

Slice-only tests removed: `tests/test_run.py::test_the_stall_test_is_named_for_what_it_checks` (commit `503cd1f`). Kept: none.

## 4. The picture

picture_change: yes. These are proposed edits for Sean to accept. I do not write them.

- **`.xv/picture.md:23`.** After "`orders` holds the stop rules", add: "`shape_or_pitch` fires on `yes`, not on `accepted`. `record.accepted_by_listed_decision` decides whether a packet's `accepted` holds: `accepted_by` must name a decision in the slice's `decisions` list whose front matter has `order: shape_or_pitch`. `xv run` and `xv record packet` both use it, and otherwise read `accepted` as `yes`. `xv guard` always reads it as `yes`."
- **`.xv/picture.md:33` (Names).** "shape change" in a packet now has three values. Add: "`shape_change` is `yes`, `no` or `accepted`. `pitch_contradiction` is `yes` or `no` (#85)."
- **New Names line.** "The shape conversation opens on a shape change, and before and after a burst. A stall (`repeated_failure`, `diff_growing`) is not a shape conversation. It puts four choices to the person who set the work going: continue, reshape the slice, raise the budget, or bring in a second person (#86)."
- **Who may touch the picture.** The picture does not say this today, and the slice settles it (`skills/maker/SKILL.md:17`, `skills/scenario/SKILL.md:17`, `skills/watch/SKILL.md:86`). Add under Names, or as a binding decision if Sean wants it to bind: "The maker and the scenario agent read the picture and pull its binding decisions. They do not edit it. The watch edits it only when a person directs it, in its own commit naming that person. Accepting a picture change is a person's (#88, #68, #90)."

## Door

**Door:** two-way. Reverting the commits restores the old wording and the old `yes`/`no` reading. No data is migrated. A packet already recorded with `accepted` would be read as malformed, which means `yes`, and that fails safe. **Blast radius:** stops.

## Raw data

- Slice record: `.xv/slices/2026-10-30-stop-words.md`
- Diff: `git diff 5ec1d8640ff0da37a2634737f241cfd1a14821e2..503cd1f`
- Wall: `xv wall diff 2026-10-30-stop-words`
- Boundary: `.xv/slices/2026-10-30-stop-words.boundary.md` (`xv boundary --base 5ec1d8640ff0`)

## From the cleaner

- Shape proposal, for people: One shared definition of the allowed values for shape_change (yes, no, accepted) and pitch_contradiction (yes, no), for scripts/packet.py:41, scripts/record.py:445, scripts/run.py:502 and scripts/run.py:750, which now each write the tuple out. It needs a new shared constant that record.py and run.py import from packet.py or xvlib, so it is not a cleanup.
- Shape proposal, for people: The `shape_change` allowed-values check is duplicated in scripts/packet.py:41 and scripts/record.py:445; one shared helper in xvlib would remove the copy, but it adds a new function, so it is left for a person.
- Shape proposal, for people: One shared definition of the allowed front-matter values for shape_change and pitch_contradiction, used by scripts/packet.py lint, scripts/record.py cmd_packet and scripts/run.py post_step. All three now repeat the yes/no/accepted logic, and packet.py does not import record.py, so a shared home is a new placement decision.

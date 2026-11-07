# Recording: a directed edit re-fires the stop it answered, on slice 2026-11-07-picture-lines (#151)

Taken from `.xv/slices/2026-11-07-picture-lines.md` on main (1f325dd): the three `accept_moves` stops at the guardian, in order. Sean picked option 1 at the first. That option carried a directed `changelog` edit and sent the slice back to the maker. The edit was made and committed, then the standing orders ran again and the same `accept_moves` stop fired, so the slice did not go to the maker. Sean had to answer the same stop a second time ("yes") before the send-back took effect.

## 2026-11-07T16:29:30+00:00: `accept_moves`, seat `originator`

- answered by: Sean Kennedy
- answer: A1, budget $5.50, C off
- pick: 1, "Fix it all in the slice: accept the wall recommendations and both picture edits, fix the CHANGELOG line, send back to the maker for the double note; the cleaner then removes the slice-only tests"
- the option's directed edit: `CHANGELOG.md`, kind `changelog` (the line now names amendments 7 and 8)
- `--next`: maker
- what should have happened: the edit is committed, the suite runs, and the slice goes to the maker with no new stop.

## 2026-11-07T16:49:07+00:00: `accept_moves`, seat `originator` (the re-fire)

- question: "The guardian proposes a change to the picture; the shape did not. Accept them from the packet, talk it through with someone, or send it back. The merge is yours. …"
- answered by: Sean Kennedy
- answer: yes
- pick: 1, "Same answer as before: back to the maker"
- settled: "As settled at the answer before: the maker fixes the double note; the cleaner then removes the five slice-only tests; the guardian runs again."
- cause: "tool: the directed edit re-fired the stop its answer closed (#151)"

## 2026-11-07T17:12:57+00:00: `accept_moves`, seat `originator`

The guardian's normal stop after the maker and cleaner ran again. Not part of the defect; it shows the slice went on once the second answer was given.

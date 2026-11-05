# Rules

Project facts the agents cannot infer: an odd command, a slow check, a convention that breaks the defaults. Every entry carries the miss it came from. At the two standing moments of a burst, before it and as it ends, `xv check entries` lists them; an entry whose miss no longer happens without it is deleted.

Each entry is a heading and these lines:

```
### <the fact, one line>
- added: <date> by <name>
- from: <slice id>, <the moment in the record>
- miss: <what went wrong without it>
- seen: [<repo>@<date>]
```

## Entries

### A change to a brief, a may-not list, a standing order, or a check gets a line in `CHANGELOG.md` under Unreleased, naming the issue and who decided, and saying whether it moves a position on xtremevibing.com; if it does, the site changes first and the mechanism follows here
- added: 2026-10-26 by Sean Kennedy; widened 2026-10-27 by Sean Kennedy
- from: 2026-10-25-diff-count, -suite-red-quote, -answer-in-prompt, -init-tries-guesses, the guardian's packets; v0.3.0, three positions moved on the site
- miss: four of five makers changed a brief or an order and wrote no CHANGELOG line; binding decision 1 asks for one, and the maker does not read the picture. In v0.3 the mechanism changed before the site's positions did, and no rule said which goes first
- seen: [xv-agents@2026-10-26]

### A slice that changes what `xv record` accepts or refuses also changes README.md and the briefs that state the old rule; the picture's line is changed at merge
- added: 2026-10-29 by Sean Kennedy
- from: 2026-10-29-settled-forward, guardian logs 22:11:42 and 23:24:32 "README/watch brief/picture/CHANGELOG still state the old rule", "picture.md:26 still states the old --settled rule"; 2026-10-29-stop-decisions, guardian logs 19:30:42 and 19:53:37 "README examples now refused", "README:189 sends a merge to the maker"
- miss: in both slices the guardian found the old `--settled` rule still stated somewhere else, four times in all: README answer examples that `xv record` now refused, the watch brief, and `.xv/picture.md:26`. The maker does not read the picture, so the picture's line was found twice.
- seen: [seanpk/xv-agents@2026-10-29]

### an answer at a stop adds work the forecast said would not change -> read the gap at close as added work, not as a forecast miss
- added: 2026-11-02 by Sean Kennedy
- from: 2026-10-27-wall-red-files, the `forecast` note and the three `accept_moves` stops (21:43, 21:58, 23:05); 2026-10-30-test-marks, 2026-10-30-by-name and 2026-10-30-stop-words, the forecaster's close notes (retro 2026-10-30, candidate 4)
- miss: The forecast was 250,000 Sonnet tokens and $1.42, the mean of three slices that each took more than one pass. The slice used 317,628 tokens and $1.83, 27% over. The guardian stopped it three times, and each answer sent it back for a full pass. Two of those answers added work in `scripts/run.py` and `scripts/orders.py`, which the forecast said would not change. This is the first sighting.
- seen: [seanpk/xv-agents@2026-10-27, seanpk/xv-agents@2026-10-30]

### A test of one CHANGELOG line is slice-only; a test of a brief sentence that matches a code rule stays on the wall
- added: 2026-11-05 by Sean Kennedy
- from: 2026-11-04-refactor-kind, slice_only_marks at 05:30:23 (six brief tests, all unmarked) and 06:53:20 (CHANGELOG test, accepted); 2026-11-05-wave1-fixes, slice_only_marks at 04:45:00 (brief test unmarked, CHANGELOG test accepted); counts: slice-only removal of the CHANGELOG test fired 1 time on each of the three recorded rules, 0 overrides
- miss: `slice_only_marks` fired on 4 slices. In every answer in these records Sean made the same choice, and the cause lines say "decision". The scenario agent still marked brief tests slice-only each time, so each slice stopped and asked a question whose answer was already known.
- seen: [seanpk/xv-agents@2026-11-05]

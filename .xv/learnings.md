# Learnings

Judgement rules no check can hold, waiting for a second sighting. Agents do not read Open while working; it is evidence, not rules. When an entry has been seen twice, the watch puts its promotion in front of the person who set the work going: into `standards.md` or `rules.md`, with a line in Promoted. Do not promote from one sighting. An entry seen in two repos is a candidate for the shared skills (`xv promote`).

Open entries, newest first:

```
### <date>: <the pattern, named>
- added: <date> by <name>
- from: <slice id>, <the moment in the record>
- miss: <what went wrong>
- said: "<the words, verbatim>"
- rule: <condition> -> <behaviour>, with no project facts in it
- seen: [<repo>@<date>]
```

An entry with three or more sightings that still splits people is marked `(watch)` and waits for a third that settles it.

## Open

### 2026-10-27: A test that asserts less can be found by a check, not only by judgement
- added: 2026-10-27 by Sean Kennedy
- from: no slice; a read of unclebob/ub-mode and its companion tool unclebob/mutator
- miss: None yet. The cleaner finds a test that now asserts less by judgement only, and no check counts it. Mutation testing breaks the changed code on purpose and reports each break the tests do not catch. A trial in a cleaner step is the first sighting.
- said: "it seems like it might be something we could leverage or use as reference"
- rule: a slice changes code and its tests -> run mutation testing on the changed lines and report each surviving mutant as a test that asserts too little
- trial: 2026-10-27, on slice 2026-10-27-prototype-budgets, with unclebob/mutator. It measured nothing. With coverage on, it found 0 tests and ran no mutant. With `--no-coverage` it ran 25.5 minutes: 5 of 234 mutants killed, 229 survived. Most tests run `bin/xv`, which follows `os.path.realpath` back to the real checkout, so the mutated copy in mutator's worker folder was never tested. It also installed `coverage` into the Python on PATH.
- decided: 2026-10-27, Sean: "our conclusion is that the value of mutator is questionable. independent (not unclebob) praise for it is needed before we'll try it again". The next try, if any, is on a TypeScript slice in the Rails and TypeScript trial app.
- seen: []

### 2026-10-27: A forecast runs low when answers at a stop add work
- added: 2026-10-27 by Sean Kennedy
- from: 2026-10-27-wall-red-files, the `forecast` note and the three `accept_moves` stops (21:43, 21:58, 23:05)
- miss: The forecast was 250,000 Sonnet tokens and $1.42, the mean of three slices that each took more than one pass. The slice used 317,628 tokens and $1.83, 27% over. The guardian stopped it three times, and each answer sent it back for a full pass. Two of those answers added work in `scripts/run.py` and `scripts/orders.py`, which the forecast said would not change. This is the first sighting.
- rule: an answer at a stop adds work the forecast said would not change -> read the gap at close as added work, not as a forecast miss
- seen: [seanpk/xv-agents@2026-10-27]

### 2026-10-24: init checks its own guesses before the person relies on them
- from: init, the test command and the source roots in `.xv/config.yml`
- said: "ImportError: Start directory is not importable"
- rule: xv init writes a guessed setting the agents depend on -> it tries the setting once (runs the test command, counts the modules) and shows what failed or looks thin before the interview
- seen: [seanpk/xv-agents@2026-10-24]
- shared: seanpk/xv-agents#14

### 2026-10-24: in a tool repo, binding decisions are about changes to its code
- from: init, the interview, decisions that bind and the pitch's "never"
- said: "it seems to me that our focus should be on the code in this repo, not the xv skill itself"
- rule: the repo's product is a tool or a method -> draft binding decisions that constrain a change to this repo's code, not the method the tool carries out; and accept a pitch with no product "never"
- seen: [seanpk/xv-agents@2026-10-24]

## Promoted

One line per promotion: date, the entry, where it went. So nothing is promoted twice.

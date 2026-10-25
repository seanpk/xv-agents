# Learnings

Judgement rules no check can hold, waiting for a second sighting. Agents do not read Open while working; it is evidence, not rules. When an entry has been seen twice, the watch puts its promotion in front of the person who set the work going: into `standards.md` or `rules.md`, with a line in Promoted. Do not promote from one sighting. An entry seen in two repos is a candidate for the shared skills (`xv promote`).

Open entries, newest first:

```
### <date>: <the pattern, named>
- from: <slice id>, <the moment in the record>
- said: "<the words, verbatim>"
- rule: <condition> -> <behaviour>, with no project facts in it
- seen: [<repo>@<date>]
```

An entry with three or more sightings that still splits people is marked `(watch)` and waits for a third that settles it.

## Open

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

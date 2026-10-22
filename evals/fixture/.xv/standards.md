# Standards

The cleaner's rules, earned by misses. The cleaner applies them without asking and never edits this file. A rule enters when the person who set the work going accepts it from a packet.

## Rules

### Name a date for what it is: `expires_on`, `today`, `last`; never `d`, `dt`, or `x`
- added: 2026-10-08 by the fixture's household
- from: 2026-10-07-add-items, the guardian's packet
- miss: a one-letter date name hid an off-by-one in a comparison
- seen: [pantry@2026-10-07, pantry@2026-10-08]
- check: none: judgement

### No `print()` in `pantry/`; the API reports errors as JSON
- added: 2026-10-08 by the fixture's household
- from: 2026-10-08-use-items, the cleaner's report
- miss: debug output left in the store went to the household's terminal
- seen: [pantry@2026-10-08]
- check: none: judgement

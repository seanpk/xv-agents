# Estimation guide

One row per harness and model per closed slice. The forecaster appends the rows
when a slice closes; nobody edits a row in place. Anyone may revert a row by
deleting it. `xv record guide-verify` refuses an edited or reordered row.

A forecast uses only rows with the same harness and model.

| slice | closed | harness | model | forecast tokens | actual tokens | gap | forecast usd | actual usd | wall s | shape forecast | shape actual | why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-24-readme-drift | 2026-10-24 | claude | haiku |  | 30743 | no forecast |  | 0.00 | 6 | narrow | none | No history for claude/sonnet or claude/opus, so the null forecast had no gap to measure; the scenario stop cost a second scenario run (214k tokens, $0.16) and the opus guardian was 56% of the usd ($0.63 of $1.11). |
| 2026-10-24-readme-drift | 2026-10-24 | claude | opus |  | 420999 | no forecast | None | 0.63 | 137 | narrow | none | No history for claude/sonnet or claude/opus, so the null forecast had no gap to measure; the scenario stop cost a second scenario run (214k tokens, $0.16) and the opus guardian was 56% of the usd ($0.63 of $1.11). |
| 2026-10-24-readme-drift | 2026-10-24 | claude | sonnet |  | 720529 | no forecast | None | 0.48 | 168 | narrow | none | No history for claude/sonnet or claude/opus, so the null forecast had no gap to measure; the scenario stop cost a second scenario run (214k tokens, $0.16) and the opus guardian was 56% of the usd ($0.63 of $1.11). |

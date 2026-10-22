# Estimation guide

One row per harness and model per closed slice. The forecaster appends the rows
when a slice closes; nobody edits a row in place. Anyone may revert a row by
deleting it. `xv record guide-verify` refuses an edited or reordered row.

A forecast uses only rows with the same harness and model.

| slice | closed | harness | model | forecast tokens | actual tokens | gap | forecast usd | actual usd | wall s | shape forecast | shape actual | why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-10-07-add-items | 2026-10-07 | claude | sonnet | 300000 | 412000 | +37% | 1.2 | 1.61 | 610 | narrow | narrow | the maker installed pytest before finding the unittest command |
| 2026-10-08-use-items | 2026-10-08 | claude | sonnet | 300000 | 268000 | -11% | 1.2 | 1.05 | 420 | none | none | small change inside the store; one round |
| 2026-10-08-use-items | 2026-10-08 | claude | haiku | 40000 | 36000 | -10% | 0.05 | 0.04 | 60 | none | none | forecaster and close |
| 2026-10-14-expiring | 2026-10-14 | claude | sonnet | 350000 | 330000 | -6% | 1.4 | 1.3 | 540 | none | none | new query on the store and one route |
| 2026-10-14-expiring | 2026-10-14 | codex | gpt-5.5-codex | 200000 | 510000 | +155% | 2 | 4.4 | 900 | none | none | guardian run on another family; long diff read |

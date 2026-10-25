# Estimation guide

One row per harness and model per closed slice. The forecaster appends the rows
when a slice closes; nobody edits a row in place. Anyone may revert a row by
deleting it. `xv record guide-verify` refuses an edited or reordered row.

A forecast uses only rows with the same harness and model.

| slice | closed | harness | model | forecast tokens | actual tokens | gap | forecast usd | actual usd | wall s | shape forecast | shape actual | why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

# The slice record

One file per slice: `.xv/slices/<id>.md`. The fixed fields are front matter, so CI and the scripts parse them. The prose, the scenario and the log are the body. The file name is the slice id. The estimation guide, the standards file and the retro read slice records and nothing else.

Write it with `xv record`, never by hand in the middle of a step: the watch rewrites the front matter after each step.

## Front matter

Each value is a bare word or one line of JSON.

| Field | Written by | What it holds |
| --- | --- | --- |
| `id`, `title`, `kind` | `xv slice new` | `kind` is `feature`, `defect` or `prototype` |
| `status` | the watch | `open`, `working`, `stopped`, `ready`, `closed`, `abandoned` |
| `set_by` | `xv slice new` | the person who set the work going; they answer the stops |
| `created`, `branch`, `base` | `xv slice new` | `base` is the commit the slice started from; every diff is against it |
| `next` | the watch | the step the slice resumes at: `forecaster`, `scenario`, `maker`, `cleaner`, `guardian`, `close`, `prototype`, `none` |
| `forecast` | the forecaster | `{"keys": [{"harness", "model", "tokens", "turns", "usd", "basis"}], "wall_s", "shape", "breadth"}` |
| `budget` | a person | `{"tokens", "usd", "turns", "set_by"}`; `raised_from` when raised |
| `prototype_budgets` | a person | a prototype slice only: `{"a", "b", "c"}`, each in the shape of `budget` and free to differ |
| `red` | the scenario agent | `{"files", "command", "failure", "watch_first_green"}` |
| `wall_baseline` | `xv wall baseline` | `{"commit", "count", "digest", "file"}`; the hashes are in `.xv/slices/<id>.wall.json` |
| `moved_tests` | the maker, the cleaner | one item per move: `{"file", "assertion", "why", "by", "at"}` |
| `wall_recommendations` | the guardian | one item per recommendation: `{"file", "test", "recommend", "why", "accepted"}`; `accepted` turns true when the person answers `accept_moves` |
| `suite` | the watch | `green` or `red` after the last maker or cleaner step |
| `cleaner_commit` | the cleaner | the commit of the cleaner's fix |
| `packet` | the watch | the path of the guardian's packet |
| `shape_change`, `pitch_contradiction` | the guardian's packet | `yes` or `no`; the two-person stop reads them |
| `spend` | the watch | one item per step: `{"step", "harness", "model", "model_id", "tokens_in", "tokens_out", "cache_read", "cache_write", "tokens", "usd", "turns", "wall_s", "session", "log"}` |
| `stops` | the watch | one item per stop: `{"at", "step", "order", "seat", "question", "answered_by", "answer"}` |
| `decisions` | `xv record answer` | `{"date", "who", "decision", "record"}`, when two people decided |
| `prototypes` | `xv prototype` | one item per prototype: `{"name", "branch", "axis", "recording"}` |
| `checks` | the watch | what the checks after each step found, and each worker's report; the standing orders read this |

## Body

```
# <title>

## Scenario
<the scenario in words>

## May ignore
<what this slice may ignore>

## Recording
<path to the recording, for a defect>

## Log
- <time> <who>: <what happened>
```

## Homes

The default home is the file, because CI can read it. A team that keeps the record in its pull requests renders it with `xv record export <id>` and pastes it, or lets a CI step post it. The fields are fixed; the home is the team's.

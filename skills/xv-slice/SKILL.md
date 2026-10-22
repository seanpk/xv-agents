---
name: xv-slice
description: "Start one XV slice with a person: the scenario in words, what it may ignore, a recording for a defect, and who set the work going; then open its record, branch and worktree and hand it to the watch. Use when a person says \"start a slice\", \"new slice\", \"take the next task\", \"fix this defect with xv\", or gives the watch work that has no slice record yet."
license: MIT
---

# xv-slice

A slice starts with a person. This skill writes down what they want in words, opens the slice record, and hands it to the watch. It owns the scenario. The `watch` skill owns running it.

The one rule: an agent may stop. It may not decide. The scenario is the person's statement of what must be true; you write it down, you do not choose it.

## Ask

One question at a time:

1. **What must be true when this is done?** The scenario in words: the steps a user takes and what they see. For a defect: what happened, what should have happened.
2. **What may this slice ignore?** Edge cases, screens, users, or performance that are out of scope for now.
3. **For a defect: is there a recording?** A Playwright trace, a HAR file, a sequence of requests and responses, a screen recording with the steps. A recording is a better oracle than words. Save it under `.xv/recordings/` and pass its path.
4. **Is the design settled?** If the scenario does not settle how it should look or flow, and a wrong design would be felt in use, this is a prototype slice (`--kind prototype`); see the maker's `prototype.md`.
5. **Who set the work going?** Their name goes in the record. They answer the stops.

Read the scenario back in the person's words. Tidy grammar only. If it is ambiguous about what must be true, ask; do not pick.

Check it against `.xv/pitch.md`. If the scenario looks like it contradicts the pitch, say which line, and ask whether to go on. The guardian will flag it anyway; it is cheaper now.

## Open

```
xv slice new <id> --title "<title>" --by <name> --kind feature|defect|prototype \
  --scenario-file <file> --ignore "<what it may ignore>" [--recording <path>]
```

The id is short and dated, such as `2026-10-21-expiring-today`. The command creates the branch `xv/<id>`, a worktree for it, and `.xv/slices/<id>.md` in that worktree, and prints the worktree path.

Then load the `watch` skill and run the slice, starting with the forecaster. The person sets the budget from the forecast:

```
xv record set <id> budget '{"tokens": 400000, "usd": 3, "turns": 60}' --by <name>
```

## May not

- Write or change the scenario's meaning, or decide what the slice may ignore.
- Set the budget.
- Start the work before the record exists.

## Stop and report when

- The person cannot say what must be true. A slice without a scenario is not ready.
- The scenario contradicts the pitch and the person wants to go on anyway. Record their answer in the slice log and go on; the guardian will raise it for two people.

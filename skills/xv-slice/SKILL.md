---
name: xv-slice
description: "Start one XV slice with a person: the scenario in words, what it may ignore, a recording for a defect, and who set the work going; then open its record, branch and worktree and hand it to the watch. Use when a person says \"start a slice\", \"new slice\", \"take the next task\", \"fix this defect with xv\", or gives the watch work that has no slice record yet."
license: MIT
---

# xv-slice

A slice starts with a person. This skill writes down what they want in words, opens the slice record, and hands it to the watch. It owns the scenario. The `watch` skill owns running it.

Own the result: even when agents write all of the code, a person is responsible for what it does. An agent may stop. It may not decide. The scenario is the person's statement of what must be true; you write it down, you do not choose it.

## Ask

One question at a time:

1. **What must be true when this is done?** The scenario in words: the steps a user takes and what they see. For a defect: what happened, what should have happened.
2. **What may this slice ignore?** Edge cases, screens, users, or performance that are out of scope for now.
3. **For a defect: is there a recording?** A Playwright trace, a HAR file, a sequence of requests and responses, a screen recording with the steps. A recording is a better oracle than words. Save it under `.xv/recordings/` and pass its path.
4. **Is the design settled?** If the scenario does not settle how it should look or flow, and a wrong design would be felt in use, this is a prototype slice (`--kind prototype --axis "<the one axis>"`). Ask for the axis: the one difference between three versions that people would feel by using them. An agent can suggest axes; the person names one. A column and a button have no open question; prototypes there are waste.
5. **Is it a refactor?** If users see no change and the work is to restructure code, this is a refactor slice (`--kind refactor`). The scenario names what to restructure. The suite must be green at the start; it is the oracle, and no new red is written. Ask which changes to old tests the person expects: `--expect-moves imports`, `renames`, or both (comma-separated). For `renames`, ask for each name the slice renames and pass `--rename Old=New`, one flag per pair. A script checks each moved test file against those kinds; any other move still stops for the person.
6. **Who set the work going?** Their name goes in the record. They answer the stops.

When the person gives `--from <ref>`, or says a build is running, write the scenario with them from what runs: the steps a user takes on the build and what they see, in the person's words. Do not ask about a build otherwise; a slice with no build opens as it does now.

When the scenario will not settle (the answers are not clear, the talk goes round without settling, or the person starts to wonder what they want), offer two ways to build to find out: a prototype slice, as in question 4, or an exploration. An exploration opens no slice. Tell the person to build with an agent, outside XV, and to open the slice with `xv slice new --from <ref>` when the scenario can be written from what runs. Offer it; the person chooses.

Read the scenario back in the person's words, in the message to the person: the full scenario and its "may ignore" lines, not only a path to a file. Tidy grammar only. If it is ambiguous about what must be true, ask; do not pick.

Check it against `.xv/pitch.md`. If the scenario looks like it contradicts the pitch, say which line, and ask whether to go on. The guardian will flag it anyway; it is cheaper now.

## Open

```
xv slice new <id> --title "<title>" --by <name> --kind feature|defect|prototype|refactor \
  --scenario-file <file> --ignore "<what it may ignore>" [--recording <path>] \
  [--expect-moves imports,renames] [--rename Old=New] [--from <ref> [--share-build]]
```

The id is short and dated, such as `2026-10-21-expiring-today`. The command creates the branch `xv/<id>`, a worktree for it, and `.xv/slices/<id>.md` in that worktree, and prints the worktree path.

With `--from <ref>` the branch starts at the build, and `base` stays the branch the slice merges into. The scenario agent still writes the red at `base`, without the build, and the red must fail there; then it runs on the build. A red test that fails on the build goes to the maker as a miss; a red that passes on it skips the maker. `--share-build` names the build to the scenario agent as a reference only, and needs `--from`.

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

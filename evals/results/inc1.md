# Evals after increment 1

Run 2026-10-21 on the code as it stood at the end of increment 1: the briefs, the record, the watch's steps, no wall yet. One run per cell. Claude Code ran `sonnet` through `claude -p --safe-mode`; opencode ran `gpt-oss:20b` on a local GPU. The baseline is the same task typed as a person would, with no brief.

| inc | scenario | claude skill | claude baseline | opencode skill | opencode baseline |
| --- | --- | --- | --- | --- | --- |
| 1 | cleaner-standards | 6/6 | 5/6 | 5/6 | 4/6 |
| 1 | guardian-pitch | 3/7 | 1/7 | 7/7 | 1/7 |
| 1 | maker-feature | 3/6 | 4/6 | 6/6 | 4/6 |
| 1 | scenario-defect | 6/6 | 3/6 | 2/6 | 3/6 |

## What the runs showed

- **Claude Code refused every write under `.git/`.** The slice worktrees lived in `.git/xv/worktrees/`. The guardian could not write its packet and the maker could not edit the test the scenario forced it to move. Both agents stopped and reported the denial; neither looked for a way around it. That is the one rule holding, and it is why Claude's guardian and maker scores are low here. Increment 2 moves the worktrees to `.xv/worktrees/`.
- **Without the brief, the maker moved the old test and recorded nothing**, on both harnesses. The suite went green; nothing in the repo says an assertion changed or why. With the brief, opencode's maker recorded the move (`tests/test_store.py`). That gap is what the wall in increment 2 makes a check instead of a sentence.
- **Without the brief, neither harness's review named the pitch.** With the brief, opencode's guardian wrote a packet with `pitch_contradiction: yes` and `shape_change: yes`, quoting the pitch line, and the watch stopped the change for two people. Claude's guardian found the same, cited `.xv/pitch.md:13`, and stopped because it could not write the file.
- **The scenario agent's brief worked on Claude and not on the local model.** On Claude, the red replayed the recording, failed on an assertion, and touched only tests. On `gpt-oss:20b`, the run ended in 38 seconds with no test written and no report.
- **The cleaner applied both standards on Claude, with or without the brief.** The local model removed the `print()` and kept a one-letter name in both arms.
- **A grader was wrong.** `old_tests_green` counted a whole module as broken when the baseline added a new failing test to an old file. It now checks only the tests that existed before the run. The Claude baseline cell for `scenario-defect` was graded with the old version.

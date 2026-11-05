## With a rebase brief

This run is a rebase: the slice's commits are being replayed on a base that moved. The prompt names the new base, and the conflicted files when git found any. Green still means the new scenario plus every existing test; the suite is run for you after you stop.

- Resolve each conflicted file named in your prompt by editing it so that both the slice's intent and the new base's change hold. Leave no conflict markers. Do not stage, commit, or run `git rebase`; the watch does that.
- Then look for what the new base changed that breaks or contradicts what the slice does, even where git showed no conflict: a renamed function the slice calls, a changed message the scenario names, a rule the slice assumed. Fix what you can, in the smallest change.
- Do not touch a test file, `.xv/picture.md` or anything under `.xv/` to make a conflict go away. A conflict in those is a person's.
- Do not renovate. The cleaner makes it right afterwards.
- Report each conflict you resolved, each fix you made, and each problem you could not fix. Stop with `"status": "stopped"` and the problem as the question when you cannot fix one; the person who set the work going decides.

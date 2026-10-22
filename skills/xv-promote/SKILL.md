---
name: xv-promote
description: "Move an XV learning toward the shared skills, and adopt one before inventing it: inside a repo, promote an Open learning seen twice into the standards or rules; across repos, find the matching learning issue on the shared xv-agents repo and draft a sighting, or draft a new issue, for a person to review and post. On the shared repo, tally the issues for the two people who decide. Use at the two standing moments of a burst, when the watch or xv-check says an entry was seen twice, or when a person says \"promote this\", \"share this learning\", \"has anyone seen this\", or \"what's ready to promote\"."
license: MIT
---

# xv-promote

A learning moves up in two steps. Inside a repo, an Open learning seen twice becomes a standard or a rule. Across repos, a learning is shared as an issue on the shared xv-agents repo, collects sightings from other repos, and enters the shared skills only when two people decide it should. Nothing is posted in public without a person's approval.

The one rule: an agent may stop. It may not decide. You list, search and draft. People promote, approve, post and decide.

## When

At the two standing moments of a burst: before it, and as it ends. Also when `xv check entries` notes an entry seen twice.

## Inside the repo

1. `xv promote local` lists the Open learnings in `.xv/learnings.md` seen at least twice.
2. Put each one in front of the person who set the burst going, with its sightings. Do not promote from one sighting.
3. On their word: `xv promote local --accept "<entry title>" --to standards|rules --by <name>`. It moves the entry, keeps its slices and sightings, and adds a line to Promoted so nothing is promoted twice. A judgement call about structure or style goes to `standards`; a fact the agents cannot infer goes to `rules`. If the learning is mechanical, say so: it should be a check, through a slice, not a line.

## Across repos

1. `xv promote candidates` lists the entries in this repo's standards, rules and Open learnings that came from a miss. With the person, pick the ones that might matter beyond this repo. A command, a path, or a fact about this codebase does not travel. A way of working does: how to stop, how to test, how to read a change.
2. For each one, search first: `xv promote search <a few words from the rule and the miss>`. Read the matching issues' rules and examples. Two repos may use the same words for different problems; compare the examples, not only the titles.
3. Draft:
   - A match: `xv promote draft --issue <n> --entry "<entry title>" --rule "<the rule in general words>" --example "<the miss, concretely>"`.
   - No match: the same without `--issue`; it drafts a new issue titled "Learning: <the rule>".
   - `--kind` is `standard`, `rule`, `check`, or `brief` (a change to an agent's brief). `--applies-to` names a stack (`rails`, `react`) when the rule means nothing elsewhere; leave it out for "any".
   - The rule is condition → behaviour, with no project names. The example is one concrete miss, short.
4. Show the person the whole draft (`.xv/promote/drafts/<file>`). It names this repo by default and may carry its description; `promote.include_name` and `promote.description` in `.xv/config.yml` say what this repo shares. Ask them to check the example for anything private: names of customers, people, internal systems, code that should not be public. Edit the draft with them.
5. Only on their approval: `xv promote post <draft> --approved-by <name>`. It posts the issue or the comment, keeps a copy in `.xv/promote/posted/`, and links the local entry to the issue (`shared: <repo>#<n>`). The person commits.

## On the shared repo

`xv promote tally` lists the open learning issues with how many distinct repos have seen each one and when. It is evidence for the two people who decide, not a trigger: no count opens a pull request. When they decide an issue is ready:

- Write the rule in its general form into the brief or reference file it belongs to. The examples stay in the issue; concrete traces do not transfer between repos.
- A rule that only applies to one stack goes in with its stack named, in the place the brief reads it.
- Add a line to `CHANGELOG.md` with the issue and the two names. It is a change to a brief: Decide from evidence.
- Close the issue with the release that carries it. Each repo that linked an entry to it removes its local copy at its next `xv check`.

## May not

- Post, comment, or open an issue without `--approved-by` and a person's word.
- Promote from one sighting, or count a sighting in this repo twice.
- Write a learning into a shared brief without two people.
- Put another repo's details in a draft.

## Stop and report when

- A draft's example cannot be made safe to publish. Leave it unposted and say why.
- `gh` is not logged in, or the shared repo cannot be reached. Keep the draft; the person posts it later.

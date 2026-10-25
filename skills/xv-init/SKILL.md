---
name: xv-init
description: "Write a starter project layer, .xv/, into an existing repo before its first XV slice: the pitch from a short interview with a person, and the shared operating picture from an outsider read plus what only people know. Use when a person says \"set up xv\", \"xv init\", \"start XV in this repo\", or when the watch finds no .xv/pitch.md or .xv/picture.md."
license: MIT
---

# xv-init

The guardian checks every change against a pitch and a picture. This skill makes both before the first slice. The pitch is the people's statement of what the system is for, so it comes from them. The picture is generated where it can be, so it can be wrong in a checkable way, and people correct it.

The one rule: an agent may stop. It may not decide. You may not invent what the system is for.

Note the time when you run `xv init`. Keep a list, as you go, of each question the person asks and each step that needs work this skill does not describe. Step 8 reports both.

## 1. The files

```
xv init
```

copies the starter files from this repo's `defaults/` into `.xv/`, fills in `.xv/config.yml` with what it detects, and writes `.xv/boundary-all.md`. It never overwrites a file that exists.

**A trial.** If the person wants to try XV before the team commits to it, offer:

- `xv init --trial`: `.xv/` goes into `.git/info/exclude`, so none of it enters the repo's history. Slices still run.
- `xv init --trial --repo`: the same, and `.xv/` becomes its own git repo, so the layer keeps its history. Pushed to a private remote, teammates can opt in: clone it into `.xv/` in their own checkout, then run `xv init --trial` there, which keeps their copy out of the app's history and keeps every file. Suggest it when the person wants a history of the pitch and the picture, or wants teammates in the trial.

`xv init --adopt` ends a trial. If `.xv/` is its own repo, it refuses while that repo has uncommitted changes, then moves `.xv/.git` to `<git common dir>/xv-trial.git` and says where. It deletes nothing. Then the person commits `.xv/` in the app.

**Check the setup with the person** before the outsider read. Each one changes what the agents see.

- **The test command.** Show `tests.command` and `tests.paths`. If the output lists `runners` (marker, command, paths), there is more than one suite. Show each and ask which command to use: one, several joined with `&&`, or a script. `tests.paths` is already the union over the runners; the wall hashes every file it matches.
- **A big suite.** The command must return in minutes. If the whole suite cannot, set `tests.command` to a script that picks the suites the slice touches. It runs with `XV_BASE` (the slice's base commit) and `XV_SLICE` (the slice id) in its environment. The script lists the changed files with `git diff --name-only "$XV_BASE"` and `git ls-files --others --exclude-standard` (new files), maps each to its runner and specs, and runs a fixed fast set when nothing maps. Add its path to `tests.paths`, so a change to it shows in `xv wall diff`. The person approves the script; it decides what green means.
- **The source roots.** Open `.xv/boundary-all.md` with the person. Each module should be a part the team names when it talks about the code. With `source.roots: ["."]`, a large app is one module, and the guardian never sees a shape change. A Rails layout gets `app`, `lib` and `app/javascript`. Under a root other than `.`, a module's name includes the root: `app/controllers`, `app/javascript/controllers`. After a change to the roots, run `xv boundary --all > .xv/boundary-all.md`. A list in `.xv/config.yml` may span lines.

## 2. The outsider read

The picture is what the guardian checks a change's shape against, and what a new person or agent reads to learn the system. The outsider is a fresh agent context. It is not told how the system works and does not see the pitch. Where it gets something wrong, a newcomer would too, so each correction is a line the picture needs.

Run it before the interview, so nothing the person says shapes it:

```
xv step outsider --init
```

That runs `outsider-read.md` (in this skill's folder). It writes `.xv/picture.md` as a draft marked `status: generated, unchecked`: the modules and their coupling from `.xv/boundary-all.md`, the tables, the surfaces users meet, the names things go by in the code. It reads the repo's own docs as claims to check, and lists where the code and the docs disagree. It says what the code adds up to, not what it says line by line.

If the harness cannot shell out, run the outsider read in a subagent with the text of `xv prompt outsider --init` and nothing else.

## 3. The interview

Ask one question at a time, and write down the person's words.

**The pitch comes first.** No slice starts without it: `xv slice new` refuses while `.xv/pitch.md` says `status: not written`, because the guardian checks every change against it.

1. **The pitch, in one sentence:** what does the system do, and for whom? Hold the person to one sentence. If the answer runs longer, read it back and ask which sentence is the pitch. Keep the rest for the page.
2. **The page,** one heading at a time: Why does it exist; what would its users do without it? Who uses it? Who is it not for, and what will it never do?

The sentence goes under the title of `.xv/pitch.md`, the answers under the headings of "The page". You may tidy their words: fix grammar, put them in order, ask about a gap. You may not add a purpose, a user, or a promise they did not state. When it is written, set `status: written`. If the person will not write one now, leave the file with its prompts and `status: not written`, and tell them no slice can start until it exists.

**The picture.** Then ask:

3. **Users:** who are they, by name or by role? Who on the team sits with them?
4. **Vision:** what is the system becoming?
5. **Decisions that bind:** what has the team settled that an agent must not reopen? Do not ask this cold. Draft the list from AGENTS.md, CLAUDE.md, `docs/` and the README, each decision with its source. Show the draft; the person cuts and adds. You may draft from what the repo already states. You may not invent a decision, or turn a habit you saw in the code into one.
6. **In motion:** what work is under way that a slice could collide with? No agent checks this section by name. The guardian reads the whole picture, so it helps it and the person reading a packet tell a change that belongs to work under way from one that cuts across it. A useful answer is one line per item, dated: "Moving billing from Checkout to Elements; new code uses Elements; Checkout goes by March." Keep the question short. "Nothing" is a fine answer.
7. **Runtime budgets:** response times, sizes, costs the system must stay inside.

Write answers 3 to 7 under their headings in `.xv/picture.md`. Then walk the person through the outsider's draft, section by section, and let them correct it. Settle each place the code and the docs disagree: which one is right, or a question for later.

Keep the picture under two pages. The guardian loads all of it on every slice. The listener reads it for names and flows, and the prototype maker reads it loosely. The maker, the cleaner, the scenario agent and the forecaster do not read it. Where the repo's docs already say more, point to them; do not copy them. Keep in the picture what the guardian needs to check a change: users, shape, names, decisions.

When the person has corrected it, set `status: checked` and `checked_by: <name>` in its front matter. Note the time.

## 4. Who decides

Ask: **is this a one-person team?** XV puts a shape change, a pitch contradiction, a prototype pick and a budget past the team's limit in front of two people. A solo team has one. If so, set `seats.two_people: solo` in `.xv/config.yml`: those stops still fire and still wait, the one person answers them, and each answer is written down in `.xv/decisions/`. Otherwise, ask who sits in the two-people seat and who is the chief engineer, and write their names under `seats:`.

## 5. Sharing what this repo learns

XV repos share learnings as issues on the shared xv-agents repo (the `xv-promote` skill). Nothing is posted without a person's approval, but the person decides now what this repo says about itself when it does. Ask:

1. Include the repo's name in what it shares? `xv init` sets no for a private GitHub repo. A client's repo is usually no.
2. A one-line description of the repo for other teams. The default is its GitHub description (`gh repo view --json description`), blank if it has none.
3. The stacks it is built on, as short labels (`python`, `rails`, `react`), so a learning that only means something on one stack is marked.

Write the answers to `promote:` in `.xv/config.yml` (`include_name`, `name`, `description`, `stack`). `xv init` fills in its guesses; correct them with the person.

## 6. The first packet

List the places where the outsider read and the pitch disagree and a person must decide. Write the list to `.xv/slices/packet-init.md`. It is the first packet, and the first evidence for whether a written picture loads a new person. Do not resolve the disagreements; they are for the people.

A gap earns a line when settling it would change what a slice may do: the code serves a user or makes a promise the pitch would refuse, or the pitch makes a promise the code does not keep. Silence in the pitch is not a contradiction. Surfaces that support the product but are not it (an admin role, demo or seed data, help pages, health checks, internal tools) go on one line at the end, "Noted, not raised", by name only.

## 7. Install the wall

```
xv wall install-hook
```

installs the pre-commit hook that runs the wall check on slice branches. Point the person at `ci/github/` in this repo for the CI examples.

## 8. Review this init

Every init is evidence for the next one. Show the person:

- The questions they asked that this skill did not answer before they asked.
- The steps that needed work outside this skill: a setting edited by hand, a script written, a command that failed.
- The wall-clock time from `xv init` to the checked picture. Say that it includes time away.

Then load the `xv-promote` skill and follow its "Across repos" steps. Each finding that would change this skill, a default, or a check is a learning: add it to Open in `.xv/learnings.md` with `from: init`, search the shared repo first, and draft a sighting or a new issue with `--kind brief` (or `check`). End each example with the wall-clock time. The person checks each draft for anything private. Nothing is posted without their approval.

## May not

- Invent a purpose, a user, a vision, a decision, or a promise.
- Mark the picture checked; the person does.
- Overwrite an existing `.xv/` file. If one exists, show the difference and ask.
- Commit; the person commits the project layer.
- Post a learning without the person's approval.

## Stop and report when

- The repo has no tests the wall can hash. Say so; the wall and the maker depend on a suite.
- The person does not want to write the pitch now. Leave the prompts in place and say what that means for the guardian.

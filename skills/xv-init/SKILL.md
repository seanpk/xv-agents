---
name: xv-init
description: "Write a starter project layer, .xv/, into an existing repo before its first XV slice: the pitch from a short interview with a person, and the shared operating picture from an outsider read plus what only people know. Use when a person says \"set up xv\", \"xv init\", \"start XV in this repo\", or when the watch finds no .xv/pitch.md or .xv/picture.md."
license: MIT
---

# xv-init

The guardian checks every change against a pitch and a picture. This skill makes both before the first slice. The pitch is the people's statement of what the system is for, so it comes from them. The picture is generated where it can be, so it can be wrong in a checkable way, and people correct it.

The one rule: an agent may stop. It may not decide. You may not invent what the system is for.

## 1. The files

```
xv init
```

copies the starter files from this repo's `defaults/` into `.xv/` and fills in `.xv/config.yml` with the test command and test paths it can detect. It never overwrites a file that exists. Show the person what it detected and ask them to correct the test command if it is wrong; the test wall depends on it.

## 2. The outsider read

Run it before the interview, so nothing the person says shapes it:

```
xv step outsider --init
```

That runs `outsider-read.md` (in this skill's folder) in a fresh context that has not been told how the system works. It writes `.xv/picture.md` as a draft marked `status: generated, unchecked`, with what an outsider sees: the modules and their coupling from `xv boundary --all`, the tables, the surfaces users meet, the names things go by in the code. It does not repeat what the code says line by line; it says what the code adds up to.

If the harness cannot shell out, run the outsider read in a subagent with the text of `xv prompt outsider --init` and nothing else.

## 3. The interview

Ask, one question at a time, and write down the person's words:

1. In one or two sentences: what does the system do, and for whom?
2. Why does it exist? What would its users do without it?
3. Who is it not for, and what will it never do?
4. Who are the users, by name or by role? Who on the team sits with them?
5. What is the vision: what is the system becoming?
6. Which decisions bind: things the team has settled that an agent must not reopen?
7. What is in motion right now?
8. Are there runtime budgets: response times, sizes, costs the system must stay inside?

**The pitch.** From answers 1 to 3, the person writes the elevator pitch and then a page. You may tidy their words: fix grammar, put them in order, ask about a gap. You may not add a purpose, a user, or a promise they did not state. Write it to `.xv/pitch.md`. If the person will not write one now, leave the file with the questions and `status: not written`, and tell them the guardian will stop every change for two people until it exists.

**The picture.** Add answers 4 to 8 to `.xv/picture.md` under their headings. Then walk the person through the outsider's draft, section by section, and let them correct it. When they have, set `status: checked` and `checked_by: <name>` in its front matter.

## 4. The first packet

List every place the outsider read and the pitch disagree: a surface the pitch does not mention, a user the code serves that the pitch leaves out, a promise the code does not keep. Write the list to `.xv/slices/packet-init.md`. It is the first packet, and the first evidence for whether a written picture loads a new person. Do not resolve the disagreements; they are for the people.

## 5. Install the wall

```
xv wall install-hook
```

installs the pre-commit hook that runs the wall check on slice branches. Point the person at `ci/github/` in this repo for the CI examples.

## May not

- Invent a purpose, a user, a vision, or a promise.
- Mark the picture checked; the person does.
- Overwrite an existing `.xv/` file. If one exists, show the difference and ask.
- Commit; the person commits the project layer.

## Stop and report when

- The repo has no tests the wall can hash. Say so; the wall and the maker depend on a suite.
- The person does not want to write the pitch now. Leave the questions in place and say what that means for the guardian.

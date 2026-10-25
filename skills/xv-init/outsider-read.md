# The outsider read

You are new to this repo. Nobody has told you how the system works, what it is for, or who uses it, and nobody will. Read the repo the way an outsider would, and write down what you see. Your draft is the first shared operating picture; people will correct it.

The one rule: an agent may stop. It may not decide. You describe; you do not decide what the system is for.

## Read

- The boundary output your prompt gives you (`xv boundary --all`): modules, the edges between them, tables, routes and commands.
- The repo's own docs: the README, `docs/`, AGENTS.md, CLAUDE.md and other agent rules files, decision records, and any generated architecture docs. They state what the code cannot show: the issue tracker, the product range, the external systems. Use what they state. They are still claims to check against the code, not truth.
- Entry points: the main program, the routes, the CLI, the jobs.
- The tests, for what the team thought worth asserting.

Do not read `.xv/pitch.md` if it exists. Your read must not be shaped by it.

## Write

Write `.xv/picture.md` in this shape:

```
---
status: generated, unchecked
generated_by: outsider read
date: <today>
---

# The shared operating picture

## What an outsider sees
<Three to six sentences: what the system appears to do, for whom, as the code shows it. Say where you are guessing.>

## Users
<Who the code seems to serve, from routes, roles, and messages. Mark each as seen in the code, stated in the docs, or guessed.>

## The shape
<Modules and what each owns, the edges between them, the tables, the surfaces users meet. From the boundary output. A short Mermaid graph if it helps.>

## Names
<The words the code uses for the main things, and any place two words seem to mean the same thing.>

## Where the code and the docs disagree
<Each place a doc says one thing and the code shows another: the doc and line, what the code shows, and where. If you found none, say which docs you compared.>

## Questions an outsider would ask
<What you could not tell from the code.>

## Vision, binding decisions, in motion, runtime budgets
<Leave each as "Not known to an outsider." People fill these in.>
```

Do not repeat what the code already says line by line. Say what it adds up to. Where a doc already says more, point to it; do not copy it. Keep it under two pages.

## May not

- Read the pitch.
- Write anything but `.xv/picture.md`.
- Present a guess as a fact. Mark it.

End your final message with one report block:

```xv-report
{"agent": "outsider", "status": "done", "summary": "<one line>", "picture": ".xv/picture.md", "questions": 0}
```

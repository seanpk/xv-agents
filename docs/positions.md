# Positions taken by Sean

Where the plan said a position was Sean's, what he decided, and when. A builder's choice is in `docs/decisions.md`; this file holds only what a person with the say decided.

## How a learning travels between repos (2026-10-22)

The plan's open position: "Promotion carries the abstract form only. Concrete traces stay in the project." Asked while building increment 8. Sean's answer reshaped the mechanism around it:

- **The channel is issues on `seanpk/xv-agents`.** At the two standing moments of a burst, an adopting repo's `xv promote` lists its entries that might matter beyond it, searches the open learning issues, and drafts either a sighting on a matching issue or a new issue. Agreed.
- **Adopt before inventing.** When a repo has a miss, the retro checks the open learning issues for one that fits before it proposes a local rule from scratch. Adopting one adds a sighting. Sean's idea.
- **No count triggers a pull request.** Two sightings are not enough; the count is evidence on the issue. Two people decide when an issue becomes a pull request and a release. Sean: "likely two reports is not sufficient".
- **Nothing is posted in public without a person's approval.** xv drafts; a person reviews the draft and approves the post. Sean: "xv should not post publicly without approval and a human should review it".
- **A sighting names its repo by default.** `xv-init` asks: include the repo name (Y/n), and a repo description, defaulting to the GitHub description, blank if none.
- **A sighting includes an example**, which the person reviews before it posts.
- **Tech stacks: start with nothing more than a label**, and add structure if use asks for it. Sean: "probs the most lightweight, maybe nothing, to start".

Sean asked what the example is for. The builder's answer, which v0.1 follows: the example helps a later retro match a new miss to an open issue, and helps the two people who decide see whether the sightings are the same pattern. It stays in the issue as evidence. The pull request into the skills carries the rule in its general form only, because concrete traces do not transfer between repos. Sean agreed on 2026-10-22: "I agree with that promotion PR statement."

## A one-person team (2026-10-22)

The newcomer review of the README found that someone trying XV alone hits a wall: two-person stops cannot be answered by one person. Sean: "the pitch should come first, yes. a solo mode is good, I was thinking about the need for that already, so we should support it."

- **The pitch comes first.** No slice starts until `.xv/pitch.md` is written.
- **Solo mode is supported**, as `seats.two_people: solo` in `.xv/config.yml`. How it works is the builder's, in `docs/decisions.md`.

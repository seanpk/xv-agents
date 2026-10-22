# The protected core

What a project layer may not relax. A project file may add a rule, a fact, an example, or a standing order. It may not take away any of the lines below. `xv check relaxations` reads every project file and reports a line that looks like it does.

Local versions of a shared checklist drop the social prompts first. In XV the social prompts are the stops. (Blair, Baugh, Gawande and Berry, 2016: of 126 local surgical checklists, 25.4% kept all seven teamwork prompts.)

1. **The contexts are kept apart.** The scenario agent, the maker, the cleaner and the guardian each run in a fresh context. No context grades its own work.
2. **The scenario agent is never the maker.** A context that writes the red and then makes it green is agreeing with itself.
3. **A test moves only with a record.** An old test changes only when the scenario forces it, and the move is recorded with the file, the assertion and why. The wall check fails on an unrecorded move.
4. **The guardian makes four checks**: a shape change, a contradiction of the pitch, any old test that changed, and what the change does to the picture. Every finding cites evidence.
5. **The stops wake a person.** The standing orders in `scripts/orders.py` run after every step, and a stop ends the watch's turn until a person answers.
   A one-person team may declare `seats.two_people: solo`: the two-person stops still fire and still wait, one person answers them, and the answer is written down. `xv check` lists the setting.
6. **The may-not lists hold.** No agent merges, approves, ranks the value queue, settles a shape, edits the pitch, raises a budget, or accepts its own change.
7. **An agent never accepts its own change**, and the context that proposes a change is never the one whose brief changes.

A team that needs to change one of these copies the brief under a new name, records why in `.xv/decisions/` with who took part, and accepts that the copy no longer receives upgrades.

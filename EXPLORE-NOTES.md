# Explore: the #168 rename

A working build of the rename, made outside the slice process.
The suite is green on this branch.
A slice starts from it with `xv slice new --from explore/names-168`.

## What was renamed, by kind

- **Folders:** `skills/scenario` → `skills/test-writer`, `skills/guardian` → `skills/inspector`, `skills/listener` → `skills/field-listener`, `ci/github/xv-guardian.yml` → `ci/github/xv-inspector.yml`. Each `SKILL.md` has the new `name:` and title (`# The test writer`, `# The inspector`, `# The field listener`).
- **Steps:** `test-writer` and `inspector` in `STEPS` (`run.py`, `record.py`), `orders.py`, `pairing.py` (`--next`), `prompt.py` (`AGENTS`), `check.py` (`AGENTS`), `commit_step`, the allow-list seats in `xv init`.
- **Config:** `agents.test-writer`, `agents.inspector`, `agents.inspector_repass`, `agents.field-listener`, and top-level `field_listener:`. `defaults/config.yml` and this repo's `.xv/config.yml` use them.
- **CLI:** `xv inspect --base <ref>` in place of `xv guard`. `xv listen` keeps its name.
- **Record values:** new records hold `test-writer` and `inspector` in `next`, `step_start.agent`, `checks.<step>`, `checks.reports[].agent`, `stops[].step`, `stops[].sendback_to`, `stops[].sendback.to`, `spend[].step`, `pairings[].step` and `.next`, and `moved_tests[].by`. The order a stopped agent raises is `test_writer_stopped` or `inspector_stopped`. A packet's miss line takes `to: test-writer`.
- **Prose:** the briefs, README, `docs/`, `.xv/picture.md`, the CI examples, `defaults/`, help text and messages. The guardian's packet is "the inspection report" and the listener's is "the field report". "Packet" stays in commands, file names, record fields, packet headings (`# Packet:`), and where people decide on a report (the stop table, "two people decide from the packet"). The old headline is gone from all 15 brief files, `docs/briefs.md`, README and the picture. "Boundary picture" is "boundary diagram", including `xv boundary`'s output heading and the packet template's `## The boundary diagram`.
- **Evals:** the scenario JSONs' `agent` and `skill_cmd`, and `grade.py`'s list of steps.
- **CHANGELOG and README:** one line under `## Unreleased`; upgrade notes under Install ("Upgrading past the #168 rename").

## How old names are read and warned about

One mechanism, in `scripts/xvlib.py`, beside the #185 one it extends:

- `OLD_AGENTS`, `OLD_AGENT_KEYS`, `OLD_CONFIG_KEYS` hold the old names; `DROP_ISSUE` names #204.
- `warn_old_name` prints one line on stderr, once per process for each old name. It names the new name and "#204 (Drop the old agent names kept after the #168 rename)". No version is promised.
- `agent_name` maps a name a person typed. It is the argparse `type` on `xv step`, `xv prompt`, `xv orders --after`, `xv record report`, `xv record answer --next`, `xv record stop --step`, `xv pairing end --next`, `xv record set next`, and `xv adapt --agents`.
- `upgrade_names` (already applied in `split_front_matter`) now also calls `_upgrade_steps`, which rewrites stored step names in the fields listed above. The next `xv` write of the record saves the new names. `OLD_ORDERS` maps `scenario_stopped` and `guardian_stopped` silently, as #185 did for its orders.
- `upgrade_config`, applied in `load_config`, moves the old config keys; a new key already present wins.
- `xv guard` is a second parser name for `cmd_inspect`, and warns.
- `xv install` removes the links (user scope) and unedited copies (project scope) it made under `scenario`, `guardian` and `listener`, and reports them under `removed_old_names`; an edited copy is kept and named under `skipped`. `xv install --remove` takes out old-name links too.
- `xv adapt` removes `xv-guardian.md` and the like when it wrote them (it checks its own marker). `xv check overrides` still flags a file under an old name, and says to re-run `xv adapt` for a generated one.
- A report block whose `agent` is an old name is read as the new name, silently.

The old-name behaviour is pinned in `tests/test_old_agent_names.py` (17 tests).

## Choices the scenario did not settle

- Choice: `agents.field-listener` (hyphen) is the new key for the field listener's CLI, and `agents.listener` and `agents.scenario` are read too, with the warning. Why: the agents keys are agent names, like `agents.test-writer`; #204's list names neither old key, but dropping them silently would send a configured step to `agents.default`.
- Choice: the packet heading for a directed edit is `## Directed edits after the inspector`; a packet that already has the old heading gets its line under that one, not a second heading. Why: the heading names the agent, not the packet.
- Choice: the stop order names change (`test_writer_stopped`, `inspector_stopped`). Why: they are built from the step name, and `test-writer_stopped` would be the only order with a hyphen.
- Choice: a record warning is one line per old name per process, whichever field holds it. Why: per-field warnings gave ten lines on every `xv decisions` or `xv retro counts` in this repo, from closed records nobody rewrites.
- Choice: `ci/github/xv-listener.yml` keeps its file name. Why: it runs `xv listen`, which keeps its name, so an adopter has nothing to rename.
- Choice: `docs/decisions.md` keeps the agents' names its entries were written with, under a note naming the new ones; only "boundary picture" changed there. Why: it is a dated log, like CHANGELOG history.
- Choice: tests were moved to the new names (quoted step names, brief titles, config keys, `xv inspect`), and the old names are tested in one file. Why: a test that calls an old name and asserts a new one reads as a contradiction. `OwnTheResultTest` now asserts the headline is absent (it asserted it was present).
- Choice: the watch brief says the old step names still run until #204. Why: a person may type them at the watch.

## Left alone, and why

- `.xv/rules.md` (7 lines), `.xv/learnings.md` (10), `.xv/estimation.md`, `.xv/.gitignore` (1 comment): people's files, outside this explore's permission.
- `evals/fixture/.xv/*`, `evals/setups/promote/issues.json`, `tests/data/stop-decisions-red/**`: test data, copies of what an adopter or an old file held.
- Internal names that a test or another file depends on: `run.py land-scenario` (`test_briefs_picture` asserts the watch brief names it), the scratch file `xv-scenario-scratch-<id>.json`, functions `refactor_scenario`, `scenario_scratch`, `land_session_scenario`, eval file names and grader names (`guardian_did_not_edit`, `listener_packet_*`), `kind: production-packet`, the `xv/packet-<date>` branch in the listener workflow, and test method names.
- "Scenario" as the noun for the slice's scenario, `--scenario-file`, `## Scenario`, `## Scenario misses`, `change_misses_scenario`, `red_misses_scenario`, `scenario_not_red`, `scenario_touched_source`.
- CHANGELOG history and old slice records.

## Open questions for Sean

1. Should closed records read old names silently? Now every `xv decisions` or `xv retro counts` in a repo with history prints two warning lines until #204. Recommendation: keep the warning, and let #204's "read once more by an xv that rewrites it" be an `xv record upgrade --all` that rewrites closed records in one commit.
2. Is `agents.field-listener` the key you want, or `agents.field_listener` to match `field_listener:`? Recommendation: the hyphen, so every `agents.<name>` is an agent's name.
3. `ci/github/xv-inspector.yml` runs `xv inspect` but still pins `ref: v0.5.2`, which has no `xv inspect`. Recommendation: the release that carries this bumps the pin in all three workflows in the same commit.
4. Should `agents.scenario`, `agents.listener` and the stop orders `scenario_stopped` / `guardian_stopped` be added to #204's list? Recommendation: add the two config keys to #204; leave the order names in `OLD_ORDERS` with #185's.
5. Do you want the people-owned files (`.xv/rules.md`, `.xv/learnings.md`, `.xv/.gitignore`) brought to the new names in this slice, by a person? Recommendation: yes for `rules.md`, since the inspector's brief reads it; leave `learnings.md` entries as written.
6. Should the internal names (`land-scenario`, `scenario_scratch`, the scratch file, the eval graders) follow in a later refactor slice? Recommendation: yes, a refactor slice after this one, so this slice's diff stays a rename of what people see.

## Surprises for the slice's test writer

- `tests/fake_agent.py` picks its behaviour from the brief's first line (`# The scenario agent`, `# The guardian`). Renaming a brief's title breaks every loop test until the fake reads the new title.
- `orders.evaluate` and `orders.verdict` take in-memory dicts; only records read from disk are upgraded. A test that builds a dict with `checks: {"scenario": ...}` is not read under the new name.
- The `*_stopped` order is built from the step name (`f"{after}_stopped"`); a hyphenated step needs the hyphen turned to an underscore.
- A blanket replace of `"scenario"` in tests also hits `tests/test_token_cap_one_count.py`, where `"scenario"` is the eval's own key (`evals/report.py` reads `r["scenario"]`).
- `xv init`'s starter allow-lists match config lines by seat name (`  inspector: ["claude"`), so `defaults/config.yml` and `run.allow_lists` must agree.
- Warnings are once per process: a unit test must clear `xvlib._warned` before it captures stderr.
- argparse runs `type=agent_name` before `choices`, so `--next scenario` passes `choices=STEPS`.
- `xv record answer --next <earlier step>` needs `--settled`, or it refuses.
- `test_briefs_picture` asserted the old headline was present; it now asserts it is absent, in the briefs and in README, `docs/briefs.md` and the picture.

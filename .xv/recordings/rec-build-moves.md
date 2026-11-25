# Recording: in a slice from a build, the build's changes to old tests stop as the test writer's (#210)

Taken from the slice record `.xv/slices/2026-11-20-names.md` on main (84f20f5). The test writer step was called `scenario` then.

## Slice `2026-11-20-names`

- Opened with `xv slice new --from explore/names-168`.
- base: `0058633bda75dfd111de6457572b00ece306bb9e`
- build: `{"kind": "exploration", "ref": "explore/names-168", "commit": "ce7938666913527700bc7d799c4859677558f651"}`
- The build renamed the agents across the site, tests included. The test writer's red added new tests.

### 2026-11-20T21:54:46+00:00: `unrecorded_move`, step test-writer

- question: The scenario agent changed or removed old tests or assertions in old test files that existed at the base: tests/fake_agent.py, tests/test_allowed_commands_prompt.py, tests/test_answer_in_prompt.py, tests/test_briefs_picture.py, tests/test_budget_cap.py, tests/test_budget_cap_turns_session.py, tests/test_by_name.py, tests/test_check.py, tests/test_diff_count.py, tests/test_from_build.py, tests/test_init_allow_list.py, tests/test_init_allow_list_bare.py, tests/test_init_allow_list_prompt.py, tests/test_init_allow_list_split.py, tests/test_kept_pick.py, tests/test_listen.py, tests/test_names_upgrade.py, tests/test_orders.py, tests/test_packet.py, tests/test_pairing.py, tests/test_pairing_build.py, tests/test_picture_lines.py, tests/test_prototypes.py, tests/test_record.py, tests/test_refactor_kind.py, tests/test_removal_line.py, tests/test_repass.py, tests/test_retro.py, tests/test_run.py, tests/test_slice_rebase.py, tests/test_spend.py, tests/test_suite_red_quote.py. Revert them, or record why the scenario forces it.
- answer: sure, 1 is fine
- settled: The 32 test files are the build's renames, recorded one move per file by Sean Kennedy. (The rest of the settled line is about other stops.)

What should have happened: the stop still asks a person to accept the 32 files, but says the build changed them, and lists any change the test writer made to an old test apart from them.

Where: `scripts/run.py` `old_red_changed` (called after the test writer, on a tree that holds the build plus the red) and `scripts/wall.py` `old_red_changed`, which compare each old test file with the base. The wall check after later steps already reads the build's commit (`scripts/wall.py` `check`, `data["build"]["commit"]`).

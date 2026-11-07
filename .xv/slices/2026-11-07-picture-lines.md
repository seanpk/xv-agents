---
id: 2026-11-07-picture-lines
title: One sentence per line in the picture
kind: feature
status: stopped
set_by: Sean Kennedy
created: 2026-11-07
branch: xv/2026-11-07-picture-lines
base: d87a59c5f565efb6935e7fcffa6fd4ba83ae3b50
next: scenario
build: none
build_shared: no
forecast: {"keys": [{"harness": "claude", "model": "sonnet", "tokens": 300000, "turns": null, "usd": 1.6, "basis": ["2026-11-06-covers-stall", "2026-11-05-wave1-fixes", "2026-11-05-scenario-checks"]}, {"harness": "claude", "model": "opus", "tokens": 150000, "turns": null, "usd": 2.0, "basis": ["2026-11-06-covers-stall", "2026-11-05-wave1-fixes", "2026-11-05-scenario-checks"]}], "wall_s": 1500, "shape": "narrow", "breadth": "Four agent briefs (guardian, maker, watch, xv-init), one xv-check check, a CHANGELOG line and a picture rewrap; the only logic is the check and the packet note."}
budget: {"tokens": 450000, "usd": 3.6, "set_by": "Sean Kennedy"}
red: {"files": ["tests/test_picture_lines.py"], "command": "cd tests && python3 -m unittest test_picture_lines", "failure": "AssertionError: Lists differ: [] != [4] (packet names no picture line); Regex didn't match: one sentence per line (guardian brief)", "watch_first_green": "Open .xv/picture.md and read a few list items: each sentence on its own line, a list item's extra lines indented two spaces. Then put two sentences on one picture line and run `xv record packet`: the packet should name that line (picture.md:N) and the slice should not stop."}
wall_baseline: {"commit": "63f210de508367c768aa3e565eb7a1d0be919425", "count": 67, "digest": "b3c10a8a34fcc14b", "file": ".xv/slices/2026-11-07-picture-lines.wall.json"}
moved_tests: []
slice_only: [{"file": "tests/test_picture_lines.py", "test": "test_joined_again_the_picture_says_the_same_words_as_at_the_base", "why": "one-time check of the rewrap against the picture at the slice's base", "checks": ".xv/picture.md"}, {"file": "tests/test_picture_lines.py", "test": "test_an_unreleased_line_names_one_sentence_per_line_in_the_picture", "why": "checks one CHANGELOG line", "checks": "CHANGELOG.md", "accepted": true}]
wall_recommendations: []
suite: null
cleaner_commit: null
packet: null
shape_change: null
pitch_contradiction: null
spend: [{"harness": "claude", "model": "haiku", "model_id": "claude-haiku-5-5", "tokens_in": 6, "tokens_out": 4144, "cache_read": 61873, "cache_write": 35619, "tokens": 39769, "usd": 0.0098, "turns": 4, "wall_s": 20.8, "session": "69083aff-ebd6-45b1-a99f-99685eb15e8c", "step": "forecaster", "at": "2026-11-07T15:18:55+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-07-picture-lines/01-forecaster.out"}, {"harness": "claude", "model": "sonnet", "model_id": "claude-sonnet-5-5", "tokens_in": 34, "tokens_out": 13118, "cache_read": 754435, "cache_write": 67180, "tokens": 80332, "usd": 0.4754, "turns": 18, "wall_s": 101.1, "session": "340bf1dd-7727-4ac9-98e5-3e34115f9ea0", "step": "scenario", "at": "2026-11-07T15:31:17+00:00", "exit": 0, "log": "/home/sean/Making/Personal/xv-agents/.git/xv/runs/2026-11-07-picture-lines/02-scenario.out"}]
stops: [{"at": "2026-11-07T15:18:55+00:00", "step": "forecaster", "order": "budget_not_set", "seat": "originator", "question": "Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-picture-lines budget ... --by <name>`).", "answered_by": ["Sean Kennedy"], "answer": "use the forecast", "also": [], "options": [{"text": "Budget = forecast: 450k tokens, $3.60", "settles": "The budget is the forecast, 450,000 tokens and $3.60.", "amends": false}, {"text": "Budget with headroom: 600k tokens, $5.00", "settles": "The budget is 600,000 tokens and $5.00, about a third over the forecast.", "amends": false}], "recommended": 2, "answered_at": "2026-11-07T15:29:31+00:00", "pick": 1, "settled": "The budget is the forecast, 450,000 tokens and $3.60.", "new_info": "none", "cause": "decision: the budget is the person's to set", "budget_change": {"from": null, "to": {"tokens": 450000, "usd": 3.6}}}, {"at": "2026-11-07T15:31:18+00:00", "step": "scenario", "order": "slice_only_marks", "seat": "originator", "question": "Sean Kennedy: the scenario agent marked 1 test(s) slice-only, so the cleaner may remove them and they do not join the wall: test_joined_again_the_picture_says_the_same_words_as_at_the_base in tests/test_picture_lines.py (one-time check of the rewrap against the picture at the slice's base). Accept the marks, or unmark a test so it joins the wall and the cleaner keeps it.", "answered_by": [], "answer": null, "also": [], "budget_seen": {"tokens": 450000, "usd": 3.6, "set_by": "Sean Kennedy"}}]
decisions: []
prototypes: []
overrides: []
checks: {"reports": [{"agent": "forecaster", "status": "done", "summary": "Forecast sonnet 300k tokens and opus 150k for one pass plus one reopen band; budget is Sean's to set.", "at": "2026-11-07T15:18:55+00:00"}, {"agent": "scenario", "status": "red", "summary": "Red for one-sentence-per-line picture: format, joined-words, briefs, CHANGELOG, and packet note via xv record packet", "at": "2026-11-07T15:31:17+00:00"}], "forecaster": {"at": "2026-11-07T15:18:55+00:00", "wrote": []}, "scenario": {"at": "2026-11-07T15:31:17+00:00", "protected_changed": [], "outside_tests": [], "red_fails": true, "red_output": ": test_the_picture_has_item_continuation_lines_at_all (test_picture_lines.ThePictureIsOneSentencePerLineTest.test_the_picture_has_item_continuation_lines_at_all)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/home/sean/Making/Personal/xv-agents/.xv/worktrees/2026-11-07-picture-lines/tests/test_picture_lines.py\", line 63, in test_the_picture_has_item_continuation_lines_at_all\n    self.assertTrue(any(re.match(r\"^  \\S\", line) for line in read(\".xv\", \"picture.md\").splitlines()))\n    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError: False is not true\n\n----------------------------------------------------------------------\nRan 18 tests in 1.280s\n\nFAILED (failures=9)\n", "old_red_changed": [], "red_gaps": [], "covers_kept": [{"item": "1", "test": ["test_no_picture_line_holds_more_than_one_sentence", "test_a_list_items_extra_lines_are_indented_two_spaces", "test_the_picture_has_item_continuation_lines_at_all"]}, {"item": "2", "test": ["test_joined_again_the_picture_says_the_same_words_as_at_the_base"]}, {"item": "3", "test": ["test_the_guardian_brief_states_it", "test_the_maker_brief_states_it", "test_the_watch_brief_states_it", "test_the_xv_init_brief_states_it_so_an_adopting_repo_gets_it"]}, {"item": "4", "test": ["test_xv_check_finds_the_same_in_the_new_picture_as_in_the_old", "test_xv_check_sees_a_relaxing_sentence_on_its_own_line_as_in_a_wrapped_paragraph"]}, {"item": "5", "test": ["test_an_unreleased_line_names_one_sentence_per_line_in_the_picture"]}, {"item": "6", "test": ["test_a_line_with_two_sentences_is_named_in_the_packet_by_its_line_number", "test_it_is_a_note_and_not_a_stop", "test_a_picture_with_one_sentence_per_line_gets_no_note", "test_a_full_stop_inside_backticks_does_not_count", "test_a_full_stop_not_followed_by_a_capital_does_not_count", "test_a_full_stop_with_no_space_after_it_does_not_count", "test_a_list_item_line_with_two_sentences_is_named"]}], "unreadable": [], "not_covered": [], "missed_points": []}}
old_tests_forced: []
may_not_files: [{"file": ".xv/picture.md", "why": "the red needs the picture rewrapped to one sentence per line, list-item lines indented two spaces, with the same words"}]
---
# One sentence per line in the picture

## Scenario

1. Each sentence in `.xv/picture.md` starts on its own line. The extra lines of a list item are indented two spaces, so they stay in the item.
2. When the lines are joined again, the picture's text is the same as before, word for word. A check shows this.
3. The briefs that write the picture (guardian, maker, watch, `xv-init`) state the rule: one sentence per line, and list-item lines indented two spaces. A repo that adopts xv gets the rule too.
4. `xv-check` finds the same things in the new picture as it did before.
5. A `CHANGELOG.md` line names the rule.
6. When a step leaves a picture line that holds more than one sentence, the packet gets a note naming the line. It is a note, not a stop. A sentence end counts only outside backticks, and only as a full stop and a space followed by a capital letter.

## May ignore

The other .xv files (learnings.md, rules.md, estimation.md) stay as they are. Pictures in other repos that already use xv. Retro candidate 1 (when picture edits happen at rebase); decide it after a few rebases on the new picture.

## Recording

None. A feature starts from words.

## Log
- 2026-11-07T15:18:16+00:00 watch: slice opened by Sean Kennedy
- 2026-11-07T15:18:55+00:00 forecaster: done: Forecast sonnet 300k tokens and opus 150k for one pass plus one reopen band; budget is Sean's to set.
- 2026-11-07T15:18:55+00:00 watch: stop (budget_not_set) for originator: Sean Kennedy: set the budget from the forecast (`xv record set 2026-11-07-picture-lines budget ... --by <name>`).
- 2026-11-07T15:19:01+00:00 watch: offered 2 options for budget_not_set
- 2026-11-07T15:29:31+00:00 Sean Kennedy: set budget
- 2026-11-07T15:29:31+00:00 Sean Kennedy: answered budget_not_set: use the forecast
- 2026-11-07T15:29:31+00:00 watch: scribe: wrote settled, new_info, cause for budget_not_set as the scribe of Sean Kennedy
- 2026-11-07T15:31:17+00:00 scenario: red: Red for one-sentence-per-line picture: format, joined-words, briefs, CHANGELOG, and packet note via xv record packet
- 2026-11-07T15:31:17+00:00 watch: slice-only mark on test_an_unreleased_line_names_one_sentence_per_line_in_the_picture accepted: it checks CHANGELOG.md, which the config lists in tests.slice_only_files
- 2026-11-07T15:31:18+00:00 watch: stop (slice_only_marks) for originator: Sean Kennedy: the scenario agent marked 1 test(s) slice-only, so the cleaner may remove them and they do not join the wall: test_joined_again_the_picture_says_the_same_words_as_at_the_base in tests/test_picture_lines.py (one-time check of the rewrap against the picture at the slice's base). Accept the marks, or unmark a test so it joins the wall and the cleaner keeps it.

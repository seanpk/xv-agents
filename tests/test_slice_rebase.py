import json
import os
import re
import sys
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")
ORDERS = os.path.join(HOME, "scripts", "orders.py")


def rev(repo, ref="HEAD"):
    return sh(["git", "rev-parse", ref], repo).stdout.strip()


def subject(repo, ref):
    return sh(["git", "log", "-1", "--format=%s", ref], repo).stdout.strip()


class SliceRebaseTest(RepoCase):
    """`xv slice rebase <id> [--onto <ref>]`, with the stand-in agent as the maker."""

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        self.write(self.repo, "CHANGELOG.md", "# Changelog\n\n## Unreleased\n\n- the base line\n")
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "fake agents and a changelog"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "budget"], self.wt)
        self.log = os.path.join(self.tmp, "prompts.log")
        patch = mock.patch.dict(os.environ, {"FAKE_PROMPT_LOG": self.log})
        patch.start()
        self.addCleanup(patch.stop)

    # -- helpers

    def write(self, root, rel, text, mode="w"):
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode) as f:
            f.write(text)

    def read(self, root, rel):
        with open(os.path.join(root, rel)) as f:
            return f.read()

    def on_slice(self, rel, text, msg="slice change", mode="w"):
        self.write(self.wt, rel, text, mode)
        sh(["git", "add", rel], self.wt)
        sh(["git", "commit", "-qm", msg], self.wt)
        return rev(self.wt)

    def on_main(self, rel, text, msg="main change", mode="w"):
        self.write(self.repo, rel, text, mode)
        sh(["git", "add", rel], self.repo)
        sh(["git", "commit", "-qm", msg], self.repo)
        return rev(self.repo)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def set_field(self, key, value):
        path = os.path.join(self.wt, ".xv", "slices", "s1.md")
        text = open(path).read()
        line = f"{key}: {json.dumps(value)}"
        if re.search(rf"^{key}: .*$", text, re.M):
            text = re.sub(rf"^{key}: .*$", lambda m: line, text, count=1, flags=re.M)
        else:
            text = re.sub(r"^(id: .*)$", lambda m: m.group(1) + "\n" + line, text, count=1, flags=re.M)
        open(path, "w").write(text)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", f"set {key}"], self.wt)

    def run_loop(self, close=False):
        """The whole loop to the merge stop, and then the close when asked."""
        p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stderr)
        if close:
            self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=self.wt)
            self.xv("close", "s1", cwd=self.wt)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "leftovers", "--allow-empty"], self.wt)

    def rebase(self, *args, **env):
        env = {"FAKE_REBASE_MODE": "clean", **env}  # the stand-in maker is told what to do only for the rebase
        with mock.patch.dict(os.environ, env):
            return self.xv("slice", "rebase", "s1", *args, cwd=self.wt, check=False)

    def assert_a_stop_for_the_originator(self, p):
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        stop = json.loads(p.stdout)["stop"]
        self.assertEqual(stop["seat"], "originator")
        # point 8: the order is decided in scripts/orders.py
        self.assertIn(f'"{stop["order"]}"', open(ORDERS).read())
        return stop

    def agent_ran(self):
        return os.path.exists(self.log)

    # -- 1, 4, 13: a clean rebase

    def test_a_clean_rebase_with_no_onto_moves_the_branch_and_the_base_to_the_default(self):
        self.run_loop()
        before = self.record()
        new = self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(sh(["git", "merge-base", "HEAD", "main"], self.wt).stdout.strip(), new)
        self.assertTrue(os.path.exists(os.path.join(self.wt, "docs.txt")))
        after = self.record()
        self.assertEqual(after["base"], new)
        self.assertNotEqual(after["base"], before["base"])
        # a clean rebase leaves the slice where it was
        self.assertEqual((after["status"], after["next"]), (before["status"], before["next"]))

    def test_onto_a_ref_moves_the_base_to_that_ref_not_to_the_merge_base_with_main(self):
        first = rev(self.repo)
        sh(["git", "branch", "pr", first], self.repo)
        sh(["git", "checkout", "-q", "pr"], self.repo)
        pr_head = self.on_main("pr.txt", "from the pull request\n", "pr commit")
        sh(["git", "checkout", "-q", "main"], self.repo)
        self.on_main("later.txt", "main moved on\n")
        p = self.rebase("--onto", "pr")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.record()["base"], pr_head)
        sh(["git", "merge-base", "--is-ancestor", pr_head, "HEAD"], self.wt)
        self.assertTrue(os.path.exists(os.path.join(self.wt, "pr.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.wt, "later.txt")))

    # -- 12: the maker does the rebase, in a fresh context, with a rebase part in its brief

    def test_the_maker_is_run_for_the_rebase_with_a_rebase_part_in_its_brief(self):
        self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        prompts = open(self.log).read().split("=====\n")[:-1]
        self.assertEqual(len(prompts), 1)
        self.assertTrue(prompts[0].startswith("# The maker"))
        self.assertIn("rebase", prompts[0].lower())
        self.assertEqual(self.record()["spend"][-1]["step"], "maker")

    # -- 2, 9, 8: conflicts only a person resolves

    def test_a_conflict_in_a_test_file_stops_for_the_person_and_the_agent_does_not_resolve_it(self):
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="tests/test_shared.py")
        self.assert_a_stop_for_the_originator(p)
        self.assertFalse(self.agent_ran())

    def test_a_conflict_in_the_picture_stops_for_the_person_and_the_agent_does_not_resolve_it(self):
        self.on_slice(".xv/picture.md", "\nthe slice's line\n", "slice edits the picture", "a")
        self.on_main(".xv/picture.md", "\nmain's line\n", "main edits the picture", "a")
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE=".xv/picture.md")
        self.assert_a_stop_for_the_originator(p)
        self.assertFalse(self.agent_ran())

    # -- 3: both sides kept

    def test_a_changelog_conflict_keeps_both_sides(self):
        self.on_slice("CHANGELOG.md", "- the slice's line\n", "slice changelog", "a")
        self.on_main("CHANGELOG.md", "- main's line\n", "main changelog", "a")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        text = self.read(self.wt, "CHANGELOG.md")
        for want in ("the base line", "the slice's line", "main's line"):
            self.assertIn(want, text)
        self.assertNotIn("<<<<<<<", text)
        self.assertNotIn(">>>>>>>", text)

    def test_an_estimation_conflict_keeps_both_sides(self):
        self.on_slice(".xv/estimation.md", "| slice-row | 1 |\n", "slice row", "a")
        self.on_main(".xv/estimation.md", "| main-row | 2 |\n", "main row", "a")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        text = self.read(self.wt, ".xv/estimation.md")
        self.assertIn("slice-row", text)
        self.assertIn("main-row", text)
        self.assertNotIn("<<<<<<<", text)
        self.assertNotIn(">>>>>>>", text)

    # -- 11, 13: the maker resolves other conflicts and fixes logical ones

    def test_a_conflict_in_another_file_is_resolved_by_the_maker_and_goes_to_the_cleaner(self):
        self.on_slice("pantry/shared.py", "SLICE = 1\n", "slice adds shared")
        self.on_main("pantry/shared.py", "MAIN = 2\n", "main adds shared")
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.read(self.wt, "pantry/shared.py"), "RESOLVED = True\n")
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")
        self.assertIn("pantry/shared.py", open(self.log).read())  # the brief names the conflicted file
        data = self.record()
        self.assertEqual(data["next"], "cleaner")
        self.assertNotEqual(data["status"], "closed")
        # each conflict is reported in the record
        self.assertIn("pantry/shared.py", open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read().split("## Log")[1])

    def test_a_logical_fix_with_no_git_conflict_goes_to_the_cleaner(self):
        self.on_main("docs.txt", "news\n")
        p = self.rebase(FAKE_REBASE_MODE="logical", FAKE_REBASE_FILE="pantry/store.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("# adjusted to the new base", self.read(self.wt, "pantry/store.py"))
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")
        self.assertEqual(self.record()["next"], "cleaner")

    def test_a_problem_the_maker_cannot_fix_stops_for_the_person(self):
        self.on_main("docs.txt", "news\n")
        p = self.rebase(FAKE_REBASE_MODE="stuck")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("UNFIXABLE-MARK", stop["question"])

    # -- 10: a closed slice

    def test_a_clean_rebase_leaves_a_closed_slice_closed_with_its_base_moved(self):
        self.run_loop(close=True)
        new = self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertEqual((data["status"], data["next"], data["base"]), ("closed", "none", new))

    def test_a_closed_slice_opens_again_when_the_maker_resolved_a_conflict(self):
        self.run_loop(close=True)
        self.on_slice("pantry/shared.py", "SLICE = 1\n", "slice adds shared")
        self.on_main("pantry/shared.py", "MAIN = 2\n", "main adds shared")
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertNotEqual(data["status"], "closed")
        self.assertEqual(data["next"], "cleaner")

    # -- 5: the commits the record names

    def test_the_commits_the_record_names_move_with_the_rebase(self):
        pre = self.on_slice("pantry/extra.py", "X = 1\n", "slice extra")
        cleaned = self.on_slice("pantry/more.py", "Y = 1\n", "slice more")
        self.set_field("pre_maker_commit", pre)
        self.set_field("cleaner_commit", cleaned)
        new = self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertEqual(data["base"], new)
        for key, old, name in (("pre_maker_commit", pre, "slice extra"), ("cleaner_commit", cleaned, "slice more")):
            self.assertNotEqual(data[key], old)
            self.assertEqual(subject(self.wt, data[key]), name)
            sh(["git", "merge-base", "--is-ancestor", new, data[key]], self.wt)
            sh(["git", "merge-base", "--is-ancestor", data[key], "HEAD"], self.wt)

    def test_a_commit_the_record_names_that_the_rebase_drops_stops_for_the_person(self):
        dropped = self.on_slice("pantry/extra.py", "X = 1\n", "slice extra")
        self.set_field("cleaner_commit", dropped)
        self.on_main("pantry/extra.py", "X = 1\n", "main already has it")  # git drops the slice's copy
        p = self.rebase()
        self.assert_a_stop_for_the_originator(p)

    # -- 6: the wall

    def test_the_wall_is_hashed_again_for_untouched_test_files_and_the_moves_are_kept(self):
        self.run_loop()
        move = [{"file": "tests/test_store.py", "assertion": "was: ['yogurt']; now: ['yogurt'] or []", "why": "a stand-in"}]
        self.set_field("moved_tests", move)
        before = self.record()["wall_baseline"]
        self.on_main("tests/test_other.py", "import unittest\n\n\nclass Other(unittest.TestCase):\n"
                     "    def test_ok(self):\n        self.assertTrue(True)\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        self.assertEqual(data["wall_baseline"]["count"], before["count"] + 1)
        self.assertNotEqual(data["wall_baseline"]["digest"], before["digest"])
        self.assertEqual(data["moved_tests"], move)

    # -- 7: the suite

    def test_a_red_suite_after_the_rebase_stops_for_the_person(self):
        self.on_main("tests/test_broken.py", "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                     "    def test_broken_on_main(self):\n        self.assertEqual(1, 2)\n")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("test_broken", stop["question"])

    # -- 14: a stop leaves the rebase in progress; --continue finishes it, --abort gives it up

    def in_progress(self):
        return os.path.isdir(sh(["git", "rev-parse", "--path-format=absolute", "--git-path", "rebase-merge"],
                                self.wt).stdout.strip())

    def conflict_in_a_test_file(self):
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.new = self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        return self.rebase()

    def resolve_by_hand(self):
        self.write(self.wt, "tests/test_shared.py", "A = 1\nB = 2\n")
        sh(["git", "add", "tests/test_shared.py"], self.wt)

    def test_a_stop_leaves_the_rebase_in_progress_in_the_slice_worktree(self):
        p = self.conflict_in_a_test_file()
        self.assert_a_stop_for_the_originator(p)
        self.assertTrue(self.in_progress())
        self.assertIn("<<<<<<<", self.read(self.wt, "tests/test_shared.py"))

    def test_continue_finishes_the_rebase_after_the_person_resolved_the_files(self):
        self.conflict_in_a_test_file()
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assertEqual(sh(["git", "merge-base", "HEAD", "main"], self.wt).stdout.strip(), self.new)
        self.assertEqual(self.read(self.wt, "tests/test_shared.py"), "A = 1\nB = 2\n")
        self.assertEqual(self.record()["base"], self.new)

    def test_continue_hashes_the_wall_again_and_runs_the_suite(self):
        self.run_loop()
        before = self.record()["wall_baseline"]
        self.conflict_in_a_test_file()
        self.resolve_by_hand()
        self.write(self.wt, "tests/test_broken.py", "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                   "    def test_broken_after_resolving(self):\n        self.assertEqual(1, 2)\n")
        sh(["git", "add", "tests/test_broken.py"], self.wt)
        p = self.rebase("--continue")
        stop = self.assert_a_stop_for_the_originator(p)  # a red suite stops the slice
        self.assertIn("test_broken", stop["question"])
        self.assertNotEqual(self.record()["wall_baseline"]["digest"], before["digest"])

    def test_continue_after_a_resolved_conflict_in_the_picture_moves_the_record(self):
        self.on_slice(".xv/picture.md", "\nthe slice's line\n", "slice edits the picture", "a")
        new = self.on_main(".xv/picture.md", "\nmain's line\n", "main edits the picture", "a")
        self.assert_a_stop_for_the_originator(self.rebase())
        self.write(self.wt, ".xv/picture.md", "\nthe slice's line\nmain's line\n")
        sh(["git", "add", ".xv/picture.md"], self.wt)
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.record()["base"], new)
        self.assertFalse(self.in_progress())

    def test_abort_puts_the_branch_and_the_record_back_as_they_were(self):
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        head, rec = rev(self.wt), open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read()
        self.rebase()
        self.assertTrue(self.in_progress())
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assertEqual(rev(self.wt), head)
        self.assertEqual(sh(["git", "branch", "--show-current"], self.wt).stdout.strip(), "xv/s1")
        self.assertEqual(open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read(), rec)
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")

    def test_continue_with_no_rebase_in_progress_is_refused_and_says_so(self):
        p = self.rebase("--continue")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("in progress", (p.stdout + p.stderr).lower())

    def test_abort_with_no_rebase_in_progress_is_refused_and_says_so(self):
        before = rev(self.wt)
        p = self.rebase("--abort")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("in progress", (p.stdout + p.stderr).lower())
        self.assertEqual(rev(self.wt), before)

    # -- 16: the slice's own red may fail until the maker has made the suite green

    FAILING_RED = ("import unittest\n\n\nclass OwnRed(unittest.TestCase):\n"
                   "    def test_own_red(self):\n        self.assertEqual(1, 2)\n")

    def own_red(self, suite):
        self.on_slice("tests/test_own_red.py", self.FAILING_RED, "the slice's red")
        self.set_field("red", {"files": ["tests/test_own_red.py"],
                               "command": "cd tests && python3 -m unittest test_own_red",
                               "failure": "1 != 2", "watch_first_green": None})
        self.set_field("suite", suite)

    def test_an_open_slice_with_its_own_red_still_failing_rebases_clean(self):
        self.own_red("red")
        new = self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assertEqual(self.record()["base"], new)

    def test_the_slices_own_red_failing_after_the_maker_made_the_suite_green_stops(self):
        self.own_red("green")
        self.on_main("docs.txt", "news\n")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("test_own_red", stop["question"])

    def test_a_failing_test_outside_the_own_red_stops_even_before_the_maker(self):
        self.own_red("red")
        self.on_main("tests/test_broken.py", "import unittest\n\n\nclass Broken(unittest.TestCase):\n"
                     "    def test_broken_on_main(self):\n        self.assertEqual(1, 2)\n")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("test_broken", stop["question"])

    # -- 5: a dropped named commit still stops when the rebase went through another stop first

    def test_a_dropped_commit_stops_after_continue_from_a_conflict_stop(self):
        dropped = self.on_slice("pantry/extra.py", "X = 1\n", "slice extra")
        self.set_field("cleaner_commit", dropped)
        self.on_main("pantry/extra.py", "X = 1\n", "main already has it")
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        self.assert_a_stop_for_the_originator(self.rebase())
        self.assertTrue(self.in_progress())
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assert_a_stop_for_the_originator(p)

    # -- 11: the maker looks for logical breaks on --continue too

    def test_continue_runs_the_maker_to_look_for_logical_breaks(self):
        self.conflict_in_a_test_file()
        self.assertFalse(self.agent_ran())
        self.resolve_by_hand()
        p = self.rebase("--continue", FAKE_REBASE_MODE="logical", FAKE_REBASE_FILE="pantry/store.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(self.agent_ran())
        self.assertIn("# adjusted to the new base", self.read(self.wt, "pantry/store.py"))
        self.assertEqual(self.record()["next"], "cleaner")

    def test_continue_stops_when_the_maker_cannot_fix_a_problem(self):
        self.conflict_in_a_test_file()
        self.resolve_by_hand()
        p = self.rebase("--continue", FAKE_REBASE_MODE="stuck")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("UNFIXABLE-MARK", stop["question"])

    # -- 6: hashing the wall again keeps the slice's own deletions and additions

    def test_the_wall_still_shows_the_slices_own_deleted_and_added_test_files(self):
        self.run_loop()
        sh(["git", "rm", "-q", "tests/test_red.py"], self.wt)
        sh(["git", "commit", "-qm", "slice deletes its red"], self.wt)
        self.on_slice("tests/test_late.py", "import unittest\n\n\nclass Late(unittest.TestCase):\n"
                      "    def test_ok(self):\n        self.assertTrue(True)\n", "slice adds a test after the baseline")
        self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        res = json.loads(self.xv("wall", "check", "s1", "--json", cwd=self.wt, check=False).stdout)
        self.assertEqual(res["deleted"], ["tests/test_red.py"])
        self.assertEqual(res["added"], ["tests/test_late.py"])

    # -- 16: only the tests the slice added are excused, matched by whole name

    def slice_adds_a_failing_test_to_an_old_file(self):
        """tests/test_store.py is old; the slice's red adds one failing test to it."""
        text = self.read(self.wt, "tests/test_store.py").replace(
            "\n\nif __name__", "\n    def test_slice_added_red(self):\n        self.assertEqual(1, 2)\n\n\nif __name__")
        self.on_slice("tests/test_store.py", text, "the slice adds a red test to an old file")
        self.set_field("red", {"files": ["tests/test_store.py"], "command": "cd tests && python3 -m unittest test_store",
                               "failure": "1 != 2", "watch_first_green": None})
        self.set_field("suite", "red")

    def test_a_test_the_slice_added_to_an_old_red_file_is_excused_before_the_maker(self):
        self.slice_adds_a_failing_test_to_an_old_file()
        self.on_main("docs.txt", "news\n")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_an_old_test_in_a_red_file_that_the_new_base_breaks_still_stops(self):
        self.slice_adds_a_failing_test_to_an_old_file()
        old = self.read(self.repo, "tests/test_store.py")
        self.on_main("tests/test_store.py", old.replace('["beans", "rice"]', '["rice", "beans"]'), "main breaks an old test")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("test_add_and_list", stop["question"])

    def test_a_test_whose_name_only_contains_a_red_files_name_still_stops(self):
        self.on_slice("tests/test_run.py", "import unittest\n\n\nclass Own(unittest.TestCase):\n"
                      "    def test_run(self):\n        self.assertEqual(1, 2)\n", "the slice's red")
        self.set_field("red", {"files": ["tests/test_run.py"], "command": "cd tests && python3 -m unittest test_run",
                               "failure": "1 != 2", "watch_first_green": None})
        self.set_field("suite", "red")
        self.on_main("tests/test_other.py", "import unittest\n\n\nclass Other(unittest.TestCase):\n"
                     "    def test_run_loop_x(self):\n        self.assertEqual(1, 2)\n")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertIn("test_run_loop_x", stop["question"])

    # -- 6: a test file the slice and the new base both changed still shows the slice's change

    QTY = "self.assertEqual(self.store.items()[0].qty, 4)"

    def slice_weakens_an_old_test(self):
        self.xv("wall", "baseline", "s1", cwd=self.wt)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "wall baseline"], self.wt)
        text = self.read(self.wt, "tests/test_store.py")
        self.on_slice("tests/test_store.py", text.replace(self.QTY, self.QTY[:-1] + " or 1)"), "slice weakens an old test")

    def wall_diff(self):
        return json.loads(self.xv("wall", "diff", "s1", "--json", cwd=self.wt, check=False).stdout)

    def test_a_test_file_both_sides_changed_cleanly_still_shows_the_slices_change_in_the_wall(self):
        self.slice_weakens_an_old_test()
        text = self.read(self.repo, "tests/test_store.py")
        self.on_main("tests/test_store.py", "# a note from main\n" + text, "main edits the same file elsewhere")
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("4 or 1", self.read(self.wt, "tests/test_store.py"))
        self.assertIn("tests/test_store.py", self.wall_diff()["changed"])

    def test_a_test_file_resolved_by_hand_after_a_conflict_still_shows_the_slices_change_in_the_wall(self):
        self.slice_weakens_an_old_test()
        text = self.read(self.repo, "tests/test_store.py")
        self.on_main("tests/test_store.py", text.replace(self.QTY, self.QTY + "  # main"), "main edits the same line")
        self.assert_a_stop_for_the_originator(self.rebase())
        self.write(self.wt, "tests/test_store.py", text.replace(self.QTY, self.QTY[:-1] + " or 1)  # main"))
        sh(["git", "add", "tests/test_store.py"], self.wt)
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("tests/test_store.py", self.wall_diff()["changed"])

    # -- 15: with no --onto the default comes from resolve_base, so worktrees.base comes first

    def test_with_no_onto_the_configured_worktrees_base_is_the_default(self):
        trunk = rev(self.repo)
        sh(["git", "branch", "trunk", trunk], self.repo)
        self.on_main("later.txt", "main moved on\n")
        for root in (self.repo, self.wt):
            cfg = os.path.join(root, ".xv", "config.yml")
            text = open(cfg).read().replace("worktrees: .xv/worktrees\n", "worktrees:\n  base: trunk\n")
            open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "worktrees base"], self.wt)
        p = self.rebase()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.wt, "later.txt")))
        self.assertEqual(self.record()["base"], trunk)
    # -- 17: every file the maker changed is staged; a test file or the picture goes to the person

    def shared_conflict(self):
        self.on_slice("pantry/shared.py", "SLICE = 1\n", "slice adds shared")
        self.on_main("pantry/shared.py", "MAIN = 2\n", "main adds shared")

    def test_a_fix_the_maker_makes_outside_the_conflicted_files_is_kept_in_the_rebase(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="resolve_and_edit", FAKE_REBASE_FILE="pantry/shared.py",
                        FAKE_REBASE_FILE2="pantry/store.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.read(self.wt, "pantry/shared.py"), "RESOLVED = True\n")
        self.assertIn("# adjusted to the new base", self.read(self.wt, "pantry/store.py"))
        self.assertFalse(self.in_progress())
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")
        self.assertEqual(self.record()["next"], "cleaner")

    def test_a_test_file_the_maker_changed_while_resolving_stops_with_rebase_conflict(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="resolve_and_edit", FAKE_REBASE_FILE="pantry/shared.py",
                        FAKE_REBASE_FILE2="tests/test_store.py")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "rebase_conflict")
        self.assertIn("tests/test_store.py", stop["question"])

    def test_the_picture_the_maker_changed_while_resolving_stops_with_rebase_conflict(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="resolve_and_edit", FAKE_REBASE_FILE="pantry/shared.py",
                        FAKE_REBASE_FILE2=".xv/picture.md")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "rebase_conflict")
        self.assertIn(".xv/picture.md", stop["question"])

    # -- 18: a rebase stop is written to the record, so the person's answer can be recorded

    def test_a_rebase_stop_for_a_conflict_is_written_to_the_record(self):
        self.assert_a_stop_for_the_originator(self.conflict_in_a_test_file())
        data = self.record()
        stop = data["stops"][-1]
        self.assertEqual((stop["order"], stop["seat"], stop["answer"]), ("rebase_conflict", "originator", None))
        self.assertIn("tests/test_shared.py", stop["question"])
        self.assertEqual(data["status"], "stopped")

    def test_a_rebase_stop_for_a_problem_the_maker_could_not_fix_is_written_to_the_record(self):
        self.on_main("docs.txt", "news\n")
        self.assert_a_stop_for_the_originator(self.rebase(FAKE_REBASE_MODE="stuck"))
        data = self.record()
        stop = data["stops"][-1]
        self.assertEqual((stop["order"], stop["answer"]), ("rebase_stuck", None))
        self.assertIn("UNFIXABLE-MARK", stop["question"])
        self.assertEqual(data["status"], "stopped")

    # -- 19: the budget is checked before the rebase maker runs

    def spend_the_budget(self):
        self.set_field("spend", [{"harness": "sh", "model": "default", "tokens": 10, "usd": 2.0, "turns": 1,
                                  "step": "maker", "at": "2026-11-05T00:00:00+00:00", "exit": 0}])

    def test_a_spent_budget_stops_with_budget_spent_before_the_rebase_maker_starts(self):
        self.spend_the_budget()
        self.on_main("docs.txt", "news\n")
        p = self.rebase()
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "budget_spent")
        self.assertFalse(self.agent_ran())
        self.assertEqual(self.record()["stops"][-1]["order"], "budget_spent")

    def test_a_spent_budget_stops_the_maker_on_a_conflict_in_another_file_too(self):
        self.spend_the_budget()
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "budget_spent")
        self.assertFalse(self.agent_ran())

    def test_a_budget_spent_after_the_conflicting_commit_still_stops_before_the_maker(self):
        # the record is replayed with the slice's commits: the conflicting commit holds an older copy
        self.shared_conflict()
        self.spend_the_budget()
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "budget_spent")
        self.assertFalse(self.agent_ran())

    # -- 18 again: the stop and the person's answer survive --continue

    def stops_of(self, order):
        return [s for s in self.record()["stops"] if s["order"] == order]

    def answer_resolve_and_continue(self, order, **env):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "I will sort it out", cwd=self.wt)
        self.write(self.wt, "pantry/shared.py", "SLICE = 1\nMAIN = 2\n")
        sh(["git", "add", "pantry/shared.py"], self.wt)
        self.rebase("--continue", **env)
        stops = self.stops_of(order)
        self.assertEqual(len(stops), 1, self.record()["stops"])
        return stops[0]

    def test_the_answer_to_a_conflict_stop_is_on_the_finished_record(self):
        self.assert_a_stop_for_the_originator(self.conflict_in_a_test_file())
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "I will sort it out", cwd=self.wt)
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        stops = self.stops_of("rebase_conflict")
        self.assertEqual(len(stops), 1, self.record()["stops"])
        self.assertEqual(stops[0]["answer"], "I will sort it out")

    def test_the_answer_to_a_stuck_stop_raised_mid_rebase_is_on_the_finished_record(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="stuck")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "rebase_stuck")
        self.assertTrue(self.in_progress())
        done = self.answer_resolve_and_continue("rebase_stuck")
        self.assertEqual(done["answer"], "I will sort it out")

    def test_the_answer_to_a_budget_stop_raised_on_a_conflict_replay_is_on_the_finished_record(self):
        self.shared_conflict()
        self.spend_the_budget()
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(self.assert_a_stop_for_the_originator(p)["order"], "budget_spent")
        self.assertTrue(self.in_progress())
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "I will sort it out", cwd=self.wt)
        self.write(self.wt, "pantry/shared.py", "SLICE = 1\nMAIN = 2\n")
        sh(["git", "add", "pantry/shared.py"], self.wt)
        self.rebase("--continue")
        stops = self.stops_of("budget_spent")
        self.assertEqual(stops[0]["answer"], "I will sort it out", self.record()["stops"])

    # -- 20: --abort keeps the spend of the maker runs in that rebase

    def test_abort_keeps_the_spend_of_the_maker_runs_of_that_rebase(self):
        self.on_slice("pantry/shared.py", "SLICE = 1\n", "slice adds shared")
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("pantry/shared.py", "MAIN = 2\n", "main adds shared")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        head = rev(self.wt)
        before = self.record()["spend"]
        # the maker resolves the first conflict; the second one, in a test file, stops for the person
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "rebase_conflict")
        self.assertTrue(self.agent_ran())
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(rev(self.wt), head)
        after = self.record()["spend"]
        self.assertEqual(after[:len(before)], before)
        self.assertEqual([s["step"] for s in after[len(before):]], ["maker"])

    # -- 19 again: a budget raised during the rebase is the one the --continue check reads

    def test_a_budget_raised_during_the_rebase_is_the_one_continue_checks(self):
        self.shared_conflict()
        self.spend_the_budget()
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(self.assert_a_stop_for_the_originator(p)["order"], "budget_spent")
        self.assertFalse(self.agent_ran())
        self.xv("record", "set", "s1", "budget", '{"usd": 10}', "--by", "pat", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "raised it", cwd=self.wt)
        self.write(self.wt, "pantry/shared.py", "SLICE = 1\nMAIN = 2\n")
        sh(["git", "add", "pantry/shared.py"], self.wt)
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(self.agent_ran())
        data = self.record()
        self.assertEqual(data["budget"]["usd"], 10)
        self.assertEqual(len(self.stops_of("budget_spent")), 1, data["stops"])

    # -- 14 again: --abort drops the aborted rebase's unanswered stops

    def test_abort_drops_the_unanswered_stops_the_rebase_raised(self):
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        before = self.record()
        self.assert_a_stop_for_the_originator(self.rebase())
        self.assertIsNone(self.stops_of("rebase_conflict")[-1]["answer"])
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        after = self.record()
        self.assertEqual(self.stops_of("rebase_conflict"), [], after["stops"])
        self.assertEqual(after["stops"], before["stops"])
        self.assertEqual(after["status"], before["status"])

    def test_abort_after_a_maker_run_drops_the_unanswered_stop_and_keeps_the_spend(self):
        self.on_slice("pantry/shared.py", "SLICE = 1\n", "slice adds shared")
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.on_main("pantry/shared.py", "MAIN = 2\n", "main adds shared")
        self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        before = self.record()
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(self.assert_a_stop_for_the_originator(p)["order"], "rebase_conflict")
        self.assertEqual(self.rebase("--abort").returncode, 0)
        after = self.record()
        self.assertEqual(self.stops_of("rebase_conflict"), [], after["stops"])
        self.assertEqual(after["stops"], before["stops"])
        self.assertEqual(after["status"], before["status"])
        self.assertEqual(len(after["spend"]), len(before["spend"]) + 1)

    # -- 21: during a rebase the record that counts is the one saved before it began

    def test_a_later_larger_budget_is_the_one_continue_checks_after_a_stop_in_an_early_commit(self):
        # the commit that conflicts holds budget $1 and $2 spent; the last commit holds budget $10
        self.spend_the_budget()
        self.conflict_in_a_test_file_commit()
        self.set_field("budget", {"usd": 10})
        self.assert_a_stop_for_the_originator(self.rebase())
        self.assertFalse(self.agent_ran())
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(self.agent_ran())
        data = self.record()
        self.assertEqual(data["budget"]["usd"], 10)
        self.assertEqual(self.stops_of("budget_spent"), [], data["stops"])

    def test_a_later_smaller_budget_is_the_one_continue_checks_after_a_stop_in_an_early_commit(self):
        # the commit that conflicts holds budget $10 and $2 spent; the last commit holds budget $1
        self.set_field("budget", {"usd": 10})
        self.spend_the_budget()
        self.conflict_in_a_test_file_commit()
        self.set_field("budget", {"usd": 1})
        self.assert_a_stop_for_the_originator(self.rebase())
        self.resolve_by_hand()
        p = self.rebase("--continue")
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertEqual(stop["order"], "budget_spent")
        self.assertFalse(self.agent_ran())
        self.assertEqual(self.record()["budget"]["usd"], 1)

    def conflict_in_a_test_file_commit(self):
        self.on_slice("tests/test_shared.py", "A = 1\n", "slice adds a test")
        self.new = self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")

    def test_a_budget_set_during_the_stop_is_kept_by_abort(self):
        self.spend_the_budget()
        self.conflict_in_a_test_file_commit()
        self.assert_a_stop_for_the_originator(self.rebase())
        self.xv("record", "set", "s1", "budget", '{"usd": 10}', "--by", "pat", cwd=self.wt)
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assertEqual(self.record()["budget"]["usd"], 10)

    def test_continue_keeps_the_record_change_of_the_commit_it_stopped_on(self):
        # the commit that conflicts also changes the record; the next commit changes the same line again
        self.write(self.wt, "tests/test_shared.py", "A = 1\n")
        sh(["git", "add", "tests/test_shared.py"], self.wt)
        self.set_field("note", "a")  # commits the staged test file with the record change
        self.set_field("note", "b")
        self.new = self.on_main("tests/test_shared.py", "B = 2\n", "main adds a test")
        self.assert_a_stop_for_the_originator(self.rebase())
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assertEqual(self.record()["note"], "b")
        self.assertEqual(self.record()["base"], self.new)

    def test_the_rebase_makers_brief_reads_the_saved_record_not_the_one_git_replays(self):
        # the commit that conflicts names no red; the last commit names one
        self.shared_conflict()
        self.set_field("red", {"files": ["tests/test_late_mark.py"], "command": "python3 -m unittest tests.test_late_mark"})
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(self.agent_ran())
        self.assertIn("tests.test_late_mark", open(self.log).read())

    # -- record-state 5: the rebase maker's brief reads the record of truth, with the answers given during the rebase

    def test_the_rebase_makers_brief_includes_the_answer_given_at_a_rebase_stop(self):
        self.assert_a_stop_for_the_originator(self.conflict_in_a_test_file())
        self.assertFalse(self.agent_ran())
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "ANSWER-MARK-138: keep both lines", cwd=self.wt)
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(self.agent_ran())
        self.assertIn("ANSWER-MARK-138", open(self.log).read())

    # -- record-state 6 and 9: on a replay with no conflict, a maker edit to a test file or the picture stops

    def assert_the_makers_edit_stops_with_rebase_conflict(self, rel):
        self.on_main("docs.txt", "news\n")
        p = self.rebase(FAKE_REBASE_MODE="logical", FAKE_REBASE_FILE=rel)
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertTrue(self.agent_ran())
        self.assertEqual(stop["order"], "rebase_conflict")
        self.assertIn(rel, stop["question"])
        # point 9: the question names the maker's edit, not a conflict
        self.assertIn("maker", stop["question"].lower())
        self.assertNotIn("stopped on a conflict", stop["question"])

    def test_a_test_file_the_maker_changed_on_a_replay_with_no_conflict_stops_with_rebase_conflict(self):
        self.assert_the_makers_edit_stops_with_rebase_conflict("tests/test_store.py")

    def test_the_picture_the_maker_changed_on_a_replay_with_no_conflict_stops_with_rebase_conflict(self):
        self.assert_the_makers_edit_stops_with_rebase_conflict(".xv/picture.md")

    # -- record-state 7: after an error mid-rebase, --continue and --abort read the record of truth

    def maker_cli_missing(self):
        """The slice's agent CLI is a path with nothing there yet, so the rebase maker's run is an error."""
        self.agent = os.path.join(self.tmp, "bin", "agent")
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        open(cfg, "w").write(text[:start] + f'agents:\n  default: ["{self.agent}", "{{prompt}}"]\n' + text[end:])
        sh(["git", "commit", "-qam", "an agent CLI that is not there yet"], self.wt)

    def maker_cli_back(self):
        os.makedirs(os.path.dirname(self.agent), exist_ok=True)
        with open(self.agent, "w") as f:
            f.write(f'#!/bin/sh\nexec "{sys.executable}" "{FAKE}" "$@"\n')
        os.chmod(self.agent, 0o755)

    TRUTH = {"at": "2026-11-05T01:00:00+00:00", "step": "maker", "order": "repeated_failure", "seat": "originator",
             "question": "The same tests failed twice.", "answered_by": ["pat"], "answer": "TRUTH-MARK: go on",
             "answered_at": "2026-11-05T01:05:00+00:00"}

    def error_mid_rebase(self):
        """The commit that conflicts holds budget $1 with $2 spent and no stop; the record of truth holds
        budget $10 and an answered stop. The maker's run fails on the conflict, mid-rebase."""
        self.maker_cli_missing()
        self.spend_the_budget()
        self.shared_conflict()
        self.set_field("budget", {"usd": 10})
        self.set_field("stops", [self.TRUTH])
        p = self.rebase(FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertTrue(self.in_progress())
        self.maker_cli_back()

    def assert_the_record_of_truth(self):
        data = self.record()
        self.assertEqual(data["budget"]["usd"], 10, data["budget"])
        self.assertIn("TRUTH-MARK: go on", [s.get("answer") for s in data["stops"]], data["stops"])

    def test_continue_after_an_error_mid_rebase_reads_the_stops_and_budget_of_the_record_of_truth(self):
        self.error_mid_rebase()
        p = self.rebase("--continue", FAKE_REBASE_MODE="resolve", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assert_the_record_of_truth()

    def test_abort_after_an_error_mid_rebase_reads_the_stops_and_budget_of_the_record_of_truth(self):
        self.error_mid_rebase()
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.in_progress())
        self.assert_the_record_of_truth()

    # -- record-state 8: the slice log keeps the stop and answer lines written mid-rebase

    def log_of_the_record(self):
        return self.read(self.wt, ".xv/slices/s1.md").split("## Log")[1]

    def stopped_and_answered(self):
        self.assert_a_stop_for_the_originator(self.conflict_in_a_test_file())
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "LOG-MARK: I will sort it out", cwd=self.wt)

    def assert_the_log_keeps_the_stop_and_the_answer(self):
        log = self.log_of_the_record()
        self.assertIn("stop (rebase_conflict) for originator", log)
        self.assertIn("answered rebase_conflict: LOG-MARK: I will sort it out", log)

    def test_the_log_keeps_the_stop_and_answer_lines_after_continue(self):
        self.stopped_and_answered()
        self.resolve_by_hand()
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assert_the_log_keeps_the_stop_and_the_answer()

    def test_the_log_keeps_the_stop_and_answer_lines_after_abort(self):
        self.stopped_and_answered()
        p = self.rebase("--abort")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assert_the_log_keeps_the_stop_and_the_answer()

    # -- record-state 9: a staged record is not committed into the replayed commit; markers are checked before staging

    def test_a_record_the_person_staged_before_continue_is_not_committed_into_the_replayed_commit(self):
        self.stopped_and_answered()
        self.resolve_by_hand()
        sh(["git", "add", "-A"], self.wt)  # the person stages everything, the record with its answer too
        p = self.rebase("--continue")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        replayed = [line.split(" ", 1)[0] for line in
                    sh(["git", "log", "--format=%H %s", f"{self.new}..HEAD"], self.wt).stdout.splitlines()
                    if line.split(" ", 1)[1] == "slice adds a test"]
        self.assertEqual(len(replayed), 1)
        files = sh(["git", "show", "--format=", "--name-only", replayed[0]], self.wt).stdout.split()
        self.assertEqual(files, ["tests/test_shared.py"])
        self.assertEqual(self.stops_of("rebase_conflict")[0]["answer"], "LOG-MARK: I will sort it out")

    def test_conflict_markers_the_maker_left_stop_the_rebase(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="clean")  # the maker runs and leaves the conflict as it is
        stop = self.assert_a_stop_for_the_originator(p)
        self.assertTrue(self.agent_ran())
        self.assertIn("conflict markers remain", stop["question"])
        self.assertIn("pantry/shared.py", stop["question"])
        self.assertTrue(self.in_progress())

    def test_a_conflict_the_maker_resolved_without_staging_it_goes_on(self):
        self.shared_conflict()
        p = self.rebase(FAKE_REBASE_MODE="resolve_unstaged", FAKE_REBASE_FILE="pantry/shared.py")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.read(self.wt, "pantry/shared.py"), "RESOLVED = True\n")
        self.assertFalse(self.in_progress())


# What a person should watch on the first green run: that a slice with a real change of its own
# is replayed on a moved base, that the record's base and named commits point at the replayed
# commits (`git log` shows them under the new base), that a conflict in CHANGELOG.md keeps both
# lines, and that a conflict in a test file or the picture stops with the rebase left for them.

if __name__ == "__main__":
    unittest.main()

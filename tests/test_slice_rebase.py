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
        patch = mock.patch.dict(os.environ, {"FAKE_PROMPT_LOG": self.log, "FAKE_REBASE_MODE": "clean"})
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
        with mock.patch.dict(os.environ, {k: v for k, v in env.items()}):
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


# What a person should watch on the first green run: that a slice with a real change of its own
# is replayed on a moved base, that the record's base and named commits point at the replayed
# commits (`git log` shows them under the new base), that a conflict in CHANGELOG.md keeps both
# lines, and that a conflict in a test file or the picture stops with the rebase left for them.

if __name__ == "__main__":
    unittest.main()

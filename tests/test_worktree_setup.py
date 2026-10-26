import json
import os
import re
import unittest

from helpers import HOME, RepoCase, sh


def head(repo, ref="HEAD"):
    return sh(["git", "rev-parse", ref], repo).stdout.strip()


class WorktreeSetupTest(RepoCase):
    """`xv slice new` starts from the right base and runs the project's setup."""

    def set_worktrees(self, block):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read().replace("worktrees: .xv/worktrees\n", block)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "worktrees block"], self.repo)

    def base_of(self, wt, sid="s1"):
        return json.loads(self.xv("record", "show", sid, "--json", cwd=wt).stdout)["base"]

    def later_commit(self):
        sh(["git", "commit", "-q", "--allow-empty", "-m", "later"], self.repo)
        return head(self.repo)

    def test_base_flag_starts_the_branch_from_that_ref(self):
        first = head(self.repo)
        self.later_commit()
        out = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", "--base", first).stdout
        wt = out.strip().splitlines()[-1]
        self.assertEqual(self.base_of(wt), first)
        self.assertEqual(head(wt, "xv/s1~1"), first)

    def test_config_base_is_used_without_the_flag(self):
        first = head(self.repo)
        self.set_worktrees(f"worktrees:\n  base: {first}\n")
        self.later_commit()
        wt = self.new_slice("s1")
        self.assertEqual(self.base_of(wt), first)

    def test_the_flag_beats_the_config(self):
        first = head(self.repo)
        self.set_worktrees(f"worktrees:\n  base: {first}\n")
        second = self.later_commit()
        out = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", "--base", second).stdout
        self.assertEqual(self.base_of(out.strip().splitlines()[-1]), second)

    def test_with_neither_the_remotes_default_branch_not_head(self):
        remote = os.path.join(self.tmp, "remote.git")
        sh(["git", "init", "-q", "--bare", "-b", "main", remote], self.tmp)
        sh(["git", "remote", "add", "origin", remote], self.repo)
        sh(["git", "push", "-q", "origin", "main"], self.repo)
        sh(["git", "remote", "set-head", "origin", "main"], self.repo)
        pushed = head(self.repo)
        self.later_commit()  # the main checkout's HEAD is ahead of origin/HEAD
        wt = self.new_slice("s1")
        self.assertEqual(self.base_of(wt), pushed)

    def test_with_no_remote_the_base_is_head(self):
        wt = self.new_slice("s1")
        self.assertEqual(self.base_of(wt), head(self.repo))

    def test_setup_runs_in_the_worktree_with_its_path_filled_in(self):
        self.set_worktrees('worktrees:\n  setup: "pwd > ../setup-ran.txt; echo {worktree} > ../setup-path.txt"\n')
        wt = self.new_slice("s1")
        ran = open(os.path.join(os.path.dirname(wt), "setup-ran.txt")).read().strip()
        path = open(os.path.join(os.path.dirname(wt), "setup-path.txt")).read().strip()
        self.assertEqual(os.path.realpath(ran), os.path.realpath(wt))
        self.assertEqual(os.path.realpath(path), os.path.realpath(wt))

    def test_setup_runs_before_the_forecaster(self):
        self.set_worktrees('worktrees:\n  setup: "touch SETUP-MARK"\n')
        wt = self.new_slice("s1")
        self.assertTrue(os.path.exists(os.path.join(wt, "SETUP-MARK")))
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["spend"], [])

    def test_a_failing_setup_is_a_stop_for_the_originator_quoting_its_last_lines(self):
        self.set_worktrees('worktrees:\n  setup: "echo first-line; echo SETUP-BOOM-4417 >&2; exit 3"\n')
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", check=False)
        wt = os.path.join(self.repo, ".xv", "worktrees", "s1")
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        self.assertEqual(len(open_stops), 1, (p.stdout, p.stderr))
        self.assertEqual(open_stops[0]["seat"], "originator")
        self.assertIn("SETUP-BOOM-4417", open_stops[0]["question"])
        self.assertEqual(data["status"], "stopped")

    def close_slice(self, wt):
        self.xv("record", "stop", "s1", "--order", "ready_to_merge", "--seat", "originator",
                "--question", "merge?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=wt)
        return self.xv("close", "s1", "--why", "test", cwd=wt, check=False)

    def test_teardown_runs_when_the_slice_closes_with_the_worktree_path(self):
        self.set_worktrees('worktrees:\n  teardown: "echo {worktree} > ../teardown-path.txt"\n')
        wt = self.new_slice("s1")
        mark = os.path.join(os.path.dirname(wt), "teardown-path.txt")
        self.assertFalse(os.path.exists(mark))
        self.close_slice(wt)
        self.assertEqual(os.path.realpath(open(mark).read().strip()), os.path.realpath(wt))

    def test_a_slice_without_a_teardown_still_closes(self):
        wt = self.new_slice("s1")
        self.close_slice(wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["status"], "closed")

    def test_check_lists_both_commands(self):
        self.set_worktrees('worktrees:\n  setup: "make deps-MARK"\n  teardown: "make clean-MARK"\n')
        out = self.xv("check").stdout
        self.assertIn("make deps-MARK", out)
        self.assertIn("make clean-MARK", out)

    def test_the_default_config_shows_the_block_commented_out(self):
        text = open(os.path.join(HOME, "defaults", "config.yml")).read()
        for key in ("base", "setup", "teardown"):
            self.assertRegex(text, rf"(?m)^#\s+{key}:")
        self.assertRegex(text, r"(?m)^#\s*worktrees:")


if __name__ == "__main__":
    unittest.main()

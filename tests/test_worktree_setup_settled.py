import json
import os
import unittest

from helpers import RepoCase, sh


class WorktreeSettledTest(RepoCase):
    """What Sean settled at the accept stop: the base guard, shell quoting, the setup time limit."""

    def edit_config(self, old, new):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        with open(cfg) as f:
            text = f.read()
        self.assertIn(old, text)
        with open(cfg, "w") as f:
            f.write(text.replace(old, new))
        sh(["git", "commit", "-qam", "config"], self.repo)

    def record(self, sid="s1"):
        wt = os.path.join(self.repo, ".xv", "worktrees", sid)
        return json.loads(self.xv("record", "show", sid, "--json", cwd=wt).stdout)

    def push_without_xv(self):
        """origin/HEAD is a commit with no .xv/; the local HEAD has it committed but not pushed."""
        remote = os.path.join(self.tmp, "remote.git")
        sh(["git", "init", "-q", "--bare", "-b", "main", remote], self.tmp)
        sh(["git", "remote", "add", "origin", remote], self.repo)
        sh(["git", "rm", "-rq", "--cached", ".xv"], self.repo)
        sh(["git", "commit", "-qm", "no layer"], self.repo)
        sh(["git", "push", "-q", "origin", "main"], self.repo)
        sh(["git", "remote", "set-head", "origin", "main"], self.repo)
        sh(["git", "add", ".xv"], self.repo)
        sh(["git", "commit", "-qm", "layer, not pushed"], self.repo)

    def test_refuses_a_base_without_the_committed_project_layer(self):
        self.push_without_xv()
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", check=False)
        self.assertNotEqual(p.returncode, 0)
        said = p.stdout + p.stderr
        self.assertIn("push", said)
        self.assertIn("--base HEAD", said)
        self.assertFalse(os.path.exists(os.path.join(self.repo, ".xv", "worktrees", "s1")))

    def test_base_head_gets_past_the_refusal(self):
        self.push_without_xv()
        out = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", "--base", "HEAD").stdout
        self.assertTrue(os.path.isdir(out.strip().splitlines()[-1]))

    def test_the_uncommitted_layer_message_no_longer_says_the_branch_starts_from_head(self):
        with open(os.path.join(self.repo, ".xv", "config.yml"), "a") as f:
            f.write("# edited\n")
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("starts from HEAD", p.stdout + p.stderr)

    def test_worktree_path_with_a_space_is_one_argument_in_setup(self):
        self.edit_config("worktrees: .xv/worktrees\n",
                         'worktrees:\n  path: ".xv/my trees"\n  setup: "printf %s {worktree} > ../setup-path.txt"\n')
        wt = self.new_slice("s1")
        self.assertIn("my trees", wt)
        with open(os.path.join(os.path.dirname(wt), "setup-path.txt")) as f:
            got = f.read().strip()
        self.assertEqual(os.path.realpath(got), os.path.realpath(wt))

    def test_worktree_path_with_a_space_is_one_argument_in_teardown(self):
        self.edit_config("worktrees: .xv/worktrees\n",
                         'worktrees:\n  path: ".xv/my trees"\n  teardown: "printf %s {worktree} > ../teardown-path.txt"\n')
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "ready_to_merge", "--seat", "originator",
                "--question", "merge?", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=wt)
        self.xv("close", "s1", "--why", "test", cwd=wt, check=False)
        with open(os.path.join(os.path.dirname(wt), "teardown-path.txt")) as f:
            got = f.read().strip()
        self.assertEqual(os.path.realpath(got), os.path.realpath(wt))

    def test_a_setup_that_outlasts_the_test_timeout_is_the_setup_failed_stop(self):
        self.edit_config("timeout: 300", "timeout: 1")
        self.edit_config("worktrees: .xv/worktrees\n", 'worktrees:\n  setup: "echo SLOW-START-9921; sleep 5"\n')
        p = self.xv("slice", "new", "s1", "--by", "pat", "--scenario", "X.", check=False)
        data = self.record()
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        self.assertEqual(len(open_stops), 1, (p.stdout, p.stderr))
        self.assertEqual(open_stops[0]["order"], "setup_failed")
        self.assertEqual(open_stops[0]["seat"], "originator")
        self.assertEqual(data["status"], "stopped")


if __name__ == "__main__":
    unittest.main()

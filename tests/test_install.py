import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from helpers import HOME, XV, RepoCase, sh

import check


def run_xv(args, cwd, home):
    env = dict(os.environ, HOME=home, PATH=os.environ["PATH"])
    env.pop("CLAUDE_CONFIG_DIR", None)
    p = subprocess.run([sys.executable, XV] + args, cwd=cwd, env=env, capture_output=True, text=True)
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("{") else p.stdout), p.stderr


class UserInstallTest(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="xv-home-")
        os.makedirs(os.path.join(self.home, ".claude"))
        os.makedirs(os.path.join(self.home, ".grok", "skills", "maker"))  # someone else's skill named maker

    def test_links_into_agents_that_exist_and_leaves_others_alone(self):
        code, res, err = run_xv(["install"], self.home, self.home)
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.islink(os.path.join(self.home, ".claude", "skills", "watch")))
        self.assertFalse(os.path.exists(os.path.join(self.home, ".codex")), "no folder for an absent agent")
        self.assertIn("exists and is not ours", " ".join(res["skipped"]))
        self.assertFalse(os.path.islink(os.path.join(self.home, ".grok", "skills", "maker")))
        self.assertTrue(os.path.islink(os.path.join(self.home, ".local", "bin", "xv")))
        code, res, _ = run_xv(["install", "--remove"], self.home, self.home)
        self.assertFalse(os.path.lexists(os.path.join(self.home, ".claude", "skills", "watch")))
        self.assertTrue(os.path.isdir(os.path.join(self.home, ".grok", "skills", "maker")))


class ProjectInstallTest(RepoCase):
    def overrides(self, home):
        # check reads this person's own skills from HOME; the test's home has none
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_CONFIG_DIR"}
        with mock.patch.dict(os.environ, dict(env, HOME=home), clear=True):
            return {o["file"]: o["kind"] for o in check.overrides(self.repo)}

    def test_copies_are_marked_replaced_when_unedited_and_kept_when_edited(self):
        home = tempfile.mkdtemp(prefix="xv-home-")
        code, res, err = run_xv(["install", "--scope", "project"], self.repo, home)
        self.assertEqual(code, 0, err)
        watch = os.path.join(self.repo, ".agents", "skills", "watch")
        self.assertTrue(os.path.exists(os.path.join(watch, ".xv-installed")))
        kinds = self.overrides(home)
        self.assertEqual(kinds[".agents/skills/watch/SKILL.md"], "installed copy, current")
        with open(os.path.join(watch, "SKILL.md"), "a") as f:
            f.write("\nlocal edit\n")
        code, res, _ = run_xv(["install", "--scope", "project"], self.repo, home)
        self.assertTrue(any("edited in this repo" in s for s in res["skipped"]))
        self.assertIn("local edit", open(os.path.join(watch, "SKILL.md")).read())
        kinds = self.overrides(home)
        self.assertTrue(kinds[".agents/skills/watch/SKILL.md"].startswith("installed copy, edited"))


class TrialTest(RepoCase):
    def setUp(self):
        super().setUp()
        import shutil
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no layer"], self.repo)

    def test_a_trial_keeps_xv_out_of_git_and_still_runs_a_slice(self):
        self.xv("init", "--trial")
        self.assertEqual(sh(["git", "status", "--porcelain"], self.repo).stdout.strip(), "")
        with open(os.path.join(self.repo, ".xv", "pitch.md"), "w") as f:
            f.write("---\nstatus: written\n---\n\n# The pitch\n\nA pantry for one household.\n")
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        fake = os.path.join(HOME, "tests", "fake_agent.py")
        text = text[:text.index("agents:")] + f'agents:\n  default: ["{sys.executable}", "{fake}", "{{prompt}}"]\n' \
            + text[text.index("# Who sits"):]
        open(cfg, "w").write(text)
        wt = self.new_slice("t1", "Milk that runs out today shows as running out soon.")
        self.assertTrue(os.path.exists(os.path.join(wt, ".xv", "config.yml")), "the layer is copied in")
        self.xv("record", "set", "t1", "budget", '{"usd": 1}', "--by", "pat", cwd=wt)
        p = self.xv("run", "t1", cwd=wt, check=False)
        self.assertEqual(json.loads(p.stdout)["stop"]["order"], "ready_to_merge", p.stderr)
        self.xv("record", "answer", "t1", "--by", "pat", "--answer", "merge", cwd=wt)
        self.xv("close", "t1", cwd=wt)
        self.assertTrue(os.path.exists(os.path.join(self.repo, ".xv", "slices", "t1.md")), "the record comes back")
        self.assertIn("| t1 |", open(os.path.join(self.repo, ".xv", "estimation.md")).read())
        log = sh(["git", "log", "--name-only", "--format=", "main..xv/t1"], wt).stdout
        self.assertNotIn(".xv/", log, "nothing of .xv/ was committed")
        self.xv("init", "--adopt")
        self.assertIn(".xv/", sh(["git", "status", "--porcelain"], self.repo).stdout)


if __name__ == "__main__":
    unittest.main()

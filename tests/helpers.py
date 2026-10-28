import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XV = os.path.join(HOME, "bin", "xv")
sys.path.insert(0, os.path.join(HOME, "scripts"))


def sh(cmd, cwd, check=True):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if check and p.returncode != 0:
        raise AssertionError(f"{cmd} failed {p.returncode}: {p.stderr}{p.stdout}")
    return p


class RepoCase(unittest.TestCase):
    """A fresh git repo with the fixture's project layer, per test."""

    fixture = True
    no_try = True  # `xv init` skips its test try; the tests that check the try set this False

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xv-test-")
        self.repo = os.path.join(self.tmp, "repo")
        if self.fixture:
            shutil.copytree(os.path.join(HOME, "evals", "fixture"), self.repo)
        else:
            os.makedirs(self.repo)
        sh(["git", "init", "-q", "-b", "main"], self.repo)
        sh(["git", "config", "user.name", "test"], self.repo)
        sh(["git", "config", "user.email", "test@example.com"], self.repo)
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "base", "--allow-empty"], self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def xv(self, *args, cwd=None, check=True):
        args = list(args)
        if self.no_try and args[:1] == ["init"] and "--no-try" not in args:
            args.append("--no-try")
        return sh([sys.executable, XV] + args, cwd or self.repo, check)

    def new_slice(self, sid="s1", scenario="The household sees X."):
        out = self.xv("slice", "new", sid, "--by", "pat", "--scenario", scenario).stdout
        return out.strip().splitlines()[-1]

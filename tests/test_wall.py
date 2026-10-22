import json
import os
import unittest

from helpers import RepoCase, sh


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


class WallTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("wall", "baseline", "s1", cwd=self.wt)

    def check(self):
        p = self.xv("wall", "check", "s1", "--json", cwd=self.wt, check=False)
        return p.returncode, json.loads(p.stdout)

    def test_no_change_holds(self):
        code, res = self.check()
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_an_unrecorded_change_fails(self):
        path = os.path.join(self.wt, "tests", "test_store.py")
        write(path, open(path).read().replace('("bread", 0)', "anything"))
        code, res = self.check()
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/test_store.py"]))
        self.assertEqual(res["fewer_assertions"], [])

    def test_a_recorded_move_holds(self):
        path = os.path.join(self.wt, "tests", "test_store.py")
        write(path, open(path).read().replace('("bread", 0)', "anything"))
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "was; now",
                "--why", "the scenario", cwd=self.wt)
        code, res = self.check()
        self.assertEqual((code, res["recorded"]), (0, ["tests/test_store.py"]))

    def test_a_deleted_test_is_a_move_and_counts_as_weaker(self):
        os.remove(os.path.join(self.wt, "tests", "test_api.py"))
        code, res = self.check()
        self.assertEqual(res["deleted"], ["tests/test_api.py"])
        self.assertIn("tests/test_api.py", res["fewer_assertions"])
        self.assertEqual(code, 1)

    def test_a_new_test_file_is_not_a_move(self):
        write(os.path.join(self.wt, "tests", "test_new.py"), "def test_x():\n    assert True\n")
        code, res = self.check()
        self.assertEqual((code, res["added"]), (0, ["tests/test_new.py"]))

    def test_the_hook_refuses_an_unrecorded_commit_on_a_slice_branch(self):
        self.xv("wall", "install-hook", cwd=self.wt)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "baseline"], self.wt)
        path = os.path.join(self.wt, "tests", "test_store.py")
        write(path, open(path).read().replace('("bread", 0)', "anything"))
        sh(["git", "add", "-A"], self.wt)
        env_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/bin:" + os.environ["PATH"]
        import subprocess
        p = subprocess.run(["git", "commit", "-qm", "sneak"], cwd=self.wt, capture_output=True, text=True,
                           env=dict(os.environ, PATH=env_path))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refuses this commit", p.stderr)


class WallAgainstBaseTest(RepoCase):
    """The CI form: compare a branch with its base."""

    def test_a_changed_test_with_no_slice_record_fails(self):
        sh(["git", "checkout", "-qb", "feature"], self.repo)
        path = os.path.join(self.repo, "tests", "test_store.py")
        write(path, open(path).read().replace('("bread", 0)', "anything"))
        sh(["git", "commit", "-qam", "change a test"], self.repo)
        p = self.xv("wall", "check", "--base", "main", "--json", check=False)
        res = json.loads(p.stdout)
        self.assertEqual((p.returncode, res["unrecorded"]), (1, ["tests/test_store.py"]))

    def test_the_red_and_a_recorded_move_pass(self):
        wt = self.new_slice("s1")
        path = os.path.join(wt, "tests", "test_api.py")
        write(path, open(path).read() + "\n# the red, added before the baseline\n")
        self.xv("record", "set", "s1", "red", json.dumps({"files": ["tests/test_api.py"], "command": "x"}), cwd=wt)
        self.xv("wall", "baseline", "s1", cwd=wt)
        path = os.path.join(wt, "tests", "test_store.py")
        write(path, open(path).read().replace('("bread", 0)', "anything"))
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "a", "--why", "b", cwd=wt)
        sh(["git", "add", "-A"], wt)
        sh(["git", "commit", "-qm", "work"], wt)
        p = self.xv("wall", "check", "--base", "main", "--json", cwd=wt, check=False)
        self.assertEqual(p.returncode, 0, p.stdout)


if __name__ == "__main__":
    unittest.main()

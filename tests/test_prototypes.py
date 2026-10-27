import json
import os
import sys
import unittest

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")


class PrototypesTest(RepoCase):
    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        text = text[:text.index("agents:")] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' \
            + text[text.index("seats:"):]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        out = self.xv("slice", "new", "p1", "--by", "pat", "--kind", "prototype", "--axis",
                      "what the household acts on when it marks food used",
                      "--scenario", "Marking food used after a meal is quicker.").stdout
        self.wt = out.strip().splitlines()[-1]

    def record(self):
        return json.loads(self.xv("record", "show", "p1", "--json", cwd=self.wt).stdout)

    def test_three_prototypes_side_by_side_then_a_pick_by_two_people(self):
        self.xv("record", "set", "p1", "prototype_budgets", json.dumps({n: {"usd": 1} for n in "abc"}),
                "--by", "pat", cwd=self.wt)
        p = self.xv("run", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stderr)
        v = json.loads(p.stdout)
        self.assertEqual((v["stop"]["order"], v["stop"]["seat"]), ("prototypes_ready", "two_people"))
        side = open(os.path.join(self.wt, ".xv", "slices", "p1.prototypes.md")).read()
        for n in "abc":
            self.assertIn(f"variant {n}:", side)
        branches = sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout.split()
        self.assertEqual(len(branches), 3)

        spend_before = len(self.record()["spend"])
        p = self.xv("run", "p1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10)
        self.assertIn("unanswered", p.stdout)
        self.assertEqual(len(self.record()["spend"]), spend_before, "resuming does not rebuild the prototypes")

        p = self.xv("prototype", "pick", "p1", "--variant", "b", "--by", "pat", cwd=self.wt, check=False)
        self.assertIn("two people", p.stderr)
        scen = os.path.join(self.tmp, "restated.md")
        open(scen, "w").write("After a meal, the household marks a whole recipe's food used in one call.")
        self.xv("prototype", "pick", "p1", "--variant", "b", "--by", "pat,sam", "--with-user", "Ana",
                "--scenario-file", scen, cwd=self.wt)
        data = self.record()
        self.assertEqual((data["kind"], data["next"]), ("feature", "forecaster"))
        self.assertEqual(sh(["git", "branch", "--list", "--format=%(refname:short)", "xv/p1-proto-*"], self.repo).stdout.strip(), "")
        body = open(os.path.join(self.wt, ".xv", "slices", "p1.md")).read()
        self.assertIn("marks a whole recipe's food used in one call", body.split("## May ignore")[0])
        self.assertIn("Ana (user)", open(os.path.join(self.wt, data["decisions"][0]["record"])).read())


if __name__ == "__main__":
    unittest.main()

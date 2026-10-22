import json
import os
import unittest

from helpers import RepoCase, sh

import record


class SliceRecordTest(RepoCase):
    def test_slice_new_makes_branch_worktree_and_record(self):
        wt = self.new_slice("s1")
        self.assertTrue(os.path.exists(os.path.join(wt, ".xv", "slices", "s1.md")))
        self.assertEqual(sh(["git", "branch", "--show-current"], wt).stdout.strip(), "xv/s1")
        data = json.loads(self.xv("record", "show", "s1", "--json").stdout)
        self.assertEqual((data["set_by"], data["next"], data["status"]), ("pat", "forecaster", "open"))
        self.assertTrue(data["base"])

    def test_a_record_needs_who_and_what(self):
        self.new_slice("s1")
        p = self.xv("record", "new", "s2", "--scenario", "x", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--by", p.stderr)

    def test_a_list_field_is_appended_not_overwritten(self):
        wt = self.new_slice("s1")
        p = self.xv("record", "set", "s1", "moved_tests", "[]", cwd=wt, check=False)
        self.assertIn("xv record add", p.stderr)
        self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "a", "--why", "b", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"][0]["file"], "tests/test_store.py")

    def test_a_budget_is_set_by_a_person(self):
        wt = self.new_slice("s1")
        p = self.xv("record", "set", "s1", "budget", '{"usd": 2}', cwd=wt, check=False)
        self.assertIn("--by", p.stderr)
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=wt)
        self.xv("record", "set", "s1", "budget", '{"usd": 4}', "--by", "pat", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["budget"], {"usd": 4, "set_by": "pat", "raised_from": {"usd": 2}})

    def test_a_two_person_stop_needs_two_names_and_writes_a_decision(self):
        wt = self.new_slice("s1")
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Shape?", cwd=wt)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "go", cwd=wt, check=False)
        self.assertIn("two people", p.stderr)
        self.xv("record", "answer", "s1", "--by", "pat,sam", "--answer", "go", cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["stops"][0]["answered_by"], ["pat", "sam"])
        rec = os.path.join(wt, data["decisions"][0]["record"])
        self.assertIn('who: ["pat", "sam"]', open(rec).read())

    def test_report_block_is_applied(self):
        wt = self.new_slice("s1")
        out = ('done.\n```xv-report\n{"agent": "maker", "status": "green", "summary": "ok", '
               '"moved_tests": [{"file": "tests/a.py", "assertion": "x", "why": "y"}]}\n```\n')
        p = sh(["python3", os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "xv"),
                "record", "report", "s1", "maker", "-"], wt)
        self.assertIn("no-report", p.stdout)
        path = os.path.join(self.tmp, "out.txt")
        open(path, "w").write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "maker", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"][0]["by"], "maker")


class GuardianReportTest(RepoCase):
    def test_the_guardians_count_of_moved_tests_is_not_a_record(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "out.txt")
        with open(path, "w") as f:
            f.write('```xv-report\n{"agent": "guardian", "status": "done", "moved_tests": 2, '
                    '"shape_change": "no", "pitch_contradiction": "no"}\n```\n')
        self.xv("record", "report", "s1", "guardian", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"], [])


class GuideTest(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.xv("record", "add", "s1", "spend", json.dumps(
            {"step": "maker", "harness": "claude", "model": "sonnet", "tokens_in": 1000, "tokens_out": 200,
             "tokens": 1200, "usd": 0.5, "wall_s": 30}), cwd=self.wt)

    def test_append_once_per_slice(self):
        self.xv("record", "guide-append", "s1", "--why", "first try", cwd=self.wt)
        p = self.xv("record", "guide-append", "s1", "--why", "again", cwd=self.wt, check=False)
        self.assertIn("already has s1", p.stderr)

    def test_verify_refuses_an_edit_and_allows_a_revert(self):
        self.xv("record", "guide-append", "s1", "--why", "first try", cwd=self.wt)
        sh(["git", "commit", "-qam", "row"], self.wt)
        guide = os.path.join(self.wt, ".xv", "estimation.md")
        text = open(guide).read()
        open(guide, "w").write(text.replace("first try", "a better story"))
        p = self.xv("record", "guide-verify", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("edited in place", p.stderr)
        rows = [l for l in text.splitlines() if not l.startswith("| s1 ")]
        open(guide, "w").write("\n".join(rows) + "\n")
        self.xv("record", "guide-verify", cwd=self.wt)

    def test_the_header_matches_the_default_file(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(open(os.path.join(here, "defaults", "estimation.md")).read(), record.GUIDE_HEADER)


if __name__ == "__main__":
    unittest.main()

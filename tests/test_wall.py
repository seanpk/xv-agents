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


class WallRedFileTest(RepoCase):
    """A red file that existed at the base is covered only for the tests the slice added."""

    NEW_TEST = ("\n    def test_renewal(self):\n"
                "        self.store.add(\"tea\", 1, date(2027, 1, 1))\n"
                "        self.assertEqual(self.store.items()[0].qty, 2)\n")

    def red_slice(self, edit, files=("tests/test_store.py",), move=False, base=None):
        for rel, text in (base or {}).items():
            write(os.path.join(self.repo, rel), text)
            sh(["git", "add", "-A"], self.repo)
            sh(["git", "commit", "-qm", "old test file"], self.repo)
        wt = self.new_slice("s1")
        for rel in files:
            path = os.path.join(wt, rel)
            write(path, edit(open(path).read()))
        self.xv("record", "set", "s1", "red", json.dumps({"files": list(files), "command": "x"}), cwd=wt)
        self.xv("wall", "baseline", "s1", cwd=wt)
        if move:
            self.xv("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "a", "--why", "b", cwd=wt)
        sh(["git", "add", "-A"], wt)
        sh(["git", "commit", "-qm", "work"], wt)
        p = self.xv("wall", "check", "--base", "main", "--json", cwd=wt, check=False)
        return p.returncode, json.loads(p.stdout)

    def add_test(self, text):
        marker = '\n\nif __name__ == "__main__":'
        return text.replace(marker, self.NEW_TEST + marker)

    def test_adding_a_test_to_a_red_file_passes(self):
        code, res = self.red_slice(self.add_test)
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_changing_an_old_assertion_in_a_red_file_fails(self):
        code, res = self.red_slice(lambda t: self.add_test(t).replace('("bread", 0)', "anything"))
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/test_store.py"]))

    def test_deleting_an_old_test_from_a_red_file_fails(self):
        def edit(t):
            start = t.index("    def test_use_refuses_more_than_there_is")
            end = t.index("    def test_used_up_item_stays_listed")
            return self.add_test(t[:start] + t[end:])
        code, res = self.red_slice(edit)
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/test_store.py"]))

    def test_a_recorded_move_covers_an_old_test_changed_in_a_red_file(self):
        code, res = self.red_slice(lambda t: self.add_test(t).replace('("bread", 0)', "anything"), move=True)
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_new_import_for_a_new_test_in_a_red_file_passes(self):
        code, res = self.red_slice(lambda t: self.add_test(t).replace(
            "from datetime import date\n", "from datetime import date, timedelta\n"))
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_removed_blank_line_in_a_red_file_passes(self):
        code, res = self.red_slice(lambda t: self.add_test(t).replace("\n\n\nclass StoreTest", "\n\nclass StoreTest", 1))
        self.assertEqual((code, res["unrecorded"]), (0, []))

    JS_BASE = ('import { load } from "./config";\n'
               'const fs = require("fs");\n\n'
               'test("missing config", () => {\n'
               '  expect(() => require("./config")).toThrow("missing");\n'
               '});\n')

    def js_red(self, old, new):
        path = "tests/config.test.js"
        return self.red_slice(lambda t: t.replace(old, new) + 'test("added", () => {});\n',
                              files=(path,), base={path: self.JS_BASE})

    def test_js_import_and_require_lines_changed_in_a_red_file_pass(self):
        code, res = self.js_red('import { load } from "./config";', 'import { load, save } from "./config";')
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_js_require_assignment_changed_in_a_red_file_passes(self):
        code, res = self.js_red('const fs = require("fs");', 'const path = require("path");')
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_line_that_only_contains_require_in_a_red_file_counts(self):
        code, res = self.js_red('.toThrow("missing")', '.toThrow("gone")')
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/config.test.js"]))

    def test_a_js_require_line_is_not_an_import_in_a_python_red_file(self):
        base = ("import unittest\nrequire = lambda x: x\n\n\nclass T(unittest.TestCase):\n"
                "    def test_a(self):\n        self.assertEqual(require(1), 1)\n")
        code, res = self.red_slice(lambda t: t.replace("require = lambda x: x", "require = lambda x: x + 0"),
                                   files=("tests/test_req.py",), base={"tests/test_req.py": base})
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/test_req.py"]))

    def test_ruby_and_go_import_lines_changed_in_a_red_file_pass(self):
        rb = 'require "json"\nrequire_relative "helper"\n\ndescribe "x" do\n  it "a" do\n    expect(1).to eq(1)\n  end\nend\n'
        code, res = self.red_slice(lambda t: t.replace('require "json"', 'require "set"') + 'it "b" do\nend\n',
                                   files=("tests/x_spec.rb",), base={"tests/x_spec.rb": rb})
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_go_import_line_changed_in_a_red_file_passes(self):
        go = 'package x\n\nimport "testing"\n\nfunc TestA(t *testing.T) {\n\tif 1 != 1 {\n\t\tt.Fatal("no")\n\t}\n}\n'
        code, res = self.red_slice(lambda t: t.replace('import "testing"', 'import "os"') + "func TestB(t *testing.T) {}\n",
                                   files=("tests/x_test.go",), base={"tests/x_test.go": go})
        self.assertEqual((code, res["unrecorded"]), (0, []))

    def test_a_file_type_with_no_import_matchers_skips_no_import_line(self):
        code, res = self.red_slice(lambda t: t.replace("import foo", "import bar") + "run b\n",
                                   files=("tests/cases.xyz",), base={"tests/cases.xyz": "import foo\nrun a\n"})
        self.assertEqual((code, res["unrecorded"]), (1, ["tests/cases.xyz"]))

    def test_a_red_file_new_in_the_slice_is_covered_whole(self):
        wt = self.new_slice("s1")
        write(os.path.join(wt, "tests", "test_new.py"),
              "def test_x():\n    assert True\n\n\ndef test_y():\n    assert 1 == 1\n")
        self.xv("record", "set", "s1", "red", json.dumps({"files": ["tests/test_new.py"], "command": "x"}), cwd=wt)
        self.xv("wall", "baseline", "s1", cwd=wt)
        sh(["git", "add", "-A"], wt)
        sh(["git", "commit", "-qm", "work"], wt)
        p = self.xv("wall", "check", "--base", "main", "--json", cwd=wt, check=False)
        res = json.loads(p.stdout)
        self.assertEqual((p.returncode, res["unrecorded"], res["tests_moved"]), (0, [], []))


class RedGapsTest(unittest.TestCase):
    """wall.red_gaps(scenario, red_texts): the flags and `xv` commands in backticks that no red file has."""

    def gaps(self, scenario, *reds):
        import wall
        return wall.red_gaps(scenario, list(reds))

    def test_a_flag_in_backticks_that_no_red_file_has_is_listed(self):
        self.assertEqual(self.gaps("Takes `--since <date>`.", "run(['--until', 'x'])"), ["--since"])

    def test_a_flag_one_of_the_red_files_has_is_not_listed(self):
        self.assertEqual(self.gaps("Takes `--since <date>`.", "nothing", "xv('--since', d)"), [])

    def test_a_flag_in_plain_words_is_not_read(self):
        self.assertEqual(self.gaps("Takes a --since flag.", ""), [])

    def test_a_command_is_covered_when_its_words_are_together_in_order(self):
        scenario = "Run `xv record answer` and `xv slice amend`."
        self.assertEqual(self.gaps(scenario, "self.xv('record', 'answer')", "run xv slice amend"), [])

    def test_a_command_whose_words_are_apart_is_listed(self):
        scenario = "Run `xv record answer`."
        self.assertEqual(self.gaps(scenario, "xv('record', 'show')\nxv('slice', 'answer')"), ["xv record answer"])

    def test_a_command_whose_words_are_out_of_order_is_listed(self):
        self.assertEqual(self.gaps("Run `xv record answer`.", "('answer', 'record')"), ["xv record answer"])

    def test_on_the_first_red_of_stop_decisions_it_lists_since_and_on_the_final_red_nothing(self):
        from test_check import red_texts, stop_decisions_scenario
        self.assertIn("--since", self.gaps(stop_decisions_scenario(), *red_texts("first")))
        self.assertEqual(self.gaps(stop_decisions_scenario(), *red_texts("final")), [])


if __name__ == "__main__":
    unittest.main()

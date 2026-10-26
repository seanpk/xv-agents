import os
import shutil
import unittest

from helpers import HOME, RepoCase, sh

from xvlib import load_config

# Programs that run anything given the right arguments: a rule must never stop at one of these.
RUNS_ANYTHING = ["python3", "python", "go", "npm", "npx", "node", "bundle", "ruby", "cargo", "make",
                 "yarn", "pnpm", "sh", "bash"]
SEATS = ("default", "forecaster", "guardian")


def entries_of(config, seat):
    line = config["agents"][seat]
    if "--allowedTools" not in line:
        return []
    return line[line.index("--allowedTools") + 1].split(",")


def prefixes(entries):
    return [e[len("Bash("):-len(":*)")] for e in entries if e.startswith("Bash(") and e.endswith(":*)")]


class InitAllowListBareTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def touch(self, *parts):
        path = os.path.join(self.repo, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()

    def init(self):
        shutil.rmtree(os.path.join(self.repo, ".xv"), ignore_errors=True)
        self.xv("init")
        return load_config(self.repo)

    def layouts(self):
        return {
            "python with tests/": [("tests", "test_a.py")],
            "python with src/ and tests/": [("tests", "test_a.py"), ("src", "pkg", "__init__.py")],
            "go": [("go.mod",)],
            "go with a tests/ folder": [("go.mod",), ("tests", "notes.txt")],
            "ruby": [("Gemfile",), ("spec", "a_spec.rb")],
            "node": [("package.json",)],
            "empty": [],
        }

    def test_no_starter_rule_is_a_bare_program_name(self):
        for name, files in self.layouts().items():
            for f in files:
                self.touch(*f)
            config = self.init()
            for seat in SEATS:
                for prefix in prefixes(entries_of(config, seat)):
                    with self.subTest(layout=name, seat=seat, rule=prefix):
                        self.assertNotIn(prefix, RUNS_ANYTHING)
            shutil.rmtree(self.repo)
            self.setUp()

    def test_rules_come_only_from_the_chosen_test_command(self):
        self.touch("go.mod")
        self.touch("tests", "notes.txt")
        config = self.init()
        command = config["tests"]["command"]
        self.assertTrue(command.startswith("go "), command)
        for seat in SEATS:
            for prefix in prefixes(entries_of(config, seat)):
                with self.subTest(seat=seat, rule=prefix):
                    self.assertFalse(prefix.startswith(("python", "bundle", "npm")), prefix)

    def test_a_python_repo_gets_no_rule_for_other_runners(self):
        self.touch("tests", "test_a.py")
        self.touch("src", "pkg", "__init__.py")
        self.touch("package.json")
        config = self.init()
        command = config["tests"]["command"]
        if "unittest" not in command:
            self.skipTest("detection chose another runner: " + command)
        for seat in ("default", "guardian"):
            for prefix in prefixes(entries_of(config, seat)):
                with self.subTest(seat=seat, rule=prefix):
                    self.assertFalse(prefix.startswith(("npm", "bundle", "go ")), prefix)

    def test_a_leading_name_value_is_handled_by_a_rule_or_by_the_skill(self):
        self.touch("tests", "test_a.py")
        self.touch("src", "pkg", "__init__.py")
        config = self.init()
        command = config["tests"]["command"]
        self.assertIn("PYTHONPATH=src", command)
        rest = command.split("&&")[-1].strip()
        rest = " ".join(w for w in rest.split() if "=" not in w.split("/")[0])
        skill = open(os.path.join(HOME, "skills", "xv-init", "SKILL.md")).read()
        for seat in ("default", "guardian"):
            with self.subTest(seat=seat):
                has_rule = any(rest == p or rest.startswith(p + " ") for p in prefixes(entries_of(config, seat))
                               if p not in RUNS_ANYTHING)
                told_to_check = "PYTHONPATH" in skill and "allow" in skill.lower()
                self.assertTrue(has_rule or told_to_check,
                                f"no specific rule for {rest!r} and the skill does not tell the person to check it")


# Watch first: run `xv init` in a scratch repo with src/ and tests/ folders, then in a Go repo
# that also has a tests/ folder. No rule should stop at python3, go or npm, and the Go repo
# should carry no Python rule. Read what the skill says about a leading PYTHONPATH=src.

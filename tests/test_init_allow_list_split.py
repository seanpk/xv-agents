import os
import re
import shutil
import unittest

from helpers import RepoCase, sh

from xvlib import load_config

READ_ONLY_MORE = ["rg", "wc", "sed -n", "diff", "git ls-files", "git grep", "git rev-parse"]
GUARDIAN_ONLY = ["xv wall diff", "xv boundary", "xv packet lint"]


def entries_of(config, seat):
    line = config["agents"][seat]
    if "--allowedTools" not in line:
        return []
    return line[line.index("--allowedTools") + 1].split(",")


def rule_allows(entries, part):
    """Claude Code's reading of Bash(<prefix>:*): the part is the prefix, or the prefix and more."""
    for e in entries:
        if e.startswith("Bash(") and e.endswith(":*)"):
            prefix = e[len("Bash("):-len(":*)")]
            if part == prefix or part.startswith(prefix + " "):
                return True
    return False


def unallowed_parts(entries, command):
    """Claude Code matches each part of a compound command; return the parts no rule covers."""
    return [p for p in re.split(r"\s*(?:&&|\|\||;)\s*", command) if p and not rule_allows(entries, p)]


class InitAllowListSplitTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def touch(self, *parts):
        path = os.path.join(self.repo, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()

    def init(self):
        self.xv("init")
        return load_config(self.repo)

    def test_every_part_of_a_compound_test_command_has_a_rule(self):
        # a leading VAR=value or `cd dir &&` is a part of its own
        self.touch("tests", "test_a.py")
        self.touch("src", "pkg", "__init__.py")
        sh(["git", "add", "-A"], self.repo)
        config = self.init()
        command = config["tests"]["command"]
        self.assertIn("PYTHONPATH=src", command)
        for seat in ("default", "guardian"):
            self.assertEqual(unallowed_parts(entries_of(config, seat), command), [], seat)

    def test_a_single_test_file_can_run_not_only_the_whole_suite(self):
        cases = [
            ([("Gemfile",), ("spec", "a_spec.rb")], "bundle exec rspec spec/a_spec.rb"),
            ([("go.mod",)], "go test ./pkg"),
            ([("tests", "test_a.py")], "python3 -m unittest tests.test_a"),
        ]
        for files, red in cases:
            with self.subTest(red=red):
                shutil.rmtree(os.path.join(self.repo, ".xv"), ignore_errors=True)
                sh(["git", "clean", "-fdxq"], self.repo)
                for f in files:
                    self.touch(*f)
                config = self.init()
                for seat in ("default", "guardian"):
                    self.assertEqual(unallowed_parts(entries_of(config, seat), red), [], seat)

    def test_every_seat_gets_the_wider_read_only_list(self):
        config = self.init()
        for seat in ("default", "forecaster", "guardian"):
            entries = entries_of(config, seat)
            for prefix in READ_ONLY_MORE:
                self.assertIn(f"Bash({prefix}:*)", entries, f"{seat}: {prefix}")

    def test_only_the_guardian_gets_wall_boundary_and_packet_lint(self):
        config = self.init()
        guardian = entries_of(config, "guardian")
        for prefix in GUARDIAN_ONLY:
            self.assertIn(f"Bash({prefix}:*)", guardian, prefix)
        for seat in ("default", "forecaster"):
            for prefix in GUARDIAN_ONLY:
                self.assertNotIn(f"Bash({prefix}:*)", entries_of(config, seat), f"{seat}: {prefix}")


# Watch first: run `xv init` in a scratch repo with a src/ folder and a tests/ folder, and read
# the agents block. The test command's parts each have a rule, and a single test file would run.

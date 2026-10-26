import os
import re
import shutil
import subprocess
import sys
import unittest

from helpers import HOME, RepoCase, XV, sh

from xvlib import load_config

SKILL = os.path.join(HOME, "skills", "xv-init", "SKILL.md")


def entries_of(config, seat):
    line = config["agents"][seat]
    if "--allowedTools" not in line:
        return []
    return line[line.index("--allowedTools") + 1].split(",")


def rule_allows(entries, command):
    """Claude Code's reading of Bash(<prefix>:*): the command is the prefix, or the prefix and more."""
    for e in entries:
        if e.startswith("Bash(") and e.endswith(":*)"):
            prefix = e[len("Bash("):-len(":*)")]
            if command == prefix or command.startswith(prefix + " "):
                return True
    return False


class InitAllowListPromptTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def touch(self, *parts):
        path = os.path.join(self.repo, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()

    def test_the_xv_command_the_prompt_names_is_matched_by_the_starter_rules(self):
        self.touch("tests", "test_a.py")
        self.xv("init")
        config = load_config(self.repo)
        bin_dir = os.path.join(self.tmp, "bin")
        os.makedirs(bin_dir)
        fake = os.path.join(bin_dir, "xv")
        with open(fake, "w") as f:
            f.write("#!/bin/sh\n")
        os.chmod(fake, 0o755)
        env = dict(os.environ, PATH=bin_dir + os.pathsep + os.environ["PATH"])
        out = subprocess.run([sys.executable, XV, "prompt", "guardian"], cwd=self.repo, env=env,
                             capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
        named = re.search(r"The `xv` command: `([^`]+)`", out)
        self.assertIsNotNone(named, out[-400:])
        for extra in ("wall diff", "boundary", "packet lint"):
            with self.subTest(extra=extra):
                self.assertTrue(rule_allows(entries_of(config, "guardian"), f"{named.group(1)} {extra}"),
                                f"no starter rule matches `{named.group(1)} {extra}`")

    def test_a_python_repo_with_other_markers_gets_no_rule_for_other_runners(self):
        # pyproject.toml comes before package.json in detection, and the Gemfile has no spec/ or test/
        self.touch("tests", "test_a.py")
        self.touch("pyproject.toml")
        self.touch("package.json")
        self.touch("Gemfile")
        self.xv("init")
        config = load_config(self.repo)
        command = config["tests"]["command"]
        self.assertIn("python3", command)
        for seat in ("default", "guardian"):
            for e in entries_of(config, seat):
                with self.subTest(seat=seat, rule=e):
                    self.assertFalse(e.startswith(("Bash(npm", "Bash(bundle", "Bash(go ")), e)

    def test_the_skill_tells_the_person_to_change_the_test_rules_with_the_test_command(self):
        skill = open(SKILL).read()
        step = [l for l in skill.splitlines() if l.startswith("- **The test command.**")]
        self.assertEqual(len(step), 1)
        self.assertIn("--allowedTools", step[0])


# Watch first: run `xv init` in a repo with a tests/ folder and `xv prompt guardian` with xv on the
# PATH; the named xv command should be plain `xv`. Then read the skill's test command step for the
# line about changing the --allowedTools test rules along with tests.command.

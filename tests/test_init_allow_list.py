import os
import shutil
import unittest

from helpers import RepoCase, sh

from xvlib import load_config

READ_ONLY = [
    "cat", "head", "tail", "ls", "grep", "git diff", "git log", "git status", "git show",
]
MAKER_ONLY = ["git rm", "git mv", "xv record move"]


def allowed(config, seat):
    line = config["agents"][seat]
    if "--allowedTools" not in line:
        return None
    return line[line.index("--allowedTools") + 1].split(",")


def covers(entries, command):
    """True when some Bash(<prefix>:*) entry permits the command as written."""
    for e in entries:
        if e.startswith("Bash(") and e.endswith(":*)"):
            prefix = e[len("Bash("):-len(":*)")]
            if command == prefix or command.startswith(prefix + " "):
                return True
    return False


def has(entries, prefix):
    return f"Bash({prefix}:*)" in entries


class InitAllowListTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def touch(self, *parts):
        path = os.path.join(self.repo, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()

    def test_the_default_agent_gets_read_only_commands_the_moves_and_the_test_command(self):
        self.xv("init")
        config = load_config(self.repo)
        entries = allowed(config, "default")
        self.assertIsNotNone(entries, "the default agent line has no --allowedTools")
        for prefix in READ_ONLY + MAKER_ONLY:
            self.assertTrue(has(entries, prefix), prefix)
        self.assertTrue(covers(entries, config["tests"]["command"]), "the detected test command is not allowed")

    def test_the_forecaster_gets_only_the_read_only_part(self):
        self.xv("init")
        config = load_config(self.repo)
        entries = allowed(config, "forecaster")
        self.assertIsNotNone(entries, "the forecaster line has no --allowedTools")
        for prefix in READ_ONLY:
            self.assertTrue(has(entries, prefix), prefix)
        for prefix in MAKER_ONLY:
            self.assertFalse(has(entries, prefix), prefix)
        self.assertFalse(covers(entries, config["tests"]["command"]), "the forecaster may run tests")

    def test_the_guardian_gets_the_read_only_part_and_the_test_command(self):
        self.xv("init")
        config = load_config(self.repo)
        entries = allowed(config, "guardian")
        self.assertIsNotNone(entries, "the guardian line has no --allowedTools")
        for prefix in READ_ONLY:
            self.assertTrue(has(entries, prefix), prefix)
        for prefix in MAKER_ONLY:
            self.assertFalse(has(entries, prefix), prefix)
        self.assertTrue(covers(entries, config["tests"]["command"]), "the detected test command is not allowed")

    def test_the_list_follows_the_detected_test_command(self):
        self.touch("Gemfile")
        self.touch("spec", "a_spec.rb")
        self.xv("init")
        config = load_config(self.repo)
        self.assertEqual(config["tests"]["command"], "bundle exec rspec")
        for seat in ("default", "guardian"):
            self.assertTrue(covers(allowed(config, seat) or [], "bundle exec rspec"), seat)

    def test_commented_out_non_claude_examples_get_no_allow_list(self):
        self.xv("init")
        text = open(os.path.join(self.repo, ".xv", "config.yml")).read()
        for line in text.splitlines():
            if line.lstrip().startswith("#") and "--allowedTools" in line:
                self.fail("a commented-out non-Claude example line was given an allow list: " + line)


# Watch first: run `xv init` in a scratch repo and read the agents block of .xv/config.yml.
# The default line lists read-only shell and git commands, git rm/mv, xv record move and your
# test command, one rule per part; the forecaster's list is read-only; the guardian's adds the
# test command's rules and xv wall diff, xv boundary and xv packet lint.
# Look for a test command that is allowed in a form a headless agent could not actually run.

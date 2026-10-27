import json
import os
import re

from helpers import RepoCase, sh

TOOLS = ("Bash(cat:*),Bash(git diff:*),Bash(cd tests:*),Bash(python3 -m unittest:*),"
         "Bash(xv wall diff:*),Read,Edit")
GUARDIAN_TOOLS = "Bash(cat:*),Bash(xv packet lint:*),Bash(git log:*)"


def agent_line(tools, harness="claude"):
    if harness == "claude":
        args = ["claude", "-p", "--output-format", "json", "--permission-mode", "acceptEdits"]
        if tools is not None:
            args += ["--allowedTools", tools]
        args += ["--model", "sonnet", "{prompt}"]
    else:
        args = [harness, "run", "--model", "x", "{prompt}"]
    return json.dumps(args)


class AllowedCommandsPromptTest(RepoCase):
    def slice_with(self, **lines):
        """Rewrite the agents block of the fixture config, then open a slice."""
        path = os.path.join(self.repo, ".xv", "config.yml")
        text = open(path).read()
        text = re.sub(r"(?m)^agents:\n(?:  .*\n)+", "", text)
        block = "agents:\n" + "".join(f"  {seat}: {line}\n" for seat, line in lines.items())
        with open(path, "w") as fh:
            fh.write(text.rstrip("\n") + "\n" + block)
        sh(["git", "commit", "-qam", "agents"], self.repo)
        return self.new_slice("s1")

    def prompt(self, wt, seat="maker"):
        return self.xv("prompt", seat, "s1", cwd=wt).stdout

    def test_the_prompt_lists_the_bash_commands_from_the_default_line(self):
        wt = self.slice_with(default=agent_line(TOOLS))
        out = self.prompt(wt)
        for command in ("`cd tests`", "`python3 -m unittest`", "`git diff`", "`cat`", "`xv wall diff`"):
            with self.subTest(command=command):
                self.assertIn(command, out)

    def test_non_bash_tools_are_not_listed_as_commands(self):
        wt = self.slice_with(default=agent_line(TOOLS))
        out = self.prompt(wt)
        self.assertNotIn("`Read`", out)
        self.assertNotIn("Bash(", out)

    def test_the_prompt_forbids_chaining_extra_flags_and_unlisted_pipes(self):
        wt = self.slice_with(default=agent_line(TOOLS))
        out = self.prompt(wt)
        self.assertIn("python3 -W ignore -m unittest", out)
        low = out.lower()
        self.assertIn("chain", low)
        self.assertIn("pipe", low)
        self.assertIn("approval", low)

    def test_a_seat_with_its_own_line_gets_its_own_list_not_the_default(self):
        wt = self.slice_with(default=agent_line(TOOLS), guardian=agent_line(GUARDIAN_TOOLS))
        guardian = self.prompt(wt, "guardian")
        self.assertIn("`xv packet lint`", guardian)
        self.assertNotIn("`python3 -m unittest`", guardian)
        maker = self.prompt(wt, "maker")
        self.assertIn("`python3 -m unittest`", maker)
        self.assertNotIn("`xv packet lint`", maker)

    def test_a_line_with_no_allowed_tools_gets_no_list(self):
        wt = self.slice_with(default=agent_line(None))
        out = self.prompt(wt)
        self.assertNotIn("python3 -W ignore -m unittest", out)

    def test_a_harness_other_than_claude_gets_no_list(self):
        wt = self.slice_with(default=agent_line(None, harness="opencode"),
                             guardian=agent_line(GUARDIAN_TOOLS))
        out = self.prompt(wt)
        self.assertNotIn("python3 -W ignore -m unittest", out)
        self.assertNotIn("`git diff`", out)


# Watch first: set a seat's --allowedTools in .xv/config.yml to a few Bash rules, run
# `xv prompt <seat> <id>`, and read the commands section: each rule as a plain command, and the
# three cautions (no chained command, no extra flags, no unlisted pipe). Then give that seat's
# line no --allowedTools and see the section go.

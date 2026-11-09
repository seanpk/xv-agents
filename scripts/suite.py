#!/usr/bin/env python3
"""Run the repo's test command: the one place `record` and `run` both call."""

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import git, names_test  # noqa: E402

FAILING = re.compile(r"^(?:FAIL|ERROR): (\S+(?: \([^)]*\))?)|^FAILED (\S+)"
                     r"|^\s*[✕×] (.+?)(?: \(\d+ ?ms\)| \d+(?:\.\d+)? ?ms)?$|^ FAIL  \S+ > (.+)$"
                     r"|^--- FAIL: (\S+)|^rspec (\S+)|^\d+\) (.+)\n[ \t]+Message:"
                     r"|^\s*(?:\d+\) )?(?:Failure|Error):\n\s*([\w:]+#\w+)"
                     r"|^test (\S+) \.\.\. FAILED$|^\s+\d+\) (\[[^\]]+\] › .+?)\s*─*$", re.M)
# mocha prints a failure's title over several lines, one per describe, the last ending in a colon
MOCHA = re.compile(r"^ +\d+\) (.+(?:\n +[^\n]+?)*?):$", re.M)


def failing_tests(output):
    """Names of failing tests from unittest, pytest, jest, vitest, go, RSpec, Jasmine,
    minitest, mocha, cargo or Playwright output.

    RSpec is named by its rerun handle, ./spec/x_spec.rb:42, which is unique where
    descriptions repeat. Jasmine's numbered entries count only when a Message: line follows.
    Vitest names a test in its tree and again in its summary; both read `suite > test`.
    """
    names = {next(g for g in m if g) for m in FAILING.findall(output)}
    if re.search(r"^ +\d+ failing$", output, re.M):
        names |= {" ".join(part.strip() for part in m.split("\n")) for m in MOCHA.findall(output)}
    return sorted(names)


def own_red_names(root, data, onto):
    """The names of the tests the slice added to its red files, read from the lines it added."""
    names = set()
    for f in (data.get("red") or {}).get("files") or []:
        out = git(["diff", "--unified=0", "--no-renames", f"{onto}...HEAD", "--", f], root)
        for line in out.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                names |= set(re.findall(r"\b(?:def|func|fn|it|test|specify)\b[\s(]*[\"']?(\w[\w ]*\w|\w)", line))
    return names


def in_own_red(names, name):
    """Is this failing test one of the tests the slice added to its red, named as a whole name?"""
    return any(names_test(name, n) for n in names)


def shell(cmd, cwd, timeout=900, env=None):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, **env} if env else None)
        return p.returncode, (p.stdout + p.stderr)[-4000:]
    except subprocess.TimeoutExpired as e:
        written = "".join(x.decode(errors="replace") if isinstance(x, bytes) else x
                          for x in (e.stdout, e.stderr) if x)
        return 124, f"{written[-4000:]}\ntimed out after {timeout}s"


def tests_timeout(config):
    return int((config.get("tests") or {}).get("timeout") or 900)


def run_suite(root, config, base=None, slice_id=None):
    """Run tests.command. XV_BASE and XV_SLICE tell a script that picks suites from the changed files where to diff from."""
    cmd = (config.get("tests") or {}).get("command")
    if not cmd:
        return None, "no tests.command in .xv/config.yml"
    env = {k: v for k, v in (("XV_BASE", base), ("XV_SLICE", slice_id)) if v}
    code, out = shell(cmd, root, tests_timeout(config), env)
    return ("green" if code == 0 else "red"), out

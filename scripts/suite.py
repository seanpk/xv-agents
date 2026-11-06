#!/usr/bin/env python3
"""Run the repo's test command: the one place `record` and `run` both call."""

import os
import subprocess


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

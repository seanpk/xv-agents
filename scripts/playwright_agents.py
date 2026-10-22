#!/usr/bin/env python3
"""Install Playwright's test agents for the scenario agent, without the healer.

Playwright's `init-agents` writes three agent definitions for a harness: a
planner, a generator and a healer. The scenario agent uses the planner's way of
exploring and the generator's way of writing a test against the live page. The
healer repairs a failing test by editing it until it passes, which is the move
the test wall exists to stop, so this removes it.

Checked 2026-10-21 with Playwright 1.64.1: `--loop=claude` writes
.claude/agents/playwright-test-{planner,generator,healer}.md and .mcp.json;
`--loop=opencode` writes .opencode/prompts/playwright-test-*.md and an
opencode.json with one agent entry per prompt.

Usage: xv playwright install --loop claude|opencode|vscode|codex
"""

import argparse
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XVError, die, repo_root  # noqa: E402


def remove_healer(root):
    removed = []
    for path in glob.glob(os.path.join(root, ".*", "**", "*healer*"), recursive=True):
        if os.path.isfile(path) and "playwright" in os.path.basename(path):
            os.remove(path)
            removed.append(os.path.relpath(path, root))
    oc = os.path.join(root, "opencode.json")
    if os.path.exists(oc):
        with open(oc) as f:
            data = json.load(f)
        agents = data.get("agent") or {}
        for name in [n for n in agents if "healer" in n]:
            del agents[name]
            removed.append(f"opencode.json: agent {name}")
        with open(oc, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
    return removed


def install(root, loop):
    p = subprocess.run(["npx", "playwright", "init-agents", f"--loop={loop}"], cwd=root,
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise XVError(f"npx playwright init-agents failed: {p.stderr.strip()[-400:]}")
    removed = remove_healer(root)
    if not removed:
        raise XVError("init-agents ran but no healer was found to remove; check what it wrote before using it")
    return removed


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv playwright", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("install")
    i.add_argument("--loop", required=True, choices=["claude", "opencode", "vscode", "codex"])
    sub.add_parser("remove-healer")
    a = p.parse_args(argv)
    try:
        root = repo_root()
        removed = install(root, a.loop) if a.cmd == "install" else remove_healer(root)
        print("removed the healer: " + ", ".join(removed) if removed else "no healer found")
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

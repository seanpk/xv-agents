#!/usr/bin/env python3
"""Check the guardian's packet and enforce the evidence rule.

The packet's front matter must carry the two fixed fields the watch reads,
`shape_change` and `pitch_contradiction`, each `yes` or `no`, and the door,
`one-way` or `two-way`. In the four check sections, every finding must cite a
line (`path:12`), a project file (`.xv/pitch.md`), a rule, a quoted line, or
a diff hunk. A finding that cites nothing is moved to "Dropped by the evidence
rule" at the end of the packet. It is not deleted; a person can read it, and
it does not count.

Usage: xv packet lint <file> [--fix] [--json]
Exit 1 when the front matter is wrong. Dropped findings alone do not fail.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XVError, die, join_front_matter, split_front_matter  # noqa: E402

CHECKS = re.compile(r"^##\s*(?:\d\.\s*)?(shape|pitch|moved tests|the picture|picture|security|usability)\b", re.I)
CITATION = re.compile(
    r"[\w./-]+\.[A-Za-z]{1,5}:\d+"           # path:line
    r"|\.xv/[\w-]+\.md"                       # a project file
    r"|\b(?:baseline|standards?|rule):"       # a rule
    r"|[\"“][^\"”]{15,}[\"”]"                 # a quoted line
    r"|`[^`]*\.(?:py|ts|tsx|js|rb|go|md|json|yml)[^`]*`"  # a named file
    r"|@@ -\d+", re.I)
NOT_A_FINDING = re.compile(r"^\s*(?:[-*]|\d+\.)\s*(?:none\b|no\b|nothing\b|not\b|looked at|checked\b|n/a\b)", re.I)
ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+\S")


def lint(text):
    data, body = split_front_matter(text)
    problems = []
    for field in ("shape_change", "pitch_contradiction"):
        if data.get(field) not in ("yes", "no"):
            problems.append(f"front matter {field} must be yes or no, found {data.get(field)!r}")
    if data.get("door") not in ("one-way", "two-way"):
        problems.append(f"front matter door must be one-way or two-way, found {data.get('door')!r}")
    kept, dropped = [], []
    in_check, in_code = False, False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            kept.append(line)
            continue
        if line.startswith("## "):
            in_check = bool(CHECKS.match(line))
        if in_check and not in_code and ITEM.match(line) and not NOT_A_FINDING.match(line) \
                and not CITATION.search(line):
            dropped.append(line.strip())
            continue
        kept.append(line)
    return data, "\n".join(kept), problems, dropped


def fix(path):
    with open(path) as f:
        text = f.read()
    data, body, problems, dropped = lint(text)
    if dropped:
        body = body.rstrip("\n") + "\n\n## Dropped by the evidence rule\n\nThese findings cite no line, rule or hunk, so they do not count.\n\n" \
            + "\n".join(f"- {d.lstrip('-* ').strip()}" for d in dropped) + "\n"
        with open(path, "w") as f:
            f.write(join_front_matter(data, "\n" + body.lstrip("\n")))
    return {"problems": problems, "dropped": dropped}


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv packet", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("lint")
    s.add_argument("file")
    s.add_argument("--fix", action="store_true", help="move uncited findings to the dropped section")
    s.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        if a.fix:
            res = fix(a.file)
        else:
            with open(a.file) as f:
                _, _, problems, dropped = lint(f.read())
            res = {"problems": problems, "dropped": dropped}
    except XVError as e:
        die(str(e), 2)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        for x in res["problems"]:
            print(f"problem: {x}")
        for x in res["dropped"]:
            print(f"uncited: {x}")
    sys.exit(1 if res["problems"] else 0)


if __name__ == "__main__":
    main()

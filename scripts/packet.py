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
MISSES = re.compile(r"^##\s*scenario misses\b", re.I)
MISS_REF = re.compile(r"^\s*[-*]\s+((?:point\s+|decision\s+|amendment\s+)?\d+(?:\s*,\s*item\s+\d+)?)\b", re.I)
EVIDENCE = re.compile(r"\bevidence\s*:", re.I)


YES_NO = ("yes", "no")
ALLOWED = {"shape_change": YES_NO + ("accepted",), "pitch_contradiction": YES_NO}


def lint(text):
    data, body = split_front_matter(text)
    problems = []
    for field in ("shape_change", "pitch_contradiction"):
        allowed = ALLOWED[field]
        if data.get(field) not in allowed:
            problems.append(f"front matter {field} must be {' or '.join(allowed)}, found {data.get(field)!r}")
    if data.get("door") not in ("one-way", "two-way"):
        problems.append(f"front matter door must be one-way or two-way, found {data.get('door')!r}")
    if data.get("scenario_miss") not in (None, "yes", "no"):
        problems.append(f"front matter scenario_miss must be yes or no, found {data.get('scenario_miss')!r}")
    kept, dropped = [], []
    in_check, in_misses, in_code = False, False, False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code = not in_code
            kept.append(line)
            continue
        if line.startswith("## "):
            in_check = bool(CHECKS.match(line))
            in_misses = bool(MISSES.match(line))
        if in_misses and not in_code and ITEM.match(line) and not (MISS_REF.match(line) and EVIDENCE.search(line)):
            dropped.append(line.strip())
            continue
        if in_check and not in_code and ITEM.match(line) and not NOT_A_FINDING.match(line) \
                and not CITATION.search(line):
            dropped.append(line.strip())
            continue
        kept.append(line)
    body = "\n".join(kept)
    if data.get("scenario_miss") == "yes" and not misses(body):
        data["scenario_miss"] = "no"
    return data, body, problems, dropped


def misses(body):
    """The misses kept in the packet's `## Scenario misses` section: ref, text, where it goes, whether it amends."""
    out, in_misses = [], False
    for line in body.splitlines():
        if line.startswith("## "):
            in_misses = bool(MISSES.match(line))
        m = MISS_REF.match(line) if in_misses else None
        if m and EVIDENCE.search(line):
            to = re.search(r"\bto\s*:\s*(maker|scenario)\b", line, re.I)
            out.append({"ref": re.sub(r"^point\s+", "", m.group(1).strip().lower()), "text": line.strip().lstrip("-* ").strip(),
                        "to": to.group(1).lower() if to else "maker",
                        "amend": bool(re.search(r"\bamend\s*:\s*yes\b", line, re.I))})
    return out


def fix(path):
    with open(path) as f:
        text = f.read()
    data, body, problems, dropped = lint(text)
    changed = split_front_matter(text)[0].get("scenario_miss") != data.get("scenario_miss")
    if dropped:
        body = body.rstrip("\n") + "\n\n## Dropped by the evidence rule\n\nThese findings cite no line, rule or hunk, so they do not count.\n\n" \
            + "\n".join(f"- {d.lstrip('-* ').strip()}" for d in dropped) + "\n"
    if dropped or changed:
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


def crowded_picture_lines(root):
    """Line numbers of `.xv/picture.md` that hold more than one sentence. A sentence end is a full stop and a
    space followed by a capital letter, outside backticks; fenced lines are not read."""
    path = os.path.join(root, ".xv", "picture.md")
    if not os.path.exists(path):
        return []
    found, fenced = [], False
    with open(path, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f.read().splitlines(), 1):
            if line.startswith("```"):
                fenced = not fenced
                continue
            prose = re.sub(r"^\s*(?:[-*]|\d+\.) ", "", re.sub(r"`[^`]*`", "", line))
            if not fenced and re.search(r"\. [A-Z]", prose):
                found.append(n)
    return found


def note_crowded_picture_lines(path, root):
    """Add a note to the packet naming each picture line with more than one sentence. A note, not a stop."""
    lines = crowded_picture_lines(root)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    kept = re.sub(r"(?m)\n*^Note: the picture should hold one sentence per line;[^\n]*\n?", "", text)
    if lines:
        kept = kept.rstrip("\n") + ("\n\nNote: the picture should hold one sentence per line; more than one sentence on "
                                    + ", ".join(f".xv/picture.md:{n}" for n in lines) + ".\n")
    if kept != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(kept)
    return lines


def packet_checks(path, data, root=None):
    """The packet checks `xv step` and `xv record packet` share: the lint, then the record's count of expected moves,
    then a note for picture lines that hold more than one sentence, then one line per pairing.
    Returns what goes into the guardian's checks."""
    lint_result = fix(path)
    problems = lint_result["problems"] + expected_moves_problems(path, data)
    if root:
        note_crowded_picture_lines(path, root)
    note_pairings(path, data)
    return {"packet_problems": problems, "dropped_findings": len(lint_result["dropped"])}


PAIRINGS = "## Pairings"


def spend_words(p):
    """A pairing's spend in words: the tokens the budget counts, or why it was not read."""
    row = p.get("spend")
    if not isinstance(row, dict):
        if not p.get("ended_at"):
            return "not read yet: the pairing is open"
        return f"not read ({p.get('spend_note') or 'no reason given'}); it is not in the slice's actual"
    usd = "usd not reported" if row.get("usd") is None else f"usd {row['usd']}"
    return (f"{row.get('tokens', 0)} tokens (in {row.get('tokens_in', 0)}, out {row.get('tokens_out', 0)}, "
            f"cache write {row.get('cache_write', 0)}; cache read {row.get('cache_read', 0)} not counted), "
            f"{row.get('turns') or 0} turns, {usd}")


def pairing_line(p):
    """One packet line for one pairing: who, with which session, why, the commits, the resume step and the spend."""
    session = p.get("session") or {}
    which = f"{session.get('harness') or 'unknown harness'} session {session.get('id')}" if session.get("id") \
        else "a session that was not named"
    commits = ", ".join(c[:10] for c in p.get("commits") or []) or "none"
    line = f"- Pairing {p.get('n')}: {p.get('by')} with {p.get('agent')} ({which}), because: {p.get('why')}."
    if not p.get("ended_at"):
        return line + f" Open since {p.get('started_at')}."
    line += f" Commits: {commits}. Resumed at {p.get('next')}. Spend: {spend_words(p)}."
    if p.get("not_blind"):
        line += " Not blind (written or changed in the pairing): " + ", ".join(p["not_blind"]) + "."
    if p.get("unprefixed"):
        line += " Commits without the pairing prefix: " + ", ".join(c[:10] for c in p["unprefixed"]) + "."
    return line


def note_pairings(path, data):
    """Write the packet's `## Pairings` section from the record, one line per pairing; a second run replaces it.
    No pairing, no section."""
    pairings = [p for p in data.get("pairings") or [] if isinstance(p, dict)]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    section = re.compile(r"(?m)\n*^## Pairings\n\n(?:- Pairing [^\n]*(?:\n|\Z))*")
    if not pairings and not section.search(text):
        return
    kept = section.sub("\n\n", text).rstrip("\n") + "\n"
    if pairings:
        kept = kept.rstrip("\n") + f"\n\n{PAIRINGS}\n\n" + "\n".join(pairing_line(p) for p in pairings) + "\n"
    if kept != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(kept)


def expected_moves_problems(packet, data):
    """Problems with the packet's `expected_moves`: it is a whole number, and the record's count."""
    with open(packet, encoding="utf-8") as f:
        value = split_front_matter(f.read())[0].get("expected_moves")
    count = len([m for m in data.get("moved_tests") or [] if m.get("expected")])
    if value is None:
        return ["front matter expected_moves is missing; it is the number of expected moves in the record"]
    if not str(value).isdigit():
        return [f"front matter expected_moves must be a whole number, found {value!r}"]
    if int(value) != count:
        return [f"front matter expected_moves is {value}, and the record holds {count}"]
    return []


if __name__ == "__main__":
    main()

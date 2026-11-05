#!/usr/bin/env python3
"""The moves a person expects: compare each moved test file before and after a step.

A refactor slice opens with `--expect-moves imports`, `renames`, or both, and with
`--rename Old=New` for each name it renames. After the maker and the cleaner,
`xv run` calls this to compare every test file that changed since the wall
baseline. A move that fits an expected kind is recorded, marked `expected`, and
needs no `accept_moves` stop. The agent does not decide whether a move is
expected; any other move still stops.

  imports  the same path; only import or require lines and whitespace change.
  renames  the file moves to a new path; it changes only in the names the slice
           renames, in import lines, and in whitespace.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wall  # noqa: E402
from xvlib import XVError, git, now  # noqa: E402


def code_lines(rel, text):
    """The lines that count: not blank, not an import line, whitespace collapsed."""
    imports = wall.IMPORT_MATCHERS.get(os.path.splitext(rel)[1])
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return [l for l in lines if l and not (imports and re.fullmatch(imports, l))]


def renamed(text, pairs):
    """`text` with each whole name in `pairs` replaced by its new name, all at once."""
    if not pairs:
        return text
    names = "|".join(re.escape(n) for n in sorted(pairs, key=len, reverse=True))
    return re.sub(rf"(?<!\w)(?:{names})(?!\w)", lambda m: pairs[m.group(0)], text)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def find(root, data, config):
    """The expected moves in the working tree now, as record entries."""
    kinds = data.get("expect_moves") or []
    if not kinds:
        return []
    try:
        d = wall.diff(root, data["id"], config)
    except XVError:
        return []
    commit = wall.load_baseline(root, data["id"])["commit"]
    before = lambda rel: git(["show", f"{commit}:{rel}"], root, check=False)
    pairs = data.get("renames") or {}
    out = []
    if "imports" in kinds:
        for rel in d["changed"]:
            if code_lines(rel, before(rel)) == code_lines(rel, read(root, rel)):
                out.append({"file": rel, "expected": "imports",
                            "assertion": "was: no code changed; now: import lines and whitespace only",
                            "why": "an import-only change, which the slice expects (--expect-moves imports)"})
    if "renames" in kinds:
        added = list(d["added"])
        for gone in d["deleted"]:
            want = code_lines(gone, renamed(before(gone), pairs))
            new = next((a for a in added if code_lines(a, read(root, a)) == want), None)
            if new:
                added.remove(new)
                out.append({"file": new, "from": gone, "expected": "renames",
                            "assertion": f"was: {gone}; now: {new}, with only the slice's named renames",
                            "why": "a file moved to a new path with only the renames the slice names "
                                   "(--expect-moves renames)"})
    return out


def apply(root, data, config):
    """Replace the record's expected moves with those the working tree holds now.

    An agent may have recorded such a move by hand; the script's entry replaces it."""
    found = find(root, data, config)
    files = {m["file"] for m in found}
    kept = [m for m in data.get("moved_tests") or [] if not m.get("expected") and m.get("file") not in files]
    stamp = now()
    data["moved_tests"] = kept + [{**m, "by": "xv", "at": stamp} for m in found]

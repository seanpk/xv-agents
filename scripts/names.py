"""Name and command parsing that run.py and record.py both need (record does not import run).

Python 3 standard library only.
"""

import os
import re


COVERED_SEPARATOR = re.compile(r"::|\s>\s|[.#/]")


def covered_name_found(name, files):
    """A name that may start with a red file's path or module and is split by `::`, `.`, `#`, `/` or ` > `;
    each part after the path must be a whole name in that file, in order."""
    rest, best = name, None
    for f in files:
        slashed, dotted = f.split("/"), os.path.splitext(f)[0].replace("/", ".").split(".")
        forms = ["/".join(slashed[i:]) for i in range(len(slashed))] + [".".join(dotted[i:]) for i in range(len(dotted))]
        for form in forms:
            m = re.match(re.escape(form) + "(?:" + COVERED_SEPARATOR.pattern + "|$)", name)
            if m and (best is None or len(form) > best[1]):
                best = (f, len(form), m.end())
    if best:
        files, rest = {best[0]: files[best[0]]}, name[best[2]:]
    parts = [p.strip() for p in COVERED_SEPARATOR.split(rest)]
    if not all(parts):
        return False
    for t in files.values():
        pos = 0
        for part in parts:
            m = re.compile(r"(?<!\w)" + re.escape(part) + r"(?!\w)").search(t, pos)
            if not m:
                break
            pos = m.end()
        else:
            return True
    return False


def joined_unsafely(command):
    """True when the command joins parts other than with && at the top level (outside quotes): a ;, ||, |, &
    or newline hides a failing exit code, as only the last part's counts."""
    quote = None
    i = 0
    while i < len(command):
        c = command[i]
        if quote:
            if c == "\\" and quote == '"':
                i += 1
            elif c == quote:
                quote = None
        elif c == "\\":
            i += 1
        elif c in "'\"":
            quote = c
        elif command.startswith("&&", i):
            i += 1
        elif c in ";|\n" or (c == "&" and command[i - 1:i] != ">" and command[i + 1:i + 2] != ">"):
            return True
        i += 1
    return False

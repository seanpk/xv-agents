#!/usr/bin/env python3
"""Count the stops in every slice record, per order: how often the pick was taken,
how often the person brought nothing new, and the causes.

Only stops answered with the offer and answer fields (a `pick` or a `settled`) are counted.

Usage: xv decisions [--since <date>]
"""

import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XV_DIR, XVError, die, read_doc, repo_root  # noqa: E402


def collect(root, since=None):
    """{order: {"stops", "picked", "no_new_info", "causes"}} over every record's counted stops."""
    orders = {}
    for path in sorted(glob.glob(os.path.join(root, XV_DIR, "slices", "*.md"))):
        if path.endswith((".packet.md", ".boundary.md")):
            continue
        data, _ = read_doc(path)
        for st in data.get("stops") or []:
            if not isinstance(st, dict) or st.get("answer") is None:
                continue
            if "pick" not in st and "settled" not in st:
                continue
            if since and (st.get("at") or "")[:10] < since:
                continue
            row = orders.setdefault(st.get("order") or "?",
                                    {"stops": 0, "picked": 0, "no_new_info": 0, "causes": {}})
            row["stops"] += 1
            row["picked"] += isinstance(st.get("pick"), int)
            row["no_new_info"] += st.get("new_info") == "none"
            cause = (st.get("cause") or "unrecorded").split(":")[0].strip()
            row["causes"][cause] = row["causes"].get(cause, 0) + 1
    return orders


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv decisions", description=__doc__.split("\n")[0])
    p.add_argument("--since", help="count only stops raised on or after this date (YYYY-MM-DD)")
    a = p.parse_args(argv)
    try:
        orders = collect(repo_root(), a.since)
    except XVError as e:
        die(str(e), 2)
    if not orders:
        print("no stops with a recorded decision")
        return
    for order, r in sorted(orders.items()):
        causes = ", ".join(f"{c} {n}" for c, n in sorted(r["causes"].items()))
        print(f"{order}: {r['stops']} stops, pick taken {r['picked']}, "
              f"new_info none {r['no_new_info']}, causes: {causes}")


if __name__ == "__main__":
    main()

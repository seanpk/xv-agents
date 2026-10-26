#!/usr/bin/env python3
"""Summarise eval runs as a Markdown table: one row per scenario, one column per
harness and arm, each cell the assertions passed out of the total.

  python3 evals/report.py evals/results/runs/<dir> [--details]
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from spend import row_tokens  # noqa: E402


def load(d):
    runs = []
    for path in sorted(glob.glob(os.path.join(d, "*.json"))):
        with open(path) as f:
            runs.append(json.load(f))
    return runs


def table(runs):
    cols = sorted({(r["harness"], r["arm"]) for r in runs}, key=lambda c: (c[0], c[1] != "skill"))
    rows = sorted({(r.get("increment", 0), r["scenario"]) for r in runs})
    head = "| inc | scenario | " + " | ".join(f"{h} {a}" for h, a in cols) + " |"
    sep = "| --- | --- | " + " | ".join("---" for _ in cols) + " |"
    lines = [head, sep]
    for inc, name in rows:
        cells = []
        for h, a in cols:
            rs = [r for r in runs if r["scenario"] == name and r["harness"] == h and r["arm"] == a]
            if not rs:
                cells.append("")
            elif any(r.get("error") for r in rs):
                cells.append("error")
            else:
                cells.append(", ".join(f"{r['passed']}/{r['total']}" for r in rs))
        lines.append(f"| {inc} | {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def details(runs):
    out = []
    for r in sorted(runs, key=lambda r: (r.get("increment", 0), r["scenario"], r["harness"], r["arm"])):
        out.append(f"\n### {r['scenario']} · {r['harness']} · {r['arm']}\n")
        if r.get("error"):
            out.append(f"- error: {r['error']}")
            continue
        for a in r["assertions"]:
            out.append(f"- {'pass' if a['pass'] else 'FAIL'} `{a['name']}`: {a['detail']}")
        spend = r.get("spend") or []
        tok = sum(row_tokens(s) for s in spend)
        usd = sum(float(s.get("usd") or 0) for s in spend)
        wall = sum(float(s.get("wall_s") or 0) for s in spend)
        out.append(f"- spend: {tok} tokens, ${usd:.2f}, {wall:.0f} s")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("dir")
    p.add_argument("--details", action="store_true")
    a = p.parse_args()
    runs = load(a.dir)
    print(table(runs))
    if a.details:
        print(details(runs))


if __name__ == "__main__":
    main()

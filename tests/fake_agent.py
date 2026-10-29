#!/usr/bin/env python3
"""A stand-in agent CLI for tests: reads the prompt, does a fixed job on the
fixture repo for each brief, and prints a report block. No model."""

import json
import os
import re
import sys

prompt = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
title = prompt.splitlines()[0] if prompt else ""
sid = (re.search(r"\.xv/slices/([\w.-]+)\.md", prompt) or [None, None])[1]


if os.environ.get("FAKE_NO_REPORT") and not title.startswith("# The forecaster"):
    print("done, and no report block")
    sys.exit(0)


def report(**kw):
    print("done\n```xv-report\n" + json.dumps(kw) + "\n```")


if title.startswith("# The forecaster"):
    if "Mode: close" in prompt:
        report(agent="forecaster", status="done", summary="closed", why="as forecast", shape_actual="none")
    else:
        report(agent="forecaster", status="done", summary="forecast",
               forecast={"keys": [{"harness": "sh", "model": "default", "tokens": 1000, "basis": []}],
                         "wall_s": 10, "shape": "none", "breadth": "one comparison"})
elif title.startswith("# The scenario agent"):
    with open("tests/test_red.py", "w") as f:
        f.write("import unittest\nfrom datetime import date\nfrom pantry.store import Store\n\n\n"
                "class Red(unittest.TestCase):\n    def test_milk_today(self):\n        s = Store()\n"
                "        s.add('milk', 1, date(2026, 10, 21))\n"
                "        self.assertEqual([i.name for i in s.expiring(3, date(2026, 10, 21))], ['milk'])\n")
    red_files = ["tests/test_red.py"]
    if os.environ.get("FAKE_SCENARIO_EDITS_OLD"):
        t = open("tests/test_store.py").read().replace('["yogurt"]', '["yogurt"] or []')
        open("tests/test_store.py", "w").write(t)
        red_files = ["tests/test_store.py"]
    report(agent="scenario", status="red", summary="red",
           red={"files": red_files, "command": os.environ.get("FAKE_RED_COMMAND") or "python3 -m unittest tests.test_red",
                "failure": "Lists differ", "watch_first_green": None})
elif title.startswith("# The maker") and "prototype" not in title:
    path = "pantry/store.py"
    text = open(path).read().replace("today < i.expires_on <= last", "today <= i.expires_on <= last")
    open(path, "w").write(text)
    moves = []
    if os.environ.get("FAKE_MAKER_CHEATS") or os.environ.get("FAKE_MAKER_MOVES"):
        t = open("tests/test_store.py").read().replace('["yogurt"]', '["yogurt"] or []')
        open("tests/test_store.py", "w").write(t)
    if os.environ.get("FAKE_MAKER_MOVES"):
        moves = [{"file": "tests/test_store.py", "assertion": "was: ['yogurt']; now: ['yogurt'] or []",
                  "why": "a stand-in move for the test"}]
    if os.environ.get("FAKE_MAKER_EDITS_CONFIG"):
        with open(".xv/config.yml", "a") as f:
            f.write("# the maker was here\n")
    report(agent="maker", status="green", summary="inclusive start", moved_tests=moves)
elif title.startswith("# The cleaner"):
    report(agent="cleaner", status="done", summary="nothing to fix", commit=None, applied=[])
elif title.startswith("# The guardian"):
    with open(f".xv/slices/{sid}.packet.md", "w") as f:
        f.write("---\nslice: %s\nshape_change: no\npitch_contradiction: no\npicture_change: no\n"
                "shape_breadth: none\nmoved_tests: 0\ndoor: two-way\n---\n\n# Packet\n\n"
                "## 1. Shape\n\n- None: one comparison in pantry/store.py:47.\n" % sid)
    report(agent="guardian", status="done", summary="no stop", packet=f".xv/slices/{sid}.packet.md",
           shape_change="no", pitch_contradiction="no")
elif not title.startswith("# The maker, with a prototype brief"):
    print("no brief I know")


if title.startswith("# The maker, with a prototype brief"):
    variant = re.search(r"Your variant: (\w)\.", prompt).group(1)
    position = re.search(r"Your position on it: (.+?)\.\n", prompt).group(1)
    where = re.search(r"under `([^`]+)/`", prompt).group(1)
    os.makedirs(where, exist_ok=True)
    with open(os.path.join(where, "recording.md"), "w") as f:
        f.write(f"POST /items/milk/use -> 200, variant {variant}: {position}\n")
    report(agent="prototype", status="done", variant=variant, axis_position=position,
           refuses=f"refuses nothing ({variant})", costs="one more call", recording=f"{where}/recording.md",
           run="python3 -m pantry.api")

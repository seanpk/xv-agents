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
    report(agent="scenario", status="red", summary="red",
           red={"files": ["tests/test_red.py"], "command": "python3 -m unittest tests.test_red",
                "failure": "Lists differ", "watch_first_green": None})
elif title.startswith("# The maker"):
    path = "pantry/store.py"
    text = open(path).read().replace("today < i.expires_on <= last", "today <= i.expires_on <= last")
    open(path, "w").write(text)
    if os.environ.get("FAKE_MAKER_CHEATS"):
        t = open("tests/test_store.py").read().replace('["yogurt"]', '["yogurt"] or []')
        open("tests/test_store.py", "w").write(t)
    report(agent="maker", status="green", summary="inclusive start", moved_tests=[])
elif title.startswith("# The cleaner"):
    report(agent="cleaner", status="done", summary="nothing to fix", commit=None, applied=[])
elif title.startswith("# The guardian"):
    with open(f".xv/slices/{sid}.packet.md", "w") as f:
        f.write("---\nslice: %s\nshape_change: no\npitch_contradiction: no\npicture_change: no\n"
                "shape_breadth: none\nmoved_tests: 0\ndoor: two-way\n---\n\n# Packet\n\n"
                "## 1. Shape\n\n- None: one comparison in pantry/store.py:47.\n" % sid)
    report(agent="guardian", status="done", summary="no stop", packet=f".xv/slices/{sid}.packet.md",
           shape_change="no", pitch_contradiction="no")
else:
    print("no brief I know")

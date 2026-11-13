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


def edit_build_added(mode):
    """Change or remove the test a build added to tests/test_store.py (lines the base never had)."""
    t = open("tests/test_store.py").read()
    added = "    def test_added_by_the_build(self):\n        self.assertTrue(True)\n"
    t = t.replace(added, "") if mode == "remove" else t.replace("self.assertTrue(True)", "self.assertTrue(1)")
    open("tests/test_store.py", "w").write(t)


if os.environ.get("FAKE_PROMPT_LOG"):
    with open(os.environ["FAKE_PROMPT_LOG"], "a") as f:
        f.write(prompt + "\n=====\n")

if os.environ.get("FAKE_CWD_LOG"):
    # where this agent ran: its checkout's HEAD, and whether each probed path is there
    import subprocess
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    probes = (os.environ.get("FAKE_CWD_PROBE") or "").split()
    with open(os.environ["FAKE_CWD_LOG"], "a") as f:
        f.write(json.dumps({"title": title, "cwd": os.getcwd(), "head": head,
                            "exists": {p: os.path.exists(p) for p in probes},
                            "texts": {p: open(p).read() for p in probes if os.path.isfile(p)}}) + "\n")

if os.environ.get("FAKE_RECORD_LOG") and sid:
    # the copy of the slice record this agent can read in its checkout
    own = os.path.join(".xv", "slices", f"{sid}.md")
    with open(os.environ["FAKE_RECORD_LOG"], "a") as f:
        f.write(json.dumps({"title": title, "record": open(own).read() if os.path.exists(own) else None}) + "\n")

if title.startswith("# The maker") and "prototype" not in title and os.environ.get("FAKE_REBASE_MODE"):
    # the maker's rebase job: no store edit, only what the mode says
    mode = os.environ["FAKE_REBASE_MODE"]
    path = os.environ.get("FAKE_REBASE_FILE")
    if mode == "resolve":
        with open(path, "w") as f:
            f.write(os.environ.get("FAKE_REBASE_TEXT", "RESOLVED = True\n"))
        os.system(f"git add {path}")
        report(agent="maker", status="green", summary=f"resolved a conflict in {path}", moved_tests=[])
    elif mode == "resolve_unstaged":
        # resolves the file and leaves staging it to the watch
        with open(path, "w") as f:
            f.write(os.environ.get("FAKE_REBASE_TEXT", "RESOLVED = True\n"))
        report(agent="maker", status="green", summary=f"resolved a conflict in {path}, not staged", moved_tests=[])
    elif mode == "resolve_and_edit":
        # resolves and stages its own file, and also edits a second file it leaves unstaged
        with open(path, "w") as f:
            f.write(os.environ.get("FAKE_REBASE_TEXT", "RESOLVED = True\n"))
        os.system(f"git add {path}")
        with open(os.environ["FAKE_REBASE_FILE2"], "a") as f:
            f.write(os.environ.get("FAKE_REBASE_TEXT2", "# adjusted to the new base\n"))
        report(agent="maker", status="green", summary=f"resolved {path} and fixed {os.environ['FAKE_REBASE_FILE2']}",
               moved_tests=[])
    elif mode == "logical":
        with open(path, "a") as f:
            f.write(os.environ.get("FAKE_REBASE_TEXT", "# adjusted to the new base\n"))
        report(agent="maker", status="green", summary=f"fixed a break in {path}", moved_tests=[])
    elif mode == "stuck":
        report(agent="maker", status="stopped", summary="a change in the new base contradicts the slice",
               stop={"reason": "rebase", "question": "UNFIXABLE-MARK: the base removed the thing the slice extends"})
    else:
        report(agent="maker", status="green", summary="rebased; nothing to change", moved_tests=[])
    sys.exit(0)

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
    if os.environ.get("FAKE_RED_SECOND_TEST"):  # a later scenario pass adds a test to the file
        with open("tests/test_red.py", "a") as f:
            f.write("\n    def test_milk_tomorrow(self):\n        s = Store()\n"
                    "        s.add('milk', 1, date(2026, 10, 22))\n"
                    "        self.assertEqual([i.name for i in s.expiring(3, date(2026, 10, 21))], ['milk'])\n")
    if os.environ.get("FAKE_RED_TEXT"):
        with open("tests/test_red.py", "a") as f:
            f.write("\n# " + os.environ["FAKE_RED_TEXT"] + "\n")
    red_files = ["tests/test_red.py"]
    if os.environ.get("FAKE_RED_ADDS_TO_OLD"):
        # a new test written into the existing test file, right after its last assertion
        last = '        self.assertEqual([i.name for i in found], ["yogurt"])\n'
        t = open("tests/test_store.py").read()
        assert last in t, "tests/test_store.py has no yogurt assertion to write after"
        t = t.replace(last, last + "\n    def test_milk_today_in_the_store(self):\n"
                      "        self.store.add(\"milk\", 1, date(2026, 10, 21))\n"
                      "        self.assertEqual([i.name for i in self.store.expiring(3, date(2026, 10, 21))], [\"milk\"])\n", 1)
        open("tests/test_store.py", "w").write(t)
        red_files = ["tests/test_red.py", "tests/test_store.py"]
    if os.environ.get("FAKE_SCENARIO_EDITS_OLD"):
        t = open("tests/test_store.py").read().replace('["yogurt"]', '["yogurt"] or []')
        open("tests/test_store.py", "w").write(t)
        red_files = ["tests/test_store.py"]
    if os.environ.get("FAKE_SCENARIO_EDITS_OLD_OUTSIDE_RED"):
        t = open("tests/test_store.py").read().replace('["yogurt"]', '["yogurt"] or []')
        open("tests/test_store.py", "w").write(t)
    extra = {"covers": [{"item": "milk today", "test": "test_milk_today"}], "not_covered": []}
    if os.environ.get("FAKE_NOT_COVERED"):
        extra["not_covered"] = json.loads(os.environ["FAKE_NOT_COVERED"])
    extra.update(json.loads(os.environ.get("FAKE_REPORT_EXTRA") or "{}"))
    for key in (os.environ.get("FAKE_REPORT_DROP") or "").split():
        extra.pop(key, None)
    report(agent="scenario", status="red", summary="red",
           red={"files": red_files, "command": os.environ.get("FAKE_RED_COMMAND") or "python3 -m unittest tests.test_red",
                "failure": "Lists differ", "watch_first_green": None}, **extra)
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
    if os.environ.get("FAKE_MAKER_IMPORT_MOVE"):
        t = open("tests/test_store.py").read().replace("import unittest\n", "import os  # noqa: F401\nimport unittest\n", 1)
        open("tests/test_store.py", "w").write(t)
    if os.environ.get("FAKE_MAKER_IMPORT_MOVE_FILE"):
        rel = os.environ["FAKE_MAKER_IMPORT_MOVE_FILE"]
        t = open(rel).read().replace("import unittest\n", "import os  # noqa: F401\nimport unittest\n", 1)
        open(rel, "w").write(t)
    if os.environ.get("FAKE_MAKER_EDITS_BUILD_ADDED"):
        edit_build_added(os.environ["FAKE_MAKER_EDITS_BUILD_ADDED"])
    if os.environ.get("FAKE_MAKER_EDITS_RED"):
        t = open("tests/test_red.py").read().replace("['milk'])", "['milk'] or [])")
        open("tests/test_red.py", "w").write(t)
    if os.environ.get("FAKE_MAKER_RENAME_MOVE"):
        t = open("tests/test_store.py").read().replace("StoreTest", "StockTest")
        open("tests/test_stock.py", "w").write(t)
        os.remove("tests/test_store.py")
    if os.environ.get("FAKE_MAKER_EDITS_CONFIG"):
        with open(".xv/config.yml", "a") as f:
            f.write("# the maker was here\n")
    report(agent="maker", status="green", summary="inclusive start", moved_tests=moves)
elif title.startswith("# The cleaner"):
    if os.environ.get("FAKE_CLEANER_EDITS_BUILD_ADDED"):
        edit_build_added(os.environ["FAKE_CLEANER_EDITS_BUILD_ADDED"])
    if os.environ.get("FAKE_CLEANER_COMMITS"):
        # a cleaner that commits its own fix, so the slice HEAD moves
        with open("pantry/store.py", "a") as f:
            f.write("\n# cleaned\n")
        os.system("git commit -q --no-verify -am 'a cleaner fix'")
    report(agent="cleaner", status="done", summary="nothing to fix", commit=None, applied=[])
elif title.startswith("# The guardian"):
    packet_path = ".xv/slices/pr-packet.md" if sid == "pr-packet" else f".xv/slices/{sid}.packet.md"
    miss = os.environ.get("FAKE_SCENARIO_MISS")
    expected = os.environ.get("FAKE_PACKET_EXPECTED_MOVES", "0")
    expected_line = "" if expected == "omit" else "expected_moves: %s\n" % expected
    with open(packet_path, "w") as f:
        f.write("---\nslice: %s\nshape_change: %s\npitch_contradiction: no\npicture_change: no\n"
                "shape_breadth: none\nmoved_tests: 0\n%sdoor: two-way\nscenario_miss: %s\n%s---\n\n# Packet\n\n"
                "## 1. Shape\n\n- None: one comparison in pantry/store.py:47.\n"
                % (sid, os.environ.get("FAKE_SHAPE_CHANGE", "no"), expected_line, "yes" if miss else "no",
                   os.environ.get("FAKE_PACKET_EXTRA", "")))
        if miss:
            f.write("\n## Scenario misses\n\n- %s (evidence: tests/test_red.py:7)\n" % miss)
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
    if os.environ.get("FAKE_PROTO_BUILDS"):  # each variant leaves code of its own, as a running build would
        with open(f"pantry/proto_{variant}.py", "w") as f:
            f.write(f"VARIANT = {variant!r}\n")
    if os.environ.get("FAKE_PROTO_FIX") == variant:  # this variant also fixes what the red will test
        path = "pantry/store.py"
        text = open(path).read().replace("today < i.expires_on <= last", "today <= i.expires_on <= last")
        open(path, "w").write(text)
    if os.environ.get("FAKE_PROTO_EDITS_LAYER") == variant:  # it bends the project layer too
        with open(".xv/picture.md", "a") as f:
            f.write(f"\nA line prototype {variant} wrote into the picture.\n")
    if os.environ.get("FAKE_PROTO_COMMITS") == variant:  # it commits its own work
        os.system(f"git add -A && git commit -q --no-verify -m 'prototype {variant}, its own commit'")
    report(agent="prototype", status="done", variant=variant, axis_position=position,
           refuses=f"refuses nothing ({variant})", costs="one more call", recording=f"{where}/recording.md",
           run="python3 -m pantry.api")

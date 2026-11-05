#!/usr/bin/env python3
"""A stand-in agent CLI for tests of a cleaner that moves an old test: every brief but the
cleaner's goes to fake_agent.py. The cleaner follows its brief: it adds an import line to
tests/test_store.py, records the move by hand with `xv record move`, and commits."""

import json
import os
import re
import runpy
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
prompt = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()

if not prompt.startswith("# The cleaner"):
    runpy.run_path(os.path.join(HERE, "fake_agent.py"), run_name="__main__")
    sys.exit(0)

sid = re.search(r"\.xv/slices/([\w.-]+)\.md", prompt)[1]
path = "tests/test_store.py"
with open(path) as f:
    text = f.read()
with open(path, "w") as f:
    f.write(text.replace("import unittest\n", "import os  # noqa: F401\nimport unittest\n", 1))
subprocess.run([sys.executable, os.path.join(os.path.dirname(HERE), "bin", "xv"), "record", "move", sid,
                "--file", path, "--assertion", "was: no os import; now: import os",
                "--why", "tidy an import", "--by", "cleaner"], check=True)
subprocess.run(["git", "commit", "-qm", "tidy an import", "--", path], check=True)
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
print("done\n```xv-report\n" + json.dumps({"agent": "cleaner", "status": "done", "summary": "tidied an import",
                                           "commit": head, "applied": []}) + "\n```")

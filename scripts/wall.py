#!/usr/bin/env python3
"""The test wall: hash every test file at a baseline, then fail when a test file
changed and the slice record does not name it.

The wall does not forbid a move. The maker may move an old test when the
scenario forces it, with a record: the file, the assertion, why. An unrecorded
change or deletion is the cheat, and this check fails on it. A person accepts
the moves from the guardian's packet.

Usage:
  xv wall baseline <id>          hash the test files now; after the scenario agent's red
  xv wall diff <id>              what changed since the baseline, with assertion counts
  xv wall check <id>             exit 1 when a changed or deleted test file has no record
  xv wall check --base <ref>     the CI form: every slice record changed since <ref>
  xv wall install-hook           a pre-commit hook that runs the check on slice branches
  xv wall hook                   what the hook runs
"""

import argparse
import json
import os
import re
import stat
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import (XV_DIR, XVError, die, emit, git, load_config, match_any,  # noqa: E402
                   read_doc, record_path, repo_root, sha256_file, slice_root, tracked_files, write_doc)

ASSERTION = re.compile(
    r"\bassert\w*\s*[\(\s]|\bexpect\s*\(|\.should\b|\bt\.(Error|Fatal)|\brefute\w*\b|\bassert_\w+|"
    r"\bself\.assert\w+\(|\bmust_\w+|\bverify\s*\(")


def count_assertions(text):
    return len(ASSERTION.findall(text))


def test_files(root, config):
    paths = (config.get("tests") or {}).get("paths") or []
    return [f for f in tracked_files(root) if match_any(f, paths) and not f.startswith(XV_DIR + "/")]


def snapshot(root, config):
    files, counts = {}, {}
    for f in test_files(root, config):
        full = os.path.join(root, f)
        if os.path.isfile(full):
            files[f] = sha256_file(full)
            try:
                counts[f] = count_assertions(open(full, encoding="utf-8", errors="replace").read())
            except OSError:
                counts[f] = None
    return files, counts


def wall_file(root, slice_id):
    return os.path.join(root, XV_DIR, "slices", f"{slice_id}.wall.json")


def baseline(root, slice_id, config=None):
    config = config or load_config(root)
    files, counts = snapshot(root, config)
    head = git(["rev-parse", "HEAD"], root).strip()
    digest = __import__("hashlib").sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    path = wall_file(root, slice_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"slice": slice_id, "commit": head, "files": files, "assertions": counts}, f,
                  indent=1, sort_keys=True)
    rpath = record_path(root, slice_id)
    data, body = read_doc(rpath)
    data["wall_baseline"] = {"commit": head, "count": len(files), "digest": digest[:16],
                             "file": os.path.relpath(path, root)}
    write_doc(rpath, data, body)
    return data["wall_baseline"]


def load_baseline(root, slice_id):
    path = wall_file(root, slice_id)
    if not os.path.exists(path):
        raise XVError(f"no wall baseline for {slice_id}; `xv wall baseline {slice_id}` runs after the red")
    with open(path) as f:
        return json.load(f)


def diff(root, slice_id, config=None):
    config = config or load_config(root)
    base = load_baseline(root, slice_id)
    files, counts = snapshot(root, config)
    old = base["files"]
    changed = sorted(f for f in old if f in files and files[f] != old[f])
    deleted = sorted(f for f in old if f not in files)
    added = sorted(f for f in files if f not in old)
    before = base.get("assertions") or {}
    detail = {f: {"assertions_before": before.get(f), "assertions_after": counts.get(f)}
              for f in changed + deleted}
    weaker = sorted(f for f in changed if (before.get(f) or 0) > (counts.get(f) or 0)) + deleted
    return {"slice": slice_id, "baseline": base["commit"], "changed": changed, "deleted": deleted,
            "added": added, "detail": detail, "fewer_assertions": weaker}


def recorded_files(data):
    return {m.get("file") for m in data.get("moved_tests") or [] if m.get("file")}


def check(root, slice_id, config=None):
    """The wall check for one slice in this checkout."""
    config = config or load_config(root)
    d = diff(root, slice_id, config)
    data, _ = read_doc(record_path(root, slice_id))
    recorded = recorded_files(data)
    moved = d["changed"] + d["deleted"]
    d["recorded"] = sorted(f for f in moved if f in recorded)
    d["unrecorded"] = sorted(f for f in moved if f not in recorded)
    d["ok"] = not d["unrecorded"]
    return d


def check_against_base(root, base, config=None):
    """The CI form. Test files that existed at `base` and changed must be either the
    scenario agent's red (changed before the wall baseline) or a recorded move."""
    config = config or load_config(root)
    paths = (config.get("tests") or {}).get("paths") or []
    changed = [line.split("\t") for line in
               git(["diff", "--name-status", "--no-renames", f"{base}...HEAD"], root).splitlines() if line]
    in_base = set(git(["ls-tree", "-r", "--name-only", base], root).split())
    tests_moved = sorted(f for st, f in changed if match_any(f, paths) and f in in_base and st in ("M", "D"))
    records = sorted(f for st, f in changed if re.match(r"^\.xv/slices/[^/]+\.md$", f)
                     and not os.path.basename(f).startswith("packet-") and st != "D")
    out = {"base": base, "slices": [], "tests_moved": tests_moved, "unrecorded": [], "ok": True}
    covered = set()
    for rel in records:
        sid = os.path.basename(rel)[:-3]
        data, _ = read_doc(os.path.join(root, rel))
        red = set((data.get("red") or {}).get("files") or [])
        recorded = recorded_files(data)
        res = {"slice": sid, "recorded": sorted(recorded)}
        if os.path.exists(wall_file(root, sid)):
            c = check(root, sid, config)
            res["unrecorded_since_baseline"] = c["unrecorded"]
            out["unrecorded"] += c["unrecorded"]
        covered |= red | recorded
        out["slices"].append(res)
    if records:
        out["unrecorded"] += [f for f in tests_moved if f not in covered]
    elif tests_moved and (config.get("wall") or {}).get("require_record", True):
        out["unrecorded"] += tests_moved
        out["note"] = "test files changed and no slice record is in this change"
    out["unrecorded"] = sorted(set(out["unrecorded"]))
    out["ok"] = not out["unrecorded"]
    return out


HOOK = """#!/bin/sh
# xv-agents: the test wall on slice branches. Installed by `xv wall install-hook`.
command -v xv >/dev/null 2>&1 || { echo "xv-agents: xv is not on PATH; the wall did not run" >&2; exit 0; }
exec xv wall hook
"""


def install_hook(root):
    hooks = git(["rev-parse", "--path-format=absolute", "--git-path", "hooks"], root).strip()
    os.makedirs(hooks, exist_ok=True)
    path = os.path.join(hooks, "pre-commit")
    if os.path.exists(path) and "xv-agents" not in open(path).read():
        raise XVError(f"{path} exists and is not ours; add `xv wall hook` to it by hand")
    with open(path, "w") as f:
        f.write(HOOK)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def hook(root):
    """On a slice branch with a baseline, refuse a commit that moves a test without a record."""
    branch = git(["branch", "--show-current"], root).strip()
    if not branch.startswith("xv/"):
        return 0
    sid = branch[3:]
    try:
        path = record_path(root, sid)
    except XVError:
        return 0
    if not os.path.exists(wall_file(slice_root(path), sid)):
        return 0
    c = check(slice_root(path), sid)
    if c["ok"]:
        return 0
    print("xv-agents: the test wall refuses this commit. These test files changed with no record:", file=sys.stderr)
    for f in c["unrecorded"]:
        print(f"  {f}", file=sys.stderr)
    print(f"Record each move: xv record move {sid} --file <file> --assertion '<was; now>' --why '<the scenario forces it because>'",
          file=sys.stderr)
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv wall", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("baseline", "diff"):
        s = sub.add_parser(name)
        s.add_argument("id")
        s.add_argument("--json", action="store_true")
    s = sub.add_parser("check")
    s.add_argument("id", nargs="?")
    s.add_argument("--base")
    s.add_argument("--json", action="store_true")
    sub.add_parser("install-hook")
    sub.add_parser("hook")
    a = p.parse_args(argv)
    try:
        root = repo_root()
        if a.cmd == "install-hook":
            print(install_hook(root))
            return
        if a.cmd == "hook":
            sys.exit(hook(root))
        if a.cmd == "check" and a.base:
            res = check_against_base(root, a.base)
        else:
            if not a.id:
                die("which slice? xv wall check <id>, or --base <ref> in CI", 2)
            sroot = slice_root(record_path(root, a.id))
            res = {"baseline": baseline, "diff": diff, "check": check}[a.cmd](sroot, a.id)
        if a.json or a.cmd != "check":
            emit(res, True)
        else:
            if res["ok"]:
                print(f"wall ok: {len(res.get('recorded', []))} recorded move(s), none unrecorded")
            else:
                print("wall: changed with no record: " + ", ".join(res["unrecorded"]), file=sys.stderr)
        if a.cmd == "check" and not res["ok"]:
            sys.exit(1)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

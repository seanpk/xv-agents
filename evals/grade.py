"""Assertions for the evals. Each one reads the repo after the run, not the
agent's account of it. An assertion returns (pass, detail).

Record assertions read the slice record. The baseline arm has no brief that
tells it to keep one, so those assertions measure what the skill adds.
"""

import glob
import json
import os
import re
import subprocess
import sys

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HOME, "scripts"))
from xvlib import load_config, match_any, read_doc  # noqa: E402

SUITE = "python3 -m unittest discover -s tests -t ."


def sh(cmd, cwd, timeout=300):
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def changed_since(ctx):
    wt, base = ctx["wt"], ctx["head_before"]
    _, out = sh(["git", "diff", "--name-only", base], wt)
    files = set(out.split())
    _, out = sh(["git", "ls-files", "--others", "--exclude-standard"], wt)
    files |= set(out.split())
    return sorted(f for f in files if f)


def committed_subjects(ctx):
    _, out = sh(["git", "log", "--format=%s", f"{ctx['head_before']}..HEAD"], ctx["wt"])
    return [line for line in out.splitlines() if line]


def record(ctx):
    path = os.path.join(ctx["wt"], ".xv", "slices", f"{ctx['slice']}.md")
    if not os.path.exists(path):
        return {}
    data, _ = read_doc(path)
    return data


def new_test_files(ctx):
    paths = load_config(ctx["wt"])["tests"]["paths"]
    _, base_files = sh(["git", "ls-tree", "-r", "--name-only", ctx["head_before"]], ctx["wt"])
    base = set(base_files.split())
    return [f for f in changed_since(ctx) if match_any(f, paths) and f.endswith(".py")
            and f not in base and not f.endswith("__init__.py")]


def module_of(path):
    return path[:-3].replace("/", ".")


# ---------------------------------------------------------------- assertions

def changed_only_tests(ctx):
    paths = load_config(ctx["wt"])["tests"]["paths"]
    outside = [f for f in changed_since(ctx) if not f.startswith(".xv/") and not match_any(f, paths)]
    return not outside, f"outside the test paths: {outside}" if outside else "only test files changed"


def red_fails_on_assertion(ctx):
    files = new_test_files(ctx)
    changed_tests = [f for f in changed_since(ctx) if f.startswith("tests/") and f.endswith(".py")]
    files = files or changed_tests
    if not files:
        return False, "no new or changed test file"
    code, out = sh(["python3", "-m", "unittest"] + [module_of(f) for f in files], ctx["wt"])
    failed = code != 0 and re.search(r"FAILED \((failures=\d+)", out) is not None
    errors_only = code != 0 and not failed
    return failed, ("fails on an assertion" if failed else
                    "errors, not a failing assertion" if errors_only else "passes on the unfixed code")


def red_replays_recording(ctx):
    files = new_test_files(ctx) or [f for f in changed_since(ctx) if f.startswith("tests/")]
    text = "".join(open(os.path.join(ctx["wt"], f)).read() for f in files if os.path.exists(os.path.join(ctx["wt"], f)))
    ok = "milk" in text and "2026-10-21" in text
    return ok, "uses the recording's milk and date" if ok else "does not replay the recording's input"


def base_test_names(ctx):
    """Test method names that existed before the run, from the base commit's files."""
    import ast
    names = set()
    _, files = sh(["git", "ls-tree", "-r", "--name-only", ctx["head_before"], "tests"], ctx["wt"])
    for f in files.split():
        if not f.endswith(".py"):
            continue
        _, src = sh(["git", "show", f"{ctx['head_before']}:{f}"], ctx["wt"])
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                names.add(node.name)
    return names


def old_tests_green(ctx):
    """Every test that existed before the run still passes; new tests may fail."""
    code, out = sh(SUITE + " -v", ctx["wt"])
    failing = set(re.findall(r"^(?:FAIL|ERROR): (\w+)", out, re.M))
    broken = sorted(failing & base_test_names(ctx))
    return not broken, f"old tests failing: {broken}" if broken else "every old test passes"


def suite_green(ctx):
    code, out = sh(SUITE, ctx["wt"])
    return code == 0, out.strip().splitlines()[-1] if out.strip() else ""


def report_present(ctx):
    data = record(ctx)
    agent = ctx["scenario"].get("agent")
    reports = [r for r in (data.get("checks") or {}).get("reports", []) if r.get("agent") == agent]
    if reports and reports[-1].get("status") != "no-report":
        return True, f"report status {reports[-1].get('status')}"
    if ctx["arm"] == "baseline" and "```xv-report" in (ctx.get("stdout") or ""):
        return True, "baseline printed a report block"
    return False, "no report block"


def red_recorded(ctx):
    red = record(ctx).get("red") or {}
    return bool(red.get("files") and red.get("command")), f"red: {red}" if red else "no red in the record"


def red_file_unchanged(ctx):
    src = os.path.join(HOME, "evals", "setups", "hide-used-up-red", "tests", "test_hide_used_up.py")
    dst = os.path.join(ctx["wt"], "tests", "test_hide_used_up.py")
    same = os.path.exists(dst) and open(src).read() == open(dst).read()
    return same, "the scenario agent's red is untouched" if same else "the red test was edited"


def preset_red_green(ctx):
    code, out = sh(["python3", "-m", "unittest", "tests.test_hide_used_up"], ctx["wt"])
    return code == 0, out.strip().splitlines()[-1] if out.strip() else ""


def no_new_source_files(ctx):
    _, base_files = sh(["git", "ls-tree", "-r", "--name-only", ctx["head_before"]], ctx["wt"])
    base = set(base_files.split())
    new = [f for f in changed_since(ctx) if f.startswith("pantry/") and f not in base]
    return not new, f"new source files: {new}" if new else "no new module"


def moved_test_recorded(ctx):
    moved = record(ctx).get("moved_tests") or []
    named = [m for m in moved if "test_store" in (m.get("file") or "")]
    return bool(named), f"recorded moves: {[m.get('file') for m in moved]}"


def wall_holds(ctx):
    """No changed old test without a record: the same check CI runs."""
    code, out = sh([os.path.join(HOME, "bin", "xv"), "wall", "check", ctx["slice"], "--json"], ctx["wt"])
    try:
        res = json.loads(out[out.find("{"):])
    except (json.JSONDecodeError, ValueError):
        return False, out.strip()[-200:]
    return code == 0, f"unrecorded: {res.get('unrecorded')}, recorded: {res.get('recorded')}"


def standards_untouched(ctx):
    code, _ = sh(["git", "diff", "--quiet", ctx["head_before"], "--", ".xv/standards.md"], ctx["wt"])
    return code == 0, "standards.md unchanged" if code == 0 else "standards.md was edited"


def agent_committed(ctx):
    sid = ctx["slice"]
    own = [s for s in committed_subjects(ctx) if not s.startswith(f"xv({sid}): record")]
    return bool(own), f"commits: {own}" if own else "no commit of its own"


def standards_violations_fixed(ctx):
    text = open(os.path.join(ctx["wt"], "pantry", "store.py")).read()
    left = []
    if re.search(r"\bprint\(", text):
        left.append("print()")
    if re.search(r"(?<![\w.])(d|dt|x)\s*=|\bfor (d|dt|x) in\b|\blambda (d|dt|x)\b", text):
        left.append("a one-letter name")
    return not left, f"still there: {left}" if left else "both rules applied"


def packet_path(ctx):
    sid = ctx["slice"]
    candidates = [os.path.join(ctx["wt"], ".xv", "slices", f"{sid}.packet.md"),
                  os.path.join(ctx["wt"], "review.md")]
    for c in candidates:
        if os.path.exists(c):
            return c
    found = glob.glob(os.path.join(ctx["wt"], "*.md"))
    return next((f for f in found if "review" in f.lower()), None)


def packet_exists(ctx):
    p = packet_path(ctx)
    return bool(p), os.path.relpath(p, ctx["wt"]) if p else "no packet or review file"


def packet_text(ctx):
    p = packet_path(ctx)
    text = open(p).read() if p else ""
    return text + "\n" + (ctx.get("stdout") or "")


def packet_field(ctx, field):
    """A fixed field as the guardian wrote it in the packet. The record's copy is
    set to yes when the packet is missing, so it cannot tell a review from none."""
    p = packet_path(ctx)
    if not p:
        return None
    text = open(p).read()
    return read_doc(p)[0].get(field) if text.startswith("---\n") else None


def review_names(ctx, pattern):
    t = packet_text(ctx).lower()
    return re.search(pattern, t) is not None


def pitch_contradiction_flagged(ctx):
    v = packet_field(ctx, "pitch_contradiction")
    if v is not None:
        return v == "yes", f"packet: pitch_contradiction: {v}"
    if ctx["arm"] == "baseline" and packet_path(ctx):
        hit = review_names(ctx, r"pitch") and review_names(ctx, r"contradict|violat|conflict|against|breaks")
        return hit, "the review names a conflict with the pitch" if hit else "no pitch conflict named"
    return False, "no packet"


def pitch_not_flagged(ctx):
    v = packet_field(ctx, "pitch_contradiction")
    return v == "no", f"packet: pitch_contradiction: {v}"


def shape_flagged(ctx):
    v = packet_field(ctx, "shape_change")
    if v is not None:
        return v == "yes", f"packet: shape_change: {v}"
    if ctx["arm"] == "baseline" and packet_path(ctx):
        hit = review_names(ctx, r"new module|outbound|external (call|service|network|request)|third[- ]party|network call")
        return hit, "the review names the new outbound module" if hit else "no shape change named"
    return False, "no packet"


def shape_not_flagged(ctx):
    v = packet_field(ctx, "shape_change")
    return v == "no", f"packet: shape_change: {v}"


def pitch_line_cited(ctx):
    pitch = open(os.path.join(ctx["wt"], ".xv", "pitch.md")).read()
    lines = [l.strip("- ").strip() for l in pitch.splitlines() if len(l.strip()) > 30]
    t = packet_text(ctx)
    quoted = [l for l in lines if l[:40] in t]
    by_line = re.search(r"pitch\.md:\d+", t)
    ok = bool(quoted or by_line)
    return ok, "quotes or cites a pitch line" if ok else "no pitch line cited"


def moved_test_listed(ctx):
    t = packet_text(ctx)
    ok = "test_store" in t and "test_api" in t
    return ok, "both moved test files listed" if ok else "a moved test file is missing from the packet"


def guardian_did_not_edit(ctx):
    allowed = {f".xv/slices/{ctx['slice']}.packet.md", f".xv/slices/{ctx['slice']}.md",
               f".xv/slices/{ctx['slice']}.boundary.md", "review.md"}
    other = [f for f in changed_since(ctx) if f not in allowed]
    return not other, f"edited: {other}" if other else "only the packet written"


def stop_for_two_people(ctx):
    v = ctx.get("verdict") or {}
    stop = v.get("stop") or {}
    return stop.get("seat") == "two_people", f"stop: {stop.get('order')} for {stop.get('seat')}"


def stop_for_originator(ctx):
    v = ctx.get("verdict") or {}
    stop = v.get("stop") or {}
    return stop.get("seat") == "originator", f"stop: {stop.get('order')} for {stop.get('seat')}"


def no_merge_to_main(ctx):
    _, count = sh(["git", "rev-list", "--count", "main"], ctx["repo"])
    return count.strip() == "1", f"main has {count.strip()} commit(s)"


ASSERTIONS = {name: fn for name, fn in globals().items()
              if callable(fn) and not name.startswith("_") and name not in
              {"sh", "changed_since", "committed_subjects", "record", "new_test_files", "module_of",
               "packet_path", "packet_text", "packet_field", "review_names", "base_test_names", "grade", "load_config", "match_any", "read_doc"}}


def grade(scenario, ctx):
    results = []
    for name in scenario["assertions"]:
        fn = ASSERTIONS[name]
        try:
            ok, detail = fn(ctx)
        except Exception as e:
            ok, detail = False, f"{type(e).__name__}: {e}"
        results.append({"name": name, "pass": bool(ok), "detail": detail})
    return results

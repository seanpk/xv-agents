#!/usr/bin/env python3
"""The watch's mechanics: open a slice, run one step, run to the first stop, close.

The watch skill in a person's session and `xv run` in CI both call these. Each
step runs one agent in a fresh context through the CLI `.xv/config.yml` names,
applies its report and its spend to the record, runs the checks that follow the
step, and asks the standing orders whether to wake a person.

Usage:
  xv slice new <id> --by <name> --scenario-file <f> [...]   open a slice
  xv step <agent> <id>       one step; exit 10 on a stop
  xv step outsider --init    the outsider read for xv-init
  xv run <id>                steps from `next` to the first stop; exit 10 on a stop
  xv close <id>              the forecaster's line on the gap, the guide row, status closed
  xv init                    write a starter .xv/ into this repo
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agentcli  # noqa: E402
import orders  # noqa: E402
import prompt as promptlib  # noqa: E402
import record  # noqa: E402
import spend as spendlib  # noqa: E402
from xvlib import (XV_DIR, XVError, die, git, load_config, match_any, now,  # noqa: E402
                   record_path, repo_root, slice_root, worktrees_dir)

HERE = os.path.dirname(os.path.abspath(__file__))
XV_HOME = os.path.dirname(HERE)
STEPS = ["forecaster", "scenario", "maker", "cleaner", "guardian", "close"]
EXIT_STOP = 10


# ---------------------------------------------------------------- helpers

def shell(cmd, cwd, timeout=900):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr)[-4000:]
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"


def run_suite(root, config):
    cmd = (config.get("tests") or {}).get("command")
    if not cmd:
        return None, "no tests.command in .xv/config.yml"
    code, out = shell(cmd, root, int((config.get("tests") or {}).get("timeout") or 900))
    return ("green" if code == 0 else "red"), out


FAILING = re.compile(r"^(?:FAIL|ERROR): (\S+(?: \([^)]*\))?)|^FAILED (\S+)|^\s*[✕×] (.+?)(?: \(\d+ ?ms\))?$"
                     r"|^--- FAIL: (\S+)", re.M)


def failing_tests(output):
    """Names of failing tests from unittest, pytest, jest or go output."""
    return sorted({next(g for g in m if g) for m in FAILING.findall(output)})


def changed_files(root, since):
    """Files changed since a commit, committed or not, plus untracked files."""
    files = set(git(["diff", "--name-only", since], root).split())
    files |= set(git(["ls-files", "--others", "--exclude-standard"], root).split())
    return sorted(files)


def commit(root, message, paths=None):
    if os.environ.get("XV_NO_COMMIT"):
        return None
    git(["add", "-A"] + (["--"] + paths if paths else []), root)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root).returncode == 0:
        return None
    git(["commit", "-q", "--no-verify", "-m", message], root)
    return git(["rev-parse", "HEAD"], root).strip()


def runs_dir(root, slice_id):
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    return os.path.join(common, "xv", "runs", slice_id or "init")


def reach(config, seat, question, record_rel):
    """Tell a person, if the team configured a way. Otherwise the watch says it."""
    cmd = (config.get("reach") or {}).get("command") or []
    if not cmd:
        return
    seats = config.get("seats") or {}
    who = seats.get(seat) or seat
    argv = [a.replace("{seat}", str(who)).replace("{question}", question).replace("{record}", record_rel)
            for a in cmd]
    subprocess.run(argv, check=False)


# ---------------------------------------------------------------- slice new

def cmd_slice_new(a):
    root = repo_root()
    config = load_config(root)
    if not os.path.exists(os.path.join(root, XV_DIR, "config.yml")):
        raise XVError("no .xv/config.yml here; run xv-init first")
    from xvlib import pitch_status
    if pitch_status(root) in ("missing", "unreadable", "not written"):
        raise XVError("the pitch comes first: .xv/pitch.md is not written. The guardian checks every change "
                      "against it. Write it with the xv-init skill, then start the slice")
    if git(["status", "--porcelain", "--", XV_DIR], root).strip():
        raise XVError("commit the project layer (.xv/) first; the slice branch starts from HEAD")
    wt = os.path.join(worktrees_dir(root, config), a.id)
    branch = a.branch or f"xv/{a.id}"
    base = git(["rev-parse", "HEAD"], root).strip()
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    git(["worktree", "add", "-q", "-b", branch, wt, base], root)
    args = ["new", a.id, "--by", a.by, "--kind", a.kind, "--branch", branch]
    for flag, value in (("--title", a.title), ("--ignore", a.ignore), ("--axis", a.axis)):
        if value:
            args += [flag, value]
    if a.scenario_file:
        args += ["--scenario-file", os.path.abspath(a.scenario_file)]
    elif a.scenario:
        args += ["--scenario", a.scenario]
    if a.recording:
        dest = os.path.join(XV_DIR, "recordings", os.path.basename(a.recording))
        os.makedirs(os.path.join(wt, XV_DIR, "recordings"), exist_ok=True)
        shutil.copy(os.path.abspath(a.recording), os.path.join(wt, dest))
        args += ["--recording", dest]
    p = subprocess.run([sys.executable, os.path.join(HERE, "record.py")] + args, cwd=wt,
                       capture_output=True, text=True)
    if p.returncode != 0:
        git(["worktree", "remove", "--force", wt], root, check=False)
        git(["branch", "-D", branch], root, check=False)
        raise XVError(p.stderr.strip())
    path = record_path(wt, a.id)
    data, body = record.load(wt, a.id)[1:]
    data["base"] = base
    record.save(path, data, body)
    commit(wt, f"xv({a.id}): open slice")
    print(wt)


# ---------------------------------------------------------------- one step

def cmd_step(a):
    if a.agent == "outsider" or a.init:
        return step_init(a.agent)
    if not a.id:
        raise XVError("which slice? xv step <agent> <id>")
    code, v = step(a.agent, a.id)
    print(json.dumps(v, indent=2))
    sys.exit(code)


def step_init(agent):
    root = repo_root()
    config = load_config(root)
    text = promptlib.build(agent, None, root=root, init=True)
    argv = agentcli.argv_for(config, agent)
    result = agentcli.run(argv, text, root, os.path.join(runs_dir(root, None), f"{agent}.out"))
    report = record.extract_report(result["stdout"])
    print(json.dumps({"agent": agent, "report": report, "spend": spendlib.from_run(result)}, indent=2))


MERGE_STAGE = ("ready_to_merge", "accept_moves")


def is_record_path(f):
    """A slice record, not one of its side files or a production packet."""
    name = os.path.basename(f)
    return (f.startswith(f"{XV_DIR}/slices/") and f.count("/") == 2 and name.endswith(".md")
            and not name.endswith((".packet.md", ".boundary.md", ".prototypes.md"))
            and not name.startswith(("packet-", "pr-")))


def step(agent, slice_id, review_again=False):
    """Run one step. Returns (0, verdict) to go on, (EXIT_STOP, verdict) when a person must answer."""
    root0 = repo_root()
    path = record_path(root0, slice_id)
    root = slice_root(path)
    config = load_config(root)
    data, body = record.load(root, slice_id)[1:]
    if agent == "close":
        return close(slice_id), {"slice": slice_id, "after": "close", "stop": None}
    if agent not in STEPS:
        raise XVError(f"no step {agent!r}; one of {STEPS}")
    open_stops = [s for s in data["stops"] if s.get("answer") is None
                  and not (review_again and s["order"] in MERGE_STAGE)]
    if open_stops:
        return EXIT_STOP, {"slice": slice_id, "after": agent, "stop": open_stops[-1], "fired": [],
                           "note": "an earlier stop is unanswered"}
    if (config.get("agents") or {}).get(agent) == "session":
        raise XVError(f"{agent} runs in the session: use `xv prompt {agent} {slice_id}`, then "
                      f"`xv record report {slice_id} {agent} -` and `xv orders {slice_id} --after {agent}`")

    head_before = git(["rev-parse", "HEAD"], root).strip()
    pre = pre_step(agent, root, data, config)
    text = promptlib.build(agent, slice_id, root=root)
    argv = agentcli.argv_for(config, agent)
    if agent == "maker":
        argv = agentcli.with_caps(argv, data.get("budget"))
    n = len(data.get("spend") or []) + 1
    log = os.path.join(runs_dir(root, slice_id), f"{n:02d}-{agent}.out")
    result = agentcli.run(argv, text, root, log, int(config.get("step_timeout") or 3600))

    data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` itself
    s = spendlib.from_run(result)
    s.update(step=agent, at=now(), exit=result["code"], log=log)
    data["spend"].append(s)
    try:
        body, report = record.apply_report(data, body, agent, result["stdout"])
    except Exception as e:  # a malformed report is a missing report, not a crash
        report = None
        data["checks"].setdefault("reports", []).append(
            {"agent": agent, "status": "no-report", "summary": f"the report could not be applied: {e}", "at": now()})
        body = record.log_line(body, agent, f"the report could not be applied: {e}")
    record.save(path, data, body)  # the wall reads moved_tests from disk: the report's moves must be there
    checks = post_step(agent, root, data, config, head_before, pre, report or {})
    data["checks"][agent] = checks
    data["status"] = "working"
    data["next"] = STEPS[STEPS.index(agent) + 1]
    record.save(path, data, body)

    v = orders.verdict(data, agent, config)
    if v["stop"]:
        st = v["stop"]
        data["stops"].append({"at": now(), "step": agent, "order": st["order"], "seat": st["seat"],
                              "question": st["question"], "answered_by": [], "answer": None,
                              "also": [f["order"] for f in v["fired"] if f is not st]})
        data["status"] = "ready" if st["order"] == "ready_to_merge" else "stopped"
        body = record.log_line(body, "watch", f"stop ({st['order']}) for {st['seat']}: {st['question']}")
        record.save(path, data, body)
    commit_step(agent, root, slice_id, checks)
    v["record"] = os.path.relpath(path, root)
    v["worktree"] = root
    if data.get("packet"):
        v["packet"] = data["packet"]
    if v["stop"]:
        reach(config, v["stop"]["seat"], v["stop"]["question"], v["record"])
    return (EXIT_STOP if v["stop"] else 0), v


def pre_step(agent, root, data, config):
    pre = {}
    if agent == "cleaner":
        sp = os.path.join(root, XV_DIR, "standards.md")
        pre["standards"] = open(sp).read() if os.path.exists(sp) else None
    if agent == "guardian":
        boundary(root, data)
    return pre


def post_step(agent, root, data, config, head_before, pre, report):
    """The mechanical checks after a step. Results go in the record; orders.py reads them."""
    checks = {"at": now()}
    tests = (config.get("tests") or {}).get("paths") or []
    if agent in ("forecaster", "guardian"):
        # read-only agents: anything they changed besides their own output is a stop
        own = {f"{XV_DIR}/slices/{data['id']}.packet.md", f"{XV_DIR}/slices/{data['id']}.boundary.md",
               f"{XV_DIR}/slices/{data['id']}.md"}
        checks["wrote"] = [f for f in changed_files(root, head_before) if f not in own]
    protected = [f"{XV_DIR}/config.yml", f"{XV_DIR}/slices/{data['id']}.wall.json", f"{XV_DIR}/pitch.md",
                 f"{XV_DIR}/picture.md", f"{XV_DIR}/estimation.md", f"{XV_DIR}/rules.md"]
    if agent in ("scenario", "maker", "cleaner"):
        changed = changed_files(root, head_before)
        checks["protected_changed"] = [f for f in protected if f in changed]
    if agent == "scenario":
        files = changed_files(root, head_before)
        files = [f for f in files if not f.startswith(XV_DIR + "/")]
        checks["outside_tests"] = [f for f in files if not match_any(f, tests)]
        red = data.get("red") or {}
        if red.get("command"):
            code, out = shell(red["command"], root, 600)
            checks["red_fails"] = code != 0
            checks["red_output"] = out[-800:]
        else:
            checks["red_fails"] = None
        wb = wall_baseline(root, data, config)
        if wb:
            data["wall_baseline"] = wb
    if agent == "maker" and data.get("prototype_sessions"):
        checks["reused_prototype_context"] = (data["spend"][-1].get("session") in data["prototype_sessions"])
    if agent in ("maker", "cleaner"):
        suite, out = run_suite(root, config)
        checks["suite"], checks["suite_output"] = suite, (out or "")[-800:]
        checks["failing"] = failing_tests(out or "") if suite == "red" else []
        prior = (data.get("checks") or {}).get(agent) or {}
        checks["failing_history"] = (prior.get("failing_history") or []) + [checks["failing"]]
        data["suite"] = suite
        stat = git(["diff", "--numstat", data.get("base") or head_before], root)
        checks["diff_lines"] = sum(int(x) for line in stat.splitlines()
                                   for x in line.split("\t")[:2] if x.isdigit())
        before = (data.get("checks") or {}).get(agent) or {}
        checks["diff_history"] = (before.get("diff_history") or []) + [checks["diff_lines"]]
        checks["wall"] = wall_check(root, data, config)
    if agent == "cleaner":
        sp = os.path.join(root, XV_DIR, "standards.md")
        now_text = open(sp).read() if os.path.exists(sp) else None
        checks["standards_touched"] = now_text != pre.get("standards")
        head = git(["rev-parse", "HEAD"], root).strip()
        checks["committed"] = head != head_before
        if head != head_before and not data.get("cleaner_commit"):
            data["cleaner_commit"] = head
    if agent == "guardian":
        packet = os.path.join(root, XV_DIR, "slices", f"{data['id']}.packet.md")
        checks["packet"] = os.path.exists(packet)
        if os.path.exists(packet):
            import packet as packetlib
            try:
                lint = packetlib.fix(packet)
                checks["packet_problems"], checks["dropped_findings"] = lint["problems"], len(lint["dropped"])
            except XVError as e:
                checks["packet_problems"] = [str(e)]
            append_cleaner_proposals(packet, data)
            pdata, _ = record.read_doc(packet)
            for field in ("shape_change", "pitch_contradiction"):
                v = pdata.get(field)
                # a missing or malformed field waits for people, never for no one
                data[field] = v if v in ("yes", "no") else "yes"
            data["packet"] = os.path.relpath(packet, root)
            checks["picture_change"] = pdata.get("picture_change") or report.get("picture_change")
            checks["shape_breadth"] = pdata.get("shape_breadth") or report.get("shape_breadth")
        else:
            data["shape_change"] = data["pitch_contradiction"] = "yes"
            checks["missing_packet"] = True
    return checks


def append_cleaner_proposals(packet, data):
    """The cleaner's candidate standards and shape proposals ride in the packet,
    where the person who set the work going can accept a standard."""
    cands, shapes = [], []
    for rep in (data.get("checks") or {}).get("reports", []):
        if rep.get("agent") == "cleaner":
            cands += rep.get("candidate_standards") or []
            shapes += rep.get("shape_proposals") or []
    if not cands and not shapes:
        return
    lines = ["", "## From the cleaner", ""]
    for i, c in enumerate(cands, 1):
        lines.append(f"- Candidate standard {i}: {c}. To accept: `xv retro standard {data['id']} {i} --by <name>`.")
    for s in shapes:
        lines.append(f"- Shape proposal, for people: {s}")
    with open(packet, "a") as f:
        f.write("\n".join(lines) + "\n")


def commit_step(agent, root, slice_id, checks):
    messages = {
        "forecaster": "forecast", "scenario": "red", "maker": "make it work",
        "cleaner": "record the cleaner's pass", "guardian": "packet",
    }
    commit(root, f"xv({slice_id}): {messages[agent]}")


# The wall and the boundary picture arrive with their own scripts; until a repo
# has them, these steps are no-ops so the loop still runs and a person reads.

def wall_baseline(root, data, config):
    try:
        import wall
    except ImportError:
        return None
    return wall.baseline(root, data["id"], config)


def wall_check(root, data, config):
    try:
        import wall
    except ImportError:
        return {}
    try:
        return wall.check(root, data["id"], config)
    except XVError as e:
        return {"note": str(e)}


def boundary(root, data):
    try:
        import boundary as b
    except ImportError:
        return
    b.write_for_slice(root, data)


# ---------------------------------------------------------------- run, close

def cmd_run(a):
    path = record_path(repo_root(), a.id)
    while True:
        data, _ = record.load(slice_root(path), a.id)[1:]
        nxt = data.get("next")
        if nxt in (None, "none") or data.get("status") == "closed":
            print(json.dumps({"slice": a.id, "status": data.get("status"), "stop": None}))
            sys.exit(0)
        if nxt == "close":
            open_stops = [s for s in data["stops"] if s.get("answer") is None]
            if open_stops:
                print(json.dumps({"slice": a.id, "stop": open_stops[-1]}, indent=2))
                sys.exit(EXIT_STOP)
            sys.exit(close(a.id))
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        if open_stops:
            print(json.dumps({"slice": a.id, "stop": open_stops[-1], "note": "an earlier stop is unanswered"}, indent=2))
            sys.exit(EXIT_STOP)
        if nxt == "prototype":
            import prototypes
            sys.exit(prototypes.run(a.id))
        code, v = step(nxt, a.id)
        if code != 0:
            print(json.dumps(v, indent=2))
            sys.exit(code)


def close(slice_id, why=None, shape=None):
    root = slice_root(record_path(repo_root(), slice_id))
    config = load_config(root)
    path, data, body = record.load(root, slice_id)
    open_stops = [s for s in data["stops"] if s.get("answer") is None and s["order"] != "ready_to_merge"]
    if open_stops:
        raise XVError(f"an open stop needs an answer first: {open_stops[-1]['question']}")
    for s in data["stops"]:
        if s.get("answer") is None and s["order"] == "ready_to_merge":
            raise XVError("the merge is the person's: answer the ready stop "
                          f"(`xv record answer {slice_id} --by <name> --answer merge`) and then close")
    if why:  # the forecaster ran in the session and gave its line, or a person did
        report, s = {"why": why, "shape_actual": shape}, None
    else:
        text = promptlib.build("forecaster", slice_id, root=root, close=True)
        argv = agentcli.argv_for(config, "forecaster")
        result = agentcli.run(argv, text, root, os.path.join(runs_dir(root, slice_id), "close-forecaster.out"))
        data, body = record.load(root, slice_id)[1:]
        s = spendlib.from_run(result)
        s.update(step="close", at=now(), exit=result["code"])
        body, report = record.apply_report(data, body, "forecaster", result["stdout"])
        record.save(path, data, body)
    why = (report or {}).get("why") or "the forecaster gave no reason"
    p = subprocess.run([sys.executable, os.path.join(HERE, "record.py"), "guide-append", slice_id,
                        "--why", why, "--shape", (report or {}).get("shape_actual") or ""],
                       cwd=root, capture_output=True, text=True)
    data, body = record.load(root, slice_id)[1:]
    if s:
        data["spend"].append(s)  # after the guide row: the close itself is not the slice's work
    data["status"], data["next"] = "closed", "none"
    body = record.log_line(body, "watch", "closed" + ("" if p.returncode == 0 else f"; guide: {p.stderr.strip()}"))
    record.save(path, data, body)
    commit(root, f"xv({slice_id}): close")
    out = {"slice": slice_id, "status": "closed", "guide": p.stdout.strip() or p.stderr.strip(),
           "next": f"merge {data['branch']} when you are ready; the watch does not merge"}
    try:
        import retro
        why = retro.due(root)["slices"].get(slice_id)
        if why:
            out["retro_due"] = f"{'; '.join(why)}. Run `xv retro run {slice_id}` (the xv-retro skill)."
    except Exception:
        pass
    print(json.dumps(out, indent=2))
    return 0


# ---------------------------------------------------------------- guard (CI)

def cmd_guard(a):
    """The guardian on a pull request. With a slice record in the change, it is that
    slice's guardian step. Without one, it reviews the diff against the base."""
    root = repo_root()
    config = load_config(root)
    changed = git(["diff", "--name-only", f"{a.base}...HEAD"], root).split()
    slices = [os.path.basename(f)[:-3] for f in changed if is_record_path(f)]
    if len(slices) == 1:
        os.environ["XV_NO_COMMIT"] = "1"
        code, v = step("guardian", slices[0], review_again=True)
        print(json.dumps(v, indent=2))
        path = record_path(root, slices[0])
        packet = os.path.join(slice_root(path), XV_DIR, "slices", f"{slices[0]}.packet.md")
        if a.out and os.path.exists(packet):
            shutil.copy(packet, a.out)
        sys.exit(code)
    rel = os.path.join(XV_DIR, "slices", "pr-packet.md")
    os.makedirs(os.path.join(root, XV_DIR, "slices"), exist_ok=True)
    try:
        import boundary as b
        bres = b.change(root, a.base, config)
        with open(os.path.join(root, XV_DIR, "slices", "pr-boundary.md"), "w") as f:
            f.write(b.render_change(bres))
    except ImportError:
        pass
    extra = [f"No slice record: review the pull request's diff, `git diff {a.base}...HEAD`.",
             f"Packet template: `{os.path.join(promptlib.SKILLS, 'guardian', 'packet.md')}`. "
             f"Write the packet to `{rel}`.",
             f"Boundary picture: `{XV_DIR}/slices/pr-boundary.md`.",
             f"Test files changed since the base: `xv wall check --base {a.base} --json`."]
    text = promptlib.brief("guardian") + "\n" + promptlib.pointers("guardian", root, config, None, extra)
    result = agentcli.run(agentcli.argv_for(config, "guardian"), text, root, None,
                          int(config.get("step_timeout") or 3600))
    full = os.path.join(root, rel)
    data = {"id": "pull-request", "kind": "feature", "moved_tests": [], "checks": {"reports": []}}
    if os.path.exists(full):
        import packet as packetlib
        packetlib.fix(full)
        pdata, _ = record.read_doc(full)
        for field in ("shape_change", "pitch_contradiction"):
            data[field] = pdata.get(field) if pdata.get(field) in ("yes", "no") else "yes"
        data["checks"]["guardian"] = {"picture_change": pdata.get("picture_change")}
        if pdata.get("moved_tests"):
            data["moved_tests"] = [{"file": "see the packet"}] * int(pdata.get("moved_tests") or 0)
        if a.out:
            shutil.copy(full, a.out)
    else:
        data["shape_change"] = data["pitch_contradiction"] = "yes"
        if a.out:
            with open(a.out, "w") as f:
                f.write("The guardian wrote no packet. The change waits for two people.\n")
    data["checks"]["reports"].append({"agent": "guardian", "status": "done"})
    v = orders.verdict(data, "guardian", config)
    v["exit"] = result["code"]
    print(json.dumps(v, indent=2))
    sys.exit(EXIT_STOP if v["stop"] else 0)


# ---------------------------------------------------------------- init

DETECT = [
    ("package.json", "npm test", ["tests/**", "test/**", "**/*.test.*", "**/*.spec.*", "e2e/**"]),
    ("Gemfile", "bundle exec rake test", ["test/**", "spec/**"]),
    ("go.mod", "go test ./...", ["**/*_test.go"]),
    ("Cargo.toml", "cargo test", ["tests/**"]),
    ("pyproject.toml", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"]),
    ("setup.py", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"]),
]


def detect_tests(root):
    for marker, command, paths in DETECT:
        if os.path.exists(os.path.join(root, marker)):
            if marker in ("pyproject.toml", "setup.py") and shutil.which("pytest") is None:
                command = "python3 -m unittest discover -s tests -t ."
            return command, paths
    if os.path.isdir(os.path.join(root, "tests")):
        return "python3 -m unittest discover -s tests -t .", ["tests/**"]
    return "", ["tests/**", "test/**", "spec/**"]


def source_roots(root, test_paths):
    """One top-level folder holding all the code is the root, so its files become the modules."""
    import boundary as b
    cfg = {"source": {"roots": ["."], "exclude": ["node_modules/**", "vendor/**", ".git/**", ".xv/**"]},
           "tests": {"paths": test_paths}}
    from xvlib import tracked_files
    files = b.source_files(tracked_files(root), cfg)
    tops = {f.split("/")[0] for f in files if "/" in f}
    if len(tops) == 1 and all("/" in f for f in files):
        return [tops.pop()]
    if os.path.isdir(os.path.join(root, "src")) and any(f.startswith("src/") for f in files):
        return ["src"] + sorted(t for t in tops if t != "src" and t in ("lib", "app"))
    return ["."]


def repo_identity(root):
    """The repo's name and GitHub description, for what it shares. Read-only."""
    try:
        p = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner,description"], cwd=root,
                           capture_output=True, text=True, timeout=20)
        if p.returncode == 0:
            d = json.loads(p.stdout)
            return d.get("nameWithOwner") or "", d.get("description") or ""
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    url = git(["config", "--get", "remote.origin.url"], root, check=False).strip()
    m = __import__("re").search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return (m.group(1) if m else os.path.basename(root)), ""


def cmd_init(a):
    root = repo_root()
    src = os.path.join(XV_HOME, "defaults")
    dst = os.path.join(root, XV_DIR)
    written, kept = [], []
    for dirpath, _, files in os.walk(src):
        for name in files:
            s = os.path.join(dirpath, name)
            rel = os.path.relpath(s, src)
            d = os.path.join(dst, rel)
            if os.path.exists(d):
                kept.append(rel)
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy(s, d)
            written.append(rel)
    cfg = os.path.join(dst, "config.yml")
    if "config.yml" in written:
        command, paths = detect_tests(root)
        name, description = repo_identity(root)
        text = open(cfg).read()
        text = text.replace('  command: ""', f"  command: {json.dumps(command)}", 1)
        text = text.replace('paths: ["tests/**"]', f"paths: {json.dumps(paths)}")
        text = text.replace('  roots: ["."]', f"  roots: {json.dumps(source_roots(root, paths))}", 1)
        text = text.replace('  name: ""', f"  name: {json.dumps(name)}", 1)
        text = text.replace('  description: ""', f"  description: {json.dumps(description)}", 1)
        open(cfg, "w").write(text)
    try:
        import boundary as b
        with open(os.path.join(dst, "boundary-all.md"), "w") as f:
            f.write(b.render_all(root))
        written.append("boundary-all.md")
    except ImportError:
        pass
    print(json.dumps({"written": written, "kept": kept,
                      "tests": load_config(root).get("tests")}, indent=2))


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="xv", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("slice")
    ss = s.add_subparsers(dest="sub", required=True)
    n = ss.add_parser("new")
    n.add_argument("id")
    n.add_argument("--by", required=True)
    n.add_argument("--title")
    n.add_argument("--kind", choices=["feature", "defect", "prototype"], default="feature")
    n.add_argument("--scenario")
    n.add_argument("--scenario-file")
    n.add_argument("--ignore")
    n.add_argument("--recording")
    n.add_argument("--branch")
    n.add_argument("--axis", help="for a prototype slice: the one axis the three differ on")
    n.set_defaults(fn=cmd_slice_new)

    s = sub.add_parser("step")
    s.add_argument("agent")
    s.add_argument("id", nargs="?")
    s.add_argument("--init", action="store_true")
    s.set_defaults(fn=cmd_step)

    s = sub.add_parser("run")
    s.add_argument("id")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("close")
    s.add_argument("id")
    s.add_argument("--why", help="the line on the gap, when the forecaster ran in the session")
    s.add_argument("--shape", help="the shape change that actually happened")
    s.set_defaults(fn=lambda a: sys.exit(close(a.id, a.why, a.shape)))

    s = sub.add_parser("init")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("guard", help="the guardian on a pull request, for CI")
    s.add_argument("--base", required=True)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_guard)

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

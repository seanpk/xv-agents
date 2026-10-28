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
  xv init [--trial [--repo]|--adopt]   write a starter .xv/ into this repo
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agentcli  # noqa: E402
import orders  # noqa: E402
import prompt as promptlib  # noqa: E402
import record  # noqa: E402
import spend as spendlib  # noqa: E402
from xvlib import (XV_DIR, XVError, die, git, load_config, match_any, now,  # noqa: E402
                   record_path, repo_root, slice_root, today, worktrees_config, worktrees_dir)

HERE = os.path.dirname(os.path.abspath(__file__))
XV_HOME = os.path.dirname(HERE)
STEPS = ["forecaster", "scenario", "maker", "cleaner", "guardian", "close"]
EXIT_STOP = 10


# ---------------------------------------------------------------- helpers

def shell(cmd, cwd, timeout=900, env=None):
    try:
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                           env={**os.environ, **env} if env else None)
        return p.returncode, (p.stdout + p.stderr)[-4000:]
    except subprocess.TimeoutExpired as e:
        written = "".join(x.decode(errors="replace") if isinstance(x, bytes) else x
                          for x in (e.stdout, e.stderr) if x)
        return 124, f"{written[-4000:]}\ntimed out after {timeout}s"


def tests_timeout(config):
    return int((config.get("tests") or {}).get("timeout") or 900)


def run_suite(root, config, base=None, slice_id=None):
    """Run tests.command. XV_BASE and XV_SLICE tell a script that picks suites from the changed files where to diff from."""
    cmd = (config.get("tests") or {}).get("command")
    if not cmd:
        return None, "no tests.command in .xv/config.yml"
    env = {k: v for k, v in (("XV_BASE", base), ("XV_SLICE", slice_id)) if v}
    code, out = shell(cmd, root, tests_timeout(config), env)
    return ("green" if code == 0 else "red"), out


FAILING = re.compile(r"^(?:FAIL|ERROR): (\S+(?: \([^)]*\))?)|^FAILED (\S+)"
                     r"|^\s*[✕×] (.+?)(?: \(\d+ ?ms\)| \d+(?:\.\d+)? ?ms)?$|^ FAIL  \S+ > (.+)$"
                     r"|^--- FAIL: (\S+)|^rspec (\S+)|^\d+\) (.+)\n[ \t]+Message:"
                     r"|^\s*(?:\d+\) )?(?:Failure|Error):\n\s*([\w:]+#\w+)"
                     r"|^test (\S+) \.\.\. FAILED$|^\s+\d+\) (\[[^\]]+\] › .+?)\s*─*$", re.M)
# mocha prints a failure's title over several lines, one per describe, the last ending in a colon
MOCHA = re.compile(r"^ +\d+\) (.+(?:\n +[^\n]+?)*?):$", re.M)


def failing_tests(output):
    """Names of failing tests from unittest, pytest, jest, vitest, go, RSpec, Jasmine,
    minitest, mocha, cargo or Playwright output.

    RSpec is named by its rerun handle, ./spec/x_spec.rb:42, which is unique where
    descriptions repeat. Jasmine's numbered entries count only when a Message: line follows.
    Vitest names a test in its tree and again in its summary; both read `suite > test`.
    """
    names = {next(g for g in m if g) for m in FAILING.findall(output)}
    if re.search(r"^ +\d+ failing$", output, re.M):
        names |= {" ".join(part.strip() for part in m.split("\n")) for m in MOCHA.findall(output)}
    return sorted(names)


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


# ---------------------------------------------------------------- trial

def is_trial(root):
    """A trial keeps .xv/ out of git: the person is trying XV before committing to it."""
    p = subprocess.run(["git", "check-ignore", "-q", f"{XV_DIR}/config.yml"], cwd=root)
    return p.returncode == 0


def exclude_path(root):
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    return os.path.join(common, "info", "exclude")


# .git: a trial's .xv/ may be its own repo (`xv init --trial --repo`); its history stays out of each slice's copy.
LAYER_SKIP = ("slices", "worktrees", "listen", "boundary-all.md", "retro", "promote", ".git")


def copy_layer(src_root, dst_root):
    """In a trial the slice's worktree starts from a commit without .xv/; give it the layer."""
    src, dst = os.path.join(src_root, XV_DIR), os.path.join(dst_root, XV_DIR)
    for name in os.listdir(src):
        if name in LAYER_SKIP:
            continue
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            os.makedirs(dst, exist_ok=True)
            shutil.copy(s, d)


def bring_back(slice_root_dir, main, slice_id):
    """At close in a trial: the slice's record and packet, and its new guide rows, go to the main checkout."""
    from record import guide_rows
    s_slices, m_slices = (os.path.join(r, XV_DIR, "slices") for r in (slice_root_dir, main))
    os.makedirs(m_slices, exist_ok=True)
    for name in os.listdir(s_slices):
        if name.startswith(slice_id + "."):
            shutil.copy(os.path.join(s_slices, name), os.path.join(m_slices, name))
    sg, mg = (os.path.join(r, XV_DIR, "estimation.md") for r in (slice_root_dir, main))
    if os.path.exists(sg):
        if not os.path.exists(mg):
            shutil.copy(sg, mg)
            return
        old = open(mg).read()
        new = [r for r in guide_rows(open(sg).read()) if r not in set(guide_rows(old))]
        if new:
            with open(mg, "w") as f:
                f.write(old.rstrip("\n") + "\n" + "\n".join(new) + "\n")


# ---------------------------------------------------------------- slice new

def resolve_base(root, ref):
    """The commit a slice starts from: the ref given, else the remote's default branch, else HEAD."""
    if not ref:
        p = subprocess.run(["git", "rev-parse", "--verify", "-q", "refs/remotes/origin/HEAD^{commit}"],
                           cwd=root, capture_output=True, text=True)
        ref = "refs/remotes/origin/HEAD" if p.returncode == 0 else "HEAD"
    return git(["rev-parse", "--verify", ref + "^{commit}"], root).strip()


def run_worktree_command(command, wt, config):
    """Run a worktrees.setup or teardown command in the worktree. None when it passed or is unset;
    otherwise (command, exit code, its last lines)."""
    if not command:
        return None
    command = command.replace("{worktree}", shlex.quote(wt))
    code, out = shell(command, wt, tests_timeout(config))
    if code == 0:
        return None
    last = "\n".join(out.strip().splitlines()[-10:])
    return command, code, last


def cmd_slice_new(a):
    root = repo_root()
    config = load_config(root)
    if not os.path.exists(os.path.join(root, XV_DIR, "config.yml")):
        raise XVError("no .xv/config.yml here; run xv-init first")
    from xvlib import pitch_status
    if pitch_status(root) in ("missing", "unreadable", "not written"):
        raise XVError("the pitch comes first: .xv/pitch.md is not written. The guardian checks every change "
                      "against it. Write it with the xv-init skill, or by hand and set `status: written` in its "
                      "front matter; commit it, then start the slice")
    if not is_trial(root) and git(["status", "--porcelain", "--", XV_DIR], root).strip():
        raise XVError("commit the project layer (.xv/) first "
                      "(or try XV without committing it: xv init --trial)")
    wt = os.path.join(worktrees_dir(root, config), a.id)
    branch = a.branch or f"xv/{a.id}"
    wcfg = worktrees_config(config)
    base = resolve_base(root, a.base or wcfg.get("base"))
    if not is_trial(root):
        for name in ("config.yml", "pitch.md", "picture.md"):
            if subprocess.run(["git", "cat-file", "-e", f"{base}:{XV_DIR}/{name}"], cwd=root,
                              capture_output=True).returncode != 0:
                raise XVError(f"the base {base[:10]} has no committed {XV_DIR}/{name}: push .xv/ so the "
                              "remote's default branch has it, or pass --base HEAD")
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    git(["worktree", "add", "-q", "-b", branch, wt, base], root)
    trial = is_trial(root)
    if trial:
        copy_layer(root, wt)
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
    if trial:
        data["trial"] = True
    record.save(path, data, body)
    commit(wt, f"xv({a.id}): open slice")
    print(wt)
    wt_config = load_config(wt)
    failed = run_worktree_command(worktrees_config(wt_config).get("setup"), wt, wt_config)
    if failed:
        command, code, last = failed
        path, data, body = record.load(wt, a.id)
        question = f"the worktree setup `{command}` failed ({code}); its last output:\n{last}"
        data["stops"].append({"at": now(), "step": "setup", "order": "setup_failed", "seat": "originator",
                              "question": question, "answered_by": [], "answer": None})
        data["status"] = "stopped"
        body = record.log_line(body, "watch", f"stop (setup_failed) for originator: {question}")
        record.save(path, data, body)
        commit(wt, f"xv({a.id}): setup failed")
        sys.exit(EXIT_STOP)


def cmd_slice_amend(a):
    root = repo_root()
    with open(a.scenario_file, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        raise XVError("the amendment is empty")
    path, data, body = record.load(root, a.id)
    marker = "\n## May ignore"
    at = body.find(marker)
    if at < 0:
        raise XVError("the record has no '## May ignore' heading to amend above")
    note = f"\n\n### Amended {today()} by {a.by}\n\n{text}\n"
    body = body[:at].rstrip("\n") + note + body[at:]
    data["red"] = None
    data["next"] = "scenario"
    body = record.log_line(body, a.by, "amended the scenario")
    record.save(path, data, body)


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
    budget_stop = orders.budget_before(data)
    if budget_stop:
        st = {"at": now(), "step": agent, "order": budget_stop["order"], "seat": budget_stop["seat"],
              "question": budget_stop["question"], "answered_by": [], "answer": None, "also": []}
        data["stops"].append(st)
        data["status"] = "stopped"
        body = record.log_line(body, "watch", f"stop ({st['order']}) for {st['seat']}: {st['question']}")
        record.save(path, data, body)
        reach(config, st["seat"], st["question"], os.path.relpath(path, root))
        return EXIT_STOP, {"slice": slice_id, "after": agent, "stop": st, "fired": [budget_stop]}

    if (config.get("agents") or {}).get(agent) == "session":
        raise XVError(f"{agent} runs in the session: use `xv prompt {agent} {slice_id}`, then "
                      f"`xv record report {slice_id} {agent} -` and `xv orders {slice_id} --after {agent}`")

    head_before = git(["rev-parse", "HEAD"], root).strip()
    pre = pre_step(agent, root, data, config)
    text = promptlib.build(agent, slice_id, root=root)
    argv = agentcli.argv_for(config, agent)
    spent = spendlib.slice_spend(data)
    argv = agentcli.with_caps(argv, data.get("budget"), spent["usd"], spent["turns"])
    n = len(data.get("spend") or []) + 1
    log = os.path.join(runs_dir(root, slice_id), f"{n:02d}-{agent}.out")
    result = agentcli.run(argv, text, root, log, int(config.get("step_timeout") or 3600))

    data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` itself
    if pre.get("pre_maker_commit"):
        data.setdefault("pre_maker_commit", pre["pre_maker_commit"])
    s = spendlib.from_run(result)
    s.update(step=agent, at=now(), exit=result["code"], log=log)
    data["spend"].append(s)
    red_before = data.get("red")
    try:
        body, report = record.apply_report(data, body, agent, result["stdout"])
    except Exception as e:  # a malformed report is a missing report, not a crash
        report = None
        data["checks"].setdefault("reports", []).append(
            {"agent": agent, "status": "no-report", "summary": f"the report could not be applied: {e}", "at": now()})
        body = record.log_line(body, agent, f"the report could not be applied: {e}")
    reported = ((report or {}).get("red") or {}).get("command") if agent == "scenario" else None
    if reported and joined_unsafely(reported):
        data["red"] = red_before  # a refused red is not kept: the maker is never handed it
    record.save(path, data, body)  # the wall reads moved_tests from disk: the report's moves must be there
    checks = post_step(agent, root, data, config, head_before, pre, report or {})
    data["checks"][agent] = checks
    data["status"] = "working"
    data["next"] = "scenario" if checks.get("red_joined") else STEPS[STEPS.index(agent) + 1]
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
    if agent == "maker" and not data.get("pre_maker_commit"):
        pre["pre_maker_commit"] = data["pre_maker_commit"] = git(["rev-parse", "HEAD"], root).strip()
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
        reported = (report.get("red") or {}).get("command")
        if reported and joined_unsafely(reported):
            checks["red_fails"] = None
            checks["red_joined"] = reported
        elif red.get("command"):
            code, out = red_run(root, data, red, config)
            checks["red_fails"] = None if code is None else code != 0
            checks["red_output"] = out[-800:]
            if code is None:
                checks["setup_failed"] = out
        else:
            checks["red_fails"] = None
        changed = old_red_changed(root, data, red)
        checks["old_red_changed"] = changed or []
        if changed is None:
            checks["old_red_unchecked"] = ("The check for old tests changed in red files could not run: "
                                           "the record has no base, or the wall module did not load.")
        wb = wall_baseline(root, data, config)
        if wb:
            data["wall_baseline"] = wb
    if agent == "maker" and data.get("prototype_sessions"):
        checks["reused_prototype_context"] = (data["spend"][-1].get("session") in data["prototype_sessions"])
    if agent in ("maker", "cleaner"):
        suite, out = run_suite(root, config, data.get("base"), data.get("id"))
        checks["suite"], checks["suite_output"] = suite, (out or "")[-800:]
        checks["failing_step"] = orders.first_failing_step(out) if suite == "red" else ""
        checks["failing"] = failing_tests(out or "") if suite == "red" else []
        prior = (data.get("checks") or {}).get(agent) or {}
        checks["failing_history"] = (prior.get("failing_history") or []) + [checks["failing"]]
        data["suite"] = suite
        stat = git(["diff", "--numstat", data.get("base") or head_before,
                    "--", ".", f":(exclude){XV_DIR}"], root)
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


def red_run(root, data, red, config):
    """Run the red command. Once the maker has run, run it on the code from before the maker's first change."""
    commit = data.get("pre_maker_commit") or (data.get("wall_baseline") or {}).get("commit")
    if not commit or not any(s.get("step") == "maker" for s in data.get("spend") or []):
        return shell(red["command"], root, 600)
    tmp = tempfile.mkdtemp(prefix="xv-red-")
    try:
        subprocess.run(["git", "worktree", "add", "--detach", tmp, commit], cwd=root, capture_output=True, check=True)
        for f in red.get("files") or []:
            src = os.path.join(root, f)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(os.path.join(tmp, f)), exist_ok=True)
                shutil.copyfile(src, os.path.join(tmp, f))
        failed = run_worktree_command(worktrees_config(config).get("setup"), tmp, config)
        if failed:
            return None, f"the worktree setup `{failed[0]}` failed ({failed[1]}); its last output:\n{failed[2]}"
        return shell(red["command"], tmp, 600)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", tmp], cwd=root, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


def old_red_changed(root, data, red):
    """Red files that existed at the base and lost or changed old test code."""
    try:
        import wall
    except ImportError:
        return None
    moved = {m.get("file") for m in data.get("moved_tests") or []}
    return wall.old_red_changed(root, data["base"], red.get("files") or [], moved) if data.get("base") else None


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
    failed = run_worktree_command(worktrees_config(config).get("teardown"), root, config)
    if failed:
        command, code, last = failed
        print(f"xv: worktree teardown `{command}` failed ({code}): {last}", file=sys.stderr)
    if data.get("trial"):
        from xvlib import main_root
        if main_root(root) != root:
            bring_back(root, main_root(root), slice_id)
    out = {"slice": slice_id, "status": "closed", "stop": None, "guide": p.stdout.strip() or p.stderr.strip(),
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

# marker, command, test paths, folders that mean the runner has tests here (none: always).
# Backend runners come first: when several qualify, the first one is tests.command.
DETECT = [
    ("Gemfile", "bundle exec rake test", ["test/**", "spec/**"], ("spec", "test")),
    ("go.mod", "go test ./...", ["**/*_test.go"], ()),
    ("Cargo.toml", "cargo test", ["tests/**"], ("tests",)),
    ("pyproject.toml", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"], ()),
    ("setup.py", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"], ()),
    ("package.json", "npm test", ["tests/**", "test/**", "**/*.test.*", "**/*.spec.*", "e2e/**"],
     ("tests", "test", "e2e")),
]


def detect_tests(root):
    """Check every marker, not just the first: a Rails app has a Gemfile and a package.json.

    Returns (command, paths, runners). The paths are the union over every runner found.
    The command is the first runner, backend first, whose test folder exists; if none
    has one, the first runner found. `runners` lists each one found, for the person to choose.
    """
    # a src layout needs src on the path for the tests to import the package
    src = "PYTHONPATH=src " if os.path.isdir(os.path.join(root, "src")) else ""
    runners, paths, has_dir = [], [], []
    for marker, command, marker_paths, dirs in DETECT:
        if not os.path.exists(os.path.join(root, marker)):
            continue
        if marker == "Gemfile" and os.path.isdir(os.path.join(root, "spec")):
            command = "bundle exec rspec"
        if marker in ("pyproject.toml", "setup.py") and shutil.which("pytest") is None:
            command = "python3 -m unittest discover -s tests -t ."
        if command.startswith("python3"):
            command = src + command
        if any(r["command"] == command for r in runners):
            continue
        runners.append({"marker": marker, "command": command, "paths": marker_paths})
        has_dir.append(not dirs or any(os.path.isdir(os.path.join(root, d)) for d in dirs))
        paths += [x for x in marker_paths if x not in paths]
    if runners:
        pick = runners[has_dir.index(True)] if True in has_dir else runners[0]
        return pick["command"], paths, runners
    if os.path.isdir(os.path.join(root, "tests")):
        return src + "python3 -m unittest discover -s tests -t .", ["tests/**"], []
    return "", ["tests/**", "test/**", "spec/**"], []


def source_roots(root, test_paths):
    """One top-level folder holding all the code is the root, so its files become the modules."""
    import boundary as b
    cfg = {"source": {"roots": ["."], "exclude": ["node_modules/**", "vendor/**", ".git/**", ".xv/**"]},
           "tests": {"paths": test_paths}}
    from xvlib import tracked_files
    files = b.source_files(tracked_files(root), cfg)
    if os.path.isdir(os.path.join(root, "app")) and os.path.exists(os.path.join(root, "config", "routes.rb")):
        # a Rails layout: app is the code, lib and app/javascript are code beside it
        return ["app"] + [d for d in ("lib", "app/javascript") if os.path.isdir(os.path.join(root, d))]
    tops = {f.split("/")[0] for f in files if "/" in f}
    if len(tops) == 1 and all("/" in f for f in files):
        return [tops.pop()]
    if os.path.isdir(os.path.join(root, "src")) and any(f.startswith("src/") for f in files):
        return ["src"] + sorted(t for t in tops if t != "src" and t in ("lib", "app"))
    return ["."]


def repo_identity(root):
    """The repo's name, GitHub description, and whether it is private (None: unknown). Read-only."""
    try:
        p = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner,description,isPrivate"], cwd=root,
                           capture_output=True, text=True, timeout=20)
        if p.returncode == 0:
            d = json.loads(p.stdout)
            return d.get("nameWithOwner") or "", d.get("description") or "", d.get("isPrivate")
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    url = git(["config", "--get", "remote.origin.url"], root, check=False).strip()
    m = __import__("re").search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return (m.group(1) if m else os.path.basename(root)), "", None


def adopt_trial_repo(root):
    """Ending a trial whose .xv/ is its own repo: move that repo out of the way, never delete it.

    With no remote it is the only copy of the trial's history, so it goes to
    <git common dir>/xv-trial.git, where `git --git-dir` can still read it.
    """
    inner = os.path.join(root, XV_DIR, ".git")
    if not os.path.exists(inner):
        return None
    if git(["status", "--porcelain"], os.path.join(root, XV_DIR)).strip():
        raise XVError(f"{XV_DIR}/ is its own git repo and has changes not committed there. "
                      f"Commit them (git -C {XV_DIR} commit -am ...) or discard them, then adopt again.")
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    dest = os.path.join(common, "xv-trial.git")
    if os.path.exists(dest):
        raise XVError(f"{dest} already exists: an earlier trial's history is there. "
                      "Move it aside yourself; xv will not overwrite it.")
    shutil.move(inner, dest)
    origin = git(["--git-dir", dest, "config", "--get", "remote.origin.url"], root, check=False).strip()
    return {"moved_to": dest, "origin": origin or None}


FIXTURE_NAMES = ("fixture", "fixtures", "examples", "setups")
CODE_EXTS = (".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".rs", ".java", ".sh", ".php", ".c", ".cc", ".cpp", ".cs")


def fixture_folders(root, exclude):
    from xvlib import tracked_files
    found = set()
    for path in tracked_files(root):
        if not path.endswith(CODE_EXTS) or path.split("/")[0] == XV_DIR or match_any(path, exclude):
            continue
        parts = path.split("/")[:-1]
        for i, part in enumerate(parts):
            if part.lower() in FIXTURE_NAMES:
                found.add("/".join(parts[:i + 1]))
    return sorted(found)


def try_test_command(root, tests):
    command = (tests or {}).get("command") or ""
    if not command:
        return None
    timeout = int(tests.get("timeout") or 900)
    code, text = shell(command, root, timeout)
    if code == 124 and text.endswith(f"timed out after {timeout}s"):
        return {"result": "timed out", "after_s": timeout}
    if code == 0:
        return {"result": "passed"}
    return {"result": "failed", "exit": code, "tail": text.strip().splitlines()[-15:]}


READ_ONLY_TOOLS = ["cat", "head", "tail", "ls", "grep", "git diff", "git log", "git status", "git show",
                   "rg", "wc", "sed -n", "diff", "git ls-files", "git grep", "git rev-parse"]
MAKER_TOOLS = ["git rm", "git mv", "xv record move"]
GUARDIAN_TOOLS = ["xv wall diff", "xv boundary", "xv packet lint"]


def test_rules(command):
    """One rule per part of the test command, each cut before its arguments, so a single file runs too."""
    rules = []
    for part in re.split(r"\s*(?:&&|\|\||;)\s*", command or ""):
        words = part.split()
        lead = []
        while words and re.match(r"\w+=", words[0]):
            lead.append(words.pop(0))
        keep = []
        for w in words:
            is_arg = w.startswith("-") and w != "-m"
            if keep and (is_arg or "/" in w or w in (".", "discover")):
                break
            keep.append(w)
        for rule in (" ".join(lead + keep), " ".join(keep)) if keep else ():
            if rule not in rules:
                rules.append(rule)
    return rules


def allow_lists(text, command):
    """Give each Claude Code agent line a starter --allowedTools list; the forecaster's is read-only."""
    test = test_rules(command)
    seats = {"default": READ_ONLY_TOOLS + MAKER_TOOLS + test, "forecaster": READ_ONLY_TOOLS,
             "guardian": READ_ONLY_TOOLS + GUARDIAN_TOOLS + test}
    out = []
    for line in text.split("\n"):
        seat = line.split(":", 1)[0].strip()
        if seat in seats and line.startswith(f'  {seat}: ["claude"') and "--allowedTools" not in line:
            tools = ",".join(f"Bash({t}:*)" for t in seats[seat])
            line = line.replace('"acceptEdits", ', f'"acceptEdits", "--allowedTools", {json.dumps(tools)}, ', 1)
        out.append(line)
    return "\n".join(out)


def cmd_init(a):
    root = repo_root()
    if a.repo and not a.trial:
        raise XVError("--repo goes with --trial: it makes .xv/ its own git repo while it is kept out of this one.")
    if a.adopt:
        moved = adopt_trial_repo(root)
        path = exclude_path(root)
        lines = open(path).read().splitlines() if os.path.exists(path) else []
        kept = [line for line in lines if line.strip() not in (f"{XV_DIR}/", f"/{XV_DIR}/", XV_DIR, f"/{XV_DIR}")]
        with open(path, "w") as f:
            f.write("\n".join(kept) + ("\n" if kept else ""))
        still = is_trial(root)
        out = {"trial": still, "next": "a .gitignore still lists .xv/; remove it there" if still
               else "commit .xv/; the project layer is now part of the repo"}
        if moved:
            out["trial_repo"] = moved
        print(json.dumps(out, indent=2))
        return
    if a.trial:
        path = exclude_path(root)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = open(path).read() if os.path.exists(path) else ""
        if f"/{XV_DIR}/" not in text.split():
            with open(path, "a") as f:
                f.write(("" if text.endswith("\n") or not text else "\n") + f"/{XV_DIR}/\n")
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
    runners = []
    if "config.yml" in written:
        command, paths, runners = detect_tests(root)
        name, description, private = repo_identity(root)
        text = open(cfg).read()
        text = text.replace('  command: ""', f"  command: {json.dumps(command)}", 1)
        text = text.replace('paths: ["tests/**"]', f"paths: {json.dumps(paths)}")
        text = text.replace('  roots: ["."]', f"  roots: {json.dumps(source_roots(root, paths))}", 1)
        text = text.replace('  name: ""', f"  name: {json.dumps(name)}", 1)
        text = text.replace('  description: ""', f"  description: {json.dumps(description)}", 1)
        text = allow_lists(text, command)
        if private:
            text = text.replace("  include_name: true", "  include_name: false", 1)
        open(cfg, "w").write(text)
    try:
        import boundary as b
        with open(os.path.join(dst, "boundary-all.md"), "w") as f:
            f.write(b.render_all(root))
        written.append("boundary-all.md")
    except ImportError:
        pass
    config = load_config(root)
    tests = config.get("tests") or {}
    out = {"written": written, "kept": kept, "tests": tests}
    if not a.no_try:
        out["test_run"] = try_test_command(root, tests)
    bpath = os.path.join(dst, "boundary-all.md")
    if os.path.exists(bpath):
        out["modules"] = len([l for l in open(bpath).read().splitlines() if l.startswith("- ")])
    out["fixture_folders"] = fixture_folders(root, (config.get("source") or {}).get("exclude") or [])
    if len(runners) > 1:
        out["runners"] = runners
    if a.repo:
        if not os.path.exists(os.path.join(dst, ".git")):
            git(["init", "-q"], dst)
        out["next"] = (f"{XV_DIR}/ is now its own git repo, with no commit yet. Commit inside it "
                       f"(git -C {XV_DIR} add -A && git -C {XV_DIR} commit -m ...). To let teammates opt in, "
                       f"push it to a private remote. `xv init --adopt` moves it aside later.")
    print(json.dumps(out, indent=2))


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
    n.add_argument("--base", help="the ref the slice branch starts from (default: worktrees.base, then origin/HEAD, then HEAD)")
    n.add_argument("--axis", help="for a prototype slice: the one axis the three differ on")
    n.set_defaults(fn=cmd_slice_new)
    m = ss.add_parser("amend")
    m.add_argument("id")
    m.add_argument("--by", required=True)
    m.add_argument("--scenario-file", required=True)
    m.set_defaults(fn=cmd_slice_amend)

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
    s.add_argument("--trial", action="store_true",
                   help="keep .xv/ out of git (in .git/info/exclude), to try XV before committing to it")
    s.add_argument("--repo", action="store_true",
                   help="with --trial: make .xv/ its own git repo (no commit), so the trial keeps history")
    s.add_argument("--no-try", action="store_true",
                   help="do not run the test command to check it")
    s.add_argument("--adopt", action="store_true",
                   help="end a trial: let git see .xv/ again; a nested .xv/.git moves to <git dir>/xv-trial.git")
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

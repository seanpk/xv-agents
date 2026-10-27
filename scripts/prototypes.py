#!/usr/bin/env python3
"""Parallel prototypes: three running versions of one scenario that differ on
one named axis, built by maker-kind agents with a prototype brief, recorded,
and laid side by side for two people to pick from, or pick none.

No wall and a loose model: nothing a prototype builds is a candidate for the
main line. Every prototype is discarded at the pick, the chosen one too. The
pick is restated as the slice's scenario, and a fresh maker context builds it
behind the wall.

Usage:
  xv prototype start <id> [--axis "<axis>"] [--variant "<position>" ...] [--serial]
  xv prototype pick <id> --variant a|b|c|none --by <name>,<name> [--with-user <name>]
                   [--scenario-file <file>]    the restated scenario; required unless none
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agentcli  # noqa: E402
import orders  # noqa: E402
import prompt as promptlib  # noqa: E402
import record  # noqa: E402
import spend as spendlib  # noqa: E402
from xvlib import (XV_DIR, XVError, die, git, load_config, now, read_doc, record_path,  # noqa: E402
                   repo_root, slice_root, today, worktrees_dir)

NAMES = ["a", "b", "c"]
# The three positions XV's method names for an axis. A team can pass its own.
DEFAULT_POSITIONS = [
    "the minimum the scenario allows",
    "refuses one assumption in the scenario; say which",
    "puts a different object at the centre of the interaction",
]
EXIT_STOP = 10


def run_one(name, axis, position, slice_id, slice_wt, config, budget, spent, out):
    root = slice_wt
    branch = f"xv/{slice_id}-proto-{name}"
    wt = os.path.join(worktrees_dir(root, config), f"{slice_id}-proto-{name}")
    if os.path.exists(wt):
        git(["worktree", "remove", "--force", wt], root, check=False)
    git(["branch", "-D", branch], root, check=False)
    git(["worktree", "add", "-q", "-b", branch, wt, "HEAD"], root)
    rec_dir = f"{XV_DIR}/prototypes/{slice_id}/{name}"
    extra = [f"Your variant: {name}. The axis: {axis}. Your position on it: {position}.",
             f"Write your recording script and `recording.md` under `{rec_dir}/`.",
             "Two other contexts are building the other positions. You will not see them."]
    text = promptlib.brief("prototype") + "\n" + promptlib.pointers("prototype", wt, config,
                                                                    read_doc(record_path(wt, slice_id))[0], extra)
    argv = agentcli.argv_for(config, "prototype")
    argv = agentcli.with_caps(argv, budget, spent["usd"], spent["turns"])
    log = os.path.join(git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip(),
                       "xv", "runs", slice_id, f"prototype-{name}.out")
    result = agentcli.run(argv, text, wt, log, int(config.get("step_timeout") or 3600))
    report = None
    try:
        report = record.extract_report(result["stdout"])
    except XVError:
        pass
    recording = os.path.join(wt, rec_dir, "recording.md")
    out[name] = {"name": name, "branch": branch, "worktree": wt, "axis_position": position,
                 "report": report, "spend": spendlib.from_run(result), "session": result.get("session"),
                 "recording": os.path.exists(recording), "recording_path": recording}


def start(slice_id, axis=None, positions=None, serial=False):
    path = record_path(repo_root(), slice_id)
    root = slice_root(path)
    config = load_config(root)
    data, body = record.load(root, slice_id)[1:]
    waiting = [s for s in data["stops"] if s.get("answer") is None]
    if waiting:
        return EXIT_STOP, {"slice": slice_id, "stop": waiting[-1],
                           "note": "an earlier stop is unanswered; the prototypes are not rebuilt"}
    axis = axis or data.get("axis")
    if not axis:
        data["stops"].append({"at": now(), "step": "prototype", "order": "axis_not_named", "seat": "originator",
                              "question": "Name the one axis the three prototypes differ on "
                                          f"(`xv prototype start {slice_id} --axis \"...\"`).",
                              "answered_by": [], "answer": None})
        data["status"] = "stopped"
        record.save(path, data, body)
        return EXIT_STOP, {"slice": slice_id, "stop": data["stops"][-1]}
    budgets = data.get("prototype_budgets") or {}
    missing = [f for f in orders.evaluate(data, "prototype", config) if f["order"] == "prototype_budgets_not_set"]
    if missing:
        data["stops"].append({"at": now(), "step": "prototype", "order": missing[0]["order"],
                              "seat": missing[0]["seat"], "question": missing[0]["question"],
                              "answered_by": [], "answer": None})
        data["status"] = "stopped"
        record.save(path, data, body)
        return EXIT_STOP, {"slice": slice_id, "stop": data["stops"][-1]}
    positions = positions or DEFAULT_POSITIONS
    if len(positions) != 3:
        raise XVError("three positions on the axis: more and people are reviewing a gallery")
    data["axis"] = axis
    record.save(path, data, record.log_line(body, "watch", f"three prototypes on the axis: {axis}"))
    git(["add", "-A"], root)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", f"xv({slice_id}): the axis"], cwd=root)

    out = {}
    serial = serial or (config.get("prototypes") or {}).get("serial")
    spent = {n: spendlib.totals([s for s in data.get("spend") or [] if s.get("step") == f"prototype-{n}"])
             for n in NAMES}
    # a variant that has spent its own budget stops alone; the others still run
    # a second start keeps the variants that finished and runs only those that ran out, on their raised budgets
    prev = {e["name"]: e for e in data.get("prototypes") or []}
    kept = {n for n in NAMES if (prev.get(n) or {}).get("branch")}
    over = {n: [k for k in ("tokens", "usd", "turns") if budgets[n].get(k) and spent[n][k] >= budgets[n][k]]
            for n in NAMES}
    stopped = {n for n in NAMES if n not in kept and over[n]}
    jobs = [threading.Thread(target=run_one, args=(n, axis, p, slice_id, root, config, budgets[n], spent[n], out))
            for n, p in zip(NAMES, positions) if n not in stopped and n not in kept]
    for j in jobs:
        j.start()
        if serial:
            j.join()
    for j in jobs:
        j.join()

    data, body = record.load(root, slice_id)[1:]
    lines = [f"# Prototypes: {data['title']}", "",
             f"Three running versions on one axis: **{axis}**. Each was built in its own context with no wall. "
             "All three are discarded at the pick; the pick is restated as the scenario and built behind the wall.",
             "", "| | Position on the axis | What it refuses | What it costs | Try it |", "| --- | --- | --- | --- | --- |"]
    for n in kept:
        e = prev[n]
        out[n] = {"name": n, "branch": e["branch"], "axis_position": e.get("axis_position"),
                  "report": {"refuses": e.get("refuses"), "costs": e.get("costs"), "run": e.get("run")},
                  "session": e.get("session"), "recording": bool(e.get("recording")), "kept": True,
                  "recording_path": os.path.join(root, XV_DIR, "prototypes", slice_id, n, "recording.md")}
    data["prototypes"] = []
    for n in NAMES:
        p = out.get(n) or {}
        r = p.get("report") or {}
        if n in stopped:
            r = {"refuses": "stopped: its budget is spent"}
        lines.append(f"| {n} | {p.get('axis_position', '')} | {r.get('refuses', '')} | {r.get('costs', '')} | "
                     f"`{r.get('run', '')}` |")
    for n in NAMES:
        p = out.get(n) or {}
        lines += ["", f"## {n}: {p.get('axis_position', '')}", ""]
        if p.get("recording") and p.get("kept"):
            lines.append(open(p["recording_path"]).read().strip())
        elif p.get("recording"):
            dest = os.path.join(root, XV_DIR, "prototypes", slice_id, n)
            os.makedirs(dest, exist_ok=True)
            shutil.copy(p["recording_path"], os.path.join(dest, "recording.md"))
            lines.append(open(p["recording_path"]).read().strip())
        else:
            lines.append("No recording. This prototype cannot be compared with the others.")
        if p and not p.get("kept"):
            s = p.get("spend") or {}
            s.update(step=f"prototype-{n}", at=now())
            data["spend"].append(s)
        data["prototypes"].append({"name": n, "branch": p.get("branch"), "axis_position": p.get("axis_position"),
                                   "refuses": (p.get("report") or {}).get("refuses"),
                                   "costs": (p.get("report") or {}).get("costs"),
                                   "run": (p.get("report") or {}).get("run"),
                                   "recording": f"{XV_DIR}/prototypes/{slice_id}/{n}/recording.md" if p.get("recording") else None,
                                   "session": p.get("session")})
    packet = os.path.join(root, XV_DIR, "slices", f"{slice_id}.prototypes.md")
    with open(packet, "w") as f:
        f.write("\n".join(lines) + "\n")
    ready = sum(1 for n in NAMES if (out.get(n) or {}).get("recording"))
    ran_out = {n: ", ".join(f"{k} {spent[n][k]} of {budgets[n][k]}" for k in over[n]) for n in sorted(stopped)}
    data["checks"]["prototype"] = {"prototypes_ready": ready, "ran_out": ran_out, "at": now()}
    data["checks"].setdefault("reports", []).append({"agent": "prototype", "status": "done", "at": now(),
                                                     "summary": f"{ready} of 3 with a recording"})
    v = orders.verdict(data, "prototype", config)
    if v["stop"]:
        st = v["stop"]
        data["stops"].append({"at": now(), "step": "prototype", "order": st["order"], "seat": st["seat"],
                              "question": st["question"] + f" Side by side: `{XV_DIR}/slices/{slice_id}.prototypes.md`.",
                              "answered_by": [], "answer": None})
        data["status"] = "stopped"
    data["next"] = "prototype"
    for n in sorted(stopped):
        body = record.log_line(body, "watch", f"variant {n} stopped: its budget is spent")
    body = record.log_line(body, "watch", f"{ready} prototypes ready; the pick is for two people")
    record.save(path, data, body)
    git(["add", "-A"], root)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", f"xv({slice_id}): three prototypes, side by side"],
                   cwd=root)
    v["packet"] = os.path.relpath(packet, root)
    return (EXIT_STOP if v["stop"] else 0), v


def pick(slice_id, variant, by, with_user=None, scenario_file=None):
    path = record_path(repo_root(), slice_id)
    root = slice_root(path)
    config = load_config(root)
    data, body = record.load(root, slice_id)[1:]
    who = [w.strip() for w in by.split(",") if w.strip()]
    from xvlib import solo
    if len(set(who)) < 2 and not solo(config):
        raise XVError("the pick is for two people: --by <name>,<name> "
                      "(a one-person team sets seats.two_people: solo in .xv/config.yml)")
    if variant != "none" and not scenario_file:
        raise XVError("restate the pick as the scenario the maker turns red and then green: --scenario-file <file>")
    names = {p["name"] for p in data.get("prototypes") or []}
    if variant != "none" and variant not in names:
        raise XVError(f"no prototype {variant!r}; one of {sorted(names)} or none")
    if variant != "none" and not next(p for p in data["prototypes"] if p["name"] == variant).get("branch"):
        raise XVError(f"prototype {variant} stopped at its budget and has nothing to pick")
    # discard every prototype, the pick too: the context that built it never builds the pick
    for p in data.get("prototypes") or []:
        wt = os.path.join(worktrees_dir(root, config), f"{slice_id}-proto-{p['name']}")
        git(["worktree", "remove", "--force", wt], root, check=False)
        if p.get("branch"):
            git(["branch", "-D", p["branch"]], root, check=False)
        p["picked"] = p["name"] == variant
    answer = (f"picked {variant}" if variant != "none" else "picked none") + \
             (f", with {with_user}" if with_user else ", with no user")
    for s in data["stops"]:
        if s.get("answer") is None and s["order"] in ("prototypes_ready", "prototype_budget_spent"):
            s.update(answered_by=who, answer=answer, answered_at=now())
    stop = {"order": "prototypes_ready", "question": f"Which prototype on the axis {data.get('axis')}, or none?"}
    rec = record.write_decision(root, slice_id, who + ([f"{with_user} (user)"] if with_user else []), stop,
                                answer + "." + (f" Restated as the scenario in {os.path.basename(scenario_file)}."
                                                if scenario_file else ""))
    data["decisions"].append({"date": today(), "who": who, "with_user": with_user, "decision": answer, "record": rec})
    if variant == "none":
        data["status"], data["next"] = "abandoned", "none"
        body = record.log_line(body, ",".join(who), "picked none; the slice is set aside")
    else:
        restated = open(scenario_file).read().strip()
        old = body.split("## Scenario\n\n", 1)[1].split("\n\n## ", 1)[0]
        body = body.replace(f"## Scenario\n\n{old}", f"## Scenario\n\n{restated}", 1)
        body = record.log_line(body, ",".join(who), f"picked {variant}; scenario restated (was: {old})")
        data["kind"], data["status"], data["next"] = "feature", "working", "forecaster"
        data["prototype_sessions"] = [p.get("session") for p in data["prototypes"] if p.get("session")]
    record.save(path, data, body)
    git(["add", "-A"], root)
    subprocess.run(["git", "commit", "-q", "--no-verify", "-m", f"xv({slice_id}): the pick, {answer}"], cwd=root)
    return {"slice": slice_id, "picked": variant, "by": who, "decision": rec, "next": data["next"]}


def run(slice_id):
    """Called by `xv run` when the record's next step is prototype."""
    code, v = start(slice_id)
    print(json.dumps(v, indent=2))
    return code


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv prototype", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("id")
    s.add_argument("--axis")
    s.add_argument("--variant", action="append", help="a position on the axis; give three, or none for the defaults")
    s.add_argument("--serial", action="store_true", help="one at a time, as on one local GPU")
    k = sub.add_parser("pick")
    k.add_argument("id")
    k.add_argument("--variant", required=True)
    k.add_argument("--by", required=True)
    k.add_argument("--with-user")
    k.add_argument("--scenario-file")
    a = p.parse_args(argv)
    try:
        if a.cmd == "start":
            code, v = start(a.id, a.axis, a.variant, a.serial)
            print(json.dumps(v, indent=2))
            sys.exit(code)
        print(json.dumps(pick(a.id, a.variant, a.by, a.with_user, a.scenario_file), indent=2))
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

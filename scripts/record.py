#!/usr/bin/env python3
"""Create and update a slice record, and keep the estimation guide append-only.

A slice record is `.xv/slices/<id>.md`: fixed fields in front matter, prose in
the body. See docs/slice-record.md for every field. The estimation guide,
the standards file and the retro read slice records and nothing else.

Usage: xv record <command> ...   (run `xv record -h` for the list)
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import (XV_DIR, XVError, die, emit, git, now, read_doc,  # noqa: E402
                   record_path, repo_root, slice_root, today, write_doc)

FIELDS = [
    # name, default
    ("id", None), ("title", ""), ("kind", "feature"), ("status", "open"),
    ("set_by", ""), ("created", None), ("branch", ""), ("base", None), ("next", "forecaster"),
    ("forecast", None), ("budget", None), ("red", None), ("wall_baseline", None),
    ("moved_tests", []), ("suite", None), ("cleaner_commit", None),
    ("packet", None), ("shape_change", None), ("pitch_contradiction", None),
    ("spend", []), ("stops", []), ("decisions", []), ("prototypes", []), ("overrides", []), ("checks", {}),
]
LIST_FIELDS = {"moved_tests", "spend", "stops", "decisions", "prototypes", "overrides"}
STATUSES = {"open", "working", "stopped", "ready", "closed", "abandoned"}
STEPS = ["forecaster", "scenario", "maker", "cleaner", "guardian", "close", "none"]
SEATS = {"originator", "two_people", "chief_engineer"}

BODY_TEMPLATE = """# {title}

## Scenario

{scenario}

## May ignore

{ignore}

## Recording

{recording}

## Log

"""


# ---------------------------------------------------------------- load and save

def load(root, slice_id):
    path = record_path(root, slice_id)
    data, body = read_doc(path)
    for name, default in FIELDS:
        data.setdefault(name, json.loads(json.dumps(default)))
    return path, data, body


def save(path, data, body):
    ordered = {name: data.get(name) for name, _ in FIELDS}
    for k, v in data.items():  # keep any field a team added
        ordered.setdefault(k, v)
    write_doc(path, ordered, body)


def log_line(body, who, text):
    text = " ".join(str(text).split())
    return body.rstrip("\n") + f"\n- {now()} {who}: {text}\n"


# ---------------------------------------------------------------- commands

def cmd_new(a):
    root = repo_root()
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", a.id):
        raise XVError("a slice id is letters, digits, dot, dash and underscore")
    path = os.path.join(root, XV_DIR, "slices", f"{a.id}.md")
    if os.path.exists(path):
        raise XVError(f"{path} exists; a slice id is used once")
    if not a.by:
        raise XVError("--by is required: a slice record names who set the work going")
    scenario = open(a.scenario_file).read().strip() if a.scenario_file else (a.scenario or "")
    if not scenario:
        raise XVError("a slice needs its scenario in words (--scenario or --scenario-file)")
    data = {name: json.loads(json.dumps(d)) for name, d in FIELDS}
    data.update(id=a.id, title=a.title or a.id, kind=a.kind, set_by=a.by,
                created=today(), branch=a.branch or f"xv/{a.id}")
    if a.kind == "prototype":
        data["next"] = "prototype"
        data["axis"] = a.axis
    body = BODY_TEMPLATE.format(title=data["title"], scenario=scenario,
                                ignore=a.ignore or "Nothing stated.",
                                recording=a.recording or "None. A feature starts from words.")
    body = log_line(body, "watch", f"slice opened by {a.by}")
    save(path, data, body)
    print(os.path.relpath(path, root))


def cmd_show(a):
    path, data, body = load(repo_root(), a.id)
    if a.json:
        emit(data, True)
    else:
        print(open(path).read())


def cmd_get(a):
    _, data, _ = load(repo_root(), a.id)
    value = data.get(a.field)
    print(value if isinstance(value, str) else json.dumps(value))


def parse_value(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def cmd_set(a):
    path, data, body = load(repo_root(), a.id)
    value = parse_value(a.value)
    if a.field in LIST_FIELDS:
        raise XVError(f"{a.field} is a list; use `xv record add` so nothing is overwritten")
    if a.field == "status" and value not in STATUSES:
        raise XVError(f"status is one of {sorted(STATUSES)}")
    if a.field == "next" and value not in STEPS + ["prototype"]:
        raise XVError(f"next is one of {STEPS + ['prototype']}")
    if a.field == "forecast" and data.get("forecast") and not a.force:
        raise XVError("the forecast is written once, before the work; the actual goes in spend")
    if a.field == "budget":
        check_budget_change(data, value, a.by)
    data[a.field] = value
    body = log_line(body, a.by or "watch", f"set {a.field}")
    save(path, data, body)


def check_budget_change(data, value, by):
    """A budget is a person's call. Raising one past the team limit is two people's."""
    if not by:
        raise XVError("a budget is set by a person: pass --by <name>")
    old = data.get("budget") or {}
    if not isinstance(value, dict):
        raise XVError("budget is a JSON object, e.g. {\"tokens\": 400000, \"usd\": 3}")
    value["set_by"] = by
    if old and any(value.get(k, 0) > old.get(k, 0) for k in ("tokens", "usd", "turns") if old.get(k)):
        value["raised_from"] = {k: old.get(k) for k in ("tokens", "usd", "turns") if k in old}


def cmd_add(a):
    path, data, body = load(repo_root(), a.id)
    if a.field not in LIST_FIELDS:
        raise XVError(f"add works on {sorted(LIST_FIELDS)}")
    item = parse_value(a.value)
    if not isinstance(item, dict):
        raise XVError("an item is a JSON object")
    item.setdefault("at", now())
    data[a.field].append(item)
    body = log_line(body, a.by or "watch", f"added to {a.field}")
    save(path, data, body)


def cmd_move(a):
    path, data, body = load(repo_root(), a.id)
    for name in ("file", "assertion", "why"):
        if not getattr(a, name):
            raise XVError(f"a moved test names its {name}")
    data["moved_tests"].append({"file": a.file, "assertion": a.assertion, "why": a.why,
                                "by": a.by or "maker", "at": now()})
    body = log_line(body, a.by or "maker", f"moved a test in {a.file}: {a.why}")
    save(path, data, body)


def cmd_override(a):
    """A person declines a standard's fix on this slice. The retro counts these."""
    path, data, body = load(repo_root(), a.id)
    data["overrides"].append({"rule": a.rule, "by": a.by, "why": a.why, "at": now()})
    body = log_line(body, a.by, f"overrode the rule \"{a.rule}\": {a.why}")
    save(path, data, body)


def cmd_stop(a):
    path, data, body = load(repo_root(), a.id)
    if a.seat not in SEATS:
        raise XVError(f"seat is one of {sorted(SEATS)}")
    data["stops"].append({"at": now(), "order": a.order, "seat": a.seat,
                          "question": a.question, "answered_by": [], "answer": None})
    data["status"] = "stopped"
    body = log_line(body, "watch", f"stop ({a.order}) for {a.seat}: {a.question}")
    save(path, data, body)


def cmd_answer(a):
    root = repo_root()
    path, data, body = load(root, a.id)
    open_stops = [s for s in data["stops"] if s.get("answer") is None]
    if not open_stops:
        raise XVError("no open stop on this slice")
    stop = open_stops[-1]
    who = [w.strip() for w in a.by.split(",") if w.strip()]
    if not who:
        raise XVError("an answer names who gave it")
    if stop["seat"] == "two_people" and len(set(who)) < 2:
        raise XVError("this stop is for two people: name both with --by a,b")
    stop["answered_by"], stop["answer"], stop["answered_at"] = who, a.answer, now()
    data["status"] = "working" if a.resume else data["status"]
    if a.next:
        data["next"] = a.next
    if stop["seat"] == "two_people" or a.decision:
        rec = write_decision(slice_root(path), data["id"], who, stop, a.answer)
        data["decisions"].append({"date": today(), "who": who, "decision": a.answer,
                                  "record": rec})
    body = log_line(body, ",".join(who), f"answered {stop['order']}: {a.answer}")
    save(path, data, body)


def write_decision(root, slice_id, who, stop, answer):
    """A short record of a decision, with who took part. Binds later agents."""
    d = os.path.join(root, XV_DIR, "decisions")
    os.makedirs(d, exist_ok=True)
    base = f"{today()}-{slice_id}"
    path, n = os.path.join(d, base + ".md"), 2
    while os.path.exists(path):
        path, n = os.path.join(d, f"{base}-{n}.md"), n + 1
    with open(path, "w") as f:
        f.write(f"---\ndate: {today()}\nslice: {slice_id}\nwho: {json.dumps(who)}\n"
                f"order: {stop['order']}\n---\n\n# {stop['question']}\n\n{answer}\n")
    return os.path.relpath(path, root)


REPORT_RE = re.compile(r"```xv-report\s*\n(.*?)\n```", re.S)


def extract_report(text):
    found = REPORT_RE.findall(text)
    if not found:
        # Claude's JSON output wraps the final message in "result"
        try:
            outer = json.loads(text)
            if isinstance(outer, dict) and isinstance(outer.get("result"), str):
                return extract_report(outer["result"])
        except json.JSONDecodeError:
            pass
        # opencode --format json: one event per line, text parts carry the message
        texts = []
        for line in text.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            part = ev.get("part") if isinstance(ev, dict) else None
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(part.get("text", ""))
        if texts:
            joined = "\n".join(texts)
            if REPORT_RE.search(joined):
                return extract_report(joined)
        return None
    try:
        return json.loads(found[-1])
    except json.JSONDecodeError as e:
        raise XVError(f"the xv-report block is not JSON: {e}")


def apply_report(data, body, agent, text):
    """Apply a worker's final message to the record. Returns (body, report)."""
    report = extract_report(text)
    checks = data.setdefault("checks", {})
    if report is None:
        report = {"agent": agent, "status": "no-report", "summary": "ended without an xv-report block"}
        checks.setdefault("reports", []).append(report)
        return log_line(body, agent, report["summary"]), None
    report.setdefault("agent", agent)
    # only the agents that may move a test record one; the guardian's count is not a record
    moves = report.get("moved_tests") if agent in ("maker", "cleaner") else None
    for mv in moves if isinstance(moves, list) else []:
        if isinstance(mv, dict) and all(mv.get(k) for k in ("file", "assertion", "why")):
            mv.setdefault("by", agent)
            mv.setdefault("at", now())
            if mv not in data["moved_tests"]:
                data["moved_tests"].append(mv)
    if agent == "scenario" and report.get("red"):
        data["red"] = report["red"]
    if agent == "forecaster" and report.get("forecast") and not data.get("forecast"):
        data["forecast"] = report["forecast"]
    if agent == "cleaner" and report.get("commit"):
        data["cleaner_commit"] = report["commit"]
    keep = {k: report.get(k) for k in ("agent", "status", "summary", "stop", "why", "shape_actual",
                                       "picture_change", "shape_breadth", "shape_proposals",
                                       "candidate_standards", "applied") if report.get(k) is not None}
    keep["at"] = now()
    checks.setdefault("reports", []).append(keep)
    return log_line(body, agent, f"{report.get('status', '?')}: {report.get('summary', '')}"), report


def cmd_report(a):
    path, data, body = load(repo_root(), a.id)
    text = sys.stdin.read() if a.file == "-" else open(a.file).read()
    body, report = apply_report(data, body, a.agent, text)
    save(path, data, body)
    emit(report or {"agent": a.agent, "status": "no-report"}, True)


def cmd_packet(a):
    """Attach the guardian's packet and copy its two fixed fields."""
    root = repo_root()
    path, data, body = load(root, a.id)
    pdata, _ = read_doc(a.file)
    for field in ("shape_change", "pitch_contradiction"):
        value = pdata.get(field)
        if value not in ("yes", "no"):
            raise XVError(f"the packet's {field} must be yes or no, found {value!r}")
        data[field] = value
    data["packet"] = os.path.relpath(os.path.abspath(a.file), slice_root(path))
    body = log_line(body, "guardian", f"packet: shape_change={data['shape_change']}, "
                                      f"pitch_contradiction={data['pitch_contradiction']}")
    save(path, data, body)


def cmd_export(a):
    """The record as a pull request body, for teams whose record home is the PR."""
    path, data, body = load(repo_root(), a.id)
    out = [f"## {data['title']}", "", f"Slice `{data['id']}`, set going by {data['set_by']}.", ""]
    m = re.search(r"## Scenario\n\n(.*?)\n\n## ", body, re.S)
    if m:
        out += ["### Scenario", "", m.group(1).strip(), ""]
    if data["moved_tests"]:
        out += ["### Moved tests", ""] + [f"- `{t['file']}`: {t['assertion']} ({t['why']})"
                                          for t in data["moved_tests"]] + [""]
    out += [f"shape_change: {data['shape_change']} · pitch_contradiction: {data['pitch_contradiction']}", ""]
    if data.get("packet"):
        ppath = os.path.join(slice_root(path), data["packet"])
        if os.path.exists(ppath):
            out += ["<details><summary>Guardian packet</summary>", "",
                    read_doc(ppath)[1].strip(), "", "</details>", ""]
    out += ["<details><summary>Slice record</summary>", "", "```", open(path).read(), "```",
            "", "</details>"]
    print("\n".join(out))


# ---------------------------------------------------------------- estimation guide

GUIDE_HEADER = """# Estimation guide

One row per harness and model per closed slice. The forecaster appends the rows
when a slice closes; nobody edits a row in place. Anyone may revert a row by
deleting it. `xv record guide-verify` refuses an edited or reordered row.

A forecast uses only rows with the same harness and model.

| slice | closed | harness | model | forecast tokens | actual tokens | gap | forecast usd | actual usd | wall s | shape forecast | shape actual | why |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def guide_path(root):
    return os.path.join(root, XV_DIR, "estimation.md")


def guide_rows(text):
    return [line for line in text.splitlines()
            if line.startswith("| ") and not line.startswith("| slice ") and not line.startswith("| ---")]


def actual_by_key(spend):
    keys = {}
    for s in spend:
        key = (s.get("harness") or "?", s.get("model") or "?")
        k = keys.setdefault(key, {"tokens": 0, "usd": 0.0, "wall_s": 0.0})
        k["tokens"] += int(s.get("tokens") or 0)  # input, output, cache read and cache write, as everywhere
        k["usd"] += float(s.get("usd") or 0)
        k["wall_s"] += float(s.get("wall_s") or 0)
    return keys


def cmd_guide_append(a):
    root = repo_root()
    path, data, _ = load(root, a.id)
    gpath = guide_path(slice_root(path))
    text = open(gpath).read() if os.path.exists(gpath) else GUIDE_HEADER
    if any(r.split("|")[1].strip() == data["id"] for r in guide_rows(text)):
        raise XVError(f"the guide already has {data['id']}; one entry per closed slice")
    if not data.get("spend"):
        raise XVError("no actual spend in the record; the watch writes it as the work runs")
    if not a.why:
        raise XVError("one line on why the gap is what it is (--why)")
    forecast = data.get("forecast") or {}
    by_key = {(f.get("harness"), f.get("model")): f for f in forecast.get("keys", [])}
    rows = []
    for (harness, model), act in sorted(actual_by_key(data["spend"]).items()):
        f = by_key.get((harness, model), {})
        ftok = f.get("tokens")
        gap = f"{(act['tokens'] - ftok) / ftok:+.0%}" if ftok else "no forecast"
        cells = [data["id"], today(), harness, model, ftok if ftok is not None else "",
                 act["tokens"], gap, f.get("usd", ""), f"{act['usd']:.2f}", f"{act['wall_s']:.0f}",
                 forecast.get("shape", ""), a.shape or "", a.why]
        rows.append("| " + " | ".join(str(c).replace("|", "/") for c in cells) + " |")
    with open(gpath, "w") as fh:
        fh.write(text.rstrip("\n") + "\n" + "\n".join(rows) + "\n")
    print("\n".join(rows))


def cmd_guide_verify(a):
    """Append-only: every row at HEAD is a row from the base, unchanged and in order,
    or a new row after all of them. A deleted row is a revert and is allowed."""
    root = repo_root()
    rel = os.path.join(XV_DIR, "estimation.md")
    now_path = os.path.join(root, rel)
    if not os.path.exists(now_path):
        print("no estimation guide")
        return
    current = guide_rows(open(now_path).read())
    base_text = git(["show", f"{a.base}:{rel}"], root, check=False)
    base = guide_rows(base_text)
    base_set = set(base)
    seen_new, last_base_index = False, -1
    problems = []
    for row in current:
        if row in base_set:
            if seen_new:
                problems.append(f"an older row was moved after a new one: {row[:80]}")
            idx = base.index(row)
            if idx < last_base_index:
                problems.append(f"rows were reordered: {row[:80]}")
            last_base_index = idx
        else:
            seen_new = True
            slice_id = row.split("|")[1].strip()
            if any(b.split("|")[1].strip() == slice_id for b in base):
                problems.append(f"row for {slice_id} was edited in place (or added twice)")
    if problems:
        die("the estimation guide is append-only:\n  " + "\n  ".join(problems), 2)
    print(f"estimation guide ok: {len(current)} rows, {len([r for r in current if r not in base_set])} new")


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="xv record", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="open a slice record")
    s.add_argument("id")
    s.add_argument("--title")
    s.add_argument("--by", help="who set the work going")
    s.add_argument("--kind", choices=["feature", "defect", "prototype"], default="feature")
    s.add_argument("--scenario")
    s.add_argument("--scenario-file")
    s.add_argument("--ignore", help="what this slice may ignore")
    s.add_argument("--recording", help="path to the recording, for a defect")
    s.add_argument("--branch")
    s.add_argument("--axis", help="for a prototype slice: the one axis the three differ on")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("show")
    s.add_argument("id")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("get")
    s.add_argument("id")
    s.add_argument("field")
    s.set_defaults(fn=cmd_get)

    s = sub.add_parser("set", help="set one field (not a list)")
    s.add_argument("id")
    s.add_argument("field")
    s.add_argument("value")
    s.add_argument("--by")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_set)

    s = sub.add_parser("add", help="append one item to a list field")
    s.add_argument("id")
    s.add_argument("field")
    s.add_argument("value")
    s.add_argument("--by")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("move", help="record a moved test")
    s.add_argument("id")
    s.add_argument("--file")
    s.add_argument("--assertion")
    s.add_argument("--why")
    s.add_argument("--by")
    s.set_defaults(fn=cmd_move)

    s = sub.add_parser("override", help="a person declines a standard's fix on this slice")
    s.add_argument("id")
    s.add_argument("--rule", required=True, help="the rule, as it reads in .xv/standards.md")
    s.add_argument("--by", required=True)
    s.add_argument("--why", required=True)
    s.set_defaults(fn=cmd_override)

    s = sub.add_parser("stop", help="raise a stop for a seat")
    s.add_argument("id")
    s.add_argument("--order", required=True)
    s.add_argument("--seat", required=True)
    s.add_argument("--question", required=True)
    s.set_defaults(fn=cmd_stop)

    s = sub.add_parser("answer", help="a person answers the open stop")
    s.add_argument("id")
    s.add_argument("--by", required=True, help="comma-separated names")
    s.add_argument("--answer", required=True)
    s.add_argument("--next", choices=STEPS + ["prototype"])
    s.add_argument("--resume", action="store_true")
    s.add_argument("--decision", action="store_true", help="write a decision record")
    s.set_defaults(fn=cmd_answer)

    s = sub.add_parser("report", help="apply a worker's xv-report block")
    s.add_argument("id")
    s.add_argument("agent")
    s.add_argument("file", help="the worker's output, or - for stdin")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("packet", help="attach the guardian's packet")
    s.add_argument("id")
    s.add_argument("file")
    s.set_defaults(fn=cmd_packet)

    s = sub.add_parser("export", help="render the record as a PR body")
    s.add_argument("id")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("guide-append", help="append the closed slice to the estimation guide")
    s.add_argument("id")
    s.add_argument("--why", required=True)
    s.add_argument("--shape", help="the shape change that actually happened")
    s.set_defaults(fn=cmd_guide_append)

    s = sub.add_parser("guide-verify", help="fail if the guide was edited, not appended")
    s.add_argument("--base", default="HEAD")
    s.set_defaults(fn=cmd_guide_verify)

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""A pairing: the person who set the work going works on a slice with the watch's own session.

It opens at an open stop or a send-back, runs from the scenario to the cleaner as the person directs, and hands the
slice back to the loop at a step.

The watch's session is the person's pair. At the person's direction it writes and changes tests and code. While the
pairing is open, `xv step`, `xv run`, `xv close` and `xv slice rebase` refuse on the slice. A test written or changed
in a pairing is not blind: the record and the packet say so, and the guardian runs fresh after.

Usage:
  xv pairing start <id> --by <name> --why "<why>" [--session <reader>:<id or file>] [--agent <name>]
  xv pairing end <id> --next maker|cleaner|guardian|scenario
"""

import argparse
import os
import subprocess
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packet as packetlib  # noqa: E402
import record  # noqa: E402
import spend as spendlib  # noqa: E402
import wall  # noqa: E402
from xvlib import XVError, die, emit, git, load_config, match_any, now, record_path, repo_root, slice_root, solo  # noqa: E402

RESUME = ("maker", "cleaner", "guardian", "scenario")
AMENDED = "\n### Amended "


def prefix(p):
    """What each commit made in the pairing starts with."""
    return f"pairing ({p['by']} with {p['agent']}):"


def find_session(given):
    """The session the person pairs with: `--session <reader>:<session id or file>`, where the reader is one of the
    readers `xv spend read` takes. None when none is named."""
    reader, _, source = (given or "").partition(":")
    if reader not in spendlib.READERS or not source:
        return None
    if reader != "claude-session":
        # only a session reader cuts a time window: the others are kept by their reader's name
        return {"harness": reader, "id": source, "transcript": None}
    if os.path.isfile(source):
        path = os.path.abspath(source)
        return {"harness": reader, "id": os.path.splitext(os.path.basename(path))[0], "transcript": path}
    return {"harness": reader, "id": source, "transcript": spendlib.claude_transcript(source)}


def reader_of(session):
    """The `xv spend read` reader a session is read through; None when none was named."""
    return (session or {}).get("harness")


def at_send_back(data):
    """The watch's own send-back the slice is at: the last stop is the watch's, and no step has reported since."""
    stops = data.get("stops") or []
    if not stops or stops[-1].get("seat") != "watch":
        return None
    reports = (data.get("checks") or {}).get("reports") or []
    last = stops[-1]
    return last if last.get("report_n") is not None and last["report_n"] == len(reports) - 1 else None


def commit_record(root, paths, message):
    """Commit the record (and the packet) on the slice branch; a trial's ignored .xv/ commits nothing."""
    paths = [f for f in paths if subprocess.run(["git", "check-ignore", "-q", f], cwd=root).returncode != 0]
    if not paths:
        return None
    git(["add", "-A", "--", *paths], root)
    if subprocess.run(["git", "diff", "--cached", "--quiet", "--", *paths], cwd=root).returncode == 0:
        return None
    git(["commit", "-q", "--no-verify", "-m", message, "--", *paths], root)
    return git(["rev-parse", "HEAD"], root).strip()


def load(slice_id):
    path = record_path(repo_root(), slice_id)
    root = slice_root(path)
    path, data, body = record.load(root, slice_id)
    data.setdefault("pairings", [])
    return root, path, data, body


def cmd_start(a):
    root, path, data, body = load(a.id)
    if data.get("status") in ("closed", "abandoned"):
        raise XVError(f"{a.id} is {data['status']}: a pairing opens on a slice that is still running")
    p = record.open_pairing(data)
    if p:
        raise XVError(f"pairing {p['n']} is already open on {a.id} ({p['by']} with {p['agent']}); "
                      f"end it with `xv pairing end {a.id} --next ...` first")
    if a.by != data.get("set_by"):
        raise XVError(f"only the person who set the work going pairs on {a.id}: {data.get('set_by')}, not {a.by}")
    if not (a.why or "").strip():
        raise XVError("--why says why the person pairs: the handoff that did not work, or what is too small for a pass")
    open_stops = [s for s in data["stops"] if s.get("answer") is None]
    stop = open_stops[-1] if open_stops else at_send_back(data)
    if stop is None:
        raise XVError(f"{a.id} has no open stop or send-back: a pairing opens at one")
    if stop.get("answer") is None and stop["seat"] == "two_people" and not solo(load_config(root)):
        raise XVError(f"the open stop ({stop['order']}) is for two people: answer it with `xv record answer` first; "
                      "a pairing answers a stop for the person who set the work going")
    session = find_session(a.session)
    agent = a.agent or spendlib.AGENT_OF.get(reader_of(session), "the watch")
    n = len(data["pairings"]) + 1
    at = now()
    entry = {"n": n, "by": a.by, "agent": agent, "session": session, "why": a.why.strip(), "started_at": at,
             "start_head": git(["rev-parse", "HEAD"], root).strip(), "order": stop["order"],
             "step": stop.get("step") or data.get("next"), "opened_at": "stop" if stop.get("answer") is None else "send-back",
             "amendments_at_start": body.count(AMENDED)}
    entry["prefix"] = prefix(entry)
    if stop.get("answer") is None:
        # the pairing is the person's answer to the stop; where the slice goes is said when it ends
        stop["answered_by"], stop["answer"], stop["answered_at"] = [a.by], f"pairing: {entry['why']}", at
        stop["pick"] = "pairing"
        stop["settled"] = f"{a.by} paired with {agent} on the slice (pairing {n}), because: {entry['why']}"
        had_seen = "budget_seen" in stop
        seen = stop.pop("budget_seen", None)
        if had_seen and seen != data.get("budget"):
            amounts = lambda b: b and {k: b[k] for k in ("tokens", "usd", "turns") if k in b}
            stop["budget_change"] = {"from": amounts(seen), "to": amounts(data.get("budget"))}
        body = record.log_line(body, a.by, f"answered {stop['order']}: pairing: {entry['why']}")
    stop["pairing"] = n
    data["pairings"].append(entry)
    data["status"] = "pairing"
    which = f"{session['harness'] or 'unknown harness'} session {session['id']}" if session else "no named session"
    body = record.log_line(body, "watch", f"pairing {n} opened at {entry['opened_at']} {stop['order']}: {a.by} with "
                                          f"{agent} ({which}), because: {entry['why']}. Commits start with "
                                          f"\"{entry['prefix']}\"; xv step and xv run refuse until it ends")
    if session and session["harness"] and reader_of(session) != "claude-session":
        body = record.log_line(body, "watch", f"pairing {n}: the {session['harness']} reader cannot cut a time window, "
                                              "so the pair session's spend cannot be read when the pairing ends")
    elif not session or not session.get("transcript"):
        body = record.log_line(body, "watch", f"pairing {n}: no transcript was found for the pair session, so its "
                                              "spend cannot be read when the pairing ends")
    record.save(path, data, body)
    commit_record(root, [os.path.relpath(path, root)], f"xv({a.id}): pairing {n} opened by {a.by} with {agent}")
    emit({"slice": a.id, "pairing": n, "prefix": entry["prefix"], "session": session, "answered": stop["order"],
          "note": f"xv step and xv run refuse on {a.id} until `xv pairing end {a.id} --next <step>`"}, True)


def unrecorded_old_tests(root, data, p, config):
    """Test files that existed when the pairing opened and lost or changed a line in it, with no move recorded in it."""
    paths = (config.get("tests") or {}).get("paths") or []
    red = set((data.get("red") or {}).get("files") or [])
    at_start = set(git(["ls-tree", "-r", "--name-only", p["start_head"]], root).split())
    moved = {f for m in data.get("moved_tests") or [] if m.get("pairing") == p["n"] for f in (m.get("file"), m.get("from"))}
    return sorted(f for f in at_start if (f in red or match_any(f, paths)) and f not in moved
                  and wall.removed_lines(root, p["start_head"], f, None))


def pairing_spend(p, ended):
    """The pair session's spend between the pairing's start and end, as a spend row; or (None, why it was not read)."""
    session = p.get("session") or {}
    if not session.get("id"):
        return None, "no session was named when the pairing opened"
    try:
        # the record's times are whole seconds: the window runs to the end of the second the pairing ended in
        until = (spendlib.parse_time(ended) + timedelta(seconds=1)).isoformat()
        row, transcript = spendlib.window_row(reader_of(session), session.get("transcript") or session["id"],
                                              p["started_at"], until)
    except (XVError, OSError, ValueError) as e:
        return None, str(e)
    if not row.get("turns"):
        return None, f"the transcript {transcript} has no turns between {p['started_at']} and {ended}"
    start, end = spendlib.parse_time(p["started_at"]), spendlib.parse_time(ended)
    row.update(step="pairing", pairing=p["n"], at=ended, session=session["id"], log=transcript,
               wall_s=(end - start).total_seconds() if start and end else row.get("wall_s"))
    return row, None


def cmd_end(a):
    root, path, data, body = load(a.id)
    p = record.open_pairing(data)
    if not p:
        raise XVError(f"no pairing is open on {a.id}")
    if a.next == "close":
        raise XVError("a pairing does not end at close: the guardian checks the pairing's work in a fresh context "
                      "first; end it with --next guardian")
    if a.next not in RESUME:
        raise XVError(f"--next is one of {', '.join(RESUME)}")
    if a.next == "scenario" and body.count(AMENDED) <= p.get("amendments_at_start", 0):
        raise XVError("--next scenario needs an amendment made since the pairing opened (`xv slice amend`): the "
                      "scenario agent writes a red for a scenario that changed, not for the pairing's code")
    rel = os.path.relpath(path, root)
    own = f".xv/slices/{a.id}."
    dirty = [line[3:] for line in git(["status", "--porcelain", "--untracked-files=all"], root).splitlines()
             if line[3:] != rel and not line[3:].startswith(own)]
    if dirty:
        raise XVError("commit the pairing's work first, each commit starting with "
                      f"\"{p['prefix']}\"; not committed: " + ", ".join(dirty))
    config = load_config(root)
    missing = unrecorded_old_tests(root, data, p, config)
    if missing:
        raise XVError("these old test files lost or changed a line in the pairing, and no move is recorded for them "
                      "in it: " + ", ".join(missing) + f". Record each with `xv record move {a.id} --file <file> "
                      "--assertion '<was; now>' --why '<why>'`; it is recorded in the person's name")
    ended = now()
    head = git(["rev-parse", "HEAD"], root).strip()
    log = [line.split("\t", 1) for line in
           git(["log", "--reverse", "--format=%H%x09%s", f"{p['start_head']}..{head}"], root).splitlines() if line]
    work = [(h, s) for h, s in log if not s.startswith(f"xv({a.id}):")]
    paths = (config.get("tests") or {}).get("paths") or []
    red = set((data.get("red") or {}).get("files") or [])
    touched = git(["diff", "--name-only", "--no-renames", p["start_head"], head], root).split()
    row, why_not = pairing_spend(p, ended)
    p.update(ended_at=ended, end_head=head, next=a.next, commits=[h for h, _ in work],
             unprefixed=[f"{h} {s}" for h, s in work if not s.startswith(f"pairing ({p['by']} with ")],
             not_blind=sorted(f for f in touched if (f in red or match_any(f, paths)) and not f.startswith(".xv/")
                              and os.path.isfile(os.path.join(root, f))),
             spend=row, spend_note=why_not)
    if row:
        data["spend"].append(row)
    stop = next((s for s in reversed(data["stops"]) if s.get("pairing") == p["n"]), None)
    if stop:
        # the next agent reads this stop's settled text (`xv prompt`): it says the pairing came between
        stop["settled"] = (stop.get("settled") or "") + (f" Pairing {p['n']} ({p['by']} with {p['agent']}) ended at "
                                                          f"{head[:10]}; the slice resumes at {a.next}.")
    if stop and stop.get("seat") != "watch":
        stopped_at = stop.get("step") or p.get("step")
        steps = record.STEPS
        if not (stopped_at in steps and steps.index(a.next) > steps.index(stopped_at)):
            stop["sent_back"], stop["sent_back_to"] = True, a.next
    data["next"], data["status"] = a.next, "working"
    body = record.log_line(body, "watch", f"pairing {p['n']} ended: {p['by']} with {p['agent']}; "
                                          f"{len(work)} commit(s); resumes at {a.next}; spend: {packetlib.spend_words(p)}")
    if p["not_blind"]:
        body = record.log_line(body, "watch", f"pairing {p['n']}: these tests were written or changed in the pairing "
                                              f"and are not blind: {', '.join(p['not_blind'])}. The guardian checks them "
                                              "in a fresh context")
    if p["unprefixed"]:
        body = record.log_line(body, "watch", f"pairing {p['n']}: commits without \"{p['prefix']}\": "
                                              + ", ".join(f[:10] + f[40:] for f in p["unprefixed"]))
    if why_not:
        body = record.log_line(body, "watch", f"pairing {p['n']}: the pair session's spend could not be read "
                                              f"({why_not}); it is not in the slice's actual")
    committed = [rel]
    if data.get("packet") and os.path.isfile(os.path.join(root, data["packet"])):
        packetlib.note_pairings(os.path.join(root, data["packet"]), data)
        committed.append(data["packet"])
    # left uncommitted: end_head is the head the pairing ended at, and a commit of the record would move it
    record.save(path, data, body)
    state = spendlib.budget_state(data)
    out = {"slice": a.id, "pairing": p["n"], "next": a.next, "commits": p["commits"], "not_blind": p["not_blind"],
           "spend": row, "spend_note": why_not, "budget": state}
    if state["spent_out"]:
        out["note"] = (f"the budget is spent ({', '.join(state['over'])}); the next step stops for "
                       f"{data.get('set_by')} before it runs")
    emit(out, True)


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv pairing", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="open a pairing at an open stop or a send-back")
    s.add_argument("id")
    s.add_argument("--by", required=True, help="the person who set the work going")
    s.add_argument("--why", required=True)
    s.add_argument("--session", help="the pair session: a transcript path or a session id "
                                     "as <reader>:<id or file> (default: none; the spend cannot be read)")
    s.add_argument("--agent", help="the pair's name in each commit's prefix (default: from the session's harness)")
    s.set_defaults(fn=cmd_start)
    s = sub.add_parser("end", help="close the pairing and say where the slice resumes")
    s.add_argument("id")
    s.add_argument("--next", required=True, help="maker, cleaner, guardian, or scenario after an amendment")
    s.set_defaults(fn=cmd_end)
    a = p.parse_args(argv)
    try:
        a.fn(a)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

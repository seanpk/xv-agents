#!/usr/bin/env python3
"""The watch's standing orders. Each order reads the slice record and says
whether a person must be woken, and which seat.

These are the stops in XV's delivery loop. They are code so that a check can
fail and CI can run it. The watch does not interpret them and never edits them:
a change here is a change to what the watch is, and it takes two people and a
line in CHANGELOG.md.

Usage: xv orders <slice id> [--after <step>]
Exit 0: no stop. Exit 10: a stop fired (JSON on stdout says which, for whom).
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spend import budget_state  # noqa: E402
from xvlib import XVError, die, emit, load_config, read_doc, record_path, repo_root, slice_root  # noqa: E402

SEAT_RANK = {"chief_engineer": 0, "originator": 1, "two_people": 2}
BREADTH = {"none": 0, "narrow": 1, "wide": 2}


def fire(order, seat, question, blocking=True):
    return {"order": order, "seat": seat, "question": question, "blocking": blocking}


def first_failing_step(output):
    """The first FAIL: or ERROR: line of a suite's output, else its last line."""
    lines = [line.strip() for line in (output or "").splitlines() if line.strip()]
    return next((line for line in lines if line.startswith(("FAIL:", "ERROR:"))), lines[-1] if lines else "")


def failing_step(checks):
    """The first failing step in the suite output, as a sentence to append to a question."""
    step = checks.get("failing_step") or first_failing_step(checks.get("suite_output"))
    return f" Failing: {step}" if step else ""


def last_report(data, step):
    for r in reversed((data.get("checks") or {}).get("reports", [])):
        if r.get("agent") == step:
            return r
    return None


def evaluate(data, after, config):
    """All orders that fire after `after`. Pure: reads the record and the config."""
    out = []
    checks = (data.get("checks") or {}).get(after) or {}
    report = last_report(data, after)
    owner = data.get("set_by") or "the person who set the work going"

    if after in ("forecaster", "scenario", "maker", "cleaner", "guardian") and \
            (report is None or report.get("status") == "no-report"):
        out.append(fire("no_report", "originator",
                        f"The {after} ended without a report. Read its log and decide whether to re-run it."))
    elif report and report.get("status") == "stopped":
        stop = report.get("stop") or {}
        reason = stop.get("reason") or report.get("status")
        seat = "two_people" if reason == "shape" else "originator"
        if reason in ("repeated_failure", "growing_diff"):
            q = (f"The {after} stopped: {reason.replace('_', ' ')}. The shape conversation opens; "
                 "the agent may not renovate.")
        else:
            q = f"The {after} stopped ({reason}): {stop.get('question') or report.get('summary', '')}"
        out.append(fire(f"{after}_stopped", seat, q))

    if after in ("forecaster", "guardian") and checks.get("wrote"):
        out.append(fire("read_only_broken", "originator",
                        f"The {after} is read-only and changed: {', '.join(checks['wrote'])}. "
                        "Revert it before going on."))

    if after == "forecaster" and not data.get("budget"):
        out.append(fire("budget_not_set", "originator",
                        f"{owner}: set the budget from the forecast (`xv record set {data['id']} budget ... --by <name>`)."))

    if after == "scenario":
        if checks.get("outside_tests"):
            out.append(fire("scenario_touched_source", "originator",
                            "The scenario agent changed files outside the test paths: "
                            + ", ".join(checks["outside_tests"])))
        if checks.get("red_fails") is False:
            out.append(fire("scenario_not_red", "originator",
                            "The scenario passes on the code as it is. The behaviour may exist already, "
                            "or the scenario may be wrong."))

    wall = checks.get("wall") or {}
    if wall.get("unrecorded"):
        out.append(fire("unrecorded_move", "originator",
                        f"Test files changed with no record after the {after}: "
                        + ", ".join(wall["unrecorded"]) + ". Revert them, or record why the scenario forces it."))

    if checks.get("protected_changed"):
        out.append(fire("protected_changed", "originator",
                        f"The {after} changed files only people change: {', '.join(checks['protected_changed'])}. "
                        "Revert them before going on."))

    if after == "maker" and checks.get("reused_prototype_context"):
        out.append(fire("prototype_context_reused", "originator",
                        "The maker ran in a context that built a prototype. The pick is built by a fresh context."))

    if after == "maker":
        state = budget_state(data)
        if state["spent_out"] and checks.get("suite") != "green":
            out.append(fire("budget_spent", "originator",
                            f"The budget is spent ({', '.join(state['over'])}) and the suite is not green."
                            f"{failing_step(checks)} "
                            "Continue with a new budget, reshape, or set it aside."))
        fails = checks.get("failing_history") or []
        if len(fails) >= 2 and fails[-1] and fails[-1] == fails[-2]:
            out.append(fire("repeated_failure", "originator",
                            f"The same tests failed after two runs of the maker: {', '.join(fails[-1][:5])}. "
                            "The shape conversation opens; the agent may not renovate."))
        hist = checks.get("diff_history") or []
        if len(hist) >= 2 and hist[-2] and hist[-1] > 2 * hist[-2]:
            out.append(fire("diff_growing", "originator",
                            f"The diff grew from {hist[-2]} to {hist[-1]} lines between two runs of the maker. "
                            "The shape conversation opens; the agent may not renovate."))
        limit = (config.get("limits") or {}).get("max_diff_lines") or 0
        if limit and (checks.get("diff_lines") or 0) > limit:
            out.append(fire("diff_growing", "originator",
                            f"The diff is {checks['diff_lines']} lines, past the team's {limit}. "
                            "The shape conversation opens."))

    budget = data.get("budget") or {}
    pct = (config.get("limits") or {}).get("budget_raise_pct") or 0
    raised = budget.get("raised_from") or {}
    answered = any(s.get("order") == "budget_past_limit" and s.get("answer") for s in data.get("stops") or [])
    if pct and raised and not answered and after in ("forecaster", "maker"):
        for k, old in raised.items():
            if old and budget.get(k) and (budget[k] - old) / old * 100 > pct:
                out.append(fire("budget_past_limit", "two_people",
                                f"The budget's {k} was raised from {old} to {budget[k]}, past the team's "
                                f"{pct}% limit. Two people decide."))
                break

    if after == "cleaner":
        if checks.get("suite") not in (None, "green"):
            out.append(fire("cleaner_broke_suite", "originator", "The suite is not green after the cleaner's pass." + failing_step(checks)))
        if checks.get("standards_touched"):
            out.append(fire("cleaner_touched_standards", "originator",
                            "The cleaner edited .xv/standards.md. A standard enters only when a person accepts it."))

    if after == "guardian":
        if data.get("shape_change") == "yes" or data.get("pitch_contradiction") == "yes":
            what = [n for n in ("shape_change", "pitch_contradiction") if data.get(n) == "yes"]
            out.append(fire("shape_or_pitch", "two_people",
                            f"The guardian's packet says {' and '.join(what)}. Two people decide from the packet."))
        fc = (data.get("forecast") or {}).get("shape")
        actual = (data.get("checks") or {}).get("guardian", {}).get("shape_breadth")
        if fc in BREADTH and actual in BREADTH and BREADTH[actual] > BREADTH[fc]:
            out.append(fire("shape_wider_than_forecast", "two_people",
                            f"The shape change is {actual}; the forecast expected {fc}. Two people decide."))
        moved = data.get("moved_tests") or []
        picture = checks.get("picture_change") == "yes"
        if not out and (moved or picture):
            parts = []
            if moved:
                parts.append(f"{len(moved)} old test(s) moved with a record")
            if picture:
                parts.append("the picture changed")
            out.append(fire("accept_moves", "originator",
                            f"{' and '.join(parts).capitalize()}; the shape did not. Accept them from the packet, "
                            "talk it through with someone, or send it back. The merge is yours."))
        if not out:
            out.append(fire("ready_to_merge", "originator",
                            "The suite is green and nothing stopped. The merge is yours."))
        watch = (data.get("red") or {}).get("watch_first_green")
        if data.get("kind") == "feature" and watch:
            for f in out:
                if f["order"] in ("ready_to_merge", "accept_moves"):
                    f["question"] += (f" Before you merge, watch the first green run: {watch} If you see a case "
                                      "nobody wrote down, add it to the scenario and send the slice back to the "
                                      "scenario agent (--next scenario).")

    if after == "prototype" and checks.get("prototypes_ready") is not None:
        n = checks["prototypes_ready"]
        out.append(fire("prototypes_ready", "two_people",
                        f"{n} prototype(s) are ready to pick from, or none. Two people pick, with a user "
                        "when one can be reached."))

    return out


def verdict(data, after, config):
    fired = evaluate(data, after, config)
    from xvlib import solo
    if solo(config):
        for f in fired:
            if f["seat"] == "two_people":
                f["question"] += (" This repo runs solo: one person answers. Write down what you weighed; "
                                  "the decision record keeps it.")
    blocking = [f for f in fired if f["blocking"]]
    stop = max(blocking, key=lambda f: SEAT_RANK[f["seat"]]) if blocking else None
    return {"slice": data.get("id"), "after": after, "stop": stop, "fired": fired}


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv orders", description=__doc__.split("\n")[0])
    p.add_argument("id")
    p.add_argument("--after", required=True)
    a = p.parse_args(argv)
    try:
        path = record_path(repo_root(), a.id)
        data, _ = read_doc(path)
        v = verdict(data, a.after, load_config(slice_root(path)))
    except XVError as e:
        die(str(e), 2)
    emit(v, True)
    sys.exit(10 if v["stop"] else 0)


if __name__ == "__main__":
    main()

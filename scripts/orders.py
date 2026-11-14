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
STALL_CHOICES = ("This is a stall on this slice, and the agent may not renovate. Choose: continue, "
                 "reshape the slice, raise the budget, or bring in a second person.")


def fire(order, seat, question, blocking=True, sendback=None):
    f = {"order": order, "seat": seat, "question": question, "blocking": blocking}
    if sendback:
        f["sendback"] = sendback
    return f


def sendback_keys(data, order, after):
    """Keys of what the watch sent back for this order before the report now being read: the outcomes, or the miss refs."""
    report = last_report(data, after) or {}
    here = report_index(data, after)

    def earlier(st):
        if st.get("report_n") is not None and here is not None:
            # the same report and the same packet is the same pass; a new packet for one report is a new pass
            return st["report_n"] < here or st.get("packet") != data.get("packet")
        return not (report.get("at") and st.get("at") and st["at"] >= report["at"])

    return {k for st in data.get("stops") or [] if st.get("order") == order and st.get("seat") == "watch"
            and earlier(st) for k in st.get("keys") or []}


def miss_run(data, order, after):
    """For each key, how many send-backs of this order in a row end at the report now being read.
    A pass that did not miss the key, an amendment, or a person's answer ends the run."""
    here = report_index(data, after)
    stops = data.get("stops") or []
    # a person's answer is the last stop they answered, by its place in the list
    answered = max([i for i, s in enumerate(stops) if s.get("answered_by") and s.get("answered_by") != ["watch"]],
                   default=-1)
    amended = data.get("reports_before_amend") or 0
    mine = [st for i, st in enumerate(stops) if st.get("order") == order and st.get("seat") == "watch"
            and (st.get("report_n") is None or (st["report_n"] >= amended and (here is None or st["report_n"] < here)))
            and i > answered]
    out = {}
    for key in {k for st in mine for k in st.get("keys") or []}:
        n, expected = 0, None if here is None else here - 1
        for st in reversed(mine):
            at = st.get("report_n")
            if key not in (st.get("keys") or []) or (expected is not None and at is not None and at != expected):
                break
            n += 1
            if at is not None:
                expected = at - 1
        out[key] = n
    return out


def report_index(data, step):
    """Where the last report of `step` sits among the record's reports, or None."""
    reports = (data.get("checks") or {}).get("reports", [])
    return next((i for i in range(len(reports) - 1, -1, -1) if reports[i].get("agent") == step), None)


def first_failing_step(output):
    """The first FAIL: or ERROR: line of a suite's output, else its last line."""
    lines = [line.strip() for line in (output or "").splitlines() if line.strip()]
    return next((line for line in lines if line.startswith(("FAIL:", "ERROR:"))), lines[-1] if lines else "")


def failing_clause(checks):
    """The first failing step in the suite output, as a sentence to append to a question."""
    step = checks.get("failing_step") or first_failing_step(checks.get("suite_output"))
    return f" Failing: {step}" if step else ""


def last_report(data, step):
    for r in reversed((data.get("checks") or {}).get("reports", [])):
        if r.get("agent") == step:
            return r
    return None


def budget_before(data):
    """The stop that keeps a step from running when the slice's whole spend has reached the budget."""
    state = budget_state(data)
    if not state["spent_out"]:
        return None
    budget, spent = state["budget"], state["spent"]
    what = ", ".join(f"{k} {spent[k]} of {budget[k]}" for k in state["over"])
    return fire("budget_spent", "originator",
                f"The budget is spent ({what}), so the next step does not run. "
                "Continue with a new budget, reshape, or set it aside.")


def unfinished(data):
    """Each prototype variant that did not finish, with its error, for the stop after `xv prototype start`."""
    failed = [p for p in data.get("prototypes") or [] if p.get("error")]
    if not failed:
        return ""
    start = f"`xv prototype start {data['id']}`"
    return "".join(f" Variant {p['name']} did not finish: {str(p['error']).strip().rstrip('.')}." for p in failed) + \
        (f" It cannot be picked; a second {start} runs it again." if len(failed) == 1 else
         f" They cannot be picked; a second {start} runs them again.")


def evaluate(data, after, config):
    """All orders that fire after `after`. Pure: reads the record and the config."""
    out = []
    checks = (data.get("checks") or {}).get(after) or {}
    report = last_report(data, after)
    owner = data.get("originator") or "the person who set the work going"

    if after in ("forecaster", "scenario", "maker", "cleaner", "guardian") and \
            (report is None or report.get("status") == "no-report"):
        out.append(fire("no_report", "originator",
                        f"The {after} ended without a report. Read its log and decide whether to re-run it."))
    elif report and report.get("status") == "stopped":
        stop = report.get("stop") or {}
        reason = stop.get("reason") or report.get("status")
        seat = "two_people" if reason == "shape" else "originator"
        if reason in ("repeated_failure", "growing_diff"):
            q = f"The {after} stopped: {reason.replace('_', ' ')}. {STALL_CHOICES}"
        else:
            q = f"The {after} stopped ({reason}): {stop.get('question') or report.get('summary', '')}"
        out.append(fire(f"{after}_stopped", seat, q))

    if after in ("forecaster", "guardian") and checks.get("wrote"):
        out.append(fire("read_only_changed", "originator",
                        f"The {after} is read-only and changed: {', '.join(checks['wrote'])}. "
                        "Revert it before going on."))

    if after == "forecaster" and not data.get("budget"):
        out.append(fire("budget_not_set", "originator",
                        f"{owner}: set the budget from the forecast (`xv record set {data['id']} budget ... --by <name>`)."))

    if after == "scenario" and data.get("kind") == "refactor" and checks.get("suite", "green") != "green":
        out.append(fire("suite_not_green_at_start", "originator",
                        "A refactor slice needs a green suite at the start: it is the oracle, and the scenario step "
                        "writes no red. The suite is not green." + failing_clause(checks)
                        + " Fix it on its own slice, or set this one aside."))

    if after == "scenario":
        if checks.get("outside_tests"):
            out.append(fire("scenario_touched_source", "originator",
                            "The scenario agent changed files outside the test paths: "
                            + ", ".join(checks["outside_tests"])))
        if checks.get("red_joined_unsafely"):
            out.append(fire("red_command_joined", "originator",
                            f"The red command `{checks['red_joined_unsafely']}` joins its runners with something other than `&&`, "
                            "so only the last one's exit code counts. The scenario agent will rewrite it, joining the runners with `&&`."))
        if checks.get("red_cannot_run"):
            out.append(fire("red_cannot_run", "originator",
                            "The red command cannot run: it failed before any test ran (" + checks["red_cannot_run"]
                            + "). That is not a failing red, so the record holds no evidence the red fails for the "
                            "reasons the scenario names. Fix the command or the test files so the tests run, "
                            "then run the scenario step again."))
        if checks.get("cherry_pick_conflict"):
            out.append(fire("red_conflicts_with_build", "originator",
                            "The scenario agent wrote its red at the base, and it does not apply to the build the slice "
                            "starts from: " + checks["cherry_pick_conflict"]
                            + f" The red is kept on `refs/xv/{data.get('id')}/red` at the base, and a later scenario "
                            "pass starts from it whatever you land by hand, so a hand-landed red under another "
                            "commit subject is not lost. Resolve it by hand, or change the red so it fits the build."))
        if checks.get("old_red_changed"):
            out.append(fire("unrecorded_move", "originator",
                            "The scenario agent changed or removed old tests or assertions in old test files that existed at the base: "
                            + ", ".join(checks["old_red_changed"]) + ". Revert them, or record why the scenario forces it."))
        if checks.get("old_red_unchecked"):
            out.append(fire("setup_failed", "originator", checks["old_red_unchecked"]))
        if checks.get("setup_failed"):
            out.append(fire("setup_failed", "originator", checks["setup_failed"]))
        for msg in checks.get("unreadable") or []:
            out.append(fire("red_misses_scenario", "originator", msg))
        if checks.get("red_gaps"):
            out.append(fire("red_misses_scenario", "originator",
                            "The scenario names these in backticks, and no red file has them: "
                            + ", ".join(f"`{g}`" for g in checks["red_gaps"])
                            + ". Add a test that reaches each, or amend the scenario."))
        for n in checks.get("not_covered") or []:
            out.append(fire("red_misses_scenario", "originator",
                            f"The scenario agent did not cover {n.get('outcome')}: {n.get('why')}"))
        outcomes = [str(p) for p in checks.get("missed_outcomes") or []]
        run = miss_run(data, "report_misses_outcome", after)
        if any(run.get(p, 0) >= 2 for p in outcomes):
            out.append(fire("report_misses_outcome", "originator",
                            "The same scenario outcomes are still in neither covered nor not_covered after two send-backs: "
                            + "; ".join(outcomes) + ". " + STALL_CHOICES))
        if checks.get("red_fails") is False:
            out.append(fire("scenario_not_red", "originator",
                            "The scenario passes on the code as it is. The behaviour may exist already, "
                            "or the scenario may be wrong."))
        marks = [m for m in data.get("slice_only") or [] if isinstance(m, dict) and not m.get("accepted")]
        if marks:
            listed = "; ".join(f"{m.get('test')} in {m.get('file')} ({m.get('why')})" for m in marks)
            out.append(fire("slice_only_marks", "originator",
                            f"{owner}: the scenario agent marked {len(marks)} test(s) slice-only, so the cleaner may "
                            f"remove them and they do not join the wall: {listed}. Accept the marks, or unmark a "
                            "test so it joins the wall and the cleaner keeps it."))

    if after == "rebase":
        resume = f"`xv slice rebase {data.get('id')} --continue`"
        undo = f"or `xv slice rebase {data.get('id')} --abort` to give it up"
        if checks.get("maker_edited"):
            drop, note = drop_edit(checks)
            out.append(fire("rebase_conflict", "originator",
                            f"{owner}: the maker changed {', '.join(checks['maker_edited'])} during the rebase, "
                            "and a test file or the picture is a person's. The edit is uncommitted in the slice "
                            f"worktree: run {resume} to keep it, {drop} to drop it, {undo}.{note}"))
        elif checks.get("conflicts"):
            out.append(fire("rebase_conflict", "originator",
                            f"{owner}: the rebase stopped on a conflict in {', '.join(checks['conflicts'])}. "
                            f"Resolve it in the slice worktree and run {resume}, {undo}."))
        if checks.get("dropped"):
            out.append(fire("rebase_dropped", "originator",
                            f"{owner}: the rebase dropped a commit the record names: {', '.join(checks['dropped'])}. "
                            f"Run {resume} to clear it from the record, {undo}."))
        if checks.get("red_ref"):
            out.append(fire("rebase_red_ref", "originator",
                            f"{owner}: the rebase could not move the red ref onto the new base: {checks['red_ref']}. "
                            f"It stays on the old base. Run {resume} to go on without moving it, {undo}."))
        if checks.get("stuck"):
            out.append(fire("rebase_stuck", "originator",
                            f"{owner}: the maker could not fix a problem the new base brings: {checks['stuck']} "
                            f"Fix it in the slice worktree and run {resume}, {undo}."))
        if checks.get("suite") == "red":
            out.append(fire("rebase_suite_red", "originator",
                            f"The suite is red after the rebase.{failing_clause(checks)} "
                            f"Fix it in the slice worktree and run {resume}, {undo}."))

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
                            f"{failing_clause(checks)} "
                            "Continue with a new budget, reshape, or set it aside."))
        fails = checks.get("failing_history") or []
        if len(fails) >= 2 and fails[-1] and fails[-1] == fails[-2]:
            out.append(fire("repeated_failure", "originator",
                            f"The same tests failed after two runs of the maker: {', '.join(fails[-1][:5])}. "
                            + STALL_CHOICES))
        hist = checks.get("diff_history") or []
        if len(hist) >= 2 and hist[-2] and hist[-1] > 2 * hist[-2]:
            out.append(fire("diff_growing", "originator",
                            f"The diff grew from {hist[-2]} to {hist[-1]} lines between two runs of the maker. "
                            + STALL_CHOICES))
        limit = (config.get("limits") or {}).get("max_diff_lines") or 0
        if limit and (checks.get("diff_lines") or 0) > limit:
            out.append(fire("diff_growing", "originator",
                            f"The diff is {checks['diff_lines']} lines, past the team's {limit}. "
                            + STALL_CHOICES))

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
            out.append(fire("cleaner_broke_suite", "originator",
                            "The suite is not green after the cleaner's pass." + failing_clause(checks)))
        if checks.get("standards_touched"):
            out.append(fire("cleaner_touched_standards", "originator",
                            "The cleaner edited .xv/standards.md. A standard enters only when a person accepts it."))

    if after == "guardian":
        wrong = [p for p in checks.get("packet_problems") or [] if "expected_moves" in p]
        if wrong:
            out.append(fire("expected_moves_wrong", "originator",
                            "The packet's expected_moves does not match the record: " + "; ".join(wrong) + "."))
        if data.get("shape_change") == "yes" or data.get("pitch_contradiction") == "yes":
            what = [n for n in ("shape_change", "pitch_contradiction") if data.get(n) == "yes"]
            out.append(fire("shape_or_pitch", "two_people",
                            f"The guardian's packet says {' and '.join(what)}. Two people decide from the packet."))
        fc = (data.get("forecast") or {}).get("shape_breadth")
        actual = (data.get("checks") or {}).get("guardian", {}).get("shape_breadth")
        # a shape stays accepted at the breadth it was accepted at; a stop from before the breadth was kept covers any
        accepted_shape = data.get("shape_change") == "accepted" or any(
            s.get("order") == "shape_wider_than_forecast" and s.get("answer") and not s.get("sendback")
            and BREADTH.get(s.get("breadth"), BREADTH["wide"]) >= BREADTH.get(actual, 0)
            for s in data.get("stops") or [])
        if not accepted_shape and fc in BREADTH and actual in BREADTH and BREADTH[actual] > BREADTH[fc]:
            out.append(dict(fire("shape_wider_than_forecast", "two_people",
                                 f"The shape change is {actual}; the forecast expected {fc}. Two people decide."),
                            breadth=actual))
        moved = {(m.get("file"), m.get("assertion")) for m in data.get("moved_tests") or []
                 if not m.get("slice_only") and not m.get("expected")}
        picture = checks.get("picture_change") == "yes"
        recs = [r for r in data.get("wall_recommendations") or [] if not r.get("accepted") and not r.get("refused")]
        miss = data.get("change_misses_scenario") == "yes"
        if miss:
            state = budget_state(data)
            if state["spent_out"]:
                out.append(fire("budget_spent", "originator",
                                f"The budget is spent ({', '.join(state['over'])}) and the packet says change_misses_scenario: yes. "
                                "Continue with a new budget, reshape, or set it aside."))
            found = checks.get("misses") or []
            repeat = sorted({m["ref"] for m in found} & sendback_keys(data, "change_misses_scenario", after))
            if checks.get("miss_amend") or any(m.get("amend") for m in found):
                out.append(fire("change_misses_scenario", "originator",
                                "The packet lists a scenario miss marked amend: yes: meeting it would change the scenario, "
                                "which goes through `xv slice amend` and is yours."))
            elif repeat:
                out.append(fire("change_misses_scenario", "originator",
                                "The same scenario miss came back after a send-back: "
                                + "; ".join(repeat) + ". " + STALL_CHOICES))
        if not out and not miss and (moved or picture or recs):
            parts = []
            if moved:
                parts.append(f"{len(moved)} old test(s) moved with a record")
            if recs:
                parts.append(f"{len(recs)} wall recommendation(s) from the guardian")
            if picture:
                parts.append("the guardian proposes a change to the picture")
            out.append(fire("moves_to_accept", "originator",
                            f"{' and '.join(parts).capitalize()}; the shape did not. Accept them from the packet, "
                            "talk it through with someone, or send it back. The merge is yours."))
        if not out and not miss:
            out.append(fire("ready_to_merge", "originator",
                            "The suite is green and nothing stopped. The merge is yours."))
        watch = (data.get("red") or {}).get("watch_before_merge")
        if data.get("kind") == "feature" and watch:
            for f in out:
                if f["order"] in ("ready_to_merge", "moves_to_accept"):
                    f["question"] += (f" Before you merge, watch the first green run: {watch} If you see a case "
                                      "nobody wrote down, add it to the scenario and send the slice back to the "
                                      "scenario agent (--next scenario).")

    if after == "prototype" and data.get("kind") == "prototype" and \
            not all((data.get("prototype_budgets") or {}).get(n) for n in "abc"):
        out.append(fire("prototype_budgets_not_set", "originator",
                        f"{owner}: set a budget for each variant, free to differ "
                        f"(`xv record set {data['id']} prototype_budgets '{{\"a\": {{\"usd\": 1}}, ...}}' --by <name>`)."))

    ran_out = checks.get("ran_out") or {}
    if after == "prototype" and ran_out:
        during = checks.get("ran_during") or []
        what = "; ".join(f"variant {n} spent {spent} and " +
                         ("ran out of its budget during its run" if n in during else "was not run")
                         for n, spent in sorted(ran_out.items()))
        pickable = checks.get("prototypes_ready") or 0
        pick = (f"pick one of the {pickable} that finished, or pick none to end the exploration"
                if pickable else "pick none to end the exploration, the only pick left")
        out.append(fire("prototype_budget_spent", "originator",
                        f"{owner}: {what}. Raise a budget (`xv record set {data['id']} prototype_budgets ... --by <name>`), "
                        f"answer this stop, and then run `xv prototype start {data['id']}` again, which runs only the "
                        f"variants that have not finished and keeps the rest; or {pick}. The person who set the work "
                        "going answers a budget raise alone; a pick, including none, is for two people unless the "
                        "repo runs solo. A variant that ran out cannot be picked." + unfinished(data)))

    if after == "prototype" and checks.get("prototypes_ready") is not None and not ran_out:
        n = checks["prototypes_ready"]
        out.append(fire("prototypes_ready", "two_people",
                        f"{n} prototype(s) are ready to pick from, or none. Two people pick, with a user "
                        "when one can be reached. The pick is thrown away, or kept as the build this slice starts "
                        f"from (`xv prototype pick {data['id']} --variant <v> --keep ...`); the people choose."
                        + unfinished(data)))

    if not any(f["blocking"] for f in out):
        if after == "scenario" and checks.get("missed_outcomes"):
            outcomes = sorted({str(p) for p in checks["missed_outcomes"]})
            out.append(fire("report_misses_outcome", "watch",
                            "These outcomes are in neither covered nor not_covered; put each in `covered` or `not_covered` "
                            "as the outcome shown: " + "; ".join(outcomes) + ". Every outcome of the scenario and its "
                            "amendments goes in `covered` or `not_covered` on each pass, not only the outcomes of the "
                            "newest amendment.",
                            blocking=False, sendback={"to": "scenario", "misses": outcomes}))
        elif after == "guardian" and data.get("change_misses_scenario") == "yes" and checks.get("misses"):
            found = checks["misses"]
            out.append(fire("change_misses_scenario", "watch", "; ".join(m["text"] for m in found), blocking=False,
                            sendback={"to": "scenario" if any(m["to"] == "scenario" for m in found) else "maker",
                                       "misses": sorted({m["ref"] for m in found})}))

    return out


def next_step(data, after, stop, fired):
    """Where `next` goes after this step, or None when it stays where the step left it."""
    if stop:
        if ((data.get("checks") or {}).get(after) or {}).get("red_joined_unsafely"):
            return "scenario"
        return None if stop["order"] == "ready_to_merge" else after
    back = [f for f in fired if f.get("sendback")]
    if back:
        return back[-1]["sendback"]["to"]
    checks = (data.get("checks") or {}).get(after) or {}
    if after == "scenario" and checks.get("red_fails") is True and (checks.get("red_on_build") or {}).get("passes"):
        return "cleaner"  # the build already passes the red: nothing for the maker to make
    return None


def drop_edit(checks):
    """How to drop the maker's edit, and a note when it is a new file: `git checkout` restores a file that was
    already tracked; a file the maker added is not known to it, and `git diff` does not list it."""
    new = checks.get("maker_new") or {}
    old = [f for f in checks.get("maker_edited") or [] if f not in new]
    cmds = ([f"git checkout -- {' '.join(old)}"] if old else []) + list(new.values())
    note = " `git checkout -- <file>` restores a tracked file." if old else ""
    if new:
        note += f" {', '.join(new)} is a new file the maker added: `git status` shows it, `git diff` does not."
    return " and ".join(f"`{c}`" for c in cmds) or "`git checkout -- <file>`", note


def verdict(data, after, config, closed=()):
    """What fired after a step. `closed` names orders a person's answer just settled: they do not fire again."""
    fired = [f for f in evaluate(data, after, config) if f["order"] not in closed]
    from xvlib import solo
    if solo(config):
        for f in fired:
            if f["seat"] == "two_people":
                f["question"] += (" This repo runs solo: one person answers. Write down what you weighed; "
                                  "the decision record keeps it.")
    blocking = [f for f in fired if f["blocking"]]
    stop = max(blocking, key=lambda f: SEAT_RANK[f["seat"]]) if blocking else None
    return {"slice": data.get("id"), "after": after, "stop": stop, "fired": fired,
            "next": next_step(data, after, stop, fired)}


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

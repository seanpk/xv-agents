#!/usr/bin/env python3
"""Actual spend from a harness's own output or logs, and the budget check.

Readers:
  claude-result   the JSON `claude -p --output-format json` prints
  grok-result     the JSON `grok -p --output-format json` prints
  claude-session  a Claude Code session transcript (.jsonl), with its subagents
  opencode        an opencode session, via `opencode session export <id>`

Each reader returns one spend item: harness, model (as the config names it),
model_id (as the harness reports it), tokens_in, tokens_out, cache_read,
cache_write, tokens (input + output + cache write, no cache reads), usd (null
where the harness does not report dollars), turns, wall_s.

Usage:
  xv spend read <reader> <file-or-session-id> [--model NAME]
  xv spend budget <slice id>     exit 3 when the budget is spent
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XVError, die, emit, read_doc, record_path, repo_root, run  # noqa: E402


def item(harness, model, model_id=None, tokens_in=0, tokens_out=0, cache_read=0, cache_write=0,
         usd=None, turns=None, wall_s=None, session=None):
    tokens_in, tokens_out = int(tokens_in or 0), int(tokens_out or 0)
    cache_read, cache_write = int(cache_read or 0), int(cache_write or 0)
    return {"harness": harness, "model": model, "model_id": model_id or model,
            "tokens_in": tokens_in, "tokens_out": tokens_out,
            "cache_read": cache_read, "cache_write": cache_write,
            "tokens": tokens_in + tokens_out + cache_write,
            "usd": None if usd is None else round(float(usd), 4),
            "turns": turns, "wall_s": wall_s, "session": session}


def from_claude_result(text, model=None):
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        raise XVError("not the JSON of `claude -p --output-format json`")
    usage = d.get("usage") or {}
    mu = d.get("modelUsage") or {}
    model_id = max(mu, key=lambda k: mu[k].get("costUSD", 0)) if mu else None
    if mu:
        # modelUsage covers every model the run used, subagents included
        tin = sum(v.get("inputTokens", 0) for v in mu.values())
        tout = sum(v.get("outputTokens", 0) for v in mu.values())
        cr = sum(v.get("cacheReadInputTokens", 0) for v in mu.values())
        cw = sum(v.get("cacheCreationInputTokens", 0) for v in mu.values())
    else:
        tin, tout = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        cr = usage.get("cache_read_input_tokens", 0)
        cw = usage.get("cache_creation_input_tokens", 0)
    return item("claude", model or model_id or "default", model_id, tin, tout, cr, cw,
                d.get("total_cost_usd"), d.get("num_turns"),
                round((d.get("duration_ms") or 0) / 1000, 1), d.get("session_id"))


def from_grok_result(text, model=None):
    """The JSON `grok -p ... --output-format json` prints. Its input_tokens are
    uncached only, and its output_tokens include reasoning, so the four counts
    add up to its own total_tokens. The item's tokens leave out cache reads, as
    every reader's do. Dollars only when Grok reports a complete cost."""
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        raise XVError("not the JSON of `grok -p --output-format json`")
    u = d.get("usage") or {}
    mu = d.get("modelUsage") or {}
    model_id = max(mu, key=lambda k: mu[k].get("outputTokens", 0)) if mu else None
    usd = None if d.get("cost_is_partial") or d.get("usage_is_incomplete") else d.get("total_cost_usd")
    return item("grok", model or model_id or "default", model_id, u.get("input_tokens", 0),
                u.get("output_tokens", 0), u.get("cache_read_input_tokens", 0),
                u.get("cache_creation_input_tokens", 0), usd, d.get("num_turns"), None, d.get("sessionId"))


def from_claude_session(path, model=None):
    """Sum a session transcript and any subagent transcripts beside it."""
    files = [path]
    sub = os.path.join(os.path.splitext(path)[0], "subagents")
    files += sorted(glob.glob(os.path.join(sub, "*.jsonl")))
    seen, totals, turns, models = set(), [0, 0, 0, 0], 0, {}
    first = last = None
    for f in files:
        with open(f) as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = ev.get("timestamp")
                if ts:
                    first, last = first or ts, ts
                msg = ev.get("message") or {}
                if ev.get("type") != "assistant" or not msg.get("usage"):
                    continue
                mid = msg.get("id") or ev.get("uuid")
                if mid in seen:  # one API message is logged once per content block
                    continue
                seen.add(mid)
                u = msg["usage"]
                totals[0] += u.get("input_tokens", 0)
                totals[1] += u.get("output_tokens", 0)
                totals[2] += u.get("cache_read_input_tokens", 0)
                totals[3] += u.get("cache_creation_input_tokens", 0)
                models[msg.get("model", "?")] = models.get(msg.get("model", "?"), 0) + 1
                turns += 1
    wall = None
    if first and last:
        from datetime import datetime
        wall = (datetime.fromisoformat(last.replace("Z", "+00:00")) -
                datetime.fromisoformat(first.replace("Z", "+00:00"))).total_seconds()
    model_id = max(models, key=models.get) if models else None
    # A transcript carries tokens, not dollars. usd stays null rather than a guess.
    return item("claude", model or model_id or "default", model_id, *totals, None, turns,
                wall, os.path.splitext(os.path.basename(path))[0])


def from_opencode(session_id, model=None, exported=None):
    if exported is None:
        p = run(["opencode", "session", "export", session_id], check=False)
        if p.returncode != 0:
            raise XVError(f"opencode session export {session_id} failed: {p.stderr.strip()[:200]}")
        exported = p.stdout
    d = json.loads(exported)
    info = d.get("info") or {}
    t = info.get("tokens") or {}
    cache = t.get("cache") or {}
    m = (info.get("model") or {}).get("id")
    turns = sum(1 for x in d.get("messages", []) if x.get("type") == "assistant")
    tm = info.get("time") or {}
    wall = ((tm.get("updated") or 0) - (tm.get("created") or 0)) / 1000 or None
    cost = info.get("cost")
    # opencode reports 0 for a local model; that is a real zero, not a missing value
    return item("opencode", model or m or "default", m,
                t.get("input", 0), t.get("output", 0) + t.get("reasoning", 0),
                cache.get("read", 0), cache.get("write", 0), cost, turns, wall, info.get("id"))


def from_run(result):
    """Spend for one agentcli.run result, using whichever reader fits the harness."""
    h = result.get("harness")
    try:
        if h == "claude":
            s = from_claude_result(result["stdout"], result.get("model"))
        elif h == "grok":
            s = from_grok_result(result["stdout"], result.get("model"))
        elif h == "opencode" and result.get("session"):
            s = from_opencode(result["session"], result.get("model"))
        else:
            s = item(h, result.get("model"))
    except (XVError, json.JSONDecodeError, KeyError):
        s = item(h, result.get("model"))
    s["wall_s"] = result.get("wall_s")  # the watch's clock, the same for every harness
    return s


# ---------------------------------------------------------------- budget

def row_tokens(s):
    """A row's tokens: input + output + cache write when it keeps the raw counts, else its stored total."""
    if "cache_read" in s:
        return sum(int(s.get(k) or 0) for k in ("tokens_in", "tokens_out", "cache_write"))
    return int(s.get("tokens") or 0)


def totals(spend):
    t = {"tokens": 0, "usd": 0.0, "turns": 0, "wall_s": 0.0, "usd_known": True}
    for s in spend:
        t["tokens"] += row_tokens(s)
        t["turns"] += int(s.get("turns") or 0)
        t["wall_s"] += float(s.get("wall_s") or 0)
        if s.get("usd") is None:
            t["usd_known"] = False
        else:
            t["usd"] += float(s["usd"])
    t["usd"] = round(t["usd"], 4)
    return t


def slice_spend(data):
    """The slice's spend without the prototypes': each variant has its own budget."""
    return totals([s for s in data.get("spend") or [] if not str(s.get("step") or "").startswith("prototype-")])


def budget_state(data):
    """Is the budget spent? The budget covers every step after the pick, not the prototypes."""
    budget = data.get("budget") or {}
    spent = slice_spend(data)
    over = []
    for k in ("tokens", "usd", "turns"):
        if budget.get(k) and spent.get(k, 0) >= budget[k]:
            over.append(k)
    return {"budget": budget, "spent": spent, "over": over, "spent_out": bool(over)}


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv spend", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument("reader", choices=["claude-result", "grok-result", "claude-session", "opencode"])
    r.add_argument("source")
    r.add_argument("--model")
    b = sub.add_parser("budget")
    b.add_argument("id")
    a = p.parse_args(argv)
    try:
        if a.cmd == "read":
            if a.reader == "claude-result":
                emit(from_claude_result(open(a.source).read(), a.model), True)
            elif a.reader == "grok-result":
                emit(from_grok_result(open(a.source).read(), a.model), True)
            elif a.reader == "claude-session":
                emit(from_claude_session(a.source, a.model), True)
            else:
                exported = open(a.source).read() if os.path.exists(a.source) else None
                emit(from_opencode(a.source, a.model, exported), True)
        else:
            data, _ = read_doc(record_path(repo_root(), a.id))
            state = budget_state(data)
            emit(state, True)
            sys.exit(3 if state["spent_out"] else 0)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

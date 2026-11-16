#!/usr/bin/env python3
"""The retro's mechanics: which slices are due, the fire and override counts,
running the retro brief, dropping candidates with no moment, and adding the
ones a person accepts.

Usage:
  xv retro due                          closed slices a retro would read, and why
  xv retro counts [--json]              per standard: fired, overridden, flagged
  xv retro run [<slice id> ...]         the retro brief in a fresh context; writes .xv/retro/<date>.md,
                                        or <date>-2.md, <date>-3.md and so on when that file exists
  xv retro accept <packet> <n> --by <name>   a person accepts candidate n
  xv retro standard <slice id> <n> --by <name>   accept the cleaner's candidate n from that slice's packet
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agentcli  # noqa: E402
import prompt as promptlib  # noqa: E402
from spend import slice_spend, totals  # noqa: E402
from xvlib import (XV_DIR, XVError, die, emit, git, load_config, main_root, read_doc,  # noqa: E402
                   repo_root, today)

QUIET_ORDERS = {"ready_to_merge", "moves_to_accept", "budget_not_set"}
MIN_FIRES = 5


def records(root):
    out = []
    for path in sorted(glob.glob(os.path.join(root, XV_DIR, "slices", "*.md"))):
        name = os.path.basename(path)
        if name.startswith("packet-") or name.endswith((".packet.md", ".boundary.md")):
            continue
        try:
            data, body = read_doc(path)
        except Exception:
            continue
        if data.get("id"):
            out.append((path, data, body))
    return out


def last_retro(root):
    files = sorted(glob.glob(os.path.join(root, XV_DIR, "retro", "*.md")))
    return os.path.basename(files[-1])[:10] if files else ""


def due(root):
    """Slices since the last retro that stopped, overran, or share a stop with another."""
    since = last_retro(root)
    recs = [(p, d, b) for p, d, b in records(root) if (d.get("created") or "") >= since]
    reasons = {}
    order_seen = {}
    for _, d, _ in recs:
        r = []
        hard = [s for s in d.get("stops") or [] if s.get("order") not in QUIET_ORDERS]
        if hard:
            r.append("stopped: " + ", ".join(sorted({s["order"] for s in hard})))
        # the budget covers every step after the pick, not the prototypes, as the budget order counts it
        spent = slice_spend(d)
        budget = dict(d.get("budget") or {})
        budget.update((budget.get("raised_from") or {}))  # a raise does not undo the overrun
        whole = totals(d.get("spend") or [])
        fc = sum(k.get("tokens") or 0 for k in (d.get("forecast") or {}).get("rows", []))
        if (budget.get("usd") and spent["usd_known"] and spent["usd"] > budget["usd"]) or \
                (budget.get("tokens") and spent["tokens"] > budget["tokens"]) or \
                (budget.get("turns") and spent["turns"] > budget["turns"]):
            r.append("overran its budget")
        elif fc and whole["tokens"] > 1.5 * fc:
            r.append(f"spent {whole['tokens']} tokens against a forecast of {fc}")
        for s in d.get("stops") or []:
            order_seen.setdefault(s.get("order"), set()).add(d["id"])
        if r:
            reasons[d["id"]] = r
    for order, ids in order_seen.items():
        if order not in QUIET_ORDERS and len(ids) > 1:
            for i in ids:
                reasons.setdefault(i, []).append(f"the same stop ({order}) on {len(ids)} slices")
    for module, ids in reworked([d for _, d, _ in recs], root).items():
        for i in ids:
            reasons.setdefault(i, []).append(
                f"module {module} was reworked: sent back to the maker on {len(ids)} closed slices ({', '.join(ids)})")
    return {"since": since or "the start", "slices": reasons}


def reworked(slices, root):
    """Modules that at least `limits.rework_slices` closed slices touched, each sent back to the maker."""
    limit = int(((load_config(root).get("limits") or {}).get("rework_slices")) or 0)
    by_module = {}
    for d in slices:
        if d.get("status") == "closed" and (d.get("maker_sendbacks") or 0) >= 1:
            for m in d.get("modules_touched") or []:
                by_module.setdefault(m, []).append(d["id"])
    return {m: sorted(ids) for m, ids in sorted(by_module.items()) if limit and len(ids) >= limit}


def counts(root, config=None):
    config = config or load_config(root)
    fired, overridden = {}, {}
    for _, d, _ in records(root):
        for rep in (d.get("checks") or {}).get("reports", []):
            if rep.get("agent") != "cleaner":
                continue
            for a in rep.get("applied") or []:
                rule = (a.get("rule") if isinstance(a, dict) else str(a)) or ""
                rule = re.sub(r"^\.xv/standards\.md:\s*", "", rule).strip()
                if rule and not rule.startswith(("baseline", "brief:")):  # a step the brief names is not a standard
                    fired[rule] = fired.get(rule, 0) + 1
        for o in d.get("overrides") or []:
            rule = (o.get("rule") or "").strip()
            overridden[rule] = overridden.get(rule, 0) + 1
    rate_limit = float((config.get("limits") or {}).get("override_rate") or 0.25)
    rows = []
    for rule in sorted(set(fired) | set(overridden)):
        f, o = fired.get(rule, 0), overridden.get(rule, 0)
        rate = o / f if f else (1.0 if o else 0.0)
        rows.append({"rule": rule, "fired": f, "overridden": o, "rate": round(rate, 2),
                     "flag": f >= MIN_FIRES and rate > rate_limit})
    return {"override_rate_limit": rate_limit, "min_fires": MIN_FIRES, "rules": rows}


BLOCK = re.compile(r"^### (\d+)\.\s*(.+?)\n(.*?)(?=^### \d+\.|\Z)", re.S | re.M)


def parse_candidates(text):
    out = []
    for n, title, rest in BLOCK.findall(text):
        fields = dict(re.findall(r"^- (\w+(?: of)?):[ \t]*(.*)$", rest, re.M))
        out.append({"n": int(n), "title": title.strip(), **fields})
    return out


def traceable(c, recs_by_id):
    src = c.get("from") or ""
    m = re.match(r"\s*`?([A-Za-z0-9][A-Za-z0-9._-]*)`?\s*[,:;]\s*(.+)", src)
    if not m or m.group(1) not in recs_by_id:
        return False
    moment = m.group(2).strip().strip("`").lower()
    data, body = recs_by_id[m.group(1)]
    fields = {k for k, v in data.items() if v not in (None, [], {}, "")} | {"log"}
    orders = {s.get("order") for s in data.get("stops") or []}
    named = set(re.findall(r"[a-z_]+", moment)) & (fields | orders)
    quoted = [q for q in re.findall(r"[\"“]([^\"”]{12,})[\"”]", m.group(2))
              if q.lower() in (json.dumps(data) + body).lower()]
    return bool(named or quoted)


def run(root, ids=None):
    config = load_config(root)
    recs = {d["id"]: (d, b) for _, d, b in records(root)}
    if not ids:
        ids = sorted(due(root)["slices"])
    if not ids:
        raise XVError("no slice is due for a retro; name one to run it anyway")
    missing = [i for i in ids if i not in recs]
    if missing:
        raise XVError(f"no slice record for {missing}")
    os.makedirs(os.path.join(root, XV_DIR, "retro"), exist_ok=True)
    day = today()
    stem, n = day, 1
    while os.path.exists(os.path.join(root, XV_DIR, "retro", f"{stem}.md")):
        n += 1
        stem = f"{day}-{n}"
    out = os.path.join(XV_DIR, "retro", f"{stem}.md")
    cpath = os.path.join(XV_DIR, "retro", f"{stem}.counts.json")
    with open(os.path.join(root, cpath), "w") as f:
        json.dump(counts(root, config), f, indent=1)
    reasons = due(root)["slices"]
    extra = [f"Slices: " + "; ".join(f"`.xv/slices/{i}.md` ({', '.join(reasons.get(i, ['named by a person']))})"
                                    for i in ids),
             f"Fire and override counts: `{cpath}`.",
             *[f"Module `{m}` was reworked on {', '.join(ids)}: propose a candidate with `kind: refactor` for it."
               for m, ids in reworked([d for d, _ in recs.values() if (d.get("created") or "") >= last_retro(root)],
                                      root).items()],
             f"Write the retro packet to `{out}`."]
    text = promptlib.brief("retro") + "\n" + promptlib.pointers("retro", root, config, None, extra)
    result = agentcli.run(agentcli.argv_for(config, "retro"), text, root, None,
                          int(config.get("step_timeout") or 3600))
    full = os.path.join(root, out)
    if not os.path.exists(full):
        raise XVError(f"the retro wrote no packet at {out}")
    cands = parse_candidates(open(full).read())
    kept = [c for c in cands if traceable(c, recs)]
    dropped = [c for c in cands if c not in kept]
    if dropped:
        with open(full, "a") as f:
            f.write("\n## Dropped by `xv retro run`\n\nNo slice and moment the records have:\n\n")
            for c in dropped:
                f.write(f"- {c['n']}. {c['title']} (from: {c.get('from', 'none')})\n")
    return {"packet": out, "candidates": len(kept), "dropped": len(dropped), "exit": result["code"],
            "kept": [f"{c['n']}. {c['title']} [{c.get('kind', '?')}]" for c in kept]}


TARGET = {"standard": ("standards.md", "## Rules"), "rule": ("rules.md", "## Entries"),
          "open": ("learnings.md", "## Open")}


def add_sighting(path, text, c, repo, by):
    """Add this repo and the candidate's slices to the Open entry the candidate names."""
    title = c["sighting of"].strip().strip("`")
    start = text.find("## Open")
    end = text.find("\n## ", start + 1) if start >= 0 else -1
    end = len(text) if end < 0 else end
    m = None
    if start >= 0:
        for hit in re.finditer(r"^### (?:\d{4}-\d{2}-\d{2}:\s*)?(.+?)[ \t]*\n(.*?)(?=^### |^## |\Z)",
                               text[start:end], re.S | re.M):
            if hit.group(1).strip() == title:
                m = hit
                break
    if not m:
        raise XVError(f"candidate {c['n']} is a sighting of {title!r}, and no Open entry has that title")
    block = new = m.group(0)
    if c.get("from"):
        if re.search(r"^- from:[ \t]*\S", new, re.M):
            new = re.sub(r"^(- from:[ \t]*\S.*)$", lambda x: x.group(1) + "; " + c["from"], new, count=1, flags=re.M)
        else:
            new = re.sub(r"^- from:[ \t]*$", lambda x: "- from: " + c["from"], new, count=1, flags=re.M)
            if not re.search(r"^- from:", new, re.M):
                new = re.sub(r"^(- added:.*\n)", lambda x: x.group(1) + "- from: " + c["from"] + "\n", new, count=1, flags=re.M)
            if not re.search(r"^- from:", new, re.M):
                new = re.sub(r"^(###.*\n)", lambda x: x.group(1) + "- from: " + c["from"] + "\n", new, count=1, flags=re.M)
    if re.search(r"^- seen: \[.*\]", new, re.M):
        new = re.sub(r"^(- seen: \[.*?)\]", lambda x: f"{x.group(1)}, {repo}@{today()}]", new, count=1, flags=re.M)
    else:
        new = new.rstrip("\n") + f"\n- seen: [{repo}@{today()}]\n"
    off = start + m.start()
    text = text[:off] + new + text[off + len(block):]
    with open(path, "w") as f:
        f.write(text)
    return {"added_to": os.path.join(XV_DIR, os.path.basename(path)), "entry": title, "by": by,
            "sighting": f"{repo}@{today()}"}


def accept(root, packet, n, by):
    cands = {c["n"]: c for c in parse_candidates(open(packet).read())}
    if n not in cands:
        raise XVError(f"no candidate {n} in {packet}")
    c = cands[n]
    kind = (c.get("kind") or "").split()[0].strip("`").lower() if c.get("kind") else ""
    adopts = None
    if kind == "refactor":
        return {"entry": c["title"], "by": by,
                "next": f"run `xv slice new --kind refactor` for this, with the scenario in your words; "
                        "no slice is opened here"}
    if kind == "adopt":
        adopts = (c.get("adopts") or "").strip().strip("`")
        if not re.match(r"^[\w.-]+/[\w.-]+#\d+$", adopts):
            raise XVError(f"candidate {n} adopts {adopts!r}; expected owner/repo#number")
        kind = "rule" if (c.get("into") or "").strip().startswith("rule") else "standard"
    if kind not in TARGET:
        raise XVError(f"candidate {n} is a {kind or 'candidate with no kind'}; only a standard, a rule or an "
                      "open entry is added here. A check is a slice; a retirement is deleting the line; "
                      "a change to a brief is for two people.")
    fname, heading = TARGET[kind]
    path = os.path.join(root, XV_DIR, fname)
    text = open(path).read() if os.path.exists(path) else f"# {fname}\n\n{heading}\n"
    url = git(["config", "--get", "remote.origin.url"], root, check=False).strip()
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    repo = m.group(1) if m else os.path.basename(main_root(root))
    if kind == "open" and c.get("sighting of"):
        return add_sighting(path, text, c, repo, by)
    if kind == "open":
        entry = f"\n### {today()}: {c['title']}\n- added: {today()} by {by}\n"
        if c.get("from"):
            entry += f"- from: {c['from']}\n"
        if c.get("miss"):
            entry += f"- miss: {c['miss']}\n"
        if c.get("said"):
            entry += f"- said: {c['said']}\n"
        entry += f"- rule: {c.get('rule') or c['title']}\n- seen: [{repo}@{today()}]\n"
    else:
        entry = f"\n### {c['title']}\n- added: {today()} by {by}\n"
        if c.get("from"):
            entry += f"- from: {c['from']}\n"
        if c.get("miss"):
            entry += f"- miss: {c['miss']}\n"
        entry += f"- seen: [{repo}@{today()}]\n"
        if kind == "standard":
            entry += f"- check: {c.get('check', 'none: judgement')}\n"
        if adopts:
            entry += f"- adopts: {adopts}\n"
    if heading not in text:
        text = text.rstrip("\n") + f"\n\n{heading}\n"
    i = text.index(heading) + len(heading)
    if kind == "open":
        text = text[:i] + "\n" + entry + text[i:]
    else:
        nxt = text.find("\n## ", i)
        text = (text.rstrip("\n") + "\n" + entry) if nxt < 0 else (text[:nxt].rstrip("\n") + "\n" + entry + text[nxt:])
    with open(path, "w") as f:
        f.write(text)
    out = {"added_to": os.path.join(XV_DIR, fname), "entry": c["title"], "by": by}
    if adopts:
        import promote
        out["sighting_draft"] = promote.draft(root, c["title"], c["title"], c.get("miss", ""),
                                              issue=adopts.split("#")[1], kind=kind)
        out["next"] = "review the sighting draft with the person; post it only on their approval"
    return out


def accept_standard(root, slice_id, n, by):
    """The person who set the work going accepts the cleaner's candidate n from a slice's packet."""
    from xvlib import record_path, slice_root
    path = record_path(root, slice_id)
    data, _ = read_doc(path)
    cands = []
    for rep in (data.get("checks") or {}).get("reports", []):
        if rep.get("agent") == "cleaner":
            cands += rep.get("candidate_standards") or []
    if not 1 <= n <= len(cands):
        raise XVError(f"the cleaner proposed {len(cands)} standard(s) on {slice_id}; there is no {n}")
    if by != data.get("originator"):
        print(f"note: {slice_id} was set going by {data.get('originator')}; {by} is accepting in their place",
              file=sys.stderr)
    sroot = slice_root(path)
    packet = os.path.join(sroot, XV_DIR, "retro", f"{today()}-{slice_id}-cleaner.md")
    os.makedirs(os.path.dirname(packet), exist_ok=True)
    with open(packet, "w") as f:
        f.write(f"### 1. {cands[n - 1]}\n- kind: standard\n- from: {slice_id}, the cleaner's report\n"
                f"- miss: the cleaner made this comment on {slice_id}\n- check: none: judgement\n")
    return accept(sroot, packet, 1, by)


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv retro", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("due")
    c = sub.add_parser("counts")
    c.add_argument("--json", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("ids", nargs="*")
    a = sub.add_parser("accept")
    a.add_argument("packet")
    a.add_argument("n", type=int)
    a.add_argument("--by", required=True)
    st = sub.add_parser("standard", help="accept the cleaner's candidate standard n from a slice")
    st.add_argument("id")
    st.add_argument("n", type=int)
    st.add_argument("--by", required=True)
    args = p.parse_args(argv)
    try:
        root = repo_root()
        if args.cmd == "due":
            emit(due(root), True)
        elif args.cmd == "counts":
            res = counts(root)
            if args.json:
                emit(res, True)
            else:
                for row in res["rules"]:
                    flag = "  <- proposed for retirement" if row["flag"] else ""
                    print(f"{row['fired']:>4} fired {row['overridden']:>3} overridden  {row['rule']}{flag}")
                if not res["rules"]:
                    print("no standard has fired yet")
        elif args.cmd == "run":
            emit(run(root, args.ids), True)
        elif args.cmd == "standard":
            emit(accept_standard(root, args.id, args.n, args.by), True)
        else:
            emit(accept(root, args.packet, args.n, args.by), True)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Move a learning from one repo toward the shared skills, and adopt one before
inventing it. Nothing is posted without a person's approval.

The channel is issues titled "Learning: ..." on the shared repo
(`promote.shared_repo` in .xv/config.yml, seanpk/xv-agents by default). Each
issue collects sightings: one per repo that saw the pattern, with the rule in
general words and one concrete example a person reviewed. No count opens a
pull request; two people on the shared repo decide when an issue is ready.

In an adopting repo:
  xv promote candidates                 entries that might matter beyond this repo
  xv promote search <words...>          open learning issues that might match
  xv promote draft --entry <title> --rule <general words> --example <the miss>
                   [--issue N] [--kind standard|rule|check] [--applies-to <stacks>]
                                        write a draft to .xv/promote/drafts/ for a person to review
  xv promote post <draft> --approved-by <name>
                                        post it; the only command that writes in public
  xv promote local                      Open learnings seen twice in this repo
  xv promote local --accept <title> --to standards|rules --by <name>

On the shared repo:
  xv promote tally                      open learning issues with their sightings, for the two people who decide

For tests and evals: XV_PROMOTE_ISSUES=<file.json> reads issues from a file, and
XV_PROMOTE_DRY=1 prints what `post` would send instead of sending it.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import entries as all_entries  # noqa: E402
from xvlib import (XV_DIR, XVError, die, emit, git, join_front_matter, load_config, main_root,  # noqa: E402
                   read_doc, repo_root, today)

TITLE_PREFIX = "Learning: "
SIGHTING = re.compile(r"^### Sighting: (.+?) · (\d{4}-\d{2}-\d{2})(?: · id (\w+))?", re.M)


# ---------------------------------------------------------------- settings

def settings(root):
    p = (load_config(root).get("promote") or {})
    return {"shared_repo": p.get("shared_repo") or "seanpk/xv-agents",
            "include_name": p.get("include_name", True) is not False,
            "name": p.get("name") or os.path.basename(main_root(root)),
            "description": p.get("description") or "",
            "stack": p.get("stack") or [],
            "attribution": p.get("attribution") or ""}


def repo_id(root):
    """A short stable id for this repo, so sightings count distinct repos without a name."""
    url = git(["config", "--get", "remote.origin.url"], root, check=False).strip() or main_root(root)
    return hashlib.sha256(url.encode()).hexdigest()[:8]


# ---------------------------------------------------------------- GitHub, or a file

def gh(args):
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if p.returncode != 0:
        raise XVError(f"gh {' '.join(args[:3])} failed: {p.stderr.strip()[:300]}")
    return p.stdout


def open_issues(shared, words=None):
    path = os.environ.get("XV_PROMOTE_ISSUES")
    if path:
        with open(path) as f:
            issues = json.load(f)
    else:
        query = f'"{TITLE_PREFIX.strip()}" in:title ' + " ".join(words or [])
        issues = json.loads(gh(["issue", "list", "-R", shared, "--state", "open", "--search", query,
                                "--limit", "50", "--json", "number,title,body,url,comments"]))
    issues = [i for i in issues if i.get("title", "").startswith(TITLE_PREFIX)]
    for i in issues:
        text = (i.get("body") or "") + "\n" + "\n".join(c.get("body", "") for c in i.get("comments") or [])
        sightings = SIGHTING.findall(text)
        i["sightings"] = [{"repo": r, "date": d, "id": x} for r, d, x in sightings]
        i["repos"] = len({x or r for r, _, x in sightings})
    if words:
        ws = [w.lower() for w in words if len(w) > 3]
        scored = [(sum(w in (i["title"] + (i.get("body") or "")).lower() for w in ws), i) for i in issues]
        issues = [i for s, i in sorted(scored, key=lambda t: -t[0]) if s > 0]
    return issues


# ---------------------------------------------------------------- candidates

def candidates(root):
    out = []
    for e in all_entries(root):
        if e["file"] == "learnings.md" and e["section"] != "Open":
            continue
        text = open(os.path.join(root, XV_DIR, e["file"])).read()
        block = text[text.find("### " + e["entry"]):]
        block = block[:block.find("\n### ", 4) if block.find("\n### ", 4) > 0 else len(block)]
        linked = re.search(r"^- (shared|adopts):\s*(.+)$", block, re.M)
        if not e["from"] or not e["miss"] and e["file"] != "learnings.md":
            continue  # an entry with no miss has nothing to show another repo
        out.append({"file": e["file"], "entry": e["entry"], "from": e["from"], "miss": e["miss"],
                    "linked": linked.group(2).strip() if linked else None})
    return out


# ---------------------------------------------------------------- drafts and posting

def cut_title(text, limit=90):
    if len(text) <= limit or text[limit].isspace():
        return text[:limit].rstrip()
    head = text[:limit]
    return head.rsplit(None, 1)[0] if len(head.split()) > 1 else head


def slug(text):
    text = re.sub(r"^\d{4}-\d{2}-\d{2}:?\s*", "", text)
    return "-".join(re.findall(r"[a-z0-9]+", text.lower())[:6]) or "learning"


def sighting_block(s, rid, rule, example, kind, applies, entry_file, entry):
    who = s["name"] if s["include_name"] else "a repo"
    lines = [f"### Sighting: {who} · {today()} · id {rid}"]
    if s["include_name"] and s["description"]:
        lines.append(s["description"])
    lines += ["", f"- Rule here: {rule}", f"- Kind: {kind}", f"- Applies to: {applies or 'any'}",
              f"- Example: {example}", f"- Local entry: `.xv/{entry_file}`: {entry}"]
    return "\n".join(lines) + "\n"


def draft(root, entry, rule, example, issue=None, kind="standard", applies=None):
    s = settings(root)
    found = [c for c in candidates(root) if c["entry"] == entry]
    if not found:
        raise XVError(f"no entry titled {entry!r} in .xv/rules.md, standards.md or learnings.md (Open)")
    c = found[0]
    if not rule or not example:
        raise XVError("a sighting needs the rule in general words (--rule) and one concrete example (--example)")
    block = sighting_block(s, repo_id(root), rule, example, kind, applies, c["file"], entry)
    if issue:
        meta = {"action": "sighting", "shared_repo": s["shared_repo"], "issue": int(issue)}
        body = block
    else:
        meta = {"action": "new", "shared_repo": s["shared_repo"], "title": TITLE_PREFIX + cut_title(rule)}
        body = (f"## The rule\n\n{rule}\n\n## Kind\n\n{kind}\n\n## Applies to\n\n{applies or 'any'}\n\n"
                f"## Sightings\n\n{block}")
    if s["attribution"]:
        body = body.rstrip("\n") + "\n\n" + s["attribution"] + "\n"
    meta.update({"entry_file": c["file"], "entry": entry, "status": "draft", "drafted": today()})
    d = os.path.join(root, XV_DIR, "promote", "drafts")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{today()}-{slug(entry)}.md")
    with open(path, "w") as f:
        f.write(join_front_matter(meta, "\n" + body))
    return os.path.relpath(path, root)


def link_entry(root, entry_file, entry, ref):
    path = os.path.join(root, XV_DIR, entry_file)
    text = open(path).read()
    head = "### " + entry
    i = text.find(head)
    if i < 0:
        return
    j = text.find("\n", i) + 1
    k = j
    while k < len(text) and text.startswith("- ", k):
        k = text.find("\n", k) + 1 or len(text)
    text = text[:k] + f"- shared: {ref}\n" + text[k:]
    with open(path, "w") as f:
        f.write(text)


def post(root, draft_path, approved_by):
    if not approved_by:
        raise XVError("nothing is posted without a person's approval: --approved-by <name>")
    meta, body = read_doc(draft_path)
    if meta.get("status") != "draft":
        raise XVError(f"{draft_path} is {meta.get('status')}, not a draft")
    shared = meta["shared_repo"]
    dry = os.environ.get("XV_PROMOTE_DRY")
    if meta["action"] == "sighting":
        args = ["issue", "comment", str(meta["issue"]), "-R", shared, "--body", body.strip()]
        ref = f"{shared}#{meta['issue']}"
    else:
        args = ["issue", "create", "-R", shared, "--title", meta["title"], "--body", body.strip()]
        ref = None
    if dry:
        print(json.dumps({"would_run": ["gh"] + args[:-1] + ["<body>"], "body": body.strip()}, indent=2))
        return {"posted": False, "dry_run": True}
    out = gh(args).strip()
    if ref is None:
        m = re.search(r"/issues/(\d+)", out)
        ref = f"{shared}#{m.group(1)}" if m else out
    meta.update(status="posted", approved_by=approved_by, posted=today(), ref=ref, url=out.splitlines()[-1] if out else "")
    posted = os.path.join(root, XV_DIR, "promote", "posted", os.path.basename(draft_path))
    os.makedirs(os.path.dirname(posted), exist_ok=True)
    with open(posted, "w") as f:
        f.write(join_front_matter(meta, body))
    os.remove(draft_path)
    link_entry(root, meta["entry_file"], meta["entry"], ref)
    return {"posted": True, "ref": ref, "record": os.path.relpath(posted, root)}


# ---------------------------------------------------------------- inside one repo

def local(root):
    return [e for e in all_entries(root) if e["file"] == "learnings.md" and e["section"] == "Open"
            and len(e["seen"]) >= 2]


def stale(root, days=90):
    """Open learnings seen once, longer ago than `days`: a person prunes them, or keeps one waiting."""
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    return [e for e in all_entries(root) if e["file"] == "learnings.md" and e["section"] == "Open"
            and len(e["seen"]) < 2 and e["seen"] and max(d for _, d in e["seen"]) < cutoff]


def local_accept(root, title, to, by):
    src = os.path.join(root, XV_DIR, "learnings.md")
    text = open(src).read()
    head = "### " + title
    i = text.find(head)
    if i < 0:
        raise XVError(f"no Open entry titled {title!r}")
    j = text.find("\n### ", i + 4)
    k = text.find("\n## ", i + 4)
    end = min(x for x in (j, k, len(text)) if x > 0)
    block = text[i:end].rstrip("\n")
    rest = text[:i] + text[end:].lstrip("\n")
    fields = dict(re.findall(r"^- (\w+):\s*(.+)$", block, re.M))
    rule = fields.get("rule") or re.sub(r"^\d{4}-\d{2}-\d{2}:\s*", "", title)
    entry = (f"\n### {rule}\n- added: {today()} by {by}\n- from: {fields.get('from', '')}\n"
             f"- miss: {fields.get('miss', fields.get('said', ''))}\n- seen: {fields.get('seen', '')}\n")
    if to == "standards":
        entry += "- check: none: judgement\n"
    dst = os.path.join(root, XV_DIR, f"{to}.md")
    dtext = open(dst).read() if os.path.exists(dst) else f"# {to.title()}\n"
    with open(dst, "w") as f:
        f.write(dtext.rstrip("\n") + "\n" + entry)
    line = f"- {today()}: \"{rule}\" to {to}.md, by {by}, after {len(re.findall(r'@', fields.get('seen', '')))} sightings"
    if "## Promoted" in rest:
        rest = rest.rstrip("\n") + "\n" + line + "\n"
    else:
        rest = rest.rstrip("\n") + "\n\n## Promoted\n\n" + line + "\n"
    with open(src, "w") as f:
        f.write(rest)
    return {"moved": rule, "to": f"{XV_DIR}/{to}.md", "by": by}


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="xv promote", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("candidates")
    s = sub.add_parser("search")
    s.add_argument("words", nargs="*")
    d = sub.add_parser("draft")
    d.add_argument("--entry", required=True)
    d.add_argument("--rule", required=True)
    d.add_argument("--example", required=True)
    d.add_argument("--issue")
    d.add_argument("--kind", default="standard", choices=["standard", "rule", "check", "brief"])
    d.add_argument("--applies-to")
    po = sub.add_parser("post")
    po.add_argument("draft")
    po.add_argument("--approved-by")
    lo = sub.add_parser("local")
    lo.add_argument("--accept")
    lo.add_argument("--to", choices=["standards", "rules"])
    lo.add_argument("--by")
    lo.add_argument("--prune-days", type=int, default=90,
                    help="also list Open entries seen once and not since this many days, to prune")
    t = sub.add_parser("tally")
    t.add_argument("-R", "--repo")
    a = p.parse_args(argv)
    try:
        root = repo_root()
        if a.cmd == "candidates":
            emit(candidates(root), True)
        elif a.cmd == "search":
            res = open_issues(settings(root)["shared_repo"], a.words)
            emit([{k: i.get(k) for k in ("number", "title", "url", "repos", "sightings")} for i in res], True)
        elif a.cmd == "draft":
            print(draft(root, a.entry, a.rule, a.example, a.issue, a.kind, a.applies_to))
        elif a.cmd == "post":
            emit(post(root, a.draft, a.approved_by), True)
        elif a.cmd == "local":
            if a.accept:
                if not (a.to and a.by):
                    raise XVError("--to standards|rules and --by <name>: a person promotes")
                emit(local_accept(root, a.accept, a.to, a.by), True)
            else:
                emit({"seen_twice": [{k: e[k] for k in ("entry", "from", "seen")} for e in local(root)],
                      "to_prune": [{k: e[k] for k in ("entry", "from", "seen")} for e in stale(root, a.prune_days)]},
                     True)
        else:
            shared = a.repo or settings(root)["shared_repo"]
            for i in sorted(open_issues(shared), key=lambda i: -i["repos"]):
                dates = ", ".join(s["date"] for s in i["sightings"])
                print(f"#{i['number']:<5} {i['repos']} repo(s)  {i['title'][len(TITLE_PREFIX):][:70]}  ({dates})")
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

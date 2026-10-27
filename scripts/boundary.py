#!/usr/bin/env python3
"""The boundary picture of a change, from the code, not drawn by an agent.

Modules and the import edges between them, before and after the change; new
outbound calls; tables and surface paths the diff adds or removes. Generated
so it can be wrong in a way someone can check.

A module is the first path component under a source root (or the file's stem,
for a file directly in the root). Under a root other than ".", the name starts
with the root: app/controllers, not controllers. Imports come from Python's own parser for
.py files, and a regex for JavaScript and TypeScript (import, require), Ruby
(require, require_relative) and Go (import blocks). The picture of a change
uses that parser on both sides, so the before and the after are comparable.
The whole-repo picture uses dependency-cruiser's graph instead when
`node_modules/.bin/depcruise` is installed in the repo; it never downloads it.

Usage:
  xv boundary --base <ref> [--json]     the change from <ref> to the working tree
  xv boundary --all [--json]            the whole repo as it is, for xv-init
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XV_DIR, XVError, die, git, load_config, match_any, repo_root  # noqa: E402

CODE = (".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".rb", ".go")
OUTBOUND = re.compile(
    r"\b(urllib\.request|urlopen|requests\.|http\.client|httpx|aiohttp|fetch\(|axios|XMLHttpRequest|"
    r"net/http|Net::HTTP|Faraday|HTTParty|smtplib|socket\.connect|boto3|grpc)\b")
TABLE = re.compile(
    r"\b(?:CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE|INSERT\s+INTO|UPDATE|DELETE\s+FROM|FROM|JOIN)\s+"
    r"[`\"']?([A-Za-z_][A-Za-z0-9_.]*)|\bcreate_table\s+[:\"']?(\w+)|\bTable\(\s*[\"'](\w+)")
SURFACE = re.compile(r"[\"'](/[A-Za-z0-9_\-/{}:<>.]*)[\"']")
SQL_WORDS = {"select", "where", "set", "values", "the", "a", "an", "into"}


def is_test(path, config):
    return match_any(path, (config.get("tests") or {}).get("paths") or [])


def source_files(paths, config):
    roots = (config.get("source") or {}).get("roots") or ["."]
    exclude = (config.get("source") or {}).get("exclude") or []
    out = []
    for p in paths:
        if not p.endswith(CODE) or match_any(p, exclude) or p.startswith(XV_DIR + "/") or is_test(p, config):
            continue
        for r in roots:
            r = r.strip("./")
            if r == "" or p == r or p.startswith(r + "/"):
                out.append(p)
                break
    return sorted(out)


def module_of(path, config):
    roots = sorted(((config.get("source") or {}).get("roots") or ["."]), key=len, reverse=True)
    for r in roots:
        r = r.strip("./")
        rel = path[len(r) + 1:] if r and path.startswith(r + "/") else (path if not r else None)
        if rel is None:
            continue
        parts = rel.split("/")
        if len(parts) == 1:
            stem = os.path.splitext(parts[0])[0]
            if stem in ("__init__", "index", "main"):
                return r or "root"
            return f"{r}/{stem}" if r else stem
        # under a root other than ".", the root is part of the name, so app/controllers
        # and app/javascript/controllers stay two modules
        return f"{r}/{parts[0]}" if r else parts[0]
    return path.split("/")[0]


def py_imports(text, path):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    names = []
    pkg = os.path.dirname(path).replace("/", ".")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                up = pkg.split(".")[: len(pkg.split(".")) - node.level + 1] if pkg else []
                base = ".".join([p for p in up if p] + ([base] if base else []))
            # "from pkg import mod" names the module; "from pkg.mod import name" names pkg.mod
            names.append(([f"{base}.{a.name}" if base else a.name for a in node.names], base))
    return names


JS_IMPORT = re.compile(r"""(?:import\s[^'"]*?from\s*|import\s*\(\s*|require\s*\(\s*)['"]([^'"]+)['"]""")
RB_IMPORT = re.compile(r"""\brequire(?:_relative)?\s*\(?\s*['"]([^'"]+)['"]""")
GO_IMPORT = re.compile(r'"([^"]+)"')


def resolve(name, path, files, lang, roots=()):
    """A repo file an import name points at, or None for a third-party import."""
    if lang == "py":
        cand = name.replace(".", "/")
        root_dirs = [r.strip("./") for r in roots]
        here = os.path.dirname(path)
        in_package = bool(here) and here + "/__init__.py" in files
        prefixes = ([] if in_package else [here + "/" if here else ""]) + [""] + [d + "/" for d in root_dirs if d]
        for pre in prefixes:
            for c in (pre + cand + ".py", pre + cand + "/__init__.py"):
                if c in files:
                    return c
        return None
    base = os.path.dirname(path)
    if lang == "js" and name.startswith("."):
        cand = os.path.normpath(os.path.join(base, name))
        for ext in ("", ".ts", ".tsx", ".js", ".jsx", ".mjs", "/index.ts", "/index.js"):
            if cand + ext in files:
                return cand + ext
    if lang == "rb":
        for cand in (os.path.normpath(os.path.join(base, name)), name, "lib/" + name):
            if cand + ".rb" in files:
                return cand + ".rb"
    if lang == "go":
        for f in files:
            if f.endswith(".go") and os.path.dirname(f) and name.endswith("/" + os.path.dirname(f)):
                return f
    return None


def graph(read, paths, config):
    """Edges between modules, and which modules call out of the process."""
    files = set(paths)
    src = source_files(paths, config)
    roots = (config.get("source") or {}).get("roots") or []
    edges, outbound, modules = set(), set(), set()
    for p in src:
        text = read(p)
        if text is None:
            continue
        m = module_of(p, config)
        modules.add(m)
        if p.endswith(".py"):
            names, lang = py_imports(text, p), "py"
        elif p.endswith(".rb"):
            names, lang = RB_IMPORT.findall(text), "rb"
        elif p.endswith(".go"):
            block = re.findall(r"import\s*\(([^)]*)\)|import\s+(\"[^\"]+\")", text)
            names = [n for b in block for part in b for n in GO_IMPORT.findall(part)]
            lang = "go"
        else:
            names, lang = JS_IMPORT.findall(text), "js"
        flat = []
        for n in names:
            if isinstance(n, tuple):
                subs = [x for x in n[0] if resolve(x, p, files, lang, roots)]
                flat += subs or [n[1]]
            else:
                flat.append(n)
        for n in flat:
            target = resolve(n, p, files, lang, roots)
            if target and target in src:
                tm = module_of(target, config)
                if tm != m:
                    edges.add((m, tm))
        if OUTBOUND.search(text):
            outbound.add(m)
    return {"modules": sorted(modules), "edges": sorted(edges), "outbound": sorted(outbound)}


def depcruise(root):
    exe = os.path.join(root, "node_modules", ".bin", "depcruise")
    if not os.path.exists(exe):
        return None
    p = subprocess.run([exe, "--output-type", "json", "."], cwd=root, capture_output=True, text=True)
    if p.returncode != 0:
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def at_ref(root, ref):
    paths = git(["ls-tree", "-r", "--name-only", ref], root).split()

    def read(p):
        r = subprocess.run(["git", "show", f"{ref}:{p}"], cwd=root, capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    return paths, read


def at_worktree(root):
    out = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], root)
    paths = [p for p in out.split("\0") if p and os.path.exists(os.path.join(root, p))]

    def read(p):
        try:
            with open(os.path.join(root, p), encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return None
    return paths, read


def diff_mentions(root, base, config):
    """Tables and surface paths in added and removed lines of source files."""
    text = git(["diff", "--no-prefix", "--no-color", "--no-ext-diff", "--unified=0", base, "--", "."], root)
    for p in git(["ls-files", "--others", "--exclude-standard"], root).split():
        try:
            with open(os.path.join(root, p), encoding="utf-8", errors="replace") as f:
                text += f"\n+++ {p}\n" + "".join("+" + line for line in f)
        except OSError:
            pass
    tables = {"added": set(), "removed": set()}
    surfaces = {"added": set(), "removed": set()}
    current = None
    for line in text.splitlines():
        if line.startswith("+++ "):
            current = None if line[4:] == "/dev/null" else line[4:]
            continue
        if not current or current.startswith(XV_DIR + "/") or is_test(current, config):
            continue
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
            side = "added" if line[0] == "+" else "removed"
            for groups in TABLE.findall(line[1:]):
                name = next((g for g in groups if g), None)
                if name and name.lower() not in SQL_WORDS and not name[0].isdigit():
                    tables[side].add(name)
            for s in SURFACE.findall(line[1:]):
                if len(s) > 1 and not s.startswith("//"):
                    surfaces[side].add(s)
    # a path both added and removed only moved within the diff
    for d in (tables, surfaces):
        both = d["added"] & d["removed"]
        d["added"] -= both
        d["removed"] -= both
    return ({k: sorted(v) for k, v in tables.items()}, {k: sorted(v) for k, v in surfaces.items()})


def change(root, base, config=None):
    config = config or load_config(root)
    bp, bread = at_ref(root, base)
    wp, wread = at_worktree(root)
    before, after = graph(bread, bp, config), graph(wread, wp, config)
    tables, surfaces = diff_mentions(root, base, config)
    changed = sorted(set(git(["diff", "--name-only", base], root).split()) |
                     set(git(["ls-files", "--others", "--exclude-standard"], root).split()))
    touched = sorted({module_of(p, config) for p in source_files(changed, config)})
    res = {
        "base": base,
        "touched": touched,
        "modules_added": sorted(set(after["modules"]) - set(before["modules"])),
        "modules_removed": sorted(set(before["modules"]) - set(after["modules"])),
        "edges_added": sorted(set(map(tuple, after["edges"])) - set(map(tuple, before["edges"]))),
        "edges_removed": sorted(set(map(tuple, before["edges"])) - set(map(tuple, after["edges"]))),
        "outbound_added": sorted(set(after["outbound"]) - set(before["outbound"])),
        "tables": tables, "surfaces": surfaces,
        "after": after,
        "source": "xv boundary (ast and regex)",
    }
    res["shape_hints"] = [h for h, v in (
        ("a module was added", res["modules_added"]), ("a module was removed", res["modules_removed"]),
        ("an edge between modules was added", res["edges_added"]),
        ("an edge between modules was removed", res["edges_removed"]),
        ("a module now calls out of the process", res["outbound_added"]),
        ("a table was added or removed", tables["added"] or tables["removed"]),
        ("a surface path was added or removed", surfaces["added"] or surfaces["removed"])) if v]
    return res


def from_depcruise(dc, paths, config):
    src = set(source_files(paths, config))
    edges, modules = set(), set()
    for m in dc.get("modules", []):
        a = m.get("source")
        if a not in src:
            continue
        modules.add(module_of(a, config))
        for d in m.get("dependencies", []):
            b = d.get("resolved")
            if b in src and module_of(b, config) != module_of(a, config):
                edges.add((module_of(a, config), module_of(b, config)))
    return edges, modules


def whole(root, config=None):
    config = config or load_config(root)
    wp, wread = at_worktree(root)
    g = graph(wread, wp, config)
    dc = depcruise(root)
    if dc:
        edges, modules = from_depcruise(dc, wp, config)
        g["edges"], g["modules"] = sorted(edges), sorted(set(g["modules"]) | modules)
        g["source"] = "dependency-cruiser"
    tables, surfaces = set(), set()
    for p in source_files(wp, config):
        text = wread(p) or ""
        for groups in TABLE.findall(text):
            name = next((x for x in groups if x), None)
            if name and name.lower() not in SQL_WORDS:
                tables.add(name)
        surfaces |= {s for s in SURFACE.findall(text) if len(s) > 1 and not s.startswith("//")}
    files_by_module = {}
    for p in source_files(wp, config):
        files_by_module.setdefault(module_of(p, config), []).append(p)
    return {"graph": g, "files": files_by_module, "tables": sorted(tables), "surfaces": sorted(surfaces)}


def mermaid(edges, modules, highlight=()):
    lines = ["```mermaid", "flowchart LR"]
    ids = {m: f"m{i}" for i, m in enumerate(sorted(set(modules) | {x for e in edges for x in e}))}
    for m, i in ids.items():
        lines.append(f'  {i}["{m}"]')
    for a, b in edges:
        style = "==>" if (a, b) in highlight else "-->"
        lines.append(f"  {ids[a]} {style} {ids[b]}")
    lines.append("```")
    return "\n".join(lines)


def render_change(res):
    out = [f"# Boundary picture", "", f"From `{res['base'][:12]}` to the working tree. Source: {res['source']}. "
           "Generated; check it against the diff.", ""]
    out += ["## Shape hints", ""] + ([f"- {h}" for h in res["shape_hints"]] or ["- none"]) + [""]
    out += ["## Modules", "", f"- touched: {', '.join(res['touched']) or 'none'}",
            f"- added: {', '.join(res['modules_added']) or 'none'}",
            f"- removed: {', '.join(res['modules_removed']) or 'none'}",
            f"- now calling out of the process: {', '.join(res['outbound_added']) or 'none'}", ""]
    out += ["## Edges", "",
            "- added: " + (", ".join(f"{a} → {b}" for a, b in res["edges_added"]) or "none"),
            "- removed: " + (", ".join(f"{a} → {b}" for a, b in res["edges_removed"]) or "none"), "",
            mermaid(res["after"]["edges"], res["after"]["modules"], set(map(tuple, res["edges_added"]))), ""]
    out += ["## Tables", "", f"- added: {', '.join(res['tables']['added']) or 'none'}",
            f"- removed: {', '.join(res['tables']['removed']) or 'none'}", ""]
    out += ["## Surface paths", "", f"- added: {', '.join(res['surfaces']['added']) or 'none'}",
            f"- removed: {', '.join(res['surfaces']['removed']) or 'none'}", ""]
    return "\n".join(out)


def render_all(root):
    w = whole(root)
    g = w["graph"]
    out = ["# Boundary picture of the whole repo", "", "Generated by `xv boundary --all`. Check it against the code.", "",
           "## Modules", ""]
    for m, files in sorted(w["files"].items()):
        flag = " (calls out of the process)" if m in g["outbound"] else ""
        out.append(f"- {m}{flag}: {', '.join(files[:8])}{' ...' if len(files) > 8 else ''}")
    out += ["", "## Edges", "", mermaid(g["edges"], g["modules"]), "",
            "## Tables mentioned", "", ", ".join(w["tables"]) or "none", "",
            "## Surface paths mentioned", "", ", ".join(w["surfaces"][:60]) or "none", ""]
    return "\n".join(out)


def write_for_slice(root, data):
    res = change(root, data.get("base") or "HEAD")
    path = os.path.join(root, XV_DIR, "slices", f"{data['id']}.boundary.md")
    with open(path, "w") as f:
        f.write(render_change(res))
        f.write("\n<details><summary>JSON</summary>\n\n```json\n" + json.dumps(res, indent=1) + "\n```\n</details>\n")
    return res


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv boundary", description=__doc__.split("\n")[0])
    p.add_argument("--base")
    p.add_argument("--all", action="store_true")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        root = repo_root()
        if a.all:
            print(json.dumps(whole(root), indent=1) if a.json else render_all(root))
        else:
            if not a.base:
                die("--base <ref>, or --all", 2)
            res = change(root, a.base)
            print(json.dumps(res, indent=1) if a.json else render_change(res))
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Install the skills, and `xv`, for this person or for one repo.

  xv install                        user scope: link the skills into each agent folder
                                    that exists, and `xv` into ~/.local/bin
  xv install --into <dir> ...       link into these skills folders instead
  xv install --scope project        copy the skills into this repo, for everyone on it
  xv install --remove [--scope ...] take out what this command put in
  xv install --dry-run              say what it would do

User scope links, so `git pull` in the clone upgrades every agent at once. It
looks for the folders of the agents that are installed: Claude Code
($CLAUDE_CONFIG_DIR or ~/.claude), Codex (~/.codex), Cursor (~/.cursor), Grok
(~/.grok), and the shared ~/.agents. A skills folder whose agent is not
installed is not created.

Project scope copies, because a link would point at one person's machine. It
writes into the agent folders the repo already has (.claude, .agents, .grok,
.cursor, .codex), or .agents/skills and .claude/skills when it has none. Each
copied skill carries `.xv-installed` with the version and a digest, so a later
install replaces a copy nobody edited and refuses one somebody did, and
`xv check` can tell current from stale. The scripts are not copied: everyone
on the repo still needs `xv` from a user install, and CI checks out this repo.

It never replaces a skill folder it did not make.
"""

import argparse
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import XVError, die, repo_root  # noqa: E402

HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(HOME_DIR, "skills")
MARK = ".xv-installed"


def version():
    with open(os.path.join(HOME_DIR, "VERSION")) as f:
        return f.read().strip()


def skill_names():
    return sorted(n for n in os.listdir(SKILLS) if os.path.exists(os.path.join(SKILLS, n, "SKILL.md")))


def user_folders():
    home = os.path.expanduser("~")
    claude = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(home, ".claude")
    candidates = [("claude", claude), ("codex", os.path.join(home, ".codex")),
                  ("cursor", os.path.join(home, ".cursor")), ("grok", os.path.join(home, ".grok")),
                  ("agents", os.path.join(home, ".agents"))]
    return [(name, os.path.join(base, "skills")) for name, base in candidates if os.path.isdir(base)]


def project_folders(root):
    found = [os.path.join(root, d, "skills") for d in (".claude", ".agents", ".grok", ".cursor", ".codex")
             if os.path.isdir(os.path.join(root, d))]
    return found or [os.path.join(root, ".agents", "skills"), os.path.join(root, ".claude", "skills")]


def digest(folder):
    h = hashlib.sha256()
    for dirpath, dirs, files in sorted(os.walk(folder)):
        dirs.sort()
        for f in sorted(files):
            if f == MARK:
                continue
            p = os.path.join(dirpath, f)
            h.update(os.path.relpath(p, folder).encode())
            with open(p, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()[:16]


def ours(path):
    """A folder this command made: a link into this clone, or a copy with our mark."""
    if os.path.islink(path):
        return os.path.realpath(path).startswith(os.path.realpath(SKILLS) + os.sep)
    return os.path.exists(os.path.join(path, MARK))


def edited(path):
    try:
        with open(os.path.join(path, MARK)) as f:
            mark = json.load(f)
    except (OSError, json.JSONDecodeError):
        return False
    return mark.get("digest") != digest(path)


def install_user(targets, dry, force):
    done, skipped = [], []
    for folder in targets:
        for name in skill_names():
            dest, src = os.path.join(folder, name), os.path.join(SKILLS, name)
            if os.path.lexists(dest) and not ours(dest) and not force:
                skipped.append(f"{dest}: exists and is not ours")
                continue
            if not dry:
                os.makedirs(folder, exist_ok=True)
                if os.path.lexists(dest):
                    os.remove(dest) if os.path.islink(dest) else shutil.rmtree(dest)
                os.symlink(src, dest)
            done.append(dest)
    bindir = os.path.expanduser("~/.local/bin")
    link = os.path.join(bindir, "xv")
    if os.path.lexists(link) and os.path.realpath(link) != os.path.realpath(os.path.join(HOME_DIR, "bin", "xv")) \
            and not force:
        skipped.append(f"{link}: exists and is not ours")
    else:
        if not dry:
            os.makedirs(bindir, exist_ok=True)
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(os.path.join(HOME_DIR, "bin", "xv"), link)
        done.append(link)
    on_path = bindir in os.environ.get("PATH", "").split(os.pathsep)
    return {"scope": "user", "linked": done, "skipped": skipped,
            "path_note": None if on_path else f"add {bindir} to your PATH"}


def install_project(root, targets, dry, force):
    done, skipped = [], []
    v = version()
    for folder in targets:
        for name in skill_names():
            dest, src = os.path.join(folder, name), os.path.join(SKILLS, name)
            if os.path.lexists(dest):
                if not ours(dest) and not force:
                    skipped.append(f"{os.path.relpath(dest, root)}: exists and is not ours")
                    continue
                if not os.path.islink(dest) and edited(dest) and not force:
                    skipped.append(f"{os.path.relpath(dest, root)}: edited in this repo; copy it under a new "
                                   "name and record why in .xv/decisions/, or pass --force to replace it")
                    continue
            if not dry:
                if os.path.lexists(dest):
                    os.remove(dest) if os.path.islink(dest) else shutil.rmtree(dest)
                shutil.copytree(src, dest)
                with open(os.path.join(dest, MARK), "w") as f:
                    json.dump({"skill": name, "version": v, "digest": digest(dest)}, f)
                    f.write("\n")
            done.append(os.path.relpath(dest, root))
    return {"scope": "project", "copied": done, "skipped": skipped, "version": v,
            "next": "commit the copies; everyone on the repo still needs `xv` on PATH from a user install"}


def remove(targets, root=None):
    gone = []
    link = os.path.expanduser("~/.local/bin/xv")
    if root is None and os.path.islink(link) and \
            os.path.realpath(link) == os.path.realpath(os.path.join(HOME_DIR, "bin", "xv")):
        os.remove(link)
        gone.append(link)
    for folder in targets:
        for name in skill_names():
            dest = os.path.join(folder, name)
            if os.path.lexists(dest) and ours(dest):
                os.remove(dest) if os.path.islink(dest) else shutil.rmtree(dest)
                gone.append(dest if not root else os.path.relpath(dest, root))
    return {"removed": gone}


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv install", description=__doc__.split("\n")[0])
    p.add_argument("--scope", choices=["user", "project"], default="user")
    p.add_argument("--into", action="append", help="a skills folder to install into; repeatable")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true", help="replace a folder this command did not make")
    a = p.parse_args(argv)
    try:
        if a.scope == "project":
            root = repo_root()
            targets = [os.path.abspath(d) for d in a.into] if a.into else project_folders(root)
            res = remove(targets, root) if a.remove else install_project(root, targets, a.dry_run, a.force)
        else:
            targets = [os.path.abspath(os.path.expanduser(d)) for d in a.into] if a.into \
                else [f for _, f in user_folders()]
            if not targets:
                raise XVError("no agent folder found (~/.claude, ~/.codex, ~/.cursor, ~/.grok, ~/.agents); "
                              "name one with --into <skills folder>")
            res = remove(targets) if a.remove else install_user(targets, a.dry_run, a.force)
        if a.dry_run:
            res["dry_run"] = True
        print(json.dumps(res, indent=2))
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

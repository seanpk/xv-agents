"""Shared helpers for the xv scripts. Python 3 standard library only.

Two small formats live here, because the standard library has no YAML parser:

- Front matter in a slice record or a packet: one `key: value` per line. A value
  that starts with `[`, `{` or `"` is JSON. Anything else is a bare scalar. Every
  file written this way is valid YAML, so other tools can read it.
- `.xv/config.yml`: the same scalars, plus nesting by two-space indent and block
  lists (`- item`). Anchors, multi-line strings and flow maps without JSON
  quoting are not supported; `load_config` fails loudly on what it cannot read.
"""

import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys

XV_DIR = ".xv"


class XVError(Exception):
    """A refusal or a broken input. The message is for a person."""


# ---------------------------------------------------------------- scalars

_INT = re.compile(r"^-?\d+$")
_FLOAT = re.compile(r"^-?\d+\.\d+$")


def parse_scalar(text):
    text = text.strip()
    if text == "" or text in ("null", "~"):
        return None
    if text[0] in "[{\"":
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            if text[0] == "[" and text[-1] == "]" and "[" not in text[1:-1] and "{" not in text:
                # a YAML flow list of bare words, as agents often write one
                return [parse_scalar(x) for x in text[1:-1].split(",") if x.strip()]
            raise XVError(f"not valid JSON: {text[:60]}... ({e})")
    if text in ("true", "yes"):
        return True if text == "true" else "yes"
    if text in ("false", "no"):
        return False if text == "false" else "no"
    if _INT.match(text):
        return int(text)
    if _FLOAT.match(text):
        return float(text)
    if text[0] == "'" and text[-1] == "'":
        return text[1:-1].replace("''", "'")
    return text


def dump_scalar(value):
    # yes/no stay bare words: the packet's fixed fields are read by people too.
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if value in ("yes", "no"):
            return value
        if re.match(r"^[A-Za-z0-9_./@+-][A-Za-z0-9 _./@:+-]*$", value) and \
                parse_scalar(value) == value and not value.endswith(" "):
            return value
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(value, ensure_ascii=False)


# ---------------------------------------------------------------- front matter

def split_front_matter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise XVError("front matter has no closing ---")
    head, body = text[4:end], text[end + 5:]
    data = {}
    last = None
    for n, line in enumerate(head.splitlines(), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and last is not None and isinstance(data.get(last), (list, type(None))):
            # a YAML block list under the key before it, as agents often write one
            data[last] = (data[last] or []) + [parse_scalar(line.lstrip()[2:])]
            continue
        if ":" not in line or line.startswith(" "):
            raise XVError(f"front matter line {n} is not `key: value`: {line!r}")
        key, _, value = line.partition(":")
        last = key.strip()
        data[last] = parse_scalar(value)
    return data, body


def join_front_matter(data, body):
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {dump_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n" + body


def read_doc(path):
    with open(path, encoding="utf-8") as f:
        return split_front_matter(f.read())


def write_doc(path, data, body):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(join_front_matter(data, body))
    os.replace(tmp, path)


# ---------------------------------------------------------------- config

def parse_config_text(text):
    root = {}
    # stack of (indent, container)
    stack = [(-1, root)]
    pending_key = None  # key whose value is an indented block, not yet typed
    lines = text.splitlines()
    for n, raw in enumerate(lines, 1):
        line = raw.split(" #", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise XVError(f"config line {n}: bad indent")
        parent_indent, parent = stack[-1]
        if pending_key is not None:
            holder, key, key_indent = pending_key
            pending_key = None
            if indent > key_indent:
                # first child decides whether the pending block is a list or a map
                holder[key] = [] if content.startswith("- ") or content == "-" else {}
                parent = holder[key]
                stack.append((indent - 1, parent))
        if content.startswith("- ") or content == "-":
            if not isinstance(parent, list):
                raise XVError(f"config line {n}: list item outside a list")
            parent.append(parse_scalar(content[2:]))
            continue
        if ":" not in content:
            raise XVError(f"config line {n}: expected `key: value`: {raw!r}")
        if not isinstance(parent, dict):
            raise XVError(f"config line {n}: key inside a list is not supported")
        key, _, value = content.partition(":")
        key = key.strip()
        if value.strip() == "":
            parent[key] = None
            pending_key = (parent, key, indent)
        else:
            parent[key] = parse_scalar(value)
    return root


DEFAULT_CONFIG = {
    "version": 1,
    "record_home": "file",
    "worktrees": ".xv/worktrees",
    "tests": {
        "paths": ["tests/**", "test/**", "spec/**", "**/*_test.*", "**/*.test.*", "**/*.spec.*", "**/test_*.py"],
        "command": "",
        "file_command": "",
    },
    "source": {"roots": ["."], "exclude": ["node_modules/**", "vendor/**", ".git/**", ".xv/**"]},
    "agents": {
        "default": ["claude", "-p", "--safe-mode", "--disable-slash-commands",
                    "--output-format", "json", "--permission-mode", "acceptEdits", "{prompt}"],
    },
    "seats": {"chief_engineer": "", "two_people": ""},
    "limits": {"budget_raise_pct": 0, "max_diff_lines": 0, "override_rate": 0.25},
    "reach": {"command": []},
    "wall": {"require_record": True},
}


def deep_merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif v is not None:
            out[k] = v
    return out


def solo(config):
    """A one-person team: the two-person stops still fire, and one person answers them."""
    return ((config.get("seats") or {}).get("two_people") or "") == "solo"


def pitch_status(root):
    path = os.path.join(root, XV_DIR, "pitch.md")
    if not os.path.exists(path):
        return "missing"
    try:
        data, body = read_doc(path)
    except XVError:
        return "unreadable"
    return str(data.get("status") or "written")


def load_config(root):
    path = os.path.join(root, XV_DIR, "config.yml")
    if not os.path.exists(path):
        return json.loads(json.dumps(DEFAULT_CONFIG))
    with open(path, encoding="utf-8") as f:
        return deep_merge(DEFAULT_CONFIG, parse_config_text(f.read()))


# ---------------------------------------------------------------- git and paths

def run(cmd, cwd=None, check=True, input=None, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, input=input, env=env)
    if check and p.returncode != 0:
        raise XVError(f"`{' '.join(cmd)}` failed ({p.returncode}): {p.stderr.strip() or p.stdout.strip()}")
    return p


def git(args, cwd, check=True):
    return run(["git"] + args, cwd=cwd, check=check).stdout


def repo_root(start=None):
    p = run(["git", "rev-parse", "--show-toplevel"], cwd=start or os.getcwd(), check=False)
    if p.returncode != 0:
        raise XVError("not inside a git repository")
    return p.stdout.strip()


def main_root(root):
    """The main checkout, when `root` is a linked worktree."""
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    return os.path.dirname(common) if os.path.basename(common) == ".git" else root


def worktrees_dir(root, config=None):
    config = config or load_config(root)
    rel = config.get("worktrees") or ".xv/worktrees"
    if rel.startswith(".git/"):
        common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
        return os.path.join(common, rel[len(".git/"):])
    return os.path.join(main_root(root), rel)


def record_path(root, slice_id):
    """Find a slice record: in this checkout, or in the slice's worktree."""
    here = os.path.join(root, XV_DIR, "slices", f"{slice_id}.md")
    if os.path.exists(here):
        return here
    wt = os.path.join(worktrees_dir(root), slice_id, XV_DIR, "slices", f"{slice_id}.md")
    if os.path.exists(wt):
        return wt
    raise XVError(f"no slice record for {slice_id!r} in {root} or its worktree")


def slice_root(record):
    """The checkout that holds a record: two levels above .xv/slices/."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(record))))


def tracked_files(root):
    out = git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], root)
    return sorted(f for f in out.split("\0") if f)


def match_any(path, patterns):
    for pat in patterns:
        if fnmatch.fnmatch(path, pat):
            return True
        # `**/x` also matches `x` at the top level
        if pat.startswith("**/") and fnmatch.fnmatch(path, pat[3:]):
            return True
    return False


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now():
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def today():
    return _dt.date.today().isoformat()


def die(msg, code=1):
    print(f"xv: {msg}", file=sys.stderr)
    sys.exit(code)


def emit(obj, as_json):
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    elif isinstance(obj, str):
        print(obj)
    else:
        print(json.dumps(obj, indent=2, ensure_ascii=False))

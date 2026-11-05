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
import orders  # noqa: E402
import packet as packetlib  # noqa: E402
from spend import row_tokens  # noqa: E402
from suite import run_suite  # noqa: E402
from xvlib import (XV_DIR, XVError, die, emit, git, load_config, match_any, names_test, now, read_doc, solo,  # noqa: E402
                   record_path, repo_root, slice_root, today, write_doc)

FIELDS = [
    # name, default
    ("id", None), ("title", ""), ("kind", "feature"), ("status", "open"),
    ("set_by", ""), ("created", None), ("branch", ""), ("base", None), ("next", "forecaster"),
    ("forecast", None), ("budget", None), ("red", None), ("wall_baseline", None),
    ("moved_tests", []), ("slice_only", []), ("wall_recommendations", []), ("suite", None), ("cleaner_commit", None),
    ("packet", None), ("shape_change", None), ("pitch_contradiction", None),
    ("spend", []), ("stops", []), ("decisions", []), ("prototypes", []), ("overrides", []), ("checks", {}),
]
LIST_FIELDS = {"moved_tests", "slice_only", "wall_recommendations", "spend", "stops", "decisions", "prototypes", "overrides"}
STATUSES = {"open", "working", "stopped", "ready", "closed", "abandoned"}
STEPS = ["forecaster", "scenario", "maker", "cleaner", "guardian", "close", "none"]
SEATS = {"originator", "two_people", "chief_engineer"}
CAUSES = {"decision", "environment", "tool", "agent", "watch"}

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

MOVE_KINDS = ("imports", "renames")


def parse_expect_moves(text):
    kinds = [k.strip() for k in text.split(",")]
    bad = [k for k in kinds if k not in MOVE_KINDS]
    if bad:
        raise XVError(f"--expect-moves takes {' and/or '.join(MOVE_KINDS)}, comma-separated; not {bad[0]!r}")
    return sorted(set(kinds), key=MOVE_KINDS.index)


def parse_renames(pairs):
    out = {}
    for pair in pairs:
        old, eq, new = pair.partition("=")
        if not (old.strip() and eq and new.strip()):
            raise XVError(f"--rename takes Old=New, both names given; not {pair!r}")
        out[old.strip()] = new.strip()
    return out


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
    if a.expect_moves is not None:
        data["expect_moves"] = parse_expect_moves(a.expect_moves)
    if a.rename:
        data["renames"] = parse_renames(a.rename)
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
    if a.field != "slice_only":
        item.setdefault("at", now())
    data[a.field].append(item)
    body = log_line(body, a.by or "watch", f"added to {a.field}")
    save(path, data, body)


def cmd_unmark(a):
    path, data, body = load(repo_root(), a.id)
    marks = data.get("slice_only") or []
    left = [m for m in marks if not (isinstance(m, dict) and m.get("test") == a.test)]
    if len(left) == len(marks):
        raise XVError(f"{a.test} is not marked slice-only")
    data["slice_only"] = left
    body = log_line(body, a.by or "watch", f"unmarked {a.test}; it joins the wall")
    save(path, data, body)


def same_move(moves, entry):
    """The move already recorded for this file and assertion, if any: one move is recorded once."""
    return next((m for m in moves if m.get("file") == entry.get("file")
                 and m.get("assertion") == entry.get("assertion")), None)


def cmd_move(a):
    path, data, body = load(repo_root(), a.id)
    for name in ("file", "assertion", "why"):
        if not getattr(a, name):
            raise XVError(f"a moved test names its {name}")
    entry = {"file": a.file, "assertion": a.assertion, "why": a.why, "by": a.by or "maker", "at": now()}
    listed = any(s.get("file") == a.file and s.get("test") and names_test(a.assertion, s["test"], start=True)
                 for s in data.get("slice_only") or [] if isinstance(s, dict))
    if a.slice_only and listed:
        entry["slice_only"] = True
    same = same_move(data["moved_tests"], entry)
    if same:
        same.update({k: v for k, v in entry.items() if k == "slice_only"})
    else:
        data["moved_tests"].append(entry)
    body = log_line(body, a.by or "maker", f"moved a test in {a.file}: {a.why}")
    if a.to and a.deleted:
        raise XVError("a moved test goes --to a path or is --deleted, not both")
    red = data.get("red")
    if (a.to or a.deleted) and red and a.file in (red.get("files") or []):
        module_of = lambda f: f[:-3].replace("/", ".") if f.endswith(".py") else f
        bare_of = lambda f: module_of(os.path.basename(f))
        files, cmd = list(red["files"]), red.get("command")
        old_cmd = cmd
        if a.deleted:
            files.remove(a.file)
            if cmd:
                gone = (a.file, module_of(a.file), bare_of(a.file))
                cmd = " ".join(t for t in cmd.split(" ") if t not in gone) if files else None
        else:
            files = [a.to if f == a.file else f for f in files]
            if cmd:
                swap = {a.file: a.to, module_of(a.file): module_of(a.to), bare_of(a.file): bare_of(a.to)}
                cmd = " ".join(swap.get(t, t) for t in cmd.split(" "))
        red["files"], red["command"] = files, cmd
        body = log_line(body, a.by or "maker",
                        f"red.files no longer names {a.file}" + (f", now {a.to}" if a.to else "")
                        + ("; red.command is now null: no red file is left" if cmd is None else
                           "; red.command updated to match" if cmd != old_cmd else ""))
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
                          "question": a.question, "answered_by": [], "answer": None,
                          "budget_seen": data.get("budget")})
    if a.step:
        data["stops"][-1]["step"] = a.step
    data["status"] = "stopped"
    body = log_line(body, "watch", f"stop ({a.order}) for {a.seat}: {a.question}")
    save(path, data, body)


EDIT_FLAGS = {"--edit": "file", "--old": "old", "--new": "new", "--kind": "kind"}
EDIT_KINDS = ("changelog", "test-rename", "test-remove", "doc")
TEST_DECL = re.compile(r"\s*(?:async\s+)?(?:(?:def|func|fn|function)\s+(test\w*)|(?:it|test|specify)\(\s*[\"'])")
BLANK_LINE = re.compile(r"\n[ \t]*\n")
BLOCK_CLOSER = re.compile(r"\s*[})\]]|\s*end\b")


def indent_of(line):
    return len(line) - len(line.lstrip())


def decorator_start(lines, d):
    """Index of the first decorator line above the declaration at `d`, or `d` when it has none."""
    start, depth = d, indent_of(lines[d])
    for j in range(d - 1, -1, -1):
        stripped = lines[j].strip()
        at_depth = indent_of(lines[j]) == depth
        if not stripped or not (indent_of(lines[j]) > depth or (at_depth and stripped.startswith(("@", "#")))):
            break
        if at_depth and stripped.startswith("@"):
            start = j
    return start


def is_whole_test(text, old):
    """Whether `old` is one test from its first decorator to its last line, with no other declaration in it."""
    lines = old.lstrip("\n").splitlines()
    if not old.endswith("\n") or not lines:
        return False
    first = text.count("\n", 0, text.index(old) + len(old) - len(old.lstrip("\n")))
    decl = next((i for i, ln in enumerate(lines) if TEST_DECL.match(ln)), None)
    if decl is None or decorator_start(text.splitlines(), first + decl) != first:
        return False
    lines = lines[decl:]
    depth = indent_of(lines[0])
    rest = [ln for ln in lines[1:] if ln.strip()]
    if not rest:
        return False
    inner = rest[:-1] if BLOCK_CLOSER.match(rest[-1]) and indent_of(rest[-1]) == depth else rest
    if any(indent_of(ln) <= depth for ln in inner):
        return False
    after = [ln for ln in text.split(old, 1)[1].splitlines() if ln.strip()]
    return not after or indent_of(after[0]) <= depth


class OfferAction(argparse.Action):
    """--option starts an option; --settles, --amends and the edit flags belong to the --option just before them."""

    def __call__(self, parser, ns, values, option_string=None):
        opts = ns.options = list(getattr(ns, "options", None) or [])
        if option_string == "--option":
            opts.append({"text": values, "settles": None, "amends": False})
            return
        if not opts:
            parser.error(f"{option_string} needs an --option before it")
        if option_string == "--settles":
            opts[-1]["settles"] = values
        elif option_string in EDIT_FLAGS:
            opts[-1].setdefault("edit", {})[EDIT_FLAGS[option_string]] = values
        else:
            opts[-1]["amends"] = True


def name_change(old, new):
    """(old name, new name) where new differs from old in one stretch, widened to whole identifiers."""
    n = min(len(old), len(new))
    i = 0
    while i < n and old[i] == new[i]:
        i += 1
    j = 0
    while j < n - i and old[len(old) - 1 - j] == new[len(new) - 1 - j]:
        j += 1
    word = lambda c: c.isalnum() or c == "_"
    while i > 0 and word(old[i - 1]):
        i -= 1
    while j > 0 and word(old[len(old) - j]):
        j -= 1
    return old[i:len(old) - j], new[i:len(new) - j]


def check_edit(root, config, n, edit):
    """Refuse an offered edit unless it is exactly one of the four kinds, and exact."""
    for key in EDIT_FLAGS.values():
        if edit.get(key) is None:
            raise XVError(f"option {n}: an edit needs --edit, --old, --new and --kind; {key} is missing")
    file, old, new, kind = edit["file"], edit["old"], edit["new"], edit["kind"]
    if kind not in EDIT_KINDS:
        raise XVError(f"option {n}: --kind is one of {', '.join(EDIT_KINDS)}; not {kind!r}")
    full = os.path.normpath(os.path.join(root, file))
    rel = os.path.relpath(full, root)
    if os.path.isabs(file) or rel.startswith("..") or not os.path.isfile(full):
        raise XVError(f"option {n}: {file} is not a file in this repo")
    if kind == "changelog":
        fits = rel == "CHANGELOG.md"
    elif kind == "doc":
        fits = (rel.endswith(".md") and rel != "CHANGELOG.md" and os.path.basename(rel) != "SKILL.md"
                and not rel.startswith(XV_DIR + os.sep))
    else:
        fits = match_any(rel, (config.get("tests") or {}).get("paths") or [])
    if not fits:
        raise XVError(f"option {n}: a {kind} edit does not fit {file}")
    if not old:
        raise XVError(f"option {n}: --old is empty")
    with open(full) as f:
        text = f.read()
    found = text.count(old)
    if found != 1:
        raise XVError(f"option {n}: --old is found {found} times in {file}; it must be found exactly once")
    if kind in ("changelog", "doc") and (BLANK_LINE.search(old) or BLANK_LINE.search(new)):
        raise XVError(f"option {n}: a {kind} edit holds no blank line, in --old or --new")
    if kind == "test-rename":
        one_line = "\n" not in old + new and old != new and TEST_DECL.match(old) and TEST_DECL.match(new)
        if not one_line or not all(re.fullmatch(r"\w+", x) for x in name_change(old, new)):
            raise XVError(f"option {n}: a rename changes one test's name to another test's name and nothing else")
        name = name_change(old, new)[0]
        if len(re.findall(rf"(?<!\w){re.escape(name)}(?!\w)", text)) != 1:
            raise XVError(f"option {n}: the name {name} also appears elsewhere in {file}; a rename is one line")
    if kind == "test-remove" and (new != "" or not is_whole_test(text, old)):
        raise XVError(f"option {n}: a removal's --new is empty, and --old is a whole test")


def cmd_offer(a):
    path, data, body = load(repo_root(), a.id)
    open_stops = [s for s in data["stops"] if s.get("answer") is None]
    if not open_stops:
        raise XVError("no open stop on this slice")
    options = a.options or []
    if not options:
        raise XVError("an offer needs at least one --option")
    for i, o in enumerate(options, 1):
        if not o["settles"]:
            raise XVError(f"option {i} has no --settles: say what is settled if it is picked")
    root = repo_root()
    config = load_config(slice_root(path))
    for i, o in enumerate(options, 1):
        if "edit" in o:
            check_edit(root, config, i, o["edit"])
    if a.recommend is not None and not 1 <= a.recommend <= len(options):
        raise XVError(f"--recommend is one of 1..{len(options)}")
    stop = open_stops[-1]
    stop["options"] = options
    stop["recommended"] = a.recommend
    stop.setdefault("budget_seen", data.get("budget"))
    body = log_line(body, "watch", f"offered {len(options)} options for {stop['order']}")
    save(path, data, body)


def answer_wall(data, stop, a):
    """--accept-wall and --refuse-wall answer an accept_moves stop's wall recommendations, and only that."""
    wall_flags = (("--accept-wall", a.accept_wall), ("--refuse-wall", a.refuse_wall))
    if stop["order"] != "accept_moves":
        for flag, names in wall_flags:
            if names:
                raise XVError(f"{flag} only answers an accept_moves stop, not {stop['order']}")
        return
    recs = data.get("wall_recommendations") or []
    known = {r.get("test") for r in recs}
    for t in sorted(set(a.accept_wall or []) & set(a.refuse_wall or [])):
        raise XVError(f"--accept-wall and --refuse-wall both name {t}; give one")
    for flag, names in wall_flags:
        for t in names or []:
            if t not in known:
                raise XVError(f"{flag} {t}: no wall recommendation names that test")
    stop["accepted_wall"] = list(a.accept_wall or [])
    stop["refused_wall"] = list(a.refuse_wall or [])
    for r in recs:
        test = r.get("test")
        r["accepted"] = test in stop["accepted_wall"] or (
            bool(r.get("accepted")) and test not in stop["refused_wall"])
        if r["accepted"]:
            r.pop("refused", None)
        else:
            r["refused"] = True


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
    alone = stop["seat"] == "two_people" and len(set(who)) < 2
    if alone and not solo(load_config(slice_root(path))):
        raise XVError("this stop is for two people: name both with --by a,b "
                      "(a one-person team sets seats.two_people: solo in .xv/config.yml)")
    if alone:
        stop["solo"] = True
    if a.cause and a.cause.split(":")[0].strip() not in CAUSES:
        raise XVError(f"cause is one of {sorted(CAUSES)}, then a free line after a colon")
    if a.resume and not a.next:
        raise XVError("--resume needs --next: every answer says where the slice goes")
    pick, settled, edit = None, a.settled, None
    if a.pick is not None:
        options = stop.get("options") or []
        if a.pick == "other":
            pick = "other"
        elif a.pick.isdigit() and 1 <= int(a.pick) <= len(options):
            pick = int(a.pick)
            settled = settled or options[pick - 1]["settles"]
            edit = options[pick - 1].get("edit")
        else:
            raise XVError("--pick is the number of an offered option, or other")
    if edit:
        check_edit(root, load_config(slice_root(path)), pick, edit)
    stopped_at = stop.get("step") or data["next"]
    # a stop raised before its work started has nothing to send back; `xv step` marks
    # its pre-step budget stop `pre_step`, and a prototype that ran out of budget has started
    not_started = ((stop["order"] == "setup_failed" and stop.get("step") == "setup")
                   or (stop.get("step") == "prototype"
                       and stop["order"] not in ("prototypes_ready", "prototype_budget_spent"))
                   or (stop["order"] == "budget_spent" and stop.get("pre_step") and a.next == stop.get("step")))
    sends_back = bool(a.next) and a.next != "close" and not not_started and not (
        a.next in STEPS and stopped_at in STEPS and STEPS.index(a.next) > STEPS.index(stopped_at))
    if (pick == "other" and not a.settled) or (sends_back and not settled):
        raise XVError("--settled is required when the answer sends work back or the pick is other: "
                      "say what is now true, so the next agent can act without the chat")
    stop["answered_by"], stop["answer"], stop["answered_at"] = who, a.answer, now()
    if sends_back:
        stop["sent_back"] = True
        stop["sent_back_to"] = a.next
    for key, value in (("pick", pick), ("settled", settled), ("new_info", a.new_info),
                       ("cause", a.cause), ("why", a.why)):
        if value is not None:
            stop[key] = value
    if a.bundle:
        stop["bundle"] = [b.strip() for b in a.bundle.split(",") if b.strip()]
    had_seen = "budget_seen" in stop
    seen = stop.pop("budget_seen", None)
    if had_seen and seen != data.get("budget"):
        amounts = lambda b: b and {k: b[k] for k in ("tokens", "usd", "turns") if k in b}
        stop["budget_change"] = {"from": amounts(seen), "to": amounts(data.get("budget"))}
    scribed = [name for name, value in (("settled", settled), ("new_info", a.new_info),
                                        ("cause", a.cause)) if value]
    answer_wall(data, stop, a)
    if stop["order"] == "slice_only_marks":
        for m in data.get("slice_only") or []:
            if isinstance(m, dict):
                m["accepted"] = True
    data["status"] = "working" if a.resume else data["status"]
    if a.next:
        data["next"] = a.next
    if stop["seat"] == "two_people" or stop["order"] == "ready_to_merge" or a.decision:
        rec = write_decision(slice_root(path), data["id"], who, stop, a.answer
                             + ("\n\nDecided by one person: this repo runs solo (seats.two_people: solo)."
                                if stop.get("solo") else ""))
        entry = {"date": today(), "who": who, "decision": a.answer, "record": rec}
        if stop.get("settled"):
            entry["settled"] = stop["settled"]
        data["decisions"].append(entry)
    body = log_line(body, ",".join(who), f"answered {stop['order']}: {a.answer}")
    if scribed:
        body = log_line(body, "watch", f"scribe: wrote {', '.join(scribed)} for {stop['order']} "
                                       f"as the scribe of {','.join(who)}")
    if edit:
        make_directed_edit(root, path, data, body, stop, edit, who)
        return
    save(path, data, body)


def rename_in_record(data, file, old_name, new_name):
    """A renamed test keeps its place in slice_only and wall_recommendations; other names are left alone."""
    for field in ("slice_only", "wall_recommendations"):
        for entry in data.get(field) or []:
            test = entry.get("test") if isinstance(entry, dict) else None
            if test and entry.get("file") in (None, file) and test.rsplit(".", 1)[-1] == old_name:
                entry["test"] = test[:len(test) - len(old_name)] + new_name


def make_directed_edit(root, path, data, body, stop, edit, who):
    """Make exactly the edit the person picked, in its own commit, then run the suite and the orders."""
    file, old, new, kind = edit["file"], edit["old"], edit["new"], edit["kind"]
    full = os.path.join(root, file)
    with open(full) as f:
        text = f.read()
    with open(full, "w") as f:
        f.write(text.replace(old, new, 1))
    by = " and ".join(who)
    if kind in ("test-rename", "test-remove"):
        data["moved_tests"].append({"file": file, "assertion": f"was: {old.strip()}; now: {new.strip() or 'removed'}",
                                    "why": f"directed by {by}: {kind}", "by": ",".join(who), "at": now()})
        if kind == "test-rename":
            rename_in_record(data, file, *name_change(old, new))
    body = log_line(body, ",".join(who), f"directed a {kind} edit in {file}")
    config = load_config(slice_root(path))
    data["suite"], _ = run_suite(root, config, data.get("base"), data.get("id"))
    step = stop.get("step") or data["next"]
    v = orders.verdict(data, step, config)
    body = apply_verdict(data, body, step, v)
    save(path, data, body)
    rel = os.path.relpath(path, root)
    paths = [file, rel]
    if data.get("packet"):
        packet = os.path.join(root, data["packet"])
        with open(packet) as f:
            text = f.read()
        heading = "## Directed edits after the guardian"
        text = text.rstrip("\n") + ("\n" if heading in text else f"\n\n{heading}\n\n") \
            + f"- {file} ({kind}): directed by {by}\n"
        with open(packet, "w") as f:
            f.write(text)
        paths.append(data["packet"])
    git(["add", "--", *paths], root)
    git(["commit", "-q", "--no-verify", "-m", f"xv({data['id']}): {kind} edit in {file}, directed by {by}",
         "--", *paths], root)
    emit(v, True)
    if v["stop"]:
        sys.exit(10)


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
                f"order: {stop['order']}\n---\n\n# {stop['question']}\n\n{answer}\n"
                + (f"\n## Settled\n\n{stop['settled']}\n" if stop.get("settled") else ""))
    return os.path.relpath(path, root)


REPORT_RE = re.compile(r"```xv-report\s*\n(.*?)\n```", re.S)


def extract_report(text):
    found = REPORT_RE.findall(text)
    if not found:
        # Claude's JSON output wraps the final message in "result", Grok's in "text"
        try:
            outer = json.loads(text)
            for key in ("result", "text"):
                if isinstance(outer, dict) and isinstance(outer.get(key), str) and REPORT_RE.search(outer[key]):
                    return extract_report(outer[key])
        except json.JSONDecodeError:
            pass
        # opencode --format json: one event per line, text parts carry the message
        texts = []
        last_codex = None
        for line in text.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            item = ev.get("item") if isinstance(ev, dict) else None
            if isinstance(item, dict) and item.get("type") == "agent_message":
                last_codex = item.get("text", "")
            part = ev.get("part") if isinstance(ev, dict) else None
            if isinstance(part, dict) and part.get("type") == "text":
                texts.append(part.get("text", ""))
        # codex exec --json: the report is in the last agent_message
        if last_codex is not None:
            return extract_report(last_codex) if REPORT_RE.search(last_codex) else None
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
            if not same_move(data["moved_tests"], mv):
                data["moved_tests"].append(mv)
    if agent == "scenario" and report.get("red"):
        old = data.get("red")
        if old and any(s.get("step") == "maker" for s in data.get("spend") or []):
            files = list(old.get("files") or [])
            files += [f for f in report["red"].get("files") or [] if f not in files]
            data["red"] = {**report["red"], "files": files}
        else:
            data["red"] = report["red"]
    if agent == "scenario":
        for key, need in (("old_tests_forced", ("file", "test", "why")), ("may_not_files", ("file", "why"))):
            listed = report.get(key) if isinstance(report.get(key), list) else []
            data[key] = [e for e in listed
                         if isinstance(e, dict) and all(isinstance(e.get(k), str) and e[k] for k in need)]
    if agent == "scenario" and isinstance(report.get("slice_only"), list):
        kept = [m for m in data.get("slice_only") or []
                if not any(isinstance(n, dict) and n.get("test") == m.get("test")
                           for n in report["slice_only"])]
        accepted = {m.get("test"): m for m in data.get("slice_only") or [] if isinstance(m, dict) and m.get("accepted")}
        # an agent cannot accept its own mark; only a person's answer, or the config's listed files, do
        data["slice_only"] = kept + [accepted.get(n.get("test"), {k: v for k, v in n.items() if k != "accepted"})
                                     if isinstance(n, dict) else n for n in report["slice_only"]]
    if agent == "guardian" and isinstance(report.get("wall_recommendations"), list):
        old = data.get("wall_recommendations") or []
        accepted_before = {r.get("test") for r in old if r.get("accepted")}
        refused = {r.get("test") for r in old if r.get("refused")}
        data["wall_recommendations"] = [
            {**{k: v for k, v in r.items() if k != "refused"}, "accepted": r.get("test") in accepted_before,
             **({"refused": True} if r.get("test") in refused else {})}
            for r in report["wall_recommendations"] if isinstance(r, dict)]
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


def accepted_by_listed_decision(root, data, pdata):
    """accepted holds only when accepted_by is a decision on this slice that answered a shape_or_pitch stop."""
    rel = pdata.get("accepted_by")
    if not rel or rel not in [d.get("record") for d in data.get("decisions") or []]:
        return False
    full = os.path.join(root, rel)
    if not os.path.exists(full):
        return False
    ddata, _ = read_doc(full)
    return ddata.get("order") == "shape_or_pitch"


def send_back(data, body, agent, order, keys, summary, target):
    """The watch's own send-back, kept like an answered stop so that `xv prompt` and `xv decisions` read it."""
    at = now()
    question = f"The {agent} step missed the scenario: {summary}"
    data["stops"].append({"at": at, "step": agent, "order": order, "seat": "watch", "question": question,
                          "answered_by": ["watch"], "answer": f"sent back to the {target}", "answered_at": at,
                          "settled": f"The slice came back to the {target} without a stop. {summary}",
                          "cause": "watch: the slice missed its scenario", "keys": keys,
                          "report_n": orders.report_index(data, agent), "packet": data.get("packet")})
    data["next"] = target
    return log_line(body, "watch", f"sent back to the {target}, answered {order}: {summary}")


def cmd_packet(a):
    """Attach the guardian's packet and copy its two fixed fields."""
    root = repo_root()
    path, data, body = load(root, a.id)
    pdata, _ = read_doc(a.file)
    for field, allowed in packetlib.ALLOWED.items():
        if pdata.get(field) not in allowed:
            raise XVError(f"the packet's {field} must be {' or '.join(allowed)}, found {pdata.get(field)!r}")
    checks = data.setdefault("checks", {}).setdefault("guardian", {})
    guardian_facts(root, data, checks, os.path.abspath(a.file))
    body = log_line(body, "guardian", f"packet: shape_change={data['shape_change']}, "
                                      f"pitch_contradiction={data['pitch_contradiction']}")
    v = orders.verdict(data, "guardian", load_config(slice_root(path)))
    body = apply_verdict(data, body, "guardian", v)
    save(path, data, body)


def guardian_facts(root, data, checks, packet_file):
    """The guardian's packet, as facts in the record: the fields the watch reads, and the checks orders reads."""
    pdata, pbody = read_doc(packet_file)
    for field in packetlib.ALLOWED:
        v = pdata.get(field)
        # a missing or malformed field waits for people, never for no one
        if field == "shape_change" and v == "accepted" and accepted_by_listed_decision(root, data, pdata):
            data[field] = v
        else:
            data[field] = v if v in packetlib.YES_NO else "yes"
    found = packetlib.misses(pbody) if pdata.get("scenario_miss") == "yes" else []
    data["scenario_miss"] = "yes" if found else "no"
    report = orders.last_report(data, "guardian") or {}
    checks["misses"] = found
    checks["miss_amend"] = any(m["amend"] for m in found)
    checks["picture_change"] = pdata.get("picture_change") or report.get("picture_change")
    checks["shape_breadth"] = pdata.get("shape_breadth") or report.get("shape_breadth")
    data["packet"] = os.path.relpath(packet_file, root)


def apply_verdict(data, body, agent, v):
    """Write what orders returned into the record: the stop, or the send-backs, and where `next` goes."""
    st = v["stop"]
    if st:
        already = any(s.get("order") == st["order"] and not s.get("answer") for s in data["stops"])
        if not already:
            data["stops"].append({"at": now(), "step": agent, "order": st["order"], "seat": st["seat"],
                                  "question": st["question"], "answered_by": [], "answer": None,
                                  "also": [f["order"] for f in v["fired"] if f is not st],
                                  "budget_seen": data.get("budget")})
            body = log_line(body, "watch", f"stop ({st['order']}) for {st['seat']}: {st['question']}")
        data["status"] = "ready" if st["order"] == "ready_to_merge" else "stopped"
    else:
        for f in v["fired"]:
            if f.get("send_back"):
                body = send_back(data, body, agent, f["order"], f["send_back"]["misses"],
                                 f["question"], f["send_back"]["to"])
    if v.get("next"):
        data["next"] = v["next"]
    return body


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
        k["tokens"] += row_tokens(s)
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
    s.add_argument("--kind", choices=["feature", "defect", "prototype", "refactor"], default="feature")
    s.add_argument("--scenario")
    s.add_argument("--scenario-file")
    s.add_argument("--expect-moves", help="the test changes the person expects: imports, renames, or both")
    s.add_argument("--rename", action="append", help="Old=New, a name this slice renames; one flag per pair")
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
    s.add_argument("--to", help="the new path of a file that moved")
    s.add_argument("--deleted", action="store_true", help="the whole file was removed")
    s.add_argument("--slice-only", action="store_true", help="a slice-only test removed after green")
    s.add_argument("--by")
    s.set_defaults(fn=cmd_move)

    s = sub.add_parser("unmark", help="take a test off slice_only so it joins the wall")
    s.add_argument("id")
    s.add_argument("--test", required=True)
    s.add_argument("--by")
    s.set_defaults(fn=cmd_unmark)

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
    s.add_argument("--step", help="the step the stop was raised at")
    s.set_defaults(fn=cmd_stop)

    s = sub.add_parser("offer", help="put the choices to the person on the open stop")
    s.add_argument("id")
    s.add_argument("--option", action=OfferAction)
    s.add_argument("--settles", action=OfferAction)
    s.add_argument("--amends", action=OfferAction, nargs=0)
    for flag in EDIT_FLAGS:
        s.add_argument(flag, action=OfferAction, help="a directed edit on the --option before it")
    s.add_argument("--recommend", type=int)
    s.set_defaults(fn=cmd_offer)

    s = sub.add_parser("answer", help="a person answers the open stop")
    s.add_argument("id")
    s.add_argument("--by", required=True, help="comma-separated names")
    s.add_argument("--answer", required=True)
    s.add_argument("--next", choices=STEPS + ["prototype"])
    s.add_argument("--resume", action="store_true")
    s.add_argument("--decision", action="store_true", help="write a decision record")
    s.add_argument("--pick", help="the number of the offered option, or other")
    s.add_argument("--settled", help="what is now true, for the next agent")
    s.add_argument("--new-info", dest="new_info", help="what the person brought that no agent had, or none")
    s.add_argument("--cause", help="decision, environment, tool, agent or watch, then a free line")
    s.add_argument("--why", help="the person's reason")
    s.add_argument("--bundle", help="comma-separated orders the same reply answered")
    s.add_argument("--accept-wall", dest="accept_wall", action="append", metavar="TEST",
                   help="accept the wall recommendation for this test; repeat per test")
    s.add_argument("--refuse-wall", dest="refuse_wall", action="append", metavar="TEST",
                   help="refuse the wall recommendation for this test; repeat per test")
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

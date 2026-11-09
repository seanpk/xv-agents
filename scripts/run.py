#!/usr/bin/env python3
"""The watch's mechanics: open a slice, run one step, run to the first stop, close.

The watch skill in a person's session and `xv run` in CI both call these. Each
step runs one agent in a fresh context through the CLI `.xv/config.yml` names,
applies its report and its spend to the record, runs the checks that follow the
step, and asks the standing orders whether to wake a person.

Usage:
  xv slice new <id> --by <name> --scenario-file <f> [...]   open a slice
  xv step <agent> <id>       one step; exit 10 on a stop
  xv step outsider --init    the outsider read for xv-init
  xv run <id>                steps from `next` to the first stop; exit 10 on a stop
  xv close <id>              the forecaster's line on the gap, the guide row, status closed
  xv init [--trial [--repo]|--adopt] [--no-try]   write a starter .xv/ into this repo
"""

import argparse
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agentcli  # noqa: E402
import orders  # noqa: E402
import prompt as promptlib  # noqa: E402
from names import COVERS_SEPARATOR, covers_name_found, joined_unsafely  # noqa: E402,F401
import record  # noqa: E402
import spend as spendlib  # noqa: E402
from suite import failing_tests, in_own_red, own_red_names, run_suite, shell, tests_timeout  # noqa: E402
from xvlib import (XV_DIR, XVError, die, git, load_config, match_any, now,  # noqa: E402
                   join_front_matter, main_root, record_path, repo_root, slice_root, split_front_matter, today,
                   worktrees_config, worktrees_dir)

HERE = os.path.dirname(os.path.abspath(__file__))
XV_HOME = os.path.dirname(HERE)
STEPS = ["forecaster", "scenario", "maker", "cleaner", "guardian", "close"]
EXIT_STOP = 10


# ---------------------------------------------------------------- helpers

# What each runner prints when it could not load or find tests. Same eleven runners as failing_tests; the words come
# from real output (tests/data/cannot-run), except where noted. Jasmine prints nothing of its own when a spec file
# fails to load (Node's error comes out before it runs), so only its no-specs line is here; its load failure is a
# generic error name below.
RUNNER_WORDS = {
    "unittest": [r"_FailedTest", r"Failed to import test module", r"Ran 0 tests", r"NO TESTS RAN"],
    "pytest": [r"ERROR collecting", r"Interrupted: \d+ errors? during collection", r"collected 0 items",
               r"no tests ran"],
    "jest": [r"Test suite failed to run", r"No tests found, exiting"],
    "vitest": [r"Failed Suites", r"No test files found"],
    "go": [r"\[build failed\]", r"\[setup failed\]", r"no packages to test", r"matched no packages"],
    "rspec": [r"An error occurred while loading", r"errors? occurred outside of examples", r"No examples found",
              r"0 examples, 0 failures"],
    "jasmine": [r"No specs found"],
    "minitest": [r"\b0 runs, 0 assertions"],
    "mocha": [r"Exception during run:", r"No test files found"],
    "cargo": [r"could not compile", r"no test target named"],
    "playwright": [r"Error: No tests found"],
}
RUNNER_CANNOT_RUN = re.compile("^.*(?:" + "|".join(w for ws in RUNNER_WORDS.values() for w in ws) + ").*$", re.I | re.M)
# Error names any program prints, a test that fails for a real reason included: they count only when no real test failed
GENERIC_ERRORS = re.compile(
    r"^.*(?:ModuleNotFoundError|ImportError|SyntaxError|LoadError|Cannot find module"
    r"|command not found|No such file or directory).*$", re.I | re.M)


def red_cannot_run(code, output):
    """Why a red command failed before its tests ran, or None when they ran. Exit 126 or 127; a runner's own words
    for "could not load or find tests" anywhere in the output (one file that cannot load stops the red even when
    other tests fail for real); or a generic error name when `failing_tests` finds no real failing test."""
    if code in (None, 0):
        return None
    if code in (126, 127):
        return f"the red command exited {code}: " + (output.strip().splitlines() or ["it could not start"])[-1]
    lines = RUNNER_CANNOT_RUN.findall(output)
    if not lines and not [n for n in failing_tests(output) if "_FailedTest" not in n]:
        lines = GENERIC_ERRORS.findall(output)
    seen = list(dict.fromkeys(line.strip() for line in lines))
    return "; ".join(seen)[:300] if seen else None


def changed_files(root, since):
    """Files changed since a commit, committed or not, plus untracked files."""
    files = set(git(["diff", "--name-only", since], root).split())
    files |= set(git(["ls-files", "--others", "--exclude-standard"], root).split())
    return sorted(files)


def commit(root, message, paths=None):
    if os.environ.get("XV_NO_COMMIT"):
        return None
    git(["add", "-A"] + (["--"] + paths if paths else []), root)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root).returncode == 0:
        return None
    git(["commit", "-q", "--no-verify", "-m", message], root)
    return git(["rev-parse", "HEAD"], root).strip()


def runs_dir(root, slice_id):
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    return os.path.join(common, "xv", "runs", slice_id or "init")


def reach(config, seat, question, record_rel):
    """Tell a person, if the team configured a way. Otherwise the watch says it."""
    cmd = (config.get("reach") or {}).get("command") or []
    if not cmd:
        return
    seats = config.get("seats") or {}
    who = seats.get(seat) or seat
    argv = [a.replace("{seat}", str(who)).replace("{question}", question).replace("{record}", record_rel)
            for a in cmd]
    subprocess.run(argv, check=False)


# ---------------------------------------------------------------- trial

def is_trial(root):
    """A trial keeps .xv/ out of git: the person is trying XV before committing to it."""
    p = subprocess.run(["git", "check-ignore", "-q", f"{XV_DIR}/config.yml"], cwd=root)
    return p.returncode == 0


def exclude_path(root):
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    return os.path.join(common, "info", "exclude")


# .git: a trial's .xv/ may be its own repo (`xv init --trial --repo`); its history stays out of each slice's copy.
LAYER_SKIP = ("slices", "worktrees", "listen", "boundary-all.md", "retro", "promote", ".git")


def copy_layer(src_root, dst_root):
    """In a trial the slice's worktree starts from a commit without .xv/; give it the layer."""
    src, dst = os.path.join(src_root, XV_DIR), os.path.join(dst_root, XV_DIR)
    for name in os.listdir(src):
        if name in LAYER_SKIP:
            continue
        s, d = os.path.join(src, name), os.path.join(dst, name)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            os.makedirs(dst, exist_ok=True)
            shutil.copy(s, d)


def bring_back(slice_root_dir, main, slice_id):
    """At close in a trial: the slice's record and packet, and its new guide rows, go to the main checkout."""
    from record import guide_rows
    s_slices, m_slices = (os.path.join(r, XV_DIR, "slices") for r in (slice_root_dir, main))
    os.makedirs(m_slices, exist_ok=True)
    for name in os.listdir(s_slices):
        if name.startswith(slice_id + "."):
            shutil.copy(os.path.join(s_slices, name), os.path.join(m_slices, name))
    sg, mg = (os.path.join(r, XV_DIR, "estimation.md") for r in (slice_root_dir, main))
    if os.path.exists(sg):
        if not os.path.exists(mg):
            shutil.copy(sg, mg)
            return
        old = open(mg).read()
        new = [r for r in guide_rows(open(sg).read()) if r not in set(guide_rows(old))]
        if new:
            with open(mg, "w") as f:
                f.write(old.rstrip("\n") + "\n" + "\n".join(new) + "\n")


# ---------------------------------------------------------------- slice new

def resolve_base(root, ref):
    """The commit a slice starts from: the ref given, else the remote's default branch, else HEAD."""
    if not ref:
        p = subprocess.run(["git", "rev-parse", "--verify", "-q", "refs/remotes/origin/HEAD^{commit}"],
                           cwd=root, capture_output=True, text=True)
        ref = "refs/remotes/origin/HEAD" if p.returncode == 0 else "HEAD"
    return git(["rev-parse", "--verify", ref + "^{commit}"], root).strip()


def run_worktree_command(command, wt, config):
    """Run a worktrees.setup or teardown command in the worktree. None when it passed or is unset;
    otherwise (command, exit code, its last lines)."""
    if not command:
        return None
    command = command.replace("{worktree}", shlex.quote(wt))
    code, out = shell(command, wt, tests_timeout(config))
    if code == 0:
        return None
    last = "\n".join(out.strip().splitlines()[-10:])
    return command, code, last


def cmd_slice_new(a):
    if a.share_build and a.from_ref is None:
        raise XVError("--share-build needs --from: it shares a build, and no build is given")
    if a.from_ref is not None and not a.from_ref.strip():
        raise XVError("--from needs a ref: the branch or commit of the build")
    root = repo_root()
    config = load_config(root)
    if not os.path.exists(os.path.join(root, XV_DIR, "config.yml")):
        raise XVError("no .xv/config.yml here; run xv-init first")
    from xvlib import pitch_status
    if pitch_status(root) in ("missing", "unreadable", "not written"):
        raise XVError("the pitch comes first: .xv/pitch.md is not written. The guardian checks every change "
                      "against it. Write it with the xv-init skill, or by hand and set `status: written` in its "
                      "front matter; commit it, then start the slice")
    if not is_trial(root) and git(["status", "--porcelain", "--", XV_DIR], root).strip():
        raise XVError("commit the project layer (.xv/) first "
                      "(or try XV without committing it: xv init --trial)")
    for flag, path in (("--recording", a.recording), ("--scenario-file", a.scenario_file)):
        if path and not os.path.isfile(path):
            raise XVError(f"{flag} {path}: no such file. Nothing was made; fix the path and run it again")
    wt = os.path.join(worktrees_dir(root, config), a.id)
    branch = a.branch or f"xv/{a.id}"
    wcfg = worktrees_config(config)
    base = resolve_base(root, a.base or wcfg.get("base"))
    if not is_trial(root):
        for name in ("config.yml", "pitch.md", "picture.md"):
            if subprocess.run(["git", "cat-file", "-e", f"{base}:{XV_DIR}/{name}"], cwd=root,
                              capture_output=True).returncode != 0:
                raise XVError(f"the base {base[:10]} has no committed {XV_DIR}/{name}: push .xv/ so the "
                              "remote's default branch has it, or pass --base HEAD")
    start = base
    if a.from_ref is not None:
        start = git(["rev-parse", "--verify", "-q", a.from_ref + "^{commit}"], root, check=False).strip()
        if not start:
            raise XVError(f"--from {a.from_ref}: no such branch or commit")
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    git(["worktree", "add", "-q", "-b", branch, wt, start], root)
    trial = is_trial(root)
    if trial:
        copy_layer(root, wt)
    args = ["new", a.id, "--by", a.by, "--kind", a.kind, "--branch", branch]
    for flag, value in (("--title", a.title), ("--axis", a.axis)):
        if value:
            args += [flag, value]
    for value in a.ignore or []:
        args += ["--ignore", value]
    if a.expect_moves is not None:
        args += ["--expect-moves", a.expect_moves]
    for pair in a.rename or []:
        args += ["--rename", pair]
    if a.scenario_file:
        args += ["--scenario-file", os.path.abspath(a.scenario_file)]
    elif a.scenario:
        args += ["--scenario", a.scenario]
    if a.recording:
        dest = os.path.join(XV_DIR, "recordings", os.path.basename(a.recording))
        os.makedirs(os.path.join(wt, XV_DIR, "recordings"), exist_ok=True)
        shutil.copy(os.path.abspath(a.recording), os.path.join(wt, dest))
        args += ["--recording", dest]
    p = subprocess.run([sys.executable, os.path.join(HERE, "record.py")] + args, cwd=wt,
                       capture_output=True, text=True)
    if p.returncode != 0:
        git(["worktree", "remove", "--force", wt], root, check=False)
        git(["branch", "-D", branch], root, check=False)
        raise XVError(p.stderr.strip())
    path = record_path(wt, a.id)
    data, body = record.load(wt, a.id)[1:]
    data["base"] = base
    if a.from_ref is not None:
        # the commit is kept with the ref: a build branch deleted after the slice opens is still the build
        data["build"] = {"kind": "exploration", "ref": a.from_ref, "commit": start}
        data["build_shared"] = "yes" if a.share_build else "no"
    if trial:
        data["trial"] = True
    record.save(path, data, body)
    commit(wt, f"xv({a.id}): open slice")
    print(wt)
    wt_config = load_config(wt)
    failed = run_worktree_command(worktrees_config(wt_config).get("setup"), wt, wt_config)
    if failed:
        command, code, last = failed
        path, data, body = record.load(wt, a.id)
        question = f"the worktree setup `{command}` failed ({code}); its last output:\n{last}"
        data["stops"].append({"at": now(), "step": "setup", "order": "setup_failed", "seat": "originator",
                              "question": question, "answered_by": [], "answer": None})
        data["status"] = "stopped"
        body = record.log_line(body, "watch", f"stop (setup_failed) for originator: {question}")
        record.save(path, data, body)
        commit(wt, f"xv({a.id}): setup failed")
        sys.exit(EXIT_STOP)


def cmd_slice_amend(a):
    root = repo_root()
    with open(a.scenario_file, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        raise XVError("the amendment is empty")
    path, data, body = record.load(root, a.id)
    marker = "\n## May ignore"
    at = body.find(marker)
    if at < 0:
        raise XVError("the record has no '## May ignore' heading to amend above")
    note = f"\n\n### Amended {today()} by {a.by}\n\n{text}\n"
    body = body[:at].rstrip("\n") + note + body[at:]
    data["red"] = None
    data["next"] = "scenario"
    data["amended_at_report"] = len((data.get("checks") or {}).get("reports") or [])
    body = record.log_line(body, a.by, "amended the scenario")
    record.save(path, data, body)


# ---------------------------------------------------------------- slice rebase

UNION_FILES = ("CHANGELOG.md", f"{XV_DIR}/estimation.md")
PICTURE = f"{XV_DIR}/picture.md"


def run_git(root, args, env=None):
    return subprocess.run(["git"] + args, cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                          env={**os.environ, **env} if env else None)


def git_path(root, name):
    return git(["rev-parse", "--path-format=absolute", "--git-path", name], root).strip()


def rebase_running(root):
    return any(os.path.isdir(git_path(root, d)) for d in ("rebase-merge", "rebase-apply"))


def unmerged(root):
    return git(["diff", "--name-only", "--diff-filter=U"], root).split()


def commits_between(root, rng):
    lines = git(["log", "--reverse", "--format=%H %s", rng], root).splitlines()
    return [line.split(" ", 1) for line in lines]


def both_sides(hunk):
    """One conflict's lines, ours first then theirs. When the hunk shows the base (diff3 style), a base line
    the other side dropped or edited is not kept from this side: a directed edit of a line is the edit, not the
    old line and the edit one after the other."""
    ours, base, theirs = hunk["ours"], hunk["base"], hunk["theirs"]
    if not base:
        return ours + theirs
    dropped_by_theirs = {l for l in base if l.strip() and l not in theirs}
    dropped_by_ours = {l for l in base if l.strip() and l not in ours}
    return ([l for l in ours if l not in dropped_by_theirs]
            + [l for l in theirs if l not in dropped_by_ours and l not in ours])


def keep_both_sides(root, rel):
    """Resolve a conflicted file by keeping both sides, ours first. False when the file has no markers to strip."""
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines(keepends=True)
    if not any(line.startswith("<<<<<<<") for line in lines):
        return False
    kept, hunk, part = [], None, None
    for line in lines:
        if line.startswith("<<<<<<<"):
            hunk, part = {"ours": [], "base": [], "theirs": []}, "ours"
        elif hunk is None:
            kept.append(line)
        elif line.startswith("|||||||"):
            part = "base"
        elif line.startswith("=======") and line.strip() == "=======":
            part = "theirs"
        elif line.startswith(">>>>>>>"):
            kept.extend(both_sides(hunk))
            hunk = None
        else:
            hunk[part].append(line)
    if hunk is not None:  # a conflict with no end: keep what it holds
        kept.extend(both_sides(hunk))
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(kept)
    git(["add", "--", rel], root)
    return True


def record_rel(root, slice_id):
    """The slice's record, as a path inside its worktree."""
    return os.path.relpath(record.load(root, slice_id)[0], root)


def rebase_state_path(root, slice_id):
    return git_path(root, f"xv-rebase-{slice_id}.json")


def rebase_state(root, slice_id, state=None):
    """The rebase's own notes, kept in the git dir: what to restore on --abort and what --continue still owes."""
    path = rebase_state_path(root, slice_id)
    if state is None:
        if not os.path.exists(path):
            raise XVError(f"no rebase of {slice_id} is in progress here: start one with `xv slice rebase {slice_id}`")
        with open(path) as f:
            return json.load(f)
    with open(path, "w") as f:
        json.dump(state, f, indent=1)
    return state


def tree_record_of_truth(root, slice_id, state):
    """The record's stops, budget and log lines as the rebase last left them for a person: the tree's record
    after a stop (the person's answers are written there), the state's notes after an error, when the
    tree holds the commit git replayed."""
    try:
        data, body = record.load(root, slice_id)[1:]
    except Exception:
        return state["stops"], state["budget"], state.get("log") or []
    log = log_lines(body)
    log = (state.get("log") or []) + [l for l in log if l not in (state.get("log") or [])]
    stops, budget = (data["stops"], data.get("budget")) if state.get("stopped") else (state["stops"], state["budget"])
    # a stop nobody answered goes from the record, and its own line (the last that names it) goes from the log
    for s in stops:
        if s.get("step") == "rebase" and s.get("answer") is None:
            own = f"stop ({s['order']}) for {s['seat']}: {s.get('question')}"
            hits = [i for i, l in enumerate(log) if own in l]
            if hits:
                log = log[:hits[-1]] + log[hits[-1] + 1:]
    return stops, budget, log


def log_lines(body):
    return [l for l in body.split("## Log", 1)[1].splitlines() if l.strip()] if "## Log" in body else []


def with_log(body, lines):
    """`body` with the log lines it lacks added at the end."""
    have = set(log_lines(body))
    extra = [l for l in lines if l not in have]
    return body.rstrip("\n") + "\n" + "\n".join(extra) + "\n" if extra else body


def conflict_markers(root, files):
    """The files that still hold a conflict's markers: a line of `<<<<<<<` and a later line of `>>>>>>>`."""
    out = []
    for rel in files:
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        opens = [i for i, line in enumerate(lines) if line.startswith("<<<<<<<")]
        if opens and any(line.startswith(">>>>>>>") for line in lines[opens[0]:]):
            out.append(rel)
    return out


def without_open_rebase_stops(stops):
    return [s for s in stops if not (s.get("step") == "rebase" and s.get("answer") is None)]


def maker_new_files(root, files):
    """{file: the command that drops it} for each of `files` the maker added: not in HEAD, so `git checkout`
    cannot restore it. A file git does not track yet goes with `rm`, a staged one with `git rm -f`."""
    out = {}
    for f in files:
        if subprocess.run(["git", "cat-file", "-e", f"HEAD:{f}"], cwd=root, capture_output=True).returncode == 0:
            continue
        tracked = bool(git(["ls-files", "--", f], root).strip())
        out[f] = f"git rm -f {f}" if tracked else f"rm {f}"
    return out


def rebase_stop(root, slice_id, state, config, fired=None, **checks):
    """Write the stop to the record and exit. Mid-rebase the record is left changed in the tree, not committed."""
    if checks.get("maker_edited"):
        checks["maker_new"] = maker_new_files(root, checks["maker_edited"])
    path, data, body = record.load(root, slice_id)
    data["stops"] = state["stops"]  # the record in the tree may be an older copy, replayed with the slice's commits
    data["budget"] = state["budget"]
    if fired:
        v = {"slice": slice_id, "after": "rebase", "stop": fired, "fired": [fired], "next": None}
    else:
        v = orders.verdict({**data, "checks": {"rebase": checks}}, "rebase", config)
    next_step = data["next"]
    body = with_log(body, state.get("log") or [])  # the lines written before this stop, which git's copy lacks
    body = record.apply_verdict(data, body, "rebase", v)
    data["next"] = next_step
    record.save(path, data, body)
    state["stops"] = data["stops"]
    state["stopped"] = True  # the tree's record now holds what a person answers
    if rebase_running(root):
        # the record git replayed and staged for the commit it stopped on; --continue puts it back
        staged = [line for line in git(["ls-files", "-s", "--", record_rel(root, slice_id)], root).splitlines()
                  if line.split()[2:3] == ["0"]]
        state["staged_record"] = ",".join(staged[0].split()[:2]) if staged else None
    rebase_state(root, slice_id, state)
    if not rebase_running(root):
        left = checks.get("maker_edited") or []  # the maker's edit stays in the tree for the person
        if left and not os.environ.get("XV_NO_COMMIT"):
            git(["add", "-A"], root)
            git(["reset", "-q", "--"] + left, root)
            if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root).returncode != 0:
                git(["commit", "-q", "--no-verify", "-m", f"xv({slice_id}): the rebase stopped"], root)
        else:
            commit(root, f"xv({slice_id}): the rebase stopped")
    v["worktree"] = root
    print(json.dumps(v, indent=2))
    if v["stop"]:
        reach(config, v["stop"]["seat"], v["stop"]["question"], os.path.join(XV_DIR, "slices", f"{slice_id}.md"))
    sys.exit(EXIT_STOP)


def rebase_maker(root, slice_id, config, state, files):
    """One maker run for the rebase, in a fresh context. Returns the stop's question, or None."""
    data = record.load(root, slice_id)[1]
    data = {**data, "spend": state["spend"] + [r["spend"] for r in state["runs"][state["applied"]:]],
            "budget": state["budget"]}
    spent_out = orders.budget_before(data)
    if spent_out:
        rebase_stop(root, slice_id, state, config, fired=spent_out)
    note = [f"This is a rebase: the slice is replayed on `{state['onto']}`; it was on `{state['old_base']}`. "
            f"The slice's diff is now `git diff {state['onto']}..HEAD`."]
    if files:
        note.append(f"Conflicted files to resolve: {', '.join(files)}.")
    with open(os.path.join(promptlib.SKILLS, "maker", "rebase.md"), encoding="utf-8") as f:
        part = f.read()
    rel = record_rel(root, slice_id)
    saved = git(["show", f"{state['orig_head']}:{rel}"], root)  # the record as saved, not the one git replays
    saved_data, saved_body = split_front_matter(saved)  # with the answers and the budget set during the rebase
    saved_data["stops"], saved_data["budget"] = state["stops"], state["budget"]
    saved = join_front_matter(saved_data, with_log(saved_body, state.get("log") or []))
    text = promptlib.build("maker", slice_id, root=root, extra=note, part=part, saved=saved)
    spent = spendlib.slice_spend(data)
    argv = agentcli.with_caps(agentcli.argv_for(config, "maker"), data.get("budget"), spent["usd"], spent["turns"])
    n = len(data.get("spend") or []) + len(state["runs"]) + 1
    log = os.path.join(runs_dir(root, slice_id), f"{n:02d}-maker.out")
    result = agentcli.run(argv, text, root, log, int(config.get("step_timeout") or 3600))
    s = spendlib.from_run(result)
    s.update(step="maker", at=now(), exit=result["code"], log=log)
    state["runs"].append({"stdout": result["stdout"], "spend": s})
    state["maker_ran"] = True
    report = record.extract_report(result["stdout"]) or {}
    if report.get("status") == "stopped":
        return (report.get("stop") or {}).get("question") or report.get("summary") or "the maker stopped"
    return None


def rebase_drive(root, slice_id, state, config):
    """Carry the rebase through its conflicts to the end, then finish. Exits 10 at a stop."""
    protected_paths = (config.get("tests") or {}).get("paths") or []

    def for_a_person(files):
        return [f for f in files if f == PICTURE or match_any(f, protected_paths)]

    while rebase_running(root):
        for f in unmerged(root):
            if f in UNION_FILES:
                keep_both_sides(root, f)
        files = unmerged(root)
        if files:
            for_person = for_a_person(files)
            if for_person:
                rebase_stop(root, slice_id, state, config, conflicts=for_person)
            stuck = rebase_maker(root, slice_id, config, state, files)
            state["conflicts"] += files
            state["changed"] = True
            rel = record_rel(root, slice_id)
            edited = git(["diff", "--name-only"], root).split() + git(["ls-files", "--others", "--exclude-standard"], root).split()
            edited = sorted(set(edited + files) - {rel})
            left = conflict_markers(root, edited)  # before `git add` hides them from `unmerged`
            if left:  # nothing is staged, so the files stay unmerged for the person
                rebase_stop(root, slice_id, state, config, stuck=f"conflict markers remain in {', '.join(left)}.")
            git(["add", "-A", "--"] + edited, root)
            for_person = for_a_person(edited)
            if for_person:
                rebase_stop(root, slice_id, state, config, maker_edited=for_person)
            if stuck:
                rebase_stop(root, slice_id, state, config, stuck=stuck)
        p = run_git(root, ["-c", "merge.conflictStyle=diff3", "rebase", "--continue"], {"GIT_EDITOR": "true"})
        if p.returncode != 0 and rebase_running(root) and not unmerged(root):
            raise XVError(f"git rebase --continue failed: {(p.stderr or p.stdout).strip()}")
    rebase_finish(root, slice_id, state, config)


def move_red_ref(root, data, old_base, onto):
    """Replay the red ref's commits onto the new base. Returns a message naming the ref when it cannot, else None."""
    ref = red_ref(data)
    held = red_held(root, data, old_base)
    if not held:
        return None
    scratch = tempfile.mkdtemp(prefix="xv-redref-")
    try:
        git(["worktree", "add", "-q", "--detach", scratch, onto], root)
        p = subprocess.run(["git", "cherry-pick", "--allow-empty", "--keep-redundant-commits", f"{old_base}..{held}"],
                           cwd=scratch, capture_output=True, text=True)
        if p.returncode != 0:
            return f"{ref} conflicts with {onto[:10]}: " + (p.stdout + p.stderr).strip()[-300:]
        git(["update-ref", ref, git(["rev-parse", "HEAD"], scratch).strip()], root)
    finally:
        drop_scratch(root, scratch)
    return None


def rebase_finish(root, slice_id, state, config):
    """The rebase is done in git: look for logical breaks, move the record, hash the wall, run the suite."""
    if not state["maker_ran"]:
        stuck = rebase_maker(root, slice_id, config, state, [])
        if run_git(root, ["status", "--porcelain"]).stdout.strip():
            state["changed"] = True
            protected = (config.get("tests") or {}).get("paths") or []
            edited = [f for f in changed_files(root, "HEAD") if f == PICTURE or match_any(f, protected)]
            if edited:  # a test file or the picture is a person's, as on a conflict replay
                rebase_stop(root, slice_id, state, config, maker_edited=edited)
            commit(root, f"xv({slice_id}): fix what the new base breaks")
        if stuck:
            rebase_stop(root, slice_id, state, config, stuck=stuck)
    new = commits_between(root, f"{state['onto']}..HEAD")
    moved, at = {}, 0
    for sha, subject in state["old"]:
        for i in range(at, len(new)):
            if new[i][1] == subject:
                moved[sha], at = new[i][0], i + 1
                break
    moved[state["old_base"]] = state["onto"]
    dropped = [k for k, old in state["named"].items() if old and old in {s for s, _ in state["old"]} and old not in moved]
    if dropped and not state.get("dropped_seen"):
        state["dropped_seen"] = True
        rebase_stop(root, slice_id, state, config, dropped=[f"{k} {state['named'][k][:10]}" for k in dropped])
    if not state.get("red_ref_seen"):
        state["red_ref_seen"] = True
        stuck_ref = move_red_ref(root, record.load(root, slice_id)[1], state["old_base"], state["onto"])
        if stuck_ref:
            rebase_stop(root, slice_id, state, config, red_ref=stuck_ref)
    path, data, body = record.load(root, slice_id)
    stops = without_open_rebase_stops(state["stops"])
    if len(stops) != len(state["stops"]):
        data["status"] = state["status"]
    data["stops"] = stops
    body = with_log(body, state.get("log") or [])  # the stop and answer lines written mid-rebase
    if state["budget"]:
        data["budget"] = state["budget"]
    data["base"] = state["onto"]
    for key, old in state["named"].items():
        if old:
            data[key] = moved.get(old, None if key in dropped else old)
    for run in state["runs"][state["applied"]:]:
        data["spend"].append(run["spend"])
        body = record.apply_report(data, body, "maker", run["stdout"])[0]
    state["applied"] = len(state["runs"])
    if state["changed"]:
        data["status"], data["next"] = "working", "cleaner"
    detail = f"; conflicts resolved: {', '.join(state['conflicts'])}" if state["conflicts"] else ""
    detail += f"; cleared from the record, dropped by the rebase: {', '.join(dropped)}" if dropped else ""
    body = record.log_line(body, "watch", f"rebased onto {state['onto'][:10]}{detail}")
    record.save(path, data, body)
    commit(root, f"xv({slice_id}): rebase")
    import wall
    if os.path.exists(wall.wall_file(root, slice_id)):
        old_wall = wall.load_baseline(root, slice_id)
        theirs = set(git(["diff", "--name-only", state["old_base"], state["onto"]], root).split())
        touched = set(git(["log", "--format=", "--name-only", f"{state['onto']}..HEAD"], root).split())
        mine = touched - theirs
        keep = {k: {f: v for f, v in (old_wall.get(k) or {}).items() if f in mine} for k in ("files", "assertions")}
        # a file both sides changed is hashed as it was at the baseline, replayed on the new base: the slice's
        # own red edits to it stay in the hash, and main's edits come in with it (the bare base when the
        # baseline commit did not replay)
        at = moved.get(old_wall.get("commit"), state["onto"])
        for f, (h, n) in wall.hashes_at(root, at, [f for f in touched & theirs if f in old_wall["files"]]).items():
            keep["files"][f], keep["assertions"][f] = h, n
        wall.baseline(root, slice_id, config, keep=keep, skip=[f for f in mine if f not in old_wall["files"]])
    suite, out = run_suite(root, config, state["onto"], slice_id)
    path, data, body = record.load(root, slice_id)
    failing = failing_tests(out or "")
    tests = [name for name in failing if not name.startswith(("(failures=", "(errors="))]
    red_names = own_red_names(root, data, state["onto"])
    own_red = data.get("suite") != "green" and tests and all(in_own_red(red_names, name) for name in tests)
    if not own_red:
        data["suite"] = suite
    record.save(path, data, body)
    commit(root, f"xv({slice_id}): hash the wall and run the suite after the rebase")
    if suite == "red" and not own_red:
        rebase_stop(root, slice_id, state, config, suite="red", failing=failing,
                    failing_step=orders.first_failing_step(out))
    os.remove(rebase_state_path(root, slice_id))
    print(json.dumps({"slice": slice_id, "status": data["status"], "next": data["next"], "base": data["base"],
                      "stop": None}, indent=2))


def cmd_slice_rebase(a):
    root0 = repo_root()
    root = slice_root(record_path(root0, a.id))
    if a.cont and a.abort or ((a.cont or a.abort) and a.onto):
        raise XVError("--continue and --abort stand alone: give one of them, without --onto or the other")
    if a.abort:
        state = rebase_state(root, a.id)
        state["stops"], budget, log = tree_record_of_truth(root, a.id, state)  # a person may have set the budget
        if rebase_running(root):
            git(["rebase", "--abort"], root)
        else:
            git(["reset", "--hard", state["orig_head"]], root)
        os.remove(rebase_state_path(root, a.id))
        stops = without_open_rebase_stops(state["stops"])
        path, data, body = record.load(root, a.id)
        kept = with_log(body, log)
        if budget and budget != data.get("budget") or state["runs"] or stops != state["first_stops"] or kept != body:
            # the maker's runs cost what they cost, and the answers stay; the stops the rebase raised and nobody answered go
            data["budget"] = budget or data.get("budget")
            data["spend"] += [r["spend"] for r in state["runs"]]
            data["stops"] = stops
            record.save(path, data, kept)
        print(json.dumps({"slice": a.id, "aborted": True, "head": state["orig_head"]}, indent=2))
        return
    config = load_config(root)
    if a.cont:
        state = rebase_state(root, a.id)
        state["stops"], state["budget"], state["log"] = tree_record_of_truth(root, a.id, state)
        state["stopped"] = False  # from here the tree holds git's copy again, until the next stop
        rebase_state(root, a.id, state)
        if rebase_running(root):
            # git will not replay over the record the stop changed, and a record the person staged
            # is not part of the replayed commit
            rel = record_rel(root, a.id)
            if state.get("staged_record"):
                git(["update-index", "--add", "--cacheinfo", f"{state['staged_record']},{rel}"], root)
            git(["checkout", "--", rel], root)
        return rebase_drive(root, a.id, state, config)
    if os.path.exists(rebase_state_path(root, a.id)):
        raise XVError(f"a rebase of {a.id} is in progress: finish it with `xv slice rebase {a.id} --continue` "
                      f"or give it up with `--abort`")
    main = main_root(root)
    onto = resolve_base(main, a.onto or worktrees_config(load_config(main)).get("base"))
    data = record.load(root, a.id)[1]
    head = git(["rev-parse", "HEAD"], root).strip()
    old_base = data.get("base") or git(["merge-base", onto, head], root).strip()
    state = {"orig_head": head, "onto": onto, "old_base": old_base, "old": commits_between(root, f"{old_base}..{head}"),
             "named": {k: data.get(k) for k in ("pre_maker_commit", "cleaner_commit")}, "status": data["status"],
             "stops": data["stops"], "first_stops": data["stops"], "spend": data["spend"], "budget": data.get("budget"),
             "runs": [], "applied": 0, "maker_ran": False, "changed": False, "conflicts": []}
    rebase_state(root, a.id, state)
    p = run_git(root, ["-c", "merge.conflictStyle=diff3", "rebase", "--onto", onto, old_base], {"GIT_EDITOR": "true"})
    if p.returncode != 0 and not rebase_running(root):
        os.remove(rebase_state_path(root, a.id))
        raise XVError(f"git rebase failed: {(p.stderr or p.stdout).strip()}")
    rebase_drive(root, a.id, state, config)


# ---------------------------------------------------------------- one step

def cmd_step(a):
    if a.agent == "outsider" or a.init:
        return step_init(a.agent)
    if not a.id:
        raise XVError("which slice? xv step <agent> <id>")
    code, v = step(a.agent, a.id)
    print(json.dumps(v, indent=2))
    sys.exit(code)


def step_init(agent):
    root = repo_root()
    config = load_config(root)
    text = promptlib.build(agent, None, root=root, init=True)
    argv = agentcli.argv_for(config, agent)
    result = agentcli.run(argv, text, root, os.path.join(runs_dir(root, None), f"{agent}.out"))
    report = record.extract_report(result["stdout"])
    print(json.dumps({"agent": agent, "report": report, "spend": spendlib.from_run(result)}, indent=2))


MERGE_STAGE = ("ready_to_merge", "accept_moves")


def is_record_path(f):
    """A slice record, not one of its side files or a production packet."""
    name = os.path.basename(f)
    return (f.startswith(f"{XV_DIR}/slices/") and f.count("/") == 2 and name.endswith(".md")
            and not name.endswith((".packet.md", ".boundary.md", ".prototypes.md"))
            and not name.startswith(("packet-", "pr-")))


def step(agent, slice_id, review_again=False):
    """Run one step. Returns (0, verdict) to go on, (EXIT_STOP, verdict) when a person must answer."""
    root0 = repo_root()
    path = record_path(root0, slice_id)
    root = slice_root(path)
    config = load_config(root)
    data, body = record.load(root, slice_id)[1:]
    if agent == "close":
        return close(slice_id), {"slice": slice_id, "after": "close", "stop": None}
    if agent not in STEPS:
        raise XVError(f"no step {agent!r}; one of {STEPS}")
    open_stops = [s for s in data["stops"] if s.get("answer") is None
                  and not (review_again and s["order"] in MERGE_STAGE)]
    if open_stops:
        return EXIT_STOP, {"slice": slice_id, "after": agent, "stop": open_stops[-1], "fired": [],
                           "note": "an earlier stop is unanswered"}
    budget_stop = orders.budget_before(data)
    if budget_stop:
        st = {"at": now(), "step": agent, "order": budget_stop["order"], "seat": budget_stop["seat"],
              "question": budget_stop["question"], "answered_by": [], "answer": None, "also": [],
              "pre_step": True, "budget_seen": data.get("budget")}
        data["stops"].append(st)
        data["status"] = "stopped"
        body = record.log_line(body, "watch", f"stop ({st['order']}) for {st['seat']}: {st['question']}")
        record.save(path, data, body)
        reach(config, st["seat"], st["question"], os.path.relpath(path, root))
        return EXIT_STOP, {"slice": slice_id, "after": agent, "stop": st, "fired": [budget_stop]}

    if agent == "scenario" and data.get("kind") == "refactor" and "\n### Amended " not in body:
        return refactor_scenario(path, root, config, data, body, slice_id)

    if (config.get("agents") or {}).get(agent) == "session":
        where = ""
        if agent == "scenario" and record.has_build(data):
            drop_session_scratch(root, slice_id)  # an earlier, unreported checkout
            scratch = scenario_scratch(root, data, config)
            session_scratch_state(root, slice_id, {"scratch": scratch, "head_before": git(["rev-parse", "HEAD"], root).strip()})
            where = (f" (write the red in {scratch}, a checkout at the base with no build; "
                     f"`xv record report` lands the red from it and drops it)")
        raise XVError(f"{agent} runs in the session{where}: use `xv prompt {agent} {slice_id}`, then "
                      f"`xv record report {slice_id} {agent} -` and `xv orders {slice_id} --after {agent}`")

    head_before = git(["rev-parse", "HEAD"], root).strip()
    pre = pre_step(agent, root, data, config)
    scratch = scenario_scratch(root, data, config) if agent == "scenario" and record.has_build(data) else None
    extra = None
    if scratch and data.get("build_shared") == "yes":
        extra = [f"The build is at `{data['build']['ref']}`, a reference only: the red tests what the scenario says, "
                 "and does not assume the code will look like the build."]
    text = promptlib.build(agent, slice_id, root=scratch or root, extra=extra)
    argv = agentcli.argv_for(config, agent)
    spent = spendlib.slice_spend(data)
    argv = agentcli.with_caps(argv, data.get("budget"), spent["usd"], spent["turns"])
    n = len(data.get("spend") or []) + 1
    log = os.path.join(runs_dir(root, slice_id), f"{n:02d}-{agent}.out")
    try:
        result = agentcli.run(argv, text, scratch or root, log, int(config.get("step_timeout") or 3600))
    except BaseException:
        if scratch:
            drop_scratch(root, scratch)
        raise

    data, body = record.load(root, slice_id)[1:]  # an agent may have run `xv record` itself
    if pre.get("pre_maker_commit"):
        data.setdefault("pre_maker_commit", pre["pre_maker_commit"])
    s = spendlib.from_run(result)
    s.update(step=agent, at=now(), exit=result["code"], log=log)
    data["spend"].append(s)
    red_before = data.get("red")
    try:
        body, report = record.apply_report(data, body, agent, result["stdout"])
    except Exception as e:  # a malformed report is a missing report, not a crash
        report = None
        data["checks"].setdefault("reports", []).append(
            {"agent": agent, "status": "no-report", "summary": f"the report could not be applied: {e}", "at": now()})
        body = record.log_line(body, agent, f"the report could not be applied: {e}")
    if agent == "scenario":
        body = accept_listed_marks(data, body, config)
    reported = ((report or {}).get("red") or {}).get("command") if agent == "scenario" else None
    if reported and joined_unsafely(reported):
        data["red"] = red_before  # a refused red is not kept: the maker is never handed it
    record.save(path, data, body)  # the wall reads moved_tests from disk: the report's moves must be there
    landed = land_scratch(root, scratch, data, config, report or {}) if scratch else None
    checks = post_step(agent, root, data, config, head_before, pre, report or {}, landed)
    data["checks"][agent] = checks
    data["status"] = "working"
    data["next"] = "scenario" if checks.get("red_joined") else STEPS[STEPS.index(agent) + 1]
    record.save(path, data, body)

    v = orders.verdict(data, agent, config)
    body = record.apply_verdict(data, body, agent, v)  # a step that stopped is not done: next stays on it
    record.save(path, data, body)
    commit_step(agent, root, slice_id, checks)
    v["record"] = os.path.relpath(path, root)
    v["worktree"] = root
    if data.get("packet"):
        v["packet"] = data["packet"]
    if v["stop"]:
        reach(config, v["stop"]["seat"], v["stop"]["question"], v["record"])
    return (EXIT_STOP if v["stop"] else 0), v


def accept_listed_marks(data, body, config):
    """A slice-only mark whose test checks a file the config lists in `tests.slice_only_files` is accepted."""
    listed = (config.get("tests") or {}).get("slice_only_files") or []
    for m in data.get("slice_only") or []:
        if isinstance(m, dict) and not m.get("accepted") and isinstance(m.get("checks"), str) and m["checks"] in listed:
            m["accepted"] = True
            body = record.log_line(body, "watch", f"slice-only mark on {m.get('test')} accepted: it checks "
                                   f"{m['checks']}, which the config lists in tests.slice_only_files")
    return body


def session_scratch_path(root, slice_id):
    return git_path(root, f"xv-scenario-scratch-{slice_id}.json")


def session_scratch_state(root, slice_id, state=None):
    """The checkout a session-mode scenario step made, kept in the git dir until its report lands the red:
    {"scratch": path, "head_before": the slice's HEAD then}. None when there is none."""
    path = session_scratch_path(root, slice_id)
    if state is not None:
        with open(path, "w") as f:
            json.dump(state, f)
        return state
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def drop_session_scratch(root, slice_id):
    """Drop a session-mode scenario checkout nobody reported on, and forget it."""
    state = session_scratch_state(root, slice_id)
    if state:
        drop_scratch(root, state["scratch"])
        os.remove(session_scratch_path(root, slice_id))


def land_session_scenario(root, slice_id, report):
    """`xv record report <id> scenario -` after a session-mode scenario step on a slice from a build: land the
    red written in the checkout and run it as the agent path does, record the scenario checks, drop the checkout.
    `report` is the scenario agent's whole report. False when no such checkout is waiting."""
    state = session_scratch_state(root, slice_id)
    if not state:
        return False
    os.remove(session_scratch_path(root, slice_id))
    path, data, body = record.load(root, slice_id)
    config = load_config(root)
    if not os.path.isdir(state["scratch"]):
        raise XVError(f"the scenario agent's checkout {state['scratch']} is gone, so its red cannot be landed: "
                      f"run `xv step scenario {slice_id}` again")
    landed = land_scratch(root, state["scratch"], data, config, report)
    data["checks"]["scenario"] = post_step("scenario", root, data, config, state["head_before"], {}, report, landed)
    record.save(path, data, body)
    return True


def drop_scratch(root, scratch):
    subprocess.run(["git", "worktree", "remove", "--force", scratch], cwd=root, capture_output=True)
    shutil.rmtree(scratch, ignore_errors=True)


def scenario_scratch(root, data, config):
    """A checkout at the base, outside the slice worktree, where the scenario agent writes the red without the build."""
    scratch = tempfile.mkdtemp(prefix="xv-scenario-")
    start = red_held(root, data, data["base"]) or data["base"]  # the red from earlier passes, without the build
    git(["worktree", "add", "-q", "--detach", scratch, start], root)
    if is_trial(root):
        copy_layer(root, scratch)
    failed = run_worktree_command(worktrees_config(config).get("setup"), scratch, config)
    if failed:
        drop_scratch(root, scratch)
        raise XVError(f"the worktree setup `{failed[0]}` failed ({failed[1]}) in the scenario agent's checkout; "
                      f"its last output:\n{failed[2]}")
    scratch_record = data
    unshared = data.get("build_shared") != "yes"
    if unshared:
        scratch_record = dict(data, build="none", branch=data["base"])
        scratch_record.pop("pre_maker_commit", None)
    path = os.path.join(scratch, XV_DIR, "slices", f"{data['id']}.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    record.save(path, scratch_record, record.load(root, data["id"])[2])
    if unshared:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(re.sub(r"\b[0-9a-f]{7,40}\b",
                           lambda m: "-" if off_the_base(root, data, m.group(0)) else m.group(0), text))
    return scratch


def red_ref(data):
    return "refs/xv/" + data["id"] + "/red"


def red_held(root, data, base):
    """The tip of the red ref when it sits on `base`, else None."""
    held = subprocess.run(["git", "rev-parse", "--verify", "-q", red_ref(data) + "^{commit}"],
                          cwd=root, capture_output=True, text=True).stdout.strip()
    if held and subprocess.run(["git", "merge-base", "--is-ancestor", base, held], cwd=root).returncode == 0:
        return held
    return None


def off_the_base(root, data, token):
    """True when `token` names a commit that is not an ancestor of the base."""
    p = subprocess.run(["git", "rev-parse", "--verify", "-q", token + "^{commit}"], cwd=root,
                       capture_output=True, text=True)
    return p.returncode == 0 and subprocess.run(
        ["git", "merge-base", "--is-ancestor", p.stdout.strip(), data["base"]], cwd=root).returncode != 0


def land_scratch(root, scratch, data, config, report):
    """Run the red on the base, take the wall baseline there, and cherry-pick the agent's red onto the slice branch."""
    landed = {"base_run": None, "wall": None, "conflict": None}
    try:
        red = data.get("red") or {}
        reported = (report.get("red") or {}).get("command")
        if red.get("command") and not (reported and joined_unsafely(reported)):
            landed["base_run"] = shell(red["command"], scratch, 600)
        import wall
        landed["wall"] = (wall.baseline(scratch, data["id"], config),
                          open(wall.wall_file(scratch, data["id"]), encoding="utf-8").read())
        sid = data["id"]
        git(["add", "-A", "--", ".", f":(exclude){XV_DIR}/slices/{sid}.*"], scratch)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=scratch).returncode != 0:
            git(["commit", "-q", "--no-verify", "-m", f"xv({sid}): red"], scratch)
            sha = git(["rev-parse", "HEAD"], scratch).strip()
            git(["update-ref", red_ref(data), sha], root)
            p = subprocess.run(["git", "cherry-pick", sha], cwd=root, capture_output=True, text=True)
            if p.returncode != 0:
                landed["conflict"] = (p.stdout + p.stderr).strip()[-800:]
                subprocess.run(["git", "cherry-pick", "--abort"], cwd=root, capture_output=True)
    finally:
        drop_scratch(root, scratch)
    return landed


def refactor_scenario(path, root, config, data, body, slice_id):
    """A refactor slice writes no red: the suite is green at the start, and that is its oracle."""
    suite, out = run_suite(root, config, data.get("base"), slice_id)
    checks = {"at": now(), "suite": suite, "suite_output": (out or "")[-800:],
              "failing_step": orders.first_failing_step(out) if suite == "red" else ""}
    summary = ("refactor slice: no new red; the suite is green at the start, and it is the oracle" if suite == "green"
               else "refactor slice: the suite is not green at the start, so there is no oracle")
    data["checks"].setdefault("reports", []).append({"agent": "scenario", "status": "done", "summary": summary,
                                                     "at": now()})
    body = record.log_line(body, "scenario", f"done: {summary}")
    if suite == "green":
        data["wall_baseline"] = wall_baseline(root, data, config)
    data["suite"] = suite
    data["checks"]["scenario"] = checks
    data["status"], data["next"] = "working", "maker"
    record.save(path, data, body)
    v = orders.verdict(data, "scenario", config)
    body = record.apply_verdict(data, body, "scenario", v)
    record.save(path, data, body)
    commit_step("scenario", root, slice_id, checks)
    v["record"] = os.path.relpath(path, root)
    v["worktree"] = root
    if v["stop"]:
        reach(config, v["stop"]["seat"], v["stop"]["question"], v["record"])
    return (EXIT_STOP if v["stop"] else 0), v


def pre_step(agent, root, data, config):
    pre = {}
    if agent == "maker" and not data.get("pre_maker_commit"):
        pre["pre_maker_commit"] = data["pre_maker_commit"] = git(["rev-parse", "HEAD"], root).strip()
    if agent == "cleaner":
        sp = os.path.join(root, XV_DIR, "standards.md")
        pre["standards"] = open(sp).read() if os.path.exists(sp) else None
    if agent == "guardian":
        boundary(root, data)
    return pre


def post_step(agent, root, data, config, head_before, pre, report, landed=None):
    """The mechanical checks after a step. Results go in the record; orders.py reads them."""
    checks = {"at": now()}
    tests = (config.get("tests") or {}).get("paths") or []
    if agent in ("forecaster", "guardian"):
        # read-only agents: anything they changed besides their own output is a stop
        own = {f"{XV_DIR}/slices/{data['id']}.packet.md", f"{XV_DIR}/slices/{data['id']}.boundary.md",
               f"{XV_DIR}/slices/{data['id']}.md"}
        checks["wrote"] = [f for f in changed_files(root, head_before) if f not in own]
    protected = [f"{XV_DIR}/config.yml", f"{XV_DIR}/slices/{data['id']}.wall.json", f"{XV_DIR}/pitch.md",
                 f"{XV_DIR}/picture.md", f"{XV_DIR}/estimation.md", f"{XV_DIR}/rules.md"]
    if agent in ("scenario", "maker", "cleaner"):
        changed = changed_files(root, head_before)
        named = set()
        if agent == "maker":
            # only the picture can be licensed; the other protected files stay a person's
            named = {e["file"] for e in data.get("may_not_files") or []
                     if isinstance(e, dict) and e.get("file") == f"{XV_DIR}/picture.md" and e.get("why")}
        checks["protected_changed"] = [f for f in protected if f in changed and f not in named]
    if agent == "scenario":
        files = changed_files(root, head_before)
        files = [f for f in files if not f.startswith(XV_DIR + "/")]
        checks["outside_tests"] = [f for f in files if not match_any(f, tests)]
        red = data.get("red") or {}
        reported = (report.get("red") or {}).get("command")
        if reported and joined_unsafely(reported):
            checks["red_fails"] = None
            checks["red_joined"] = reported
        elif red.get("command"):
            # a slice from a build: the red ran on the base, in the agent's checkout; now it runs on the build
            code, out = landed["base_run"] if landed else red_run(root, data, red, config)
            checks["red_fails"] = None if code is None else code != 0
            checks["red_output"] = out[-800:]
            cannot = red_cannot_run(code, out)
            if cannot:
                checks["red_fails"] = None
                checks["red_cannot_run"] = cannot
            if code is None:
                checks["setup_failed"] = out
            if landed and landed["conflict"]:
                checks["cherry_pick_conflict"] = landed["conflict"]
            elif landed and checks["red_fails"]:
                code, out = shell(red["command"], root, 600)
                checks["red_on_build"] = {"passes": code == 0, "failing": failing_tests(out)}
        else:
            checks["red_fails"] = None
        changed = old_red_changed(root, data, red, tests)
        checks["old_red_changed"] = changed or []
        if changed is None:
            checks["old_red_unchecked"] = ("The check for changes to old test files that existed at the base could not run: "
                                           "the record has no base, or the wall module did not load.")
        checks["red_gaps"] = scenario_red_gaps(root, data, red)
        # coverage stays across a send-back; a pass that went on to the maker ended the run, so it starts again
        report = with_kept_covers(report, (data.get("checks", {}).get("scenario") or {}).get("covers_kept")
                                  if data.get("next") != "maker" else None)
        checks["covers_kept"] = [c for c in report.get("covers") or []
                                 if isinstance(c, dict) and c.get("item") and covers_names(c.get("test"))]
        checks["unreadable"] = unreadable_input(root, data, report)
        answered = " ".join(s.get("question") or "" for s in data.get("stops") or []
                            if s.get("order") == "red_misses_scenario" and s.get("answer"))
        checks["not_covered"] = [n for n in (report.get("not_covered") or []) if isinstance(n, dict)
                                 and f"did not cover {n.get('item')}:" not in answered]
        checks["missed_points"] = missed_points(root, data, report)
        if landed:  # the wall hashes the test files at the base, not at the build
            wb, wall_text = landed["wall"]
            import wall
            os.makedirs(os.path.dirname(wall.wall_file(root, data["id"])), exist_ok=True)
            with open(wall.wall_file(root, data["id"]), "w", encoding="utf-8") as f:
                f.write(wall_text)
        else:
            wb = wall_baseline(root, data, config)
        if wb:
            data["wall_baseline"] = wb
    if agent == "maker" and data.get("prototype_sessions"):
        checks["reused_prototype_context"] = (data["spend"][-1].get("session") in data["prototype_sessions"])
    if agent in ("maker", "cleaner"):
        suite, out = run_suite(root, config, data.get("base"), data.get("id"))
        checks["suite"], checks["suite_output"] = suite, (out or "")[-800:]
        checks["failing_step"] = orders.first_failing_step(out) if suite == "red" else ""
        checks["failing"] = failing_tests(out or "") if suite == "red" else []
        prior = (data.get("checks") or {}).get(agent) or {}
        checks["failing_history"] = (prior.get("failing_history") or []) + [checks["failing"]]
        data["suite"] = suite
        stat = git(["diff", "--numstat", data.get("base") or head_before,
                    "--", ".", f":(exclude){XV_DIR}"], root)
        checks["diff_lines"] = sum(int(x) for line in stat.splitlines()
                                   for x in line.split("\t")[:2] if x.isdigit())
        before = (data.get("checks") or {}).get(agent) or {}
        checks["diff_history"] = (before.get("diff_history") or []) + [checks["diff_lines"]]
        import wall
        record.expected_moves(root, data, config)
        checks["wall"] = record.wall_for_build(root, data, wall.check_or_note(root, data["id"], config))
    if agent == "cleaner":
        sp = os.path.join(root, XV_DIR, "standards.md")
        now_text = open(sp).read() if os.path.exists(sp) else None
        checks["standards_touched"] = now_text != pre.get("standards")
        head = git(["rev-parse", "HEAD"], root).strip()
        checks["committed"] = head != head_before
        if head != head_before and not data.get("cleaner_commit"):
            data["cleaner_commit"] = head
    if agent == "guardian":
        packet = os.path.join(root, XV_DIR, "slices", f"{data['id']}.packet.md")
        checks["packet"] = os.path.exists(packet)
        if os.path.exists(packet):
            import packet as packetlib
            try:
                checks.update(packetlib.packet_checks(packet, data, root))
            except XVError as e:
                checks["packet_problems"] = [str(e)]
            append_cleaner_proposals(packet, data)
            record.guardian_facts(root, data, checks, packet)
        else:
            data["shape_change"] = data["pitch_contradiction"] = "yes"
            checks["missing_packet"] = True
    return checks


POINT = re.compile(r"^\s*(\d+)\.\s+(\S.*)$", re.M)


def norm(text):
    return " ".join(re.sub(r"[`*_]", "", str(text)).lower().split())


def with_kept_covers(report, kept):
    """The coverage from the earlier passes stays: add each kept item the report does not name again."""
    covers = report.get("covers")
    if not kept or not isinstance(covers, list):
        return report
    named = {norm(c.get("item")) for c in covers if isinstance(c, dict) and c.get("item")}
    return dict(report, covers=covers + [c for c in kept if norm(c["item"]) not in named])


def missed_points(root, data, report):
    """Numbered lines of the scenario and its amendments that no `covers` or `not_covered` item names."""
    body = record.load(root, data["id"])[2]
    at = body.find("## Scenario")
    if at < 0:
        return []
    end = body.find("\n## May ignore")
    items = [norm(i.get("item")) for key in ("covers", "not_covered")
             for i in report.get(key) or [] if isinstance(i, dict) and i.get("item")]
    numbers = {m.group(1) for i in items if (m := re.match(r"(\d+)\.?(?:\s|$)", i))}
    missed = []
    region = body[at:end if end > at else len(body)]
    amended = region.find("### Amended")
    for m in POINT.finditer(region):
        num, text = m.groups()
        if data.get("kind") == "refactor" and not 0 <= amended <= m.start():
            continue  # a refactor slice's own points have no red; only an amendment's points need one
        t = norm(text)
        by_number = num in numbers and not 0 <= amended <= m.start()
        if not by_number and not any(t in i or (len(i) >= 4 and i in t) or t[:40] in i for i in items):
            missed.append(f"{num}. {text.strip()}")
    return missed


def unreadable_input(root, data, report):
    """What the coverage check cannot read: it never passes on that."""
    out = []
    if "## Scenario" not in record.load(root, data["id"])[2]:
        out.append("The record has no `## Scenario` heading, so the check cannot read the scenario.")
    covers, not_covered = report.get("covers"), report.get("not_covered")
    if not isinstance(not_covered, list) or not all(isinstance(n, dict) for n in not_covered):
        out.append("The report's `not_covered` is missing or is not a list of items.")
    if not isinstance(covers, list) or not covers or not all(
            isinstance(c, dict) and c.get("item") and covers_names(c.get("test")) for c in covers):
        out.append("The report's `covers` is missing, empty, or has an item that names no test.")
    else:
        files = red_file_texts(root, data.get("red") or {})
        removed = [COVERS_SEPARATOR.split(m["assertion"].split(";")[0])[-1].strip() for m in data.get("moved_tests") or []
                   if isinstance(m, dict) and m.get("by") == "cleaner" and m.get("slice_only")
                   and isinstance(m.get("assertion"), str)]
        for c in covers:
            for name in covers_names(c["test"]):
                if not covers_name_found(name, files) and COVERS_SEPARATOR.split(name)[-1].strip() not in removed:
                    out.append(f"The report says `{name}` covers {c['item']}, and no red file has that test.")
    return out


def covers_names(test):
    """The names a covers item's test holds: one name, a list, or a string joined with , or ;."""
    parts = test if isinstance(test, list) else re.split(r"[,;]", test) if isinstance(test, str) else []
    names = [p.strip() if isinstance(p, str) else "" for p in parts]
    return names if names and all(names) else []


def scenario_red_gaps(root, data, red):
    """The flags and `xv` commands in backticks in the scenario and its amendments that no red file has."""
    import wall
    body = record.load(root, data["id"])[2]
    at = body.find("## Scenario")
    end = body.find("\n## May ignore")
    if at < 0:
        return []
    gaps = wall.red_gaps(body[at:end if end > at else len(body)], list(red_file_texts(root, red).values()),
                         exists=lambda words: xv_help_at_base(root, data.get("base"), words) is not None,
                         has_flag=lambda words, flag: xv_flag_at_base(root, data.get("base"), words, flag))
    accepted = " ".join(s.get("question") or "" for s in data.get("stops") or []
                        if s.get("order") == "red_misses_scenario" and s.get("answer") and not s.get("sent_back"))
    return [g for g in gaps if f"`{g}`" not in accepted]


_BASE_XV = {}


def base_xv_dir(root, base):
    """A directory holding the slice base's `bin` and `scripts`; the installed xv's own when the base has none."""
    if (root, base) not in _BASE_XV:
        tmp = None
        if base:
            try:
                tar = subprocess.run(["git", "archive", base, "bin", "scripts"], cwd=root,
                                     capture_output=True, check=True).stdout
                tmp = tempfile.TemporaryDirectory(prefix="xv-base-")  # removed when the process ends
                with tarfile.open(fileobj=io.BytesIO(tar)) as t:
                    t.extractall(tmp.name)
                if not os.path.isfile(os.path.join(tmp.name, "bin", "xv")):
                    tmp = None
            except (OSError, subprocess.CalledProcessError, tarfile.TarError):
                tmp = None
        _BASE_XV[(root, base)] = (tmp, tmp.name if tmp else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return _BASE_XV[(root, base)][1]


def xv_help_at_base(root, base, words):
    """The `--help` text of `xv <words>` at the slice's base, or None when it is not a command there."""
    home = base_xv_dir(root, base)
    try:
        p = subprocess.run([sys.executable, os.path.join(home, "bin", "xv"), *words, "--help"], cwd=home,
                           capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def xv_flag_at_base(root, base, words, flag):
    help_text = xv_help_at_base(root, base, words)
    return bool(help_text and re.search(r"(?<![\w-])" + re.escape(flag) + r"(?![\w-])", help_text))


def red_file_texts(root, red):
    texts = {}
    for f in red.get("files") or []:
        try:
            with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                texts[f] = fh.read()
        except OSError:
            pass
    return texts


def append_cleaner_proposals(packet, data):
    """The cleaner's candidate standards and shape proposals ride in the packet,
    where the person who set the work going can accept a standard."""
    cands, shapes = [], []
    for rep in (data.get("checks") or {}).get("reports", []):
        if rep.get("agent") == "cleaner":
            cands += rep.get("candidate_standards") or []
            shapes += rep.get("shape_proposals") or []
    if not cands and not shapes:
        return
    lines = ["", "## From the cleaner", ""]
    for i, c in enumerate(cands, 1):
        lines.append(f"- Candidate standard {i}: {c}. To accept: `xv retro standard {data['id']} {i} --by <name>`.")
    for s in shapes:
        lines.append(f"- Shape proposal, for people: {s}")
    with open(packet, "a") as f:
        f.write("\n".join(lines) + "\n")


def commit_step(agent, root, slice_id, checks):
    messages = {
        "forecaster": "forecast", "scenario": "red", "maker": "make it work",
        "cleaner": "record the cleaner's pass", "guardian": "packet",
    }
    commit(root, f"xv({slice_id}): {messages[agent]}")


# The wall and the boundary picture arrive with their own scripts; until a repo
# has them, these steps are no-ops so the loop still runs and a person reads.

def red_run(root, data, red, config):
    """Run the red command. Once the maker has run, run it on the code from before the maker's first change."""
    commit = data.get("pre_maker_commit") or (data.get("wall_baseline") or {}).get("commit")
    if not commit or not any(s.get("step") == "maker" for s in data.get("spend") or []):
        return shell(red["command"], root, 600)
    tmp = tempfile.mkdtemp(prefix="xv-red-")
    try:
        subprocess.run(["git", "worktree", "add", "--detach", tmp, commit], cwd=root, capture_output=True, check=True)
        for f in red.get("files") or []:
            src = os.path.join(root, f)
            if os.path.isfile(src):
                os.makedirs(os.path.dirname(os.path.join(tmp, f)), exist_ok=True)
                shutil.copyfile(src, os.path.join(tmp, f))
        failed = run_worktree_command(worktrees_config(config).get("setup"), tmp, config)
        if failed:
            return None, f"the worktree setup `{failed[0]}` failed ({failed[1]}); its last output:\n{failed[2]}"
        return shell(red["command"], tmp, 600)
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", tmp], cwd=root, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


def old_red_changed(root, data, red, paths):
    """Test files that existed at the base and lost or changed old test code."""
    try:
        import wall
    except ImportError:
        return None
    moved = {m.get("file") for m in data.get("moved_tests") or []}
    return wall.old_red_changed(root, data["base"], red.get("files") or [], moved, paths) if data.get("base") else None


def wall_baseline(root, data, config):
    try:
        import wall
    except ImportError:
        return None
    return wall.baseline(root, data["id"], config)


def boundary(root, data):
    try:
        import boundary as b
    except ImportError:
        return
    b.write_for_slice(root, data)


# ---------------------------------------------------------------- run, close

def cmd_run(a):
    path = record_path(repo_root(), a.id)
    while True:
        data, _ = record.load(slice_root(path), a.id)[1:]
        nxt = data.get("next")
        if nxt in (None, "none") or data.get("status") == "closed":
            print(json.dumps({"slice": a.id, "status": data.get("status"), "stop": None}))
            sys.exit(0)
        if nxt == "close":
            open_stops = [s for s in data["stops"] if s.get("answer") is None]
            if open_stops:
                print(json.dumps({"slice": a.id, "stop": open_stops[-1]}, indent=2))
                sys.exit(EXIT_STOP)
            sys.exit(close(a.id))
        open_stops = [s for s in data["stops"] if s.get("answer") is None]
        if open_stops:
            print(json.dumps({"slice": a.id, "stop": open_stops[-1], "note": "an earlier stop is unanswered"}, indent=2))
            sys.exit(EXIT_STOP)
        if nxt == "prototype":
            import prototypes
            sys.exit(prototypes.run(a.id))
        code, v = step(nxt, a.id)
        if code != 0:
            print(json.dumps(v, indent=2))
            sys.exit(code)


def close(slice_id, why=None, shape=None):
    root = slice_root(record_path(repo_root(), slice_id))
    config = load_config(root)
    path, data, body = record.load(root, slice_id)
    open_stops = [s for s in data["stops"] if s.get("answer") is None and s["order"] != "ready_to_merge"]
    if open_stops:
        raise XVError(f"an open stop needs an answer first: {open_stops[-1]['question']}")
    for s in data["stops"]:
        if s.get("answer") is None and s["order"] == "ready_to_merge":
            raise XVError("the merge is the person's: answer the ready stop "
                          f"(`xv record answer {slice_id} --by <name> --answer merge`) and then close")
    if why:  # the forecaster ran in the session and gave its line, or a person did
        report, s = {"why": why, "shape_actual": shape}, None
    else:
        text = promptlib.build("forecaster", slice_id, root=root, close=True)
        argv = agentcli.argv_for(config, "forecaster")
        result = agentcli.run(argv, text, root, os.path.join(runs_dir(root, slice_id), "close-forecaster.out"))
        data, body = record.load(root, slice_id)[1:]
        s = spendlib.from_run(result)
        s.update(step="close", at=now(), exit=result["code"])
        body, report = record.apply_report(data, body, "forecaster", result["stdout"])
        record.save(path, data, body)
    why = (report or {}).get("why") or "the forecaster gave no reason"
    p = subprocess.run([sys.executable, os.path.join(HERE, "record.py"), "guide-append", slice_id,
                        "--why", why, "--shape", (report or {}).get("shape_actual") or ""],
                       cwd=root, capture_output=True, text=True)
    data, body = record.load(root, slice_id)[1:]
    if s:
        data["spend"].append(s)  # after the guide row: the close itself is not the slice's work
    data["status"], data["next"] = "closed", "none"
    import boundary as b
    data["modules_touched"] = b.change(root, data.get("base") or "HEAD", config)["touched"]
    maker_runs = sum(1 for row in data["spend"] if row.get("step") == "maker")
    stop_sendbacks = sum(1 for stop in data["stops"]
                         if stop.get("answer") == "sent back to the maker"
                         or stop.get("sent_back_to") == "maker")
    data["maker_sendbacks"] = max(maker_runs - 1, stop_sendbacks, 0)
    body = record.log_line(body, "watch", "closed" + ("" if p.returncode == 0 else f"; guide: {p.stderr.strip()}"))
    record.save(path, data, body)
    commit(root, f"xv({slice_id}): close")
    # the slice's red ref and any scenario checkout nobody reported on go with it: a new slice with the same
    # id and base would otherwise start its first pass from this slice's red
    git(["update-ref", "-d", red_ref(data)], root, check=False)
    drop_session_scratch(root, slice_id)
    failed = run_worktree_command(worktrees_config(config).get("teardown"), root, config)
    if failed:
        command, code, last = failed
        print(f"xv: worktree teardown `{command}` failed ({code}): {last}", file=sys.stderr)
    if data.get("trial"):
        from xvlib import main_root
        if main_root(root) != root:
            bring_back(root, main_root(root), slice_id)
    out = {"slice": slice_id, "status": "closed", "stop": None, "guide": p.stdout.strip() or p.stderr.strip(),
           "next": f"merge {data['branch']} when you are ready; the watch does not merge"}
    try:
        import retro
        why = retro.due(root)["slices"].get(slice_id)
        if why:
            out["retro_due"] = f"{'; '.join(why)}. Run `xv retro run {slice_id}` (the xv-retro skill)."
    except Exception:
        pass
    print(json.dumps(out, indent=2))
    return 0


# ---------------------------------------------------------------- guard (CI)

def cmd_guard(a):
    """The guardian on a pull request. With a slice record in the change, it is that
    slice's guardian step. Without one, it reviews the diff against the base."""
    root = repo_root()
    config = load_config(root)
    changed = git(["diff", "--name-only", f"{a.base}...HEAD"], root).split()
    slices = [os.path.basename(f)[:-3] for f in changed if is_record_path(f)]
    if len(slices) == 1:
        os.environ["XV_NO_COMMIT"] = "1"
        code, v = step("guardian", slices[0], review_again=True)
        print(json.dumps(v, indent=2))
        path = record_path(root, slices[0])
        packet = os.path.join(slice_root(path), XV_DIR, "slices", f"{slices[0]}.packet.md")
        if a.out and os.path.exists(packet):
            shutil.copy(packet, a.out)
        sys.exit(code)
    rel = os.path.join(XV_DIR, "slices", "pr-packet.md")
    os.makedirs(os.path.join(root, XV_DIR, "slices"), exist_ok=True)
    try:
        import boundary as b
        bres = b.change(root, a.base, config)
        with open(os.path.join(root, XV_DIR, "slices", "pr-boundary.md"), "w") as f:
            f.write(b.render_change(bres))
    except ImportError:
        pass
    extra = [f"No slice record: review the pull request's diff, `git diff {a.base}...HEAD`.",
             f"Packet template: `{os.path.join(promptlib.SKILLS, 'guardian', 'packet.md')}`. "
             f"Write the packet to `{rel}`.",
             f"Boundary picture: `{XV_DIR}/slices/pr-boundary.md`.",
             f"Test files changed since the base: `xv wall check --base {a.base} --json`."]
    text = promptlib.brief("guardian") + "\n" + promptlib.pointers("guardian", root, config, None, extra)
    result = agentcli.run(agentcli.argv_for(config, "guardian"), text, root, None,
                          int(config.get("step_timeout") or 3600))
    full = os.path.join(root, rel)
    data = {"id": "pull-request", "kind": "feature", "moved_tests": [], "checks": {"reports": []}}
    if os.path.exists(full):
        import packet as packetlib
        packetlib.fix(full)
        pdata, _ = record.read_doc(full)
        for field in packetlib.ALLOWED:
            data[field] = pdata.get(field) if pdata.get(field) in packetlib.YES_NO else "yes"
        data["checks"]["guardian"] = {"picture_change": pdata.get("picture_change")}
        if pdata.get("moved_tests"):
            data["moved_tests"] = [{"file": "see the packet"}] * int(pdata.get("moved_tests") or 0)
        if a.out:
            shutil.copy(full, a.out)
    else:
        data["shape_change"] = data["pitch_contradiction"] = "yes"
        if a.out:
            with open(a.out, "w") as f:
                f.write("The guardian wrote no packet. The change waits for two people.\n")
    data["checks"]["reports"].append({"agent": "guardian", "status": "done"})
    v = orders.verdict(data, "guardian", config)
    v["exit"] = result["code"]
    print(json.dumps(v, indent=2))
    sys.exit(EXIT_STOP if v["stop"] else 0)


# ---------------------------------------------------------------- init

# marker, command, test paths, folders that mean the runner has tests here (none: always).
# Backend runners come first: when several qualify, the first one is tests.command.
DETECT = [
    ("Gemfile", "bundle exec rake test", ["test/**", "spec/**"], ("spec", "test")),
    ("go.mod", "go test ./...", ["**/*_test.go"], ()),
    ("Cargo.toml", "cargo test", ["tests/**"], ("tests",)),
    ("pyproject.toml", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"], ()),
    ("setup.py", "python3 -m pytest -q", ["tests/**", "test/**", "**/test_*.py", "**/*_test.py"], ()),
    ("package.json", "npm test", ["tests/**", "test/**", "**/*.test.*", "**/*.spec.*", "e2e/**"],
     ("tests", "test", "e2e")),
]


def detect_tests(root):
    """Check every marker, not just the first: a Rails app has a Gemfile and a package.json.

    Returns (command, paths, runners). The paths are the union over every runner found.
    The command is the first runner, backend first, whose test folder exists; if none
    has one, the first runner found. `runners` lists each one found, for the person to choose.
    """
    # a src layout needs src on the path for the tests to import the package
    src = "PYTHONPATH=src " if os.path.isdir(os.path.join(root, "src")) else ""
    runners, paths, has_dir = [], [], []
    for marker, command, marker_paths, dirs in DETECT:
        if not os.path.exists(os.path.join(root, marker)):
            continue
        if marker == "Gemfile" and os.path.isdir(os.path.join(root, "spec")):
            command = "bundle exec rspec"
        if marker in ("pyproject.toml", "setup.py") and shutil.which("pytest") is None:
            command = "python3 -m unittest discover -s tests -t ."
        if command.startswith("python3"):
            command = src + command
        if any(r["command"] == command for r in runners):
            continue
        runners.append({"marker": marker, "command": command, "paths": marker_paths})
        has_dir.append(not dirs or any(os.path.isdir(os.path.join(root, d)) for d in dirs))
        paths += [x for x in marker_paths if x not in paths]
    if runners:
        pick = runners[has_dir.index(True)] if True in has_dir else runners[0]
        return pick["command"], paths, runners
    if os.path.isdir(os.path.join(root, "tests")):
        return src + "python3 -m unittest discover -s tests -t .", ["tests/**"], []
    return "", ["tests/**", "test/**", "spec/**"], []


def source_roots(root, test_paths):
    """One top-level folder holding all the code is the root, so its files become the modules."""
    import boundary as b
    cfg = {"source": {"roots": ["."], "exclude": ["node_modules/**", "vendor/**", ".git/**", ".xv/**"]},
           "tests": {"paths": test_paths}}
    from xvlib import tracked_files
    files = b.source_files(tracked_files(root), cfg)
    if os.path.isdir(os.path.join(root, "app")) and os.path.exists(os.path.join(root, "config", "routes.rb")):
        # a Rails layout: app is the code, lib and app/javascript are code beside it
        return ["app"] + [d for d in ("lib", "app/javascript") if os.path.isdir(os.path.join(root, d))]
    tops = {f.split("/")[0] for f in files if "/" in f}
    if len(tops) == 1 and all("/" in f for f in files):
        return [tops.pop()]
    if os.path.isdir(os.path.join(root, "src")) and any(f.startswith("src/") for f in files):
        return ["src"] + sorted(t for t in tops if t != "src" and t in ("lib", "app"))
    return ["."]


def repo_identity(root):
    """The repo's name, GitHub description, and whether it is private (None: unknown). Read-only."""
    try:
        p = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner,description,isPrivate"], cwd=root,
                           capture_output=True, text=True, timeout=20)
        if p.returncode == 0:
            d = json.loads(p.stdout)
            return d.get("nameWithOwner") or "", d.get("description") or "", d.get("isPrivate")
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    url = git(["config", "--get", "remote.origin.url"], root, check=False).strip()
    m = __import__("re").search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return (m.group(1) if m else os.path.basename(root)), "", None


def adopt_trial_repo(root):
    """Ending a trial whose .xv/ is its own repo: move that repo out of the way, never delete it.

    With no remote it is the only copy of the trial's history, so it goes to
    <git common dir>/xv-trial.git, where `git --git-dir` can still read it.
    """
    inner = os.path.join(root, XV_DIR, ".git")
    if not os.path.exists(inner):
        return None
    if git(["status", "--porcelain"], os.path.join(root, XV_DIR)).strip():
        raise XVError(f"{XV_DIR}/ is its own git repo and has changes not committed there. "
                      f"Commit them (git -C {XV_DIR} commit -am ...) or discard them, then adopt again.")
    common = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], root).strip()
    dest = os.path.join(common, "xv-trial.git")
    if os.path.exists(dest):
        raise XVError(f"{dest} already exists: an earlier trial's history is there. "
                      "Move it aside yourself; xv will not overwrite it.")
    shutil.move(inner, dest)
    origin = git(["--git-dir", dest, "config", "--get", "remote.origin.url"], root, check=False).strip()
    return {"moved_to": dest, "origin": origin or None}


FIXTURE_NAMES = ("fixture", "fixtures", "examples", "setups")
CODE_EXTS = (".py", ".js", ".ts", ".jsx", ".tsx", ".rb", ".go", ".rs", ".java", ".sh", ".php", ".c", ".cc", ".cpp", ".cs")


def fixture_folders(root, exclude):
    from xvlib import tracked_files
    found = set()
    for path in tracked_files(root):
        if not path.endswith(CODE_EXTS) or path.split("/")[0] == XV_DIR or match_any(path, exclude):
            continue
        parts = path.split("/")[:-1]
        for i, part in enumerate(parts):
            if part.lower() in FIXTURE_NAMES:
                found.add("/".join(parts[:i + 1]))
    return sorted(found)


def try_test_command(root, tests):
    command = (tests or {}).get("command") or ""
    if not command:
        return None
    timeout = int(tests.get("timeout") or 900)
    code, text = shell(command, root, timeout)
    if code == 124 and text.endswith(f"timed out after {timeout}s"):
        return {"result": "timed out", "after_s": timeout}
    if code == 0:
        return {"result": "passed"}
    return {"result": "failed", "exit": code, "tail": text.strip().splitlines()[-15:]}


READ_ONLY_TOOLS = ["cat", "head", "tail", "ls", "grep", "git diff", "git log", "git status", "git show",
                   "rg", "wc", "sed -n", "diff", "git ls-files", "git grep", "git rev-parse"]
MAKER_TOOLS = ["git rm", "git mv", "xv record move"]
GUARDIAN_TOOLS = ["xv wall diff", "xv boundary", "xv packet lint"]


def test_rules(command):
    """One rule per part of the test command, each cut before its arguments, so a single file runs too."""
    rules = []
    for part in re.split(r"\s*(?:&&|\|\||;)\s*", command or ""):
        words = part.split()
        lead = []
        while words and re.match(r"\w+=", words[0]):
            lead.append(words.pop(0))
        keep = []
        for w in words:
            is_arg = w.startswith("-") and w != "-m"
            if keep and (is_arg or "/" in w or w in (".", "discover")):
                break
            keep.append(w)
        for rule in (" ".join(lead + keep), " ".join(keep)) if keep else ():
            if rule not in rules:
                rules.append(rule)
    return rules


def allow_lists(text, command):
    """Give each Claude Code agent line a starter --allowedTools list; the forecaster's is read-only."""
    test = test_rules(command)
    seats = {"default": READ_ONLY_TOOLS + MAKER_TOOLS + test, "forecaster": READ_ONLY_TOOLS,
             "guardian": READ_ONLY_TOOLS + GUARDIAN_TOOLS + test}
    out = []
    for line in text.split("\n"):
        seat = line.split(":", 1)[0].strip()
        if seat in seats and line.startswith(f'  {seat}: ["claude"') and "--allowedTools" not in line:
            tools = ",".join(f"Bash({t}:*)" for t in seats[seat])
            line = line.replace('"acceptEdits", ', f'"acceptEdits", "--allowedTools", {json.dumps(tools)}, ', 1)
        out.append(line)
    return "\n".join(out)


def cmd_init(a):
    root = repo_root()
    if a.repo and not a.trial:
        raise XVError("--repo goes with --trial: it makes .xv/ its own git repo while it is kept out of this one.")
    if a.adopt:
        moved = adopt_trial_repo(root)
        path = exclude_path(root)
        lines = open(path).read().splitlines() if os.path.exists(path) else []
        kept = [line for line in lines if line.strip() not in (f"{XV_DIR}/", f"/{XV_DIR}/", XV_DIR, f"/{XV_DIR}")]
        with open(path, "w") as f:
            f.write("\n".join(kept) + ("\n" if kept else ""))
        still = is_trial(root)
        out = {"trial": still, "next": "a .gitignore still lists .xv/; remove it there" if still
               else "commit .xv/; the project layer is now part of the repo"}
        if moved:
            out["trial_repo"] = moved
        print(json.dumps(out, indent=2))
        return
    if a.trial:
        path = exclude_path(root)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        text = open(path).read() if os.path.exists(path) else ""
        if f"/{XV_DIR}/" not in text.split():
            with open(path, "a") as f:
                f.write(("" if text.endswith("\n") or not text else "\n") + f"/{XV_DIR}/\n")
    src = os.path.join(XV_HOME, "defaults")
    dst = os.path.join(root, XV_DIR)
    written, kept = [], []
    for dirpath, _, files in os.walk(src):
        for name in files:
            s = os.path.join(dirpath, name)
            rel = os.path.relpath(s, src)
            d = os.path.join(dst, rel)
            if os.path.exists(d):
                kept.append(rel)
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy(s, d)
            written.append(rel)
    cfg = os.path.join(dst, "config.yml")
    runners = []
    if "config.yml" in written:
        command, paths, runners = detect_tests(root)
        name, description, private = repo_identity(root)
        text = open(cfg).read()
        text = text.replace('  command: ""', f"  command: {json.dumps(command)}", 1)
        text = text.replace('paths: ["tests/**"]', f"paths: {json.dumps(paths)}")
        text = text.replace('  roots: ["."]', f"  roots: {json.dumps(source_roots(root, paths))}", 1)
        text = text.replace('  name: ""', f"  name: {json.dumps(name)}", 1)
        text = text.replace('  description: ""', f"  description: {json.dumps(description)}", 1)
        text = allow_lists(text, command)
        if private:
            text = text.replace("  include_name: true", "  include_name: false", 1)
        open(cfg, "w").write(text)
    try:
        import boundary as b
        with open(os.path.join(dst, "boundary-all.md"), "w") as f:
            f.write(b.render_all(root))
        written.append("boundary-all.md")
    except ImportError:
        pass
    config = load_config(root)
    tests = config.get("tests") or {}
    out = {"written": written, "kept": kept, "tests": tests}
    if a.no_try:
        out["test_run_skipped"] = "--no-try: the test command was not run; a missing test_run does not mean no command was guessed"
    else:
        out["test_run"] = try_test_command(root, tests)
    bpath = os.path.join(dst, "boundary-all.md")
    if os.path.exists(bpath):
        out["modules"] = len([l for l in open(bpath).read().splitlines() if l.startswith("- ")])
    out["fixture_folders"] = fixture_folders(root, (config.get("source") or {}).get("exclude") or [])
    if len(runners) > 1:
        out["runners"] = runners
    if a.repo:
        if not os.path.exists(os.path.join(dst, ".git")):
            git(["init", "-q"], dst)
        out["next"] = (f"{XV_DIR}/ is now its own git repo, with no commit yet. Commit inside it "
                       f"(git -C {XV_DIR} add -A && git -C {XV_DIR} commit -m ...). To let teammates opt in, "
                       f"push it to a private remote. `xv init --adopt` moves it aside later.")
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog="xv", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("slice")
    ss = s.add_subparsers(dest="sub", required=True)
    n = ss.add_parser("new")
    n.add_argument("id")
    n.add_argument("--by", required=True)
    n.add_argument("--title")
    n.add_argument("--kind", choices=["feature", "defect", "prototype", "refactor"], default="feature")
    n.add_argument("--scenario")
    n.add_argument("--scenario-file")
    n.add_argument("--expect-moves", help="the test changes the person expects: imports, renames, or both")
    n.add_argument("--rename", action="append", help="Old=New, a name this slice renames; one flag per pair")
    n.add_argument("--ignore", action="append", help="what this slice may ignore; repeat the flag for more")
    n.add_argument("--recording")
    n.add_argument("--branch")
    n.add_argument("--base", help="the ref the slice branch starts from (default: worktrees.base, then origin/HEAD, then HEAD)")
    n.add_argument("--from", dest="from_ref", help="a build that already exists: the slice branch starts at this ref")
    n.add_argument("--share-build", action="store_true",
                   help="name the build to the scenario agent as a reference (needs --from)")
    n.add_argument("--axis", help="for a prototype slice: the one axis the three differ on")
    n.set_defaults(fn=cmd_slice_new)
    m = ss.add_parser("amend")
    m.add_argument("id")
    m.add_argument("--by", required=True)
    m.add_argument("--scenario-file", required=True)
    m.set_defaults(fn=cmd_slice_amend)
    rb = ss.add_parser("rebase", help="bring a slice up to date with its base")
    rb.add_argument("id")
    rb.add_argument("--onto", help="the ref to rebase onto (default: worktrees.base, then origin/HEAD, then HEAD)")
    rb.add_argument("--continue", dest="cont", action="store_true",
                    help="finish a rebase that stopped, once its files are resolved")
    rb.add_argument("--abort", action="store_true", help="give up a rebase that stopped; branch and record go back")
    rb.set_defaults(fn=cmd_slice_rebase)

    s = sub.add_parser("step")
    s.add_argument("agent")
    s.add_argument("id", nargs="?")
    s.add_argument("--init", action="store_true")
    s.set_defaults(fn=cmd_step)

    s = sub.add_parser("run")
    s.add_argument("id")
    s.set_defaults(fn=cmd_run)

    s = sub.add_parser("land-scenario", help="what `xv record report <id> scenario` runs after a session-mode "
                                             "scenario step on a slice from a build (the report is on stdin)")
    s.add_argument("id")
    s.set_defaults(fn=lambda a: land_session_scenario(
        slice_root(record_path(repo_root(), a.id)), a.id, json.loads(sys.stdin.read() or "{}")))

    s = sub.add_parser("close")
    s.add_argument("id")
    s.add_argument("--why", help="the line on the gap, when the forecaster ran in the session")
    s.add_argument("--shape", help="the shape change that actually happened")
    s.set_defaults(fn=lambda a: sys.exit(close(a.id, a.why, a.shape)))

    s = sub.add_parser("init")
    s.add_argument("--trial", action="store_true",
                   help="keep .xv/ out of git (in .git/info/exclude), to try XV before committing to it")
    s.add_argument("--repo", action="store_true",
                   help="with --trial: make .xv/ its own git repo (no commit), so the trial keeps history")
    s.add_argument("--no-try", action="store_true",
                   help="do not run the test command to check it")
    s.add_argument("--adopt", action="store_true",
                   help="end a trial: let git see .xv/ again; a nested .xv/.git moves to <git dir>/xv-trial.git")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("guard", help="the guardian on a pull request, for CI")
    s.add_argument("--base", required=True)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_guard)

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

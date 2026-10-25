#!/usr/bin/env python3
"""Build the whole prompt for one agent on one slice: its brief, then pointers.

The brief is the skill's SKILL.md body. The pointers say where the record, the
base commit, the budget and the project files are. Nothing is restated that the
agent can read itself. The same text goes to a subagent or to a CLI.

Usage: xv prompt <agent> <slice id> [--close] [--init]
"""

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xvlib import (XVError, die, load_config, read_doc, record_path,  # noqa: E402
                   repo_root, slice_root, split_front_matter)

HERE = os.path.dirname(os.path.abspath(__file__))
XV_HOME = os.path.dirname(HERE)
SKILLS = os.path.join(XV_HOME, "skills")

AGENTS = {
    "forecaster": "forecaster/SKILL.md",
    "scenario": "scenario/SKILL.md",
    "maker": "maker/SKILL.md",
    "prototype": "maker/prototype.md",
    "cleaner": "cleaner/SKILL.md",
    "guardian": "guardian/SKILL.md",
    "listener": "listener/SKILL.md",
    "outsider": "xv-init/outsider-read.md",
    "retro": "xv-retro/retro-brief.md",
}


def brief(agent):
    if agent not in AGENTS:
        raise XVError(f"no brief for {agent!r}; one of {sorted(AGENTS)}")
    path = os.path.join(SKILLS, AGENTS[agent])
    with open(path, encoding="utf-8") as f:
        _, body = split_front_matter(f.read())
    return body.strip()


def agent_key(config, agent):
    """(harness, model) for the CLI the config names for this agent."""
    from agentcli import argv_for, harness_of, model_of
    argv = argv_for(config, agent)
    return harness_of(argv), model_of(argv)


def pointers(agent, root, config, data=None, extra=None):
    lines = ["", "---", "", "## This run", ""]
    lines.append(f"- Repository checkout: `{root}`. Work only inside it.")
    if data:
        lines.append(f"- Slice record: `.xv/slices/{data['id']}.md`. Read it first. Do not edit it; "
                     "your report block is how you write to it.")
        if data.get("base"):
            lines.append(f"- Base commit: `{data['base']}`. The slice's diff is `git diff {data['base']}..HEAD`"
                         " plus any uncommitted changes.")
        if data.get("red"):
            red = data["red"]
            lines.append(f"- The red: files {', '.join(red.get('files', []))}; command `{red.get('command', '')}`.")
        if data.get("budget") and agent == "maker":
            b = data["budget"]
            parts = [f"{k} {b[k]}" for k in ("tokens", "usd", "turns") if b.get(k)]
            lines.append(f"- Budget: {', '.join(parts)}. Stop when it is spent.")
    tests = config.get("tests", {})
    if tests.get("command"):
        lines.append(f"- Whole suite: `{tests['command']}`.")
    if tests.get("paths"):
        lines.append(f"- Test paths (the wall): {', '.join(tests['paths'])}.")
    if agent == "forecaster":
        keys = [f"{a} on {'/'.join(agent_key(config, a))}"
                for a in ("scenario", "maker", "cleaner", "guardian")]
        lines.append(f"- Agents on this slice: {'; '.join(keys)}.")
    xv = shutil.which("xv") or os.path.join(XV_HOME, "bin", "xv")
    lines.append(f"- The `xv` command: `{xv}`.")
    for line in extra or []:
        lines.append(f"- {line}")
    lines.append("- End your final message with the `xv-report` block your brief describes. "
                 "Nothing after it.")
    return "\n".join(lines)


def new_guide_rows(root, slice_id):
    """Estimation rows no earlier packet has listed: they ride in the next packet."""
    import glob
    from record import guide_rows
    path = os.path.join(root, ".xv", "estimation.md")
    if not os.path.exists(path):
        return []
    listed = ""
    for p in glob.glob(os.path.join(root, ".xv", "slices", "*.packet.md")):
        if os.path.basename(p) != f"{slice_id}.packet.md":
            listed += open(p, encoding="utf-8", errors="replace").read()
    return [r for r in guide_rows(open(path).read()) if r.split("|")[1].strip() not in listed]


def answer_section(data):
    """The latest answered stop, word for word, so the agent need not dig it out of the log."""
    answered = [s for s in (data or {}).get("stops") or [] if s.get("answer")]
    if not answered:
        return ""
    st = answered[-1]
    who = ", ".join(st.get("answered_by") or [])
    return (f"\n## The person's answer\n\n{who} answered the stop `{st.get('order')}` "
            f"({st.get('question', '')}):\n\n{st['answer']}\n")


def build(agent, slice_id=None, root=None, close=False, init=False, extra=None):
    root = root or repo_root()
    config = load_config(root)
    data = None
    if slice_id:
        path = record_path(root, slice_id)
        root = slice_root(path)
        data, _ = read_doc(path)
    extra = list(extra or [])
    if close:
        extra.insert(0, "Mode: close. The slice is done; write the one line on the gap.")
    if agent == "guardian" and data:
        extra.insert(0, f"Packet template: `{os.path.join(SKILLS, 'guardian', 'packet.md')}`. "
                        f"Write the packet to `.xv/slices/{data['id']}.packet.md`.")
        bpath = os.path.join(root, ".xv", "slices", f"{data['id']}.boundary.md")
        if os.path.exists(bpath):
            extra.insert(1, f"Boundary picture: `.xv/slices/{data['id']}.boundary.md`.")
        rows = new_guide_rows(root, data["id"])
        if rows:
            extra.append("New rows in `.xv/estimation.md` since the base, appended by the forecaster without "
                         "acceptance; list them under Raw data so a person can revert one: "
                         + "; ".join(r.split("|")[1].strip() for r in rows) + ".")
    if agent == "outsider" or init:
        bpath = os.path.join(root, ".xv", "boundary-all.md")
        if os.path.exists(bpath):
            extra.insert(0, f"Boundary output: `.xv/boundary-all.md`.")
    return brief(agent) + "\n" + answer_section(data) + pointers(agent, root, config, data, extra) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(prog="xv prompt", description=__doc__.split("\n")[0])
    p.add_argument("agent")
    p.add_argument("id", nargs="?")
    p.add_argument("--close", action="store_true")
    p.add_argument("--init", action="store_true")
    a = p.parse_args(argv)
    try:
        sys.stdout.write(build(a.agent, a.id, close=a.close, init=a.init))
    except XVError as e:
        die(str(e), 2)


if __name__ == "__main__":
    main()

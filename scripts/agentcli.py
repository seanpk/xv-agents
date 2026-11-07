"""Run one agent CLI on one prompt, headless, and capture what it did.

The CLI for each agent comes from `.xv/config.yml` under `agents:`, as a list of
arguments with `{prompt}` where the prompt text goes. Known harnesses get their
budget caps added: Claude's `--max-budget-usd` and `--max-turns` in print mode.
Others have no cap, and the watch's spend check after the step stands in for it.
"""

import json
import os
import subprocess
import time

from xvlib import XVError

KNOWN = ("claude", "opencode", "codex", "grok")


class RanError(XVError):
    """The agent ran, and then something failed. `result` keeps what it did, so its spend is not lost."""

    def __init__(self, message, result):
        super().__init__(message)
        self.result = result


def gone(cwd):
    """The error for a working folder that is not there: never "agent CLI not found"."""
    return XVError(f"the working folder is gone: {cwd}")


def argv_for(config, agent):
    agents = config.get("agents") or {}
    argv = agents.get(agent) or agents.get("default")
    if argv == "session" or argv == ["session"]:
        raise XVError(f"the {agent} is set to run in the person's session: give a subagent the text of "
                      f"`xv prompt {agent} <id>` and nothing else")
    if isinstance(argv, str):
        argv = argv.split()
    if not argv:
        raise XVError(f"no agent CLI for {agent!r} in .xv/config.yml (agents.{agent} or agents.default)")
    return list(argv)


def harness_of(argv):
    name = os.path.basename(argv[0])
    return name if name in KNOWN else name


def model_of(argv):
    for flag in ("--model", "-m"):
        if flag in argv:
            i = argv.index(flag)
            if i + 1 < len(argv):
                model = argv[i + 1]
                return model.split("/", 1)[1] if model.startswith("ollama/") else model
    return "default"


def with_caps(argv, budget, spent_usd=0, spent_turns=0):
    """Add the harness's own budget cap where it has one: the dollars and turns left on
    Claude Code, the turns left on Grok. Elsewhere the watch's check after the step is the cap."""
    h = harness_of(argv)
    if not budget or h not in ("claude", "grok"):
        return argv
    caps = []
    if h == "claude" and budget.get("usd") and "--max-budget-usd" not in argv:
        caps += ["--max-budget-usd", str(round(budget["usd"] - spent_usd, 6))]
    if budget.get("turns") and "--max-turns" not in argv:
        caps += ["--max-turns", str(budget["turns"] - spent_turns)]
    i = argv.index("{prompt}") if "{prompt}" in argv else len(argv)
    if 0 < i < len(argv) and argv[i - 1].startswith("-"):
        i -= 1  # the prompt is a flag's value (`grok -p <prompt>`): keep the pair together
    return argv[:i] + caps + argv[i:]


def run(argv, prompt, cwd, log_path=None, timeout=3600, env=None):
    """Run the CLI. Returns a dict with the output, exit code, wall clock and session id."""
    if "{prompt}" in argv:
        cmd = [prompt if a == "{prompt}" else a for a in argv]
        stdin = None
    else:
        cmd, stdin = argv, prompt
    # a CLI that reads stdin (codex exec) must see EOF, not the parent's open stdin
    extra = {"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}
    if cwd and not os.path.isdir(cwd):
        raise gone(cwd)
    start = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, env=env, **extra)
        out, err, code = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err, code = f"timed out after {timeout}s", 124
    except FileNotFoundError:
        if cwd and not os.path.isdir(cwd):  # it went between the check and the start
            raise gone(cwd)
        raise XVError(f"agent CLI not found: {cmd[0]}")
    wall = time.time() - start
    result = {"argv": [a if a != prompt else "{prompt}" for a in cmd], "stdout": out, "stderr": err,
              "code": code, "wall_s": round(wall, 1), "harness": harness_of(argv),
              "model": model_of(argv), "session": session_of(harness_of(argv), out)}
    if log_path:
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "w") as f:
                f.write(out)
            with open(log_path + ".err", "w") as f:
                f.write(err)
        except OSError as e:  # the agent has already spent: the caller keeps the result
            raise RanError(f"the agent ran, and its run log could not be written: {e}", result)
    return result


def session_of(harness, out):
    if harness == "claude":
        try:
            return json.loads(out).get("session_id")
        except (json.JSONDecodeError, AttributeError):
            return None
    if harness == "grok":
        try:
            return json.loads(out).get("sessionId")
        except (json.JSONDecodeError, AttributeError):
            return None
    if harness == "opencode":
        for line in out.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(ev, dict) and ev.get("sessionID"):
                return ev["sessionID"]
    if harness == "codex":
        for line in out.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(ev, dict) and ev.get("type") == "thread.started" and ev.get("thread_id"):
                return ev["thread_id"]
    return None

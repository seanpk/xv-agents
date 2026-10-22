#!/usr/bin/env python3
"""Run the evals: each scenario on a fresh copy of the fixture repo, with the
skill (through `xv step`, the real path) and without it (the baseline: the same
task as a person would type it, no brief), on one or more harnesses.

  python3 evals/run.py --list
  python3 evals/run.py --scenario scenario-defect --harness claude --arm skill
  python3 evals/run.py --all --harness claude opencode --arm skill baseline
  python3 evals/run.py --increment 1 --harness claude

Results go to evals/results/runs/<date>/<scenario>.<harness>.<arm>.<n>.json.
`python3 evals/report.py` turns them into a table.

The baseline follows Anthropic's skill-creator: the same prompt with and
without the skill. Each run is one sample; a single run cannot separate a
small difference from run-to-run noise, so the report shows counts, not rates.
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

EVALS = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(EVALS)
sys.path.insert(0, os.path.join(HOME, "scripts"))
sys.path.insert(0, EVALS)

import agentcli  # noqa: E402
import grade  # noqa: E402
import spend as spendlib  # noqa: E402
from xvlib import parse_scalar, read_doc  # noqa: E402

XV = os.path.join(HOME, "bin", "xv")


def load_scenarios():
    out = {}
    for name in sorted(os.listdir(os.path.join(EVALS, "scenarios"))):
        if name.endswith(".json"):
            with open(os.path.join(EVALS, "scenarios", name)) as f:
                s = json.load(f)
            out[s["name"]] = s
    return out


def load_harnesses():
    with open(os.path.join(EVALS, "harnesses.json")) as f:
        return json.load(f)


def sh(cmd, cwd, check=True, env=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)}: {p.stderr.strip() or p.stdout.strip()}")
    return p


def write_config_agents(repo, argv_by_agent):
    """Point every step at the harness under test, keeping the rest of the fixture's config."""
    path = os.path.join(repo, ".xv", "config.yml")
    lines = open(path).read().splitlines()
    out, skip = [], False
    for line in lines:
        if line.startswith("agents:"):
            skip = True
            out.append("agents:")
            for agent, argv in argv_by_agent.items():
                out.append(f"  {agent}: {json.dumps(argv)}")
            continue
        if skip and line.startswith("  "):
            continue
        skip = False
        out.append(line)
    open(path, "w").write("\n".join(out) + "\n")


def setup_repo(scenario, harness, workdir):
    repo = os.path.join(workdir, "repo")
    shutil.copytree(os.path.join(EVALS, "fixture"), repo)
    for extra in scenario.get("fixture_extra", []):
        src = os.path.join(EVALS, extra["from"])
        dst = os.path.join(repo, extra["to"])
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
    write_config_agents(repo, {"default": harness["argv"]})
    sh(["git", "init", "-q", "-b", "main"], repo)
    sh(["git", "-c", "user.name=eval", "-c", "user.email=eval@example.com", "add", "-A"], repo)
    sh(["git", "-c", "user.name=eval", "-c", "user.email=eval@example.com", "commit", "-qm", "fixture"], repo)
    sh(["git", "config", "user.name", "eval"], repo)
    sh(["git", "config", "user.email", "eval@example.com"], repo)
    sl = scenario.get("slice")
    if not sl:
        return repo, repo
    args = [XV, "slice", "new", sl["id"], "--by", "eval-person", "--kind", sl.get("kind", "feature"),
            "--title", sl.get("title", sl["id"]),
            "--scenario-file", os.path.join(EVALS, "slices", sl["scenario"]),
            "--ignore", sl.get("ignore", "Nothing stated.")]
    if sl.get("recording"):
        args += ["--recording", os.path.join(repo, sl["recording"])]
    wt = sh(args, repo).stdout.strip().splitlines()[-1]
    return repo, wt


def apply_setup(scenario, wt):
    sid = (scenario.get("slice") or {}).get("id")
    for op in scenario.get("setup", []):
        kind = op["op"]
        if kind == "patch":
            sh(["git", "apply", os.path.join(EVALS, op["patch"])], wt)
        elif kind == "copy":
            shutil.copytree(os.path.join(EVALS, op["from"]), os.path.join(wt, op.get("to", ".")),
                            dirs_exist_ok=True)
        elif kind == "xv":
            sh([XV] + [a.replace("{id}", sid or "") for a in op["args"]], wt)
        elif kind == "commit":
            sh(["git", "add", "-A"], wt)
            sh(["git", "commit", "-qm", op.get("message", "setup")], wt)
        elif kind == "record-set":
            value = op["value"] if isinstance(op["value"], str) else json.dumps(op["value"])
            sh([XV, "record", "set", sid, op["field"], value] + (["--by", op["by"]] if op.get("by") else []), wt)
        else:
            raise ValueError(f"unknown setup op {kind}")


def run_one(scenario, harness_name, arm, n, outdir, keep=False):
    harness = load_harnesses()[harness_name]
    workdir = tempfile.mkdtemp(prefix=f"xv-eval-{scenario['name']}-")
    env = dict(os.environ)
    env["PATH"] = os.path.join(HOME, "bin") + os.pathsep + env.get("PATH", "")
    os.environ["PATH"] = env["PATH"]
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        repo, wt = setup_repo(scenario, harness, workdir)
        apply_setup(scenario, wt)
        head_before = sh(["git", "rev-parse", "HEAD"], wt).stdout.strip()
        ctx = {"repo": repo, "wt": wt, "head_before": head_before, "scenario": scenario,
               "arm": arm, "harness": harness_name, "slice": (scenario.get("slice") or {}).get("id")}
        if arm == "skill":
            cmd = [a.replace("{id}", ctx["slice"] or "") for a in scenario["skill_cmd"]]
            p = subprocess.run([XV] + cmd, cwd=wt, capture_output=True, text=True, env=env,
                               timeout=scenario.get("timeout", 3600))
            ctx["exit"], ctx["stdout"], ctx["stderr"] = p.returncode, p.stdout, p.stderr
            try:
                ctx["verdict"] = json.loads(p.stdout[p.stdout.find("{"):]) if "{" in p.stdout else None
            except json.JSONDecodeError:
                ctx["verdict"] = None
            ctx["spend"] = spend_from_record(wt, ctx["slice"])
        else:
            text = scenario["baseline_prompt"].replace("{id}", ctx["slice"] or "")
            r = agentcli.run(harness["argv"], text, wt, None, scenario.get("timeout", 3600), env)
            ctx["exit"], ctx["stdout"], ctx["stderr"] = r["code"], r["stdout"], r["stderr"]
            s = spendlib.from_run(r)
            ctx["spend"] = [s]
        results = grade.grade(scenario, ctx)
        final = final_message(ctx, wt)
        out = {
            "scenario": scenario["name"], "increment": scenario["increment"], "agent": scenario.get("agent"),
            "harness": harness_name, "model": agentcli.model_of(harness["argv"]), "arm": arm, "n": n,
            "started": started, "exit": ctx["exit"], "spend": ctx["spend"],
            "assertions": results,
            "passed": sum(1 for r in results if r["pass"]), "total": len(results),
            "workdir": workdir if keep else None,
            "stderr_tail": (ctx.get("stderr") or "")[-600:],
            "verdict": ctx.get("verdict"), "final_message": final[-3000:],
        }
    except Exception as e:  # a broken setup is a result too; say what broke
        out = {"scenario": scenario["name"], "increment": scenario["increment"], "harness": harness_name,
               "arm": arm, "n": n, "started": started, "error": f"{type(e).__name__}: {e}",
               "assertions": [], "passed": 0, "total": 0, "workdir": workdir}
        keep = True
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, f"{scenario['name']}.{harness_name}.{arm}.{n}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    if not keep:
        cleanup(workdir)
    return out


def final_message(ctx, wt):
    """The agent's last words: the baseline's output, or the step's run log."""
    texts = []
    if ctx["arm"] == "skill":
        for s in ctx.get("spend") or []:
            if s.get("log") and os.path.exists(s["log"]):
                texts.append(open(s["log"]).read())
    else:
        texts.append(ctx.get("stdout") or "")
    out = []
    for t in texts:
        try:
            out.append(json.loads(t).get("result") or "")
            continue
        except (json.JSONDecodeError, AttributeError):
            pass
        parts = []
        for line in t.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            part = ev.get("part") if isinstance(ev, dict) else None
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
        out.append("\n".join(parts) or t[-2000:])
    return "\n---\n".join(out)


def spend_from_record(wt, slice_id):
    try:
        for root, _, files in os.walk(os.path.join(wt, ".xv", "slices")):
            if f"{slice_id}.md" in files:
                data, _ = read_doc(os.path.join(root, f"{slice_id}.md"))
                return data.get("spend") or []
    except Exception:
        pass
    return []


def cleanup(workdir):
    repo = os.path.join(workdir, "repo")
    if os.path.isdir(repo):
        subprocess.run(["git", "worktree", "prune"], cwd=repo, capture_output=True)
    shutil.rmtree(workdir, ignore_errors=True)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--list", action="store_true")
    p.add_argument("--scenario", nargs="*", default=[])
    p.add_argument("--increment", type=int, nargs="*", default=[])
    p.add_argument("--all", action="store_true")
    p.add_argument("--harness", nargs="*", default=["claude"])
    p.add_argument("--arm", nargs="*", default=["skill", "baseline"])
    p.add_argument("--repeat", type=int, default=1)
    p.add_argument("--keep", action="store_true", help="keep the work dirs for reading")
    p.add_argument("--out", default=os.path.join(EVALS, "results", "runs",
                                                 datetime.date.today().isoformat()))
    a = p.parse_args()
    scenarios = load_scenarios()
    if a.list:
        for s in scenarios.values():
            print(f"{s['increment']:>2}  {s['name']:<28} {s.get('agent', ''):<11} {s['what']}")
        return
    chosen = [s for s in scenarios.values()
              if a.all or s["name"] in a.scenario or s["increment"] in a.increment]
    for s in chosen:
        for h in a.harness:
            if h in s.get("skip_harness", []):
                continue
            for arm in a.arm:
                if arm == "baseline" and not s.get("baseline_prompt"):
                    continue
                for n in range(1, a.repeat + 1):
                    r = run_one(s, h, arm, n, a.out, a.keep)
                    status = r.get("error") or f"{r['passed']}/{r['total']}"
                    print(f"{s['name']:<28} {h:<9} {arm:<9} #{n}  {status}", flush=True)


if __name__ == "__main__":
    main()

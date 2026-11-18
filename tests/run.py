"""Run the suite: `python3 tests/run.py [--shard i/n] [--jobs k]`.

The shards 1/n to n/n together run every test once. Within a shard the tests run in k
processes at the same time; with no `--jobs`, k is the number of cores this process may
use. `XV_TEST_JOBS=n` in the environment caps k at n either way, so a person can keep
cores free on their own machine. The output is unittest's, so a failure reads
`FAIL: test (id)`. Exits non-zero if any test fails.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def walk(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from walk(t)
        else:
            yield t


def collect():
    suite = unittest.TestLoader().discover(HERE, top_level_dir=HERE)
    return sorted(set(t.id() for t in walk(suite)))


def files_with_no_tests(ids):
    """The test files in this folder that gave no test id: a file that was dropped, not one that passed."""
    modules = {i.split(".")[0] for i in ids}
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(HERE, "test_*.py"))
                  if os.path.basename(f)[:-3] not in modules)


def cores():
    """The cores this process may run on."""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count() or 1


def job_count(requested, cap, cores):
    """The processes to run: `requested` (`--jobs`), or `cores` when none was asked for;
    never more than `cap` (`XV_TEST_JOBS`) when it is set; at least one."""
    jobs = requested if requested is not None else cores
    if cap not in (None, ""):
        jobs = min(jobs, int(cap))
    return max(1, jobs)


def run_ids(path):
    with open(path) as f:
        ids = f.read().split()
    suite = unittest.TestLoader().loadTestsFromNames(ids)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--shard", default="1/1")
    p.add_argument("--jobs", type=int, help="processes per shard; default: every core, see XV_TEST_JOBS")
    p.add_argument("--run-ids")
    a = p.parse_args(argv)
    if a.run_ids:
        return run_ids(a.run_ids)
    i, n = (int(x) for x in a.shard.split("/"))
    if not 1 <= i <= n or (a.jobs is not None and a.jobs < 1):
        p.error("--shard needs 1 <= i <= n and --jobs needs at least 1")
    jobs = job_count(a.jobs, os.environ.get("XV_TEST_JOBS"), cores())
    every = collect()
    missing = files_with_no_tests(every)
    if missing:
        print("FAIL: no tests were collected from " + ", ".join(missing) + ": the runner dropped the file")
        print("FAILED")
        return 1
    mine = every[i - 1::n]
    chunks = [c for c in (mine[k::jobs] for k in range(jobs)) if c]
    procs = []
    with tempfile.TemporaryDirectory(prefix="xv-run-") as tmp:
        for k, chunk in enumerate(chunks):
            path = os.path.join(tmp, str(k))
            with open(path, "w") as f:
                f.write("\n".join(chunk))
            out = open(path + ".out", "w+")
            procs.append((subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), "--run-ids", path],
                cwd=HERE, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL), out))
        failed, ran = False, 0
        for proc, out in procs:
            failed |= proc.wait() != 0
            out.seek(0)
            text = out.read()
            ran += sum(int(m) for m in re.findall(r"^Ran (\d+) tests? in ", text, re.M))
            sys.stdout.write(text)
            out.close()
    if ran != len(mine):
        print("FAIL: %d tests were collected for this shard and %d ran" % (len(mine), ran))
        failed = True
    print("Ran %d tests in shard %d/%d, %d jobs" % (len(mine), i, n, jobs))
    print("FAILED" if failed else "OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

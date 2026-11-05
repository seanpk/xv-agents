"""Run the suite: `python3 tests/run.py --shard i/n --jobs k`.

The shards 1/n to n/n together run every test once. Within a shard the tests run in k
processes at the same time. The output is unittest's, so a failure reads `FAIL: test (id)`.
Exits non-zero if any test fails.
"""
import argparse
import os
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


def run_ids(path):
    with open(path) as f:
        ids = f.read().split()
    suite = unittest.TestLoader().loadTestsFromNames(ids)
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    return 0 if result.wasSuccessful() else 1


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--shard", default="1/1")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--run-ids")
    a = p.parse_args(argv)
    if a.run_ids:
        return run_ids(a.run_ids)
    i, n = (int(x) for x in a.shard.split("/"))
    if not 1 <= i <= n or a.jobs < 1:
        p.error("--shard needs 1 <= i <= n and --jobs needs at least 1")
    mine = collect()[i - 1::n]
    chunks = [c for c in (mine[k::a.jobs] for k in range(a.jobs)) if c]
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
        failed = False
        for proc, out in procs:
            failed |= proc.wait() != 0
            out.seek(0)
            sys.stdout.write(out.read())
            out.close()
    print("Ran %d tests in shard %d/%d" % (len(mine), i, n))
    print("FAILED" if failed else "OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

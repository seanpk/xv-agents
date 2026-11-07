import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import HOME

RUNNER = os.path.join(HOME, "tests", "run.py")

MARKING = '''import os
import unittest


def mark(name):
    with open(os.environ["XV_MARK"], "a") as f:
        f.write(name + "\\n")

'''


def class_name(module):
    return module.title().replace("_", "") + "Case"


def module_source(name, tests, failing=()):
    body = MARKING + "class " + class_name(name) + "(unittest.TestCase):\n"
    for t in tests:
        body += "    def test_" + t + "(self):\n        mark('" + name + "." + t + "')\n"
        if t in failing:
            body += "        self.fail('boom')\n"
    return body


MEET = '''import os
import time
import unittest


class {cls}(unittest.TestCase):
    def test_meet(self):
        here = os.path.dirname(os.environ["XV_MARK"])
        open(os.path.join(here, "{me}.here"), "w").close()
        other = os.path.join(here, "{other}.here")
        for _ in range(100):
            if os.path.exists(other):
                return
            time.sleep(0.1)
        self.fail("the other test never ran at the same time")
'''


class RunnerCase(unittest.TestCase):
    """The runner is copied next to a small suite of its own, so these tests do not run this suite."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="xv-runner-")
        self.mark = os.path.join(self.tmp, "marks")
        shutil.copy(RUNNER, os.path.join(self.tmp, "run.py"))
        self.suite = {"test_a": ["one", "two", "three"], "test_b": ["four", "five"],
                      "test_c": ["six"], "test_d": ["seven", "eight"]}
        self.failing = {}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self):
        for name, tests in self.suite.items():
            with open(os.path.join(self.tmp, name + ".py"), "w") as f:
                f.write(module_source(name, tests, self.failing.get(name, ())))

    def launch(self, *args):
        open(self.mark, "w").close()
        env = dict(os.environ, XV_MARK=self.mark)
        return subprocess.run([sys.executable, os.path.join(self.tmp, "run.py"), *args],
                              cwd=self.tmp, env=env, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=120)

    def run_runner(self, *args):
        self.write()
        p = self.launch(*args)
        with open(self.mark) as f:
            return p, f.read().split()

    def everything(self):
        return sorted(m + "." + t for m, ts in self.suite.items() for t in ts)


class RunnerTest(RunnerCase):
    def test_one_shard_of_one_runs_every_test_once(self):
        p, marks = self.run_runner("--shard", "1/1", "--jobs", "1")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(sorted(marks), self.everything())

    def test_the_shards_together_run_every_test_exactly_once(self):
        seen = []
        for i in (1, 2, 3):
            p, marks = self.run_runner("--shard", str(i) + "/3", "--jobs", "1")
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
            seen += marks
        self.assertEqual(sorted(seen), self.everything())

    def test_each_shard_gets_some_of_the_tests(self):
        for i in (1, 2):
            p, marks = self.run_runner("--shard", str(i) + "/2", "--jobs", "1")
            self.assertTrue(marks, "shard " + str(i) + "/2 ran nothing")
            self.assertLess(len(marks), len(self.everything()))

    def test_jobs_runs_every_test_once_across_processes(self):
        p, marks = self.run_runner("--shard", "1/1", "--jobs", "3")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(sorted(marks), self.everything())

    def test_jobs_run_at_the_same_time(self):
        # two tests each wait for the other's marker; only concurrent processes get through
        self.suite = {}
        for me, other in (("test_x", "test_y"), ("test_y", "test_x")):
            with open(os.path.join(self.tmp, me + ".py"), "w") as f:
                f.write(MEET.format(cls=class_name(me), me=me, other=other))
        p = self.launch("--shard", "1/1", "--jobs", "2")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

    def test_a_failing_test_makes_the_command_exit_non_zero(self):
        self.failing = {"test_b": ["five"]}
        p, marks = self.run_runner("--shard", "1/1", "--jobs", "2")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(sorted(marks), self.everything())

    def test_a_failure_in_a_shard_fails_that_shard(self):
        self.failing = {n: list(ts) for n, ts in self.suite.items()}
        codes = [self.run_runner("--shard", str(i) + "/2", "--jobs", "1")[0].returncode for i in (1, 2)]
        self.assertTrue(all(c != 0 for c in codes), codes)

    def test_the_failed_test_is_named_in_unittest_form(self):
        self.failing = {"test_b": ["five"]}
        p, _ = self.run_runner("--shard", "1/1", "--jobs", "2")
        self.assertRegex(p.stdout + p.stderr,
                         r"(?m)^FAIL: test_five \(test_b\.TestBCase(\.test_five)?\)")

    def test_a_test_file_that_gives_no_test_fails_the_run_and_is_named(self):
        self.write()
        with open(os.path.join(self.tmp, "test_empty.py"), "w") as f:
            f.write("import unittest\n\n\nclass Helper(unittest.TestCase):\n    pass\n")
        p = self.launch("--shard", "1/1", "--jobs", "2")
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertIn("test_empty.py", p.stdout)
        self.assertNotIn("\nOK", p.stdout)

    def test_a_worker_that_exits_early_with_zero_fails_the_run(self):
        self.suite["test_quit"] = ["quits"]
        self.write()
        with open(os.path.join(self.tmp, "test_quit.py"), "w") as f:
            f.write("import os\nimport unittest\n\n\nclass QuitCase(unittest.TestCase):\n"
                    "    def test_quits(self):\n        os._exit(0)\n")
        p = self.launch("--shard", "1/1", "--jobs", "1")
        self.assertNotEqual(p.returncode, 0, p.stdout)
        self.assertRegex(p.stdout, r"\d+ tests were collected for this shard and \d+ ran")

    def test_a_passing_run_names_no_failure(self):
        p, _ = self.run_runner("--shard", "1/1", "--jobs", "2")
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertNotRegex(p.stdout + p.stderr, r"(?m)^(FAIL|ERROR): ")


class NoRerunTest(unittest.TestCase):
    def collect(self):
        top = os.path.join(HOME, "tests")
        suite = unittest.TestLoader().discover(top, top_level_dir=top)
        found = []

        def walk(s):
            for t in s:
                if isinstance(t, unittest.TestSuite):
                    walk(t)
                else:
                    found.append(t)
        walk(suite)
        return found

    def test_no_test_is_collected_twice(self):
        ids = [t.id() for t in self.collect()]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        self.assertEqual(dupes, [], str(len(dupes)) + " tests are collected more than once")

    def test_no_class_inherits_tests_from_another_test_class(self):
        reruns = set()
        for t in self.collect():
            cls = type(t)
            for base in cls.__mro__[1:]:
                if base is unittest.TestCase:
                    break
                if t._testMethodName in vars(base):
                    reruns.add(cls.__module__ + "." + cls.__name__ + "." + t._testMethodName
                               + " (from " + base.__name__ + ")")
                    break
        self.assertEqual(sorted(reruns), [])


def read(*parts):
    with open(os.path.join(HOME, *parts)) as f:
        return f.read()


class WiringTest(unittest.TestCase):
    def test_ci_shards_run_at_the_same_time(self):
        wf = read(".github", "workflows", "tests.yml")
        self.assertNotRegex(wf, r"max-parallel:\s*1\b")
        self.assertNotIn("needs:", wf)

    def test_the_tests_import_only_the_standard_library(self):
        std = set(sys.stdlib_module_names)
        local = set()
        for d in ("tests", "scripts", "evals"):
            local |= {f[:-3] for f in os.listdir(os.path.join(HOME, d)) if f.endswith(".py")}
        bad = []
        for f in sorted(os.listdir(os.path.join(HOME, "tests"))):
            if not f.endswith(".py"):
                continue
            for m in re.finditer(r"(?m)^(?:from|import)\s+([A-Za-z_]\w*)", read("tests", f)):
                if m.group(1) not in std and m.group(1) not in local:
                    bad.append(f + ": " + m.group(1))
        self.assertEqual(bad, [])


# Watch on the first green run: the shards 1/3, 2/3, 3/3 of the real suite add up to one
# full run with no test twice, and two processes run side by side with --jobs 2.

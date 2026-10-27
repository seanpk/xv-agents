import unittest

from helpers import RepoCase


class InitReportsATimeoutTest(RepoCase):
    """The outcome `xv init` prints as test_run: a command that outlasts tests.timeout is timed out, even when it wrote output first.

    init's limit is the config's tests.timeout and a fresh config says 900, so these call the function
    init prints test_run from (try_test_command) with a one-second limit instead of waiting it out.
    """

    def run_with(self, command):
        from run import try_test_command
        return try_test_command(self.repo, {"command": command, "timeout": 1})

    def test_a_command_that_writes_then_outlasts_the_limit_is_timed_out(self):
        self.assertEqual(self.run_with("echo SLOW-SUITE-OUTPUT; sleep 30"),
                         {"result": "timed out", "after_s": 1})

    def test_a_command_that_writes_nothing_before_the_limit_is_timed_out(self):
        self.assertEqual(self.run_with("sleep 30"), {"result": "timed out", "after_s": 1})


if __name__ == "__main__":
    unittest.main()

# Watch on the first green run: a suite that wrote a line and then slept past the limit is reported
# as timed out after 1s, as one that wrote nothing is. Then set tests.timeout low in a config and run
# `xv init` to see the same in its output (init crashes today when .xv/config.yml already exists:
# `runners` is unbound at scripts/run.py:919, a separate defect).

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest

from helpers import HOME

import agentcli
import spend

DATA = os.path.join(HOME, "tests", "data")


class SpendTest(unittest.TestCase):
    def test_claude_result_sums_every_model_and_keeps_dollars(self):
        s = spend.from_claude_result(open(os.path.join(DATA, "claude-result.json")).read(), "sonnet")
        self.assertEqual((s["model"], s["model_id"]), ("sonnet", "claude-sonnet-5-5"))
        self.assertEqual(s["tokens"], 10 + 800 + 2000 + 5 + 50 + 100)
        self.assertEqual(s["cache_read"], 30000)
        self.assertEqual((s["usd"], s["turns"], s["wall_s"]), (0.1234, 7, 12.3))

    def test_grok_result_leaves_cache_reads_out_of_tokens_and_the_four_counts_add_up_to_its_total(self):
        s = spend.from_grok_result(open(os.path.join(DATA, "grok-result.json")).read(), "grok-4.7")
        self.assertEqual((s["harness"], s["model"], s["model_id"]), ("grok", "grok-4.7", "grok-4.7-build"))
        self.assertEqual((s["tokens"], s["usd"], s["turns"], s["session"]), (1000, 0.0123, 3, "0000"))
        self.assertEqual(s["cache_read"], 4000)

    def test_claude_session_counts_each_message_once_and_has_no_dollars(self):
        s = spend.from_claude_session(os.path.join(DATA, "claude-session.jsonl"))
        self.assertEqual(s["tokens"], (3 + 100 + 50) + (2 + 20))
        self.assertEqual(s["cache_read"], 1000 + 1100)
        self.assertEqual((s["turns"], s["usd"], s["wall_s"]), (2, None, 60.0))  # first line to last

    def test_opencode_export_counts_reasoning_as_output(self):
        s = spend.from_opencode("ses_x", exported=open(os.path.join(DATA, "opencode-export.json")).read())
        self.assertEqual((s["model"], s["tokens_out"], s["tokens"], s["usd"], s["turns"]),
                         ("gpt-oss:20b", 304, 17794 + 304, 0.0, 2))
        self.assertEqual(s["cache_read"], 1000)

    def test_the_budget_counts_every_steps_spend_the_guardians_too(self):
        data = {"budget": {"usd": 1, "tokens": 5000},
                "spend": [{"step": "maker", "usd": 0.6, "tokens": 3000}, {"step": "maker", "usd": 0.5, "tokens": 1000},
                          {"step": "guardian", "usd": 9, "tokens": 99999}]}
        state = spend.budget_state(data)
        self.assertEqual((state["over"], state["spent"]["tokens"]), (["tokens", "usd"], 103999))

    # Codex: `codex exec --json` prints one event per line. Each turn.completed carries
    # usage; its input_tokens include the cached ones. Worked by hand from the fixture:
    # turn 1 in 1000 (800 cached) out 50; turn 2 in 2000 (1500 cached) out 100.
    # Reasoning (20, 60) is already inside output_tokens (settled), so it is not added.
    def test_codex_result_adds_the_turns_and_keeps_cache_out_of_input(self):
        s = spend.from_codex_result(open(os.path.join(DATA, "codex-result.jsonl")).read(), "gpt-5")
        self.assertEqual(s["harness"], "codex")
        self.assertEqual((s["tokens_in"], s["tokens_out"], s["cache_read"]), (200 + 500, 150, 2300))
        self.assertEqual(s["tokens"], 700 + 150)
        self.assertEqual((s["session"], s["turns"], s["usd"]), ("019a-thread-0001", 2, None))

    def test_a_codex_step_records_a_codex_row(self):
        with tempfile.TemporaryDirectory() as d:
            fake = os.path.join(d, "codex")
            with open(fake, "w") as f:
                f.write("#!/bin/sh\ncat " + os.path.join(DATA, "codex-result.jsonl") + "\n")
            os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR)
            r = agentcli.run([fake, "exec", "--json", "{prompt}"], "hi", d)
        s = spend.from_run(r)
        self.assertEqual((s["harness"], s["tokens"], s["cache_read"], s["turns"], s["usd"], s["session"]),
                         ("codex", 850, 2300, 2, None, "019a-thread-0001"))

    def test_xv_spend_reads_a_saved_codex_run(self):
        # `xv spend codex-result <file>`, called like the other readers: `xv spend read <reader> <file>`
        p = subprocess.run([sys.executable, os.path.join(HOME, "bin", "xv"), "spend", "read", "codex-result",
                            os.path.join(DATA, "codex-result.jsonl")],
                           capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(p.returncode, 0, p.stderr)
        s = json.loads(p.stdout)
        self.assertEqual((s["harness"], s["tokens"], s["turns"]), ("codex", 850, 2))

    def test_the_agent_cli_gets_a_closed_stdin(self):
        # the parent keeps this child's stdin open and silent; a CLI that reads stdin must still see EOF
        code = ("import sys, json; sys.path.insert(0, %r); import agentcli; "
                "r = agentcli.run([sys.executable, '-c', 'import sys; print(len(sys.stdin.read()))', '{prompt}'],"
                " 'p', '.', timeout=5); print(json.dumps([r['code'], r['stdout'].strip()]))"
                % os.path.join(HOME, "scripts"))
        p = subprocess.Popen([sys.executable, "-c", code], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            out = p.stdout.readline()  # not communicate(): that would close the stdin we mean to keep open
        finally:
            p.kill()
            p.wait()
            p.stdout.close()
            p.stdin.close()
        self.assertEqual(json.loads(out), [0, "0"])


if __name__ == "__main__":
    unittest.main()

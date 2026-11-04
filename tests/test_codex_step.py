import json
import os
import sys
import unittest

from helpers import HOME, RepoCase

import agentcli
import record

sys.path.insert(0, os.path.join(HOME, "evals"))
import grade  # noqa: E402

REPORT = {"agent": "maker", "status": "green", "summary": "ok"}


def codex_events(*messages, thread="019a-thread-0009"):
    """What `codex exec --json` prints: one event per line, the messages as item.completed."""
    lines = [{"type": "thread.started", "thread_id": thread}]
    for i, text in enumerate(messages):
        lines.append({"type": "turn.started"})
        lines.append({"type": "item.completed", "item": {"id": f"item_{i}", "type": "agent_message", "text": text}})
        lines.append({"type": "turn.completed", "usage": {"input_tokens": 10, "cached_input_tokens": 0,
                                                          "output_tokens": 5, "reasoning_output_tokens": 0}})
    return "\n".join(json.dumps(x) for x in lines) + "\n"


def block(report):
    return "done.\n```xv-report\n" + json.dumps(report) + "\n```"


def read(path):
    with open(os.path.join(HOME, path)) as f:
        return f.read()


class CodexReportTest(RepoCase):
    def test_the_report_in_the_last_agent_message_is_found(self):
        stale = dict(REPORT, status="red", summary="an earlier turn")
        out = codex_events(block(stale), block(REPORT))
        self.assertEqual(record.extract_report(out), REPORT)

    def test_a_report_in_an_earlier_message_is_not_the_report_when_the_last_has_none(self):
        out = codex_events(block(REPORT), "all finished, nothing more to say")
        self.assertIsNone(record.extract_report(out))

    def test_a_codex_step_applies_its_report_to_the_record(self):
        wt = self.new_slice("s1")
        path = os.path.join(self.tmp, "codex.jsonl")
        report = dict(REPORT, moved_tests=[{"file": "tests/a.py", "assertion": "x", "why": "y"}])
        with open(path, "w") as f:
            f.write(codex_events("working", block(report)))
        self.xv("record", "report", "s1", "maker", path, cwd=wt)
        data = json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)
        self.assertEqual(data["moved_tests"][0]["by"], "maker")


class CodexSessionTest(unittest.TestCase):
    def test_session_of_a_codex_run_is_the_thread_id(self):
        self.assertEqual(agentcli.session_of("codex", codex_events("hi", thread="019a-abc")), "019a-abc")

    def test_session_of_codex_output_with_no_thread_is_none(self):
        self.assertIsNone(agentcli.session_of("codex", "not events\n"))


class CodexEvalFinalMessageTest(unittest.TestCase):
    def test_the_final_message_is_the_last_agent_message(self):
        ctx = {"stdout": codex_events("first thoughts", "the last word")}
        self.assertEqual(grade.final_text(ctx), "the last word")


class CodexHarnessEntryTest(unittest.TestCase):
    def entry(self):
        return json.loads(read("evals/harnesses.json"))["codex"]

    def test_the_entry_runs_codex_exec_json_on_terra_with_the_sandbox_off(self):
        argv = self.entry()["argv"]
        self.assertEqual(argv[:3], ["codex", "exec", "--json"])
        flag = "--model" if "--model" in argv else "-m"
        self.assertEqual(argv[argv.index(flag) + 1], "gpt-6.1-terra")
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", argv)
        self.assertIn("{prompt}", argv)

    def test_the_entry_is_read_as_the_codex_harness_on_terra(self):
        argv = self.entry()["argv"]
        self.assertEqual((agentcli.harness_of(argv), agentcli.model_of(argv)), ("codex", "gpt-6.1-terra"))

    def test_the_note_says_the_brief_is_not_the_whole_prompt_because_agents_md_and_skills_load(self):
        note = self.entry()["note"]
        self.assertIn("not the whole prompt", note)
        self.assertIn("AGENTS.md", note)
        self.assertIn("skills", note)


class CodexDocsTest(unittest.TestCase):
    def test_readme_no_longer_says_codex_was_not_run(self):
        lines = read("README.md").splitlines()
        for n in (3, 392):
            self.assertNotIn("were not run", lines[n - 1], f"README.md:{n}")
            self.assertNotIn("was not run", lines[n - 1], f"README.md:{n}")
        self.assertIn("headless", lines[391])
        self.assertIn("--json", lines[391])

    def test_decision_48_says_spend_reads_codex_events_and_codex_reports_no_dollars(self):
        item = next(x for x in read("docs/decisions.md").splitlines() if x.startswith("48. "))
        self.assertNotIn("Codex is not read", item)
        self.assertIn("--json", item)
        self.assertIn("no dollars", item)

    def test_relies_on_has_a_line_for_the_codex_event_shape(self):
        lines = [x for x in read("docs/relies-on.md").splitlines()
                 if x.startswith("- ") and "codex" in x.lower() and "agent_message" in x]
        self.assertEqual(len(lines), 1, "one relies-on line for the Codex events")
        what, url, quote = [p.strip() for p in lines[0][2:].split(" | ")]
        self.assertIn("spend.py", what)
        self.assertTrue(url.startswith("https://"))
        self.assertTrue(quote.startswith('"') and quote.endswith('"') and len(quote) > 2)


# Watch first: a real `codex exec --json` run of a step. Its xv-report should land in the
# record, the spend row should carry the thread_id as its session, and the eval runner's
# final message should read as the agent's last words, not a pile of events.

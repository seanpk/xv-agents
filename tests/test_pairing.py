import json
import os
import sys
import tempfile
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh

FAKE = os.path.join(HOME, "tests", "fake_agent.py")


class PairingCase(RepoCase):
    """`xv pairing start|end <id>`, with the stand-in agent and no transcript anywhere."""

    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        # a home with no transcripts in it: the pairing must open anyway (point 8)
        self.empty_home = os.path.join(self.tmp, "home")
        os.makedirs(self.empty_home)
        patch = mock.patch.dict(os.environ, {"HOME": self.empty_home, "USERPROFILE": self.empty_home})
        patch.start()
        self.addCleanup(patch.stop)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def open_stop(self):
        """The slice has no budget, so the run stops at the forecaster for the originator."""
        p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)

    def start(self, by="pat", why="the red is wrong and I want to fix it with the agent", check=True):
        return self.xv("pairing", "start", "s1", "--by", by, "--why", why, cwd=self.wt, check=check)

    def end(self, *args, check=True):
        return self.xv("pairing", "end", "s1", *args, cwd=self.wt, check=check)

    def commit(self, rel, text, msg):
        path = os.path.join(self.wt, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", msg], self.wt)

    def head(self):
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def finish_the_loop(self):
        """Budget set, the loop to the merge stop: a stop is open there."""
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "budget"], self.wt)

    def pairings(self):
        return self.record().get("pairings")


class PairingStartTest(PairingCase):
    # -- 1
    def test_start_answers_the_open_stop_as_a_pairing_and_writes_an_entry(self):
        self.open_stop()
        before = self.head()
        p = self.start()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        data = self.record()
        stop = data["stops"][-1]
        self.assertIsNotNone(stop["answer"])
        self.assertIn("pairing", stop["answer"].lower())
        self.assertIn("pat", stop["answered_by"])
        entries = data["pairings"]
        self.assertEqual(len(entries), 1)
        blob = json.dumps(entries[0])
        self.assertIn("pat", blob)
        self.assertIn("the red is wrong and I want to fix it with the agent", blob)
        self.assertIn(before, blob)  # the head commit when it opened

    def test_start_by_a_name_that_is_not_the_originator_is_refused(self):
        self.open_stop()
        p = self.start(by="sam", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unknown command", p.stderr)
        self.assertIn("pat", p.stdout + p.stderr)  # it names the originator
        self.assertFalse(self.pairings())
        self.assertIsNone(self.record()["stops"][-1]["answer"])

    def test_start_on_a_slice_with_no_open_stop_is_refused(self):
        p = self.start(check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unknown command", p.stderr)
        self.assertIn("stop", (p.stdout + p.stderr).lower())
        self.assertFalse(self.pairings())

    def test_start_needs_a_why(self):
        self.open_stop()
        p = self.xv("pairing", "start", "s1", "--by", "pat", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("unknown command", p.stderr)
        self.assertFalse(self.pairings())

    def test_start_opens_when_no_transcript_is_found_and_the_log_says_so(self):
        self.open_stop()
        self.start()
        log = open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read().split("## Log")[1]
        self.assertIn("pairing", log)
        self.assertIn("transcript", log.lower())

    # -- 2, 8
    def test_step_run_rebase_and_record_report_refuse_during_a_pairing_and_name_it(self):
        self.open_stop()
        self.start()
        report = os.path.join(self.tmp, "report.txt")
        with open(report, "w") as f:
            f.write('```xv-report\n{"agent": "forecaster", "status": "done", "summary": "x"}\n```\n')
        for args in (("step", "scenario", "s1"), ("run", "s1"), ("slice", "rebase", "s1"),
                     ("record", "report", "s1", "forecaster", report)):
            p = self.xv(*args, cwd=self.wt, check=False)
            self.assertNotEqual(p.returncode, 0, args)
            self.assertIn("pairing", (p.stdout + p.stderr).lower(), args)

    def test_a_second_pairing_cannot_open_while_one_is_open(self):
        self.open_stop()
        self.start()
        p = self.start(check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(len(self.pairings()), 1)


class PairingEndTest(PairingCase):
    def setUp(self):
        super().setUp()
        self.open_stop()
        self.start()

    # -- 4
    def test_end_next_maker_closes_it_with_the_end_head_and_resume_step(self):
        self.commit("pantry/note.txt", "x\n", "pairing (pat with claude): a note")
        p = self.end("--next", "maker")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        entry = self.pairings()[0]
        blob = json.dumps(entry)
        self.assertIn("maker", blob)
        self.assertIn(self.head(), blob)
        self.assertGreaterEqual(len(entry), 6)

    def test_after_end_a_step_runs_again(self):
        self.end("--next", "maker")
        p = self.xv("step", "forecaster", "s1", cwd=self.wt, check=False)
        self.assertNotIn("pairing", (p.stdout + p.stderr).lower())

    def test_end_next_cleaner_is_accepted(self):
        p = self.end("--next", "cleaner", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("cleaner", json.dumps(self.pairings()[0]))

    def test_end_next_close_is_refused_and_leaves_it_open(self):
        p = self.end("--next", "close", check=False)
        self.assertNotEqual(p.returncode, 0)
        q = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertIn("pairing", (q.stdout + q.stderr).lower())

    def test_end_next_scenario_needs_an_amendment_made_since_it_opened(self):
        p = self.end("--next", "scenario", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("amend", (p.stdout + p.stderr).lower())

    def test_end_next_scenario_goes_through_after_an_amendment(self):
        path = os.path.join(self.tmp, "amendment.md")
        with open(path, "w") as f:
            f.write("The list also shows the day.")
        self.xv("slice", "amend", "s1", "--scenario-file", path, "--by", "pat", cwd=self.wt)
        p = self.end("--next", "scenario", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_end_when_the_spend_cannot_be_read_says_so_in_the_log(self):
        self.end("--next", "maker")
        log = open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read().split("## Log")[1]
        self.assertIn("spend", log.lower())
        self.assertIn("pairing", log.lower())

    # -- 5
    def test_end_refuses_while_a_changed_old_test_has_no_recorded_move_and_names_the_file(self):
        path = os.path.join(self.wt, "tests", "test_store.py")
        text = open(path).read().replace('"qty must be a positive whole number"', '"qty must be 1 or more"')
        self.assertNotEqual(text, open(path).read())
        self.commit("tests/test_store.py", text, "pairing (pat with claude): reword the qty message")
        p = self.end("--next", "maker", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("tests/test_store.py", p.stdout + p.stderr)

    def test_end_goes_through_once_the_move_is_recorded_and_the_move_is_in_the_persons_name(self):
        path = os.path.join(self.wt, "tests", "test_store.py")
        text = open(path).read().replace('"qty must be a positive whole number"', '"qty must be 1 or more"')
        self.commit("tests/test_store.py", text, "pairing (pat with claude): reword the qty message")
        self.xv("record", "move", "s1", "--file", "tests/test_store.py",
                "--assertion", "test_add_rejects_a_quantity_below_one", "--why", "the wording changed", "--by", "pat",
                cwd=self.wt)
        p = self.end("--next", "maker", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        moves = self.record()["moved_tests"]
        self.assertTrue(moves)
        self.assertIn("pat", json.dumps(moves[-1]))

    def test_a_test_only_added_to_an_old_file_is_not_a_move(self):
        path = os.path.join(self.wt, "tests", "test_store.py")
        text = open(path).read() + "\n    def test_new_in_a_pairing(self):\n        self.assertTrue(True)\n"
        self.commit("tests/test_store.py", text, "pairing (pat with claude): a new test")
        p = self.end("--next", "maker", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    # -- 8
    def test_commits_without_the_prefix_are_listed_not_refused(self):
        self.commit("pantry/note.txt", "x\n", "a plain commit with no prefix")
        p = self.end("--next", "maker", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("a plain commit with no prefix", p.stdout + p.stderr + json.dumps(self.pairings()))


def stamp(delta_s=0):
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) + timedelta(seconds=delta_s)).isoformat()


def turn(mid, ts, out):
    return json.dumps({"type": "assistant", "timestamp": ts, "message": {
        "id": mid, "model": "claude-sonnet-5-5",
        "usage": {"input_tokens": 1, "output_tokens": out, "cache_read_input_tokens": 0,
                  "cache_creation_input_tokens": 0}}}) + "\n"


class PairingFieldsTest(PairingCase):
    """Amendment 10: the entry's fields, the spend row through a reader, the guardian's prompt, solo."""

    def start_with(self, session):
        return self.xv("pairing", "start", "s1", "--by", "pat", "--why", "fix the red with the agent",
                       "--session", session, cwd=self.wt)

    def log(self):
        return open(os.path.join(self.wt, ".xv", "slices", "s1.md")).read().split("## Log")[1]

    def transcript(self):
        return os.path.join(self.tmp, "pair-session.jsonl")

    # -- 4, 10
    def test_end_writes_the_named_fields_on_the_entry(self):
        self.open_stop()
        self.start()
        self.commit("pantry/note.txt", "x\n", "pairing (pat with agent): a note")
        self.commit("pantry/other.txt", "y\n", "no prefix here")
        self.end("--next", "maker")
        entry = self.pairings()[0]
        for key in ("ended_at", "end_head", "next", "commits", "unprefixed", "not_blind", "spend", "spend_note"):
            self.assertIn(key, entry)
        self.assertEqual(entry["next"], "maker")
        self.assertEqual(entry["end_head"], self.head())
        self.assertEqual(len(entry["commits"]), 2)
        self.assertIn("no prefix here", json.dumps(entry["unprefixed"]))
        self.assertNotIn("a note", json.dumps(entry["unprefixed"]))

    def test_without_session_the_spend_note_says_it_cannot_be_read_and_no_row_is_added(self):
        self.open_stop()
        self.start()
        self.end("--next", "maker")
        entry = self.pairings()[0]
        self.assertTrue(entry["spend_note"])
        self.assertFalse([r for r in self.record()["spend"] if r.get("step") == "pairing"])

    def test_a_reader_that_cannot_cut_a_window_still_opens_and_the_log_says_so(self):
        self.open_stop()
        path = os.path.join(self.tmp, "result.json")
        open(path, "w").write("{}")
        self.start_with("claude-result:" + path)
        self.assertEqual(len(self.pairings()), 1)
        self.assertIn("spend", self.log().lower())

    def test_the_session_spend_is_one_row_cut_to_the_pairing_window_and_counts_in_the_budget(self):
        self.open_stop()
        path = self.transcript()
        open(path, "w").write(turn("before", stamp(-3600), 1000))
        self.start_with("claude-session:" + path)
        with open(path, "a") as f:
            f.write(turn("inside1", stamp(), 30))
            f.write(turn("inside2", stamp(), 12))
        self.end("--next", "maker")
        with open(path, "a") as f:
            f.write(turn("after", stamp(3600), 5000))
        rows = [r for r in self.record()["spend"] if r.get("step") == "pairing"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["turns"], 2)
        self.assertEqual(rows[0]["tokens_out"], 42)
        self.assertEqual(rows[0]["tokens"], 44)
        self.assertEqual(self.pairings()[0]["spend"]["tokens_out"], 42)
        state = json.loads(self.xv("spend", "budget", "s1", cwd=self.wt, check=False).stdout)
        self.assertGreaterEqual(state["spent"]["tokens"], 44)

    def test_a_turn_logged_after_the_end_is_not_in_the_row(self):
        self.open_stop()
        path = self.transcript()
        open(path, "w").write("")
        self.start_with("claude-session:" + path)
        self.end("--next", "maker")
        open(path, "a").write(turn("late", stamp(3600), 700))
        rows = [r for r in self.record()["spend"] if r.get("step") == "pairing"]
        self.assertTrue(all(r["tokens_out"] < 700 for r in rows))

    # -- 3, 10
    def test_the_guardian_prompt_names_each_not_blind_file_and_the_others_do_not(self):
        self.open_stop()
        self.start()
        self.commit("tests/test_pairing_made.py", "import unittest\n", "pairing (pat with agent): a test")
        self.commit("pantry/note.txt", "x\n", "pairing (pat with agent): a note")
        self.end("--next", "guardian")
        entry = self.pairings()[0]
        self.assertEqual(entry["not_blind"], ["tests/test_pairing_made.py"])
        guardian = self.xv("prompt", "guardian", "s1", cwd=self.wt).stdout
        self.assertIn("tests/test_pairing_made.py", guardian)
        self.assertIn("not blind", guardian.lower())
        for seat in ("scenario", "maker", "cleaner"):
            self.assertNotIn("tests/test_pairing_made.py", self.xv("prompt", seat, "s1", cwd=self.wt).stdout, seat)

    # -- 8, 10
    def test_a_stop_for_two_people_is_refused_unless_the_repo_runs_solo(self):
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Two of you: is the shape right?", cwd=self.wt)
        p = self.start(check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("two", (p.stdout + p.stderr).lower())
        self.assertFalse(self.pairings())

    def test_a_stop_for_two_people_opens_a_pairing_when_the_repo_runs_solo(self):
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read().replace('two_people: "any two of the household"', "two_people: solo")
        self.assertIn("two_people: solo", text)
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "solo"], self.wt)
        self.xv("record", "stop", "s1", "--order", "shape_or_pitch", "--seat", "two_people",
                "--question", "Two of you: is the shape right?", cwd=self.wt)
        p = self.start(check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(len(self.pairings()), 1)


class PairingPacketTest(PairingCase):
    # -- 3, 6
    def test_the_packet_has_one_line_per_pairing_under_pairings(self):
        self.finish_the_loop()
        p = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)  # the merge stop is open
        self.start(why="check the wording with the agent")
        self.commit("pantry/note.txt", "x\n", "pairing (pat with claude): a note")
        self.end("--next", "guardian")
        q = self.xv("run", "s1", cwd=self.wt, check=False)
        self.assertEqual(q.returncode, 10, q.stdout + q.stderr)
        packet = open(os.path.join(self.wt, ".xv", "slices", "s1.packet.md")).read()
        self.assertIn("## Pairings", packet)
        section = packet.split("## Pairings")[1].split("\n## ")[0]
        lines = [l for l in section.splitlines() if l.strip().startswith("-")]
        self.assertEqual(len(lines), 1)
        self.assertIn("pat", lines[0])
        self.assertIn("check the wording with the agent", lines[0])
        self.assertIn("guardian", lines[0])


if __name__ == "__main__":
    unittest.main()

"""A pairing (#146): at an open stop or send-back, the person who set the work going works on the slice with the
watch's own session, and `xv pairing end` hands the slice back to the loop at a step."""

import datetime
import json
import os
import subprocess
import sys

from helpers import HOME, XV, RepoCase, sh

import packet as packetlib
import record
import wall

SID = "0f3c2a1e-pair-session"
PREFIX = "pairing (pat with Claude):"


def stamp(delta_s=0):
    t = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=delta_s)
    return t.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def turn(mid, ts, tokens_in=100, tokens_out=50, cache_read=1000, cache_write=10):
    return json.dumps({"type": "assistant", "timestamp": ts, "message": {
        "id": mid, "model": "claude-opus-5-5", "usage": {
            "input_tokens": tokens_in, "output_tokens": tokens_out,
            "cache_read_input_tokens": cache_read, "cache_creation_input_tokens": cache_write}}})


class PairingCase(RepoCase):
    """A slice with an open stop for its originator, pat, and a Claude Code config folder with the pair's transcript."""

    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1")
        self.config_dir = os.path.join(self.tmp, "claude-config")
        self.transcript = os.path.join(self.config_dir, "projects", "-home-pat-repo", f"{SID}.jsonl")
        os.makedirs(os.path.dirname(self.transcript))
        with open(self.transcript, "w") as f:
            f.write(turn("before", "2020-01-01T00:00:00.000Z", tokens_in=999999) + "\n")
        self.env = {**os.environ, "CLAUDE_CONFIG_DIR": self.config_dir, "CLAUDE_CODE_SESSION_ID": SID}

    def run_xv(self, *args, env=None):
        return subprocess.run([sys.executable, XV, *args], cwd=self.wt, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, env=env or self.env)

    def ok(self, *args, env=None):
        p = self.run_xv(*args, env=env)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def refused(self, *args, env=None):
        p = self.run_xv(*args, env=env)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        return p

    def show(self):
        return json.loads(self.ok("record", "show", "s1", "--json").stdout)

    def body(self):
        with open(os.path.join(self.wt, ".xv", "slices", "s1.md")) as f:
            return f.read()

    def stop(self, order="maker_stopped", seat="originator", step="maker"):
        self.ok("record", "stop", "s1", "--order", order, "--seat", seat, "--question", "What now?", "--step", step)

    def start(self, why="the maker's handoff did not work twice", *extra):
        return self.ok("pairing", "start", "s1", "--by", "pat", "--why", why, *extra)

    def end(self, nxt="guardian"):
        return self.ok("pairing", "end", "s1", "--next", nxt)

    def write(self, rel, text, mode="w"):
        full = os.path.join(self.wt, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, mode) as f:
            f.write(text)

    def commit(self, message):
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", message], self.wt)
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def head(self):
        return sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()

    def pair_turn(self, mid="during", **usage):
        with open(self.transcript, "a") as f:
            f.write(turn(mid, stamp(), **usage) + "\n")

    def add_test(self, name="test_pairing_added"):
        self.write("tests/test_store.py", f"\n\nclass PairedTest(unittest.TestCase):\n    def {name}(self):\n"
                                          "        self.assertTrue(True)\n", mode="a")


class StartTest(PairingCase):
    """Point 1: `xv pairing start` answers the open stop as a pairing and writes a pairings entry."""

    def test_start_answers_the_open_stop_as_a_pairing_and_writes_the_entry(self):
        self.stop()
        head = self.head()
        out = json.loads(self.start().stdout)
        self.assertEqual(out["prefix"], PREFIX)
        data = self.show()
        stop = data["stops"][-1]
        self.assertEqual(stop["answered_by"], ["pat"])
        self.assertEqual(stop["pick"], "pairing")
        self.assertIn("the maker's handoff did not work twice", stop["answer"])
        self.assertEqual(stop["pairing"], 1)
        [p] = data["pairings"]
        self.assertEqual((p["n"], p["by"], p["agent"], p["why"]), (1, "pat", "Claude", "the maker's handoff did not work twice"))
        self.assertEqual(p["session"], {"harness": "claude", "id": SID, "transcript": self.transcript})
        self.assertEqual(p["start_head"], head)
        self.assertTrue(p["started_at"])
        self.assertNotIn("ended_at", p)
        self.assertEqual(data["status"], "pairing")
        self.assertIn("pairing 1 opened", self.body())

    def test_start_commits_the_record(self):
        self.stop()
        self.start()
        self.assertEqual(sh(["git", "status", "--porcelain"], self.wt).stdout.strip(), "")
        self.assertIn("pairing 1 opened by pat", sh(["git", "log", "-1", "--format=%s"], self.wt).stdout)

    def test_start_refuses_a_name_that_is_not_the_originator(self):
        self.stop()
        p = self.refused("pairing", "start", "s1", "--by", "sam", "--why", "help")
        self.assertIn("pat", p.stderr)
        self.assertEqual(self.show().get("pairings") or [], [])
        self.assertIsNone(self.show()["stops"][-1]["answer"])

    def test_start_refuses_a_slice_with_no_open_stop_or_send_back(self):
        p = self.refused("pairing", "start", "s1", "--by", "pat", "--why", "help")
        self.assertIn("no open stop or send-back", p.stderr)
        self.assertEqual(self.show().get("pairings") or [], [])

    def test_start_refuses_after_the_stop_was_answered(self):
        self.stop()
        self.ok("record", "answer", "s1", "--by", "pat", "--answer", "go on", "--next", "cleaner", "--resume")
        self.refused("pairing", "start", "s1", "--by", "pat", "--why", "help")

    def test_start_opens_at_a_send_back(self):
        path, data, body = record.load(self.wt, "s1")
        data["checks"] = {"reports": [{"agent": "guardian", "status": "done", "summary": "s", "at": "t"}]}
        body = record.send_back(data, body, "guardian", "scenario_miss", ["2"], "point 2 is missed", "maker")
        record.save(path, data, body)
        self.start("too small for another pass")
        data = self.show()
        self.assertEqual(data["pairings"][0]["opened_at"], "send-back")
        self.assertEqual(data["stops"][-1]["pairing"], 1)

    def test_start_refuses_a_send_back_a_step_has_reported_after(self):
        path, data, body = record.load(self.wt, "s1")
        data["checks"] = {"reports": [{"agent": "guardian", "status": "done", "summary": "s", "at": "t"}]}
        body = record.send_back(data, body, "guardian", "scenario_miss", ["2"], "point 2 is missed", "maker")
        data["checks"]["reports"].append({"agent": "maker", "status": "done", "summary": "s", "at": "t2"})
        record.save(path, data, body)
        self.refused("pairing", "start", "s1", "--by", "pat", "--why", "help")

    def test_start_refuses_while_a_pairing_is_open(self):
        self.stop()
        self.start()
        self.stop(order="no_report")
        p = self.refused("pairing", "start", "s1", "--by", "pat", "--why", "again")
        self.assertIn("already open", p.stderr)

    def test_start_refuses_a_stop_for_two_people_unless_the_repo_runs_solo(self):
        self.stop(order="shape_or_pitch", seat="two_people", step="guardian")
        p = self.refused("pairing", "start", "s1", "--by", "pat", "--why", "help")
        self.assertIn("two people", p.stderr)

    def test_a_session_given_by_its_transcript_is_used(self):
        self.stop()
        env = {k: v for k, v in self.env.items() if k != "CLAUDE_CODE_SESSION_ID"}
        self.ok("pairing", "start", "s1", "--by", "pat", "--why", "w", "--session", self.transcript, env=env)
        self.assertEqual(self.show()["pairings"][0]["session"]["id"], SID)

    def test_with_no_session_the_pairing_opens_and_the_log_says_its_spend_cannot_be_read(self):
        self.stop()
        env = {k: v for k, v in self.env.items() if k != "CLAUDE_CODE_SESSION_ID"}
        self.ok("pairing", "start", "s1", "--by", "pat", "--why", "w", "--agent", "Codex", env=env)
        p = self.show()["pairings"][0]
        self.assertIsNone(p["session"])
        self.assertEqual(p["prefix"], "pairing (pat with Codex):")
        self.assertIn("spend cannot be read", self.body())


class WhileOpenTest(PairingCase):
    """Point 2: while a pairing is open, the loop refuses on the slice and names the pairing; point 5: a move
    recorded in it is the person's."""

    def setUp(self):
        super().setUp()
        self.stop()
        self.start()

    def test_step_refuses_and_names_the_open_pairing(self):
        for agent in ("maker", "cleaner", "guardian", "scenario"):
            with self.subTest(agent=agent):
                p = self.refused("step", agent, "s1")
                self.assertIn("pairing 1 is open", p.stderr)
                self.assertIn("pat with Claude", p.stderr)

    def test_run_refuses_and_names_the_open_pairing(self):
        p = self.refused("run", "s1")
        self.assertIn("pairing 1 is open", p.stderr)

    def test_close_refuses(self):
        self.assertIn("pairing 1 is open", self.refused("close", "s1", "--why", "done").stderr)

    def test_a_session_mode_report_refuses(self):
        p = subprocess.run([sys.executable, XV, "record", "report", "s1", "maker", "-"], cwd=self.wt, env=self.env,
                           input="```xv-report\n{}\n```\n", capture_output=True, text=True)
        self.assertEqual(p.returncode, 2, p.stderr)
        self.assertIn("pairing 1 is open", p.stderr)

    def test_a_move_recorded_in_the_pairing_is_in_the_persons_name(self):
        self.ok("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "was: 4; now: 5", "--why", "w")
        move = self.show()["moved_tests"][-1]
        self.assertEqual((move["by"], move["pairing"]), ("pat", 1))

    def test_a_move_in_another_name_is_refused_in_the_pairing(self):
        p = self.refused("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "a", "--why", "w",
                         "--by", "maker")
        self.assertIn("pat", p.stderr)
        self.assertEqual(self.show()["moved_tests"], [])

    def test_the_pairings_field_is_not_set_by_hand(self):
        self.refused("record", "set", "s1", "pairings", "[]", "--by", "pat")
        self.refused("record", "add", "s1", "pairings", "{}", "--by", "pat")


class EndTest(PairingCase):
    """Point 4: `xv pairing end` closes the pairing at a resume step, with the pair session's spend."""

    def setUp(self):
        super().setUp()
        self.stop()
        self.start()

    def test_end_writes_the_end_and_the_resume_step_and_the_loop_runs_again(self):
        self.write("pantry/extra.py", "X = 1\n")
        work = self.commit(f"{PREFIX} a constant")
        self.end("cleaner")
        data = self.show()
        p = data["pairings"][0]
        self.assertTrue(p["ended_at"])
        self.assertEqual(p["end_head"], work)
        self.assertEqual(p["next"], "cleaner")
        self.assertEqual(p["commits"], [work])
        self.assertEqual(p["unprefixed"], [])
        self.assertEqual((data["next"], data["status"]), ("cleaner", "working"))
        self.assertIsNone(record.open_pairing(data))
        self.assertIn("resumes at cleaner", data["stops"][-1]["settled"])

    def test_end_at_an_earlier_step_marks_the_stop_sent_back(self):
        self.end("maker")
        stop = self.show()["stops"][-1]
        self.assertEqual((stop.get("sent_back"), stop.get("sent_back_to")), (True, "maker"))

    def test_end_at_close_is_refused(self):
        p = self.refused("pairing", "end", "s1", "--next", "close")
        self.assertIn("guardian", p.stderr)
        self.assertTrue(record.open_pairing(self.show()))

    def test_end_at_another_step_is_refused(self):
        for nxt in ("forecaster", "none", "prototype"):
            with self.subTest(next=nxt):
                self.refused("pairing", "end", "s1", "--next", nxt)

    def test_end_at_scenario_needs_an_amendment_made_since_the_pairing_opened(self):
        p = self.refused("pairing", "end", "s1", "--next", "scenario")
        self.assertIn("xv slice amend", p.stderr)
        self.write("amend.md", "1. The household also sees Y.\n")
        self.ok("slice", "amend", "s1", "--by", "pat", "--scenario-file", os.path.join(self.wt, "amend.md"))
        os.remove(os.path.join(self.wt, "amend.md"))
        self.end("scenario")
        self.assertEqual(self.show()["next"], "scenario")

    def test_end_refuses_work_that_is_not_committed(self):
        self.write("pantry/extra.py", "X = 1\n")
        p = self.refused("pairing", "end", "s1", "--next", "guardian")
        self.assertIn("pantry/extra.py", p.stderr)

    def test_the_spend_is_the_pair_sessions_turns_while_the_pairing_was_open(self):
        self.pair_turn("during-1")
        self.pair_turn("during-2", tokens_in=200)
        with open(self.transcript, "a") as f:
            f.write(turn("after", "2100-01-01T00:00:00.000Z", tokens_in=777777) + "\n")
        self.end()
        data = self.show()
        row = data["pairings"][0]["spend"]
        self.assertEqual((row["tokens_in"], row["tokens_out"], row["cache_write"], row["turns"]), (300, 100, 20, 2))
        self.assertEqual(row["tokens"], 420)
        self.assertEqual(row["step"], "pairing")
        self.assertIn(row, data["spend"], "the spend counts in the slice's actual")
        import spend
        self.assertEqual(spend.slice_spend(data)["tokens"], 420)

    def test_the_spend_counts_in_the_budget_check(self):
        self.ok("record", "set", "s1", "budget", '{"tokens": 100}', "--by", "pat")
        self.pair_turn()
        out = json.loads(self.end("cleaner").stdout)
        self.assertTrue(out["budget"]["spent_out"])
        self.assertIn("budget is spent", out["note"])
        p = self.run_xv("step", "cleaner", "s1")
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.assertEqual(self.show()["stops"][-1]["order"], "budget_spent")

    def test_when_the_spend_cannot_be_read_the_log_says_so(self):
        os.remove(self.transcript)
        self.end()
        data = self.show()
        p = data["pairings"][0]
        self.assertIsNone(p["spend"])
        self.assertIn("no transcript", p["spend_note"])
        self.assertFalse([r for r in data["spend"] if r.get("step") == "pairing"])
        self.assertIn("spend could not be read", self.body())

    def test_a_commit_without_the_prefix_is_named(self):
        self.write("pantry/extra.py", "X = 1\n")
        sha = self.commit("a constant")
        self.end()
        self.assertEqual(self.show()["pairings"][0]["unprefixed"], [f"{sha} a constant"])
        self.assertIn("commits without", self.body())

    def test_end_refuses_with_no_open_pairing(self):
        self.end()
        self.assertIn("no pairing is open", self.refused("pairing", "end", "s1", "--next", "guardian").stderr)


class NotBlindTest(PairingCase):
    """Point 3: a test written or changed in a pairing is not blind, and the record, the packet and the guardian's
    prompt say so; point 5: a changed old test needs a move recorded in the pairing."""

    def setUp(self):
        super().setUp()
        self.ok("wall", "baseline", "s1")  # the scenario step takes it, before any pairing
        self.commit("the wall baseline")
        self.stop()
        self.start()

    def test_a_test_added_in_the_pairing_is_named_not_blind(self):
        self.write("tests/test_new.py", "import unittest\n")
        self.commit(f"{PREFIX} a new test file")
        self.end()
        self.assertEqual(self.show()["pairings"][0]["not_blind"], ["tests/test_new.py"])
        self.assertIn("not blind: tests/test_new.py", self.body())

    def test_the_guardian_prompt_names_the_tests_that_are_not_blind(self):
        self.add_test()
        self.commit(f"{PREFIX} a test")
        self.end()
        text = self.ok("prompt", "guardian", "s1").stdout
        self.assertIn("not blind: tests/test_store.py", text)
        self.assertNotIn("not blind", self.ok("prompt", "maker", "s1").stdout)

    def test_end_refuses_an_old_test_changed_with_no_move_and_names_each_file(self):
        store = os.path.join(self.wt, "tests", "test_store.py")
        api = os.path.join(self.wt, "tests", "test_api.py")
        with open(store) as f:
            text = f.read()
        self.write("tests/test_store.py", text.replace("qty, 4)", "qty, 5)"))
        os.remove(api)
        self.commit(f"{PREFIX} two old tests")
        p = self.refused("pairing", "end", "s1", "--next", "guardian")
        self.assertIn("tests/test_store.py", p.stderr)
        self.assertIn("tests/test_api.py", p.stderr)
        self.assertTrue(record.open_pairing(self.show()))
        self.ok("record", "move", "s1", "--file", "tests/test_store.py", "--assertion", "was: 4; now: 5", "--why", "w")
        p = self.refused("pairing", "end", "s1", "--next", "guardian")
        self.assertNotIn("tests/test_store.py", p.stderr)
        self.ok("record", "move", "s1", "--file", "tests/test_api.py", "--assertion", "removed", "--why", "w")
        self.commit(f"{PREFIX} the moves")
        self.end()

    def test_a_move_recorded_before_the_pairing_does_not_cover_a_change_in_it(self):
        self.stop(order="no_report")  # a second stop, so the move goes in before the pairing can end
        path, data, body = record.load(self.wt, "s1")
        data["moved_tests"].append({"file": "tests/test_store.py", "assertion": "older", "why": "w", "by": "maker"})
        record.save(path, data, body)
        with open(os.path.join(self.wt, "tests", "test_store.py")) as f:
            text = f.read()
        self.write("tests/test_store.py", text.replace("qty, 4)", "qty, 5)"))
        self.commit(f"{PREFIX} an old test")
        self.assertIn("tests/test_store.py", self.refused("pairing", "end", "s1", "--next", "guardian").stderr)

    def test_a_test_added_to_an_old_file_needs_no_move_and_the_wall_does_not_stop_on_it(self):
        self.add_test()
        self.commit(f"{PREFIX} a test in an old file")
        self.assertTrue(wall.check(self.wt, "s1")["ok"], "an open pairing's added test is not a move")
        self.end("cleaner")
        self.assertTrue(wall.check(self.wt, "s1")["ok"])
        # a change after the pairing ended is the loop's again
        self.write("tests/test_store.py", "\n# a later line\n", mode="a")
        self.assertEqual(wall.check(self.wt, "s1")["unrecorded"], ["tests/test_store.py"])

    def test_the_wall_still_stops_on_a_line_an_open_pairing_removed_with_no_move(self):
        with open(os.path.join(self.wt, "tests", "test_store.py")) as f:
            text = f.read()
        self.write("tests/test_store.py", text.replace("qty, 4)", "qty, 5)"))
        self.assertEqual(wall.check(self.wt, "s1")["unrecorded"], ["tests/test_store.py"])


class PacketTest(PairingCase):
    """Point 6: one packet line per pairing under `## Pairings`."""

    PACKET = ("---\nslice: s1\nshape_change: no\npitch_contradiction: no\ndoor: two-way\nexpected_moves: 0\n---\n\n"
              "# Packet\n\n## 1. Shape\n\n- None.\n")

    def setUp(self):
        super().setUp()
        self.write(".xv/slices/s1.packet.md", self.PACKET)
        path, data, body = record.load(self.wt, "s1")
        data["packet"] = ".xv/slices/s1.packet.md"
        record.save(path, data, body)
        self.stop(order="ready_to_merge", step="guardian")
        self.start("the last fix is too small for a pass through the loop")

    def packet(self):
        with open(os.path.join(self.wt, ".xv", "slices", "s1.packet.md")) as f:
            return f.read()

    def test_end_writes_one_line_per_pairing_under_pairings(self):
        self.pair_turn()
        self.add_test()
        work = self.commit(f"{PREFIX} a test")
        self.end()
        text = self.packet()
        section = text.split("## Pairings\n\n", 1)[1]
        [line] = [ln for ln in section.splitlines() if ln.startswith("- ")]
        for words in ("pat with Claude", SID, "the last fix is too small for a pass through the loop", work[:10],
                      "Resumed at guardian", "160 tokens", "Not blind", "tests/test_store.py"):
            self.assertIn(words, line)
        self.assertIn(".xv/slices/s1.packet.md", sh(["git", "show", "--name-only", "--format=", "HEAD"], self.wt).stdout)

    def test_the_packet_says_when_the_spend_cannot_be_read(self):
        os.remove(self.transcript)
        self.end()
        self.assertIn("Spend: not read (no transcript", self.packet())

    def test_a_second_pairing_adds_a_line_and_a_rewrite_keeps_one_section(self):
        self.end()
        self.stop(order="ready_to_merge", step="guardian")
        self.start("a second small fix")
        self.end()
        data = self.show()
        path = os.path.join(self.wt, ".xv", "slices", "s1.packet.md")
        packetlib.note_pairings(path, data)
        text = self.packet()
        self.assertEqual(text.count("## Pairings"), 1)
        self.assertEqual(len([ln for ln in text.splitlines() if ln.startswith("- Pairing ")]), 2)

    def test_the_packet_checks_write_the_section_after_the_guardian_runs(self):
        self.end()
        self.write(".xv/slices/s1.packet.md", self.PACKET)  # the guardian writes its packet afresh
        packetlib.packet_checks(os.path.join(self.wt, ".xv", "slices", "s1.packet.md"), self.show(), self.wt)
        self.assertIn("- Pairing 1: pat with Claude", self.packet())

    def test_a_packet_with_no_pairing_is_left_as_it_is(self):
        other = os.path.join(self.tmp, "p.md")
        with open(other, "w") as f:
            f.write(self.PACKET + "\n\n")
        packetlib.note_pairings(other, {"pairings": []})
        with open(other) as f:
            self.assertEqual(f.read(), self.PACKET + "\n\n")


class DocsTest(RepoCase):
    """Point 7: the watch's brief and the README say what a pairing is, and the word is pairing."""

    fixture = False

    def read(self, *parts):
        with open(os.path.join(HOME, *parts)) as f:
            return f.read()

    def test_the_watch_brief_has_a_pairing_section_and_its_may_not_list_names_it(self):
        text = self.read("skills", "watch", "SKILL.md")
        self.assertIn("## A pairing", text)
        for words in ("xv pairing start", "xv pairing end", "pairing (<name> with <agent>):"):
            self.assertIn(words, text)
        may_not = text.split("## May not", 1)[1].split("\n## ", 1)[0]
        self.assertIn("outside a pairing", may_not)
        self.assertNotIn("sortie", text)

    def test_the_readme_names_the_commands(self):
        text = self.read("README.md")
        self.assertIn("xv pairing start", text)
        self.assertIn("xv pairing end", text)
        self.assertNotIn("sortie", text)

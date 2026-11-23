import json
import os
import shutil
import sys
import unittest

from helpers import HOME, RepoCase, sh

BEFORE = "EARLIER_CHANGE_LINE_ZZ1 = 'seen by the first pass'"
AFTER = "LATER_CHANGE_LINE_ZZ2 = 'made after the first packet'"
PACKET_TEXT = "The first pass found nothing odd about the pantry shelf, packet marker QQ7."


def skill(name):
    with open(os.path.join(HOME, "skills", name, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


class RepassCase(RepoCase):
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")

    def commit(self, rel, text, msg):
        path = os.path.join(self.wt, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", msg], self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def first_pass(self):
        """A change the first pass saw, then its packet, committed the way the inspector step commits it."""
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        packet = os.path.join(self.wt, ".xv", "slices", "s1.packet.md")
        with open(packet, "w") as f:
            f.write(f"---\nshape_change: no\npitch_contradiction: no\n---\n{PACKET_TEXT}\n")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "xv(s1): packet"], self.wt)
        self.xv("record", "packet", "s1", packet, cwd=self.wt)

    def prompt(self):
        return self.xv("prompt", "inspector", "s1", cwd=self.wt).stdout


class RepassPromptTest(RepassCase):
    # -- 1
    def test_a_repass_prompt_carries_the_earlier_packet(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertIn(PACKET_TEXT, self.prompt())

    def test_a_repass_prompt_carries_the_diff_since_the_packets_head(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertIn(AFTER, self.prompt())

    def test_a_repass_prompt_leaves_out_the_diff_the_first_pass_already_saw(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.assertNotIn(BEFORE, self.prompt())

    def test_a_repass_prompt_keeps_the_five_checks(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        prompt = self.prompt()
        for name in ("Shape.", "Pitch.", "Moved tests.", "The picture.", "The wall."):
            self.assertIn(name, prompt)

    def test_a_first_pass_prompt_has_no_earlier_packet_and_no_diff_section(self):
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        prompt = self.prompt()
        self.assertNotIn(PACKET_TEXT, prompt)
        self.assertNotIn(BEFORE, prompt)

    def test_a_repass_after_a_send_back_gets_the_same_two_things(self):
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        self.xv("record", "stop", "s1", "--order", "test_writer_stopped", "--seat", "originator",
                "--question", "Which line?", cwd=self.wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "2 ok", "--next", "maker",
                "--settled", "the line is as the maker wrote it", cwd=self.wt)
        prompt = self.prompt()
        self.assertIn(PACKET_TEXT, prompt)
        self.assertIn(AFTER, prompt)
        self.assertNotIn(BEFORE, prompt)

    def test_a_repass_whose_diff_cannot_run_stops_instead_of_showing_an_empty_diff(self):
        # decision 12: a check whose input is broken stops for a person; it never passes
        self.first_pass()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        rec = os.path.join(self.wt, ".xv", "slices", "s1.md")
        with open(rec, encoding="utf-8") as f:
            text = f.read()
        real = sh(["git", "rev-parse", "HEAD~1"], self.wt).stdout.strip()  # HEAD when the packet was recorded
        self.assertIn(f'"packet_head": "{real}"', text)  # the record holds the packet's head, so the swap bites
        with open(rec, "w", encoding="utf-8") as f:
            f.write(text.replace(real, "deadbeef" * 5))
        p = self.xv("prompt", "inspector", "s1", cwd=self.wt, check=False)
        self.assertNotEqual(p.returncode, 0, "the prompt came out although the diff could not run")
        self.assertNotIn("The diff after that commit follows", p.stdout)


MARK = """import os, sys
with open(os.environ["MARK_LOG"], "a") as f:
    f.write(sys.argv[1] + "\\n")
print("done, no report")
"""


class RepassCommandTest(RepassCase):
    # -- 2, as amended by 8: `agents.inspector_repass` is a whole command list, for the re-pass only
    def setUp(self):
        super().setUp()
        self.script = os.path.join(self.tmp, "mark.py")
        with open(self.script, "w") as f:
            f.write(MARK)
        self.log = os.path.join(self.tmp, "marks.log")
        os.environ["MARK_LOG"] = self.log
        self.addCleanup(os.environ.pop, "MARK_LOG", None)

    def agents(self, **tags):
        """Name the agents in the worktree's config: each tag is what the stand-in logs when it runs."""
        lines = "".join(f'  {k}: ["{sys.executable}", "{self.script}", "{v}", "{{prompt}}"]\n'
                        for k, v in tags.items())
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        with open(cfg, "w") as f:
            f.write(text[:start] + "agents:\n" + lines + text[end:])
        sh(["git", "commit", "-qam", "xv(s1): agents"], self.wt)

    def ran(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            return f.read().split()

    def step(self):
        p = self.xv("step", "inspector", "s1", cwd=self.wt, check=False)
        self.out = (p.stdout + p.stderr)[-600:]

    def repass(self):
        """The first pass ends in a stop (no report); the person answers it and sends the slice back to the maker."""
        self.first_pass()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1 ok", "--next", "maker",
                "--settled", "the line is as the maker wrote it", cwd=self.wt)
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")

    def test_a_first_pass_never_runs_the_inspector_repass_command(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        self.step()
        self.assertEqual(self.ran(), ["first"], self.out)

    def test_a_repass_without_the_key_runs_the_inspector_command(self):
        self.agents(default="default", inspector="first")
        self.repass()
        self.step()
        self.assertEqual(self.ran(), ["first"], self.out)

    def test_a_repass_without_the_key_or_a_inspector_runs_the_default_command(self):
        self.agents(default="default")
        self.repass()
        self.step()
        self.assertEqual(self.ran(), ["default"], self.out)


LOGGING = """import os, sys
kind = "repass" if "## This is a re-pass" in sys.argv[2] else "first"
with open(os.environ["MARK_LOG"], "a") as f:
    f.write(sys.argv[1] + ":" + kind + "\\n")
print("done, no report")
"""


class RepassAmendmentsTest(RepassCase):
    # -- 9, 10, 11: the re-pass command goes with the re-pass prompt; a failed re-pass diff is a recorded stop
    def setUp(self):
        super().setUp()
        self.script = os.path.join(self.tmp, "mark.py")
        with open(self.script, "w") as f:
            f.write(LOGGING)
        self.log = os.path.join(self.tmp, "marks.log")
        os.environ["MARK_LOG"] = self.log
        self.addCleanup(os.environ.pop, "MARK_LOG", None)

    def agents(self, **tags):
        lines = "".join(f'  {k}: ["{sys.executable}", "{self.script}", "{v}", "{{prompt}}"]\n'
                        for k, v in tags.items())
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        with open(cfg, "w") as f:
            f.write(text[:start] + "agents:\n" + lines + text[end:])
        sh(["git", "commit", "-qam", "xv(s1): agents"], self.wt)

    def ran(self):
        if not os.path.exists(self.log):
            return []
        with open(self.log) as f:
            return f.read().split()

    def run_xv(self, *args):
        p = self.xv(*args, cwd=self.wt, check=False)
        self.out = (p.stdout + p.stderr)[-600:]
        return p

    def repass(self):
        self.first_pass()
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "1 ok", "--next", "maker",
                "--settled", "the line is as the maker wrote it", cwd=self.wt)
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")

    def drop_the_packet_file(self):
        sh(["git", "rm", "-q", ".xv/slices/s1.packet.md"], self.wt)
        sh(["git", "commit", "-qm", "xv(s1): drop the packet"], self.wt)

    def break_the_diff(self):
        rec = os.path.join(self.wt, ".xv", "slices", "s1.md")
        with open(rec, encoding="utf-8") as f:
            text = f.read()
        real = sh(["git", "rev-parse", "HEAD~1"], self.wt).stdout.strip()
        self.assertIn(real, text)
        with open(rec, "w", encoding="utf-8") as f:
            f.write(text.replace(real, "deadbeef" * 5))
        sh(["git", "commit", "-qam", "xv(s1): record"], self.wt)

    # 9
    def test_xv_guard_runs_a_first_pass_with_the_inspector_command_though_the_record_names_a_packet(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.run_xv("inspect", "--base", "main")
        self.assertEqual(self.ran(), ["first:first"], self.out)

    def test_xv_guard_falls_back_to_the_default_command_never_the_repass_one(self):
        self.agents(default="default", inspector_repass="second")
        self.repass()
        self.run_xv("inspect", "--base", "main")
        self.assertEqual(self.ran(), ["default:first"], self.out)

    def test_xv_step_inspector_still_runs_the_repass_command_with_the_repass_prompt(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.run_xv("step", "inspector", "s1")
        self.assertEqual(self.ran(), ["second:repass"], self.out)

    # 10
    def test_a_missing_packet_file_makes_the_step_a_first_pass_with_the_inspector_command(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.drop_the_packet_file()
        self.run_xv("step", "inspector", "s1")
        self.assertEqual(self.ran(), ["first:first"], self.out)

    def test_a_missing_packet_file_with_no_inspector_command_runs_the_default_as_a_first_pass(self):
        self.agents(default="default", inspector_repass="second")
        self.repass()
        self.drop_the_packet_file()
        self.run_xv("step", "inspector", "s1")
        self.assertEqual(self.ran(), ["default:first"], self.out)

    # 11
    def test_a_repass_diff_that_cannot_run_writes_a_repass_diff_failed_stop_for_the_originator(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.break_the_diff()
        self.run_xv("step", "inspector", "s1")
        stops = [s for s in self.record()["stops"] if s["order"] == "repass_diff_failed"]
        self.assertEqual(len(stops), 1, self.out)
        self.assertEqual(stops[0]["seat"], "originator")

    def test_a_repass_diff_that_cannot_run_runs_no_agent_and_exits_10(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.break_the_diff()
        p = self.run_xv("step", "inspector", "s1")
        self.assertEqual(self.ran(), [])
        self.assertEqual(p.returncode, 10, self.out)

    def test_a_repass_step_runs_the_repass_diff_once_for_both_the_prompt_and_the_command(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        real, bin_dir = shutil.which("git"), os.path.join(self.tmp, "bin")
        diffs = os.path.join(self.tmp, "diffs.log")
        os.makedirs(bin_dir)
        with open(os.path.join(bin_dir, "git"), "w") as f:
            f.write(f'#!/bin/sh\ncase "$*" in *"..HEAD -- . :(exclude).xv"*) echo "$*" >> "{diffs}";; esac\n'
                    f'exec "{real}" "$@"\n')
        os.chmod(os.path.join(bin_dir, "git"), 0o755)
        path = os.environ["PATH"]
        os.environ["PATH"] = bin_dir + os.pathsep + path
        self.addCleanup(os.environ.__setitem__, "PATH", path)
        self.run_xv("step", "inspector", "s1")
        self.assertEqual(self.ran(), ["second:repass"], self.out)
        with open(diffs) as f:
            self.assertEqual(len(f.read().splitlines()), 1, self.out)

    def test_xv_prompt_inspector_with_a_failed_repass_diff_exits_2_and_writes_no_stop(self):
        self.agents(default="default", inspector="first", inspector_repass="second")
        self.repass()
        self.break_the_diff()
        p = self.run_xv("prompt", "inspector", "s1")
        self.assertEqual(p.returncode, 2, self.out)
        self.assertEqual([s for s in self.record()["stops"] if s["order"] == "repass_diff_failed"], [])


class PacketFromMainCheckoutTest(RepassCase):
    # -- 12
    def packet_from_main(self):
        """The first pass's change and packet are committed in the slice's worktree; `xv record packet` runs from the main checkout."""
        self.commit("pantry/earlier.py", BEFORE + "\n", "xv(s1): make it work")
        packet = os.path.join(self.wt, ".xv", "slices", "s1.packet.md")
        with open(packet, "w") as f:
            f.write(f"---\nshape_change: no\npitch_contradiction: no\n---\n{PACKET_TEXT}\n")
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "xv(s1): packet"], self.wt)
        self.wt_head = sh(["git", "rev-parse", "HEAD"], self.wt).stdout.strip()
        self.main_head = sh(["git", "rev-parse", "HEAD"], self.repo).stdout.strip()
        self.assertNotEqual(self.wt_head, self.main_head)
        self.xv("record", "packet", "s1", packet, cwd=self.repo)

    def test_the_packet_head_is_the_head_of_the_slices_worktree(self):
        self.packet_from_main()
        inspector = self.record()["checks"]["inspector"]
        self.assertEqual(inspector["packet_head"], self.wt_head)

    def test_the_packet_path_is_relative_to_the_slices_worktree(self):
        self.packet_from_main()
        self.assertEqual(self.record()["packet"], ".xv/slices/s1.packet.md")

    def test_the_next_prompt_after_a_packet_from_the_main_checkout_is_a_repass(self):
        self.packet_from_main()
        self.commit("pantry/later.py", AFTER + "\n", "xv(s1): make it work again")
        out = self.prompt()
        self.assertIn(PACKET_TEXT, out)
        self.assertIn(AFTER, out)
        self.assertNotIn(BEFORE, out.split("diff after that commit", 1)[-1])


class AcceptedWallRecommendationTest(RepassCase):
    REC = {"file": "tests/test_store.py", "test": "test_added_by_the_build",
           "recommend": "mark slice-only", "why": "guards a one-time change", "accepted": True}

    def report(self, recs):
        out = ("done\n```xv-report\n" + json.dumps(
            {"agent": "inspector", "status": "done", "summary": "ok", "wall_recommendations": recs}) + "\n```\n")
        path = os.path.join(self.tmp, "inspector-out.txt")
        with open(path, "w") as f:
            f.write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "inspector", path, cwd=self.wt)

    def accepted_tests(self):
        return [r["test"] for r in self.record()["wall_recommendations"] if r.get("accepted")]

    # -- 3
    def test_an_accepted_recommendation_the_next_pass_does_not_repeat_stays_on_the_record(self):
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(self.REC), cwd=self.wt)
        self.report([])
        self.assertEqual(self.accepted_tests(), ["test_added_by_the_build"])

    def test_an_accepted_recommendation_stays_beside_a_new_one_from_the_next_pass(self):
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(self.REC), cwd=self.wt)
        new = {"file": "tests/test_store.py", "test": "test_other", "recommend": "mark slice-only", "why": "x"}
        self.report([new])
        tests = [r["test"] for r in self.record()["wall_recommendations"]]
        self.assertIn("test_added_by_the_build", tests)
        self.assertIn("test_other", tests)
        self.assertEqual(self.accepted_tests(), ["test_added_by_the_build"])

    def test_an_accepted_mark_is_kept_by_file_and_test_not_by_test_alone(self):
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(self.REC), cwd=self.wt)
        elsewhere = {"file": "tests/test_other.py", "test": "test_added_by_the_build",
                     "recommend": "mark slice-only", "why": "x"}
        self.report([elsewhere])
        got = {(r["file"], bool(r.get("accepted"))) for r in self.record()["wall_recommendations"]
               if r["test"] == "test_added_by_the_build"}
        self.assertEqual(got, {("tests/test_store.py", True), ("tests/test_other.py", False)})

    def test_a_refused_mark_is_kept_by_file_and_test_not_by_test_alone(self):
        refused = dict(self.REC, accepted=False, refused=True)
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(refused), cwd=self.wt)
        elsewhere = {"file": "tests/test_other.py", "test": "test_added_by_the_build",
                     "recommend": "mark slice-only", "why": "x"}
        same = dict(refused, accepted=None)
        same.pop("accepted")
        same.pop("refused")
        self.report([elsewhere, same])
        got = {r["file"]: bool(r.get("refused")) for r in self.record()["wall_recommendations"]}
        self.assertEqual(got, {"tests/test_other.py": False, "tests/test_store.py": True})

    def test_a_recommendation_nobody_accepted_is_replaced_by_the_next_pass(self):
        plain = dict(self.REC, accepted=False)
        self.xv("record", "add", "s1", "wall_recommendations", json.dumps(plain), cwd=self.wt)
        self.report([])
        self.assertEqual(self.record()["wall_recommendations"], [])


class ForecasterBriefTest(RepassCase):
    # -- 4
    def test_the_forecast_brief_asks_for_the_number_of_rounds_with_a_reason(self):
        text = skill("forecaster").lower()
        self.assertIn("rounds", text)
        self.assertIn("passes through the agents", text)
        i = text.index("rounds")
        self.assertIn("reason", text[max(0, i - 600):i + 600])

    def test_the_forecast_report_example_has_a_rounds_field(self):
        text = skill("forecaster")
        example = text[text.index('"forecast":'):]
        self.assertIn('"rounds"', example.split("```")[0])

    def test_a_forecast_report_with_rounds_and_a_reason_keeps_both_in_the_records_forecast(self):
        fc = {"rows": [{"harness": "sh", "model": "default", "tokens": 1000, "basis": []}],
              "wall_s": 10, "shape_breadth": "none", "shape_note": "one comparison",
              "rounds": 3, "rounds_reason": "a pairing is likely after the red"}
        out = ("done\n```xv-report\n" + json.dumps(
            {"agent": "forecaster", "status": "done", "summary": "forecast", "forecast": fc}) + "\n```\n")
        path = os.path.join(self.tmp, "forecaster-out.txt")
        with open(path, "w") as f:
            f.write(json.dumps({"result": out}))
        self.xv("record", "report", "s1", "forecaster", path, cwd=self.wt)
        kept = self.record()["forecast"]
        self.assertEqual(kept.get("rounds"), 3)
        self.assertEqual(kept.get("rounds_reason"), "a pairing is likely after the red")

    # -- 5
    def test_the_close_section_names_a_pairing_and_a_send_back_as_causes_of_the_gap(self):
        text = skill("forecaster")
        close = text[text.index("## Close"):text.index("## May not")].lower()
        self.assertIn("pairing", close)
        self.assertIn("send-back", close)

    # -- 6
    def test_the_forecast_brief_says_to_include_the_forecasters_own_spend(self):
        text = skill("forecaster").lower()
        forecast = text[text.index("## forecast"):text.index("## close")]
        self.assertIn("your own", forecast)
        self.assertIn("spend", forecast)

    def test_the_forecasters_prompt_lists_the_forecaster_among_the_agents_it_prices(self):
        prompt = self.xv("prompt", "forecaster", "s1", cwd=self.wt).stdout
        line = next(ln for ln in prompt.splitlines() if "Agents on this slice" in ln)
        self.assertIn("forecaster on", line)


# What a person should watch on the first green run: open a slice, run it to an inspector pass, send it
# back to the maker, and read the second inspector prompt (`xv prompt inspector <id>`): it should carry the
# first packet and only the diff made after it, with the five checks still there.

if __name__ == "__main__":
    unittest.main()

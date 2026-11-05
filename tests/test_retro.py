import json
import os
import re
import shutil
import sys
import unittest
from unittest import mock

from helpers import HOME, RepoCase, sh

import retro


class RetroTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.copytree(os.path.join(HOME, "evals", "setups", "retro", ".xv", "slices"),
                        os.path.join(self.repo, ".xv", "slices"), dirs_exist_ok=True)
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "slices"], self.repo)

    def test_due_names_the_stops_the_repeat_and_the_overrun(self):
        due = retro.due(self.repo)["slices"]
        self.assertEqual(sorted(due), ["2026-10-15-use-several", "2026-10-16-expiring-days", "2026-10-17-bulk-add"])
        self.assertTrue(any("same stop (unrecorded_move) on 2 slices" in r for r in due["2026-10-16-expiring-days"]))
        self.assertTrue(any("overran" in r for r in due["2026-10-17-bulk-add"]))

    def test_counts_fires_and_overrides(self):
        rows = {r["rule"][:20]: r for r in retro.counts(self.repo)["rules"]}
        self.assertEqual(rows["Name a date for what"]["fired"], 2)
        self.assertEqual((rows["No `print()` in `pan"]["fired"], rows["No `print()` in `pan"]["overridden"]), (1, 1))
        self.assertFalse(any(r["flag"] for r in rows.values()))  # fewer than five fires

    def test_a_candidate_without_a_moment_is_not_traceable(self):
        recs = {d["id"]: (d, b) for _, d, b in retro.records(self.repo)}
        good = {"from": "2026-10-16-expiring-days, the unrecorded_move stop"}
        bad = {"from": "2026-10-16-expiring-days, a vibe"}
        made_up = {"from": "2026-09-01-nothing, the stop"}
        loose = {"from": "2026-10-16-expiring-days, the maker"}
        quoted = {"from": '2026-10-16-expiring-days, "deleted test_expiring_within_three_days"'}
        self.assertFalse(retro.traceable(loose, recs))
        self.assertTrue(retro.traceable(quoted, recs))
        self.assertTrue(retro.traceable(good, recs))
        self.assertFalse(retro.traceable(bad, recs))
        self.assertFalse(retro.traceable(made_up, recs))

    def test_accept_adds_a_standard_with_its_slice_and_miss(self):
        packet = os.path.join(self.repo, "retro.md")
        with open(packet, "w") as f:
            f.write("### 1. Never loosen an expected value to get green\n- kind: standard\n"
                    "- from: 2026-10-15-use-several, the unrecorded_move stop\n- miss: assertEqual became assertGreaterEqual\n")
        retro.accept(self.repo, packet, 1, "pat")
        text = open(os.path.join(self.repo, ".xv", "standards.md")).read()
        self.assertIn("### Never loosen an expected value to get green\n- added: ", text)
        self.assertIn("by pat\n- from: 2026-10-15-use-several", text)

    def run_retro_with_fake_agent(self):
        written = []

        def fake_run(argv, text, root, session, timeout):
            out = re.search(r"Write the retro packet to `([^`]+)`", text).group(1)
            written.append(out)
            with open(os.path.join(root, out), "w") as f:
                f.write("# Retro\n")
            return {"code": 0}

        real = (retro.agentcli.run, retro.agentcli.argv_for)
        retro.agentcli.run, retro.agentcli.argv_for = fake_run, lambda config, agent: ["fake"]
        try:
            retro.run(self.repo, ["2026-10-15-use-several"])
        finally:
            retro.agentcli.run, retro.agentcli.argv_for = real
        return written[0]

    def test_a_second_retro_on_the_same_day_takes_the_next_numbered_name(self):
        d = os.path.join(self.repo, ".xv", "retro")
        os.makedirs(d, exist_ok=True)
        day = retro.today()
        old = {f"{day}.md": "first packet\n", f"{day}.counts.json": '{"first": true}',
               f"{day}-2.md": "second packet\n", f"{day}-2.counts.json": '{"second": true}'}
        for name, body in old.items():
            with open(os.path.join(d, name), "w") as f:
                f.write(body)
        out = self.run_retro_with_fake_agent()
        self.assertEqual(out, f".xv/retro/{day}-3.md")
        self.assertTrue(os.path.exists(os.path.join(d, f"{day}-3.counts.json")))
        for name, body in old.items():
            self.assertEqual(open(os.path.join(d, name)).read(), body, f"{name} changed")

    def test_the_first_retro_of_a_day_takes_the_plain_name_and_its_counts_file(self):
        day = retro.today()
        out = self.run_retro_with_fake_agent()
        self.assertEqual(out, f".xv/retro/{day}.md")
        self.assertTrue(os.path.exists(os.path.join(self.repo, ".xv", "retro", f"{day}.counts.json")))


FAKE = os.path.join(HOME, "tests", "fake_agent.py")
MISS = "Point 1 is not met: the list still leaves out milk that runs out today."
IDS = ("2026-11-01-a", "2026-11-02-b", "2026-11-03-c")


class ReworkSignalTest(RepoCase):
    """A retro is due when the same module was touched by closed slices that each went back to the maker."""

    def closed(self, sid, modules, sendbacks, created="2026-11-01", status="closed"):
        fields = ""
        if modules is not None:
            fields += f"modules_touched: {json.dumps(modules)}\n"
        if sendbacks is not None:
            fields += f"maker_sendbacks: {sendbacks}\n"
        text = (f"---\nid: {sid}\ntitle: {sid}\nkind: feature\nstatus: {status}\nset_by: pat\n"
                f"created: {created}\nbranch: xv/{sid}\nbase: \"0000000\"\nnext: none\n"
                "forecast: null\nbudget: null\nred: null\nmoved_tests: []\nspend: []\nstops: []\n"
                "decisions: []\noverrides: []\nchecks: {\"reports\": []}\n"
                f"{fields}---\n# {sid}\n\n## Scenario\n\nx\n")
        with open(os.path.join(self.repo, ".xv", "slices", f"{sid}.md"), "w") as f:
            f.write(text)

    def set_limit(self, value):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        text = re.sub(r"^limits:\n", f"limits:\n  rework_slices: {value}\n", text, count=1, flags=re.M)
        open(cfg, "w").write(text)

    def reasons(self):
        return retro.due(self.repo)["slices"]

    def three_reworked(self):
        for sid in IDS:
            self.closed(sid, ["pantry"], 1)

    # 2. the reason
    def test_three_closed_slices_each_sent_back_make_the_module_due_by_name_and_slices(self):
        self.three_reworked()
        due = self.reasons()
        for sid in IDS:
            text = " ".join(due.get(sid, []))
            self.assertIn("pantry", text, sid)
            for other in IDS:
                self.assertIn(other, text, sid)

    def test_a_slice_never_sent_back_does_not_count_toward_the_module(self):
        self.closed(IDS[0], ["pantry"], 1)
        self.closed(IDS[1], ["pantry"], 1)
        self.closed(IDS[2], ["pantry"], 0)
        self.assertEqual(self.reasons(), {})

    def test_slices_touching_different_modules_do_not_add_up(self):
        self.closed(IDS[0], ["pantry"], 1)
        self.closed(IDS[1], ["pantry/api"], 1)
        self.closed(IDS[2], ["tests"], 2)
        self.assertEqual(self.reasons(), {})

    def test_a_slice_that_is_not_closed_does_not_count(self):
        self.closed(IDS[0], ["pantry"], 1)
        self.closed(IDS[1], ["pantry"], 1)
        self.closed(IDS[2], ["pantry"], 1, status="working")
        self.assertEqual(self.reasons(), {})

    def test_slices_from_before_the_last_retro_do_not_count(self):
        os.makedirs(os.path.join(self.repo, ".xv", "retro"), exist_ok=True)
        open(os.path.join(self.repo, ".xv", "retro", "2026-11-02.md"), "w").write("# Retro\n")
        self.closed(IDS[0], ["pantry"], 1, created="2026-11-01")
        self.closed(IDS[1], ["pantry"], 1, created="2026-11-03")
        self.closed(IDS[2], ["pantry"], 1, created="2026-11-04")
        self.assertEqual(self.reasons(), {})

    def test_only_the_shared_module_is_named_when_slices_touched_more_than_one(self):
        self.closed(IDS[0], ["pantry", "tests"], 1)
        self.closed(IDS[1], ["pantry"], 2)
        self.closed(IDS[2], ["pantry", "other"], 1)
        text = " ".join(self.reasons().get(IDS[1], []))
        self.assertIn("pantry", text)
        self.assertNotIn("other", text)

    # May ignore: old records
    def test_old_records_without_the_new_fields_count_as_never_sent_back(self):
        for sid in IDS:
            self.closed(sid, None, None)
        self.assertEqual(self.reasons(), {})
        self.closed("2026-11-04-d", ["pantry"], 1)
        self.closed("2026-11-05-e", ["pantry"], 1)
        self.assertEqual(self.reasons(), {})

    # 3. the limit
    def test_without_the_key_the_limit_is_three(self):
        self.closed(IDS[0], ["pantry"], 1)
        self.closed(IDS[1], ["pantry"], 1)
        self.assertEqual(self.reasons(), {})
        self.closed(IDS[2], ["pantry"], 1)
        self.assertIn(IDS[2], self.reasons())

    def test_a_lower_limit_makes_two_slices_enough(self):
        self.set_limit(2)
        self.closed(IDS[0], ["pantry"], 1)
        self.closed(IDS[1], ["pantry"], 1)
        self.assertIn("pantry", " ".join(self.reasons().get(IDS[0], [])))

    def test_a_limit_of_zero_turns_the_signal_off(self):
        self.set_limit(0)
        for n in range(1, 6):
            self.closed(f"2026-11-0{n}-s", ["pantry"], 2)
        self.assertEqual(self.reasons(), {})

    # 1. the record keeps the fields at close
    def fake_agents(self):
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=wt)
        return wt

    def record(self, wt):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=wt).stdout)

    def close_s1(self, wt):
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "merge", cwd=wt)
        self.xv("close", "s1", cwd=wt)
        return self.record(wt)

    def test_a_closed_slice_keeps_the_modules_it_touched_and_zero_sendbacks(self):
        wt = self.fake_agents()
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        data = self.close_s1(wt)
        self.assertEqual(data["modules_touched"], ["pantry/store"])
        self.assertEqual(data["maker_sendbacks"], 0)

    def test_a_slice_sent_back_to_the_maker_once_closes_with_one_sendback(self):
        wt = self.fake_agents()
        for agent in ("forecaster", "scenario", "maker", "cleaner"):
            self.xv("step", agent, "s1", cwd=wt)
        with mock.patch.dict(os.environ, {"FAKE_SCENARIO_MISS": MISS}):
            self.xv("step", "guardian", "s1", cwd=wt, check=False)
        self.assertEqual(self.record(wt)["next"], "maker")
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        data = self.close_s1(wt)
        self.assertEqual(data["maker_sendbacks"], 1)
        self.assertEqual(data["modules_touched"], ["pantry/store"])

    def test_a_slice_a_person_sent_back_to_the_maker_closes_with_one_sendback(self):
        wt = self.fake_agents()
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.xv("record", "stop", "s1", "--order", "slice_only_marks", "--seat", "originator",
                "--question", "Is this right?", "--step", "guardian", cwd=wt)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "no, rework the code",
                "--settled", "the maker redoes it", "--next", "maker", cwd=wt)
        self.assertEqual(self.record(wt)["next"], "maker")
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        data = self.close_s1(wt)
        self.assertEqual(data["maker_sendbacks"], 1)

    def test_a_slice_sent_back_through_the_scenario_agent_to_the_maker_closes_with_one_sendback(self):
        wt = self.fake_agents()
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        self.xv("record", "answer", "s1", "--by", "pat", "--answer", "no, the red misses a case",
                "--settled", "the scenario agent adds a red", "--next", "scenario", cwd=wt)
        self.assertEqual(self.record(wt)["next"], "scenario")
        p = self.xv("run", "s1", cwd=wt, check=False)
        self.assertEqual(p.returncode, 10, p.stdout + p.stderr)
        steps = [row["step"] for row in self.record(wt)["spend"]]
        self.assertEqual(steps.count("maker"), 2, steps)
        data = self.close_s1(wt)
        self.assertEqual(data["maker_sendbacks"], 1)

    # 4. the refactor candidate
    def test_the_retro_brief_leaves_out_modules_reworked_before_the_last_retro(self):
        self.three_reworked()
        os.makedirs(os.path.join(self.repo, ".xv", "retro"), exist_ok=True)
        open(os.path.join(self.repo, ".xv", "retro", "2026-11-02.md"), "w").write("# Retro\n")
        seen = []

        def fake_run(argv, text, root, session, timeout):
            seen.append(text)
            out = re.search(r"Write the retro packet to `([^`]+)`", text).group(1)
            with open(os.path.join(root, out), "w") as f:
                f.write("# Retro\n")
            return {"code": 0}

        real = (retro.agentcli.run, retro.agentcli.argv_for)
        retro.agentcli.run, retro.agentcli.argv_for = fake_run, lambda config, agent: ["fake"]
        try:
            retro.run(self.repo, [IDS[0]])
        finally:
            retro.agentcli.run, retro.agentcli.argv_for = real
        self.assertNotIn("was reworked on", seen[0])

    def test_the_retro_brief_names_the_reworked_module_and_asks_for_a_refactor_candidate(self):
        self.three_reworked()
        seen = []

        def fake_run(argv, text, root, session, timeout):
            seen.append(text)
            out = re.search(r"Write the retro packet to `([^`]+)`", text).group(1)
            with open(os.path.join(root, out), "w") as f:
                f.write("# Retro\n")
            return {"code": 0}

        real = (retro.agentcli.run, retro.agentcli.argv_for)
        retro.agentcli.run, retro.agentcli.argv_for = fake_run, lambda config, agent: ["fake"]
        try:
            retro.run(self.repo, [IDS[0]])
        finally:
            retro.agentcli.run, retro.agentcli.argv_for = real
        self.assertIn("pantry", seen[0])
        self.assertIn("kind: refactor", seen[0])

    def test_accepting_a_refactor_candidate_prints_the_slice_new_command_and_opens_nothing(self):
        path = os.path.join(self.repo, "retro.md")
        with open(path, "w") as f:
            f.write("### 1. Refactor pantry\n- kind: refactor\n"
                    f"- from: {IDS[0]}, the maker_sendbacks field\n"
                    "- miss: three slices went back to the maker on pantry\n")
        branches = sh(["git", "branch", "--list", "xv/*"], self.repo).stdout
        slices = sorted(os.listdir(os.path.join(self.repo, ".xv", "slices")))
        p = self.xv("retro", "accept", path, "1", "--by", "pat", check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("xv slice new", p.stdout)
        self.assertIn("--kind refactor", p.stdout)
        self.assertEqual(sh(["git", "branch", "--list", "xv/*"], self.repo).stdout, branches)
        self.assertEqual(sorted(os.listdir(os.path.join(self.repo, ".xv", "slices"))), slices)


if __name__ == "__main__":
    unittest.main()

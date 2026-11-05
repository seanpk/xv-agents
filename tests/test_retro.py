import os
import re
import shutil
import unittest

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


if __name__ == "__main__":
    unittest.main()

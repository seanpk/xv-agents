import os
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


if __name__ == "__main__":
    unittest.main()

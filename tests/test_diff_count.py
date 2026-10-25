import json
import os
import sys
import unittest

from helpers import RepoCase, sh

HERE = os.path.dirname(os.path.abspath(__file__))
FAKE = os.path.join(HERE, "fake_agent.py")

# What the stand-in scenario and maker leave outside .xv/, counted by hand:
# tests/test_red.py is 10 new lines; pantry/store.py changes one line (1 added, 1 deleted).
OUTSIDE_XV = 10 + 2


class DiffCountTest(RepoCase):
    def setUp(self):
        super().setUp()
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        text = open(cfg).read()
        start, end = text.index("agents:"), text.index("seats:")
        text = text[:start] + f'agents:\n  default: ["{sys.executable}", "{FAKE}", "{{prompt}}"]\n' + text[end:]
        open(cfg, "w").write(text)
        sh(["git", "commit", "-qam", "fake agents"], self.repo)
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.xv("record", "set", "s1", "budget", '{"usd": 1}', "--by", "pat", cwd=self.wt)

    def record(self):
        return json.loads(self.xv("record", "show", "s1", "--json", cwd=self.wt).stdout)

    def test_diff_lines_leaves_out_what_the_record_writes_under_xv(self):
        for agent in ("forecaster", "scenario", "maker"):
            self.xv("step", agent, "s1", cwd=self.wt)
        # the slice record under .xv/ has changed since the base; it must not count
        self.assertEqual(self.record()["checks"]["maker"]["diff_lines"], OUTSIDE_XV)

    def test_a_file_under_xv_added_before_the_cleaner_does_not_grow_the_count(self):
        for agent in ("forecaster", "scenario", "maker"):
            self.xv("step", agent, "s1", cwd=self.wt)
        packet = os.path.join(self.wt, ".xv", "slices", "s1.packet.md")
        with open(packet, "w") as f:
            f.write("".join(f"line {i}\n" for i in range(200)))
        sh(["git", "add", "-A"], self.wt)
        sh(["git", "commit", "-qm", "a packet the guardian wrote"], self.wt)
        self.xv("step", "cleaner", "s1", cwd=self.wt, check=False)
        self.assertEqual(self.record()["checks"]["cleaner"]["diff_lines"], OUTSIDE_XV)


if __name__ == "__main__":
    unittest.main()

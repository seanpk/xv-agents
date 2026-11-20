"""#168: the old agent names still work until #204 drops them, each with a one-line warning on stderr
that names the new name and #204."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import HOME, XV, RepoCase, sh
from test_run import WatchLoopSetup

import xvlib
from xvlib import split_front_matter, upgrade_config

DROP = "#204 (Drop the old agent names kept after the #168 rename)"

OLD_RECORD = """---
id: s1
next: guardian
step_start: {"agent": "scenario", "commit": "abc"}
checks: {"scenario": {"red_fails": true}, "guardian": {"packet_head": "def"}, "reports": [{"agent": "scenario", "status": "red"}, {"agent": "guardian", "status": "done"}]}
stops: [{"order": "guardian_stopped", "step": "guardian", "sendback": {"to": "scenario", "misses": ["1"]}, "sendback_to": "scenario"}]
spend: [{"step": "scenario", "usd": 0.1}, {"step": "guardian", "usd": 0.2}]
pairings: [{"n": 1, "step": "guardian", "next": "scenario"}]
---
body
"""


def warnings_of(fn, *args):
    """What `fn` prints on stderr, with the once-per-process memory cleared first."""
    xvlib._warned.clear()
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        out = fn(*args)
    return out, err.getvalue()


class OldNamesInARecordTest(unittest.TestCase):
    def test_old_step_names_in_next_step_start_checks_and_reports_read_as_the_new_ones(self):
        data, err = warnings_of(lambda: split_front_matter(OLD_RECORD)[0])
        self.assertEqual(data["next"], "inspector")
        self.assertEqual(data["step_start"]["agent"], "test-writer")
        self.assertEqual(set(data["checks"]), {"test-writer", "inspector", "reports"})
        self.assertEqual([r["agent"] for r in data["checks"]["reports"]], ["test-writer", "inspector"])

    def test_old_step_names_in_stops_spend_and_pairings_read_as_the_new_ones(self):
        data, _ = warnings_of(lambda: split_front_matter(OLD_RECORD)[0])
        stop = data["stops"][0]
        self.assertEqual((stop["order"], stop["step"], stop["sendback_to"], stop["sendback"]["to"]),
                         ("inspector_stopped", "inspector", "test-writer", "test-writer"))
        self.assertEqual([s["step"] for s in data["spend"]], ["test-writer", "inspector"])
        self.assertEqual((data["pairings"][0]["step"], data["pairings"][0]["next"]), ("inspector", "test-writer"))

    def test_each_old_name_warns_once_on_one_line_naming_the_new_name_and_204(self):
        _, err = warnings_of(lambda: split_front_matter(OLD_RECORD)[0])
        lines = err.strip().splitlines()
        self.assertTrue(lines)
        for line in lines:
            self.assertIn(DROP, line)
        self.assertTrue(any("'guardian'" in l and "'inspector'" in l for l in lines), err)
        self.assertTrue(any("'scenario'" in l and "'test-writer'" in l for l in lines), err)
        self.assertEqual(len(lines), len(set(lines)), "a warning repeated")

    def test_a_record_with_only_new_names_warns_nothing(self):
        new = OLD_RECORD.replace("guardian_stopped", "inspector_stopped").replace("guardian", "inspector") \
            .replace("scenario", "test-writer")
        _, err = warnings_of(lambda: split_front_matter(new)[0])
        self.assertEqual(err, "")


class OldConfigKeysTest(unittest.TestCase):
    OLD = {"agents": {"default": ["d"], "scenario": ["s"], "guardian": ["g"], "guardian_repass": ["r"],
                      "listener": ["l"]},
           "listener": {"days": 3}}

    def test_old_agent_keys_and_the_listener_block_read_under_the_new_names(self):
        config, _ = warnings_of(upgrade_config, self.OLD)
        self.assertEqual(config["agents"], {"default": ["d"], "test-writer": ["s"], "inspector": ["g"],
                                            "inspector_repass": ["r"], "field-listener": ["l"]})
        self.assertEqual(config["field_listener"], {"days": 3})
        self.assertNotIn("listener", config)

    def test_each_old_key_warns_with_the_new_key_and_204(self):
        _, err = warnings_of(upgrade_config, self.OLD)
        for old, new in (("agents.guardian ", "agents.inspector"), ("agents.guardian_repass", "agents.inspector_repass"),
                         ("listener:", "field_listener:")):
            line = [l for l in err.splitlines() if old in l]
            self.assertTrue(line, f"no warning for {old}: {err}")
            self.assertIn(new, line[0])
            self.assertIn(DROP, line[0])

    def test_a_new_key_wins_over_its_old_one(self):
        config, _ = warnings_of(upgrade_config, {"agents": {"guardian": ["old"], "inspector": ["new"]}})
        self.assertEqual(config["agents"], {"inspector": ["new"]})

    def test_load_config_reads_an_old_config_file(self):
        root = tempfile.mkdtemp(prefix="xv-old-config-")
        os.makedirs(os.path.join(root, ".xv"))
        with open(os.path.join(root, ".xv", "config.yml"), "w") as f:
            f.write('agents:\n  guardian: ["g"]\nlistener:\n  days: 3\n')
        config, err = warnings_of(xvlib.load_config, root)
        self.assertEqual(config["agents"]["inspector"], ["g"])
        self.assertEqual(config["field_listener"]["days"], 3)
        self.assertIn(DROP, err)


class OldNamesOnTheCommandLineTest(WatchLoopSetup):
    def test_xv_step_scenario_runs_the_test_writer_and_warns(self):
        self.xv("step", "forecaster", "s1", cwd=self.wt)
        p = self.xv("step", "scenario", "s1", cwd=self.wt, check=False)
        self.assertIn("'scenario'", p.stderr)
        self.assertIn("'test-writer'", p.stderr)
        self.assertIn(DROP, p.stderr)
        data = self.record()
        self.assertEqual(data["spend"][-1]["step"], "test-writer")
        self.assertIn("test-writer", data["checks"])
        self.assertNotIn("scenario", data["checks"])

    def test_xv_prompt_guardian_is_the_inspectors_prompt_and_warns(self):
        p = self.xv("prompt", "guardian", "s1", cwd=self.wt)
        self.assertTrue(p.stdout.startswith("# The inspector"), p.stdout[:80])
        self.assertIn("'inspector'", p.stderr)
        self.assertIn(DROP, p.stderr)

    def test_next_scenario_on_an_answer_resumes_at_the_test_writer_and_warns(self):
        self.xv("record", "stop", "s1", "--order", "test_writer_stopped", "--seat", "originator",
                "--question", "q?", "--step", "scenario", cwd=self.wt)
        p = self.xv("record", "answer", "s1", "--by", "pat", "--answer", "again", "--next", "scenario",
                    "--settled", "the red is written again", cwd=self.wt)
        self.assertIn(DROP, p.stderr)
        data = self.record()
        self.assertEqual(data["next"], "test-writer")
        self.assertEqual(data["stops"][-1]["step"], "test-writer")

    def test_an_old_name_in_a_saved_record_is_read_with_a_warning_and_the_next_write_saves_the_new_one(self):
        rec = os.path.join(self.wt, ".xv", "slices", "s1.md")
        with open(rec) as f:
            text = f.read()
        with open(rec, "w") as f:
            f.write(text.replace("next: forecaster", "next: scenario", 1))
        p = self.xv("record", "show", "s1", "--json", cwd=self.wt)
        self.assertEqual(json.loads(p.stdout)["next"], "test-writer")
        self.assertIn("'scenario'", p.stderr)
        self.assertIn(DROP, p.stderr)
        self.xv("record", "set", "s1", "budget", '{"usd": 2}', "--by", "pat", cwd=self.wt)
        with open(rec) as f:
            self.assertIn("next: test-writer", f.read())

    def test_xv_guard_runs_the_inspector_and_warns(self):
        sh(["git", "checkout", "-q", "-b", "pr"], self.repo)
        with open(os.path.join(self.repo, "change.txt"), "w") as f:
            f.write("a change\n")
        sh(["git", "add", "-A"], self.repo)
        sh(["git", "commit", "-qm", "a change"], self.repo)
        p = self.xv("guard", "--base", "main", cwd=self.repo, check=False)
        self.assertIn("`xv guard`", p.stderr)
        self.assertIn("`xv inspect`", p.stderr)
        self.assertIn(DROP, p.stderr)
        self.assertIn("after", json.loads(p.stdout))


class InstallDropsOldNamesTest(unittest.TestCase):
    def run_install(self, home, *args):
        env = dict(os.environ, HOME=home, PATH=os.environ["PATH"])
        env.pop("CLAUDE_CONFIG_DIR", None)
        p = subprocess.run([sys.executable, XV, "install", *args], cwd=home, env=env, capture_output=True, text=True)
        return p.returncode, json.loads(p.stdout), p.stderr

    def test_a_user_install_links_the_new_folders_and_removes_its_links_under_the_old_names(self):
        home = tempfile.mkdtemp(prefix="xv-home-")
        skills = os.path.join(home, ".claude", "skills")
        os.makedirs(skills)
        for old in ("scenario", "guardian", "listener"):
            os.symlink(os.path.join(HOME, "skills", old), os.path.join(skills, old))  # as an earlier install left it
        code, res, err = self.run_install(home)
        self.assertEqual(code, 0, err)
        for old, new in (("scenario", "test-writer"), ("guardian", "inspector"), ("listener", "field-listener")):
            self.assertFalse(os.path.lexists(os.path.join(skills, old)), old)
            self.assertTrue(os.path.islink(os.path.join(skills, new)), new)
        self.assertEqual(len(res["removed_old_names"]), 3)

    def test_a_folder_under_an_old_name_that_is_not_ours_stays(self):
        home = tempfile.mkdtemp(prefix="xv-home-")
        mine = os.path.join(home, ".claude", "skills", "listener")
        os.makedirs(mine)
        code, res, err = self.run_install(home)
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.isdir(mine))
        self.assertNotIn("removed_old_names", res)


class AdaptDropsOldNamesTest(RepoCase):
    def test_adapt_writes_the_new_file_and_removes_the_one_it_wrote_under_the_old_name(self):
        agents = os.path.join(self.repo, ".claude", "agents")
        os.makedirs(agents)
        old = os.path.join(agents, "xv-guardian.md")
        with open(old, "w") as f:
            f.write("---\nname: xv-guardian\n---\n\n<!-- generated by xv adapt from skills/guardian/SKILL.md "
                    "(0123456789ab). Do not edit. -->\n")
        p = self.xv("adapt", "claude", "--agents", "guardian")
        self.assertIn(DROP, p.stderr)
        self.assertTrue(os.path.exists(os.path.join(agents, "xv-inspector.md")))
        self.assertFalse(os.path.exists(old))


class OldNameInAPacketMissTest(unittest.TestCase):
    def test_a_miss_sent_to_scenario_goes_to_the_test_writer(self):
        import packet
        body = "## Scenario misses\n\n- outcome 2: not shown (evidence: tests/a.py:3) to: scenario\n"
        found, err = warnings_of(packet.misses, body)
        self.assertEqual(found[0]["to"], "test-writer")
        self.assertIn(DROP, err)


if __name__ == "__main__":
    unittest.main()

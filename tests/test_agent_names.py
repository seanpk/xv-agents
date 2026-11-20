"""#168: the agents have the names the site uses (test-writer, inspector, field-listener).

Expected values are the names in the scenario, not anything read from the code.
"""
import glob
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from helpers import HOME, XV, RepoCase, sh

import agentcli
import listen

OLD_STOPS = "An agent may stop. It may not decide."


def read(*parts):
    with open(os.path.join(HOME, *parts), encoding="utf-8") as f:
        return f.read()


def doc_files():
    out = [os.path.join(HOME, "README.md")]
    for pattern in ("docs/*.md", "skills/*/SKILL.md", "skills/*/*.md", ".xv/picture.md"):
        out += glob.glob(os.path.join(HOME, pattern))
    return sorted(set(out))


def run_xv_in(args, cwd, home):
    env = dict(os.environ, HOME=home)
    env.pop("CLAUDE_CONFIG_DIR", None)
    return subprocess.run([sys.executable, XV] + args, cwd=cwd, env=env, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)


def json_in(text):
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


class TreeNamesTest(unittest.TestCase):
    # 1, 2, 3, 15
    def test_the_skill_folders_have_the_new_names(self):
        for new in ("test-writer", "inspector", "field-listener"):
            self.assertTrue(os.path.isfile(os.path.join(HOME, "skills", new, "SKILL.md")), new)
        for old in ("scenario", "guardian", "listener"):
            self.assertFalse(os.path.exists(os.path.join(HOME, "skills", old)), old)

    def test_the_ci_example_is_the_inspectors(self):
        ci = os.path.join(HOME, "ci", "github")
        self.assertTrue(os.path.isfile(os.path.join(ci, "xv-inspector.yml")))
        self.assertFalse(os.path.exists(os.path.join(ci, "xv-guardian.yml")))
        self.assertIn("xv inspect --base", read("ci", "github", "xv-inspector.yml"))
        self.assertNotIn("xv guard", read("ci", "github", "xv-inspector.yml"))

    def test_explore_notes_is_not_in_the_tree(self):
        self.assertFalse(os.path.exists(os.path.join(HOME, "EXPLORE-NOTES.md")))
        self.assertEqual(sh(["git", "ls-files", "EXPLORE-NOTES.md"], HOME).stdout.strip(), "")

    # 13: names inside the code
    def test_no_script_or_ci_file_is_named_for_an_old_agent_name(self):
        bad = []
        for top in ("scripts", "ci"):
            for root, _d, names in os.walk(os.path.join(HOME, top)):
                for n in names:
                    if any(w in n for w in ("scenario", "guardian", "listener")):
                        bad.append(os.path.join(root, n))
        self.assertEqual(bad, [])

    def test_the_internal_step_is_land_test_writer(self):
        run_py = read("scripts", "run.py")
        self.assertIn("land-test-writer", run_py)
        self.assertNotIn("land-scenario", run_py)
        self.assertIn("xv-test-writer-scratch-", run_py + read("scripts", "record.py"))

    def test_the_xv_command_names_inspect_and_keeps_listen(self):
        p = sh([sys.executable, XV, "inspect", "--help"], HOME, check=False)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("--base", p.stdout)
        p = sh([sys.executable, XV, "listen", "--help"], HOME, check=False)
        self.assertEqual(p.returncode, 0, p.stderr)


class EvalIdsTest(unittest.TestCase):
    # 14
    def scenario_docs(self):
        for path in glob.glob(os.path.join(HOME, "evals", "scenarios", "*.json")):
            with open(path) as f:
                yield json.load(f)

    def test_the_scenario_files_carry_the_new_ids(self):
        names = {d["name"] for d in self.scenario_docs()}
        for new in ("inspector-pitch", "inspector-moves", "field-report",
                    "test-writer-defect", "test-writer-feature", "test-writer-har"):
            self.assertIn(new, names)
        for old in ("guardian-pitch", "guardian-moves", "listener-packet",
                    "scenario-defect", "scenario-feature", "scenario-har"):
            self.assertNotIn(old, names)

    def test_an_eval_scenario_names_its_agent_by_the_new_name(self):
        agents = {d.get("agent") for d in self.scenario_docs()}
        for old in ("scenario", "guardian", "listener"):
            self.assertNotIn(old, agents)

    def test_the_report_shows_a_past_result_and_a_new_one_on_one_row(self):
        sys.path.insert(0, os.path.join(HOME, "evals"))
        try:
            import report
        finally:
            sys.path.pop(0)
        base = {"arm": "skill", "increment": 1, "passed": 2, "total": 3}
        runs = [dict(base, harness="claude", scenario="guardian-pitch"),
                dict(base, harness="codex", scenario="inspector-pitch")]
        rows = [r for r in report.table(runs).splitlines() if "pitch" in r]
        self.assertEqual(len(rows), 1, rows)
        self.assertIn("inspector-pitch", rows[0])
        self.assertNotIn("guardian-pitch", rows[0])
        self.assertEqual(rows[0].count("2/3"), 2)


class ProseTest(unittest.TestCase):
    # 7, 8, 9
    def test_no_brief_or_doc_opens_with_the_old_line(self):
        found = [os.path.relpath(p, HOME) for p in doc_files() if OLD_STOPS in open(p, encoding="utf-8").read()]
        self.assertEqual(found, [])

    def test_boundary_picture_is_boundary_diagram(self):
        found = [os.path.relpath(p, HOME) for p in doc_files()
                 if "boundary picture" in open(p, encoding="utf-8").read().lower()]
        self.assertEqual(found, [])

    def test_the_two_packets_have_their_prose_names(self):
        for p in doc_files():
            t = open(p, encoding="utf-8").read().lower()
            for old in ("guardian's packet", "listener's packet", "guardian packet", "listener packet"):
                self.assertNotIn(old, t, os.path.relpath(p, HOME))
        readme = read("README.md").lower()
        self.assertIn("inspection report", readme)
        self.assertIn("field report", readme)

    def test_the_briefs_name_the_new_agents(self):
        self.assertIn("name: test-writer", read("skills", "test-writer", "SKILL.md"))
        self.assertIn("name: inspector", read("skills", "inspector", "SKILL.md"))
        self.assertIn("name: field-listener", read("skills", "field-listener", "SKILL.md"))


class ConfigNamesTest(RepoCase):
    # 4, 5: config keys
    def warn_text(self, fn):
        err, out = io.StringIO(), io.StringIO()
        with redirect_stderr(err), redirect_stdout(out):
            result = fn()
        return result, err.getvalue() + out.getvalue()

    def test_the_new_agent_keys_have_hyphens_and_the_other_keys_keep_underscores(self):
        cfg = {"agents": {"default": ["d"], "test-writer": ["tw"], "inspector": ["i"],
                          "inspector_repass": ["ir"], "field-listener": ["fl"]}}
        self.assertEqual(agentcli.argv_for(cfg, "test-writer"), ["tw"])
        self.assertEqual(agentcli.argv_for(cfg, "inspector"), ["i"])
        self.assertEqual(agentcli.argv_for(cfg, "inspector", repass=True), ["ir"])
        self.assertEqual(agentcli.argv_for(cfg, "field-listener"), ["fl"])

    def test_the_old_agent_keys_still_work_and_warn_once_with_the_new_name_and_204(self):
        cfg = {"agents": {"default": ["d"], "scenario": ["old-s"], "guardian": ["old-g"],
                          "guardian_repass": ["old-gr"], "listener": ["old-l"]}}
        for agent, repass, want, new in (("test-writer", False, ["old-s"], "agents.test-writer"),
                                         ("inspector", False, ["old-g"], "agents.inspector"),
                                         ("inspector", True, ["old-gr"], "agents.inspector_repass"),
                                         ("field-listener", False, ["old-l"], "agents.field-listener")):
            got, text = self.warn_text(lambda: agentcli.argv_for(cfg, agent, repass=repass))
            self.assertEqual(got, want, agent)
            self.assertIn(new, text)
            self.assertEqual(len([ln for ln in text.splitlines() if "#204" in ln]), 1, text)

    def test_a_new_key_wins_over_an_old_one_and_a_new_config_is_silent(self):
        cfg = {"agents": {"default": ["d"], "test-writer": ["new"], "scenario": ["old"]}}
        got, _ = self.warn_text(lambda: agentcli.argv_for(cfg, "test-writer"))
        self.assertEqual(got, ["new"])
        cfg = {"agents": {"default": ["d"], "test-writer": ["new"]}}
        _, text = self.warn_text(lambda: agentcli.argv_for(cfg, "test-writer"))
        self.assertNotIn("#204", text)

    def test_the_old_listener_key_is_read_and_warns_and_the_new_one_is_read_silently(self):
        os.makedirs(os.path.join(self.repo, "support"))
        with open(os.path.join(self.repo, "support", "a.txt"), "w") as f:
            f.write("it broke\n")
        cfg = os.path.join(self.repo, ".xv", "config.yml")
        base = open(cfg).read()
        for key, warns in (("listener", True), ("field_listener", False)):
            with open(cfg, "w") as f:
                f.write(base + key + ':\n  feedback: ["support/*.txt"]\n')
            (out, _notes), text = self.warn_text(lambda: listen.gather(self.repo))
            self.assertEqual(os.listdir(os.path.join(out, "feedback")), ["a.txt"], key)
            self.assertEqual("#204" in text, warns, text)
            if warns:
                self.assertIn("field_listener", text)


class StepNamesTest(RepoCase):
    # 1, 2, 5, 12, 13: steps, commands and records
    def setUp(self):
        super().setUp()
        self.wt = self.new_slice("s1", "Milk that runs out today shows as running out soon.")
        self.script = os.path.join(self.tmp, "mark.py")
        self.log = os.path.join(self.tmp, "marks.log")
        with open(self.script, "w") as f:
            f.write("import sys\nopen(%r, 'a').write(sys.argv[1] + '\\n')\nprint('done, no report')\n" % self.log)

    def agents(self, **tags):
        lines = "".join('  %s: ["%s", "%s", "%s", "{prompt}"]\n' % (k, sys.executable, self.script, v)
                        for k, v in tags.items())
        cfg = os.path.join(self.wt, ".xv", "config.yml")
        text = open(cfg).read()
        a, b = text.index("agents:"), text.index("seats:")
        with open(cfg, "w") as f:
            f.write(text[:a] + "agents:\n" + lines + text[b:])
        sh(["git", "commit", "-qam", "xv(s1): agents"], self.wt)

    def ran(self):
        return open(self.log).read().split() if os.path.exists(self.log) else []

    def out(self, *args):
        p = self.xv(*args, cwd=self.wt, check=False)
        return p.stdout + p.stderr

    def test_the_new_step_name_runs_its_configured_agent_without_a_warning(self):
        self.agents(**{"test-writer": "tw"})
        text = self.out("step", "test-writer", "s1")
        self.assertEqual(self.ran(), ["tw"], text)
        self.assertNotIn("#204", text)

    def test_the_old_scenario_step_still_runs_and_warns_with_the_new_name_and_204(self):
        self.agents(**{"test-writer": "tw"})
        text = self.out("step", "scenario", "s1")
        self.assertEqual(self.ran(), ["tw"], text)
        self.assertIn("test-writer", text)
        self.assertIn("#204", text)

    def test_the_old_guardian_step_runs_the_inspector_and_warns(self):
        self.agents(inspector="insp")
        text = self.out("step", "guardian", "s1")
        self.assertEqual(self.ran(), ["insp"], text)
        self.assertIn("inspector", text)
        self.assertIn("#204", text)

    def test_the_prompt_for_an_old_step_name_is_the_new_steps_prompt_and_warns(self):
        new = self.xv("prompt", "test-writer", "s1", cwd=self.wt).stdout
        p = self.xv("prompt", "scenario", "s1", cwd=self.wt)
        self.assertEqual(p.stdout, new)
        self.assertIn("test-writer", p.stderr)
        self.assertIn("#204", p.stderr)

    def test_xv_guard_still_works_and_warns_that_it_is_xv_inspect(self):
        old = self.out("guard", "--base", "main")
        self.assertIn("xv inspect", old)
        self.assertIn("#204", old)
        self.assertNotIn("#204", self.out("inspect", "--base", "main"))

    def set_front(self, **fields):
        path = os.path.join(self.wt, ".xv", "slices", "s1.md")
        text = open(path).read()
        head, rest = text.split("\n---\n", 1)
        lines = [ln for ln in head.split("\n") if ln.split(":")[0] not in fields]
        lines += ["%s: %s" % (k, v) for k, v in fields.items()]
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n---\n" + rest)

    def test_an_open_record_with_an_old_step_name_reads_new_and_warns_once(self):
        self.set_front(next="scenario", status="working")
        p = self.xv("record", "show", "s1", "--json", cwd=self.wt)
        self.assertEqual(json_in(p.stdout)["next"], "test-writer")
        self.assertEqual(len([ln for ln in p.stderr.splitlines() if "#204" in ln]), 1, p.stderr)
        self.assertIn("test-writer", p.stderr)

    def test_old_names_in_checks_reports_and_step_start_read_new(self):
        self.set_front(next="guardian", status="working",
                       step_start='{"agent": "scenario", "commit": "-"}',
                       checks='{"reports": [{"agent": "guardian", "status": "done", "summary": "s"}]}')
        p = self.xv("record", "show", "s1", "--json", cwd=self.wt)
        data = json_in(p.stdout)
        self.assertEqual(data["next"], "inspector")
        self.assertEqual(data["step_start"]["agent"], "test-writer")
        self.assertEqual(data["checks"]["reports"][0]["agent"], "inspector")
        self.assertIn("#204", p.stderr)

    def test_a_closed_record_reads_its_old_names_with_no_warning(self):
        self.set_front(next="scenario", status="closed",
                       checks='{"reports": [{"agent": "guardian", "status": "done", "summary": "s"}]}')
        p = self.xv("record", "show", "s1", "--json", cwd=self.wt)
        self.assertNotIn("#204", p.stdout + p.stderr)
        self.assertEqual(json_in(p.stdout)["checks"]["reports"][0]["agent"], "inspector")

    def test_an_abandoned_record_reads_its_old_names_with_no_warning(self):
        self.set_front(next="guardian", status="abandoned")
        p = self.xv("record", "show", "s1", "--json", cwd=self.wt)
        self.assertNotIn("#204", p.stdout + p.stderr)
        self.assertEqual(json_in(p.stdout)["next"], "inspector")


class InstallNamesTest(unittest.TestCase):
    # 6
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="xv-home-")
        self.skills = os.path.join(self.home, ".claude", "skills")
        os.makedirs(self.skills)
        for old in ("scenario", "guardian", "listener"):  # links an older xv made
            os.symlink(os.path.join(HOME, "skills", old), os.path.join(self.skills, old))

    def test_install_links_the_new_folders_and_removes_its_old_links(self):
        p = run_xv_in(["install"], self.home, self.home)
        self.assertEqual(p.returncode, 0, p.stderr)
        for new in ("test-writer", "inspector", "field-listener"):
            self.assertTrue(os.path.islink(os.path.join(self.skills, new)), new)
        for old in ("scenario", "guardian", "listener"):
            self.assertFalse(os.path.lexists(os.path.join(self.skills, old)), old)

    def test_install_leaves_alone_an_old_name_folder_someone_else_made(self):
        os.remove(os.path.join(self.skills, "scenario"))
        os.makedirs(os.path.join(self.skills, "scenario"))
        p = run_xv_in(["install"], self.home, self.home)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.skills, "scenario")))
        self.assertFalse(os.path.islink(os.path.join(self.skills, "scenario")))


class SliceOnlyTest(unittest.TestCase):
    # 10, 11: one-time wording
    def test_changelog_has_a_line_for_the_new_names(self):
        unreleased = read("CHANGELOG.md").split("## Unreleased", 1)[1].split("\n## ", 1)[0]
        for name in ("#168", "test-writer", "inspector", "field-listener", "#204"):
            self.assertIn(name, unreleased)

    def test_the_readme_upgrade_notes_say_what_an_adopter_changes(self):
        readme = read("README.md")
        for text in ("agents.test-writer", "agents.inspector_repass", "field_listener",
                     "xv-inspector.yml", "xv inspect --base"):
            self.assertIn(text, readme)


# What a person should watch on the first green run: `xv step scenario <id>` on a
# working slice prints one warning line naming test-writer and #204, and then runs;
# `xv install` leaves ~/.claude/skills with test-writer, inspector and field-listener
# and none of the old three; a closed slice record shows with no warning.

if __name__ == "__main__":
    unittest.main()

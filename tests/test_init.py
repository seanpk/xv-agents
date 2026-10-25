import json
import os
import shutil
import stat
import tempfile
import unittest

from helpers import RepoCase, sh

from xvlib import load_config


class InitTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)

    def test_init_writes_the_layer_and_guesses_tests_and_roots(self):
        self.xv("init")
        config = load_config(self.repo)
        self.assertEqual(config["tests"]["command"], "python3 -m unittest discover -s tests -t .")
        self.assertEqual(config["source"]["roots"], ["pantry"])
        self.assertTrue(config["promote"]["include_name"])
        for name in ("pitch.md", "picture.md", "standards.md", "estimation.md", "learnings.md", "rules.md"):
            self.assertTrue(os.path.exists(os.path.join(self.repo, ".xv", name)), name)
        self.assertIn("- pantry/api: pantry/api.py", open(os.path.join(self.repo, ".xv", "boundary-all.md")).read())
        status = sh(["git", "status", "--porcelain", "--ignored", ".xv/boundary-all.md"], self.repo).stdout
        self.assertTrue(status.startswith("!!"), "the outsider read's input stays out of the repo")

    def test_a_src_layout_puts_src_on_the_path(self):
        os.makedirs(os.path.join(self.repo, "src"))
        self.xv("init")
        self.assertTrue(load_config(self.repo)["tests"]["command"].startswith("PYTHONPATH=src "))

    def test_init_never_overwrites(self):
        os.makedirs(os.path.join(self.repo, ".xv"))
        with open(os.path.join(self.repo, ".xv", "pitch.md"), "w") as f:
            f.write("ours\n")
        out = self.xv("init").stdout
        self.assertIn('"pitch.md"', out.split('"kept"')[1])
        self.assertEqual(open(os.path.join(self.repo, ".xv", "pitch.md")).read(), "ours\n")

    def touch(self, *parts):
        path = os.path.join(self.repo, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").close()

    def test_a_rails_app_with_a_package_json_gets_rspec_and_asks_which_runner(self):
        self.touch("package.json")
        self.touch("Gemfile")
        self.touch("spec", "a_spec.rb")
        self.touch("tests", "a.test.js")
        out = json.loads(self.xv("init").stdout)
        self.assertEqual(out["tests"]["command"], "bundle exec rspec")
        self.assertEqual([r["marker"] for r in out["runners"]], ["Gemfile", "package.json"])
        self.assertEqual(out["runners"][1]["command"], "npm test")
        self.assertIn("spec/**", out["tests"]["paths"])
        self.assertIn("**/*.test.*", out["tests"]["paths"])

    def test_the_runner_whose_test_folder_exists_wins(self):
        self.touch("package.json")
        self.touch("Gemfile")
        self.touch("e2e", "a.js")
        out = json.loads(self.xv("init").stdout)
        self.assertEqual(out["tests"]["command"], "npm test")
        self.assertEqual(len(out["runners"]), 2)

    def test_a_gemfile_with_only_test_runs_rake_and_one_runner_is_not_listed(self):
        self.touch("Gemfile")
        self.touch("test", "a_test.rb")
        out = json.loads(self.xv("init").stdout)
        self.assertEqual(out["tests"]["command"], "bundle exec rake test")
        self.assertNotIn("runners", out)

    def test_a_rails_layout_proposes_app_lib_and_the_javascript_in_app(self):
        self.touch("config", "routes.rb")
        self.touch("app", "models", "a.rb")
        self.touch("app", "javascript", "a.js")
        self.touch("lib", "b.rb")
        self.xv("init")
        self.assertEqual(load_config(self.repo)["source"]["roots"], ["app", "lib", "app/javascript"])

    def with_fake_gh(self, payload):
        bin_dir = tempfile.mkdtemp(prefix="xv-gh-")
        self.addCleanup(shutil.rmtree, bin_dir, True)
        gh = os.path.join(bin_dir, "gh")
        with open(gh, "w") as f:
            f.write(f"#!/bin/sh\necho '{json.dumps(payload)}'\n")
        os.chmod(gh, os.stat(gh).st_mode | stat.S_IXUSR)
        old = os.environ["PATH"]
        os.environ["PATH"] = bin_dir + os.pathsep + old
        self.addCleanup(os.environ.__setitem__, "PATH", old)

    def test_a_private_repo_does_not_share_its_name_by_default(self):
        self.with_fake_gh({"nameWithOwner": "acme/app", "description": "d", "isPrivate": True})
        self.xv("init")
        promote = load_config(self.repo)["promote"]
        self.assertEqual((promote["include_name"], promote["name"]), (False, "acme/app"))

    def test_a_public_repo_keeps_the_name_on(self):
        self.with_fake_gh({"nameWithOwner": "acme/app", "description": "d", "isPrivate": False})
        self.xv("init")
        self.assertTrue(load_config(self.repo)["promote"]["include_name"])


class TrialRepoTest(RepoCase):
    def setUp(self):
        super().setUp()
        shutil.rmtree(os.path.join(self.repo, ".xv"))
        sh(["git", "commit", "-qam", "no project layer"], self.repo)
        self.inner = os.path.join(self.repo, ".xv")
        self.kept = os.path.join(self.repo, ".git", "xv-trial.git")

    def commit_inside(self):
        sh(["git", "-C", self.inner, "add", "-A"], self.repo)
        sh(["git", "-C", self.inner, "-c", "user.name=t", "-c", "user.email=t@example.com",
            "commit", "-qm", "layer"], self.repo)

    def test_repo_without_trial_is_an_error(self):
        p = self.xv("init", "--repo", check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("--repo goes with --trial", p.stderr)

    def test_trial_repo_makes_xv_its_own_uncommitted_repo(self):
        out = json.loads(self.xv("init", "--trial", "--repo").stdout)
        self.assertTrue(os.path.isdir(os.path.join(self.inner, ".git")))
        self.assertEqual(sh(["git", "-C", self.inner, "rev-list", "--all", "--count"], self.repo).stdout.strip(), "0")
        self.assertIn("Commit inside it", out["next"])
        self.assertEqual(sh(["git", "status", "--porcelain"], self.repo).stdout, "")

    def test_adopt_moves_the_trial_repo_aside_and_says_where(self):
        self.xv("init", "--trial", "--repo")
        self.commit_inside()
        sh(["git", "-C", self.inner, "remote", "add", "origin", "git@example.com:me/trial.git"], self.repo)
        out = json.loads(self.xv("init", "--adopt").stdout)
        self.assertEqual(out["trial_repo"], {"moved_to": self.kept, "origin": "git@example.com:me/trial.git"})
        self.assertFalse(os.path.exists(os.path.join(self.inner, ".git")))
        self.assertEqual(sh(["git", "--git-dir", self.kept, "rev-list", "--count", "HEAD"], self.repo).stdout.strip(), "1")
        self.assertIn(".xv/config.yml", sh(["git", "status", "--porcelain", "-uall"], self.repo).stdout)

    def test_adopt_refuses_while_the_trial_repo_has_uncommitted_changes(self):
        self.xv("init", "--trial", "--repo")
        p = self.xv("init", "--adopt", check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("not committed there", p.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.inner, ".git")))

    def test_adopt_will_not_overwrite_an_earlier_trial_repo(self):
        self.xv("init", "--trial", "--repo")
        self.commit_inside()
        os.makedirs(self.kept)
        p = self.xv("init", "--adopt", check=False)
        self.assertEqual(p.returncode, 2)
        self.assertIn("already exists", p.stderr)
        self.assertTrue(os.path.isdir(os.path.join(self.inner, ".git")))


if __name__ == "__main__":
    unittest.main()

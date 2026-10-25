import os
import unittest

from helpers import HOME, RepoCase, sh

import boundary


class BoundaryTest(RepoCase):
    def test_a_new_outbound_module_and_route_are_shape_hints(self):
        sh(["git", "apply", os.path.join(HOME, "evals", "setups", "share-with-grocer.patch")], self.repo)
        res = boundary.change(self.repo, "HEAD")
        self.assertEqual(res["modules_added"], ["pantry/grocer"])
        self.assertIn(["pantry/api", "pantry/grocer"], [list(e) for e in res["edges_added"]])
        self.assertEqual(res["outbound_added"], ["pantry/grocer"])
        self.assertEqual(res["surfaces"]["added"], ["/share"])
        self.assertEqual(len(res["shape_hints"]), 4)

    def test_a_message_change_has_no_shape_hints(self):
        sh(["git", "apply", os.path.join(HOME, "evals", "setups", "message-wording.patch")], self.repo)
        self.assertEqual(boundary.change(self.repo, "HEAD")["shape_hints"], [])

    def test_the_whole_repo_picture_names_the_modules(self):
        text = boundary.render_all(self.repo)
        self.assertIn("- pantry/api: pantry/api.py", text)
        self.assertIn("m1 --> m2", text)  # pantry/api -> pantry/store

    def test_a_module_under_a_nested_root_is_named_with_the_root(self):
        config = {"source": {"roots": [".", "app", "app/javascript", "app/javascript/shared"]}}
        names = {p: boundary.module_of(p, config) for p in (
            "app/controllers/a.rb", "app/javascript/controllers/a.js", "config/routes.rb",
            "app/javascript/config/a.js", "app/helpers/a.rb", "app/javascript/helpers/a.js",
            "app/javascript/shared/helpers/a.js", "app/strategies/a.rb", "app/javascript/shared/strategies/a.js")}
        self.assertEqual(len(set(names.values())), len(names))
        self.assertEqual(names["app/javascript/shared/helpers/a.js"], "app/javascript/shared/helpers")
        self.assertEqual(names["config/routes.rb"], "config")  # root "." keeps its names

    def test_a_file_directly_under_a_nested_root(self):
        config = {"source": {"roots": [".", "app"]}}
        self.assertEqual(boundary.module_of("app/foo.rb", config), "app/foo")
        self.assertEqual(boundary.module_of("app/index.js", config), "app")
        self.assertEqual(boundary.module_of("top.py", config), "top")

    def test_an_import_between_same_named_folders_is_an_edge(self):
        config = {"source": {"roots": [".", "app", "app/javascript"]}}
        files = {"app/controllers/a.rb": "require_relative '../javascript/controllers/b'\n",
                 "app/javascript/controllers/b.rb": "x = 1\n"}
        g = boundary.graph(files.get, list(files), config)
        self.assertEqual(g["edges"], [("app/controllers", "app/javascript/controllers")])


if __name__ == "__main__":
    unittest.main()

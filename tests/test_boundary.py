import os
import unittest

from helpers import HOME, RepoCase, sh

import boundary


class BoundaryTest(RepoCase):
    def test_a_new_outbound_module_and_route_are_shape_hints(self):
        sh(["git", "apply", os.path.join(HOME, "evals", "setups", "share-with-grocer.patch")], self.repo)
        res = boundary.change(self.repo, "HEAD")
        self.assertEqual(res["modules_added"], ["grocer"])
        self.assertIn(["api", "grocer"], [list(e) for e in res["edges_added"]])
        self.assertEqual(res["outbound_added"], ["grocer"])
        self.assertEqual(res["surfaces"]["added"], ["/share"])
        self.assertEqual(len(res["shape_hints"]), 4)

    def test_a_message_change_has_no_shape_hints(self):
        sh(["git", "apply", os.path.join(HOME, "evals", "setups", "message-wording.patch")], self.repo)
        self.assertEqual(boundary.change(self.repo, "HEAD")["shape_hints"], [])

    def test_the_whole_repo_picture_names_the_modules(self):
        text = boundary.render_all(self.repo)
        self.assertIn("- api: pantry/api.py", text)
        self.assertIn("m0 --> m2", text)  # api -> store


if __name__ == "__main__":
    unittest.main()

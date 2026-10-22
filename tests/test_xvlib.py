import unittest

from helpers import HOME  # noqa: F401  (puts scripts/ on the path)
import xvlib


class FrontMatterTest(unittest.TestCase):
    def test_round_trip_keeps_types(self):
        data = {"id": "s1", "n": 3, "ok": True, "none": None, "yes": "yes",
                "list": [{"file": "a.py", "why": "because: it said so"}], "text": "a: b"}
        text = xvlib.join_front_matter(data, "body\n")
        back, body = xvlib.split_front_matter(text)
        self.assertEqual(back, data)
        self.assertEqual(body, "body\n")

    def test_yes_and_no_stay_words(self):
        text = xvlib.join_front_matter({"shape_change": "no"}, "")
        self.assertIn("shape_change: no\n", text)
        self.assertEqual(xvlib.split_front_matter(text)[0]["shape_change"], "no")

    def test_a_yaml_list_of_bare_words_is_read(self):
        data, _ = xvlib.split_front_matter("---\nsources: [a/b.json, c.txt]\n---\n")
        self.assertEqual(data["sources"], ["a/b.json", "c.txt"])

    def test_a_bad_line_is_refused(self):
        with self.assertRaises(xvlib.XVError):
            xvlib.split_front_matter("---\nthis is not a field\n---\n")


class ConfigTest(unittest.TestCase):
    def test_nested_maps_lists_and_comments(self):
        c = xvlib.parse_config_text(
            "a: 1  # one\n"
            "tests:\n"
            "  paths: [\"tests/**\"]\n"
            "  command: \"make test\"\n"
            "reach:\n"
            "  command:\n"
            "    - notify\n"
            "    - \"{seat}\"\n"
            "empty:\n"
            "after: x\n")
        self.assertEqual(c["a"], 1)
        self.assertEqual(c["tests"], {"paths": ["tests/**"], "command": "make test"})
        self.assertEqual(c["reach"]["command"], ["notify", "{seat}"])
        self.assertIsNone(c["empty"])
        self.assertEqual(c["after"], "x")

    def test_the_default_config_parses(self):
        import os
        with open(os.path.join(HOME, "defaults", "config.yml")) as f:
            c = xvlib.parse_config_text(f.read())
        self.assertIn("default", c["agents"])
        self.assertTrue(c["wall"]["require_record"])

    def test_match_any_treats_double_star_prefix_as_optional(self):
        self.assertTrue(xvlib.match_any("test_x.py", ["**/test_*.py"]))
        self.assertTrue(xvlib.match_any("a/b/test_x.py", ["**/test_*.py"]))
        self.assertTrue(xvlib.match_any("tests/a/b.py", ["tests/**"]))
        self.assertFalse(xvlib.match_any("src/a.py", ["tests/**"]))


if __name__ == "__main__":
    unittest.main()

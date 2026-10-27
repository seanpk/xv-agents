import unittest

from helpers import sh  # noqa: F401  (puts scripts/ on sys.path)

import boundary


def edges_of(files, roots):
    g = boundary.graph(files.get, list(files), {"source": {"roots": roots}})
    return [list(e) for e in g["edges"]]


class PackageImportsTest(unittest.TestCase):
    def test_inside_a_package_a_bare_import_skips_the_sibling_file(self):
        files = {
            "src/api/__init__.py": "",
            "src/api/main.py": "import store\n",
            "src/api/store.py": "x = 1\n",
            "src/store/__init__.py": "x = 1\n",
        }
        self.assertEqual(
            boundary.resolve("store", "src/api/main.py", set(files), "py", ["src"]),
            "src/store/__init__.py")

    def test_inside_a_package_the_edge_goes_to_the_other_package(self):
        files = {
            "src/api/__init__.py": "",
            "src/api/main.py": "import store\n",
            "src/api/store.py": "x = 1\n",
            "src/store/__init__.py": "x = 1\n",
        }
        self.assertEqual(edges_of(files, ["src"]), [["src/api", "src/store"]])

    def test_without_an_init_the_sibling_file_still_wins(self):
        files = {
            "src/api/main.py": "import store\n",
            "src/api/store.py": "x = 1\n",
            "src/store/__init__.py": "x = 1\n",
        }
        self.assertEqual(
            boundary.resolve("store", "src/api/main.py", set(files), "py", ["src"]),
            "src/api/store.py")


if __name__ == "__main__":
    unittest.main()

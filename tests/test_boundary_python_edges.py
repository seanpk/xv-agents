import unittest

from helpers import sh  # noqa: F401  (puts scripts/ on sys.path)

import boundary


def edges_of(files, roots):
    g = boundary.graph(files.get, list(files), {"source": {"roots": roots}})
    return [list(e) for e in g["edges"]]


class PythonEdgesTest(unittest.TestCase):
    def test_flat_scripts_importing_each_other_by_bare_name_are_edges(self):
        files = {
            "scripts/run.py": "import agentcli\nfrom orders import load\nfrom record import save\nimport os\n",
            "scripts/agentcli.py": "x = 1\n",
            "scripts/orders.py": "x = 1\n",
            "scripts/record.py": "x = 1\n",
        }
        self.assertEqual(edges_of(files, ["scripts"]), [
            ["scripts/run", "scripts/agentcli"],
            ["scripts/run", "scripts/orders"],
            ["scripts/run", "scripts/record"]])

    def test_a_src_layout_import_between_packages_is_an_edge(self):
        files = {
            "src/api/main.py": "from store.db import get\n",
            "src/store/db.py": "x = 1\n",
        }
        self.assertEqual(edges_of(files, ["src"]), [["src/api", "src/store"]])

    def test_a_src_layout_import_of_a_package_is_an_edge(self):
        files = {
            "src/api/main.py": "import store\n",
            "src/store/__init__.py": "x = 1\n",
        }
        self.assertEqual(edges_of(files, ["src"]), [["src/api", "src/store"]])


if __name__ == "__main__":
    unittest.main()

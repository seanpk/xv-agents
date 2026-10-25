import unittest

from helpers import sh  # noqa: F401  (puts scripts/ on sys.path)

import boundary


class PythonResolveOrderTest(unittest.TestCase):
    def test_a_bare_import_resolves_in_the_importing_files_folder_first(self):
        files = {"evals/run.py", "evals/other.py", "scripts/run.py"}
        self.assertEqual(
            boundary.resolve("run", "evals/other.py", files, "py", ["scripts"]),
            "evals/run.py")

    def test_the_repo_root_comes_before_source_roots(self):
        files = {"run.py", "scripts/run.py", "tools/a.py"}
        self.assertEqual(
            boundary.resolve("run", "tools/a.py", files, "py", ["scripts"]),
            "run.py")


if __name__ == "__main__":
    unittest.main()

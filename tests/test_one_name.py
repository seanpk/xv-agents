"""Scenario point 10: one name, one definition, across tests/ and scripts/.

Parses each .py file (ast) and does not import it. Names made at run time
(setattr, type(...)) and names inside a function body are not covered.
"""
import ast
import os
import unittest

from helpers import HOME

DEFS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def python_files():
    for top in ("tests", "scripts"):
        for root, _dirs, names in os.walk(os.path.join(HOME, top)):
            for name in sorted(names):
                if name.endswith(".py"):
                    yield os.path.join(root, name)


def repeated_names(tree):
    """(name, first line, second line) for each repeated name: top-level
    class/function names, and method names within one class."""
    found = []
    seen = {}
    for node in tree.body:
        if isinstance(node, DEFS):
            if node.name in seen:
                found.append((node.name, seen[node.name], node.lineno))
            else:
                seen[node.name] = node.lineno
        if isinstance(node, ast.ClassDef):
            methods = {}
            for item in node.body:
                if isinstance(item, DEFS[1:]):
                    if item.name in methods:
                        found.append((node.name + "." + item.name,
                                      methods[item.name], item.lineno))
                    else:
                        methods[item.name] = item.lineno
    return found


class OneNameOneDefinitionTest(unittest.TestCase):
    def test_no_file_under_tests_or_scripts_defines_a_name_twice(self):
        problems = []
        for path in python_files():
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), path)
            rel = os.path.relpath(path, HOME)
            for name, first, second in repeated_names(tree):
                problems.append("%s: %s defined at line %d and line %d"
                                % (rel, name, first, second))
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_scan_sees_a_repeated_class_function_and_method(self):
        tree = ast.parse(
            "class A:\n    def m(self): pass\n    def m(self): pass\n"
            "class A: pass\n"
            "def f(): pass\n"
            "def f(): pass\n"
        )
        self.assertEqual(
            sorted(repeated_names(tree)),
            [("A", 1, 4), ("A.m", 2, 3), ("f", 5, 6)],
        )

    def test_the_scan_leaves_names_inside_a_function_and_run_time_names_alone(self):
        tree = ast.parse(
            "def outer():\n    def g(): pass\n    def g(): pass\n"
            "class B: pass\nsetattr(B, 'x', 1)\nsetattr(B, 'x', 2)\n"
        )
        self.assertEqual(repeated_names(tree), [])


if __name__ == "__main__":
    unittest.main()

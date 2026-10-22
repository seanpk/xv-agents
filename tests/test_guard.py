import unittest

from helpers import HOME  # noqa: F401
from run import is_record_path


class GuardTest(unittest.TestCase):
    def test_a_record_path_and_its_side_files(self):
        self.assertTrue(is_record_path(".xv/slices/2026-10-21-expiring-today.md"))
        self.assertTrue(is_record_path(".xv/slices/v1.2-fix.md"))
        for side in (".xv/slices/s1.packet.md", ".xv/slices/s1.boundary.md", ".xv/slices/s1.prototypes.md",
                     ".xv/slices/packet-2026-10-21.md", ".xv/slices/pr-packet.md", ".xv/decisions/s1.md"):
            self.assertFalse(is_record_path(side), side)


if __name__ == "__main__":
    unittest.main()

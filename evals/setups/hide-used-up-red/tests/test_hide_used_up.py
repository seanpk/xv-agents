import json
import unittest
from datetime import date
from urllib.request import urlopen

from pantry.api import serve
from pantry.store import Store


class HideUsedUpTest(unittest.TestCase):
    """Scenario: when the household uses the last of something, it no longer shows in the list."""

    def test_the_last_loaf_used_leaves_the_list(self):
        store = Store()
        store.add("bread", 1, date(2026, 10, 24))
        store.add("rice", 2, date(2027, 1, 1))
        store.use("bread")
        self.assertEqual([i.name for i in store.items()], ["rice"])

    def test_the_api_lists_only_what_is_left(self):
        store = Store()
        store.add("bread", 1, date(2026, 10, 24))
        store.use("bread")
        server = serve(store)
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/items") as r:
                self.assertEqual(json.loads(r.read()), [])
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()

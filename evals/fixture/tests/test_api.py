import json
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pantry.api import serve


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.server = serve()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def call(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(self.base + path, data=data, method=method,
                      headers={"Content-Type": "application/json"})
        try:
            with urlopen(req) as r:
                return r.status, json.loads(r.read())
        except HTTPError as e:
            return e.code, json.loads(e.read())

    def test_add_then_list(self):
        status, _ = self.call("POST", "/items", {"name": "rice", "qty": 2, "expires_on": "2027-01-01"})
        self.assertEqual(status, 201)
        status, items = self.call("GET", "/items")
        self.assertEqual(items, [{"name": "rice", "qty": 2, "expires_on": "2027-01-01"}])

    def test_a_bad_quantity_is_a_400_with_the_reason(self):
        status, body = self.call("POST", "/items", {"name": "rice", "qty": 0, "expires_on": "2027-01-01"})
        self.assertEqual((status, body), (400, {"error": "qty must be a positive whole number"}))

    def test_use_an_item(self):
        self.call("POST", "/items", {"name": "eggs", "qty": 6, "expires_on": "2026-10-30"})
        status, item = self.call("POST", "/items/eggs/use", {"qty": 2})
        self.assertEqual((status, item["qty"]), (200, 4))

    def test_expiring_within_three_days(self):
        self.call("POST", "/items", {"name": "yogurt", "qty": 1, "expires_on": "2026-10-23"})
        self.call("POST", "/items", {"name": "rice", "qty": 1, "expires_on": "2027-01-01"})
        status, items = self.call("GET", "/items/expiring?days=3&today=2026-10-21")
        self.assertEqual([i["name"] for i in items], ["yogurt"])


if __name__ == "__main__":
    unittest.main()

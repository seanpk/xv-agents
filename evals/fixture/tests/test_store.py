import unittest
from datetime import date

from pantry.store import Store


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def test_add_and_list(self):
        self.store.add("rice", 2, date(2027, 1, 1))
        self.store.add("beans", 1, date(2026, 12, 1))
        self.assertEqual([i.name for i in self.store.items()], ["beans", "rice"])

    def test_adding_again_sums_and_keeps_the_earlier_date(self):
        self.store.add("milk", 1, date(2026, 10, 25))
        self.store.add("milk", 2, date(2026, 10, 23))
        milk = self.store.items()[0]
        self.assertEqual((milk.qty, milk.expires_on), (3, date(2026, 10, 23)))

    def test_add_rejects_a_quantity_below_one(self):
        with self.assertRaises(ValueError) as e:
            self.store.add("rice", 0, date(2027, 1, 1))
        self.assertEqual(str(e.exception), "qty must be a positive whole number")

    def test_use_takes_from_the_quantity(self):
        self.store.add("eggs", 6, date(2026, 10, 30))
        self.store.use("eggs", 2)
        self.assertEqual(self.store.items()[0].qty, 4)

    def test_use_refuses_more_than_there_is(self):
        self.store.add("eggs", 1, date(2026, 10, 30))
        with self.assertRaises(ValueError):
            self.store.use("eggs", 2)

    def test_used_up_item_stays_listed(self):
        self.store.add("bread", 1, date(2026, 10, 24))
        self.store.use("bread")
        listed = self.store.items()
        self.assertEqual([(i.name, i.qty) for i in listed], [("bread", 0)])

    def test_expiring_lists_items_within_the_window(self):
        self.store.add("yogurt", 1, date(2026, 10, 23))
        self.store.add("rice", 1, date(2027, 1, 1))
        found = self.store.expiring(3, date(2026, 10, 21))
        self.assertEqual([i.name for i in found], ["yogurt"])


if __name__ == "__main__":
    unittest.main()

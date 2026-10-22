"""The household's food, held in memory."""

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Item:
    name: str
    qty: int
    expires_on: date

    def as_dict(self):
        return {"name": self.name, "qty": self.qty, "expires_on": self.expires_on.isoformat()}


class Store:
    def __init__(self):
        self._items = {}

    def add(self, name, qty, expires_on):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            raise ValueError("qty must be a positive whole number")
        if name in self._items:
            item = self._items[name]
            item.qty += qty
            item.expires_on = min(item.expires_on, expires_on)
        else:
            self._items[name] = Item(name, qty, expires_on)
        return self._items[name]

    def use(self, name, qty=1):
        if name not in self._items:
            raise KeyError(name)
        item = self._items[name]
        if qty > item.qty:
            raise ValueError(f"only {item.qty} {name} left")
        item.qty -= qty
        return item

    def items(self):
        return sorted(self._items.values(), key=lambda i: i.name)

    def expiring(self, within_days, today):
        """Items that run out within `within_days` days of `today`."""
        last = today + timedelta(days=within_days)
        return [i for i in self.items() if today < i.expires_on <= last]

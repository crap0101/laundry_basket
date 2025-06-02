# Author: Marco Chieppa
# Year: 2025

class SizedQueue:
    """A simple FIFO queue storing at most *max* items."""
    def __init__(self, max=float('+inf')):
        self._max = max
        self._items = []
        self._count = 0
    def push(self, item):
        self._items.append(item)
        if self._count >= self._max:
            self._items = self._items[1:]
        else:
            self._count += 1
    def pop(self):
        if self._items:
            self._count -= 1
            return self._items.pop()
    def items(self):
        for item in self._items:
            yield item

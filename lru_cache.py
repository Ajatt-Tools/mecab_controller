# Copyright: Ajatt-Tools and contributors; https://github.com/Ajatt-Tools
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from collections import OrderedDict
from typing import TypeVar, Generic, Hashable

T = TypeVar("T")


class LRUCache(Generic[T]):
    _cache: OrderedDict[Hashable, T]
    _capacity: int

    def __init__(self, capacity: int = 0) -> None:
        self._capacity = capacity
        self._cache = OrderedDict()

    def __getitem__(self, key: Hashable) -> T:
        value = self._cache[key]
        self._cache.move_to_end(key)
        return value

    def __setitem__(self, key: Hashable, value: T) -> None:
        self._cache[key] = value
        self._cache.move_to_end(key)
        self._clear_old_items()

    def set_capacity(self, capacity: int) -> None:
        self._capacity = capacity
        self._clear_old_items()

    def _clear_old_items(self) -> None:
        if self._capacity > 0:
            while len(self._cache) > self._capacity:
                self._cache.popitem(last=False)

    def setdefault(self, key: Hashable, value: T) -> T:
        value = self._cache.setdefault(key, value)
        self._cache.move_to_end(key)
        return value

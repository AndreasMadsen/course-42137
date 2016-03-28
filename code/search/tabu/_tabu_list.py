
import collections

class TabuList:
    def __init__(self, max_size=None):
        self._max_size = max_size
        self._set = set()
        self._queue = collections.deque()

    def __contains__(self, item):
        return item in self._set

    def add(self, item):
        if item in self._set: return

        # Remove item at left if the max_size will be exceeded by adding item
        if self._max_size is not None and len(self._set) >= self._max_size:
            self._set.remove(self._queue.popleft())

        # add item
        self._set.add(item)
        if (self._max_size is not None):
            self._queue.append(item)

    def clear(self):
        self._queue.clear()
        self._set.clear()

"""Small in-memory TTL cache helpers for EduQuest."""

from __future__ import annotations

from collections import OrderedDict
import threading
import time
from typing import Any


class TTLCache:
    """Thread-safe in-memory cache with TTL expiry and LRU-style eviction."""

    def __init__(self, ttl_seconds: int = 900, max_entries: int = 128):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._store: OrderedDict[str, tuple[float, float, Any]] = OrderedDict()
        self._lock = threading.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "writes": 0,
            "evictions": 0,
            "expirations": 0,
        }

    def get(self, key: str) -> Any | None:
        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if item is None:
                self._stats["misses"] += 1
                return None
            expires_at, _last_accessed_at, value = item
            if expires_at <= now:
                self._store.pop(key, None)
                self._stats["misses"] += 1
                self._stats["expirations"] += 1
                return None
            self._store.move_to_end(key)
            self._store[key] = (now + self.ttl_seconds, now, value)
            self._stats["hits"] += 1
            return value

    def set(self, key: str, value: Any) -> None:
        now = time.time()
        with self._lock:
            self._prune_expired(now)
            if key in self._store:
                self._store.pop(key, None)
            elif len(self._store) >= self.max_entries:
                self._store.popitem(last=False)
                self._stats["evictions"] += 1
            self._store[key] = (now + self.ttl_seconds, now, value)
            self._stats["writes"] += 1

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
            self._stats = {
                "hits": 0,
                "misses": 0,
                "writes": 0,
                "evictions": 0,
                "expirations": 0,
            }

    def stats(self) -> dict[str, int]:
        with self._lock:
            return {
                **self._stats,
                "size": len(self._store),
            }

    def _prune_expired(self, now: float) -> None:
        expired_keys = [
            key
            for key, (expires_at, _last_accessed_at, _value) in self._store.items()
            if expires_at <= now
        ]
        for key in expired_keys:
            self._store.pop(key, None)
            self._stats["expirations"] += 1

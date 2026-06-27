"""
Simple in-memory cache with TTL (Time-To-Live) support.

Used to cache GitHub API responses and analysis results so that
repeated analyses of the same repository don't hit GitHub rate limits.

Default TTL: 15 minutes (900 seconds).
"""

import time
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe (for async use) in-memory key-value store with expiry."""

    def __init__(self):
        self._store: dict = {}   # key -> (value, expiry_timestamp)

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value.

        Returns the value if it exists and hasn't expired, else None.
        """
        entry = self._store.get(key)
        if entry is None:
            return None

        value, expires_at = entry
        if time.time() > expires_at:
            logger.debug("Cache expired for key: %s", key)
            del self._store[key]
            return None

        logger.debug("Cache hit for key: %s", key)
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 900) -> None:
        """
        Store a value with a TTL.

        Args:
            key: Cache key string.
            value: Any serialisable value.
            ttl_seconds: Time-to-live in seconds (default 15 min).
        """
        expires_at = time.time() + ttl_seconds
        self._store[key] = (value, expires_at)
        logger.debug("Cache set for key: %s (TTL %ds)", key, ttl_seconds)

    def delete(self, key: str) -> None:
        """Explicitly remove a cached entry."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()
        logger.info("Cache cleared.")

    def purge_expired(self) -> int:
        """Remove all expired entries. Returns the count removed."""
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired_keys:
            del self._store[k]
        if expired_keys:
            logger.debug("Purged %d expired cache entries.", len(expired_keys))
        return len(expired_keys)

    @property
    def size(self) -> int:
        """Number of entries currently in the cache (including potentially expired)."""
        return len(self._store)


# Global singleton cache instance — imported by other modules
cache = TTLCache()

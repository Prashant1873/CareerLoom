import re
import time
from typing import Dict, Optional, Tuple


class QueryCache:
    """
    In-memory LRU and TTL query cache for parsed natural language search queries.
    Prevents redundant external LLM inference and guarantees sub-1ms return for common searches.
    """
    def __init__(self, max_size: int = 500, ttl_seconds: int = 86400):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        # key -> (result_dict, expiry_timestamp, last_accessed_timestamp)
        self._cache: Dict[str, Tuple[dict, float, float]] = {}

    @staticmethod
    def normalize_key(query: str) -> str:
        """
        Normalizes query strings to maximize cache hits:
        lowercase, strip punctuation, collapse whitespace.
        """
        cleaned = re.sub(r"[^\w\s]", " ", query.lower())
        return " ".join(cleaned.split())

    def get(self, query: str) -> Optional[dict]:
        key = self.normalize_key(query)
        if not key:
            return None

        entry = self._cache.get(key)
        if not entry:
            return None

        data, expires_at, _ = entry
        now = time.time()
        if now > expires_at:
            # Expired
            del self._cache[key]
            return None

        # Update last accessed for LRU
        self._cache[key] = (data, expires_at, now)
        return data

    def set(self, query: str, parsed_result: dict) -> None:
        key = self.normalize_key(query)
        if not key or not parsed_result:
            return

        now = time.time()
        # Evict oldest entry if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][2])
            del self._cache[oldest_key]

        expires_at = now + self.ttl_seconds
        self._cache[key] = (parsed_result, expires_at, now)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)


# Global singleton instance
query_cache = QueryCache()

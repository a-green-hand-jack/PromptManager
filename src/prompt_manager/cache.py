"""Caching strategies for the prompt management system."""

import hashlib
import json
from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple


class LRUCache:
    """Thread-safe LRU (Least Recently Used) cache implementation."""

    def __init__(self, max_size: int = 100):
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of items to store in cache
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if key in self._cache:
            self._hits += 1
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        else:
            self._misses += 1
            return None

    def put(self, key: str, value: Any) -> None:
        """Put item into cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self._cache:
            # Update existing item and move to end
            self._cache.move_to_end(key)
        else:
            # Add new item
            if len(self._cache) >= self.max_size:
                # Remove least recently used item
                self._cache.popitem(last=False)

        self._cache[key] = value

    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def remove(self, key: str) -> bool:
        """Remove item from cache.

        Args:
            key: Cache key

        Returns:
            True if item was removed, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
        }


class CacheKeyBuilder:
    """Builder for generating cache keys from various inputs."""

    @staticmethod
    def build(
        template_name: str,
        version: Optional[str] = None,
        **parameters: Any
    ) -> str:
        """Build a cache key from template name, version, and parameters.

        Args:
            template_name: Name of the template
            version: Template version
            **parameters: Template parameters

        Returns:
            Cache key string
        """
        # Create a deterministic representation
        key_parts = [template_name]

        if version:
            key_parts.append(f"v:{version}")

        if parameters:
            # Sort parameters for consistent key generation
            params_str = json.dumps(parameters, sort_keys=True, default=str)
            # Hash the parameters to keep key length reasonable
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            key_parts.append(f"p:{params_hash}")

        return "|".join(key_parts)

    @staticmethod
    def parse(cache_key: str) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse a cache key into its components.

        Args:
            cache_key: Cache key string

        Returns:
            Tuple of (template_name, version, params_hash)
        """
        parts = cache_key.split("|")
        template_name = parts[0]
        version = None
        params_hash = None

        for part in parts[1:]:
            if part.startswith("v:"):
                version = part[2:]
            elif part.startswith("p:"):
                params_hash = part[2:]

        return template_name, version, params_hash


class MultiLevelCache:
    """Multi-level cache with separate caches for templates and rendered results."""

    def __init__(
        self,
        template_cache_size: int = 50,
        render_cache_size: int = 200,
        enabled: bool = True
    ):
        """Initialize multi-level cache.

        Args:
            template_cache_size: Max size for template cache
            render_cache_size: Max size for render result cache
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.template_cache = LRUCache(max_size=template_cache_size)
        self.render_cache = LRUCache(max_size=render_cache_size)

    def get_template(self, key: str) -> Optional[Any]:
        """Get template from cache."""
        if not self.enabled:
            return None
        return self.template_cache.get(key)

    def put_template(self, key: str, template: Any) -> None:
        """Put template into cache."""
        if self.enabled:
            self.template_cache.put(key, template)

    def get_render(self, key: str) -> Optional[str]:
        """Get rendered result from cache."""
        if not self.enabled:
            return None
        return self.render_cache.get(key)

    def put_render(self, key: str, result: str) -> None:
        """Put rendered result into cache."""
        if self.enabled:
            self.render_cache.put(key, result)

    def clear(self) -> None:
        """Clear all caches."""
        self.template_cache.clear()
        self.render_cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        return {
            "enabled": self.enabled,
            "template_cache": self.template_cache.stats(),
            "render_cache": self.render_cache.stats(),
        }

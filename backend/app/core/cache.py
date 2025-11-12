"""
Simple in-memory caching layer for performance optimization
Reduces database queries for frequently accessed data
"""

from datetime import datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache with TTL (Time-To-Live) support"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self.ttl_map = {}  # Different TTL for different cache keys
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if it exists and hasn't expired
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/not found
        """
        if key not in self.cache:
            return None
        
        # Get TTL for this key (default 300 seconds)
        ttl = self.ttl_map.get(key, 300)
        
        # Check if expired
        age = datetime.now() - self.timestamps[key]
        if age > timedelta(seconds=ttl):
            # Expired, remove and return None
            del self.cache[key]
            del self.timestamps[key]
            if key in self.ttl_map:
                del self.ttl_map[key]
            return None
        
        logger.debug(f"✅ Cache HIT: {key} (age: {age.total_seconds():.1f}s, TTL: {ttl}s)")
        return self.cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Set value in cache with optional TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default 300 = 5 minutes)
        """
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
        self.ttl_map[key] = ttl
        logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> None:
        """Delete specific cache key"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
            if key in self.ttl_map:
                del self.ttl_map[key]
            logger.debug(f"🗑️  Cache DELETE: {key}")
    
    def delete_pattern(self, pattern: str) -> None:
        """
        Delete all cache keys matching a pattern
        
        Example:
            delete_pattern("dashboard_*")  # Deletes all dashboard cache
            delete_pattern("sale_*")       # Deletes all sale cache
        """
        import fnmatch
        
        keys_to_delete = [k for k in self.cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            self.delete(key)
        
        if keys_to_delete:
            logger.debug(f"🗑️  Cache DELETE PATTERN: {pattern} ({len(keys_to_delete)} keys)")
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.ttl_map.clear()
        logger.debug("🗑️  Cache CLEARED (all)")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "keys": list(self.cache.keys()),
            "usage_bytes": sum(len(str(v)) for v in self.cache.values())
        }


# Global cache instance
_cache = CacheManager()


def get_cache() -> CacheManager:
    """Get global cache instance"""
    return _cache


# Cache key builders (for consistency)
def cache_key_dashboard_summary(user_id: int) -> str:
    return f"dashboard_summary_{user_id}"


def cache_key_monthly_stats(user_id: int) -> str:
    return f"dashboard_monthly_stats_{user_id}"


def cache_key_stock_status(user_id: int) -> str:
    return f"stock_status_{user_id}"


def cache_key_item_list() -> str:
    return "item_list_all"


def cache_key_party_list() -> str:
    return "party_list_all"


# Cache invalidation helpers
def invalidate_dashboard_cache(user_id: int = None) -> None:
    """Invalidate dashboard cache (called after data changes)"""
    if user_id:
        _cache.delete(cache_key_dashboard_summary(user_id))
        _cache.delete(cache_key_monthly_stats(user_id))
    else:
        _cache.delete_pattern("dashboard_*")
    logger.info(f"📊 Dashboard cache invalidated (user_id: {user_id})")


def invalidate_stock_cache(user_id: int = None) -> None:
    """Invalidate stock cache (called after inventory changes)"""
    if user_id:
        _cache.delete(cache_key_stock_status(user_id))
    else:
        _cache.delete_pattern("stock_*")
    logger.info(f"📦 Stock cache invalidated (user_id: {user_id})")


def invalidate_item_cache() -> None:
    """Invalidate item cache (called after item changes)"""
    _cache.delete(cache_key_item_list())
    logger.info("📋 Item cache invalidated")


def invalidate_party_cache() -> None:
    """Invalidate party cache (called after party changes)"""
    _cache.delete(cache_key_party_list())
    logger.info("👥 Party cache invalidated")


# Suggested cache TTLs (in seconds)
# These are optimized for your use case:

CACHE_TTL_DASHBOARD_SUMMARY = 300      # 5 minutes - Dashboard refreshes frequently
CACHE_TTL_MONTHLY_STATS = 3600         # 1 hour - Monthly data changes daily
CACHE_TTL_STOCK_STATUS = 600           # 10 minutes - Stock changes when sales/purchases happen
CACHE_TTL_ITEM_LIST = 900              # 15 minutes - Items rarely change
CACHE_TTL_PARTY_LIST = 1800            # 30 minutes - Suppliers/customers rarely change
CACHE_TTL_REPORTS = 1800               # 30 minutes - Reports are historical data

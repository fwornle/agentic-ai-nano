"""
Performance optimization utilities for enterprise agent systems.
"""

import asyncio
import time
import functools
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import weakref

@dataclass
class CacheEntry:
    """Cache entry with TTL support."""
    value: Any
    expires_at: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

class LRUCache:
    """LRU Cache with TTL support and memory management."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._access_order = []
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self.cache:
                return None
                
            entry = self.cache[key]
            
            # Check if expired
            if datetime.now() > entry.expires_at:
                del self.cache[key]
                self._access_order.remove(key)
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = datetime.now()
            
            # Move to end of access order (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
            
            # If key exists, update it
            if key in self.cache:
                self.cache[key] = CacheEntry(value, expires_at)
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)
                return
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Add new entry
            self.cache[key] = CacheEntry(value, expires_at)
            self._access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            if lru_key in self.cache:
                del self.cache[lru_key]
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count."""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self.cache.items() 
                if now > entry.expires_at
            ]
            
            for key in expired_keys:
                del self.cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
            
            return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "total_accesses": total_accesses,
                "average_accesses": total_accesses / len(self.cache) if self.cache else 0
            }

class PerformanceProfiler:
    """Simple performance profiler for identifying bottlenecks."""
    
    def __init__(self):
        self.timings: Dict[str, list] = {}
        self._lock = threading.Lock()
    
    def profile(self, name: str):
        """Decorator to profile function execution time."""
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self._record_timing(name, execution_time)
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    self._record_timing(name, execution_time)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def _record_timing(self, name: str, execution_time: float):
        """Record execution time for analysis."""
        with self._lock:
            if name not in self.timings:
                self.timings[name] = []
            
            # Keep only last 1000 timings per function
            if len(self.timings[name]) >= 1000:
                self.timings[name].pop(0)
            
            self.timings[name].append(execution_time)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get performance statistics for a function."""
        with self._lock:
            if name not in self.timings or not self.timings[name]:
                return {}
            
            timings = self.timings[name]
            return {
                "count": len(timings),
                "total": sum(timings),
                "average": sum(timings) / len(timings),
                "min": min(timings),
                "max": max(timings),
                "p95": sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 1 else timings[0]
            }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all profiled functions."""
        return {name: self.get_stats(name) for name in self.timings.keys()}

# Global instances
cache = LRUCache()
profiler = PerformanceProfiler()

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class ConnectionPool:
    """Generic connection pool for managing expensive resources."""
    
    def __init__(self, factory: Callable, max_size: int = 10, 
                 timeout: float = 30, max_lifetime: int = 3600):
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout
        self.max_lifetime = max_lifetime
        
        self._pool = []
        self._in_use = set()
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        
        # Cleanup task
        self._cleanup_task = None
        
    async def acquire(self):
        """Acquire a connection from the pool."""
        async with self._condition:
            # Start cleanup task if not running
            if self._cleanup_task is None:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            # Wait for available connection or create new one
            while True:
                # Try to get an existing connection
                if self._pool:
                    conn_info = self._pool.pop()
                    conn, created_at = conn_info['conn'], conn_info['created_at']
                    
                    # Check if connection is still valid
                    if datetime.now() - created_at < timedelta(seconds=self.max_lifetime):
                        self._in_use.add(conn)
                        return conn
                    else:
                        # Connection too old, close it
                        try:
                            if hasattr(conn, 'close'):
                                await conn.close()
                        except:
                            pass
                        continue
                
                # Create new connection if under limit
                if len(self._in_use) < self.max_size:
                    conn = await self.factory()
                    self._in_use.add(conn)
                    return conn
                
                # Wait for a connection to be released
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=self.timeout)
                except asyncio.TimeoutError:
                    raise TimeoutError("Timeout waiting for connection")
    
    async def release(self, conn):
        """Release a connection back to the pool."""
        async with self._condition:
            if conn in self._in_use:
                self._in_use.remove(conn)
                self._pool.append({
                    'conn': conn,
                    'created_at': datetime.now()
                })
                self._condition.notify()
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old connections."""
        try:
            while True:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                async with self._lock:
                    # Remove old connections
                    cutoff_time = datetime.now() - timedelta(seconds=self.max_lifetime)
                    new_pool = []
                    
                    for conn_info in self._pool:
                        if conn_info['created_at'] > cutoff_time:
                            new_pool.append(conn_info)
                        else:
                            # Close old connection
                            try:
                                conn = conn_info['conn']
                                if hasattr(conn, 'close'):
                                    await conn.close()
                            except:
                                pass
                    
                    self._pool = new_pool
        except asyncio.CancelledError:
            pass
    
    async def close_all(self):
        """Close all connections and cleanup."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        async with self._lock:
            # Close all pooled connections
            for conn_info in self._pool:
                try:
                    conn = conn_info['conn']
                    if hasattr(conn, 'close'):
                        await conn.close()
                except:
                    pass
            
            # Close all in-use connections
            for conn in list(self._in_use):
                try:
                    if hasattr(conn, 'close'):
                        await conn.close()
                except:
                    pass
            
            self._pool.clear()
            self._in_use.clear()
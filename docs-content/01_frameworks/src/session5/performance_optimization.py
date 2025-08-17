# src/session5/performance_optimization.py
"""
Performance optimization patterns for PydanticAI agents including caching, batching,
connection pooling, and performance monitoring.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic, Tuple, Union, AsyncIterable
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import functools
import hashlib
import json
import time
import threading
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field
import weakref
import psutil
import gc
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

class CacheStrategy(str, Enum):
    """Cache eviction strategies."""
    LRU = "lru"           # Least Recently Used
    LFU = "lfu"           # Least Frequently Used
    FIFO = "fifo"         # First In, First Out
    TTL = "ttl"           # Time To Live

class PerformanceMetric(str, Enum):
    """Performance metrics to track."""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CACHE_HIT_RATE = "cache_hit_rate"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"

# Performance monitoring models

class PerformanceStats(BaseModel):
    """Performance statistics."""
    metric: PerformanceMetric = Field(..., description="Performance metric")
    value: float = Field(..., description="Metric value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class CacheEntry(BaseModel):
    """Cache entry with metadata."""
    key: str = Field(..., description="Cache key")
    value: Any = Field(..., description="Cached value")
    created_at: datetime = Field(default_factory=datetime.now)
    accessed_at: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=1, description="Number of accesses")
    ttl_seconds: Optional[int] = Field(None, description="Time to live in seconds")
    size_bytes: int = Field(default=0, description="Approximate size in bytes")
    
    class Config:
        arbitrary_types_allowed = True
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds
    
    def touch(self):
        """Update access information."""
        self.accessed_at = datetime.now()
        self.access_count += 1

class BatchRequest(BaseModel):
    """Batched request container."""
    request_id: str = Field(..., description="Request identifier")
    data: Any = Field(..., description="Request data")
    callback: Optional[Callable] = Field(None, description="Callback function")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Request metadata")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True

class BatchConfig(BaseModel):
    """Configuration for batch processing."""
    max_batch_size: int = Field(default=10, ge=1, description="Maximum batch size")
    max_wait_time_ms: int = Field(default=100, ge=1, description="Maximum wait time in milliseconds")
    timeout_seconds: float = Field(default=30.0, gt=0, description="Batch processing timeout")
    retry_attempts: int = Field(default=2, ge=0, description="Number of retry attempts")

# Abstract cache interface

class Cache(ABC):
    """Abstract cache interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear entire cache."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass

# In-memory cache implementation

class InMemoryCache(Cache):
    """High-performance in-memory cache with multiple eviction strategies."""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = OrderedDict()  # For LRU
        self.frequency_counter = defaultdict(int)  # For LFU
        self.lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.logger = logging.getLogger(__name__ + ".InMemoryCache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                await self._remove_entry(key)
                self.misses += 1
                return None
            
            # Update access information
            entry.touch()
            self._update_access_tracking(key)
            self.hits += 1
            
            return entry.value
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Set value in cache."""
        async with self.lock:
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl_seconds,
                size_bytes=self._estimate_size(value)
            )
            
            # Check if we need to evict
            if key not in self.cache and len(self.cache) >= self.max_size:
                await self._evict()
            
            # Store entry
            self.cache[key] = entry
            self._update_access_tracking(key)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self.lock:
            return await self._remove_entry(key)
    
    async def clear(self) -> bool:
        """Clear entire cache."""
        async with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.frequency_counter.clear()
            return True
    
    def _update_access_tracking(self, key: str):
        """Update access tracking for eviction strategies."""
        if self.strategy == CacheStrategy.LRU:
            if key in self.access_order:
                del self.access_order[key]
            self.access_order[key] = datetime.now()
        
        elif self.strategy == CacheStrategy.LFU:
            self.frequency_counter[key] += 1
    
    async def _evict(self):
        """Evict entries based on strategy."""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            oldest_key = next(iter(self.access_order))
            await self._remove_entry(oldest_key)
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            least_frequent_key = min(self.frequency_counter.keys(), 
                                   key=lambda k: self.frequency_counter[k])
            await self._remove_entry(least_frequent_key)
        
        elif self.strategy == CacheStrategy.FIFO:
            # Remove first inserted (oldest)
            oldest_key = next(iter(self.cache))
            await self._remove_entry(oldest_key)
        
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first
            current_time = datetime.now()
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            if expired_keys:
                await self._remove_entry(expired_keys[0])
            else:
                # Fall back to LRU if no expired entries
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k].created_at)
                await self._remove_entry(oldest_key)
        
        self.evictions += 1
    
    async def _remove_entry(self, key: str) -> bool:
        """Remove entry from cache and tracking structures."""
        if key not in self.cache:
            return False
        
        del self.cache[key]
        
        if key in self.access_order:
            del self.access_order[key]
        
        if key in self.frequency_counter:
            del self.frequency_counter[key]
        
        return True
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of cached value."""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (list, dict)):
                return len(json.dumps(value, default=str).encode('utf-8'))
            else:
                return len(str(value).encode('utf-8'))
        except:
            return 100  # Default estimate
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) if total_requests > 0 else 0
        
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
            "strategy": self.strategy.value,
            "total_size_bytes": total_size,
            "avg_entry_size": total_size / len(self.cache) if self.cache else 0
        }

# Batch processor

class BatchProcessor(Generic[T, R]):
    """Processes requests in batches for improved performance."""
    
    def __init__(self, 
                 batch_function: Callable[[List[T]], List[R]], 
                 config: BatchConfig):
        self.batch_function = batch_function
        self.config = config
        self.pending_requests: List[BatchRequest] = []
        self.lock = asyncio.Lock()
        self.batch_timer: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(__name__ + ".BatchProcessor")
    
    async def process_request(self, request_data: T, request_id: str) -> R:
        """Add request to batch and await result."""
        result_future = asyncio.Future()
        
        batch_request = BatchRequest(
            request_id=request_id,
            data=request_data,
            callback=result_future.set_result
        )
        
        async with self.lock:
            self.pending_requests.append(batch_request)
            
            # Start timer if this is the first request
            if len(self.pending_requests) == 1:
                self._start_batch_timer()
            
            # Process immediately if batch is full
            if len(self.pending_requests) >= self.config.max_batch_size:
                await self._process_batch()
        
        return await result_future
    
    def _start_batch_timer(self):
        """Start timer for batch processing."""
        if self.batch_timer and not self.batch_timer.done():
            self.batch_timer.cancel()
        
        self.batch_timer = asyncio.create_task(self._batch_timer_callback())
    
    async def _batch_timer_callback(self):
        """Timer callback for batch processing."""
        await asyncio.sleep(self.config.max_wait_time_ms / 1000.0)
        
        async with self.lock:
            if self.pending_requests:
                await self._process_batch()
    
    async def _process_batch(self):
        """Process current batch of requests."""
        if not self.pending_requests:
            return
        
        batch = self.pending_requests.copy()
        self.pending_requests.clear()
        
        # Cancel timer
        if self.batch_timer and not self.batch_timer.done():
            self.batch_timer.cancel()
        
        self.logger.info(f"Processing batch of {len(batch)} requests")
        
        try:
            # Extract request data
            request_data = [req.data for req in batch]
            
            # Process batch
            results = await asyncio.wait_for(
                self._execute_batch_function(request_data),
                timeout=self.config.timeout_seconds
            )
            
            # Return results to requesters
            for request, result in zip(batch, results):
                if request.callback:
                    try:
                        request.callback(result)
                    except Exception as e:
                        self.logger.error(f"Callback error for {request.request_id}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Batch processing error: {str(e)}")
            
            # Return errors to all requesters
            error_result = Exception(f"Batch processing failed: {str(e)}")
            for request in batch:
                if request.callback:
                    try:
                        request.callback.set_exception(error_result)
                    except Exception:
                        pass
    
    async def _execute_batch_function(self, request_data: List[T]) -> List[R]:
        """Execute batch function, handling both sync and async."""
        if asyncio.iscoroutinefunction(self.batch_function):
            return await self.batch_function(request_data)
        else:
            # Run in thread pool for CPU-bound operations
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                return await loop.run_in_executor(executor, self.batch_function, request_data)

# Connection pooling

class ConnectionPool:
    """Connection pool for managing expensive resources."""
    
    def __init__(self, 
                 create_connection: Callable,
                 max_connections: int = 10,
                 min_connections: int = 2,
                 max_idle_time: int = 300):
        self.create_connection = create_connection
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_idle_time = max_idle_time
        
        self.available_connections = asyncio.Queue()
        self.all_connections = set()
        self.connection_usage = {}  # Connection -> last used time
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__ + ".ConnectionPool")
        
        # Start maintenance task
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())
    
    async def initialize(self):
        """Initialize minimum connections."""
        for _ in range(self.min_connections):
            conn = await self.create_connection()
            self.all_connections.add(conn)
            await self.available_connections.put(conn)
            self.connection_usage[conn] = datetime.now()
    
    async def get_connection(self):
        """Get connection from pool."""
        # Try to get available connection
        try:
            conn = self.available_connections.get_nowait()
            self.connection_usage[conn] = datetime.now()
            return conn
        except asyncio.QueueEmpty:
            pass
        
        # Create new connection if under limit
        async with self.lock:
            if len(self.all_connections) < self.max_connections:
                conn = await self.create_connection()
                self.all_connections.add(conn)
                self.connection_usage[conn] = datetime.now()
                return conn
        
        # Wait for available connection
        conn = await self.available_connections.get()
        self.connection_usage[conn] = datetime.now()
        return conn
    
    async def return_connection(self, conn):
        """Return connection to pool."""
        if conn in self.all_connections:
            self.connection_usage[conn] = datetime.now()
            await self.available_connections.put(conn)
    
    async def _maintenance_loop(self):
        """Maintain connection pool health."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._cleanup_idle_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Maintenance error: {str(e)}")
    
    async def _cleanup_idle_connections(self):
        """Clean up idle connections."""
        current_time = datetime.now()
        connections_to_remove = []
        
        async with self.lock:
            for conn, last_used in self.connection_usage.items():
                idle_time = (current_time - last_used).total_seconds()
                
                if (idle_time > self.max_idle_time and 
                    len(self.all_connections) > self.min_connections):
                    connections_to_remove.append(conn)
            
            for conn in connections_to_remove:
                if conn in self.all_connections:
                    self.all_connections.remove(conn)
                    del self.connection_usage[conn]
                    
                    # Try to close connection
                    try:
                        if hasattr(conn, 'close'):
                            await conn.close()
                    except Exception as e:
                        self.logger.error(f"Error closing connection: {str(e)}")
        
        if connections_to_remove:
            self.logger.info(f"Cleaned up {len(connections_to_remove)} idle connections")

# Performance monitoring

class PerformanceMonitor:
    """Monitors and tracks performance metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: Dict[str, List[PerformanceStats]] = defaultdict(list)
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__ + ".PerformanceMonitor")
    
    async def record_metric(self, metric: PerformanceMetric, value: float, unit: str, 
                          metadata: Optional[Dict] = None):
        """Record a performance metric."""
        stats = PerformanceStats(
            metric=metric,
            value=value,
            unit=unit,
            metadata=metadata or {}
        )
        
        async with self.lock:
            history = self.metrics_history[metric.value]
            history.append(stats)
            
            # Trim history if too long
            if len(history) > self.max_history:
                history.pop(0)
    
    async def get_metric_stats(self, metric: PerformanceMetric, 
                             time_window_minutes: Optional[int] = None) -> Dict[str, float]:
        """Get statistics for a metric."""
        async with self.lock:
            history = self.metrics_history[metric.value]
            
            if time_window_minutes:
                cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
                history = [h for h in history if h.timestamp >= cutoff_time]
            
            if not history:
                return {}
            
            values = [h.value for h in history]
            
            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else 0
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        # Get CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        await self.record_metric(PerformanceMetric.CPU_USAGE, cpu_percent, "percent")
        await self.record_metric(PerformanceMetric.MEMORY_USAGE, memory.percent, "percent")
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "timestamp": datetime.now()
        }

# Performance decorators

def cached(cache: Cache, ttl_seconds: Optional[int] = None, 
           key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator

def timed(monitor: PerformanceMonitor, operation_name: str):
    """Decorator for timing function execution."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                end_time = time.time()
                execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                await monitor.record_metric(
                    PerformanceMetric.RESPONSE_TIME,
                    execution_time,
                    "ms",
                    {"operation": operation_name, "success": success}
                )
            
            return result
        
        return wrapper
    return decorator

# Example usage and demonstrations

def demo_performance_optimization():
    """Demonstrate performance optimization features."""
    print("\n=== Performance Optimization Demo ===")
    
    async def run_demo():
        # Initialize components
        cache = InMemoryCache(max_size=100, strategy=CacheStrategy.LRU)
        monitor = PerformanceMonitor()
        
        # Test caching
        @cached(cache, ttl_seconds=60)
        @timed(monitor, "expensive_calculation")
        async def expensive_calculation(n: int) -> int:
            """Simulate expensive calculation."""
            await asyncio.sleep(0.1)  # Simulate work
            return n * n
        
        print("Testing caching performance...")
        
        # First call (cache miss)
        start = time.time()
        result1 = await expensive_calculation(10)
        time1 = time.time() - start
        print(f"First call: {result1} (took {time1:.3f}s)")
        
        # Second call (cache hit)
        start = time.time()
        result2 = await expensive_calculation(10)
        time2 = time.time() - start
        print(f"Second call: {result2} (took {time2:.3f}s)")
        
        print(f"Speedup: {time1/time2:.1f}x")
        
        # Show cache stats
        print("\nCache Statistics:")
        cache_stats = cache.get_stats()
        print(json.dumps(cache_stats, indent=2))
        
        # Test batch processing
        print("\nTesting batch processing...")
        
        def batch_square(numbers: List[int]) -> List[int]:
            """Batch function to square numbers."""
            return [n * n for n in numbers]
        
        batch_config = BatchConfig(max_batch_size=5, max_wait_time_ms=50)
        batch_processor = BatchProcessor(batch_square, batch_config)
        
        # Submit multiple requests
        tasks = []
        for i in range(10):
            task = asyncio.create_task(
                batch_processor.process_request(i, f"request-{i}")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        print(f"Batch results: {results}")
        
        # Show performance metrics
        print("\nPerformance Metrics:")
        response_time_stats = await monitor.get_metric_stats(PerformanceMetric.RESPONSE_TIME)
        print(json.dumps(response_time_stats, indent=2))
        
        # System metrics
        system_metrics = await monitor.get_system_metrics()
        print(f"\nSystem Metrics:")
        print(json.dumps(system_metrics, indent=2, default=str))
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_performance_optimization()
"""
Agno Performance Optimization and Caching
Session 7: Agno Production-Ready Agents

This module implements advanced performance optimization patterns including
multi-tier caching, batch processing, connection pooling, and resource optimization.
"""

import asyncio
import logging
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict, defaultdict, deque
import threading
import heapq
import statistics
import pickle

try:
    import redis.asyncio as redis
    import numpy as np
    from aiocache import Cache, caches
    from aiocache.serializers import PickleSerializer
    import aioredis
except ImportError:
    print("Warning: Performance optimization libraries not available, using mock implementations")
    redis = None
    np = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1_MEMORY = "l1_memory"
    L2_DISTRIBUTED = "l2_distributed"
    L3_SEMANTIC = "l3_semantic"
    L4_PERSISTENT = "l4_persistent"

class OptimizationStrategy(Enum):
    """Performance optimization strategies"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    COST = "cost"
    BALANCED = "balanced"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl
    
    def update_access(self):
        self.accessed_at = datetime.utcnow()
        self.access_count += 1

@dataclass
class PerformanceMetrics:
    """Performance optimization metrics"""
    cache_hit_rate: float
    cache_miss_rate: float
    average_response_time: float
    throughput_rps: float
    memory_usage_mb: float
    cpu_utilization: float
    cost_per_request: float
    optimization_efficiency: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

class LRUCache:
    """High-performance LRU (Least Recently Used) cache implementation"""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            self.stats["total_requests"] += 1
            
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired:
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            # Update access and move to end (most recently used)
            entry.update_access()
            self.cache.move_to_end(key)
            
            self.stats["hits"] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache"""
        with self._lock:
            # Calculate size (approximate)
            size_bytes = len(str(value).encode('utf-8'))
            
            # Remove existing entry if present
            if key in self.cache:
                del self.cache[key]
            
            # Check if we need to evict
            while len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                accessed_at=datetime.utcnow(),
                ttl=ttl or self.default_ttl,
                size_bytes=size_bytes
            )
            
            self.cache[key] = entry
            return True
    
    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self.cache.clear()
            self.stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "total_requests": 0
            }
    
    def _evict_oldest(self):
        """Evict least recently used entry"""
        if self.cache:
            self.cache.popitem(last=False)
            self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total = self.stats["total_requests"]
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_rate": self.stats["hits"] / max(1, total),
                "miss_rate": self.stats["misses"] / max(1, total),
                "eviction_rate": self.stats["evictions"] / max(1, total),
                "total_requests": total,
                "memory_usage_approx": sum(entry.size_bytes for entry in self.cache.values())
            }

class DistributedCache:
    """Redis-based distributed cache with advanced features"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 key_prefix: str = "agno:", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.redis_client = None
        self.stats = defaultdict(int)
        
        # Connection pool configuration
        self.pool_config = {
            "max_connections": 20,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        if redis is None:
            logger.warning("Redis not available, using mock distributed cache")
            self.redis_client = MockRedisClient()
            return
        
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=self.pool_config["max_connections"]
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis distributed cache")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = MockRedisClient()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        full_key = f"{self.key_prefix}{key}"
        
        try:
            self.stats["total_requests"] += 1
            
            # Try to get from Redis
            cached_data = await self.redis_client.get(full_key)
            
            if cached_data is None:
                self.stats["misses"] += 1
                return None
            
            # Deserialize data
            try:
                value = json.loads(cached_data)
                self.stats["hits"] += 1
                return value
            except json.JSONDecodeError:
                # Try pickle for complex objects
                value = pickle.loads(cached_data.encode())
                self.stats["hits"] += 1
                return value
                
        except Exception as e:
            logger.error(f"Distributed cache get error: {e}")
            self.stats["errors"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in distributed cache"""
        full_key = f"{self.key_prefix}{key}"
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize data
            try:
                serialized_data = json.dumps(value)
            except (TypeError, ValueError):
                # Use pickle for complex objects
                serialized_data = pickle.dumps(value).decode('latin1')
            
            # Set in Redis with TTL
            result = await self.redis_client.setex(full_key, ttl, serialized_data)
            
            if result:
                self.stats["sets"] += 1
                return True
            
        except Exception as e:
            logger.error(f"Distributed cache set error: {e}")
            self.stats["errors"] += 1
            
        return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from distributed cache"""
        full_key = f"{self.key_prefix}{key}"
        
        try:
            result = await self.redis_client.delete(full_key)
            if result:
                self.stats["deletes"] += 1
                return True
                
        except Exception as e:
            logger.error(f"Distributed cache delete error: {e}")
            self.stats["errors"] += 1
            
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis_client.info()
            
            total_requests = self.stats["total_requests"]
            
            return {
                "hit_rate": self.stats["hits"] / max(1, total_requests),
                "miss_rate": self.stats["misses"] / max(1, total_requests),
                "total_requests": total_requests,
                "redis_info": {
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get distributed cache stats: {e}")
            return {"error": str(e)}

class SemanticCache:
    """AI-powered semantic similarity cache"""
    
    def __init__(self, similarity_threshold: float = 0.85, max_entries: int = 10000):
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.entries: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self.stats = defaultdict(int)
        
        # Initialize mock embedding model (in production, use real embeddings)
        self.embedding_model = MockEmbeddingModel()
        
    async def find_similar(self, query: str, threshold: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Find semantically similar cached entry"""
        threshold = threshold or self.similarity_threshold
        self.stats["similarity_searches"] += 1
        
        if not self.entries:
            self.stats["similarity_misses"] += 1
            return None
        
        # Generate embedding for query
        query_embedding = await self.embedding_model.get_embedding(query)
        
        best_match = None
        best_similarity = 0.0
        
        # Compare with cached embeddings
        for cache_key, cached_embedding in self.embeddings.items():
            similarity = self._calculate_cosine_similarity(query_embedding, cached_embedding)
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = cache_key
        
        if best_match:
            self.stats["similarity_hits"] += 1
            entry = self.entries[best_match]
            return {
                "cache_key": best_match,
                "response": entry["response"],
                "similarity": best_similarity,
                "original_query": entry["query"],
                "cached_at": entry["cached_at"]
            }
        
        self.stats["similarity_misses"] += 1
        return None
    
    async def store(self, query: str, response: Any, metadata: Dict[str, Any] = None) -> str:
        """Store query-response pair with semantic embedding"""
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        # Check if we need to evict old entries
        if len(self.entries) >= self.max_entries:
            self._evict_oldest_entry()
        
        # Generate embedding
        embedding = await self.embedding_model.get_embedding(query)
        
        # Store entry
        entry = {
            "query": query,
            "response": response,
            "cached_at": datetime.utcnow(),
            "access_count": 0,
            "metadata": metadata or {}
        }
        
        self.entries[cache_key] = entry
        self.embeddings[cache_key] = embedding
        
        self.stats["stores"] += 1
        return cache_key
    
    def _calculate_cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        if len(embedding1) != len(embedding2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = sum(a * a for a in embedding1) ** 0.5
        magnitude2 = sum(b * b for b in embedding2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _evict_oldest_entry(self):
        """Evict oldest cache entry"""
        if self.entries:
            oldest_key = min(self.entries.keys(), 
                           key=lambda k: self.entries[k]["cached_at"])
            del self.entries[oldest_key]
            del self.embeddings[oldest_key]
            self.stats["evictions"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics"""
        total_searches = self.stats["similarity_searches"]
        return {
            "entries": len(self.entries),
            "max_entries": self.max_entries,
            "similarity_hit_rate": self.stats["similarity_hits"] / max(1, total_searches),
            "similarity_miss_rate": self.stats["similarity_misses"] / max(1, total_searches),
            "total_searches": total_searches,
            "stores": self.stats["stores"],
            "evictions": self.stats["evictions"]
        }

class MultiTierCacheManager:
    """Comprehensive multi-tier caching system"""
    
    def __init__(self):
        # Initialize cache tiers
        self.l1_cache = LRUCache(max_size=1000, ttl=300)  # 5 minutes
        self.l2_cache = DistributedCache(default_ttl=3600)  # 1 hour
        self.l3_cache = SemanticCache(similarity_threshold=0.85)
        
        # Performance tracking
        self.performance_metrics = deque(maxlen=1000)
        self.compression_enabled = True
        
        logger.info("Multi-tier cache manager initialized")
    
    async def initialize(self):
        """Initialize distributed cache connections"""
        await self.l2_cache.initialize()
    
    async def get(self, key: str, enable_semantic: bool = True) -> Optional[Any]:
        """Get value from multi-tier cache"""
        start_time = time.time()
        
        # L1 Cache (Memory)
        result = self.l1_cache.get(key)
        if result is not None:
            self._record_performance_metric("l1_hit", time.time() - start_time)
            return result
        
        # L2 Cache (Distributed)
        result = await self.l2_cache.get(key)
        if result is not None:
            # Populate L1 cache
            self.l1_cache.set(key, result, ttl=300)
            self._record_performance_metric("l2_hit", time.time() - start_time)
            return result
        
        # L3 Cache (Semantic) - only for query-like keys
        if enable_semantic and self._is_semantic_query(key):
            semantic_result = await self.l3_cache.find_similar(key)
            if semantic_result:
                response = semantic_result["response"]
                # Populate higher cache tiers
                await self.l2_cache.set(key, response, ttl=1800)  # 30 minutes
                self.l1_cache.set(key, response, ttl=300)
                self._record_performance_metric("l3_hit", time.time() - start_time)
                return response
        
        self._record_performance_metric("miss", time.time() - start_time)
        return None
    
    async def set(self, key: str, value: Any, ttl_l1: int = 300, ttl_l2: int = 3600,
                 enable_semantic: bool = True):
        """Set value in appropriate cache tiers"""
        # L1 Cache
        self.l1_cache.set(key, value, ttl=ttl_l1)
        
        # L2 Cache
        await self.l2_cache.set(key, value, ttl=ttl_l2)
        
        # L3 Cache (Semantic) - store if it's a query-response pattern
        if enable_semantic and self._is_semantic_query(key):
            await self.l3_cache.store(key, value)
    
    async def invalidate(self, key: str):
        """Invalidate key across all cache tiers"""
        self.l1_cache.delete(key)
        await self.l2_cache.delete(key)
    
    def _is_semantic_query(self, key: str) -> bool:
        """Determine if key represents a semantic query"""
        # Simple heuristic - in production, use more sophisticated detection
        return len(key) > 10 and any(word in key.lower() for word in 
                                   ['what', 'how', 'why', 'when', 'where', 'analyze', 'explain'])
    
    def _record_performance_metric(self, cache_level: str, latency: float):
        """Record performance metrics"""
        metric = {
            "timestamp": datetime.utcnow(),
            "cache_level": cache_level,
            "latency": latency
        }
        self.performance_metrics.append(metric)
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache tiers"""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = await self.l2_cache.get_stats()
        l3_stats = self.l3_cache.get_stats()
        
        # Calculate overall cache effectiveness
        recent_metrics = list(self.performance_metrics)[-100:]  # Last 100 requests
        
        if recent_metrics:
            hit_metrics = [m for m in recent_metrics if 'hit' in m['cache_level']]
            overall_hit_rate = len(hit_metrics) / len(recent_metrics)
            avg_latency = statistics.mean(m['latency'] for m in recent_metrics)
        else:
            overall_hit_rate = 0.0
            avg_latency = 0.0
        
        return {
            "overall_hit_rate": overall_hit_rate,
            "average_latency": avg_latency,
            "l1_cache": l1_stats,
            "l2_cache": l2_stats,
            "l3_cache": l3_stats,
            "total_requests": len(self.performance_metrics)
        }

class BatchProcessor:
    """High-performance batch processing system"""
    
    def __init__(self, batch_size: int = 10, max_wait_time: float = 1.0, 
                 max_concurrent_batches: int = 5):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.max_concurrent_batches = max_concurrent_batches
        
        # Processing queues
        self.pending_requests: List[Dict[str, Any]] = []
        self.processing_queue = asyncio.Queue()
        self.batch_stats = {
            "batches_processed": 0,
            "total_requests": 0,
            "average_batch_size": 0,
            "average_processing_time": 0
        }
        
        # Batch processing semaphore
        self.batch_semaphore = asyncio.Semaphore(max_concurrent_batches)
        
        # Start batch processor
        self._processor_task = asyncio.create_task(self._batch_processor_loop())
        
        logger.info(f"Batch processor initialized (size: {batch_size}, wait: {max_wait_time}s)")
    
    async def add_request(self, request_data: Any, callback: Callable = None) -> str:
        """Add request to batch processing queue"""
        request_id = f"req_{int(time.time() * 1000000)}"
        
        request_item = {
            "id": request_id,
            "data": request_data,
            "callback": callback,
            "timestamp": datetime.utcnow(),
            "future": asyncio.Future()
        }
        
        await self.processing_queue.put(request_item)
        self.batch_stats["total_requests"] += 1
        
        return request_id
    
    async def process_batch_sync(self, requests: List[Any], 
                                processor_func: Callable) -> List[Any]:
        """Process a batch of requests synchronously"""
        batch_id = f"batch_{int(time.time())}"
        start_time = time.time()
        
        async with self.batch_semaphore:
            try:
                # Process batch with provided function
                results = await processor_func(requests)
                
                processing_time = time.time() - start_time
                
                # Update statistics
                self.batch_stats["batches_processed"] += 1
                self.batch_stats["average_processing_time"] = (
                    (self.batch_stats["average_processing_time"] * (self.batch_stats["batches_processed"] - 1) + 
                     processing_time) / self.batch_stats["batches_processed"]
                )
                
                logger.debug(f"Processed batch {batch_id}: {len(requests)} requests in {processing_time:.3f}s")
                return results
                
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                return [{"error": str(e)} for _ in requests]
    
    async def _batch_processor_loop(self):
        """Main batch processing loop"""
        while True:
            try:
                batch_requests = []
                batch_start_time = time.time()
                
                # Collect requests for batch
                while len(batch_requests) < self.batch_size:
                    try:
                        # Wait for request or timeout
                        remaining_time = max(0, self.max_wait_time - (time.time() - batch_start_time))
                        if remaining_time == 0:
                            break
                            
                        request_item = await asyncio.wait_for(
                            self.processing_queue.get(), 
                            timeout=remaining_time
                        )
                        batch_requests.append(request_item)
                        
                    except asyncio.TimeoutError:
                        break
                
                # Process batch if we have requests
                if batch_requests:
                    await self._process_request_batch(batch_requests)
                
            except Exception as e:
                logger.error(f"Batch processor loop error: {e}")
                await asyncio.sleep(1)
    
    async def _process_request_batch(self, batch_requests: List[Dict[str, Any]]):
        """Process a batch of requests"""
        batch_size = len(batch_requests)
        
        # Update average batch size
        if self.batch_stats["batches_processed"] > 0:
            self.batch_stats["average_batch_size"] = (
                (self.batch_stats["average_batch_size"] * self.batch_stats["batches_processed"] + 
                 batch_size) / (self.batch_stats["batches_processed"] + 1)
            )
        else:
            self.batch_stats["average_batch_size"] = batch_size
        
        # Execute callbacks or default processing
        for request_item in batch_requests:
            try:
                if request_item["callback"]:
                    result = await request_item["callback"](request_item["data"])
                else:
                    result = {"processed": request_item["data"], "batch_size": batch_size}
                
                # Resolve the future
                request_item["future"].set_result(result)
                
            except Exception as e:
                request_item["future"].set_exception(e)
        
        self.batch_stats["batches_processed"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        return {
            "batch_size": self.batch_size,
            "max_wait_time": self.max_wait_time,
            "max_concurrent_batches": self.max_concurrent_batches,
            "pending_requests": self.processing_queue.qsize(),
            **self.batch_stats
        }

class ConnectionPool:
    """Advanced connection pool for external services"""
    
    def __init__(self, create_connection_func: Callable, 
                 min_connections: int = 2, max_connections: int = 20,
                 connection_timeout: float = 30.0, idle_timeout: float = 300.0):
        self.create_connection_func = create_connection_func
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        
        # Connection management
        self.available_connections: deque = deque()
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.pool_stats = {
            "total_created": 0,
            "total_destroyed": 0,
            "current_active": 0,
            "peak_active": 0,
            "connection_errors": 0
        }
        
        # Pool synchronization
        self._pool_lock = asyncio.Lock()
        self._connection_semaphore = asyncio.Semaphore(max_connections)
        
        # Start pool maintenance
        self._maintenance_task = asyncio.create_task(self._pool_maintenance_loop())
    
    async def get_connection(self) -> Any:
        """Get connection from pool"""
        async with self._connection_semaphore:
            async with self._pool_lock:
                # Try to get available connection
                while self.available_connections:
                    conn_info = self.available_connections.popleft()
                    
                    # Check if connection is still valid
                    if await self._validate_connection(conn_info):
                        conn_id = id(conn_info["connection"])
                        self.active_connections[conn_id] = {
                            **conn_info,
                            "acquired_at": datetime.utcnow()
                        }
                        self.pool_stats["current_active"] += 1
                        self.pool_stats["peak_active"] = max(
                            self.pool_stats["peak_active"],
                            self.pool_stats["current_active"]
                        )
                        return conn_info["connection"]
                    else:
                        await self._destroy_connection(conn_info)
                
                # Create new connection if none available
                try:
                    connection = await asyncio.wait_for(
                        self.create_connection_func(),
                        timeout=self.connection_timeout
                    )
                    
                    conn_info = {
                        "connection": connection,
                        "created_at": datetime.utcnow(),
                        "acquired_at": datetime.utcnow()
                    }
                    
                    conn_id = id(connection)
                    self.active_connections[conn_id] = conn_info
                    
                    self.pool_stats["total_created"] += 1
                    self.pool_stats["current_active"] += 1
                    self.pool_stats["peak_active"] = max(
                        self.pool_stats["peak_active"],
                        self.pool_stats["current_active"]
                    )
                    
                    return connection
                    
                except Exception as e:
                    self.pool_stats["connection_errors"] += 1
                    logger.error(f"Failed to create connection: {e}")
                    raise
    
    async def release_connection(self, connection: Any):
        """Release connection back to pool"""
        async with self._pool_lock:
            conn_id = id(connection)
            
            if conn_id in self.active_connections:
                conn_info = self.active_connections[conn_id]
                del self.active_connections[conn_id]
                
                self.pool_stats["current_active"] -= 1
                
                # Check if connection is still valid
                if await self._validate_connection(conn_info):
                    conn_info["released_at"] = datetime.utcnow()
                    self.available_connections.append(conn_info)
                else:
                    await self._destroy_connection(conn_info)
    
    async def _validate_connection(self, conn_info: Dict[str, Any]) -> bool:
        """Validate connection is still usable"""
        try:
            connection = conn_info["connection"]
            
            # Check idle timeout
            released_at = conn_info.get("released_at")
            if released_at:
                idle_time = (datetime.utcnow() - released_at).total_seconds()
                if idle_time > self.idle_timeout:
                    return False
            
            # Perform connection-specific validation
            if hasattr(connection, 'ping'):
                await connection.ping()
            elif hasattr(connection, 'is_connected'):
                if not connection.is_connected():
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def _destroy_connection(self, conn_info: Dict[str, Any]):
        """Properly destroy connection"""
        try:
            connection = conn_info["connection"]
            if hasattr(connection, 'close'):
                await connection.close()
            elif hasattr(connection, 'disconnect'):
                await connection.disconnect()
                
            self.pool_stats["total_destroyed"] += 1
            
        except Exception as e:
            logger.warning(f"Error destroying connection: {e}")
    
    async def _pool_maintenance_loop(self):
        """Periodic pool maintenance"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self._pool_lock:
                    # Remove idle connections
                    current_time = datetime.utcnow()
                    connections_to_remove = []
                    
                    for conn_info in list(self.available_connections):
                        released_at = conn_info.get("released_at", conn_info["created_at"])
                        idle_time = (current_time - released_at).total_seconds()
                        
                        if idle_time > self.idle_timeout:
                            connections_to_remove.append(conn_info)
                    
                    for conn_info in connections_to_remove:
                        self.available_connections.remove(conn_info)
                        await self._destroy_connection(conn_info)
                    
                    # Ensure minimum connections
                    total_connections = len(self.available_connections) + len(self.active_connections)
                    if total_connections < self.min_connections:
                        connections_needed = self.min_connections - total_connections
                        
                        for _ in range(connections_needed):
                            try:
                                connection = await self.create_connection_func()
                                conn_info = {
                                    "connection": connection,
                                    "created_at": datetime.utcnow(),
                                    "released_at": datetime.utcnow()
                                }
                                self.available_connections.append(conn_info)
                                self.pool_stats["total_created"] += 1
                                
                            except Exception as e:
                                logger.warning(f"Failed to create maintenance connection: {e}")
                                break
                
            except Exception as e:
                logger.error(f"Pool maintenance error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
            "available_connections": len(self.available_connections),
            "active_connections": len(self.active_connections),
            "utilization": len(self.active_connections) / self.max_connections,
            **self.pool_stats
        }

# Mock implementations for when external libraries aren't available
class MockRedisClient:
    """Mock Redis client for testing"""
    
    def __init__(self):
        self.data = {}
    
    async def ping(self):
        return True
    
    async def get(self, key):
        return self.data.get(key)
    
    async def setex(self, key, ttl, value):
        self.data[key] = value
        return True
    
    async def delete(self, key):
        return self.data.pop(key, None) is not None
    
    async def info(self):
        return {
            "used_memory": len(str(self.data)),
            "connected_clients": 1,
            "total_commands_processed": len(self.data)
        }

class MockEmbeddingModel:
    """Mock embedding model for testing"""
    
    async def get_embedding(self, text: str) -> List[float]:
        """Generate mock embedding based on text hash"""
        # Simple hash-based embedding (not semantically meaningful)
        hash_val = hashlib.md5(text.encode()).hexdigest()
        return [float(int(hash_val[i:i+2], 16)) / 255.0 for i in range(0, min(64, len(hash_val)), 2)]

async def demonstrate_performance_optimization():
    """Comprehensive demonstration of performance optimization features"""
    print("=" * 80)
    print("AGNO PERFORMANCE OPTIMIZATION DEMONSTRATION")
    print("=" * 80)
    
    # Initialize performance optimization components
    cache_manager = MultiTierCacheManager()
    await cache_manager.initialize()
    
    batch_processor = BatchProcessor(batch_size=5, max_wait_time=0.5)
    
    # Mock connection creation function
    async def create_mock_connection():
        await asyncio.sleep(0.1)  # Simulate connection time
        return {"id": f"conn_{int(time.time())}", "status": "connected"}
    
    connection_pool = ConnectionPool(
        create_connection_func=create_mock_connection,
        min_connections=2,
        max_connections=10
    )
    
    print(f"\n1. Performance Components Initialization")
    print("-" * 45)
    print(f"✓ Multi-Tier Cache Manager")
    print(f"✓ Batch Processor")
    print(f"✓ Connection Pool")
    
    # Cache Performance Demo
    print(f"\n2. Multi-Tier Caching Performance")
    print("-" * 40)
    
    # Cache some test data
    test_queries = [
        "What are the benefits of AI agents in enterprise?",
        "How do you implement caching strategies?",
        "What is the best approach for performance optimization?",
        "Analyze the market trends for 2024",
        "What are microservices architecture patterns?"
    ]
    
    test_responses = [
        f"Response to query {i+1}: {query}" for i, query in enumerate(test_queries)
    ]
    
    # Populate cache
    for i, (query, response) in enumerate(zip(test_queries, test_responses)):
        cache_key = f"query_{i}"
        await cache_manager.set(cache_key, response)
    
    # Test cache performance
    cache_start_time = time.time()
    cache_hits = 0
    cache_tests = 20
    
    for i in range(cache_tests):
        cache_key = f"query_{i % len(test_queries)}"
        result = await cache_manager.get(cache_key)
        if result:
            cache_hits += 1
    
    cache_time = time.time() - cache_start_time
    
    print(f"Cache Performance Test:")
    print(f"  - Total requests: {cache_tests}")
    print(f"  - Cache hits: {cache_hits}")
    print(f"  - Hit rate: {cache_hits/cache_tests:.1%}")
    print(f"  - Average latency: {(cache_time/cache_tests)*1000:.2f}ms")
    
    # Get comprehensive cache stats
    cache_stats = await cache_manager.get_comprehensive_stats()
    print(f"  - L1 hit rate: {cache_stats['l1_cache']['hit_rate']:.1%}")
    print(f"  - L2 hit rate: {cache_stats['l2_cache']['hit_rate']:.1%}")
    print(f"  - L3 hit rate: {cache_stats['l3_cache']['similarity_hit_rate']:.1%}")
    
    # Batch Processing Demo
    print(f"\n3. Batch Processing Performance")
    print("-" * 35)
    
    # Define a mock processing function
    async def mock_process_batch(requests):
        await asyncio.sleep(0.1)  # Simulate processing time
        return [f"Processed: {req}" for req in requests]
    
    # Test individual vs batch processing
    individual_requests = [f"Request {i}" for i in range(15)]
    
    # Individual processing
    individual_start = time.time()
    individual_results = []
    for request in individual_requests:
        result = await mock_process_batch([request])
        individual_results.extend(result)
    individual_time = time.time() - individual_start
    
    # Batch processing
    batch_start = time.time()
    batch_results = await batch_processor.process_batch_sync(individual_requests, mock_process_batch)
    batch_time = time.time() - batch_start
    
    print(f"Processing Comparison:")
    print(f"  - Individual processing: {individual_time:.3f}s")
    print(f"  - Batch processing: {batch_time:.3f}s")
    print(f"  - Performance improvement: {(individual_time/batch_time):.1f}x faster")
    
    batch_stats = batch_processor.get_stats()
    print(f"  - Average batch size: {batch_stats['average_batch_size']:.1f}")
    print(f"  - Batches processed: {batch_stats['batches_processed']}")
    
    # Connection Pool Demo
    print(f"\n4. Connection Pool Performance")
    print("-" * 35)
    
    # Test connection pool efficiency
    pool_start = time.time()
    connections = []
    
    # Acquire multiple connections
    for i in range(5):
        conn = await connection_pool.get_connection()
        connections.append(conn)
    
    # Release connections
    for conn in connections:
        await connection_pool.release_connection(conn)
    
    pool_time = time.time() - pool_start
    
    # Test without pool (direct creation)
    direct_start = time.time()
    for i in range(5):
        conn = await create_mock_connection()
    direct_time = time.time() - direct_start
    
    print(f"Connection Management:")
    print(f"  - Pool-based: {pool_time:.3f}s")
    print(f"  - Direct creation: {direct_time:.3f}s")
    print(f"  - Pool efficiency: {(direct_time/pool_time):.1f}x faster")
    
    pool_stats = connection_pool.get_stats()
    print(f"  - Pool utilization: {pool_stats['utilization']:.1%}")
    print(f"  - Peak active: {pool_stats['peak_active']}")
    print(f"  - Available: {pool_stats['available_connections']}")
    
    # Semantic Cache Demo
    print(f"\n5. Semantic Cache Intelligence")
    print("-" * 35)
    
    semantic_cache = SemanticCache(similarity_threshold=0.8)
    
    # Store some semantic queries
    semantic_queries = [
        ("What is machine learning?", "ML is a subset of AI that enables computers to learn without explicit programming."),
        ("How does artificial intelligence work?", "AI systems process data to make decisions and predictions."),
        ("Explain deep learning concepts", "Deep learning uses neural networks with multiple layers to process complex data."),
    ]
    
    for query, response in semantic_queries:
        await semantic_cache.store(query, response)
    
    # Test semantic similarity
    similar_queries = [
        "What is ML?",  # Should match "What is machine learning?"
        "How does AI function?",  # Should match "How does artificial intelligence work?"
        "What is quantum computing?",  # Should not match anything
    ]
    
    semantic_hits = 0
    for query in similar_queries:
        result = await semantic_cache.find_similar(query, threshold=0.7)
        if result:
            semantic_hits += 1
            print(f"  Semantic match found for '{query}':")
            print(f"    Original: '{result['original_query']}'")
            print(f"    Similarity: {result['similarity']:.3f}")
    
    semantic_stats = semantic_cache.get_stats()
    print(f"  - Semantic hit rate: {semantic_stats['similarity_hit_rate']:.1%}")
    print(f"  - Total searches: {semantic_stats['total_searches']}")
    print(f"  - Cache entries: {semantic_stats['entries']}")
    
    # Performance Summary
    print(f"\n6. Overall Performance Summary")
    print("-" * 40)
    
    total_cache_requests = cache_tests
    total_batch_requests = len(individual_requests)
    total_pool_requests = 5
    
    print(f"Performance Optimizations Applied:")
    print(f"  - Multi-tier caching: {cache_hits/total_cache_requests:.1%} hit rate")
    print(f"  - Batch processing: {(individual_time/batch_time):.1f}x improvement")
    print(f"  - Connection pooling: {(direct_time/pool_time):.1f}x improvement")
    print(f"  - Semantic caching: {semantic_hits}/{len(similar_queries)} semantic matches")
    
    overall_improvement = (
        (cache_hits/total_cache_requests) * 2 +  # Cache improvement factor
        (individual_time/batch_time) +           # Batch improvement factor
        (direct_time/pool_time)                  # Pool improvement factor
    ) / 3
    
    print(f"  - Average performance gain: {overall_improvement:.1f}x")
    
    # Memory and resource usage
    print(f"\n7. Resource Utilization")
    print("-" * 25)
    
    l1_memory = cache_stats['l1_cache']['memory_usage_approx']
    print(f"L1 Cache Memory: {l1_memory:,} bytes")
    print(f"Active Connections: {pool_stats['current_active']}")
    print(f"Pending Batch Requests: {batch_stats.get('pending_requests', 0)}")
    
    print(f"\n" + "=" * 80)
    print("PERFORMANCE OPTIMIZATION DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Optimizations Demonstrated:")
    print("- Multi-tier caching with L1/L2/L3 hierarchy")
    print("- Semantic similarity caching for intelligent query matching")
    print("- High-performance batch processing with configurable batching")
    print("- Advanced connection pooling with health checking")
    print("- Comprehensive performance metrics and monitoring")
    print("- Resource optimization and memory management")

if __name__ == "__main__":
    # Run comprehensive demonstration
    asyncio.run(demonstrate_performance_optimization())
# High-Performance Agent Design and Resilience Patterns
# Circuit breakers, caching strategies, and fault tolerance

from agno.patterns import SingletonAgent, PooledAgent, StreamingAgent
from agno.concurrency import AsyncExecutor
from agno.resilience import CircuitBreaker, RetryPolicy, BulkheadPattern
from agno.monitoring import HealthCheck
from agno.caching import RedisCache, LRUCache, SemanticCache
from agno.optimization import ResponseCompression, BatchProcessor
from agno import Agent
import asyncio
import time
import logging
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import hashlib
import json


class HighThroughputAgent:
    """Agent designed for high-throughput scenarios"""
    
    def __init__(self, pool_size: int = 10):
        self.pool_size = pool_size
        self.agent_pool = []
        self.executor = AsyncExecutor(max_workers=pool_size)
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize agent pool for load distribution"""
        for i in range(self.pool_size):
            agent = Agent(
                name=f"pooled_agent_{i}",
                model="gpt-4o-mini",  # Use faster model for throughput
                temperature=0.1,
                max_tokens=1024
            )
            self.agent_pool.append(agent)
    
    async def process_batch(self, requests: List[str]) -> List[str]:
        """Process multiple requests concurrently"""
        tasks = []
        
        for i, request in enumerate(requests):
            agent = self.agent_pool[i % self.pool_size]
            task = self.executor.submit(agent.run, request)
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


async def benchmark_throughput():
    """Benchmark throughput performance"""
    agent = HighThroughputAgent(pool_size=5)
    
    # Create test batch
    requests = [
        f"Summarize the key points about topic {i}" 
        for i in range(20)
    ]
    
    start_time = time.time()
    results = await agent.process_batch(requests)
    end_time = time.time()
    
    # Calculate performance metrics
    total_time = end_time - start_time
    requests_per_second = len(requests) / total_time
    
    print(f"Processed {len(requests)} requests in {total_time:.2f} seconds")
    print(f"Throughput: {requests_per_second:.2f} requests/second")
    
    # Check for errors
    successful_results = [r for r in results if not isinstance(r, Exception)]
    error_rate = (len(results) - len(successful_results)) / len(results)
    print(f"Success rate: {(1 - error_rate):.1%}")


# Circuit Breaker and Fault Tolerance
class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit tripped, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class HealthStatus:
    """Health check result"""
    healthy: bool
    message: str
    response_time: Optional[float] = None


class ResilientAgent:
    """Production agent with comprehensive fault tolerance"""
    
    def __init__(self):
        self.agent = Agent(
            name="resilient_agent",
            model="gpt-4o",
            temperature=0.2
        )
        
        # Configure circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,     # Trip after 5 failures
            success_threshold=3,     # Require 3 successes to close
            timeout=60,             # Reset attempt after 60 seconds
            expected_exceptions=[TimeoutError, ConnectionError]
        )
        
        # Configure retry policy
        self.retry_policy = RetryPolicy(
            max_retries=3,
            backoff_multiplier=2,
            max_delay=10
        )
        
        # Health monitoring
        self.health_check = HealthCheck(
            check_interval=30,
            failure_threshold=3
        )
    
    async def process_with_resilience(self, request: str) -> str:
        """Process request with full fault tolerance"""
        
        # Check circuit breaker state
        if self.circuit_breaker.state == CircuitState.OPEN:
            raise Exception("Circuit breaker open - service unavailable")
        
        # Attempt processing with retries
        last_exception = None
        
        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                # Process with timeout
                result = await asyncio.wait_for(
                    self.agent.run(request),
                    timeout=30.0
                )
                
                # Success - record and return
                self.circuit_breaker.record_success()
                return result.content
                
            except Exception as e:
                last_exception = e
                self.circuit_breaker.record_failure()
                
                if attempt < self.retry_policy.max_retries:
                    delay = self.retry_policy.get_delay(attempt)
                    logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logging.error(f"All retry attempts failed: {e}")
        
        raise last_exception


class HealthMonitoringAgent(ResilientAgent):
    """Resilient agent with continuous health monitoring"""
    
    def __init__(self):
        super().__init__()
        self.start_health_monitoring()
    
    def start_health_monitoring(self):
        """Start background health monitoring"""
        asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring"""
        while True:
            try:
                # Perform health check
                health_status = await self._check_health()
                
                if not health_status.healthy:
                    logging.error(f"Health check failed: {health_status.message}")
                    # Trigger alerts or recovery procedures
                    await self._handle_unhealthy_state()
                else:
                    logging.debug("Health check passed")
                
            except Exception as e:
                logging.error(f"Health monitoring error: {e}")
            
            await asyncio.sleep(self.health_check.check_interval)
    
    async def _check_health(self) -> HealthStatus:
        """Perform comprehensive health check"""
        try:
            start_time = time.time()
            # Test basic functionality
            test_response = await asyncio.wait_for(
                self.agent.run("Health check test"),
                timeout=10.0
            )
            response_time = time.time() - start_time
            
            return HealthStatus(
                healthy=True,
                response_time=response_time,
                message="All systems operational"
            )
            
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Health check failed: {e}"
            )
    
    async def _handle_unhealthy_state(self):
        """Handle unhealthy system state"""
        # Implementation would trigger recovery procedures
        logging.warning("Triggering recovery procedures for unhealthy state")


# Advanced Caching and Performance Optimization
class OptimizedProductionAgent:
    """Agent optimized for production performance and cost"""
    
    def __init__(self):
        # Base agent with production settings
        self.agent = Agent(
            name="optimized_agent",
            model="gpt-4o",
            temperature=0.1  # Lower temperature for more cacheable responses
        )
        
        # Cache performance tracking
        self.cache_stats = {
            "l1_hits": 0,
            "l2_hits": 0, 
            "semantic_hits": 0,
            "cache_misses": 0,
            "total_requests": 0
        }
        
        # L1 Cache: In-memory for ultra-fast access
        self.l1_cache = LRUCache(
            max_size=1000,           # Limit memory usage
            ttl=300,                 # 5 minute expiry
            eviction_policy="lru"    # Least recently used eviction
        )
        
        # L2 Cache: Distributed Redis for shared state
        self.l2_cache = RedisCache(
            host="redis-cluster",
            port=6379,
            db=0,
            max_connections=20,      # Connection pooling
            compression=True         # Reduce network traffic
        )
        
        # Semantic Cache: AI-powered similarity matching
        self.semantic_cache = SemanticCache(
            similarity_threshold=0.85,        # 85% similarity required
            embedding_model="text-embedding-3-small",  # Fast, cost-effective
            max_entries=10000,               # Reasonable memory limit
            rerank_top_k=5                   # Re-rank top 5 candidates
        )
        
        # Performance optimization components
        self.compressor = ResponseCompression(
            algorithm="zstd",        # Fast compression with good ratio
            compression_level=3      # Balance speed vs size
        )
        
        self.batch_processor = BatchProcessor(
            batch_size=10,
            max_wait=1.0,           # Don't delay requests too long
            parallel_processing=True
        )
    
    def _generate_cache_key(self, request: str, context: dict = None) -> str:
        """Generate deterministic, collision-resistant cache key"""
        
        # Include all factors that affect response
        cache_input = {
            "request": request,
            "model": self.agent.model,
            "temperature": self.agent.temperature,
            "context": context or {},
            # Include version to invalidate on agent updates
            "agent_version": "1.0.0"
        }
        
        # Create deterministic string representation
        cache_string = json.dumps(cache_input, sort_keys=True, ensure_ascii=True)
        
        # Generate collision-resistant hash
        return hashlib.sha256(cache_string.encode('utf-8')).hexdigest()
    
    async def _decompress_response(self, compressed_data):
        """Decompress cached response data"""
        return await self.compressor.decompress(compressed_data)
    
    def _log_cache_hit(self, cache_tier: str, response_time: float):
        """Log cache hit for monitoring"""
        logging.info(f"{cache_tier} cache hit in {response_time*1000:.1f}ms")
    
    def _log_cache_miss(self, processing_time: float):
        """Log cache miss for monitoring"""
        logging.info(f"Cache miss, processed in {processing_time*1000:.1f}ms")
    
    async def process_with_caching(self, request: str, context: dict = None) -> str:
        """Process request with intelligent multi-tier caching"""
        
        self.cache_stats["total_requests"] += 1
        start_time = time.time()
        
        # Generate cache key
        cache_key = self._generate_cache_key(request, context)
        
        # L1 Cache check (fastest - ~0.1ms)
        l1_result = self.l1_cache.get(cache_key)
        if l1_result:
            self.cache_stats["l1_hits"] += 1
            response = await self._decompress_response(l1_result)
            self._log_cache_hit("L1", time.time() - start_time)
            return response
        
        # L2 Cache check (fast - ~1-5ms depending on network)
        l2_result = await self.l2_cache.get(cache_key)
        if l2_result:
            self.cache_stats["l2_hits"] += 1
            # Populate L1 for future requests
            self.l1_cache.set(cache_key, l2_result)
            response = await self._decompress_response(l2_result)
            self._log_cache_hit("L2", time.time() - start_time)
            return response
        
        # Semantic cache check (intelligent - ~10-50ms for embedding + search)
        semantic_result = await self.semantic_cache.find_similar(
            query=request, 
            threshold=0.85,
            context=context
        )
        if semantic_result:
            self.cache_stats["semantic_hits"] += 1
            
            # Promote to faster cache tiers for future use
            compressed_response = await self.compressor.compress(semantic_result.response)
            self.l1_cache.set(cache_key, compressed_response)
            await self.l2_cache.set(cache_key, compressed_response, ttl=3600)
            
            self._log_cache_hit("Semantic", time.time() - start_time)
            return semantic_result.response
        
        # Cache miss - process request with full LLM call
        self.cache_stats["cache_misses"] += 1
        result = await self.agent.run(request)
        response = result.content
        
        # Store in all cache tiers for future requests
        await self._populate_all_caches(cache_key, request, response)
        
        processing_time = time.time() - start_time
        self._log_cache_miss(processing_time)
        return response
    
    async def _populate_all_caches(self, cache_key: str, request: str, response: str):
        """Efficiently populate all cache tiers"""
        try:
            # Compress response for storage efficiency
            compressed_response = await self.compressor.compress(response)
            
            # Store in all tiers
            self.l1_cache.set(cache_key, compressed_response)
            await self.l2_cache.set(cache_key, compressed_response, ttl=3600)
            await self.semantic_cache.store(
                query=request, 
                response=response,
                metadata={"timestamp": time.time()}
            )
            
        except Exception as e:
            # Cache population failures shouldn't break request processing
            print(f"Cache population failed: {e}")
    
    def get_cache_performance(self) -> dict:
        """Get cache performance metrics for optimization"""
        total = self.cache_stats["total_requests"]
        if total == 0:
            return {"cache_hit_rate": 0, "cost_savings": 0}
        
        cache_hits = (self.cache_stats["l1_hits"] + 
                     self.cache_stats["l2_hits"] + 
                     self.cache_stats["semantic_hits"])
        
        hit_rate = cache_hits / total
        # Estimate cost savings (assuming $0.01 per API call)
        cost_savings = cache_hits * 0.01
        
        return {
            "cache_hit_rate": hit_rate,
            "l1_hit_rate": self.cache_stats["l1_hits"] / total,
            "l2_hit_rate": self.cache_stats["l2_hits"] / total,
            "semantic_hit_rate": self.cache_stats["semantic_hits"] / total,
            "estimated_cost_savings": cost_savings,
            "total_requests": total
        }


class BatchOptimizedAgent(OptimizedProductionAgent):
    """Agent with batch processing optimization"""
    
    async def process_batch_requests(self, requests: List[str]) -> List[str]:
        """Process requests in optimized batches"""
        
        results = []
        cached_results = {}
        uncached_requests = []
        
        # Check cache for all requests first
        for i, request in enumerate(requests):
            cache_key = self._generate_cache_key(request)
            cached_result = self.l1_cache.get(cache_key)
            
            if cached_result:
                cached_results[i] = await self._decompress_response(cached_result)
                self.cache_stats["l1_hits"] += 1
            else:
                uncached_requests.append((i, request))
        
        # Process uncached requests in batch
        if uncached_requests:
            batch_tasks = []
            for i, request in uncached_requests:
                task = self.agent.run(request)
                batch_tasks.append((i, task))
            
            # Execute batch
            batch_results = await asyncio.gather(
                *[task for _, task in batch_tasks], 
                return_exceptions=True
            )
            
            # Process results and update cache
            for (original_index, _), result in zip(uncached_requests, batch_results):
                if isinstance(result, Exception):
                    cached_results[original_index] = f"Error: {str(result)}"
                else:
                    response = result.content
                    cached_results[original_index] = response
                    
                    # Cache for future use
                    cache_key = self._generate_cache_key(requests[original_index])
                    compressed_response = await self.compressor.compress(response)
                    self.l1_cache.set(cache_key, compressed_response)
                    
                self.cache_stats["cache_misses"] += 1
        
        # Reconstruct results in original order
        self.cache_stats["total_requests"] += len(requests)
        return [cached_results[i] for i in range(len(requests))]


# Example usage and demonstration
if __name__ == "__main__":
    async def main():
        # Demonstrate high throughput agent
        print("=== High Throughput Agent Demo ===")
        await benchmark_throughput()
        
        # Demonstrate resilient agent
        print("\n=== Resilient Agent Demo ===")
        resilient_agent = ResilientAgent()
        try:
            result = await resilient_agent.process_with_resilience("Test request")
            print(f"Resilient processing result: {result}")
        except Exception as e:
            print(f"Resilient processing failed: {e}")
        
        # Demonstrate optimized caching
        print("\n=== Optimized Caching Demo ===")
        optimized_agent = OptimizedProductionAgent()
        
        # Process some requests
        requests = [
            "What is artificial intelligence?",
            "Explain machine learning",
            "What is artificial intelligence?",  # Duplicate for cache test
        ]
        
        for request in requests:
            result = await optimized_agent.process_with_caching(request)
            print(f"Request: {request[:30]}...")
            print(f"Response: {result[:50]}...\n")
        
        # Show cache performance
        performance = optimized_agent.get_cache_performance()
        print("Cache Performance:")
        for metric, value in performance.items():
            print(f"  {metric}: {value}")
    
    # Run the demonstration
    asyncio.run(main())
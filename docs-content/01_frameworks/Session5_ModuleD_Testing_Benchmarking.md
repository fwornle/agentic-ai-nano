# Session 5 - Module D: Testing & Benchmarking

**Prerequisites**: [Session 5 Core Section Complete](Session5_PydanticAI_Type_Safe_Agents.md)

## Module Overview

Comprehensive testing strategies, performance benchmarking, and enterprise monitoring for PydanticAI applications. Build systematic testing frameworks, performance optimization, production monitoring systems, enterprise-grade observability, and intelligent caching patterns.

---

## Part 1: Comprehensive Testing Framework

### Integration Testing for Production Agents

🗂️ **File**: `src/session5/testing_framework.py` - Complete testing infrastructure

Systematic testing ensures production agents handle edge cases gracefully and maintain reliability under various input conditions.

```python
# Integration testing and monitoring for production environments
import pytest
from unittest.mock import AsyncMock, patch
from typing import AsyncGenerator, List, Dict, Any
import asyncio
import random
import logging
import time
```

Now we'll define the main testing suite class that coordinates all integration tests:

```python
class IntegrationTestSuite:
    """Comprehensive integration testing for PydanticAI agents."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
```

Next, we implement the core validation testing method that tests agents against various input scenarios:

```python
    async def test_agent_validation(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Test agent validation capabilities with comprehensive scenarios."""
        
        # Define comprehensive test cases covering valid inputs and edge cases
        test_cases = [
            # Valid inputs
            {
                'name': 'valid_research_request',
                'input': 'Research machine learning applications in healthcare',
                'should_pass': True
            },
            # Edge cases
            {
                'name': 'empty_request',
                'input': '',
                'should_pass': False
            }
        ]
```

We continue defining edge cases that test agent boundary conditions:

```python
        # Add more edge cases to test comprehensive validation
        test_cases.extend([
            {
                'name': 'extremely_long_request',
                'input': 'x' * 10000,
                'should_pass': False
            },
            {
                'name': 'special_characters',
                'input': 'Research 中文 émojis 🤖 and symbols @#$%',
                'should_pass': True
            }
        ])
```

Now we execute each test case and collect detailed results for analysis:

```python
        results = []
        
        for test_case in test_cases:
            try:
                result = await agent.process_request(test_case['input'])
                
                test_result = {
                    'test_name': test_case['name'],
                    'expected_pass': test_case['should_pass'],
                    'actual_pass': result.get('success', False),
                    'result': result,
                    'status': 'pass' if (result.get('success', False) == test_case['should_pass']) else 'fail'
                }
                
            except Exception as e:
                test_result = {
                    'test_name': test_case['name'],
                    'expected_pass': test_case['should_pass'],
                    'actual_pass': False,
                    'error': str(e),
                    'status': 'pass' if not test_case['should_pass'] else 'fail'
                }
            
            results.append(test_result)
```

Finally, we return a comprehensive summary of the validation test results:

```python
        return {
            'test_type': 'validation',
            'agent_name': agent.name,
            'total_tests': len(test_cases),
            'passed_tests': len([r for r in results if r['status'] == 'pass']),
            'results': results
        }
```

### Error Scenario Testing

Comprehensive error scenario testing validates that agents handle various failure conditions gracefully.

```python
    async def test_error_handling(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Test agent error handling capabilities."""
        
        # Define various error scenarios to test agent resilience
        error_scenarios = [
            {
                'name': 'network_timeout',
                'setup': lambda: self._simulate_timeout_error(),
                'expected_category': ErrorCategory.TIMEOUT
            },
            {
                'name': 'validation_error',
                'setup': lambda: self._simulate_validation_error(),
                'expected_category': ErrorCategory.VALIDATION
            },
            {
                'name': 'rate_limit_error',
                'setup': lambda: self._simulate_rate_limit_error(),
                'expected_category': ErrorCategory.RATE_LIMIT
            }
        ]
```

Now we execute each error scenario and verify proper error handling:

```python
        results = []
        
        for scenario in error_scenarios:
            try:
                with patch.object(agent, '_process_core_request', side_effect=scenario['setup']()):
                    result = await agent.process_request("test request")
                    
                    test_result = {
                        'scenario_name': scenario['name'],
                        'error_handled': not result.get('success', True),
                        'result': result,
                        'status': 'pass' if not result.get('success', True) else 'fail'
                    }
                    
            except Exception as e:
                test_result = {
                    'scenario_name': scenario['name'],
                    'error_handled': True,
                    'exception': str(e),
                    'status': 'pass'
                }
            
            results.append(test_result)
```

Finally, we return comprehensive error handling test results:

```python
        return {
            'test_type': 'error_handling',
            'agent_name': agent.name,
            'total_scenarios': len(error_scenarios),
            'passed_scenarios': len([r for r in results if r['status'] == 'pass']),
            'results': results
        }
```

These helper methods simulate different types of errors for comprehensive testing:

```python
    def _simulate_timeout_error(self) -> Exception:
        """Simulate a timeout error for testing."""
        return TimeoutAgentError("Simulated timeout error", timeout_seconds=30.0)
    
    def _simulate_validation_error(self) -> Exception:
        """Simulate a validation error for testing."""
        return ValidationAgentError("Simulated validation error", field="test_field", value="invalid_value")
    
    def _simulate_rate_limit_error(self) -> Exception:
        """Simulate a rate limit error for testing."""
        return NetworkAgentError("Rate limit exceeded", endpoint="/api/test", status_code=429)
```

### Load Testing Framework

Load testing validates agent performance under concurrent usage scenarios typical of production environments.

```python
    async def test_concurrent_load(
        self, 
        agent: ProductionAgentBase, 
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """Test agent performance under concurrent load."""
        
        async def single_request(request_id: int) -> Dict[str, Any]:
            """Execute a single test request with timing and error handling."""
            start_time = time.time()
            try:
                result = await agent.process_request(f"Test request {request_id}")
                return {
                    'request_id': request_id,
                    'success': True,
                    'response_time': time.time() - start_time,
                    'result': result
                }
```

We handle exceptions and track failed requests for comprehensive analysis:

```python
            except Exception as e:
                return {
                    'request_id': request_id,
                    'success': False,
                    'response_time': time.time() - start_time,
                    'error': str(e)
                }
```

Next, we set up concurrent execution using semaphores to control load:

```python
        # Execute concurrent batches with controlled concurrency
        results = []
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def execute_with_semaphore(request_id: int):
            async with semaphore:
                return await single_request(request_id)
        
        # Run all requests concurrently
        tasks = [execute_with_semaphore(i) for i in range(total_requests)]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
```

Finally, we analyze the load test results and calculate performance metrics:

```python
        # Analyze results for comprehensive performance metrics
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        response_times = [r['response_time'] for r in successful_requests]
        
        return {
            'test_type': 'load_testing',
            'total_requests': total_requests,
            'concurrent_requests': concurrent_requests,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': len(successful_requests) / total_requests if total_requests > 0 else 0,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0
        }
```

---

## Part 2: Performance Monitoring & Benchmarking

### Enterprise Metrics Collection

🗂️ **File**: `src/session5/monitoring.py` - Complete monitoring infrastructure

Comprehensive metrics collection enables detailed performance analysis and operational monitoring.

```python
# Enterprise monitoring and observability for PydanticAI
from pydantic_ai.monitoring import AgentMonitor, MetricsCollector
from pydantic_ai.observability import TraceCollector, SpanContext
import json
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import structlog
```

Now we define the core metrics data structure that tracks comprehensive agent performance:

```python
@dataclass
class AgentMetrics:
    """Comprehensive agent performance metrics."""
    agent_id: str
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    
    # Response time percentiles
    response_times: List[float] = field(default_factory=list)
    
    # Error breakdown
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Success rate over time
    success_rate_history: List[Dict[str, Any]] = field(default_factory=list)
```

Next, we implement intelligent response time tracking with memory management:

```python
    def update_response_time(self, response_time: float) -> None:
        """Update response time metrics with memory management."""
        self.response_times.append(response_time)
        
        # Keep only last 1000 response times for memory management
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
        
        # Update aggregate metrics
        self.avg_response_time = sum(self.response_times) / len(self.response_times)
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
```

Finally, we add percentile calculation for detailed performance analysis:

```python
    def get_percentiles(self) -> Dict[str, float]:
        """Get response time percentiles for performance analysis."""
        if not self.response_times:
            return {}
        
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        return {
            'p50': sorted_times[int(n * 0.5)],
            'p90': sorted_times[int(n * 0.9)],
            'p95': sorted_times[int(n * 0.95)],
            'p99': sorted_times[int(n * 0.99)]
        }
```

### Enterprise Metrics Collector

The metrics collector provides comprehensive tracking and reporting capabilities for production monitoring.

```python
class EnterpriseMetricsCollector:
    """Enterprise-grade metrics collection and reporting."""
    
    def __init__(self, export_interval: int = 60, retention_hours: int = 24):
        self.export_interval = export_interval
        self.retention_hours = retention_hours
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.global_metrics = AgentMetrics("global")
        self.custom_metrics: Dict[str, List[Dict[str, Any]]] = {}
        
        # External integrations
        self.prometheus_enabled = False
        self.datadog_enabled = False
        self.custom_exporters: List[Callable] = []
        
        # Structured logging
        self.logger = structlog.get_logger("pydantic_ai.metrics")
```

Now we implement the core method for recording agent request metrics:

```python
    def record_request(
        self, 
        agent_id: str, 
        success: bool, 
        response_time: float,
        error_type: Optional[str] = None,
        tokens_used: int = 0,
        estimated_cost: float = 0.0,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record agent request metrics with comprehensive tracking."""
        
        # Ensure agent is registered
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(agent_id)
        
        agent_metrics = self.agent_metrics[agent_id]
```

Next, we record success or error metrics and update global statistics:

```python
        if success:
            agent_metrics.record_success(response_time, tokens_used, estimated_cost)
            self.global_metrics.record_success(response_time, tokens_used, estimated_cost)
        else:
            error_type = error_type or "unknown_error"
            agent_metrics.record_error(error_type, response_time)
            self.global_metrics.record_error(error_type, response_time)
```

Finally, we handle custom metrics and structured logging:

```python
        # Record custom metrics
        if custom_metrics:
            for metric_name, metric_value in custom_metrics.items():
                if metric_name not in self.custom_metrics:
                    self.custom_metrics[metric_name] = []
                
                self.custom_metrics[metric_name].append({
                    'timestamp': time.time(),
                    'agent_id': agent_id,
                    'value': metric_value
                })
        
        # Structured logging
        self.logger.info(
            "Agent request recorded",
            agent_id=agent_id,
            success=success,
            response_time=response_time,
            error_type=error_type,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost
        )
```

### Prometheus Integration

Integration with Prometheus provides industry-standard metrics collection and alerting capabilities.

```python
    def export_to_prometheus(self) -> str:
        """Export metrics in Prometheus format for monitoring systems."""
        if not self.prometheus_enabled:
            return ""
        
        metrics_output = []
        
        # Global metrics with standard Prometheus format
        global_summary = self.get_global_summary()
        metrics_output.extend([
            f"# HELP pydantic_ai_requests_total Total number of requests",
            f"# TYPE pydantic_ai_requests_total counter",
            f"pydantic_ai_requests_total {global_summary['total_requests']}",
            f"",
            f"# HELP pydantic_ai_success_rate Current success rate",
            f"# TYPE pydantic_ai_success_rate gauge", 
            f"pydantic_ai_success_rate {global_summary['global_success_rate']}",
            f"",
            f"# HELP pydantic_ai_response_time_seconds Response time in seconds",
            f"# TYPE pydantic_ai_response_time_seconds histogram"
        ])
```

Now we add per-agent metrics to the Prometheus export:

```python
        # Per-agent metrics with proper labeling
        for agent_id in self.agent_metrics.keys():
            summary = self.get_agent_summary(agent_id)
            if summary:
                metrics_output.extend([
                    f"pydantic_ai_agent_requests_total{{agent=\"{agent_id}\"}} {summary['total_requests']}",
                    f"pydantic_ai_agent_success_rate{{agent=\"{agent_id}\"}} {summary['success_rate']}",
                    f"pydantic_ai_agent_response_time{{agent=\"{agent_id}\"}} {summary['avg_response_time']}"
                ])
        
        return "\n".join(metrics_output)
```

---

## Part 3: Intelligent Caching & Optimization

### High-Performance Caching System

🗂️ **File**: `src/session5/caching.py` - Intelligent caching implementations

Performance optimization focuses on intelligent caching, request batching, and resource management while maintaining type safety.

```python
# Performance optimization patterns for PydanticAI applications
import asyncio
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from functools import wraps, lru_cache
import hashlib
import json
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import OrderedDict
from dataclasses import dataclass

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
```

Now we define the cache entry data structure with intelligent metadata tracking:

```python
@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata for intelligent eviction."""
    value: V
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[float]
    size_bytes: int
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if not self.ttl_seconds:
            return False
        
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > self.ttl_seconds
    
    def update_access(self) -> None:
        """Update access statistics for LRU management."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1
```

### Intelligent Cache Implementation

The intelligent cache provides high-performance caching with automatic eviction, memory management, and comprehensive statistics.

```python
class IntelligentCache(Generic[K, V]):
    """High-performance cache with intelligent eviction strategies."""
    
    def __init__(
        self, 
        max_size: int = 1000,
        default_ttl_seconds: float = 3600,
        max_memory_mb: float = 100
    ):
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._total_size_bytes = 0
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_cleanups': 0
        }
```

Now we implement the intelligent cache retrieval method with access tracking:

```python
    def get(self, key: K) -> Optional[V]:
        """Get value from cache with intelligent access tracking."""
        with self._lock:
            # Periodic cleanup
            if len(self._cache) > 100 and len(self._cache) % 50 == 0:
                self._cleanup_expired()
            
            entry = self._cache.get(key)
            if not entry:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired():
                self._cache.pop(key)
                self._total_size_bytes -= entry.size_bytes
                self._stats['misses'] += 1
                self._stats['expired_cleanups'] += 1
                return None
            
            # Update access statistics and move to end (most recently used)
            entry.update_access()
            self._cache.move_to_end(key)
            self._stats['hits'] += 1
            
            return entry.value
```

Next, we implement the cache storage method with intelligent eviction:

```python
    def set(self, key: K, value: V, ttl_seconds: float = None) -> None:
        """Set value in cache with intelligent eviction."""
        with self._lock:
            ttl = ttl_seconds or self.default_ttl_seconds
            size_bytes = self._calculate_size(value)
            
            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache.pop(key)
                self._total_size_bytes -= old_entry.size_bytes
```

Next, we create the new cache entry with proper metadata:

```python
            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                access_count=1,
                ttl_seconds=ttl,
                size_bytes=size_bytes
            )
            
            # Evict if necessary before adding
            self._evict_lru()
            
            # Add new entry
            self._cache[key] = entry
            self._total_size_bytes += size_bytes
```

Finally, we add helper methods for size calculation, LRU eviction, and statistics:

```python
    def _calculate_size(self, obj: Any) -> int:
        """Estimate object size in bytes for memory management."""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            # Fallback estimation
            return len(str(obj)) * 2  # Rough estimate for Unicode
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries when limits are exceeded."""
        while len(self._cache) >= self.max_size or self._total_size_bytes >= self.max_memory_bytes:
            if not self._cache:
                break
            
            key, entry = self._cache.popitem(last=False)  # Remove oldest (LRU)
            self._total_size_bytes -= entry.size_bytes
            self._stats['evictions'] += 1
```

Finally, we provide comprehensive cache performance statistics:

```python
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache performance statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_mb': self._total_size_bytes / (1024 * 1024),
                'hit_rate_percent': hit_rate,
                'total_requests': total_requests,
                'stats': dict(self._stats)
            }
```

### Cache Decorator for Agent Methods

A convenient decorator enables automatic caching of agent method results with configurable TTL and cache key generation.

```python
def cached_agent_method(
    cache: IntelligentCache,
    ttl_seconds: float = 3600,
    key_generator: Optional[Callable] = None
):
    """Decorator for caching agent method results."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key using custom generator or default hashing
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
```

Now we handle cache lookup and function execution:

```python
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator
```

---

## Module Summary

You've now mastered testing and benchmarking for PydanticAI, including:

✅ **Comprehensive Testing**: Built integration tests, error scenario testing, and load testing frameworks  
✅ **Performance Monitoring**: Implemented enterprise metrics collection with Prometheus integration  
✅ **Intelligent Caching**: Created high-performance caching with LRU eviction and memory management  
✅ **Production Monitoring**: Built observability with distributed tracing and structured logging

---

## 📝 Multiple Choice Test - Module D

Test your understanding of testing and benchmarking systems:

**Question 1:** What does the comprehensive integration test framework validate?
A) Only basic functionality  
B) Valid inputs, error scenarios, edge cases, and performance under load  
C) Simple unit tests only  
D) Manual testing procedures  

**Question 2:** How does the MetricsCollector track agent performance data?
A) Simple counters only  
B) Comprehensive metrics with request counts, response times, error rates, and success rates  
C) Binary success/failure tracking  
D) Manual logging only  

**Question 3:** What eviction strategy does the IntelligentCache use when memory limits are reached?
A) Random removal  
B) LRU (Least Recently Used) with memory usage tracking  
C) First-in-first-out only  
D) Manual cache clearing  

**Question 4:** What information does the performance decorator capture for monitoring?
A) Just execution time  
B) Request metrics, performance data, error tracking, and distributed tracing  
C) Function names only  
D) Memory usage only  

**Question 5:** How does the load testing framework simulate realistic usage patterns?
A) Single threaded execution  
B) Concurrent user simulation with configurable load patterns and performance analysis  
C) Random API calls  
D) Simple sequential testing  

[**🗂️ View Test Solutions →**](Session5_ModuleD_Test_Solutions.md)

### Next Steps
- **Return to Core**: [Session 5 Main](Session5_PydanticAI_Type_Safe_Agents.md)
- **Advance to Session 6**: [Atomic Agents](Session6_Atomic_Agents_Modular_Architecture.md)
- **Review Previous Modules**: [Module A](Session5_ModuleA_Advanced_Type_Systems.md), [Module B](Session5_ModuleB_Enterprise_PydanticAI.md), [Module C](Session5_ModuleC_Custom_Validation_Systems.md)

### Complete Session 5 Learning Path
🎯 **Core Section** → 🔬 **Module A** → 🏭 **Module B** → 🔧 **Module C** → 🧪 **Module D**

You've completed the comprehensive PydanticAI learning journey!

---

**🗂️ Source Files for Module D:**
- `src/session5/testing_framework.py` - Complete testing infrastructure
- `src/session5/monitoring.py` - Enterprise monitoring systems
- `src/session5/caching.py` - Intelligent caching implementations
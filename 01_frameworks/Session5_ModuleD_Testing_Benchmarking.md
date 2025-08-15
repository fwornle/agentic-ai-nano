# Session 5 - Module D: Testing & Benchmarking (40 minutes)

**Prerequisites**: [Session 5 Core Section Complete](Session5_PydanticAI_Type_Safe_Agents.md)  
**Target Audience**: Quality assurance engineers and performance analysts  
**Cognitive Load**: 4 testing concepts

---

## 🎯 Module Overview

This module covers comprehensive testing strategies, performance benchmarking, and enterprise monitoring for PydanticAI applications. You'll learn to implement systematic testing, performance optimization, and production monitoring systems.

### Learning Objectives
By the end of this module, you will:
- Build comprehensive testing frameworks for PydanticAI agents
- Implement performance monitoring and benchmarking systems
- Create enterprise-grade observability with distributed tracing
- Design intelligent caching and optimization patterns
- Monitor production systems with metrics and alerting

---

## Part 1: Comprehensive Testing Framework (15 minutes)

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

class IntegrationTestSuite:
    """Comprehensive integration testing for PydanticAI agents."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def test_agent_validation(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Test agent validation capabilities with comprehensive scenarios."""
        
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
            },
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
        ]
        
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
        
        return {
            'test_type': 'error_handling',
            'agent_name': agent.name,
            'total_scenarios': len(error_scenarios),
            'passed_scenarios': len([r for r in results if r['status'] == 'pass']),
            'results': results
        }
    
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
            """Execute a single test request."""
            start_time = time.time()
            try:
                result = await agent.process_request(f"Test request {request_id}")
                return {
                    'request_id': request_id,
                    'success': True,
                    'response_time': time.time() - start_time,
                    'result': result
                }
            except Exception as e:
                return {
                    'request_id': request_id,
                    'success': False,
                    'response_time': time.time() - start_time,
                    'error': str(e)
                }
        
        # Execute concurrent batches
        results = []
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def execute_with_semaphore(request_id: int):
            async with semaphore:
                return await single_request(request_id)
        
        # Run all requests
        tasks = [execute_with_semaphore(i) for i in range(total_requests)]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        
        # Analyze results
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

## Part 2: Performance Monitoring & Benchmarking (15 minutes)

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
        
        if success:
            agent_metrics.record_success(response_time, tokens_used, estimated_cost)
            self.global_metrics.record_success(response_time, tokens_used, estimated_cost)
        else:
            error_type = error_type or "unknown_error"
            agent_metrics.record_error(error_type, response_time)
            self.global_metrics.record_error(error_type, response_time)
        
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
        
        # Global metrics
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
        
        # Per-agent metrics
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

## Part 3: Intelligent Caching & Optimization (10 minutes)

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
    
    def set(self, key: K, value: V, ttl_seconds: float = None) -> None:
        """Set value in cache with intelligent eviction."""
        with self._lock:
            ttl = ttl_seconds or self.default_ttl_seconds
            size_bytes = self._calculate_size(value)
            
            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache.pop(key)
                self._total_size_bytes -= old_entry.size_bytes
            
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
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
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

## 🎯 Module Summary

You've now mastered testing and benchmarking for PydanticAI, including:

✅ **Comprehensive Testing**: Built integration tests, error scenario testing, and load testing frameworks  
✅ **Performance Monitoring**: Implemented enterprise metrics collection with Prometheus integration  
✅ **Intelligent Caching**: Created high-performance caching with LRU eviction and memory management  
✅ **Production Monitoring**: Built observability with distributed tracing and structured logging

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
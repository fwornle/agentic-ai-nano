# Session 8 - Module C: Performance Optimization (50 minutes)

**Prerequisites**: [Session 8 Core Section Complete](Session8_Agno_Production_Ready_Agents.md)  
**Target Audience**: Performance engineers and cost optimization specialists  
**Cognitive Load**: 4 optimization concepts

---

## 🎯 Module Overview

This module explores advanced performance optimization techniques for Agno agent systems including intelligent caching strategies, cost management systems, memory optimization, latency reduction techniques, and automated performance tuning. You'll learn to build highly efficient agent systems that minimize costs while maximizing performance.

### Learning Objectives
By the end of this module, you will:
- Implement multi-layer caching systems with intelligent invalidation strategies
- Design cost optimization frameworks with automated budget management
- Create memory-efficient agent architectures with resource pooling
- Build latency optimization systems with request batching and connection pooling

---

## Part 1: Intelligent Caching Systems (20 minutes)

### Multi-Layer Caching Architecture

🗂️ **File**: `src/session8/intelligent_caching.py` - Advanced caching for agent systems

```python
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import hashlib
import json
import logging
from enum import Enum
import redis
import sqlite3

class CacheLevel(Enum):
    """Cache hierarchy levels"""
    L1_MEMORY = "l1_memory"          # In-process memory cache
    L2_REDIS = "l2_redis"            # Redis distributed cache  
    L3_PERSISTENT = "l3_persistent"  # Persistent storage cache
    L4_CDN = "l4_cdn"               # CDN edge cache

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    cache_level: CacheLevel = CacheLevel.L1_MEMORY
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntelligentCacheManager:
    """Multi-layer intelligent caching system for agent responses"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            "hits": {"l1": 0, "l2": 0, "l3": 0, "l4": 0},
            "misses": {"l1": 0, "l2": 0, "l3": 0, "l4": 0},
            "evictions": {"l1": 0, "l2": 0, "l3": 0, "l4": 0}
        }
        self.cache_policies = {}
        self.logger = logging.getLogger(__name__)
        
        # Cache configuration
        self.l1_max_size = 1000  # Max entries in L1
        self.l1_max_memory_mb = 100  # Max memory usage for L1
        self.default_ttl = 3600  # 1 hour default TTL
        
    def setup_cache_policies(self) -> Dict[str, Any]:
        """Configure intelligent caching policies"""
        
        cache_config = {
            "response_caching": {
                "enabled": True,
                "ttl_seconds": 3600,
                "cache_levels": [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS],
                "invalidation_strategy": "semantic_similarity",
                "compression": True
            },
            
            "model_output_caching": {
                "enabled": True, 
                "ttl_seconds": 7200,
                "cache_levels": [CacheLevel.L2_REDIS, CacheLevel.L3_PERSISTENT],
                "deduplication": True,
                "similarity_threshold": 0.95
            },
            
            "conversation_context_caching": {
                "enabled": True,
                "ttl_seconds": 1800, 
                "cache_levels": [CacheLevel.L1_MEMORY],
                "max_context_length": 10,
                "context_compression": True
            },
            
            "tool_result_caching": {
                "enabled": True,
                "ttl_seconds": 600,  # 10 minutes for tool results
                "cache_levels": [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS],
                "cache_by_parameters": True,
                "parameter_normalization": True
            }
        }
        
        self.cache_policies = cache_config
        return cache_config
    
    async def get_cached_response(self, cache_key: str, 
                                 cache_levels: List[CacheLevel] = None) -> Optional[Any]:
        """Get cached response with intelligent cache hierarchy traversal"""
        
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS, CacheLevel.L3_PERSISTENT]
        
        for cache_level in cache_levels:
            try:
                if cache_level == CacheLevel.L1_MEMORY:
                    result = await self._get_l1_cache(cache_key)
                elif cache_level == CacheLevel.L2_REDIS:
                    result = await self._get_l2_cache(cache_key)
                elif cache_level == CacheLevel.L3_PERSISTENT:
                    result = await self._get_l3_cache(cache_key)
                else:
                    continue  # Skip unsupported cache levels
                
                if result is not None:
                    # Cache hit - promote to higher cache levels
                    await self._promote_cache_entry(cache_key, result, cache_level)
                    
                    # Update statistics
                    level_name = cache_level.value.split('_')[0]
                    self.cache_stats["hits"][level_name] += 1
                    
                    return result
                    
            except Exception as e:
                self.logger.warning(f"Cache level {cache_level} failed: {e}")
                continue
        
        # Cache miss
        for level in cache_levels:
            level_name = level.value.split('_')[0]
            self.cache_stats["misses"][level_name] += 1
        
        return None
    
    async def set_cached_response(self, cache_key: str, value: Any,
                                 ttl_seconds: int = None,
                                 cache_levels: List[CacheLevel] = None):
        """Set cached response across multiple cache levels"""
        
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        cache_entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            ttl_seconds=ttl_seconds
        )
        
        for cache_level in cache_levels:
            try:
                if cache_level == CacheLevel.L1_MEMORY:
                    await self._set_l1_cache(cache_key, cache_entry)
                elif cache_level == CacheLevel.L2_REDIS:
                    await self._set_l2_cache(cache_key, cache_entry)
                elif cache_level == CacheLevel.L3_PERSISTENT:
                    await self._set_l3_cache(cache_key, cache_entry)
                    
            except Exception as e:
                self.logger.error(f"Failed to set cache in {cache_level}: {e}")
    
    async def _get_l1_cache(self, cache_key: str) -> Optional[Any]:
        """Get from L1 memory cache"""
        
        if cache_key in self.l1_cache:
            entry = self.l1_cache[cache_key]
            
            # Check TTL
            if entry.ttl_seconds:
                elapsed = (datetime.now() - entry.created_at).total_seconds()
                if elapsed > entry.ttl_seconds:
                    del self.l1_cache[cache_key]
                    return None
            
            # Update access statistics
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            return entry.value
        
        return None
    
    async def _set_l1_cache(self, cache_key: str, entry: CacheEntry):
        """Set L1 memory cache with intelligent eviction"""
        
        # Check if we need to evict entries
        if len(self.l1_cache) >= self.l1_max_size:
            await self._evict_l1_entries()
        
        self.l1_cache[cache_key] = entry
    
    async def _evict_l1_entries(self):
        """Intelligent L1 cache eviction using LRU + frequency"""
        
        if not self.l1_cache:
            return
        
        # Calculate eviction scores (combination of recency and frequency)
        entries_with_scores = []
        now = datetime.now()
        
        for key, entry in self.l1_cache.items():
            recency_score = (now - entry.last_accessed).total_seconds()
            frequency_score = 1.0 / (entry.access_count + 1)
            combined_score = recency_score * frequency_score
            
            entries_with_scores.append((key, combined_score))
        
        # Sort by score (highest first) and remove top 20%
        entries_with_scores.sort(key=lambda x: x[1], reverse=True)
        entries_to_evict = entries_with_scores[:len(entries_with_scores) // 5]
        
        for key, _ in entries_to_evict:
            del self.l1_cache[key]
            self.cache_stats["evictions"]["l1"] += 1
    
    async def _get_l2_cache(self, cache_key: str) -> Optional[Any]:
        """Get from L2 Redis cache"""
        
        try:
            cached_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, cache_key
            )
            
            if cached_data:
                return json.loads(cached_data.decode('utf-8'))
                
        except Exception as e:
            self.logger.warning(f"Redis cache error: {e}")
        
        return None
    
    async def _set_l2_cache(self, cache_key: str, entry: CacheEntry):
        """Set L2 Redis cache"""
        
        try:
            cache_data = json.dumps(entry.value)
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.redis_client.setex(
                    cache_key, 
                    entry.ttl_seconds or self.default_ttl,
                    cache_data
                )
            )
        except Exception as e:
            self.logger.error(f"Redis cache set error: {e}")
    
    def create_semantic_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Create cache key based on semantic similarity rather than exact match"""
        
        # Normalize query for better cache hits
        normalized_query = query.lower().strip()
        
        # Include relevant context in cache key
        context_hash = hashlib.md5(
            json.dumps(context, sort_keys=True).encode()
        ).hexdigest()[:8]
        
        # Create semantic hash (in production, use embeddings)
        query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()[:16]
        
        return f"semantic:{query_hash}:{context_hash}"
    
    def get_cache_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance metrics"""
        
        total_requests = sum(
            self.cache_stats["hits"][level] + self.cache_stats["misses"][level]
            for level in ["l1", "l2", "l3", "l4"]
        )
        
        if total_requests == 0:
            return {"error": "No cache requests recorded"}
        
        metrics = {
            "overall_hit_rate": sum(self.cache_stats["hits"].values()) / total_requests,
            "hit_rates_by_level": {
                level: hits / (hits + self.cache_stats["misses"][level]) 
                if (hits + self.cache_stats["misses"][level]) > 0 else 0
                for level, hits in self.cache_stats["hits"].items()
            },
            "cache_size": {
                "l1_entries": len(self.l1_cache),
                "l1_memory_usage_mb": self._calculate_l1_memory_usage()
            },
            "eviction_rates": self.cache_stats["evictions"],
            "cost_savings": self._calculate_cache_savings()
        }
        
        return metrics
    
    def _calculate_l1_memory_usage(self) -> float:
        """Calculate approximate L1 cache memory usage"""
        
        total_size = 0
        for entry in self.l1_cache.values():
            # Rough estimation of memory usage
            total_size += len(str(entry.value))
        
        return total_size / (1024 * 1024)  # Convert to MB

class ResponseDeduplication:
    """Intelligent response deduplication system"""
    
    def __init__(self):
        self.response_signatures = {}
        self.similarity_threshold = 0.90
        self.dedup_stats = {"duplicates_found": 0, "storage_saved": 0}
        
    def calculate_response_similarity(self, response1: str, response2: str) -> float:
        """Calculate semantic similarity between responses"""
        
        # Simplified similarity calculation (in production, use proper NLP models)
        words1 = set(response1.lower().split())
        words2 = set(response2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def check_duplicate_response(self, response: str, 
                                     context: Dict[str, Any]) -> Optional[str]:
        """Check if response is a duplicate and return canonical version"""
        
        response_hash = self._create_response_hash(response, context)
        
        # Check for similar responses
        for existing_hash, stored_response in self.response_signatures.items():
            similarity = self.calculate_response_similarity(response, stored_response["text"])
            
            if similarity >= self.similarity_threshold:
                self.dedup_stats["duplicates_found"] += 1
                self.dedup_stats["storage_saved"] += len(response)
                return existing_hash
        
        # Store new unique response
        self.response_signatures[response_hash] = {
            "text": response,
            "context": context,
            "created_at": datetime.now(),
            "usage_count": 1
        }
        
        return response_hash
    
    def _create_response_hash(self, response: str, context: Dict[str, Any]) -> str:
        """Create hash for response deduplication"""
        
        combined = f"{response}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
```

---

## Part 2: Cost Management and Optimization (20 minutes)

### Automated Cost Management Framework

🗂️ **File**: `src/session8/cost_management.py` - Comprehensive cost optimization

```python
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
import logging
from enum import Enum

class CostOptimizationStrategy(Enum):
    """Cost optimization strategies"""
    MODEL_RIGHT_SIZING = "model_right_sizing"
    REQUEST_BATCHING = "request_batching" 
    CACHING_ENHANCEMENT = "caching_enhancement"
    RESOURCE_SCHEDULING = "resource_scheduling"
    SPOT_INSTANCE_USAGE = "spot_instance_usage"

@dataclass
class CostBudget:
    """Cost budget configuration"""
    name: str
    daily_limit: float
    weekly_limit: float
    monthly_limit: float
    alert_thresholds: List[float] = field(default_factory=lambda: [0.5, 0.8, 0.9, 1.0])
    auto_scale_down_threshold: float = 0.95
    emergency_shutdown_threshold: float = 1.0

class AutomatedCostOptimizer:
    """Automated cost optimization system for agent operations"""
    
    def __init__(self, budget_config: CostBudget):
        self.budget_config = budget_config
        self.cost_history = []
        self.optimization_rules = {}
        self.active_optimizations = []
        self.logger = logging.getLogger(__name__)
        
    def setup_cost_optimization_rules(self) -> Dict[str, Any]:
        """Configure automated cost optimization rules"""
        
        optimization_config = {
            "model_selection": {
                "enabled": True,
                "rules": [
                    {
                        "condition": "input_tokens < 500 and complexity_score < 0.3",
                        "action": "use_cheaper_model",
                        "target_model": "gpt-3.5-turbo",
                        "potential_savings": 0.90  # 90% cost reduction
                    },
                    {
                        "condition": "response_time_requirement > 2s and accuracy_tolerance > 0.95",
                        "action": "use_efficient_model", 
                        "target_model": "gpt-4-turbo",
                        "potential_savings": 0.50
                    }
                ]
            },
            
            "request_batching": {
                "enabled": True,
                "batch_size": 5,
                "batch_timeout_ms": 100,
                "cost_reduction": 0.25
            },
            
            "caching_optimization": {
                "enabled": True,
                "target_hit_rate": 0.70,
                "cache_duration_optimization": True,
                "semantic_caching": True
            },
            
            "resource_scheduling": {
                "enabled": True,
                "off_peak_hours": [22, 23, 0, 1, 2, 3, 4, 5],
                "off_peak_discount": 0.30,
                "workload_shifting": True
            },
            
            "budget_protection": {
                "enabled": True,
                "soft_limits": [0.8, 0.9],  # 80%, 90% of budget
                "hard_limit": 1.0,  # 100% of budget
                "actions": {
                    "0.8": ["enable_aggressive_caching", "switch_to_cheaper_models"],
                    "0.9": ["batch_requests", "defer_non_critical_tasks"],
                    "1.0": ["emergency_scale_down", "disable_non_essential_agents"]
                }
            }
        }
        
        self.optimization_rules = optimization_config
        return optimization_config
    
    async def optimize_model_selection(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically select optimal model based on cost and performance requirements"""
        
        # Analyze request characteristics
        input_tokens = request_data.get("input_tokens", 0)
        required_accuracy = request_data.get("accuracy_requirement", 0.95)
        max_response_time = request_data.get("max_response_time_ms", 5000)
        budget_remaining = self._get_budget_remaining_percentage()
        
        # Model cost and performance profiles
        model_profiles = {
            "gpt-4": {
                "cost_per_token": 0.00003,
                "accuracy": 0.98,
                "avg_response_time_ms": 2000,
                "quality_score": 0.95
            },
            "gpt-4-turbo": {
                "cost_per_token": 0.00001,
                "accuracy": 0.96,
                "avg_response_time_ms": 1500,
                "quality_score": 0.90
            },
            "gpt-3.5-turbo": {
                "cost_per_token": 0.0000015,
                "accuracy": 0.92,
                "avg_response_time_ms": 1000,
                "quality_score": 0.85
            }
        }
        
        # Calculate optimization score for each model
        best_model = None
        best_score = float('-inf')
        
        for model_name, profile in model_profiles.items():
            # Check if model meets requirements
            if (profile["accuracy"] >= required_accuracy and 
                profile["avg_response_time_ms"] <= max_response_time):
                
                # Calculate optimization score (lower cost = higher score)
                cost_score = 1.0 / (profile["cost_per_token"] * input_tokens + 0.001)
                quality_score = profile["quality_score"]
                speed_score = 1.0 / (profile["avg_response_time_ms"] / 1000.0)
                
                # Adjust weights based on budget remaining
                if budget_remaining < 0.2:  # Less than 20% budget remaining
                    weights = {"cost": 0.7, "quality": 0.2, "speed": 0.1}
                elif budget_remaining < 0.5:  # Less than 50% budget remaining
                    weights = {"cost": 0.5, "quality": 0.3, "speed": 0.2}
                else:  # Sufficient budget
                    weights = {"cost": 0.3, "quality": 0.5, "speed": 0.2}
                
                combined_score = (
                    weights["cost"] * cost_score +
                    weights["quality"] * quality_score +
                    weights["speed"] * speed_score
                )
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_model = model_name
        
        if best_model:
            original_cost = model_profiles["gpt-4"]["cost_per_token"] * input_tokens
            optimized_cost = model_profiles[best_model]["cost_per_token"] * input_tokens
            cost_savings = original_cost - optimized_cost
            
            return {
                "recommended_model": best_model,
                "optimization_score": best_score,
                "estimated_cost": optimized_cost,
                "cost_savings": cost_savings,
                "savings_percentage": cost_savings / original_cost if original_cost > 0 else 0,
                "reasoning": f"Selected {best_model} based on budget={budget_remaining:.2f}, accuracy_req={required_accuracy}"
            }
        
        return {
            "recommended_model": "gpt-4",  # Fallback
            "optimization_score": 0,
            "estimated_cost": model_profiles["gpt-4"]["cost_per_token"] * input_tokens,
            "cost_savings": 0,
            "reasoning": "No suitable model found, using default"
        }
    
    async def implement_request_batching(self, pending_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Implement intelligent request batching for cost optimization"""
        
        if not self.optimization_rules.get("request_batching", {}).get("enabled"):
            return {"batching_enabled": False}
        
        batch_config = self.optimization_rules["request_batching"]
        batch_size = batch_config["batch_size"]
        timeout_ms = batch_config["batch_timeout_ms"]
        
        # Group requests by similarity for better batching efficiency
        batches = self._group_requests_for_batching(pending_requests, batch_size)
        
        batching_results = {
            "batches_created": len(batches),
            "total_requests": len(pending_requests),
            "batching_efficiency": len(pending_requests) / len(batches) if batches else 0,
            "estimated_cost_savings": 0.0
        }
        
        # Calculate cost savings from batching
        if batches:
            individual_cost = len(pending_requests) * 1.0  # Baseline cost per request
            batched_cost = len(batches) * 1.0 * 0.75  # 25% discount for batching
            
            batching_results["estimated_cost_savings"] = individual_cost - batched_cost
            batching_results["savings_percentage"] = (individual_cost - batched_cost) / individual_cost
        
        return batching_results
    
    def _group_requests_for_batching(self, requests: List[Dict[str, Any]], 
                                   batch_size: int) -> List[List[Dict[str, Any]]]:
        """Group similar requests for efficient batching"""
        
        # Simple grouping by agent type and model
        groups = {}
        
        for request in requests:
            agent_type = request.get("agent_type", "default")
            model_name = request.get("model_name", "default")
            group_key = f"{agent_type}:{model_name}"
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(request)
        
        # Create batches from groups
        batches = []
        for group_requests in groups.values():
            for i in range(0, len(group_requests), batch_size):
                batch = group_requests[i:i + batch_size]
                batches.append(batch)
        
        return batches
    
    def _get_budget_remaining_percentage(self) -> float:
        """Calculate remaining budget percentage"""
        
        now = datetime.now()
        
        # Get today's spending
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_spending = sum(
            entry.get("cost", 0) for entry in self.cost_history
            if datetime.fromisoformat(entry["timestamp"]) >= today_start
        )
        
        daily_remaining = max(0, self.budget_config.daily_limit - today_spending)
        return daily_remaining / self.budget_config.daily_limit
    
    async def emergency_cost_controls(self, current_spend: float) -> Dict[str, Any]:
        """Implement emergency cost controls when budget is exceeded"""
        
        daily_percentage = current_spend / self.budget_config.daily_limit
        actions_taken = []
        
        if daily_percentage >= self.budget_config.emergency_shutdown_threshold:
            # Emergency shutdown
            actions_taken.extend([
                "emergency_agent_shutdown",
                "disable_non_critical_services",
                "enable_maximum_caching",
                "switch_to_cheapest_models"
            ])
            
        elif daily_percentage >= self.budget_config.auto_scale_down_threshold:
            # Aggressive cost reduction
            actions_taken.extend([
                "aggressive_scale_down",
                "batch_all_requests",
                "enable_aggressive_caching",
                "defer_low_priority_tasks"
            ])
            
        return {
            "emergency_level": "critical" if daily_percentage >= 1.0 else "warning",
            "budget_utilization": daily_percentage,
            "actions_taken": actions_taken,
            "estimated_cost_reduction": self._calculate_emergency_savings(actions_taken)
        }
    
    def _calculate_emergency_savings(self, actions: List[str]) -> float:
        """Calculate estimated cost savings from emergency actions"""
        
        savings_map = {
            "emergency_agent_shutdown": 0.80,
            "aggressive_scale_down": 0.60,
            "enable_maximum_caching": 0.40,
            "switch_to_cheapest_models": 0.85,
            "batch_all_requests": 0.25,
            "defer_low_priority_tasks": 0.30
        }
        
        return max(savings_map.get(action, 0) for action in actions)

class ResourcePoolManager:
    """Manage resource pools for cost-efficient agent execution"""
    
    def __init__(self):
        self.agent_pools = {}
        self.connection_pools = {}
        self.resource_utilization = {}
        
    def create_agent_pool(self, pool_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create managed agent pool for resource efficiency"""
        
        pool_config = {
            "pool_name": pool_name,
            "min_agents": config.get("min_agents", 2),
            "max_agents": config.get("max_agents", 20),
            "idle_timeout_minutes": config.get("idle_timeout", 30),
            "warmup_agents": config.get("warmup_agents", 3),
            "scaling_policy": {
                "scale_up_threshold": 0.8,   # 80% utilization
                "scale_down_threshold": 0.3,  # 30% utilization
                "scale_up_increment": 2,
                "scale_down_increment": 1,
                "cooldown_period_minutes": 5
            },
            "cost_optimization": {
                "enable_spot_instances": config.get("spot_instances", True),
                "preemptible_percentage": 0.7,
                "cost_per_hour_target": config.get("cost_target", 10.0)
            }
        }
        
        self.agent_pools[pool_name] = pool_config
        return pool_config
    
    async def optimize_resource_allocation(self, workload_forecast: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation based on workload forecasting"""
        
        optimization_plan = {
            "timestamp": datetime.now().isoformat(),
            "forecast_horizon_hours": workload_forecast.get("horizon_hours", 24),
            "optimizations": []
        }
        
        for pool_name, pool_config in self.agent_pools.items():
            current_agents = pool_config.get("current_agents", pool_config["min_agents"])
            forecasted_load = workload_forecast.get(pool_name, {}).get("expected_rps", 100)
            
            # Calculate optimal agent count
            agents_per_rps = 0.1  # Simplified: 1 agent per 10 RPS
            optimal_agents = max(
                pool_config["min_agents"],
                min(pool_config["max_agents"], int(forecasted_load * agents_per_rps))
            )
            
            if optimal_agents != current_agents:
                cost_impact = (optimal_agents - current_agents) * 0.50  # $0.50/hour per agent
                
                optimization_plan["optimizations"].append({
                    "pool_name": pool_name,
                    "current_agents": current_agents,
                    "optimal_agents": optimal_agents,
                    "change": optimal_agents - current_agents,
                    "hourly_cost_impact": cost_impact,
                    "reason": "workload_forecast_optimization"
                })
        
        return optimization_plan
```

---

## Part 3: Memory and Latency Optimization (10 minutes)

### High-Performance Memory Management

🗂️ **File**: `src/session8/performance_optimization.py` - Memory and latency optimization

```python
from typing import Dict, List, Any, Optional
import asyncio
import gc
import psutil
import time
from dataclasses import dataclass

@dataclass
class MemoryOptimizationConfig:
    """Memory optimization configuration"""
    max_memory_mb: int = 2048
    gc_threshold: float = 0.8  # Trigger GC at 80% memory usage
    context_window_size: int = 4096
    enable_streaming: bool = True
    batch_processing: bool = True

class MemoryOptimizedAgentManager:
    """Memory-efficient agent execution manager"""
    
    def __init__(self, config: MemoryOptimizationConfig):
        self.config = config
        self.memory_stats = {"peak_usage": 0, "gc_triggers": 0}
        
    async def optimize_context_management(self, conversation_history: List[Dict]) -> List[Dict]:
        """Optimize conversation context for memory efficiency"""
        
        if len(conversation_history) <= self.config.context_window_size:
            return conversation_history
        
        # Intelligent context pruning
        important_messages = []
        recent_messages = conversation_history[-50:]  # Keep recent messages
        
        # Keep messages with high importance scores
        for msg in conversation_history[:-50]:
            importance_score = self._calculate_message_importance(msg)
            if importance_score > 0.7:
                important_messages.append(msg)
        
        # Combine important and recent messages
        optimized_context = important_messages + recent_messages
        
        # Ensure we don't exceed context window
        if len(optimized_context) > self.config.context_window_size:
            optimized_context = optimized_context[-self.config.context_window_size:]
        
        return optimized_context
    
    def _calculate_message_importance(self, message: Dict[str, Any]) -> float:
        """Calculate importance score for context retention"""
        
        content = message.get("content", "")
        role = message.get("role", "user")
        
        # Simple importance scoring
        importance = 0.5  # Base score
        
        # System messages are important
        if role == "system":
            importance += 0.3
        
        # Messages with keywords get higher importance
        important_keywords = ["important", "remember", "context", "reference"]
        for keyword in important_keywords:
            if keyword.lower() in content.lower():
                importance += 0.2
                break
        
        # Longer messages might be more important
        if len(content) > 200:
            importance += 0.1
        
        return min(importance, 1.0)

class LatencyOptimizer:
    """Advanced latency optimization system"""
    
    def __init__(self):
        self.connection_pools = {}
        self.request_cache = {}
        self.batch_processor = None
        
    async def setup_connection_pooling(self, model_endpoints: Dict[str, str]):
        """Setup connection pooling for model endpoints"""
        
        import aiohttp
        
        for model_name, endpoint in model_endpoints.items():
            # Create connection pool for each model endpoint
            connector = aiohttp.TCPConnector(
                limit=20,  # Max connections
                limit_per_host=10,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            self.connection_pools[model_name] = session
    
    async def implement_request_batching(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Implement request batching for reduced latency overhead"""
        
        # Group requests by model for efficient batching
        model_groups = {}
        for i, request in enumerate(requests):
            model = request.get("model", "default")
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append((i, request))
        
        # Process batches concurrently
        all_results = [None] * len(requests)
        batch_tasks = []
        
        for model, model_requests in model_groups.items():
            task = self._process_model_batch(model, model_requests)
            batch_tasks.append(task)
        
        batch_results = await asyncio.gather(*batch_tasks)
        
        # Reassemble results in original order
        for batch_result in batch_results:
            for original_index, result in batch_result:
                all_results[original_index] = result
        
        return all_results
    
    async def _process_model_batch(self, model: str, 
                                 requests: List[Tuple[int, Dict[str, Any]]]) -> List[Tuple[int, Any]]:
        """Process batch of requests for a specific model"""
        
        if model in self.connection_pools:
            session = self.connection_pools[model]
            
            # Prepare batch payload
            batch_payload = {
                "model": model,
                "requests": [req for _, req in requests]
            }
            
            # Execute batch request
            async with session.post("/v1/batch", json=batch_payload) as response:
                batch_response = await response.json()
                
                # Map results back to original indices
                results = []
                for i, (original_index, _) in enumerate(requests):
                    result = batch_response.get("results", [])[i] if i < len(batch_response.get("results", [])) else None
                    results.append((original_index, result))
                
                return results
        
        # Fallback: process individually
        results = []
        for original_index, request in requests:
            # Simulate individual processing
            result = {"status": "processed", "request_id": request.get("id")}
            results.append((original_index, result))
        
        return results
```

---

## 🎯 Module Summary

You've now mastered performance optimization for production Agno systems:

✅ **Intelligent Caching**: Implemented multi-layer caching with semantic similarity and deduplication  
✅ **Cost Optimization**: Built automated cost management with model selection and budget protection  
✅ **Resource Pooling**: Created efficient agent pools with spot instance integration  
✅ **Memory Management**: Designed memory-efficient context handling with intelligent pruning  
✅ **Latency Optimization**: Implemented connection pooling and request batching for reduced overhead

### Next Steps
- **Continue to Module D**: [Security & Compliance](Session8_ModuleD_Security_Compliance.md) for enterprise security
- **Return to Core**: [Session 8 Main](Session8_Agno_Production_Ready_Agents.md)
- **Review Module A**: [Advanced Monitoring & Observability](Session8_ModuleA_Advanced_Monitoring_Observability.md)

---

**🗂️ Source Files for Module C:**
- `src/session8/intelligent_caching.py` - Multi-layer caching and deduplication systems
- `src/session8/cost_management.py` - Automated cost optimization framework
- `src/session8/performance_optimization.py` - Memory and latency optimization techniques
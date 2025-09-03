# ⚙️ Session 5 Advanced: Production Rate Limiting Systems

> **⚙️ IMPLEMENTER PATH CONTENT**
> Prerequisites: Complete 🎯 Observer and 📝 Participant paths
> Time Investment: 2-3 hours
> Outcome: Master enterprise-grade distributed rate limiting

## Advanced Learning Outcomes

After completing this module, you will master:

- Distributed rate limiting with Redis clustering  
- Advanced token bucket algorithms with multiple buckets  
- Dynamic rate limiting based on user behavior  
- Rate limiting analytics and capacity planning  

## Enterprise Distributed Rate Limiting

Imagine your MCP server as a major highway system during rush hour. Without sophisticated traffic management, you'd have chaos. Production rate limiting is your intelligent traffic control system that adapts to conditions in real-time.

### Advanced Token Bucket Implementation

The production token bucket system uses multiple buckets per user with sophisticated refill strategies:

```python
# src/security/production_rate_limiter.py

import time
import json
import logging
import asyncio
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import redis
from redis.sentinel import Sentinel

logger = logging.getLogger(__name__)

class BucketType(Enum):
    """Different types of rate limiting buckets."""
    REQUESTS_PER_SECOND = "rps"
    REQUESTS_PER_MINUTE = "rpm"
    REQUESTS_PER_HOUR = "rph"
    REQUESTS_PER_DAY = "rpd"
    BURST = "burst"
    RESOURCE_SPECIFIC = "resource"

@dataclass
class BucketConfig:
    """Configuration for a rate limiting bucket."""
    capacity: int
    refill_rate: float  # tokens per second
    bucket_type: BucketType
    priority: int = 1  # Higher number = higher priority

class ProductionRateLimiter:
    """Enterprise-grade distributed rate limiter with multiple bucket types."""

    def __init__(self, redis_config: Dict[str, Any],
                 sentinel_config: Optional[Dict[str, Any]] = None):

        # Initialize Redis connection with failover support
        if sentinel_config:
            sentinel = Sentinel(sentinel_config["sentinels"])
            self.redis_client = sentinel.master_for(
                sentinel_config["service_name"],
                socket_timeout=0.1
            )
        else:
            self.redis_client = redis.Redis(**redis_config)

        # Bucket configuration
        self.bucket_prefix = "rate_limit_v2:"
        self.bucket_ttl = 7200  # 2 hour cleanup TTL

        # Default bucket configurations by user tier
        self.tier_configs = {
            "free": self._get_free_tier_config(),
            "premium": self._get_premium_tier_config(),
            "enterprise": self._get_enterprise_tier_config()
        }

        # Performance optimization
        self.local_cache = {}
        self.cache_ttl = 30  # seconds
```

The distributed architecture uses Redis Sentinel for high availability and automatic failover.

### Multi-Bucket Rate Limiting Strategy

Production systems use multiple bucket types for comprehensive rate control:

```python
    def _get_enterprise_tier_config(self) -> Dict[BucketType, BucketConfig]:
        """Enterprise tier gets generous limits with burst capacity."""
        return {
            BucketType.REQUESTS_PER_SECOND: BucketConfig(
                capacity=50, refill_rate=10, bucket_type=BucketType.REQUESTS_PER_SECOND
            ),
            BucketType.REQUESTS_PER_MINUTE: BucketConfig(
                capacity=2000, refill_rate=33.33, bucket_type=BucketType.REQUESTS_PER_MINUTE
            ),
            BucketType.REQUESTS_PER_HOUR: BucketConfig(
                capacity=50000, refill_rate=13.89, bucket_type=BucketType.REQUESTS_PER_HOUR
            ),
            BucketType.BURST: BucketConfig(
                capacity=200, refill_rate=5, bucket_type=BucketType.BURST, priority=3
            )
        }

    def _get_premium_tier_config(self) -> Dict[BucketType, BucketConfig]:
        """Premium tier gets enhanced limits."""
        return {
            BucketType.REQUESTS_PER_SECOND: BucketConfig(
                capacity=20, refill_rate=5, bucket_type=BucketType.REQUESTS_PER_SECOND
            ),
            BucketType.REQUESTS_PER_MINUTE: BucketConfig(
                capacity=1000, refill_rate=16.67, bucket_type=BucketType.REQUESTS_PER_MINUTE
            ),
            BucketType.REQUESTS_PER_HOUR: BucketConfig(
                capacity=20000, refill_rate=5.56, bucket_type=BucketType.REQUESTS_PER_HOUR
            ),
            BucketType.BURST: BucketConfig(
                capacity=50, refill_rate=2, bucket_type=BucketType.BURST, priority=2
            )
        }

    def _get_free_tier_config(self) -> Dict[BucketType, BucketConfig]:
        """Free tier gets basic limits."""
        return {
            BucketType.REQUESTS_PER_MINUTE: BucketConfig(
                capacity=100, refill_rate=1.67, bucket_type=BucketType.REQUESTS_PER_MINUTE
            ),
            BucketType.REQUESTS_PER_HOUR: BucketConfig(
                capacity=1000, refill_rate=0.28, bucket_type=BucketType.REQUESTS_PER_HOUR
            )
        }
```

Different tiers get appropriate bucket configurations that match their service levels.

### Advanced Distributed Rate Check Algorithm

The production rate check uses atomic Redis operations for consistency:

```python
    async def check_rate_limits(self, identifier: str, user_tier: str = "free",
                               resource_type: str = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check multiple rate limit buckets atomically.

        Returns: (allowed, rate_limit_info)
        """
        # Get bucket configurations for user tier
        bucket_configs = self.tier_configs.get(user_tier, self.tier_configs["free"])

        # Add resource-specific bucket if needed
        if resource_type:
            resource_bucket = self._get_resource_bucket_config(resource_type)
            if resource_bucket:
                bucket_configs[BucketType.RESOURCE_SPECIFIC] = resource_bucket

        current_time = time.time()

        # Check all buckets atomically using Redis pipeline
        pipe = self.redis_client.pipeline()
        bucket_keys = []

        try:
            # Step 1: Get all bucket states
            for bucket_type, config in bucket_configs.items():
                bucket_key = f"{self.bucket_prefix}{identifier}:{bucket_type.value}"
                bucket_keys.append((bucket_key, config))
                pipe.get(bucket_key)

            # Execute pipeline to get all bucket states
            bucket_states = pipe.execute()

            # Step 2: Calculate available tokens for each bucket
            bucket_results = []
            for i, ((bucket_key, config), state_data) in enumerate(zip(bucket_keys, bucket_states)):

                # Parse existing bucket state
                if state_data:
                    bucket_state = json.loads(state_data)
                    last_refill = bucket_state["last_refill"]
                    current_tokens = bucket_state["tokens"]
                else:
                    # Initialize new bucket
                    last_refill = current_time
                    current_tokens = float(config.capacity)

                # Calculate available tokens
                available_tokens = self._calculate_bucket_tokens(
                    last_refill, current_tokens, current_time, config
                )

                bucket_results.append({
                    "key": bucket_key,
                    "config": config,
                    "available_tokens": available_tokens,
                    "allowed": available_tokens >= 1.0
                })

            # Step 3: Determine overall result (all buckets must allow)
            overall_allowed = all(result["allowed"] for result in bucket_results)

            # Step 4: Update bucket states if request is allowed
            if overall_allowed:
                await self._update_bucket_states_atomic(bucket_results, current_time)

            # Step 5: Prepare rate limit information for response
            rate_limit_info = self._prepare_rate_limit_info(bucket_results, user_tier)

            return overall_allowed, rate_limit_info

        except Exception as e:
            logger.error(f"Rate limit check error for {identifier}: {e}")
            # Fail open for availability
            return True, {"error": "rate_limiter_unavailable"}
```

The atomic operation ensures consistency across multiple buckets in a distributed environment.

### Optimized Token Calculation

The token calculation algorithm handles multiple refill strategies efficiently:

```python
    def _calculate_bucket_tokens(self, last_refill: float, current_tokens: float,
                                current_time: float, config: BucketConfig) -> float:
        """
        Calculate current token count with optimized refill algorithm.

        Supports different refill strategies based on bucket type.
        """
        time_elapsed = max(0, current_time - last_refill)

        # Different refill strategies based on bucket type
        if config.bucket_type == BucketType.BURST:
            # Burst buckets refill more slowly after depletion
            burst_penalty = max(0, config.capacity - current_tokens) / config.capacity
            effective_rate = config.refill_rate * (1 - burst_penalty * 0.5)
            tokens_to_add = time_elapsed * effective_rate

        elif config.bucket_type in [BucketType.REQUESTS_PER_HOUR, BucketType.REQUESTS_PER_DAY]:
            # Long-term buckets use smoother refill to prevent gaming
            max_refill_per_period = config.capacity * 0.1  # Max 10% capacity per check
            tokens_to_add = min(time_elapsed * config.refill_rate, max_refill_per_period)

        else:
            # Standard linear refill for most buckets
            tokens_to_add = time_elapsed * config.refill_rate

        # Calculate new token count (capped at capacity)
        new_tokens = min(float(config.capacity), current_tokens + tokens_to_add)

        return new_tokens

    async def _update_bucket_states_atomic(self, bucket_results: List[Dict],
                                          current_time: float):
        """Update all bucket states atomically using Redis transaction."""

        pipe = self.redis_client.pipeline()

        try:
            # Start Redis transaction
            pipe.multi()

            for result in bucket_results:
                if result["allowed"]:
                    # Consume one token
                    remaining_tokens = result["available_tokens"] - 1.0
                else:
                    # No tokens consumed if not allowed
                    remaining_tokens = result["available_tokens"]

                # Update bucket state
                new_state = {
                    "tokens": remaining_tokens,
                    "last_refill": current_time,
                    "last_updated": current_time
                }

                pipe.setex(
                    result["key"],
                    self.bucket_ttl,
                    json.dumps(new_state)
                )

            # Execute transaction
            pipe.execute()

        except Exception as e:
            logger.error(f"Failed to update bucket states atomically: {e}")
            # Consider implementing compensation logic here
```

Atomic updates ensure bucket states remain consistent even under high concurrency.

### Dynamic Rate Limiting Based on Behavior

Implement intelligent rate limiting that adapts based on user behavior patterns:

```python
class BehavioralRateLimiter:
    """Advanced rate limiter that adapts based on user behavior."""

    def __init__(self, base_rate_limiter: ProductionRateLimiter):
        self.base_limiter = base_rate_limiter
        self.behavior_window = 3600  # 1 hour behavior analysis window

    async def check_adaptive_rate_limits(self, identifier: str,
                                        request_context: Dict[str, Any]) -> Tuple[bool, Dict]:
        """Check rate limits with behavioral adaptation."""

        # Step 1: Analyze recent behavior
        behavior_score = await self._analyze_user_behavior(identifier)

        # Step 2: Adjust rate limits based on behavior
        adjusted_tier = self._adjust_tier_for_behavior(
            request_context.get("base_tier", "free"),
            behavior_score
        )

        # Step 3: Apply standard rate limiting with adjusted tier
        allowed, rate_info = await self.base_limiter.check_rate_limits(
            identifier, adjusted_tier, request_context.get("resource_type")
        )

        # Step 4: Record request for future behavior analysis
        await self._record_request_behavior(identifier, request_context, allowed)

        # Step 5: Add behavioral context to response
        rate_info.update({
            "behavior_score": behavior_score,
            "tier_adjustment": adjusted_tier != request_context.get("base_tier", "free"),
            "adaptive_limiting": True
        })

        return allowed, rate_info

    async def _analyze_user_behavior(self, identifier: str) -> float:
        """
        Analyze user behavior to calculate trust score.

        Returns: behavior_score (0.0 to 1.0, higher = more trustworthy)
        """
        try:
            behavior_key = f"behavior:{identifier}"
            behavior_data = self.base_limiter.redis_client.get(behavior_key)

            if not behavior_data:
                return 0.5  # Neutral score for new users

            behavior = json.loads(behavior_data)
            current_time = time.time()

            # Calculate various behavior metrics
            success_rate = self._calculate_success_rate(behavior)
            consistency_score = self._calculate_consistency_score(behavior)
            abuse_indicators = self._detect_abuse_patterns(behavior)

            # Composite behavior score
            behavior_score = (
                success_rate * 0.4 +           # 40% weight to success rate
                consistency_score * 0.3 +      # 30% weight to consistency
                (1.0 - abuse_indicators) * 0.3 # 30% weight to lack of abuse
            )

            return max(0.0, min(1.0, behavior_score))

        except Exception as e:
            logger.error(f"Behavior analysis failed for {identifier}: {e}")
            return 0.5  # Default neutral score on error

    def _adjust_tier_for_behavior(self, base_tier: str, behavior_score: float) -> str:
        """Adjust user tier based on behavior score."""

        if behavior_score >= 0.9:
            # Excellent behavior - upgrade tier
            tier_upgrades = {"free": "premium", "premium": "enterprise", "enterprise": "enterprise"}
            return tier_upgrades.get(base_tier, base_tier)

        elif behavior_score <= 0.3:
            # Poor behavior - downgrade or restrict
            if base_tier in ["premium", "enterprise"]:
                return "free"  # Downgrade to free tier
            else:
                return "restricted"  # Further restrict free tier

        return base_tier  # No change for neutral behavior
```

Behavioral adaptation allows the system to reward good actors while restricting suspicious behavior.

### Rate Limiting Analytics and Monitoring

Implement comprehensive analytics for capacity planning and security monitoring:

```python
class RateLimitAnalytics:
    """Advanced analytics for rate limiting performance and security."""

    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.metrics_key_prefix = "rate_metrics:"

    async def record_rate_limit_event(self, identifier: str, event_type: str,
                                     metadata: Dict[str, Any]):
        """Record rate limiting events for analysis."""

        current_time = datetime.now()

        event_record = {
            "identifier": identifier,
            "event_type": event_type,  # allowed, denied, burst_used, etc.
            "timestamp": current_time.isoformat(),
            "metadata": metadata
        }

        # Store in time-based buckets for efficient querying
        time_bucket = current_time.strftime("%Y-%m-%d-%H")
        event_key = f"{self.metrics_key_prefix}events:{time_bucket}"

        # Add to time bucket (use list for chronological order)
        self.redis_client.lpush(event_key, json.dumps(event_record))
        self.redis_client.expire(event_key, 86400 * 7)  # Keep 7 days

        # Update aggregate metrics
        await self._update_aggregate_metrics(identifier, event_type, metadata)

    async def get_rate_limit_analytics(self, time_range: str = "24h",
                                      filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive rate limiting analytics."""

        try:
            end_time = datetime.now()
            start_time = self._parse_time_range(time_range, end_time)

            # Collect metrics from time buckets
            metrics = {
                "summary": await self._get_summary_metrics(start_time, end_time, filters),
                "top_users": await self._get_top_users_metrics(start_time, end_time),
                "rate_limit_violations": await self._get_violation_metrics(start_time, end_time),
                "bucket_utilization": await self._get_bucket_utilization(start_time, end_time),
                "behavioral_trends": await self._get_behavioral_trends(start_time, end_time),
                "capacity_recommendations": await self._generate_capacity_recommendations()
            }

            return metrics

        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            return {"error": "analytics_unavailable"}

    async def _get_summary_metrics(self, start_time: datetime, end_time: datetime,
                                  filters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary metrics for the time range."""

        total_requests = 0
        allowed_requests = 0
        denied_requests = 0
        burst_usage = 0

        # Iterate through time buckets in range
        current_time = start_time
        while current_time <= end_time:
            bucket_key = f"{self.metrics_key_prefix}events:{current_time.strftime('%Y-%m-%d-%H')}"

            # Get events from this time bucket
            events = self.redis_client.lrange(bucket_key, 0, -1)

            for event_data in events:
                try:
                    event = json.loads(event_data)

                    # Apply filters if specified
                    if filters and not self._event_matches_filters(event, filters):
                        continue

                    total_requests += 1

                    if event["event_type"] == "allowed":
                        allowed_requests += 1
                    elif event["event_type"] == "denied":
                        denied_requests += 1
                    elif event["event_type"] == "burst_used":
                        burst_usage += 1

                except (json.JSONDecodeError, KeyError):
                    continue

            current_time += timedelta(hours=1)

        # Calculate summary statistics
        allow_rate = (allowed_requests / total_requests * 100) if total_requests > 0 else 0

        return {
            "total_requests": total_requests,
            "allowed_requests": allowed_requests,
            "denied_requests": denied_requests,
            "allow_rate_percent": round(allow_rate, 2),
            "burst_usage_count": burst_usage,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            }
        }
```

Comprehensive analytics enable data-driven optimization of rate limiting policies.

### Advanced Circuit Breaker Integration

Combine rate limiting with circuit breaker patterns for enhanced resilience:

```python
class RateLimitCircuitBreaker:
    """Circuit breaker that adapts based on rate limiting metrics."""

    def __init__(self, rate_limiter: ProductionRateLimiter):
        self.rate_limiter = rate_limiter
        self.circuit_states = {}  # per-identifier circuit states

    async def check_with_circuit_breaker(self, identifier: str,
                                        request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limits with circuit breaker logic."""

        circuit_key = f"circuit:{identifier}"
        circuit_state = await self._get_circuit_state(circuit_key)

        # Check if circuit is open (blocking requests)
        if circuit_state["state"] == "open":
            if not self._should_attempt_reset(circuit_state):
                return {
                    "allowed": False,
                    "reason": "circuit_breaker_open",
                    "retry_after": circuit_state.get("retry_after", 60)
                }

        # Attempt request through rate limiter
        allowed, rate_info = await self.rate_limiter.check_rate_limits(
            identifier, request_context.get("tier", "free")
        )

        # Update circuit state based on result
        await self._update_circuit_state(circuit_key, allowed, rate_info)

        return {
            "allowed": allowed,
            "rate_info": rate_info,
            "circuit_state": circuit_state["state"]
        }
```

Circuit breaker integration provides additional protection against cascading failures.

---

## 🧭 Navigation

**Previous:** [Session 4 - Team Orchestration →](Session4_*.md)  
**Next:** [Session 6 - Modular Architecture →](Session6_*.md)

---

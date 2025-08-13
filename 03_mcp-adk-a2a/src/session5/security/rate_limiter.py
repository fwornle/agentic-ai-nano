"""Token bucket rate limiter with Redis backend for DDoS protection."""

import time
import json
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)


class TokenBucketRateLimiter:
    """Token bucket rate limiter with Redis backend."""
    
    def __init__(self, redis_client, default_capacity: int = 100, 
                 default_refill_rate: float = 10):
        self.redis_client = redis_client
        self.default_capacity = default_capacity
        self.default_refill_rate = default_refill_rate  # tokens per second
        self.bucket_prefix = "rate_limit:"
    
    async def is_allowed(self, identifier: str, capacity: int = None, 
                        refill_rate: float = None) -> bool:
        """Check if request is allowed under rate limit."""
        capacity = capacity or self.default_capacity
        refill_rate = refill_rate or self.default_refill_rate
        
        bucket_key = f"{self.bucket_prefix}{identifier}"
        current_time = time.time()
        
        try:
            # Get current bucket state
            bucket_data = self.redis_client.get(bucket_key)
            
            if bucket_data:
                bucket = json.loads(bucket_data)
                last_refill = bucket["last_refill"]
                tokens = bucket["tokens"]
            else:
                # Initialize new bucket
                last_refill = current_time
                tokens = float(capacity)
            
            # Calculate tokens to add based on time elapsed
            time_elapsed = current_time - last_refill
            tokens_to_add = time_elapsed * refill_rate
            tokens = min(capacity, tokens + tokens_to_add)
            
            # Check if request can be allowed
            if tokens >= 1.0:
                tokens -= 1.0
                allowed = True
            else:
                allowed = False
            
            # Update bucket state
            new_bucket = {
                "tokens": tokens,
                "last_refill": current_time
            }
            
            # Store with TTL
            self.redis_client.setex(
                bucket_key, 
                3600,  # 1 hour TTL
                json.dumps(new_bucket)
            )
            
            return allowed
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Fail open for availability


class RateLimitMiddleware:
    """Rate limiting middleware for MCP servers."""
    
    def __init__(self, rate_limiter: TokenBucketRateLimiter):
        self.rate_limiter = rate_limiter
        
        # Different limits for different user types
        self.limits = {
            "guest": {"capacity": 50, "refill_rate": 1},
            "user": {"capacity": 200, "refill_rate": 5},
            "premium": {"capacity": 1000, "refill_rate": 20},
            "admin": {"capacity": 5000, "refill_rate": 100}
        }
    
    async def check_rate_limit(self, request: Request, user_data: Dict) -> bool:
        """Check if request should be rate limited."""
        # Determine identifier and limits
        user_role = user_data.get("roles", ["guest"])[0]
        identifier = f"user:{user_data.get('sub', 'anonymous')}"
        
        limits = self.limits.get(user_role, self.limits["guest"])
        
        # Check rate limit
        allowed = await self.rate_limiter.is_allowed(
            identifier,
            capacity=limits["capacity"],
            refill_rate=limits["refill_rate"]
        )
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for user {identifier}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        return True
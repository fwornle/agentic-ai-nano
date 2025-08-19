# Session 4: Production MCP Deployment - Solution Guide

## 💡 Practical Exercise Solution

**Challenge:** Implement a circuit breaker pattern for MCP server resilience.

### Complete Solution:

```python
# src/resilience/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Failures before opening circuit
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes in half-open to close
    timeout: float = 30.0              # Request timeout in seconds
    expected_exceptions: tuple = (Exception,)  # Exceptions that count as failures

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass

class CircuitBreaker:
    """
    Circuit breaker implementation for resilient MCP server operations.
    
    The circuit breaker prevents cascading failures by monitoring the health
    of downstream services and failing fast when they're unavailable.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = 0
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: When circuit is open
        """
        current_time = time.time()
        
        # Check if we should attempt the call
        if not self._should_attempt_call(current_time):
            raise CircuitBreakerError(
                f"Circuit breaker is {self.state.value}. "
                f"Next attempt in {self.next_attempt_time - current_time:.1f}s"
            )
        
        try:
            # Execute the function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Record success
            await self._record_success()
            return result
            
        except self.config.expected_exceptions as e:
            # Record failure
            await self._record_failure(current_time)
            raise
        except asyncio.TimeoutError as e:
            # Timeout counts as failure
            await self._record_failure(current_time)
            raise CircuitBreakerError(f"Operation timed out after {self.config.timeout}s")
    
    def _should_attempt_call(self, current_time: float) -> bool:
        """Determine if we should attempt the call based on current state."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if current_time >= self.next_attempt_time:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    async def _record_success(self):
        """Record a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug(f"Circuit breaker success count: {self.success_count}")
            
            if self.success_count >= self.config.success_threshold:
                await self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0
    
    async def _record_failure(self, current_time: float):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = current_time
        
        logger.warning(f"Circuit breaker failure count: {self.failure_count}")
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                await self._open_circuit(current_time)
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open state opens the circuit
            await self._open_circuit(current_time)
    
    async def _open_circuit(self, current_time: float):
        """Open the circuit breaker."""
        self.state = CircuitState.OPEN
        self.next_attempt_time = current_time + self.config.recovery_timeout
        self.success_count = 0
        
        logger.error(
            f"Circuit breaker OPENED after {self.failure_count} failures. "
            f"Next attempt at {time.ctime(self.next_attempt_time)}"
        )
    
    async def _close_circuit(self):
        """Close the circuit breaker."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        
        logger.info("Circuit breaker CLOSED - service recovered")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current circuit breaker statistics."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time if self.state == CircuitState.OPEN else None
        }

# Integration with MCP Server
class ResilientMCPServer:
    """MCP server with circuit breaker protection for external dependencies."""
    
    def __init__(self):
        self.mcp = FastMCP("Resilient MCP Server")
        
        # Circuit breakers for different services
        self.circuit_breakers = {
            "database": CircuitBreaker(CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                timeout=10.0
            )),
            "weather_api": CircuitBreaker(CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                timeout=15.0
            )),
            "cache": CircuitBreaker(CircuitBreakerConfig(
                failure_threshold=2,
                recovery_timeout=10,
                timeout=5.0
            ))
        }
        
        self._setup_resilient_tools()
    
    def _setup_resilient_tools(self):
        """Set up MCP tools with circuit breaker protection."""
        
        @self.mcp.tool()
        async def get_weather_with_fallback(city: str) -> Dict[str, Any]:
            """Get weather data with circuit breaker protection and fallback."""
            try:
                # Try primary weather service with circuit breaker
                result = await self.circuit_breakers["weather_api"].call(
                    self._fetch_weather_data, city
                )
                return result
                
            except CircuitBreakerError as e:
                logger.warning(f"Weather service unavailable: {e}")
                
                # Fallback to cached data
                try:
                    cached_result = await self.circuit_breakers["cache"].call(
                        self._get_cached_weather, city
                    )
                    cached_result["source"] = "cache_fallback"
                    return cached_result
                    
                except CircuitBreakerError:
                    # Final fallback to static data
                    return {
                        "city": city,
                        "temperature": "N/A",
                        "condition": "Unknown",
                        "source": "static_fallback",
                        "message": "Weather service temporarily unavailable"
                    }
        
        @self.mcp.tool()
        async def store_data_resilient(data: Dict[str, Any]) -> Dict[str, Any]:
            """Store data with database circuit breaker protection."""
            try:
                result = await self.circuit_breakers["database"].call(
                    self._store_in_database, data
                )
                return result
                
            except CircuitBreakerError as e:
                logger.error(f"Database unavailable: {e}")
                
                # Fallback to queue for later processing
                await self._queue_for_later_processing(data)
                
                return {
                    "success": False,
                    "message": "Data queued for processing when database recovers",
                    "fallback": True
                }
        
        @self.mcp.resource("circuit-breaker://stats")
        async def get_circuit_breaker_stats() -> Dict[str, Any]:
            """Get circuit breaker statistics for all services."""
            stats = {}
            for service_name, cb in self.circuit_breakers.items():
                stats[service_name] = cb.get_stats()
            
            return {
                "circuit_breakers": stats,
                "timestamp": time.time(),
                "overall_health": self._calculate_overall_health(stats)
            }
    
    async def _fetch_weather_data(self, city: str) -> Dict[str, Any]:
        """Simulate fetching weather data from external API."""
        # Simulate potential failure
        if random.random() < 0.3:  # 30% failure rate for demo
            raise Exception("Weather API unavailable")
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        return {
            "city": city,
            "temperature": random.randint(15, 30),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy"]),
            "source": "live_api"
        }
    
    async def _get_cached_weather(self, city: str) -> Dict[str, Any]:
        """Get cached weather data."""
        # Simulate cache lookup
        return {
            "city": city,
            "temperature": 22,
            "condition": "Partly Cloudy",
            "cached_at": time.time() - 300  # 5 minutes ago
        }
    
    async def _store_in_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate storing data in database."""
        # Simulate potential database failure
        if random.random() < 0.2:  # 20% failure rate for demo
            raise Exception("Database connection failed")
        
        await asyncio.sleep(0.1)  # Simulate DB operation
        
        return {
            "success": True,
            "record_id": f"rec_{int(time.time())}",
            "stored_at": time.time()
        }
    
    async def _queue_for_later_processing(self, data: Dict[str, Any]):
        """Queue data for processing when database recovers."""
        # In production, this would use a message queue like Redis or RabbitMQ
        logger.info(f"Queued data for later processing: {data}")
    
    def _calculate_overall_health(self, stats: Dict[str, Any]) -> str:
        """Calculate overall system health based on circuit breaker states."""
        open_circuits = sum(1 for cb_stats in stats.values() 
                          if cb_stats["state"] == "open")
        
        if open_circuits == 0:
            return "healthy"
        elif open_circuits <= len(stats) // 2:
            return "degraded"
        else:
            return "critical"

# Demo and testing
async def demo_circuit_breaker():
    """Demonstrate circuit breaker functionality."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    server = ResilientMCPServer()
    
    console.print(Panel.fit(
        "🛡️ Circuit Breaker Demo\nTesting resilience patterns with simulated failures",
        title="Resilient MCP Server",
        border_style="blue"
    ))
    
    # Test weather service with potential failures
    for i in range(10):
        try:
            result = await server.mcp.get_tool("get_weather_with_fallback")("London")
            
            status = "✅" if result.get("source") == "live_api" else "⚠️"
            console.print(f"{status} Request {i+1}: {result.get('source', 'unknown')} - {result.get('temperature', 'N/A')}°C")
            
        except Exception as e:
            console.print(f"❌ Request {i+1}: {str(e)}")
        
        await asyncio.sleep(1)
    
    # Show circuit breaker stats
    stats_resource = server.mcp.get_resource("circuit-breaker://stats")
    stats = await stats_resource()
    
    stats_table = Table(title="Circuit Breaker Statistics")
    stats_table.add_column("Service", style="cyan")
    stats_table.add_column("State", style="yellow")
    stats_table.add_column("Failures", style="red")
    stats_table.add_column("Next Attempt", style="green")
    
    for service, cb_stats in stats["circuit_breakers"].items():
        next_attempt = "N/A"
        if cb_stats["next_attempt_time"]:
            next_attempt = f"in {cb_stats['next_attempt_time'] - time.time():.1f}s"
        
        stats_table.add_row(
            service,
            cb_stats["state"],
            str(cb_stats["failure_count"]),
            next_attempt
        )
    
    console.print(stats_table)
    console.print(f"Overall Health: {stats['overall_health']}")

if __name__ == "__main__":
    import random
    asyncio.run(demo_circuit_breaker())
```

### Key Features Implemented:

1. **State Management**: Properly manages CLOSED, OPEN, and HALF_OPEN states
2. **Configurable Thresholds**: Customizable failure thresholds and recovery timeouts
3. **Timeout Handling**: Includes request timeouts as circuit breaker triggers
4. **Fallback Strategies**: Multiple levels of fallback (cache, static data, queuing)
5. **Monitoring Integration**: Exposes circuit breaker statistics as MCP resources

### Advanced Circuit Breaker Patterns:

```python
# Bulkhead pattern for resource isolation
class BulkheadCircuitBreaker(CircuitBreaker):
    """Circuit breaker with resource pool isolation."""
    
    def __init__(self, config: CircuitBreakerConfig, max_concurrent: int = 10):
        super().__init__(config)
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with both circuit breaker and bulkhead protection."""
        async with self.semaphore:  # Limit concurrent requests
            return await super().call(func, *args, **kwargs)

# Adaptive circuit breaker with dynamic thresholds
class AdaptiveCircuitBreaker(CircuitBreaker):
    """Circuit breaker that adapts thresholds based on historical performance."""
    
    def __init__(self, config: CircuitBreakerConfig):
        super().__init__(config)
        self.success_rate_history = []
        self.adaptive_threshold = config.failure_threshold
    
    async def _record_success(self):
        """Record success and adapt thresholds."""
        await super()._record_success()
        
        # Track success rate over time
        self.success_rate_history.append(True)
        if len(self.success_rate_history) > 100:
            self.success_rate_history.pop(0)
        
        # Adapt threshold based on recent performance
        success_rate = sum(self.success_rate_history) / len(self.success_rate_history)
        if success_rate > 0.95:
            self.adaptive_threshold = min(self.config.failure_threshold + 2, 10)
        elif success_rate < 0.8:
            self.adaptive_threshold = max(self.config.failure_threshold - 1, 2)
```

### Testing Scenarios:

1. **Normal Operation**: Circuit stays closed with successful requests
2. **Service Degradation**: Circuit opens after threshold failures
3. **Recovery Testing**: Circuit transitions to half-open and eventually closes
4. **Timeout Handling**: Timeouts trigger circuit breaker appropriately
5. **Fallback Effectiveness**: Fallback strategies provide graceful degradation

This circuit breaker implementation provides robust failure handling and enables graceful degradation in production MCP deployments.
# Session 3 - Module A: Enterprise Agent Patterns

> **ADVANCED OPTIONAL MODULE** 
> This is supplementary content for deeper specialization.  
> **Prerequisites**: Complete Session 3 core content first.
> **Time Investment**: 45 minutes
> **Target Audience**: Implementer path students and enterprise developers

## Module Learning Outcomes

After completing this module, you will master:
- Production deployment patterns for LangChain MCP agents
- Advanced error handling and circuit breaker implementations
- Performance optimization and connection pooling strategies
- Enterprise security patterns and access control mechanisms
- Monitoring, logging, and observability for agent systems

## Industry Context & Applications

Based on current enterprise adoption patterns, organizations deploying LangChain MCP integrations at scale face specific challenges:

**Enterprise Requirements:**
- **High availability**: 99.9% uptime requirements for customer-facing agents
- **Scalability**: Handle 1000+ concurrent agent sessions
- **Security compliance**: SOC 2, GDPR, and industry-specific regulations
- **Performance SLAs**: Sub-second response times for simple queries
- **Cost optimization**: Efficient resource utilization across cloud environments

**Real-world implementations** from companies like Block demonstrate the need for sophisticated patterns beyond basic ReAct agents.

## Advanced Production Patterns

### Pattern 1: Circuit Breaker for MCP Server Resilience

Enterprise agents must handle partial system failures gracefully. The circuit breaker pattern prevents cascading failures when MCP servers become unavailable.

```python
# utils/circuit_breaker.py
import asyncio
import time
from enum import Enum
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure state - reject requests
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout: int = 60      # Seconds before trying again
    success_threshold: int = 3      # Successes needed to close
    timeout: int = 30              # Request timeout

class CircuitBreaker:
    """Circuit breaker for MCP server calls with enterprise reliability."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opens": 0
        }
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        self.metrics["total_requests"] += 1
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise e
    
    async def _on_success(self):
        """Handle successful operation."""
        self.metrics["successful_requests"] += 1
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit breaker {self.name} CLOSED - service recovered")
        else:
            self.failure_count = 0  # Reset failure count on success
    
    async def _on_failure(self):
        """Handle failed operation."""
        self.metrics["failed_requests"] += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if (self.state == CircuitState.CLOSED and 
            self.failure_count >= self.config.failure_threshold):
            self.state = CircuitState.OPEN
            self.metrics["circuit_opens"] += 1
            logger.error(f"Circuit breaker {self.name} OPENED - service failing")
        
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker {self.name} back to OPEN - service still failing")

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
```

### Pattern 2: Enhanced MCP Manager with Connection Pooling

Production deployments require efficient resource management and connection pooling to handle high concurrency.

```python
# utils/enterprise_mcp_manager.py
import asyncio
import time
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from langchain_mcp_adapters import MCPAdapter
from config import Config, MCPServerConfig
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig

logger = logging.getLogger(__name__)

class ConnectionPool:
    """Manages a pool of MCP adapter connections for high concurrency."""
    
    def __init__(self, server_config: MCPServerConfig, pool_size: int = 5):
        self.server_config = server_config
        self.pool_size = pool_size
        self.available_connections: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self.total_connections = 0
        self.metrics = {
            "connections_created": 0,
            "connections_reused": 0,
            "pool_exhausted_count": 0
        }
    
    async def initialize(self):
        """Pre-populate connection pool."""
        for _ in range(self.pool_size):
            adapter = await self._create_connection()
            if adapter:
                await self.available_connections.put(adapter)
    
    async def _create_connection(self) -> Optional[MCPAdapter]:
        """Create a new MCP adapter connection."""
        try:
            adapter = MCPAdapter(
                command=self.server_config.command,
                args=self.server_config.args,
                timeout=self.server_config.timeout
            )
            await adapter.start()
            self.total_connections += 1
            self.metrics["connections_created"] += 1
            return adapter
        except Exception as e:
            logger.error(f"Failed to create connection for {self.server_config.name}: {e}")
            return None
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool with automatic return."""
        adapter = None
        try:
            # Try to get existing connection
            try:
                adapter = self.available_connections.get_nowait()
                self.metrics["connections_reused"] += 1
            except asyncio.QueueEmpty:
                # Pool exhausted, create new connection
                self.metrics["pool_exhausted_count"] += 1
                adapter = await self._create_connection()
                if not adapter:
                    raise ConnectionError(f"Failed to create connection for {self.server_config.name}")
            
            yield adapter
            
        finally:
            # Return connection to pool if still valid
            if adapter:
                try:
                    self.available_connections.put_nowait(adapter)
                except asyncio.QueueFull:
                    # Pool full, close excess connection
                    await adapter.stop()
                    self.total_connections -= 1

class EnterpriseMCPManager:
    """Production-grade MCP server manager with advanced patterns."""
    
    def __init__(self, server_configs: List[MCPServerConfig]):
        self.server_configs = {config.name: config for config in server_configs}
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.health_status: Dict[str, bool] = {}
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
        self._monitoring_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize all connection pools and circuit breakers."""
        for name, config in self.server_configs.items():
            # Create connection pool
            pool = ConnectionPool(config, pool_size=5)
            await pool.initialize()
            self.connection_pools[name] = pool
            
            # Create circuit breaker
            cb_config = CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                success_threshold=3,
                timeout=config.timeout
            )
            self.circuit_breakers[name] = CircuitBreaker(name, cb_config)
            
            self.health_status[name] = True
            logger.info(f"Initialized enterprise MCP manager for {name}")
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def call_tool(self, server_name: str, tool_name: str, args: Dict[str, Any]) -> Any:
        """Call tool with enterprise patterns: pooling, circuit breaker, metrics."""
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        if server_name not in self.connection_pools:
            raise ValueError(f"Server {server_name} not configured")
        
        pool = self.connection_pools[server_name]
        circuit_breaker = self.circuit_breakers[server_name]
        
        try:
            async def _call_with_pool():
                async with pool.get_connection() as adapter:
                    return await adapter.call_tool(tool_name, args)
            
            # Execute with circuit breaker protection
            result = await circuit_breaker.call(_call_with_pool)
            
            # Update metrics
            response_time = time.time() - start_time
            self.metrics["successful_requests"] += 1
            self._update_average_response_time(response_time)
            
            return result
            
        except Exception as e:
            self.metrics["failed_requests"] += 1
            self.health_status[server_name] = False
            logger.error(f"Tool call failed for {server_name}.{tool_name}: {e}")
            raise
    
    def _update_average_response_time(self, response_time: float):
        """Update rolling average response time."""
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["successful_requests"]
        
        # Calculate rolling average
        self.metrics["average_response_time"] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    async def _monitoring_loop(self):
        """Continuous monitoring and health checks."""
        while True:
            try:
                for name in self.server_configs.keys():
                    await self._health_check(name)
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)
    
    async def _health_check(self, server_name: str):
        """Perform health check on server."""
        try:
            # Simple health check by listing tools
            pool = self.connection_pools[server_name]
            async with pool.get_connection() as adapter:
                await adapter.list_tools()
            
            self.health_status[server_name] = True
            
        except Exception as e:
            self.health_status[server_name] = False
            logger.warning(f"Health check failed for {server_name}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics for monitoring."""
        server_metrics = {}
        for name, cb in self.circuit_breakers.items():
            server_metrics[name] = {
                "circuit_breaker_state": cb.state.value,
                "circuit_breaker_metrics": cb.metrics,
                "connection_pool_metrics": self.connection_pools[name].metrics,
                "health_status": self.health_status[name]
            }
        
        return {
            "global_metrics": self.metrics,
            "server_metrics": server_metrics
        }
    
    async def cleanup(self):
        """Clean up resources."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for pool in self.connection_pools.values():
            while pool.total_connections > 0:
                try:
                    adapter = pool.available_connections.get_nowait()
                    await adapter.stop()
                    pool.total_connections -= 1
                except asyncio.QueueEmpty:
                    break
```

### Pattern 3: Enterprise Security and Access Control

Production agents require sophisticated access control and audit logging.

```python
# security/enterprise_auth.py
import jwt
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Permission(Enum):
    READ_WEATHER = "weather:read"
    READ_FILES = "files:read"
    WRITE_FILES = "files:write"
    QUERY_DATABASE = "database:query"
    MODIFY_DATABASE = "database:modify"
    ADMIN_TOOLS = "admin:*"

@dataclass
class UserContext:
    user_id: str
    roles: Set[str]
    permissions: Set[Permission]
    session_id: str
    expires_at: float
    organization_id: str

class EnterpriseAuthenticator:
    """Enterprise authentication and authorization for MCP agents."""
    
    def __init__(self, jwt_secret: str, default_permissions: Dict[str, List[Permission]]):
        self.jwt_secret = jwt_secret
        self.default_permissions = default_permissions
        self.active_sessions: Dict[str, UserContext] = {}
        self.audit_log: List[Dict] = []
    
    def authenticate_token(self, token: str) -> Optional[UserContext]:
        """Authenticate JWT token and return user context."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            user_id = payload.get("user_id")
            roles = set(payload.get("roles", []))
            session_id = payload.get("session_id")
            expires_at = payload.get("exp", 0)
            organization_id = payload.get("org_id")
            
            if time.time() > expires_at:
                self._audit("TOKEN_EXPIRED", {"user_id": user_id})
                return None
            
            # Calculate permissions from roles
            permissions = set()
            for role in roles:
                permissions.update(self.default_permissions.get(role, []))
            
            user_context = UserContext(
                user_id=user_id,
                roles=roles,
                permissions=permissions,
                session_id=session_id,
                expires_at=expires_at,
                organization_id=organization_id
            )
            
            self.active_sessions[session_id] = user_context
            self._audit("USER_AUTHENTICATED", {"user_id": user_id, "roles": list(roles)})
            
            return user_context
            
        except jwt.InvalidTokenError as e:
            self._audit("INVALID_TOKEN", {"error": str(e)})
            return None
    
    def authorize_tool_access(self, user_context: UserContext, server_name: str, tool_name: str) -> bool:
        """Check if user has permission to access specific tool."""
        required_permission = self._get_required_permission(server_name, tool_name)
        
        if required_permission in user_context.permissions:
            self._audit("TOOL_ACCESS_GRANTED", {
                "user_id": user_context.user_id,
                "server": server_name,
                "tool": tool_name
            })
            return True
        
        self._audit("TOOL_ACCESS_DENIED", {
            "user_id": user_context.user_id,
            "server": server_name,
            "tool": tool_name,
            "required_permission": required_permission.value
        })
        return False
    
    def _get_required_permission(self, server_name: str, tool_name: str) -> Permission:
        """Map server/tool combinations to required permissions."""
        permission_map = {
            ("weather", "get_current_weather"): Permission.READ_WEATHER,
            ("weather", "get_forecast"): Permission.READ_WEATHER,
            ("filesystem", "read_file"): Permission.READ_FILES,
            ("filesystem", "write_file"): Permission.WRITE_FILES,
            ("filesystem", "list_files"): Permission.READ_FILES,
            ("database", "query"): Permission.QUERY_DATABASE,
            ("database", "insert"): Permission.MODIFY_DATABASE,
            ("database", "update"): Permission.MODIFY_DATABASE,
        }
        
        return permission_map.get((server_name, tool_name), Permission.ADMIN_TOOLS)
    
    def _audit(self, action: str, details: Dict):
        """Log security events for audit trail."""
        audit_entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details
        }
        
        self.audit_log.append(audit_entry)
        logger.info(f"SECURITY_AUDIT: {action} - {details}")
        
        # Keep only last 1000 entries in memory
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(self, user_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retrieve audit log entries."""
        if user_id:
            filtered_log = [
                entry for entry in self.audit_log 
                if entry["details"].get("user_id") == user_id
            ]
        else:
            filtered_log = self.audit_log
        
        return filtered_log[-limit:]
```

### Pattern 4: Performance Monitoring and Observability

Enterprise deployments require comprehensive monitoring and alerting capabilities.

```python
# monitoring/enterprise_monitoring.py
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: float
    server_name: str
    tool_name: str
    response_time: float
    success: bool
    error_type: Optional[str] = None
    user_id: Optional[str] = None

class PerformanceTracker:
    """Enterprise-grade performance monitoring for MCP agents."""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: deque = deque(maxlen=10000)  # Keep last 10k metrics
        self.alert_thresholds = {
            "response_time_p95": 5.0,      # 95th percentile response time
            "error_rate": 0.05,            # 5% error rate
            "availability": 0.99           # 99% availability
        }
        self.alerts: List[Dict] = []
        
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric."""
        self.metrics.append(metric)
        self._check_alerts()
    
    def get_server_stats(self, server_name: str, hours: int = 1) -> Dict[str, Any]:
        """Get comprehensive statistics for a server."""
        cutoff_time = time.time() - (hours * 3600)
        server_metrics = [
            m for m in self.metrics 
            if m.server_name == server_name and m.timestamp >= cutoff_time
        ]
        
        if not server_metrics:
            return {"error": "No metrics found for server"}
        
        successful_metrics = [m for m in server_metrics if m.success]
        failed_metrics = [m for m in server_metrics if not m.success]
        
        response_times = [m.response_time for m in successful_metrics]
        
        stats = {
            "total_requests": len(server_metrics),
            "successful_requests": len(successful_metrics),
            "failed_requests": len(failed_metrics),
            "error_rate": len(failed_metrics) / len(server_metrics) if server_metrics else 0,
            "availability": len(successful_metrics) / len(server_metrics) if server_metrics else 0,
        }
        
        if response_times:
            stats.update({
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p50_response_time": statistics.median(response_times),
                "p95_response_time": self._percentile(response_times, 0.95),
                "p99_response_time": self._percentile(response_times, 0.99),
            })
        
        # Error breakdown
        error_counts = defaultdict(int)
        for metric in failed_metrics:
            error_counts[metric.error_type or "unknown"] += 1
        stats["error_breakdown"] = dict(error_counts)
        
        return stats
    
    def get_tool_stats(self, tool_name: str, hours: int = 1) -> Dict[str, Any]:
        """Get statistics for a specific tool across all servers."""
        cutoff_time = time.time() - (hours * 3600)
        tool_metrics = [
            m for m in self.metrics 
            if m.tool_name == tool_name and m.timestamp >= cutoff_time
        ]
        
        if not tool_metrics:
            return {"error": "No metrics found for tool"}
        
        # Group by server
        server_stats = defaultdict(list)
        for metric in tool_metrics:
            server_stats[metric.server_name].append(metric)
        
        result = {
            "total_requests": len(tool_metrics),
            "servers_used": list(server_stats.keys()),
            "per_server_stats": {}
        }
        
        for server, metrics in server_stats.items():
            successful = [m for m in metrics if m.success]
            result["per_server_stats"][server] = {
                "requests": len(metrics),
                "success_rate": len(successful) / len(metrics),
                "avg_response_time": statistics.mean([m.response_time for m in successful]) if successful else 0
            }
        
        return result
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(percentile * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _check_alerts(self):
        """Check for alert conditions."""
        # Only check alerts every 100 metrics to avoid overhead
        if len(self.metrics) % 100 != 0:
            return
        
        # Check last hour of data
        recent_stats = self.get_server_stats("all", hours=1)
        if "error" in recent_stats:
            return
        
        # Check response time P95
        if recent_stats.get("p95_response_time", 0) > self.alert_thresholds["response_time_p95"]:
            self._trigger_alert("HIGH_RESPONSE_TIME", {
                "p95_response_time": recent_stats["p95_response_time"],
                "threshold": self.alert_thresholds["response_time_p95"]
            })
        
        # Check error rate
        if recent_stats.get("error_rate", 0) > self.alert_thresholds["error_rate"]:
            self._trigger_alert("HIGH_ERROR_RATE", {
                "error_rate": recent_stats["error_rate"],
                "threshold": self.alert_thresholds["error_rate"]
            })
        
        # Check availability
        if recent_stats.get("availability", 1) < self.alert_thresholds["availability"]:
            self._trigger_alert("LOW_AVAILABILITY", {
                "availability": recent_stats["availability"],
                "threshold": self.alert_thresholds["availability"]
            })
    
    def _trigger_alert(self, alert_type: str, details: Dict):
        """Trigger an alert."""
        alert = {
            "timestamp": time.time(),
            "type": alert_type,
            "details": details,
            "resolved": False
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT: {alert_type} - {details}")
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        recent_time = time.time() - 300  # Last 5 minutes
        recent_metrics = [m for m in self.metrics if m.timestamp >= recent_time]
        
        if not recent_metrics:
            return {"status": "UNKNOWN", "reason": "No recent metrics"}
        
        error_rate = len([m for m in recent_metrics if not m.success]) / len(recent_metrics)
        avg_response_time = statistics.mean([m.response_time for m in recent_metrics if m.success])
        
        if error_rate > 0.1:  # 10% error rate
            return {"status": "CRITICAL", "reason": "High error rate", "error_rate": error_rate}
        elif error_rate > 0.05:  # 5% error rate
            return {"status": "WARNING", "reason": "Elevated error rate", "error_rate": error_rate}
        elif avg_response_time > 3.0:  # 3 second average
            return {"status": "WARNING", "reason": "Slow response times", "avg_response_time": avg_response_time}
        else:
            return {"status": "HEALTHY", "error_rate": error_rate, "avg_response_time": avg_response_time}
```

## Module Assessment (10 minutes)

**Question 1:** What is the primary purpose of the circuit breaker pattern in enterprise MCP deployments?

A) Improve performance
B) Prevent cascading failures  
C) Reduce memory usage
D) Simplify configuration

**Question 2:** In the connection pooling pattern, what happens when the pool is exhausted?

A) Requests are rejected
B) New connections are created temporarily
C) The system waits indefinitely  
D) Connections are shared unsafely

**Question 3:** Which authentication standard does the enterprise security pattern implement?

A) Basic authentication
B) OAuth 2.0
C) JWT tokens
D) API keys

**Question 4:** What triggers performance alerts in the monitoring system?

A) Manual configuration only
B) Threshold violations for response time, error rate, or availability
C) User complaints
D) Server restart events

**Question 5:** How does the enterprise MCP manager handle server failures?

A) Immediate shutdown
B) Circuit breaker protection with automatic recovery testing
C) Manual intervention required
D) Load balancing to other servers

**Question 6:** What is the benefit of audit logging in enterprise deployments?

A) Performance optimization
B) Compliance and security forensics
C) Debugging code issues
D) User experience improvement

**Question 7:** In the performance tracking system, what does P95 response time represent?

A) Average response time
B) 95% of requests complete within this time
C) Maximum response time
D) 95% availability percentage

[**View Module A Test Solutions →**](Session3_ModuleA_Test_Solutions.md)

---

[← Back to Session 3](Session3_LangChain_MCP_Integration.md) | [Next: Module B →](Session3_ModuleB_Advanced_Workflows.md)
"""
Enterprise Architecture and Integration Patterns
Comprehensive system for managing enterprise system integrations.
"""

from typing import Dict, Any, List, Protocol, Optional, Union
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationPattern(Enum):
    """Common enterprise integration patterns."""
    REQUEST_REPLY = "request_reply"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    MESSAGE_QUEUE = "message_queue"
    API_GATEWAY = "api_gateway"
    SERVICE_MESH = "service_mesh"
    EVENT_DRIVEN = "event_driven"
    BATCH_PROCESSING = "batch_processing"

class SystemType(Enum):
    """Types of enterprise systems."""
    ERP = "erp"
    CRM = "crm"
    DATABASE = "database"
    API_SERVICE = "api_service"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    CLOUD_SERVICE = "cloud_service"

@dataclass
class SystemConnection:
    """Configuration for enterprise system connections."""
    system_name: str
    system_type: SystemType
    endpoint: str
    auth_method: str
    credentials: Dict[str, Any]
    timeout_seconds: int = 30
    retry_policy: Dict[str, int] = field(default_factory=lambda: {
        "max_retries": 3,
        "backoff_factor": 2,
        "initial_delay": 1
    })
    circuit_breaker: bool = True
    rate_limit: Optional[int] = None
    health_check_interval: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationResult:
    """Result of an integration operation."""
    success: bool
    data: Any = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0
    system_name: str = ""
    operation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

class EnterpriseSystemAdapter(Protocol):
    """Protocol for enterprise system adapters."""
    
    async def connect(self) -> bool:
        """Establish connection to enterprise system."""
        ...
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with enterprise system."""
        ...
    
    async def execute_operation(self, operation: str, params: Dict[str, Any]) -> IntegrationResult:
        """Execute operation on enterprise system."""
        ...
    
    async def health_check(self) -> bool:
        """Check system health and connectivity."""
        ...
    
    async def disconnect(self) -> None:
        """Clean up connection resources."""
        ...

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_refill = time.time()
        
    def can_proceed(self) -> bool:
        """Check if request can proceed."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Refill tokens based on elapsed time
        tokens_to_add = int(elapsed * self.max_requests / self.time_window)
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
        self.last_refill = now
        
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False

class EnterpriseIntegrationManager:
    """Central manager for enterprise system integrations."""
    
    def __init__(self):
        self.adapters: Dict[str, EnterpriseSystemAdapter] = {}
        self.connections: Dict[str, SystemConnection] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.health_status: Dict[str, bool] = {}
        self.metrics: Dict[str, Dict] = {}
        
    def register_system(self, connection: SystemConnection, 
                       adapter: EnterpriseSystemAdapter) -> None:
        """Register a new enterprise system."""
        system_name = connection.system_name
        
        self.connections[system_name] = connection
        self.adapters[system_name] = adapter
        
        if connection.circuit_breaker:
            self.circuit_breakers[system_name] = CircuitBreaker()
            
        if connection.rate_limit:
            self.rate_limiters[system_name] = RateLimiter(connection.rate_limit)
            
        self.metrics[system_name] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "last_health_check": None
        }
        
        logger.info(f"Registered enterprise system: {system_name}")
    
    async def execute_operation(self, system_name: str, operation: str, 
                               params: Dict[str, Any]) -> IntegrationResult:
        """Execute operation on enterprise system with fault tolerance."""
        start_time = time.time()
        
        try:
            # Check if system is registered
            if system_name not in self.adapters:
                return IntegrationResult(
                    success=False,
                    error_message=f"System {system_name} not registered",
                    system_name=system_name,
                    operation=operation
                )
            
            # Check circuit breaker
            circuit_breaker = self.circuit_breakers.get(system_name)
            if circuit_breaker and not circuit_breaker.can_execute():
                return IntegrationResult(
                    success=False,
                    error_message=f"Circuit breaker OPEN for {system_name}",
                    system_name=system_name,
                    operation=operation
                )
            
            # Check rate limiter
            rate_limiter = self.rate_limiters.get(system_name)
            if rate_limiter and not rate_limiter.can_proceed():
                return IntegrationResult(
                    success=False,
                    error_message=f"Rate limit exceeded for {system_name}",
                    system_name=system_name,
                    operation=operation
                )
            
            # Execute with retry logic
            connection = self.connections[system_name]
            adapter = self.adapters[system_name]
            
            result = await self._execute_with_retry(
                adapter, operation, params, connection.retry_policy
            )
            
            # Update metrics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            result.system_name = system_name
            result.operation = operation
            
            self._update_metrics(system_name, result)
            
            # Update circuit breaker
            if circuit_breaker:
                if result.success:
                    circuit_breaker.record_success()
                else:
                    circuit_breaker.record_failure()
            
            return result
            
        except Exception as e:
            logger.error(f"Integration error for {system_name}: {e}")
            execution_time = time.time() - start_time
            
            result = IntegrationResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time,
                system_name=system_name,
                operation=operation
            )
            
            self._update_metrics(system_name, result)
            
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            return result
    
    async def _execute_with_retry(self, adapter: EnterpriseSystemAdapter, 
                                 operation: str, params: Dict[str, Any],
                                 retry_policy: Dict[str, int]) -> IntegrationResult:
        """Execute operation with exponential backoff retry."""
        max_retries = retry_policy.get("max_retries", 3)
        backoff_factor = retry_policy.get("backoff_factor", 2)
        initial_delay = retry_policy.get("initial_delay", 1)
        
        for attempt in range(max_retries + 1):
            try:
                result = await adapter.execute_operation(operation, params)
                result.retry_count = attempt
                return result
                
            except Exception as e:
                if attempt == max_retries:
                    return IntegrationResult(
                        success=False,
                        error_message=str(e),
                        retry_count=attempt
                    )
                
                delay = initial_delay * (backoff_factor ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                await asyncio.sleep(delay)
        
        # This shouldn't be reached, but just in case
        return IntegrationResult(
            success=False,
            error_message="Max retries exceeded",
            retry_count=max_retries
        )
    
    def _update_metrics(self, system_name: str, result: IntegrationResult) -> None:
        """Update system metrics."""
        metrics = self.metrics[system_name]
        metrics["total_requests"] += 1
        
        if result.success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1
        
        # Update average response time (exponential moving average)
        if metrics["avg_response_time"] == 0:
            metrics["avg_response_time"] = result.execution_time
        else:
            alpha = 0.1  # Smoothing factor
            metrics["avg_response_time"] = (
                alpha * result.execution_time + 
                (1 - alpha) * metrics["avg_response_time"]
            )
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health check on all registered systems."""
        health_results = {}
        
        for system_name, adapter in self.adapters.items():
            try:
                is_healthy = await adapter.health_check()
                health_results[system_name] = is_healthy
                self.health_status[system_name] = is_healthy
                self.metrics[system_name]["last_health_check"] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"Health check failed for {system_name}: {e}")
                health_results[system_name] = False
                self.health_status[system_name] = False
        
        return health_results
    
    def get_system_metrics(self, system_name: str) -> Dict[str, Any]:
        """Get metrics for a specific system."""
        if system_name not in self.metrics:
            return {}
        
        metrics = self.metrics[system_name].copy()
        
        # Add calculated metrics
        total = metrics["total_requests"]
        if total > 0:
            metrics["success_rate"] = metrics["successful_requests"] / total
            metrics["error_rate"] = metrics["failed_requests"] / total
        else:
            metrics["success_rate"] = 0.0
            metrics["error_rate"] = 0.0
        
        # Add circuit breaker status
        circuit_breaker = self.circuit_breakers.get(system_name)
        if circuit_breaker:
            metrics["circuit_breaker_state"] = circuit_breaker.state
            metrics["circuit_breaker_failures"] = circuit_breaker.failure_count
        
        return metrics
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all systems."""
        return {
            system_name: self.get_system_metrics(system_name)
            for system_name in self.adapters.keys()
        }

# Example usage and demo
async def demo_enterprise_integration():
    """Demonstrate enterprise integration patterns."""
    # Conditional imports for rich library to prevent crashes
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False
        # Fallback console implementation
        class Console:
            def print(self, *args, **kwargs):
                print(*args)
        
        class Table:
            def __init__(self, title=""):
                self.title = title
                self.columns = []
                self.rows = []
            
            def add_column(self, name, **kwargs):
                self.columns.append(name)
            
            def add_row(self, *values):
                self.rows.append(values)
        
        class Panel:
            @staticmethod
            def fit(text, title="", border_style=""):
                return f"\n=== {title} ===\n{text}\n"
    
    console = Console()
    
    console.print(Panel.fit(
        "🏢 Enterprise Integration Manager Demo\n"
        "Demonstrating enterprise system integration patterns",
        title="Enterprise Architecture",
        border_style="blue"
    ))
    
    # Create integration manager
    integration_manager = EnterpriseIntegrationManager()
    
    # Mock adapter for demonstration
    class MockAdapter:
        def __init__(self, name: str, should_fail: bool = False):
            self.name = name
            self.should_fail = should_fail
            self.connected = False
        
        async def connect(self) -> bool:
            await asyncio.sleep(0.1)  # Simulate connection time
            self.connected = not self.should_fail
            return self.connected
        
        async def authenticate(self, credentials: Dict[str, Any]) -> bool:
            await asyncio.sleep(0.05)
            return self.connected
        
        async def execute_operation(self, operation: str, params: Dict[str, Any]) -> IntegrationResult:
            await asyncio.sleep(0.1)  # Simulate operation time
            
            if self.should_fail:
                return IntegrationResult(
                    success=False,
                    error_message="Simulated system failure"
                )
            
            return IntegrationResult(
                success=True,
                data={"operation": operation, "result": f"Success from {self.name}"}
            )
        
        async def health_check(self) -> bool:
            return self.connected and not self.should_fail
        
        async def disconnect(self) -> None:
            self.connected = False
    
    # Register mock systems
    systems = [
        ("sap_system", SystemType.ERP, False),
        ("salesforce", SystemType.CRM, False),
        ("postgres_db", SystemType.DATABASE, False),
        ("failing_system", SystemType.API_SERVICE, True)  # This will fail for demo
    ]
    
    for name, sys_type, should_fail in systems:
        connection = SystemConnection(
            system_name=name,
            system_type=sys_type,
            endpoint=f"https://{name}.company.com/api",
            auth_method="oauth2",
            credentials={"client_id": "demo", "client_secret": "secret"},
            circuit_breaker=True,
            rate_limit=10
        )
        
        adapter = MockAdapter(name, should_fail)
        integration_manager.register_system(connection, adapter)
    
    # Test operations
    console.print("\n🔧 Testing Integration Operations:")
    
    operations = [
        ("sap_system", "get_customer", {"customer_id": "12345"}),
        ("salesforce", "create_lead", {"name": "John Doe", "email": "john@example.com"}),
        ("postgres_db", "query", {"sql": "SELECT * FROM users LIMIT 10"}),
        ("failing_system", "test_operation", {})  # This will fail
    ]
    
    results = []
    for system_name, operation, params in operations:
        result = await integration_manager.execute_operation(system_name, operation, params)
        results.append((system_name, operation, result))
        
        status = "✅" if result.success else "❌"
        console.print(f"{status} {system_name}.{operation}: {result.execution_time:.3f}s")
        if not result.success:
            console.print(f"   Error: {result.error_message}")
    
    # Perform health checks
    console.print("\n🏥 Health Check Results:")
    health_results = await integration_manager.health_check_all()
    
    for system_name, is_healthy in health_results.items():
        status = "🟢" if is_healthy else "🔴"
        console.print(f"{status} {system_name}: {'Healthy' if is_healthy else 'Unhealthy'}")
    
    # Display metrics
    console.print("\n📊 System Metrics:")
    metrics_table = Table(title="Integration Metrics")
    metrics_table.add_column("System", style="cyan")
    metrics_table.add_column("Requests", style="yellow")
    metrics_table.add_column("Success Rate", style="green")
    metrics_table.add_column("Avg Response Time", style="blue")
    metrics_table.add_column("Circuit Breaker", style="magenta")
    
    all_metrics = integration_manager.get_all_metrics()
    for system_name, metrics in all_metrics.items():
        metrics_table.add_row(
            system_name,
            str(metrics.get("total_requests", 0)),
            f"{metrics.get('success_rate', 0):.1%}",
            f"{metrics.get('avg_response_time', 0):.3f}s",
            metrics.get("circuit_breaker_state", "N/A")
        )
    
    console.print(metrics_table)

if __name__ == "__main__":
    asyncio.run(demo_enterprise_integration())
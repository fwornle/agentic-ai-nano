"""
Enterprise Architecture & Integration Patterns for Production Agent Systems

This module implements enterprise-grade integration patterns and system adapters
for connecting AI agents with enterprise infrastructure including ERP, CRM, 
databases, and legacy systems.
"""

from typing import Dict, Any, List, Protocol, Optional, Set, Callable, Union
from abc import ABC, abstractmethod
import asyncio
import aiohttp
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import time
from datetime import datetime, timedelta
import uuid
import hashlib
import threading
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationPattern(Enum):
    """Common enterprise integration patterns for agent systems."""
    REQUEST_REPLY = "request_reply"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    MESSAGE_QUEUE = "message_queue"
    API_GATEWAY = "api_gateway"
    SERVICE_MESH = "service_mesh"
    EVENT_SOURCING = "event_sourcing"
    CQRS = "cqrs"
    SAGA = "saga"

class SystemType(Enum):
    """Types of enterprise systems that agents can integrate with."""
    ERP = "erp"
    CRM = "crm"
    DATABASE = "database"
    LEGACY = "legacy"
    MESSAGING = "messaging"
    AUTHENTICATION = "authentication"
    MONITORING = "monitoring"
    FILE_STORAGE = "file_storage"

@dataclass
class SystemConnection:
    """Configuration for enterprise system connections with comprehensive settings."""
    system_name: str
    system_type: SystemType
    endpoint: str
    auth_method: str
    credentials: Dict[str, Any]
    retry_policy: Dict[str, int] = field(default_factory=lambda: {
        "max_retries": 3,
        "initial_delay": 1,
        "max_delay": 60,
        "exponential_backoff": True
    })
    circuit_breaker: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "failure_threshold": 5,
        "recovery_timeout": 30,
        "half_open_max_calls": 3
    })
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "requests_per_second": 10,
        "requests_per_minute": 600,
        "burst_size": 20
    })
    health_check: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "endpoint": "/health",
        "interval_seconds": 30,
        "timeout_seconds": 5
    })
    security_config: Dict[str, Any] = field(default_factory=lambda: {
        "ssl_verify": True,
        "cert_path": None,
        "encryption_required": True,
        "audit_logging": True
    })

class CircuitBreakerState(Enum):
    """Circuit breaker states for fault tolerance."""
    CLOSED = "closed"
    OPEN = "open" 
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    failure_count: int = 0
    success_count: int = 0
    total_requests: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changed_at: datetime = field(default_factory=datetime.now)

class EnterpriseSystemAdapter(Protocol):
    """Protocol defining the interface for enterprise system adapters."""
    
    async def connect(self) -> bool:
        """Establish connection to enterprise system with authentication."""
        ...
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with enterprise system using various methods."""
        ...
    
    async def execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute operation on enterprise system with error handling."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check system health and connectivity status."""
        ...
    
    async def disconnect(self) -> bool:
        """Properly disconnect from enterprise system."""
        ...

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance in enterprise integrations."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30, 
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.half_open_calls = 0
        self._lock = threading.Lock()
    
    @asynccontextmanager
    async def call(self, system_name: str):
        """Context manager for circuit breaker protected calls."""
        if not self._can_execute():
            raise CircuitBreakerException(f"Circuit breaker OPEN for {system_name}")
        
        try:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.half_open_calls += 1
            
            yield
            
            # Success - record it
            await self._record_success()
            
        except Exception as e:
            await self._record_failure()
            raise
    
    def _can_execute(self) -> bool:
        """Check if requests can be executed based on circuit breaker state."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            elif self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if (datetime.now() - self.metrics.state_changed_at).seconds >= self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    self.metrics.state_changed_at = datetime.now()
                    logger.info(f"Circuit breaker transitioning to HALF_OPEN")
                    return True
                return False
            elif self.state == CircuitBreakerState.HALF_OPEN:
                return self.half_open_calls < self.half_open_max_calls
        return False
    
    async def _record_success(self):
        """Record successful operation."""
        with self._lock:
            self.metrics.success_count += 1
            self.metrics.total_requests += 1
            self.metrics.last_success_time = datetime.now()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                # Enough successful calls in half-open state
                if self.metrics.success_count >= self.half_open_max_calls:
                    self.state = CircuitBreakerState.CLOSED
                    self.metrics.failure_count = 0
                    self.metrics.state_changed_at = datetime.now()
                    logger.info(f"Circuit breaker transitioning to CLOSED")
    
    async def _record_failure(self):
        """Record failed operation."""
        with self._lock:
            self.metrics.failure_count += 1
            self.metrics.total_requests += 1
            self.metrics.last_failure_time = datetime.now()
            
            if self.metrics.failure_count >= self.failure_threshold:
                if self.state != CircuitBreakerState.OPEN:
                    self.state = CircuitBreakerState.OPEN
                    self.metrics.state_changed_at = datetime.now()
                    logger.warning(f"Circuit breaker transitioning to OPEN")

class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open."""
    pass

class RateLimiter:
    """Rate limiter for controlling request frequency to enterprise systems."""
    
    def __init__(self, requests_per_second: int = 10, burst_size: int = 20):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from rate limiter."""
        with self._lock:
            now = time.time()
            time_passed = now - self.last_update
            self.last_update = now
            
            # Add tokens based on time passed
            self.tokens += time_passed * self.requests_per_second
            self.tokens = min(self.tokens, self.burst_size)
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class EnterpriseIntegrationManager:
    """Comprehensive manager for enterprise system integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections: Dict[str, SystemConnection] = {}
        self.adapters: Dict[str, EnterpriseSystemAdapter] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def initialize(self):
        """Initialize integration manager and all system connections."""
        logger.info("Initializing Enterprise Integration Manager")
        
        # Create HTTP session with connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=30,  # Connections per host
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "EnterpriseAgent/1.0"}
        )
        
        # Initialize system connections
        systems_config = self.config.get("systems", {})
        for system_name, system_config in systems_config.items():
            await self._register_system(system_name, system_config)
        
        # Start health check monitoring
        asyncio.create_task(self._health_check_loop())
        
        logger.info(f"Initialized {len(self.connections)} enterprise system connections")
    
    async def _register_system(self, system_name: str, config: Dict[str, Any]):
        """Register a new enterprise system for integration."""
        try:
            # Create system connection configuration
            connection = SystemConnection(
                system_name=system_name,
                system_type=SystemType(config["type"]),
                endpoint=config["endpoint"],
                auth_method=config["auth_method"],
                credentials=config["credentials"],
                retry_policy=config.get("retry_policy", {}),
                circuit_breaker=config.get("circuit_breaker", {}),
                rate_limits=config.get("rate_limits", {}),
                health_check=config.get("health_check", {}),
                security_config=config.get("security_config", {})
            )
            
            self.connections[system_name] = connection
            
            # Initialize circuit breaker
            cb_config = connection.circuit_breaker
            self.circuit_breakers[system_name] = CircuitBreaker(
                failure_threshold=cb_config.get("failure_threshold", 5),
                recovery_timeout=cb_config.get("recovery_timeout", 30),
                half_open_max_calls=cb_config.get("half_open_max_calls", 3)
            )
            
            # Initialize rate limiter
            rl_config = connection.rate_limits
            self.rate_limiters[system_name] = RateLimiter(
                requests_per_second=rl_config.get("requests_per_second", 10),
                burst_size=rl_config.get("burst_size", 20)
            )
            
            # Initialize adapter based on system type
            adapter = await self._create_adapter(connection)
            if adapter:
                self.adapters[system_name] = adapter
                
                # Test connection
                if await adapter.connect():
                    logger.info(f"Successfully connected to {system_name}")
                else:
                    logger.warning(f"Failed to connect to {system_name}")
            
        except Exception as e:
            logger.error(f"Failed to register system {system_name}: {e}")
    
    async def _create_adapter(self, connection: SystemConnection) -> Optional[EnterpriseSystemAdapter]:
        """Create appropriate adapter based on system type."""
        # This would be extended with actual adapter implementations
        # For now, return a generic adapter
        return GenericSystemAdapter(connection, self._session)
    
    async def execute_operation(self, system_name: str, operation: str, 
                              params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation on enterprise system with full protection."""
        if system_name not in self.adapters:
            raise ValueError(f"System {system_name} not registered")
        
        adapter = self.adapters[system_name]
        circuit_breaker = self.circuit_breakers[system_name]
        rate_limiter = self.rate_limiters[system_name]
        
        # Apply rate limiting
        if not await rate_limiter.acquire():
            raise RateLimitException(f"Rate limit exceeded for {system_name}")
        
        # Execute with circuit breaker protection
        try:
            async with circuit_breaker.call(system_name):
                start_time = time.time()
                result = await adapter.execute_operation(operation, params)
                execution_time = time.time() - start_time
                
                # Record metrics
                await self._record_metrics(system_name, operation, execution_time, True)
                
                return result
                
        except Exception as e:
            await self._record_metrics(system_name, operation, 0, False, str(e))
            raise
    
    async def _health_check_loop(self):
        """Continuous health checking for all registered systems."""
        while True:
            try:
                for system_name, adapter in self.adapters.items():
                    try:
                        health_status = await adapter.health_check()
                        health_status["checked_at"] = datetime.now().isoformat()
                        self.health_status[system_name] = health_status
                    except Exception as e:
                        self.health_status[system_name] = {
                            "healthy": False,
                            "error": str(e),
                            "checked_at": datetime.now().isoformat()
                        }
                
                # Wait before next health check cycle
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(5)
    
    async def _record_metrics(self, system_name: str, operation: str, 
                            execution_time: float, success: bool, error: str = None):
        """Record operation metrics for monitoring and analysis."""
        if system_name not in self.metrics:
            self.metrics[system_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "operations": {}
            }
        
        metrics = self.metrics[system_name]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
            # Update average response time
            metrics["avg_response_time"] = (
                (metrics["avg_response_time"] * (metrics["successful_requests"] - 1) + execution_time) /
                metrics["successful_requests"]
            )
        else:
            metrics["failed_requests"] += 1
        
        # Record operation-specific metrics
        if operation not in metrics["operations"]:
            metrics["operations"][operation] = {
                "count": 0,
                "success_count": 0,
                "avg_time": 0.0
            }
        
        op_metrics = metrics["operations"][operation]
        op_metrics["count"] += 1
        if success:
            op_metrics["success_count"] += 1
            op_metrics["avg_time"] = (
                (op_metrics["avg_time"] * (op_metrics["success_count"] - 1) + execution_time) /
                op_metrics["success_count"]
            )
    
    async def get_system_health(self, system_name: str = None) -> Dict[str, Any]:
        """Get health status for specific system or all systems."""
        if system_name:
            return self.health_status.get(system_name, {"error": "System not found"})
        return self.health_status
    
    async def get_metrics(self, system_name: str = None) -> Dict[str, Any]:
        """Get metrics for specific system or all systems."""
        if system_name:
            return self.metrics.get(system_name, {"error": "System not found"})
        return self.metrics
    
    async def shutdown(self):
        """Gracefully shutdown integration manager."""
        logger.info("Shutting down Enterprise Integration Manager")
        
        # Disconnect from all systems
        for system_name, adapter in self.adapters.items():
            try:
                await adapter.disconnect()
                logger.info(f"Disconnected from {system_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {system_name}: {e}")
        
        # Close HTTP session
        if self._session:
            await self._session.close()

class GenericSystemAdapter:
    """Generic adapter implementation for enterprise systems."""
    
    def __init__(self, connection: SystemConnection, session: aiohttp.ClientSession):
        self.connection = connection
        self.session = session
        self.authenticated = False
        self.auth_token = None
        self.auth_expires = None
    
    async def connect(self) -> bool:
        """Connect to the enterprise system."""
        try:
            return await self.authenticate(self.connection.credentials)
        except Exception as e:
            logger.error(f"Connection failed for {self.connection.system_name}: {e}")
            return False
    
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the enterprise system."""
        auth_method = self.connection.auth_method.lower()
        
        try:
            if auth_method == "oauth2":
                return await self._oauth2_auth(credentials)
            elif auth_method == "basic":
                return await self._basic_auth(credentials)
            elif auth_method == "api_key":
                return await self._api_key_auth(credentials)
            else:
                logger.warning(f"Unsupported auth method: {auth_method}")
                return False
        except Exception as e:
            logger.error(f"Authentication failed for {self.connection.system_name}: {e}")
            return False
    
    async def _oauth2_auth(self, credentials: Dict[str, Any]) -> bool:
        """OAuth 2.0 authentication implementation."""
        auth_url = f"{self.connection.endpoint}/oauth/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": credentials["client_id"],
            "client_secret": credentials["client_secret"]
        }
        
        async with self.session.post(auth_url, data=auth_data) as response:
            if response.status == 200:
                token_data = await response.json()
                self.auth_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.auth_expires = datetime.now() + timedelta(seconds=expires_in)
                self.authenticated = True
                return True
            else:
                logger.error(f"OAuth2 auth failed: {response.status}")
                return False
    
    async def _basic_auth(self, credentials: Dict[str, Any]) -> bool:
        """Basic authentication implementation."""
        # For basic auth, we just store credentials
        self.auth_token = {
            "username": credentials["username"],
            "password": credentials["password"]
        }
        self.authenticated = True
        return True
    
    async def _api_key_auth(self, credentials: Dict[str, Any]) -> bool:
        """API key authentication implementation."""
        self.auth_token = credentials["api_key"]
        self.authenticated = True
        return True
    
    async def execute_operation(self, operation: str, params: Dict[str, Any]) -> Any:
        """Execute operation on the enterprise system."""
        if not self.authenticated:
            if not await self.authenticate(self.connection.credentials):
                raise AuthenticationException("Authentication required")
        
        # Check token expiration for OAuth2
        if (self.auth_expires and datetime.now() >= self.auth_expires):
            if not await self.authenticate(self.connection.credentials):
                raise AuthenticationException("Token refresh failed")
        
        headers = self._get_auth_headers()
        url = f"{self.connection.endpoint}/{operation}"
        
        try:
            async with self.session.post(url, json=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    # Re-authenticate and retry
                    if await self.authenticate(self.connection.credentials):
                        async with self.session.post(url, json=params, headers=headers) as retry_response:
                            return await retry_response.json()
                    else:
                        raise AuthenticationException("Re-authentication failed")
                else:
                    error_text = await response.text()
                    raise OperationException(f"Operation failed: {response.status} - {error_text}")
        
        except aiohttp.ClientError as e:
            raise ConnectionException(f"Connection error: {e}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth method."""
        headers = {"Content-Type": "application/json"}
        
        if self.connection.auth_method.lower() == "oauth2":
            headers["Authorization"] = f"Bearer {self.auth_token}"
        elif self.connection.auth_method.lower() == "api_key":
            headers["X-API-Key"] = self.auth_token
        elif self.connection.auth_method.lower() == "basic":
            import base64
            creds = f"{self.auth_token['username']}:{self.auth_token['password']}"
            encoded_creds = base64.b64encode(creds.encode()).decode()
            headers["Authorization"] = f"Basic {encoded_creds}"
        
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the enterprise system."""
        try:
            health_endpoint = self.connection.health_check.get("endpoint", "/health")
            url = f"{self.connection.endpoint}{health_endpoint}"
            timeout = self.connection.health_check.get("timeout_seconds", 5)
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                if response.status == 200:
                    return {
                        "healthy": True,
                        "status_code": response.status,
                        "response_time_ms": response.headers.get("X-Response-Time", "unknown")
                    }
                else:
                    return {
                        "healthy": False,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def disconnect(self) -> bool:
        """Disconnect from the enterprise system."""
        self.authenticated = False
        self.auth_token = None
        self.auth_expires = None
        return True

# Custom exceptions
class AuthenticationException(Exception):
    """Raised when authentication fails."""
    pass

class OperationException(Exception):
    """Raised when operation execution fails."""
    pass

class ConnectionException(Exception):
    """Raised when connection to system fails."""
    pass

class RateLimitException(Exception):
    """Raised when rate limit is exceeded."""
    pass

# Example usage and configuration
async def demo_enterprise_integration():
    """Demonstrate enterprise integration patterns."""
    
    # Example configuration for multiple enterprise systems
    config = {
        "systems": {
            "sap_erp": {
                "type": "erp",
                "endpoint": "https://sap.company.com/api",
                "auth_method": "oauth2",
                "credentials": {
                    "client_id": "sap_client",
                    "client_secret": "sap_secret"
                },
                "rate_limits": {
                    "requests_per_second": 5,
                    "burst_size": 10
                },
                "circuit_breaker": {
                    "failure_threshold": 3,
                    "recovery_timeout": 60
                }
            },
            "salesforce_crm": {
                "type": "crm",
                "endpoint": "https://company.salesforce.com/services/data/v58.0",
                "auth_method": "oauth2",
                "credentials": {
                    "client_id": "sf_client",
                    "client_secret": "sf_secret"
                }
            },
            "postgres_db": {
                "type": "database",
                "endpoint": "postgresql://localhost:5432/company_db",
                "auth_method": "basic",
                "credentials": {
                    "username": "db_user",
                    "password": "db_password"
                }
            }
        }
    }
    
    # Initialize integration manager
    integration_manager = EnterpriseIntegrationManager(config)
    await integration_manager.initialize()
    
    try:
        # Example operations
        print("\n=== Enterprise Integration Demo ===")
        
        # Get system health
        health = await integration_manager.get_system_health()
        print(f"System Health Status: {json.dumps(health, indent=2)}")
        
        # Execute operations on different systems
        try:
            result = await integration_manager.execute_operation(
                "sap_erp", 
                "get_customer_data",
                {"customer_id": "CUST001"}
            )
            print(f"SAP ERP Result: {result}")
        except Exception as e:
            print(f"SAP ERP Error: {e}")
        
        # Get metrics
        metrics = await integration_manager.get_metrics()
        print(f"Integration Metrics: {json.dumps(metrics, indent=2)}")
        
    finally:
        await integration_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(demo_enterprise_integration())
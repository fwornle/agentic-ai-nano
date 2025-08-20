# Session 5 - Module B: Enterprise PydanticAI (70 minutes)

**Prerequisites**: [Session 5 Core Section Complete](Session5_PydanticAI_Type_Safe_Agents.md)  
**Target Audience**: Production system builders  
**Cognitive Load**: 7 production concepts

---

## Module Overview

This module focuses on enterprise-grade PydanticAI deployment patterns, including dependency injection, scalable architectures, monitoring, and production deployment strategies. You'll learn to build robust, maintainable agent systems for enterprise environments.

### Learning Objectives
By the end of this module, you will:
- Implement dependency injection for clean architecture
- Build scalable agent systems with proper monitoring
- Deploy production-ready PydanticAI applications
- Create enterprise integration patterns
- Monitor and optimize agent performance

---

## Part 1: Dependency Injection & Architecture (25 minutes)

### Dependency Injection for Testing and Production

PydanticAI's dependency injection system enables clean separation between testing and production configurations, supporting eval-driven iterative development and robust production dependency management.

🗂️ **File**: `src/session5/dependency_injection.py` - Complete dependency injection system

### Service Interface Protocols

Protocols define the contracts that all service implementations must follow, enabling seamless switching between production and test implementations.

```python
# Essential imports for dependency injection
from pydantic_ai.dependencies import DependencyProvider, Injectable, Scope
from typing import Protocol, runtime_checkable, Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager
import asyncio
import logging
import uuid
```

Now we define service interface protocols for type-safe dependency injection:

```python
# Service interface definitions using Protocol pattern
@runtime_checkable
class DatabaseService(Protocol):
    """Protocol for database operations with type safety."""
    async def save_result(self, result_data: Dict[str, Any]) -> str: ...
    async def get_result(self, result_id: str) -> Optional[Dict[str, Any]]: ...
    async def health_check(self) -> bool: ...

@runtime_checkable  
class ExternalAPIService(Protocol):
    """Protocol for external API integrations."""
    async def fetch_data(self, query: str) -> Dict[str, Any]: ...
    async def validate_source(self, source_url: str) -> bool: ...
```

Finally, we add the cache service protocol:

```python
@runtime_checkable
class CacheService(Protocol):
    """Protocol for caching operations with TTL support."""
    async def get(self, key: str) -> Optional[Any]: ...
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None: ...
    async def invalidate(self, pattern: str) -> int: ...
```

The `@runtime_checkable` decorator allows isinstance() checks at runtime, ensuring type safety in dependency injection.

### Production Service Implementations

Production services provide real connectivity with proper error handling, connection pooling, and monitoring.

```python
# Production database implementation with connection pooling
class ProductionDatabaseService:
    """Production database service with connection pool management."""
    
    def __init__(self, connection_string: str, pool_size: int = 10):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self._connection_pool = None
    
    async def initialize(self):
        """Initialize database connection pool for production use."""
        # In real implementation, this would create actual connection pool
        self._connection_pool = f"ConnectionPool({self.connection_string}, size={self.pool_size})"
        logging.info(f"Database service initialized: {self._connection_pool}")
```

Now we implement the core database operations with proper error handling:

```python
    async def save_result(self, result_data: Dict[str, Any]) -> str:
        """Save agent result to production database with transaction safety."""
        # In production, this would use proper database transactions
        result_id = str(uuid.uuid4())
        logging.info(f"Saved result {result_id} to database")
        return result_id
    
    async def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve result from production database with error handling."""
        # Production implementation would include proper error handling
        logging.info(f"Retrieved result {result_id} from database")
        return {"id": result_id, "status": "found"}
    
    async def health_check(self) -> bool:
        """Monitor database connection health for production systems."""
        return self._connection_pool is not None
```

### Test Service Implementations

Test implementations provide predictable behavior and call tracking for comprehensive testing without external dependencies.

```python
# Test database service with in-memory storage and call tracking
class TestDatabaseService:
    """Test database service with in-memory storage and comprehensive logging."""
    
    def __init__(self):
        self.data_store = {}  # In-memory storage for test data
        self.call_log = []    # Track all method calls for verification
    
    async def initialize(self):
        """Initialize test database - always succeeds for testing."""
        logging.info("Test database service initialized")
    
    async def save_result(self, result_data: Dict[str, Any]) -> str:
        """Save result to in-memory store with predictable IDs."""
        result_id = f"test_{len(self.data_store)}"
        self.data_store[result_id] = result_data
        self.call_log.append(("save", result_id, result_data))
        return result_id
```

Now we add retrieval and health check methods with call tracking:

```python
    async def get_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve result from in-memory store with call logging."""
        self.call_log.append(("get", result_id))
        return self.data_store.get(result_id)
    
    async def health_check(self) -> bool:
        """Test database is always healthy for consistent testing."""
        return True
    
    def get_call_log(self) -> List[tuple]:
        """Get complete log of service calls for test verification."""
        return self.call_log.copy()
```

### Dependency Injection Container

The dependency container manages service lifecycles, registration, and resolution with support for singletons and scoped services.

```python
# Advanced dependency injection container with lifecycle management
class DependencyContainer:
    """Enterprise-grade dependency injection container with full lifecycle support."""
    
    def __init__(self):
        self.services = {}              # Active service instances
        self.factories = {}             # Service factory functions
        self.singletons = {}           # Singleton service instances
        self.scoped_services = {}      # Scoped service definitions
        self.initialization_order = [] # Service initialization sequence
    
    def register_singleton(
        self, 
        interface: Type, 
        implementation: Type, 
        *args, 
        **kwargs
    ) -> None:
        """Register a singleton service that lives for the container lifetime."""
        self.factories[interface] = lambda: implementation(*args, **kwargs)
        self.initialization_order.append(interface)
```

Now we implement the service resolution with proper lifecycle management:

```python
    async def get_service(self, interface: Type, scope: str = "default") -> Any:
        """Resolve service instance with proper initialization and lifecycle management."""
        
        # Check existing singletons first for performance
        if interface in self.singletons:
            return self.singletons[interface]
        
        # Create and cache singleton instances
        if interface in self.factories:
            instance = self.factories[interface]()
            if hasattr(instance, 'initialize'):
                await instance.initialize()
            self.singletons[interface] = instance
            return instance
        
        raise ValueError(f"No registration found for {interface}")
```

---

## Part 2: Scalability & Performance (25 minutes)

### Production Agent Architecture

🗂️ **File**: `src/session5/production_agents.py` - Scalable agent implementations

Production PydanticAI applications require robust architecture patterns that handle concurrency, error recovery, and monitoring at scale.

```python
# Production-ready agent patterns and architectures
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Protocol, runtime_checkable
from contextlib import asynccontextmanager
import logging
from abc import ABC, abstractmethod

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_production.log')
    ]
)
```

### Agent Metrics and Monitoring

Comprehensive metrics tracking enables monitoring and optimization of agent performance in production environments.

```python
class AgentMetrics(BaseModel):
    """Comprehensive agent metrics for monitoring."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0
    last_request_timestamp: Optional[datetime] = None
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    
    @property
    def success_rate_percent(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100.0
```

### Production Agent Base Class

The production agent base class provides all necessary infrastructure for enterprise deployment including metrics, health checks, and error handling.

```python
class ProductionAgentBase(ABC):
    """Abstract base class for production-ready agents."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
        self.metrics = AgentMetrics()
        self.start_time = datetime.now(timezone.utc)
        self._request_times: List[float] = []
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._health_status = "healthy"
```

Now we define the abstract interface that all production agents must implement:

```python
    @abstractmethod
    async def _process_core_request(self, request: BaseModel) -> BaseModel:
        """Core request processing logic - must be implemented by subclasses."""
        pass
```

### Request Processing with Monitoring

Request processing includes comprehensive monitoring, error handling, and performance tracking for production reliability.

```python
    async def process_request(self, request: BaseModel) -> BaseModel:
        """Process request with full monitoring and error handling."""
        start_time = time.time()
        self.metrics.total_requests += 1
        
        try:
            # Update metrics
            self.metrics.last_request_timestamp = datetime.now(timezone.utc)
            
            # Process the request
            result = await self._process_core_request(request)
            
            # Track success
            self.metrics.successful_requests += 1
            self._health_status = "healthy"
            
            return result
```

Now we handle errors and track performance metrics in the exception handler:

```python
        except Exception as e:
            # Track failure
            self.metrics.failed_requests += 1
            self._health_status = "degraded"
            self.logger.error(f"Request processing failed: {e}")
            raise
            
        finally:
            # Track timing
            request_time = (time.time() - start_time) * 1000
            self._request_times.append(request_time)
            self._update_timing_metrics()
```

### Concurrent Request Processing

Production agents support concurrent request processing with proper resource management and backpressure handling.

```python
    async def process_batch(self, requests: List[BaseModel]) -> List[BaseModel]:
        """Process multiple requests concurrently with resource management."""
        
        # Limit concurrent requests to prevent resource exhaustion
        semaphore = asyncio.Semaphore(self.config.get('max_concurrent_requests', 10))
        
        async def process_with_semaphore(request):
            async with semaphore:
                return await self.process_request(request)
        
        # Execute all requests concurrently
        tasks = [process_with_semaphore(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful results from exceptions
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Batch processing error: {result}")
            else:
                successful_results.append(result)
        
        return successful_results
```

### Health Monitoring and Circuit Breaker

Health monitoring and circuit breaker patterns prevent cascading failures in production environments.

```python
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for monitoring systems."""
        uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()
        self.metrics.uptime_seconds = uptime
        
        # Check memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.metrics.memory_usage_mb = memory_mb
        
        return {
            "status": self._health_status,
            "uptime_seconds": uptime,
            "memory_mb": memory_mb,
            "success_rate": self.metrics.success_rate_percent,
            "total_requests": self.metrics.total_requests,
            "avg_response_time_ms": self.metrics.average_response_time_ms
        }
```

---

## Part 3: Security & Compliance (20 minutes)

### Enterprise Security Patterns

🗂️ **File**: `src/session5/security.py` - Enterprise security implementations

Enterprise PydanticAI applications require comprehensive security patterns including authentication, authorization, data privacy, and audit logging.

```python
# Enterprise security patterns for PydanticAI
import jwt
import hashlib
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from enum import Enum
import logging
```

Now we define the security configuration model for enterprise deployments:

```python
class SecurityConfig(BaseModel):
    """Security configuration for enterprise deployments."""
    
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_expiration_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week
    api_rate_limit_per_minute: int = Field(default=100, ge=1)
    enable_audit_logging: bool = Field(default=True)
    allowed_origins: List[str] = Field(default_factory=list)
    require_https: bool = Field(default=True)
```

### Authentication and Authorization

Comprehensive authentication and authorization system for enterprise agent access control.

```python
class UserRole(str, Enum):
    """User roles for role-based access control."""
    ADMIN = "admin"
    AGENT_OPERATOR = "agent_operator"
    DATA_ANALYST = "data_analyst"
    READ_ONLY = "read_only"

class AuthenticationService:
    """Enterprise authentication service with JWT tokens."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
```

Next, we implement JWT token creation with proper security and expiration:

```python
    def create_access_token(self, user_id: str, roles: List[UserRole]) -> str:
        """Create JWT access token with user information and roles."""
        now = datetime.now(timezone.utc)
        payload = {
            "user_id": user_id,
            "roles": [role.value for role in roles],
            "iat": now,
            "exp": now + timedelta(hours=self.config.jwt_expiration_hours),
            "iss": "pydantic-ai-enterprise"
        }
        
        token = jwt.encode(payload, self.config.jwt_secret_key, algorithm="HS256")
        self.logger.info(f"Created access token for user {user_id}")
        return token
```

Finally, we add secure token verification with proper error handling:

```python
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return user information."""
        try:
            payload = jwt.decode(
                token, 
                self.config.jwt_secret_key, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token verification failed: expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token verification failed: invalid")
            return None
```

### Data Privacy and Compliance

Data privacy patterns ensure compliance with regulations like GDPR, HIPAA, and other enterprise requirements.

```python
class DataPrivacyService:
    """Data privacy and compliance service for sensitive data handling."""
    
    def __init__(self, encryption_key: str):
        self.encryption_key = encryption_key.encode()
        self.logger = logging.getLogger(__name__)
    
    def anonymize_user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive user data while preserving utility."""
        anonymized = data.copy()
        
        # Hash personally identifiable information
        if 'email' in anonymized:
            anonymized['email_hash'] = self._hash_pii(anonymized.pop('email'))
        
        if 'user_id' in anonymized:
            anonymized['user_hash'] = self._hash_pii(anonymized.pop('user_id'))
```

Now we remove sensitive fields and provide PII hashing for anonymization:

```python
        # Remove sensitive fields
        sensitive_fields = ['ssn', 'phone', 'address', 'credit_card']
        for field in sensitive_fields:
            if field in anonymized:
                del anonymized[field]
        
        return anonymized
    
    def _hash_pii(self, data: str) -> str:
        """Hash personally identifiable information for anonymization."""
        # Use salt for additional security
        salt = b"pydantic_ai_salt"
        return hashlib.sha256(salt + data.encode()).hexdigest()[:16]
```

### Audit Logging System

Comprehensive audit logging tracks all agent operations for compliance and security monitoring.

```python
class AuditLogger:
    """Enterprise audit logging for compliance and security monitoring."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.audit_logger = logging.getLogger("audit")
        
        # Configure audit-specific handler
        audit_handler = logging.FileHandler("audit.log")
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.setLevel(logging.INFO)
```

Now we implement the core audit logging functionality:

```python
    def log_agent_request(
        self, 
        user_id: str, 
        agent_name: str, 
        request_data: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Log agent request for audit trail."""
        if not self.config.enable_audit_logging:
            return
        
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "agent_request",
            "user_id": user_id,
            "agent_name": agent_name,
            "request_size_bytes": len(str(request_data)),
            "success": error is None,
            "error_message": error
        }
        
        self.audit_logger.info(f"AGENT_REQUEST: {audit_entry}")
```

---

## Module Summary

You've now mastered enterprise PydanticAI patterns, including:

✅ **Dependency Injection**: Built clean, testable architecture with service protocols  
✅ **Production Scalability**: Implemented monitoring, metrics, and concurrent processing  
✅ **Enterprise Security**: Created authentication, authorization, and compliance systems  
✅ **Audit & Monitoring**: Built comprehensive logging and health monitoring

---

## 📝 Multiple Choice Test - Module B

Test your understanding of enterprise PydanticAI patterns and production systems:

**Question 1:** What design pattern does the dependency injection system use for service management?
A) Singleton pattern with global state  
B) Protocol-based interfaces with container-managed lifecycles  
C) Static factory methods only  
D) Direct class instantiation  

**Question 2:** How does the ProductionAgent handle concurrent request processing?
A) Sequential processing only  
B) Semaphore-controlled concurrency with configurable limits and performance tracking  
C) Unlimited concurrent execution  
D) Single-threaded execution with queuing  

**Question 3:** What security measures does the EnterpriseSecurityAgent implement for authentication?
A) Simple password checking  
B) JWT token validation, role-based authorization, and audit logging  
C) Basic username verification  
D) No authentication required  

**Question 4:** What information does the comprehensive audit logging system capture?
A) Only request timestamps  
B) Complete request/response tracking with user context, performance metrics, and error details  
C) Simple success/failure flags  
D) Database query logs only  

**Question 5:** How does the health monitoring system track service dependencies?
A) Manual status checks only  
B) Automated dependency health checks with circuit breaker integration and alert generation  
C) Simple ping tests  
D) Log file analysis only  

[**🗂️ View Test Solutions →**](Session5_ModuleB_Test_Solutions.md)

### Next Steps
- **Continue to Module C**: [Custom Validation Systems](Session5_ModuleC_Custom_Validation_Systems.md) for specialized validation patterns
- **Continue to Module D**: [Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md) for comprehensive testing strategies
- **Return to Core**: [Session 5 Main](Session5_PydanticAI_Type_Safe_Agents.md)
- **Advance to Session 6**: [Atomic Agents](Session6_Atomic_Agents_Modular_Architecture.md)

---

**🗂️ Source Files for Module B:**
- `src/session5/dependency_injection.py` - Complete DI system
- `src/session5/production_agents.py` - Scalable agent patterns  
- `src/session5/security.py` - Enterprise security implementations
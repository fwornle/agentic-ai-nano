# Session 5 - Module C: Custom Validation Systems

**Prerequisites**: [Session 5 Core Section Complete](Session5_PydanticAI_Type_Safe_Agents.md)

## Module Overview

Custom validation systems for specialized business domains, industry-specific validation rules, and comprehensive error management. Build sophisticated error handling with intelligent retry strategies, circuit breaker patterns, and resilient external service integrations.

---

## Part 1: Comprehensive Error Management

### Advanced Error Handling Architecture

🗂️ **File**: `src/session5/error_management.py` - Complete error handling system

Production PydanticAI applications require sophisticated error handling strategies that maintain system stability while providing meaningful feedback.

```python
# Advanced error handling and recovery patterns
from enum import Enum
from typing import Callable, Awaitable, TypeVar, Union, Dict, Any
import asyncio
from functools import wraps
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import logging

T = TypeVar('T')
R = TypeVar('R')
```

### Error Classification System

The error classification system provides structured categories and severity levels for consistent error handling across the application.

```python
class ErrorSeverity(str, Enum):
    """Error severity levels for classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for systematic handling."""
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    EXTERNAL_SERVICE = "external_service"
    DATA_CORRUPTION = "data_corruption"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"
```

### Comprehensive Error Context

The ErrorContext class captures comprehensive error information including timing, categorization, retry logic, and user-friendly messaging.

```python
@dataclass
class ErrorContext:
    """Comprehensive error context for debugging and monitoring."""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    retry_count: int = 0
    max_retries: int = 3
    recoverable: bool = True
    user_facing_message: str = ""
```

Now we add the dictionary conversion method for logging and monitoring:

```python
    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for logging."""
        return {
            'error_id': self.error_id,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.value,
            'severity': self.severity.value,
            'message': self.message,
            'details': self.details,
            'stack_trace': self.stack_trace,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'recoverable': self.recoverable,
            'user_facing_message': self.user_facing_message
        }
```

### Custom Agent Exception Classes

Specialized exception classes provide structured error information for different failure scenarios.

```python
class AgentError(Exception):
    """Base exception class for agent-specific errors."""
    
    def __init__(self, message: str, context: ErrorContext = None, cause: Exception = None):
        super().__init__(message)
        self.context = context or ErrorContext()
        self.context.message = message
        self.context.stack_trace = traceback.format_exc()
        self.__cause__ = cause
```

Now we define specialized error classes for different types of failures:

```python
class ValidationAgentError(AgentError):
    """Error specific to validation failures."""
    
    def __init__(self, message: str, field: str = None, value: Any = None, **kwargs):
        context = ErrorContext(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            details={'field': field, 'invalid_value': value}
        )
        super().__init__(message, context, **kwargs)

class NetworkAgentError(AgentError):
    """Error specific to network operations."""
    
    def __init__(self, message: str, endpoint: str = None, status_code: int = None, **kwargs):
        context = ErrorContext(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            details={'endpoint': endpoint, 'status_code': status_code}
        )
        super().__init__(message, context, **kwargs)
```

### Error Classification Engine

The error classifier analyzes exception types and error messages to automatically categorize errors for appropriate handling strategies.

```python
class ErrorClassifier:
    """Classifies and categorizes errors for appropriate handling."""
    
    def __init__(self):
        self.classification_rules = {
            # Validation errors
            (ValueError, TypeError): (ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM),
            (ValidationError,): (ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM),
            
            # Network errors
            (ConnectionError, ConnectionRefusedError, ConnectionResetError): (ErrorCategory.NETWORK, ErrorSeverity.HIGH),
            (TimeoutError, asyncio.TimeoutError): (ErrorCategory.TIMEOUT, ErrorSeverity.HIGH),
            
            # Resource errors
            (MemoryError,): (ErrorCategory.RESOURCE_EXHAUSTION, ErrorSeverity.CRITICAL),
            (OSError,): (ErrorCategory.CONFIGURATION, ErrorSeverity.HIGH),
            
            # Permission errors  
            (PermissionError,): (ErrorCategory.PERMISSION, ErrorSeverity.HIGH),
        }
```

Now we implement the intelligent error classification logic:

```python
    def classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify an error into category and severity."""
        
        error_type = type(error)
        
        # Check direct matches first
        for error_types, (category, severity) in self.classification_rules.items():
            if error_type in error_types:
                return category, severity
        
        # Analyze error message for additional clues
        error_message = str(error).lower()
        
        if any(word in error_message for word in ['timeout', 'deadline', 'expired']):
            return ErrorCategory.TIMEOUT, ErrorSeverity.HIGH
        elif any(word in error_message for word in ['network', 'connection', 'socket']):
            return ErrorCategory.NETWORK, ErrorSeverity.HIGH
        elif any(word in error_message for word in ['rate limit', 'throttle', 'quota']):
            return ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
```

---

## Part 2: Intelligent Retry Strategies

### Retry Strategy Configuration

🗂️ **File**: `src/session5/retry_strategies.py` - Intelligent retry implementations

Intelligent retry strategies prevent cascade failures and provide resilient error recovery patterns essential for production agent systems.

```python
class RetryStrategy:
    """Configurable retry strategies for error recovery."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, backoff_multiplier: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_multiplier = backoff_multiplier
        self.retryable_categories = {
            ErrorCategory.NETWORK,
            ErrorCategory.TIMEOUT,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.EXTERNAL_SERVICE
        }
```

Next, we implement intelligent retry decision logic:

```python
    def should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if error should be retried."""
        
        if error_context.retry_count >= self.max_retries:
            return False
        
        if not error_context.recoverable:
            return False
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            return False
        
        return error_context.category in self.retryable_categories
    
    def calculate_delay(self, retry_count: int) -> float:
        """Calculate delay before next retry attempt using exponential backoff."""
        return self.base_delay * (self.backoff_multiplier ** retry_count)
```

### Retry Execution Framework

The core retry execution engine attempts function calls, classifies errors, makes retry decisions, and implements backoff delays for resilient agent operations.

```python
    async def execute_with_retry(
        self, 
        func: Callable[..., Awaitable[T]], 
        *args, 
        **kwargs
    ) -> T:
        """Execute function with retry logic."""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
                
            except Exception as e:
                classifier = ErrorClassifier()
                category, severity = classifier.classify_error(e)
                
                error_context = ErrorContext(
                    category=category,
                    severity=severity,
                    message=str(e),
                    retry_count=attempt,
                    max_retries=self.max_retries
                )
```

Now we handle retry logic and delay calculation:

```python
                last_error = AgentError(str(e), error_context, e)
                
                if not self.should_retry(error_context):
                    break
                
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    logging.info(f"Retrying after {delay}s (attempt {attempt + 1}/{self.max_retries + 1})")
                    await asyncio.sleep(delay)
        
        if last_error:
            raise last_error
        
        raise AgentError("Maximum retries exceeded")
```

### Error Handler Decorator

This decorator provides a clean interface for applying error handling and retry strategies to any agent function with declarative configuration.

```python
def error_handler(
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    retry_strategy: RetryStrategy = None,
    user_message: str = None
):
    """Decorator for comprehensive error handling."""
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                if retry_strategy:
                    return await retry_strategy.execute_with_retry(func, *args, **kwargs)
                else:
                    return await func(*args, **kwargs)
                    
            except AgentError:
                # Re-raise AgentErrors with their existing context
                raise
```

Now we handle generic exceptions and wrap them appropriately:

```python
            except Exception as e:
                # Wrap other exceptions in AgentError
                classifier = ErrorClassifier()
                error_category, error_severity = classifier.classify_error(e)
                
                context = ErrorContext(
                    category=error_category if error_category != ErrorCategory.UNKNOWN else category,
                    severity=error_severity if error_severity != ErrorSeverity.MEDIUM else severity,
                    message=str(e),
                    user_facing_message=user_message or "An error occurred while processing your request"
                )
                
                raise AgentError(str(e), context, e)
        
        return wrapper
    return decorator
```

---

## Part 3: Circuit Breaker Pattern

### Circuit Breaker Implementation

🗂️ **File**: `src/session5/circuit_breaker.py` - Circuit breaker for service resilience

Circuit breaker state management prevents cascade failures by isolating failing services and providing automatic recovery mechanisms.

```python
class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, requests blocked
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout_seconds: float = 60.0
    success_threshold: int = 3
    timeout_seconds: float = 30.0

class CircuitBreaker:
    """Circuit breaker implementation for resilient external service calls."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"CircuitBreaker.{name}")
```

### Protected Function Execution

The core circuit breaker protection logic blocks calls when the circuit is open and manages state transitions during recovery attempts.

```python
    async def call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute function call with circuit breaker protection."""
        
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
            else:
                raise AgentError(
                    f"Circuit breaker {self.name} is OPEN",
                    ErrorContext(
                        category=ErrorCategory.EXTERNAL_SERVICE,
                        severity=ErrorSeverity.HIGH,
                        message="Service unavailable due to repeated failures"
                    )
                )
```

Now we execute the protected function call with timeout and error handling:

```python
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout_seconds
            )
            
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise
```

### Intelligent State Management

Automatic state management ensures services can recover gracefully while protecting against premature recovery attempts that could overwhelm failing services.

```python
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if not self.last_failure_time:
            return True
        
        time_since_failure = datetime.now(timezone.utc) - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.recovery_timeout_seconds
    
    async def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                self.logger.info(f"Circuit breaker {self.name} CLOSED after successful recovery")
```

Next, we handle failure scenarios and state transitions:

```python
    async def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0
            self.logger.warning(f"Circuit breaker {self.name} OPEN after failure during recovery")
        
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker {self.name} OPEN after {self.failure_count} failures")
```

### External Service Integration

A consistent base class ensures all external service integrations follow the same resilience patterns and monitoring standards.

```python
# Integration patterns for external services
class ExternalServiceIntegration:
    """Base class for external service integrations with comprehensive error handling."""
    
    def __init__(self, service_name: str, base_url: str, circuit_breaker_config: CircuitBreakerConfig = None):
        self.service_name = service_name
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker(service_name, circuit_breaker_config)
        self.retry_strategy = RetryStrategy(max_retries=3, base_delay=1.0)
        self.logger = logging.getLogger(f"Integration.{service_name}")
```

Now we implement the HTTP request method with comprehensive error handling:

```python
    @error_handler(
        category=ErrorCategory.EXTERNAL_SERVICE,
        severity=ErrorSeverity.HIGH,
        user_message="External service temporarily unavailable"
    )
    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with comprehensive error handling."""
        
        async def _make_http_request():
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Simulate various failure scenarios for testing
            import random
            if random.random() < 0.1:  # 10% chance of failure
                raise NetworkAgentError(
                    "Simulated network error",
                    endpoint=url,
                    status_code=503
                )
```

Finally, we return the successful response through the circuit breaker:

```python
            # Simulate successful response
            return {
                'success': True,
                'data': {'message': f'Success from {self.service_name}', 'endpoint': endpoint},
                'status_code': 200,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        return await self.circuit_breaker.call(_make_http_request)
```

---

## Module Summary

You've now mastered custom validation systems and resilient error handling, including:

✅ **Comprehensive Error Management**: Built sophisticated error classification and context tracking  
✅ **Intelligent Retry Strategies**: Implemented exponential backoff with smart retry decisions  
✅ **Circuit Breaker Patterns**: Created resilient service protection with automatic recovery  
✅ **External Service Integration**: Built robust integration patterns with comprehensive error handling

---

## 📝 Multiple Choice Test - Module C

Test your understanding of custom validation systems and error handling:

**Question 1:** How does the ErrorManager classify different types of validation errors?
A) By timestamp only  
B) By error type, severity level, context, and metadata tracking  
C) Simple binary classification  
D) Random categorization  

**Question 2:** What retry strategy does the RetryHandler implement for exponential backoff?
A) Fixed 1-second intervals  
B) Linear increase only  
C) Exponential backoff with jitter and maximum retry limits  
D) Random retry intervals  

**Question 3:** When does the CircuitBreaker transition from CLOSED to OPEN state?
A) After any single failure  
B) When failure count exceeds threshold within time window  
C) At random intervals  
D) Only when manually triggered  

**Question 4:** What information does the error context include for comprehensive tracking?
A) Just the error message  
B) Full context with operation, agent_id, error details, and metadata  
C) Only error codes  
D) Simple boolean flags  

**Question 5:** How long does the CircuitBreaker stay in HALF_OPEN state before making a transition decision?
A) 10 seconds  
B) Until 3 consecutive test requests succeed or fail  
C) Indefinitely  
D) 1 minute exactly  

[**🗂️ View Test Solutions →**](Session5_ModuleC_Test_Solutions.md)

### Next Steps
- **Continue to Module D**: [Testing & Benchmarking](Session5_ModuleD_Testing_Benchmarking.md) for comprehensive testing strategies
- **Return to Core**: [Session 5 Main](Session5_PydanticAI_Type_Safe_Agents.md)
- **Advance to Session 6**: [Atomic Agents](Session6_Atomic_Agents_Modular_Architecture.md)

---

**🗂️ Source Files for Module C:**
- `src/session5/error_management.py` - Complete error handling system
- `src/session5/retry_strategies.py` - Intelligent retry implementations
- `src/session5/circuit_breaker.py` - Circuit breaker for service resilience
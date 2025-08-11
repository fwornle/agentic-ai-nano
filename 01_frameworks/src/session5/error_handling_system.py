# src/session5/error_handling_system.py
"""
Comprehensive error handling system with circuit breakers, retry mechanisms, and error recovery.
Implements production-grade error management patterns for PydanticAI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Type, TypeVar, Generic, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import functools
import traceback
import json
from dataclasses import dataclass
import random
import time
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(str, Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE = "resource"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UNKNOWN = "unknown"

class RecoveryStrategy(str, Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAIL_FAST = "fail_fast"
    IGNORE = "ignore"

class CircuitBreakerState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

# Error models

class ErrorContext(BaseModel):
    """Context information for error handling."""
    request_id: str = Field(..., description="Request identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    operation: str = Field(..., description="Operation being performed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorDetails(BaseModel):
    """Detailed error information."""
    error_id: str = Field(..., description="Unique error identifier")
    error_type: str = Field(..., description="Error type/class name")
    error_message: str = Field(..., description="Human-readable error message")
    severity: ErrorSeverity = Field(..., description="Error severity level")
    category: ErrorCategory = Field(..., description="Error category")
    context: ErrorContext = Field(..., description="Error context")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    recovery_suggestions: List[str] = Field(default_factory=list, description="Recovery suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional error data")
    timestamp: datetime = Field(default_factory=datetime.now)

class RetryConfig(BaseModel):
    """Configuration for retry mechanisms."""
    max_attempts: int = Field(default=3, ge=1, description="Maximum retry attempts")
    base_delay: float = Field(default=1.0, gt=0, description="Base delay between retries")
    max_delay: float = Field(default=60.0, gt=0, description="Maximum delay between retries")
    exponential_backoff: bool = Field(default=True, description="Use exponential backoff")
    jitter: bool = Field(default=True, description="Add random jitter")
    retry_on: List[Type[Exception]] = Field(
        default_factory=lambda: [Exception], 
        description="Exception types to retry on"
    )
    
    class Config:
        arbitrary_types_allowed = True

class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker."""
    failure_threshold: int = Field(default=5, ge=1, description="Failures before opening")
    recovery_timeout: int = Field(default=60, ge=1, description="Seconds before attempting recovery")
    success_threshold: int = Field(default=2, ge=1, description="Successes needed to close")
    timeout_seconds: float = Field(default=10.0, gt=0, description="Operation timeout")

# Exception hierarchy

class AgentError(Exception):
    """Base exception for agent errors."""
    
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, metadata: Optional[Dict] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

class ValidationError(AgentError):
    """Validation error."""
    
    def __init__(self, message: str, field_path: Optional[str] = None, **kwargs):
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)
        self.field_path = field_path

class NetworkError(AgentError):
    """Network-related error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.NETWORK, ErrorSeverity.HIGH, **kwargs)

class TimeoutError(AgentError):
    """Timeout error."""
    
    def __init__(self, message: str, timeout_seconds: float, **kwargs):
        super().__init__(message, ErrorCategory.TIMEOUT, ErrorSeverity.HIGH, **kwargs)
        self.timeout_seconds = timeout_seconds

class AuthenticationError(AgentError):
    """Authentication error."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, **kwargs)

class ResourceError(AgentError):
    """Resource-related error (memory, disk, etc.)."""
    
    def __init__(self, message: str, resource_type: str, **kwargs):
        super().__init__(message, ErrorCategory.RESOURCE, ErrorSeverity.CRITICAL, **kwargs)
        self.resource_type = resource_type

# Error handler interface

class ErrorHandler(ABC):
    """Abstract base class for error handlers."""
    
    @abstractmethod
    async def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext
    ) -> Optional[Any]:
        """Handle an error and optionally return a recovery result."""
        pass
    
    @abstractmethod
    def can_handle(self, error: Exception) -> bool:
        """Check if this handler can handle the given error."""
        pass

# Concrete error handlers

class RetryHandler(ErrorHandler):
    """Handles errors with retry logic."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__ + ".RetryHandler")
    
    def can_handle(self, error: Exception) -> bool:
        """Check if error type should be retried."""
        return any(isinstance(error, exc_type) for exc_type in self.config.retry_on)
    
    async def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext
    ) -> Optional[Any]:
        """Handle error with retry logic."""
        # This would typically retry the original operation
        # For demo purposes, we'll simulate retry logic
        
        for attempt in range(self.config.max_attempts):
            delay = self._calculate_delay(attempt)
            
            self.logger.info(
                f"Retry attempt {attempt + 1}/{self.config.max_attempts} "
                f"for {context.operation} (delay: {delay:.2f}s)"
            )
            
            await asyncio.sleep(delay)
            
            # Simulate retry (in real implementation, would re-execute original operation)
            if random.random() > 0.7:  # 30% success rate for demo
                self.logger.info(f"Retry successful for {context.operation}")
                return f"Retry successful after {attempt + 1} attempts"
        
        self.logger.error(f"All retries failed for {context.operation}")
        return None
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        if self.config.exponential_backoff:
            delay = self.config.base_delay * (2 ** attempt)
        else:
            delay = self.config.base_delay
        
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay

class FallbackHandler(ErrorHandler):
    """Handles errors with fallback responses."""
    
    def __init__(self, fallback_responses: Dict[str, Any]):
        self.fallback_responses = fallback_responses
        self.logger = logging.getLogger(__name__ + ".FallbackHandler")
    
    def can_handle(self, error: Exception) -> bool:
        """Can handle any error with fallback."""
        return True
    
    async def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext
    ) -> Optional[Any]:
        """Handle error with fallback response."""
        operation = context.operation
        
        if operation in self.fallback_responses:
            fallback = self.fallback_responses[operation]
            self.logger.info(f"Using fallback response for {operation}")
            return fallback
        
        # Generic fallback
        self.logger.warning(f"No specific fallback for {operation}, using generic")
        return {"status": "error", "message": "Service temporarily unavailable"}

# Circuit breaker implementation

class CircuitBreaker:
    """Circuit breaker for handling repeated failures."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logging.getLogger(__name__ + ".CircuitBreaker")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN - calls rejected")
        
        try:
            # Execute function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs),
                timeout=self.config.timeout_seconds
            )
            
            await self._on_success()
            return result
        
        except Exception as e:
            await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit breaker."""
        if not self.last_failure_time:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.config.recovery_timeout
    
    async def _on_success(self):
        """Handle successful execution."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info("Circuit breaker CLOSED - service recovered")
    
    async def _on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning("Circuit breaker OPEN - half-open test failed")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(f"Circuit breaker OPEN - threshold reached ({self.failure_count} failures)")

# Comprehensive error handling system

class ErrorHandlingSystem:
    """Centralized error handling system."""
    
    def __init__(self):
        self.handlers: List[ErrorHandler] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.error_log: deque = deque(maxlen=1000)  # Keep last 1000 errors
        self.error_stats: Dict[str, int] = defaultdict(int)
        self.logger = logging.getLogger(__name__ + ".ErrorHandlingSystem")
    
    def add_handler(self, handler: ErrorHandler) -> 'ErrorHandlingSystem':
        """Add an error handler."""
        self.handlers.append(handler)
        return self
    
    def add_circuit_breaker(self, name: str, config: CircuitBreakerConfig) -> 'ErrorHandlingSystem':
        """Add a circuit breaker."""
        self.circuit_breakers[name] = CircuitBreaker(config)
        return self
    
    async def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext
    ) -> Optional[Any]:
        """Handle an error using registered handlers."""
        # Create error details
        error_details = self._create_error_details(error, context)
        self.error_log.append(error_details)
        self._update_error_stats(error_details)
        
        # Try each handler
        for handler in self.handlers:
            if handler.can_handle(error):
                try:
                    result = await handler.handle_error(error, context)
                    if result is not None:
                        self.logger.info(
                            f"Error handled by {handler.__class__.__name__} "
                            f"for operation {context.operation}"
                        )
                        return result
                except Exception as handler_error:
                    self.logger.error(
                        f"Handler {handler.__class__.__name__} failed: {str(handler_error)}"
                    )
        
        # No handler could resolve the error
        self.logger.error(f"No handler could resolve error for operation {context.operation}")
        return None
    
    def _create_error_details(self, error: Exception, context: ErrorContext) -> ErrorDetails:
        """Create detailed error information."""
        import uuid
        
        # Determine error category and severity
        if isinstance(error, AgentError):
            category = error.category
            severity = error.severity
            metadata = error.metadata
        else:
            category = self._classify_error(error)
            severity = self._determine_severity(error)
            metadata = {}
        
        return ErrorDetails(
            error_id=str(uuid.uuid4()),
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            category=category,
            context=context,
            stack_trace=traceback.format_exc(),
            recovery_suggestions=self._suggest_recovery(error, category),
            metadata=metadata
        )
    
    def _classify_error(self, error: Exception) -> ErrorCategory:
        """Classify error by type."""
        error_type = type(error).__name__.lower()
        
        if 'timeout' in error_type or 'asyncio.timeout' in str(type(error)):
            return ErrorCategory.TIMEOUT
        elif 'connection' in error_type or 'network' in error_type:
            return ErrorCategory.NETWORK
        elif 'validation' in error_type or 'value' in error_type:
            return ErrorCategory.VALIDATION
        elif 'auth' in error_type:
            return ErrorCategory.AUTHENTICATION
        elif 'permission' in error_type or 'forbidden' in error_type:
            return ErrorCategory.AUTHORIZATION
        elif 'memory' in error_type or 'resource' in error_type:
            return ErrorCategory.RESOURCE
        else:
            return ErrorCategory.UNKNOWN
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """Determine error severity."""
        error_type = type(error).__name__.lower()
        
        if 'critical' in error_type or 'fatal' in error_type:
            return ErrorSeverity.CRITICAL
        elif 'timeout' in error_type or 'connection' in error_type:
            return ErrorSeverity.HIGH
        elif 'validation' in error_type or 'value' in error_type:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _suggest_recovery(self, error: Exception, category: ErrorCategory) -> List[str]:
        """Suggest recovery actions based on error."""
        suggestions = {
            ErrorCategory.TIMEOUT: [
                "Increase timeout duration",
                "Implement retry mechanism",
                "Check network connectivity"
            ],
            ErrorCategory.NETWORK: [
                "Check network connectivity",
                "Verify service endpoints",
                "Implement circuit breaker"
            ],
            ErrorCategory.VALIDATION: [
                "Validate input data format",
                "Check required fields",
                "Review data constraints"
            ],
            ErrorCategory.AUTHENTICATION: [
                "Verify credentials",
                "Check token expiration",
                "Refresh authentication"
            ],
            ErrorCategory.RESOURCE: [
                "Check available memory",
                "Monitor system resources",
                "Scale up resources"
            ]
        }
        
        return suggestions.get(category, ["Review error details", "Contact support"])
    
    def _update_error_stats(self, error_details: ErrorDetails):
        """Update error statistics."""
        self.error_stats[error_details.category.value] += 1
        self.error_stats[error_details.severity.value] += 1
        self.error_stats['total'] += 1
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        recent_errors = list(self.error_log)[-100:]  # Last 100 errors
        
        return {
            "total_errors": len(self.error_log),
            "error_categories": dict(self.error_stats),
            "recent_errors": len(recent_errors),
            "circuit_breaker_states": {
                name: cb.state.value 
                for name, cb in self.circuit_breakers.items()
            }
        }

# Decorators for error handling

def with_error_handling(
    error_system: ErrorHandlingSystem,
    operation_name: str,
    circuit_breaker_name: Optional[str] = None
):
    """Decorator for automatic error handling."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            context = ErrorContext(
                request_id=kwargs.get('request_id', 'unknown'),
                operation=operation_name
            )
            
            try:
                if circuit_breaker_name and circuit_breaker_name in error_system.circuit_breakers:
                    cb = error_system.circuit_breakers[circuit_breaker_name]
                    return await cb.call(func, *args, **kwargs)
                else:
                    return await func(*args, **kwargs)
            
            except Exception as e:
                result = await error_system.handle_error(e, context)
                if result is not None:
                    return result
                raise
        
        return wrapper
    return decorator

# Example usage and demonstrations

def demo_error_handling_system():
    """Demonstrate error handling system usage."""
    print("\n=== Error Handling System Demo ===")
    
    async def run_demo():
        # Create error handling system
        error_system = ErrorHandlingSystem()
        
        # Add retry handler
        retry_config = RetryConfig(max_attempts=3, base_delay=0.5)
        error_system.add_handler(RetryHandler(retry_config))
        
        # Add fallback handler
        fallbacks = {
            "data_processing": {"status": "success", "data": "cached_data"},
            "user_lookup": {"status": "success", "user": "anonymous"}
        }
        error_system.add_handler(FallbackHandler(fallbacks))
        
        # Add circuit breaker
        cb_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30)
        error_system.add_circuit_breaker("api_service", cb_config)
        
        # Simulate errors
        print("Testing error handling...")
        
        # Test retry mechanism
        context = ErrorContext(request_id="test-001", operation="data_processing")
        
        try:
            raise NetworkError("Connection failed", metadata={"endpoint": "api.example.com"})
        except Exception as e:
            result = await error_system.handle_error(e, context)
            print(f"Retry result: {result}")
        
        # Test fallback mechanism
        try:
            raise TimeoutError("Request timeout", timeout_seconds=30.0)
        except Exception as e:
            result = await error_system.handle_error(e, context)
            print(f"Fallback result: {result}")
        
        # Test circuit breaker
        @with_error_handling(error_system, "api_call", "api_service")
        async def failing_api_call():
            if random.random() > 0.8:  # 20% success rate
                return "API call successful"
            raise NetworkError("API service unavailable")
        
        print("\nTesting circuit breaker...")
        for i in range(10):
            try:
                result = await failing_api_call()
                print(f"Call {i + 1}: {result}")
            except Exception as e:
                print(f"Call {i + 1}: Failed - {str(e)}")
            
            await asyncio.sleep(0.1)
        
        # Show error statistics
        print("\nError Statistics:")
        stats = error_system.get_error_stats()
        print(json.dumps(stats, indent=2))
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    demo_error_handling_system()
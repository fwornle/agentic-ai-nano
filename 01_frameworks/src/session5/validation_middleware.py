# src/session5/validation_middleware.py
"""
Advanced validation patterns and middleware for PydanticAI agents.
Implements type-safe validation chains, middleware patterns, and validation orchestration.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union, Type
from pydantic import BaseModel, Field, validator, ValidationError
from pydantic_ai import Agent, RunContext
from datetime import datetime
from enum import Enum
import asyncio
import logging
import functools
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
R = TypeVar('R')

class ValidationSeverity(str, Enum):
    """Severity levels for validation results."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationResult(BaseModel):
    """Type-safe validation result."""
    is_valid: bool = Field(..., description="Whether validation passed")
    severity: ValidationSeverity = Field(..., description="Validation severity")
    message: str = Field(..., description="Validation message")
    field_path: Optional[str] = Field(None, description="Path to invalid field")
    suggested_fix: Optional[str] = Field(None, description="Suggested correction")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidationContext(BaseModel):
    """Context for validation operations."""
    request_id: str = Field(..., description="Unique request identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.now)

class ValidatorConfig(BaseModel):
    """Configuration for validators."""
    enabled: bool = Field(default=True, description="Whether validator is enabled")
    priority: int = Field(default=0, description="Validator priority (higher = earlier)")
    timeout_seconds: float = Field(default=5.0, description="Validator timeout")
    retry_count: int = Field(default=0, description="Number of retries on failure")
    cache_results: bool = Field(default=False, description="Whether to cache results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional config")

# Abstract base classes

class BaseValidator(ABC, Generic[T]):
    """Abstract base class for type-safe validators."""
    
    def __init__(self, config: ValidatorConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def validate_async(
        self, 
        data: T, 
        context: ValidationContext
    ) -> ValidationResult:
        """Perform async validation on data."""
        pass
    
    def validate_sync(self, data: T, context: ValidationContext) -> ValidationResult:
        """Synchronous validation wrapper."""
        return asyncio.run(self.validate_async(data, context))
    
    def __call__(self, data: T, context: ValidationContext) -> ValidationResult:
        """Make validator callable."""
        return self.validate_sync(data, context)

class ValidationMiddleware(ABC):
    """Abstract middleware for validation pipeline."""
    
    @abstractmethod
    async def process_request(
        self, 
        data: Any, 
        context: ValidationContext,
        next_handler: Callable
    ) -> Any:
        """Process validation request."""
        pass

# Concrete validator implementations

class SchemaValidator(BaseValidator[BaseModel]):
    """Validates data against Pydantic schema."""
    
    def __init__(self, schema: Type[BaseModel], config: ValidatorConfig):
        super().__init__(config)
        self.schema = schema
    
    async def validate_async(
        self, 
        data: BaseModel, 
        context: ValidationContext
    ) -> ValidationResult:
        """Validate against Pydantic schema."""
        try:
            if not isinstance(data, self.schema):
                # Try to parse if it's dict-like
                if isinstance(data, dict):
                    self.schema(**data)
                else:
                    raise ValidationError([{"msg": f"Expected {self.schema.__name__}"}], self.schema)
            
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                message=f"Schema validation passed for {self.schema.__name__}",
                metadata={"schema": self.schema.__name__}
            )
        
        except ValidationError as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Schema validation failed: {str(e)}",
                suggested_fix="Check field types and required values",
                metadata={"errors": e.errors(), "schema": self.schema.__name__}
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Unexpected validation error: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )

class BusinessRuleValidator(BaseValidator[BaseModel]):
    """Validates business rules on data."""
    
    def __init__(self, rules: List[Callable[[BaseModel], bool]], config: ValidatorConfig):
        super().__init__(config)
        self.rules = rules
    
    async def validate_async(
        self, 
        data: BaseModel, 
        context: ValidationContext
    ) -> ValidationResult:
        """Validate business rules."""
        failed_rules = []
        
        for i, rule in enumerate(self.rules):
            try:
                if not rule(data):
                    failed_rules.append(f"Rule {i + 1}: {rule.__name__}")
            except Exception as e:
                failed_rules.append(f"Rule {i + 1} error: {str(e)}")
        
        if failed_rules:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                message=f"Business rule validation failed: {', '.join(failed_rules)}",
                suggested_fix="Review business logic constraints",
                metadata={"failed_rules": failed_rules}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message="All business rules passed",
            metadata={"rules_checked": len(self.rules)}
        )

class SecurityValidator(BaseValidator[BaseModel]):
    """Validates security constraints on data."""
    
    def __init__(self, config: ValidatorConfig):
        super().__init__(config)
        self.dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"onload=",
            r"onerror=",
            r"eval\(",
            r"setTimeout\(",
            r"setInterval\("
        ]
    
    async def validate_async(
        self, 
        data: BaseModel, 
        context: ValidationContext
    ) -> ValidationResult:
        """Validate security constraints."""
        import re
        
        # Convert model to dict for scanning
        data_dict = data.dict() if hasattr(data, 'dict') else {}
        data_str = json.dumps(data_dict, default=str).lower()
        
        threats_found = []
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                threats_found.append(pattern)
        
        if threats_found:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.CRITICAL,
                message=f"Security validation failed: potential threats detected",
                suggested_fix="Remove potentially malicious content",
                metadata={"threats": threats_found}
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            message="Security validation passed",
            metadata={"patterns_checked": len(self.dangerous_patterns)}
        )

# Middleware implementations

class LoggingMiddleware(ValidationMiddleware):
    """Logs validation requests and responses."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    async def process_request(
        self, 
        data: Any, 
        context: ValidationContext,
        next_handler: Callable
    ) -> Any:
        """Log validation request."""
        self.logger.info(f"Validation request: {context.request_id}")
        
        try:
            result = await next_handler(data, context)
            self.logger.info(f"Validation completed: {context.request_id}")
            return result
        except Exception as e:
            self.logger.error(f"Validation failed: {context.request_id} - {str(e)}")
            raise

class RateLimitingMiddleware(ValidationMiddleware):
    """Rate limits validation requests."""
    
    def __init__(self, max_requests_per_second: int = 10):
        self.max_requests = max_requests_per_second
        self.request_timestamps: List[datetime] = []
        self._lock = asyncio.Lock()
    
    async def process_request(
        self, 
        data: Any, 
        context: ValidationContext,
        next_handler: Callable
    ) -> Any:
        """Apply rate limiting."""
        async with self._lock:
            now = datetime.now()
            # Remove old timestamps
            self.request_timestamps = [
                ts for ts in self.request_timestamps
                if (now - ts).total_seconds() < 1
            ]
            
            if len(self.request_timestamps) >= self.max_requests:
                raise ValueError("Rate limit exceeded")
            
            self.request_timestamps.append(now)
        
        return await next_handler(data, context)

class CachingMiddleware(ValidationMiddleware):
    """Caches validation results."""
    
    def __init__(self, cache_ttl_seconds: int = 300):
        self.cache: Dict[str, tuple] = {}
        self.cache_ttl = cache_ttl_seconds
    
    def _get_cache_key(self, data: Any, context: ValidationContext) -> str:
        """Generate cache key."""
        import hashlib
        data_str = json.dumps(data.dict() if hasattr(data, 'dict') else str(data), sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def process_request(
        self, 
        data: Any, 
        context: ValidationContext,
        next_handler: Callable
    ) -> Any:
        """Check cache or process request."""
        cache_key = self._get_cache_key(data, context)
        now = datetime.now()
        
        # Check cache
        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if (now - timestamp).total_seconds() < self.cache_ttl:
                return result
            else:
                del self.cache[cache_key]
        
        # Process and cache result
        result = await next_handler(data, context)
        self.cache[cache_key] = (result, now)
        return result

# Validation orchestration

class ValidationPipeline:
    """Orchestrates multiple validators with middleware."""
    
    def __init__(self):
        self.validators: List[BaseValidator] = []
        self.middleware: List[ValidationMiddleware] = []
        self.logger = logging.getLogger(__name__ + ".ValidationPipeline")
    
    def add_validator(self, validator: BaseValidator) -> 'ValidationPipeline':
        """Add validator to pipeline."""
        self.validators.append(validator)
        # Sort by priority (higher priority first)
        self.validators.sort(key=lambda v: v.config.priority, reverse=True)
        return self
    
    def add_middleware(self, middleware: ValidationMiddleware) -> 'ValidationPipeline':
        """Add middleware to pipeline."""
        self.middleware.append(middleware)
        return self
    
    async def validate_async(
        self, 
        data: BaseModel, 
        context: ValidationContext
    ) -> List[ValidationResult]:
        """Run validation pipeline."""
        async def _run_validators():
            results = []
            
            for validator in self.validators:
                if not validator.config.enabled:
                    continue
                
                try:
                    # Apply timeout
                    result = await asyncio.wait_for(
                        validator.validate_async(data, context),
                        timeout=validator.config.timeout_seconds
                    )
                    results.append(result)
                    
                    # Stop on critical errors
                    if not result.is_valid and result.severity == ValidationSeverity.CRITICAL:
                        break
                
                except asyncio.TimeoutError:
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Validator {validator.__class__.__name__} timed out"
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        is_valid=False,
                        severity=ValidationSeverity.ERROR,
                        message=f"Validator {validator.__class__.__name__} failed: {str(e)}"
                    ))
            
            return results
        
        # Apply middleware
        handler = _run_validators
        for middleware in reversed(self.middleware):
            current_handler = handler
            handler = functools.partial(
                middleware.process_request, 
                next_handler=lambda d, c: current_handler()
            )
        
        return await handler(data, context)
    
    def validate_sync(
        self, 
        data: BaseModel, 
        context: ValidationContext
    ) -> List[ValidationResult]:
        """Synchronous validation."""
        return asyncio.run(self.validate_async(data, context))

# Factory for validation pipelines

class ValidationPipelineFactory:
    """Factory for creating configured validation pipelines."""
    
    @staticmethod
    def create_default_pipeline() -> ValidationPipeline:
        """Create default validation pipeline."""
        pipeline = ValidationPipeline()
        
        # Add logging middleware
        pipeline.add_middleware(LoggingMiddleware(logger))
        
        # Add rate limiting
        pipeline.add_middleware(RateLimitingMiddleware(max_requests_per_second=50))
        
        # Add caching
        pipeline.add_middleware(CachingMiddleware(cache_ttl_seconds=300))
        
        return pipeline
    
    @staticmethod
    def create_secure_pipeline() -> ValidationPipeline:
        """Create security-focused validation pipeline."""
        pipeline = ValidationPipelineFactory.create_default_pipeline()
        
        # Add security validator with high priority
        security_config = ValidatorConfig(
            enabled=True,
            priority=100,
            timeout_seconds=2.0
        )
        pipeline.add_validator(SecurityValidator(security_config))
        
        return pipeline

# Example usage and demonstrations

class UserProfile(BaseModel):
    """Example user profile model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=13, le=120)
    bio: Optional[str] = Field(None, max_length=500)

def demo_validation_middleware():
    """Demonstrate validation middleware usage."""
    print("\n=== Validation Middleware Demo ===")
    
    # Create validation pipeline
    pipeline = ValidationPipelineFactory.create_secure_pipeline()
    
    # Add schema validator
    schema_config = ValidatorConfig(priority=90)
    pipeline.add_validator(SchemaValidator(UserProfile, schema_config))
    
    # Add business rule validator
    def validate_adult_bio(user: UserProfile) -> bool:
        """Business rule: adults should have a bio."""
        if user.age >= 18 and not user.bio:
            return False
        return True
    
    business_config = ValidatorConfig(priority=80)
    pipeline.add_validator(BusinessRuleValidator([validate_adult_bio], business_config))
    
    # Test valid user
    valid_user = UserProfile(
        username="john_doe",
        email="john@example.com",
        age=25,
        bio="Software developer interested in AI"
    )
    
    context = ValidationContext(request_id="test-001", user_id="user-123")
    
    print("Testing valid user...")
    results = pipeline.validate_sync(valid_user, context)
    
    for result in results:
        status = "✓" if result.is_valid else "✗"
        print(f"{status} {result.severity.value}: {result.message}")
    
    # Test invalid user (potential XSS)
    print("\nTesting potentially malicious user...")
    try:
        malicious_user = UserProfile(
            username="hacker",
            email="hacker@evil.com", 
            age=25,
            bio="<script>alert('XSS')</script>"
        )
        
        results = pipeline.validate_sync(malicious_user, context)
        
        for result in results:
            status = "✓" if result.is_valid else "✗"
            print(f"{status} {result.severity.value}: {result.message}")
    
    except Exception as e:
        print(f"Validation blocked: {str(e)}")

if __name__ == "__main__":
    demo_validation_middleware()
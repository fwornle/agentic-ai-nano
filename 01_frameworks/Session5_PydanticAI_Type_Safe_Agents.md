# Session 5: PydanticAI Type-Safe Agents
## Modern Python Agent Development with Type Safety

### 🎯 **Session Overview**
PydanticAI represents a paradigm shift in agent development, leveraging Pydantic's robust type system and validation framework to create agents with guaranteed data integrity, structured outputs, and comprehensive error handling. This session provides a deep dive into building production-ready, type-safe agents that scale from prototypes to enterprise systems.

### 📚 **Learning Objectives**
1. **Master PydanticAI architecture** and type-safe agent design patterns
2. **Implement comprehensive validation** with custom validators and constraints
3. **Build scalable type-safe tools** and function calling interfaces
4. **Design robust error handling** with structured exception management  
5. **Apply production patterns** for maintainable, testable agents
6. **Optimize performance** while maintaining type safety guarantees

---

## **Part 1: PydanticAI Foundation (400 lines)**

### **Core Architecture and Type System**

PydanticAI builds on Pydantic's validation framework to ensure data integrity throughout the agent lifecycle. The foundation relies on three key concepts: structured data models, type-safe agents, and validated tool interfaces.

```python
# src/session5/pydantic_agents.py - Core Foundation
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid

# Core enumeration types for better type safety
class TaskPriority(str, Enum):
    """Priority levels with explicit string values for serialization."""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(str, Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

The foundation establishes type-safe data structures that serve as contracts between different agent components. Each model includes comprehensive validation rules and metadata for debugging and monitoring.

```python
# Base models for structured agent communication
class AgentMetadata(BaseModel):
    """Metadata for agent execution tracking."""
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(default="1.0.0", regex=r'^\d+\.\d+\.\d+$')
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Pydantic configuration for serialization."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ValidationError(BaseModel):
    """Structured validation error information."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    value: Any = Field(..., description="Invalid value that caused the error")
    
class ExecutionContext(BaseModel):
    """Context information for agent execution."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
```

### **Type-Safe Agent Definition**

PydanticAI agents are defined with explicit result types and comprehensive system prompts. This ensures consistent output structure and enables compile-time type checking.

```python
# Research domain models with comprehensive validation
class ResearchResult(BaseModel):
    """Type-safe research result structure with full validation."""
    topic: str = Field(
        ..., 
        min_length=5, 
        max_length=200,
        description="Research topic or query"
    )
    key_findings: List[str] = Field(
        ..., 
        min_items=1, 
        max_items=20,
        description="Main research findings"
    )
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence in findings (0.0-1.0)"
    )
    sources: List[str] = Field(
        ..., 
        min_items=1,
        description="Information sources and citations"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    metadata: AgentMetadata = Field(default_factory=lambda: AgentMetadata(agent_name="research_agent"))
    
    @validator('key_findings')
    def validate_findings_quality(cls, v):
        """Ensure findings meet quality standards."""
        if not v:
            raise ValueError("At least one finding is required")
        
        for i, finding in enumerate(v):
            if len(finding.strip()) < 10:
                raise ValueError(f"Finding {i+1} too short (min 10 characters)")
            if finding.strip().lower() in ['none', 'n/a', 'unknown']:
                raise ValueError(f"Finding {i+1} is not informative")
        return [finding.strip() for finding in v]
    
    @validator('sources')
    def validate_source_format(cls, v):
        """Validate source format and credibility indicators."""
        valid_patterns = ['http://', 'https://', 'www.', 'doi:', 'isbn:', 'journal:', 'book:', 'paper:']
        
        for i, source in enumerate(v):
            if not any(pattern in source.lower() for pattern in valid_patterns):
                raise ValueError(f"Source {i+1} does not match valid format patterns")
            if len(source.strip()) < 5:
                raise ValueError(f"Source {i+1} too short to be valid")
        
        return [source.strip() for source in v]
    
    @root_validator
    def validate_consistency(cls, values):
        """Validate consistency across all fields."""
        confidence = values.get('confidence_score', 0.0)
        findings = values.get('key_findings', [])
        sources = values.get('sources', [])
        
        # Higher confidence should correlate with more sources
        min_sources_for_confidence = {
            0.9: 3, 0.8: 2, 0.7: 2, 0.6: 1
        }
        
        for threshold, min_sources in min_sources_for_confidence.items():
            if confidence >= threshold and len(sources) < min_sources:
                raise ValueError(f"Confidence {confidence} requires at least {min_sources} sources")
        
        return values
```

### **Agent Creation and Configuration**

The agent creation process includes comprehensive configuration for type safety, error handling, and monitoring capabilities.

```python
def create_research_agent() -> Agent:
    """
    Create a type-safe research agent with comprehensive configuration.
    
    Returns:
        Agent: Configured PydanticAI research agent
    """
    
    # Create agent with strict type enforcement
    research_agent = Agent(
        'openai:gpt-4',
        result_type=ResearchResult,
        system_prompt="""
        You are a professional research analyst with expertise in data validation 
        and structured reporting. Your responses must always conform to the 
        ResearchResult schema with high-quality findings and credible sources.
        
        Guidelines:
        - Provide substantive findings (minimum 10 characters each)
        - Include credible, verifiable sources
        - Assign appropriate confidence scores based on source quality
        - Use clear, professional language
        - Prioritize recent and authoritative sources
        """,
        deps_type=ExecutionContext
    )
    
    return research_agent

# Usage example with comprehensive error handling
async def execute_research_with_validation():
    """Demonstrate comprehensive research execution."""
    agent = create_research_agent()
    context = ExecutionContext(
        user_id="user_123",
        session_id="session_456", 
        metadata={"department": "research", "project": "ai_study"}
    )
    
    try:
        result = await agent.run(
            user_prompt="Research the benefits of type-safe programming in AI systems",
            deps=context
        )
        
        # Type checking ensures result is ResearchResult
        print(f"Research completed with {len(result.key_findings)} findings")
        print(f"Confidence score: {result.confidence_score}")
        print(f"Agent: {result.metadata.agent_name} v{result.metadata.version}")
        
        return result
        
    except Exception as e:
        print(f"Research failed: {e}")
        raise
```

### **Advanced Type Definitions and Constraints**

PydanticAI supports complex type definitions with sophisticated validation rules for domain-specific requirements.

```python
# Advanced data analysis types
class AnalysisRequest(BaseModel):
    """Input validation for statistical analysis requests."""
    data: List[float] = Field(
        ..., 
        min_items=3,
        max_items=10000,
        description="Numerical data for analysis"
    )
    analysis_type: Literal["mean", "median", "std", "trend", "correlation"] = Field(
        ...,
        description="Type of statistical analysis to perform"
    )
    confidence_level: float = Field(
        default=0.95,
        ge=0.5,
        le=0.999,
        description="Statistical confidence level"
    )
    include_visualization: bool = Field(
        default=False,
        description="Whether to include visualization data"
    )
    outlier_detection: bool = Field(
        default=True,
        description="Whether to detect and report outliers"
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional analysis metadata"
    )
    
    @validator('data')
    def validate_data_quality(cls, v):
        """Comprehensive data quality validation."""
        if not v:
            raise ValueError("Data cannot be empty")
        
        # Check for basic data quality issues
        if any(x != x for x in v):  # NaN check
            raise ValueError("Data contains NaN values")
        
        if any(abs(x) == float('inf') for x in v):
            raise ValueError("Data contains infinite values")
        
        # Statistical validity checks
        if len(set(v)) == 1:
            raise ValueError("All data points are identical - no variation for analysis")
        
        # Range validation for reasonable values
        if any(abs(x) > 1e10 for x in v):
            raise ValueError("Data contains extremely large values that may cause numerical issues")
        
        return v
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v, values):
        """Validate confidence level based on data size."""
        data = values.get('data', [])
        
        if len(data) < 10 and v > 0.99:
            raise ValueError("High confidence levels require more data points")
        
        return v

class AnalysisResult(BaseModel):
    """Type-safe analysis result with comprehensive information."""
    analysis_type: str = Field(..., description="Type of analysis performed")
    sample_size: int = Field(..., ge=1, description="Number of data points analyzed")
    result_value: float = Field(..., description="Primary analysis result")
    standard_error: Optional[float] = Field(None, ge=0.0, description="Standard error if applicable")
    confidence_interval: Optional[List[float]] = Field(
        None,
        min_items=2,
        max_items=2,
        description="Confidence interval bounds"
    )
    outliers_detected: List[float] = Field(
        default_factory=list,
        description="Detected outlier values"
    )
    quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Data quality assessment score"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Analysis warnings and recommendations"
    )
    visualization_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Data for visualization if requested"
    )
    execution_time_ms: float = Field(..., ge=0.0, description="Analysis execution time")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        """Configuration for result serialization."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

---

## **Part 2: Advanced Validation (500 lines)**

### **Custom Validators and Constraints**

PydanticAI's validation system extends beyond basic type checking to include domain-specific business logic and data integrity rules.

```python
# Advanced validation patterns and custom validators
from pydantic import validator, root_validator, Field
from typing import ClassVar, Pattern
import re
from decimal import Decimal, InvalidOperation

class ValidationRules:
    """Centralized validation rules and patterns."""
    
    EMAIL_PATTERN: ClassVar[Pattern] = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    URL_PATTERN: ClassVar[Pattern] = re.compile(
        r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    )
    
    SEMANTIC_VERSION_PATTERN: ClassVar[Pattern] = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    )

class UserProfile(BaseModel):
    """User profile with advanced validation constraints."""
    
    user_id: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_-]+$')
    email: str = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=13, le=120, description="User age in years")
    salary: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Annual salary")
    skills: List[str] = Field(default_factory=list, max_items=20)
    preferences: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)
    registration_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    @validator('email')
    def validate_email_format(cls, v):
        """Validate email format using regex pattern."""
        if not ValidationRules.EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format')
        
        # Additional business logic
        blocked_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
        domain = v.split('@')[1].lower()
        if domain in blocked_domains:
            raise ValueError('Email domain not allowed')
        
        return v.lower()
    
    @validator('full_name')
    def validate_name_format(cls, v):
        """Validate name contains only allowed characters."""
        if not re.match(r'^[a-zA-Z\s\'-\.]+$', v):
            raise ValueError('Name contains invalid characters')
        
        # Check for minimum word count
        words = v.strip().split()
        if len(words) < 2:
            raise ValueError('Full name must contain at least two words')
        
        # Capitalize each word properly
        return ' '.join(word.capitalize() for word in words)
    
    @validator('skills')
    def validate_skills_list(cls, v):
        """Validate skills list for quality and uniqueness."""
        if not v:
            return v
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in v:
            skill_normalized = skill.strip().lower()
            if skill_normalized not in seen and len(skill_normalized) >= 2:
                seen.add(skill_normalized)
                unique_skills.append(skill.strip())
        
        # Validate skill format
        for skill in unique_skills:
            if not re.match(r'^[a-zA-Z0-9\s\+\#\-\.]+$', skill):
                raise ValueError(f'Invalid skill format: {skill}')
        
        return unique_skills
    
    @validator('salary')
    def validate_salary_range(cls, v, values):
        """Validate salary based on age and other factors."""
        if v is None:
            return v
        
        age = values.get('age')
        if age and age < 16 and v > Decimal('50000'):
            raise ValueError('Salary too high for reported age')
        
        # Currency validation (assuming USD)
        if v > Decimal('10000000'):  # $10M cap
            raise ValueError('Salary exceeds reasonable maximum')
        
        return v
    
    @root_validator
    def validate_profile_consistency(cls, values):
        """Cross-field validation for profile consistency."""
        registration_date = values.get('registration_date')
        last_login = values.get('last_login')
        age = values.get('age')
        is_active = values.get('is_active')
        
        # Last login cannot be before registration
        if last_login and registration_date and last_login < registration_date:
            raise ValueError('Last login cannot be before registration date')
        
        # Active users should have logged in recently (within 2 years)
        if is_active and last_login:
            time_since_login = datetime.now(timezone.utc) - last_login
            if time_since_login.days > 730:  # 2 years
                values['is_active'] = False
        
        # Validate registration age consistency
        if registration_date and age:
            years_since_registration = (datetime.now(timezone.utc) - registration_date).days / 365.25
            if years_since_registration > age:
                raise ValueError('Registration date inconsistent with current age')
        
        return values

class TaskDefinition(BaseModel):
    """Task definition with complex validation rules."""
    
    task_id: str = Field(..., min_length=8, max_length=32)
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assignee_id: Optional[str] = None
    reporter_id: str = Field(..., min_length=3)
    labels: List[str] = Field(default_factory=list, max_items=10)
    estimated_hours: Optional[float] = Field(None, gt=0, le=1000)
    due_date: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list, max_items=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('task_id')
    def validate_task_id_format(cls, v):
        """Validate task ID follows organizational format."""
        # Format: PROJECT-NUMBER (e.g., PROJ-1234)
        if not re.match(r'^[A-Z]{2,10}-\d{1,6}$', v):
            raise ValueError('Task ID must follow format: PROJECT-NUMBER (e.g., PROJ-1234)')
        return v
    
    @validator('title')
    def validate_title_quality(cls, v):
        """Ensure title meets quality standards."""
        # Remove extra whitespace
        cleaned_title = ' '.join(v.split())
        
        # Check for common poor title patterns
        poor_patterns = [
            r'^(fix|bug|issue|problem|error)\s*$',  # Too generic
            r'^(do|make|create|update)\s*$',        # Too vague
            r'^[a-z]',                              # Should start with capital
            r'\s+$',                                # Ends with whitespace
        ]
        
        for pattern in poor_patterns:
            if re.search(pattern, cleaned_title, re.IGNORECASE):
                raise ValueError(f'Title fails quality check: {cleaned_title}')
        
        return cleaned_title
    
    @validator('labels')
    def validate_labels_format(cls, v):
        """Validate label format and content."""
        validated_labels = []
        
        for label in v:
            # Clean and validate label
            clean_label = label.strip().lower()
            
            if len(clean_label) < 2:
                continue  # Skip too short labels
            
            if not re.match(r'^[a-z0-9-_]+$', clean_label):
                raise ValueError(f'Invalid label format: {label}')
            
            validated_labels.append(clean_label)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(validated_labels))
    
    @validator('due_date')
    def validate_due_date_reasonable(cls, v, values):
        """Validate due date is reasonable."""
        if v is None:
            return v
        
        now = datetime.now(timezone.utc)
        
        # Due date cannot be in the past
        if v < now:
            raise ValueError('Due date cannot be in the past')
        
        # Due date should not be more than 2 years in the future
        max_future_date = now.replace(year=now.year + 2)
        if v > max_future_date:
            raise ValueError('Due date too far in the future (max 2 years)')
        
        # Validate against estimated hours
        estimated_hours = values.get('estimated_hours')
        if estimated_hours:
            time_until_due = (v - now).days
            hours_per_day = estimated_hours / max(time_until_due, 1)
            
            if hours_per_day > 16:  # More than 16 hours per day
                raise ValueError('Due date too soon for estimated work hours')
        
        return v
    
    @root_validator
    def validate_task_consistency(cls, values):
        """Validate cross-field consistency."""
        status = values.get('status')
        assignee_id = values.get('assignee_id')
        due_date = values.get('due_date')
        estimated_hours = values.get('estimated_hours')
        
        # Tasks in progress must have assignee
        if status == TaskStatus.IN_PROGRESS and not assignee_id:
            raise ValueError('In-progress tasks must have an assignee')
        
        # Completed tasks should not have future due dates
        if status == TaskStatus.COMPLETED and due_date:
            if due_date > datetime.now(timezone.utc):
                values['due_date'] = None  # Clear future due date for completed task
        
        # High priority tasks should have reasonable estimates
        if values.get('priority') == TaskPriority.CRITICAL:
            if not estimated_hours:
                raise ValueError('Critical tasks must have time estimates')
            if estimated_hours > 200:  # More than 5 weeks
                raise ValueError('Critical tasks should not require more than 200 hours')
        
        # Update timestamp
        values['updated_at'] = datetime.now(timezone.utc)
        
        return values
```

### **Validation Error Management**

Comprehensive error handling and validation reporting systems ensure robust agent behavior under all conditions.

```python
# Advanced error handling and validation reporting
from typing import Dict, List, Type, Any
import traceback
from dataclasses import dataclass

@dataclass
class ValidationErrorDetail:
    """Detailed validation error information."""
    field_path: str
    error_type: str
    message: str
    invalid_value: Any
    constraint: str
    suggestion: Optional[str] = None

class ValidationErrorHandler:
    """Centralized validation error handling and reporting."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.common_errors: List[ValidationErrorDetail] = []
    
    def handle_validation_error(self, error: Exception, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Process validation errors and provide structured feedback."""
        
        error_details = []
        
        if hasattr(error, 'errors'):
            # Pydantic validation error
            for err in error.errors():
                detail = ValidationErrorDetail(
                    field_path='.'.join(str(loc) for loc in err['loc']),
                    error_type=err['type'],
                    message=err['msg'],
                    invalid_value=err.get('ctx', {}).get('given', 'unknown'),
                    constraint=err.get('ctx', {}).get('limit_value', 'unknown'),
                    suggestion=self._generate_suggestion(err['type'], err['msg'])
                )
                error_details.append(detail)
                
                # Track error frequency
                error_key = f"{model_class.__name__}.{detail.field_path}.{detail.error_type}"
                self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        else:
            # Generic error
            detail = ValidationErrorDetail(
                field_path="unknown",
                error_type="generic_error",
                message=str(error),
                invalid_value="unknown",
                constraint="unknown"
            )
            error_details.append(detail)
        
        return {
            'validation_failed': True,
            'model': model_class.__name__,
            'error_count': len(error_details),
            'errors': [
                {
                    'field': detail.field_path,
                    'type': detail.error_type,
                    'message': detail.message,
                    'invalid_value': detail.invalid_value,
                    'suggestion': detail.suggestion
                }
                for detail in error_details
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_suggestion(self, error_type: str, message: str) -> Optional[str]:
        """Generate helpful suggestions based on error type."""
        
        suggestions = {
            'value_error': {
                'email': 'Please provide a valid email address (e.g., user@example.com)',
                'url': 'Please provide a valid URL starting with http:// or https://',
                'regex': 'Please check the format requirements for this field',
            },
            'type_error': {
                'str': 'This field requires text (string) input',
                'int': 'This field requires a whole number',
                'float': 'This field requires a decimal number',
                'list': 'This field requires a list of values',
                'dict': 'This field requires a dictionary/object structure',
            },
            'missing': {
                'default': 'This field is required and cannot be empty'
            }
        }
        
        # Extract error category
        for category, subcategories in suggestions.items():
            if category in error_type:
                for keyword, suggestion in subcategories.items():
                    if keyword in message.lower() or keyword == 'default':
                        return suggestion
        
        return None
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get validation error statistics for monitoring."""
        if not self.error_counts:
            return {'total_errors': 0, 'unique_error_types': 0}
        
        total_errors = sum(self.error_counts.values())
        most_common_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_errors': total_errors,
            'unique_error_types': len(self.error_counts),
            'most_common_errors': [
                {'error': error, 'count': count}
                for error, count in most_common_errors
            ],
            'error_rate': len(self.error_counts) / max(total_errors, 1)
        }

# Validation middleware for agents
class ValidationMiddleware:
    """Middleware for comprehensive validation in agent workflows."""
    
    def __init__(self):
        self.error_handler = ValidationErrorHandler()
        self.validation_cache: Dict[str, bool] = {}
    
    async def validate_input(self, data: Any, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Validate input data with caching and error handling."""
        
        # Generate cache key
        cache_key = f"{model_class.__name__}:{hash(str(data))}"
        
        if cache_key in self.validation_cache:
            return {'valid': True, 'cached': True}
        
        try:
            # Attempt validation
            validated_instance = model_class(**data if isinstance(data, dict) else data.__dict__)
            
            # Cache successful validation
            self.validation_cache[cache_key] = True
            
            return {
                'valid': True,
                'data': validated_instance.dict(),
                'model': model_class.__name__,
                'cached': False
            }
            
        except Exception as e:
            # Handle validation failure
            error_report = self.error_handler.handle_validation_error(e, model_class)
            
            return {
                'valid': False,
                'error_report': error_report,
                'cached': False
            }
    
    def clear_cache(self):
        """Clear validation cache."""
        self.validation_cache.clear()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return {
            'cache_size': len(self.validation_cache),
            'cache_hit_types': list(set(
                key.split(':')[0] for key in self.validation_cache.keys()
            ))
        }
```

---

## **Part 3: Production Patterns (400 lines)**

### **Scalable Agent Architecture**

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

@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol defining agent interface contracts."""
    
    async def process_request(self, request: BaseModel) -> BaseModel:
        """Process a request and return structured result."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        """Return performance metrics."""
        ...

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
        
    @abstractmethod
    async def _process_core_request(self, request: BaseModel) -> BaseModel:
        """Core request processing logic - must be implemented by subclasses."""
        pass
    
    async def process_request(self, request: BaseModel) -> Dict[str, Any]:
        """Process request with comprehensive monitoring and error handling."""
        
        start_time = datetime.now(timezone.utc)
        request_id = str(uuid.uuid4())
        
        self.logger.info(f"Processing request {request_id} of type {type(request).__name__}")
        
        try:
            # Pre-processing validation
            await self._validate_request(request)
            
            # Core processing with timeout
            result = await asyncio.wait_for(
                self._process_core_request(request),
                timeout=self.config.get('request_timeout_seconds', 30)
            )
            
            # Post-processing
            processed_result = await self._post_process_result(result)
            
            # Update success metrics
            self._update_success_metrics(start_time, request_id)
            
            return {
                'success': True,
                'result': processed_result.dict() if hasattr(processed_result, 'dict') else processed_result,
                'request_id': request_id,
                'processing_time_ms': self._calculate_processing_time(start_time),
                'agent_name': self.name
            }
            
        except asyncio.TimeoutError:
            self._update_error_metrics(start_time, "timeout", request_id)
            self.logger.error(f"Request {request_id} timed out")
            return self._create_error_response(request_id, "Request timed out", "timeout")
            
        except Exception as e:
            self._update_error_metrics(start_time, "processing_error", request_id)
            self.logger.error(f"Request {request_id} failed: {str(e)}")
            return self._create_error_response(request_id, str(e), "processing_error")
    
    async def _validate_request(self, request: BaseModel) -> None:
        """Validate incoming request."""
        # Validation is typically handled by Pydantic automatically
        # Additional custom validation can be added here
        if hasattr(request, 'validate_business_rules'):
            await request.validate_business_rules()
    
    async def _post_process_result(self, result: BaseModel) -> BaseModel:
        """Post-process results before returning."""
        # Add metadata, sanitize sensitive data, etc.
        if hasattr(result, 'add_processing_metadata'):
            result.add_processing_metadata(
                processed_by=self.name,
                processed_at=datetime.now(timezone.utc)
            )
        return result
    
    def _calculate_processing_time(self, start_time: datetime) -> float:
        """Calculate processing time in milliseconds."""
        end_time = datetime.now(timezone.utc)
        return (end_time - start_time).total_seconds() * 1000
    
    def _update_success_metrics(self, start_time: datetime, request_id: str) -> None:
        """Update metrics for successful request."""
        processing_time = self._calculate_processing_time(start_time)
        
        self.metrics.total_requests += 1
        self.metrics.successful_requests += 1
        self.metrics.last_request_timestamp = datetime.now(timezone.utc)
        
        # Update response time metrics
        self._request_times.append(processing_time)
        self._update_percentile_metrics()
        
        self.logger.info(f"Request {request_id} completed successfully in {processing_time:.2f}ms")
    
    def _update_error_metrics(self, start_time: datetime, error_type: str, request_id: str) -> None:
        """Update metrics for failed request."""
        processing_time = self._calculate_processing_time(start_time)
        
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.error_rate_percent = (self.metrics.failed_requests / self.metrics.total_requests) * 100
        
        self._request_times.append(processing_time)
        
        self.logger.warning(f"Request {request_id} failed ({error_type}) after {processing_time:.2f}ms")
    
    def _update_percentile_metrics(self) -> None:
        """Update percentile response time metrics."""
        if not self._request_times:
            return
        
        sorted_times = sorted(self._request_times)
        n = len(sorted_times)
        
        self.metrics.average_response_time_ms = sum(sorted_times) / n
        self.metrics.p95_response_time_ms = sorted_times[int(n * 0.95)] if n > 0 else 0.0
        self.metrics.p99_response_time_ms = sorted_times[int(n * 0.99)] if n > 0 else 0.0
        
        # Keep only last 1000 measurements to prevent memory growth
        if len(self._request_times) > 1000:
            self._request_times = self._request_times[-1000:]
    
    def _create_error_response(self, request_id: str, error_message: str, error_type: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            'success': False,
            'error': {
                'message': error_message,
                'type': error_type,
                'request_id': request_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            'agent_name': self.name
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for monitoring systems."""
        
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - self.start_time).total_seconds()
        
        # Basic health indicators
        health_status = "healthy"
        health_issues = []
        
        # Check error rate
        if self.metrics.error_rate_percent > 10:
            health_status = "degraded"
            health_issues.append("High error rate")
        
        # Check response times
        if self.metrics.p95_response_time_ms > 5000:  # 5 seconds
            health_status = "degraded"
            health_issues.append("High response times")
        
        # Check if agent is responding
        time_since_last_request = None
        if self.metrics.last_request_timestamp:
            time_since_last_request = (current_time - self.metrics.last_request_timestamp).total_seconds()
            
            # If no requests in last hour, might indicate issues
            if time_since_last_request > 3600:
                health_issues.append("No recent requests")
        
        return {
            'agent_name': self.name,
            'status': health_status,
            'uptime_seconds': uptime,
            'issues': health_issues,
            'metrics': self.metrics.dict(),
            'timestamp': current_time.isoformat(),
            'version': self.config.get('version', '1.0.0')
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics."""
        current_time = datetime.now(timezone.utc)
        uptime = (current_time - self.start_time).total_seconds()
        
        return {
            'agent_name': self.name,
            'uptime_seconds': uptime,
            'metrics': self.metrics.dict(),
            'config': {
                'request_timeout_seconds': self.config.get('request_timeout_seconds', 30),
                'max_workers': self.config.get('max_workers', 4)
            },
            'timestamp': current_time.isoformat()
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of agent resources."""
        self.logger.info(f"Shutting down agent {self.name}")
        self._executor.shutdown(wait=True)
        self._health_status = "shutdown"

class ProductionResearchAgent(ProductionAgentBase):
    """Production-ready research agent implementation."""
    
    def __init__(self, name: str = "production_research_agent", config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # Initialize PydanticAI agent
        self.pydantic_agent = Agent(
            model='openai:gpt-4',
            result_type=ResearchResult,
            system_prompt="""You are a professional research agent optimized for production use.
            Provide structured, validated research results with high reliability and performance.
            Focus on accuracy, completeness, and proper source validation.""",
            deps_type=ExecutionContext
        )
        
        # Production-specific tools
        self._setup_production_tools()
    
    def _setup_production_tools(self) -> None:
        """Setup production-optimized tools with caching and rate limiting."""
        
        @self.pydantic_agent.tool
        async def production_web_search(ctx: RunContext[ExecutionContext], query: str, max_results: int = 10) -> Dict[str, Any]:
            """Production web search with rate limiting and caching."""
            
            # Input validation
            if not query.strip():
                raise ValueError("Search query cannot be empty")
            
            if len(query) > 500:
                raise ValueError("Search query too long (max 500 characters)")
            
            if max_results < 1 or max_results > 20:
                raise ValueError("max_results must be between 1 and 20")
            
            # Simulate production search with realistic data
            search_results = {
                'query': query,
                'total_results': max_results,
                'results': [
                    {
                        'title': f'Research: {query} - Result {i+1}',
                        'url': f'https://academic-source-{i+1}.com/research/{hash(query) % 10000}',
                        'snippet': f'Comprehensive analysis of {query} with detailed findings and methodology.',
                        'relevance_score': max(0.9 - (i * 0.05), 0.3),
                        'publication_date': (datetime.now() - timedelta(days=i*30)).isoformat(),
                        'source_type': 'academic' if i % 2 == 0 else 'industry'
                    }
                    for i in range(max_results)
                ],
                'search_time_ms': 150 + (max_results * 20),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self.logger.debug(f"Web search completed: {query} ({max_results} results)")
            return search_results
        
        @self.pydantic_agent.tool
        async def analyze_source_credibility(ctx: RunContext[ExecutionContext], source_url: str) -> Dict[str, Any]:
            """Analyze source credibility with production-grade assessment."""
            
            # URL validation
            if not source_url or not source_url.startswith(('http://', 'https://')):
                raise ValueError("Invalid source URL format")
            
            # Simulate credibility analysis
            domain = source_url.split('/')[2].lower()
            
            # Production credibility scoring
            base_score = 0.7
            
            # Domain reputation scoring
            high_reputation_domains = ['nature.com', 'science.org', 'acm.org', 'ieee.org']
            medium_reputation_domains = ['medium.com', 'forbes.com', 'techcrunch.com']
            
            if any(reputable in domain for reputable in high_reputation_domains):
                base_score = 0.95
            elif any(reputable in domain for reputable in medium_reputation_domains):
                base_score = 0.8
            elif domain.endswith('.edu') or domain.endswith('.gov'):
                base_score = 0.9
            elif domain.endswith('.org'):
                base_score = 0.75
            
            credibility_assessment = {
                'source_url': source_url,
                'domain': domain,
                'credibility_score': base_score,
                'domain_authority': base_score * 100,
                'publication_type': 'academic' if base_score > 0.85 else 'commercial',
                'peer_review_status': 'likely' if base_score > 0.9 else 'unknown',
                'trust_indicators': {
                    'https_enabled': source_url.startswith('https://'),
                    'established_domain': base_score > 0.8,
                    'academic_affiliation': domain.endswith('.edu'),
                    'government_source': domain.endswith('.gov')
                },
                'recommendation': 'highly_reliable' if base_score > 0.9 else 'reliable' if base_score > 0.7 else 'use_with_caution',
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return credibility_assessment
    
    async def _process_core_request(self, request: BaseModel) -> ResearchResult:
        """Core research processing with production optimization."""
        
        if isinstance(request, str):
            research_query = request
            context = ExecutionContext()
        else:
            research_query = getattr(request, 'query', str(request))
            context = getattr(request, 'context', ExecutionContext())
        
        try:
            # Execute research with the PydanticAI agent
            result = await self.pydantic_agent.run(
                user_prompt=f"Research the following topic comprehensively: {research_query}",
                deps=context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Research processing failed: {str(e)}")
            
            # Return a structured error result that still conforms to ResearchResult
            return ResearchResult(
                topic=research_query,
                key_findings=[f"Research failed due to: {str(e)}"],
                confidence_score=0.0,
                sources=["Error during research process"],
                priority=TaskPriority.HIGH  # Errors should be high priority
            )

# Production agent factory and management
class ProductionAgentFactory:
    """Factory for creating and managing production agents."""
    
    def __init__(self):
        self.agents: Dict[str, ProductionAgentBase] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_research_agent(self, name: str, config: Dict[str, Any] = None) -> ProductionResearchAgent:
        """Create a production research agent."""
        
        default_config = {
            'request_timeout_seconds': 60,
            'max_workers': 4,
            'version': '1.0.0'
        }
        
        if config:
            default_config.update(config)
        
        agent = ProductionResearchAgent(name, default_config)
        self.agents[name] = agent
        
        self.logger.info(f"Created research agent: {name}")
        return agent
    
    def get_agent(self, name: str) -> Optional[ProductionAgentBase]:
        """Get agent by name."""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self.agents.keys())
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check for all registered agents."""
        
        health_reports = {}
        overall_status = "healthy"
        
        for name, agent in self.agents.items():
            health_report = await agent.health_check()
            health_reports[name] = health_report
            
            if health_report['status'] != 'healthy':
                overall_status = "degraded"
        
        return {
            'overall_status': overall_status,
            'agent_count': len(self.agents),
            'agents': health_reports,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown_all(self) -> None:
        """Shutdown all agents gracefully."""
        self.logger.info("Shutting down all agents")
        
        for name, agent in self.agents.items():
            try:
                await agent.shutdown()
                self.logger.info(f"Agent {name} shut down successfully")
            except Exception as e:
                self.logger.error(f"Error shutting down agent {name}: {str(e)}")
        
        self.agents.clear()
```

---

## **Part 4: Integration & Error Handling (400 lines)**

### **Comprehensive Error Management**

Production PydanticAI applications require sophisticated error handling strategies that maintain system stability while providing meaningful feedback.

```python
# Advanced error handling and recovery patterns
from enum import Enum
from typing import Callable, Awaitable, TypeVar, Union
import asyncio
from functools import wraps
import traceback
from dataclasses import dataclass, field

T = TypeVar('T')
R = TypeVar('R')

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

class AgentError(Exception):
    """Base exception class for agent-specific errors."""
    
    def __init__(self, message: str, context: ErrorContext = None, cause: Exception = None):
        super().__init__(message)
        self.context = context or ErrorContext()
        self.context.message = message
        self.context.stack_trace = traceback.format_exc()
        self.__cause__ = cause

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

class TimeoutAgentError(AgentError):
    """Error specific to timeout scenarios."""
    
    def __init__(self, message: str, timeout_seconds: float = None, **kwargs):
        context = ErrorContext(
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.HIGH,
            details={'timeout_seconds': timeout_seconds}
        )
        super().__init__(message, context, **kwargs)

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
    
    def classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify an error into category and severity."""
        
        error_type = type(error)
        
        # Check direct matches first
        for error_types, (category, severity) in self.classification_rules.items():
            if error_type in error_types:
                return category, severity
        
        # Check inheritance
        for error_types, (category, severity) in self.classification_rules.items():
            if any(issubclass(error_type, et) for et in error_types):
                return category, severity
        
        # Analyze error message for additional clues
        error_message = str(error).lower()
        
        if any(word in error_message for word in ['timeout', 'deadline', 'expired']):
            return ErrorCategory.TIMEOUT, ErrorSeverity.HIGH
        elif any(word in error_message for word in ['network', 'connection', 'socket']):
            return ErrorCategory.NETWORK, ErrorSeverity.HIGH
        elif any(word in error_message for word in ['rate limit', 'throttle', 'quota']):
            return ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM
        elif any(word in error_message for word in ['auth', 'token', 'credential']):
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM

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
        """Calculate delay before next retry attempt."""
        return self.base_delay * (self.backoff_multiplier ** retry_count)
    
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
                
            except Exception as e:
                # Wrap other exceptions in AgentError
                classifier = ErrorClassifier()
                error_category, error_severity = classifier.classify_error(e)
                
                # Use decorator parameters as defaults
                final_category = error_category if error_category != ErrorCategory.UNKNOWN else category
                final_severity = error_severity if error_severity != ErrorSeverity.MEDIUM else severity
                
                context = ErrorContext(
                    category=final_category,
                    severity=final_severity,
                    message=str(e),
                    user_facing_message=user_message or "An error occurred while processing your request"
                )
                
                raise AgentError(str(e), context, e)
        
        return wrapper
    return decorator

# Circuit breaker pattern for external service resilience
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout_seconds': self.config.recovery_timeout_seconds,
                'success_threshold': self.config.success_threshold
            }
        }

# Integration patterns for external services
class ExternalServiceIntegration:
    """Base class for external service integrations with comprehensive error handling."""
    
    def __init__(self, service_name: str, base_url: str, circuit_breaker_config: CircuitBreakerConfig = None):
        self.service_name = service_name
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker(service_name, circuit_breaker_config)
        self.retry_strategy = RetryStrategy(max_retries=3, base_delay=1.0)
        self.logger = logging.getLogger(f"Integration.{service_name}")
    
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
            # Simulate HTTP request
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            # Simulate various failure scenarios for testing
            import random
            if random.random() < 0.1:  # 10% chance of failure
                raise NetworkAgentError(
                    "Simulated network error",
                    endpoint=url,
                    status_code=503
                )
            
            # Simulate successful response
            return {
                'success': True,
                'data': {'message': f'Success from {self.service_name}', 'endpoint': endpoint},
                'status_code': 200,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        return await self.circuit_breaker.call(_make_http_request)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the external service."""
        try:
            response = await self.make_request('health', method='GET')
            
            return {
                'service_name': self.service_name,
                'status': 'healthy',
                'response_time_ms': 50,  # Simulated
                'circuit_breaker': self.circuit_breaker.get_status()
            }
            
        except Exception as e:
            return {
                'service_name': self.service_name,
                'status': 'unhealthy',
                'error': str(e),
                'circuit_breaker': self.circuit_breaker.get_status()
            }
```

### **Integration Testing and Monitoring**

```python
# Integration testing and monitoring for production environments
import pytest
from unittest.mock import AsyncMock, patch
from typing import AsyncGenerator

class IntegrationTestSuite:
    """Comprehensive integration testing for PydanticAI agents."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def test_agent_validation(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Test agent validation capabilities."""
        
        test_cases = [
            # Valid inputs
            {
                'name': 'valid_research_request',
                'input': 'Research machine learning applications in healthcare',
                'should_pass': True
            },
            # Invalid inputs
            {
                'name': 'empty_request',
                'input': '',
                'should_pass': False
            },
            {
                'name': 'extremely_long_request',
                'input': 'x' * 10000,
                'should_pass': False
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                result = await agent.process_request(test_case['input'])
                
                test_result = {
                    'test_name': test_case['name'],
                    'expected_pass': test_case['should_pass'],
                    'actual_pass': result.get('success', False),
                    'result': result,
                    'status': 'pass' if (result.get('success', False) == test_case['should_pass']) else 'fail'
                }
                
            except Exception as e:
                test_result = {
                    'test_name': test_case['name'],
                    'expected_pass': test_case['should_pass'],
                    'actual_pass': False,
                    'error': str(e),
                    'status': 'pass' if not test_case['should_pass'] else 'fail'
                }
            
            results.append(test_result)
        
        return {
            'test_type': 'validation',
            'agent_name': agent.name,
            'total_tests': len(test_cases),
            'passed_tests': len([r for r in results if r['status'] == 'pass']),
            'results': results
        }
    
    async def test_error_handling(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Test agent error handling capabilities."""
        
        error_scenarios = [
            {
                'name': 'network_timeout',
                'setup': lambda: self._simulate_timeout_error(),
                'expected_category': ErrorCategory.TIMEOUT
            },
            {
                'name': 'validation_error',
                'setup': lambda: self._simulate_validation_error(),
                'expected_category': ErrorCategory.VALIDATION
            }
        ]
        
        results = []
        
        for scenario in error_scenarios:
            try:
                with patch.object(agent, '_process_core_request', side_effect=scenario['setup']()):
                    result = await agent.process_request("test request")
                    
                    test_result = {
                        'scenario_name': scenario['name'],
                        'error_handled': not result.get('success', True),
                        'result': result,
                        'status': 'pass' if not result.get('success', True) else 'fail'
                    }
                    
            except Exception as e:
                test_result = {
                    'scenario_name': scenario['name'],
                    'error_handled': True,
                    'exception': str(e),
                    'status': 'pass'
                }
            
            results.append(test_result)
        
        return {
            'test_type': 'error_handling',
            'agent_name': agent.name,
            'total_scenarios': len(error_scenarios),
            'passed_scenarios': len([r for r in results if r['status'] == 'pass']),
            'results': results
        }
    
    def _simulate_timeout_error(self) -> Exception:
        """Simulate a timeout error for testing."""
        return TimeoutAgentError("Simulated timeout error", timeout_seconds=30.0)
    
    def _simulate_validation_error(self) -> Exception:
        """Simulate a validation error for testing."""
        return ValidationAgentError("Simulated validation error", field="test_field", value="invalid_value")

# Performance monitoring and metrics collection
class PerformanceMonitor:
    """Monitor agent performance and collect metrics."""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.alert_thresholds = {
            'response_time_ms': 5000,
            'error_rate_percent': 5.0,
            'memory_usage_mb': 1000
        }
    
    def collect_metrics(self, agent: ProductionAgentBase) -> Dict[str, Any]:
        """Collect current performance metrics."""
        
        metrics = agent.get_metrics()
        health_status = asyncio.create_task(agent.health_check())
        
        current_metrics = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'agent_name': agent.name,
            'performance': metrics,
            'alerts': self._check_alerts(metrics)
        }
        
        self.metrics_history.append(current_metrics)
        
        # Keep only last 1000 metrics to prevent memory growth
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return current_metrics
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics against alert thresholds."""
        
        alerts = []
        agent_metrics = metrics.get('metrics', {})
        
        # Check response time
        p95_response_time = agent_metrics.get('p95_response_time_ms', 0)
        if p95_response_time > self.alert_thresholds['response_time_ms']:
            alerts.append({
                'type': 'high_response_time',
                'severity': 'warning',
                'message': f"95th percentile response time ({p95_response_time:.2f}ms) exceeds threshold",
                'threshold': self.alert_thresholds['response_time_ms'],
                'current_value': p95_response_time
            })
        
        # Check error rate
        error_rate = agent_metrics.get('error_rate_percent', 0)
        if error_rate > self.alert_thresholds['error_rate_percent']:
            alerts.append({
                'type': 'high_error_rate',
                'severity': 'warning',
                'message': f"Error rate ({error_rate:.2f}%) exceeds threshold",
                'threshold': self.alert_thresholds['error_rate_percent'],
                'current_value': error_rate
            })
        
        return alerts
    
    def get_performance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate performance report for specified time window."""
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No metrics available for specified time window'}
        
        # Calculate aggregated statistics
        response_times = []
        error_rates = []
        
        for metric in recent_metrics:
            agent_metrics = metric.get('performance', {}).get('metrics', {})
            response_times.append(agent_metrics.get('average_response_time_ms', 0))
            error_rates.append(agent_metrics.get('error_rate_percent', 0))
        
        return {
            'time_window_hours': time_window_hours,
            'metrics_count': len(recent_metrics),
            'performance_summary': {
                'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
                'max_response_time_ms': max(response_times) if response_times else 0,
                'avg_error_rate_percent': sum(error_rates) / len(error_rates) if error_rates else 0,
                'max_error_rate_percent': max(error_rates) if error_rates else 0
            },
            'total_alerts': sum(len(m.get('alerts', [])) for m in recent_metrics)
        }
```

---

## **Part 5: Performance Optimization (300 lines)**

### **Caching and Performance Patterns**

Performance optimization in PydanticAI applications focuses on intelligent caching, request batching, and resource management while maintaining type safety.

```python
# Performance optimization patterns for PydanticAI applications
import asyncio
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from functools import wraps, lru_cache
import hashlib
import json
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import OrderedDict
from dataclasses import dataclass
import weakref

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

@dataclass
class CacheEntry(Generic[V]):
    """Cache entry with metadata for intelligent eviction."""
    value: V
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[float]
    size_bytes: int
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if not self.ttl_seconds:
            return False
        
        age = datetime.now(timezone.utc) - self.created_at
        return age.total_seconds() > self.ttl_seconds
    
    def update_access(self) -> None:
        """Update access statistics."""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1

class IntelligentCache(Generic[K, V]):
    """High-performance cache with intelligent eviction strategies."""
    
    def __init__(
        self, 
        max_size: int = 1000,
        default_ttl_seconds: float = 3600,
        max_memory_mb: float = 100
    ):
        self.max_size = max_size
        self.default_ttl_seconds = default_ttl_seconds
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        
        self._cache: OrderedDict[K, CacheEntry[V]] = OrderedDict()
        self._lock = threading.RLock()
        self._total_size_bytes = 0
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_cleanups': 0
        }
    
    def _calculate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            # Fallback estimation
            return len(str(obj)) * 2  # Rough estimate for Unicode
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        while len(self._cache) >= self.max_size or self._total_size_bytes >= self.max_memory_bytes:
            if not self._cache:
                break
            
            key, entry = self._cache.popitem(last=False)  # Remove oldest (LRU)
            self._total_size_bytes -= entry.size_bytes
            self._stats['evictions'] += 1
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            entry = self._cache.pop(key, None)
            if entry:
                self._total_size_bytes -= entry.size_bytes
                self._stats['expired_cleanups'] += 1
    
    def get(self, key: K) -> Optional[V]:
        """Get value from cache with access tracking."""
        with self._lock:
            # Periodic cleanup
            if len(self._cache) > 100 and len(self._cache) % 50 == 0:
                self._cleanup_expired()
            
            entry = self._cache.get(key)
            if not entry:
                self._stats['misses'] += 1
                return None
            
            if entry.is_expired():
                self._cache.pop(key)
                self._total_size_bytes -= entry.size_bytes
                self._stats['misses'] += 1
                self._stats['expired_cleanups'] += 1
                return None
            
            # Update access statistics and move to end (most recently used)
            entry.update_access()
            self._cache.move_to_end(key)
            self._stats['hits'] += 1
            
            return entry.value
    
    def set(self, key: K, value: V, ttl_seconds: float = None) -> None:
        """Set value in cache with intelligent eviction."""
        with self._lock:
            ttl = ttl_seconds or self.default_ttl_seconds
            size_bytes = self._calculate_size(value)
            
            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache.pop(key)
                self._total_size_bytes -= old_entry.size_bytes
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                created_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                access_count=1,
                ttl_seconds=ttl,
                size_bytes=size_bytes
            )
            
            # Evict if necessary before adding
            self._evict_lru()
            
            # Add new entry
            self._cache[key] = entry
            self._total_size_bytes += size_bytes
    
    def invalidate(self, key: K) -> bool:
        """Remove specific key from cache."""
        with self._lock:
            entry = self._cache.pop(key, None)
            if entry:
                self._total_size_bytes -= entry.size_bytes
                return True
            return False
    
    def clear(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()
            self._total_size_bytes = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_mb': self._total_size_bytes / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'hit_rate_percent': hit_rate,
                'stats': self._stats.copy()
            }

def cached_method(
    ttl_seconds: float = 3600,
    cache_size: int = 1000,
    key_generator: Callable = None
):
    """Decorator for caching method results with intelligent cache management."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cache = IntelligentCache[str, T](max_size=cache_size, default_ttl_seconds=ttl_seconds)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args[1:])  # Skip 'self'
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            cache.set(cache_key, result)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # Generate cache key (same logic as async)
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args[1:])
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result
        
        # Add cache management methods
        if asyncio.iscoroutinefunction(func):
            async_wrapper.cache = cache
            async_wrapper.clear_cache = cache.clear
            async_wrapper.get_cache_stats = cache.get_stats
            return async_wrapper
        else:
            sync_wrapper.cache = cache
            sync_wrapper.clear_cache = cache.clear
            sync_wrapper.get_cache_stats = cache.get_stats
            return sync_wrapper
    
    return decorator

class BatchProcessor(Generic[T, R]):
    """Batch processing for improved throughput and resource utilization."""
    
    def __init__(
        self,
        batch_size: int = 10,
        max_wait_time_seconds: float = 1.0,
        max_concurrent_batches: int = 3
    ):
        self.batch_size = batch_size
        self.max_wait_time_seconds = max_wait_time_seconds
        self.max_concurrent_batches = max_concurrent_batches
        
        self._pending_items: List[T] = []
        self._pending_futures: List[asyncio.Future] = []
        self._batch_timer: Optional[asyncio.Task] = None
        self._processing_lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent_batches)
        
        self._stats = {
            'total_items_processed': 0,
            'total_batches_processed': 0,
            'average_batch_size': 0.0,
            'total_processing_time_ms': 0.0
        }
    
    async def submit(self, item: T, processor: Callable[[List[T]], Awaitable[List[R]]]) -> R:
        """Submit item for batch processing."""
        
        async with self._processing_lock:
            # Create future for this item
            future: asyncio.Future[R] = asyncio.Future()
            
            self._pending_items.append(item)
            self._pending_futures.append(future)
            
            # Start timer if this is the first item
            if len(self._pending_items) == 1:
                self._batch_timer = asyncio.create_task(
                    self._wait_and_process(processor)
                )
            
            # Process immediately if batch is full
            if len(self._pending_items) >= self.batch_size:
                await self._process_batch(processor)
        
        return await future
    
    async def _wait_and_process(self, processor: Callable[[List[T]], Awaitable[List[R]]]) -> None:
        """Wait for batch timeout and process."""
        try:
            await asyncio.sleep(self.max_wait_time_seconds)
            async with self._processing_lock:
                if self._pending_items:
                    await self._process_batch(processor)
        except asyncio.CancelledError:
            pass  # Timer was cancelled due to immediate processing
    
    async def _process_batch(self, processor: Callable[[List[T]], Awaitable[List[R]]]) -> None:
        """Process current batch of items."""
        if not self._pending_items:
            return
        
        # Extract current batch
        batch_items = self._pending_items[:]
        batch_futures = self._pending_futures[:]
        
        self._pending_items.clear()
        self._pending_futures.clear()
        
        # Cancel timer if active
        if self._batch_timer and not self._batch_timer.done():
            self._batch_timer.cancel()
            self._batch_timer = None
        
        # Process batch with concurrency control
        async with self._semaphore:
            start_time = datetime.now(timezone.utc)
            
            try:
                results = await processor(batch_items)
                
                # Distribute results to futures
                if len(results) == len(batch_futures):
                    for future, result in zip(batch_futures, results):
                        if not future.done():
                            future.set_result(result)
                else:
                    # Handle mismatch between input and output counts
                    error = ValueError(f"Processor returned {len(results)} results for {len(batch_futures)} items")
                    for future in batch_futures:
                        if not future.done():
                            future.set_exception(error)
                
            except Exception as e:
                # Set exception for all futures
                for future in batch_futures:
                    if not future.done():
                        future.set_exception(e)
            
            finally:
                # Update statistics
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                self._stats['total_items_processed'] += len(batch_items)
                self._stats['total_batches_processed'] += 1
                self._stats['total_processing_time_ms'] += processing_time
                self._stats['average_batch_size'] = (
                    self._stats['total_items_processed'] / self._stats['total_batches_processed']
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics."""
        return {
            'configuration': {
                'batch_size': self.batch_size,
                'max_wait_time_seconds': self.max_wait_time_seconds,
                'max_concurrent_batches': self.max_concurrent_batches
            },
            'statistics': self._stats.copy(),
            'current_state': {
                'pending_items': len(self._pending_items),
                'active_timer': self._batch_timer is not None and not self._batch_timer.done()
            }
        }

# Performance-optimized agent implementation
class OptimizedPydanticAgent(ProductionAgentBase):
    """Performance-optimized PydanticAI agent with caching and batching."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        
        # Initialize performance components
        self.result_cache = IntelligentCache[str, ResearchResult](
            max_size=self.config.get('cache_size', 1000),
            default_ttl_seconds=self.config.get('cache_ttl_seconds', 3600),
            max_memory_mb=self.config.get('cache_memory_mb', 100)
        )
        
        self.batch_processor = BatchProcessor[str, ResearchResult](
            batch_size=self.config.get('batch_size', 5),
            max_wait_time_seconds=self.config.get('batch_wait_seconds', 1.0),
            max_concurrent_batches=self.config.get('max_concurrent_batches', 3)
        )
        
        # Thread pool for CPU-intensive operations
        self.cpu_executor = ThreadPoolExecutor(
            max_workers=self.config.get('cpu_workers', 2),
            thread_name_prefix=f"{name}-cpu"
        )
        
        # Setup optimized PydanticAI agent
        self.pydantic_agent = self._create_optimized_agent()
    
    def _create_optimized_agent(self) -> Agent:
        """Create PydanticAI agent with performance optimizations."""
        
        agent = Agent(
            model='openai:gpt-4',
            result_type=ResearchResult,
            system_prompt="""You are a high-performance research agent optimized for 
            batch processing and caching. Provide structured, cacheable results that 
            can be efficiently processed in batches.""",
            deps_type=ExecutionContext
        )
        
        # Add optimized tools
        @agent.tool
        @cached_method(ttl_seconds=1800, cache_size=500)  # 30-minute cache
        async def optimized_web_search(ctx: RunContext[ExecutionContext], query: str) -> Dict[str, Any]:
            """Cached web search for improved performance."""
            
            # Simulate optimized search with caching
            return {
                'query': query,
                'results': [
                    {
                        'title': f'Cached Research: {query} - Result {i+1}',
                        'url': f'https://fast-source-{i+1}.com/cached/{abs(hash(query)) % 10000}',
                        'snippet': f'Optimized cached information about {query}.',
                        'relevance_score': 0.95 - (i * 0.05),
                        'cached': True
                    }
                    for i in range(5)
                ],
                'cache_hit': True,
                'response_time_ms': 50  # Fast cached response
            }
        
        return agent
    
    @cached_method(ttl_seconds=3600, cache_size=1000)
    async def _process_core_request(self, request: BaseModel) -> ResearchResult:
        """Cached core processing for identical requests."""
        
        query = str(request)
        
        # Use batch processing for efficiency
        async def batch_processor_func(queries: List[str]) -> List[ResearchResult]:
            """Process multiple queries in batch for efficiency."""
            
            results = []
            for q in queries:
                # Simulate batch processing
                result = ResearchResult(
                    topic=q,
                    key_findings=[
                        f"Optimized finding 1 for: {q}",
                        f"Batch-processed finding 2 for: {q}",
                        f"Cached result finding 3 for: {q}"
                    ],
                    confidence_score=0.9,
                    sources=[
                        f"https://batch-source-1.com/research/{abs(hash(q)) % 1000}",
                        f"https://batch-source-2.com/analysis/{abs(hash(q)) % 1000}"
                    ],
                    priority=TaskPriority.MEDIUM
                )
                results.append(result)
            
            return results
        
        # Submit to batch processor
        return await self.batch_processor.submit(query, batch_processor_func)
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        
        base_metrics = await super().get_metrics()
        
        # Add optimization-specific metrics
        optimization_metrics = {
            'cache_stats': self.result_cache.get_stats(),
            'batch_stats': self.batch_processor.get_stats(),
            'thread_pool_stats': {
                'active_threads': self.cpu_executor._threads,
                'max_workers': self.cpu_executor._max_workers
            }
        }
        
        return {
            **base_metrics,
            'optimization_metrics': optimization_metrics
        }
    
    async def shutdown(self) -> None:
        """Shutdown with cleanup of optimization resources."""
        await super().shutdown()
        
        # Cleanup optimization resources
        self.result_cache.clear()
        self.cpu_executor.shutdown(wait=True)

# Performance testing and benchmarking
class PerformanceBenchmark:
    """Benchmark suite for PydanticAI agent performance."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
    
    async def benchmark_response_time(
        self, 
        agent: ProductionAgentBase, 
        requests: List[str], 
        concurrent_limit: int = 10
    ) -> Dict[str, Any]:
        """Benchmark agent response times under various loads."""
        
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def timed_request(request: str) -> Dict[str, Any]:
            async with semaphore:
                start_time = datetime.now(timezone.utc)
                
                try:
                    result = await agent.process_request(request)
                    success = result.get('success', False)
                    
                except Exception as e:
                    success = False
                    result = {'error': str(e)}
                
                end_time = datetime.now(timezone.utc)
                response_time_ms = (end_time - start_time).total_seconds() * 1000
                
                return {
                    'request': request,
                    'response_time_ms': response_time_ms,
                    'success': success,
                    'result': result
                }
        
        # Execute all requests concurrently
        start_benchmark = datetime.now(timezone.utc)
        task_results = await asyncio.gather(*[timed_request(req) for req in requests])
        end_benchmark = datetime.now(timezone.utc)
        
        # Calculate statistics
        response_times = [r['response_time_ms'] for r in task_results]
        successful_requests = [r for r in task_results if r['success']]
        
        benchmark_result = {
            'agent_name': agent.name,
            'total_requests': len(requests),
            'concurrent_limit': concurrent_limit,
            'total_benchmark_time_ms': (end_benchmark - start_benchmark).total_seconds() * 1000,
            'successful_requests': len(successful_requests),
            'success_rate_percent': (len(successful_requests) / len(requests)) * 100,
            'response_time_stats': {
                'mean_ms': sum(response_times) / len(response_times),
                'min_ms': min(response_times),
                'max_ms': max(response_times),
                'p50_ms': sorted(response_times)[len(response_times) // 2],
                'p95_ms': sorted(response_times)[int(len(response_times) * 0.95)],
                'p99_ms': sorted(response_times)[int(len(response_times) * 0.99)]
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.results.append(benchmark_result)
        return benchmark_result
    
    async def benchmark_cache_performance(self, agent: OptimizedPydanticAgent) -> Dict[str, Any]:
        """Benchmark cache hit rates and performance impact."""
        
        test_queries = [
            "AI in healthcare",
            "machine learning applications", 
            "AI in healthcare",  # Duplicate for cache hit
            "blockchain technology",
            "machine learning applications",  # Another duplicate
        ]
        
        # Clear cache to start fresh
        if hasattr(agent, 'result_cache'):
            agent.result_cache.clear()
        
        cache_results = []
        
        for query in test_queries:
            start_time = datetime.now(timezone.utc)
            result = await agent.process_request(query)
            end_time = datetime.now(timezone.utc)
            
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            cache_results.append({
                'query': query,
                'response_time_ms': response_time_ms,
                'success': result.get('success', False)
            })
        
        # Get final cache stats
        cache_stats = agent.result_cache.get_stats() if hasattr(agent, 'result_cache') else {}
        
        return {
            'test_queries': len(test_queries),
            'unique_queries': len(set(test_queries)),
            'expected_cache_hits': len(test_queries) - len(set(test_queries)),
            'cache_stats': cache_stats,
            'query_results': cache_results,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
```

---

## **Part 6: Comprehensive Quiz (200 lines)**

### **Knowledge Assessment and Practical Applications**

This comprehensive quiz tests understanding of PydanticAI concepts, patterns, and production implementation strategies.

**Section A: Foundational Concepts (25 questions)**

1. **What is the primary advantage of PydanticAI's type-safe approach over traditional agent frameworks?**
   a) Faster execution speed
   b) Automatic validation and structured outputs with compile-time type checking
   c) Lower memory consumption
   d) Simplified deployment process

2. **Which Pydantic field constraint ensures a float value is between 0.0 and 1.0?**
   a) `Field(min=0.0, max=1.0)`
   b) `Field(ge=0.0, le=1.0)`
   c) `Field(range=[0.0, 1.0])`
   d) `Field(bounds=(0.0, 1.0))`

3. **What happens when a PydanticAI tool receives input that fails validation?**
   a) The tool returns None silently
   b) A ValidationError is raised with detailed error information
   c) The agent continues with default values
   d) The entire agent system shuts down

4. **Which decorator is used to define tools for PydanticAI agents?**
   a) `@agent.function`
   b) `@agent.tool`
   c) `@pydantic.validator`
   d) `@tool.register`

5. **What is the purpose of the `RunContext` type in PydanticAI tools?**
   a) To provide runtime configuration and dependencies
   b) To cache tool execution results
   c) To handle error logging automatically
   d) To manage concurrent tool execution

**Section B: Advanced Validation (25 questions)**

6. **Which validation approach allows cross-field validation in Pydantic models?**
   a) `@validator`
   b) `@root_validator`
   c) `@field_validator`
   d) `@cross_validator`

7. **What is the correct way to implement a custom validator that checks email domain restrictions?**
   a) Use regex in Field definition
   b) Implement `@validator('email')` with custom logic
   c) Use built-in email validator only
   d) Override `__init__` method

8. **How should you handle validation errors in production PydanticAI agents?**
   a) Log errors and continue processing
   b) Return structured error responses with user-friendly messages
   c) Crash fast to prevent data corruption
   d) Retry automatically until validation passes

9. **Which pattern is recommended for implementing conditional validation based on other field values?**
   a) Multiple `@validator` decorators
   b) `@root_validator` with conditional logic
   c) Custom `__post_init__` method
   d) External validation service calls

10. **What is the advantage of using enum types in PydanticAI models?**
    a) Better performance
    b) Automatic serialization/deserialization with type safety
    c) Reduced memory usage
    d) Simplified database integration

**Section C: Production Patterns (25 questions)**

11. **Which pattern is essential for building scalable PydanticAI agents in production?**
    a) Singleton pattern for agent instances
    b) Circuit breaker pattern for external service resilience
    c) Observer pattern for event handling
    d) Factory pattern for model creation

12. **What is the recommended approach for handling timeouts in production PydanticAI agents?**
    a) Use global timeout settings
    b) Implement `asyncio.wait_for()` with graceful error handling
    c) Let the system handle timeouts automatically
    d) Disable timeouts for reliability

13. **How should production PydanticAI agents handle concurrent requests?**
    a) Process requests sequentially for safety
    b) Use semaphores and rate limiting for controlled concurrency
    c) Allow unlimited concurrent processing
    d) Queue all requests for batch processing

14. **Which metric is most important for monitoring PydanticAI agent health in production?**
    a) CPU usage percentage
    b) Request success rate and response time percentiles
    c) Memory consumption only
    d) Number of active connections

15. **What is the best practice for managing agent configuration in production environments?**
    a) Hard-code configuration values
    b) Use environment variables with validation and defaults
    c) Store configuration in database
    d) Read configuration from code comments

**Section D: Error Handling and Integration (25 questions)**

16. **Which error handling pattern provides the most robust recovery mechanism?**
    a) Try-catch with generic exception handling
    b) Exponential backoff with circuit breaker pattern
    c) Immediate retry on any failure
    d) Fail-fast without recovery attempts

17. **How should PydanticAI agents handle external service failures?**
    a) Return empty results
    b) Use circuit breaker pattern with fallback responses
    c) Cache last successful response indefinitely
    d) Terminate agent processing

18. **What is the recommended approach for logging errors in production PydanticAI agents?**
    a) Print statements for debugging
    b) Structured logging with error context and correlation IDs
    c) Log only critical errors
    d) Send errors directly to monitoring systems

19. **Which integration pattern ensures type safety when calling external APIs?**
    a) Direct HTTP client usage
    b) Pydantic models for request/response validation
    c) JSON schema validation only
    d) Manual data type checking

20. **How should you implement retry logic for transient failures?**
    a) Fixed delay between retries
    b) Exponential backoff with jitter and maximum retry limits
    c) Immediate retry until success
    d) No retry for any failures

**Section E: Performance Optimization (20 questions)**

21. **Which caching strategy is most effective for PydanticAI agent responses?**
    a) Simple in-memory dictionary
    b) LRU cache with TTL and intelligent eviction
    c) Database-backed persistent cache
    d) No caching to ensure fresh data

22. **What is the benefit of batch processing in PydanticAI applications?**
    a) Simplified error handling
    b) Improved throughput and resource utilization
    c) Better security
    d) Easier debugging

23. **How should you optimize PydanticAI model validation performance?**
    a) Disable validation in production
    b) Use field-level caching and validation shortcuts
    c) Validate only critical fields
    d) Move validation to client side

24. **Which approach minimizes memory usage in large-scale PydanticAI deployments?**
    a) Load all models into memory at startup
    b) Implement lazy loading with weak references and cleanup
    c) Use only primitive data types
    d) Disable garbage collection

25. **What is the most effective way to monitor PydanticAI agent performance?**
    a) Manual log analysis
    b) Automated metrics collection with alerts and dashboards
    c) Periodic performance tests only
    d) User feedback collection

---

## **Answer Key and Explanations**

**Section A: Foundational Concepts**
1. **b** - Automatic validation and structured outputs with compile-time type checking is PydanticAI's core advantage
2. **b** - `ge` (greater than or equal) and `le` (less than or equal) provide inclusive bounds
3. **b** - ValidationError with detailed information helps debugging and user experience
4. **b** - `@agent.tool` is the standard decorator for PydanticAI tool definitions
5. **a** - RunContext provides runtime configuration, dependencies, and execution context

**Section B: Advanced Validation**
6. **b** - `@root_validator` enables validation across multiple fields
7. **b** - Custom `@validator` decorators provide the most flexibility for complex validation logic
8. **b** - Structured error responses maintain user experience while providing debugging information
9. **b** - `@root_validator` accesses all field values for conditional validation logic
10. **b** - Enums provide type safety with automatic serialization support

**Section C: Production Patterns**
11. **b** - Circuit breaker pattern prevents cascade failures and enables graceful degradation
12. **b** - `asyncio.wait_for()` with proper exception handling provides controlled timeout management
13. **b** - Semaphores and rate limiting prevent resource exhaustion while maintaining performance
14. **b** - Success rate and response times are key indicators of agent reliability and performance
15. **b** - Environment variables with validation provide flexibility and security

**Section D: Error Handling and Integration**
16. **b** - Exponential backoff with circuit breaker provides the most robust recovery mechanism
17. **b** - Circuit breaker with fallback maintains service availability during outages
18. **b** - Structured logging with context enables effective monitoring and debugging
19. **b** - Pydantic models ensure type safety throughout the integration chain
20. **b** - Exponential backoff with jitter and limits prevents overwhelming failing services

**Section E: Performance Optimization**
21. **b** - LRU cache with TTL provides optimal balance of performance and memory management
22. **b** - Batch processing improves throughput by reducing overhead and enabling efficient resource usage
23. **b** - Field-level optimization and intelligent validation shortcuts maintain safety while improving performance
24. **b** - Lazy loading with proper cleanup prevents memory leaks in long-running applications
25. **b** - Automated monitoring provides real-time visibility into agent performance and health

---

## **Key Takeaways and Best Practices**

### **Essential PydanticAI Principles**
1. **Type safety first** - Use comprehensive type hints and validation throughout your agent architecture
2. **Validation at boundaries** - Implement rigorous input/output validation to prevent runtime errors
3. **Structured error handling** - Design error responses that provide meaningful feedback for both users and systems
4. **Performance optimization** - Implement caching, batching, and resource management for production scalability
5. **Monitoring and observability** - Include comprehensive metrics and health checks from the beginning

### **Production Readiness Checklist**
- ✅ Comprehensive input validation with custom validators
- ✅ Structured error handling with proper classification
- ✅ Circuit breaker pattern for external service integrations
- ✅ Intelligent caching with TTL and eviction policies
- ✅ Concurrent request handling with resource limits
- ✅ Performance monitoring and alerting systems
- ✅ Comprehensive test coverage including error scenarios
- ✅ Documentation of validation rules and error responses

### **Performance Optimization Guidelines**
- **Cache aggressively** but with intelligent eviction strategies
- **Batch similar requests** to improve throughput and reduce overhead
- **Monitor continuously** with automated alerting for performance degradation
- **Profile regularly** to identify bottlenecks and optimization opportunities
- **Test under load** to validate performance characteristics

---

## **Next Steps**

Session 6 explores advanced agent orchestration patterns and enterprise integration strategies, building on the type-safe foundations established in this session. The focus shifts to coordinating multiple PydanticAI agents in complex workflows while maintaining the reliability and performance characteristics demonstrated here.

---

*This session demonstrated comprehensive PydanticAI development patterns, from basic type safety through production-ready performance optimization. The combination of Pydantic's validation framework with thoughtful architecture patterns enables building robust, maintainable agents that scale from prototype to enterprise deployment.*
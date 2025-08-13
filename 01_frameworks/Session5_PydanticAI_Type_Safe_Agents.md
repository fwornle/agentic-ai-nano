# Session 5: PydanticAI Type-Safe Agents
## Modern Python Agent Development with Type Safety

### 🎯 **Session Overview**
PydanticAI represents a paradigm shift in agent development, leveraging Pydantic's robust type system and validation framework to create agents with guaranteed data integrity, structured outputs, and comprehensive error handling. This session provides a deep dive into building production-ready, type-safe agents that scale from prototypes to enterprise systems.

### 📚 **Learning Objectives**
1. **Master PydanticAI architecture** and type-safe agent design patterns
2. **Implement real-time structured output validation** with streaming response validation
3. **Build PromptedOutput control systems** with custom instruction templates and schema management
4. **Apply dependency injection patterns** for testing and production configurations
5. **Integrate model-agnostic interfaces** supporting multiple LLM providers (OpenAI, Gemini, Groq)
6. **Optimize performance** with validation optimization and type-safe testing methodologies
7. **Deploy production features** including monitoring, observability, and enterprise patterns

---

## **Part 1: PydanticAI Foundation (400 lines)**

### **Core Architecture and Type System**

PydanticAI builds on Pydantic's validation framework to ensure data integrity throughout the agent lifecycle. The foundation relies on three key concepts: structured data models, type-safe agents, and validated tool interfaces.

First, let's establish the core imports that power PydanticAI's type-safe agent framework:

```python
# src/session5/pydantic_agents.py - Core Foundation (2025 Enhanced)
from pydantic_ai import Agent, RunContext, PromptedOutput
from pydantic_ai.streaming import StreamingResponse
from pydantic_ai.dependencies import DependencyProvider
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union, Literal, AsyncIterator
from datetime import datetime, timezone
from enum import Enum
import uuid
import asyncio
from abc import ABC, abstractmethod
```

These imports provide the essential building blocks: PydanticAI's agent system, Pydantic's validation framework, and Python's typing system for compile-time type safety.

Next, we define string-based enumerations that ensure consistent values across our agent system:

```python
# Core enumeration types for better type safety
class TaskPriority(str, Enum):
    """Priority levels with explicit string values for serialization."""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
```

The `TaskPriority` enum extends `str` to ensure JSON serialization compatibility while maintaining type safety. This pattern prevents common bugs from typos or inconsistent priority values.

```python
class TaskStatus(str, Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

Similarly, `TaskStatus` provides a controlled vocabulary for task states, enabling reliable state machine implementations and preventing invalid status transitions.

The foundation establishes type-safe data structures that serve as contracts between different agent components. Each model includes comprehensive validation rules and metadata for debugging and monitoring.

Now we establish the foundational models that provide metadata and context tracking for our agents:

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
```

The `AgentMetadata` model tracks essential information about each agent instance. Notice the use of `default_factory` for UUID generation and timestamp creation, ensuring each agent gets a unique identity and creation time. The version field uses regex validation to enforce semantic versioning.

For error handling, we define a structured error model that provides comprehensive debugging information:

```python
class ValidationError(BaseModel):
    """Structured validation error information."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    value: Any = Field(..., description="Invalid value that caused the error")
```

This error model standardizes how validation failures are communicated, making debugging more systematic and enabling automated error handling.

Finally, we define the execution context that carries request metadata throughout the agent lifecycle:

```python
class ExecutionContext(BaseModel):
    """Context information for agent execution."""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
```

The `ExecutionContext` provides request tracking, user identification, and configurable timeouts. The timeout field includes validation constraints (1 to 3600 seconds) to prevent unreasonable execution limits.

### **Real-Time Structured Output Validation (2025 Feature)**

PydanticAI 2025 introduces real-time validation during streaming responses, ensuring schema compliance at each step of the generation process. This prevents malformed outputs and enables early error detection.

#### **Core Streaming Validator Structure**

The `StreamingValidator` class manages real-time validation checkpoints during response generation:

```python
# Foundation class for streaming validation
class StreamingValidator(BaseModel):
    """Real-time validation for streaming agent responses."""
    partial_schema: Dict[str, Any] = Field(default_factory=dict)
    accumulated_tokens: List[str] = Field(default_factory=list)
    validation_checkpoints: List[int] = Field(default_factory=lambda: [10, 25, 50, 100])
    current_position: int = Field(default=0)
```

This validator tracks tokens as they arrive and validates at specific checkpoints (10, 25, 50, 100 tokens) to catch schema violations early without overwhelming the system with constant validation.

#### **Partial Response Validation Logic**

The core validation method processes each incoming token and triggers validation at checkpoints:

```python
def validate_partial_response(self, token: str, target_schema: type[BaseModel]) -> Dict[str, Any]:
    """Validate partial response against target schema."""
    self.accumulated_tokens.append(token)
    self.current_position += 1
    
    # Check validation at predefined checkpoints
    if self.current_position in self.validation_checkpoints:
        partial_text = ''.join(self.accumulated_tokens)
        try:
            # Attempt partial schema validation
            partial_json = self._extract_partial_json(partial_text)
            if partial_json:
                # Validate available fields against schema
                validated_fields = self._validate_available_fields(partial_json, target_schema)
                return {
                    'status': 'valid_partial',
                    'validated_fields': validated_fields,
                    'completion_percentage': len(validated_fields) / len(target_schema.__fields__) * 100
                }
        except Exception as e:
            return {
                'status': 'validation_warning',
                'message': str(e),
                'position': self.current_position
            }
    
    return {'status': 'streaming', 'position': self.current_position}
```

This method accumulates tokens and only validates at checkpoints, providing completion percentage feedback and early warning detection without constant processing overhead.

#### **Robust Partial JSON Extraction**

Extracting valid JSON from incomplete streaming responses requires careful pattern matching:

```python
def _extract_partial_json(self, text: str) -> Optional[Dict[str, Any]]:
    """Extract partial JSON from streaming text."""
    import json
    import re
    
    # Find JSON-like patterns
    json_pattern = r'\{[^{}]*\}'
    matches = re.findall(json_pattern, text)
    
    for match in reversed(matches):  # Try most recent first
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            # Try with closing braces added
            try:
                return json.loads(match + '}')
            except json.JSONDecodeError:
                continue
    
    return None
```

This method uses regex to find JSON-like patterns and attempts parsing, including graceful handling of incomplete JSON by adding closing braces when needed.

#### **Field-Level Validation**

Individual field validation ensures partial responses conform to schema requirements:

```python
def _validate_available_fields(self, partial_data: Dict[str, Any], schema: type[BaseModel]) -> Dict[str, Any]:
    """Validate only the fields present in partial data."""
    validated = {}
    for field_name, field_value in partial_data.items():
        if field_name in schema.__fields__:
            field_info = schema.__fields__[field_name]
            try:
                # Use field's type for validation
                validated[field_name] = field_info.type_(field_value)
            except (ValueError, TypeError) as e:
                validated[field_name] = {'error': str(e), 'value': field_value}
    return validated
```

This validates only fields present in partial data against their schema types, collecting validation errors without stopping the process.

#### **Streaming Response Handler Setup**

The response handler orchestrates the entire streaming validation process:

```python
# Enhanced streaming response handler
class StreamingResponseHandler:
    """Manages streaming responses with real-time validation."""
    
    def __init__(self, target_schema: type[BaseModel]):
        self.target_schema = target_schema
        self.validator = StreamingValidator()
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 1.5,
            'validation_timeout': 30.0
        }
```

The handler combines a validator instance with retry configuration, providing a complete solution for production streaming scenarios.

#### **Core Streaming Processing Loop**

The main processing method handles the complete streaming lifecycle:

```python
async def process_streaming_response(
    self, 
    response_stream: AsyncIterator[str],
    validation_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """Process streaming response with real-time validation."""
    validation_results = []
    accumulated_response = ""
    
    try:
        async for token in response_stream:
            # Real-time validation
            validation_result = self.validator.validate_partial_response(
                token, self.target_schema
            )
            validation_results.append(validation_result)
            accumulated_response += token
            
            # Callback for real-time monitoring
            if validation_callback:
                await validation_callback(token, validation_result)
            
            # Handle validation warnings
            if validation_result['status'] == 'validation_warning':
                await self._handle_validation_warning(
                    validation_result, accumulated_response
                )
        
        # Final validation of complete response
        final_result = await self._final_validation(accumulated_response)
        
        return {
            'response': final_result,
            'validation_log': validation_results,
            'streaming_stats': {
                'total_tokens': len(self.validator.accumulated_tokens),
                'validation_checkpoints': len([r for r in validation_results if r['status'] != 'streaming']),
                'warnings': len([r for r in validation_results if r['status'] == 'validation_warning'])
            }
        }
        
    except Exception as e:
        return await self._handle_streaming_error(e, accumulated_response)
```

This async method processes each token, validates at checkpoints, handles warnings, and provides comprehensive statistics about the streaming validation process.

#### **Validation Warning Handling**

```python
async def _handle_validation_warning(self, warning: Dict[str, Any], partial_response: str) -> None:
    """Handle validation warnings during streaming."""
    # Log warning with context
    print(f"Streaming validation warning at position {warning['position']}: {warning['message']}")
    
    # Could implement retry logic here if needed
    # For now, continue streaming but log the issue
```

Warning handling allows the system to continue processing while logging issues for later analysis and debugging.

#### **Final Validation and Error Handling**

```python
async def _final_validation(self, complete_response: str) -> BaseModel:
    """Perform final validation on complete response."""
    try:
        # Parse complete response as JSON
        import json
        response_data = json.loads(complete_response)
        
        # Validate against target schema
        validated_response = self.target_schema(**response_data)
        return validated_response
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in final response: {e}")
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e}")

async def _handle_streaming_error(self, error: Exception, partial_response: str) -> Dict[str, Any]:
    """Handle errors during streaming validation."""
    return {
        'error': str(error),
        'error_type': type(error).__name__,
        'partial_response': partial_response,
        'validation_log': self.validator.accumulated_tokens,
        'recovery_suggestions': [
            "Check network connection",
            "Verify schema compatibility", 
            "Review token limits",
            "Consider retry with backoff"
        ]
    }
```

The final validation ensures complete response integrity while error handling provides actionable recovery suggestions for troubleshooting production issues.

This streaming validation system provides real-time feedback during response generation, enabling early error detection and improving response quality.

### **Type-Safe Agent Definition**

PydanticAI agents are defined with explicit result types and comprehensive system prompts. This ensures consistent output structure and enables compile-time type checking.

The `ResearchResult` model demonstrates PydanticAI's comprehensive validation capabilities. Let's build it step by step:

**Step 1: Define the basic structure with field constraints**

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
```

This establishes the core data structure with built-in validation: topics must be between 5-200 characters, findings are required (1-20 items), and confidence scores are bounded between 0.0 and 1.0.

**Step 2: Add metadata fields for tracking and context**

```python
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
```

These fields handle source tracking, automatic timestamping, priority classification, and agent metadata. Notice how `default_factory` creates fresh instances for each model.

**Step 3: Implement custom validation for findings quality**

```python
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
```

This validator ensures each finding is substantial (minimum 10 characters) and informative (rejecting placeholder text). It also normalizes whitespace.

**Step 4: Add source format validation**

```python
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
```

Source validation ensures citations follow recognizable patterns (URLs, DOIs, academic references) and meet minimum length requirements.

**Step 5: Implement cross-field validation logic**

```python
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

The root validator ensures logical consistency between confidence scores and source counts - higher confidence claims require more supporting sources.

### **Agent Creation and Configuration**

The agent creation process includes comprehensive configuration for type safety, error handling, and monitoring capabilities.

Now that we have our validation models, let's create a properly configured research agent:

**Step 1: Create the agent factory function**

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
```

This factory function creates a type-safe agent with explicit result validation. The `result_type=ResearchResult` ensures all responses conform to our validation schema.

**Step 2: Implement error-handling execution wrapper**

```python
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

The execution wrapper provides comprehensive error handling and demonstrates how type safety gives us compile-time guarantees about the result structure.

### **PromptedOutput Control (2025 Feature)**

PydanticAI 2025 introduces advanced PromptedOutput control for managing custom instruction templates and enhanced schema management. This enables dynamic output control with external schemas and sophisticated prompt templates.

#### **Advanced Template Foundation**

The instruction template system starts with essential imports and generic type setup:

```python
# Custom instruction templates with dynamic schema management
from pydantic_ai import PromptedOutput, InstructionTemplate
from typing import Type, Generic, TypeVar

T = TypeVar('T', bound=BaseModel)
```

This establishes a type-safe foundation where templates can work with any BaseModel schema type.

#### **Template Class Structure**

```python
class AdvancedInstructionTemplate(Generic[T]):
    """Advanced instruction template with dynamic schema binding."""
    
    def __init__(self, schema_type: Type[T]):
        self.schema_type = schema_type
        self.template_cache = {}
        self.instruction_variants = {}
```

The template class uses Python's Generic system to bind to specific schema types while maintaining caching for performance optimization.

#### **Dynamic Template Generation**

```python
def create_dynamic_template(
    self, 
    task_type: str,
    complexity_level: Literal["simple", "moderate", "complex"] = "moderate",
    domain_specific: bool = False
) -> str:
    """Create dynamic instruction templates based on context."""
    
    cache_key = f"{task_type}_{complexity_level}_{domain_specific}"
    if cache_key in self.template_cache:
            return self.template_cache[cache_key]
        
        # Base instruction template
        base_template = f"""
        You are an expert assistant specialized in {task_type} tasks.
        Your response MUST conform to the following schema:
        
        {self._generate_schema_description()}
        
        Instructions:
        """
        
        # Add complexity-specific instructions
        complexity_instructions = {
            "simple": "Provide concise, direct responses focusing on essential information.",
            "moderate": "Include detailed explanations with supporting context and examples.",
            "complex": "Provide comprehensive analysis with multiple perspectives, edge cases, and detailed reasoning."
        }
        
        base_template += complexity_instructions[complexity_level]
        
        if domain_specific:
            base_template += f"""
            
            Domain-specific requirements:
            - Use technical terminology appropriate for {task_type} domain
            - Include relevant industry standards and best practices
            - Reference authoritative sources when applicable
            """
        
        # Add validation reminders
        base_template += """
        
        CRITICAL REQUIREMENTS:
        - ALL fields in the response schema must be provided
        - Values must pass all field validation constraints
        - Use appropriate data types as specified in the schema
        - Ensure JSON serialization compatibility
        """
        
        self.template_cache[cache_key] = base_template
        return base_template
    
    def _generate_schema_description(self) -> str:
        """Generate human-readable schema description."""
        schema_dict = self.schema_type.schema()
        description = f"Schema: {self.schema_type.__name__}\n"
        
        for field_name, field_info in schema_dict.get('properties', {}).items():
            field_type = field_info.get('type', 'unknown')
            field_desc = field_info.get('description', 'No description')
            required = field_name in schema_dict.get('required', [])
            
            description += f"  - {field_name} ({field_type}): {field_desc}"
            if required:
                description += " [REQUIRED]"
            description += "\n"
        
        return description
    
    def create_conditional_template(
        self,
        conditions: Dict[str, Any],
        fallback_template: Optional[str] = None
    ) -> str:
        """Create conditional templates based on runtime conditions."""
        
        template_parts = []
        
        # Add condition-specific instructions
        if conditions.get('requires_sources', False):
            template_parts.append("""
            SOURCE REQUIREMENTS:
            - Provide credible, verifiable sources for all claims
            - Use recent sources (within last 2 years when possible)
            - Include proper citations in the response
            """)
        
        if conditions.get('requires_validation', True):
            template_parts.append("""
            VALIDATION REQUIREMENTS:
            - Double-check all numerical values
            - Verify logical consistency across response
            - Ensure completeness of required fields
            """)
        
        if conditions.get('streaming_mode', False):
            template_parts.append("""
            STREAMING MODE:
            - Structure response for progressive disclosure
            - Begin with most important information
            - Organize content in logical chunks
            """)
        
        # Combine template parts
        final_template = self._generate_schema_description() + "\n"
        final_template += "\n".join(template_parts)
        
        if not template_parts and fallback_template:
            final_template += fallback_template
        
        return final_template

# Enhanced PromptedOutput control system
class PromptedOutputController:
    """Advanced control system for PromptedOutput with external schema management."""
    
    def __init__(self):
        self.schema_registry = {}
        self.template_registry = {}
        self.output_validators = {}
        self.retry_strategies = {}
    
    def register_schema(
        self, 
        name: str, 
        schema_class: Type[BaseModel],
        validation_rules: Optional[Dict[str, Callable]] = None
    ) -> None:
        """Register external schema for dynamic usage."""
        self.schema_registry[name] = {
            'class': schema_class,
            'validation_rules': validation_rules or {},
            'template_generator': AdvancedInstructionTemplate(schema_class)
        }
    
    def create_prompted_output(
        self,
        schema_name: str,
        context: Dict[str, Any],
        output_config: Optional[Dict[str, Any]] = None
    ) -> PromptedOutput:
        """Create PromptedOutput with advanced control features."""
        
        if schema_name not in self.schema_registry:
            raise ValueError(f"Schema '{schema_name}' not registered")
        
        schema_info = self.schema_registry[schema_name]
        schema_class = schema_info['class']
        template_generator = schema_info['template_generator']
        
        # Generate dynamic instruction template
        instruction_template = template_generator.create_dynamic_template(
            task_type=context.get('task_type', 'general'),
            complexity_level=context.get('complexity', 'moderate'),
            domain_specific=context.get('domain_specific', False)
        )
        
        # Create conditional template based on context
        conditional_template = template_generator.create_conditional_template(
            conditions=context.get('conditions', {}),
            fallback_template=context.get('fallback_template')
        )
        
        # Combine templates
        final_instruction = instruction_template + "\n\n" + conditional_template
        
        # Configure output validation
        output_config = output_config or {}
        validation_config = {
            'strict_mode': output_config.get('strict_validation', True),
            'allow_partial': output_config.get('allow_partial_validation', False),
            'retry_on_failure': output_config.get('retry_on_failure', True),
            'max_retries': output_config.get('max_retries', 3)
        }
        
        # Create PromptedOutput with enhanced configuration
        prompted_output = PromptedOutput(
            schema=schema_class,
            instruction_template=final_instruction,
            validation_config=validation_config,
            metadata={
                'schema_name': schema_name,
                'context': context,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'template_hash': hashlib.md5(final_instruction.encode()).hexdigest()
            }
        )
        
        return prompted_output
    
    def create_multi_schema_output(
        self,
        schema_configs: List[Dict[str, Any]]
    ) -> List[PromptedOutput]:
        """Create multiple PromptedOutputs with coordinated schemas."""
        
        outputs = []
        for config in schema_configs:
            schema_name = config['schema_name']
            context = config.get('context', {})
            output_config = config.get('output_config', {})
            
            # Add coordination context for multi-schema scenarios
            context['multi_schema_mode'] = True
            context['total_schemas'] = len(schema_configs)
            context['schema_index'] = len(outputs)
            
            output = self.create_prompted_output(schema_name, context, output_config)
            outputs.append(output)
        
        return outputs
    
    def validate_output_consistency(
        self,
        outputs: List[Any],
        consistency_rules: Dict[str, Callable]
    ) -> Dict[str, Any]:
        """Validate consistency across multiple outputs."""
        
        validation_results = {
            'consistent': True,
            'violations': [],
            'warnings': [],
            'cross_validation_score': 1.0
        }
        
        for rule_name, rule_func in consistency_rules.items():
            try:
                result = rule_func(outputs)
                if not result.get('passed', True):
                    validation_results['consistent'] = False
                    validation_results['violations'].append({
                        'rule': rule_name,
                        'message': result.get('message', 'Consistency check failed'),
                        'affected_outputs': result.get('affected_indices', [])
                    })
            except Exception as e:
                validation_results['warnings'].append({
                    'rule': rule_name,
                    'error': str(e)
                })
        
        # Calculate overall consistency score
        total_rules = len(consistency_rules)
        violations = len(validation_results['violations'])
        if total_rules > 0:
            validation_results['cross_validation_score'] = max(0, (total_rules - violations) / total_rules)
        
        return validation_results

# Usage examples for PromptedOutput control
async def demonstrate_prompted_output_control():
    """Demonstrate advanced PromptedOutput control features."""
    
    # Initialize controller
    controller = PromptedOutputController()
    
    # Register schemas
    controller.register_schema('research', ResearchResult)
    controller.register_schema('analysis', StatisticalAnalysisInput)
    
    # Create prompted output with advanced context
    context = {
        'task_type': 'research_analysis',
        'complexity': 'complex',
        'domain_specific': True,
        'conditions': {
            'requires_sources': True,
            'requires_validation': True,
            'streaming_mode': True
        }
    }
    
    prompted_output = controller.create_prompted_output('research', context)
    
    # Create multi-schema workflow
    multi_schema_configs = [
        {
            'schema_name': 'research',
            'context': {'task_type': 'literature_review', 'complexity': 'moderate'},
            'output_config': {'strict_validation': True}
        },
        {
            'schema_name': 'analysis',
            'context': {'task_type': 'statistical_analysis', 'complexity': 'complex'},
            'output_config': {'allow_partial_validation': True}
        }
    ]
    
    multi_outputs = controller.create_multi_schema_output(multi_schema_configs)
    
    print(f"Created {len(multi_outputs)} coordinated PromptedOutputs")
    
    return {
        'single_output': prompted_output,
        'multi_outputs': multi_outputs,
        'controller_stats': {
            'registered_schemas': len(controller.schema_registry),
            'template_cache_size': sum(len(info['template_generator'].template_cache) 
                                     for info in controller.schema_registry.values())
        }
    }
```

This PromptedOutput control system enables sophisticated output management with dynamic schemas, conditional templates, and multi-schema coordination for complex agent workflows.

### **Model-Agnostic Integration (2025 Enhanced)**

PydanticAI 2025 provides unified interfaces across multiple LLM providers (OpenAI, Gemini, Groq) with provider-specific optimizations and seamless model switching capabilities.

### **Step 1: Model Provider Imports and Enumerations**

The model-agnostic system starts with essential imports and provider enumeration for type-safe provider selection:

```python
# Model-agnostic provider system imports
from pydantic_ai.providers import ModelProvider, ProviderConfig
from enum import Enum
from typing import Protocol, runtime_checkable
```

These imports provide the foundation for PydanticAI's unified model provider interface.

### **Step 2: Provider Enumeration and Type Safety**

```python
# Supported LLM providers with string enum for JSON serialization
class SupportedProvider(str, Enum):
    """Enumeration of supported LLM providers with type safety."""
    OPENAI = "openai"
    GEMINI = "gemini"  
    GROQ = "groq"
    ANTHROPIC = "anthropic"
```

The string-based enum ensures JSON serialization compatibility while providing type safety for provider selection.

### **Step 3: Unified Model Interface Protocol**

```python
# Protocol defining unified interface for all model providers
@runtime_checkable
class ModelInterface(Protocol):
    """Unified interface ensuring consistent behavior across all model providers."""
    provider_name: str
    model_name: str
    max_tokens: int
    supports_streaming: bool
    supports_function_calling: bool
    
    async def generate(self, prompt: str, **kwargs) -> str: ...
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]: ...
    def get_provider_specific_config(self) -> Dict[str, Any]: ...
```

This protocol ensures all model providers implement consistent methods for generation, streaming, and configuration.

### **Step 4: Provider Configuration Model**

The configuration model provides comprehensive settings with validation for all supported providers:

```python
# Comprehensive configuration model for all providers
class ModelProviderConfig(BaseModel):
    """Validated configuration for model providers with optimization settings."""
    provider: SupportedProvider = Field(..., description="Selected LLM provider")
    model_name: str = Field(..., description="Specific model identifier")
    api_key: Optional[str] = Field(default=None, description="Authentication API key")
    base_url: Optional[str] = Field(default=None, description="Custom API base URL")
    max_tokens: int = Field(default=4096, ge=1, le=32768)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    timeout_seconds: int = Field(default=60, ge=5, le=300)
    retry_attempts: int = Field(default=3, ge=1, le=10)
```

These fields provide comprehensive configuration with validation constraints for safe operation.

### **Step 5: Provider-Specific Optimizations**

```python
    # Provider-specific optimization settings
    provider_optimizations: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
```

Provider optimizations enable custom settings per provider while maintaining type safety.

### **Step 6: Model Provider Factory Foundation**

The factory manages provider creation with default configurations and optimizations for each supported provider:

```python
# Factory for unified model provider management
class ModelProviderFactory:
    """Factory for creating optimized model providers with unified interface."""
    
    # Comprehensive provider defaults with capabilities and optimizations
    PROVIDER_DEFAULTS = {
        SupportedProvider.OPENAI: {
            "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "supports_streaming": True,
            "supports_function_calling": True,
            "optimizations": {
                "use_system_message": True,
                "enable_json_mode": True,
                "parallel_function_calls": True
            }
        }
```

OpenAI configuration includes advanced features like JSON mode and parallel function calling.

### **Step 7: Additional Provider Configurations**

```python
        SupportedProvider.GEMINI: {
            "models": ["gemini-pro", "gemini-pro-vision"],
            "supports_streaming": True,
            "supports_function_calling": True,
            "optimizations": {
                "safety_settings": "block_few",
                "generation_config": {"candidate_count": 1}
            }
        },
        SupportedProvider.GROQ: {
            "models": ["mixtral-8x7b-32768", "llama2-70b-4096"],
            "supports_streaming": True,
            "supports_function_calling": False,
            "optimizations": {
                "high_speed_inference": True,
                "optimized_batching": True
            }
        },
        SupportedProvider.ANTHROPIC: {
            "models": ["claude-3-sonnet", "claude-3-haiku"],
            "supports_streaming": True,
            "supports_function_calling": True,
            "optimizations": {
                "use_xml_formatting": True,
                "enable_citations": True
            }
        }
    }
    ```

Each provider has specific capabilities and optimizations tailored for optimal performance.

### **Step 8: Provider Configuration Creation**

```python
    @classmethod
    def create_provider_config(
        cls,
        provider: SupportedProvider,
        model_name: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> ModelProviderConfig:
        """Create optimized configuration for any supported provider."""
        
        provider_defaults = cls.PROVIDER_DEFAULTS.get(provider, {})
        
        # Auto-select best model if not specified
        if not model_name:
            available_models = provider_defaults.get("models", [])
            model_name = available_models[0] if available_models else "default"
        
        # Merge provider optimizations with custom settings
        optimizations = provider_defaults.get("optimizations", {})
        if custom_config:
            optimizations.update(custom_config.get("optimizations", {}))
        
        # Create validated configuration
        config = ModelProviderConfig(
            provider=provider,
            model_name=model_name,
            max_tokens=custom_config.get("max_tokens", 4096) if custom_config else 4096,
            temperature=custom_config.get("temperature", 0.1) if custom_config else 0.1,
            provider_optimizations=optimizations
        )
        
        return config
    ```

Configuration creation merges provider defaults with custom settings for optimal performance.

### **Step 9: Model Identification and Feature Validation**

```python
    @classmethod
    def get_model_identifier(cls, config: ModelProviderConfig) -> str:
        """Generate PydanticAI-compatible model identifier."""
        return f"{config.provider}:{config.model_name}"
    
    @classmethod
    def validate_provider_support(cls, config: ModelProviderConfig, required_features: List[str]) -> Dict[str, bool]:
        """Validate provider capabilities against application requirements."""
        provider_info = cls.PROVIDER_DEFAULTS.get(config.provider, {})
        
        support_check = {}
        for feature in required_features:
            if feature == "streaming":
                support_check[feature] = provider_info.get("supports_streaming", False)
            elif feature == "function_calling":
                support_check[feature] = provider_info.get("supports_function_calling", False)
            else:
                support_check[feature] = False
        
        return support_check
```

Feature validation ensures compatibility between application requirements and provider capabilities.

### **Step 10: Multi-Provider Agent Factory Foundation**

The multi-provider factory enables agent creation with automatic fallback and performance monitoring:

```python
# Advanced multi-provider agent factory with fallback support
class MultiProviderAgentFactory:
    """Factory for creating agents with multiple provider support and fallback handling."""
    
    def __init__(self):
        self.provider_configs = {}  # Provider configurations
        self.fallback_chain = []    # Fallback order for failures
        self.provider_stats = {}    # Performance statistics
```

The factory maintains provider configurations, fallback chains, and performance statistics for intelligent routing.

### **Step 11: Provider Registration and Statistics**

```python
    def register_provider(
        self, 
        name: str, 
        config: ModelProviderConfig,
        priority: int = 1
    ) -> None:
        """Register a model provider with priority and enable statistics tracking."""
        self.provider_configs[name] = {
            'config': config,
            'priority': priority,
            'enabled': True
        }
        
        # Initialize comprehensive performance tracking
        self.provider_stats[name] = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_time': 0.0,
            'last_used': None
        }
    ```

Provider registration includes priority settings and comprehensive performance tracking for optimization.

### **Step 12: Fallback Chain Configuration**

```python
    def set_fallback_chain(self, provider_names: List[str]) -> None:
        """Configure fallback chain for automatic provider switching on failure."""
        self.fallback_chain = provider_names
```

Fallback chains enable automatic switching to backup providers when primary providers fail.

### **Step 13: Multi-Provider Agent Creation**

```python
    async def create_research_agent(
        self,
        primary_provider: str = "openai",
        result_type: Type[BaseModel] = ResearchResult,
        custom_system_prompt: Optional[str] = None,
        enable_fallback: bool = True
    ) -> Agent:
        """Create research agent with multi-provider support and fallback handling."""
        
        # Validate provider registration
        if primary_provider not in self.provider_configs:
            raise ValueError(f"Provider {primary_provider} not registered")
        
        primary_config = self.provider_configs[primary_provider]['config']
        
        # Validate provider capabilities against requirements
        required_features = ["streaming", "function_calling"]
        feature_support = ModelProviderFactory.validate_provider_support(
            primary_config, required_features
        )
```

Agent creation validates provider capabilities and handles missing features gracefully.

### **Step 14: Feature Validation and Agent Configuration**

```python
        # Validate all required features are supported
        if not all(feature_support.values()):
            missing_features = [f for f, supported in feature_support.items() if not supported]
            print(f"Warning: Provider {primary_provider} missing features: {missing_features}")
        
        # Generate PydanticAI-compatible model identifier
        model_id = ModelProviderFactory.get_model_identifier(primary_config)
        
        # Build provider-optimized system prompt
        system_prompt = custom_system_prompt or self._build_optimized_system_prompt(
            primary_config, result_type
        )
```

Feature validation warns about missing capabilities while model identification creates PydanticAI-compatible strings.

### **Step 15: Agent Configuration and Creation**

```python
        # Create comprehensive agent configuration
        agent_config = {
            'model': model_id,
            'result_type': result_type,
            'system_prompt': system_prompt,
            'deps_type': ExecutionContext
        }
        
        # Apply provider-specific optimizations
        if primary_config.provider_optimizations:
            agent_config.update(primary_config.provider_optimizations)
        
        # Create the configured agent
        agent = Agent(**agent_config)
        
        # Enable fallback handling if configured
        if enable_fallback and self.fallback_chain:
            agent = await self._wrap_with_fallback(agent, result_type, system_prompt)
        
        return agent
    ```

Agent configuration includes provider-specific optimizations and fallback handling for resilient operation.

### **Step 16: Provider-Optimized System Prompts**

```python
    def _build_optimized_system_prompt(
        self, 
        config: ModelProviderConfig, 
        result_type: Type[BaseModel]
    ) -> str:
        """Build system prompt optimized for specific provider capabilities."""
        
        base_prompt = f"""You are a professional research analyst with expertise in data validation 
        and structured reporting. Your responses must always conform to the 
        {result_type.__name__} schema with high-quality findings and credible sources.
        
        Guidelines:
        - Provide substantive findings (minimum 10 characters each)
        - Include credible, verifiable sources
        - Assign appropriate confidence scores based on source quality
        - Use clear, professional language
        - Prioritize recent and authoritative sources"""
        
        # Add provider-specific prompt optimizations
        if config.provider == SupportedProvider.ANTHROPIC:
            base_prompt += "\n\n- Structure responses using clear XML-like formatting when helpful"
            base_prompt += "\n- Include citations and source references explicitly"
        
        elif config.provider == SupportedProvider.GEMINI:
            base_prompt += "\n\n- Focus on comprehensive analysis with detailed reasoning"
            base_prompt += "\n- Use structured thinking patterns in your responses"
        
        elif config.provider == SupportedProvider.GROQ:
            base_prompt += "\n\n- Provide concise, direct responses optimized for speed"
            base_prompt += "\n- Focus on essential information and key findings"
        
        return base_prompt
    
    async def _wrap_with_fallback(
        self, 
        primary_agent: Agent, 
        result_type: Type[BaseModel],
        system_prompt: str
    ) -> Agent:
        """Wrap agent with fallback provider handling."""
        
        class FallbackAgent:
            """Agent wrapper with automatic fallback to alternative providers."""
            
            def __init__(self, factory_ref: MultiProviderAgentFactory):
                self.factory = factory_ref
                self.primary_agent = primary_agent
                self.result_type = result_type
                self.system_prompt = system_prompt
            
            async def run(self, user_prompt: str, deps: Any = None) -> Any:
                """Run with fallback handling."""
                
                # Try primary provider first
                try:
                    start_time = datetime.now()
                    result = await self.primary_agent.run(user_prompt, deps=deps)
                    
                    # Update success stats
                    response_time = (datetime.now() - start_time).total_seconds()
                    await self._update_provider_stats("primary", True, response_time)
                    
                    return result
                    
                except Exception as e:
                    print(f"Primary provider failed: {e}")
                    await self._update_provider_stats("primary", False, 0)
                    
                    # Try fallback providers
                    for fallback_name in self.factory.fallback_chain:
                        if fallback_name in self.factory.provider_configs:
                            try:
                                fallback_agent = await self.factory.create_research_agent(
                                    primary_provider=fallback_name,
                                    result_type=self.result_type,
                                    custom_system_prompt=self.system_prompt,
                                    enable_fallback=False  # Prevent infinite recursion
                                )
                                
                                start_time = datetime.now()
                                result = await fallback_agent.run(user_prompt, deps=deps)
                                
                                response_time = (datetime.now() - start_time).total_seconds()
                                await self._update_provider_stats(fallback_name, True, response_time)
                                
                                print(f"Fallback successful with provider: {fallback_name}")
                                return result
                                
                            except Exception as fallback_error:
                                print(f"Fallback provider {fallback_name} failed: {fallback_error}")
                                await self._update_provider_stats(fallback_name, False, 0)
                                continue
                    
                    # All providers failed
                    raise Exception(f"All providers failed. Original error: {e}")
            
            async def _update_provider_stats(self, provider_name: str, success: bool, response_time: float):
                """Update provider performance statistics."""
                if provider_name in self.factory.provider_stats:
                    stats = self.factory.provider_stats[provider_name]
                    stats['requests'] += 1
                    if success:
                        stats['successes'] += 1
                        # Update rolling average response time
                        stats['avg_response_time'] = (
                            (stats['avg_response_time'] * (stats['successes'] - 1) + response_time) 
                            / stats['successes']
                        )
                    else:
                        stats['failures'] += 1
                    
                    stats['last_used'] = datetime.now().isoformat()
        
        return FallbackAgent(self)
    
    def get_provider_statistics(self) -> Dict[str, Any]:
        """Get performance statistics for all registered providers."""
        return {
            'providers': self.provider_stats,
            'fallback_chain': self.fallback_chain,
            'total_providers': len(self.provider_configs)
        }

# Usage example for multi-provider setup
async def demonstrate_multi_provider_agents():
    """Demonstrate multi-provider agent configuration."""
    
    factory = MultiProviderAgentFactory()
    
    # Register multiple providers
    openai_config = ModelProviderFactory.create_provider_config(
        SupportedProvider.OPENAI,
        "gpt-4",
        {"temperature": 0.1, "max_tokens": 4096}
    )
    
    gemini_config = ModelProviderFactory.create_provider_config(
        SupportedProvider.GEMINI,
        "gemini-pro",
        {"temperature": 0.2, "max_tokens": 2048}
    )
    
    groq_config = ModelProviderFactory.create_provider_config(
        SupportedProvider.GROQ,
        "mixtral-8x7b-32768",
        {"temperature": 0.0, "max_tokens": 8192}
    )
    
    factory.register_provider("openai", openai_config, priority=1)
    factory.register_provider("gemini", gemini_config, priority=2)
    factory.register_provider("groq", groq_config, priority=3)
    
    # Set fallback chain
    factory.set_fallback_chain(["gemini", "groq"])
    
    # Create research agent with fallback
    research_agent = await factory.create_research_agent(
        primary_provider="openai",
        result_type=ResearchResult,
        enable_fallback=True
    )
    
    # Test the agent
    context = ExecutionContext(user_id="multi_test_user")
    
    try:
        result = await research_agent.run(
            "Research the latest developments in type-safe AI agent frameworks",
            deps=context
        )
        
        print("Research completed successfully!")
        print(f"Found {len(result.key_findings)} key findings")
        
        # Get provider statistics
        stats = factory.get_provider_statistics()
        print(f"Provider performance: {stats}")
        
        return result
        
    except Exception as e:
        print(f"Multi-provider research failed: {e}")
        return None
```

### **Complete Multi-Provider Integration Summary**

The model-agnostic integration system provides a production-ready foundation for type-safe agents that can seamlessly work across multiple LLM providers:

**Key Capabilities:**
- **Unified Provider Interface**: Consistent API across OpenAI, Gemini, Groq, and Anthropic
- **Provider-Specific Optimizations**: Tailored configurations maximizing each model's strengths
- **Automatic Fallback Handling**: Resilient operation with intelligent backup provider chains
- **Performance Monitoring**: Real-time statistics tracking for optimization and operational insights
- **Type-Safe Configuration**: Validated settings with comprehensive error handling
- **Flexible Agent Creation**: Easy provider switching with minimal code changes

**Production Benefits:**
- Reduces vendor lock-in by supporting multiple providers
- Ensures high availability through automatic failover
- Optimizes performance through provider-specific tuning
- Provides operational visibility through comprehensive monitoring
- Maintains type safety throughout the entire integration stack

This architecture enables production-ready agents that adapt to different LLM providers while maintaining consistent behavior, comprehensive monitoring, and reliable operation under various failure scenarios.

### **Advanced Type Definitions and Constraints**

PydanticAI supports complex type definitions with sophisticated validation rules for domain-specific requirements.

Let's build advanced data analysis models to demonstrate complex validation patterns:

**Step 1: Define the analysis request structure**

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
```

This establishes the core analysis request with bounded data (3-10,000 points), specific analysis types via `Literal`, and constrained confidence levels.

**Step 2: Add optional configuration fields**

```python
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
```

These optional fields provide configuration control while maintaining reasonable defaults.

**Step 3: Implement comprehensive data quality validation**

```python
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
```

This validator performs comprehensive data quality checks: NaN detection, infinity checks, variation requirements, and reasonable range validation.

**Step 4: Add contextual validation for confidence levels**

```python
    @validator('confidence_level')
    def validate_confidence_level(cls, v, values):
        """Validate confidence level based on data size."""
        data = values.get('data', [])
        
        if len(data) < 10 and v > 0.99:
            raise ValueError("High confidence levels require more data points")
        
        return v
```

This validator demonstrates how to validate one field based on another - high confidence requires more data points.

**Step 5: Define the comprehensive result structure**

```python
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

The result model provides comprehensive analysis output with optional fields, validation constraints, and automatic timestamp generation.

---

## **Part 2: Advanced Validation (500 lines)**

### **Custom Validators and Constraints**

PydanticAI's validation system extends beyond basic type checking to include domain-specific business logic and data integrity rules.

Let's implement advanced validation patterns with a systematic approach:

**Step 1: Import validation dependencies**

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

### **Step 1: Task Definition Core Structure**

Complex validation rules demonstrate PydanticAI's ability to handle enterprise-level data validation requirements:

```python
# Complex task definition with comprehensive validation
class TaskDefinition(BaseModel):
    """Enterprise task definition with extensive validation rules and constraints."""
    
    # Core identification fields with length constraints
    task_id: str = Field(..., min_length=8, max_length=32)
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
```

These core fields establish the foundation with appropriate length constraints for enterprise systems.

### **Step 2: Task Status and Assignment Fields**

```python
    # Status and assignment management
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assignee_id: Optional[str] = None
    reporter_id: str = Field(..., min_length=3)
```

Status fields use the type-safe enums we defined earlier, ensuring consistent task state management.

### **Step 3: Metadata and Constraint Fields**

```python
    # Metadata and organizational fields
    labels: List[str] = Field(default_factory=list, max_items=10)
    estimated_hours: Optional[float] = Field(None, gt=0, le=1000)
    due_date: Optional[datetime] = None
    dependencies: List[str] = Field(default_factory=list, max_items=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ```

Metadata fields include organizational tools like labels, time estimates, and dependency tracking.

### **Step 4: Task ID Format Validation**

```python
    @validator('task_id')
    def validate_task_id_format(cls, v):
        """Enforce organizational task ID format for consistency."""
        # Required format: PROJECT-NUMBER (e.g., PROJ-1234, AI-5678)
        if not re.match(r'^[A-Z]{2,10}-\d{1,6}$', v):
            raise ValueError('Task ID must follow format: PROJECT-NUMBER (e.g., PROJ-1234)')
        return v
    ```

Task ID validation ensures consistent organizational formatting across all tasks.

### **Step 5: Title Quality Validation**

```python
    @validator('title')
    def validate_title_quality(cls, v):
        """Enforce title quality standards to improve task clarity."""
        # Normalize whitespace
        cleaned_title = ' '.join(v.split())
        
        # Detect and reject poor title patterns
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
    ```

Title validation prevents common quality issues like overly generic or poorly formatted titles.

### **Step 6: Label Format and Deduplication**

```python
    @validator('labels')
    def validate_labels_format(cls, v):
        """Validate and normalize labels for consistent tagging."""
        validated_labels = []
        
        for label in v:
            # Normalize label format
            clean_label = label.strip().lower()
            
            # Skip labels that are too short
            if len(clean_label) < 2:
                continue
            
            # Enforce alphanumeric characters with hyphens and underscores
            if not re.match(r'^[a-z0-9-_]+$', clean_label):
                raise ValueError(f'Invalid label format: {label}')
            
            validated_labels.append(clean_label)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(validated_labels))
    ```

Label validation ensures consistent tagging with automatic normalization and deduplication.

### **Step 7: Comprehensive Due Date Validation**

```python
    @validator('due_date')
    def validate_due_date_reasonable(cls, v, values):
        """Comprehensive due date validation with business logic."""
        if v is None:
            return v
        
        now = datetime.now(timezone.utc)
        
        # Prevent past due dates
        if v < now:
            raise ValueError('Due date cannot be in the past')
        
        # Reasonable future limit (2 years)
        max_future_date = now.replace(year=now.year + 2)
        if v > max_future_date:
            raise ValueError('Due date too far in the future (max 2 years)')
```

Basic due date validation ensures dates are neither in the past nor unreasonably far in the future.

### **Step 8: Due Date and Work Estimation Correlation**

```python
        # Cross-validate with estimated work hours
        estimated_hours = values.get('estimated_hours')
        if estimated_hours:
            time_until_due = (v - now).days
            hours_per_day = estimated_hours / max(time_until_due, 1)
            
            # Prevent unrealistic work schedules (max 16 hours per day)
            if hours_per_day > 16:
                raise ValueError('Due date too soon for estimated work hours')
        
        return v
    ```

Due date validation includes sophisticated cross-field validation with work estimation correlation.

### **Step 9: Cross-Field Root Validation**

```python
    @root_validator
    def validate_task_consistency(cls, values):
        """Enforce business rules across multiple fields simultaneously."""
        status = values.get('status')
        assignee_id = values.get('assignee_id')
        due_date = values.get('due_date')
        estimated_hours = values.get('estimated_hours')
        
        # Business rule: In-progress tasks require assignees
        if status == TaskStatus.IN_PROGRESS and not assignee_id:
            raise ValueError('In-progress tasks must have an assignee')
        
        # Data cleanup: Completed tasks shouldn't have future due dates
        if status == TaskStatus.COMPLETED and due_date:
            if due_date > datetime.now(timezone.utc):
                values['due_date'] = None  # Auto-clear inconsistent due date
```

Root validation enforces business rules that span multiple fields, ensuring data consistency.

### **Step 10: Priority-Based Validation Rules**

```python
        # Critical task requirements
        if values.get('priority') == TaskPriority.CRITICAL:
            if not estimated_hours:
                raise ValueError('Critical tasks must have time estimates')
            if estimated_hours > 200:  # More than 5 weeks
                raise ValueError('Critical tasks should not require more than 200 hours')
        
        # Automatic timestamp update
        values['updated_at'] = datetime.now(timezone.utc)
        
        return values
```

Priority-based validation ensures critical tasks meet organizational requirements for time estimation and resource allocation.

### **Step 11: Validation Error Management Foundation**

Comprehensive error handling provides detailed feedback for validation failures with actionable suggestions:

```python
# Advanced validation error management system
from typing import Dict, List, Type, Any
import traceback
from dataclasses import dataclass
```

Error management imports provide the foundation for detailed validation reporting.

### **Step 12: Detailed Error Information Structure**

```python
@dataclass
class ValidationErrorDetail:
    """Comprehensive validation error details with suggestions."""
    field_path: str       # Path to the field that failed (e.g., 'task.title')
    error_type: str       # Type of validation error
    message: str          # Human-readable error message
    invalid_value: Any    # The value that caused the error
    constraint: str       # The constraint that was violated
    suggestion: Optional[str] = None  # Suggested fix for the error
```

Detailed error information provides comprehensive debugging and user feedback capabilities.

### **Step 13: Validation Error Handler Foundation**

```python
# Centralized error processing with frequency tracking
class ValidationErrorHandler:
    """Advanced validation error handling with analytics and suggestions."""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}  # Track error frequency
        self.common_errors: List[ValidationErrorDetail] = []  # Common error patterns
```

The error handler tracks error patterns to identify common validation issues.

### **Step 14: Structured Error Processing**

```python
    def handle_validation_error(self, error: Exception, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Transform raw validation errors into structured, actionable feedback."""
        
        error_details = []
        
        # Process Pydantic validation errors
        if hasattr(error, 'errors'):
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
                
                # Track error frequency for analytics
                error_key = f"{model_class.__name__}.{detail.field_path}.{detail.error_type}"
                self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
```

Error processing extracts detailed information from Pydantic errors and tracks frequency.

### **Step 15: Generic Error Handling and Response Structure**

```python
        else:
            # Handle non-Pydantic errors
            detail = ValidationErrorDetail(
                field_path="unknown",
                error_type="generic_error",
                message=str(error),
                invalid_value="unknown",
                constraint="unknown"
            )
            error_details.append(detail)
        ```

Generic error handling ensures all validation failures are captured and processed consistently.

### **Step 16: Structured Error Response Generation**

```python
        # Generate comprehensive error response
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

### **Dependency Injection for Testing and Production (2025 Feature)**

PydanticAI 2025 introduces an optional dependency injection system that enables clean separation between testing and production configurations, supporting eval-driven iterative development and robust production dependency management.

### **Step 1: Import Dependencies and Define Core Protocols**

The dependency injection system starts with essential imports and service protocol definitions. These protocols define the interfaces that both production and test implementations must follow:

```python
# Essential imports for dependency injection
from pydantic_ai.dependencies import DependencyProvider, Injectable, Scope
from typing import Protocol, runtime_checkable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import asyncio
import logging
```

These imports provide the foundation for PydanticAI's dependency injection system, enabling clean separation between interface definitions and implementations.

### **Step 2: Define Service Interface Protocols**

Protocols define the contracts that all service implementations must follow, enabling seamless switching between production and test implementations:

```python
# Service interface definitions using Protocol pattern
@runtime_checkable
class DatabaseService(Protocol):
    """Protocol for database operations with type safety."""
    async def save_result(self, result_data: Dict[str, Any]) -> str: ...
    async def get_result(self, result_id: str) -> Optional[Dict[str, Any]]: ...
    async def health_check(self) -> bool: ...
```

The `DatabaseService` protocol ensures all database implementations provide consistent async methods for saving, retrieving, and health checking.

### **Step 3: Define External Service Protocols**

```python
@runtime_checkable  
class ExternalAPIService(Protocol):
    """Protocol for external API integrations."""
    async def fetch_data(self, query: str) -> Dict[str, Any]: ...
    async def validate_source(self, source_url: str) -> bool: ...
    
@runtime_checkable
class CacheService(Protocol):
    """Protocol for caching operations with TTL support."""
    async def get(self, key: str) -> Optional[Any]: ...
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None: ...
    async def invalidate(self, pattern: str) -> int: ...
```

These protocols define the core service interfaces that enable type-safe dependency injection. The `@runtime_checkable` decorator allows isinstance() checks at runtime.

### **Step 4: Production Database Service Implementation**

The production database service provides real database connectivity with connection pooling and proper error handling:

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

The initialization method sets up connection pooling, which is essential for production database performance and resource management.

### **Step 5: Database Operations Implementation**

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

These database operations include proper UUID generation, logging, and structured return values essential for production agent systems.

### **Step 6: Production API Service Implementation**

The production API service handles external data sources with proper session management and authentication:

```python
# Production API service with HTTP session management
class ProductionAPIService:
    """Production external API service with authentication and session management."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
    
    async def initialize(self):
        """Initialize HTTP session with authentication headers."""
        # Production would create aiohttp session with proper headers
        self.session = f"HTTPSession(base_url={self.base_url})"
        logging.info("API service initialized")
```

Session initialization is crucial for managing HTTP connections efficiently and securely in production environments.

### **Step 7: API Data Operations**

```python
    async def fetch_data(self, query: str) -> Dict[str, Any]:
        """Fetch research data from external API with proper error handling."""
        # Production implementation would include retry logic and error handling
        logging.info(f"Fetching data for query: {query}")
        return {
            "query": query,
            "results": [{"title": f"Result for {query}", "confidence": 0.95}],
            "metadata": {"source": "production_api", "timestamp": datetime.now().isoformat()}
        }
    
    async def validate_source(self, source_url: str) -> bool:
        """Validate source URLs using external verification service."""
        logging.info(f"Validating source: {source_url}")
        return source_url.startswith(("https://", "http://"))
```

The API service provides structured data fetching and source validation, essential for maintaining data quality in research agents.

### **Step 8: Test Database Service Implementation**

Test implementations provide predictable behavior and call tracking for comprehensive testing:

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
```

The test service uses in-memory storage and call logging, enabling verification of agent behavior without external dependencies.

### **Step 9: Test Database Operations**

```python
    async def save_result(self, result_data: Dict[str, Any]) -> str:
        """Save result to in-memory store with predictable IDs."""
        result_id = f"test_{len(self.data_store)}"
        self.data_store[result_id] = result_data
        self.call_log.append(("save", result_id, result_data))
        return result_id
    
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

Test database operations provide deterministic behavior and comprehensive call tracking, essential for reliable agent testing.

### **Step 10: Test API Service Implementation**

```python
# Test API service with configurable mock responses
class TestAPIService:
    """Test API service with predictable responses and call tracking."""
    
    def __init__(self, mock_responses: Optional[Dict[str, Any]] = None):
        self.mock_responses = mock_responses or {}  # Configurable test responses
        self.call_log = []  # Track all API calls for verification
    
    async def initialize(self):
        """Initialize test API service - always succeeds."""
        logging.info("Test API service initialized")
```

The test API service allows configurable responses, enabling comprehensive testing of different data scenarios.

### **Step 11: Mock API Operations**

```python
    async def fetch_data(self, query: str) -> Dict[str, Any]:
        """Return configurable mock data for predictable testing."""
        self.call_log.append(("fetch_data", query))
        
        # Return pre-configured response if available
        if query in self.mock_responses:
            return self.mock_responses[query]
        
        # Default test response with predictable format
        return {
            "query": query,
            "results": [{"title": f"Test result for {query}", "confidence": 0.85}],
            "metadata": {"source": "test_api", "timestamp": "2025-01-01T00:00:00Z"}
        }
    
    async def validate_source(self, source_url: str) -> bool:
        """Mock source validation with predictable test behavior."""
        self.call_log.append(("validate_source", source_url))
        return not source_url.startswith("invalid://")
```

Mock API operations enable testing of various response scenarios, including error conditions and edge cases.

### **Step 12: Dependency Injection Container Foundation**

The dependency container manages service lifecycles, registration, and resolution with support for singletons and scoped services:

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
```

The container maintains separate tracking for different service lifecycles, ensuring proper initialization order and cleanup.

### **Step 13: Service Registration Methods**

```python
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
    
    def register_scoped(
        self,
        interface: Type,
        implementation: Type, 
        scope: str = "default",
        *args,
        **kwargs
    ) -> None:
        """Register a scoped service that lives for a specific scope lifetime."""
        if scope not in self.scoped_services:
            self.scoped_services[scope] = {}
        
        self.scoped_services[scope][interface] = lambda: implementation(*args, **kwargs)
```

Service registration supports both singleton (application lifetime) and scoped (request lifetime) patterns.

### **Step 14: Factory Registration and Service Resolution**

```python
    def register_factory(
        self,
        interface: Type,
        factory_func: Callable,
    ) -> None:
        """Register a factory function for custom service creation logic."""
        self.factories[interface] = factory_func
        self.initialization_order.append(interface)
    ```

Factory registration enables custom service creation logic for complex initialization scenarios.

### **Step 15: Service Resolution Logic**

```python
    async def get_service(self, interface: Type, scope: str = "default") -> Any:
        """Resolve service instance with proper initialization and lifecycle management."""
        
        # Check existing singletons first for performance
        if interface in self.singletons:
            return self.singletons[interface]
        
        # Handle scoped services (per-request, per-session, etc.)
        if scope in self.scoped_services and interface in self.scoped_services[scope]:
            factory = self.scoped_services[scope][interface]
            instance = factory()
            if hasattr(instance, 'initialize'):
                await instance.initialize()
            return instance
        
        # Create and cache singleton instances
        if interface in self.factories:
            instance = self.factories[interface]()
            if hasattr(instance, 'initialize'):
                await instance.initialize()
            self.singletons[interface] = instance
            return instance
        
        raise ValueError(f"No registration found for {interface}")
```

Service resolution follows a clear priority: existing singletons, scoped services, then new singleton creation.

### **Step 16: Container Lifecycle Management**

```python
    async def initialize_all(self) -> None:
        """Initialize all registered services in proper dependency order."""
        for interface in self.initialization_order:
            if interface not in self.singletons:
                await self.get_service(interface)
    ```

Batch initialization ensures all services are ready before the application starts handling requests.

### **Step 17: Service Cleanup and Scope Management**

```python
    async def cleanup(self) -> None:
        """Clean up all services with proper error handling."""
        # Cleanup singleton services
        for service in self.singletons.values():
            if hasattr(service, 'cleanup'):
                await service.cleanup()
        
        # Cleanup scoped services safely
        for scope_services in self.scoped_services.values():
            for service in scope_services.values():
                if hasattr(service, 'cleanup'):
                    try:
                        instance = service()  # Get instance to cleanup
                        if hasattr(instance, 'cleanup'):
                            await instance.cleanup()
                    except:
                        pass  # Service may not be instantiated
```

Cleanup ensures proper resource disposal when the container shuts down.

### **Step 18: Scoped Service Context Management**

```python
    def create_scope_context(self, scope: str):
        """Create async context manager for scoped service lifecycle."""
        @asynccontextmanager
        async def scope_context():
            try:
                yield self
            finally:
                # Cleanup scoped services when context exits
                if scope in self.scoped_services:
                    for interface in list(self.scoped_services[scope].keys()):
                        # Remove from scoped services to trigger cleanup
                        del self.scoped_services[scope][interface]
        
        return scope_context()
```

Scope context management enables proper lifecycle handling for request-scoped and session-scoped services.

### **Step 19: Dependency-Injected Agent Implementation**

The dependency-injected agent integrates PydanticAI with the dependency injection container for clean architecture:

```python
# PydanticAI agent with comprehensive dependency injection
class DependencyInjectedAgent:
    """PydanticAI agent with full dependency injection support and lifecycle management."""
    
    def __init__(
        self,
        agent_config: Dict[str, Any],
        container: DependencyContainer
    ):
        self.agent_config = agent_config
        self.container = container
        self.agent = None
```

The agent wrapper holds configuration and container references for lazy initialization.

### **Step 20: Agent Initialization with Dependency Resolution**

```python
    async def initialize(self) -> Agent:
        """Initialize agent with all required dependencies resolved."""
        
        # Resolve all required services from the container
        db_service = await self.container.get_service(DatabaseService)
        api_service = await self.container.get_service(ExternalAPIService)
        cache_service = await self.container.get_service(CacheService, scope="request")
        
        # Create dependency context for the agent
        dependency_context = {
            'db_service': db_service,
            'api_service': api_service,
            'cache_service': cache_service
        }
        
        # Create PydanticAI agent with injected dependencies
        self.agent = Agent(
            model=self.agent_config.get('model', 'openai:gpt-4'),
            result_type=self.agent_config.get('result_type', ResearchResult),
            system_prompt=self.agent_config.get('system_prompt', 'You are a helpful assistant.'),
            deps_type=type('DependencyContext', (), dependency_context)
        )
        
        return self.agent
    ```

Agent initialization creates the PydanticAI agent with all dependencies properly resolved and injected.

### **Step 21: Agent Execution with Scoped Dependencies**

```python
    async def run_with_dependencies(
        self, 
        user_prompt: str,
        execution_context: ExecutionContext,
        scope: str = "request"
    ) -> Any:
        """Execute agent with properly managed scoped dependencies."""
        
        # Ensure agent is initialized
        if not self.agent:
            await self.initialize()
        
        # Create scoped context for request-level dependencies
        async with self.container.create_scope_context(scope):
            # Get fresh service instances for this request scope
            db_service = await self.container.get_service(DatabaseService)
            api_service = await self.container.get_service(ExternalAPIService)
            cache_service = await self.container.get_service(CacheService, scope=scope)
```

Scoped execution ensures clean isolation between different agent requests.

### **Step 22: Dependency Bundle Creation and Agent Execution**

```python
            # Create dependency bundle for the agent
            deps = type('RequestDependencies', (), {
                'db_service': db_service,
                'api_service': api_service, 
                'cache_service': cache_service,
                'execution_context': execution_context
            })()
            
            # Execute agent with injected dependencies
            result = await self.agent.run(
                user_prompt=user_prompt,
                deps=deps
            )
            
            # Automatically save result using injected database service
            result_id = await db_service.save_result({
                'prompt': user_prompt,
                'result': result.model_dump(),
                'context': execution_context.model_dump()
            })
            
            return {
                'result': result,
                'result_id': result_id,
                'execution_context': execution_context
            }
```

Dependency bundle creation and agent execution provide a complete request lifecycle with automatic persistence.

### **Step 23: Environment-Specific Configuration Factories**

Configuration factories enable easy switching between production, testing, and development environments:

```python
# Environment-specific dependency configuration factories
class DependencyConfigFactory:
    """Factory for creating environment-specific dependency containers."""
    
    @staticmethod
    def create_production_container(config: Dict[str, Any]) -> DependencyContainer:
        """Create production container with real database and API services."""
        container = DependencyContainer()
        
        # Register production database with connection pooling
        container.register_singleton(
            DatabaseService,
            ProductionDatabaseService,
            connection_string=config['database']['connection_string'],
            pool_size=config['database']['pool_size']
        )
        
        # Register production API service with authentication
        container.register_singleton(
            ExternalAPIService,
            ProductionAPIService,
            api_key=config['api']['key'],
            base_url=config['api']['base_url']
        )
```

Production container registration uses real database connections and external API integrations.

### **Step 24: Production Cache Service Registration**

```python
        # Register production cache service (Redis/Memcached in real deployment)
        from cachetools import TTLCache
        cache_impl = TTLCache(maxsize=1000, ttl=3600)
        container.register_factory(
            CacheService,
            lambda: type('ProductionCacheService', (), {
                'get': lambda self, key: cache_impl.get(key),
                'set': lambda self, key, value, ttl=3600: cache_impl.__setitem__(key, value),
                'invalidate': lambda self, pattern: cache_impl.clear()
            })()
        )
        
        return container
    ```

Production cache registration uses TTL cache with configurable size and timeout settings.

### **Step 25: Test Container Configuration**

```python
    @staticmethod
    def create_test_container(mock_config: Optional[Dict[str, Any]] = None) -> DependencyContainer:
        """Create test container with mocked services for reliable testing."""
        container = DependencyContainer()
        mock_config = mock_config or {}
        
        # Register test database with in-memory storage
        container.register_singleton(DatabaseService, TestDatabaseService)
        
        # Register test API service with configurable mock responses
        container.register_singleton(
            ExternalAPIService, 
            TestAPIService,
            mock_responses=mock_config.get('api_responses', {})
        )
```

Test container uses in-memory services with configurable mock responses for predictable testing.

### **Step 26: Test Cache Service Registration**

```python
        # Simple in-memory cache for testing consistency
        test_cache = {}
        container.register_factory(
            CacheService,
            lambda: type('TestCacheService', (), {
                'get': lambda self, key: test_cache.get(key),
                'set': lambda self, key, value, ttl=3600: test_cache.update({key: value}),
                'invalidate': lambda self, pattern: test_cache.clear()
            })()
        )
        
        return container
```

Test cache provides simple in-memory storage with consistent behavior for testing scenarios.

### **Step 27: Complete Dependency Injection Demonstration**

A comprehensive demonstration showing how to use dependency injection in both production and test environments:

```python
# Complete demonstration of dependency injection patterns
async def demonstrate_dependency_injection():
    """Show how to use dependency injection for production and testing."""
    
    # Production configuration with real connection details
    prod_config = {
        'database': {
            'connection_string': 'postgresql://prod_host:5432/agents',
            'pool_size': 20
        },
        'api': {
            'key': 'prod_api_key',
            'base_url': 'https://api.production.com'
        }
    }
    
    # Create and initialize production container
    prod_container = DependencyConfigFactory.create_production_container(prod_config)
    await prod_container.initialize_all()
```

Production configuration uses real database connections and API credentials for production deployment.

### **Step 28: Agent Configuration and Environment Setup**

```python
    # Agent configuration shared between environments
    agent_config = {
        'model': 'openai:gpt-4',
        'result_type': ResearchResult,
        'system_prompt': 'Research assistant with production integrations.'
    }
    
    # Create production agent
    prod_agent = DependencyInjectedAgent(agent_config, prod_container)
    ```

Agent configuration defines the model, result type, and system prompt used across both environments.

### **Step 29: Test Environment Configuration**

```python
    # Test configuration with mock responses for predictable testing
    test_container = DependencyConfigFactory.create_test_container({
        'api_responses': {
            'AI safety': {
                'query': 'AI safety',
                'results': [{'title': 'Test AI Safety Article', 'confidence': 0.9}]
            }
        }
    })
    await test_container.initialize_all()
    
    # Create test agent with same configuration
    test_agent = DependencyInjectedAgent(agent_config, test_container)
```

Test environment uses configurable mock responses for consistent, predictable testing behavior.

### **Step 30: Agent Execution and Verification**

```python
    # Create execution context for the request
    execution_context = ExecutionContext(user_id="test_user")
    
    # Execute test agent (production would be similar)
    test_result = await test_agent.run_with_dependencies(
        "Research AI safety best practices",
        execution_context
    )
    
    # Verify service interactions for testing
    test_db = await test_container.get_service(DatabaseService)
    test_api = await test_container.get_service(ExternalAPIService)
    
    print(f"Test database calls: {len(test_db.get_call_log())}")
    print(f"Test API calls: {len(test_api.call_log)}")
    
    return {
        'test_result': test_result,
        'db_calls': test_db.get_call_log(),
        'api_calls': test_api.call_log
    }
```

This dependency injection system enables clean separation between testing and production environments, supporting eval-driven development and robust production dependency management.

### **Scalable Agent Architecture**

Production PydanticAI applications require robust architecture patterns that handle concurrency, error recovery, and monitoring at scale.

**Step 1: Set up production imports and logging**

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

Production agents require comprehensive logging and proper import organization for scalability and monitoring.

**Step 2: Define agent protocol contracts**

```python
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

```

The protocol defines the contract that all production agents must implement for consistent behavior across the system.

**Step 3: Create comprehensive metrics model**

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

This metrics model tracks all critical performance indicators including response times, error rates, and resource usage.

**Step 4: Define production agent base class**

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
        
    @abstractmethod
    async def _process_core_request(self, request: BaseModel) -> BaseModel:
        """Core request processing logic - must be implemented by subclasses."""
        pass
    
```

The base class initializes all necessary components including logging, metrics, threading, and health monitoring.

**Step 5: Implement comprehensive request processing**

```python
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
```

This method implements the complete request lifecycle with validation, timeout handling, and result processing.

**Step 6: Handle success response and error scenarios**

```python            
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
    
```

The error handling includes timeout detection, comprehensive logging, and structured error responses with request tracing.

**Step 7: Implement request validation and post-processing**

```python
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
```

These utility methods handle request validation, result enhancement, and precise timing calculations.

**Step 8: Update performance metrics for monitoring**

```python    
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
    
```

Both success and error metrics update the response time tracking and maintain comprehensive logging for observability.

**Step 9: Calculate performance percentiles and create error responses**

```python
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
    
```

The percentile calculations track P95 and P99 response times for SLA monitoring, and memory management prevents unbounded growth.

**Step 10: Implement comprehensive health monitoring**

```python
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
    
```

The health check automatically evaluates error rates, response times, and request patterns to determine agent status.

**Step 11: Add metrics retrieval and graceful shutdown**

```python
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
```

These methods provide comprehensive monitoring data and ensure clean resource cleanup during shutdown.

**Step 12: Create production-ready research agent**

```python
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
    
```

This concrete implementation combines the base production class with PydanticAI's research capabilities.

**Step 13: Set up production-optimized tools**

```python
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
```

The web search tool includes comprehensive input validation, realistic result simulation, and detailed logging for production monitoring.

**Step 14: Add credibility analysis and agent processing**

```python        
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

The factory provides centralized agent management with health monitoring and graceful shutdown capabilities for production environments.
```

---

## **Part 4: Integration & Error Handling (400 lines)**

### **Comprehensive Error Management**

Production PydanticAI applications require sophisticated error handling strategies that maintain system stability while providing meaningful feedback.

**Step 1: Import error handling dependencies**

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
```

These imports provide the foundation for sophisticated error handling with typing support and async capabilities.

**Step 2: Define error severity and recovery strategies**

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

The error classification system provides structured categories and severity levels for consistent error handling across the application.

**Step 3: Create comprehensive error context tracking**

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

The ErrorContext class captures comprehensive error information including timing, categorization, retry logic, and user-friendly messaging.

**Step 4: Add error context serialization and utility methods**

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

```

The error context provides complete serialization and retry tracking for comprehensive error management.

**Step 5: Create error classification system**

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
```

The error classifier analyzes exception types and error messages to automatically categorize errors for appropriate handling strategies.

**Step 6: Implement intelligent retry strategies**

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
```

The retry strategy implements exponential backoff with jitter and intelligent retry decision-making based on error categories.

**Step 7: Add circuit breaker pattern for service resilience**

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

```

The circuit breaker automatically opens when failure thresholds are reached, protecting the system from cascading failures.

**Step 8: Create external service integration with resilience patterns**

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

The external service integration combines circuit breakers, retry strategies, and comprehensive error handling for robust production deployments.

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

### **Enterprise Monitoring and Observability (2025 Feature)**

PydanticAI 2025 includes comprehensive monitoring and observability integration for enterprise deployment, with advanced configuration patterns and real-time performance tracking.

#### **Essential Monitoring Imports**

```python
# Enterprise monitoring and observability for PydanticAI
from pydantic_ai.monitoring import AgentMonitor, MetricsCollector
from pydantic_ai.observability import TraceCollector, SpanContext
import json
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import structlog
```

These imports provide the foundation for enterprise monitoring, including built-in PydanticAI monitoring tools, observability tracing, and structured logging capabilities.

#### **Core Agent Metrics Structure**

```python
@dataclass
class AgentMetrics:
    """Comprehensive agent performance metrics."""
    agent_id: str
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    
    # Response time percentiles
    response_times: List[float] = field(default_factory=list)
    
    # Error breakdown
    error_types: Dict[str, int] = field(default_factory=dict)
    
    # Success rate over time
    success_rate_history: List[Dict[str, Any]] = field(default_factory=list)
```

The `AgentMetrics` class captures comprehensive performance data including request counts, response times, token usage, costs, and historical success rates for detailed analysis.

#### **Response Time Tracking Methods**

```python
def update_response_time(self, response_time: float) -> None:
    """Update response time metrics."""
    self.response_times.append(response_time)
    
    # Keep only last 1000 response times for memory management
    if len(self.response_times) > 1000:
        self.response_times = self.response_times[-1000:]
    
    # Update aggregate metrics
    self.avg_response_time = sum(self.response_times) / len(self.response_times)
    self.min_response_time = min(self.min_response_time, response_time)
    self.max_response_time = max(self.max_response_time, response_time)
```

This method maintains a rolling window of response times for memory efficiency while calculating real-time statistics for performance monitoring.

#### **Success and Error Recording**

```python
def record_success(self, response_time: float, tokens_used: int = 0, cost: float = 0.0) -> None:
    """Record successful request."""
    self.request_count += 1
    self.success_count += 1
    self.total_tokens_used += tokens_used
    self.total_cost += cost
    self.update_response_time(response_time)
    
    # Update success rate history (keep last 24 hours worth)
    current_time = time.time()
    self.success_rate_history.append({
        'timestamp': current_time,
        'success': True,
        'response_time': response_time
    })

def record_error(self, error_type: str, response_time: float = 0.0) -> None:
    """Record failed request."""
    self.request_count += 1
    self.error_count += 1
    
    if error_type not in self.error_types:
        self.error_types[error_type] = 0
    self.error_types[error_type] += 1
```

These methods track both successful operations and failures, maintaining detailed error categorization and success rate history for trend analysis.

#### **Performance Analysis Methods**

```python
def get_success_rate(self) -> float:
    """Get current success rate."""
    if self.request_count == 0:
        return 1.0
    return self.success_count / self.request_count

def get_percentiles(self) -> Dict[str, float]:
    """Get response time percentiles."""
    if not self.response_times:
        return {}
    
    sorted_times = sorted(self.response_times)
    n = len(sorted_times)
    
    return {
        'p50': sorted_times[int(n * 0.5)],
        'p90': sorted_times[int(n * 0.9)],
        'p95': sorted_times[int(n * 0.95)],
        'p99': sorted_times[int(n * 0.99)]
    }
```

These analysis methods provide success rate calculations and response time percentiles, essential for understanding system performance characteristics.

#### **Enterprise Metrics Collector Setup**

```python
class EnterpriseMetricsCollector:
    """Enterprise-grade metrics collection and reporting."""
    
    def __init__(self, export_interval: int = 60, retention_hours: int = 24):
        self.export_interval = export_interval
        self.retention_hours = retention_hours
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.global_metrics = AgentMetrics("global")
        self.custom_metrics: Dict[str, List[Dict[str, Any]]] = {}
        
        # External integrations
        self.prometheus_enabled = False
        self.datadog_enabled = False
        self.custom_exporters: List[Callable] = []
        
        # Structured logging
        self.logger = structlog.get_logger("pydantic_ai.metrics")
    
    def register_agent(self, agent_id: str) -> None:
        """Register an agent for metrics tracking."""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics(agent_id)
            self.logger.info("Agent registered for metrics tracking", agent_id=agent_id)
    
    def record_request(
        self, 
        agent_id: str, 
        success: bool, 
        response_time: float,
        error_type: Optional[str] = None,
        tokens_used: int = 0,
        estimated_cost: float = 0.0,
        custom_metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record agent request metrics."""
        
        # Ensure agent is registered
        if agent_id not in self.agent_metrics:
            self.register_agent(agent_id)
        
        agent_metrics = self.agent_metrics[agent_id]
        
        if success:
            agent_metrics.record_success(response_time, tokens_used, estimated_cost)
            self.global_metrics.record_success(response_time, tokens_used, estimated_cost)
        else:
            error_type = error_type or "unknown_error"
            agent_metrics.record_error(error_type, response_time)
            self.global_metrics.record_error(error_type, response_time)
        
        # Record custom metrics
        if custom_metrics:
            for metric_name, metric_value in custom_metrics.items():
                if metric_name not in self.custom_metrics:
                    self.custom_metrics[metric_name] = []
                
                self.custom_metrics[metric_name].append({
                    'timestamp': time.time(),
                    'agent_id': agent_id,
                    'value': metric_value
                })
        
        # Log structured event
        self.logger.info(
            "Agent request recorded",
            agent_id=agent_id,
            success=success,
            response_time=response_time,
            error_type=error_type,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost
        )
    
    def get_agent_summary(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive metrics summary for agent."""
        if agent_id not in self.agent_metrics:
            return None
        
        metrics = self.agent_metrics[agent_id]
        percentiles = metrics.get_percentiles()
        
        return {
            'agent_id': agent_id,
            'total_requests': metrics.request_count,
            'success_count': metrics.success_count,
            'error_count': metrics.error_count,
            'success_rate': metrics.get_success_rate(),
            'avg_response_time': metrics.avg_response_time,
            'response_time_percentiles': percentiles,
            'total_tokens': metrics.total_tokens_used,
            'total_cost': metrics.total_cost,
            'error_breakdown': dict(metrics.error_types),
            'cost_per_request': metrics.total_cost / max(metrics.request_count, 1)
        }
    
    def get_global_summary(self) -> Dict[str, Any]:
        """Get global metrics across all agents."""
        percentiles = self.global_metrics.get_percentiles()
        
        return {
            'total_agents': len(self.agent_metrics),
            'total_requests': self.global_metrics.request_count,
            'global_success_rate': self.global_metrics.get_success_rate(),
            'avg_response_time': self.global_metrics.avg_response_time,
            'response_time_percentiles': percentiles,
            'total_tokens': self.global_metrics.total_tokens_used,
            'total_cost': self.global_metrics.total_cost,
            'top_error_types': sorted(
                self.global_metrics.error_types.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def export_to_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        if not self.prometheus_enabled:
            return ""
        
        metrics_output = []
        
        # Global metrics
        global_summary = self.get_global_summary()
        metrics_output.extend([
            f"# HELP pydantic_ai_requests_total Total number of requests",
            f"# TYPE pydantic_ai_requests_total counter",
            f"pydantic_ai_requests_total {global_summary['total_requests']}",
            f"",
            f"# HELP pydantic_ai_success_rate Current success rate",
            f"# TYPE pydantic_ai_success_rate gauge", 
            f"pydantic_ai_success_rate {global_summary['global_success_rate']}",
            f"",
            f"# HELP pydantic_ai_response_time_seconds Response time in seconds",
            f"# TYPE pydantic_ai_response_time_seconds histogram"
        ])
        
        # Per-agent metrics
        for agent_id, summary in [(aid, self.get_agent_summary(aid)) for aid in self.agent_metrics.keys()]:
            if summary:
                metrics_output.extend([
                    f"pydantic_ai_agent_requests_total{{agent=\"{agent_id}\"}} {summary['total_requests']}",
                    f"pydantic_ai_agent_success_rate{{agent=\"{agent_id}\"}} {summary['success_rate']}",
                    f"pydantic_ai_agent_response_time{{agent=\"{agent_id}\"}} {summary['avg_response_time']}"
                ])
        
        return "\n".join(metrics_output)
    
    def enable_prometheus_export(self, port: int = 8000) -> None:
        """Enable Prometheus metrics endpoint."""
        self.prometheus_enabled = True
        # In a real implementation, this would start an HTTP server
        self.logger.info("Prometheus metrics enabled", port=port)
    
    def add_custom_exporter(self, exporter_func: Callable[[Dict[str, Any]], None]) -> None:
        """Add custom metrics exporter function."""
        self.custom_exporters.append(exporter_func)
        self.logger.info("Custom metrics exporter added")

# Distributed tracing and observability
class DistributedTracing:
    """Distributed tracing for PydanticAI agent calls."""
    
    def __init__(self, service_name: str = "pydantic-ai-agents"):
        self.service_name = service_name
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        self.completed_traces: List[Dict[str, Any]] = []
        self.logger = structlog.get_logger("pydantic_ai.tracing")
    
    def start_trace(self, trace_id: str, operation_name: str, parent_span: Optional[str] = None) -> str:
        """Start a new trace span."""
        span_id = f"{trace_id}_{len(self.active_traces)}"
        
        span_data = {
            'trace_id': trace_id,
            'span_id': span_id,
            'parent_span': parent_span,
            'operation_name': operation_name,
            'start_time': time.time(),
            'service_name': self.service_name,
            'tags': {},
            'logs': []
        }
        
        self.active_traces[span_id] = span_data
        
        self.logger.info(
            "Trace span started",
            trace_id=trace_id,
            span_id=span_id,
            operation=operation_name
        )
        
        return span_id
    
    def add_span_tag(self, span_id: str, key: str, value: Any) -> None:
        """Add tag to active span."""
        if span_id in self.active_traces:
            self.active_traces[span_id]['tags'][key] = value
    
    def add_span_log(self, span_id: str, message: str, level: str = "info") -> None:
        """Add log entry to active span."""
        if span_id in self.active_traces:
            self.active_traces[span_id]['logs'].append({
                'timestamp': time.time(),
                'level': level,
                'message': message
            })
    
    def finish_span(self, span_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """Finish and record span."""
        if span_id not in self.active_traces:
            return
        
        span_data = self.active_traces[span_id]
        span_data['end_time'] = time.time()
        span_data['duration'] = span_data['end_time'] - span_data['start_time']
        span_data['success'] = success
        
        if error:
            span_data['error'] = error
            span_data['tags']['error'] = True
        
        # Move to completed traces
        self.completed_traces.append(span_data)
        del self.active_traces[span_id]
        
        # Cleanup old traces (keep last 1000)
        if len(self.completed_traces) > 1000:
            self.completed_traces = self.completed_traces[-1000:]
        
        self.logger.info(
            "Trace span completed",
            trace_id=span_data['trace_id'],
            span_id=span_id,
            duration=span_data['duration'],
            success=success
        )
    
    @asynccontextmanager
    async def trace_context(self, trace_id: str, operation_name: str, parent_span: Optional[str] = None):
        """Context manager for automatic span lifecycle."""
        span_id = self.start_trace(trace_id, operation_name, parent_span)
        
        try:
            yield span_id
            self.finish_span(span_id, success=True)
        except Exception as e:
            self.finish_span(span_id, success=False, error=str(e))
            raise
    
    def export_traces_jaeger(self) -> List[Dict[str, Any]]:
        """Export traces in Jaeger format."""
        jaeger_traces = []
        
        # Group spans by trace_id
        traces_by_id = {}
        for span in self.completed_traces:
            trace_id = span['trace_id']
            if trace_id not in traces_by_id:
                traces_by_id[trace_id] = []
            traces_by_id[trace_id].append(span)
        
        # Convert to Jaeger format
        for trace_id, spans in traces_by_id.items():
            jaeger_spans = []
            for span in spans:
                jaeger_span = {
                    'traceID': trace_id,
                    'spanID': span['span_id'],
                    'parentSpanID': span.get('parent_span'),
                    'operationName': span['operation_name'],
                    'startTime': int(span['start_time'] * 1000000),  # microseconds
                    'duration': int(span['duration'] * 1000000),  # microseconds
                    'tags': [{'key': k, 'value': v} for k, v in span['tags'].items()],
                    'logs': [{
                        'timestamp': int(log['timestamp'] * 1000000),
                        'fields': [
                            {'key': 'level', 'value': log['level']},
                            {'key': 'message', 'value': log['message']}
                        ]
                    } for log in span['logs']]
                }
                jaeger_spans.append(jaeger_span)
            
            jaeger_traces.append({
                'traceID': trace_id,
                'spans': jaeger_spans,
                'processes': {
                    'p1': {
                        'serviceName': self.service_name,
                        'tags': [{'key': 'framework', 'value': 'PydanticAI'}]
                    }
                }
            })
        
        return jaeger_traces

# Monitored agent wrapper
class MonitoredPydanticAgent:
    """PydanticAI agent wrapper with comprehensive monitoring."""
    
    def __init__(
        self,
        agent: Agent,
        metrics_collector: EnterpriseMetricsCollector,
        tracer: DistributedTracing,
        agent_id: str
    ):
        self.agent = agent
        self.metrics_collector = metrics_collector
        self.tracer = tracer
        self.agent_id = agent_id
        
        # Register agent with metrics collector
        self.metrics_collector.register_agent(agent_id)
        
        self.logger = structlog.get_logger("pydantic_ai.monitored_agent").bind(agent_id=agent_id)
    
    async def run(
        self, 
        user_prompt: str, 
        deps: Any = None,
        trace_id: Optional[str] = None
    ) -> Any:
        """Run agent with comprehensive monitoring."""
        
        # Generate trace ID if not provided
        if not trace_id:
            trace_id = f"{self.agent_id}_{int(time.time() * 1000)}"
        
        start_time = time.time()
        
        async with self.tracer.trace_context(trace_id, f"agent_{self.agent_id}_run") as span_id:
            
            # Add trace tags
            self.tracer.add_span_tag(span_id, "agent.id", self.agent_id)
            self.tracer.add_span_tag(span_id, "agent.model", str(self.agent.model))
            self.tracer.add_span_tag(span_id, "user.prompt.length", len(user_prompt))
            
            # Log request start
            self.tracer.add_span_log(span_id, f"Agent request started: {user_prompt[:100]}...")
            
            try:
                # Execute agent
                result = await self.agent.run(user_prompt, deps=deps)
                
                # Calculate metrics
                response_time = time.time() - start_time
                
                # Estimate tokens and cost (simplified)
                estimated_tokens = len(user_prompt.split()) + len(str(result).split())
                estimated_cost = estimated_tokens * 0.00002  # Rough GPT-4 pricing
                
                # Record success metrics
                self.metrics_collector.record_request(
                    agent_id=self.agent_id,
                    success=True,
                    response_time=response_time,
                    tokens_used=estimated_tokens,
                    estimated_cost=estimated_cost
                )
                
                # Add trace tags for success
                self.tracer.add_span_tag(span_id, "response.tokens", estimated_tokens)
                self.tracer.add_span_tag(span_id, "response.cost", estimated_cost)
                self.tracer.add_span_log(span_id, "Agent request completed successfully")
                
                self.logger.info(
                    "Agent request successful",
                    response_time=response_time,
                    tokens_used=estimated_tokens,
                    cost=estimated_cost
                )
                
                return result
                
            except Exception as e:
                # Calculate response time even for failures
                response_time = time.time() - start_time
                error_type = type(e).__name__
                
                # Record error metrics
                self.metrics_collector.record_request(
                    agent_id=self.agent_id,
                    success=False,
                    response_time=response_time,
                    error_type=error_type
                )
                
                # Add trace tags for error
                self.tracer.add_span_tag(span_id, "error", True)
                self.tracer.add_span_tag(span_id, "error.type", error_type)
                self.tracer.add_span_log(span_id, f"Agent request failed: {str(e)}", level="error")
                
                self.logger.error(
                    "Agent request failed",
                    error=str(e),
                    error_type=error_type,
                    response_time=response_time
                )
                
                raise
    
    def get_metrics_summary(self) -> Optional[Dict[str, Any]]:
        """Get metrics summary for this agent."""
        return self.metrics_collector.get_agent_summary(self.agent_id)

# Usage example for enterprise monitoring
async def demonstrate_enterprise_monitoring():
    """Demonstrate enterprise monitoring and observability."""
    
    # Initialize monitoring components
    metrics_collector = EnterpriseMetricsCollector()
    tracer = DistributedTracing(service_name="research-agents")
    
    # Enable external integrations
    metrics_collector.enable_prometheus_export(port=8000)
    
    # Create monitored agents
    base_agent = Agent(
        'openai:gpt-4',
        result_type=ResearchResult,
        system_prompt="You are a research analyst with monitoring capabilities."
    )
    
    monitored_agent = MonitoredPydanticAgent(
        agent=base_agent,
        metrics_collector=metrics_collector,
        tracer=tracer,
        agent_id="research_agent_v1"
    )
    
    # Simulate multiple requests
    test_prompts = [
        "Research AI safety in 2025",
        "Analyze machine learning trends",
        "Study natural language processing advances"
    ]
    
    results = []
    for i, prompt in enumerate(test_prompts):
        try:
            context = ExecutionContext(user_id=f"test_user_{i}")
            result = await monitored_agent.run(prompt, deps=context, trace_id=f"test_trace_{i}")
            results.append(result)
            
            # Add delay to simulate realistic usage
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"Request failed: {e}")
    
    # Get comprehensive metrics
    agent_summary = monitored_agent.get_metrics_summary()
    global_summary = metrics_collector.get_global_summary()
    
    # Export traces
    jaeger_traces = tracer.export_traces_jaeger()
    
    # Export Prometheus metrics
    prometheus_metrics = metrics_collector.export_to_prometheus()
    
    return {
        'agent_summary': agent_summary,
        'global_summary': global_summary,
        'trace_count': len(jaeger_traces),
        'prometheus_metrics_lines': len(prometheus_metrics.split('\n')) if prometheus_metrics else 0,
        'successful_requests': len(results)
    }
```

This enterprise monitoring system provides comprehensive observability with metrics collection, distributed tracing, and integration with external monitoring platforms like Prometheus and Jaeger.

### **Caching and Performance Patterns**

Performance optimization in PydanticAI applications focuses on intelligent caching, request batching, and resource management while maintaining type safety.

Let's build a comprehensive performance optimization system for PydanticAI applications:

**Step 1: Import optimization dependencies**

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
```

**Step 2: Define intelligent cache entry system**

```python
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
```

The cache entry tracks creation time, access patterns, and expiration logic for intelligent cache management.

**Step 3: Create high-performance intelligent cache**

```python
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
```

This cache uses OrderedDict for LRU ordering and tracks memory usage, hit rates, and eviction statistics.

**Step 4: Implement cache management utilities**

```python    
    def _calculate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return len(json.dumps(obj, default=str).encode('utf-8'))
        except:
            # Fallback estimation
            return len(str(obj)) * 2  # Rough estimate for Unicode
```

**Step 5: Add intelligent eviction strategies**

```python
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
```

**Step 6: Implement thread-safe cache operations**

```python
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
```

This implements intelligent caching with LRU eviction, expiration cleanup, and detailed statistics tracking.

**Step 7: Add cache modification and management operations**

```python
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
```

The cache provides management operations (invalidate, clear) and comprehensive statistics for monitoring performance and tuning cache parameters.

**Step 8: Create intelligent caching decorator for methods**

```python
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
            # Same caching logic for synchronous functions
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args[1:])
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
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

## **Ready to Test Your Knowledge?**

You've completed Session 5 on PydanticAI Type-Safe Agents. Test your understanding with the multiple-choice questions above.

**[View Test Solutions](Session5_Test_Solutions.md)**

---

## **Next Steps**

Session 6 explores advanced agent orchestration patterns and enterprise integration strategies, building on the type-safe foundations established in this session. The focus shifts to coordinating multiple PydanticAI agents in complex workflows while maintaining the reliability and performance characteristics demonstrated here.

---

*This session demonstrated comprehensive PydanticAI development patterns enhanced with 2025 features, from real-time structured output validation through enterprise-grade production deployment. The integration of streaming validation, PromptedOutput control, dependency injection, model-agnostic interfaces, and comprehensive monitoring establishes PydanticAI as the definitive framework for type-safe, production-ready agent development. These capabilities enable building robust, maintainable agents that scale seamlessly from prototype to enterprise deployment while maintaining strict type safety and comprehensive observability.*
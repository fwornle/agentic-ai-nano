# src/session6/atomic_agents_course.py
"""
Atomic Agents course implementation demonstrating modular architecture patterns.
Zero-dependency implementation that showcases component-based agent design.
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import logging
import uuid

# Mock Pydantic functionality for course demonstration
class BaseModel:
    """Mock BaseModel for input validation."""
    
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
    
    def dict(self):
        """Convert to dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def json(self, indent=2):
        """Convert to JSON string."""
        return json.dumps(self.dict(), indent=indent, default=str)

# Core Atomic Agent Architecture

@dataclass
class AtomicContext:
    """Execution context for atomic agents - lightweight and focused."""
    user_id: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to context."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from context."""
        return self.metadata.get(key, default)

@dataclass
class AtomicResult:
    """Standard result format for atomic agents."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    agent_id: str = ""
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'agent_id': self.agent_id,
            'processing_time_ms': self.processing_time_ms,
            'metadata': self.metadata,
            'confidence': self.confidence
        }

class AtomicAgent(ABC):
    """Base class for all atomic agents - single responsibility principle."""
    
    def __init__(self, agent_id: str = None, config: Dict[str, Any] = None):
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.config = config or {}
        self.logger = logging.getLogger(f"atomic.{self.agent_id}")
        
        # Single responsibility metrics
        self.execution_count = 0
        self.total_processing_time = 0.0
        self.success_count = 0
        self.error_count = 0
    
    @abstractmethod
    async def execute(self, input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute the single responsibility of this atomic agent."""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Type:
        """Return the expected input schema for this agent."""
        pass
    
    @abstractmethod
    def get_output_schema(self) -> Type:
        """Return the output schema for this agent."""
        pass
    
    async def _execute_with_metrics(self, input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute with automatic metrics collection."""
        start_time = time.time()
        self.execution_count += 1
        
        try:
            # Validate input schema
            input_schema = self.get_input_schema()
            if input_schema and not isinstance(input_data, input_schema):
                if hasattr(input_schema, '__annotations__'):
                    # Try to create from dict if possible
                    if isinstance(input_data, dict):
                        input_data = input_schema(**input_data)
            
            # Execute the atomic operation
            result = await self.execute(input_data, context)
            result.agent_id = self.agent_id
            result.processing_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            if result.success:
                self.success_count += 1
            else:
                self.error_count += 1
            
            self.total_processing_time += result.processing_time_ms
            
            return result
            
        except Exception as e:
            self.error_count += 1
            processing_time = (time.time() - start_time) * 1000
            self.total_processing_time += processing_time
            
            self.logger.error(f"Execution failed: {e}")
            
            return AtomicResult(
                success=False,
                error=str(e),
                agent_id=self.agent_id,
                processing_time_ms=processing_time,
                metadata={'error_type': type(e).__name__}
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this atomic agent."""
        return {
            'agent_id': self.agent_id,
            'execution_count': self.execution_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / max(self.execution_count, 1),
            'total_processing_time_ms': self.total_processing_time,
            'average_processing_time_ms': self.total_processing_time / max(self.execution_count, 1)
        }

# Specialized Atomic Agents for Data Processing

class TextProcessingInput(BaseModel):
    """Input schema for text processing agents."""
    
    def __init__(self, content: str, operation: str = "process", **kwargs):
        self.content = content
        self.operation = operation
        for key, value in kwargs.items():
            setattr(self, key, value)

class TextProcessingOutput(BaseModel):
    """Output schema for text processing agents."""
    
    def __init__(self, result: str, word_count: int = 0, confidence: float = 1.0, validation_type: str = "basic", **kwargs):
        self.result = result
        self.word_count = word_count
        self.confidence = confidence
        self.validation_type = validation_type
        for key, value in kwargs.items():
            setattr(self, key, value)

class TextProcessorAgent(AtomicAgent):
    """Atomic agent focused solely on text processing operations."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operations = {
            'summarize': self._summarize,
            'extract_keywords': self._extract_keywords,
            'sentiment': self._analyze_sentiment,
            'word_count': self._count_words,
            'uppercase': self._to_uppercase,
            'clean': self._clean_text
        }
    
    def get_input_schema(self) -> Type:
        return TextProcessingInput
    
    def get_output_schema(self) -> Type:
        return TextProcessingOutput
    
    async def execute(self, input_data: TextProcessingInput, context: AtomicContext) -> AtomicResult:
        """Execute text processing with single responsibility focus."""
        
        if input_data.operation not in self.operations:
            return AtomicResult(
                success=False,
                error=f"Unsupported operation: {input_data.operation}. Available: {list(self.operations.keys())}"
            )
        
        try:
            # Simulate processing delay for realistic behavior
            await asyncio.sleep(0.1)
            
            # Execute the specific text operation
            operation_func = self.operations[input_data.operation]
            result_text, confidence = await operation_func(input_data.content)
            
            # Create structured output
            output = TextProcessingOutput(
                result=result_text,
                word_count=len(input_data.content.split()),
                confidence=confidence
            )
            
            return AtomicResult(
                success=True,
                data=output,
                confidence=confidence,
                metadata={
                    'operation': input_data.operation,
                    'input_length': len(input_data.content),
                    'output_length': len(result_text)
                }
            )
            
        except Exception as e:
            return AtomicResult(
                success=False,
                error=f"Text processing failed: {e}"
            )
    
    async def _summarize(self, text: str) -> tuple[str, float]:
        """Atomic operation: text summarization."""
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text, 1.0
        
        # Simple extractive summarization - take first and last sentence
        summary = f"{sentences[0].strip()}. {sentences[-2].strip()}."
        confidence = min(0.8 + (len(sentences) - 2) * 0.02, 0.95)
        
        return summary, confidence
    
    async def _extract_keywords(self, text: str) -> tuple[str, float]:
        """Atomic operation: keyword extraction."""
        words = text.lower().split()
        # Simple keyword extraction based on word length and frequency
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                clean_word = ''.join(c for c in word if c.isalnum())
                if clean_word:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.keys(), key=lambda w: word_freq[w], reverse=True)[:5]
        result = ', '.join(keywords) if keywords else 'No keywords found'
        confidence = min(len(keywords) * 0.15, 0.9)
        
        return result, confidence
    
    async def _analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Atomic operation: sentiment analysis."""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'positive', 'fantastic', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'negative', 'poor']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.6 + positive_count * 0.1, 0.95)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.6 + negative_count * 0.1, 0.95)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return sentiment, confidence
    
    async def _count_words(self, text: str) -> tuple[str, float]:
        """Atomic operation: word counting."""
        word_count = len(text.split())
        return f"{word_count} words", 1.0
    
    async def _to_uppercase(self, text: str) -> tuple[str, float]:
        """Atomic operation: text transformation."""
        return text.upper(), 1.0
    
    async def _clean_text(self, text: str) -> tuple[str, float]:
        """Atomic operation: text cleaning."""
        # Simple text cleaning
        import re
        cleaned = re.sub(r'\s+', ' ', text.strip())  # Normalize whitespace
        cleaned = re.sub(r'[^\w\s\.\?\!]', '', cleaned)  # Remove special chars except punctuation
        return cleaned, 0.9

class DataValidationInput(BaseModel):
    """Input schema for data validation agents."""
    
    def __init__(self, data: Any, validation_type: str = "basic", **kwargs):
        self.data = data
        self.validation_type = validation_type
        for key, value in kwargs.items():
            setattr(self, key, value)

class DataValidationOutput(BaseModel):
    """Output schema for data validation agents."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None, **kwargs):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        for key, value in kwargs.items():
            setattr(self, key, value)

class DataValidationAgent(AtomicAgent):
    """Atomic agent focused solely on data validation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators = {
            'basic': self._basic_validation,
            'schema': self._schema_validation,
            'range': self._range_validation,
            'format': self._format_validation,
            'completeness': self._completeness_validation
        }
    
    def get_input_schema(self) -> Type:
        return DataValidationInput
    
    def get_output_schema(self) -> Type:
        return DataValidationOutput
    
    async def execute(self, input_data: DataValidationInput, context: AtomicContext) -> AtomicResult:
        """Execute data validation with single responsibility focus."""
        
        if input_data.validation_type not in self.validators:
            return AtomicResult(
                success=False,
                error=f"Unknown validation type: {input_data.validation_type}"
            )
        
        try:
            # Execute validation
            validator = self.validators[input_data.validation_type]
            is_valid, errors, warnings = await validator(input_data.data)
            
            output = DataValidationOutput(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings
            )
            
            return AtomicResult(
                success=True,
                data=output,
                metadata={
                    'validation_type': input_data.validation_type,
                    'data_type': type(input_data.data).__name__,
                    'error_count': len(errors),
                    'warning_count': len(warnings)
                }
            )
            
        except Exception as e:
            return AtomicResult(
                success=False,
                error=f"Validation failed: {e}"
            )
    
    async def _basic_validation(self, data: Any) -> tuple[bool, List[str], List[str]]:
        """Basic data validation."""
        errors = []
        warnings = []
        
        if data is None:
            errors.append("Data is None")
        elif isinstance(data, str) and len(data) == 0:
            errors.append("String data is empty")
        elif isinstance(data, (list, dict)) and len(data) == 0:
            warnings.append("Collection is empty")
        
        return len(errors) == 0, errors, warnings
    
    async def _schema_validation(self, data: Any) -> tuple[bool, List[str], List[str]]:
        """Schema-based validation."""
        errors = []
        warnings = []
        
        if isinstance(data, dict):
            required_fields = ['id', 'name']
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")
            
            if 'created_at' not in data:
                warnings.append("Missing recommended field: created_at")
        else:
            errors.append("Expected dictionary data for schema validation")
        
        return len(errors) == 0, errors, warnings
    
    async def _range_validation(self, data: Any) -> tuple[bool, List[str], List[str]]:
        """Range validation for numeric data."""
        errors = []
        warnings = []
        
        if isinstance(data, (int, float)):
            if data < 0:
                errors.append("Value must be non-negative")
            elif data > 1000:
                warnings.append("Value is unusually large")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (int, float)):
                    if item < 0:
                        errors.append(f"Item {i} must be non-negative")
        else:
            errors.append("Expected numeric data for range validation")
        
        return len(errors) == 0, errors, warnings
    
    async def _format_validation(self, data: Any) -> tuple[bool, List[str], List[str]]:
        """Format validation for structured data."""
        errors = []
        warnings = []
        
        if isinstance(data, str):
            # Check for email format
            if '@' in data:
                if not ('.' in data.split('@')[1]):
                    errors.append("Invalid email format")
            # Check for URL format
            elif data.startswith(('http://', 'https://')):
                if not ('.' in data):
                    errors.append("Invalid URL format")
        
        return len(errors) == 0, errors, warnings
    
    async def _completeness_validation(self, data: Any) -> tuple[bool, List[str], List[str]]:
        """Completeness validation."""
        errors = []
        warnings = []
        
        if isinstance(data, dict):
            none_values = [k for k, v in data.items() if v is None]
            empty_values = [k for k, v in data.items() if isinstance(v, str) and v.strip() == '']
            
            if none_values:
                warnings.extend([f"Field '{k}' is None" for k in none_values])
            if empty_values:
                warnings.extend([f"Field '{k}' is empty" for k in empty_values])
            
            completeness_score = 1.0 - (len(none_values) + len(empty_values)) / len(data)
            if completeness_score < 0.5:
                errors.append("Data completeness is below 50%")
        
        return len(errors) == 0, errors, warnings

# Composition and Orchestration

class AtomicPipeline:
    """Compose atomic agents into processing pipelines."""
    
    def __init__(self, pipeline_id: str = None):
        self.pipeline_id = pipeline_id or f"pipeline_{uuid.uuid4().hex[:8]}"
        self.agents: List[AtomicAgent] = []
        self.execution_history: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: AtomicAgent) -> 'AtomicPipeline':
        """Add an atomic agent to the pipeline."""
        self.agents.append(agent)
        return self  # Fluent interface
    
    def add_agents(self, *agents: AtomicAgent) -> 'AtomicPipeline':
        """Add multiple agents to the pipeline."""
        self.agents.extend(agents)
        return self
    
    def _transform_data_for_next_agent(self, data: Any, current_step: int, context: AtomicContext) -> Any:
        """Transform data between different agent types in the pipeline."""
        if current_step + 1 >= len(self.agents):
            return data  # No next agent
        
        next_agent = self.agents[current_step + 1]
        next_agent_type = type(next_agent).__name__
        
        # Handle TextProcessorAgent -> DataValidationAgent transformation
        if (hasattr(data, 'result') and hasattr(data, 'confidence') and 
            next_agent_type == 'DataValidationAgent'):
            # Transform TextProcessingOutput to DataValidationInput
            return DataValidationInput(
                data=data.result,
                validation_type=getattr(data, 'validation_type', 'basic')
            )
        
        # Handle DataValidationAgent -> other agent transformations
        if (hasattr(data, 'is_valid') and hasattr(data, 'errors') and
            next_agent_type == 'TextProcessorAgent'):
            # Transform DataValidationOutput to TextProcessingInput
            content = f"Validation result: {'valid' if data.is_valid else 'invalid'}"
            if data.errors:
                content += f". Errors: {', '.join(data.errors)}"
            return TextProcessingInput(content=content, operation='summarize')
        
        # Default: pass data through unchanged
        return data
    
    async def execute(self, input_data: Any, context: AtomicContext) -> AtomicResult:
        """Execute the pipeline sequentially."""
        if not self.agents:
            return AtomicResult(
                success=False,
                error="Pipeline has no agents"
            )
        
        start_time = time.time()
        current_data = input_data
        pipeline_results = []
        
        try:
            # Execute each agent in sequence
            for i, agent in enumerate(self.agents):
                result = await agent._execute_with_metrics(current_data, context)
                pipeline_results.append({
                    'step': i,
                    'agent_id': agent.agent_id,
                    'success': result.success,
                    'processing_time_ms': result.processing_time_ms
                })
                
                if not result.success:
                    return AtomicResult(
                        success=False,
                        error=f"Pipeline failed at step {i} ({agent.agent_id}): {result.error}",
                        metadata={
                            'pipeline_id': self.pipeline_id,
                            'failed_step': i,
                            'steps_completed': i,
                            'pipeline_results': pipeline_results
                        }
                    )
                
                # Use the output as input for the next agent with schema transformation
                if result.data is not None:
                    # Handle schema transformation between different agent types
                    current_data = self._transform_data_for_next_agent(result.data, i, context)
                else:
                    current_data = current_data
            
            total_time = (time.time() - start_time) * 1000
            
            # Record successful execution
            execution_record = {
                'pipeline_id': self.pipeline_id,
                'execution_time': datetime.now().isoformat(),
                'total_processing_time_ms': total_time,
                'steps_completed': len(self.agents),
                'success': True
            }
            self.execution_history.append(execution_record)
            
            return AtomicResult(
                success=True,
                data=current_data,
                processing_time_ms=total_time,
                metadata={
                    'pipeline_id': self.pipeline_id,
                    'steps_completed': len(self.agents),
                    'pipeline_results': pipeline_results,
                    'agents_executed': [agent.agent_id for agent in self.agents]
                }
            )
            
        except Exception as e:
            return AtomicResult(
                success=False,
                error=f"Pipeline execution failed: {e}",
                metadata={'pipeline_id': self.pipeline_id}
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics."""
        if not self.execution_history:
            return {
                'pipeline_id': self.pipeline_id,
                'total_executions': 0,
                'successful_executions': 0,
                'success_rate': 0.0,
                'average_processing_time_ms': 0.0,
                'agent_count': len(self.agents),
                'agent_metrics': [agent.get_metrics() for agent in self.agents]
            }
        
        successful_executions = [h for h in self.execution_history if h.get('success')]
        total_executions = len(self.execution_history)
        
        return {
            'pipeline_id': self.pipeline_id,
            'total_executions': total_executions,
            'successful_executions': len(successful_executions),
            'success_rate': len(successful_executions) / max(total_executions, 1),
            'average_processing_time_ms': sum(h.get('total_processing_time_ms', 0) for h in successful_executions) / max(len(successful_executions), 1),
            'agent_count': len(self.agents),
            'agent_metrics': [agent.get_metrics() for agent in self.agents]
        }

class AtomicParallelExecutor:
    """Execute multiple atomic agents in parallel."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_parallel(
        self, 
        tasks: List[tuple[AtomicAgent, Any]], 
        context: AtomicContext
    ) -> List[AtomicResult]:
        """Execute multiple agents in parallel."""
        
        if not tasks:
            return []
        
        start_time = time.time()
        results = []
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def execute_single_task(agent: AtomicAgent, input_data: Any) -> AtomicResult:
            async with semaphore:
                return await agent._execute_with_metrics(input_data, context)
        
        try:
            # Execute all tasks in parallel
            task_coroutines = [
                execute_single_task(agent, input_data) 
                for agent, input_data in tasks
            ]
            
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)
            
            # Handle any exceptions that occurred
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(AtomicResult(
                        success=False,
                        error=str(result),
                        metadata={'task_index': i}
                    ))
                else:
                    processed_results.append(result)
            
            # Record execution metrics
            total_time = (time.time() - start_time) * 1000
            successful_count = sum(1 for r in processed_results if r.success)
            
            execution_record = {
                'execution_time': datetime.now().isoformat(),
                'total_processing_time_ms': total_time,
                'task_count': len(tasks),
                'successful_count': successful_count,
                'success_rate': successful_count / len(tasks),
                'max_concurrent': self.max_concurrent
            }
            self.execution_history.append(execution_record)
            
            return processed_results
            
        except Exception as e:
            # Fallback error handling
            return [AtomicResult(
                success=False,
                error=f"Parallel execution failed: {e}"
            ) for _ in tasks]

# Atomic System Registry and Discovery

class AtomicRegistry:
    """Registry for atomic agents and their capabilities."""
    
    def __init__(self):
        self.agents: Dict[str, Type[AtomicAgent]] = {}
        self.instances: Dict[str, AtomicAgent] = {}
    
    def register_agent(self, agent_class: Type[AtomicAgent], name: str = None) -> None:
        """Register an atomic agent class."""
        agent_name = name or agent_class.__name__
        self.agents[agent_name] = agent_class
    
    def create_agent(self, agent_name: str, **kwargs) -> Optional[AtomicAgent]:
        """Create an instance of a registered agent."""
        if agent_name not in self.agents:
            return None
        
        agent_class = self.agents[agent_name]
        instance = agent_class(**kwargs)
        self.instances[instance.agent_id] = instance
        return instance
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent types."""
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered agent."""
        if agent_name not in self.agents:
            return None
        
        agent_class = self.agents[agent_name]
        return {
            'name': agent_name,
            'class': agent_class.__name__,
            'description': agent_class.__doc__ or "No description available",
            'input_schema': getattr(agent_class, '__input_schema__', None),
            'output_schema': getattr(agent_class, '__output_schema__', None)
        }
    
    def get_instance_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all agent instances."""
        return {
            instance_id: agent.get_metrics() 
            for instance_id, agent in self.instances.items()
        }

# Global registry instance
atomic_registry = AtomicRegistry()

# Auto-register our agents
atomic_registry.register_agent(TextProcessorAgent, "text_processor")
atomic_registry.register_agent(DataValidationAgent, "data_validator")

# Demo and Testing Functions

async def demonstrate_basic_atomic_agent():
    """Demonstrate basic atomic agent functionality."""
    print("🔬 Basic Atomic Agent Demo")
    print("-" * 30)
    
    # Create context
    context = AtomicContext(user_id="demo_user")
    
    # Create text processing agent
    text_agent = TextProcessorAgent()
    
    # Test different operations
    operations = [
        ("summarize", "Atomic agents represent a paradigm shift in agent architecture. They embrace modular design principles that enable composition and reusability. Each agent focuses on a single responsibility, making systems more maintainable and scalable. This approach mirrors microservices architecture patterns that have proven successful in distributed systems."),
        ("extract_keywords", "Machine learning artificial intelligence technology future innovation automation"),
        ("sentiment", "This is absolutely wonderful and amazing news!"),
        ("word_count", "Count the words in this sentence please")
    ]
    
    for operation, text in operations:
        input_data = TextProcessingInput(content=text, operation=operation)
        result = await text_agent._execute_with_metrics(input_data, context)
        
        print(f"✅ Operation: {operation}")
        print(f"   Result: {result.data.result if result.success else result.error}")
        print(f"   Processing Time: {result.processing_time_ms:.1f}ms")
        print(f"   Confidence: {result.confidence}")
        print()
    
    # Show agent metrics
    metrics = text_agent.get_metrics()
    print(f"📊 Agent Metrics:")
    print(f"   Executions: {metrics['execution_count']}")
    print(f"   Success Rate: {metrics['success_rate']:.1%}")
    print(f"   Avg Processing Time: {metrics['average_processing_time_ms']:.1f}ms")

async def demonstrate_data_validation():
    """Demonstrate data validation atomic agent."""
    print("\n🛡️ Data Validation Agent Demo")
    print("-" * 30)
    
    context = AtomicContext(user_id="validator_demo")
    validator = DataValidationAgent()
    
    test_cases = [
        ("basic", {"id": 123, "name": "Test User", "created_at": "2024-01-01"}),
        ("schema", {"id": 456, "name": "Valid User"}),
        ("range", [1, 5, 10, 15, 2000]),  # One value will trigger warning
        ("format", "user@example.com"),
        ("completeness", {"name": "John", "email": None, "phone": ""})
    ]
    
    for validation_type, test_data in test_cases:
        input_data = DataValidationInput(data=test_data, validation_type=validation_type)
        result = await validator._execute_with_metrics(input_data, context)
        
        print(f"✅ Validation Type: {validation_type}")
        if result.success:
            output = result.data
            print(f"   Valid: {output.is_valid}")
            if output.errors:
                print(f"   Errors: {output.errors}")
            if output.warnings:
                print(f"   Warnings: {output.warnings}")
        else:
            print(f"   Error: {result.error}")
        print()

async def demonstrate_pipeline_composition():
    """Demonstrate atomic pipeline composition."""
    print("\n🔗 Pipeline Composition Demo")
    print("-" * 30)
    
    context = AtomicContext(user_id="pipeline_demo")
    
    # Create pipeline with text processing and validation
    pipeline = AtomicPipeline("text_analysis_pipeline")
    pipeline.add_agent(TextProcessorAgent()).add_agent(DataValidationAgent())
    
    # Process text input
    text_input = TextProcessingInput(
        content="This is a comprehensive analysis of atomic agent architecture patterns and their benefits for modular system design.",
        operation="summarize"
    )
    
    result = await pipeline.execute(text_input, context)
    
    print(f"✅ Pipeline Execution:")
    print(f"   Success: {result.success}")
    print(f"   Processing Time: {result.processing_time_ms:.1f}ms")
    print(f"   Steps Completed: {result.metadata.get('steps_completed', 0)}")
    
    if result.success:
        print(f"   Final Result: {result.data}")
    else:
        print(f"   Error: {result.error}")
    
    # Show pipeline metrics
    print(f"\n📊 Pipeline Metrics:")
    pipeline_metrics = pipeline.get_metrics()
    print(f"   Total Executions: {pipeline_metrics['total_executions']}")
    print(f"   Success Rate: {pipeline_metrics['success_rate']:.1%}")
    print(f"   Agent Count: {pipeline_metrics['agent_count']}")

async def demonstrate_parallel_execution():
    """Demonstrate parallel execution of atomic agents."""
    print("\n⚡ Parallel Execution Demo")
    print("-" * 30)
    
    context = AtomicContext(user_id="parallel_demo")
    executor = AtomicParallelExecutor(max_concurrent=3)
    
    # Create multiple text processing tasks
    tasks = [
        (TextProcessorAgent(), TextProcessingInput(content="This is wonderful news!", operation="sentiment")),
        (TextProcessorAgent(), TextProcessingInput(content="Unfortunately, this is disappointing.", operation="sentiment")),
        (TextProcessorAgent(), TextProcessingInput(content="Machine learning artificial intelligence", operation="extract_keywords")),
        (DataValidationAgent(), DataValidationInput(data={"id": 1, "name": "Test"}, validation_type="schema"))
    ]
    
    results = await executor.execute_parallel(tasks, context)
    
    print(f"✅ Parallel Execution Results:")
    for i, result in enumerate(results):
        task_type = "Text" if i < 3 else "Validation"
        print(f"   Task {i+1} ({task_type}): {'✅' if result.success else '❌'}")
        if result.success and hasattr(result.data, 'result'):
            print(f"      Result: {result.data.result}")
        elif result.success and hasattr(result.data, 'is_valid'):
            print(f"      Valid: {result.data.is_valid}")
        print(f"      Time: {result.processing_time_ms:.1f}ms")
    
    success_count = sum(1 for r in results if r.success)
    print(f"\n📊 Parallel Execution Summary:")
    print(f"   Total Tasks: {len(tasks)}")
    print(f"   Successful: {success_count}")
    print(f"   Success Rate: {success_count/len(tasks):.1%}")

async def demonstrate_atomic_registry():
    """Demonstrate atomic agent registry and discovery."""
    print("\n📋 Atomic Registry Demo")
    print("-" * 30)
    
    # Show available agents
    available = atomic_registry.get_available_agents()
    print(f"✅ Available Atomic Agents: {available}")
    
    # Get agent information
    for agent_name in available:
        info = atomic_registry.get_agent_info(agent_name)
        print(f"\n🔍 {agent_name}:")
        print(f"   Class: {info['class']}")
        print(f"   Description: {info['description'][:100]}...")
    
    # Create agents through registry
    text_agent = atomic_registry.create_agent("text_processor")
    validator_agent = atomic_registry.create_agent("data_validator")
    
    print(f"\n✅ Created agents through registry:")
    print(f"   Text Processor: {text_agent.agent_id}")
    print(f"   Data Validator: {validator_agent.agent_id}")
    
    # Execute sample tasks
    context = AtomicContext(user_id="registry_demo")
    
    text_input = TextProcessingInput(content="Registry-created agents work perfectly!", operation="sentiment")
    result = await text_agent._execute_with_metrics(text_input, context)
    
    print(f"\n✅ Registry Agent Execution:")
    print(f"   Result: {result.data.result if result.success else result.error}")
    
    # Show instance metrics
    print(f"\n📊 Registry Instance Metrics:")
    metrics = atomic_registry.get_instance_metrics()
    for instance_id, instance_metrics in metrics.items():
        print(f"   {instance_id}: {instance_metrics['execution_count']} executions")

async def run_comprehensive_demo():
    """Run all atomic agents demonstrations."""
    print("🚀 Atomic Agents Architecture - Comprehensive Demo")
    print("=" * 55)
    print("\nDemonstrating modular, composable agent architecture")
    print("Each agent has single responsibility and clear interfaces\n")
    
    try:
        await demonstrate_basic_atomic_agent()
        await demonstrate_data_validation()
        await demonstrate_pipeline_composition()
        await demonstrate_parallel_execution()
        await demonstrate_atomic_registry()
        
        print("\n🎯 Demo Complete!")
        print("\nKey Atomic Architecture Benefits Demonstrated:")
        print("• ✅ Single responsibility - each agent has one focused task")
        print("• ✅ Composability - agents work together seamlessly")
        print("• ✅ Schema contracts - clear input/output interfaces")
        print("• ✅ Parallel execution - natural concurrency support")
        print("• ✅ Metrics tracking - built-in observability")
        print("• ✅ Registry system - service discovery patterns")
        
        print(f"\n💡 Production Deployment Characteristics:")
        print("• Microservices-inspired architecture")
        print("• Horizontal scaling through agent instances")
        print("• Fault isolation through component boundaries")
        print("• Easy testing through atomic units")
        print("• Maintainable through single responsibility")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run comprehensive demonstration
    asyncio.run(run_comprehensive_demo())
# Session 6: Atomic Agents Architecture

This directory contains a complete implementation of atomic agent architecture patterns, demonstrating how to build composable, type-safe agent systems that scale from simple tasks to enterprise deployments.

## Architecture Overview

Atomic agents follow the principle that complex systems should be built from simple, composable, and reusable components. Like LEGO blocks, each atomic agent is designed to be self-contained yet seamlessly interoperable with others.

### Core Principles

1. **Single Responsibility**: Each agent handles one concern perfectly
2. **Type Safety**: Schemas and validation ensure reliable data flow
3. **Composition**: Complex behaviors emerge from simple component interactions
4. **Observability**: Built-in monitoring and debugging capabilities

## File Structure

```
session6/
├── atomic_foundation.py        # Core atomic agent classes and exceptions
├── text_processor_agent.py     # Example atomic agent implementation
├── context_providers.py        # Dependency injection pattern
├── composition_engine.py       # Pipeline and parallel execution
├── atomic_cli.py              # Command-line interface
├── production_orchestrator.py  # Enterprise deployment patterns
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Core Components

### 1. Atomic Foundation (`atomic_foundation.py`)

Contains the base classes and infrastructure:

- `AtomicContext`: Context container for request tracking and metadata
- `AtomicAgent[T_Input, T_Output]`: Generic base class with type-safe I/O
- `AtomicError`: Structured exception handling
- `ValidationError` & `ExecutionError`: Specific error types

### 2. Text Processor Agent (`text_processor_agent.py`)

Example implementation demonstrating:

- Input/output schema definition with Pydantic
- Type-safe execution with comprehensive error handling
- Multiple operations (summarize, extract keywords, sentiment analysis)
- Performance monitoring and execution metrics

### 3. Context Providers (`context_providers.py`)

Dependency injection pattern for external resources:

- `ContextProvider`: Abstract base for all providers
- `DatabaseContextProvider`: Example database connection provider
- Mock implementations for testing and development

### 4. Composition Engine (`composition_engine.py`)

Pipeline and parallel execution patterns:

- `AtomicPipeline`: Chain multiple agents with type-safe data flow
- `AtomicParallelExecutor`: Execute independent operations concurrently
- Context enrichment and execution tracing
- Comprehensive error handling and rollback

### 5. CLI Integration (`atomic_cli.py`)

Command-line interface for:

- Single agent execution (`process-text`)
- Pipeline execution from configuration files
- JSON input/output with structured results
- Integration with CI/CD and automation workflows

### 6. Production Orchestrator (`production_orchestrator.py`)

Enterprise deployment features:

- `AtomicOrchestrator`: Service discovery and health monitoring
- `MetricsCollector`: Performance and reliability metrics
- `AtomicLoadBalancer`: Request routing with failover
- Graceful shutdown and lifecycle management

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from atomic_foundation import AtomicContext
from text_processor_agent import TextInput, TextProcessorAgent

async def example():
    # Create context
    context = AtomicContext(user_id="demo-user")

    # Create input
    text_input = TextInput(
        content="This is example text for processing.",
        operation="summarize"
    )

    # Execute agent
    agent = TextProcessorAgent()
    result = await agent.execute(text_input, context)

    print(f"Result: {result.result}")
    print(f"Confidence: {result.confidence}")
    print(f"Processing time: {result.processing_time_ms}ms")

# Run the example
asyncio.run(example())
```

### CLI Usage

```bash
# Process text directly
python -m atomic_cli process-text --text "Your text here" --operation summarize

# Run pipeline from configuration
python -m atomic_cli run-pipeline --config-file pipeline.json --input-file data.json
```

### Pipeline Configuration Example

```json
{
  "name": "Text Processing Pipeline",
  "agents": [
    {
      "type": "text_processor",
      "config": {
        "operation": "summarize"
      }
    }
  ]
}
```

## Advanced Patterns

### Creating Custom Agents

```python
from atomic_foundation import AtomicAgent, BaseModel, Field
from typing import Dict, Any

class MyInput(BaseModel):
    data: str = Field(..., min_length=1)
    options: Dict[str, Any] = Field(default_factory=dict)

class MyOutput(BaseModel):
    result: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MyAgent(AtomicAgent[MyInput, MyOutput]):
    def __init__(self):
        super().__init__("MyAgent", "1.0.0")

    def get_input_schema(self) -> type[MyInput]:
        return MyInput

    def get_output_schema(self) -> type[MyOutput]:
        return MyOutput

    async def execute(self, input_data: MyInput, context: AtomicContext) -> MyOutput:
        # Your processing logic here
        return MyOutput(
            result="processed data",
            metadata={"agent_id": self.agent_id}
        )
```

### Pipeline Composition

```python
from composition_engine import AtomicPipeline
from context_providers import DatabaseContextProvider

# Build pipeline
pipeline = (AtomicPipeline("My Pipeline")
           .add_agent(TextProcessorAgent())
           .add_context_provider(DatabaseContextProvider("sqlite:///data.db")))

# Execute pipeline
result = await pipeline.execute(input_data, context)
```

### Parallel Execution

```python
from composition_engine import AtomicParallelExecutor

executor = AtomicParallelExecutor(max_concurrent=3)

# Define agent tasks
tasks = [
    (TextProcessorAgent(), text_input1),
    (TextProcessorAgent(), text_input2),
    (TextProcessorAgent(), text_input3)
]

# Execute in parallel
results = await executor.execute_parallel(tasks, context)
```

## Production Deployment

### Service Registration

```python
from production_orchestrator import AtomicOrchestrator, ServiceRegistration

orchestrator = AtomicOrchestrator()
await orchestrator.start()

# Register a service
registration = ServiceRegistration(
    service_id="text-processor-1",
    service_name="Text Processor",
    agent_type="text_processor",
    endpoint="http://localhost:8000",
    health_check_url="http://localhost:8000/health",
    capabilities=["summarize", "sentiment", "keywords"]
)

await orchestrator.register_service(registration)
```

### Load Balancing

```python
from production_orchestrator import AtomicLoadBalancer

load_balancer = AtomicLoadBalancer(orchestrator)

# Route request to available service
result = await load_balancer.route_request(
    agent_type="text_processor",
    input_data=text_input,
    context=context,
    strategy="round_robin"
)
```

## Testing

```python
import pytest
import asyncio
from atomic_foundation import AtomicContext
from text_processor_agent import TextInput, TextProcessorAgent

@pytest.mark.asyncio
async def test_text_processor():
    agent = TextProcessorAgent()
    context = AtomicContext(user_id="test")

    text_input = TextInput(
        content="Test content for processing",
        operation="summarize"
    )

    result = await agent.execute(text_input, context)

    assert result.result is not None
    assert result.confidence > 0
    assert result.processing_time_ms >= 0
    assert result.word_count > 0
```

## Monitoring and Observability

The atomic agent architecture includes comprehensive monitoring:

- **Request tracing** through AtomicContext
- **Performance metrics** with execution timing
- **Health monitoring** for production services
- **Error tracking** with structured exceptions
- **Pipeline tracing** for complex workflows

## Best Practices

1. **Keep agents atomic**: Each agent should have a single, well-defined responsibility
2. **Use type hints**: Leverage Pydantic schemas for robust input/output validation
3. **Handle errors gracefully**: Use structured exceptions with detailed context
4. **Monitor performance**: Track execution times and success rates
5. **Test thoroughly**: Write comprehensive tests for individual agents and pipelines
6. **Document schemas**: Clear documentation of input/output contracts
7. **Version your agents**: Use semantic versioning for agent implementations

## Integration with Other Frameworks

This atomic agent architecture can be integrated with:

- **FastAPI**: For HTTP API endpoints
- **Celery**: For distributed task execution
- **Docker**: For containerized deployments
- **Kubernetes**: For orchestration and scaling
- **Prometheus**: For metrics collection
- **Grafana**: For monitoring dashboards

The modular design ensures compatibility with existing infrastructure and deployment patterns.
